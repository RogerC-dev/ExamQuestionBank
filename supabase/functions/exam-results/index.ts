import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders, handleCors } from '../_shared/cors.ts'
import { jsonResponse, errorResponse, parseBody } from '../_shared/response.ts'
import { requireAuth } from '../_shared/auth.ts'

serve(async (req: Request) => {
    // Handle CORS preflight
    const corsResponse = handleCors(req)
    if (corsResponse) return corsResponse

    // All operations require authentication
    const auth = await requireAuth(req)
    if (auth.error) return auth.error
    const userId = auth.user.id

    const method = req.method

    // Create Supabase client
    const supabase = createClient(
        Deno.env.get('SUPABASE_URL')!,
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    try {
        if (method === 'GET') {
            // GET /exam-results - Get user's exam results
            const { data, error } = await supabase
                .from('exam_result')
                .select('*')
                .eq('user_id', userId)
                .order('completed_at', { ascending: false })

            if (error) {
                return errorResponse(error.message, 500)
            }

            return jsonResponse(data || [])
        }

        if (method === 'POST') {
            // POST /exam-results - Save exam result
            const body = await parseBody<{
                exam_id?: number
                exam_name: string
                score: number
                correct_count: number
                total_count: number
                duration_seconds?: number
                answers_json?: Record<string, any>
                wrong_question_ids?: number[]
            }>(req)

            if (!body?.exam_name || body?.score === undefined) {
                return errorResponse('exam_name and score are required')
            }

            // Save exam result
            const { data: result, error } = await supabase
                .from('exam_result')
                .insert({
                    user_id: userId,
                    exam_id: body.exam_id,
                    exam_name: body.exam_name,
                    score: body.score,
                    correct_count: body.correct_count,
                    total_count: body.total_count,
                    duration_seconds: body.duration_seconds,
                    answers_json: body.answers_json
                })
                .select()
                .single()

            if (error) {
                return errorResponse(error.message, 500)
            }

            // Track wrong questions if provided
            if (body.wrong_question_ids?.length) {
                const wrongQuestions = body.wrong_question_ids.map(qId => ({
                    user_id: userId,
                    question_id: qId,
                    wrong_count: 1,
                    reviewed: false
                }))

                // Upsert wrong questions (increment count if exists)
                for (const wq of wrongQuestions) {
                    const { data: existing } = await supabase
                        .from('wrong_question')
                        .select('id, wrong_count')
                        .eq('user_id', userId)
                        .eq('question_id', wq.question_id)
                        .single()

                    if (existing) {
                        await supabase
                            .from('wrong_question')
                            .update({
                                wrong_count: existing.wrong_count + 1,
                                last_wrong_at: new Date().toISOString(),
                                reviewed: false
                            })
                            .eq('id', existing.id)
                    } else {
                        await supabase.from('wrong_question').insert(wq)
                    }
                }
            }

            return jsonResponse(result, 201)
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
