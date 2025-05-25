<script setup>
// 应用中间件保护此页面
definePageMeta({
  middleware: 'auth'
})

import { ref, onMounted, computed } from 'vue'
const adminStore = useAdminStore()
const router = useRouter()

const uncheckedImages = ref([])
const checkedImages = ref([])
const loading = ref(false)
const activeTab = ref('unchecked')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(12)
const totalPages = ref(1)
const totalUncheckedImages = ref(0)
const totalCheckedImages = ref(0)

// 悬停状态
const hoveredImage = ref(null)

// 检查认证状态
onMounted(async () => {
  if (!adminStore.checkAuth()) {
    router.push('/login')
    return
  }
  await loadAllCounts()
  await loadImages()
})

// 加载所有数量（用于标签页显示）
async function loadAllCounts() {
  try {
    const token = adminStore.getToken()
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
    
    // 获取未审核图片数量
    const uncheckedResponse = await fetch('http://127.0.0.1:8000/admin/pending-images', {
      headers
    })
    if (uncheckedResponse.ok) {
      const data = await uncheckedResponse.json()
      totalUncheckedImages.value = data.total || 0
    }
    
    // 获取已审核图片数量（只获取第一页来获取总数）
    const checkedResponse = await fetch('http://127.0.0.1:8000/admin/checked-images?page=1&page_size=1', {
      headers
    })
    if (checkedResponse.ok) {
      const data = await checkedResponse.json()
      totalCheckedImages.value = data.total || 0
    }
  } catch (error) {
    console.error('加载数量失败:', error)
  }
}

// 加载图片列表
async function loadImages() {
  loading.value = true
  try {
    const token = adminStore.getToken()
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
      if (activeTab.value === 'unchecked') {
      // 加载未审核图片
      const uncheckedResponse = await fetch('http://127.0.0.1:8000/admin/pending-images', {
        headers
      });
      
      if (uncheckedResponse.ok) {
        const data = await uncheckedResponse.json();
        uncheckedImages.value = data.images || [];
        totalUncheckedImages.value = data.total || 0;
      }    } else {
      // 加载已审核图片（分页）
      const checkedResponse = await fetch(`http://127.0.0.1:8000/admin/checked-images?page=${currentPage.value}&page_size=${pageSize.value}`, {
        headers
      });
      
      if (checkedResponse.ok) {
        const data = await checkedResponse.json()
        checkedImages.value = data.images || []
        totalCheckedImages.value = data.total || 0
        totalPages.value = data.total_pages || 1
      }
    }
  } catch (error) {
    console.error('加载图片失败:', error)
  } finally {
    loading.value = false
  }
}

// 切换标签页
async function switchTab(tab) {
  activeTab.value = tab
  currentPage.value = 1 // 重置页码
  await loadImages()
}

// 分页功能
async function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    await loadImages()
  }
}

// 计算分页显示范围
const pageNumbers = computed(() => {
  const range = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  
  for (let i = start; i <= end; i++) {
    range.push(i)
  }
  return range
})

// 审核图片
async function approveImage(imageId) {
  try {
    const token = adminStore.getToken()
    const response = await fetch(`http://127.0.0.1:8000/image/${imageId}/check`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ is_checked: true })
    })
    
    if (response.ok) {
      await loadAllCounts() // 更新所有数量
      await loadImages() // 重新加载列表
    }
  } catch (error) {
    console.error('审核图片失败:', error)
  }
}

