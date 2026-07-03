import { defineStore } from 'pinia'
import { api } from '../utils/api'

export const useConfigStore = defineStore('config', {
  state: () => ({
    systemInfo: null,
    aiConfig: null,
    loading: false
  }),
  
  actions: {
    async loadSystemInfo() {
      try {
        const res = await api.get('/config/system/info')
        this.systemInfo = res
      } catch (e) {
        console.error('加载系统信息失败', e)
      }
    },
    
    async loadAIConfig() {
      this.loading = true
      try {
        const res = await api.get('/config/ai')
        this.aiConfig = res
      } finally {
        this.loading = false
      }
    },
    
    async updateAIConfig(data) {
      const res = await api.put('/config/ai', data)
      this.aiConfig = res
      return res
    },
    
    async testAIConnection() {
      return await api.get('/config/ai/test')
    }
  }
})
