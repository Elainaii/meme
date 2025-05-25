// 验证管理员权限中间件
export default defineNuxtRouteMiddleware((to, from) => {
  // 只在客户端执行
  if (process.client) {
    // 如果尝试访问管理面板页面
    if (to.path.startsWith('/admin')) {
      // 检查是否有管理员令牌
      const token = localStorage.getItem('admin_token')
      if (!token) {
        // 如果没有令牌，重定向到登录页面
        return navigateTo('/login')
      }
    }
  }
})
