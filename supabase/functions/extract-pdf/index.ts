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

// Import PDF.js for Deno
import * as pdfjsLib from 'https://cdn.skypack.dev/pdfjs-dist@3.11.174/legacy/build/pdf.mjs'

/**
 * Extract text from PDF using PDF.js
 */
async function extractTextFromPdf(uint8Array: Uint8Array): Promise<string> {
    // Load the PDF document
    const loadingTask = pdfjsLib.getDocument({ data: uint8Array })
    const pdf = await loadingTask.promise

    let fullText = ''

    // Extract text from each page
    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum)
        const textContent = await page.getTextContent()

        // Concatenate text items
        const pageText = textContent.items
            .map((item: { str: string }) => item.str)
            .join(' ')

        fullText += pageText + '\n'
    }

    return fullText
}

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

    // Clean up text: normalize whitespace
    const cleanText = text
        .replace(/\r\n/g, '\n')
        .replace(/\r/g, '\n')
        .trim()

    // Split into lines and process
    const lines = cleanText.split('\n')

    let currentQuestion: { number: number; text: string } | null = null

    for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed) continue

        // Check if line starts with a question number (1-3 digits at start)
        const questionStartMatch = trimmed.match(/^(\d{1,3})\s+(.+)/)

        if (questionStartMatch) {
            // Save previous question if exists
            if (currentQuestion) {
                const parsed = parseQuestionBlock(currentQuestion.number, currentQuestion.text)
                if (parsed) questions.push(parsed)
            }

            // Start new question
            currentQuestion = {
                number: parseInt(questionStartMatch[1], 10),
                text: questionStartMatch[2]
            }
        } else if (currentQuestion) {
            // Append to current question
            currentQuestion.text += ' ' + trimmed
        }
    }

    // Don't forget the last question
    if (currentQuestion) {
        const parsed = parseQuestionBlock(currentQuestion.number, currentQuestion.text)
        if (parsed) questions.push(parsed)
    }

    return questions.sort((a, b) => a.number - b.number)
}

/**
 * Parse a single question block to extract content and options
 */
function parseQuestionBlock(number: number, text: string): {
    number: number
    content: string
    options: { label: string; content: string }[]
} | null {
    const options: { label: string; content: string }[] = []

    // Pattern for options: (A), (B), (C), (D) - supports both half-width and full-width
    const optionPattern = /[(\（]([A-DＡ-Ｄ])[\)）]\s*/g

    // Find all option positions
    const optionPositions: { index: number; label: string }[] = []
    let match: RegExpExecArray | null

    while ((match = optionPattern.exec(text)) !== null) {
        const label = match[1]
            .replace('Ａ', 'A')
            .replace('Ｂ', 'B')
            .replace('Ｃ', 'C')
            .replace('Ｄ', 'D')
        optionPositions.push({ index: match.index, label })
    }

    // Extract question content (before first option)
    let questionContent = text
    if (optionPositions.length > 0) {
        questionContent = text.substring(0, optionPositions[0].index).trim()
    }

    // Extract each option's content
    for (let i = 0; i < optionPositions.length; i++) {
        const startPos = optionPositions[i].index
        const endPos = i + 1 < optionPositions.length
            ? optionPositions[i + 1].index
            : text.length

        // Get content after the (X) marker
        const optionText = text.substring(startPos, endPos)
        const contentMatch = optionText.match(/[(\（][A-DＡ-Ｄ][\)）]\s*(.+)/)

        if (contentMatch) {
            options.push({
                label: optionPositions[i].label,
                content: contentMatch[1].trim()
            })
        }
    }

    // Only return if we have valid content
    if (questionContent.length < 5 && options.length === 0) {
        return null
    }

    return { number, content: questionContent, options }
}

/**
 * Parse answer key from PDF text
 * Format: 第1題-A, 第2題-D... or table with 題號/答案
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
    const pattern1 = /第\s*(\d{1,3})\s*題\s*[：:\-\s]*([A-DＡ-Ｄ])/g

    let match: RegExpExecArray | null
    while ((match = pattern1.exec(cleanText)) !== null) {
        const number = parseInt(match[1], 10)
        const answer = normalizeAnswer(match[2])
        answers.push({ number, answer })
    }

    // If pattern 1 found answers, return them
    if (answers.length > 0) {
        return dedupeAnswers(answers)
    }

    // Pattern 2: Look for "答案" rows in tables
    // Matches patterns like: "答案 A D B D A D A D A B"
    const answerRowMatch = cleanText.match(/答案\s+([A-DＡ-Ｄ\s]+)/g)
    if (answerRowMatch) {
        let questionNum = 1
        for (const row of answerRowMatch) {
            const answersInRow = row.replace(/答案\s*/, '').trim().split(/\s+/)
            for (const ans of answersInRow) {
                if (/^[A-DＡ-Ｄ]$/.test(ans)) {
                    answers.push({ number: questionNum++, answer: normalizeAnswer(ans) })
                }
            }
        }
    }

    return dedupeAnswers(answers)
}

function normalizeAnswer(ans: string): string {
    return ans
        .replace('Ａ', 'A')
        .replace('Ｂ', 'B')
        .replace('Ｃ', 'C')
        .replace('Ｄ', 'D')
}

function dedupeAnswers(answers: { number: number; answer: string }[]) {
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
 */
function parseExamMetadata(text: string): {
    year?: string
    examType?: string
    subject?: string
    code?: string
} {
    const metadata: { year?: string; examType?: string; subject?: string; code?: string } = {}

    const yearMatch = text.match(/(\d{2,4})年/)
    if (yearMatch) metadata.year = yearMatch[1]

    const codeMatch = text.match(/代號[：:]\s*(\d+)/)
    if (codeMatch) metadata.code = codeMatch[1]

    if (text.includes('司法官')) metadata.examType = '司法官考試'
    else if (text.includes('律師')) metadata.examType = '律師考試'

    const subjectMatch = text.match(/科目[：:]\s*([^\n]+)/)
    if (subjectMatch) metadata.subject = subjectMatch[1].trim()

    return metadata
}

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

        // Extract text from PDF
        let extractedText: string
        try {
            extractedText = await extractTextFromPdf(uint8Array)
        } catch (pdfError) {
            console.error('PDF text extraction error:', pdfError)
            return new Response(
                JSON.stringify({ error: 'PDF 無法解析，請確認檔案格式正確' }),
                { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )
        }

        console.log(`Extracted ${extractedText.length} characters`)

        if (type === 'questions') {
            const questions = parseQuestions(extractedText)
            const metadata = parseExamMetadata(extractedText)

            return new Response(
                JSON.stringify({
                    success: true,
                    metadata,
                    count: questions.length,
                    questions: questions.map(q => ({
                        number: q.number,
                        content: q.content,
                        options: q.options.map(opt => ({
                            label: opt.label,
                            content: opt.content,
                            is_correct: false
                        })),
                        question_type: q.options.length > 0 ? '選擇題' : '申論題',
                        difficulty: 'medium'
                    })),
                    raw_text_preview: extractedText.substring(0, 500)
                }),
                { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
            )

        } else if (type === 'answers') {
            const answers = parseAnswers(extractedText)
            const metadata = parseExamMetadata(extractedText)

            return new Response(
                JSON.stringify({
                    success: true,
                    metadata,
                    count: answers.length,
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
