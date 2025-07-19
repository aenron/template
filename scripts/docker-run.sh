#!/bin/bash

# Docker运行脚本

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
    echo -e "${BLUE}  FastAPI Docker 运行脚本${NC}"
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

# 启动生产环境
start_production() {
    print_message "启动生产环境..."
    docker-compose up -d
    print_message "生产环境启动完成"
    print_message "访问地址: http://localhost:8000"
    print_message "API文档: http://localhost:8000/docs"
}

# 启动开发环境
start_development() {
    print_message "启动开发环境..."
    docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
    print_message "开发环境启动完成"
    print_message "访问地址: http://localhost:8000"
    print_message "API文档: http://localhost:8000/docs"
    print_message "pgAdmin: http://localhost:5050"
}

# 停止服务
stop_services() {
    print_message "停止所有服务..."
    docker-compose down
    print_message "服务已停止"
}

# 重启服务
restart_services() {
    print_message "重启服务..."
    docker-compose restart
    print_message "服务重启完成"
}

# 查看日志
show_logs() {
    print_message "显示服务日志..."
    docker-compose logs -f
}

# 查看特定服务日志
show_service_logs() {
    local service=$1
    print_message "显示 $service 服务日志..."
    docker-compose logs -f $service
}

# 进入容器
enter_container() {
    local service=${1:-app}
    print_message "进入 $service 容器..."
    docker-compose exec $service bash
}

# 清理资源
cleanup() {
    print_warning "清理所有资源..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_message "资源清理完成"
}

# 显示服务状态
show_status() {
    print_message "服务状态:"
    docker-compose ps
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  start, up          启动生产环境"
    echo "  dev                启动开发环境"
    echo "  stop, down         停止所有服务"
    echo "  restart            重启服务"
    echo "  logs               查看所有服务日志"
    echo "  logs [service]     查看特定服务日志"
    echo "  exec [service]     进入容器 (默认: app)"
    echo "  status, ps         显示服务状态"
    echo "  cleanup            清理所有资源"
    echo "  help               显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start           启动生产环境"
    echo "  $0 dev             启动开发环境"
    echo "  $0 logs app        查看应用日志"
    echo "  $0 exec db         进入数据库容器"
}

# 主函数
main() {
    print_header
    
    # 检查Docker
    check_docker
    
    # 解析命令行参数
    case "${1:-}" in
        start|up)
            start_production
            ;;
        dev)
            start_development
            ;;
        stop|down)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            if [ -n "${2:-}" ]; then
                show_service_logs $2
            else
                show_logs
            fi
            ;;
        exec)
            enter_container ${2:-app}
            ;;
        status|ps)
            show_status
            ;;
        cleanup)
            cleanup
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@" 