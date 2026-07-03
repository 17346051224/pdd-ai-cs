import { defineStore } from 'pinia'
import { api } from '../utils/api'

export const useStatsStore = defineStore('stats', {
  state: () => ({
    overall: null,
    daily: [],
    chart: null,
    loading: false
  }),
  
  actions: {
    async loadOverall() {
      this.loading = true
      try {
        this.overall = await api.get('/stats/overall')
      } finally {
        this.loading = false
      }
    },
    
    async loadDaily(days = 7) {
      this.daily = await api.get('/stats/daily', { params: { days } })
    },
    
    async loadChart(days = 7) {
      this.chart = await api.get('/stats/chart', { params: { days } })
    },
    
    async loadAll(days = 7) {
      await Promise.all([
        this.loadOverall(),
        this.loadDaily(days),
        this.loadChart(days)
      ])
    }
  }
})
