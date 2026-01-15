import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders, handleCors } from '../_shared/cors.ts'
import { jsonResponse, errorResponse, extractIdFromPath, extractActionFromPath, parseBody } from '../_shared/response.ts'
import { requireAuth } from '../_shared/auth.ts'

// SM2 Algorithm implementation
function calculateSM2(rating: number, easeFactor: number, interval: number, repetition: number) {
    // Rating: 0 = Again, 1 = Hard, 2 = Good, 3 = Easy
    let newEaseFactor = easeFactor
    let newInterval = interval
    let newRepetition = repetition

    if (rating < 2) {
        // Failed - reset
        newRepetition = 0
        newInterval = 1
    } else {
        // Success
        newRepetition += 1

        if (newRepetition === 1) {
            newInterval = 1
        } else if (newRepetition === 2) {
            newInterval = 6
        } else {
            newInterval = Math.round(interval * easeFactor)
        }

        // Adjust ease factor based on rating
        newEaseFactor = Math.max(1.3, easeFactor + (0.1 - (3 - rating) * (0.08 + (3 - rating) * 0.02)))
    }

    // Determine status
    let status = 'learning'
    if (newRepetition >= 3 && newInterval >= 21) {
        status = 'mastered'
    } else if (newRepetition >= 1) {
        status = 'review'
    }

    return {
        ease_factor: newEaseFactor,
        interval_days: newInterval,
        repetition: newRepetition,
        status,
        next_review_date: new Date(Date.now() + newInterval * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    }
}

serve(async (req: Request) => {
    // Handle CORS preflight
    const corsResponse = handleCors(req)
    if (corsResponse) return corsResponse

    // All flashcard operations require authentication
    const auth = await requireAuth(req)
    if (auth.error) return auth.error
    const userId = auth.user.id

    const url = new URL(req.url)
    const method = req.method

    // Create Supabase client
    const supabase = createClient(
        Deno.env.get('SUPABASE_URL')!,
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    try {
        const flashcardId = extractIdFromPath(url.pathname)
        const action = extractActionFromPath(url.pathname)

        // GET /flashcards/due - Get due flashcards
        if (method === 'GET' && action === 'due') {
            const today = new Date().toISOString().split('T')[0]

            const { data, error } = await supabase
                .from('flashcard')
                .select(`
          *,
          question:question(
            id, content, explanation,
            options:question_option(id, content, is_correct, order)
          )
        `)
                .eq('user_id', userId)
                .lte('next_review_date', today)
                .order('next_review_date')
                .limit(20)

            if (error) {
                return errorResponse(error.message, 500)
            }

            return jsonResponse(data || [])
        }

        // GET /flashcards/stats - Get statistics
        if (method === 'GET' && action === 'stats') {
            const today = new Date().toISOString().split('T')[0]

            const { data: total } = await supabase
                .from('flashcard')
                .select('id', { count: 'exact' })
                .eq('user_id', userId)

            const { data: due } = await supabase
                .from('flashcard')
                .select('id', { count: 'exact' })
                .eq('user_id', userId)
                .lte('next_review_date', today)

            const { data: mastered } = await supabase
                .from('flashcard')
                .select('id', { count: 'exact' })
                .eq('user_id', userId)
                .eq('status', 'mastered')

            return jsonResponse({
                total: total?.length || 0,
                due: due?.length || 0,
                mastered: mastered?.length || 0,
                learning: (total?.length || 0) - (mastered?.length || 0)
            })
        }

        // GET /flashcards/history - Get review history
        if (method === 'GET' && action === 'history') {
            const { data, error } = await supabase
                .from('flashcard')
                .select(`
          id, last_reviewed_at, review_count, status,
          question:question(id, content)
        `)
                .eq('user_id', userId)
                .not('last_reviewed_at', 'is', null)
                .order('last_reviewed_at', { ascending: false })
                .limit(50)

            if (error) {
                return errorResponse(error.message, 500)
            }

            return jsonResponse(data || [])
        }

        if (method === 'GET') {
            // GET /flashcards - List all flashcards
            const { data, error } = await supabase
                .from('flashcard')
                .select(`
          *,
          question:question(
            id, content, explanation,
            options:question_option(id, content, is_correct, order)
          )
        `)
                .eq('user_id', userId)
                .order('created_at', { ascending: false })

            if (error) {
                return errorResponse(error.message, 500)
            }

            return jsonResponse(data || [])
        }

        // POST /flashcards/:id/review - Review a flashcard
        if (method === 'POST' && flashcardId && action === 'review') {
            const body = await parseBody<{ rating: number }>(req)

            if (body?.rating === undefined || body.rating < 0 || body.rating > 3) {
                return errorResponse('Rating must be between 0 and 3')
            }

            // Get current flashcard state
            const { data: flashcard, error: fetchError } = await supabase
                .from('flashcard')
                .select('*')
                .eq('id', flashcardId)
                .eq('user_id', userId)
                .single()

            if (fetchError || !flashcard) {
                return errorResponse('Flashcard not found', 404)
            }

            // Calculate new SM2 values
            const sm2Result = calculateSM2(
                body.rating,
                flashcard.ease_factor,
                flashcard.interval_days,
                flashcard.repetition
            )

            // Update flashcard
            const { data, error } = await supabase
                .from('flashcard')
                .update({
                    ...sm2Result,
                    last_reviewed_at: new Date().toISOString(),
                    review_count: flashcard.review_count + 1
                })
                .eq('id', flashcardId)
                .eq('user_id', userId)
                .select()
                .single()

            if (error) {
                return errorResponse(error.message, 500)
            }

            return jsonResponse(data)
        }

        if (method === 'POST') {
            // POST /flashcards - Create flashcard(s)
            const body = await parseBody<{ question_id?: number; question_ids?: number[] }>(req)

            const questionIds = body?.question_ids || (body?.question_id ? [body.question_id] : [])

            if (questionIds.length === 0) {
                return errorResponse('question_id or question_ids is required')
            }

            const flashcardsToInsert = questionIds.map(qId => ({
                user_id: userId,
                question_id: qId,
                ease_factor: 2.5,
                interval_days: 1,
                repetition: 0,
                status: 'new',
                next_review_date: new Date().toISOString().split('T')[0],
                review_count: 0
            }))

            const { data, error } = await supabase
                .from('flashcard')
                .upsert(flashcardsToInsert, {
                    onConflict: 'user_id,question_id',
                    ignoreDuplicates: true
                })
                .select()

            if (error) {
                return errorResponse(error.message, 500)
            }

            return jsonResponse({
                success: true,
                created: data?.length || 0
            }, 201)
        }

        if (method === 'DELETE' && flashcardId) {
            // DELETE /flashcards/:id - Delete flashcard
            const { error } = await supabase
                .from('flashcard')
                .delete()
                .eq('id', flashcardId)
                .eq('user_id', userId)

            if (error) {
                return errorResponse(error.message, 500)
            }

            return new Response(null, { status: 204, headers: corsHeaders })
        }

        return errorResponse('Method not allowed', 405)

    } catch (error) {
        console.error('Unexpected error:', error)
        return errorResponse(
            error instanceof Error ? error.message : 'Internal server error',
            500
        )
    }
})
