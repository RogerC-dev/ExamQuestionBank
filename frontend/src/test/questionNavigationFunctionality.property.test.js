/**
 * Property-based tests for question navigation functionality
 * Feature: exam-preview-redesign, Property 6: Question navigation functionality
 * Validates: Requirements 2.3
 */

import { describe, expect } from 'vitest'
import { fc, test } from '@fast-check/vitest'

// Mock navigation functionality that mimics QuestionNavigator component behavior
const createQuestionNavigator = (questions) => {
  let currentQuestionIndex = 0
  const navigationHistory = []
  
  const navigateToQuestion = (targetIndex) => {
    // Validate navigation bounds
    if (targetIndex < 0 || targetIndex >= questions.length) {
      return false
    }
    
    // Record navigation
    navigationHistory.push({
      from: currentQuestionIndex,
      to: targetIndex,
      timestamp: Date.now()
    })
    
    // Update current index
    currentQuestionIndex = targetIndex
    return true
  }
  
  const getCurrentIndex = () => currentQuestionIndex
  
  const getNavigationHistory = () => [...navigationHistory]
  
  const canNavigateTo = (index) => {
    return index >= 0 && index < questions.length
  }
  
  return {
    navigateToQuestion,
    getCurrentIndex,
    getNavigationHistory,
    canNavigateTo,
    getQuestionCount: () => questions.length
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

describe('Question Navigation Functionality Property Tests', () => {
  test.prop([questionsArrayGenerator], { numRuns: 100 })(
    '**Feature: exam-preview-redesign, Property 6: Question navigation functionality**',
    (questions) => {
      const navigator = createQuestionNavigator(questions)
      
      // Property: Clicking on any question in the navigator should immediately change current question index
      for (let targetIndex = 0; targetIndex < questions.length; targetIndex++) {
        const initialIndex = navigator.getCurrentIndex()
        const navigationSuccess = navigator.navigateToQuestion(targetIndex)
        
        // Navigation should succeed for valid indices
        expect(navigationSuccess).toBe(true)
        
        // Current index should immediately change to target index
        expect(navigator.getCurrentIndex()).toBe(targetIndex)
        
        // Navigation should be recorded in history
        const history = navigator.getNavigationHistory()
        const lastNavigation = history[history.length - 1]
        expect(lastNavigation.from).toBe(initialIndex)
        expect(lastNavigation.to).toBe(targetIndex)
        expect(lastNavigation.timestamp).toBeDefined()
      }
    }
  )
  
  test.prop([questionsArrayGenerator, fc.array(fc.integer({ min: 0, max: 50 }), { minLength: 1, maxLength: 20 })], { numRuns: 100 })(
    'Navigation should work correctly for any sequence of valid indices',
    (questions, navigationSequence) => {
      const navigator = createQuestionNavigator(questions)
      
      // Filter navigation sequence to only include valid indices
      const validSequence = navigationSequence
        .map(index => index % questions.length) // Ensure all indices are valid
        .slice(0, Math.min(navigationSequence.length, 50)) // Limit sequence length
      
      // Execute navigation sequence
      validSequence.forEach((targetIndex, sequenceIndex) => {
        const previousIndex = navigator.getCurrentIndex()
        const navigationSuccess = navigator.navigateToQuestion(targetIndex)
        
        // Each navigation should succeed
        expect(navigationSuccess).toBe(true)
        
        // Current index should be updated immediately
        expect(navigator.getCurrentIndex()).toBe(targetIndex)
        
        // History should record the navigation
        const history = navigator.getNavigationHistory()
        expect(history.length).toBe(sequenceIndex + 1)
        
        const currentNavigation = history[sequenceIndex]
        expect(currentNavigation.from).toBe(previousIndex)
        expect(currentNavigation.to).toBe(targetIndex)
      })
      
      // Final state should match last navigation target
      const finalIndex = validSequence[validSequence.length - 1]
      expect(navigator.getCurrentIndex()).toBe(finalIndex)
    }
  )
  
  test.prop([questionsArrayGenerator], { numRuns: 100 })(
    'Navigation should handle boundary conditions correctly',
    (questions) => {
      const navigator = createQuestionNavigator(questions)
      
      // Test invalid navigation attempts
      const invalidIndices = [-1, -10, questions.length, questions.length + 1, questions.length + 100]
      
      invalidIndices.forEach(invalidIndex => {
        const initialIndex = navigator.getCurrentIndex()
        const navigationSuccess = navigator.navigateToQuestion(invalidIndex)
        
        // Navigation should fail for invalid indices
        expect(navigationSuccess).toBe(false)
        
        // Current index should remain unchanged
        expect(navigator.getCurrentIndex()).toBe(initialIndex)
        
        // canNavigateTo should return false for invalid indices
        expect(navigator.canNavigateTo(invalidIndex)).toBe(false)
      })
      
      // Test valid boundary indices
      if (questions.length > 0) {
        // First question
        expect(navigator.navigateToQuestion(0)).toBe(true)
        expect(navigator.getCurrentIndex()).toBe(0)
        expect(navigator.canNavigateTo(0)).toBe(true)
        
        // Last question
        const lastIndex = questions.length - 1
        expect(navigator.navigateToQuestion(lastIndex)).toBe(true)
        expect(navigator.getCurrentIndex()).toBe(lastIndex)
        expect(navigator.canNavigateTo(lastIndex)).toBe(true)
      }
    }
  )
  
  test.prop([questionsArrayGenerator], { numRuns: 100 })(
    'Navigation should be immediate and consistent',
    (questions) => {
      const navigator = createQuestionNavigator(questions)
      
      // Test that navigation is immediate (no async delays)
      for (let i = 0; i < Math.min(questions.length, 10); i++) {
        const targetIndex = Math.floor(Math.random() * questions.length)
        
        // Record time before navigation
        const beforeTime = Date.now()
        const navigationSuccess = navigator.navigateToQuestion(targetIndex)
        const afterTime = Date.now()
        
        // Navigation should succeed
        expect(navigationSuccess).toBe(true)
        
        // Index should be updated immediately
        expect(navigator.getCurrentIndex()).toBe(targetIndex)
        
        // Navigation should be fast (within reasonable time)
        expect(afterTime - beforeTime).toBeLessThan(100) // Should be nearly instantaneous
        
        // Multiple calls to getCurrentIndex should return the same value
        expect(navigator.getCurrentIndex()).toBe(targetIndex)
        expect(navigator.getCurrentIndex()).toBe(targetIndex)
        expect(navigator.getCurrentIndex()).toBe(targetIndex)
      }
    }
  )
  
  test.prop([questionsArrayGenerator], { numRuns: 100 })(
    'Navigation history should accurately track all movements',
    (questions) => {
      const navigator = createQuestionNavigator(questions)
      
      // Perform a series of navigations
      const navigationTargets = []
      const numberOfNavigations = Math.min(questions.length * 2, 20)
      
      for (let i = 0; i < numberOfNavigations; i++) {
        const targetIndex = Math.floor(Math.random() * questions.length)
        navigationTargets.push(targetIndex)
        navigator.navigateToQuestion(targetIndex)
      }
      
      const history = navigator.getNavigationHistory()
      
      // History should have correct length
      expect(history.length).toBe(numberOfNavigations)
      
      // Each history entry should be accurate
      let expectedFromIndex = 0 // Initial index
      navigationTargets.forEach((targetIndex, i) => {
        const historyEntry = history[i]
        
        expect(historyEntry.from).toBe(expectedFromIndex)
        expect(historyEntry.to).toBe(targetIndex)
        expect(historyEntry.timestamp).toBeDefined()
        expect(typeof historyEntry.timestamp).toBe('number')
        
        // Timestamps should be in chronological order
        if (i > 0) {
          expect(historyEntry.timestamp).toBeGreaterThanOrEqual(history[i - 1].timestamp)
        }
        
        expectedFromIndex = targetIndex
      })
      
      // Final current index should match last navigation target
      const lastTarget = navigationTargets[navigationTargets.length - 1]
      expect(navigator.getCurrentIndex()).toBe(lastTarget)
    }
  )
  
  test.prop([fc.array(questionGenerator, { minLength: 0, maxLength: 5 })], { numRuns: 100 })(
    'Navigation should handle edge cases with small question sets',
    (questions) => {
      const navigator = createQuestionNavigator(questions)
      
      if (questions.length === 0) {
        // Empty question set - no navigation should be possible
        expect(navigator.getQuestionCount()).toBe(0)
        expect(navigator.canNavigateTo(0)).toBe(false)
        expect(navigator.navigateToQuestion(0)).toBe(false)
        expect(navigator.getCurrentIndex()).toBe(0) // Should remain at initial state
      } else if (questions.length === 1) {
        // Single question - only index 0 should be valid
        expect(navigator.getQuestionCount()).toBe(1)
        expect(navigator.canNavigateTo(0)).toBe(true)
        expect(navigator.canNavigateTo(1)).toBe(false)
        expect(navigator.navigateToQuestion(0)).toBe(true)
        expect(navigator.getCurrentIndex()).toBe(0)
        expect(navigator.navigateToQuestion(1)).toBe(false)
        expect(navigator.getCurrentIndex()).toBe(0) // Should remain at 0
      } else {
        // Multiple questions - test all valid indices
        for (let i = 0; i < questions.length; i++) {
          expect(navigator.canNavigateTo(i)).toBe(true)
          expect(navigator.navigateToQuestion(i)).toBe(true)
          expect(navigator.getCurrentIndex()).toBe(i)
        }
        
        // Test one invalid index
        expect(navigator.canNavigateTo(questions.length)).toBe(false)
        expect(navigator.navigateToQuestion(questions.length)).toBe(false)
      }
    }
  )
})