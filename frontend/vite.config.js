import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // El navegador pide /api al servidor de Vite y este lo reenvía al contenedor
    // del backend, así el frontend no necesita saber la URL de la API.
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY || 'http://backend:8000',
        changeOrigin: true,
      },
    },
    watch: {
      // Necesario para que el hot-reload detecte cambios dentro de Docker.
      usePolling: true,
    },
  },
})
