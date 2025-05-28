// 获取运行时配置的API基础URL
export function getApiBaseUrl() {
  if (process.client) {
    // 客户端运行时，使用Nuxt的运行时配置
    const config = useRuntimeConfig()
    return process.env.NODE_ENV === 'development' 
      ? (config.public.devApiBaseUrl || 'http://localhost:8001')
      : config.public.apiBaseUrl
  } else {
    // 服务端运行时，使用Nuxt的运行时配置
    const config = useRuntimeConfig()
    return process.env.NODE_ENV === 'development' 
      ? (config.public.devApiBaseUrl || 'http://localhost:8001')
      : config.public.apiBaseUrl
  }
}

// API配置
export const API_CONFIG = {
  // 动态获取API基础URL
  get baseURL() {
    return getApiBaseUrl()
  }
}

// 创建API请求函数
export async function apiRequest(endpoint, options = {}) {
  const url = `${API_CONFIG.baseURL}${endpoint}`
  
  const defaultOptions = {
    headers: {
      ...options.headers
    }
  }
  
  // 如果不是FormData，则设置JSON Content-Type
  if (!(options.body instanceof FormData)) {
    defaultOptions.headers['Content-Type'] = 'application/json'
  }
  
  return fetch(url, { ...defaultOptions, ...options })
}

// 获取图片URL
export function getImageUrl(path) {
  return `${API_CONFIG.baseURL}${path}`
}

// 预加载图片
export function preloadImage(url) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = url
  })
}
