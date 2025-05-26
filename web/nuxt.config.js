export default defineNuxtConfig({
  srcDir: 'app',
  app: {
    head: {
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '随机展示服务器中存储的精美图片' }
      ],      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/favicon-16x16.png' },
        { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32x32.png' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
        { rel: 'manifest', href: '/site.webmanifest' }
      ]
    },
    pageTransition: { name: 'page', mode: 'out-in' }
  },
    runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL ,
      devApiBaseUrl: process.env.NUXT_PUBLIC_DEV_API_BASE_URL || 'http://localhost:8000'
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
