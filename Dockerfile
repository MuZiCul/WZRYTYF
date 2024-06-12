# 使用官方Python 3.8镜像作为基础镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 将当前目录下的requirements.txt复制到容器的/app目录下
COPY requirements.txt .

# 安装所需包
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt
# 将当前目录下的所有文件复制到容器的/app目录下
COPY . .

# 暴露端口
EXPOSE 5700

# 定义环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 容器启动时运行的命令
CMD ["flask", "run", "--host=0.0.0.0"]