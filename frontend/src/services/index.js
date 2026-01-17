/**
 * Service Index - Main Branch (Django Backend)
 * 
 * This file automatically imports from config/main/ for the main branch.
 * For Supabase branch, this file should import from config/supabase/
 * 
 * Import from here instead of individual services:
 * import { questionService, examService } from '@/services'
 */

// Import from main branch configuration (Django)
export * from '@/config/main/services'
