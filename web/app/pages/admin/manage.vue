<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { checkAuth, logout: logoutStore, getToken } = useAdminStore()
const pendingImages = ref([])
const currentPendingImage = ref(null)
const totalPendingCount = ref(0)
const totalImagesCount = ref(0)

const allImages = ref([])
const currentPage = ref(1)
const pageSize = 5
const totalPages = ref(0)
const loading = ref(true)
const error = ref(null)

// 检查是否已登录
function validateAuth() {
  if (!checkAuth()) {
    router.push('/admin')
    return false
  }
  return true
}

// 获取待审核的图片
async function fetchPendingImages() {
  if (!validateAuth()) return
  
  loading.value = true
  error.value = null
  
  try {
    const response = await fetch('http://127.0.0.1:8000/admin/pending-images', {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    })
    
    if (!response.ok) {
      throw new Error('获取待审核图片失败')
    }
    
    const data = await response.json()
    pendingImages.value = data.images || []
    totalPendingCount.value = data.total || 0
    
    if (pendingImages.value.length > 0) {
      currentPendingImage.value = pendingImages.value[0]
    } else {
      currentPendingImage.value = null
    }
  } catch (e) {
    console.error('获取待审核图片时出错:', e)
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 获取所有已审核图片
async function fetchAllImages() {
  if (!validateAuth()) return
  
  loading.value = true
  error.value = null
  
  try {
    const response = await fetch(`http://127.0.0.1:8000/admin/all-images?page=${currentPage.value}&pageSize=${pageSize}`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    })
    
    if (!response.ok) {
      throw new Error('获取图片失败')
    }
    
    const data = await response.json()
    allImages.value = data.images || []
    totalImagesCount.value = data.total || 0
    totalPages.value = Math.ceil(totalImagesCount.value / pageSize)
  } catch (e) {
    console.error('获取图片时出错:', e)
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 审核图片（通过或拒绝）
async function reviewImage(imageId, approved) {
  if (!validateAuth()) return
  
  loading.value = true
  
  try {
    const response = await fetch('http://127.0.0.1:8000/admin/review-image', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getToken()}`
      },
      body: JSON.stringify({
        imageId,
        approved
      })
    })
    
    if (!response.ok) {
      throw new Error('审核图片失败')
    }
    
    // 更新待审核图片列表
    pendingImages.value = pendingImages.value.filter(img => img.id !== imageId)
    totalPendingCount.value = Math.max(0, totalPendingCount.value - 1)
    
    if (pendingImages.value.length > 0) {
      currentPendingImage.value = pendingImages.value[0]
    } else {
      currentPendingImage.value = null
    }
    
    // 如果是通过的图片，需要刷新全部图片列表
    if (approved) {
      await fetchAllImages()
    }
  } catch (e) {
    console.error('审核图片时出错:', e)
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 删除已审核图片
async function deleteImage(imageId) {
  if (!confirm('确定要删除这张图片吗？此操作不可恢复。')) {
    return
  }
  
  if (!validateAuth()) return
  
  loading.value = true
  
  try {
    const response = await fetch(`http://127.0.0.1:8000/admin/delete-image/${imageId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    })
    
    if (!response.ok) {
      throw new Error('删除图片失败')
    }
    
    // 更新图片列表
    allImages.value = allImages.value.filter(img => img.id !== imageId)
    totalImagesCount.value = Math.max(0, totalImagesCount.value - 1)
    totalPages.value = Math.ceil(totalImagesCount.value / pageSize)
    
    // 如果当前页已经没有图片，且不是第一页，则返回上一页
    if (allImages.value.length === 0 && currentPage.value > 1) {
      currentPage.value--
      await fetchAllImages()
    }
  } catch (e) {
    console.error('删除图片时出错:', e)
    error.value = e.message
  } finally {
    loading.value = false
  }
}

// 翻页
function changePage(page) {
  currentPage.value = page
  fetchAllImages()
}

// 退出登录
function logout() {
  logoutStore()
  router.push('/admin')
}

onMounted(() => {
  if (validateAuth()) {
    fetchPendingImages()
    fetchAllImages()
  }
})

// 定期刷新待审核图片
const refreshInterval = ref(null)

onMounted(() => {
  refreshInterval.value = setInterval(() => {
    if (validateAuth()) {
      fetchPendingImages()
    }
  }, 30000) // 每30秒刷新一次
})

onBeforeUnmount(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<template>
  <div class="px-4 py-8 sm:px-6 max-w-6xl mx-auto">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-2xl font-bold">
        <span>管理员</span>
        <span class="text-black ml-1 px-2 py-1 rounded bg-yellow inline-block">图片管理</span>
      </h1>
      <button @click="logout" class="text-red-600 px-3 py-1.5 rounded-lg bg-red-50 inline-flex gap-1 items-center hover:bg-red-100 dark:text-red-400 dark:bg-red-900/30 dark:hover:bg-red-900/50">
        <span class="i-carbon-logout" />
        <span>退出登录</span>
      </button>
    </div>
    
    <!-- 待审核图片部分 -->
    <div class="mb-10 bg-white rounded-xl shadow-md overflow-hidden p-6 dark:bg-gray-800">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">待审核图片</h2>
        <div class="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded-full dark:bg-blue-900/50 dark:text-blue-300">
          总计: {{ totalPendingCount }} 张
        </div>
      </div>
      
      <div v-if="loading && !currentPendingImage" class="p-4 text-center">
        <div class="i-carbon-image-search text-4xl text-blue-500 animate-pulse mb-2" />
        <p>加载中...</p>
      </div>
      
      <div v-else-if="error" class="bg-red-50 p-4 rounded-md text-red-700 text-sm mb-4 dark:bg-red-900/50 dark:text-red-300">
        <span class="i-carbon-warning-alt mr-1" />
        {{ error }}
        <button @click="fetchPendingImages" class="ml-2 underline">重试</button>
      </div>
      
      <div v-else-if="!currentPendingImage" class="p-4 text-center text-gray-500 border border-dashed border-gray-300 rounded-lg dark:border-gray-600">
        <div class="i-carbon-checkmark-filled text-4xl text-green-500 mb-2" />
        <p>没有待审核的图片</p>
      </div>
      
      <div v-else class="flex flex-col items-center">
        <div class="w-full max-w-lg mb-4">
          <img 
            :src="currentPendingImage.url" 
            :alt="`待审核图片 ${currentPendingImage.id}`" 
            class="rounded-lg max-w-full h-auto shadow-md"
          />
        </div>
        
        <div class="flex gap-4 mt-2">
          <button 
            @click="reviewImage(currentPendingImage.id, true)"
            class="bg-green-600 text-white py-2 px-6 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="loading"
          >
            <span class="i-carbon-checkmark mr-1" />
            通过
          </button>
          
          <button 
            @click="reviewImage(currentPendingImage.id, false)"
            class="bg-red-600 text-white py-2 px-6 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="loading"
          >
            <span class="i-carbon-close mr-1" />
            删除
          </button>
        </div>
      </div>
    </div>
    
    <!-- 所有图片部分 -->
    <div class="bg-white rounded-xl shadow-md overflow-hidden p-6 dark:bg-gray-800">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">已审核图片</h2>
        <div class="text-sm bg-green-100 text-green-800 px-3 py-1 rounded-full dark:bg-green-900/50 dark:text-green-300">
          总计: {{ totalImagesCount }} 张
        </div>
      </div>
      
      <div v-if="loading && allImages.length === 0" class="p-4 text-center">
        <div class="i-carbon-image-search text-4xl text-blue-500 animate-pulse mb-2" />
        <p>加载中...</p>
      </div>
      
      <div v-else-if="error && allImages.length === 0" class="bg-red-50 p-4 rounded-md text-red-700 text-sm mb-4 dark:bg-red-900/50 dark:text-red-300">
        <span class="i-carbon-warning-alt mr-1" />
        {{ error }}
        <button @click="fetchAllImages" class="ml-2 underline">重试</button>
      </div>
      
      <div v-else-if="allImages.length === 0" class="p-4 text-center text-gray-500 border border-dashed border-gray-300 rounded-lg dark:border-gray-600">
        <div class="i-carbon-folder text-4xl text-gray-400 mb-2" />
        <p>没有已审核的图片</p>
      </div>
      
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <div 
          v-for="image in allImages" 
          :key="image.id"
          class="relative group rounded-lg overflow-hidden"
        >
          <img 
            :src="image.url" 
            :alt="`图片 ${image.id}`" 
            class="w-full h-48 object-cover group-hover:opacity-30 transition-opacity duration-200"
          />
          <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <button 
              @click="deleteImage(image.id)"
              class="bg-red-600 text-white py-1.5 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              <span class="i-carbon-trash-can mr-1" />
              删除
            </button>
          </div>
        </div>
      </div>
      
      <!-- 分页控件 -->
      <div v-if="totalPages > 1" class="flex justify-center mt-6">
        <div class="inline-flex rounded-md shadow-sm">
          <button
            @click="changePage(Math.max(1, currentPage - 1))"
            :disabled="currentPage === 1"
            class="px-4 py-2 border border-gray-300 rounded-l-md bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-600"
          >
            <span class="i-carbon-chevron-left" />
          </button>
          
          <span class="px-4 py-2 border-t border-b border-gray-300 bg-white text-sm font-medium text-gray-700 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
            {{ currentPage }} / {{ totalPages }}
          </span>
          
          <button
            @click="changePage(Math.min(totalPages, currentPage + 1))"
            :disabled="currentPage === totalPages"
            class="px-4 py-2 border border-gray-300 rounded-r-md bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-600"
          >
            <span class="i-carbon-chevron-right" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
