/**
 * Unit tests for TimerComponent timer expiration and auto-submission
 * Requirements: 3.4, 3.5
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import TimerComponent from './TimerComponent.vue'

describe('TimerComponent', () => {
  let wrapper
  
  beforeEach(() => {
    vi.useFakeTimers()
  })
  
  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.runOnlyPendingTimers()
    vi.useRealTimers()
  })

  describe('Timer Expiration and Auto-submission', () => {
    it('should emit time-expired event when timer reaches zero', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 3, // 3 seconds
          isActive: true
        }
      })

      // Fast-forward time to just before expiration
      vi.advanceTimersByTime(2000) // 2 seconds
      await wrapper.vm.$nextTick()

      // Verify timer hasn't expired yet
      expect(wrapper.emitted('time-expired')).toBeFalsy()

      // Fast-forward to expiration
      vi.advanceTimersByTime(1000) // 1 more second
      await wrapper.vm.$nextTick()

      // Verify time-expired event was emitted
      expect(wrapper.emitted('time-expired')).toBeTruthy()
      expect(wrapper.emitted('time-expired')).toHaveLength(1)
    })

    it('should stop timer automatically when time expires', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 2, // 2 seconds
          isActive: true
        }
      })

      // Fast-forward to expiration
      vi.advanceTimersByTime(2000)
      await wrapper.vm.$nextTick()

      // Timer should have stopped - advancing more time shouldn't trigger more events
      vi.advanceTimersByTime(5000)
      await wrapper.vm.$nextTick()

      // Should only have emitted time-expired once
      expect(wrapper.emitted('time-expired')).toHaveLength(1)
    })

    it('should emit time-warning event at 5 minutes remaining', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 310, // 5 minutes 10 seconds
          isActive: true
        }
      })

      // Fast-forward to 5 minutes remaining
      vi.advanceTimersByTime(10000) // 10 seconds
      await wrapper.vm.$nextTick()

      // Verify time-warning event was emitted
      expect(wrapper.emitted('time-warning')).toBeTruthy()
      expect(wrapper.emitted('time-warning')).toHaveLength(1)
      expect(wrapper.emitted('time-warning')[0][0]).toBe(300) // 5 minutes in seconds
    })

    it('should emit time-critical event at 1 minute remaining', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 70, // 1 minute 10 seconds
          isActive: true
        }
      })

      // Fast-forward to 1 minute remaining
      vi.advanceTimersByTime(10000) // 10 seconds
      await wrapper.vm.$nextTick()

      // Verify time-critical event was emitted
      expect(wrapper.emitted('time-critical')).toBeTruthy()
      expect(wrapper.emitted('time-critical')).toHaveLength(1)
      expect(wrapper.emitted('time-critical')[0][0]).toBe(60) // 1 minute in seconds
    })

    it('should not start timer when isActive is false', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 5,
          isActive: false
        }
      })

      // Fast-forward time
      vi.advanceTimersByTime(6000)
      await wrapper.vm.$nextTick()

      // No events should be emitted since timer wasn't active
      expect(wrapper.emitted('time-expired')).toBeFalsy()
      expect(wrapper.emitted('time-warning')).toBeFalsy()
      expect(wrapper.emitted('time-critical')).toBeFalsy()
    })

    it('should start timer when isActive changes from false to true', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 3,
          isActive: false
        }
      })

      // Change isActive to true
      await wrapper.setProps({ isActive: true })

      // Fast-forward to expiration
      vi.advanceTimersByTime(3000)
      await wrapper.vm.$nextTick()

      // Timer should have expired
      expect(wrapper.emitted('time-expired')).toBeTruthy()
    })

    it('should stop timer when isActive changes from true to false', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 5,
          isActive: true
        }
      })

      // Fast-forward partway
      vi.advanceTimersByTime(2000)
      await wrapper.vm.$nextTick()

      // Stop the timer
      await wrapper.setProps({ isActive: false })

      // Fast-forward past original expiration time
      vi.advanceTimersByTime(4000)
      await wrapper.vm.$nextTick()

      // Timer should not have expired since it was stopped
      expect(wrapper.emitted('time-expired')).toBeFalsy()
    })

    it('should reset timer when timeLimit prop changes', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 5,
          isActive: true
        }
      })

      // Fast-forward partway
      vi.advanceTimersByTime(2000)
      await wrapper.vm.$nextTick()

      // Change time limit
      await wrapper.setProps({ timeLimit: 10 })

      // The timer display should show new time limit
      expect(wrapper.find('.timer-value').text()).toBe('00:10')
    })

    it('should display correct time format throughout countdown', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 125, // 2:05
          isActive: true
        }
      })

      // Initial display
      expect(wrapper.find('.timer-value').text()).toBe('02:05')

      // After 1 second
      vi.advanceTimersByTime(1000)
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.timer-value').text()).toBe('02:04')

      // After 65 seconds (1:00 remaining)
      vi.advanceTimersByTime(64000)
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.timer-value').text()).toBe('01:00')

      // After 124 seconds (0:01 remaining)
      vi.advanceTimersByTime(59000)
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.timer-value').text()).toBe('00:01')
    })

    it('should apply correct CSS classes based on time remaining', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 400, // 6:40 - normal state
          isActive: true
        }
      })

      // Should start in normal state
      expect(wrapper.find('.timer-component').classes()).toContain('normal')

      // Fast-forward to warning state (5 minutes remaining)
      vi.advanceTimersByTime(100000) // 100 seconds
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.timer-component').classes()).toContain('warning')

      // Fast-forward to danger state (1 minute remaining)
      vi.advanceTimersByTime(240000) // 240 more seconds
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.timer-component').classes()).toContain('danger')
    })
  })

  describe('Timer Component Integration', () => {
    it('should handle rapid prop changes without errors', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 10,
          isActive: false
        }
      })

      // Rapidly change props
      await wrapper.setProps({ isActive: true })
      await wrapper.setProps({ timeLimit: 20 })
      await wrapper.setProps({ isActive: false })
      await wrapper.setProps({ isActive: true })

      // Should not throw errors and should display correct time
      expect(wrapper.find('.timer-value').text()).toBe('00:20')
      
      // Fast-forward to verify timer works
      vi.advanceTimersByTime(20000)
      await wrapper.vm.$nextTick()
      expect(wrapper.emitted('time-expired')).toBeTruthy()
    })

    it('should cleanup timer on component unmount', async () => {
      wrapper = mount(TimerComponent, {
        props: {
          timeLimit: 10,
          isActive: true
        }
      })

      // Spy on clearInterval to verify cleanup
      const clearIntervalSpy = vi.spyOn(global, 'clearInterval')

      // Unmount component
      wrapper.unmount()

      // Verify clearInterval was called
      expect(clearIntervalSpy).toHaveBeenCalled()
    })
  })
})