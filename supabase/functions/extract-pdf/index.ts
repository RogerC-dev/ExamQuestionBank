/**
 * extract-pdf Edge Function
 * 
 * Parses Taiwanese Bar Exam PDF files and extracts structured questions.
 * Uses pdf-parse for text extraction and regex for question parsing.
 * 
 * Memory only: PDF is processed in memory and discarded after response.
 * Questions are returned for individual database storage.
 */

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { corsHeaders } from '../_shared/cors.ts'

// Import pdf-parse from esm.sh
import pdfParse from 'https://esm.sh/pdf-parse@1.1.1'

/**
 * Parse exam questions from extracted PDF text
 * Format: Numbered questions (1, 2, 3...) with options (A), (B), (C), (D)
 */
function parseQuestions(text: string): Array<{
    number: number
    content: string
    options: { label: string; content: string }[]
}> {
    const questions: Array<{
        number: number
        content: string
        options: { label: string; content: string }[]
    }> = []

    // Clean up text: normalize whitespace and line breaks
    const cleanText = text
        .replace(/\r\n/g, '\n')
        .replace(/\r/g, '\n')
        .replace(/\s+/g, ' ')
        .trim()

    // Pattern to match question numbers (1, 2, 3... at start of question)
    // Taiwanese exam format: number followed by question text
    // Example: "1 憲法本文及增修條文之下列何種規定..."
    const questionPattern = /(?:^|\s)(\d{1,3})\s+([^(（]+?)(?=\s*[(\（][A-DＡ-Ｄ][\)）])/g

    // Alternative pattern for full question blocks
    // Captures question number and everything until next question or end
    const fullQuestionPattern = /(?:^|\n)\s*(\d{1,3})\s+([\s\S]*?)(?=\n\s*\d{1,3}\s+[^\d]|$)/g

    // Pattern for options (A), (B), (C), (D) - supports both half-width and full-width
    const optionPattern = /[(\（]([A-DＡ-Ｄ])[\)）]\s*([^(\（]+?)(?=[(\（][A-DＡ-Ｄ][\)）]|$)/g

    // Try to extract questions using the full pattern
    let match: RegExpExecArray | null
    const questionBlocks: { number: number; rawText: string }[] = []

    // Reset regex
    fullQuestionPattern.lastIndex = 0

    while ((match = fullQuestionPattern.exec(cleanText)) !== null) {
        const qNumber = parseInt(match[1], 10)
        const rawText = match[2].trim()

        // Skip if this looks like page numbers or other artifacts
        if (rawText.length < 10) continue

        questionBlocks.push({ number: qNumber, rawText })
    }

    // If no questions found with full pattern, try simpler approach
    if (questionBlocks.length === 0) {
        // Split by question number pattern and process
        const parts = cleanText.split(/(?=\s\d{1,3}\s+)/)

        for (const part of parts) {
            const numMatch = part.match(/^\s*(\d{1,3})\s+(.+)/)
            if (numMatch) {
                const qNumber = parseInt(numMatch[1], 10)
                const rawText = numMatch[2].trim()
                if (rawText.length >= 10) {
                    questionBlocks.push({ number: qNumber, rawText })
                }
            }
        }
    }

    // Now parse each question block to extract content and options
    for (const block of questionBlocks) {
        const options: { label: string; content: string }[] = []
        let questionContent = block.rawText

        // Extract options
        optionPattern.lastIndex = 0
        let optionMatch: RegExpExecArray | null
        let firstOptionIndex = -1

        while ((optionMatch = optionPattern.exec(block.rawText)) !== null) {
            if (firstOptionIndex === -1) {
                firstOptionIndex = optionMatch.index
            }

            // Normalize option label (full-width to half-width)
            const label = optionMatch[1]
                .replace('Ａ', 'A')
                .replace('Ｂ', 'B')
                .replace('Ｃ', 'C')
                .replace('Ｄ', 'D')

            const content = optionMatch[2].trim()

            if (content.length > 0) {
                options.push({ label, content })
            }
        }

        // Extract question content (text before first option)
        if (firstOptionIndex > 0) {
            questionContent = block.rawText.substring(0, firstOptionIndex).trim()
        }

        // Only add if we have valid content
        if (questionContent.length > 5 || options.length > 0) {
            questions.push({
                number: block.number,
                content: questionContent,
                options: options
            })
        }
    }

    // Sort by question number and ensure no duplicates
    questions.sort((a, b) => a.number - b.number)

    // Remove duplicates based on question number
    const seen = new Set<number>()
    return questions.filter(q => {
        if (seen.has(q.number)) return false
        seen.add(q.number)
        return true
    })
}

/**
 * Parse answer key from PDF text
 * Format: 第1題-A, 第2題-D... or table format with 題號/答案 rows
 */
function parseAnswers(text: string): { number: number; answer: string }[] {
    const answers: { number: number; answer: string }[] = []

    // Clean text
    const cleanText = text
        .replace(/\r\n/g, '\n')
        .replace(/\r/g, '\n')
        .replace(/\s+/g, ' ')
        .trim()

    // Pattern 1: 第N題 followed by answer
    // Example: "第1題 A" or "第1題：A" or "第1題-A"
    const pattern1 = /第\s*(\d{1,3})\s*題\s*[：:\-\s]*([A-DＡ-Ｄ])/g

    // Pattern 2: Simple table format - number followed by answer
    // Matches consecutive number-letter pairs
    const pattern2 = /(?:^|\s)(\d{1,3})\s+([A-DＡ-Ｄ])(?=\s|$)/g

    // Try pattern 1 first
    let match: RegExpExecArray | null
    pattern1.lastIndex = 0

    while ((match = pattern1.exec(cleanText)) !== null) {
        const number = parseInt(match[1], 10)
        const answer = match[2]
            .replace('Ａ', 'A')
            .replace('Ｂ', 'B')
            .replace('Ｃ', 'C')
            .replace('Ｄ', 'D')

        answers.push({ number, answer })
    }

    // If pattern 1 found nothing, try pattern 2
    if (answers.length === 0) {
        pattern2.lastIndex = 0
        while ((match = pattern2.exec(cleanText)) !== null) {
            const number = parseInt(match[1], 10)
            const answer = match[2]
                .replace('Ａ', 'A')
                .replace('Ｂ', 'B')
                .replace('Ｃ', 'C')
                .replace('Ｄ', 'D')

            answers.push({ number, answer })
        }
    }

    // Sort and deduplicate
    answers.sort((a, b) => a.number - b.number)

    const seen = new Set<number>()
    return answers.filter(a => {
        if (seen.has(a.number)) return false
        seen.add(a.number)
        return true
    })
}

/**
 * Extract exam metadata from PDF text
 * Example: 114年公務人員特種考試司法官考試, 代號：2301
 */
function parseExamMetadata(text: string): {
    year?: string
    examType?: string
    subject?: string
    code?: string
    duration?: string
    totalQuestions?: number
    pointsPerQuestion?: number
} {
    const metadata: {
        year?: string
        examType?: string
        subject?: string
        code?: string
        duration?: string
        totalQuestions?: number
        pointsPerQuestion?: number
    } = {}

    // Extract year (e.g., "114年")
    const yearMatch = text.match(/(\d{2,4})年/)
    if (yearMatch) {
        metadata.year = yearMatch[1]
    }

    // Extract exam code (e.g., "代號：2301")
    const codeMatch = text.match(/代號[：:]\s*(\d+)/)
    if (codeMatch) {
        metadata.code = codeMatch[1]
    }

    // Extract duration (e.g., "1小時30分")
    const durationMatch = text.match(/(\d+小時\d*分?)/)
    if (durationMatch) {
        metadata.duration = durationMatch[1]
    }

    // Extract question count (e.g., "單選題數：75題")
    const countMatch = text.match(/(?:單選題數|共)\s*[：:]*\s*(\d+)\s*題/)
    if (countMatch) {
        metadata.totalQuestions = parseInt(countMatch[1], 10)
    }

    // Extract points per question (e.g., "每題配分：2.00分")
    const pointsMatch = text.match(/每題配分[：:]\s*([\d.]+)\s*分/)
    if (pointsMatch) {
        metadata.pointsPerQuestion = parseFloat(pointsMatch[1])
    }

    // Extract exam type
    if (text.includes('司法官考試')) {
        metadata.examType = '司法官考試'
    } else if (text.includes('律師考試')) {
        metadata.examType = '律師考試'
    }

    // Extract subject
    const subjectMatch = text.match(/科目[：:]\s*([^考\n]+)/)
    if (subjectMatch) {
        metadata.subject = subjectMatch[1].trim()
    }

    return metadata
}

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
        const buffer = uint8Array.buffer

        console.log(`Processing PDF: ${file.name}, size: ${uint8Array.length} bytes, type: ${type}`)

        // Parse PDF to extract text
        let pdfData
        try {
            pdfData = await pdfParse(Buffer.from(buffer))
        } catch (pdfError) {
            console.error('PDF parsing error:', pdfError)
            return new Response(
                JSON.stringify({ error: 'PDF 格式無法解析，請確認檔案完整性' }),
                { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )
        }

        const extractedText = pdfData.text
        console.log(`Extracted text length: ${extractedText.length} characters`)

        if (type === 'questions') {
            // Parse exam questions from PDF
            const questions = parseQuestions(extractedText)
            const metadata = parseExamMetadata(extractedText)

            const result = {
                success: true,
                metadata,
                count: questions.length,
                questions: questions.map(q => ({
                    number: q.number,
                    content: q.content,
                    options: q.options.map(opt => ({
                        label: opt.label,
                        content: opt.content,
                        is_correct: false // Will be set when merging with answer key
                    })),
                    question_type: q.options.length > 0 ? '選擇題' : '申論題',
                    difficulty: 'medium'
                })),
                raw_text: extractedText.substring(0, 1000) + '...' // First 1000 chars for debugging
            }

            console.log(`Parsed ${questions.length} questions`)

            return new Response(
                JSON.stringify(result),
                { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )

        } else if (type === 'answers') {
            // Parse answer key from PDF
            const answers = parseAnswers(extractedText)
            const metadata = parseExamMetadata(extractedText)

            const result = {
                success: true,
                metadata,
                count: answers.length,
                answers: answers.map(a => ({
                    number: a.number,
                    answer: a.answer
                })),
                raw_text: extractedText.substring(0, 500) // First 500 chars for debugging
            }

            console.log(`Parsed ${answers.length} answers`)

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

    } catch (error) {
        console.error('PDF 解析錯誤:', error)
        return new Response(
            JSON.stringify({ error: error.message || 'PDF 解析失敗' }),
            { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
    }
})
