import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    // Lets every import read `@/components/...` instead of a chain of
    // `../../..` that breaks the moment a file moves.
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    port: 5173,
    // The API is a separate origin in development. Proxying it here means
    // the browser sees one origin, so no CORS configuration is needed for
    // local work and the production setup (Nginx in front of both) is the
    // thing being imitated rather than worked around.
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/health": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
