import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
    },
    allowedHosts: ["millions-mandate-oil-republic.trycloudflare.com", "https://millions-mandate-oil-republic.trycloudflare.com"],
  },
});
