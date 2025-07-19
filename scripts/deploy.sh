#!/bin/bash

# 通用部署脚本
# 用法: ./scripts/deploy.sh [staging|production] [version]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查参数
if [ $# -lt 1 ]; then
    log_error "用法: $0 [staging|production] [version]"
    exit 1
fi

ENVIRONMENT=$1
VERSION=${2:-latest}

# 验证环境
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log_error "无效的环境: $ENVIRONMENT. 必须是 'staging' 或 'production'"
    exit 1
fi

# 环境配置
case $ENVIRONMENT in
    staging)
        SERVER_HOST=${STAGING_HOST:-"staging.example.com"}
        SERVER_USER=${STAGING_USER:-"deploy"}
        SERVER_PATH=${STAGING_PATH:-"/opt/fastapi-project"}
        DOCKER_COMPOSE_FILE="docker-compose.yml"
        ;;
    production)
        SERVER_HOST=${PRODUCTION_HOST:-"production.example.com"}
        SERVER_USER=${PRODUCTION_USER:-"deploy"}
        SERVER_PATH=${PRODUCTION_PATH:-"/opt/fastapi-project"}
        DOCKER_COMPOSE_FILE="docker-compose.yml"
        ;;
esac

log_info "开始部署到 $ENVIRONMENT 环境"
log_info "服务器: $SERVER_USER@$SERVER_HOST"
log_info "路径: $SERVER_PATH"
log_info "版本: $VERSION"

# 检查SSH连接
log_info "检查SSH连接..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "$SERVER_USER@$SERVER_HOST" exit 2>/dev/null; then
    log_error "无法连接到服务器 $SERVER_HOST"
    exit 1
fi

# 创建备份
log_info "创建当前部署的备份..."
ssh "$SERVER_USER@$SERVER_HOST" "
    cd $SERVER_PATH
    if [ -f docker-compose.yml ]; then
        cp docker-compose.yml docker-compose.yml.backup.\$(date +%Y%m%d_%H%M%S)
    fi
"

# 更新代码（如果使用Git）
if [ -d ".git" ]; then
    log_info "更新代码..."
    ssh "$SERVER_USER@$SERVER_HOST" "
        cd $SERVER_PATH
        git fetch origin
        git reset --hard origin/main
    "
fi

# 更新Docker镜像
log_info "拉取最新的Docker镜像..."
ssh "$SERVER_USER@$SERVER_HOST" "
    cd $SERVER_PATH
    docker-compose pull
"

# 停止当前服务
log_info "停止当前服务..."
ssh "$SERVER_USER@$SERVER_HOST" "
    cd $SERVER_PATH
    docker-compose down
"

# 启动新服务
log_info "启动新服务..."
ssh "$SERVER_USER@$SERVER_HOST" "
    cd $SERVER_PATH
    docker-compose up -d
"

# 等待服务启动
log_info "等待服务启动..."
sleep 10

# 健康检查
log_info "执行健康检查..."
if ssh "$SERVER_USER@$SERVER_HOST" "curl -f http://localhost:8000/health"; then
    log_success "健康检查通过"
else
    log_error "健康检查失败"
    
    # 回滚
    log_warning "开始回滚..."
    ssh "$SERVER_USER@$SERVER_HOST" "
        cd $SERVER_PATH
        docker-compose down
        if [ -f docker-compose.yml.backup.* ]; then
            cp docker-compose.yml.backup.\$(ls docker-compose.yml.backup.* | tail -1) docker-compose.yml
            docker-compose up -d
        fi
    "
    
    log_error "部署失败，已回滚到上一个版本"
    exit 1
fi

# 清理旧镜像
log_info "清理旧Docker镜像..."
ssh "$SERVER_USER@$SERVER_HOST" "
    docker image prune -f
"

# 清理备份文件（保留最近5个）
log_info "清理旧备份文件..."
ssh "$SERVER_USER@$SERVER_HOST" "
    cd $SERVER_PATH
    ls -t docker-compose.yml.backup.* | tail -n +6 | xargs -r rm
"

log_success "部署到 $ENVIRONMENT 环境完成！"
log_info "服务地址: http://$SERVER_HOST" 