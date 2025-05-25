<script setup>
import { appName } from '~/constants'

const route = useRoute()
const router = useRouter()
const isHomePage = computed(() => route.path === '/')

// 使用adminStore但不解构
const adminStore = useAdminStore()

// 创建computed属性来在模板中使用
const isAuthenticated = computed(() => adminStore.isAuthenticated.value)

// 检查登录状态
onMounted(() => {
  const authResult = adminStore.checkAuth()
  console.log('AppHeader mounted, 认证状态:', authResult, '响应式状态:', adminStore.isAuthenticated.value)
})

// 监听路由变化，重新检查认证状态
watch(() => route.path, () => {
  const authResult = adminStore.checkAuth()
  console.log('路由变化，重新检查认证状态:', authResult, '响应式状态:', adminStore.isAuthenticated.value)
})

// 监听认证状态变化
watch(() => adminStore.isAuthenticated.value, (newVal) => {
  console.log('认证状态变化:', newVal)
})

// 处理管理员登出
function handleLogout() {
  adminStore.logout()
  if (route.path.startsWith('/admin')) {
    router.push('/')
  }
}
</script>

<template>
  <header class="border-b border-gray-200 bg-white/80 left-0 right-0 top-0 fixed z-10 backdrop-blur-md dark:border-gray-800 dark:bg-gray-900/80">
    <div class="mx-auto px-4 flex h-14 items-center justify-between container sm:h-16">
      <!-- Logo and title -->
      <NuxtLink to="/" class="font-medium flex gap-1 items-center sm:gap-2">
        <span class="i-carbon-image text-lg text-blue-500 sm:text-xl" />
        <span class="text-sm sm:text-base">{{ appName }}</span>
      </NuxtLink>      <!-- Navigation -->
      <div class="flex gap-2 items-center sm:gap-4">
        <NuxtLink
          v-if="!isHomePage"
          to="/"
          class="text-xs px-2 py-1 rounded-md flex gap-1 transition-colors items-center sm:text-sm sm:px-3 sm:py-1.5 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <span class="i-carbon-home" />
          <span class="xs:inline hidden">首页</span>
        </NuxtLink>        <!-- Admin related buttons -->
        <template v-if="!isAuthenticated">
          <NuxtLink
            to="/login"
            class="text-xs px-2 py-1 rounded-md flex gap-1 transition-colors items-center sm:text-sm sm:px-3 sm:py-1.5 hover:bg-blue-50 dark:hover:bg-blue-900/30 text-blue-600 dark:text-blue-400"
          >
            <span class="i-carbon-password" />
            <span class="xs:inline hidden">登录</span>
          </NuxtLink>
        </template>
        
        <template v-else>
          <NuxtLink
            to="/admin/manage"
            class="text-xs px-2 py-1 rounded-md flex gap-1 transition-colors items-center sm:text-sm sm:px-3 sm:py-1.5 hover:bg-green-50 dark:hover:bg-green-900/30 text-green-600 dark:text-green-400"
          >
            <span class="i-carbon-user-admin" />
            <span class="xs:inline hidden">管理</span>
          </NuxtLink>
          
          <button
            @click="handleLogout"
            class="text-xs px-2 py-1 rounded-md flex gap-1 transition-colors items-center sm:text-sm sm:px-3 sm:py-1.5 hover:bg-red-50 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400"
          >
            <span class="i-carbon-logout" />
            <span class="xs:inline hidden">登出</span>
          </button>
        </template>

        <!-- Theme toggle button -->
        <ThemeToggle />
      </div>
    </div>
  </header>

  <!-- Spacer to prevent content from being hidden under the fixed header -->
  <div class="h-14 sm:h-16" />
</template>
