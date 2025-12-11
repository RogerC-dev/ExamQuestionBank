/**
 * TypeScript interfaces for flashcard-related data structures
 * Based on requirements 1.1, 2.1, 3.1, 4.1
 */

/**
 * Represents a single flashcard linked to a question
 */
export interface Flashcard {
  id: number
  question: number
  question_content: string
  question_subject: string
  status: 'learning' | 'reviewing' | 'mastered'
  ease_factor: number
  interval: number
  repetition: number
  next_review_date: string
  last_reviewed_at: string | null
  review_count: number
  created_at: string
}

/**
 * Represents an answer option for a question
 */
export interface QuestionOption {
  id: number
  content: string
  order: number
  is_correct: boolean
}

/**
 * Represents flashcard statistics for the dashboard
 */
export interface FlashcardStats {
  total_cards: number
  due_cards: number
  completion_percent: number
  review_streak: number
}

/**
 * Error state for UI error handling
 */
export interface ErrorState {
  message: string
  retryAction?: () => void
  dismissable: boolean
}

/**
 * Status filter options for card list
 */
export type StatusFilter = 'all' | 'learning' | 'reviewing' | 'mastered'
