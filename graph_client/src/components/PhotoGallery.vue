<template>
  <div class="photo-gallery">
    <!-- PC端布局 -->
    <template v-if="!isMobile">
      <div class="gallery-header">
        <div class="gallery-header-content">
          <div class="header-left">
            <h2>{{ pageTitle }}</h2>
            <span class="photo-count" v-if="allPhotosData.length > 0">{{ allPhotosData.length }}张照片</span>
          </div>
          <div class="header-right">
            <!-- 非最近上传页面显示控件 -->
            <template v-if="!isRecentPage">
              <div class="view-mode">
                <button
                    :class="{ active: viewMode === 'grid' }"
                    @click="viewMode = 'grid'"
                    title="网格视图"
                >
                  <i class="icon">▤</i>
                </button>
                <button
                    :class="{ active: viewMode === 'list' }"
                    @click="viewMode = 'list'"
                    title="列表视图"
                >
                  <i class="icon">☰</i>
                </button>
              </div>
              <div class="sort-by">
                <select v-model="sortOrder">
                  <option value="time-desc">时间降序</option>
                  <option value="time-asc">时间升序</option>
                </select>
              </div>
            </template>
            <!-- 所有页面都显示搜索框 -->
            <div class="search-box">
              <input
                  type="text"
                  v-model="searchKeyword"
                  placeholder="搜索照片..."
                  @keyup.enter="searchPhotos"
              />
              <button class="search-btn" @click="searchPhotos" title="搜索">
                <i class="icon">🔍</i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="gallery-content">
        <!-- 搜索结果提示 -->
        <div v-if="isSearching" class="search-result-info">
          搜索结果：找到 {{ filteredPhotos.length }} 张与"{{ searchKeyword }}"相关的照片
          <button class="clear-search" @click="clearSearch">清除搜索</button>
        </div>

        <!-- 搜索结果展示 -->
        <div v-if="isSearching" class="photo-grid-pc grid">
          <div v-for="photo in filteredPhotos" :key="photo.id" class="photo-item">
            <div class="photo-wrapper">
              <img :src="getPhotoUrl(photo)" :alt="photo.text">
              <div class="photo-hover-info">
                <div class="hover-top">
                  <input
                      type="checkbox"
                      class="select-photo"
                      v-model="selectedPhotos"
                      :value="photo.id"
                  >
                  <span class="photo-date">{{ formatDate(photo.time) }}</span>
                </div>
                <div class="hover-bottom">
                  <span class="photo-description">{{ photo.text }}</span>
                  <div class="photo-actions">
                    <!-- 回收站中显示恢复按钮，其他页面显示移动到相册按钮 -->
                    <template v-if="filter === 'trash'">
                      <button class="action-btn" @click="restorePhoto(photo.id)">
                        <i class="icon">↩️</i>
                      </button>
                    </template>
                    <template v-else>
                      <button class="action-btn" @click="moveToAlbum(photo)">
                        <i class="icon">📁</i>
                      </button>
                    </template>
                    <button class="action-btn" @click="deletePhoto(photo.id)">
                      <i class="icon">{{ filter === 'trash' ? '❌' : '🗑️' }}</i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 非搜索状态下的内容 -->
        <template v-else>
          <!-- 最近上传页面的特殊布局 -->
          <div v-if="isRecentPage" class="recent-photos-grid">
            <div v-for="photo in recentPhotos" :key="photo.id" class="photo-item">
              <div class="photo-wrapper">
                <img :src="getPhotoUrl(photo)" :alt="photo.text">
                <div class="photo-hover-info">
                  <div class="hover-top">
                    <input
                        type="checkbox"
                        class="select-photo"
                        v-model="selectedPhotos"
                        :value="photo.id"
                    >
                  </div>
                  <div class="hover-bottom">
                    <span class="photo-description">{{ photo.text }}</span>
                    <div class="photo-actions">
                      <button class="action-btn" @click="moveToAlbum(photo)">
                        <i class="icon">📁</i>
                      </button>
                      <button class="action-btn" @click="deletePhoto(photo.id)">
                        <i class="icon">🗑️</i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 其他页面保持原有分组布局 -->
          <template v-else>
            <div v-for="group in groupedPhotos" :key="group.date" class="photo-group">
              <div class="time-divider">{{ group.date }}</div>
              <div :class="['photo-grid-pc', viewMode]">
                <div v-for="photo in group.photos" :key="photo.id" class="photo-item">
                  <div class="photo-wrapper">
                    <img :src="getPhotoUrl(photo)" :alt="photo.text">
                    <div class="photo-hover-info">
                      <div class="hover-top">
                        <input
                            type="checkbox"
                            class="select-photo"
                            v-model="selectedPhotos"
                            :value="photo.id"
                        >
                        <span class="photo-date">{{ formatDate(photo.time) }}</span>
                      </div>
                      <div class="hover-bottom">
                        <span class="photo-description">{{ photo.text }}</span>
                        <div class="photo-actions">
                          <!-- 根据当前过滤条件显示不同的操作按钮 -->
                          <template v-if="filter === 'trash'">
                            <!-- 回收站中显示恢复按钮 -->
                            <button class="action-btn restore-btn" @click="restorePhoto(photo.id)" title="恢复照片">
                              <i class="icon">↩️</i>
                            </button>
                            <!-- 回收站中显示永久删除按钮 -->
                            <button class="action-btn delete-btn" @click="deletePhoto(photo.id)" title="永久删除">
                              <i class="icon">❌</i>
                            </button>
                          </template>
                          <template v-else>
                            <!-- 正常状态显示移动到相册按钮 -->
                            <button class="action-btn" @click="moveToAlbum(photo)" title="移动到相册">
                              <i class="icon">📁</i>
                            </button>
                            <!-- 正常状态显示移到回收站按钮 -->
                            <button class="action-btn" @click="deletePhoto(photo.id)" title="移到回收站">
                              <i class="icon">🗑️</i>
                            </button>
                          </template>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </template>
      </div>
    </template>

    <!-- 移动端布局 -->
    <template v-else>
      <div class="mobile-header">
        <h2>{{ pageTitle }}</h2>
        <button class="upload-btn" @click="triggerUpload">
          <i class="icon">+</i>
        </button>
      </div>
      <div class="photo-grid-mobile">
        <div v-for="photo in sortedPhotos" :key="photo.id" class="photo-item-mobile">
          <img :src="getPhotoUrl(photo)" :alt="photo.text">
          <div class="photo-info-mobile">
            <span class="photo-description">{{ photo.text }}</span>
            <span class="photo-date">{{ formatDate(photo.time) }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- 移动到相册的弹窗 -->
    <div v-if="showMoveDialog" class="move-dialog">
      <div class="dialog-content">
        <h3>移动到相册</h3>
        <div v-if="albumsList.length > 0" class="album-list">
          <div
              v-for="album in albumsList"
              :key="album.id"
              class="album-option"
              @click="confirmMoveToAlbum(album.id)"
          >
            {{ album.name }}
          </div>
        </div>
        <div v-else class="no-albums">
          <p>您还没有创建任何相册</p>
          <p class="hint">先创建一个相册，然后再移动照片</p>
        </div>
        <div class="dialog-actions">
          <button class="cancel-btn" @click="showMoveDialog = false">取消</button>
        </div>
      </div>
    </div>

    <!-- 隐藏的文件上传输入框 -->
    <input
        type="file"
        ref="fileInput"
        style="display: none"
        accept="image/*"
        multiple
        @change="handleFileUpload"
    >
  </div>
</template>

<script>
import {useDevice} from '../composables/useDevice'
import {usePhotoStore} from '../composables/usePhotoStore'
import {ref, computed, watch} from 'vue'
import {useRoute} from 'vue-router'

// API基础URL
const API_BASE_URL = 'http://114.215.184.67:5000/api'

export default {
  name: 'PhotoGallery',
  props: {
    albumId: {
      type: [String, Number],
      default: null
    },
    filter: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const {isMobile} = useDevice()
    const route = useRoute()
    const store = usePhotoStore()

    // 将props的filter解构出来，方便在模板中使用
    const filter = computed(() => props.filter)

    const viewMode = ref('grid')
    const sortOrder = ref('time-desc')
    const selectedPhotos = ref([])
    const showMoveDialog = ref(false)
    const photoToMove = ref(null)
    const fileInput = ref(null)

    // 获取当前相册ID（如果有）
    const currentAlbumId = computed(() => {
      return props.albumId ? parseInt(props.albumId) : null
    })

    // 获取当前相册信息
    const currentAlbum = computed(() => {
      return currentAlbumId.value ? store.getAlbumById(currentAlbumId.value) : null
    })

    // 页面标题
    const pageTitle = computed(() => {
      if (currentAlbum.value) return currentAlbum.value.name
      if (props.filter === 'recent') return '最近上传'
      if (props.filter === 'trash') return '回收站'
      return '全部照片'
    })

    // 直接获取所有照片，用于显示
    const allPhotosData = ref([]);

    // 加载照片
    const loadPhotos = async () => {
      console.log('开始加载照片');
      allPhotosData.value = await displayPhotos();
      console.log('照片加载完成，数量:', allPhotosData.value.length);
    }

    // 根据当前视图显示照片
    const displayPhotos = async () => {
      console.log('displayPhotos called, filter:', props.filter, 'currentAlbumId:', currentAlbumId.value);

      if (props.filter === 'trash') {
        console.log('获取回收站照片');
        return await store.getTrashPhotos();
      } else if (props.filter === 'recent') {
        console.log('获取最近照片');
        return await store.getRecentPhotos();
      } else if (currentAlbumId.value) {
        console.log('获取相册照片，相册ID:', currentAlbumId.value);
        return await store.getPhotosByAlbum(currentAlbumId.value);
      } else {
        console.log('获取所有照片');
        return await store.getAllPhotos();
      }
    }

    // 监听视图变化
    watch([() => props.filter, currentAlbumId], async () => {
      console.log('视图变化，重新加载照片');
      await loadPhotos();
    }, {immediate: true})

    // 上传照片
    const handleUpload = async (files) => {
      console.log('开始上传照片，文件数量:', files.length);

      for (const file of files) {
        const formData = new FormData()
        formData.append('photo', file)
        formData.append('user_id', store.getUserId())

        const result = await store.addPhoto(formData)
        if (result.success) {
          console.log('照片上传成功:', result.photoId);
          // 只获取新上传的照片
          const newPhoto = await store.getPhotoById(result.photoId);
          if (newPhoto) {
            allPhotosData.value = [newPhoto, ...allPhotosData.value];
          }
        } else {
          console.error('照片上传失败:', result.message);
        }
      }
    }

    // 按日期分组的照片
    const groupedPhotos = computed(() => {
      if (!allPhotosData.value || !Array.isArray(allPhotosData.value)) {
        console.log("groupedPhotos: 照片数据无效", allPhotosData.value);
        return [];
      }

      console.log("groupedPhotos: 处理照片数据，数量:", allPhotosData.value.length);
      console.log("照片数据示例:", allPhotosData.value.length > 0 ? allPhotosData.value[0] : null);

      // 首先按时间排序
      const sorted = [...allPhotosData.value].sort((a, b) => {
        switch (sortOrder.value) {
          case 'time-desc':
            return new Date(b.time || 0) - new Date(a.time || 0);
          case 'time-asc':
            return new Date(a.time || 0) - new Date(b.time || 0);
          default:
            return 0;
        }
      });

      // 按日期分组
      const groups = {};
      sorted.forEach(photo => {
        // 确保日期正确解析
        const photoDate = photo.time ? new Date(photo.time) : new Date();
        // 使用年月日格式
        const dateKey = formatDate(photoDate);
        if (!groups[dateKey]) {
          groups[dateKey] = [];
        }
        groups[dateKey].push(photo);
      });

      // 转换为数组格式
      const result = Object.entries(groups).map(([date, photos]) => ({
        date,
        photos
      }));

      console.log("groupedPhotos: 分组结果，组数:", result.length);
      return result;
    })

    // 获取所有相册列表
    const albums = computed(() => store.getAllAlbums())

    // 判断是否为最近上传页面
    const isRecentPage = computed(() => props.filter === 'recent')

    // 获取最近一周的照片（按上传时间倒序排列）
    const recentPhotos = computed(() => {
      if (!allPhotosData.value || !Array.isArray(allPhotosData.value)) return [];

      const oneWeekAgo = new Date();
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

      return allPhotosData.value
          .filter(photo => {
            // 确保日期正确解析
            const photoDate = photo.time ? new Date(photo.time) : new Date();
            return photoDate >= oneWeekAgo;
          })
          .sort((a, b) => new Date(b.time || 0) - new Date(a.time || 0));
    })

    // 移动端排序后的照片
    const sortedPhotos = computed(() => {
      if (!allPhotosData.value || !Array.isArray(allPhotosData.value)) return [];

      return [...allPhotosData.value].sort((a, b) => {
        switch (sortOrder.value) {
          case 'time-desc':
            return new Date(b.time || 0) - new Date(a.time || 0);
          case 'time-asc':
            return new Date(a.time || 0) - new Date(b.time || 0);
          default:
            return 0;
        }
      });
    })

    // 处理文件上传
    const handleFileUpload = async (event) => {
      console.log('文件上传开始');
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

          // 确保添加文件
          formData.append('photo', file);

          const userId = store.getUserId();
          console.log(`用户ID: ${userId}`);
          formData.append('user_id', userId);

          if (currentAlbumId.value) {
            console.log(`相册ID: ${currentAlbumId.value}`);
            formData.append('album_id', currentAlbumId.value);
          }

          formData.append('text', file.name);

          console.log('开始上传...');

          // 上传照片 - 使用fetch直接上传
          try {
            const response = await fetch(`${API_BASE_URL}/photos/upload`, {
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

        // 刷新照片列表
        console.log('刷新照片列表');
        await loadPhotos();

      } catch (error) {
        console.error('处理文件上传过程中出错:', error);
        alert(`上传处理失败: ${error.message || '未知错误'}`);
      }
    }

    // 触发文件选择
    const triggerUpload = () => {
      fileInput.value.click()
    }

    // 相册列表
    const albumsList = ref([])

    // 移动照片到相册
    const moveToAlbum = async (photo) => {
      photoToMove.value = photo
      // 在显示对话框前先加载最新的相册列表
      try {
        albumsList.value = await store.getAllAlbums()
        console.log('加载相册列表成功，数量:', albumsList.value.length)
      } catch (error) {
        console.error('加载相册列表失败:', error)
        albumsList.value = []
      }
      showMoveDialog.value = true
    }

    // 确认移动到相册
    const confirmMoveToAlbum = (albumId) => {
      if (photoToMove.value) {
        store.movePhotoToAlbum(photoToMove.value.id, albumId)
        showMoveDialog.value = false
        photoToMove.value = null
      }
    }

    // 删除照片
    const deletePhoto = (photoId) => {
      if (props.filter === 'trash') {
        // 在回收站中，执行永久删除
        if (confirm('确定要永久删除这张照片吗？此操作不可恢复。')) {
          store.permanentlyDelete(photoId).then(async (result) => {
            if (result.success) {
              // 重新加载回收站照片
              await loadPhotos();
            } else {
              alert('删除失败：' + result.message);
            }
          });
        }
      } else {
        // 在其他页面，移动到回收站
        if (confirm('确定要将这张照片移到回收站吗？')) {
          store.moveToTrash(photoId).then(async (result) => {
            if (result.success) {
              // 重新加载照片列表
              await loadPhotos();
            } else {
              alert('移动到回收站失败：' + result.message);
            }
          });
        }
      }
    }

    // 恢复照片
    const restorePhoto = (photoId) => {
      if (confirm('确定要恢复这张照片吗？')) {
        store.restoreFromTrash(photoId).then(async (result) => {
          if (result.success) {
            // 重新加载回收站照片
            await loadPhotos();
          } else {
            alert('恢复失败：' + result.message);
          }
        });
      }
    }

    // 搜索相关
    const searchKeyword = ref('')
    const isSearching = ref(false)
    const searchResults = ref([]) // 存储搜索结果

    // 获取当前视图类型，用于搜索
    const currentView = computed(() => {
      if (props.filter === 'trash') return 'trash'
      if (props.filter === 'recent') return 'recent'
      if (currentAlbumId.value) return 'album' // 相册视图特殊处理
      return 'all'
    })

    // 搜索照片
    const searchPhotos = async () => {
      if (!searchKeyword.value.trim()) return

      console.log(`执行搜索，关键词: "${searchKeyword.value}", 当前视图: ${currentView.value}`);

      try {
        // 在相册视图特殊处理
        if (currentView.value === 'album' && currentAlbumId.value) {
          // 先获取所有相册照片
          const albumPhotos = await store.getPhotosByAlbum(currentAlbumId.value) || []
          // 本地过滤
          searchResults.value = albumPhotos.filter(photo =>
              (photo.text && photo.text.toLowerCase().includes(searchKeyword.value.toLowerCase())) ||
              (photo.time && new Date(photo.time).toLocaleDateString('zh-CN').includes(searchKeyword.value))
          )
        } else {
          // 其他视图使用API搜索
          searchResults.value = await store.searchPhotos(searchKeyword.value, currentView.value) || []
        }

        console.log(`搜索完成，找到 ${searchResults.value.length} 张照片`);
        isSearching.value = true
      } catch (error) {
        console.error('搜索出错:', error)
        searchResults.value = []
        isSearching.value = true
      }
    }

    // 根据关键词过滤照片（使用搜索结果）
    const filteredPhotos = computed(() => {
      return searchResults.value
    })

    // 清除搜索
    const clearSearch = () => {
      searchKeyword.value = ''
      isSearching.value = false
      searchResults.value = []
    }

    // 获取完整的图片URL
    const getPhotoUrl = (photo) => {
      if (!photo || !photo.address) return '';

      // 如果是绝对URL，直接返回
      if (photo.address.startsWith('http')) {
        return photo.address;
      }

      // 否则构建完整URL
      const fullUrl = `http://114.215.184.67:5000/${photo.address}`;
      console.log('Photo URL:', fullUrl);
      return fullUrl;
    }

    // 自定义日期格式化函数
    const formatDate = (date) => {
      if (!date) return '';

      // 确保date是Date对象
      const dateObj = date instanceof Date ? date : new Date(date);

      // 检查日期是否有效
      if (isNaN(dateObj.getTime())) return '';

      // 格式化为 YYYY-MM-DD
      const year = dateObj.getFullYear();
      // 月份需要+1，因为getMonth()返回0-11
      const month = String(dateObj.getMonth() + 1).padStart(2, '0');
      const day = String(dateObj.getDate()).padStart(2, '0');

      return `${year}-${month}-${day}`;
    }

    return {
      isMobile,
      viewMode,
      sortOrder,
      selectedPhotos,
      showMoveDialog,
      fileInput,
      currentAlbum,
      pageTitle,
      displayPhotos,
      groupedPhotos,
      albums,
      handleFileUpload,
      triggerUpload,
      moveToAlbum,
      confirmMoveToAlbum,
      deletePhoto,
      restorePhoto,
      formatDate,
      isRecentPage,
      recentPhotos,
      sortedPhotos,
      searchKeyword,
      isSearching,
      filteredPhotos,
      searchPhotos,
      clearSearch,
      getPhotoUrl,
      allPhotosData,
      filter,
      albumsList
    }
  }
}
</script>

<style scoped>
.photo-gallery {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 0;
  margin: 0 20px; /* 减少左右边距 */
  box-sizing: border-box;
  overflow: hidden;
}

.gallery-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #fff;
  border-bottom: 1px solid #eee;
  padding: 1rem 0;
  flex-shrink: 0;
}

.gallery-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
  width: 100%;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  white-space: nowrap;
  min-width: 200px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

/* 搜索框样式 */
.search-box {
  display: flex;
  align-items: center;
  min-width: 250px;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 0.5rem 2.5rem 0.5rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: #1890ff;
}

.search-btn {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 0.3rem;
}

.search-btn:hover {
  color: #1890ff;
}

/* 搜索结果提示样式 */
.search-result-info {
  margin: 1rem 0;
  padding: 0.8rem;
  background: #f8f9fa;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.clear-search {
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.3rem 0.8rem;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.clear-search:hover {
  background: #f0f0f0;
  color: #333;
}

.gallery-content {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  padding: 1rem 0;
  width: 100%;
}

/* 隐藏Webkit浏览器的滚动条 */
.gallery-content::-webkit-scrollbar {
  display: none;
}

.header-left h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 500;
}

.photo-count {
  color: #999;
  margin-left: 1rem;
}

.view-mode {
  display: flex;
  gap: 0.5rem;
}

.view-mode button {
  padding: 0.5rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.view-mode button.active {
  background: #e6f3ff;
  border-color: #1890ff;
  color: #1890ff;
}

.sort-by select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #666;
}

.time-divider {
  width: 100%;
  padding: 0.8rem 0;
  color: #666;
  font-weight: 500;
  font-size: 1.1rem;
}

.photo-group {
  margin-bottom: 1.5rem;
}

.photo-grid-pc {
  display: grid;
  gap: 1rem;
  padding: 0.8rem 0;
  width: 100%;
}

.photo-grid-pc.grid {
  grid-template-columns: repeat(8, 1fr); /* 固定8列 */
}

.photo-grid-pc.list {
  grid-template-columns: 1fr;
}

.photo-wrapper {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 8px;
  background: #f5f5f5;
}

.photo-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-hover-info {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  color: white;
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 1rem;
}

.photo-wrapper:hover .photo-hover-info {
  opacity: 1;
}

.hover-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.hover-bottom {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.photo-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.3rem;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.action-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.action-btn i {
  font-size: 1.2rem;
}

/* 根据屏幕宽度调整列数 */
@media (max-width: 2400px) {
  .photo-grid-pc.grid {
    grid-template-columns: repeat(7, 1fr);
  }
}

@media (max-width: 2000px) {
  .photo-grid-pc.grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (max-width: 1700px) {
  .photo-grid-pc.grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 1400px) {
  .photo-grid-pc.grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1100px) {
  .photo-grid-pc.grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .photo-grid-pc.grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 移动端样式 */
.mobile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}

.mobile-header h2 {
  margin: 0;
  font-size: 1.2rem;
}

.photo-grid-mobile {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  padding: 0.5rem;
}

.photo-grid-mobile::-webkit-scrollbar {
  display: none;
}

.photo-item-mobile {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  background: white;
}

.photo-item-mobile img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
}

.photo-info-mobile {
  padding: 0.8rem;
}

.photo-info-mobile .photo-description {
  display: block;
  font-size: 0.9rem;
  margin-bottom: 0.4rem;
}

.photo-info-mobile .photo-date {
  color: #666;
  font-size: 0.8rem;
}

/* 移动到相册弹窗样式 */
.move-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  min-width: 300px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.dialog-content h3 {
  margin: 0 0 1rem 0;
  font-size: 1.2rem;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.8rem;
}

.album-list {
  max-height: 300px;
  overflow-y: auto;
  margin: 1rem 0;
}

.album-option {
  padding: 0.8rem 1rem;
  cursor: pointer;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  transition: background-color 0.2s;
}

.album-option:hover {
  background-color: #f0f7ff;
}

.no-albums {
  text-align: center;
  padding: 2rem 0;
  color: #666;
}

.no-albums .hint {
  font-size: 0.9rem;
  color: #999;
  margin-top: 0.5rem;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.cancel-btn {
  padding: 0.6rem 1.2rem;
  background: #f5f5f5;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: #333;
}

.cancel-btn:hover {
  background: #e5e5e5;
}

.recent-photos-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 1rem;
  padding: 0.8rem 0;
  width: 100%;
}

/* 响应式布局 */
@media (max-width: 2400px) {
  .recent-photos-grid {
    grid-template-columns: repeat(7, 1fr);
  }
}

@media (max-width: 2000px) {
  .recent-photos-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (max-width: 1700px) {
  .recent-photos-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 1400px) {
  .recent-photos-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1100px) {
  .recent-photos-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .recent-photos-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 新增按钮样式 */
.restore-btn:hover {
  background-color: rgba(50, 205, 50, 0.3); /* 恢复按钮悬停时显示绿色背景 */
}

.delete-btn:hover {
  background-color: rgba(255, 0, 0, 0.3); /* 永久删除按钮悬停时显示红色背景 */
}
</style> 