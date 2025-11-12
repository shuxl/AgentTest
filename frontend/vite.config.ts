import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '');
  
  // 从环境变量获取后端地址，默认为 Python 后端
  const API_BASE_URL = env.VITE_API_BASE_URL || 'http://localhost:8001';

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: API_BASE_URL,
          changeOrigin: true,
        },
        '/health': {
          target: API_BASE_URL,
          changeOrigin: true,
        },
      },
    },
  };
});

