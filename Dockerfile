FROM python:3.9-slim

WORKDIR /app

# 复制所有文件到容器
COPY . /app

# 列出文件确认复制成功
RUN ls -l /app

# 安装系统依赖和Python包
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    build-essential \
    libssl-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 8032

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8032/health || exit 1

# 使用 gunicorn 启动 Flask 应用
# 注意：由于应用需要在启动时初始化 Telegram，我们使用简单的 Python 启动方式
CMD ["python3", "main.py"]
