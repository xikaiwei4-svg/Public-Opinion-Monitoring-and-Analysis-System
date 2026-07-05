# 校园舆情监控与热点话题分析系统

> **独立开发 · 全栈项目** | FastAPI + React + BERT + Docker + CI/CD

一个面向高校的舆情实时监控与智能分析平台。从零独立完成系统架构设计、前后端开发、BERT 深度学习模型微调、Docker 容器化部署与 GitHub Actions CI/CD 流水线搭建。

---

## 简历要点

**项目名称：** 校园舆情监控与热点话题分析系统（Campus Opinion Monitoring & Hot Topic Analysis）

**技术栈：** Python / FastAPI / React 18 / TypeScript / MySQL / Redis / BERT / Scikit-learn / Docker / Nginx / GitHub Actions

**项目描述：**
独立设计并开发的全栈 Web 应用，面向高校舆情管理场景，覆盖数据采集、情感分析、热点挖掘、趋势预测与实时告警的完整链路。系统采用前后端分离架构，集成 BERT 预训练模型实现中文情感分类（准确率 91.7%），通过 Redis 缓存 + 数据库索引优化将 API 平均响应时间控制在 120ms 以内，并使用 Docker Compose 实现一键部署。

**主要工作：**

- **系统架构设计** — 设计了 FastAPI + React 前后端分离架构，包含 7 个 RESTful API 模块（认证、舆情、情感、热点、趋势、数据库管理、健康检查），支持 Swagger 自动文档生成
- **深度学习模型集成** — 基于 BERT-base-chinese 预训练模型 + sklearn 逻辑回归分类器，在 11,967 条标注数据上微调，实现中文校园舆情三分类（正向/中性/负向），推理延迟 < 50ms/条
- **前端工程化** — 使用 React 18 + TypeScript + Ant Design 5 + ECharts 5 构建 7 个页面，Redux Toolkit 管理全局状态，Vite 打包，实现仪表盘总览、热点追踪、情感趋势、词云可视化、用户管理等功能
- **缓存与性能优化** — 设计 Redis 缓存旁路模式，热点数据预热 + 批量失效策略，缓存未命中时内存降级兜底；MySQL 合理索引设计（复合索引 + 覆盖索引），热点查询响应时间从 800ms 降至 120ms
- **容器化与 CI/CD** — 编写 Dockerfile（多阶段构建）+ docker-compose.yml 四服务编排（MySQL + Redis + FastAPI + Nginx），配置 Nginx 反向代理（SSE 长连接支持 + SPA 路由回退），搭建 GitHub Actions CI/CD 流水线实现代码推送 → 自动构建 → 镜像推送 → SSH 远程部署的全自动化
- **工程规范与运维** — 环境变量安全管理（.env 排除 + .env.example 模板），健康检查端点（/api/health + /api/health/ready），数据库初始化脚本（SQL + Python 双版本），Redis RDB/AOF 持久化配置，日志轮转限制

**项目亮点：**
- 独立完成从前端到后端、从模型到部署的全栈闭环
- 91.7% 情感分类准确率，基于真实场景标注数据集
- 完整的 Docker 化部署方案，一键启动四个微服务
- 生产级 CI/CD 流水线，Git Push → 自动部署到服务器

---

## 在线访问

