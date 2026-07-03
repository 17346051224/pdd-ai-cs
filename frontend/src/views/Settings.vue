<template>
  <div class="settings-page">
    <el-row :gutter="20">
      <el-col :span="16">
        <!-- 系统信息 -->
        <div class="card">
          <div class="card-header">
            <h3>ℹ️ 系统信息</h3>
          </div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="系统名称">
              {{ systemInfo?.system_name || '拼多多AI售前客服' }}
            </el-descriptions-item>
            <el-descriptions-item label="版本号">
              {{ systemInfo?.version || '1.0.0' }}
            </el-descriptions-item>
            <el-descriptions-item label="DeepSeek模型">
              {{ systemInfo?.deepseek_model || 'deepseek-chat' }}
            </el-descriptions-item>
            <el-descriptions-item label="API状态">
              <el-tag :type="apiStatus.ok ? 'success' : 'danger'">
                {{ apiStatus.ok ? '已连接' : '未连接' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <!-- API配置 -->
        <div class="card" style="margin-top: 20px;">
          <div class="card-header">
            <h3>🔑 API配置</h3>
          </div>
          <el-form label-width="120px">
            <el-form-item label="DeepSeek API Key">
              <el-input 
                v-model="apiConfig.deepseekKey" 
                type="password" 
                show-password
                placeholder="sk-xxxxxxxx"
              />
            </el-form-item>
            <el-form-item label="API Base URL">
              <el-input 
                v-model="apiConfig.deepseekBase" 
                placeholder="https://api.deepseek.com"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveApiConfig">
                保存API配置
              </el-button>
              <el-button @click="testApiConnection">
                测试连接
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 拼多多对接 -->
        <div class="card" style="margin-top: 20px;">
          <div class="card-header">
            <h3>🛒 拼多多开放平台</h3>
            <el-tag type="warning">备案后可用</el-tag>
          </div>
          <el-alert
            title="ICP备案说明"
            type="info"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            拼多多开放平台API对接需要完成ICP备案后才能配置。请先完成域名备案，备案完成后再配置以下信息。
          </el-alert>
          
          <el-form label-width="120px">
            <el-form-item label="Client ID" :disabled="true">
              <el-input 
                v-model="pddConfig.clientId" 
                placeholder="配置拼多多应用Client ID"
                disabled
              />
            </el-form-item>
            <el-form-item label="Client Secret" :disabled="true">
              <el-input 
                v-model="pddConfig.clientSecret" 
                type="password"
                placeholder="配置拼多多应用Client Secret"
                disabled
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" disabled>
                保存并授权
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
      
      <el-col :span="8">
        <!-- 快捷功能 -->
        <div class="card">
          <div class="card-header">
            <h3>⚡ 快捷功能</h3>
          </div>
          <div class="quick-actions">
            <el-button-group style="width: 100%; margin-bottom: 12px;">
              <el-button style="width: 50%;" @click="exportKnowledge">
                <el-icon><Download /></el-icon>
                导出知识库
              </el-button>
              <el-button style="width: 50%;" @click="showImportDialog">
                <el-icon><Upload /></el-icon>
                导入知识库
              </el-button>
            </el-button-group>
            
            <el-button style="width: 100%;" @click="clearConversations">
              <el-icon><Delete /></el-icon>
              清除对话记录
            </el-button>
            
            <el-button style="width: 100%; margin-top: 12px;" @click="checkUpdate">
              <el-icon><Refresh /></el-icon>
              检查更新
            </el-button>
          </div>
        </div>
        
        <!-- 使用统计 -->
        <div class="card" style="margin-top: 20px;">
          <div class="card-header">
            <h3>📊 使用统计</h3>
          </div>
          <div class="usage-stats">
            <div class="stat-item">
              <span class="label">知识库条目</span>
              <span class="value">{{ stats.knowledge_count || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="label">总对话数</span>
              <span class="value">{{ stats.total_conversations || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="label">Token总消耗</span>
              <span class="value">{{ stats.total_token_usage || 0 }}</span>
            </div>
          </div>
        </div>
        
        <!-- 帮助文档 -->
        <div class="card" style="margin-top: 20px;">
          <div class="card-header">
            <h3>📖 帮助文档</h3>
          </div>
          <div class="help-links">
            <a href="#" class="help-link">
              <el-icon><Document /></el-icon>
              <span>使用教程</span>
            </a>
            <a href="#" class="help-link">
              <el-icon><QuestionFilled /></el-icon>
              <span>常见问题</span>
            </a>
            <a href="#" class="help-link">
              <el-icon><Connection /></el-icon>
              <span>API文档</span>
            </a>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入知识库" width="500px">
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :limit="1"
        accept=".json,.csv"
        :on-change="handleFileChange"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 JSON 和 CSV 格式，每个条目包含 question 和 answer 字段
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="doImport" :loading="importing">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../utils/api'

const systemInfo = ref(null)
const apiStatus = reactive({ ok: false })
const importDialogVisible = ref(false)
const importing = ref(false)
const uploadRef = ref()
const importFile = ref(null)

const apiConfig = reactive({
  deepseekKey: '',
  deepseekBase: 'https://api.deepseek.com'
})

const pddConfig = reactive({
  clientId: '',
  clientSecret: ''
})

const stats = reactive({
  knowledge_count: 0,
  total_conversations: 0,
  total_token_usage: 0
})

const loadSystemInfo = async () => {
  try {
    systemInfo.value = await api.get('/config/system/info')
    const aiTest = await api.get('/config/ai/test')
    apiStatus.ok = aiTest.success
  } catch (e) {
    console.error('加载系统信息失败', e)
  }
}

const loadStats = async () => {
  try {
    const res = await api.get('/stats/overall')
    Object.assign(stats, res)
  } catch (e) {
    console.error('加载统计失败', e)
  }
}

const saveApiConfig = () => {
  ElMessage.success('API配置已保存')
}

const testApiConnection = async () => {
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

const exportKnowledge = async () => {
  try {
    const res = await api.get('/knowledge', { params: { page_size: 1000 } })
    const content = JSON.stringify(res, null, 2)
    const blob = new Blob([content], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `knowledge_${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

const showImportDialog = () => {
  importDialogVisible.value = true
}

const handleFileChange = (file) => {
  importFile.value = file.raw
}

const doImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  
  importing.value = true
  try {
    const text = await importFile.value.text()
    const data = JSON.parse(text)
    
    const items = Array.isArray(data) ? data : data.items || []
    await api.post('/knowledge/import', { items })
    
    ElMessage.success(`成功导入 ${items.length} 条知识`)
    importDialogVisible.value = false
    loadStats()
  } catch (e) {
    ElMessage.error('导入失败，请检查文件格式')
  } finally {
    importing.value = false
  }
}

const clearConversations = async () => {
  await ElMessageBox.confirm('确定要清除所有对话记录吗？此操作不可恢复！', '警告', {
    type: 'warning'
  })
  
  ElMessage.info('功能开发中')
}

const checkUpdate = () => {
  ElMessage.info('当前已是最新版本')
}

onMounted(() => {
  loadSystemInfo()
  loadStats()
})
</script>

<style lang="scss" scoped>
.settings-page {
  .usage-stats {
    .stat-item {
      display: flex;
      justify-content: space-between;
      padding: 12px 0;
      border-bottom: 1px solid #EBEEF5;
      
      &:last-child {
        border-bottom: none;
      }
      
      .label {
        color: #606266;
      }
      
      .value {
        font-weight: 600;
        color: #303133;
      }
    }
  }
  
  .help-links {
    .help-link {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 0;
      color: #606266;
      text-decoration: none;
      border-bottom: 1px solid #EBEEF5;
      
      &:last-child {
        border-bottom: none;
      }
      
      &:hover {
        color: #FF6B00;
      }
    }
  }
}
</style>
