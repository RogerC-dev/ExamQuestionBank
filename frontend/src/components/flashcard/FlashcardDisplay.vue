<template>
  <div class="card-container">
    <div class="flashcard" :class="{ flipped }" @click="$emit('flip')">
      <!-- Front - Question -->
      <div class="card-face card-front">
        <div class="card-badge">{{ card.question_subject }}</div>
        <div class="card-content">
          <p class="card-question">{{ card.question_content }}</p>
        </div>
        <div v-if="!flipped" class="card-hint">點擊卡片查看答案</div>
      </div>
      <!-- Back - Answer -->
      <div class="card-face card-back">
        <div class="card-badge">答案</div>
        <div class="card-content">
          <div v-if="options.length" class="answer-options">
            <div 
              v-for="opt in options" 
              :key="opt.id" 
              class="answer-option" 
              :class="{ correct: opt.is_correct }"
            >
              <span class="option-marker">{{ opt.is_correct ? '✓' : '' }}</span>
              <span>{{ getLabel(opt.order) }}. {{ opt.content }}</span>
            </div>
          </div>
          <p v-else class="no-options">無選項資料</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Flashcard, QuestionOption } from '@/types/flashcard'

interface Props {
  card: Flashcard
  options: QuestionOption[]
  flipped?: boolean
}

withDefaults(defineProps<Props>(), {
  flipped: false
})

defineEmits<{
  (e: 'flip'): void
}>()

const getLabel = (order: number): string => {
  return String.fromCharCode(64 + (order || 1))
}
</script>

<style scoped>
/* Card Container - enables 3D perspective */
.card-container {
  perspective: 1000px;
  margin-bottom: 30px;
}

/* Flashcard - 3D flip animation */
.flashcard {
  width: 100%;
  height: 400px;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}

.flashcard.flipped {
  transform: rotateY(180deg);
}

/* Card Face - shared styles for front and back */
.card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 12px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

/* Front Face - Question side */
.card-front {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: white;
}

/* Back Face - Answer side */
.card-back {
  background: var(--surface);
  transform: rotateY(180deg);
  border: 1px solid var(--border);
}

/* Badge styling */
.card-badge {
  display: inline-block;
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 20px;
  align-self: flex-start;
}

.card-back .card-badge {
  background: var(--primary-soft);
  color: var(--primary);
}

/* Card content area */
.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card-question {
  font-size: 22px;
  line-height: 1.6;
  text-align: center;
  word-break: break-word;
}

/* Hint text shown when card is not flipped */
.card-hint {
  text-align: center;
  font-size: 14px;
  opacity: 0.7;
}

/* Answer Options styling */
.answer-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.answer-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 18px;
  background: #f7f9fb;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 15px;
  line-height: 1.5;
  word-break: break-word;
}

/* Correct answer highlighting */
.answer-option.correct {
  background: #ecf8f1;
  border: 2px solid #10b981;
}

.option-marker {
  font-weight: bold;
  color: #10b981;
  min-width: 20px;
  flex-shrink: 0;
}

.no-options {
  text-align: center;
  color: var(--text-secondary);
}

/* ========== RESPONSIVE DESIGN ========== */

/* Tablet */
@media (max-width: 1024px) {
  .flashcard {
    height: 380px;
  }
  
  .card-face {
    padding: 28px;
  }
  
  .card-question {
    font-size: 20px;
  }
}

/* Mobile */
@media (max-width: 768px) {
  .card-container {
    margin-bottom: 20px;
  }
  
  .flashcard {
    height: 320px;
  }
  
  .card-face {
    padding: 20px;
  }
  
  .card-badge {
    font-size: 11px;
    padding: 5px 12px;
  }
  
  .card-question {
    font-size: 16px;
  }
  
  .card-hint {
    font-size: 12px;
  }
  
  .answer-option {
    padding: 10px 14px;
    font-size: 14px;
    gap: 8px;
  }
}

/* Small Mobile */
@media (max-width: 480px) {
  .flashcard {
    height: 280px;
  }
  
  .card-face {
    padding: 16px;
  }
  
  .card-question {
    font-size: 15px;
  }
}

/* Landscape Mobile */
@media (max-width: 768px) and (orientation: landscape) {
  .flashcard {
    height: 250px;
  }
}
</style>
