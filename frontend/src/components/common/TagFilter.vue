<template>
    <div class="tag-filter-container">
        <div class="tag-filter-main">
            <div class="input-icon-wrapper">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" class="tags-icon">
                    <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path>
                    <line x1="7" y1="7" x2="7.01" y2="7"></line>
                </svg>
                <multiselect :model-value="modelValue" :options="options" :multiple="true" :close-on-select="false"
                    :clear-on-select="false" :preserve-search="true" :placeholder="placeholder" track-by="id"
                    label="name" class="tag-multiselect" @update:model-value="$emit('update:modelValue', $event)" />

                <!-- Mode Toggle - Absolute positioned inside input -->
                <transition name="fade-slide">
                    <button v-if="modelValue.length > 1" type="button" class="mode-toggle-inside"
                        @click.stop="toggleMode" :class="mode" :title="modeTitle">
                        <span class="mode-text">{{ mode === 'or' ? 'OR' : 'AND' }}</span>
                    </button>
                </transition>
            </div>
        </div>
    </div>
</template>

<script setup>
import Multiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.min.css'
import { computed } from 'vue'

const props = defineProps({
    modelValue: {
        type: Array,
        default: () => []
    },
    mode: {
        type: String,
        default: 'or'
    },
    options: {
        type: Array,
        default: () => []
    },
    placeholder: {
        type: String,
        default: '選擇標籤...'
    }
})

const emit = defineEmits(['update:modelValue', 'update:mode'])

const toggleMode = () => {
    emit('update:mode', props.mode === 'or' ? 'and' : 'or')
}

const modeTitle = computed(() => {
    return props.mode === 'or' ? '目前與 (OR) - 點擊切換為交集' : '目前交集 (AND) - 點擊切換為聯集'
})
</script>

<style scoped>
.tag-filter-container {
    flex: 1;
    min-width: 320px;
}

.tag-filter-main {
    display: flex;
    align-items: center;
    gap: 8px;
    position: relative;
}

.input-icon-wrapper {
    position: relative;
    flex: 1;
}

.tags-icon {
    position: absolute;
    left: 14px;
    top: 16px;
    z-index: 10;
    color: var(--text-secondary, #64748B);
    pointer-events: none;
}

.tag-multiselect {
    width: 100%;
}

.tag-multiselect :deep(.multiselect__placeholder) {
    margin-bottom: 0px;
}

/* Customized Multiselect Styles */
.tag-multiselect :deep(.multiselect__tags) {
    display: flex;
    flex-direction: column;
    border: 2px solid #e5e7eb;
    border-radius: 10px;
    padding: 8px 50px 8px 44px;
    background: #f9fafb;
    min-height: 49px;
    transition: all 0.2s ease;
}

.tag-multiselect :deep(.multiselect__tags):focus-within {
    border-color: var(--primary, #476996);
    background: white;
    box-shadow: 0 0 0 3px rgba(71, 105, 150, 0.1);
}

.tag-multiselect :deep(.multiselect__tag) {
    background: var(--primary, #476996);
    color: white;
    border-radius: 6px;
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: inline-block;
    vertical-align: top;
    padding: 6px 26px 6px 10px;
    margin: 2px 4px 2px 0;
}

.tag-multiselect :deep(.multiselect__tag-icon:after) {
    color: rgba(255, 255, 255, 0.8);
}

.tag-multiselect :deep(.multiselect__tag-icon:hover) {
    background: var(--primary-hover, #35527a);
}

.tag-multiselect :deep(.multiselect__option--highlight) {
    background: var(--primary, #476996);
}

.tag-multiselect :deep(.multiselect__option--selected) {
    background: var(--primary-soft, #EEF2FF);
    color: var(--primary, #476996);
}

/* Mode Toggle Inside */
.mode-toggle-inside {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    height: 24px;
    padding: 0 8px;
    border-radius: 6px;
    border: 1px solid transparent;
    font-size: 11px;
    font-weight: 800;
    cursor: pointer;
    z-index: 55;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
}

.mode-toggle-inside.or {
    background: #e0e7ff;
    color: #4f46e5;
    border-color: #c7d2fe;
}

.mode-toggle-inside.or:hover {
    background: #c7d2fe;
}

.mode-toggle-inside.and {
    background: #dcfce7;
    color: #16a34a;
    border-color: #bbf7d0;
}

.mode-toggle-inside.and:hover {
    background: #bbf7d0;
}

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
    transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
    opacity: 0;
    transform: translateX(-10px);
    width: 0;
    padding: 0;
    margin: 0;
    overflow: hidden;
}
</style>
