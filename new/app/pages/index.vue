<script setup>
import { appDescription } from '~/constants'
</script>

<template>
  <div class="px-4 flex flex-col h-full items-center justify-center sm:px-6">
    <div class="mb-6 text-center sm:mb-10">
      <div class="mb-3 flex justify-center sm:mb-4">
        <div class="i-carbon-image text-5xl text-blue-500 sm:text-6xl" />
      </div>
      <h1 class="text-2xl font-bold mb-2 sm:text-3xl">
        <span class="text-blue-500 mr-1">随机</span>
        <span>图片</span>
        <span class="text-black ml-1 px-2 py-1 rounded bg-yellow inline-block">展示</span>
      </h1>
      <p class="text-sm text-gray-500 mx-auto max-w-md sm:text-base dark:text-gray-400">
        {{ appDescription }}
      </p>
    </div>

    <!-- 随机图片展示区域 -->
    <RandomImage />
    
    <!-- 说明文本 -->
    <div class="mt-6 text-center">
      <p class="text-xs text-gray-500 px-4 py-2.5 rounded-full bg-gray-50/80 shadow-sm backdrop-blur-md sm:text-sm dark:text-gray-400 dark:bg-gray-800/60">
        <span class="i-carbon-information text-blue-500 mr-1" />
        <span>每次点击"换一张"按钮，将会从服务器随机获取一张新图片</span>
      </p>
    </div>
  </div>
</template>
