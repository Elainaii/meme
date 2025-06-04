<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { apiRequest, preloadImage } from '~/utils/api'

const imageUrl = ref('')
const nextImageUrl = ref('')
const nextImageInfo = ref(null) // 存储下一张图片的信息（包含尺寸）
const currentImageInfo = ref(null) // 存储当前图片的信息
const loading = ref(true)
const switchingImage = ref(false)
const error = ref(null)
const showPreview = ref(false)
const imageKey = ref(0) // 用于强制更新图片
const imageDimensions = ref({ width: 0, height: 0 })
const imageContainer = ref(null)
const currentImg = ref(null)
const nextImg = ref(null)

// 计算图片在容器中的实际显示尺寸
function calculateImageDisplaySize(imageWidth, imageHeight, container) {
  if (!container || !imageWidth || !imageHeight) {
    return { width: 0, height: 0 }
  }
  
  // 获取容器的真实可用宽度
  let availableWidth
  
  // 更稳定的方式获取容器宽度：
  // 1. 先保存当前状态
  const originalStyle = container.style.cssText
  const originalTransition = container.style.transition
  
  // 2. 临时禁用过渡效果并重置尺寸样式
  container.style.transition = 'none'
  container.style.width = ''
  container.style.height = ''
  
  // 3. 强制同步重新计算布局
  container.offsetHeight // 触发重排
  
  // 4. 获取父容器的可用宽度（更准确的计算基准）
  const parentElement = container.parentElement
  if (parentElement) {
    const parentStyle = getComputedStyle(parentElement)
    const parentPadding = parseFloat(parentStyle.paddingLeft) + parseFloat(parentStyle.paddingRight)
    const parentBorder = parseFloat(parentStyle.borderLeftWidth) + parseFloat(parentStyle.borderRightWidth)
    availableWidth = parentElement.clientWidth - parentPadding - parentBorder
    
    // 减去容器本身的边距和边框
    const containerStyle = getComputedStyle(container)
    const containerMargin = parseFloat(containerStyle.marginLeft) + parseFloat(containerStyle.marginRight)
    const containerBorder = parseFloat(containerStyle.borderLeftWidth) + parseFloat(containerStyle.borderRightWidth)
    const containerPadding = parseFloat(containerStyle.paddingLeft) + parseFloat(containerStyle.paddingRight)
    
    availableWidth = availableWidth - containerMargin - containerBorder - containerPadding
  } else {
    // 回退到直接使用容器宽度
    const containerStyle = getComputedStyle(container)
    const containerPadding = parseFloat(containerStyle.paddingLeft) + parseFloat(containerStyle.paddingRight)
    availableWidth = container.clientWidth - containerPadding
  }
  
  // 5. 恢复原始样式和过渡效果
  container.style.cssText = originalStyle
  if (originalTransition) {
    container.style.transition = originalTransition
  }
  
  // 计算宽高比
  const aspectRatio = imageHeight / imageWidth
  
  let displayWidth, displayHeight
  
  // 正确模拟 w-full h-auto 的行为
  if (imageWidth <= availableWidth) {
    // 如果图片比容器小，保持原始尺寸（不放大）
    displayWidth = imageWidth
    displayHeight = imageHeight
  } else {
    // 如果图片比容器大，缩放到容器宽度
    displayWidth = availableWidth
    displayHeight = displayWidth * aspectRatio
  }
  
  // 验证计算结果
  if (displayWidth <= 0 || displayHeight <= 0) {
    return { width: 0, height: 0 }
  }
  
  return { width: Math.round(displayWidth), height: Math.round(displayHeight) }
}

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
      // 解析JSON响应
    const data = await response.json()
    
    if (!data.image_url) {
      throw new Error('图片URL缺失')
    }
    
    // 使用返回的图片URL
    let newImageUrl = data.image_url
    
    // 时间戳处理，避免缓存问题
    if (newImageUrl.includes('?')) {
      newImageUrl += `&t=${Date.now()}`
    } else {
      newImageUrl += `?t=${Date.now()}`    }
    
    if (isPreload) {      nextImageUrl.value = newImageUrl
      nextImageInfo.value = data // 存储完整的图片信息
      
      // 预加载图片
      const img = await preloadImage(newImageUrl)
        // 确保图片真的加载完成并有有效尺寸
      if (img.naturalWidth > 0 && img.naturalHeight > 0) {
        nextImg.value = img
      } else {
        nextImg.value = null
      }
    } else {      // 非预加载模式：设置当前图片并存储其信息
      imageUrl.value = newImageUrl
      currentImageInfo.value = data // 存储当前图片信息
      // 预加载下一张图片
      fetchRandomImage(true)
    }
  } catch (e) {
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
  // 检查是否有图片信息可用于尺寸计算
  const hasImageInfo = nextImageInfo.value && nextImageInfo.value.width > 0 && nextImageInfo.value.height > 0
  
  if (!hasImageInfo) {
    
    switchingImage.value = true
    
    // 简化切换：直接切换图片，不做尺寸动画
    imageUrl.value = nextImageUrl.value
    imageKey.value++
    
    // 立即开始预加载下一张
    nextImageUrl.value = ''
    nextImageInfo.value = null
    nextImg.value = null
    fetchRandomImage(true)
    
    // 短暂延迟后重置状态
    setTimeout(() => {
      switchingImage.value = false
    }, 100)
    
    return
  }

  switchingImage.value = true

  try {
    // 1. 记录当前图片容器尺寸
    const currentImgElement = imageContainer.value?.querySelector('.current-image')
    if (currentImgElement) {
      const currentSize = {
        width: currentImgElement.offsetWidth,
        height: currentImgElement.offsetHeight      }
      imageDimensions.value = currentSize
    }

    // 2. 计算新图片的显示尺寸（在任何动画开始前）
    let targetSize = null
    if (nextImageInfo.value && nextImageInfo.value.width > 0 && nextImageInfo.value.height > 0) {
      const container = imageContainer.value
      if (container) {        targetSize = calculateImageDisplaySize(
          nextImageInfo.value.width,
          nextImageInfo.value.height,
          container
        )
      }
    }

    // 3. 开始渐出动画
    await new Promise(resolve => setTimeout(resolve, 150))    // 4. 如果有有效的目标尺寸，执行尺寸过渡动画
    if (targetSize && targetSize.width > 0 && targetSize.height > 0) {
      // 设置容器过渡到新尺寸
      imageDimensions.value = targetSize

      // 等待尺寸过渡完成（更长的延迟确保动画完成）
      await new Promise(resolve => setTimeout(resolve, 300))
    }

    // 5. 切换到预加载的图片
    imageUrl.value = nextImageUrl.value
    imageKey.value++
    
    // 更新当前图片信息
    currentImageInfo.value = nextImageInfo.value
    
    // 6. 立即清空预加载的图片并开始加载下一张（并行进行）
    nextImageUrl.value = ''
    nextImageInfo.value = null
    nextImg.value = null
    fetchRandomImage(true)

    // 7. 等待DOM更新和图片渐入动画完成
    await nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

  } finally {
    // 重置状态
    switchingImage.value = false
    // 延迟重置固定尺寸，让容器恢复自适应    // 增加延迟时间，确保图片完全加载并渲染完成
    setTimeout(() => {
      imageDimensions.value = {width: 0, height: 0}
    }, 400) // 增加到400ms确保所有动画完成
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
  // 基本的加载完成处理，移除详细的调试信息以提升性能
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
      <div v-if="error" class="p-4 text-center">
        <div class="mb-4 flex justify-center">
          <div class="i-carbon-warning-alt text-4xl text-yellow-500"/>
        </div>
        <h2 class="text-lg font-medium mb-3">
          加载图片失败
        </h2>
        <p class="text-sm text-gray-600 mb-4 dark:text-gray-400">
          {{ error }}
        </p>        <button @click="getNewImage"
                class="text-pink-700 px-4 py-2 rounded-lg bg-pink-100 inline-flex gap-2 transition-colors items-center dark:text-pink-300 dark:bg-pink-900/50 hover:bg-pink-200 dark:hover:bg-pink-800/70">
          <span class="i-carbon-restart"/>
          <span>重试</span>
        </button>
      </div>
      <div v-else-if="loading && !imageUrl" class="p-4 text-center">        <div class="mb-4 flex justify-center">
          <div class="i-carbon-image-search text-4xl text-pink-500 animate-pulse"/>
        </div>
        <h2 class="text-lg font-medium mb-3">
          正在加载图片...
        </h2>
      </div>
      <div v-else class="p-4 text-center">
        <div
            ref="imageContainer"
            class="mb-4 relative transition-all duration-300 ease-in-out rounded-lg shadow-lg hover:shadow-xl"
            :style="imageDimensions.width && imageDimensions.height ? {
            width: imageDimensions.width + 'px',
            height: imageDimensions.height + 'px'
          } : {}"
        ><img
            :key="imageKey"
            :src="imageUrl"
            alt="随机图片"
            class="current-image w-full h-auto rounded-lg cursor-pointer transition-all duration-300 ease-out" :class="{
              'opacity-0 scale-95': switchingImage,
              'hover:scale-105 hover:z-10 relative': !switchingImage
            }"
            @click="openPreview"
            @load="onImageLoad"
        />
        </div>        <button
            @click="getNewImage"
            :disabled="switchingImage || (!nextImageUrl && !loading)"
            class="text-pink-700 px-4 py-2 rounded-lg bg-pink-100 inline-flex gap-2 transition-colors items-center dark:text-pink-300 dark:bg-pink-900/50 hover:bg-pink-200 dark:hover:bg-pink-800/70 disabled:opacity-50"
        >
          <span class="i-carbon-renew" :class="{ 'animate-spin': switchingImage || !nextImageUrl }"/>
          <span>{{ switchingImage ? '换图中' : (!nextImageUrl ? '准备中' : '换一张') }}</span>
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
          <span class="i-carbon-close text-xl"/>
        </button>
        <!-- 操作按钮 -->
        <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-3 z-20">
          <button
              @click.stop="getNewImage"
              :disabled="switchingImage || (!nextImageUrl && !loading)"
              class="text-white bg-black/50 rounded-full px-6 py-3 transition-colors hover:bg-black/70 flex items-center gap-2 backdrop-blur-sm disabled:opacity-50"
          >
            <span class="i-carbon-renew" :class="{ 'animate-spin': switchingImage || !nextImageUrl }"/>
            <span>{{ switchingImage ? '换图中' : (!nextImageUrl ? '准备中' : '换一张') }}</span>
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
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
  0 2px 4px -1px rgba(0, 0, 0, 0.06),
  0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.current-image:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
  0 10px 10px -5px rgba(0, 0, 0, 0.04),
  0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

/* 容器阴影效果 */
[ref="imageContainer"] {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
  0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

[ref="imageContainer"]:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
  0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* 容器尺寸过渡 */
.image-container {
  transition: width 0.3s ease-in-out, height 0.3s ease-in-out;
}
</style>
