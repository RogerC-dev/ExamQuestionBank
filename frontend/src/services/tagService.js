/**
 * Tag Service - Supabase Direct Client
 * No Django fallback - uses direct Supabase client
 */
import { supabase } from '@/lib/supabase'

const tagService = {
  // Get all tags
  async getTags() {
    const { data, error } = await supabase.from('tag')
      .select('*')
      .order('name')
    if (error) throw new Error(error.message)
    return { data: data || [] }
  },

  // Create tag (admin only)
  async createTag(tagData) {
    const { data, error } = await supabase.from('tag')
      .insert(tagData)
      .select()
      .single()
    if (error) throw new Error(error.message)
    return { data }
  },

  // Update tag (admin only)
  async updateTag(id, tagData) {
    const { data, error } = await supabase.from('tag')
      .update(tagData)
      .eq('id', id)
      .select()
      .single()
    if (error) throw new Error(error.message)
    return { data }
  },

  // Delete tag (admin only)
  async deleteTag(id) {
    const { error } = await supabase.from('tag').delete().eq('id', id)
    if (error) throw new Error(error.message)
    return { success: true }
  }
}

export default tagService
