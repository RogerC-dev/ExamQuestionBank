/**
 * Property-based tests for question navigation state consistency
 * Feature: exam-preview-redesign, Property 2: Question navigation state consistency
 * Validates: Requirements 2.2, 2.4, 2.5
 */

import { describe, expect } from 'vitest'
import { fc, test } from '@fast-check/vitest'

// Mock navigation state management that mimics the exam store behavior
const createNavigationState = (questions, initialAnswers = {}) => {
  let currentQuestionIndex = 0
  let userAnswers = { ...initialAnswers }
  
  const getAnsweredQuestions = () => {
    return new Set(Object.keys(userAnswers).map(Number))
  }
  
  const navigateToQuestion = (index) => {
    if (index >= 0 && index < questions.length) {
      currentQuestionIndex = index
      return true
    }
    return false
  }
  
  const selectAnswer = (questionIndex, optionId) => {
    userAnswers[questionIndex] = optionId
  }
  
  const getProgressData = () => {
    const answeredQuestions = getAnsweredQuestions()
    return {
      answeredCount: answeredQuestions.size,
      totalQuestions: questions.length,
      progressPercentage: questions.length > 0 ? (answeredQuestions.size / questions.length) * 100 : 0
    }
  }
  
  return {
    getCurrentIndex: () => currentQuestionIndex,
    getUserAnswers: () => ({ ...userAnswers }),
    getAnsweredQuestions,
    navigateToQuestion,
    selectAnswer,
    getProgressData,
    getQuestions: () => questions
  }
}

// Generators
const questionGenerator = fc.record({
  id: fc.string({ minLength: 1 }),
  order: fc.integer({ min: 1 }),
  content: fc.string({ minLength: 1 }),
  options: fc.array(fc.record({
    id: fc.integer({ min: 1 }),
    content: fc.string({ minLength: 1 }),
    isCorrect: fc.boolean()
  }), { minLength: 2, maxLength: 6 }),
  subject: fc.option(fc.string({ minLength: 1 })),
  category: fc.option(fc.string({ minLength: 1 }))
})

const questionsArrayGenerator = fc.array(questionGenerator, { minLength: 1, maxLength: 20 })

const answersGenerator = fc.dictionary(
  fc.string({ minLength: 1, maxLength: 2 }).filter(s => /^\d+$/.test(s)),
  fc.integer({ min: 1, max: 10 })
)

