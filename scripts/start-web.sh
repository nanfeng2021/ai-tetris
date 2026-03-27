#!/bin/bash
# AI Tetris Web 服务管理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.web_server.pid"
LOG_FILE="$SCRIPT_DIR/logs/web_server.log"

mkdir -p "$SCRIPT_DIR/logs"

start() {
    if [ -f "$PID_FILE" ]; then
        echo "⚠️  服务已在运行 (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    echo "🚀 启动 Web 服务器..."
    cd "$SCRIPT_DIR"
    nohup ./venv/bin/python web/server.py > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 3
    
    if curl -s http://localhost:5000/api/state > /dev/null; then
        echo "✅ Web 服务器启动成功 (PID: $(cat $PID_FILE))"
        echo "📝 日志：$LOG_FILE"
    else
        echo "❌ 启动失败，查看日志：$LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "⚠️  服务未运行"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    echo "🛑 停止服务 (PID: $PID)..."
    kill $PID 2>/dev/null
    rm -f "$PID_FILE"
    sleep 2
    echo "✅ 服务已停止"
}

restart() {
    stop
    sleep 2
    start
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ 服务运行中 (PID: $PID)"
            echo "📊 资源使用:"
            ps -p $PID -o pid,pcpu,pmem,etime,cmd
            return 0
        else
            echo "⚠️  进程不存在，清理 PID 文件"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo "❌ 服务未运行"
        return 1
    fi
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -50 "$LOG_FILE"
    else
        echo "📝 日志文件不存在"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "用法：$0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
