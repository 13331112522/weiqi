# 使用Python官方镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY server.py .

# 暴露端口
EXPOSE 8080

# 启动服务器
CMD ["python", "server.py"]
