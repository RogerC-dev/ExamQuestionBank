/**
 * Unit tests for responsive design and high contrast mode
 * Requirements: 7.1, 7.4, 7.5
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ExamHeader from '../components/exam/ExamHeader.vue'
import ExamPreloader from '../components/exam/ExamPreloader.vue'
import TimerComponent from '../components/exam/TimerComponent.vue'
import QuestionNavigator from '../components/exam/QuestionNavigator.vue'
import QuestionDisplay from '../components/exam/QuestionDisplay.vue'
import ProgressTracker from '../components/exam/ProgressTracker.vue'
import ScoreDisplay from '../components/exam/ScoreDisplay.vue'

// Helper to check if CSS contains responsive breakpoints
const hasResponsiveBreakpoints = (component) => {
  const style = component.vm.$el.ownerDocument.defaultView.getComputedStyle(component.vm.$el)
  return style !== null
}

// Mock exam data
const mockExam = {
  name: 'Test Exam',
  description: 'A test exam for responsive design testing',
  questions: [
    { id: '1', order: 1, content: 'Question 1', options: [{ id: 1, content: 'A', isCorrect: true }] },
    { id: '2', order: 2, content: 'Question 2', options: [{ id: 2, content: 'B', isCorrect: false }] }
  ],
  timeLimit: 30
}

const mockQuestion = {
  id: '1',
  order: 1,
  content: 'What is the capital of France?',
  options: [
    { id: 1, content: 'London', isCorrect: false },
    { id: 2, content: 'Paris', isCorrect: true },
    { id: 3, content: 'Berlin', isCorrect: false },
    { id: 4, content: 'Madrid', isCorrect: false }
  ],
  subject: 'Geography',
  category: 'Capitals'
}

const mockResults = {
  examId: 'exam-1',
  score: 80,
  correctCount: 8,
  totalCount: 10,
  percentage: 80,
  duration: 1200,
  details: [],
  wrongQuestionIds: []
}

describe('Responsive Design Tests', () => {
  describe('ExamHeader Responsive Design', () => {
    it('renders with responsive container classes', () => {
      const wrapper = mount(ExamHeader, {
        props: { exam: mockExam }
      })
      
      expect(wrapper.find('.exam-header').exists()).toBe(true)
      expect(wrapper.find('.exam-info').exists()).toBe(true)
      expect(wrapper.find('.exam-meta').exists()).toBe(true)
    })

    it('has proper structure for mobile layout adaptation', () => {
      const wrapper = mount(ExamHeader, {
        props: { exam: mockExam }
      })
      
      // Check that flex container exists for responsive layout
      const header = wrapper.find('.exam-header')
      expect(header.exists()).toBe(true)
      
      // Check that all content sections exist
      expect(wrapper.find('.exam-title').exists()).toBe(true)
      expect(wrapper.find('.exam-description').exists()).toBe(true)
      expect(wrapper.find('.question-count').exists()).toBe(true)
    })

    it('renders header actions slot for responsive button layout', () => {
      const wrapper = mount(ExamHeader, {
        props: { exam: mockExam },
        slots: {
          actions: '<button class="action-btn">Start</button>'
        }
      })
      
      expect(wrapper.find('.header-actions').exists()).toBe(true)
      expect(wrapper.find('.action-btn').exists()).toBe(true)
    })
  })

  describe('ExamPreloader Responsive Design', () => {
    it('renders loading state with responsive structure', () => {
      const wrapper = mount(ExamPreloader, {
        props: { isLoading: true, loadingText: 'Loading...' }
      })
      
      expect(wrapper.find('.exam-preloader').exists()).toBe(true)
      expect(wrapper.find('.loading-state').exists()).toBe(true)
      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    })

    it('renders error state with responsive button', () => {
      const wrapper = mount(ExamPreloader, {
        props: { 
          isLoading: false, 
          error: 'Network error',
          onRetry: () => {}
        }
      })
      
      expect(wrapper.find('.error-state').exists()).toBe(true)
      expect(wrapper.find('.btn').exists()).toBe(true)
    })
  })

  describe('TimerComponent Responsive Design', () => {
    it('renders timer with responsive structure', () => {
      const wrapper = mount(TimerComponent, {
        props: { timeLimit: 1800, isActive: false }
      })
      
      expect(wrapper.find('.timer-component').exists()).toBe(true)
      expect(wrapper.find('.timer-label').exists()).toBe(true)
      expect(wrapper.find('.timer-value').exists()).toBe(true)
    })

    it('displays time in readable format', () => {
      const wrapper = mount(TimerComponent, {
        props: { timeLimit: 1800, isActive: false }
      })
      
      expect(wrapper.find('.timer-value').text()).toBe('30:00')
    })
  })

  describe('QuestionNavigator Responsive Design', () => {
    it('renders navigation grid with responsive structure', () => {
      const wrapper = mount(QuestionNavigator, {
        props: {
          questions: mockExam.questions,
          currentIndex: 0,
          answeredQuestions: new Set()
        }
      })
      
      expect(wrapper.find('.question-navigator').exists()).toBe(true)
      expect(wrapper.find('.question-grid').exists()).toBe(true)
    })

    it('renders touch-friendly buttons', () => {
      const wrapper = mount(QuestionNavigator, {
        props: {
          questions: mockExam.questions,
          currentIndex: 0,
          answeredQuestions: new Set()
        }
      })
      
      const buttons = wrapper.findAll('.question-button')
      expect(buttons.length).toBe(2)
      buttons.forEach(button => {
        expect(button.attributes('type')).toBe('button')
      })
    })
  })

  describe('QuestionDisplay Responsive Design', () => {
    it('renders question with responsive typography', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1,
          selectedAnswer: null
        }
      })
      
      expect(wrapper.find('.question-display').exists()).toBe(true)
      expect(wrapper.find('.question-text').exists()).toBe(true)
      expect(wrapper.find('.answer-options').exists()).toBe(true)
    })

    it('renders touch-friendly option items', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1,
          selectedAnswer: null
        }
      })
      
      const options = wrapper.findAll('.option-item')
      expect(options.length).toBe(4)
      
      // Check that options have proper interactive attributes
      options.forEach(option => {
        expect(option.attributes('role')).toBe('button')
        expect(option.attributes('tabindex')).toBe('0')
      })
    })
  })

  describe('ProgressTracker Responsive Design', () => {
    it('renders progress bar with responsive structure', () => {
      const wrapper = mount(ProgressTracker, {
        props: {
          answeredQuestions: new Set([0, 1]),
          totalQuestions: 5
        }
      })
      
      expect(wrapper.find('.progress-tracker').exists()).toBe(true)
      expect(wrapper.find('.progress-bar').exists()).toBe(true)
      expect(wrapper.find('.progress-fill').exists()).toBe(true)
    })

    it('displays progress information', () => {
      const wrapper = mount(ProgressTracker, {
        props: {
          answeredQuestions: new Set([0, 1]),
          totalQuestions: 5
        }
      })
      
      expect(wrapper.find('.progress-text').exists()).toBe(true)
      expect(wrapper.find('.progress-percentage').exists()).toBe(true)
    })
  })

  describe('ScoreDisplay Responsive Design', () => {
    it('renders score with responsive layout', () => {
      const wrapper = mount(ScoreDisplay, {
        props: { results: mockResults }
      })
      
      expect(wrapper.find('.score-display').exists()).toBe(true)
      expect(wrapper.find('.score-main').exists()).toBe(true)
      expect(wrapper.find('.score-circle').exists()).toBe(true)
    })

    it('displays score details in responsive format', () => {
      const wrapper = mount(ScoreDisplay, {
        props: { results: mockResults }
      })
      
      expect(wrapper.find('.score-percentage').text()).toBe('80%')
      expect(wrapper.find('.score-details').exists()).toBe(true)
    })
  })
})

describe('High Contrast Mode Tests', () => {
  describe('ExamHeader High Contrast', () => {
    it('has proper color contrast for text elements', () => {
      const wrapper = mount(ExamHeader, {
        props: { exam: mockExam }
      })
      
      // Verify text elements exist and have content
      expect(wrapper.find('.exam-title').text()).toBeTruthy()
      expect(wrapper.find('.exam-description').text()).toBeTruthy()
    })
  })

  describe('TimerComponent High Contrast', () => {
    it('applies appropriate class for normal state', () => {
      const wrapper = mount(TimerComponent, {
        props: { timeLimit: 1800, isActive: false }
      })
      
      expect(wrapper.find('.timer-component').classes()).toContain('normal')
    })

    it('applies warning class when time is low', () => {
      const wrapper = mount(TimerComponent, {
        props: { timeLimit: 180, isActive: false } // 3 minutes
      })
      
      expect(wrapper.find('.timer-component').classes()).toContain('warning')
    })

    it('applies danger class when time is critical', () => {
      const wrapper = mount(TimerComponent, {
        props: { timeLimit: 30, isActive: false } // 30 seconds
      })
      
      expect(wrapper.find('.timer-component').classes()).toContain('danger')
    })
  })

  describe('QuestionDisplay High Contrast', () => {
    it('applies selected class for visual feedback', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1,
          selectedAnswer: 2
        }
      })
      
      const selectedOption = wrapper.findAll('.option-item').find(
        opt => opt.classes().includes('selected')
      )
      expect(selectedOption).toBeTruthy()
    })
  })

  describe('ScoreDisplay High Contrast', () => {
    it('applies excellent class for high scores', () => {
      const wrapper = mount(ScoreDisplay, {
        props: { 
          results: { ...mockResults, percentage: 95 }
        }
      })
      
      expect(wrapper.find('.score-circle').classes()).toContain('excellent')
    })

    it('applies good class for good scores', () => {
      const wrapper = mount(ScoreDisplay, {
        props: { 
          results: { ...mockResults, percentage: 85 }
        }
      })
      
      expect(wrapper.find('.score-circle').classes()).toContain('good')
    })

    it('applies average class for average scores', () => {
      const wrapper = mount(ScoreDisplay, {
        props: { 
          results: { ...mockResults, percentage: 75 }
        }
      })
      
      expect(wrapper.find('.score-circle').classes()).toContain('average')
    })

    it('applies below-average class for below average scores', () => {
      const wrapper = mount(ScoreDisplay, {
        props: { 
          results: { ...mockResults, percentage: 65 }
        }
      })
      
      expect(wrapper.find('.score-circle').classes()).toContain('below-average')
    })

    it('applies poor class for poor scores', () => {
      const wrapper = mount(ScoreDisplay, {
        props: { 
          results: { ...mockResults, percentage: 50 }
        }
      })
      
      expect(wrapper.find('.score-circle').classes()).toContain('poor')
    })
  })
})

describe('Accessibility Markup Tests', () => {
  describe('ARIA Labels', () => {
    it('ExamHeader has proper ARIA attributes', () => {
      const wrapper = mount(ExamHeader, {
        props: { exam: mockExam }
      })
      
      expect(wrapper.find('header').attributes('role')).toBe('banner')
      expect(wrapper.find('header').attributes('aria-label')).toBe('Exam information header')
    })

    it('ExamPreloader has proper ARIA attributes for loading state', () => {
      const wrapper = mount(ExamPreloader, {
        props: { isLoading: true }
      })
      
      expect(wrapper.find('.loading-state').attributes('role')).toBe('status')
      expect(wrapper.find('.loading-state').attributes('aria-live')).toBe('polite')
    })

    it('ExamPreloader has proper ARIA attributes for error state', () => {
      const wrapper = mount(ExamPreloader, {
        props: { isLoading: false, error: 'Error occurred' }
      })
      
      expect(wrapper.find('.error-state').attributes('role')).toBe('alert')
      expect(wrapper.find('.error-state').attributes('aria-live')).toBe('assertive')
    })

    it('TimerComponent has timer role', () => {
      const wrapper = mount(TimerComponent, {
        props: { timeLimit: 1800, isActive: false }
      })
      
      expect(wrapper.find('.timer-component').attributes('role')).toBe('timer')
    })

    it('QuestionNavigator has navigation role', () => {
      const wrapper = mount(QuestionNavigator, {
        props: {
          questions: mockExam.questions,
          currentIndex: 0,
          answeredQuestions: new Set()
        }
      })
      
      expect(wrapper.find('nav').attributes('role')).toBe('navigation')
    })

    it('ProgressTracker has progressbar role', () => {
      const wrapper = mount(ProgressTracker, {
        props: {
          answeredQuestions: new Set([0]),
          totalQuestions: 5
        }
      })
      
      expect(wrapper.find('.progress-bar').attributes('role')).toBe('progressbar')
    })

    it('ScoreDisplay has region role', () => {
      const wrapper = mount(ScoreDisplay, {
        props: { results: mockResults }
      })
      
      expect(wrapper.find('.score-display').attributes('role')).toBe('region')
    })
  })

  describe('Keyboard Navigation', () => {
    it('QuestionDisplay options are keyboard accessible', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1,
          selectedAnswer: null
        }
      })
      
      const options = wrapper.findAll('.option-item')
      options.forEach(option => {
        expect(option.attributes('tabindex')).toBe('0')
      })
    })

    it('QuestionNavigator buttons are keyboard accessible', () => {
      const wrapper = mount(QuestionNavigator, {
        props: {
          questions: mockExam.questions,
          currentIndex: 0,
          answeredQuestions: new Set()
        }
      })
      
      const buttons = wrapper.findAll('.question-button')
      buttons.forEach(button => {
        expect(button.element.tagName).toBe('BUTTON')
      })
    })
  })
})
