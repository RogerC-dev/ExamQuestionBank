import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ExamPreloader from './ExamPreloader.vue'

describe('ExamPreloader', () => {
  it('displays loading state with spinner and text', () => {
    const wrapper = mount(ExamPreloader, {
      props: {
        isLoading: true,
        loadingText: 'Loading exam questions...'
      }
    })

    expect(wrapper.find('.loading-state').exists()).toBe(true)
    expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    expect(wrapper.find('.loading-text').text()).toBe('Loading exam questions...')
    expect(wrapper.find('.error-state').exists()).toBe(false)
  })

  it('displays error state with message and retry button', () => {
    const retryFn = vi.fn()
    const wrapper = mount(ExamPreloader, {
      props: {
        isLoading: false,
        error: 'Failed to load exam data',
        onRetry: retryFn
      }
    })

    expect(wrapper.find('.error-state').exists()).toBe(true)
    expect(wrapper.find('.error-title').text()).toBe('Loading Failed')
    expect(wrapper.find('.error-message').text()).toBe('Failed to load exam data')
    expect(wrapper.find('.btn-primary').exists()).toBe(true)
    expect(wrapper.find('.loading-state').exists()).toBe(false)
  })

  it('calls retry function when retry button is clicked', async () => {
    const retryFn = vi.fn()
    const wrapper = mount(ExamPreloader, {
      props: {
        isLoading: false,
        error: 'Network error',
        onRetry: retryFn
      }
    })

    await wrapper.find('.btn-primary').trigger('click')
    expect(retryFn).toHaveBeenCalledOnce()
  })

  it('hides retry button when onRetry is not provided', () => {
    const wrapper = mount(ExamPreloader, {
      props: {
        isLoading: false,
        error: 'Some error',
        onRetry: null
      }
    })

    expect(wrapper.find('.btn-primary').exists()).toBe(false)
  })

  it('uses default loading text when not provided', () => {
    const wrapper = mount(ExamPreloader, {
      props: {
        isLoading: true
      }
    })

    expect(wrapper.find('.loading-text').text()).toBe('Loading exam questions...')
  })

  it('displays custom loading text when provided', () => {
    const wrapper = mount(ExamPreloader, {
      props: {
        isLoading: true,
        loadingText: 'Preparing your exam...'
      }
    })

    expect(wrapper.find('.loading-text').text()).toBe('Preparing your exam...')
  })

  it('shows neither loading nor error state when both are false/null', () => {
    const wrapper = mount(ExamPreloader, {
      props: {
        isLoading: false,
        error: null
      }
    })

    expect(wrapper.find('.loading-state').exists()).toBe(false)
    expect(wrapper.find('.error-state').exists()).toBe(false)
  })

  it('prioritizes loading state over error state', () => {
    const wrapper = mount(ExamPreloader, {
      props: {
        isLoading: true,
        error: 'Some error occurred'
      }
    })

    expect(wrapper.find('.loading-state').exists()).toBe(true)
    expect(wrapper.find('.error-state').exists()).toBe(false)
  })
})