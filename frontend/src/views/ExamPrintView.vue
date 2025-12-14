<template>
    <div class="exam-print-container">
        <!-- Loading State -->
        <div v-if="isLoading" class="loading-state">
            <div class="spinner"></div>
            <p>載入考卷資料中...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="error-state">
            <p>{{ error }}</p>
            <button @click="loadExam">重試</button>
        </div>

        <!-- Print Content -->
        <div v-else-if="exam" class="exam-print-content" :class="{ 'hide-points': !showPoints }" ref="printContent">
            <!-- Header -->
            <header class="print-header">
                <h1 class="exam-title">{{ exam.name }}</h1>
                <p v-if="exam.description" class="exam-description">{{ exam.description }}</p>
                <div class="exam-meta">
                    <span v-if="exam.time_limit">時間限制：{{ exam.time_limit }} 分鐘</span>
                    <span>題數：{{ questions.length }} 題</span>
                    <span>總分：{{ totalScore }} 分</span>
                    <span>列印日期：{{ printDate }}</span>
                </div>
                <div v-if="showScoreBox" class="score-box no-break">
                    <div class="score-label">分數</div>
                    <div class="score-value"></div>
                </div>
            </header>

            <!-- Answer Sheet Section -->
            <section v-if="showAnswerSheet" class="answer-sheet-section no-break">
                <h2>作答欄</h2>
                <div class="answer-grid">
                    <div v-for="(q, index) in questions" :key="'answer-' + index" class="answer-item">
                        <span class="answer-number">{{ index + 1 }}.</span>
                        <span class="answer-options">
                            <span v-for="(opt, optIndex) in getOptionLabels(q.options?.length || 4)" :key="optIndex"
                                class="answer-option-circle">
                                {{ opt }}
                            </span>
                        </span>
                    </div>
                </div>
            </section>

            <!-- Questions Section -->
            <section class="questions-section">
                <!-- Page Break Instruction for Screen -->
                <div class="print-hint no-print">
                    * 列印時每 10 題會自動分頁，可於預覽時確認
                </div>

                <article v-for="(question, index) in questions" :key="index"
                    :class="['question-item', { 'page-break-before': shouldBreakBefore(index) }]">
                    <header class="question-header">
                        <span class="question-number">{{ index + 1 }}.</span>
                        <span v-if="showPoints && question.points" class="question-points">({{ question.points }}
                            分)</span>
                        <span v-if="question.subject" class="question-subject">【{{ question.subject }}】</span>
                        <span v-if="question.category" class="question-category">[{{ question.category }}]</span>
                    </header>
                    <div class="question-content">
                        <div class="question-text" v-html="formatContent(question.content)"></div>
                        <ul v-if="question.options && question.options.length" class="options-list">
                            <li v-for="(option, optIndex) in question.options" :key="optIndex" class="option-item">
                                <span class="option-label">({{ getOptionLabel(optIndex) }})</span>
                                <span class="option-text">{{ option.content || option.text }}</span>
                            </li>
                        </ul>
                    </div>
                </article>
            </section>

            <!-- Appendix: Answer Key & Explanations -->
            <section v-if="showAnswerKey || showExplanation" class="appendix-section page-break-before">
                <h2 class="appendix-title">
                    {{ showAnswerKey && showExplanation ? '參考答案與詳解' : (showAnswerKey ? '參考答案' : '詳解') }}
                </h2>

                <div class="appendix-content">
                    <div v-for="(question, index) in questions" :key="'key-' + index" class="appendix-item no-break">
                        <div class="appendix-header">
                            <span class="appendix-number">{{ index + 1 }}.</span>
                            <span v-if="showAnswerKey" class="appendix-answer">
                                答案：<strong>{{ getCorrectAnswer(question) }}</strong>
                            </span>
                        </div>
                        <div v-if="showExplanation && (question.explanation || question.resolution)"
                            class="appendix-explanation">
                            <span class="explanation-label">詳解：</span>
                            <div class="explanation-text"
                                v-html="formatContent(question.explanation || question.resolution)"></div>
                        </div>
                        <div v-else-if="showExplanation" class="appendix-explanation text-muted">
                            <span class="explanation-label">詳解：</span>無詳解
                        </div>
                    </div>
                </div>
            </section>
        </div>

        <!-- Print Controls (hidden when printing) -->
        <div class="controls-panel no-print">
            <h3>列印設定</h3>

            <div class="control-group">
                <label class="toggle-label">
                    <input type="checkbox" v-model="showAnswerSheet" />
                    <span>顯示作答欄</span>
                </label>
                <label class="toggle-label">
                    <input type="checkbox" v-model="showScoreBox" />
                    <span>顯示分數格</span>
                </label>
            </div>

            <div class="control-group">
                <label class="toggle-label">
                    <input type="checkbox" v-model="showAnswerKey" />
                    <span>包含參考答案</span>
                </label>
                <label class="toggle-label">
                    <input type="checkbox" v-model="showExplanation" />
                    <span>包含詳解</span>
                </label>
            </div>

            <div class="control-group">
                <label class="toggle-label">
                    <input type="checkbox" v-model="showPoints" />
                    <span>顯示配分</span>
                </label>
            </div>

            <div class="control-actions">
                <button @click="handlePrint" class="btn-print">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2">
                        <polyline points="6 9 6 2 18 2 18 9"></polyline>
                        <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                        <rect x="6" y="14" width="12" height="8"></rect>
                    </svg>
                    列印考卷
                </button>
                <button @click="goBack" class="btn-back">關閉</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import examService from '@/services/examService'
