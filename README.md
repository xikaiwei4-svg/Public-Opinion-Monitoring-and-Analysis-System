# 校园舆情监控与热点话题分析系统

> **生产就绪** · FastAPI + React + Docker + CI/CD

基于大数据技术的校园舆情实时监控系统，支持多平台数据采集、情感分析、热点挖掘及可视化展示。

---

## 技术栈

| 层 | 技术 |
|------|------|
| **后端** | Python 3.11, FastAPI, SQLAlchemy, PyMySQL |
| **前端** | React 18, TypeScript, Ant Design, ECharts |
| **数据库** | MySQL 8.0, Redis 7 (缓存) |
| **ML 引擎** | BERT (transformers) + sklearn |
| **Deploy** | Docker Compose, Nginx, GitHub Actions CI/CD |

## 快速启动（Docker）

```bash
# 1. 创建环境变量文件
cp .env.example .env
# 编辑 .env，填写 MYSQL_PASSWORD 和 SECRET_KEY

# 2. 一键启动所有服务
docker compose up -d

# 3. 初始化数据库表
docker exec campus-backend python /app/scripts/init_db.py

# 4. 访问
#    前端:     http://localhost
#    API:     http://localhost:8001/docs
#    Swagger: http://localhost:8000/docs
```

## 生产部署

### 完整部署架构

```
                    ┌─────────────┐
                    │  浏览器访问   │
                    │  :80/:443   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Nginx     │  ← frontend 容器
                    │  (反向代理)  │
                    └──┬──────┬───┘
                       │      │
          ┌────────────┘      └────────────┐
          ▼                                  ▼
  ┌───────────────┐               ┌──────────────────┐
  │  /api/* 代理  │               │  静态文件（前端） │
  │  backend:8000 │               │  /usr/share/...   │
  └───────┬───────┘               └──────────────────┘
          │
  ┌───────▼───────┐     ┌────────────────┐
  │  FastAPI 后端  │────▶│  Redis (缓存)   │
  │  campus-net   │     └────────────────┘
  └───────┬───────┘
          │
  ┌───────▼───────┐
  │  MySQL 8.0    │
  │  (持久化)     │
  └───────────────┘
```

### 1. 准备服务器

```bash
# 安装 Docker（Ubuntu/Debian）
curl -fsSL https://get.docker.com | sh
sudo apt install -y docker-compose-plugin

# 创建部署目录
mkdir -p /opt/campus-opinion
```

### 2. 配置 GitHub Secrets

在 GitHub 仓库 → **Settings → Secrets and variables → Actions** 添加以下密钥：

| Secret | 说明 | 示例值 |
|--------|------|--------|
| `REGISTRY_ENDPOINT` | 镜像仓库地址 | `registry.cn-hangzhou.aliyuncs.com/你的命名空间` |
| `REGISTRY_USERNAME` | 镜像仓库用户名 | — |
| `REGISTRY_PASSWORD` | 镜像仓库密码 | — |
| `DEPLOY_HOST` | 服务器 IP | `123.45.67.89` |
| `DEPLOY_USER` | SSH 登录用户名 | `root` |
| `DEPLOY_SSH_KEY` | SSH 私钥内容 | `cat ~/.ssh/id_rsa` 的输出 |
| `PROD_DB_PASSWORD` | 生产数据库密码 | 16位+大小写数字符号 |
| `PROD_SECRET_KEY` | JWT 签名密钥 | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

### 3. 推送到 main 触发 CI/CD

```bash
git init
git add .
git commit -m "initial"
git remote add origin https://github.com/你的用户/仓库名.git
git push -u origin main
```

CI/CD 流水线会自动执行：
1. **CI** (ci.yml): 前端 lint + build → 后端语法检查 → Docker 构建检查
2. **CD** (deploy.yml): 构建镜像推送到 ACR → SCP 配置文件 → SSH 部署重启

### 4. SSL / HTTPS（选择其一）

**方案 A — certbot 自动（推荐）**

