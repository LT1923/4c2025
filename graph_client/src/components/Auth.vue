<template>
  <div class="auth-container">
    <!-- 左侧产品介绍 -->
    <div class="product-info">
      <div class="product-slogan">
        <h1>"智能相册 图文检索"</h1>
        <h2>智能检索，任何设备可以搭载</h2>
      </div>
      
      <div class="features">
        <div class="feature-item">
          <div class="feature-icon">
            <span class="icon-symbol">&#8981;</span>
          </div>
          <span>快速查询</span>
        </div>
        <div class="feature-item">
          <div class="feature-icon">
            <span class="icon-symbol">&#9881;</span>
          </div>
          <span>功能齐全</span>
        </div>
        <div class="feature-item">
          <div class="feature-icon">
            <span class="icon-symbol">&#128452;</span>
          </div>
          <span>原画备份</span>
        </div>
        <div class="feature-item">
          <div class="feature-icon">
            <span class="icon-symbol">&#8635;</span>
          </div>
          <span>多端同步</span>
        </div>
      </div>
    </div>

    <!-- 右侧登录框 -->
    <div class="login-container">
      <div :class="['auth-card', { 'auth-card-mobile': isMobile }]">
        <h3 class="auth-title">{{ isLogin ? '账号密码登录' : '用户注册' }}</h3>
        
        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-group">
            <input 
              type="text" 
              v-model="form.phone" 
              placeholder="手机号/邮箱/用户名"
              required
            >
          </div>
          
          <div class="form-group">
            <input 
              type="password" 
              v-model="form.password" 
              placeholder="密码"
              required
            >
          </div>

          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
          </button>
        </form>

        <div class="auth-actions">
          <span class="auth-link" @click="isLogin = !isLogin">
            {{ isLogin ? '还没有账号？去注册' : '已有账号？去登录' }}
          </span>
          <a href="#" class="auth-link">忘记密码？</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useDevice } from '../composables/useDevice'
import { useUserStore } from '../composables/useUserStore'
import { useRouter } from 'vue-router'

export default {
  name: 'Auth',
  setup() {
    const { isMobile } = useDevice()
    const userStore = useUserStore()
    const router = useRouter()
    
    return { isMobile, userStore, router }
  },
  data() {
    return {
      isLogin: true,
      form: {
        phone: '',
        password: ''
      },
      message: '',
      messageType: 'error',
      loading: false
    }
  },
  methods: {
    async handleSubmit() {
      this.loading = true
      this.message = ''
      
      try {
        if (this.isLogin) {
          // 处理登录
          const result = await this.userStore.login(this.form.phone, this.form.password)
          
          if (result.success) {
            // 登录成功，跳转到首页
            this.router.push('/')
          } else {
            // 登录失败，显示错误信息
            this.message = result.message
            this.messageType = 'error'
          }
        } else {
          // 处理注册
          const result = await this.userStore.register(this.form.phone, this.form.password)
          
          if (result.success) {
            // 注册成功，显示成功信息并切换到登录页
            this.message = '注册成功，请登录'
            this.messageType = 'success'
            this.isLogin = true
            this.form.password = ''
          } else {
            // 注册失败，显示错误信息
            this.message = result.message
            this.messageType = 'error'
          }
        }
      } catch (error) {
        console.error('操作失败:', error)
        this.message = '操作失败，请稍后再试'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* 添加全局样式，防止滚动 */
:global(html), :global(body) {
  overflow: hidden;
  margin: 0;
  padding: 0;
  height: 100%;
}

.auth-container {
  position: fixed; /* 固定定位，防止滚动 */
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%; /* 精确设置宽度为100% */
  height: 100%; /* 精确设置高度为100% */
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  background: url('https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&q=80&w=1470&ixlib=rb-4.0.3') center/cover no-repeat;
  margin: 0;
  padding: 0;
  overflow: hidden; /* 防止内容溢出 */
}

.auth-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 3rem;
  z-index: 2;
  color: white;
  background-color: rgba(0, 0, 0, 0.2);
}

.product-slogan {
  margin-bottom: 4rem;
  text-align: center;
}

.product-slogan h1 {
  font-size: 2.8rem;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.product-slogan h2 {
  font-size: 1.6rem;
  font-weight: normal;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.features {
  display: flex;
  justify-content: space-around;
  margin-top: 2rem;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin: 0 1rem;
}

.feature-icon {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.icon-symbol {
  font-size: 28px;
  line-height: 1;
  color: white;
  filter: brightness(1.2);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.emoji-icon {
  display: none;
}

.feature-icon img {
  display: none;
}

.login-container {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  z-index: 2;
  padding-right: 50px;
}

.auth-card {
  flex: none;
  background: rgba(255, 255, 255, 0.95);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  width: 350px;
  margin-right: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  max-height: 500px;
}

.auth-title {
  text-align: center;
  font-size: 1.3rem;
  margin-bottom: 1.5rem;
  color: #333;
}

.auth-card-mobile {
  padding: 1.5rem;
  border-radius: 8px;
  margin: 0 1rem;
  max-width: none;
}

.message {
  padding: 0.8rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.message.error {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ffcdd2;
}

.message.success {
  background-color: #e8f5e9;
  color: #388e3c;
  border: 1px solid #c8e6c9;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  margin: 0 auto;
}

.form-group {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin: 0 auto;
}

.form-group input {
  padding: 0.8rem;
  border: 1px solid #eee;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border 0.2s;
  background-color: rgba(255, 255, 255, 0.8);
}

.form-group input:focus {
  outline: none;
  border-color: #1890ff;
}

.submit-btn {
  background-color: #1890ff;
  color: white;
  border: none;
  padding: 0.8rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 1rem;
  transition: background-color 0.2s;
  width: 100%;
  margin: 1rem auto 0;
}

.submit-btn:hover:not(:disabled) {
  background-color: #40a9ff;
}

.submit-btn:disabled {
  background-color: #a8d5c3;
  cursor: not-allowed;
}

.auth-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 1.2rem;
  font-size: 0.85rem;
}

.auth-link {
  color: #1890ff;
  cursor: pointer;
  text-decoration: none;
}

.auth-link:hover {
  text-decoration: underline;
}

.sms-login {
  display: none;
}

@media (max-width: 768px) {
  .auth-container {
    flex-direction: column;
    padding: 0; /* 移除内边距 */
    height: 100%;
  }
  
  .product-info {
    display: none;
  }
  
  .login-container {
    justify-content: center;
    width: 100%;
    padding-right: 0; /* 移除右侧内边距 */
  }
  
  .auth-card {
    width: 90%;
    max-width: 350px;
    height: auto;
    margin: 0 auto; /* 居中显示 */
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.99);
  }
}
</style> 