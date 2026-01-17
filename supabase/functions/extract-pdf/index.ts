/**
 * extract-pdf Edge Function
 * 
 * Parses Taiwanese Bar Exam PDF files and extracts structured questions.
 * Uses pdfjs-dist (Mozilla's PDF.js) for text extraction - Deno compatible.
 * 
 * Memory only: PDF is processed in memory and discarded after response.
 * Questions are returned for individual database storage.
 */

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { corsHeaders } from '../_shared/cors.ts'

serve(async (req) => {
  // OPTIONS 先回
  if (req.method === 'OPTIONS') {
    return new Response('ok', { status: 200, headers: corsHeaders })
  }

  try {
    const formData = await req.formData()
    const file = formData.get('file') as File | null
    const type = formData.get('type') as string | null

    if (!file) {
      return new Response(JSON.stringify({ error: '請上傳 PDF 檔案' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    const arrayBuffer = await file.arrayBuffer()

    if (type === 'questions') {
      const { parseQuestionsFromBuffer } = await import('./pdf_parser.js')
      const parsed = await parseQuestionsFromBuffer(arrayBuffer)
      return new Response(JSON.stringify(parsed), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    if (type === 'answers') {
      const { parseAnswersFromBuffer } = await import('./parse_answers.js')
      const parsed = await parseAnswersFromBuffer(arrayBuffer)
      return new Response(JSON.stringify(parsed), {
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    return new Response(JSON.stringify({ error: '請指定類型: questions 或 answers' }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  } catch (error) {
    return new Response(JSON.stringify({ error: error?.message || 'PDF 處理失敗' }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})