```bash
# SSH 登录服务器
ssh root@你的服务器IP

# 安装 certbot
apt install certbot python3-certbot-nginx

# 申请证书（certbot 会自动修改 Nginx 配置）
certbot --nginx -d yourdomain.com

# 验证自动续期
certbot renew --dry-run
```

**方案 B — 手动配置（无域名）**

docker-compose.yml 中 `frontend` 服务的 `ports` 配置为 `"80:80"`，通过 HTTP 访问。

## CI/CD 流水线

### CI (`.github/workflows/ci.yml`)

| 作业 | 触发 | 内容 |
|------|------|------|
| `frontend-check` | push/PR main | Node 20 → npm ci → ESLint → tsc → build → artifact |
| `backend-check` | push/PR main | Python 3.11 → pip install → compileall → pytest |
| `docker-check` | push main 仅 | Docker Buildx → 构建 backend + frontend 镜像（不推送） |

### CD (`.github/workflows/deploy.yml`)

| 作业 | 触发 | 内容 |
|------|------|------|
| `build-and-push` | push main / workflow_dispatch | 构建镜像 → 推送到 ACR (sha + latest) |
| `deploy` | build-and-push 成功后 | SCP 配置文件 → SSH → 生产 .env（用完销毁）→ pull → up -d → 健康检查 |

## 数据库

### 初始化

```bash
# 方式 1：Python 脚本（使用 SQLAlchemy ORM）
docker exec campus-backend python /app/scripts/init_db.py
docker exec campus-backend python /app/scripts/init_db.py --drop   # 重建

# 方式 2：纯 SQL
mysql -u root -p campus_opinion < backend/scripts/init_db.sql

# 方式 3：编排脚本（建表 + 可选灌测试数据）
bash backend/scripts/migrate.sh
bash backend/scripts/migrate.sh --with-demo   # 含 30 天演示数据
```

### 迁移

```bash
python backend/scripts/init_db.py --verbose   # 先看 SQL，不执行
python backend/scripts/init_db.py --drop      # 重建所有表（数据丢失！）
```

## 备份

```bash
# MySQL
docker exec campus-mysql mysqldump -u root -p"$MYSQL_PASSWORD" campus_opinion > backup.sql

# Redis（AOF 文件）
docker run --rm -v campus_redis_data:/data -v $(pwd):/backup alpine \
  cp /data/appendonly.aof /backup/

# ML 模型文件
tar czf models-backup.tar.gz -C backend ml/
```

## 健康检查

| 端点 | 用途 | 正常返回 |
|------|------|---------|
| `GET /api/health` | Docker healthcheck 存活探针 | 200 `{ "status": "ok" }` |
| `GET /api/health/ready` | 就绪探针（查 MySQL + Redis） | 200 或 503 |

## 项目结构

```
campus-opinion/
├── backend/                  # FastAPI 后端
│   ├── main.py
│   ├── Dockerfile
│   ├── routers/              # API 路由
│   │   ├── health_router.py
│   │   ├── sentiment_router.py
│   │   └── ...
│   ├── models/               # SQLAlchemy 模型
│   ├── scripts/              # 运维脚本
│   │   ├── init_db.py
│   │   ├── init_db.sql
│   │   └── migrate.sh
│   ├── tests/                # 测试
│   │   ├── conftest.py
│   │   └── test_health.py
│   └── ml/                   # ML 模型文件
│       ├── bert_sentiment.py
│       ├── bert_classifier.pkl
│       └── bert_embeddings.npz
├── frontend/                 # React 前端
│   ├── Dockerfile            # 多阶段构建
│   ├── nginx.conf            # 生产 Nginx 配置
│   ├── src/
│   └── .env.production
├── deploy/
│   └── docker-compose.prod.yml  # 生产覆盖配置
├── .github/workflows/
│   ├── ci.yml                # CI 流水线
│   └── deploy.yml            # CD 流水线
├── docker-compose.yml        # 主编排文件
├── redis.conf                # Redis 持久化配置
└── .env.example              # 环境变量模板

Powered by ❤️ and open source
