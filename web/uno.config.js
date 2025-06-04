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
  ],  theme: {
    colors: {
      yellow: '#F2DCAB',      pink: {
        50: '#FEFD8FB',
        100: '#FEF1F6',
        200: '#FDE3ED',
        300: '#FCC7DB',
        400: '#FAA5C6',
        500: '#FD8FB4',
        600: '#FE649A',
        700: '#E94C85',
        800: '#CE3870',
        900: '#A8295D',
      }
    }
  },
  shortcuts: {
    'bg-yellow': 'bg-yellow',
    'size-7': 'w-7 h-7',
    'size-8': 'w-8 h-8'
  }
})
