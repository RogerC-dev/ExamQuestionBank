/**
 * Service Index - Django Backend Configuration
 * 
 * This file is for the main branch (Django backend).
 * Import from here instead of individual services:
 * import { questionService, examService } from '@/config/main/services'
 */

// Django services (original)
import questionService from '@/services/questionService'
import examService from '@/services/examService'
import flashcardService from '@/services/flashcardService'
import tagService from '@/services/tagService'
import authService from '@/services/authService'

export {
    questionService,
    examService,
    flashcardService,
    tagService,
    authService
}

// Export USE_SUPABASE flag (always false for Django)
export const USE_SUPABASE = false
