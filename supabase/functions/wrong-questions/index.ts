import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders, handleCors } from '../_shared/cors.ts'
import { jsonResponse, errorResponse, extractIdFromPath, parseBody } from '../_shared/response.ts'
import { requireAuth } from '../_shared/auth.ts'

serve(async (req: Request) => {
    // Handle CORS preflight
    const corsResponse = handleCors(req)
    if (corsResponse) return corsResponse

    // All operations require authentication
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
        const wrongQuestionId = extractIdFromPath(url.pathname)

        if (method === 'GET') {
            // GET /wrong-questions - Get user's wrong questions
            const { data, error } = await supabase
                .from('wrong_question')
                .select(`
          *,
          question:question(
            id, content, type, difficulty, subject, category,
            options:question_option(id, content, is_correct, order)
          )
        `)
                .eq('user_id', userId)
                .order('wrong_count', { ascending: false })

            if (error) {
                return errorResponse(error.message, 500)
            }

            // Flatten question data
            const wrongQuestions = data?.map((wq: any) => ({
                id: wq.id,
                wrong_count: wq.wrong_count,
                last_wrong_at: wq.last_wrong_at,
                reviewed: wq.reviewed,
                ...wq.question
            })) || []

            return jsonResponse(wrongQuestions)
        }

        if (method === 'PATCH' && wrongQuestionId) {
            // PATCH /wrong-questions/:id - Update (mark as reviewed)
            const body = await parseBody<{ reviewed?: boolean }>(req)

            const { data, error } = await supabase
                .from('wrong_question')
                .update({ reviewed: body?.reviewed ?? true })
                .eq('id', wrongQuestionId)
                .eq('user_id', userId)
                .select()
                .single()

            if (error || !data) {
                return errorResponse('Wrong question not found', 404)
            }

            return jsonResponse(data)
        }

        if (method === 'DELETE' && wrongQuestionId) {
            // DELETE /wrong-questions/:id - Delete wrong question record
            const { error } = await supabase
                .from('wrong_question')
                .delete()
                .eq('id', wrongQuestionId)
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
