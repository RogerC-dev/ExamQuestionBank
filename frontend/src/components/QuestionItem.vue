<template>
  <div
    class="question-item"
    :class="{
      active: isActive,
      pending: item.isPending,
      'has-pending-edit': hasPendingEdit
    }"
    @click="$emit('select', item)"
  >
    <div
      class="question-number"
      :class="{
        pending: item.isPending,
        draft: item.status === 'draft',
        'has-pending-edit': hasPendingEdit && !item.isPending
      }"
    >
      {{ item.order }}
    </div>
    <div class="question-content">
      <div class="question-text">
        {{ item.question_content }}
        <span v-if="item.isPending" class="pending-badge">暫存</span>
        <span v-else-if="hasPendingEdit" class="pending-badge neutral">暫存</span>
      </div>
      <div class="question-meta">
        <span class="badge">{{ item.question_subject }}</span>
        <span class="badge">{{ item.question_category }}</span>
        <span class="points">{{ item.points }} 分</span>
      </div>
    </div>
    <button
      class="btn-delete"
      @click.stop="$emit('remove', item.id)"
      title="移除題目"
    >
      ×
    </button>
  </div>
</template>

<script setup>
defineProps({
  item: {
    type: Object,
    required: true
  },
  isActive: {
    type: Boolean,
    default: false
  },
  hasPendingEdit: {
    type: Boolean,
    default: false
  }
})

defineEmits(['select', 'remove'])
</script>

<style scoped>
.question-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  border: 1px solid #eee;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.question-item:hover {
  border-color: #4CAF50;
  background: #f9f9f9;
}

.question-item.active {
  border-color: #4CAF50;
  background: #e8f5e9;
}

.question-item.pending {
  border-color: #ff9800;
  border-style: dashed;
  background: #fff3e0;
}

.question-item.pending.active {
  background: #ffe0b2;
}

.question-number {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #4CAF50;
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 14px;
}

.question-number.pending {
  background: #ff9800;
}

.pending-badge {
  display: inline-block;
  position: absolute;
  bottom: 10px;
  right: 10px;
  margin-left: 8px;
  padding: 2px 8px;
  background: #ff9800;
  color: white;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.pending-badge.neutral {
  background: #6366f1;
}

.question-item.has-pending-edit:not(.pending) {
  border-color: #6366f1;
  border-style: dashed;
  background: #eef2ff;
}

.question-item.has-pending-edit:not(.pending).active {
  background: #e0e7ff;
}

.question-number.has-pending-edit {
  background: #6366f1;
}

.question-content {
  flex: 1;
  min-width: 0;
}

.question-text {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.question-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 12px;
}

.points {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.btn-delete {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border: none;
  background: #f44336;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  transition: all 0.2s;
  opacity: 0;
}

.question-item:hover .btn-delete {
  opacity: 1;
}

.btn-delete:hover {
  background: #d32f2f;
  transform: scale(1.1);
}
</style>
