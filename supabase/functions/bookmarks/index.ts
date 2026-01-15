import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders, handleCors } from '../_shared/cors.ts'
import { jsonResponse, errorResponse, extractIdFromPath, parseBody } from '../_shared/response.ts'
import { requireAuth } from '../_shared/auth.ts'

serve(async (req: Request) => {
    // Handle CORS preflight
    const corsResponse = handleCors(req)
    if (corsResponse) return corsResponse

    // All bookmark operations require authentication
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
        const questionId = extractIdFromPath(url.pathname)

        if (method === 'GET') {
            // GET /bookmarks - Get user's bookmarked questions
            const { data, error } = await supabase
                .from('bookmark')
                .select(`
          question_id,
          created_at,
          question:question(
            id, content, type, difficulty, subject, category, year,
            options:question_option(id, content, is_correct, order)
          )
        `)
                .eq('user_id', userId)
                .order('created_at', { ascending: false })

            if (error) {
                return errorResponse(error.message, 500)
            }

            // Flatten to just return questions with bookmark info
            const bookmarks = data?.map((b: any) => ({
                ...b.question,
                bookmarked_at: b.created_at
            })) || []

            return jsonResponse(bookmarks)
        }

        if (method === 'POST') {
            // POST /bookmarks - Add bookmark(s)
            const body = await parseBody<{ question_ids: number[] }>(req)

            if (!body?.question_ids || !Array.isArray(body.question_ids)) {
                return errorResponse('question_ids array is required')
            }

            // Insert bookmarks (ignore duplicates)
            const bookmarksToInsert = body.question_ids.map(qId => ({
                user_id: userId,
                question_id: qId
            }))

            const { data, error } = await supabase
                .from('bookmark')
                .upsert(bookmarksToInsert, {
                    onConflict: 'user_id,question_id',
                    ignoreDuplicates: true
                })
                .select()

            if (error) {
                return errorResponse(error.message, 500)
            }

            return jsonResponse({
                success: true,
                added_count: body.question_ids.length
            }, 201)
        }

        if (method === 'DELETE' && questionId) {
            // DELETE /bookmarks/:questionId - Remove bookmark
            const { error } = await supabase
                .from('bookmark')
                .delete()
                .eq('user_id', userId)
                .eq('question_id', questionId)

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
