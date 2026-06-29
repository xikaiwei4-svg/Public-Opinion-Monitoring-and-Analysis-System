#!/bin/bash
# ============================================================
# migrate.sh — 校园舆情系统 数据库初始化流程编排
#
# 用法：
#   ./scripts/migrate.sh                         # 仅建表
#   ./scripts/migrate.sh --with-demo              # 建表 + 灌演示数据
#   ./scripts/migrate.sh --drop --with-demo       # 重建表 + 灌演示数据
#   ./scripts/migrate.sh --env-file /path/.env    # 指定 .env 路径
#   ./scripts/migrate.sh --dry-run                # 仅打印，不动数据库
#
# 前置条件：
#   1. MySQL 服务已运行
#   2. .env 文件已配置数据库连接信息
#   3. Python 3.10+ + pip 依赖已安装
# ============================================================
set -e  # 任一步骤失败立即停止

# ---- 颜色输出 ----
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
NC="\033[0m"  # No Color
BOLD="\033[1m"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR"

print_step()   { echo -e "${CYAN}[$1/$5]${NC} $2"; }
print_ok()     { echo -e "  ${GREEN}✅${NC} $1"; }
print_warn()   { echo -e "  ${YELLOW}⚠️${NC}  $1"; }
print_err()    { echo -e "  ${RED}❌${NC} $1"; }
print_header() { echo; echo -e "${BOLD}$1${NC}"; echo; }

# ---- 参数解析 ----
WITH_DEMO=false
DROP_FIRST=false
DRY_RUN=false
ENV_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --with-demo)    WITH_DEMO=true; shift ;;
        --drop)         DROP_FIRST=true; shift ;;
        --dry-run)      DRY_RUN=true; shift ;;
        --env-file)     ENV_FILE="$2"; shift 2 ;;
        --help)
            echo "用法: $0 [选项]"
            echo "  --with-demo     建表后灌入演示数据"
            echo "  --drop          先删除旧表再重建（数据会丢失）"
            echo "  --dry-run       只打印执行计划，不动数据库"
            echo "  --env-file FILE 指定 .env 文件路径"
            echo "  --help          显示此帮助"
            exit 0
            ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

# ---- 准备 ----
echo -e "${BOLD}"
echo "======================================"
echo "  校园舆情系统 — 数据库初始化"
echo "======================================"
echo -e "${NC}"
echo "项目目录: $PROJECT_DIR"
echo "工作模式: $([ "$DROP_FIRST" = true ] && echo '重建表' || echo '增量建表')"
echo "演示数据: $([ "$WITH_DEMO" = true ] && echo '是' || echo '否')"
echo "Dry-Run:  $([ "$DRY_RUN" = true ] && echo '是' || echo '否')"
echo

# 检查 Python
PYTHON=""
for cmd in python3 python python3.10 python3.11; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    print_err "未找到 Python，请安装 Python 3.10+"
    exit 1
fi
print_ok "Python: $($PYTHON --version 2>&1)"

# 构建 --env-file 参数
ENV_ARG=""
if [ -n "$ENV_FILE" ]; then
    ENV_ARG="--env-file $ENV_FILE"
fi

# ---- 步骤 1: 加载环境变量 ----
print_header "步骤 1/3：加载环境变量"

if [ -f "$PROJECT_DIR/.env" ]; then
    set -a; source "$PROJECT_DIR/.env"; set +a
    print_ok "已加载: $PROJECT_DIR/.env"
elif [ -f "$BACKEND_DIR/.env" ]; then
    set -a; source "$BACKEND_DIR/.env"; set +a
    print_ok "已加载: $BACKEND_DIR/.env"
else
    print_warn "未找到 .env 文件，依赖系统环境变量"
fi

# 验证关键变量
if [ -z "$MYSQL_PASSWORD" ]; then
    print_warn "MYSQL_PASSWORD 未设置"
fi
if [ -z "$SECRET_KEY" ]; then
    print_warn "SECRET_KEY 未设置"
fi

# ---- 步骤 2: 建表 ----
print_header "步骤 2/3：初始化数据库表"

DROP_ARG=""
if [ "$DROP_FIRST" = true ]; then
    DROP_ARG="--drop"
fi

DRY_ARG=""
if [ "$DRY_RUN" = true ]; then
    DRY_ARG="--dry-run"
fi

echo "执行: $PYTHON $SCRIPT_DIR/init_db.py $DROP_ARG $ENV_ARG $DRY_ARG"
echo

if [ "$DRY_RUN" = true ]; then
    $PYTHON "$SCRIPT_DIR/init_db.py" $DROP_ARG $ENV_ARG --verbose
else
    $PYTHON "$SCRIPT_DIR/init_db.py" $DROP_ARG $ENV_ARG
fi

if [ $? -eq 0 ]; then
    print_ok "建表完成"
else
    print_err "建表失败"
    exit 1
fi

# ---- 步骤 3: 灌演示数据（可选） ----
if [ "$WITH_DEMO" = true ]; then
    print_header "步骤 3/3：灌入演示数据"

    DEMO_DRY_ARG=""
    if [ "$DRY_RUN" = true ]; then
        DEMO_DRY_ARG="--dry-run"
    fi

    echo "执行: $PYTHON $BACKEND_DIR/generate_demo_data.py $DEMO_DRY_ARG $ENV_ARG"
    echo

    cd "$BACKEND_DIR"
    $PYTHON generate_demo_data.py $DEMO_DRY_ARG $ENV_ARG

    if [ $? -eq 0 ]; then
        print_ok "演示数据生成完成"
    else
        print_err "演示数据生成失败"
        exit 1
    fi
else
    print_header "步骤 3/3：跳过演示数据"
    print_warn "如需灌入演示数据，请加 --with-demo 参数"
fi

# ---- 完成 ----
print_header "🎉 全部完成"
echo
echo "  数据库: $MYSQL_DATABASE"
echo "  主机:   $MYSQL_HOST:$MYSQL_PORT"
echo

if [ "$WITH_DEMO" = true ] && [ "$DRY_RUN" = false ]; then
    echo "  🔗 访问地址: http://localhost:8001/docs"
    echo "  🔐 管理员: admin / admin123"
fi
echo
