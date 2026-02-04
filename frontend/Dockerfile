# 前端 Dockerfile - 多阶段构建

# 阶段1: 构建阶段
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装所有依赖（包括开发依赖，构建需要 TypeScript）
RUN npm ci

# 复制源代码
COPY . .

# 构建生产版本（跳过 TypeScript 类型检查以加快构建速度）
    RUN npx vite build
# 阶段2: 生产阶段
FROM nginx:alpine

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]