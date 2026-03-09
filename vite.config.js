import path from "node:path";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

const projectRoot = __dirname;
const staticRoot = path.resolve(projectRoot, "static");

export default defineConfig(({ command }) => ({
    root: staticRoot,
    base: command === "serve" ? "/" : "/static/dist/",
    plugins: [vue()],
    server: {
        host: "127.0.0.1",
        port: 5173,
        strictPort: true
    },
    build: {
        outDir: path.resolve(staticRoot, "dist"),
        emptyOutDir: true,
        sourcemap: true,
        rollupOptions: {
            input: path.resolve(staticRoot, "app.js"),
            output: {
                entryFileNames: "app.js",
                chunkFileNames: "chunks/[name]-[hash].js",
                assetFileNames: "assets/[name]-[hash][extname]"
            }
        }
    }
}));
