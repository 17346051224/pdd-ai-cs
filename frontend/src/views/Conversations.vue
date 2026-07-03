<template>
  <div class="conversations-page">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索会话内容"
        style="width: 300px;"
        clearable
        @change="loadConversations"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        style="width: 280px;"
        @change="loadConversations"
      />
      
      <el-button @click="loadConversations">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 会话列表 -->
      <el-col :span="8">
        <div class="card session-list">
          <div class="card-header">
            <h3>会话列表</h3>
          </div>
          <div class="session-items">
            <div 
              v-for="session in sessions" 
              :key="session.session_id"
              :class="['session-item', { active: currentSession === session.session_id }]"
              @click="selectSession(session.session_id)"
            >
              <div class="session-header">
                <span class="session-id">{{ session.session_id.substring(0, 8) }}...</span>
                <span class="session-time">{{ formatTime(session.last_time) }}</span>
              </div>
              <div class="session-preview">{{ session.last_message }}</div>
              <div class="session-meta">
                <span>{{ session.message_count }} 条消息</span>
              </div>
            </div>
            
            <div v-if="sessions.length === 0" class="empty-state">
              <el-icon class="empty-icon"><ChatLineRound /></el-icon>
              <p>暂无会话记录</p>
            </div>
          </div>
        </div>
      </el-col>
      
      <!-- 会话详情 -->
      <el-col :span="16">
        <div class="card conversation-detail">
          <div class="card-header">
            <h3>会话详情</h3>
            <div class="header-actions">
              <el-button size="small" @click="exportConversation" :disabled="!currentSession">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
            </div>
          </div>
          
          <div v-if="currentSession" class="chat-container">
            <div class="chat-messages" ref="chatRef">
              <div 
                v-for="(msg, index) in messages" 
                :key="index"
                :class="['message', msg.is_ai_response ? 'ai' : 'user']"
              >
                <div class="message-avatar">
                  <el-avatar :size="36" :icon="msg.is_ai_response ? '🤖' : '👤'" />
                </div>
                <div class="message-body">
                  <div class="message-sender">
                    {{ msg.is_ai_response ? 'AI客服' : '用户' }}
                    <span class="message-time">{{ formatTime(msg.created_at) }}</span>
                  </div>
                  <div class="message-content">{{ msg.is_ai_response ? msg.ai_response : msg.user_message }}</div>
                  <div v-if="msg.is_ai_response && msg.token_count" class="message-meta">
                    消耗 {{ msg.token_count }} tokens · {{ msg.response_time?.toFixed(2) }}s
                  </div>
                  <div v-if="msg.rating" class="message-rating">
                    <el-rate v-model="msg.rating" disabled size="small" />
                    <span v-if="msg.feedback"> - {{ msg.feedback }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state">
            <el-icon class="empty-icon"><ChatDotRound /></el-icon>
            <p>请选择左侧会话查看详情</p>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../utils/api'
import dayjs from 'dayjs'

const loading = ref(false)
const searchKeyword = ref('')
const dateRange = ref([])
const sessions = ref([])
const currentSession = ref(null)
const messages = ref([])
const chatRef = ref()

const loadConversations = async () => {
  loading.value = true
  try {
    const res = await api.get('/chat/sessions')
    sessions.value = res
  } catch (e) {
    console.error('加载会话列表失败', e)
  } finally {
    loading.value = false
  }
}

const selectSession = async (sessionId) => {
  currentSession.value = sessionId
  try {
    const res = await api.get(`/chat/history/${sessionId}`)
    messages.value = res.messages
    await nextTick()
    chatRef.value.scrollTop = chatRef.value.scrollHeight
  } catch (e) {
    ElMessage.error('加载会话详情失败')
  }
}

const formatTime = (time) => {
  if (!time) return ''
  return dayjs(time).format('MM-DD HH:mm')
}

const exportConversation = () => {
  if (!currentSession.value) return
  
  const content = messages.value.map(m => {
    const sender = m.is_ai_response ? 'AI客服' : '用户'
    const msg = m.is_ai_response ? m.ai_response : m.user_message
    return `[${formatTime(m.created_at)}] ${sender}: ${msg}`
  }).join('\n\n')
  
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `conversation_${currentSession.value}.txt`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('导出成功')
}

onMounted(() => {
  loadConversations()
})
</script>

<style lang="scss" scoped>
.conversations-page {
  .filter-bar {
    display: flex;
    gap: 16px;
    align-items: center;
  }
  
  .session-list {
    height: calc(100vh - 200px);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    
    .session-items {
      flex: 1;
      overflow-y: auto;
    }
  }
  
  .session-item {
    padding: 16px;
    border-bottom: 1px solid #EBEEF5;
    cursor: pointer;
    transition: background 0.2s;
    
    &:hover, &.active {
      background: #F5F7FA;
    }
    
    &.active {
      border-left: 3px solid #FF6B00;
    }
    
    .session-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      
      .session-id {
        font-weight: 500;
        color: #303133;
      }
      
      .session-time {
        font-size: 12px;
        color: #909399;
      }
    }
    
    .session-preview {
      font-size: 13px;
      color: #606266;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      margin-bottom: 8px;
    }
    
    .session-meta {
      font-size: 12px;
      color: #C0C4CC;
    }
  }
  
  .conversation-detail {
    height: calc(100vh - 200px);
    display: flex;
    flex-direction: column;
    
    .header-actions {
      display: flex;
      gap: 8px;
    }
    
    .chat-container {
      flex: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    
    .chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      background: #F5F7FA;
      border-radius: 8px;
    }
    
    .message {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      
      &.user {
        flex-direction: row-reverse;
        
        .message-content {
          background: #FF6B00;
          color: white;
          border-radius: 16px 16px 0 16px;
        }
      }
      
      &.ai .message-content {
        background: white;
        border-radius: 16px 16px 16px 0;
      }
      
      .message-body {
        flex: 1;
      }
      
      .message-sender {
        font-size: 12px;
        color: #909399;
        margin-bottom: 4px;
        
        .message-time {
          margin-left: 8px;
        }
      }
      
      .message-content {
        padding: 12px 16px;
        line-height: 1.6;
      }
      
      .message-meta {
        font-size: 11px;
        color: #C0C4CC;
        margin-top: 4px;
      }
      
      .message-rating {
        margin-top: 4px;
      }
    }
  }
}
</style>
