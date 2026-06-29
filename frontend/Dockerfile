# ============================================================
# frontend/Dockerfile — 多阶段构建
# 阶段 1: Node 18 构建前端
# 阶段 2: Nginx 1.25-alpine 托管静态文件
# ============================================================

# ── 阶段 1：构建 ──
FROM node:18-alpine AS build

WORKDIR /app

# 先装依赖（利用 Docker 层缓存）
COPY package*.json ./
RUN npm ci

# 复制源码并构建
COPY . .
RUN npm run build

# ── 阶段 2：运行 ──
FROM nginx:1.25-alpine

# 从 build 阶段复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
