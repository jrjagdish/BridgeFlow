import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In Docker, API_URL is set to http://api:8000 (service name in compose).
// Locally it defaults to http://localhost:8000 so nothing changes for dev outside Docker.
const API_TARGET = process.env.API_URL || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',   // needed so the container port is reachable from the host
    port: 5173,
    proxy: {
      '/oauth':  { target: API_TARGET, changeOrigin: true },
      '/notion': { target: API_TARGET, changeOrigin: true },
      '/sheets': { target: API_TARGET, changeOrigin: true },
      '/config': { target: API_TARGET, changeOrigin: true },
      '/me':     { target: API_TARGET, changeOrigin: true },
      '/status': { target: API_TARGET, changeOrigin: true },
      '/logout': { target: API_TARGET, changeOrigin: true },
      '/sync':   { target: API_TARGET, changeOrigin: true },
    },
  },
})
