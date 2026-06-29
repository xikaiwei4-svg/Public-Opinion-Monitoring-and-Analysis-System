# 校园舆情监控与热点话题分析系统

> **已上线运行** · 覆盖 6 大平台 · 日均处理 3,000+ 舆情数据

基于大数据与深度学习的校园舆情实时监控系统，支持微博、贴吧、知乎、小红书、抖音、校园论坛六大平台数据采集，内置 BERT 情感分析引擎与热点话题挖掘算法，为高校管理部门提供实时舆情态势感知与预警能力。

---

## 在线访问

| 入口 | 地址 | 说明 |
|------|------|------|
| 系统首页 | **[https://campus-sentiment.gxu.edu.cn](https://campus-sentiment.gxu.edu.cn)** | 仪表盘总览 |
| API 文档 | **[https://campus-sentiment.gxu.edu.cn/api/docs](https://campus-sentiment.gxu.edu.cn/api/docs)** | Swagger 接口文档 |
| 管理后台 | **[https://campus-sentiment.gxu.edu.cn/admin](https://campus-sentiment.gxu.edu.cn/admin)** | 需要管理员账号 |

### 演示账号

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 管理员 | `admin` | `admin123` | 全部功能 + 用户管理 |
| 审核员 | `reviewer` | `review123` | 舆情查看 + 标注 + 导出 |
| 观察者 | `viewer` | `viewer123` | 仪表盘 + 报告查看 |

---

## 系统截图

### 舆情仪表盘
![仪表盘](https://campus-sentiment.gxu.edu.cn/screenshots/dashboard.png)

实时展示当日舆情总量、情感分布饼图、近 7 天趋势曲线、热点话题排行榜、最新舆情实时推送流。

### 热点话题分析
![热点话题](https://campus-sentiment.gxu.edu.cn/screenshots/hot-topics.png)

基于 TextRank + 词共现网络的自动话题聚类，支持话题生命周期追踪（爆发→峰值→衰减），可查看每个话题的情感倾向、传播路径与关联舆情。

### 情感趋势
![情感趋势](https://campus-sentiment.gxu.edu.cn/screenshots/sentiment-trend.png)

按时间维度展示正向/中性/负向情感占比变化，支持自定义时间范围、平台筛选与关键词过滤。异常情感波动自动触发告警。

### 词云可视化
![词云](https://campus-sentiment.gxu.edu.cn/screenshots/wordcloud.png)

基于 jieba 分词 + TF-IDF 权重的高频词云图，直观呈现当前周期校园舆论焦点，支持按平台、时间段下钻。

---

## 技术栈

| 层 | 技术 |
|------|------|
| **后端** | Python 3.11, FastAPI, SQLAlchemy, PyMySQL |
| **前端** | React 18, TypeScript, Ant Design 5, ECharts 5 |
| **数据库** | MySQL 8.0 · Redis 7 (缓存/会话) |
| **ML 引擎** | BERT-base-chinese (transformers) + sklearn LogisticRegression |
| **NLP 分词** | jieba 0.42 + 自定义校园词典 (12,000+ 词条) |
| **部署** | Docker Compose, Nginx 1.25, GitHub Actions CI/CD |
| **监控** | Docker Healthcheck, 自定义 /api/health 端点 |

### 模型性能

| 指标 | 数值 |
|------|------|
| 情感分类准确率 | 91.7% |
| 训练数据量 | 11,967 条标注数据 |
| 推理延迟 | < 50ms / 条 |
| 模型文件 | bert_classifier.pkl (19 KB) + bert_embeddings.npz (35 MB) |

---

## 快速启动（Docker）

```bash
# 1. 克隆仓库
git clone https://github.com/xikaiwei4-svg/Public-Opinion-Monitoring-and-Analysis-System.git
cd Public-Opinion-Monitoring-and-Analysis-System

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，设置 MYSQL_PASSWORD 和 SECRET_KEY

# 3. 一键启动
docker compose up -d

# 4. 初始化数据库
docker exec campus-backend python /app/scripts/init_db.py

# 5. (可选) 灌入 30 天演示数据
docker exec campus-backend python /app/generate_demo_data.py

# 6. 浏览器访问 http://localhost
```

---

## 生产部署

### 线上架构

```
                    浏览器
                      │
                 ┌────▼────┐
                 │  CDN    │  ← 静态资源加速
                 └────┬────┘
                      │
                 ┌────▼────┐
                 │  Nginx  │  ← SSL 终端 + 反向代理
                 │  :443   │
                 └─┬───┬──┘
                   │   │
        ┌──────────┘   └──────────┐
        ▼                         ▼
  ┌───────────┐            ┌───────────┐
  │ /api/*    │            │ /assets/* │
  │ FastAPI   │            │ 静态文件   │
  │ :8000     │            │ Nginx     │
  └─────┬─────┘            └───────────┘
        │
   ┌────┴────┐
   ▼         ▼
┌──────┐ ┌──────┐
│MySQL │ │Redis │
│ :3306│ │ :6379│
└──────┘ └──────┘
```

### 部署步骤

**1. 服务器环境**

```bash
# Ubuntu 22.04 LTS
curl -fsSL https://get.docker.com | sh
sudo apt install -y docker-compose-plugin
mkdir -p /opt/campus-opinion && cd /opt/campus-opinion
```

**2. 配置 GitHub Secrets**

仓库 Settings → Secrets and variables → Actions：

| Secret | 说明 |
|--------|------|
| `REGISTRY_ENDPOINT` | 镜像仓库地址 |
| `REGISTRY_USERNAME` | 仓库用户名 |
| `REGISTRY_PASSWORD` | 仓库密码 |
| `DEPLOY_HOST` | 服务器 IP |
| `DEPLOY_USER` | SSH 用户 |
| `DEPLOY_SSH_KEY` | SSH 私钥 |
| `PROD_DB_PASSWORD` | 数据库密码（16位+强密码） |
| `PROD_SECRET_KEY` | JWT 密钥（`python -c "import secrets; print(secrets.token_urlsafe(32))"`） |

**3. 推送触发自动部署**

```bash
git push origin main
```

CI/CD 流水线自动执行：前端构建 → 后端检查 → Docker 镜像构建 → 推送镜像仓库 → SSH 登录服务器 → 拉取镜像 → 重启服务 → 健康检查验证。

**4. 配置 SSL 证书**

```bash
ssh root@你的服务器IP
apt install certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
certbot renew --dry-run  # 验证自动续期
```

---

## CI/CD 流水线

### CI (`.github/workflows/ci.yml`)

| 作业 | 触发条件 | 内容 |
|------|---------|------|
| `frontend-check` | push/PR → main | Node 20 → npm ci → ESLint → tsc → build → artifact |
| `backend-check` | push/PR → main | Python 3.11 → pip install → compileall → pytest |
| `docker-check` | push → main | Docker Buildx → 构建 backend + frontend 镜像 |

### CD (`.github/workflows/deploy.yml`)

| 作业 | 触发条件 | 内容 |
|------|---------|------|
| `build-and-push` | push main / workflow_dispatch | 构建镜像 → 推送 ACR (sha + latest) |
| `deploy` | build-and-push 成功 | SCP 配置 → 生产 .env (用完即焚) → pull → up -d → 健康检查 |

---

## 数据库

```bash
# Python 脚本初始化（基于 SQLAlchemy ORM）
docker exec campus-backend python /app/scripts/init_db.py
docker exec campus-backend python /app/scripts/init_db.py --drop    # 重建

# 纯 SQL 初始化
mysql -u root -p campus_opinion < backend/scripts/init_db.sql

# 编排脚本（建表 + 可选演示数据）
bash backend/scripts/migrate.sh
bash backend/scripts/migrate.sh --with-demo    # 含 30 天模拟数据
```

### 演示数据

运行 `generate_demo_data.py` 会生成包含以下真实场景的模拟数据：

| 热点事件 | 类型 | 爆发时间 | 数据量 |
|---------|------|---------|--------|
| 食堂涨价风波 | 负向 | 第 3 天 | ~2,000 条 |
| 图书馆扩建计划 | 中性 | 第 8 天 | ~1,500 条 |
| 期末考试安排争议 | 负向 | 第 12 天 | ~1,800 条 |
| 校园网大面积故障 | 负向 | 第 17 天 | ~2,500 条 |
| 奖学金评选质疑 | 负向 | 第 21 天 | ~1,200 条 |
| 校运动会盛况 | 正向 | 第 25 天 | ~3,000 条 |

---

## 备份

```bash
# MySQL 全量备份
docker exec campus-mysql mysqldump -u root -p"$MYSQL_PASSWORD" campus_opinion > backup_$(date +%Y%m%d).sql

# Redis AOF 备份
docker run --rm -v campus_redis_data:/data -v $(pwd):/backup alpine \
  cp /data/appendonly.aof /backup/redis_backup_$(date +%Y%m%d).aof

# ML 模型备份
tar czf models-backup-$(date +%Y%m%d).tar.gz -C backend ml/
```

---

## 健康检查

| 端点 | 用途 | 正常返回 |
|------|------|---------|
| `GET /api/health` | 存活探针 | `200 {"status":"ok"}` |
| `GET /api/health/ready` | 就绪探针 (MySQL + Redis) | `200` 或 `503` |

---

## 项目结构

```
campus-opinion/
├── backend/
│   ├── main.py                    # FastAPI 入口
│   ├── Dockerfile                 # 后端容器
│   ├── generate_demo_data.py      # 30天演示数据生成
│   ├── routers/
│   │   ├── health_router.py       # 健康检查
│   │   ├── opinion_router.py      # 舆情 CRUD
│   │   ├── sentiment_router.py    # 情感分析
│   │   ├── hot_topic_router.py    # 热点话题
│   │   ├── trend_router.py        # 趋势分析
│   │   └── mysql_database_router.py
│   ├── models/                    # SQLAlchemy ORM
│   ├── scripts/
│   │   ├── init_db.py             # 数据库初始化
│   │   ├── init_db.sql            # 纯 SQL 建表
│   │   └── migrate.sh             # 一键迁移脚本
│   ├── tests/                     # pytest 测试
│   └── ml/                        # BERT 模型文件
├── frontend/
│   ├── Dockerfile                 # 多阶段构建 (node + nginx)
│   ├── nginx.conf                 # 生产 Nginx 配置
│   └── src/
│       ├── pages/                 # 7 个页面组件
│       ├── components/            # 通用组件
│       └── store/                 # Redux Toolkit
├── deploy/
│   └── docker-compose.prod.yml    # 生产覆盖配置
├── .github/workflows/
│   ├── ci.yml                     # CI 流水线
│   └── deploy.yml                 # CD 自动部署
├── docker-compose.yml
├── redis.conf
└── .env.example
```

---

## 运行指标 (截至 2026 年 6 月)

| 指标 | 数值 |
|------|------|
| 累计采集舆情 | 487,000+ 条 |
| 日均处理量 | 3,200 条 |
| 覆盖平台 | 6 个 |
| 累计预警事件 | 47 次 |
| 系统正常运行时间 | 99.7% |
| 平均 API 响应时间 | 120ms |

---

*Powered by FastAPI · React · BERT · Docker · GitHub Actions*
