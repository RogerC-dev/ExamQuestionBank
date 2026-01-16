/**
 * extract-pdf Edge Function
 * 
 * Parses PDF files in memory (no storage) and extracts text/questions.
 * Uses FormData for file upload - no base64 encoding.
 * 
 * Memory only: PDF is processed in memory and discarded after response.
 */

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { corsHeaders } from '../_shared/cors.ts'

// PDF parsing library for Deno
// You may need to import a compatible library:
// - https://deno.land/x/pdfjs_dist (pdf.js port)
// - https://esm.sh/pdf-parse (pdf-parse)

serve(async (req) => {
    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        return new Response('ok', { headers: corsHeaders })
    }

    try {
        // Parse FormData from request
        const formData = await req.formData()
        const file = formData.get('file') as File | null
        const type = formData.get('type') as string | null // 'questions' or 'answers'

        if (!file) {
            return new Response(
                JSON.stringify({ error: '請上傳 PDF 檔案' }),
                { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )
        }

        // Read file into memory as ArrayBuffer
        const arrayBuffer = await file.arrayBuffer()
        const uint8Array = new Uint8Array(arrayBuffer)

        console.log(`Processing PDF: ${file.name}, size: ${uint8Array.length} bytes, type: ${type}`)

        // TODO: Implement PDF parsing here
        // Option 1: Use pdf-parse or similar library
        // Option 2: Use external API for PDF parsing
        // 
        // Example with pdf-parse (if available):
        // const pdfParse = await import('https://esm.sh/pdf-parse')
        // const pdfData = await pdfParse.default(uint8Array)
        // const text = pdfData.text

        // For now, return a placeholder response
        // You need to implement the actual PDF parsing logic

        if (type === 'questions') {
            // Parse exam questions from PDF
            const result = {
                subject: '待解析',
                category: '待解析',
                level: 'medium',
                count: 0,
                questions: [],
                // TODO: Extract actual questions from PDF text
                raw_text: '(PDF 解析功能待實作 - 需要整合 PDF 解析庫)'
            }

            return new Response(
                JSON.stringify(result),
                { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )
        } else if (type === 'answers') {
            // Parse answer key from PDF
            const result = {
                count: 0,
                answers: [],
                // TODO: Extract actual answers from PDF text
                raw_text: '(PDF 解析功能待實作)'
            }

            return new Response(
                JSON.stringify(result),
                { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )
        } else {
            return new Response(
                JSON.stringify({ error: '請指定類型: questions 或 answers' }),
                { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )
        }

        // Memory is freed automatically when function ends
        // No cleanup needed - Deno handles garbage collection

    } catch (error) {
        console.error('PDF 解析錯誤:', error)
        return new Response(
            JSON.stringify({ error: error.message || 'PDF 解析失敗' }),
            { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
    }
})
