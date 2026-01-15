import { createClient, SupabaseClient, User } from 'https://esm.sh/@supabase/supabase-js@2'

// Create Supabase client with service role for admin operations
export function createServiceClient(): SupabaseClient {
    return createClient(
        Deno.env.get('SUPABASE_URL')!,
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )
}

// Create Supabase client with user's auth token
export function createUserClient(authHeader: string | null): SupabaseClient {
    return createClient(
        Deno.env.get('SUPABASE_URL')!,
        Deno.env.get('SUPABASE_ANON_KEY')!,
        {
            global: {
                headers: authHeader ? { Authorization: authHeader } : {}
            }
        }
    )
}

// Extract and validate user from request
export async function getUser(req: Request): Promise<{ user: User | null; error: string | null }> {
    const authHeader = req.headers.get('Authorization')

    if (!authHeader) {
        return { user: null, error: 'Missing authorization header' }
    }

    const supabase = createServiceClient()
    const token = authHeader.replace('Bearer ', '')

    const { data: { user }, error } = await supabase.auth.getUser(token)

    if (error || !user) {
        return { user: null, error: error?.message || 'Invalid token' }
    }

    return { user, error: null }
}

// Require authentication - returns error response if not authenticated
export async function requireAuth(req: Request): Promise<{ user: User; error: null } | { user: null; error: Response }> {
    const { user, error } = await getUser(req)

    if (!user) {
        return {
            user: null,
            error: new Response(
                JSON.stringify({ error: error || 'Authentication required' }),
                {
                    status: 401,
                    headers: { 'Content-Type': 'application/json' }
                }
            )
        }
    }

    return { user, error: null }
}
