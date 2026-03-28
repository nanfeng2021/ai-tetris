#!/usr/bin/env python3
# 生产环境启动脚本 - 无 debug 模式
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from web.server import app

if __name__ == "__main__":
    print("=" * 60)
    print("🌐 AI Tetris Web Server - 生产模式")
    print("=" * 60)
    print("访问地址：http://localhost:5000")
    print("=" * 60)
    
    # 生产模式：关闭 debug 和 reloader
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)
