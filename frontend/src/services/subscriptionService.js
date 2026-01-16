/**
 * Subscription Service - Placeholder for Supabase
 * Subscription features not yet implemented in Supabase
 */
import { supabase } from '@/lib/supabase'

const subscriptionService = {
  // Get subscription status (placeholder)
  async getSubscription() {
    return { data: { status: 'free', plan: null } }
  },

  // Get available plans (placeholder)
  async getPlans() {
    return { data: [] }
  },

  // Subscribe to plan (placeholder)
  async subscribe(planId) {
    throw new Error('訂閱功能尚未開放')
  }
}

export default subscriptionService
