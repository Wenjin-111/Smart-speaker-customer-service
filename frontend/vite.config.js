import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/chat': {
        target: 'http://localhost:8001',
        changeOrigin: true
      },
      '/static': {
        target: 'http://localhost:8001',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: '../static/dist',
    emptyOutDir: true
  }
})