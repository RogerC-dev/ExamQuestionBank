import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders, handleCors } from '../_shared/cors.ts'
import { jsonResponse, errorResponse, notFoundResponse, parseParams, extractIdFromPath } from '../_shared/response.ts'

serve(async (req: Request) => {
    // Handle CORS preflight
    const corsResponse = handleCors(req)
    if (corsResponse) return corsResponse

    const url = new URL(req.url)
    const method = req.method

    // Create Supabase client
    const supabase = createClient(
        Deno.env.get('SUPABASE_URL')!,
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    try {
        // Extract question ID from path if present
        const questionId = extractIdFromPath(url.pathname)

        if (method === 'GET') {
            if (questionId) {
                // GET /questions/:id - Single question with options
                const { data, error } = await supabase
                    .from('question')
                    .select(`
            *,
            options:question_option(id, content, is_correct, order),
            tags:question_tag(tag:tag(id, name))
          `)
                    .eq('id', questionId)
                    .single()

                if (error || !data) {
                    return notFoundResponse(`Question ${questionId} not found`)
                }

                // Flatten tags array
                const question = {
                    ...data,
                    tags: data.tags?.map((t: any) => t.tag) || [],
                    options: data.options || []
                }

                return jsonResponse(question)
            }

            // GET /questions - List questions with filters
            const params = parseParams(url)
            let query = supabase
                .from('question')
                .select(`
          *,
          options:question_option(id, content, is_correct, order),
          tags:question_tag(tag:tag(id, name))
        `)

            // Apply filters
            if (params.subject) {
                query = query.eq('subject', params.subject)
            }
            if (params.difficulty) {
                query = query.eq('difficulty', params.difficulty)
            }
            if (params.type) {
                query = query.eq('type', params.type)
            }
            if (params.year) {
                query = query.eq('year', parseInt(params.year))
            }
            if (params.keyword) {
                query = query.ilike('content', `%${params.keyword}%`)
            }

            // Pagination
            const page = parseInt(params.page || '1')
            const pageSize = parseInt(params.page_size || '20')
            const offset = (page - 1) * pageSize

            query = query
                .order('created_at', { ascending: false })
                .range(offset, offset + pageSize - 1)

            const { data, error, count } = await query

            if (error) {
                console.error('Query error:', error)
                return errorResponse(error.message, 500)
            }

            // Transform data to flatten tags
            const questions = data?.map((q: any) => ({
                ...q,
                tags: q.tags?.map((t: any) => t.tag) || [],
                options: q.options || []
            })) || []

            return jsonResponse({
                results: questions,
                count: count || questions.length,
                page,
                page_size: pageSize
            })
        }

        // For now, only GET is implemented
        return errorResponse('Method not allowed', 405)

    } catch (error) {
        console.error('Unexpected error:', error)
        return errorResponse(
            error instanceof Error ? error.message : 'Internal server error',
            500
        )
    }
})
