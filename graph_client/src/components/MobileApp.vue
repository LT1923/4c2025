<template>
  <div class="mobile-container">
    <!-- 顶部搜索栏 -->
    <div class="mobile-header">
      <div class="month-title" v-if="currentDate">{{ currentDate }}</div>
      <div class="search-bar">
        <i class="search-icon">🔍</i>
        <input 
          type="text" 
          v-model="searchKeyword" 
          placeholder="时间、地点、文件名称..."
          @keyup.enter="searchPhotos"
        />
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="mobile-content smooth-scroll">
      <!-- 搜索结果 -->
      <div v-if="isSearching" class="search-results">
        <div class="date-header">
          <span>搜索结果: {{ filteredPhotos.length }}张照片</span>
          <button class="edit-btn" @click="clearSearch">清除</button>
        </div>
        <div v-if="filteredPhotos.length === 0" class="empty-state">
          <div class="empty-icon">🔍</div>
          <div class="empty-text">未找到符合条件的照片</div>
          <div class="empty-subtext">请尝试其他关键词</div>
        </div>
        <div v-else class="mobile-photo-grid">
          <div 
            v-for="photo in filteredPhotos" 
            :key="photo.id" 
            class="mobile-photo-item" 
            @click="previewPhoto(photo)"
          >
            <img :src="photo.url" :alt="photo.description">
          </div>
        </div>
      </div>
      
      <!-- 全部照片（按日期分组） -->
      <div v-else-if="activeTab === 'photos'" class="all-photos">
        <div v-if="groupedPhotos.length === 0" class="empty-state">
          <div class="empty-icon">🖼️</div>
          <div class="empty-text">相册中还没有照片</div>
          <div class="empty-subtext">添加一些照片开始创建回忆</div>
        </div>
        <div v-else>
          <div v-for="group in groupedPhotos" :key="group.date" class="date-group">
            <div class="date-header wx-style">
              {{ formatChineseDate(group.date) }}
              <span v-if="getLocationForGroup(group)" class="location-tag">{{ getLocationForGroup(group) }}</span>
            </div>
            <div class="mobile-photo-grid">
              <div 
                v-for="photo in group.photos" 
                :key="photo.id" 
                class="mobile-photo-item" 
                @click="previewPhoto(photo)"
                :class="{'photo-selected': selectedPhotos.includes(photo.id)}"
              >
                <img :src="photo.url" :alt="photo.description">
                <div v-if="isSelectMode" class="photo-selection-indicator">
                  <span v-if="selectedPhotos.includes(photo.id)">✓</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 相册列表 -->
      <div v-else-if="activeTab === 'albums'" class="albums-view">
        <div v-if="albums.length === 0" class="empty-state">
          <div class="empty-icon">📁</div>
          <div class="empty-text">还没有创建任何相册</div>
          <div class="empty-subtext">创建相册整理你的照片</div>
        </div>
        <div v-else class="albums-grid">
          <div 
            v-for="album in albums" 
            :key="album.id" 
            class="album-card" 
            @click="openAlbum(album.id)"
          >
            <div class="album-cover">
              <img :src="album.coverUrl" :alt="album.name">
            </div>
            <div class="album-info">
              <div class="album-name">{{ album.name }}</div>
              <div class="album-count">{{ albumPhotoCount[album.id] || 0 }}张照片</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 相册详情 -->
      <div v-if="activeTab === 'albumDetail'" class="album-detail">
        <div class="date-header">
          <button class="edit-btn" @click="backToAlbums">返回</button>
          <span>{{ currentAlbum ? currentAlbum.name : '' }}</span>
          <button class="edit-btn" @click="toggleSelectMode">选择</button>
        </div>
        <div v-if="albumPhotos.length === 0" class="empty-state">
          <div class="empty-icon">🖼️</div>
          <div class="empty-text">此相册中还没有照片</div>
          <div class="empty-subtext">添加照片到这个相册</div>
        </div>
        <div v-else class="mobile-photo-grid">
          <div 
            v-for="photo in albumPhotos" 
            :key="photo.id" 
            class="mobile-photo-item" 
            @click="isSelectMode ? togglePhotoSelection(photo.id) : previewPhoto(photo)"
            :class="{'photo-selected': selectedPhotos.includes(photo.id)}"
          >
            <img :src="photo.url" :alt="photo.description">
            <div v-if="isSelectMode" class="photo-selection-indicator">
              <span v-if="selectedPhotos.includes(photo.id)">✓</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 照片预览 -->
    <div v-if="previewVisible" class="preview-mode">
      <div class="preview-header">
        <button class="edit-btn" @click="closePreview">返回</button>
        <div>
          <button class="edit-btn" @click="sharePhoto">分享</button>
          <button class="edit-btn" @click="toggleFavorite">收藏</button>
        </div>
      </div>
      <div class="preview-content" @click="closePreview">
        <img class="preview-image" :src="currentPhoto.url" :alt="currentPhoto.description">
      </div>
      <div class="preview-footer">
        <div class="preview-info">
          <div class="preview-date">{{ formatDate(currentPhoto.date) }}</div>
          <div class="preview-location" v-if="currentPhoto.location">{{ currentPhoto.location }}</div>
        </div>
        <div class="preview-actions">
          <button class="edit-btn" @click.stop="deletePhoto">删除</button>
          <button class="edit-btn" @click.stop="editPhoto">编辑</button>
        </div>
      </div>
    </div>

    <!-- 选择模式底部栏 -->
    <div v-if="isSelectMode" class="edit-footer">
      <button class="edit-btn cancel-btn" @click="toggleSelectMode">取消</button>
      <button class="edit-btn" @click="addToAlbum">添加到相册</button>
      <button class="edit-btn" @click="downloadSelected">下载</button>
      <button class="edit-btn" @click="deleteSelected">删除</button>
    </div>

    <!-- 底部导航栏 -->
    <div class="mobile-nav">
      <div 
        class="nav-item" 
        :class="{ active: activeTab === 'photos' }" 
        @click="switchTab('photos')"
      >
        <div class="nav-icon">相片</div>
      </div>
      <div 
        class="nav-item" 
        :class="{ active: activeTab === 'albums' || activeTab === 'albumDetail' }"
        @click="switchTab('albums')"
      >
        <div class="nav-icon">相册</div>
      </div>
      <div 
        class="nav-item" 
        :class="{ active: activeTab === 'trash' }"
        @click="switchTab('trash')"
      >
        <div class="nav-icon">回收站</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'MobileApp',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // 状态变量
    const activeTab = ref('photos')
    const searchKeyword = ref('')
    const isSearching = ref(false)
    const previewVisible = ref(false)
    const currentPhoto = ref({})
    const isSelectMode = ref(false)
    const selectedPhotos = ref([])
    const isRecentView = ref(false)
    const currentDate = ref(null)
    const currentAlbum = ref(null)
    const hasMorePhotos = ref(true)
    
    // 照片数据
    const photos = ref([
      // 示例数据，实际应从API获取
      { id: 1, url: 'https://picsum.photos/id/1/300/300', description: '海边日落', date: '2024-03-07', location: '南京市鼓楼区' },
      { id: 2, url: 'https://picsum.photos/id/10/300/300', description: '山间小路', date: '2024-03-07', location: '南京市鼓楼区' },
      { id: 3, url: 'https://picsum.photos/id/100/300/300', description: '城市夜景', date: '2024-03-07', location: '南京市鼓楼区' },
      { id: 4, url: 'https://picsum.photos/id/1000/300/300', description: '花卉特写', date: '2024-03-06', location: '南京市鼓楼区' },
      { id: 5, url: 'https://picsum.photos/id/1001/300/300', description: '森林小径', date: '2024-03-06', location: '南京市鼓楼区' },
      { id: 6, url: 'https://picsum.photos/id/1002/300/300', description: '雪山风景', date: '2024-03-06', location: '南京市鼓楼区' },
      { id: 7, url: 'https://picsum.photos/id/1003/300/300', description: '湖泊风光', date: '2024-03-05', location: '南京市' },
      { id: 8, url: 'https://picsum.photos/id/1004/300/300', description: '建筑摄影', date: '2024-03-05', location: '南京市' },
      { id: 9, url: 'https://picsum.photos/id/1005/300/300', description: '人像摄影', date: '2024-03-05', location: '南京市' },
      { id: 10, url: 'https://picsum.photos/id/1006/300/300', description: '动物摄影', date: '2024-03-04', location: '南京市鼓楼区' },
      { id: 11, url: 'https://picsum.photos/id/1008/300/300', description: 'QR码', date: '2024-03-04', location: '南京市鼓楼区' },
      { id: 12, url: 'https://picsum.photos/id/1009/300/300', description: 'QR码2', date: '2024-03-04', location: '南京市鼓楼区' },
      { id: 13, url: 'https://picsum.photos/id/1010/300/300', description: '证件照', date: '2024-03-03', location: '' },
      { id: 14, url: 'https://picsum.photos/id/1011/300/300', description: '个人档案', date: '2024-03-03', location: '' },
    ])
    
    // 相册数据
    const albums = ref([
      { id: 1, name: '旅行', coverUrl: 'https://picsum.photos/id/10/300/300' },
      { id: 2, name: '家人', coverUrl: 'https://picsum.photos/id/1001/300/300' },
      { id: 3, name: '美食', coverUrl: 'https://picsum.photos/id/1080/300/300' },
      { id: 4, name: '宠物', coverUrl: 'https://picsum.photos/id/237/300/300' },
    ])
    
    // 相册照片映射数据
    const albumPhotos = ref([])
    const albumPhotoCount = reactive({
      1: 3,
      2: 2,
      3: 1,
      4: 4
    })
    
    // 根据日期分组照片
    const groupedPhotos = computed(() => {
      const groups = {}
      photos.value.forEach(photo => {
        if (!groups[photo.date]) {
          groups[photo.date] = []
        }
        groups[photo.date].push(photo)
      })
      
      return Object.keys(groups).map(date => ({
        date,
        photos: groups[date]
      })).sort((a, b) => new Date(b.date) - new Date(a.date))
    })
    
    // 搜索结果
    const filteredPhotos = computed(() => {
      if (!searchKeyword.value) return []
      
      const keyword = searchKeyword.value.toLowerCase()
      return photos.value.filter(photo => 
        photo.description.toLowerCase().includes(keyword) || 
        photo.location?.toLowerCase().includes(keyword) ||
        photo.date.includes(keyword)
      )
    })
    
    // 最近添加的照片
    const recentPhotos = computed(() => {
      return [...photos.value].sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 20)
    })
    
    // 方法
    const searchPhotos = () => {
      if (searchKeyword.value.trim()) {
        isSearching.value = true
      }
    }
    
    const clearSearch = () => {
      searchKeyword.value = ''
      isSearching.value = false
    }
    
    const previewPhoto = (photo) => {
      currentPhoto.value = photo
      previewVisible.value = true
    }
    
    const closePreview = () => {
      previewVisible.value = false
    }
    
    const openAlbum = (albumId) => {
      currentAlbum.value = albums.value.find(a => a.id === albumId)
      // 模拟获取相册中的照片
      albumPhotos.value = photos.value.filter((_, index) => index % (albumId + 1) === 0)
      activeTab.value = 'albumDetail'
    }
    
    const backToAlbums = () => {
      activeTab.value = 'albums'
      currentAlbum.value = null
    }
    
    const toggleSelectMode = () => {
      isSelectMode.value = !isSelectMode.value
      if (!isSelectMode.value) {
        selectedPhotos.value = []
      }
    }
    
    const togglePhotoSelection = (photoId) => {
      const index = selectedPhotos.value.indexOf(photoId)
      if (index === -1) {
        selectedPhotos.value.push(photoId)
      } else {
        selectedPhotos.value.splice(index, 1)
      }
    }
    
    const addToAlbum = () => {
      // 添加到相册的逻辑
      alert(`添加 ${selectedPhotos.value.length} 张照片到相册`)
      toggleSelectMode()
    }
    
    const downloadSelected = () => {
      // 下载照片的逻辑
      alert(`下载 ${selectedPhotos.value.length} 张照片`)
      toggleSelectMode()
    }
    
    const deleteSelected = () => {
      // 删除照片的逻辑
      alert(`删除 ${selectedPhotos.value.length} 张照片`)
      toggleSelectMode()
    }
    
    const formatChineseDate = (dateString) => {
      const date = new Date(dateString)
      const month = date.getMonth() + 1
      const day = date.getDate()
      return `${month}月${day}日`
    }
    
    const getLocationForGroup = (group) => {
      if (!group.photos || group.photos.length === 0) return null
      // 返回该组中第一张照片的位置作为组位置
      return group.photos[0].location || null
    }
    
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }
    
    const loadMorePhotos = () => {
      // 加载更多照片的逻辑
      // 这里应该是API调用
      hasMorePhotos.value = false // 示例：没有更多照片了
    }
    
    const switchTab = (tab) => {
      if (tab === 'albums' && activeTab.value === 'albumDetail') {
        // 如果当前在相册详情，按下相册按钮应该返回相册列表
        backToAlbums()
      } else {
        activeTab.value = tab
      }
      
      // 重置一些状态
      clearSearch()
      isSelectMode.value = false
      selectedPhotos.value = []
    }
    
    const showUploadOptions = () => {
      // 显示上传选项（拍照或从相册选择）
      alert('选择上传方式：拍照或从相册选择')
    }
    
    const sharePhoto = () => {
      // 分享照片的逻辑
      alert(`分享照片: ${currentPhoto.value.description}`)
    }
    
    const toggleFavorite = () => {
      // 收藏照片的逻辑
      alert(`收藏照片: ${currentPhoto.value.description}`)
    }
    
    const deletePhoto = () => {
      // 删除当前照片
      alert(`删除照片: ${currentPhoto.value.description}`)
      closePreview()
    }
    
    const editPhoto = () => {
      // 编辑照片信息
      alert(`编辑照片信息: ${currentPhoto.value.description}`)
    }
    
    // 处理路由变化
    onMounted(() => {
      // 设置初始标签页
      const path = route.path
      
      if (path === '/albums' || path.startsWith('/album/')) {
        activeTab.value = 'albums'
        
        if (path.startsWith('/album/')) {
          const albumId = parseInt(path.split('/album/')[1])
          openAlbum(albumId)
        }
      } else if (path === '/recent') {
        isRecentView.value = true
      }
      
      // 设置当前日期显示
      const now = new Date()
      currentDate.value = `${now.getFullYear()}年${now.getMonth() + 1}月`
    })
    
    return {
      // 状态
      activeTab,
      searchKeyword,
      isSearching,
      previewVisible,
      currentPhoto,
      isSelectMode,
      selectedPhotos,
      isRecentView,
      currentDate,
      currentAlbum,
      hasMorePhotos,
      
      // 数据
      photos,
      albums,
      albumPhotos,
      albumPhotoCount,
      
      // 计算属性
      groupedPhotos,
      filteredPhotos,
      recentPhotos,
      
      // 方法
      searchPhotos,
      clearSearch,
      previewPhoto,
      closePreview,
      openAlbum,
      backToAlbums,
      toggleSelectMode,
      togglePhotoSelection,
      addToAlbum,
      downloadSelected,
      deleteSelected,
      formatChineseDate,
      getLocationForGroup,
      formatDate,
      loadMorePhotos,
      switchTab,
      showUploadOptions,
      sharePhoto,
      toggleFavorite,
      deletePhoto,
      editPhoto
    }
  }
}
</script>

