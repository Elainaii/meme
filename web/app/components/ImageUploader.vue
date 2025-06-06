<script setup>
import { ref } from 'vue'
import { apiRequest } from '~/utils/api'

const emit = defineEmits(['close'])
const { $config } = useNuxtApp()

// 从环境变量获取最大上传文件数量
const maxUploadFiles = parseInt($config.public.maxUploadFiles) || 9

const uploading = ref(false)
const uploadSuccess = ref(false)
const uploadError = ref(null)
const selectedFiles = ref([])
const isDragOver = ref(false)
const uploadResults = ref([])

// 文件选择处理
function handleFileSelect(event) {
  const files = Array.from(event.target.files)
  if (files.length > 0) {
    processFiles(files)
  }
}

// 处理文件
function processFiles(files) {
  // 限制最多上传文件数量（从环境变量获取）
  if (selectedFiles.value.length + files.length > maxUploadFiles) {
    uploadError.value = `最多只能选择${maxUploadFiles}张图片，当前已选择${selectedFiles.value.length}张`
    return
  }
  
  const validFiles = []
  const errors = []
  
  files.forEach(file => {
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      errors.push(`${file.name} 不是图片文件`)
      return
    }
    
    // 验证文件大小（限制为5MB）
    if (file.size > 5 * 1024 * 1024) {
      errors.push(`${file.name} 文件大小超过5MB`)
      return
    }
    
    // 检查是否已存在同名文件
    if (selectedFiles.value.some(f => f.name === file.name)) {
      errors.push(`${file.name} 已存在`)
      return
    }
    
    validFiles.push({
      file,
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      status: 'pending', // pending, uploading, success, error
      progress: 0,
      error: null
    })
  })
    if (errors.length > 0) {
    uploadError.value = errors
  } else {
    uploadError.value = null
  }
  
  selectedFiles.value.push(...validFiles)
  uploadSuccess.value = false
}

// 拖拽事件处理
function handleDragOver(event) {
  event.preventDefault()
  isDragOver.value = true
}

function handleDragLeave(event) {
  event.preventDefault()
  isDragOver.value = false
}

function handleDrop(event) {
  event.preventDefault()
  isDragOver.value = false
  
  const files = Array.from(event.dataTransfer.files)
  if (files.length > 0) {
    processFiles(files)
  }
}


// 上传图片
async function uploadImage() {
  if (selectedFiles.value.length === 0) {
    uploadError.value = '请先选择图片'
    return
  }
  
  uploading.value = true
  uploadError.value = null
  uploadSuccess.value = false
  uploadResults.value = []
    // 重置所有文件状态
  const filesToUpload = selectedFiles.value.filter(f => f.status === 'pending' || f.status === 'error')
  
  filesToUpload.forEach(fileItem => {
    fileItem.status = 'uploading'
    fileItem.progress = 0
    fileItem.error = null
  })
  
  // 并发上传待上传的文件
  const uploadPromises = filesToUpload.map(async (fileItem) => {
    try {
      const formData = new FormData()
      formData.append('file', fileItem.file)
        // 模拟进度更新
      const progressInterval = setInterval(() => {
        if (fileItem.progress < 90) {
          fileItem.progress = Math.min(90, fileItem.progress + Math.random() * 15)
        }
      }, 200)
      
      const response = await apiRequest('/upload/', {
        method: 'POST',
        body: formData
      })
      
      clearInterval(progressInterval)
      
      if (!response.ok) {
        throw new Error('上传失败，请重试')
      }
      
      const result = await response.json()
      fileItem.status = 'success'
      fileItem.progress = 100
      return { success: true, fileItem }
      
    } catch (error) {
      console.error('上传错误:', error)
      fileItem.status = 'error'
      fileItem.error = error.message
      return { success: false, fileItem, error }
    }
  })
  
  // 等待所有上传完成
  const results = await Promise.all(uploadPromises)
  
  uploading.value = false
  
  // 统计结果
  const successCount = results.filter(r => r.success).length
  const errorCount = results.filter(r => !r.success).length
    // 设置上传结果
  if (errorCount === 0) {
    uploadSuccess.value = true
    uploadResults.value = [`成功上传 ${successCount} 张图片！感谢你的贡献！`]
  } else {
    uploadResults.value = [
      `上传完成：成功 ${successCount} 张，失败 ${errorCount} 张`
    ]
  }
  
  // 清空文件输入框
  const fileInput = document.getElementById('file-input')
  if (fileInput) {
    fileInput.value = ''
  }
}

