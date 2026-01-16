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

import { parseAnswersFromBuffer } from './parse_answers.js'
import { parseQuestionsFromBuffer } from './pdf_parser.js'

serve(async (req) => {
    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        return new Response('ok', { headers: corsHeaders })
    }

    try {
        const formData = await req.formData()
        const file = formData.get('file') as File | null
        const type = formData.get('type') as string | null

        if (!file) {
            return new Response(
                JSON.stringify({ error: '請上傳 PDF 檔案' }),
                { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )
        }

        const arrayBuffer = await file.arrayBuffer()
        const uint8Array = new Uint8Array(arrayBuffer)

        console.log(`Processing PDF: ${file.name}, size: ${uint8Array.length} bytes, type: ${type}`)

        if (type === 'questions') {
            let parsed
            try {
                parsed = await parseQuestionsFromBuffer(arrayBuffer)
            } catch (pdfError) {
                console.error('PDF text extraction error:', pdfError)
                return new Response(
                    JSON.stringify({ error: 'PDF 無法解析，請確認檔案格式正確' }),
                    { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
                )
            }

            const { questions, ...metadata } = parsed
            const normalizedQuestions = questions.map((q, index) => ({
                number: q.number ?? index + 1,
                question: q.question ?? q.content ?? '',
                content: q.question ?? q.content ?? '',
                options: Array.isArray(q.options) ? q.options : []
            }))

            return new Response(
                JSON.stringify({
                    success: true,
                    metadata,
                    ...metadata,
                    count: normalizedQuestions.length,
                    questions: normalizedQuestions
                }),
                { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )

        } else if (type === 'answers') {
            let parsed
            try {
                parsed = await parseAnswersFromBuffer(arrayBuffer)
            } catch (pdfError) {
                console.error('PDF text extraction error:', pdfError)
                return new Response(
                    JSON.stringify({ error: 'PDF 無法解析，請確認檔案格式正確' }),
                    { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
                )
            }

            const answers = Array.isArray(parsed.answers) ? parsed.answers : []

            return new Response(
                JSON.stringify({
                    success: true,
                    count: answers.length,
                    ...parsed,
                    answers
                }),
                { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )

        } else {
            return new Response(
                JSON.stringify({ error: '請指定類型: questions 或 answers' }),
                { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )
        }

    } catch (error) {
        console.error('PDF processing error:', error)
        return new Response(
            JSON.stringify({ error: error.message || 'PDF 處理失敗' }),
            { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
    }
})
