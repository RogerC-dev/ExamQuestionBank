import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useExamStore } from '@/stores/examStore'

describe('ExamStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should initialize with default state', () => {
    const store = useExamStore()
    
    expect(store.exam).toBe(null)
    expect(store.currentQuestionIndex).toBe(0)
    expect(store.userAnswers).toEqual({})
    expect(store.timeLeft).toBe(0)
    expect(store.isActive).toBe(false)
    expect(store.isLoading).toBe(false)
    expect(store.error).toBe(null)
    expect(store.results).toBe(null)
  })

  it('should calculate total questions correctly', () => {
    const store = useExamStore()
    
    // Initially should be 0
    expect(store.totalQuestions).toBe(0)
    
    // Set exam with questions
    store.exam = {
      id: '1',
      name: 'Test Exam',
      questions: [
        { id: '1', content: 'Question 1' },
        { id: '2', content: 'Question 2' }
      ]
    }
    
    expect(store.totalQuestions).toBe(2)
  })

  it('should track answered questions', () => {
    const store = useExamStore()
    
    // Set up exam and start it
    store.exam = {
      id: '1',
      name: 'Test Exam',
      questions: [
        { id: '1', content: 'Question 1' },
        { id: '2', content: 'Question 2' },
        { id: '3', content: 'Question 3' }
      ]
    }
    store.startExam()
    
    // Initially no answered questions
    expect(store.answeredQuestions.size).toBe(0)
    
    // Answer some questions
    store.selectAnswer(0, 1)
    store.selectAnswer(2, 3)
    
    expect(store.answeredQuestions.size).toBe(2)
    expect(store.answeredQuestions.has(0)).toBe(true)
    expect(store.answeredQuestions.has(2)).toBe(true)
    expect(store.answeredQuestions.has(1)).toBe(false)
  })

  it('should calculate progress correctly', () => {
    const store = useExamStore()
    
    // Set exam with 4 questions
    store.exam = {
      id: '1',
      name: 'Test Exam',
      questions: [
        { id: '1', content: 'Question 1' },
        { id: '2', content: 'Question 2' },
        { id: '3', content: 'Question 3' },
        { id: '4', content: 'Question 4' }
      ]
    }
    store.startExam()
    
    // Initially 0% progress
    expect(store.progress).toBe(0)
    
    // Answer 2 questions = 50% progress
    store.selectAnswer(0, 1)
    store.selectAnswer(1, 2)
    expect(store.progress).toBe(50)
    
    // Answer all questions = 100% progress
    store.selectAnswer(2, 3)
    store.selectAnswer(3, 4)
    expect(store.progress).toBe(100)
  })
})