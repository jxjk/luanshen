import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react({
    babel: {
      plugins: []
    }
  })],
  esbuild: {
    logOverride: { 'this-is-undefined-in-esm': 'silent' }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api/v1/alarms': {
        target: 'http://localhost:5009',
        changeOrigin: true,
      },
      '/api/v1/notifications': {
        target: 'http://localhost:5009',
        changeOrigin: true,
      },
      '/api/v1/device': {
        target: 'http://localhost:5008',
        changeOrigin: true,
      },
      '/api/v1/monitoring': {
        target: 'http://localhost:5008',
        changeOrigin: true,
      },
      '/api/v1/quality': {
        target: 'http://localhost:5010',
        changeOrigin: true,
      },
      '/api/v1/batches': {
        target: 'http://localhost:5010',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://localhost:5007',
        changeOrigin: true,
      },
    },
  },
})