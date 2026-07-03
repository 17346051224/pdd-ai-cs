<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #FF6B00 0%, #FF8C33 100%);">
          <div class="stat-value">{{ stats.today_conversations || 0 }}</div>
          <div class="stat-label">今日对话</div>
          <el-icon class="stat-icon"><ChatDotRound /></el-icon>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #409EFF 0%, #66B1FF 100%);">
          <div class="stat-value">{{ stats.today_messages || 0 }}</div>
          <div class="stat-label">今日消息</div>
          <el-icon class="stat-icon"><Message /></el-icon>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);">
          <div class="stat-value">{{ stats.avg_rating || 0 }}</div>
          <div class="stat-label">平均评分</div>
          <el-icon class="stat-icon"><Star /></el-icon>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card" style="background: linear-gradient(135deg, #909399 0%, #A6A9AD 100%);">
          <div class="stat-value">{{ stats.total_token_usage || 0 }}</div>
          <div class="stat-label">Token消耗</div>
          <el-icon class="stat-icon"><Coin /></el-icon>
        </div>
      </el-col>
    </el-row>
    
    <!-- 图表 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="16">
        <div class="card">
          <div class="card-header">
            <h3>对话趋势</h3>
            <el-radio-group v-model="chartDays" size="small" @change="loadChart">
              <el-radio-button label="7">近7天</el-radio-button>
              <el-radio-button label="30">近30天</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="chartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="card">
          <div class="card-header">
            <h3>系统概览</h3>
          </div>
          <div class="overview-list">
            <div class="overview-item">
              <span class="label">总对话数</span>
              <span class="value">{{ stats.total_conversations || 0 }}</span>
            </div>
            <div class="overview-item">
              <span class="label">总消息数</span>
              <span class="value">{{ stats.total_messages || 0 }}</span>
            </div>
            <div class="overview-item">
              <span class="label">知识库条目</span>
              <span class="value">{{ stats.knowledge_count || 0 }}</span>
            </div>
            <div class="overview-item">
              <span class="label">平均响应</span>
              <span class="value">{{ stats.avg_response_time || 0 }}s</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 快捷入口 -->
    <el-row :gutter="20" class="quick-row">
      <el-col :span="24">
        <div class="card">
          <div class="card-header">
            <h3>快捷操作</h3>
          </div>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/ai-config')">
              <el-icon><Setting /></el-icon>
              AI配置
            </el-button>
            <el-button type="success" @click="$router.push('/knowledge')">
              <el-icon><Collection /></el-icon>
              知识库
            </el-button>
            <el-button type="warning" @click="$router.push('/conversations')">
              <el-icon><ChatLineRound /></el-icon>
              对话记录
            </el-button>
            <el-button type="info" @click="$router.push('/settings')">
              <el-icon><Tools /></el-icon>
              系统设置
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { api } from '../utils/api'
import * as echarts from 'echarts'

const chartRef = ref()
const chartDays = ref('7')
const chartInstance = ref()

const stats = reactive({
  today_conversations: 0,
  today_messages: 0,
  total_conversations: 0,
  total_messages: 0,
  total_token_usage: 0,
  avg_rating: 0,
  avg_response_time: 0,
  knowledge_count: 0
})

const chartData = reactive({
  dates: [],
  conversations: [],
  messages: []
})

const loadStats = async () => {
  try {
    const res = await api.get('/stats/overall')
    Object.assign(stats, res)
  } catch (e) {
    console.error('加载统计数据失败', e)
  }
}

const loadChart = async () => {
  try {
    const res = await api.get('/stats/chart', { params: { days: chartDays.value } })
    chartData.dates = res.dates
    chartData.conversations = res.conversations
    chartData.messages = res.messages
    updateChart()
  } catch (e) {
    console.error('加载图表数据失败', e)
  }
}

const updateChart = () => {
  if (!chartInstance.value) return
  
  chartInstance.value.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['对话数', '消息数']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '对话数',
        type: 'line',
        smooth: true,
        data: chartData.conversations,
        itemStyle: { color: '#FF6B00' },
        areaStyle: { color: 'rgba(255, 107, 0, 0.1)' }
      },
      {
        name: '消息数',
        type: 'line',
        smooth: true,
        data: chartData.messages,
        itemStyle: { color: '#409EFF' },
        areaStyle: { color: 'rgba(64, 158, 255, 0.1)' }
      }
    ]
  })
}

onMounted(async () => {
  await loadStats()
  await loadChart()
  
  nextTick(() => {
    chartInstance.value = echarts.init(chartRef.value)
    updateChart()
    
    window.addEventListener('resize', () => {
      chartInstance.value?.resize()
    })
  })
})
</script>

<style lang="scss" scoped>
.dashboard {
  .stat-row {
    margin-bottom: 20px;
  }
  
  .stat-card {
    position: relative;
    padding: 24px;
    border-radius: 12px;
    color: white;
    overflow: hidden;
    
    .stat-value {
      font-size: 32px;
      font-weight: bold;
      margin-bottom: 8px;
    }
    
    .stat-label {
      font-size: 14px;
      opacity: 0.9;
    }
    
    .stat-icon {
      position: absolute;
      right: 20px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 48px;
      opacity: 0.3;
    }
  }
  
  .chart-row {
    margin-bottom: 20px;
  }
  
  .chart-container {
    height: 300px;
  }
  
  .overview-list {
    .overview-item {
      display: flex;
      justify-content: space-between;
      padding: 16px 0;
      border-bottom: 1px solid #EBEEF5;
      
      &:last-child {
        border-bottom: none;
      }
      
      .label {
        color: #909399;
      }
      
      .value {
        font-weight: 600;
        color: #303133;
      }
    }
  }
  
  .quick-actions {
    display: flex;
    gap: 16px;
    
    .el-button {
      padding: 20px 30px;
      
      .el-icon {
        margin-right: 8px;
      }
    }
  }
}
</style>
