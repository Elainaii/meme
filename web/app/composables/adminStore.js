import { ref } from 'vue'

export const useAdminStore = () => {
  const isAuthenticated = ref(false)
  
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
