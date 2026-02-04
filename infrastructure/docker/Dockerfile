# Dockerfile for Parameter Optimization Service
FROM python:3.11-alpine

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    pkgconfig \
    wget \
    curl \
    && rm -rf /var/cache/apk/*

# 复制依赖文件
COPY services/parameter-optimization/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY services/parameter-optimization/src ./src
COPY services/parameter-optimization/run.py .

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/optimization/health')" || exit 1

# 启动命令
CMD ["python", "run.py"]