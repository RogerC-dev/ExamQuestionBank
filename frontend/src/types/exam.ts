/**
 * TypeScript interfaces for exam-related data structures
 * Based on requirements 1.1, 1.2, 5.1, 5.2
 */

export interface QuestionOption {
  id: number
  content: string
  isCorrect: boolean
}

export interface ExamQuestion {
  id: string
  order: number
  content: string
  options: QuestionOption[]
  subject?: string
  category?: string
  points?: number
}

export interface ExamSettings {
  allowReview: boolean
  showResults: boolean
  randomizeQuestions: boolean
  randomizeOptions: boolean
}

export interface Exam {
  id: string
  name: string
  description?: string
  timeLimit?: number // in minutes
  questions: ExamQuestion[]
  settings: ExamSettings
}

export interface QuestionResult {
  questionId: string
  question: string
  userAnswer: string | null
  correctAnswer: string
  isCorrect: boolean
  timeSpent?: number // in seconds
}

export interface ExamResults {
  examId: string
  score: number
  correctCount: number
  totalCount: number
  percentage: number
  duration: number // in seconds
  details: QuestionResult[]
  wrongQuestionIds: string[]
}

export interface ExamState {
  exam: Exam | null
  currentQuestionIndex: number
  userAnswers: Record<number, number>
  timeLeft: number
  isActive: boolean
  isLoading: boolean
  error: string | null
  results: ExamResults | null
}

export interface ExamActions {
  loadExam(id: string): Promise<void>
  startExam(): void
  selectAnswer(questionIndex: number, optionId: number): void
  navigateToQuestion(index: number): void
  submitExam(): Promise<void>
  resetExam(): void
  restoreFromStorage(): void
}

// Component prop interfaces
export interface TimerProps {
  timeLimit: number // in seconds
  onTimeExpired: () => void
}

export interface TimerEmits {
  'time-warning': (timeLeft: number) => void
  'time-critical': (timeLeft: number) => void
  'time-expired': () => void
}

export interface NavigatorProps {
  questions: ExamQuestion[]
  currentIndex: number
  answeredQuestions: Set<number>
}

export interface NavigatorEmits {
  'navigate-to': (index: number) => void
}

// Error handling interfaces
export type ErrorType = 'network' | 'data' | 'state' | 'user'

export interface ErrorState {
  type: ErrorType
  message: string
  recoverable: boolean
  retryAction?: () => void
}

// Validation types for form inputs
export interface ExamValidation {
  isValid: boolean
  errors: {
    name?: string
    description?: string
    timeLimit?: string
    questions?: string
  }
}

export interface QuestionValidation {
  isValid: boolean
  errors: {
    content?: string
    options?: string
    correctAnswer?: string
  }
}