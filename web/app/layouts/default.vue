<template>
  <div class="text-gray-900 font-sans bg-gray-50 flex flex-col min-h-screen dark:text-gray-100 dark:bg-gray-900">
    <AppHeader />

    <main class="flex-1 w-full">
      <slot />
    </main>

    <AppFooter />
  </div>
</template>
