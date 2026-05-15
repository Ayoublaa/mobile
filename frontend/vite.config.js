import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/upload-log": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/detections": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/clusters": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/recommendations": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/stats": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/alerts/history": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/settings": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/alert/test-email": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
