FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ ./src/
COPY config/ ./config/

# 暴露端口
EXPOSE 8000 9090

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0

# 默认启动命令（AI 模式）
CMD ["python", "src/game.py", "--mode", "ai", "--speed", "0.5"]
