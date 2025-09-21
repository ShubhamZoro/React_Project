import { defineConfig, loadEnv } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "")

  return {
    plugins: [react()],
    server: {
      ...(env.VITE_DEBUG === "true"
        ? {
            proxy: {
              "/api": {
                target: "http://localhost:8080",
                changeOrigin: true,
                secure: false,
              },
            },
          }
        : {}),
    },
    build: {
      outDir: "dist",
    },
  }
})
