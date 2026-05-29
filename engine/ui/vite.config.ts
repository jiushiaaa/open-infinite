import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// 开发时把 /api 代理到 `lne browse` 的 stdlib HTTP server（默认 127.0.0.1:8765）。
// 通过 LNE_API_TARGET 覆盖。生产构建时前端独立部署，运行期由 VITE_API_BASE 决定。
const API_TARGET = process.env.LNE_API_TARGET || "http://127.0.0.1:8765";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: API_TARGET,
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
