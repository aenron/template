#!/bin/bash

# Docker构建脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  FastAPI Docker 构建脚本${NC}"
    echo -e "${BLUE}================================${NC}"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    print_message "Docker 和 Docker Compose 已安装"
}

# 构建生产镜像
build_production() {
    print_message "构建生产环境镜像..."
    docker build -t fastapi-project:latest .
    print_message "生产环境镜像构建完成"
}

# 构建开发镜像
build_development() {
    print_message "构建开发环境镜像..."
    docker build -f Dockerfile.dev -t fastapi-project:dev .
    print_message "开发环境镜像构建完成"
}

# 清理镜像
clean_images() {
    print_warning "清理未使用的镜像..."
    docker image prune -f
    print_message "镜像清理完成"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -p, --production    构建生产环境镜像"
    echo "  -d, --development   构建开发环境镜像"
    echo "  -a, --all           构建所有镜像"
    echo "  -c, --clean         清理未使用的镜像"
    echo "  -h, --help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --production     构建生产镜像"
    echo "  $0 --development    构建开发镜像"
    echo "  $0 --all           构建所有镜像"
}

# 主函数
main() {
    print_header
    
    # 检查Docker
    check_docker
    
    # 解析命令行参数
    case "${1:-}" in
        -p|--production)
            build_production
            ;;
        -d|--development)
            build_development
            ;;
        -a|--all)
            build_production
            build_development
            ;;
        -c|--clean)
            clean_images
            ;;
        -h|--help|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@" 