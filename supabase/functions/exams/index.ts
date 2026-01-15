import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders, handleCors } from '../_shared/cors.ts'
import { jsonResponse, errorResponse, notFoundResponse, extractIdFromPath, extractActionFromPath, parseBody, parseParams } from '../_shared/response.ts'
import { requireAuth, getUser } from '../_shared/auth.ts'

serve(async (req: Request) => {
    // Handle CORS preflight
    const corsResponse = handleCors(req)
    if (corsResponse) return corsResponse

    const url = new URL(req.url)
    const method = req.method
    const params = parseParams(url)

    // Create Supabase client
    const supabase = createClient(
        Deno.env.get('SUPABASE_URL')!,
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    try {
        const examId = extractIdFromPath(url.pathname)
        const action = extractActionFromPath(url.pathname)

        // GET /exams/practice-list - Get practice exams (public published + user's own)
        if (method === 'GET' && action === 'practice-list') {
            const { user } = await getUser(req)

            let query = supabase
                .from('exam')
                .select(`
          id, name, description, time_limit, publish, created_at,
          question_count:exam_question(count)
        `)

            if (user) {
                // User sees their own + published
                query = query.or(`creator.eq.${user.id},publish.eq.true`)
            } else {
                // Anonymous only sees published
                query = query.eq('publish', true)
            }

            const { data, error } = await query.order('created_at', { ascending: false })

            if (error) {
                return errorResponse(error.message, 500)
            }

            // Transform to include question count
            const exams = data?.map((e: any) => ({
                ...e,
                question_count: e.question_count?.[0]?.count || 0
            })) || []

            return jsonResponse(exams)
        }

        if (method === 'GET') {
            if (examId) {
                // GET /exams/:id - Single exam with questions
                const { data, error } = await supabase
                    .from('exam')
                    .select(`
            *,
            questions:exam_question(
              id, order, points,
              question:question(
                id, content, type, difficulty, explanation,
                options:question_option(id, content, is_correct, order)
              )
            )
          `)
                    .eq('id', examId)
                    .single()

                if (error || !data) {
                    return notFoundResponse(`Exam ${examId} not found`)
                }

                // Check access - must be published or user's own
                const { user } = await getUser(req)
                if (!data.publish && (!user || data.creator !== user.id)) {
                    return errorResponse('Access denied', 403)
                }

                // Flatten questions
                const exam = {
                    ...data,
                    questions: data.questions
                        ?.sort((a: any, b: any) => a.order - b.order)
                        .map((eq: any) => ({
                            exam_question_id: eq.id,
                            order: eq.order,
                            points: eq.points,
                            ...eq.question
                        })) || []
                }

                return jsonResponse(exam)
            }

            // GET /exams - List user's exams (requires auth)
            const auth = await requireAuth(req)
            if (auth.error) return auth.error

            const { data, error } = await supabase
                .from('exam')
                .select(`
          id, name, description, time_limit, publish, created_at,
          question_count:exam_question(count)
        `)
                .eq('creator', auth.user.id)
                .order('created_at', { ascending: false })

            if (error) {
                return errorResponse(error.message, 500)
            }

            const exams = data?.map((e: any) => ({
                ...e,
                question_count: e.question_count?.[0]?.count || 0
            })) || []

            return jsonResponse(exams)
        }

        if (method === 'POST') {
            const auth = await requireAuth(req)
            if (auth.error) return auth.error

            // POST /exams/:id/add_question - Add question to exam
            if (examId && action === 'add_question') {
                const body = await parseBody<{ question_id: number; order?: number; points?: number }>(req)

                if (!body?.question_id) {
                    return errorResponse('question_id is required')
                }

                // Verify exam ownership
                const { data: exam } = await supabase
                    .from('exam')
                    .select('id')
                    .eq('id', examId)
                    .eq('creator', auth.user.id)
                    .single()

                if (!exam) {
                    return errorResponse('Exam not found or access denied', 404)
                }

                // Get next order if not specified
                let order = body.order
                if (!order) {
                    const { data: maxOrder } = await supabase
                        .from('exam_question')
                        .select('order')
                        .eq('exam_id', examId)
                        .order('order', { ascending: false })
                        .limit(1)
                        .single()

                    order = (maxOrder?.order || 0) + 1
                }

                const { data, error } = await supabase
                    .from('exam_question')
                    .insert({
                        exam_id: parseInt(examId),
                        question_id: body.question_id,
                        order,
                        points: body.points || 1
                    })
                    .select()
                    .single()

                if (error) {
                    if (error.code === '23505') {
                        return errorResponse('Question already in exam', 409)
                    }
                    return errorResponse(error.message, 500)
                }

                return jsonResponse(data, 201)
            }

            // POST /exams/custom - Create custom exam from question IDs
            if (action === 'custom') {
                const body = await parseBody<{ name: string; question_ids: number[]; time_limit?: number }>(req)

                if (!body?.name || !body?.question_ids?.length) {
                    return errorResponse('name and question_ids are required')
                }

                // Create exam
                const { data: exam, error: examError } = await supabase
                    .from('exam')
                    .insert({
                        name: body.name,
                        time_limit: body.time_limit || 60,
                        creator: auth.user.id,
                        publish: false
                    })
                    .select()
                    .single()

                if (examError) {
                    return errorResponse(examError.message, 500)
                }

                // Add questions
                const examQuestions = body.question_ids.map((qId, idx) => ({
                    exam_id: exam.id,
                    question_id: qId,
                    order: idx + 1,
                    points: 1
                }))

                await supabase.from('exam_question').insert(examQuestions)

                return jsonResponse(exam, 201)
            }

            // POST /exams - Create exam
            const body = await parseBody<{ name: string; description?: string; time_limit?: number }>(req)

            if (!body?.name) {
                return errorResponse('Exam name is required')
            }

            const { data, error } = await supabase
                .from('exam')
                .insert({
                    name: body.name,
                    description: body.description,
                    time_limit: body.time_limit || 60,
                    creator: auth.user.id,
                    publish: false
                })
                .select()
                .single()

            if (error) {
                return errorResponse(error.message, 500)
            }

            return jsonResponse(data, 201)
        }

        if (method === 'PATCH' && examId) {
            const auth = await requireAuth(req)
            if (auth.error) return auth.error

            const body = await parseBody<{ name?: string; description?: string; time_limit?: number; publish?: boolean }>(req)

            const { data, error } = await supabase
                .from('exam')
                .update(body || {})
                .eq('id', examId)
                .eq('creator', auth.user.id)
                .select()
                .single()

            if (error || !data) {
                return notFoundResponse('Exam not found or access denied')
            }

            return jsonResponse(data)
        }

        if (method === 'DELETE') {
            const auth = await requireAuth(req)
            if (auth.error) return auth.error

            // DELETE /exams/:examId/remove_question?exam_question_id=X
            if (examId && action === 'remove_question') {
                const eqId = params.exam_question_id
                if (!eqId) {
                    return errorResponse('exam_question_id query param is required')
                }

                // Verify ownership
                const { data: eq } = await supabase
                    .from('exam_question')
                    .select('exam:exam(creator)')
                    .eq('id', eqId)
                    .single()

                if (!eq || (eq as any).exam?.creator !== auth.user.id) {
                    return errorResponse('Not found or access denied', 404)
                }

                await supabase.from('exam_question').delete().eq('id', eqId)
                return new Response(null, { status: 204, headers: corsHeaders })
            }

            // DELETE /exams/:id - Delete exam
            if (examId) {
                const { error } = await supabase
                    .from('exam')
                    .delete()
                    .eq('id', examId)
                    .eq('creator', auth.user.id)

                if (error) {
                    return errorResponse(error.message, 500)
                }

                return new Response(null, { status: 204, headers: corsHeaders })
            }
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
