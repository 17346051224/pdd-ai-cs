<template>
  <div class="ai-config">
    <el-row :gutter="20">
      <el-col :span="16">
        <!-- AI人设配置 -->
        <div class="card">
          <div class="card-header">
            <h3>🤖 AI人设配置</h3>
          </div>
          <el-form :model="form" label-width="100px">
            <el-form-item label="系统提示词">
              <el-input
                v-model="form.system_prompt"
                type="textarea"
                :rows="8"
                placeholder="设置AI客服的角色定位和行为规范..."
              />
            </el-form-item>
            
            <el-form-item label="回复风格">
              <el-radio-group v-model="form.reply_style">
                <el-radio label="friendly">热情友好</el-radio>
                <el-radio label="professional">专业严谨</el-radio>
                <el-radio label="casual">轻松随意</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="温度参数">
              <el-slider 
                v-model="form.temperature"
                :min="0" 
                :max="2" 
                :step="0.1"
                show-input
              />
              <div class="slider-hint">
                较低值更确定性，较高值更有创造性
              </div>
            </el-form-item>
            
            <el-form-item label="最大Token">
              <el-input-number 
                v-model="form.max_tokens" 
                :min="100" 
                :max="4000" 
                :step="100"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="saveConfig">
                保存配置
              </el-button>
              <el-button @click="resetConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 快捷提示词 -->
        <div class="card" style="margin-top: 20px;">
          <div class="card-header">
            <h3>💡 预设提示词模板</h3>
          </div>
          <div class="preset-list">
            <el-card 
              v-for="(preset, index) in presets" 
              :key="index"
              class="preset-item"
              shadow="hover"
              @click="applyPreset(preset)"
            >
              <h4>{{ preset.name }}</h4>
              <p>{{ preset.description }}</p>
            </el-card>
          </div>
        </div>
      </el-col>
      
      <el-col :span="8">
        <!-- 配置状态 -->
        <div class="card">
          <div class="card-header">
            <h3>🔧 服务状态</h3>
          </div>
          <div class="status-list">
            <div class="status-item">
              <span class="label">DeepSeek API</span>
              <el-tag :type="apiStatus.ok ? 'success' : 'danger'">
                {{ apiStatus.ok ? '已连接' : '未连接' }}
              </el-tag>
            </div>
            <div class="status-item">
              <span class="label">AI模型</span>
              <span class="value">deepseek-chat</span>
            </div>
            <div class="status-item">
              <span class="label">回复策略</span>
              <span class="value">{{ form.reply_style === 'friendly' ? '热情友好' : form.reply_style === 'professional' ? '专业严谨' : '轻松随意' }}</span>
            </div>
          </div>
          <el-button type="primary" plain style="width: 100%; margin-top: 16px;" @click="testConnection">
            测试API连接
          </el-button>
        </div>
        
        <!-- 回复设置 -->
        <div class="card" style="margin-top: 20px;">
          <div class="card-header">
            <h3>⚙️ 回复策略</h3>
          </div>
          <el-form label-width="100px">
            <el-form-item label="自动回复">
              <el-switch v-model="form.auto_reply" />
            </el-form-item>
            <el-form-item label="转人工阈值">
              <el-input-number 
                v-model="form.transfer_threshold" 
                :min="0" 
                :max="10" 
              />
              <div class="form-hint">连续无法回答N次后转人工</div>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
    </el-row>
    
    <!-- 测试对话框 -->
    <div class="card" style="margin-top: 20px;">
      <div class="card-header">
        <h3>🧪 对话测试</h3>
      </div>
      <div class="test-chat">
        <div class="chat-messages" ref="chatRef">
          <div 
            v-for="(msg, index) in testMessages" 
            :key="index"
            :class="['message', msg.role]"
          >
            <div class="message-content">{{ msg.content }}</div>
          </div>
        </div>
        <div class="chat-input">
          <el-input
            v-model="testInput"
            placeholder="输入测试消息..."
            @keyup.enter="sendTest"
          >
            <template #append>
              <el-button :disabled="testLoading" @click="sendTest">
                {{ testLoading ? '发送中...' : '发送' }}
              </el-button>
            </template>
          </el-input>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../utils/api'

const saving = ref(false)
const chatRef = ref()
const testInput = ref('')
const testLoading = ref(false)
const testMessages = ref([
  { role: 'assistant', content: '你好！我是你的AI客服助手，请输入消息进行测试。' }
])

const apiStatus = reactive({
  ok: true
})

const form = reactive({
  system_prompt: '',
  temperature: 0.7,
  max_tokens: 1000,
  reply_style: 'friendly',
  auto_reply: true,
  transfer_threshold: 3
})