import questionService from '@/services/questionService'

const route = useRoute()
const router = useRouter()

const exam = ref(null)
const questions = ref([])
const isLoading = ref(false)
const error = ref('')
const printContent = ref(null)

// Print Settings
const showAnswerSheet = ref(true)
const showAnswerKey = ref(false)
const showExplanation = ref(false)
const showPoints = ref(true)
const showScoreBox = ref(true)

const printDate = computed(() => {
    return new Intl.DateTimeFormat('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(new Date())
})

const totalScore = computed(() => {
    return questions.value.reduce((sum, q) => sum + (Number(q.points) || 0), 0)
})

const getOptionLabel = (index) => {
    return String.fromCharCode(65 + index) // A, B, C, D, ...
}

const getOptionLabels = (count) => {
    const labels = []
    for (let i = 0; i < count; i++) {
        labels.push(getOptionLabel(i))
    }
    return labels
}

const getCorrectAnswer = (question) => {
    if (!question.options) return '-'
    const correctOpts = question.options
        .map((opt, idx) => (opt.is_correct || opt.isCorrect) ? getOptionLabel(idx) : null)
        .filter(Boolean)

    return correctOpts.length ? correctOpts.join('、') : '-'
}

const shouldBreakBefore = (index) => {
    // Add page break every 10 questions (adjust based on content density)
    return index > 0 && index % 10 === 0
}

const formatContent = (content) => {
    if (!content) return ''
    // Convert newlines to <br> for HTML display
    return content.replace(/\n/g, '<br>')
}

const loadExam = async () => {
    isLoading.value = true
    error.value = ''

    try {
        const examId = route.params.id
        const { data } = await examService.getExam(examId)
        exam.value = data

        // Load detailed question data with options
        const questionPromises = (data.exam_questions || []).map(async (eq, index) => {
            try {
                if (eq.question) {
                    const { data: questionData } = await questionService.getQuestion(eq.question)
                    return {
                        ...eq, // id, order, points
                        ...questionData, // content, options, explanation, etc.
                        points: eq.points
                    }
                }
                return {
                    ...eq,
                    content: eq.question_content,
                    options: [],
                }
            } catch (err) {
                console.error(`Failed to load question ${eq.question}`, err)
                return {
                    ...eq,
                    content: eq.question_content || '無法載入題目內容',
                    options: []
                }
            }
        })

        questions.value = await Promise.all(questionPromises)
    } catch (err) {
        console.error('Failed to load exam:', err)
        error.value = err.response?.data?.detail || '無法載入考卷資料'
    } finally {
        isLoading.value = false
    }
}

const handlePrint = () => {
    window.print()
}

const goBack = () => {
    window.close()
}

onMounted(() => {
    loadExam()
})
</script>

<style>
/* Print-specific styles */
@media print {
    @page {
        size: A4;
        margin: 15mm;
    }

    .no-print {
        display: none !important;
    }

    body {
        background: white;
        margin: 0;
        padding: 0;
        font-family: "Times New Roman", "DFKai-SB", sans-serif;
        /* Times + BiauKai is standard for exams */
        -webkit-print-color-adjust: exact;
    }

    .exam-print-container {
        padding: 0;
        background: white;
    }

    .exam-print-content {
        padding: 0;
        max-width: none;
        box-shadow: none;
    }

    .page-break-before {
        page-break-before: always;
    }

    .no-break {
        page-break-inside: avoid;
    }

    .print-header {
        border-bottom: 2px solid #000;
        margin-bottom: 20px;
        padding-bottom: 10px;
    }

    .exam-title {
        font-size: 20pt;
        text-align: center;
    }
}

/* Screen styles */
.exam-print-container {
    min-height: 100vh;
    background: #eef2f6;
    display: flex;
    justify-content: center;
    padding: 30px;
    padding-right: 300px;
    /* Space for controls */
}

.exam-print-content {
    width: 210mm;
    min-height: 297mm;
    background: white;
    padding: 20mm;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
    position: relative;
    /* For print layout simulation */
}

/* Header */
.print-header {
    text-align: center;
    border-bottom: 2px solid #000;
    padding-bottom: 16px;
    margin-bottom: 24px;
    position: relative;
}

.exam-title {
    font-size: 24px;
    font-weight: 700;
    margin: 0 0 10px 0;
    color: #000;
}

.exam-description {
    font-size: 14px;
    color: #444;
    margin: 0 0 12px 0;
}

.exam-meta {
    display: flex;
    justify-content: center;
    gap: 20px;
    font-size: 13px;
    color: #333;
}

.score-box {
    position: absolute;
    top: 0;
    right: 0;
    border: 1px solid #000;
    width: 80px;
    text-align: center;
}

.score-label {
    border-bottom: 1px solid #000;
    padding: 4px;
    font-size: 12px;
}

.score-value {
    height: 40px;
}

/* Answer Sheet */
.answer-sheet-section {
    margin-bottom: 30px;
    padding: 16px;
    border: 1px solid #000;
    background: #fff;
}

.answer-sheet-section h2 {
    font-size: 16px;
    font-weight: 700;
    margin: 0 0 12px 0;
    text-align: center;
    border-bottom: 1px dashed #999;
    padding-bottom: 8px;
}

.answer-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 8px 16px;
}

