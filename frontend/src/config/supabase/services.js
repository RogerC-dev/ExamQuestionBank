/**
 * Service Index - Supabase Backend Configuration
 * 
 * This file is for the Supabase branch.
 * Import from here instead of individual services:
 * import { questionService, examService } from '@/config/supabase/services'
 */

// Supabase services (RPC functions)
import questionService from '@/services/questionServiceSupabase'
import examService from '@/services/examServiceSupabase'
import flashcardService from '@/services/flashcardServiceSupabase'
import tagService from '@/services/tagServiceSupabase'
import authService from '@/services/authServiceSupabase'

export {
    questionService,
    examService,
    flashcardService,
    tagService,
    authService
}

// Export USE_SUPABASE flag (always true for Supabase)
export const USE_SUPABASE = true
