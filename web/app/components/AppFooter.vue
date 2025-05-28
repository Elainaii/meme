<template>
  <footer class="mt-8 py-6 border-t border-gray-200 dark:border-gray-700">
    <div class="mx-auto px-4 container">
      <div class="text-xs text-gray-500 flex flex-col items-center justify-between sm:text-sm dark:text-gray-400 md:flex-row">        <div class="mb-4 flex gap-2 items-center md:mb-0">
          <img src="/icon.svg" alt="Logo" class="w-4 h-4" />
          <span class="font-medium text-center md:text-left">© {{ new Date().getFullYear() }} Ciallo～(∠・ω< )⌒★</span>
        </div>

        <div class="flex flex-wrap gap-4 items-center justify-center">
          <a href="#" class="text-gray-600 flex gap-1.5 transition-colors items-center dark:text-gray-300 hover:text-blue-500">
            <span class="i-carbon-help" />
            <span>帮助</span>
          </a>
          <a href="https://github.com/Elainaii/meme" target="_blank" class="text-gray-600 flex gap-1.5 transition-colors items-center dark:text-gray-300 hover:text-blue-500">
            <span class="i-carbon-logo-github" />
            <span>GitHub</span>
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>
