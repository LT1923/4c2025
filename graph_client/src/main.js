import './assets/main.css'
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import PhotoGallery from './components/PhotoGallery.vue'
import AlbumList from './components/AlbumList.vue'
import Auth from './components/Auth.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: PhotoGallery,
      meta: { requiresAuth: true }
    },
    {
      path: '/recent',
      component: PhotoGallery,
      props: { filter: 'recent' },
      meta: { requiresAuth: true }
    },
    {
      path: '/albums',
      component: AlbumList,
      meta: { requiresAuth: true }
    },
    {
      path: '/album/:albumId',
      component: PhotoGallery,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/trash',
      component: PhotoGallery,
      props: { filter: 'trash' },
      meta: { requiresAuth: true }
    },
    {
      path: '/auth',
      component: Auth,
      meta: { requiresAuth: false }
    }
  ]
})

// 添加全局路由守卫
router.beforeEach((to, from, next) => {
  console.log('路由守卫执行中...')
  console.log('目标路由:', to.path)
  console.log('路由需要认证:', to.meta.requiresAuth)
  
  // 检查用户是否已登录
  const savedUser = localStorage.getItem('user')
  const isAuthenticated = !!savedUser
  
  console.log('localStorage中的用户信息:', savedUser)
  console.log('是否已认证:', isAuthenticated)
  
  // 如果路由需要身份验证但用户未登录，则重定向到登录页面
  if (to.meta.requiresAuth && !isAuthenticated) {
    console.log('未登录，重定向到登录页面')
    next({ path: '/auth', replace: true })
  } else if (to.path === '/auth' && isAuthenticated) {
    // 如果用户已登录，但试图访问登录页面，则重定向到首页
    console.log('已登录，从登录页面重定向到首页')
    next({ path: '/', replace: true })
  } else {
    console.log('继续导航到:', to.path)
    next()
  }
})

const app = createApp(App)
app.config.devtools = true
app.config.productionTip = false

// 添加调试信息
console.log('=== 应用启动 ===')
const userData = localStorage.getItem('user')
console.log('localStorage 中的用户数据:', userData)
try {
  if (userData) {
    const parsedUser = JSON.parse(userData)
    console.log('解析后的用户数据:', parsedUser)
  }
} catch (e) {
  console.error('解析用户数据失败:', e)
  console.log('清除无效的用户数据')
  localStorage.removeItem('user')
}

app.use(router)
app.mount('#app')
