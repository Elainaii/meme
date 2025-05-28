<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { apiRequest } from '~/utils/api'

const imageUrl = ref('')
const loading = ref(true)
const error = ref(null)
const showPreview = ref(false)
const imageKey = ref(0) // 用于强制更新图片

// 从服务器获取随机图片
async function fetchRandomImage() {
  loading.value = true
  error.value = null
  
  try {
    await new Promise(resolve => setTimeout(resolve, 500))

    const response = await apiRequest('/image')
    if (!response.ok) {
      throw new Error('无法获取图片')
    }
    
    // 添加时间戳防止缓存
    const timestamp = Date.now()
    const url = new URL(response.url)
    url.searchParams.set('t', timestamp)
    imageUrl.value = url.toString()
    
    // 更新图片key强制重新渲染
    imageKey.value++

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

// 打开预览
function openPreview() {
  showPreview.value = true
}

// 关闭预览
function closePreview() {
  showPreview.value = false
}

// 键盘事件处理
function handleKeydown(event) {
  if (event.key === 'Escape') {
    closePreview()
  }
}

// 组件挂载时获取第一张图片
onMounted(() => {
  fetchRandomImage()
  // 监听键盘事件
  document.addEventListener('keydown', handleKeydown)
})

// 组件卸载时清理事件监听
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
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
      </div>      <div v-else class="p-4 text-center">
        <div class="mb-4">
          <img 
            :key="imageKey"
            :src="imageUrl" 
            alt="随机图片" 
            class="rounded-lg max-w-full h-auto shadow-md cursor-pointer transform transition-transform duration-300 hover:scale-105" 
            @click="openPreview"
          />
        </div>
        <p class="text-sm text-gray-600 mb-4 dark:text-gray-400">
          这是一张从服务器随机获取的图片
        </p>
        <button @click="getNewImage" class="text-blue-700 px-4 py-2 rounded-lg bg-blue-100 inline-flex gap-2 transition-colors items-center dark:text-blue-300 dark:bg-blue-900/50 hover:bg-blue-200 dark:hover:bg-blue-800/70">
          <span class="i-carbon-renew" />
          <span>换一张</span>
        </button>      </div>
    </div>
      <!-- 全屏预览模态框 -->
    <Teleport to="body">
      <div 
        v-if="showPreview" 
        class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm"
        @click="closePreview"
      >
        <!-- 关闭按钮 -->
        <button 
          @click="closePreview"
          class="absolute top-4 right-4 text-white bg-black/50 rounded-full p-3 transition-colors hover:bg-black/70 z-20"
        >
          <span class="i-carbon-close text-xl" />
        </button>
        
        <!-- 操作按钮 -->
        <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-3 z-20">
          <button 
            @click.stop="getNewImage"
            class="text-white bg-black/50 rounded-full px-6 py-3 transition-colors hover:bg-black/70 flex items-center gap-2 backdrop-blur-sm"
          >
            <span class="i-carbon-renew" />
            <span>换一张</span>
          </button>
        </div>        <!-- 图片容器 -->
        <div class="absolute inset-0 flex items-center justify-center pt-16 pb-24 px-16">
          <img 
            :key="imageKey"
            :src="imageUrl" 
            alt="预览图片" 
            class="max-w-full max-h-full object-contain rounded-lg shadow-2xl animate-fade-in"
            @click.stop
          />
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>
