<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { apiRequest, preloadImage } from '~/utils/api'

const imageUrl = ref('')
const nextImageUrl = ref('')
const loading = ref(true)
const switchingImage = ref(false)
const error = ref(null)
const showPreview = ref(false)
const imageKey = ref(0) // 用于强制更新图片
const imageDimensions = ref({ width: 0, height: 0 })
const imageContainer = ref(null)
const currentImg = ref(null)
const nextImg = ref(null)

// 从服务器获取随机图片
async function fetchRandomImage(isPreload = false) {
  if (!isPreload) {
    loading.value = true
    error.value = null
  }
  
  try {
    const response = await apiRequest('/image')
    if (!response.ok) {
      throw new Error('无法获取图片')
    }
    
    // 添加时间戳防止缓存
    const timestamp = Date.now()
    const url = new URL(response.url)
    url.searchParams.set('t', timestamp)
    const newImageUrl = url.toString()
    
    if (isPreload) {
      nextImageUrl.value = newImageUrl
      // 预加载图片
      const img = await preloadImage(newImageUrl)
      nextImg.value = img
    } else {
      imageUrl.value = newImageUrl
      // 预加载下一张图片
      fetchRandomImage(true)
    }

  } catch (e) {
    console.error('获取图片时出错:', e)
    if (!isPreload) {
      error.value = e.message
    }
  } finally {
    if (!isPreload) {
      loading.value = false
    }
  }
}

// 获取新的随机图片（带动画）
async function getNewImage() {
  if (switchingImage.value) return
  
  // 如果没有预加载的图片，先加载一张
  if (!nextImageUrl.value) {
    switchingImage.value = true
    await fetchRandomImage(true)
    if (!nextImageUrl.value) {
      switchingImage.value = false
      return
    }
  }
  
  switchingImage.value = true
  
  try {
    // 记录当前图片容器尺寸
    const currentImgElement = imageContainer.value?.querySelector('.current-image')
    if (currentImgElement) {
      imageDimensions.value = { 
        width: currentImgElement.offsetWidth, 
        height: currentImgElement.offsetHeight 
      }
    }
    
    // 先让当前图片渐出
    await new Promise(resolve => setTimeout(resolve, 150))
    
    // 计算新图片的显示尺寸（保持纵横比）
    if (nextImg.value) {
      const containerMaxWidth = imageContainer.value?.offsetWidth || 400
      const aspectRatio = nextImg.value.naturalHeight / nextImg.value.naturalWidth
      const newWidth = Math.min(nextImg.value.naturalWidth, containerMaxWidth)
      const newHeight = newWidth * aspectRatio
      
      // 设置容器过渡到新尺寸
      imageDimensions.value = { width: newWidth, height: newHeight }
      
      // 等待尺寸过渡完成
      await new Promise(resolve => setTimeout(resolve, 250))
    }
    
    // 切换到预加载的图片
    imageUrl.value = nextImageUrl.value
    imageKey.value++
    
    // 等待DOM更新
    await nextTick()
    
    // 等待图片渐入动画完成
    await new Promise(resolve => setTimeout(resolve, 200))
    
    // 清空预加载的图片并加载新的
    nextImageUrl.value = ''
    nextImg.value = null
    fetchRandomImage(true)
    
  } finally {
    // 重置状态
    switchingImage.value = false
    // 延迟重置固定尺寸，让容器恢复自适应
    setTimeout(() => {
      imageDimensions.value = { width: 0, height: 0 }
    }, 150)
  }
}

// 打开预览
function openPreview() {
  showPreview.value = true
}

// 关闭预览
function closePreview() {
  showPreview.value = false
}

// 图片加载完成处理
function onImageLoad() {
  // 图片加载完成后重置固定尺寸，让容器自适应
  if (!switchingImage.value) {
    imageDimensions.value = { width: 0, height: 0 }
  }
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

<template>  <div class="flex flex-col items-center">
    <div class="mb-6 p-4 rounded-xl bg-white max-w-md w-full shadow-lg sm:mb-8 sm:p-6 dark:bg-gray-800">      
      <div v-if="error" class="p-4 text-center">
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
        <div v-else-if="loading && !imageUrl" class="p-4 text-center">
        <div class="mb-4 flex justify-center">
          <div class="i-carbon-image-search text-4xl text-blue-500 animate-pulse" />
        </div>
        <h2 class="text-lg font-medium mb-3">
          正在加载图片...
        </h2>
      </div>
        <div v-else class="p-4 text-center">        
        <div 
          ref="imageContainer"
          class="mb-4 relative overflow-hidden transition-all duration-300 ease-in-out rounded-lg"
          :style="imageDimensions.width && imageDimensions.height ? {
            width: imageDimensions.width + 'px',
            height: imageDimensions.height + 'px'
          } : {}"
        >          <img 
            :key="imageKey"
            :src="imageUrl" 
            alt="随机图片" 
            class="current-image w-full h-auto rounded-lg cursor-pointer transition-all duration-300 ease-out shadow-lg hover:shadow-2xl"
            :class="{ 
              'opacity-0 scale-95': switchingImage,
              'hover:scale-105': !switchingImage
            }"
            @click="openPreview"
            @load="onImageLoad"
          />
        </div>
        <p class="text-sm text-gray-600 mb-4 dark:text-gray-400">
          这是一张从服务器随机获取的图片
        </p>        <button 
          @click="getNewImage" 
          :disabled="switchingImage || (!nextImageUrl && !loading)"
          class="text-blue-700 px-4 py-2 rounded-lg bg-blue-100 inline-flex gap-2 transition-colors items-center dark:text-blue-300 dark:bg-blue-900/50 hover:bg-blue-200 dark:hover:bg-blue-800/70 disabled:opacity-50"
        >
          <span class="i-carbon-renew" :class="{ 'animate-spin': switchingImage || !nextImageUrl }" />
          <span>{{ switchingImage ? '换图中...' : (!nextImageUrl ? '准备中...' : '换一张') }}</span>
        </button>
      </div>
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
        <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-3 z-20">          <button 
            @click.stop="getNewImage"
            :disabled="switchingImage || (!nextImageUrl && !loading)"
            class="text-white bg-black/50 rounded-full px-6 py-3 transition-colors hover:bg-black/70 flex items-center gap-2 backdrop-blur-sm disabled:opacity-50"
          >
            <span class="i-carbon-renew" :class="{ 'animate-spin': switchingImage || !nextImageUrl }" />
            <span>{{ switchingImage ? '换图中...' : (!nextImageUrl ? '准备中...' : '换一张') }}</span>
          </button>
        </div>        <!-- 图片容器 -->
        <div class="absolute inset-0 flex items-center justify-center pt-16 pb-24 px-16">
          <img 
            :key="imageKey"
            :src="imageUrl" 
            alt="预览图片" 
            class="max-w-full max-h-full object-contain rounded-lg shadow-2xl transition-all duration-300 ease-in-out"
            :class="{ 
              'opacity-0 scale-95': switchingImage,
              'animate-fade-in': !switchingImage
            }"
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

/* 自定义阴影效果 */
.current-image {
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06),
    0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.current-image:hover {
  box-shadow: 
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04),
    0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* 容器尺寸过渡 */
.image-container {
  transition: width 0.3s ease-in-out, height 0.3s ease-in-out;
}
</style>
