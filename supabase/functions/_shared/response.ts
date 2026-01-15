import { corsHeaders } from './cors.ts'

// Success response helper
export function jsonResponse(data: unknown, status = 200): Response {
    return new Response(JSON.stringify(data), {
        status,
        headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
        },
    })
}

// Error response helper
export function errorResponse(message: string, status = 400): Response {
    return new Response(JSON.stringify({ error: message }), {
        status,
        headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
        },
    })
}

// Not found response
export function notFoundResponse(message = 'Resource not found'): Response {
    return errorResponse(message, 404)
}

// Unauthorized response
export function unauthorizedResponse(message = 'Authentication required'): Response {
    return errorResponse(message, 401)
}

// Method not allowed response
export function methodNotAllowedResponse(): Response {
    return errorResponse('Method not allowed', 405)
}

// Parse JSON body safely
export async function parseBody<T>(req: Request): Promise<T | null> {
    try {
        return await req.json() as T
    } catch {
        return null
    }
}

// Parse URL parameters
export function parseParams(url: URL): Record<string, string> {
    const params: Record<string, string> = {}
    url.searchParams.forEach((value, key) => {
        params[key] = value
    })
    return params
}

// Extract ID from path like /questions/123
export function extractIdFromPath(pathname: string): string | null {
    const parts = pathname.split('/').filter(Boolean)
    const lastPart = parts[parts.length - 1]
    // Check if last part is a number
    if (lastPart && /^\d+$/.test(lastPart)) {
        return lastPart
    }
    return null
}

// Extract action from path like /questions/123/bookmark
export function extractActionFromPath(pathname: string): string | null {
    const parts = pathname.split('/').filter(Boolean)
    if (parts.length >= 3) {
        const potentialAction = parts[parts.length - 1]
        // If the last part is NOT a number, it's an action
        if (!/^\d+$/.test(potentialAction)) {
            return potentialAction
        }
    }
    return null
}