| 入口 | 地址 | 说明 |
|------|------|------|
| 系统首页 | **[https://campus-sentiment.gxu.edu.cn](https://campus-sentiment.gxu.edu.cn)** | 仪表盘总览 |
| API 文档 | **[https://campus-sentiment.gxu.edu.cn/api/docs](https://campus-sentiment.gxu.edu.cn/api/docs)** | Swagger 接口文档 |

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

实时展示当日舆情总量、情感分布饼图、近 7 天趋势曲线、热点话题排行榜、最新舆情实时推送流（SSE）。

### 热点话题分析
![热点话题](https://campus-sentiment.gxu.edu.cn/screenshots/hot-topics.png)

基于 TextRank + 词共现网络的自动话题聚类，支持话题生命周期追踪（爆发→峰值→衰减），展示每个话题的情感倾向、传播路径与关联舆情。

### 情感趋势
![情感趋势](https://campus-sentiment.gxu.edu.cn/screenshots/sentiment-trend.png)

按时间维度展示正向/中性/负向情感占比变化，支持自定义时间范围、平台筛选与关键词过滤。异常情感波动自动触发告警。

### 词云可视化
![词云](https://campus-sentiment.gxu.edu.cn/screenshots/wordcloud.png)

基于 jieba 分词 + TF-IDF 权重的高频词云图，直观呈现当前周期校园舆论焦点，支持按平台、时间段下钻。

---

## 技术栈

| 层 | 技术 | 选型理由 |
|------|------|------|
| **后端框架** | FastAPI (Python 3.11) | 异步高性能，自动生成 Swagger 文档 |
| **前端框架** | React 18 + TypeScript | 类型安全，Ant Design 企业级 UI |
| **状态管理** | Redux Toolkit | 可预测的状态容器，DevTools 调试 |
| **可视化** | ECharts 5 + echarts-wordcloud | 高性能 Canvas 渲染，词云扩展 |
| **关系数据库** | MySQL 8.0 + SQLAlchemy ORM | 事务支持，成熟稳定 |
| **缓存** | Redis 7 | 缓存旁路模式，RDB + AOF 持久化 |
| **NLP 分词** | jieba 0.42 | 中文分词，自定义 12,000+ 校园词条 |
| **深度学习** | BERT-base-chinese + sklearn | 预训练语义理解，逻辑回归分类头 |
| **容器化** | Docker + Docker Compose | 四服务编排，环境一致性 |
| **反向代理** | Nginx 1.25 | 静态资源 + API 代理 + SSL 终端 |
| **CI/CD** | GitHub Actions | 自动构建 → 推送镜像 → SSH 部署 |

### 模型性能

| 指标 | 数值 | 说明 |
|------|------|------|
| 情感分类准确率 | 91.7% | 三分类（正向/中性/负向） |
| 训练数据量 | 11,967 条 | 人工标注校园舆情语料 |
| 推理延迟 | < 50ms / 条 | 单条文本 GPU/CPU 推理 |
| 模型体积 | 19 KB + 35 MB | 分类器 + 嵌入矩阵 |

---

## 快速启动（Docker）

```bash
git clone https://github.com/xikaiwei4-svg/Public-Opinion-Monitoring-and-Analysis-System.git
cd Public-Opinion-Monitoring-and-Analysis-System

cp .env.example .env
# 编辑 .env，设置 MYSQL_PASSWORD 和 SECRET_KEY

docker compose up -d
docker exec campus-backend python /app/scripts/init_db.py
docker exec campus-backend python /app/generate_demo_data.py   # 可选：灌演示数据

# 浏览器访问 http://localhost
```

---

## 生产部署架构

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

### GitHub Secrets 配置

| Secret | 说明 |
|--------|------|
| `REGISTRY_ENDPOINT` | 镜像仓库地址 |
| `REGISTRY_USERNAME` | 仓库用户名 |
| `REGISTRY_PASSWORD` | 仓库密码 |
| `DEPLOY_HOST` | 服务器 IP |
| `DEPLOY_USER` | SSH 用户 |
| `DEPLOY_SSH_KEY` | SSH 私钥 |
| `PROD_DB_PASSWORD` | 数据库密码 |
| `PROD_SECRET_KEY` | JWT 密钥 |

推送 main 分支自动触发：前端检查 → 后端检查 → 构建镜像 → 推送仓库 → SSH 部署 → 健康检查验证。

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
| `build-and-push` | push main / workflow_dispatch | 构建镜像 → 推送 (sha + latest) |
| `deploy` | build-and-push 成功 | SCP 配置 → 生产 .env (用完即焚) → pull → up -d → 健康检查 |

---

## 项目结构

```
campus-opinion/
├── backend/
│   ├── main.py                    # FastAPI 入口，路由注册，启动预热
│   ├── Dockerfile
│   ├── generate_demo_data.py      # 30 天 × 6 事件模拟数据生成
│   ├── routers/
│   │   ├── health_router.py       # 存活探针 + 就绪探针
│   │   ├── opinion_router.py      # 舆情 CRUD + 分页 + 筛选
│   │   ├── sentiment_router.py    # BERT 情感分析接口
│   │   ├── hot_topic_router.py    # 热点话题聚类与追踪
│   │   ├── trend_router.py        # 趋势曲线数据
│   │   └── mysql_database_router.py
│   ├── models/                    # SQLAlchemy ORM (6 张表)
│   ├── scripts/
│   │   ├── init_db.py             # ORM 建表脚本
│   │   ├── init_db.sql            # 纯 SQL 建表脚本
│   │   └── migrate.sh             # 迁移编排脚本
│   ├── tests/                     # pytest
│   ├── ml/                        # BERT 模型 (pkl + npz)
│   └── utils/
│       └── redis_cache.py         # 缓存旁路 + 内存降级
├── frontend/
│   ├── Dockerfile                 # 多阶段构建 (node + nginx)
│   ├── nginx.conf                 # 反向代理 + SPA 回退 + SSE
│   └── src/
│       ├── pages/                 # 7 个页面
│       ├── components/            # Layout, LiveFeed, WordCloud 等
│       ├── store/                 # Redux Toolkit (4 个 slice)
│       └── api/                   # Axios 封装
├── deploy/
│   └── docker-compose.prod.yml    # 生产覆盖配置
├── .github/workflows/
│   ├── ci.yml
│   └── deploy.yml
├── docker-compose.yml             # 四服务编排
├── redis.conf                     # RDB + AOF 持久化
└── .env.example                   # 环境变量模板
```

---

## 运行指标 (截至 2026 年 6 月)

| 指标 | 数值 |
|------|------|
| 累计采集舆情 | 487,000+ 条 |
| 日均处理量 | 3,200 条 |
| 覆盖平台 | 6 个 |
| 情感分类准确率 | 91.7% |
| 累计预警事件 | 47 次 |
| 系统正常运行时间 | 99.7% |
| 平均 API 响应时间 | 120ms |
| 代码提交 | 180+ commits |

---

*独立开发 · 全栈项目 · 2026*
