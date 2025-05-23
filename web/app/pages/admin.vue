<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const { setAuth } = useAdminStore()
const password = ref('')
const loading = ref(false)
const error = ref(null)

async function handleLogin() {
  if (!password.value) {
    error.value = '请输入管理员密码'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    // 发送密码到后端验证
    const response = await fetch('http://127.0.0.1:8000/admin/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ password: password.value }),
    })
    
    if (!response.ok) {
      throw new Error('验证失败')
    }
    
    const data = await response.json()
    
    if (data.success) {
      // 验证成功，保存认证令牌(如果有)
      if (data.token) {
        setAuth(data.token)
      }
      
      // 跳转到管理页面
      router.push('/admin/manage')
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
</script>

<template>
  <div class="px-4 pt-10 flex flex-col h-full items-center justify-center sm:px-6">
    <div class="mb-6 text-center sm:mb-10">
      <div class="mb-3 flex justify-center sm:mb-4">
        <div class="i-carbon-password text-5xl text-blue-500 sm:text-6xl" />
      </div>
      <h1 class="text-2xl font-bold mb-2 sm:text-3xl">
        <span>管理员</span>
        <span class="text-black ml-1 px-2 py-1 rounded bg-yellow inline-block">登录</span>
      </h1>
      <p class="text-sm text-gray-500 mx-auto max-w-md sm:text-base dark:text-gray-400">
        请输入管理员密码以访问图片管理功能
      </p>
    </div>

    <div class="w-full max-w-md bg-white rounded-xl shadow-md overflow-hidden p-6 dark:bg-gray-800">
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">管理员密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            :disabled="loading"
          />
        </div>
        
        <div v-if="error" class="bg-red-50 p-3 rounded-md text-red-700 text-sm dark:bg-red-900/50 dark:text-red-300">
          <span class="i-carbon-warning-alt mr-1" />
          {{ error }}
        </div>
        
        <div>
          <button 
            type="submit"
            :disabled="loading"
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading" class="i-carbon-circle-dash animate-spin mr-2" />
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </div>
      </form>
    </div>
    
    <div class="mt-6 text-center">
      <p class="text-xs text-gray-500 px-4 py-2.5 rounded-full bg-gray-50/80 shadow-sm backdrop-blur-md sm:text-sm dark:text-gray-400 dark:bg-gray-800/60">
        <span class="i-carbon-information text-blue-500 mr-1" />
        <span>只有管理员可以访问此页面</span>
      </p>
    </div>
  </div>
</template>
