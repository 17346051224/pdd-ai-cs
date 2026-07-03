#!/bin/bash

# 拼多多AI售前客服系统 - 阿里云部署脚本

set -e

echo "========================================"
echo "  拼多多AI客服系统 - 部署脚本"
echo "========================================"

# 配置变量
PROJECT_DIR="/opt/pdd-ai-cs"
BACKUP_DIR="/opt/pdd-ai-cs-backup"
SERVICE_PORT=3000
API_PORT=8000

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装"
        exit 1
    fi
    
    log_info "Docker环境检查通过"
}

# 备份函数
backup() {
    if [ -d "$PROJECT_DIR" ]; then
        log_info "正在备份现有数据..."
        mkdir -p "$BACKUP_DIR"
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        
        if [ -f "$PROJECT_DIR/backend/data/pdd_cs.db" ]; then
            cp "$PROJECT_DIR/backend/data/pdd_cs.db" "$BACKUP_DIR/pdd_cs.db.$TIMESTAMP"
            log_info "数据库已备份"
        fi
        
        log_info "备份完成"
    fi
}

# 部署函数
deploy() {
    log_info "开始部署..."
    
    # 进入项目目录
    cd "$PROJECT_DIR"
    
    # 停止现有服务
    log_info "停止现有服务..."
    docker-compose down 2>/dev/null || true
    
    # 拉取最新代码（如使用git）
    # git pull origin main
    
    # 构建并启动
    log_info "构建Docker镜像..."
    docker-compose build --no-cache
    
    log_info "启动服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log_info "服务启动成功!"
    else
        log_error "服务启动失败，请检查日志"
        docker-compose logs
        exit 1
    fi
}

# 防火墙配置
config_firewall() {
    log_info "配置防火墙..."
    
    # 检查并开放端口
    if command -v ufw &> /dev/null; then
        ufw allow $SERVICE_PORT/tcp 2>/dev/null || true
        ufw allow $API_PORT/tcp 2>/dev/null || true
    fi
    
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=$SERVICE_PORT/tcp 2>/dev/null || true
        firewall-cmd --permanent --add-port=$API_PORT/tcp 2>/dev/null || true
        firewall-cmd --reload 2>/dev/null || true
    fi
    
    log_info "防火墙配置完成"
}

# 查看状态
show_status() {
    echo ""
    echo "========================================"
    echo "  服务状态"
    echo "========================================"
    docker-compose ps
    
    echo ""
    echo "========================================"
    echo "  访问地址"
    echo "========================================"
    echo "  前端: http://116.62.129.232:$SERVICE_PORT"
    echo "  API:  http://116.62.129.232:$API_PORT"
    echo "  Docs: http://116.62.129.232:$API_PORT/docs"
    echo ""
}

# 主菜单
main() {
    check_docker
    
    case "${1:-deploy}" in
        deploy)
            backup
            deploy
            config_firewall
            show_status
            ;;
        start)
            cd "$PROJECT_DIR"
            docker-compose start
            show_status
            ;;
        stop)
            cd "$PROJECT_DIR"
            docker-compose stop
            log_info "服务已停止"
            ;;
        restart)
            cd "$PROJECT_DIR"
            docker-compose restart
            show_status
            ;;
        logs)
            cd "$PROJECT_DIR"
            docker-compose logs -f
            ;;
        status)
            show_status
            ;;
        backup)
            backup
            ;;
        *)
            echo "用法: $0 {deploy|start|stop|restart|logs|status|backup}"
            echo ""
            echo "  deploy   - 部署/更新服务"
            echo "  start    - 启动服务"
            echo "  stop     - 停止服务"
            echo "  restart  - 重启服务"
            echo "  logs     - 查看日志"
            echo "  status   - 查看状态"
            echo "  backup   - 备份数据"
            exit 1
            ;;
    esac
}

main "$@"
