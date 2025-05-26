<script setup>
import { ref } from 'vue'
import { apiRequest } from '~/utils/api'

const emit = defineEmits(['close'])

const uploading = ref(false)
const uploadSuccess = ref(false)
const uploadError = ref(null)
const selectedFile = ref(null)
const isDragOver = ref(false)

// 文件选择处理
function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

// 处理文件
function processFile(file) {
  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    uploadError.value = '请选择一个图片文件'
    return
  }
  
  // 验证文件大小（限制为5MB）
  if (file.size > 5 * 1024 * 1024) {
    uploadError.value = '图片文件大小不能超过5MB'
    return
  }
  
  selectedFile.value = file
  uploadError.value = null
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
  
  const files = event.dataTransfer.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

// 上传图片
async function uploadImage() {
  if (!selectedFile.value) {
    uploadError.value = '请先选择一张图片'
    return
  }
  
  uploading.value = true
  uploadError.value = null
  uploadSuccess.value = false
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const response = await apiRequest('/upload/', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('上传失败，请重试')
    }
    
    const result = await response.json()
    uploadSuccess.value = true
    selectedFile.value = null
    
    // 清空文件输入框
    const fileInput = document.getElementById('file-input')
    if (fileInput) {
      fileInput.value = ''
    }
    
    // 3秒后关闭上传框
    setTimeout(() => {
      emit('close')
    }, 2000)
    
  } catch (error) {
    console.error('上传错误:', error)
    uploadError.value = error.message
  } finally {
    uploading.value = false
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
        class="hidden"
        @change="handleFileSelect"
      />
      
      <!-- 拖拽上传区域 -->
      <div 
        @click="triggerFileSelect"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
        :class="[
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200',
          isDragOver ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 dark:border-gray-600',
          'hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-700'
        ]"
      >
        <div class="flex flex-col items-center">
          <span class="i-carbon-cloud-upload text-4xl text-blue-500 mb-3" />
          <p class="text-gray-600 dark:text-gray-300 mb-2">
            点击选择文件或拖拽文件到此处
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            支持 JPG、PNG、GIF 等格式，文件大小不超过 5MB
          </p>
        </div>
      </div>
      
      <!-- 已选择的文件信息 -->
      <div v-if="selectedFile" class="mt-4 p-3 rounded-lg bg-gray-50 dark:bg-gray-700">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2 flex-1 min-w-0">
            <span class="i-carbon-document text-blue-500" />
            <span class="text-sm text-gray-700 dark:text-gray-300 truncate">
              {{ selectedFile.name }}
            </span>
          </div>
          <span class="text-xs text-gray-500 ml-2">
            {{ (selectedFile.size / (1024 * 1024)).toFixed(2) }}MB
          </span>
        </div>
        
        <!-- 上传按钮 -->
        <button 
          @click="uploadImage"
          :disabled="uploading"
          class="w-full text-white px-4 py-2 rounded-lg bg-green-500 inline-flex gap-2 transition-colors items-center justify-center hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="uploading" class="i-carbon-renew animate-spin" />
          <span v-else class="i-carbon-upload" />
          <span>{{ uploading ? '上传中...' : '确认上传' }}</span>
        </button>
      </div>
      
      <!-- 成功消息 -->
      <div v-if="uploadSuccess" class="mt-4 p-3 rounded-lg bg-green-50 dark:bg-green-900/30">
        <div class="flex items-center gap-2 text-green-700 dark:text-green-400">
          <span class="i-carbon-checkmark-filled" />
          <span class="text-sm">图片上传成功！感谢你的贡献！</span>
        </div>
      </div>
      
      <!-- 错误消息 -->
      <div v-if="uploadError" class="mt-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/30">
        <div class="flex items-center gap-2 text-red-700 dark:text-red-400">
          <span class="i-carbon-warning-alt" />
          <span class="text-sm">{{ uploadError }}</span>
        </div>
      </div>
    </div>
  </div>
</template>