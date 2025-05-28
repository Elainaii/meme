<script setup>
import { ref, onMounted } from 'vue'
import { apiRequest, getApiBaseUrl } from '~/utils/api'

const imageUrl = ref('')
const imageInfo = ref(null)
const loading = ref(true)
const error = ref(null)
const imageLoading = ref(false)

// 从服务器获取随机图片
async function fetchRandomImage() {
  loading.value = true
  error.value = null

  try {
    // 调用新的图片信息API
    const response = await apiRequest('/image')
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    imageInfo.value = data
      // 设置图片URL
    if (data.image_url.startsWith('http')) {
      // 如果是完整的图床URL，直接使用
      imageUrl.value = data.image_url
    } else {
      // 如果是相对路径，拼接API基础URL
      const apiUrl = getApiBaseUrl()
      imageUrl.value = `${apiUrl}${data.image_url}`
    }
    
    // 添加时间戳防止缓存问题
    if (imageUrl.value.includes('?')) {
      imageUrl.value += `&t=${Date.now()}`
    } else {
      imageUrl.value += `?t=${Date.now()}`
    }
    
  } catch (e) {
    console.error('获取图片时出错:', e)
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 获取新的随机图片
function getNewImage() {
  fetchRandomImage()
}

// 处理图片加载错误
function handleImageError() {
  error.value = '图片加载失败，可能是网络问题或图片链接无效'
}

// 组件挂载时获取第一张图片
onMounted(() => {
  fetchRandomImage()
})
</script>

<template>
  <div class="flex flex-col items-center">
    <div class="mb-6 p-4 rounded-xl bg-white max-w-md w-full shadow-lg sm:mb-8 sm:p-6 dark:bg-gray-800">
      <div v-if="loading" class="p-4 text-center">
        <div class="mb-4 flex justify-center">
          <div class="i-carbon-image-search text-4xl text-blue-500 animate-pulse"/>
        </div>
        <h2 class="text-lg font-medium mb-3">
          正在加载图片...
        </h2>
      </div>

      <div v-else-if="error" class="p-4 text-center">
        <div class="mb-4 flex justify-center">
          <div class="i-carbon-warning-alt text-4xl text-yellow-500"/>
        </div>
        <h2 class="text-lg font-medium mb-3">
          加载图片失败
        </h2>
        <p class="text-sm text-gray-600 mb-4 dark:text-gray-400">
          {{ error }}
        </p>
        <button @click="getNewImage" class="text-blue-700 px-4 py-2 rounded-lg bg-blue-100 inline-flex gap-2 transition-colors items-center dark:text-blue-300 dark:bg-blue-900/50 hover:bg-blue-200 dark:hover:bg-blue-800/70">
          <span class="i-carbon-restart" />
          <span>重试</span>
        </button>
      </div>      <div v-else class="p-4 text-center">
        <div class="mb-4 relative">
          <!-- 图片加载指示器 -->
          <div 
            v-if="imageLoading" 
            class="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded-lg"
          >
            <div class="flex flex-col items-center">
              <div class="i-carbon-circle-dash text-2xl text-blue-500 animate-spin mb-2" />
              <span class="text-xs text-gray-500 dark:text-gray-400">图片加载中...</span>
            </div>
          </div>
          
          <img 
            :src="imageUrl" 
            :alt="imageInfo?.file_name || '随机图片'" 
            class="rounded-lg max-w-full h-auto shadow-md"
            @load="imageLoading = false"
            @loadstart="imageLoading = true"
            @error="handleImageError"
          />
        </div>
        
        <!-- 图片信息 -->
        <div v-if="imageInfo" class="mb-4 text-xs text-gray-500 dark:text-gray-400">
          <p>文件名: {{ imageInfo.file_name }}</p>
          <div class="flex justify-center gap-4 mt-1">
            <span class="flex items-center gap-1">
              <span class="i-carbon-thumbs-up" />
              {{ imageInfo.likes || 0 }}
            </span>
            <span class="flex items-center gap-1">
              <span class="i-carbon-thumbs-down" />
              {{ imageInfo.dislikes || 0 }}
            </span>
          </div>
        </div>
        
        <p class="text-sm text-gray-600 mb-4 dark:text-gray-400">
          这是一张从图床随机获取的图片
        </p>
        <button @click="getNewImage" class="text-blue-700 px-4 py-2 rounded-lg bg-blue-100 inline-flex gap-2 transition-colors items-center dark:text-blue-300 dark:bg-blue-900/50 hover:bg-blue-200 dark:hover:bg-blue-800/70">
          <span class="i-carbon-renew" />
          <span>换一张</span>
        </button>
      </div>
    </div>
  </div>
</template>
