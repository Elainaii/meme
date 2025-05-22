<script setup>
import { appName } from '~/constants'

const route = useRoute()
const isHomePage = computed(() => route.path === '/')
</script>

<template>
  <header class="border-b border-gray-200 bg-white/80 left-0 right-0 top-0 fixed z-10 backdrop-blur-md dark:border-gray-800 dark:bg-gray-900/80">
    <div class="mx-auto px-4 flex h-14 items-center justify-between container sm:h-16">
      <!-- Logo and title -->
      <NuxtLink to="/" class="font-medium flex gap-1 items-center sm:gap-2">
        <span class="i-carbon-image text-lg text-blue-500 sm:text-xl" />
        <span class="text-sm sm:text-base">{{ appName }}</span>
      </NuxtLink>

      <!-- Navigation -->
      <div class="flex gap-2 items-center sm:gap-4">
        <NuxtLink
          v-if="!isHomePage"
          to="/"
          class="text-xs px-2 py-1 rounded-md flex gap-1 transition-colors items-center sm:text-sm sm:px-3 sm:py-1.5 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <span class="i-carbon-home" />
          <span class="xs:inline hidden">首页</span>
        </NuxtLink>

        <!-- Theme toggle button -->
        <ThemeToggle />
      </div>
    </div>
  </header>

  <!-- Spacer to prevent content from being hidden under the fixed header -->
  <div class="h-14 sm:h-16" />
</template>
