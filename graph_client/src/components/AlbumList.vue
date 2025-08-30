<template>
  <div class="album-list">
    <div class="album-header">
      <h2>图集</h2>
      <button class="create-album-btn" @click="showCreateDialog = true">
        <i class="icon">+</i> 创建新图集
      </button>
    </div>

    <!-- PC端布局 -->
    <div v-if="!isMobile" class="albums-container">
      <div class="albums-grid-pc">
        <div v-for="album in albums" :key="album.id" class="album-item">
          <div class="album-cover" @click="openAlbum(album.id)">
            <img :src="getCoverUrl(album)" :alt="album.name">
            <div class="album-hover-info">
              <span class="photo-count">{{ albumPhotoCount[album.id] || 0 }}张照片</span>
            </div>
          </div>
          <div class="album-info">
            <div class="album-title">
              <h3>{{ album.name }}</h3>
              <div class="album-actions">
                <button class="action-btn" @click.stop="editAlbum(album)">
                  <i class="icon">✏️</i>
                </button>
                <button class="action-btn" @click.stop="deleteAlbum(album.id)">
                  <i class="icon">🗑️</i>
                </button>
              </div>
            </div>
            <p class="album-date">创建于 {{ formatDate(album.created_at) }}</p>
            <p class="album-desc">{{ album.content }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 移动端布局 -->
    <div v-else class="albums-grid-mobile">
      <div v-for="album in albums" :key="album.id" class="album-item-mobile" @click="openAlbum(album.id)">
        <div class="album-cover-mobile">
          <img :src="getCoverUrl(album)" :alt="album.name">
        </div>
        <div class="album-info-mobile">
          <div>
            <h3>{{ album.name }}</h3>
            <p>{{ albumPhotoCount[album.id] || 0 }}张照片</p>
          </div>
          <i class="arrow-right">›</i>
        </div>
      </div>
    </div>

    <!-- 创建/编辑相册弹窗 -->
    <div v-if="showCreateDialog || editingAlbum" class="album-dialog">
      <div class="dialog-content">
        <h3>{{ editingAlbum ? '编辑相册' : '创建新图集' }}</h3>
        <form @submit.prevent="handleSubmit" class="album-form">
          <div class="form-group">
            <label>图集名称</label>
            <input
                v-model="albumForm.name"
                type="text"
                placeholder="请输入图集名称"
                required
            >
          </div>
          <div class="form-group">
            <label>图集描述</label>
            <textarea
                v-model="albumForm.description"
                placeholder="请输入图集描述"
                rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label>封面图片 {{ editingAlbum ? '(可选)' : '(必选)' }}</label>
            <input
                type="file"
                ref="coverInput"
                accept="image/*"
                @change="handleCoverUpload"
                :required="!editingAlbum"
            >
            <div v-if="editingAlbum && editingAlbum.cover_url" class="current-cover-info">
              <p>当前封面：{{ editingAlbum.cover_url }}</p>
            </div>
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeDialog">取消</button>
            <button type="submit" class="submit-btn">
              {{ editingAlbum ? '保存' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import {useDevice} from '../composables/useDevice'
import {usePhotoStore} from '../composables/usePhotoStore'
import {ref, computed, onMounted} from 'vue'
import {useRouter} from 'vue-router'

export default {
  name: 'AlbumList',
  setup() {
    const {isMobile} = useDevice()
    const store = usePhotoStore()
    const router = useRouter()

    const showCreateDialog = ref(false)
    const editingAlbum = ref(null)
    const albumForm = ref({
      name: '',
      description: '',
      coverFile: null
    })

    // 获取所有相册
    const albums = ref([])

    // 获取每个相册的照片数量
    const albumPhotoCount = ref({})

    // 加载相册数据
    const loadAlbums = async () => {
      try {
        const albumData = await store.getAllAlbums()
        albums.value = albumData

        // 获取每个相册的照片数量
        for (const album of albumData) {
          const photos = await store.getPhotosByAlbum(album.id)
          albumPhotoCount.value[album.id] = photos.length
        }
      } catch (error) {
        console.error('加载相册失败:', error)
      }
    }

    // 页面加载时获取相册数据
    onMounted(() => {
      loadAlbums()
    })

    // 打开相册
    const openAlbum = (albumId) => {
      router.push(`/album/${albumId}`)
    }

    // 处理封面图片上传
    const handleCoverUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
        albumForm.value.coverFile = file;
      }
    }

    // 创建或更新相册
    const handleSubmit = async () => {
      try {
        // 首先检查是否有封面文件
        if (!albumForm.value.coverFile && !editingAlbum.value) {
          alert('请选择封面图片');
          return;
        }

        // 准备基本相册数据
        const albumData = {
          name: albumForm.value.name,
          content: albumForm.value.description,
          user_id: store.getUserId()
        };

        // 如果有封面文件，先上传封面
        if (albumForm.value.coverFile) {
          console.log('上传封面图片:', albumForm.value.coverFile.name);

          // 创建FormData对象用于上传照片
          const formData = new FormData();
          formData.append('photo', albumForm.value.coverFile);
          formData.append('user_id', store.getUserId());
          formData.append('text', `${albumForm.value.name} 的封面`);
          formData.append('status', 2); // 添加状态参数，2表示封面图片

          // 上传照片
          try {
            const response = await fetch(`http://114.215.184.67:5000/api/photos/upload`, {
              method: 'POST',
              body: formData
            });

            console.log('封面上传响应状态:', response.status);

            if (response.ok) {
              const data = await response.json();
              console.log('封面上传响应数据:', data);

              if (data.success) {
                console.log('封面上传成功，路径:', data.photo_url);
                // 将得到的路径设置为封面URL
                albumData.cover_url = data.photo_url;
              } else {
                alert(`封面上传失败: ${data.message || '未知错误'}`);
                return;
              }
            } else {
              alert(`封面上传失败，服务器返回: ${response.status}`);
              return;
            }
          } catch (uploadError) {
            console.error('封面上传过程中出错:', uploadError);
            alert(`封面上传失败: ${uploadError.message || '网络错误'}`);
            return;
          }
        }

        // 处理编辑还是新建
        if (editingAlbum.value) {
          const result = await store.updateAlbum(editingAlbum.value.id, albumData);
          if (result.success) {
            await loadAlbums();
            closeDialog();
          } else {
            alert(`更新相册失败: ${result.message || '未知错误'}`);
          }
        } else {
          console.log('创建相册，数据:', albumData);
          const result = await store.createAlbum(albumData);
          if (result.success) {
            await loadAlbums();
            closeDialog();
          } else {
            alert(`创建相册失败: ${result.message || '未知错误'}`);
          }
        }
      } catch (error) {
        console.error('保存图集失败:', error);
        alert('保存图集失败: ' + error.message);
      }
    }

    // 编辑相册
    const editAlbum = (album) => {
      console.log('编辑相册:', album);
      editingAlbum.value = album;
      albumForm.value = {
        name: album.name,
        description: album.content,
        coverFile: null // 在编辑模式下，可以选择是否上传新封面
      };
    }

    // 删除相册
    const deleteAlbum = (albumId) => {
      if (confirm('确定要删除这个相册吗？相册中的照片将被移到未分类')) {
        store.deleteAlbum(albumId)
      }
    }

    // 关闭弹窗
    const closeDialog = () => {
      showCreateDialog.value = false
      editingAlbum.value = null
      albumForm.value = {
        name: '',
        description: '',
        coverFile: null
      }
    }

    // 获取封面图片完整URL
    const getCoverUrl = (album) => {
      if (!album || !album.cover_url) return '';

      // 如果是绝对URL，直接返回
      if (album.cover_url.startsWith('http')) {
        return album.cover_url;
      }

      // 否则构建完整URL
      return `http://114.215.184.67:5000/${album.cover_url}`;
    };

    return {
      isMobile,
      albums,
      albumPhotoCount,
      showCreateDialog,
      editingAlbum,
      albumForm,
      openAlbum,
      editAlbum,
      deleteAlbum,
      handleSubmit,
      closeDialog,
      formatDate: (date) => new Date(date).toLocaleDateString('zh-CN'),
      handleCoverUpload,
      getCoverUrl
    }
  }
}
</script>

<style scoped>
.album-list {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 0;
  margin: 0 20px; /* 减少左右边距 */
  box-sizing: border-box;
  overflow: hidden;
}

.album-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  background: #fff;
  border-bottom: 1px solid #eee;
  z-index: 10;
  flex-shrink: 0;
}

