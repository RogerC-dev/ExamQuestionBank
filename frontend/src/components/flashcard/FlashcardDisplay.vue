<template>
  <div class="flashcard-card" :class="{ 'is-flipped': isFlipped }">
    <!-- Front Side - Question -->
    <div class="card-side card-front" @click="handleFlip">
      <div class="card-badge">{{ card.question_subject }}</div>
      <div class="card-content">
        <p class="card-question">{{ card.question_content }}</p>
      </div>
      <div v-if="!isFlipped" class="card-hint">
        <i class="bi bi-hand-index-thumb"></i>
        <span>點擊卡片查看答案</span>
      </div>
    </div>

    <!-- Back Side - Answer -->
    <div class="card-side card-back">
      <div class="card-badge answer-badge">答案</div>
      <div class="card-content">
        <div v-if="options.length" class="answer-options">
          <div v-for="(opt, index) in options" :key="opt.id" class="answer-option" :class="{ correct: opt.is_correct }">
            <span class="option-marker">{{ opt.is_correct ? '✓' : '' }}</span>
            <span>{{ getLabel(index) }}. {{ opt.content }}</span>
          </div>
        </div>
        <p v-else class="no-options">無選項資料</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Flashcard, QuestionOption } from '@/types/flashcard'

interface Props {
  card: Flashcard
  options: QuestionOption[]
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'flip'): void
}>()

const isFlipped = ref(false)

const handleFlip = () => {
  // Only flip if currently showing front side
  if (!isFlipped.value) {
    isFlipped.value = true
    emit('flip')
  }
}

const getLabel = (index: number): string => {
  return String.fromCharCode(65 + index)
}

// Reset flip state when card changes
defineExpose({
  resetFlip: () => {
    isFlipped.value = false
  }
})
</script>

<style scoped>
/* Individual Card with 3D Flip */
.flashcard-card {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 0.7s cubic-bezier(0.4, 0.0, 0.2, 1);
  cursor: pointer;
}

.flashcard-card.is-flipped {
  transform: rotateY(180deg);
}

/* Card Sides */
.card-side {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  border-radius: 20px;
  padding: 40px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15), 0 8px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* Front Side - Question (Using Website Theme Colors) */
.card-front {
  background: linear-gradient(135deg, #476996 0%, #35527a 100%);
  color: white;
  z-index: 2;
}

/* Back Side - Answer */
.card-back {
  background: white;
  border: 2px solid #CBD5E1;
  transform: rotateY(180deg);
  color: #1E293B;
}

/* Badge Styling */
.card-badge {
  display: inline-block;
  padding: 8px 18px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 24px;
  align-self: flex-start;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.answer-badge {
  background: linear-gradient(135deg, #476996 0%, #35527a 100%);
  color: white;
}

/* Card Content */
.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

/* Question Text */
.card-question {
  font-size: 24px;
  line-height: 1.6;
  text-align: center;
  word-break: break-word;
  margin: 0;
  font-weight: 500;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

/* Hint Text */
.card-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 15px;
  opacity: 0.95;
  margin-top: 20px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-hint i {
  font-size: 18px;
}

/* Answer Options */
.answer-options {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 5px;
}

/* Custom scrollbar for answer options */
.answer-options::-webkit-scrollbar {
  width: 6px;
}

.answer-options::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.answer-options::-webkit-scrollbar-thumb {
  background: #476996;
  border-radius: 10px;
}

.answer-options::-webkit-scrollbar-thumb:hover {
  background: #35527a;
}

.answer-option {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 20px;
  background: #F8FAFC;
  border: 2px solid #E2E8F0;
  border-radius: 12px;
  font-size: 16px;
  line-height: 1.6;
  word-break: break-word;
  transition: all 0.3s ease;
}

.answer-option:hover {
  background: #EEF2FF;
  border-color: #476996;
  transform: translateX(4px);
}

/* Correct Answer Highlighting */
.answer-option.correct {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  border: 2px solid #10b981;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.option-marker {
  font-weight: 800;
  color: #10b981;
  font-size: 20px;
  min-width: 24px;
  flex-shrink: 0;
}

.no-options {
  text-align: center;
  color: #64748b;
  font-size: 16px;
  margin: 0;
}

/* Responsive Design - Tablet */
@media (max-width: 1024px) {
  .card-side {
    padding: 32px;
  }

  .card-question {
    font-size: 22px;
  }
}

/* Responsive Design - Mobile */
@media (max-width: 768px) {
  .card-side {
    padding: 24px;
    border-radius: 16px;
  }

  .card-badge {
    font-size: 12px;
    padding: 6px 14px;
  }

  .card-question {
    font-size: 18px;
  }

  .card-hint {
    font-size: 13px;
    padding: 10px 16px;
  }

  .answer-option {
    padding: 12px 16px;
    font-size: 14px;
    gap: 10px;
  }
}

/* Small Mobile */
@media (max-width: 480px) {
  .card-side {
    padding: 20px;
  }

  .card-question {
    font-size: 16px;
  }

  .card-hint {
    font-size: 12px;
  }

  .answer-option {
    padding: 10px 14px;
    font-size: 13px;
  }
}

/* Landscape Mobile */
@media (max-width: 768px) and (orientation: landscape) {
  .card-side {
    padding: 16px;
  }
}
</style>
