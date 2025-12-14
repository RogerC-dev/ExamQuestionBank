<template>
    <div class="chart-container">
        <div class="chart-header">
            <h4><i class="bi bi-graph-up"></i> 正確率趨勢</h4>
            <div class="time-range-selector">
                <button v-for="range in timeRanges" :key="range.value"
                    :class="{ active: selectedRange === range.value }" @click="selectedRange = range.value">
                    {{ range.label }}
                </button>
            </div>
        </div>
        <div class="chart-wrapper">
            <Line v-if="chartData.labels.length > 0" :data="chartData" :options="chartOptions" />
            <div v-else class="empty-chart">
                <i class="bi bi-bar-chart"></i>
                <p>尚無趨勢資料</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js'

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
)

const props = defineProps({
    data: {
        type: Array,
        default: () => []
    }
})

const timeRanges = [
    { label: '7天', value: 7 },
    { label: '30天', value: 30 },
    { label: '全部', value: -1 }
]

const selectedRange = ref(30)

const filteredData = computed(() => {
    if (selectedRange.value === -1 || !props.data.length) {
        return props.data
    }

    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - selectedRange.value)

    return props.data.filter(item => {
        const itemDate = new Date(item.date)
        return itemDate >= cutoff
    })
})

const chartData = computed(() => {
    const sorted = [...filteredData.value].sort((a, b) =>
        new Date(a.date) - new Date(b.date)
    )

    return {
        labels: sorted.map(item => {
            const date = new Date(item.date)
            return date.toLocaleDateString('zh-TW', { month: 'short', day: 'numeric' })
        }),
        datasets: [
            {
                label: '正確率 (%)',
                data: sorted.map(item => item.accuracy ?? 0),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }
        ]
    }
})

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        intersect: false,
        mode: 'index'
    },
    plugins: {
        legend: {
            display: false
        },
        tooltip: {
            backgroundColor: '#1e293b',
            titleColor: '#f8fafc',
            bodyColor: '#e2e8f0',
            padding: 12,
            cornerRadius: 8,
            displayColors: false,
            callbacks: {
                label: (context) => `正確率: ${context.parsed.y.toFixed(1)}%`
            }
        }
    },
    scales: {
        x: {
            grid: {
                display: false
            },
            ticks: {
                color: '#94a3b8',
                font: { size: 11 },
                maxTicksLimit: 7
            }
        },
        y: {
            min: 0,
            max: 100,
            grid: {
                color: 'rgba(148, 163, 184, 0.1)'
            },
            ticks: {
                color: '#94a3b8',
                font: { size: 11 },
                callback: (value) => value + '%'
            }
        }
    }
}
</script>

<style scoped>
.chart-container {
    display: flex;
    flex-direction: column;
}

.chart-wrapper {
    height: 220px;
    position: relative;
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.chart-header h4 {
    margin: 0;
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}

.chart-header h4 i {
    color: var(--primary);
}

.time-range-selector {
    display: flex;
    gap: 4px;
}

.time-range-selector button {
    padding: 4px 12px;
    border: 1px solid #e2e8f0;
    background: #fff;
    border-radius: 6px;
    font-size: 12px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
}

.time-range-selector button:hover {
    background: #f8fafc;
}

.time-range-selector button.active {
    background: var(--primary);
    color: #fff;
    border-color: var(--primary);
}

.empty-chart {
    height: 200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
}

.empty-chart i {
    font-size: 32px;
    margin-bottom: 8px;
    opacity: 0.5;
}
</style>
