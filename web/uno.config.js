import { defineConfig, presetUno, presetIcons, presetTypography } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetIcons({
      scale: 1.2,
      collections: {
        carbon: () => import('@iconify-json/carbon/icons.json').then(i => i.default)
      }
    }),
    presetTypography()
  ],
  theme: {
    colors: {
      yellow: '#FFD166'
    }
  },
  shortcuts: {
    'bg-yellow': 'bg-yellow',
    'size-7': 'w-7 h-7',
    'size-8': 'w-8 h-8'
  }
})