.album-header h2 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 500;
  flex: 1;
}

.create-album-btn {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: 3rem;
}

.albums-container {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  padding: 1.5rem 0;
}

/* 隐藏Webkit浏览器的滚动条 */
.albums-container::-webkit-scrollbar {
  display: none;
}

/* PC端样式 */
.albums-grid-pc {
  display: grid;
  grid-template-columns: repeat(6, 1fr); /* 固定6列 */
  gap: 1.5rem;
  width: 100%;
}

.album-item {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: white;
  transition: transform 0.2s;
}

.album-item:hover {
  transform: translateY(-4px);
}

.album-cover {
  position: relative;
  aspect-ratio: 4/3;
  overflow: hidden;
  cursor: pointer;
}

.album-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.album-hover-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1rem;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
  opacity: 0;
  transition: opacity 0.2s;
}

.album-cover:hover .album-hover-info {
  opacity: 1;
}

.album-info {
  padding: 1rem;
}

.album-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.album-title h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 500;
}

.album-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  background: none;
  border: none;
  padding: 0.4rem;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background-color: #f5f5f5;
}

.album-date {
  color: #666;
  font-size: 0.9rem;
  margin: 0.5rem 0;
}

.album-desc {
  color: #666;
  font-size: 0.9rem;
  margin: 0.5rem 0;
  line-height: 1.4;
  max-height: 2.8em;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 根据屏幕宽度调整列数 */
@media (max-width: 1920px) {
  .albums-grid-pc {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 1500px) {
  .albums-grid-pc {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1200px) {
  .albums-grid-pc {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .albums-grid-pc {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 移动端样式 */
.albums-grid-mobile {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.album-item-mobile {
  display: flex;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.album-cover-mobile {
  width: 100px;
  height: 100px;
  flex-shrink: 0;
}

.album-cover-mobile img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.album-info-mobile {
  flex: 1;
  padding: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.album-info-mobile h3 {
  margin: 0;
  font-size: 1rem;
}

.album-info-mobile p {
  margin: 0.3rem 0 0;
  color: #666;
  font-size: 0.8rem;
}

.arrow-right {
  font-size: 1.5rem;
  color: #999;
}

/* 创建/编辑相册弹窗 */
.album-dialog {
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
  width: 90%;
  max-width: 500px;
}

.dialog-content h3 {
  margin: 0 0 1.5rem;
  font-size: 1.2rem;
}

.album-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #666;
  font-size: 0.9rem;
}

.form-group input,
.form-group textarea {
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.cancel-btn {
  padding: 0.8rem 1.5rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 6px;
  cursor: pointer;
}

.submit-btn {
  padding: 0.8rem 1.5rem;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

@media (max-width: 768px) {
  .album-list {
    padding: 0.5rem;
  }

  .album-header {
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .create-album-btn {
    padding: 0.6rem 1rem;
  }

  .dialog-content {
    width: 95%;
    padding: 1rem;
  }
}
</style> 