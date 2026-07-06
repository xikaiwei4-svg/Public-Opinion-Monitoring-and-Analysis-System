FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（包很小，不用换源）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    libmariadb-dev-compat \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# 用清华镜像加速 pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
