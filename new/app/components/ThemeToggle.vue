<script setup>
const colorMode = useColorMode()

function toggleTheme() {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
}
</script>

<template>
  <button
    class="p-1 rounded-md flex size-7 transition-colors items-center justify-center sm:p-1.5 hover:bg-gray-100 sm:size-8 dark:hover:bg-gray-800"
    aria-label="切换主题"
    @click="toggleTheme"
  >
    <span class="i-carbon-moon dark:i-carbon-sun" />
  </button>
</template>
