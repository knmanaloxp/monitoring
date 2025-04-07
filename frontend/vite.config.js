import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Load environment variables
const VITE_API_URL = process.env.VITE_API_URL || 'https://network-monitor-api.example.com'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: VITE_API_URL,
        changeOrigin: true,
        secure: true,
        ws: true
      }
    }
  },
  define: {
    'process.env.VITE_API_URL': JSON.stringify(VITE_API_URL)
  }
})