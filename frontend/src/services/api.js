import examService from '@/services/examService'
import questionService from '@/services/questionService'
import tagService from '@/services/tagService'
import { supabase } from '@/lib/supabase'

const normalizePath = (path) => (path.endsWith('/') ? path : `${path}/`)

const notImplemented = (path) => {
  const error = new Error(`Supabase API not implemented: ${path}`)
  error.code = 'SUPABASE_NOT_IMPLEMENTED'
  throw error
}

const fetchSubjects = async () => {
  const { data, error } = await supabase
    .from('question')
    .select('subject')
    .neq('subject', '')
  if (error) throw new Error(error.message)
  const subjects = Array.from(new Set((data || []).map(row => row.subject).filter(Boolean)))
  return { data: subjects }
}

const api = {
  async get(path, config = {}) {
    const normalized = normalizePath(path)
    if (normalized === '/exams/') {
      return examService.getUserExams()
    }
    if (normalized === '/question_bank/tags/') {
      return tagService.getTags()
    }
    if (normalized === '/question_bank/questions/') {
      const params = config?.params || {}
      return questionService.getQuestions({
        subject: params.subject || null,
        difficulty: params.difficulty || null,
        type: params.type || null,
        year: params.year || null,
        keyword: params.keyword || params.search || null,
        page: params.page || 1,
        page_size: params.page_size || 20
      })
    }
    if (normalized === '/question_bank/subjects/') {
      return fetchSubjects()
    }
    return notImplemented(normalized)
  },

  async post(path, body, config = {}) {
    const normalized = normalizePath(path)
    if (normalized === '/exams/') {
      return examService.createExam(body || {})
    }
    return notImplemented(normalized)
  },

  async patch(path, body, config = {}) {
    const normalized = normalizePath(path)
    return notImplemented(normalized)
  },

  async put(path, body, config = {}) {
    const normalized = normalizePath(path)
    return notImplemented(normalized)
  },

  async delete(path, config = {}) {
    const normalized = normalizePath(path)
    const match = normalized.match(/^\/exams\/(\d+)\/$/)
    if (match) {
      return examService.deleteExam(Number(match[1]))
    }
    return notImplemented(normalized)
  }
}

export { fetchSubjects }
export default api
