import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/oauth':  { target: 'http://localhost:8000', changeOrigin: true },
      '/notion': { target: 'http://localhost:8000', changeOrigin: true },
      '/sheets': { target: 'http://localhost:8000', changeOrigin: true },
      '/config': { target: 'http://localhost:8000', changeOrigin: true },
      '/me':     { target: 'http://localhost:8000', changeOrigin: true },
      '/status': { target: 'http://localhost:8000', changeOrigin: true },
      '/logout': { target: 'http://localhost:8000', changeOrigin: true },
      '/sync':   { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
