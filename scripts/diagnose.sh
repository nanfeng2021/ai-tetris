#!/bin/bash
# AI Tetris 诊断脚本

echo "🔍 AI Tetris 健康检查"
echo "===================="
echo ""

# 1. 检查 Python 依赖
echo "1️⃣ 检查 Python 依赖..."
cd /root/.openclaw/workspace/ai-tetris
source venv/bin/activate
python3 -c "import flask; import flask_cors; print('✅ Flask 和 Flask-CORS 已安装')" 2>/dev/null || echo "❌ 缺少依赖"

# 2. 检查后端导入
echo ""
echo "2️⃣ 检查后端模块..."
python3 -c "
import sys
sys.path.insert(0, 'src')
from board import GameBoard
from harness.monitors import Monitors
b = GameBoard(Monitors())
b.spawn_piece()
print('✅ 后端模块正常')
" 2>&1 | grep -E "✅|❌|Error"

# 3. 检查服务器进程
echo ""
echo "3️⃣ 检查服务器进程..."
if pgrep -f "web/server.py" > /dev/null; then
    PID=$(pgrep -f "web/server.py")
    echo "✅ 服务器运行中 (PID: $PID)"
else
    echo "❌ 服务器未运行"
fi

# 4. 检查 API 端点
echo ""
echo "4️⃣ 检查 API 端点..."
INIT_RESP=$(curl -s -X POST http://localhost:5000/api/init)
if echo "$INIT_RESP" | grep -q "success"; then
    echo "✅ /api/init 正常"
else
    echo "❌ /api/init 失败"
fi

STATE_RESP=$(curl -s http://localhost:5000/api/state)
if echo "$STATE_RESP" | grep -q "board"; then
    echo "✅ /api/state 正常"
else
    echo "❌ /api/state 失败"
fi

# 5. 检查 HTML 文件
echo ""
echo "5️⃣ 检查 HTML 文件..."
if [ -f "web/templates/index.html" ]; then
    LINES=$(wc -l < web/templates/index.html)
    echo "✅ index.html 存在 ($LINES 行)"
else
    echo "❌ index.html 不存在"
fi

# 6. 检查 JavaScript 语法
echo ""
echo "6️⃣ 检查 JavaScript 语法..."
node -e "
const fs = require('fs');
const html = fs.readFileSync('web/templates/index.html', 'utf8');
const match = html.match(/<script>([\s\S]*)<\/script>/);
if (match) {
    try {
        new Function(match[1]);
        console.log('✅ JavaScript 语法正常');
    } catch(e) {
        console.log('❌ JavaScript 错误:', e.message);
    }
}
" 2>&1

# 7. 检查 Git 状态
echo ""
echo "7️⃣ 检查 Git 状态..."
cd /root/.openclaw/workspace/ai-tetris
if git status --porcelain | grep -q "^ M"; then
    echo "⚠️  有未提交的修改"
    git status --porcelain | head -5
else
    echo "✅ Git 工作区干净"
fi

echo ""
echo "===================="
echo "📊 诊断完成！"
echo ""
echo "💡 如果页面没反应，请尝试:"
echo "   1. 硬刷新页面 (Ctrl+Shift+R)"
echo "   2. 清除浏览器缓存"
echo "   3. 打开浏览器控制台查看错误 (F12)"
echo "   4. 检查服务器日志：tail -f logs/web.log"