const presets = [
  {
    name: '标准售前客服',
    description: '热情专业，解答商品疑问，引导下单',
    prompt: `你是一个专业的拼多多店铺售前客服助手。你的职责是：
1. 热情友好地接待顾客，解答关于商品的疑问
2. 了解顾客需求，推荐合适的商品
3. 介绍商品的特点、规格、价格、优惠活动
4. 解答物流、发货、售后等问题
5. 引导顾客下单，提供优质的购物体验
请使用友好、专业的语气与顾客交流。`
  },
  {
    name: '耐心解答型',
    description: '详细耐心解答，适合高客单价商品',
    prompt: `你是一个耐心的拼多多店铺客服。你的特点是：
1. 非常耐心，详细解答每一个问题
2. 会主动询问顾客的需求和顾虑
3. 提供全面的商品信息和对比
4. 站在顾客角度考虑问题
5. 不急于推销，让顾客充分了解后再决定
请保持专业且耐心的态度。`
  },
  {
    name: '促销导向型',
    description: '注重优惠推送，提升转化率',
    prompt: `你是一个擅长促销的拼多多售前客服。你的目标是：
1. 热情接待每位顾客
2. 及时介绍当前优惠活动和折扣
3. 强调性价比和限时优惠
4. 适时提醒库存紧张或活动即将结束
5. 灵活运用优惠券促进成交
请在保持友好的同时，注重促销转化。`
  }
]

const loadConfig = async () => {
  try {
    const res = await api.get('/config/ai')
    Object.assign(form, res)
  } catch (e) {
    console.error('加载配置失败', e)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    await api.put('/config/ai', form)
    ElMessage.success('配置保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const resetConfig = () => {
  loadConfig()
}

const applyPreset = (preset) => {
  form.system_prompt = preset.prompt
  ElMessage.success(`已应用"${preset.name}"模板`)
}

const testConnection = async () => {
  try {
    const res = await api.get('/config/ai/test')
    apiStatus.ok = res.success
    if (res.success) {
      ElMessage.success(res.message)
    } else {
      ElMessage.error(res.message)
    }
  } catch (e) {
    apiStatus.ok = false
    ElMessage.error('API连接失败')
  }
}

const sendTest = async () => {
  if (!testInput.value.trim()) return
  
  testMessages.value.push({
    role: 'user',
    content: testInput.value
  })
  
  const input = testInput.value
  testInput.value = ''
  testLoading.value = true
  
  await nextTick()
  chatRef.value.scrollTop = chatRef.value.scrollHeight
  
  try {
    const res = await api.post('/chat/chat', {
      message: input,
      session_id: 'test-' + Date.now()
    })
    
    testMessages.value.push({
      role: 'assistant',
      content: res.response
    })
  } catch (e) {
    testMessages.value.push({
      role: 'assistant',
      content: '抱歉，发生了错误，请稍后重试。'
    })
  } finally {
    testLoading.value = false
    await nextTick()
    chatRef.value.scrollTop = chatRef.value.scrollHeight
  }
}

onMounted(() => {
  loadConfig()
  testConnection()
})
</script>

<style lang="scss" scoped>
.ai-config {
  .preset-list {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
  
  .preset-item {
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-4px);
    }
    
    h4 {
      margin: 0 0 8px 0;
      color: #FF6B00;
    }
    
    p {
      margin: 0;
      font-size: 13px;
      color: #909399;
    }
  }
  
  .status-list {
    .status-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #EBEEF5;
      
      &:last-child {
        border-bottom: none;
      }
      
      .label {
        color: #606266;
      }
      
      .value {
        font-weight: 500;
      }
    }
  }
  
  .slider-hint, .form-hint {
    font-size: 12px;
    color: #909399;
    margin-top: 8px;
  }
  
  .test-chat {
    .chat-messages {
      height: 300px;
      overflow-y: auto;
      padding: 16px;
      background: #F5F7FA;
      border-radius: 8px;
      margin-bottom: 16px;
    }
    
    .message {
      margin-bottom: 16px;
      
      &.user {
        text-align: right;
        
        .message-content {
          background: #FF6B00;
          color: white;
          display: inline-block;
          padding: 10px 16px;
          border-radius: 12px 12px 0 12px;
          max-width: 70%;
        }
      }
      
      &.assistant {
        text-align: left;
        
        .message-content {
          background: white;
          color: #303133;
          display: inline-block;
          padding: 10px 16px;
          border-radius: 12px 12px 12px 0;
          max-width: 70%;
        }
      }
    }
  }
}
</style>
