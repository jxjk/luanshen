# 报警管理微服务 Dockerfile
FROM python:3.11-alpine

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    curl

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 复制源代码
COPY src/ ./src/

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 5009

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5009/api/v1/health || exit 1

# 启动命令
CMD ["python", "run.py"]