.answer-item {
    display: flex;
    align-items: center;
    gap: 8px;
}

.answer-number {
    font-weight: 700;
    min-width: 24px;
    font-size: 14px;
}

.answer-options {
    display: flex;
    gap: 4px;
}

.answer-option-circle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border: 1px solid #333;
    border-radius: 50%;
    font-size: 11px;
    line-height: 1;
}

/* Questions */
.questions-section {
    margin-top: 20px;
}

.print-hint {
    background: #fff3cd;
    color: #856404;
    padding: 8px 12px;
    margin-bottom: 16px;
    border-radius: 4px;
    font-size: 13px;
    text-align: center;
}

.question-item {
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px dashed #ddd;
}

.question-item:last-child {
    border-bottom: none;
}

.question-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    flex-wrap: wrap;
}

.question-number {
    font-size: 16px;
    font-weight: 700;
}

.question-points {
    font-size: 13px;
    color: #666;
}

.question-subject,
.question-category {
    font-size: 12px;
    background: #eee;
    padding: 2px 6px;
    border-radius: 4px;
    color: #444;
}

.question-content {
    padding-left: 0;
}

.question-text {
    font-size: 15px;
    line-height: 1.6;
    margin-bottom: 12px;
    color: #000;
}

.options-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    /* Two columns for options */
    gap: 8px 20px;
}

.option-item {
    display: flex;
    gap: 6px;
    font-size: 14px;
}

.option-label {
    font-weight: 600;
}

/* Appendix (Answers & Explanations) */
.appendix-section {
    margin-top: 40px;
    border-top: 3px double #000;
    padding-top: 20px;
}

.appendix-title {
    font-size: 18px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 20px;
}

.appendix-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.appendix-item {
    padding: 8px 0;
    border-bottom: 1px dotted #ccc;
}

.appendix-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 6px;
}

.appendix-number {
    font-weight: 700;
}

.appendix-answer {
    font-size: 14px;
}

.appendix-explanation {
    font-size: 13px;
    color: #444;
    padding: 8px;
    background: #f9f9f9;
    border-left: 3px solid #ccc;
    margin-top: 4px;
}

.explanation-label {
    font-weight: 700;
    color: #000;
}

/* Controls Panel (Fixed Right) */
.controls-panel {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 250px;
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    z-index: 100;
    max-height: calc(100vh - 40px);
    overflow-y: auto;
}

.controls-panel h3 {
    font-size: 16px;
    font-weight: 700;
    margin: 0 0 16px 0;
    color: #1a1a1a;
    border-bottom: 1px solid #eee;
    padding-bottom: 8px;
}

.control-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #f0f0f0;
}

.toggle-label {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    color: #333;
    cursor: pointer;
    user-select: none;
}

.toggle-label input {
    width: 16px;
    height: 16px;
    accent-color: #476996;
    cursor: pointer;
}

.btn-print {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px;
    background: #476996;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 12px;
}

.btn-print:hover {
    background: #35527a;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(71, 105, 150, 0.2);
}

.btn-back {
    width: 100%;
    padding: 10px;
    background: #f0f0f0;
    color: #555;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    cursor: pointer;
    transition: background 0.2s;
}

.btn-back:hover {
    background: #e0e0e0;
}

/* Loading & Error */
.loading-state,
.error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    width: 100%;
    background: #f8fafc;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e0e0e0;
    border-top-color: #476996;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
</style>
