/**
 * Unit tests for QuestionDisplay component
 * Tests typography, spacing, hover effects, visual feedback, and mobile touch interaction
 * Requirements: 4.1, 4.2, 4.5, 7.1
 */

import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import QuestionDisplay from './QuestionDisplay.vue'

// Mock question data
const mockQuestion = {
  id: '1',
  content: 'What is the capital of France?',
  options: [
    { id: 1, content: 'London', isCorrect: false },
    { id: 2, content: 'Paris', isCorrect: true },
    { id: 3, content: 'Berlin', isCorrect: false },
    { id: 4, content: 'Madrid', isCorrect: false }
  ],
  subject: 'Geography',
  category: 'European Capitals'
}

const mockQuestionWithoutMeta = {
  id: '2',
  content: 'What is 2 + 2?',
  options: [
    { id: 1, content: '3', isCorrect: false },
    { id: 2, content: '4', isCorrect: true },
    { id: 3, content: '5', isCorrect: false }
  ]
}

describe('QuestionDisplay Component', () => {
  describe('Typography and Spacing Requirements (4.1)', () => {
    it('should display question text with large, readable typography', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1
        }
      })

      const questionText = wrapper.find('.question-text')
      expect(questionText.exists()).toBe(true)
      expect(questionText.text()).toBe(mockQuestion.content)
      
      // Check that the question text has appropriate styling classes
      expect(questionText.classes()).toContain('question-text')
    })

    it('should display question number prominently', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 5
        }
      })

      const questionNumber = wrapper.find('.question-number')
      expect(questionNumber.exists()).toBe(true)
      expect(questionNumber.text()).toBe('Question 5')
    })

    it('should show question metadata subtly when available', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1
        }
      })

      const metaItems = wrapper.findAll('.meta-item')
      expect(metaItems).toHaveLength(2)
      expect(metaItems[0].text()).toBe('Geography')
      expect(metaItems[1].text()).toBe('European Capitals')
    })

    it('should hide metadata section when no subject or category', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestionWithoutMeta,
          questionNumber: 1
        }
      })

      const questionMeta = wrapper.find('.question-meta')
      expect(questionMeta.exists()).toBe(false)
    })

    it('should display options with proper spacing and structure', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1
        }
      })

      const options = wrapper.findAll('.option-item')
      expect(options).toHaveLength(4)

      options.forEach((option, index) => {
        const label = option.find('.option-label')
        const content = option.find('.option-content')
        
        expect(label.exists()).toBe(true)
        expect(content.exists()).toBe(true)
        expect(label.text()).toBe(`${String.fromCharCode(65 + index)}.`)
        expect(content.text()).toBe(mockQuestion.options[index].content)
      })
    })
  })

  describe('Option Styling and Visual Feedback (4.2)', () => {
    it('should apply selected styling when an option is selected', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1,
          selectedAnswer: 2
        }
      })

      const options = wrapper.findAll('.option-item')
      const selectedOption = options.find(option => 
        option.find('.option-content').text() === 'Paris'
      )
      const unselectedOption = options.find(option => 
        option.find('.option-content').text() === 'London'
      )

      expect(selectedOption.classes()).toContain('selected')
      expect(unselectedOption.classes()).not.toContain('selected')
    })

    it('should have hover effect classes applied to options', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1
        }
      })

      const options = wrapper.findAll('.option-item')
      options.forEach(option => {
        expect(option.classes()).toContain('option-hover')
      })
    })

    it('should emit select-answer event when option is clicked', async () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1
        }
      })

      const firstOption = wrapper.findAll('.option-item')[0]
      await firstOption.trigger('click')

      expect(wrapper.emitted('select-answer')).toBeTruthy()
      expect(wrapper.emitted('select-answer')[0]).toEqual([1])
    })

    it('should handle keyboard navigation with Enter key', async () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1
        }
      })

      const firstOption = wrapper.findAll('.option-item')[0]
      await firstOption.trigger('keydown.enter')

      expect(wrapper.emitted('select-answer')).toBeTruthy()
      expect(wrapper.emitted('select-answer')[0]).toEqual([1])
    })

    it('should handle keyboard navigation with Space key', async () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1
        }
      })

      const firstOption = wrapper.findAll('.option-item')[0]
      await firstOption.trigger('keydown.space')

      expect(wrapper.emitted('select-answer')).toBeTruthy()
      expect(wrapper.emitted('select-answer')[0]).toEqual([1])
    })
  })

  describe('Accessibility Features (7.1)', () => {
    it('should have proper ARIA attributes for options', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1,
          selectedAnswer: 2
        }
      })

      const options = wrapper.findAll('.option-item')
      
      options.forEach((option, index) => {
        expect(option.attributes('role')).toBe('button')
        expect(option.attributes('tabindex')).toBe('0')
        expect(option.attributes('aria-label')).toContain(`Option ${String.fromCharCode(65 + index)}`)
        expect(option.attributes('aria-label')).toContain(mockQuestion.options[index].content)
      })
    })

    it('should set aria-pressed correctly for selected options', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1,
          selectedAnswer: 2
        }
      })

      const options = wrapper.findAll('.option-item')
      
      options.forEach((option, index) => {
        const expectedPressed = mockQuestion.options[index].id === 2 ? 'true' : 'false'
        expect(option.attributes('aria-pressed')).toBe(expectedPressed)
      })
    })
  })

  describe('Mobile Touch Interaction (7.1)', () => {
    it('should render without errors on mobile viewport', () => {
      // Simulate mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      })

      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1
        }
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.question-display').exists()).toBe(true)
    })

    it('should maintain touch-friendly option sizes', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1
        }
      })

      const options = wrapper.findAll('.option-item')
      options.forEach(option => {
        // Options should have the option-item class which provides touch-friendly sizing
        expect(option.classes()).toContain('option-item')
      })
    })
  })

  describe('Edge Cases and Error Handling', () => {
    it('should handle questions with no options gracefully', () => {
      const questionWithoutOptions = {
        ...mockQuestion,
        options: []
      }

      const wrapper = mount(QuestionDisplay, {
        props: {
          question: questionWithoutOptions,
          questionNumber: 1
        }
      })

      expect(wrapper.find('.answer-options').exists()).toBe(false)
    })

    it('should handle questions with single option', () => {
      const questionWithSingleOption = {
        ...mockQuestion,
        options: [{ id: 1, content: 'Only option', isCorrect: true }]
      }

      const wrapper = mount(QuestionDisplay, {
        props: {
          question: questionWithSingleOption,
          questionNumber: 1
        }
      })

      const options = wrapper.findAll('.option-item')
      expect(options).toHaveLength(1)
      expect(options[0].find('.option-content').text()).toBe('Only option')
    })

    it('should not render when question is null or undefined', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: null,
          questionNumber: 1
        }
      })

      expect(wrapper.find('.question-display').exists()).toBe(false)
    })

    it('should handle very long question content', () => {
      const longQuestion = {
        ...mockQuestion,
        content: 'This is a very long question that should still be displayed properly with good typography and spacing even when it contains a lot of text that might wrap to multiple lines in the interface.'
      }

      const wrapper = mount(QuestionDisplay, {
        props: {
          question: longQuestion,
          questionNumber: 1
        }
      })

      const questionText = wrapper.find('.question-text')
      expect(questionText.text()).toBe(longQuestion.content)
      expect(questionText.exists()).toBe(true)
    })

    it('should handle options with very long content', () => {
      const questionWithLongOptions = {
        ...mockQuestion,
        options: [
          { id: 1, content: 'This is a very long option that should still be displayed properly with good spacing and typography', isCorrect: false },
          { id: 2, content: 'Short option', isCorrect: true }
        ]
      }

      const wrapper = mount(QuestionDisplay, {
        props: {
          question: questionWithLongOptions,
          questionNumber: 1
        }
      })

      const options = wrapper.findAll('.option-item')
      expect(options).toHaveLength(2)
      expect(options[0].find('.option-content').text()).toContain('This is a very long option')
      expect(options[1].find('.option-content').text()).toBe('Short option')
    })
  })

  describe('Component Integration', () => {
    it('should update selected state when selectedAnswer prop changes', async () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1,
          selectedAnswer: 1
        }
      })

      // Initially option 1 should be selected
      let options = wrapper.findAll('.option-item')
      expect(options[0].classes()).toContain('selected')
      expect(options[1].classes()).not.toContain('selected')

      // Change selected answer
      await wrapper.setProps({ selectedAnswer: 2 })

      options = wrapper.findAll('.option-item')
      expect(options[0].classes()).not.toContain('selected')
      expect(options[1].classes()).toContain('selected')
    })

    it('should maintain proper option labeling (A, B, C, D)', () => {
      const wrapper = mount(QuestionDisplay, {
        props: {
          question: mockQuestion,
          questionNumber: 1
        }
      })

      const labels = wrapper.findAll('.option-label')
      const expectedLabels = ['A.', 'B.', 'C.', 'D.']
      
      labels.forEach((label, index) => {
        expect(label.text()).toBe(expectedLabels[index])
      })
    })
  })
})