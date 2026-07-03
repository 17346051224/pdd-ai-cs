import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('./views/Layout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('./views/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'ai-config',
        name: 'AIConfig',
        component: () => import('./views/AIConfig.vue'),
        meta: { title: 'AI配置' }
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('./views/Knowledge.vue'),
        meta: { title: '知识库管理' }
      },
      {
        path: 'conversations',
        name: 'Conversations',
        component: () => import('./views/Conversations.vue'),
        meta: { title: '对话记录' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('./views/Settings.vue'),
        meta: { title: '系统设置' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '系统'} - 拼多多AI客服`
  next()
})

export default router
