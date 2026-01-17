/**
 * API Service - Supabase Backend Configuration
 * 
 * This file is for the Supabase branch.
 */
import { callEdgeFunction } from '@/lib/supabase'

// Helper to convert params to query string
const buildQuery = (params) => {
    if (!params || Object.keys(params).length === 0) return ''
    const query = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
            query.append(key, value)
        }
    })
    return `?${query.toString()}`
}

// Create an axios-like API object for compatibility
const supabaseApi = {
    async get(path, options = {}) {
        const { params } = options
        const [, functionName, ...rest] = path.split('/').filter(Boolean)
        const subPath = rest.length ? `/${rest.join('/')}` : ''
        const data = await callEdgeFunction(`${functionName}${subPath}${buildQuery(params)}`, {
            method: 'GET'
        })
        return { data }
    },

    async post(path, body = {}, options = {}) {
        const [, functionName, ...rest] = path.split('/').filter(Boolean)
        const subPath = rest.length ? `/${rest.join('/')}` : ''
        const data = await callEdgeFunction(`${functionName}${subPath}`, {
            method: 'POST',
            body: JSON.stringify(body)
        })
        return { data }
    },

    async patch(path, body = {}, options = {}) {
        const [, functionName, ...rest] = path.split('/').filter(Boolean)
        const subPath = rest.length ? `/${rest.join('/')}` : ''
        const data = await callEdgeFunction(`${functionName}${subPath}`, {
            method: 'PATCH',
            body: JSON.stringify(body)
        })
        return { data }
    },

    async put(path, body = {}, options = {}) {
        const [, functionName, ...rest] = path.split('/').filter(Boolean)
        const subPath = rest.length ? `/${rest.join('/')}` : ''
        const data = await callEdgeFunction(`${functionName}${subPath}`, {
            method: 'PUT',
            body: JSON.stringify(body)
        })
        return { data }
    },

    async delete(path, options = {}) {
        const { params } = options
        const [, functionName, ...rest] = path.split('/').filter(Boolean)
        const subPath = rest.length ? `/${rest.join('/')}` : ''
        const data = await callEdgeFunction(`${functionName}${subPath}${buildQuery(params)}`, {
            method: 'DELETE'
        })
        return { data }
    }
}

const fetchSubjects = () => supabaseApi.get('/question_bank/subjects/')

export { fetchSubjects, USE_SUPABASE: true }
export default supabaseApi
