<script>
import { useDevice } from './composables/useDevice'
import { useUserStore } from './composables/useUserStore'
import { onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'

export default {
  components: {
    Sidebar
  },
  setup() {
    const { isMobile } = useDevice()
    const userStore = useUserStore()
    
    // 移除了先前的认证检查逻辑，因为现在在全局路由守卫中处理
    
    return { isMobile, userStore }
  }
}
</script>

<template>
  <div class="app">
    <!-- 登录/注册页面 -->
    <template v-if="$route.path === '/auth'">
      <router-view></router-view>
    </template>
    
    <!-- 已登录状态下的页面 -->
    <template v-else>
      <!-- PC端布局 -->
      <template v-if="!isMobile">
        <Sidebar />
        <div class="main-content">
          <router-view></router-view>
        </div>
      </template>
      
      <!-- 移动端布局 -->
      <template v-else>
        <router-view></router-view>
        <nav class="nav-bar">
          <router-link to="/">相册</router-link> |
          <router-link to="/albums">图集</router-link>
        </nav>
      </template>
    </template>
  </div>
</template>

<style>
.app {
  display: flex;
  min-height: 100vh;
  max-width: 2400px;
  margin: 0 auto;
  background: #fff;
}

.main-content {
  flex: 1;
  overflow: auto;
  position: relative;
  padding: 0;
  background: #fff;
  margin-left: 200px;
  min-height: 100vh;
  background: #fff;
  padding-left: 2rem;
  padding-right: 2rem;
  width: calc(100% - 200px);
  max-width: none;
}

/* 确保内容区域能够完整显示photo-gallery的内容 */
.content-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  overflow-x: auto;
}

.user-info {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.user-info span {
  margin-right: 1rem;
  color: #666;
}

.logout-btn {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.logout-btn:hover {
  background-color: #d32f2f;
}

/* 移动端样式 */
.nav-bar {
  padding: 1rem;
  background-color: #f8f9fa;
  text-align: center;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.nav-bar a {
  color: #666;
  text-decoration: none;
  padding: 0.5rem 1rem;
}

.nav-bar a.router-link-active {
  color: #42b983;
  font-weight: bold;
}

/* 移动端样式 */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    width: 100%;
    padding-left: 1rem;
    padding-right: 1rem;
  }
}
</style>
