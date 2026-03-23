# PersonalMind Dockerfile
# 使用方式:
#   docker build -t personalmind .
#   docker run -p 7860:7860 -e DEEPSEEK_API_KEY=sk-xxx personalmind

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖（使用国内镜像加速）
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目文件
COPY . .

# 创建数据目录（用于持久化记忆数据库）
RUN mkdir -p /app/data

# 声明数据卷（持久化记忆数据库）
VOLUME ["/app/data"]

# 暴露端口
EXPOSE 7860

# 环境变量默认值
ENV AI_PROVIDER=deepseek \
    WEB_UI_PORT=7860 \
    MEMORY_DB_PATH=/app/data/memory.db

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/')" || exit 1

# 启动命令
CMD ["python", "main.py"]
