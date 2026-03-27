"""
Web 服务器 - Flask + HTML5 Canvas
提供浏览器可玩的 Web 版本
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from board import GameBoard
from harness.monitors import Monitors

app = Flask(__name__)
CORS(app)

# 全局游戏实例
game_state = {
    'board': None,
    'monitor': None,
    'running': False
}


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/init', methods=['POST'])
def init_game():
    """初始化游戏"""
    monitor = Monitors(game_id="web_game")
    board = GameBoard(monitor)
    board.reset()
    board.spawn_piece()
    
    game_state['board'] = board
    game_state['monitor'] = monitor
    game_state['running'] = True
    
    monitor.start_game(mode='web')
    
    return jsonify({
        'success': True,
        'message': 'Game initialized'
    })


@app.route('/api/state', methods=['GET'])
def get_state():
    """获取游戏状态"""
    if not game_state['board']:
        return jsonify({'error': 'Game not initialized'}), 400
    
    board = game_state['board']
    
    # 序列化面板
    board_data = []
    for row in board.board:
        board_data.append([cell if cell else None for cell in row])
    
    current_piece = None
    if board.current_piece:
        current_piece = {
            'type': board.current_piece.type.value,
            'shape': board.current_piece.shape,
            'x': board.current_piece.x,
            'y': board.current_piece.y,
            'color': board.current_piece.color
        }
    
    next_piece = None
    if board.next_piece:
        next_piece = {
            'type': board.next_piece.type.value,
            'shape': board.next_piece.shape,
            'color': board.next_piece.color
        }
    
    return jsonify({
        'board': board_data,
        'score': board.score,
        'lines': board.lines,
        'level': board.level,
        'game_over': board.game_over,
        'current_piece': current_piece,
        'next_piece': next_piece
    })


@app.route('/api/move', methods=['POST'])
def move():
    """执行移动"""
    if not game_state['board'] or not game_state['running']:
        return jsonify({'error': 'Game not running'}), 400
    
    data = request.json
    action = data.get('action')
    
    board = game_state['board']
    
    if action == 'left':
        success = board.move_piece(-1, 0)
    elif action == 'right':
        success = board.move_piece(1, 0)
    elif action == 'down':
        success = board.move_piece(0, 1)
    elif action == 'rotate':
        success = board.rotate_piece()
    elif action == 'drop':
        board.hard_drop()
        board.lock_piece()
        success = True
    else:
        return jsonify({'error': 'Invalid action'}), 400
    
    # 检查是否需要锁定
    if not board.move_piece(0, 1):
        board.lock_piece()
    
    return jsonify({
        'success': success,
        'state': get_state().json
    })


@app.route('/api/reset', methods=['POST'])
def reset():
    """重置游戏"""
    if game_state['board']:
        game_state['board'].reset()
        game_state['board'].spawn_piece()
        game_state['running'] = True
    
    return jsonify({'success': True})


@app.route('/metrics')
def metrics():
    """Prometheus 格式指标"""
    if game_state['monitor']:
        return game_state['monitor'].get_metrics(), 200, {'Content-Type': 'text/plain'}
    return '', 404


if __name__ == "__main__":
    print("=" * 60)
    print("🌐 AI Tetris Web Server")
    print("=" * 60)
    print("访问地址：http://localhost:5000")
    print("API 文档：http://localhost:5000/docs")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