<style scoped>
.mobile-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  max-width: 100vw;
  background-color: #f2f2f2;
  position: relative;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  left: 0;
  right: 0;
}

/* 顶部搜索栏 - 微信风格 */
.mobile-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #f2f2f2;
  padding: 10px 0;
  width: 100vw;
  margin-left: 0;
  margin-right: 0;
  box-sizing: border-box;
}

.month-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
  padding: 0 10px;
  text-align: left;
}

.search-bar {
  display: flex;
  align-items: center;
  background-color: #fff;
  border-radius: 20px;
  padding: 6px 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  width: calc(100vw - 20px);
  margin: 0 10px;
}

.search-icon {
  font-size: 16px;
  color: #888;
  padding: 0 4px;
}

.search-bar input {
  flex: 1;
  border: none;
  outline: none;
  padding: 0 8px;
  font-size: 14px;
  background-color: transparent;
  color: #333;
  width: 100%;
}

/* 主内容区域 */
.mobile-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  -webkit-overflow-scrolling: touch;
  width: 100vw;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* 照片网格 - 完全填满屏幕版本 */
.mobile-photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 33.33vw);
  gap: 0;
  padding: 0;
  background-color: #f2f2f2;
  width: 100vw;
  box-sizing: border-box;
  margin: 0;
}

