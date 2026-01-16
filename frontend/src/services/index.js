/**
 * Service Index - Automatic backend switching
 * Uses VITE_USE_SUPABASE env variable to determine backend
 * 
 * Import from here instead of individual services:
 * import { questionService, examService } from '@/services'
 */

const USE_SUPABASE = import.meta.env.VITE_USE_SUPABASE === 'true'

// Conditional exports based on backend
let questionService, examService, flashcardService, tagService, authService

if (USE_SUPABASE) {
    // Supabase services (RPC functions)
    questionService = (await import('./questionServiceSupabase.js')).default
    examService = (await import('./examServiceSupabase.js')).default
    flashcardService = (await import('./flashcardServiceSupabase.js')).default
    tagService = (await import('./tagServiceSupabase.js')).default
    authService = (await import('./authServiceSupabase.js')).default
} else {
    // Django services (original)
    questionService = (await import('./questionService.js')).default
    examService = (await import('./examService.js')).default
    flashcardService = (await import('./flashcardService.js')).default
    tagService = (await import('./tagService.js')).default
    authService = (await import('./authService.js')).default
}

export {
    questionService,
    examService,
    flashcardService,
    tagService,
    authService
}

// Also export the USE_SUPABASE flag for components that need to know
export { USE_SUPABASE }