// 移除文件
function removeFile(fileId) {
  selectedFiles.value = selectedFiles.value.filter(f => f.id !== fileId)
  if (selectedFiles.value.length === 0) {
    uploadError.value = null
    uploadSuccess.value = false
  }
}

// 清理已完成文件
function clearCompletedFiles() {
  selectedFiles.value = selectedFiles.value.filter(f => f.status === 'pending' || f.status === 'uploading')
  if (selectedFiles.value.length === 0) {
    uploadError.value = null
    uploadSuccess.value = false
    uploadResults.value = []
  }
}

// 触发文件选择
function triggerFileSelect() {
  const fileInput = document.getElementById('file-input')
  if (fileInput) {
    fileInput.click()
  }
}

// 关闭上传框
function closeUploader() {
  emit('close')
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="closeUploader">
    <div class="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 p-6 dark:bg-gray-800">
      <!-- 关闭按钮 -->
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">上传图片</h3>
        <button @click="closeUploader" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
          <span class="i-carbon-close text-xl" />
        </button>
      </div>
        <!-- 隐藏的文件输入框 -->
      <input
        id="file-input"
        type="file"
        accept="image/*"
        multiple
        class="hidden"
        @change="handleFileSelect"
      />
      
      <!-- 拖拽上传区域 -->
      <div 
        @click="triggerFileSelect"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"        :class="[
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200',
          isDragOver ? 'border-pink-500 bg-pink-50 dark:bg-pink-900/20' : 'border-gray-300 dark:border-gray-600',
          'hover:border-pink-400 hover:bg-gray-50 dark:hover:bg-gray-700'
        ]"
      >
        <div class="flex flex-col items-center">
          <span class="i-carbon-cloud-upload text-4xl text-pink-500 mb-3" />          <p class="text-gray-600 dark:text-gray-300 mb-2">
            点击选择文件或拖拽文件到此处
          </p>          <p class="text-xs text-gray-500 dark:text-gray-400">
            支持 JPG、PNG、GIF 等格式，文件大小不超过 5MB，最多{{ maxUploadFiles }}张图片
          </p>
        </div>
      </div>      
      <!-- 已选择的文件列表 -->
      <div v-if="selectedFiles.length > 0" class="mt-4 space-y-3">        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
            已选择 {{ selectedFiles.length }} 张图片
          </span>
          <div class="flex items-center gap-2">
            <button 
              v-if="selectedFiles.some(f => f.status === 'success' || f.status === 'error')"
              @click="clearCompletedFiles"
              class="text-xs text-gray-500 hover:text-blue-500 transition-colors"
            >
              清理已完成
            </button>
            <button 
              @click="selectedFiles = []; uploadError = null; uploadSuccess = false; uploadResults = []"
              class="text-xs text-gray-500 hover:text-red-500 transition-colors"
            >
              清空全部
            </button>
          </div>
        </div>
          <div class="max-h-60 overflow-y-auto space-y-1">          <div 
            v-for="fileItem in selectedFiles" 
            :key="fileItem.id"
            class="relative p-2 rounded transition-all duration-200 overflow-hidden"
            :class="{
              'bg-pink-100 dark:bg-pink-900/30': fileItem.status !== 'error',
              'bg-red-100 dark:bg-red-900/30': fileItem.status === 'error'
            }"
          >            <!-- 进度条背景 -->
            <div 
              v-if="fileItem.status === 'uploading' || fileItem.status === 'success'"
              class="absolute top-0 left-0 h-full transition-all duration-300 rounded-l"
              :class="{
                'bg-pink-300 dark:bg-pink-600': fileItem.status === 'uploading',
                'bg-pink-400 dark:bg-pink-600': fileItem.status === 'success'
              }"
              :style="{ width: Math.min(100, fileItem.progress || 0) + '%' }"
            />
            
            <!-- 文件信息 -->
            <div class="relative flex items-center justify-between">
              <div class="flex items-center gap-2 flex-1 min-w-0">
                <span 
                  class="text-sm flex-shrink-0"
                  :class="{
                    'i-carbon-document text-pink-600 dark:text-pink-400': fileItem.status === 'pending',
                    'i-carbon-renew animate-spin text-pink-700 dark:text-pink-300': fileItem.status === 'uploading',
                    'i-carbon-checkmark-filled text-pink-800 dark:text-pink-200': fileItem.status === 'success',
                    'i-carbon-warning-alt text-red-600 dark:text-red-400': fileItem.status === 'error'
                  }"
                />                <span class="text-xs truncate font-medium"
                  :class="{
                    'text-pink-800 dark:text-pink-200': fileItem.status !== 'error',
                    'text-red-800 dark:text-red-200': fileItem.status === 'error'
                  }"
                >
                  {{ fileItem.name }}
                </span>
              </div>              <div class="flex items-center gap-2 flex-shrink-0">
                <span class="text-xs"
                  :class="{
                    'text-pink-700 dark:text-pink-300': fileItem.status !== 'error',
                    'text-red-700 dark:text-red-300': fileItem.status === 'error'
                  }"
                >
                  {{ (fileItem.size / (1024 * 1024)).toFixed(1) }}MB
                </span>
                <!-- 状态文本 -->
                <span class="text-xs font-medium">
                  <span 
                    v-if="fileItem.status === 'pending'"
                    class="text-pink-600 dark:text-pink-400"
                  >
                    等待
                  </span>                  <span 
                    v-else-if="fileItem.status === 'uploading'"
                    class="text-pink-800 dark:text-pink-200"
                  >
                    {{ Math.min(100, Math.round(fileItem.progress)) }}%
                  </span><span 
                    v-else-if="fileItem.status === 'success'"
                    class="text-pink-800 dark:text-pink-200"
                  >
                    完成
                  </span>
                  <span 
                    v-else-if="fileItem.status === 'error'"
                    class="text-red-800 dark:text-red-200"
                  >
                    失败
                  </span>
                </span>                <button 
                  v-if="!uploading && fileItem.status !== 'uploading'"
                  @click="removeFile(fileItem.id)"
                  class="transition-colors flex-shrink-0"
                  :class="{
                    'text-pink-600 hover:text-red-500': fileItem.status !== 'error',
                    'text-red-600 hover:text-red-700': fileItem.status === 'error'
                  }"
                >
                  <span class="i-carbon-close text-xs" />
                </button>
              </div>
            </div>
          </div>
        </div>        <!-- 批量上传按钮 -->
        <button 
          @click="uploadImage"
          :disabled="uploading || selectedFiles.filter(f => f.status === 'pending' || f.status === 'error').length === 0"
          class="w-full text-white px-4 py-3 rounded-lg bg-pink-500 inline-flex gap-2 transition-colors items-center justify-center hover:bg-pink-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="uploading" class="i-carbon-renew animate-spin" />
          <span v-else class="i-carbon-upload" />
          <span>
            {{ uploading ? '上传中...' : `上传 ${selectedFiles.filter(f => f.status === 'pending' || f.status === 'error').length} 张图片` }}
          </span>        </button>
      </div>
        <!-- 错误消息 -->
      <div v-if="uploadError" class="mt-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/30">
        <div class="flex items-start gap-2 text-red-700 dark:text-red-400">
          <span class="i-carbon-warning-alt flex-shrink-0 mt-0.5" />
          <div class="text-sm">
            <div v-if="Array.isArray(uploadError)">
              <div v-for="error in uploadError" :key="error" class="mb-1 last:mb-0">
                {{ error }}
              </div>
            </div>
            <div v-else>
              {{ uploadError }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>