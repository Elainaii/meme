import { ref } from 'vue'

// 全局状态，确保所有组件共享同一个状态
const isAuthenticated = ref(false)

export const useAdminStore = () => {
  // 检查是否已登录
  function checkAuth() {
    if (process.client) {
      const token = localStorage.getItem('admin_token')
      isAuthenticated.value = !!token
      return isAuthenticated.value
    }
    return false
  }
  
  // 设置登录状态
  function setAuth(token) {
    if (process.client && token) {
      localStorage.setItem('admin_token', token)
      isAuthenticated.value = true
    }
  }
  
  // 登出
  function logout() {
    if (process.client) {
      localStorage.removeItem('admin_token')
      isAuthenticated.value = false
    }
  }
  
  // 获取token
  function getToken() {
    if (process.client) {
      return localStorage.getItem('admin_token')
    }
    return null
  }
  
  return {
    isAuthenticated,
    checkAuth,
    setAuth,
    logout,
    getToken
  }
}
