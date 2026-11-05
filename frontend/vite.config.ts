import { defineConfig } from 'vitest/config'
import viteReact from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import tanstackRouter from '@tanstack/router-plugin/vite'
import tsconfigPaths from 'vite-tsconfig-paths'


// https://vitejs.dev/config/
export default defineConfig(() => {
  return {
    plugins: [
        tanstackRouter({
            target: 'react',
            autoCodeSplitting: true,
        }),
      viteReact(),
      tailwindcss(),
      tsconfigPaths(),
    ],
    server: {
      proxy: {
        '/api': {
          target: "http://localhost:8000",
          changeOrigin: true,
        },
      },
    },
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './src/test/setup.ts',
    },
  }
})
