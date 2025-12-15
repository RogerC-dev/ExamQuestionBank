<template>
    <div class="question-filter-panel">
        <h2 v-if="showTitle" class="filter-title">{{ title }}</h2>

        <div class="filter-grid">
            <!-- Subject Filter (Text Input) -->
            <div v-if="showSubjectFilter" class="filter-item">
                <label class="filter-label">科目</label>
                <input v-model="localFilters.subject" type="text" class="filter-input" placeholder="輸入科目名稱..."
                    @input="emitUpdate" />
            </div>

            <!-- Difficulty Filter -->
            <div v-if="showDifficultyFilter" class="filter-item">
                <label class="filter-label">難度</label>
                <select v-model="localFilters.difficulty" class="filter-select" @change="emitUpdate">
                    <option value="">全部難度</option>
                    <option value="easy">簡單</option>
                    <option value="medium">中等</option>
                    <option value="hard">困難</option>
                </select>
            </div>

            <!-- Source Filter -->
            <div v-if="showSourceFilter" class="filter-item">
                <label class="filter-label">題目來源</label>
                <select v-model="localFilters.source" class="filter-select" @change="emitUpdate">
                    <option value="all">全部題目</option>
                    <option value="wrong">錯題本</option>
                    <option value="bookmark">收藏題目</option>
                </select>
            </div>

            <!-- Keyword Search -->
            <div v-if="showKeywordSearch" class="filter-item filter-item-wide">
                <label class="filter-label">關鍵字搜尋</label>
                <div class="search-input-wrapper">
                    <input v-model="localFilters.search" type="text" class="filter-input" placeholder="搜尋題目內容..."
                        @keyup.enter="handleSearch" @input="emitUpdate" />
                    <button class="search-btn" @click="handleSearch" :disabled="loading">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="m21 21-4.35-4.35"></path>
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        <!-- Tag Filter -->
        <div v-if="showTagFilter" class="filter-row">
            <TagFilter v-model="localFilters.tags" v-model:mode="localFilters.tag_mode" :options="tags"
                placeholder="選擇標籤篩選..." @update:modelValue="emitUpdate" @update:mode="emitUpdate" />
        </div>

        <!-- Filter Actions -->
        <div class="filter-actions">
            <button class="btn btn-secondary" @click="handleReset">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2">
                    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
                    <path d="M3 3v5h5"></path>
                </svg>
                重設篩選
            </button>
            <span v-if="showResultCount" class="result-count">找到 {{ totalCount }} 題</span>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import TagFilter from './TagFilter.vue'

const props = defineProps({
    modelValue: {
        type: Object,
        default: () => ({
            subject: '',
            difficulty: '',
            search: '',
            tags: [],
            tag_mode: 'or',
            source: 'all'
        })
    },
    tags: {
        type: Array,
        default: () => []
    },
    loading: {
        type: Boolean,
        default: false
    },
    totalCount: {
        type: Number,
        default: 0
    },
    showTitle: {
        type: Boolean,
        default: true
    },
    title: {
        type: String,
        default: '篩選題目'
    },
    showSubjectFilter: {
        type: Boolean,
        default: true
    },
    showDifficultyFilter: {
        type: Boolean,
        default: true
    },
    showTagFilter: {
        type: Boolean,
        default: true
    },
    showKeywordSearch: {
        type: Boolean,
        default: true
    },
    showResultCount: {
        type: Boolean,
        default: true
    },
    showSourceFilter: {
        type: Boolean,
        default: true
    }
})

const emit = defineEmits(['update:modelValue', 'search', 'reset'])

const localFilters = ref({ ...props.modelValue })

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
    localFilters.value = { ...newVal }
}, { deep: true })

const emitUpdate = () => {
    emit('update:modelValue', { ...localFilters.value })
}

const handleSearch = () => {
    emitUpdate()
    emit('search')
}

const handleReset = () => {
    localFilters.value = {
        subject: '',
        difficulty: '',
        search: '',
        tags: [],
        tag_mode: 'or',
        source: 'all'
    }
    emitUpdate()
    emit('reset')
}
</script>

<style scoped>
.question-filter-panel {
    background: var(--surface, #FFFFFF);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-title {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary, #1E293B);
    margin: 0 0 20px 0;
}

.filter-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin-bottom: 16px;
}

.filter-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.filter-item-wide {
    grid-column: span 2;
}

.filter-label {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary, #1E293B);
}

.filter-select,
.filter-input {
    padding: 10px 12px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 14px;
    background: #f9fafb;
    transition: all 0.2s;
}

.filter-select:focus,
.filter-input:focus {
    outline: none;
    border-color: var(--primary, #476996);
    background: white;
    box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.search-input-wrapper {
    position: relative;
    display: flex;
    gap: 8px;
}

.search-input-wrapper .filter-input {
    flex: 1;
}

.search-btn {
    padding: 10px 16px;
    background: var(--primary, #476996);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
}

.search-btn:hover:not(:disabled) {
    background: var(--primary-hover, #35527a);
}

.search-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.filter-row {
    margin-bottom: 16px;
}

.filter-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 16px;
    border-top: 1px solid #e5e7eb;
}

.btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-secondary {
    background: #f3f4f6;
    color: var(--text-secondary, #64748B);
}

.btn-secondary:hover {
    background: #e5e7eb;
    color: var(--text-primary, #1E293B);
}

.result-count {
    font-size: 14px;
    color: var(--text-secondary, #64748B);
    font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
    .filter-grid {
        grid-template-columns: 1fr;
    }

    .filter-item-wide {
        grid-column: span 1;
    }

    .filter-actions {
        flex-direction: column;
        gap: 12px;
        align-items: stretch;
    }

    .result-count {
        text-align: center;
    }
}
</style>