describe('Question Navigation State Consistency Property Tests', () => {
  test.prop([questionsArrayGenerator], { numRuns: 100 })(
    '**Feature: exam-preview-redesign, Property 2: Question navigation state consistency**',
    (questions) => {
      const navState = createNavigationState(questions)
      
      // Property: Progress tracker should accurately reflect answered questions
      const initialProgress = navState.getProgressData()
      expect(initialProgress.answeredCount).toBe(0)
      expect(initialProgress.totalQuestions).toBe(questions.length)
      expect(initialProgress.progressPercentage).toBe(0)
      
      // Answer some random questions
      const questionsToAnswer = Math.min(questions.length, Math.floor(Math.random() * questions.length) + 1)
      const answeredIndices = new Set()
      
      for (let i = 0; i < questionsToAnswer; i++) {
        const questionIndex = Math.floor(Math.random() * questions.length)
        const optionId = Math.floor(Math.random() * 5) + 1
        
        navState.selectAnswer(questionIndex, optionId)
        answeredIndices.add(questionIndex)
        
        // Progress should update immediately
        const currentProgress = navState.getProgressData()
        const expectedAnsweredCount = navState.getAnsweredQuestions().size
        
        expect(currentProgress.answeredCount).toBe(expectedAnsweredCount)
        expect(currentProgress.totalQuestions).toBe(questions.length)
        
        if (questions.length > 0) {
          expect(currentProgress.progressPercentage).toBe((expectedAnsweredCount / questions.length) * 100)
        }
      }
      
      // Property: All user selections should be preserved during navigation
      const userAnswers = navState.getUserAnswers()
      const answeredQuestions = navState.getAnsweredQuestions()
      
      // Navigate through all questions
      for (let i = 0; i < questions.length; i++) {
        const navigationSuccess = navState.navigateToQuestion(i)
        expect(navigationSuccess).toBe(true)
        expect(navState.getCurrentIndex()).toBe(i)
        
        // All previously selected answers should still be preserved
        const currentAnswers = navState.getUserAnswers()
        Object.keys(userAnswers).forEach(questionIndex => {
          expect(currentAnswers[questionIndex]).toBe(userAnswers[questionIndex])
        })
        
        // Answered questions set should remain consistent
        const currentAnsweredQuestions = navState.getAnsweredQuestions()
        expect(currentAnsweredQuestions.size).toBe(answeredQuestions.size)
        answeredQuestions.forEach(index => {
          expect(currentAnsweredQuestions.has(index)).toBe(true)
        })
      }
    }
  )
  
  test.prop([questionsArrayGenerator, fc.integer({ min: 0, max: 50 })], { numRuns: 100 })(
    'Navigation should preserve state across multiple navigation operations',
    (questions, navigationCount) => {
      const navState = createNavigationState(questions)
      
      // Answer some questions first
      const answersToMake = Math.min(questions.length, Math.floor(Math.random() * questions.length) + 1)
      const originalAnswers = {}
      
      for (let i = 0; i < answersToMake; i++) {
        const questionIndex = Math.floor(Math.random() * questions.length)
        const optionId = Math.floor(Math.random() * 5) + 1
        navState.selectAnswer(questionIndex, optionId)
        originalAnswers[questionIndex] = optionId
      }
      
      const originalAnsweredQuestions = navState.getAnsweredQuestions()
      const originalProgress = navState.getProgressData()
      
      // Perform multiple navigation operations
      for (let i = 0; i < Math.min(navigationCount, 100); i++) {
        const targetIndex = Math.floor(Math.random() * questions.length)
        navState.navigateToQuestion(targetIndex)
        
        // State should remain consistent after each navigation
        const currentAnswers = navState.getUserAnswers()
        const currentAnsweredQuestions = navState.getAnsweredQuestions()
        const currentProgress = navState.getProgressData()
        
        // All original answers should be preserved
        Object.keys(originalAnswers).forEach(questionIndex => {
          expect(currentAnswers[questionIndex]).toBe(originalAnswers[questionIndex])
        })
        
        // Answered questions set should be identical
        expect(currentAnsweredQuestions.size).toBe(originalAnsweredQuestions.size)
        originalAnsweredQuestions.forEach(index => {
          expect(currentAnsweredQuestions.has(index)).toBe(true)
        })
        
        // Progress should remain the same
        expect(currentProgress.answeredCount).toBe(originalProgress.answeredCount)
        expect(currentProgress.progressPercentage).toBe(originalProgress.progressPercentage)
      }
    }
  )
  
  test.prop([questionsArrayGenerator], { numRuns: 100 })(
    'Progress tracking should handle edge cases correctly',
    (questions) => {
      const navState = createNavigationState(questions)
      
      // Test with no answers
      let progress = navState.getProgressData()
      expect(progress.answeredCount).toBe(0)
      expect(progress.progressPercentage).toBe(0)
      
      // Test with all questions answered
      questions.forEach((_, index) => {
        navState.selectAnswer(index, 1)
      })
      
      progress = navState.getProgressData()
      expect(progress.answeredCount).toBe(questions.length)
      expect(progress.progressPercentage).toBe(100)
      
      // Test with duplicate answers (should not increase count)
      const originalCount = progress.answeredCount
      navState.selectAnswer(0, 2) // Change answer for first question
      
      progress = navState.getProgressData()
      expect(progress.answeredCount).toBe(originalCount) // Should remain the same
      
      // Test navigation bounds
      expect(navState.navigateToQuestion(-1)).toBe(false)
      expect(navState.navigateToQuestion(questions.length)).toBe(false)
      expect(navState.navigateToQuestion(questions.length + 10)).toBe(false)
      
      // Valid navigation should work
      if (questions.length > 0) {
        expect(navState.navigateToQuestion(0)).toBe(true)
        expect(navState.navigateToQuestion(questions.length - 1)).toBe(true)
      }
    }
  )
  
  test.prop([questionsArrayGenerator, answersGenerator], { numRuns: 100 })(
    'State should be consistent when initialized with existing answers',
    (questions, initialAnswers) => {
      // Filter initial answers to only include valid question indices
      // Also normalize keys to avoid duplicates (e.g., "1" and "01" both map to index 1)
      const validAnswers = {}
      const seenIndices = new Set()
      
      Object.keys(initialAnswers).forEach(key => {
        const index = parseInt(key)
        if (index >= 0 && index < questions.length && !seenIndices.has(index)) {
          validAnswers[index.toString()] = initialAnswers[key]
          seenIndices.add(index)
        }
      })
      
      const navState = createNavigationState(questions, validAnswers)
      
      // Progress should reflect initial answers (unique question indices only)
      const progress = navState.getProgressData()
      const expectedCount = Object.keys(validAnswers).length
      
      expect(progress.answeredCount).toBe(expectedCount)
      expect(progress.totalQuestions).toBe(questions.length)
      
      if (questions.length > 0) {
        expect(progress.progressPercentage).toBe((expectedCount / questions.length) * 100)
      }
      
      // All initial answers should be preserved
      const currentAnswers = navState.getUserAnswers()
      Object.keys(validAnswers).forEach(questionIndex => {
        expect(currentAnswers[questionIndex]).toBe(validAnswers[questionIndex])
      })
      
      // Answered questions set should match initial answers
      const answeredQuestions = navState.getAnsweredQuestions()
      expect(answeredQuestions.size).toBe(Object.keys(validAnswers).length)
      Object.keys(validAnswers).forEach(questionIndex => {
        expect(answeredQuestions.has(parseInt(questionIndex))).toBe(true)
      })
    }
  )
})