.mobile-photo-item {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  background-color: #eee;
  width: 33.33vw;
  box-sizing: border-box;
}

.mobile-photo-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 日期分组 - 微信风格 */
.date-header.wx-style {
  padding: 8px 10px 6px 10px;
  font-size: 16px;
  font-weight: 500;
  color: #000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f2f2f2;
  margin: 0;
  width: 100vw;
  box-sizing: border-box;
}

.location-tag {
  font-size: 13px;
  color: #576b95;
  font-weight: normal;
  display: flex;
  align-items: center;
}

.location-tag::after {
  content: '>';
  margin-left: 4px;
  font-size: 12px;
  color: #999;
}

.date-group {
  margin-bottom: 0;
  border-bottom: none;
  background-color: #f2f2f2;
  width: 100vw;
  box-sizing: border-box;
}

/* 底部导航栏 - 微信风格 */
.mobile-nav {
  display: flex;
  justify-content: space-around;
  align-items: center;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #f9f9f9;
  border-top: 1px solid #e0e0e0;
  padding: 12px 0;
  z-index: 100;
  width: 100vw;
  box-sizing: border-box;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #666;
  font-size: 14px;
  padding: 0 20px;
}

.nav-item.active {
  color: #07c160;
}

/* 其他微信风格整体调整 */
.edit-btn {
  color: #576b95;
  background: none;
  border: none;
  font-size: 14px;
  padding: 4px 8px;
}

