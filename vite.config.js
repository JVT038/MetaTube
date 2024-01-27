import { defineConfig, splitVendorChunkPlugin } from "vite";
export default defineConfig({
  plugins: [splitVendorChunkPlugin()],
  server: {
    port: 3000,
    strictPort: true,
  },

  resolve: {
    alias: {
      '@': '/src',
    }
  },
  build: {
    rollupOptions: {
      input: {
        'overview': '/metatube/static/JS/overview.js',
        'settings': '/metatube/static/JS/settings.js',
        'global': '/metatube/static/JS/global.js',
      },
      output: {
        entryFileNames: '[name]-[hash].js',
        assetFileNames: '[name]-[hash][extname]',
      },
      manualChunks(id) {
        if(id.includes('node_modules')) {
            if(id.includes('bootstrap')) {
                return 'vendor-bootstrap';
            } else if(id.includes('jquery')) {
                return 'vendor-jquery'
            }
            return 'vendor';
        }
    }
    }
  }
});
