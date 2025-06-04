<script setup>
import { ref, onUnmounted } from 'vue'

const showHelpTooltip = ref(false)
let tooltipTimer = null

// 点击帮助时显示气泡
function handleHelpClick(event) {
  event.preventDefault()
  showHelpTooltip.value = true
  
  // 清除之前的定时器
  if (tooltipTimer) {
    clearTimeout(tooltipTimer)
  }
  
  // 2秒后自动隐藏气泡
  tooltipTimer = setTimeout(() => {
    showHelpTooltip.value = false
  }, 2000)
}

// 组件卸载时清理定时器
onUnmounted(() => {
  if (tooltipTimer) {
    clearTimeout(tooltipTimer)
  }
})
</script>

<template>
  <footer class="mt-8 py-6 border-t border-gray-200 dark:border-gray-700">
    <div class="mx-auto px-4 container">
      <div class="text-xs text-gray-500 flex flex-col items-center justify-between sm:text-sm dark:text-gray-400 md:flex-row">        <div class="mb-4 flex gap-2 items-center md:mb-0">
          <img src="/icon.svg" alt="Logo" class="w-4 h-4" />
          <span class="font-medium text-center md:text-left">© {{ new Date().getFullYear() }} Ciallo～(∠・ω< )⌒★</span>
        </div>        <div class="flex flex-wrap gap-4 items-center justify-center">
          <div class="relative">
            <a 
              href="#" 
              @click="handleHelpClick"
              class="text-gray-600 flex gap-1.5 transition-colors items-center dark:text-gray-300 hover:text-pink-500"
            >
              <span class="i-carbon-help" />
              <span>帮助</span>
            </a>
              <!-- 气泡提示 -->
            <div 
              v-if="showHelpTooltip"
              class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-3 px-4 py-3 bg-white text-gray-800 text-sm rounded-lg shadow-xl border border-gray-200 whitespace-nowrap dark:bg-gray-900 dark:text-white dark:border-gray-700 animate-bounce-in"
            >
              杂鱼~杂鱼~就两个按钮，点一下就知道了
              <!-- 小三角形 -->
              <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-white dark:border-t-gray-900"></div>
            </div>
          </div>
          
          <a href="https://github.com/Elainaii/meme" target="_blank" class="text-gray-600 flex gap-1.5 transition-colors items-center dark:text-gray-300 hover:text-pink-500">
            <span class="i-carbon-logo-github" />
            <span>GitHub</span>
          </a>
        </div>
      </div>
    </div>  </footer>
</template>

<style scoped>
@keyframes bounce-in {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(10px) scale(0.8);
  }
  50% {
    opacity: 1;
    transform: translateX(-50%) translateY(-2px) scale(1.05);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
}

.animate-bounce-in {
  animation: bounce-in 0.3s ease-out;
}
</style>