.empty-state {
  padding: 40px 20px;
}

.empty-icon {
  font-size: 36px;
}

/* 修正底部内容区域的内边距 */
.all-photos {
  padding-bottom: 60px;
}

/* 修改相册视图的布局，使其完全填满屏幕 */
.albums-grid {
  display: grid;
  grid-template-columns: repeat(2, 50vw);
  gap: 0;
  padding: 0;
  margin: 0;
  width: 100vw;
}

.album-card {
  width: 50vw;
  box-sizing: border-box;
  padding: 5px;
}

/* 大屏幕适配 */
@media (min-width: 769px) {
  .mobile-container {
    width: 450px;
    max-width: 450px;
    margin: 0 auto;
  }
  
  .mobile-header,
  .mobile-content,
  .date-header.wx-style,
  .date-group,
  .mobile-nav {
    width: 450px;
  }
  
  .mobile-photo-grid {
    width: 450px;
    grid-template-columns: repeat(3, 150px);
  }
  
  .mobile-photo-item {
    width: 150px;
  }
  
  .albums-grid {
    width: 450px;
    grid-template-columns: repeat(2, 225px);
  }
  
  .album-card {
    width: 225px;
  }
  
  .search-bar {
    width: calc(450px - 20px);
  }
}
</style>

<!-- 强化全局样式，不受scoped限制 -->
<style>
/* 全局重置，确保没有默认边距 */
html, body, #app, .app {
  margin: 0 !important;
  padding: 0 !important;
  width: 100vw !important;
  max-width: 100vw !important;
  overflow-x: hidden !important;
  box-sizing: border-box !important;
}

/* 修复所有可能的父容器 */
html, body, #app, .app, .app > div, .app > :first-child {
  width: 100vw !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow-x: hidden !important;
}

/* 调整页面布局容器 */
.content-wrapper {
  width: 100vw !important;
  max-width: 100vw !important;
  margin: 0 !important;
  padding: 0 !important;
}

.main-content {
  width: 100vw !important;
  max-width: 100vw !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* 添加meta viewport标签确保移动设备正确渲染 */
@media (max-width: 768px) {
  head {
    display: block !important;
  }
  
  head::after {
    content: '' !important;
    display: block !important;
    width: 100vw !important;
  }
}
</style> 