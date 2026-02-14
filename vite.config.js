import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// https://vite.dev/config/
export default defineConfig({
    base: './',
    plugins: [react()],
    server: {
        port: 5173,
        fs: {
            // 외부 폴더(..)의 이미지를 제공할 수 있도록 허용
            allow: ['..']
        }
    },
    build: {
        outDir: 'dist',
        minify: false
    },
    publicDir: 'public',
    resolve: {
        alias: {
        }
    }
})
