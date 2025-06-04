<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiRequest } from '~/utils/api'

const router = useRouter()
const adminStore = useAdminStore()
const password = ref('')
const loading = ref(false)
const error = ref(null)

// 检查是否已经登录
onMounted(() => {
  if (adminStore.checkAuth()) {
    // 如果已经登录，重定向到首页或管理页面
    router.push('/')
  }
})

async function handleLogin() {
  if (!password.value) {
    error.value = '请输入管理员密码'
    return
  }
  
  loading.value = true
  error.value = null
    try {
    // 发送密码到后端验证
    const response = await apiRequest('/admin/verify', {
      method: 'POST',
      body: JSON.stringify({ password: password.value }),
    })
      if (!response.ok) {
      throw new Error('验证失败')
    }
    
    const data = await response.json()
    
    if (data.success) {
      // 验证成功，保存认证令牌
      if (data.token) {
        adminStore.setAuth(data.token)
        console.log('登录成功，token已保存:', data.token)
      } else {
        // 如果没有token，使用默认标识
        adminStore.setAuth('authenticated')
        console.log('登录成功，使用默认认证标识')
      }
      
      // 确保状态已更新
      console.log('当前认证状态:', adminStore.checkAuth())
      
      // 登录成功后重定向到首页
      router.push('/')
    } else {
      error.value = data.message || '密码不正确'
    }
  } catch (e) {
    console.error('登录时出错:', e)
    error.value = e.message || '登录过程中发生错误'
  } finally {
    loading.value = false
  }
}

// 返回首页
function goHome() {
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen px-4 pt-6 flex flex-col items-center justify-center sm:px-6 bg-gradient-to-br from-pink-50 to-rose-100 dark:from-gray-900 dark:to-gray-800">
    <div class="mb-8 text-center sm:mb-10">
      <div class="mb-4 flex justify-center sm:mb-6">
        <div class="i-carbon-password text-6xl text-pink-500 sm:text-7xl" />
      </div>
      <h1 class="text-3xl font-bold mb-3 sm:text-4xl">
        <span>管理员</span>
        <span class="text-white ml-2 px-3 py-1 rounded-lg bg-pink-500 inline-block shadow-md">登录</span>
      </h1>
      <p class="text-base text-gray-600 mx-auto max-w-md sm:text-lg dark:text-gray-300">
        请输入管理员密码以访问系统管理功能
      </p>
    </div>

    <div class="w-full max-w-md bg-white rounded-2xl shadow-lg overflow-hidden p-8 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label for="password" class="block text-sm font-semibold text-gray-700 mb-2 dark:text-gray-300">管理员密码</label>
          <div class="relative">
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="请输入管理员密码"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400"
              :disabled="loading"
              autocomplete="current-password"
            />
            <div class="absolute inset-y-0 right-0 pr-3 flex items-center">
              <div class="i-carbon-locked text-gray-400 text-lg" />
            </div>
          </div>
        </div>
        
        <div v-if="error" class="bg-red-50 border border-red-200 p-4 rounded-lg text-red-700 text-sm dark:bg-red-900/30 dark:border-red-800 dark:text-red-300">
          <div class="flex items-center">
            <div class="i-carbon-warning-alt mr-2 text-red-500" />
            <span>{{ error }}</span>
          </div>
        </div>
        
        <div class="space-y-3">
          <button 
            type="submit"
            :disabled="loading || !password"
            class="w-full bg-pink-600 text-white py-3 px-4 rounded-lg hover:bg-pink-700 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-colors shadow-md"
          >
            <div class="flex items-center justify-center">
              <div v-if="loading" class="i-carbon-circle-dash animate-spin mr-2" />
              <span>{{ loading ? '登录中...' : '登录' }}</span>
            </div>
          </button>
          
          <button 
            type="button"
            @click="goHome"
            :disabled="loading"
            class="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
          >
            <div class="flex items-center justify-center">
              <div class="i-carbon-home mr-2" />
              <span>返回首页</span>
            </div>
          </button>
        </div>
      </form>
    </div>
      <div class="mt-8 text-center">
      <div class="text-sm text-gray-500 px-6 py-3 rounded-full bg-white/60 shadow-sm backdrop-blur-md sm:text-base dark:text-gray-400 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-center">
          <div class="i-carbon-information text-pink-500 mr-2" />
          <span>仅限管理员访问</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 添加一些自定义样式增强视觉效果 */
.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}

@media (prefers-color-scheme: dark) {
  .bg-gradient-to-br {
    background-image: linear-gradient(to bottom right, 
      rgb(17 24 39), 
      rgb(31 41 55)
    );
  }
}
</style>
