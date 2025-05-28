export default defineNuxtConfig({
  srcDir: 'app',
  dir: {
    public: '../public'
  },
  app: {
    head: {
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '随机展示服务器中存储的沙雕梗图～(∠・ω< )⌒★' }
      ],      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/icon.svg' },
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    },
    pageTransition: { name: 'page', mode: 'out-in' }
  },    runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL ,
      devApiBaseUrl: process.env.NUXT_PUBLIC_DEV_API_BASE_URL || 'http://localhost:8001'
    }
  },
  
  modules: [
    '@unocss/nuxt',
    '@vueuse/nuxt',
    '@nuxtjs/color-mode'
  ],
  
  colorMode: {
    classSuffix: ''
  },
  
  css: ['@unocss/reset/tailwind.css'],
  
  devtools: { enabled: true },
  
  nitro: {
    prerender: {
      failOnError: false,
      routes: ['/'],
      ignore: ['/admin/**', '/login']
    }
  },
  
  router: {
    options: {
      strict: false
    }
  }
})
