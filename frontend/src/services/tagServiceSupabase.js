/**
 * Tag Service - Supabase Direct Client Version
 * Uses direct Supabase client for simple CRUD
 */
import { supabase } from '@/lib/supabase'

const tagService = {
    /**
     * Get all tags
     */
    async getTags() {
        const { data, error } = await supabase.from('tag')
            .select('*')
            .order('name')

        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Create tag
     */
    async createTag(tagData) {
        const { data, error } = await supabase.from('tag')
            .insert(tagData)
            .select()
            .single()

        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Update tag
     */
    async updateTag(id, tagData) {
        const { data, error } = await supabase.from('tag')
            .update(tagData)
            .eq('id', id)
            .select()
            .single()

        if (error) throw new Error(error.message)
        return { data }
    },

    /**
     * Delete tag
     */
    async deleteTag(id) {
        const { error } = await supabase.from('tag').delete().eq('id', id)
        if (error) throw new Error(error.message)
        return { success: true }
    }
}

export default tagService
