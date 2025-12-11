import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ExamHeader from './ExamHeader.vue'

describe('ExamHeader', () => {
  it('displays exam metadata when exam data is provided', () => {
    const exam = {
      name: 'Sample Exam',
      description: 'This is a test exam',
      questions: [{ id: 1 }, { id: 2 }, { id: 3 }],
      timeLimit: 60
    }

    const wrapper = mount(ExamHeader, {
      props: { exam }
    })

    expect(wrapper.find('.exam-title').text()).toBe('Sample Exam')
    expect(wrapper.find('.exam-description').text()).toBe('This is a test exam')
    expect(wrapper.find('.question-count').text()).toBe('Questions: 3')
    expect(wrapper.find('.time-limit').text()).toBe('Time Limit: 60 minutes')
  })

  it('displays appropriate placeholders when exam data is missing', () => {
    const wrapper = mount(ExamHeader, {
      props: { exam: null }
    })

    expect(wrapper.find('.exam-title').text()).toBe('Loading exam...')
    expect(wrapper.find('.exam-description').text()).toBe('No description provided')
    expect(wrapper.find('.question-count').text()).toBe('Questions: 0')
    expect(wrapper.find('.time-limit').exists()).toBe(false)
  })

  it('handles partial exam data gracefully', () => {
    const exam = {
      name: 'Partial Exam',
      questions: [{ id: 1 }, { id: 2 }]
      // missing description and timeLimit
    }

    const wrapper = mount(ExamHeader, {
      props: { exam }
    })

    expect(wrapper.find('.exam-title').text()).toBe('Partial Exam')
    expect(wrapper.find('.exam-description').text()).toBe('No description provided')
    expect(wrapper.find('.question-count').text()).toBe('Questions: 2')
    expect(wrapper.find('.time-limit').exists()).toBe(false)
  })

  it('hides time limit when not provided', () => {
    const exam = {
      name: 'No Time Limit Exam',
      description: 'This exam has no time limit',
      questions: [{ id: 1 }]
      // no timeLimit property
    }

    const wrapper = mount(ExamHeader, {
      props: { exam }
    })

    expect(wrapper.find('.time-limit').exists()).toBe(false)
  })

  it('renders actions slot when provided', () => {
    const exam = {
      name: 'Test Exam',
      questions: [{ id: 1 }]
    }

    const wrapper = mount(ExamHeader, {
      props: { exam },
      slots: {
        actions: '<button class="test-action">Start Exam</button>'
      }
    })

    expect(wrapper.find('.test-action').exists()).toBe(true)
    expect(wrapper.find('.test-action').text()).toBe('Start Exam')
  })

  it('applies responsive design classes', () => {
    const exam = {
      name: 'Test Exam',
      questions: [{ id: 1 }]
    }

    const wrapper = mount(ExamHeader, {
      props: { exam }
    })

    expect(wrapper.find('.exam-header').exists()).toBe(true)
    expect(wrapper.find('.exam-info').exists()).toBe(true)
    expect(wrapper.find('.exam-meta').exists()).toBe(true)
  })
})