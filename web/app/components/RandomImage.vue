<script setup>
import { ref, onMounted } from 'vue'
import { apiRequest } from '~/utils/api'

const imageUrl = ref('')
const loading = ref(true)
const error = ref(null)

// 从服务器获取随机图片
async function fetchRandomImage() {
  loading.value = true
  error.value = null
  
  try {
    // 这里有两种模式：
    // 1. 使用本地图片目录中的图片（如果有）
    // 2. 如果没有本地图片，则使用在线API
    
    // 为了演示，我们首先使用公共图片API
    // 在实际应用中，你可以创建一个API端点来返回服务器上的随机图片路径
    // 例如: const response = await fetch('/api/random-image')
    
    // 模拟加载，以便用户看到加载状态
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 方式1：使用本地图片（需要实现后端API）
    // const response = await fetch('/api/random-image')
    // const data = await response.json()
    // imageUrl.value = data.imageUrl
    
    // 方式2：使用公共图片API
    const response = await apiRequest('/image')
    if (!response.ok) {
      throw new Error('无法获取图片')
    }
    imageUrl.value = response.url
    
    // 方式3：使用预定义的本地图片列表（如果你将图片放在public/images目录中）
    // const localImages = [
    //   '/images/image1.jpg',
    //   '/images/image2.jpg',
    //   '/images/image3.jpg'
    //   // 添加更多图片路径
    // ]
    // const randomIndex = Math.floor(Math.random() * localImages.length)
    // imageUrl.value = localImages[randomIndex]
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
          <div class="i-carbon-image-search text-4xl text-blue-500 animate-pulse" />
        </div>
        <h2 class="text-lg font-medium mb-3">
          正在加载图片...
        </h2>
      </div>
      
      <div v-else-if="error" class="p-4 text-center">
        <div class="mb-4 flex justify-center">
          <div class="i-carbon-warning-alt text-4xl text-yellow-500" />
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
      </div>
      
      <div v-else class="p-4 text-center">
        <div class="mb-4">
          <img :src="imageUrl" alt="随机图片" class="rounded-lg max-w-full h-auto shadow-md" />
        </div>
        <p class="text-sm text-gray-600 mb-4 dark:text-gray-400">
          这是一张从服务器随机获取的图片
        </p>
        <button @click="getNewImage" class="text-blue-700 px-4 py-2 rounded-lg bg-blue-100 inline-flex gap-2 transition-colors items-center dark:text-blue-300 dark:bg-blue-900/50 hover:bg-blue-200 dark:hover:bg-blue-800/70">
          <span class="i-carbon-renew" />
          <span>换一张</span>
        </button>
      </div>
    </div>
  </div>
</template>
