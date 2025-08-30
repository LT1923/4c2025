import {ref, computed} from 'vue'

// 用户状态
const currentUser = ref(null)
const isAuthenticated = computed(() => !!currentUser.value)

// API基础URL
// const API_BASE_URL = '/api'  // 使用相对路径，通过Vite代理访问后端
const API_BASE_URL = 'http://114.215.184.67:5000/api'

export function useUserStore() {
    // 登录
    const login = async (phone, password) => {
        try {
            const response = await fetch(`${API_BASE_URL}/users/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({phone, password})
            })

            // 检查响应状态
            if (!response.ok) {
                console.error('服务器返回错误状态码:', response.status);
                if (response.status === 500) {
                    return {success: false, message: '服务器内部错误，请联系管理员或稍后再试'};
                }
                return {success: false, message: `服务器错误 (${response.status})`};
            }

            const data = await response.json()

            if (data.success) {
                // 登录成功，保存用户信息
                currentUser.value = data.user
                // 保存到本地存储，以便刷新页面后保持登录状态
                localStorage.setItem('user', JSON.stringify(data.user))
                return {success: true, user: data.user}
            } else {
                // 登录失败
                return {success: false, message: data.message}
            }
        } catch (error) {
            console.error('登录请求失败:', error)
            return {success: false, message: '网络错误，请稍后再试'}
        }
    }

    // 注册
    const register = async (phone, password) => {
        try {
            const response = await fetch(`${API_BASE_URL}/users/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({phone, password})
            })

            // 检查响应状态
            if (!response.ok) {
                console.error('服务器返回错误状态码:', response.status);
                if (response.status === 500) {
                    return {success: false, message: '服务器内部错误，请联系管理员或稍后再试'};
                }
                return {success: false, message: `服务器错误 (${response.status})`};
            }

            const data = await response.json()

            if (data.success) {
                // 注册成功
                return {success: true, message: data.message, userId: data.user_id}
            } else {
                // 注册失败
                return {success: false, message: data.message}
            }
        } catch (error) {
            console.error('注册请求失败:', error)
            return {success: false, message: '网络错误，请稍后再试'}
        }
    }

    // 登出
    const logout = () => {
        currentUser.value = null
        localStorage.removeItem('user')
        return {success: true}
    }

    // 检查是否已登录（从本地存储恢复用户状态）
    const checkAuth = () => {
        if (!currentUser.value) {
            const savedUser = localStorage.getItem('user')
            if (savedUser) {
                try {
                    currentUser.value = JSON.parse(savedUser)
                } catch (e) {
                    localStorage.removeItem('user')
                }
            }
        }
        return isAuthenticated.value
    }

    // 获取当前用户
    const getUser = () => currentUser.value

    // 检查用户是否已登录
    const isLoggedIn = () => {
        return checkAuth();
    }

    return {
        login,
        register,
        logout,
        checkAuth,
        getUser,
        isAuthenticated,
        isLoggedIn
    }
}