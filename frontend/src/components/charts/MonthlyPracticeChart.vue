<template>
    <div class="chart-container">
        <div class="chart-header">
            <h4><i class="bi bi-bar-chart-fill"></i> 月度練習統計</h4>
        </div>
        <div class="chart-wrapper">
            <Bar v-if="chartData.labels.length > 0" :data="chartData" :options="chartOptions" />
            <div v-else class="empty-chart">
                <i class="bi bi-bar-chart"></i>
                <p>尚無練習資料</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js'

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
)

const props = defineProps({
    data: {
        type: Array,
        default: () => []
    }
})

const chartData = computed(() => {
    // Group data by month
    const monthlyData = new Map()

    props.data.forEach(item => {
        if (!item.date) return
        const date = new Date(item.date)
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
        const current = monthlyData.get(monthKey) || { attempts: 0, correct: 0 }
        current.attempts += (item.attempts || item.count || 0)
        current.correct += (item.correct || 0)
        monthlyData.set(monthKey, current)
    })

    // Sort by month and get last 12 months
    const sortedMonths = Array.from(monthlyData.entries())
        .sort((a, b) => a[0].localeCompare(b[0]))
        .slice(-12)

    return {
        labels: sortedMonths.map(([month]) => {
            const [year, m] = month.split('-')
            return `${m}月`
        }),
        datasets: [
            {
                label: '練習次數',
                data: sortedMonths.map(([, data]) => data.attempts),
                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                borderColor: '#3b82f6',
                borderWidth: 1,
                borderRadius: 6,
                barThickness: 24
            }
        ]
    }
})

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
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
                label: (context) => `練習次數: ${context.parsed.y}`
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
                font: { size: 11 }
            }
        },
        y: {
            beginAtZero: true,
            grid: {
                color: 'rgba(148, 163, 184, 0.1)'
            },
            ticks: {
                color: '#94a3b8',
                font: { size: 11 },
                stepSize: 1,
                precision: 0
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
