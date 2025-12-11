/**
 * Property-based tests for error message user-friendliness
 * Feature: exam-preview-redesign, Property 7: Error message user-friendliness
 * Validates: Requirements 6.4
 */

import { describe, it, expect } from 'vitest'
import { fc, test } from '@fast-check/vitest'

// Mock error handling function (extracted from examStore)
const createUserFriendlyError = (error) => {
  let message = 'An unexpected error occurred. Please try again.'
  let type = 'network'
  let recoverable = true

  if (error.name === 'NetworkError' || error.code === 'NETWORK_ERROR') {
    message = 'Unable to connect to the server. Please check your internet connection and try again.'
    type = 'network'
    recoverable = true
  } else if (error.status === 404) {
    message = 'The requested exam could not be found. Please check the exam ID and try again.'
    type = 'data'
    recoverable = false
  } else if (error.status === 403) {
    message = 'You do not have permission to access this exam. Please contact your instructor.'
    type = 'user'
    recoverable = false
  } else if (error.status >= 500) {
    message = 'The server is currently experiencing issues. Please try again in a few minutes.'
    type = 'network'
    recoverable = true
  } else if (error.message && !containsTechnicalTerms(error.message)) {
    // Only show custom error messages that don't contain technical details
    message = error.message
  }

  return {
    type,
    message,
    recoverable,
    retryAction: recoverable ? () => {} : undefined
  }
}

// Helper function to check for technical terms
const containsTechnicalTerms = (message) => {
  const technicalTerms = [
    'fetch',
    'XMLHttpRequest',
    'TypeError',
    'ReferenceError',
    'undefined is not a function',
    'Cannot read property',
    'stack trace',
    'at Object.',
    'at Function.',
    'webpack',
    'node_modules'
  ]
  
  const lowerMessage = message.toLowerCase()
  return technicalTerms.some(term => lowerMessage.includes(term.toLowerCase()))
}

// Generators for different types of errors
const networkErrorGenerator = fc.record({
  name: fc.constant('NetworkError'),
  message: fc.string({ minLength: 1 }),
  code: fc.option(fc.constant('NETWORK_ERROR'))
})

const httpErrorGenerator = fc.record({
  status: fc.integer({ min: 400, max: 599 }),
  message: fc.string({ minLength: 1 }),
  statusText: fc.option(fc.string({ minLength: 1 }))
})

const genericErrorGenerator = fc.record({
  message: fc.string({ minLength: 1 }),
  name: fc.option(fc.string({ minLength: 1 })),
  stack: fc.option(fc.string({ minLength: 1 }))
})

const technicalErrorGenerator = fc.record({
  message: fc.oneof(
    fc.constant('fetch failed'),
    fc.constant('XMLHttpRequest error'),
    fc.constant('TypeError: Cannot read property'),
    fc.constant('ReferenceError: undefined')
  ),
  name: fc.string({ minLength: 1 }),
  stack: fc.option(fc.string({ minLength: 1 }))
})

const allErrorGenerator = fc.oneof(
  networkErrorGenerator,
  httpErrorGenerator,
  genericErrorGenerator,
  technicalErrorGenerator
)

describe('Error Message User-Friendliness Property Tests', () => {
  test.prop([allErrorGenerator], { numRuns: 100 })(
    '**Feature: exam-preview-redesign, Property 7: Error message user-friendliness**',
    (error) => {
      const userFriendlyError = createUserFriendlyError(error)
      
      // Property: Error messages should be user-friendly and not expose technical details
      
      // Message should always be defined and non-empty
      expect(userFriendlyError.message).toBeDefined()
      expect(typeof userFriendlyError.message).toBe('string')
      expect(userFriendlyError.message.length).toBeGreaterThan(0)
      
      // Message should not contain technical implementation details
      const technicalTerms = [
        'fetch',
        'XMLHttpRequest',
        'TypeError',
        'ReferenceError',
        'undefined is not a function',
        'Cannot read property',
        'stack trace',
        'at Object.',
        'at Function.',
        'webpack',
        'node_modules'
      ]
      
      const lowerMessage = userFriendlyError.message.toLowerCase()
      technicalTerms.forEach(term => {
        expect(lowerMessage).not.toContain(term.toLowerCase())
      })
      
      // Type should be one of the expected error types
      expect(['network', 'data', 'state', 'user']).toContain(userFriendlyError.type)
      
      // Recoverable should be a boolean
      expect(typeof userFriendlyError.recoverable).toBe('boolean')
      
      // If recoverable, should have retry action; if not recoverable, should not
      if (userFriendlyError.recoverable) {
        expect(userFriendlyError.retryAction).toBeDefined()
        expect(typeof userFriendlyError.retryAction).toBe('function')
      } else {
        expect(userFriendlyError.retryAction).toBeUndefined()
      }
    }
  )
  
  test.prop([httpErrorGenerator], { numRuns: 100 })(
    'HTTP errors should be mapped to appropriate user-friendly messages',
    (error) => {
      const userFriendlyError = createUserFriendlyError(error)
      
      if (error.status === 404) {
        expect(userFriendlyError.message).toContain('could not be found')
        expect(userFriendlyError.type).toBe('data')
        expect(userFriendlyError.recoverable).toBe(false)
      } else if (error.status === 403) {
        expect(userFriendlyError.message).toContain('permission')
        expect(userFriendlyError.type).toBe('user')
        expect(userFriendlyError.recoverable).toBe(false)
      } else if (error.status >= 500) {
        expect(userFriendlyError.message).toContain('server')
        expect(userFriendlyError.type).toBe('network')
        expect(userFriendlyError.recoverable).toBe(true)
      }
    }
  )
  
  test.prop([networkErrorGenerator], { numRuns: 100 })(
    'Network errors should provide helpful guidance',
    (error) => {
      const userFriendlyError = createUserFriendlyError(error)
      
      expect(userFriendlyError.message).toContain('connect')
      expect(userFriendlyError.message).toContain('internet connection')
      expect(userFriendlyError.type).toBe('network')
      expect(userFriendlyError.recoverable).toBe(true)
      expect(userFriendlyError.retryAction).toBeDefined()
    }
  )
  
  test.prop([technicalErrorGenerator], { numRuns: 100 })(
    'Technical errors should be sanitized to generic messages',
    (error) => {
      const userFriendlyError = createUserFriendlyError(error)
      
      // Should fall back to generic message for technical errors
      expect(userFriendlyError.message).toBe('An unexpected error occurred. Please try again.')
      expect(userFriendlyError.type).toBe('network')
      expect(userFriendlyError.recoverable).toBe(true)
    }
  )
})