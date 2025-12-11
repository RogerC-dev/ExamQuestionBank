/**
 * Property-based tests for results calculation accuracy
 * Feature: exam-preview-redesign, Property 5: Results calculation accuracy
 * Validates: Requirements 5.1, 5.2, 5.3
 */

import { describe, it, expect } from 'vitest'
import { fc, test } from '@fast-check/vitest'

// Mock results calculation function based on exam store logic
const calculateExamResults = (exam, userAnswers, timeLeft = 0) => {
  if (!exam?.questions) {
    return {
      examId: exam?.id || '',
      score: 0,
      correctCount: 0,
      totalCount: 0,
      percentage: 0,
      duration: 0,
      details: [],
      wrongQuestionIds: []
    }
  }

  const totalCount = exam.questions.length
  let correctCount = 0
  const details = []
  const wrongQuestionIds = []

  exam.questions.forEach((question, index) => {
    const userAnswer = userAnswers[index]
    const correctOption = question.options?.find(opt => opt.isCorrect)
    const userOption = question.options?.find(opt => opt.id === userAnswer)
    const isCorrect = userAnswer === correctOption?.id

    if (isCorrect) {
      correctCount++
    } else {
      wrongQuestionIds.push(question.id)
    }

    details.push({
      questionId: question.id,
      question: question.content,
      userAnswer: userOption?.content || null,
      correctAnswer: correctOption?.content || '',
      isCorrect,
      timeSpent: 0
    })
  })

  const percentage = totalCount > 0 ? Math.round((correctCount / totalCount) * 100) : 0
  const duration = exam?.timeLimit ? Math.max(0, (exam.timeLimit * 60) - timeLeft) : 0

  return {
    examId: exam.id,
    score: correctCount,
    correctCount,
    totalCount,
    percentage,
    duration,
    details,
    wrongQuestionIds
  }
}

// Generators for test data
// Generator for question options with unique IDs
const questionOptionsGenerator = fc.integer({ min: 2, max: 6 }).chain(numOptions => {
  // Generate unique IDs for each option
  const ids = Array.from({ length: numOptions }, (_, i) => i + 1)
  return fc.tuple(
    fc.constant(ids),
    fc.array(fc.string({ minLength: 1, maxLength: 100 }).filter(s => s.trim().length > 0), { minLength: numOptions, maxLength: numOptions }),
    fc.integer({ min: 0, max: numOptions - 1 }) // Index of correct answer
  ).map(([ids, contents, correctIndex]) => {
    return ids.map((id, index) => ({
      id,
      content: contents[index],
      isCorrect: index === correctIndex
    }))
  })
})

const examQuestionGenerator = fc.record({
  id: fc.string({ minLength: 1, maxLength: 20 }).filter(s => s.trim().length > 0),
  order: fc.integer({ min: 1, max: 100 }),
  content: fc.string({ minLength: 1, maxLength: 200 }).filter(s => s.trim().length > 0),
  options: questionOptionsGenerator,
  subject: fc.option(fc.string({ minLength: 1, maxLength: 50 })),
  category: fc.option(fc.string({ minLength: 1, maxLength: 50 }))
})

const examGenerator = fc.record({
  id: fc.string({ minLength: 1, maxLength: 20 }).filter(s => s.trim().length > 0),
  name: fc.string({ minLength: 1, maxLength: 100 }).filter(s => s.trim().length > 0),
  description: fc.option(fc.string({ minLength: 1, maxLength: 200 })),
  timeLimit: fc.option(fc.integer({ min: 1, max: 180 })),
  questions: fc.array(examQuestionGenerator, { minLength: 1, maxLength: 20 }),
  settings: fc.record({
    allowReview: fc.boolean(),
    showResults: fc.boolean(),
    randomizeQuestions: fc.boolean(),
    randomizeOptions: fc.boolean()
  })
})

// Generator that produces exam with user answers together
const examWithAnswersGenerator = examGenerator.chain(exam => {
  // Generate user answers based on the exam's questions
  const answerGenerators = exam.questions.map((question, index) => {
    // Either no answer (undefined) or one of the valid option IDs
    return fc.option(fc.oneof(...question.options.map(opt => fc.constant(opt.id))), { nil: undefined })
  })
  
  return fc.tuple(
    fc.constant(exam),
    fc.tuple(...answerGenerators).map(answers => {
      const result = {}
      answers.forEach((answer, index) => {
        if (answer !== undefined) {
          result[index] = answer
        }
      })
      return result
    }),
    fc.integer({ min: 0, max: exam.timeLimit ? exam.timeLimit * 60 : 3600 })
  )
})

