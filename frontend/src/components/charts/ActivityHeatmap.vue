<template>
    <div class="activity-heatmap">
        <div class="heatmap-header">
            <h4><i class="bi bi-calendar3"></i> 學習活動</h4>
            <div class="legend">
                <span class="legend-label">少</span>
                <div class="legend-box level-0"></div>
                <div class="legend-box level-1"></div>
                <div class="legend-box level-2"></div>
                <div class="legend-box level-3"></div>
                <div class="legend-box level-4"></div>
                <span class="legend-label">多</span>
            </div>
        </div>

        <div class="heatmap-container">
            <div class="months-row">
                <div v-for="month in monthLabels" :key="month.key" class="month-label"
                    :style="{ width: month.weeks * 15 + 'px' }">
                    {{ month.label }}
                </div>
            </div>

            <div class="heatmap-grid">
                <div class="weekday-labels">
                    <span></span>
                    <span>一</span>
                    <span></span>
                    <span>三</span>
                    <span></span>
                    <span>五</span>
                    <span></span>
                </div>

                <div class="weeks-grid">
                    <div v-for="(week, weekIdx) in weeksData" :key="weekIdx" class="week-column">
                        <div v-for="(day, dayIdx) in week" :key="dayIdx" class="day-cell" :class="getDayClass(day)"
                            :title="getDayTooltip(day)" @mouseenter="hoveredDay = day" @mouseleave="hoveredDay = null">
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="hoveredDay && hoveredDay.date" class="heatmap-tooltip">
            <strong>{{ formatDate(hoveredDay.date) }}</strong>
            <span>{{ hoveredDay.count }} 次練習</span>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
    data: {
        type: Array,
        default: () => []
    }
})

const hoveredDay = ref(null)

// Generate 52 weeks of data
const weeksData = computed(() => {
    const today = new Date()
    const weeks = []
    const dataMap = new Map()

    // Create map from props data
    props.data.forEach(item => {
        const dateStr = item.date?.split('T')[0]
        if (dateStr) {
            dataMap.set(dateStr, item.attempts || item.count || 0)
        }
    })

    // Generate 52 weeks (364 days)
    const startDate = new Date(today)
    startDate.setDate(startDate.getDate() - 364 + (7 - startDate.getDay()))

    for (let w = 0; w < 52; w++) {
        const week = []
        for (let d = 0; d < 7; d++) {
            const date = new Date(startDate)
            date.setDate(date.getDate() + w * 7 + d)
            const dateStr = date.toISOString().split('T')[0]
            const count = dataMap.get(dateStr) || 0

            week.push({
                date: dateStr,
                count,
                isFuture: date > today
            })
        }
        weeks.push(week)
    }

    return weeks
})

// Month labels
const monthLabels = computed(() => {
    const months = []
    const today = new Date()
    const startDate = new Date(today)
    startDate.setDate(startDate.getDate() - 364)

    let currentMonth = -1
    let weekCount = 0

    for (let w = 0; w < 52; w++) {
        const weekStart = new Date(startDate)
        weekStart.setDate(weekStart.getDate() + w * 7)
        const month = weekStart.getMonth()

        if (month !== currentMonth) {
            if (currentMonth !== -1) {
                months[months.length - 1].weeks = weekCount
            }
            months.push({
                key: `${month}-${weekStart.getFullYear()}`,
                label: weekStart.toLocaleDateString('zh-TW', { month: 'short' }),
                weeks: 0
            })
            currentMonth = month
            weekCount = 1
        } else {
            weekCount++
        }
    }
    if (months.length > 0) {
        months[months.length - 1].weeks = weekCount
    }

    return months
})

const getDayClass = (day) => {
    if (!day || day.isFuture) return 'level-empty'
    const count = day.count
    if (count === 0) return 'level-0'
    if (count <= 5) return 'level-1'
    if (count <= 15) return 'level-2'
    if (count <= 30) return 'level-3'
    return 'level-4'
}

const getDayTooltip = (day) => {
    if (!day || !day.date) return ''
    return `${formatDate(day.date)}: ${day.count} 次練習`
}

const formatDate = (dateStr) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    })
}
</script>

<style scoped>
.activity-heatmap {
    position: relative;
}

.heatmap-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.heatmap-header h4 {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}

.heatmap-header h4 i {
    color: var(--primary);
}

.legend {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    color: var(--text-secondary);
}

.legend-box {
    width: 12px;
    height: 12px;
    border-radius: 2px;
}

.heatmap-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    overflow-x: auto;
    padding-bottom: 8px;
}

.months-row {
    display: flex;
    margin-left: 28px;
    margin-bottom: 4px;
    font-size: 11px;
    color: var(--text-secondary);
}

.month-label {
    text-align: left;
    flex-shrink: 0;
}

.heatmap-grid {
    display: flex;
    gap: 4px;
}

.weekday-labels {
    display: flex;
    flex-direction: column;
    gap: 2px;
    font-size: 10px;
    color: var(--text-secondary);
    width: 24px;
}

.weekday-labels span {
    height: 12px;
    line-height: 12px;
    text-align: right;
    padding-right: 4px;
}

.weeks-grid {
    display: flex;
    gap: 3px;
}

.week-column {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.day-cell {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    cursor: pointer;
    transition: transform 0.1s;
}

.day-cell:hover {
    transform: scale(1.2);
}

.day-cell.level-empty {
    background: transparent;
}

.day-cell.level-0 {
    background: #ebedf0;
}

.day-cell.level-1 {
    background: #9be9a8;
}

.day-cell.level-2 {
    background: #40c463;
}

.day-cell.level-3 {
    background: #30a14e;
}

.day-cell.level-4 {
    background: #216e39;
}

.legend-box.level-0 {
    background: #ebedf0;
}

.legend-box.level-1 {
    background: #9be9a8;
}

.legend-box.level-2 {
    background: #40c463;
}

.legend-box.level-3 {
    background: #30a14e;
}

.legend-box.level-4 {
    background: #216e39;
}

.heatmap-tooltip {
    position: absolute;
    bottom: -40px;
    left: 50%;
    transform: translateX(-50%);
    background: #24292f;
    color: #fff;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 12px;
    display: flex;
    flex-direction: column;
    gap: 2px;
    white-space: nowrap;
    z-index: 10;
}

@media (max-width: 768px) {
    .day-cell {
        width: 10px;
        height: 10px;
    }

    .legend-box {
        width: 10px;
        height: 10px;
    }
}
</style>
