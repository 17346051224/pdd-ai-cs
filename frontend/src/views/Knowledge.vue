<template>
  <div class="knowledge-page">
    <el-row :gutter="20">
      <el-col :span="16">
        <!-- 搜索和操作栏 -->
        <div class="toolbar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索问题、答案或关键词"
            style="width: 300px;"
            clearable
            @change="loadKnowledge"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <el-select 
            v-model="filterCategory" 
            placeholder="选择分类"
            style="width: 150px;"
            clearable
            @change="loadKnowledge"
          >
            <el-option label="全部" value="" />
            <el-option label="通用" value="general" />
            <el-option label="商品" value="product" />
            <el-option label="FAQ" value="faq" />
            <el-option label="政策" value="policy" />
          </el-select>
          
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加知识
          </el-button>
        </div>
        
        <!-- 知识列表 -->
        <div class="card" style="margin-top: 16px;">
          <el-table 
            :data="knowledgeList" 
            v-loading="loading"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="分类" width="100">
              <template #default="{ row }">
                <el-tag :type="getCategoryType(row.category)">
                  {{ getCategoryLabel(row.category) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="question" label="问题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="answer" label="答案" min-width="250" show-overflow-tooltip />
            <el-table-column prop="priority" label="优先级" width="80" align="center" />
            <el-table-column label="状态" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                  {{ row.is_active ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="editItem(row)">
                  编辑
                </el-button>
                <el-button 
                  :type="row.is_active ? 'warning' : 'success'" 
                  link 
                  size="small"
                  @click="toggleItem(row)"
                >
                  {{ row.is_active ? '禁用' : '启用' }}
                </el-button>
                <el-button type="danger" link size="small" @click="deleteItem(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 分页 -->
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="loadKnowledge"
              @current-change="loadKnowledge"
            />
          </div>
        </div>
      </el-col>
      
      <el-col :span="8">
        <!-- 分类统计 -->
        <div class="card">
          <div class="card-header">
            <h3>📊 分类统计</h3>
          </div>
          <div ref="categoryChartRef" class="category-chart"></div>
        </div>
        
        <!-- 快速添加 -->
        <div class="card" style="margin-top: 20px;">
          <div class="card-header">
            <h3>⚡ 快速添加FAQ</h3>
          </div>
          <div class="quick-faq">
            <el-input
              v-model="quickQuestion"
              type="textarea"
              :rows="2"
              placeholder="输入常见问题..."
            />
            <el-input
              v-model="quickAnswer"
              type="textarea"
              :rows="3"
              placeholder="输入标准答案..."
              style="margin-top: 12px;"
            />
            <el-button 
              type="primary" 
              style="width: 100%; margin-top: 12px;"
              @click="addQuickFaq"
            >
              快速添加
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑知识' : '添加知识'"
      width="600px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="分类">
          <el-select v-model="form.category" style="width: 100%;">
            <el-option label="通用" value="general" />
            <el-option label="商品相关" value="product" />
            <el-option label="常见问题" value="faq" />
            <el-option label="政策规则" value="policy" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题" required>
          <el-input v-model="form.question" placeholder="请输入问题" />
        </el-form-item>
        <el-form-item label="答案" required>
          <el-input 
            v-model="form.answer" 
            type="textarea" 
            :rows="4"
            placeholder="请输入标准答案" 
          />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="form.keywords" placeholder="用逗号分隔关键词，如：价格,运费,优惠" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="form.priority" :min="0" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../utils/api'
import * as echarts from 'echarts'

const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)

const searchKeyword = ref('')
const filterCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const knowledgeList = ref([])
const categories = ref([])

const categoryChartRef = ref()

const form = reactive({
  category: 'general',
  question: '',
  answer: '',
  keywords: '',
  priority: 0
})

const quickQuestion = ref('')
const quickAnswer = ref('')

const getCategoryType = (category) => {
  const types = {
    general: '',
    product: 'success',
    faq: 'warning',
    policy: 'info'
  }
  return types[category] || ''
}

const getCategoryLabel = (category) => {
  const labels = {
    general: '通用',
    product: '商品',
    faq: 'FAQ',
    policy: '政策'
  }
  return labels[category] || category
}

const loadKnowledge = async () => {
  loading.value = true
  try {
    const res = await api.get('/knowledge', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        keyword: searchKeyword.value,
        category: filterCategory.value
      }
    })
    knowledgeList.value = res
    total.value = res.length
  } catch (e) {
    console.error('加载知识库失败', e)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const res = await api.get('/knowledge/categories/list')
    categories.value = res
    updateCategoryChart()
  } catch (e) {
    console.error('加载分类失败', e)
  }
}

const updateCategoryChart = () => {
  if (!categoryChartRef.value) return
  
  const chart = echarts.init(categoryChartRef.value)
  chart.setOption({
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [{
      type: 'pie',
      radius: '60%',
      data: categories.value.map(c => ({
        name: getCategoryLabel(c.category),
        value: c.count
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })
}

const showAddDialog = () => {
  editingId.value = null
  Object.assign(form, {
    category: 'general',
    question: '',
    answer: '',
    keywords: '',
    priority: 0
  })
  dialogVisible.value = true
}

const editItem = (row) => {
  editingId.value = row.id
  Object.assign(form, {
    category: row.category,
    question: row.question,
    answer: row.answer,
    keywords: row.keywords,
    priority: row.priority
  })
  dialogVisible.value = true
}

const saveItem = async () => {
  if (!form.question || !form.answer) {
    ElMessage.warning('请填写问题和答案')
    return
  }
  
  try {
    if (editingId.value) {
      await api.put(`/knowledge/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/knowledge', form)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadKnowledge()
    loadCategories()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const toggleItem = async (row) => {
  try {
    await api.post(`/knowledge/toggle/${row.id}`)
    ElMessage.success(row.is_active ? '已禁用' : '已启用')
    loadKnowledge()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const deleteItem = async (row) => {
  await ElMessageBox.confirm('确定要删除这条知识吗？', '提示', {
    type: 'warning'
  })
  
  try {
    await api.delete(`/knowledge/${row.id}`)
    ElMessage.success('删除成功')
    loadKnowledge()
    loadCategories()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const addQuickFaq = async () => {
  if (!quickQuestion.value || !quickAnswer.value) {
    ElMessage.warning('请填写问题和答案')
    return
  }
  
  try {
    await api.post('/knowledge', {
      category: 'faq',
      question: quickQuestion.value,
      answer: quickAnswer.value
    })
    ElMessage.success('添加成功')
    quickQuestion.value = ''
    quickAnswer.value = ''
    loadKnowledge()
    loadCategories()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

onMounted(() => {
  loadKnowledge()
  loadCategories()
  
  nextTick(() => {
    const chart = echarts.init(categoryChartRef.value)
    window.addEventListener('resize', () => chart.resize())
  })
})
</script>

<style lang="scss" scoped>
.knowledge-page {
  .toolbar {
    display: flex;
    gap: 16px;
    align-items: center;
  }
  
  .pagination-wrapper {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
  
  .category-chart {
    height: 250px;
  }
  
  .quick-faq {
    padding: 8px 0;
  }
}
</style>
