import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: '/tools-assets/',
  build: { outDir: 'dist', emptyOutDir: true },
  server: {
    port: 5175,
    proxy: { '/tools': 'http://localhost:8000', '/search': 'http://localhost:8000' },
  },
});
