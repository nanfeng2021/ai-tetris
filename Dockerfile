FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ ./src/
COPY web/ ./web/
COPY config/ ./config/

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/state || exit 1

# 默认启动命令（Web 模式）
CMD ["python", "web/server.py"]
