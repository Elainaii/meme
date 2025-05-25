export default defineNuxtConfig({
  srcDir: 'app',
  app: {
    head: {
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '随机展示服务器中存储的精美图片' }
      ],
      link: [
        { rel: 'icon', href: '/favicon.ico' }
      ]
    },
    pageTransition: { name: 'page', mode: 'out-in' }
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
