import {ref, computed} from 'vue'
import {useUserStore} from './useUserStore'

// API基础URL
// const API_BASE_URL = '/api'  // 使用相对路径，配合vite代理使用
const API_BASE_URL = 'http://114.215.184.67:5000/api'

// 获取用户状态
const getUserStore = () => {
    const userStore = useUserStore()
    return userStore
}

// 获取当前用户ID
const getCurrentUserId = () => {
    const userStore = getUserStore()
    const user = userStore.getUser()
    return user ? user.id : null
}

export function usePhotoStore() {
    // 获取用户ID - 用于上传
    const getUserId = () => {
        return getCurrentUserId()
    }

    // 获取所有照片（不包括回收站的照片）
    const getAllPhotos = async () => {
        const userId = getCurrentUserId()
        if (!userId) return []

        try {
            const response = await fetch(`${API_BASE_URL}/photos/user/${userId}`)
            const data = await response.json()

            if (data.success) {
                return data.photos
            }
            return []
        } catch (error) {
            console.error('获取照片失败:', error)
            return []
        }
    }

    // 获取最近照片
    const getRecentPhotos = async () => {
        const userId = getCurrentUserId()
        if (!userId) return []

        try {
            const response = await fetch(`${API_BASE_URL}/photos/recent/${userId}`)
            const data = await response.json()

            if (data.success) {
                return data.photos
            }
            return []
        } catch (error) {
            console.error('获取最近照片失败:', error)
            return []
        }
    }

    // 获取回收站照片
    const getTrashPhotos = async () => {
        const userId = getCurrentUserId()
        if (!userId) return []

        console.log("开始获取回收站照片，用户ID:", userId);

        try {
            const response = await fetch(`${API_BASE_URL}/photos/trash/${userId}`)
            console.log("回收站照片响应状态:", response.status);

            const data = await response.json()
            console.log("回收站照片响应数据:", data);

            if (data.success) {
                console.log("获取到回收站照片，数量:", data.photos.length);
                return data.photos
            }
            console.log("获取回收站照片失败，返回空数组");
            return []
        } catch (error) {
            console.error('获取回收站照片失败:', error)
            return []
        }
    }

    // 获取指定图集的照片
    const getPhotosByAlbum = async (albumId) => {
        if (!albumId) return []

        try {
            const response = await fetch(`${API_BASE_URL}/albums/${albumId}/photos`)
            const data = await response.json()

            if (data.success) {
                return data.photos
            }
            return []
        } catch (error) {
            console.error('获取图集照片失败:', error)
            return []
        }
    }

    // 获取所有图集
    const getAllAlbums = async () => {
        const userId = getCurrentUserId()
        if (!userId) return []

        try {
            const response = await fetch(`${API_BASE_URL}/albums/user/${userId}`)
            const data = await response.json()

            if (data.success) {
                return data.albums
            }
            return []
        } catch (error) {
            console.error('获取图集失败:', error)
            return []
        }
    }

    // 获取指定图集
    const getAlbumById = async (albumId) => {
        if (!albumId) return null

        try {
            const response = await fetch(`${API_BASE_URL}/albums/${albumId}`)
            const data = await response.json()

            if (data.success) {
                return data.album
            }
            return null
        } catch (error) {
            console.error('获取图集详情失败:', error)
            return null
        }
    }

    // 上传照片
    const addPhoto = async (formData) => {
        try {
            // 检查是否是FormData类型
            if (formData instanceof FormData) {
                // 打印调试信息
                console.log('准备上传照片，FormData内容:');
                try {
                    for (let [key, value] of formData.entries()) {
                        console.log(`${key}: ${value instanceof File ? value.name : value}`);
                    }
                } catch (e) {
                    console.log('无法遍历FormData内容:', e);
                }

                const response = await fetch(`${API_BASE_URL}/photos/upload`, {
                    method: 'POST',
                    body: formData,
                })

                console.log('上传响应状态:', response.status);

                const data = await response.json()
                console.log('上传响应数据:', data);

                if (data.success) {
                    return {success: true, photoId: data.photo_id, photoUrl: data.photo_url}
                } else {
                    console.error('上传失败:', data.message);
                    return {success: false, message: data.message}
                }
            } else {
                return {success: false, message: '无效的照片数据'}
            }
        } catch (error) {
            console.error('上传照片失败:', error)
            return {success: false, message: '网络错误，请稍后再试'}
        }
    }

    // 创建新相册
    const createAlbum = async (albumData) => {
        try {
            console.log('创建相册，数据:', albumData);
            const response = await fetch(`${API_BASE_URL}/albums/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(albumData)
            });

            console.log('创建相册响应状态:', response.status);
            const data = await response.json();
            console.log('创建相册响应数据:', data);

            if (response.ok) {
                return {success: true, album: data.album};
            }
            return {success: false, message: data.message || '创建图集失败'};
        } catch (error) {
            console.error('创建图集失败:', error);
            return {success: false, message: error.message};
        }
    };

    // 将照片移动到图集
    const movePhotoToAlbum = async (photoId, albumId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/photos/move/${photoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({album_id: albumId})
            })

            const data = await response.json()

            if (data.success) {
                return {success: true}
            } else {
                return {success: false, message: data.message}
            }
        } catch (error) {
            console.error('移动照片失败:', error)
            return {success: false, message: '网络错误，请稍后再试'}
        }
    }

    // 删除照片
    const deletePhoto = async (photoId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/photos/${photoId}`, {
                method: 'DELETE'
            })

            const data = await response.json()

            if (data.success) {
                return {success: true}
            } else {
                return {success: false, message: data.message}
            }
        } catch (error) {
            console.error('删除照片失败:', error)
            return {success: false, message: '网络错误，请稍后再试'}
        }
    }

    // 删除图集
    const deleteAlbum = async (albumId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/albums/${albumId}`, {
                method: 'DELETE'
            })

            const data = await response.json()

            if (data.success) {
                return {success: true}
            } else {
                return {success: false, message: data.message}
            }
        } catch (error) {
            console.error('删除图集失败:', error)
            return {success: false, message: '网络错误，请稍后再试'}
        }
    }

    // 更新照片信息
    const updatePhoto = async (photoId, updates) => {
        try {
            const response = await fetch(`${API_BASE_URL}/photos/${photoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            })

            const data = await response.json()

            if (data.success) {
                return {success: true}
            } else {
                return {success: false, message: data.message}
            }
        } catch (error) {
            console.error('更新照片失败:', error)
            return {success: false, message: '网络错误，请稍后再试'}
        }
    }

    // 更新相册
    const updateAlbum = async (albumId, albumData) => {
        try {
            console.log('更新相册，ID:', albumId, '数据:', albumData);

            const response = await fetch(`${API_BASE_URL}/albums/${albumId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(albumData)
            });

            console.log('更新相册响应状态:', response.status);
            const data = await response.json();
            console.log('更新相册响应数据:', data);

            if (response.ok) {
                return {success: true, album: data.album};
            }
            return {success: false, message: data.message || '更新图集失败'};
        } catch (error) {
            console.error('更新图集失败:', error);
            return {success: false, message: error.message};
        }
    };

    // 搜索照片
    const searchPhotos = async (keyword, view = 'all') => {
        const userId = getCurrentUserId()
        if (!userId) return []

        console.log(`搜索照片，关键词: "${keyword}"，视图: "${view}"`);

        try {
            const response = await fetch(`${API_BASE_URL}/photos/search/${userId}?keyword=${encodeURIComponent(keyword)}&view=${view}`)
            const data = await response.json()

            if (data.success) {
                console.log(`搜索结果: 找到 ${data.photos.length} 张照片`);
                return data.photos
            }
            console.log('搜索失败:', data.message);
            return []
        } catch (error) {
            console.error('搜索照片失败:', error)
            return []
        }
    }

    // 将照片移动到回收站
    const moveToTrash = async (photoId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/photos/${photoId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({status: 1}) // 1表示在回收站
            })

            const data = await response.json()

            if (data.success) {
                return {success: true}
            }
            return {success: false, message: data.message || '移动到回收站失败'}
        } catch (error) {
            console.error('移动到回收站失败:', error)
            return {success: false, message: error.message}
        }
    }

    // 从回收站恢复照片
    const restoreFromTrash = async (photoId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/photos/${photoId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({status: 0}) // 0表示正常状态
            })

            const data = await response.json()

            if (data.success) {
                return {success: true}
            }
            return {success: false, message: data.message || '恢复照片失败'}
        } catch (error) {
            console.error('恢复照片失败:', error)
            return {success: false, message: error.message}
        }
    }

    // 永久删除照片
    const permanentlyDelete = async (photoId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/photos/${photoId}`, {
                method: 'DELETE'
            })

            const data = await response.json()

            if (data.success) {
                return {success: true}
            }
            return {success: false, message: data.message || '删除照片失败'}
        } catch (error) {
            console.error('删除照片失败:', error)
            return {success: false, message: error.message}
        }
    }

    return {
        getUserId,
        getAllPhotos,
        getRecentPhotos,
        getTrashPhotos,
        getPhotosByAlbum,
        getAllAlbums,
        getAlbumById,
        addPhoto,
        createAlbum,
        movePhotoToAlbum,
        deletePhoto,
        deleteAlbum,
        updatePhoto,
        updateAlbum,
        searchPhotos,
        moveToTrash,
        restoreFromTrash,
        permanentlyDelete
    }
} 