import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

import { defineConfig, loadEnv } from 'vite'
import viteReact from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { tanStackRouterCodeSplitter } from '@tanstack/router-plugin/vite'
import tsconfigPaths from 'vite-tsconfig-paths'

const __dirname = dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  return {
    plugins: [
      tanStackRouterCodeSplitter(),
      viteReact(),
      tailwindcss(),
      tsconfigPaths(),
    ],
    server: {
      proxy: {
        '/api': {
          target: env.VITE_API_URL,
          changeOrigin: true,
        },
      },
    },
  }
})
