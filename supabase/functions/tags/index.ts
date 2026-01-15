import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { corsHeaders, handleCors } from '../_shared/cors.ts'
import { jsonResponse, errorResponse, notFoundResponse, parseParams, extractIdFromPath, parseBody } from '../_shared/response.ts'
import { requireAuth } from '../_shared/auth.ts'

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
        const tagId = extractIdFromPath(url.pathname)

        if (method === 'GET') {
            // GET /tags - List all tags
            const params = parseParams(url)
            let query = supabase.from('tag').select('*')

            if (params.category) {
                query = query.eq('category', params.category)
            }
            if (params.search) {
                query = query.ilike('name', `%${params.search}%`)
            }

            query = query.order('name')

            const { data, error } = await query

            if (error) {
                return errorResponse(error.message, 500)
            }

            return jsonResponse(data || [])
        }

        if (method === 'POST') {
            // POST /tags - Create tag (requires auth)
            const auth = await requireAuth(req)
            if (auth.error) return auth.error

            const body = await parseBody<{ name: string; category?: string }>(req)
            if (!body?.name) {
                return errorResponse('Tag name is required')
            }

            const { data, error } = await supabase
                .from('tag')
                .insert({ name: body.name, category: body.category })
                .select()
                .single()

            if (error) {
                if (error.code === '23505') { // Unique violation
                    return errorResponse('Tag already exists', 409)
                }
                return errorResponse(error.message, 500)
            }

            return jsonResponse(data, 201)
        }

        if (method === 'PATCH' && tagId) {
            // PATCH /tags/:id - Update tag (requires auth)
            const auth = await requireAuth(req)
            if (auth.error) return auth.error

            const body = await parseBody<{ name?: string; category?: string }>(req)
            if (!body) {
                return errorResponse('Request body is required')
            }

            const { data, error } = await supabase
                .from('tag')
                .update(body)
                .eq('id', tagId)
                .select()
                .single()

            if (error) {
                return errorResponse(error.message, 500)
            }

            if (!data) {
                return notFoundResponse(`Tag ${tagId} not found`)
            }

            return jsonResponse(data)
        }

        if (method === 'DELETE' && tagId) {
            // DELETE /tags/:id - Delete tag (requires auth)
            const auth = await requireAuth(req)
            if (auth.error) return auth.error

            const { error } = await supabase
                .from('tag')
                .delete()
                .eq('id', tagId)

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
