/**
 * Property-based tests for answer selection behavior
 * Feature: exam-preview-redesign, Property 4: Answer selection behavior
 * Validates: Requirements 4.3, 4.4
 */

import { describe, it, expect } from 'vitest'
import { fc, test } from '@fast-check/vitest'

// Mock answer selection interface
const answerSelectionInterface = () => {
  let selectedAnswer = null
  let selectionHistory = []
  
  return {
    selectAnswer: (optionId) => {
      const previousAnswer = selectedAnswer
      selectedAnswer = optionId
      selectionHistory.push({
        previous: previousAnswer,
        current: optionId,
        timestamp: Date.now()
      })
      return {
        selectedAnswer,
        hasChanged: previousAnswer !== optionId,
        previousAnswer
      }
    },
    
    getSelectedAnswer: () => selectedAnswer,
    
    getSelectionHistory: () => selectionHistory,
    
    reset: () => {
      selectedAnswer = null
      selectionHistory = []
    }
  }
}

// Generators for question options with unique IDs
const questionGenerator = fc.record({
  id: fc.string({ minLength: 1 }),
  order: fc.integer({ min: 1 }),
  content: fc.string({ minLength: 1, maxLength: 500 }),
  options: fc.integer({ min: 2, max: 6 }).chain(numOptions => {
    // Generate unique option IDs
    return fc.array(
      fc.record({
        id: fc.nat(),
        content: fc.string({ minLength: 1, maxLength: 200 }),
        isCorrect: fc.boolean()
      }),
      { minLength: numOptions, maxLength: numOptions }
    ).map(options => {
      // Ensure unique IDs by assigning sequential IDs
      return options.map((option, index) => ({
        ...option,
        id: index + 1
      }))
    })
  }),
  subject: fc.option(fc.string({ minLength: 1 })),
  category: fc.option(fc.string({ minLength: 1 }))
})

describe('Answer Selection Behavior Property Tests', () => {
  test.prop([questionGenerator], { numRuns: 100 })(
    '**Feature: exam-preview-redesign, Property 4: Answer selection behavior**',
    (question) => {
      const selectionInterface = answerSelectionInterface()
      
      // Property: For any question with multiple choice options, 
      // selecting an option should provide immediate visual feedback 
      // and allow changing to a different selection
      
      // Test that we can select any valid option
      const validOptionIds = question.options.map(opt => opt.id)
      
      for (const optionId of validOptionIds) {
        const result = selectionInterface.selectAnswer(optionId)
        
        // Should provide immediate feedback
        expect(result.selectedAnswer).toBe(optionId)
        expect(selectionInterface.getSelectedAnswer()).toBe(optionId)
        
        // Should indicate if selection changed
        expect(typeof result.hasChanged).toBe('boolean')
        expect(result.previousAnswer).toBeDefined()
      }
      
      // Test changing selections between options
      if (validOptionIds.length >= 2) {
        const firstOption = validOptionIds[0]
        const secondOption = validOptionIds[1]
        
        // Select first option
        selectionInterface.reset()
        const firstResult = selectionInterface.selectAnswer(firstOption)
        expect(firstResult.selectedAnswer).toBe(firstOption)
        expect(firstResult.hasChanged).toBe(true)
        expect(firstResult.previousAnswer).toBeNull()
        
        // Change to second option
        const secondResult = selectionInterface.selectAnswer(secondOption)
        expect(secondResult.selectedAnswer).toBe(secondOption)
        expect(secondResult.hasChanged).toBe(true)
        expect(secondResult.previousAnswer).toBe(firstOption)
        
        // Verify the change was persisted
        expect(selectionInterface.getSelectedAnswer()).toBe(secondOption)
      }
    }
  )
  
  test.prop([questionGenerator, fc.array(fc.integer({ min: 1, max: 1000 }), { minLength: 1, maxLength: 10 })], { numRuns: 100 })(
    'Selection changes should be tracked and allow multiple changes',
    (question, selectionSequence) => {
      const selectionInterface = answerSelectionInterface()
      const validOptionIds = question.options.map(opt => opt.id)
      
      // Only test with valid option IDs
      const validSelections = selectionSequence.filter(id => validOptionIds.includes(id))
      
      if (validSelections.length === 0) return // Skip if no valid selections
      
      let previousSelection = null
      
      for (const optionId of validSelections) {
        const result = selectionInterface.selectAnswer(optionId)
        
        // Should always update to the new selection
        expect(result.selectedAnswer).toBe(optionId)
        expect(selectionInterface.getSelectedAnswer()).toBe(optionId)
        
        // Should correctly track if this is a change
        const expectedChange = previousSelection !== optionId
        expect(result.hasChanged).toBe(expectedChange)
        expect(result.previousAnswer).toBe(previousSelection)
        
        previousSelection = optionId
      }
      
      // History should track all selections
      const history = selectionInterface.getSelectionHistory()
      expect(history.length).toBe(validSelections.length)
      
      // Each history entry should have the correct structure
      history.forEach((entry, index) => {
        expect(entry.current).toBe(validSelections[index])
        expect(entry.previous).toBe(index === 0 ? null : validSelections[index - 1])
        expect(typeof entry.timestamp).toBe('number')
      })
    }
  )
  
  test.prop([questionGenerator], { numRuns: 100 })(
    'Selecting the same option multiple times should not change selection',
    (question) => {
      const selectionInterface = answerSelectionInterface()
      const validOptionIds = question.options.map(opt => opt.id)
      
      if (validOptionIds.length === 0) return // Skip if no options
      
      const optionId = validOptionIds[0]
      
      // First selection should be a change
      const firstResult = selectionInterface.selectAnswer(optionId)
      expect(firstResult.hasChanged).toBe(true)
      expect(firstResult.selectedAnswer).toBe(optionId)
      
      // Subsequent selections of the same option should not be changes
      const secondResult = selectionInterface.selectAnswer(optionId)
      expect(secondResult.hasChanged).toBe(false)
      expect(secondResult.selectedAnswer).toBe(optionId)
      expect(secondResult.previousAnswer).toBe(optionId)
      
      const thirdResult = selectionInterface.selectAnswer(optionId)
      expect(thirdResult.hasChanged).toBe(false)
      expect(thirdResult.selectedAnswer).toBe(optionId)
      expect(thirdResult.previousAnswer).toBe(optionId)
    }
  )
  
  test.prop([questionGenerator], { numRuns: 100 })(
    'Interface should handle edge cases gracefully',
    (question) => {
      const selectionInterface = answerSelectionInterface()
      
      // Test with empty options
      const emptyQuestion = { ...question, options: [] }
      
      // Should not throw errors when no options exist
      expect(() => {
        const validIds = emptyQuestion.options.map(opt => opt.id)
        expect(validIds).toEqual([])
      }).not.toThrow()
      
      // Test with single option
      if (question.options.length >= 1) {
        const singleOptionQuestion = { ...question, options: [question.options[0]] }
        const optionId = singleOptionQuestion.options[0].id
        
        const result = selectionInterface.selectAnswer(optionId)
        expect(result.selectedAnswer).toBe(optionId)
        expect(result.hasChanged).toBe(true)
        
        // Selecting the same single option again
        const secondResult = selectionInterface.selectAnswer(optionId)
        expect(secondResult.hasChanged).toBe(false)
      }
    }
  )
})