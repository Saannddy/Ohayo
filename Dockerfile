# ──────────────────────────────────────────────────────────────────
# Ohayo — Web-only preview (Vite frontend, no Tauri native features)
# Usage:
#   docker build -t ohayo-web .
#   docker run -p 1420:1420 ohayo-web
# Then open http://localhost:1420 in your browser.
# ──────────────────────────────────────────────────────────────────
FROM node:22-alpine AS base
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci --frozen-lockfile

# Copy source
COPY index.html .
COPY vite.config.ts tsconfig.json tsconfig.node.json tailwind.config.ts postcss.config.js ./
COPY src/ ./src/

# ── Dev target (hot-reload) ───────────────────────────────────────
FROM base AS dev
EXPOSE 1420
CMD ["npx", "vite", "--host", "0.0.0.0", "--port", "1420"]

# ── Production web build ──────────────────────────────────────────
FROM base AS builder
RUN npm run build

FROM nginx:alpine AS prod
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
