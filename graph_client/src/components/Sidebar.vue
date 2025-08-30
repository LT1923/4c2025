<template>
  <div class="sidebar">
    <div class="logo">
      <div class="logo-icon">AI</div>
      <span>智能相册</span>
      <button v-if="isLoggedIn" class="minimal-logout-btn" @click="handleLogout" title="退出登录">
        <i class="icon">🚪</i>
      </button>
    </div>

    <div class="menu-section">
      <div class="section-title">照片</div>
      <router-link to="/" class="menu-item" active-class="active">
        <i class="icon">📸</i>
        <span>全部照片</span>
      </router-link>
      <router-link to="/recent" class="menu-item" active-class="active">
        <i class="icon">🕒</i>
        <span>最近上传</span>
      </router-link>
    </div>

    <div class="menu-section">
      <div class="section-title">整理</div>
      <router-link to="/albums" class="menu-item" active-class="active">
        <i class="icon">📁</i>
        <span>相册</span>
      </router-link>
    </div>

    <div class="menu-section">
      <div class="section-title">工具</div>
      <router-link to="/trash" class="menu-item" active-class="active">
        <i class="icon">🗑️</i>
        <span>回收站</span>
      </router-link>
    </div>

    <div class="upload-btn">
      <input
          type="file"
          ref="fileInput"
          style="display: none"
          accept="image/*"
          multiple
          @change="handleFileUpload"
      >
      <button @click="triggerUpload">
        <i class="icon">⬆️</i>
        上传照片
      </button>
    </div>

    <div class="login-btn" v-if="!isLoggedIn">
      <router-link to="/login">
        <button>
          <i class="icon">🔑</i>
          登录/注册
        </button>
      </router-link>
    </div>
  </div>
</template>

<script>
import {ref, computed, onMounted} from 'vue'
import {usePhotoStore} from '../composables/usePhotoStore'
import {useUserStore} from '../composables/useUserStore'
import {useRouter} from 'vue-router'

export default {
  name: 'Sidebar',
  setup() {
    const store = usePhotoStore()
    const userStore = useUserStore()
    const router = useRouter()
    const fileInput = ref(null)
    const totalPhotos = ref(null)

    const isLoggedIn = computed(() => {
      return userStore.isLoggedIn()
    })

    onMounted(async () => {
      if (isLoggedIn.value) {
        try {
          const photos = await store.getAllPhotos()
          totalPhotos.value = photos.length
        } catch (error) {
          console.error('获取照片数量失败:', error)
        }
      }
    })

    const handleLogout = () => {
      userStore.logout();
      router.push('/auth');
    }

    const triggerUpload = () => {
      fileInput.value.click()
    }

    const handleFileUpload = async (event) => {
      console.log('侧边栏文件上传开始');
      const files = event.target.files;
      if (!files.length) {
        console.log('没有选择文件');
        return;
      }

      console.log(`选择了${files.length}个文件`);

      try {
        for (const file of Array.from(files)) {
          console.log(`处理文件: ${file.name}, 大小: ${file.size}字节, 类型: ${file.type}`);

          // 创建FormData对象
          const formData = new FormData();

          // 添加文件
          formData.append('photo', file);

          const userId = store.getUserId();
          console.log(`用户ID: ${userId}`);
          formData.append('user_id', userId);

          formData.append('text', file.name);

          console.log('开始上传...');

          // 上传照片 - 使用fetch直接上传
          try {
            // const response = await fetch('http://172.29.4.133:5000/api/photos/upload', {
            const response = await fetch('http://114.215.184.67:5000/api/photos/upload', {
              method: 'POST',
              body: formData
            });

            console.log('上传响应状态:', response.status);

            if (response.ok) {
              const data = await response.json();
              console.log('上传响应数据:', data);

              if (data.success) {
                console.log('上传成功');
              } else {
                alert(`上传失败: ${data.message || '未知错误'}`);
              }
            } else {
              alert(`上传失败，服务器返回: ${response.status}`);
            }
          } catch (uploadError) {
            console.error('上传过程中出错:', uploadError);
            alert(`上传失败: ${uploadError.message || '网络错误'}`);
          }
        }

        // 清除input
        event.target.value = '';

      } catch (error) {
        console.error('处理文件上传过程中出错:', error);
        alert(`上传处理失败: ${error.message || '未知错误'}`);
      }
    }

    return {
      fileInput,
      triggerUpload,
      handleFileUpload,
      isLoggedIn,
      totalPhotos,
      handleLogout
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 240px;
  height: 100vh;
  background: #f8f9fa;
  border-right: 1px solid #eee;
  padding: 1rem;
  position: fixed;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  z-index: 100;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.8rem;
  margin-bottom: 1rem;
  position: relative;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #42b983, #1890ff);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-weight: bold;
  font-size: 1.2rem;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

.logo span {
  font-size: 1.4rem;
  font-weight: bold;
  color: #333;
}

.menu-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.section-title {
  padding: 0.5rem;
  color: #999;
  font-size: 0.9rem;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.8rem;
  border-radius: 8px;
  color: #666;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  justify-content: flex-start;
  width: 100%;
}

.menu-item:hover {
  background: #eee;
}

.menu-item.active {
  background: #e6f3ff;
  color: #1890ff;
}

.icon {
  font-size: 1.2rem;
}

.upload-btn {
  margin-top: auto;
  padding: 1rem;
}

.upload-btn button {
  width: 100%;
  padding: 0.8rem;
  border: none;
  border-radius: 8px;
  background: #1890ff;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background 0.2s;
}

.upload-btn button:hover {
  background: #40a9ff;
}

.login-btn {
  padding: 0 1rem 1rem 1rem;
}

.login-btn a {
  text-decoration: none;
  display: block;
  width: 100%;
}

.login-btn button {
  width: 100%;
  padding: 0.8rem;
  border: none;
  border-radius: 8px;
  background: #1890ff;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background 0.2s;
}

.login-btn button:hover {
  background: #40a9ff;
}

.photo-count {
  margin-left: auto;
  font-size: 0.9rem;
  color: #999;
}

.minimal-logout-btn {
  border: none;
  color: #eff7fd;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 4px;
  position: absolute;
  right: 0;
  bottom: -20px;
  transition: color 0.2s;
}

.minimal-logout-btn:hover {
  color: #f44336;
}
</style> 