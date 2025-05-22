<script setup>
import { ref, onMounted } from 'vue'

const debugging = ref(true)
const info = ref({
  routes: [],
  components: [],
  appState: null
})

onMounted(async () => {
  // 获取当前路由信息
  const router = useRouter()
  const routes = router.getRoutes().map(route => ({
    path: route.path,
    name: route.name,
    components: Object.keys(route.components || {})
  }))
  
  info.value.routes = routes
  
  // 模拟获取应用状态
  info.value.appState = {
    colorMode: useColorMode().value,
    appName: '随机图片展示',
    currentTime: new Date().toLocaleString()
  }
  
  debugging.value = false
})
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-6">应用调试页面</h1>
    
    <div v-if="debugging" class="text-center p-4">
      <div class="animate-spin i-carbon-circle-dash text-4xl text-blue-500 mx-auto"></div>
      <p class="mt-2 text-gray-600">收集应用信息中...</p>
    </div>
    
    <div v-else class="space-y-8">
      <div class="p-4 bg-white rounded-lg shadow dark:bg-gray-800">
        <h2 class="text-xl font-semibold mb-4">路由信息</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead>
              <tr>
                <th class="px-4 py-2 text-left">路径</th>
                <th class="px-4 py-2 text-left">名称</th>
                <th class="px-4 py-2 text-left">组件</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="route in info.routes" :key="route.path">
                <td class="px-4 py-2">{{ route.path }}</td>
                <td class="px-4 py-2">{{ route.name }}</td>
                <td class="px-4 py-2">{{ route.components.join(', ') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div class="p-4 bg-white rounded-lg shadow dark:bg-gray-800">
        <h2 class="text-xl font-semibold mb-4">应用状态</h2>
        <pre class="p-3 bg-gray-100 rounded dark:bg-gray-900 overflow-x-auto">{{ JSON.stringify(info.appState, null, 2) }}</pre>
      </div>
      
      <div class="flex justify-center">
        <NuxtLink to="/" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
          返回首页
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