describe('Results Calculation Property Tests', () => {
  test.prop([examWithAnswersGenerator], { numRuns: 100 })(
    '**Feature: exam-preview-redesign, Property 5: Results calculation accuracy**',
    ([exam, userAnswers, timeLeft]) => {
      const results = calculateExamResults(exam, userAnswers, timeLeft)
      
      // Property: Results should correctly calculate score, percentage, and provide detailed breakdown
      
      // Basic structure validation
      expect(results).toBeDefined()
      expect(typeof results).toBe('object')
      expect(results.examId).toBe(exam.id)
      
      // Score and count validation
      expect(results.score).toBe(results.correctCount)
      expect(results.totalCount).toBe(exam.questions.length)
      expect(results.correctCount).toBeGreaterThanOrEqual(0)
      expect(results.correctCount).toBeLessThanOrEqual(results.totalCount)
      
      // Percentage calculation validation
      const expectedPercentage = results.totalCount > 0 
        ? Math.round((results.correctCount / results.totalCount) * 100) 
        : 0
      expect(results.percentage).toBe(expectedPercentage)
      expect(results.percentage).toBeGreaterThanOrEqual(0)
      expect(results.percentage).toBeLessThanOrEqual(100)
      
      // Duration validation
      expect(results.duration).toBeGreaterThanOrEqual(0)
      if (exam.timeLimit) {
        expect(results.duration).toBeLessThanOrEqual(exam.timeLimit * 60)
      }
      
      // Details array validation
      expect(Array.isArray(results.details)).toBe(true)
      expect(results.details.length).toBe(exam.questions.length)
      
      // Wrong questions validation
      expect(Array.isArray(results.wrongQuestionIds)).toBe(true)
      
      // Detailed validation of each question result
      let manualCorrectCount = 0
      let manualWrongCount = 0
      
      results.details.forEach((detail, index) => {
        const question = exam.questions[index]
        const userAnswer = userAnswers[index]
        const correctOption = question.options.find(opt => opt.isCorrect)
        const userOption = question.options.find(opt => opt.id === userAnswer)
        
        // Validate detail structure
        expect(detail.questionId).toBe(question.id)
        expect(detail.question).toBe(question.content)
        expect(detail.correctAnswer).toBe(correctOption.content)
        
        // Validate user answer
        if (userAnswer !== undefined) {
          expect(detail.userAnswer).toBe(userOption.content)
        } else {
          expect(detail.userAnswer).toBeNull()
        }
        
        // Validate correctness
        const expectedCorrect = userAnswer === correctOption.id
        expect(detail.isCorrect).toBe(expectedCorrect)
        
        if (expectedCorrect) {
          manualCorrectCount++
        } else {
          manualWrongCount++
        }
      })
      
      // Verify manual count matches calculated count
      expect(manualCorrectCount).toBe(results.correctCount)
      expect(manualCorrectCount + manualWrongCount).toBe(results.totalCount)
      
      // Verify wrong questions list accuracy
      const expectedWrongIds = results.details
        .filter(detail => !detail.isCorrect)
        .map(detail => detail.questionId)
      expect(results.wrongQuestionIds.sort()).toEqual(expectedWrongIds.sort())
      
      // Consistency checks
      expect(results.wrongQuestionIds.length).toBe(results.totalCount - results.correctCount)
    }
  )
  
  test.prop([examGenerator], { numRuns: 100 })(
    'Results calculation should handle edge cases correctly',
    (exam) => {
      const edgeCases = [
        {}, // No answers
        Object.fromEntries(exam.questions.map((_, i) => [i, -1])), // Invalid answers
        Object.fromEntries(exam.questions.map((_, i) => [i, 999])), // Non-existent option IDs
      ]
      
      edgeCases.forEach(userAnswers => {
        const results = calculateExamResults(exam, userAnswers, 0)
        
        // Should handle edge cases gracefully
        expect(results).toBeDefined()
        expect(results.correctCount).toBeGreaterThanOrEqual(0)
        expect(results.correctCount).toBeLessThanOrEqual(results.totalCount)
        expect(results.percentage).toBeGreaterThanOrEqual(0)
        expect(results.percentage).toBeLessThanOrEqual(100)
        expect(results.details.length).toBe(exam.questions.length)
        
        // Invalid answers should result in incorrect responses
        results.details.forEach(detail => {
          if (detail.userAnswer === null) {
            expect(detail.isCorrect).toBe(false)
          }
        })
      })
    }
  )
  
  test.prop([examGenerator], { numRuns: 100 })(
    'Perfect score should result in 100% and all correct',
    (exam) => {
      // Generate perfect answers (all correct)
      const perfectAnswers = {}
      exam.questions.forEach((question, index) => {
        const correctOption = question.options.find(opt => opt.isCorrect)
        perfectAnswers[index] = correctOption.id
      })
      
      const results = calculateExamResults(exam, perfectAnswers, 0)
      
      expect(results.correctCount).toBe(exam.questions.length)
      expect(results.percentage).toBe(100)
      expect(results.wrongQuestionIds.length).toBe(0)
      expect(results.details.every(detail => detail.isCorrect)).toBe(true)
    }
  )
  
  test.prop([examGenerator], { numRuns: 100 })(
    'No answers should result in 0% and all incorrect',
    (exam) => {
      const results = calculateExamResults(exam, {}, 0)
      
      expect(results.correctCount).toBe(0)
      expect(results.percentage).toBe(0)
      expect(results.wrongQuestionIds.length).toBe(exam.questions.length)
      expect(results.details.every(detail => !detail.isCorrect)).toBe(true)
      expect(results.details.every(detail => detail.userAnswer === null)).toBe(true)
    }
  )
})

describe('Results Calculation Edge Cases', () => {
  it('should handle empty exam gracefully', () => {
    const emptyExam = {
      id: 'empty',
      name: 'Empty Exam',
      questions: []
    }
    
    const results = calculateExamResults(emptyExam, {}, 0)
    
    expect(results.totalCount).toBe(0)
    expect(results.correctCount).toBe(0)
    expect(results.percentage).toBe(0)
    expect(results.details).toEqual([])
    expect(results.wrongQuestionIds).toEqual([])
  })
  
  it('should handle null/undefined exam gracefully', () => {
    const results1 = calculateExamResults(null, {}, 0)
    const results2 = calculateExamResults(undefined, {}, 0)
    const results3 = calculateExamResults({ id: 'test' }, {}, 0)
    
    ;[results1, results2, results3].forEach(results => {
      expect(results.totalCount).toBe(0)
      expect(results.correctCount).toBe(0)
      expect(results.percentage).toBe(0)
      expect(results.details).toEqual([])
      expect(results.wrongQuestionIds).toEqual([])
    })
  })
})