// 删除图片
async function deleteImage(imageId) {
  if (!confirm('确定要删除这张图片吗？')) {
    return
  }
  
  try {
    const token = adminStore.getToken()
    const response = await fetch(`http://127.0.0.1:8000/admin/image/${imageId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      await loadAllCounts() // 更新所有数量
      await loadImages() // 重新加载列表
    }
  } catch (error) {
    console.error('删除图片失败:', error)
  }
}

// 登出
function handleLogout() {
  adminStore.logout()
  router.push('/')
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (!bytes) return ''
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

// 格式化日期
function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit'
  })
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- 顶部导航 -->
    <div class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900 dark:text-white">管理面板</h1>
          </div>
          <div class="flex items-center space-x-4">
            <NuxtLink 
              to="/"
              class="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
            >
              <span class="i-carbon-home mr-1" />
              首页
            </NuxtLink>
            <button 
              @click="handleLogout"
              class="bg-red-600 text-white px-4 py-2 rounded-md text-sm hover:bg-red-700"
            >
              <span class="i-carbon-logout mr-1" />
              登出
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <!-- 标签页 -->
      <div class="mb-6">
        <div class="border-b border-gray-200 dark:border-gray-700">
          <nav class="-mb-px flex space-x-8">            <button
              @click="switchTab('unchecked')"
              :class="[
                activeTab === 'unchecked'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
              ]"
            >
              <span class="i-carbon-time mr-1" />
              待审核 ({{ totalUncheckedImages }})
            </button>
            <button
              @click="switchTab('checked')"
              :class="[
                activeTab === 'checked'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
              ]"
            >
              <span class="i-carbon-checkmark mr-1" />
              已审核 ({{ totalCheckedImages }})
            </button>
          </nav>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <div class="i-carbon-circle-dash animate-spin text-4xl text-blue-500 mb-4" />
        <p class="text-gray-500 dark:text-gray-400">加载中...</p>
      </div>

      <!-- 图片网格 -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">        <!-- 待审核图片 -->
        <template v-if="activeTab === 'unchecked'">
          <div 
            v-for="image in uncheckedImages" 
            :key="image.id"
            class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden relative group transition-transform duration-200 hover:scale-105"
            @mouseenter="hoveredImage = image.id"
            @mouseleave="hoveredImage = null"
          >
            <div class="relative">
              <img 
                :src="`http://127.0.0.1:8000/image/unchecked/${image.id}`"
                :alt="image.file_name"
                class="w-full h-48 object-cover"
              />
              <!-- 悬停时显示的操作按钮 -->
              <div 
                v-show="hoveredImage === image.id"
                class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center space-x-3 transition-opacity duration-200"
              >
                <button 
                  @click="approveImage(image.id)"
                  class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg shadow-lg transform hover:scale-110 transition-all duration-200 flex items-center"
                >
                  <span class="i-carbon-checkmark mr-1" />
                  通过
                </button>
                <button 
                  @click="deleteImage(image.id)"
                  class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg shadow-lg transform hover:scale-110 transition-all duration-200 flex items-center"
                >
                  <span class="i-carbon-trash-can mr-1" />
                  删除
                </button>
              </div>
            </div>
            <div class="p-4">
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-2 truncate">{{ image.file_name }}</p>
              <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <span v-if="image.file_size">{{ formatFileSize(image.file_size) }}</span>
                <span v-if="image.created_at">{{ formatDate(image.created_at) }}</span>
              </div>
            </div>
          </div>
        </template>        <!-- 已审核图片 -->
        <template v-if="activeTab === 'checked'">
          <div 
            v-for="image in checkedImages" 
            :key="image.id"
            class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden relative group transition-transform duration-200 hover:scale-105"
            @mouseenter="hoveredImage = image.id"
            @mouseleave="hoveredImage = null"
          >
            <div class="relative">
              <img 
                :src="`http://127.0.0.1:8000/image/checked/${image.id}`"
                :alt="image.file_name"
                class="w-full h-48 object-cover"
              />
              <!-- 悬停时显示的删除按钮 -->
              <div 
                v-show="hoveredImage === image.id"
                class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center transition-opacity duration-200"
              >
                <button 
                  @click="deleteImage(image.id)"
                  class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg shadow-lg transform hover:scale-110 transition-all duration-200 flex items-center"
                >
                  <span class="i-carbon-trash-can mr-1" />
                  删除
                </button>
              </div>
            </div>
            <div class="p-4">
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-2 truncate">{{ image.file_name }}</p>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded">
                  <span class="i-carbon-checkmark mr-1" />
                  已审核
                </span>
                <div class="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                  <span class="flex items-center">
                    <span class="i-carbon-thumbs-up mr-1" />
                    {{ image.likes || 0 }}
                  </span>
                  <span class="flex items-center">
                    <span class="i-carbon-thumbs-down mr-1" />
                    {{ image.dislikes || 0 }}
                  </span>
                </div>
              </div>
              <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <span v-if="image.file_size">{{ formatFileSize(image.file_size) }}</span>
                <span v-if="image.created_at">{{ formatDate(image.created_at) }}</span>
              </div>
            </div>
          </div>
        </template>
      </div>      <!-- 空状态 -->
      <div v-if="!loading && ((activeTab === 'unchecked' && uncheckedImages.length === 0) || (activeTab === 'checked' && checkedImages.length === 0))" class="text-center py-12">
        <div class="i-carbon-image text-6xl text-gray-300 dark:text-gray-600 mb-4" />
        <p class="text-gray-500 dark:text-gray-400">
          {{ activeTab === 'unchecked' ? '暂无待审核图片' : '暂无已审核图片' }}
        </p>
      </div>

      <!-- 分页组件（仅在已审核标签页显示） -->
      <div v-if="activeTab === 'checked' && totalPages > 1" class="flex justify-center items-center mt-8 space-x-2">
        <!-- 上一页 -->
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage <= 1"
          class="px-3 py-2 rounded-md text-sm font-medium bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span class="i-carbon-chevron-left" />
        </button>

        <!-- 页码 -->
        <button
          v-for="page in pageNumbers"
          :key="page"
          @click="goToPage(page)"
          :class="[
            page === currentPage
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700',
            'px-3 py-2 rounded-md text-sm font-medium border'
          ]"
        >
          {{ page }}
        </button>

        <!-- 下一页 -->
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage >= totalPages"
          class="px-3 py-2 rounded-md text-sm font-medium bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span class="i-carbon-chevron-right" />
        </button>        <!-- 页码信息 -->
        <div class="ml-4 text-sm text-gray-500 dark:text-gray-400">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页 ({{ totalCheckedImages }} 张图片)
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 添加一些自定义样式 */
.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}
</style>
