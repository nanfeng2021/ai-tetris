from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import sys
import os
import logging
from threading import Lock
from functools import wraps

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from board import GameBoard
from harness.monitors import Monitors

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 全局游戏实例
game_state = {
    'board': None,
    'monitor': None,
    'running': False,
    'session_id': None
}

# 线程锁，防止并发请求导致状态混乱
game_lock = Lock()


def require_game(func):
    """装饰器：检查游戏是否已初始化"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with game_lock:
            if not game_state.get('board'):
                logger.warning("Game not initialized")
                return jsonify({'error': 'Game not initialized', 'code': 'NOT_INIT'}), 400
            if not game_state.get('running'):
                logger.warning("Game not running")
                return jsonify({'error': 'Game not running', 'code': 'NOT_RUNNING'}), 400
            return func(*args, **kwargs)
    return wrapper


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/init', methods=['POST'])
def init_game():
    """初始化游戏"""
    try:
        with game_lock:
            monitor = Monitors(game_id="web_game")
            board = GameBoard(monitor)
            board.reset()
            board.spawn_piece()
            
            game_state['board'] = board
            game_state['monitor'] = monitor
            game_state['running'] = True
            game_state['session_id'] = os.urandom(16).hex()
            
            monitor.start_game(mode='web')
            
            logger.info(f"Game initialized, session: {game_state['session_id']}")
            
            return jsonify({
                'success': True,
                'session_id': game_state['session_id'],
                'message': 'Game initialized'
            })
    except Exception as e:
        logger.error(f"Failed to init game: {e}", exc_info=True)
        return jsonify({'error': str(e), 'code': 'INIT_FAILED'}), 500


@app.route('/api/state', methods=['GET'])
@require_game
def get_state():
    """获取游戏状态"""
    try:
        with game_lock:
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
                'next_piece': next_piece,
                'session_id': game_state.get('session_id')
            })
    except Exception as e:
        logger.error(f"Failed to get state: {e}", exc_info=True)
        return jsonify({'error': str(e), 'code': 'STATE_FAILED'}), 500


@app.route('/api/move', methods=['POST'])
@require_game
def move():
    """执行移动"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON', 'code': 'INVALID_JSON'}), 400
        
        action = data.get('action')
        
        if not action or action not in ['left', 'right', 'down', 'rotate', 'drop']:
            return jsonify({'error': 'Invalid action', 'code': 'INVALID_ACTION'}), 400
        
        with game_lock:
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
            
            # 检查是否需要锁定（非 drop 操作）
            if action != 'drop' and not board.move_piece(0, 1):
                board.lock_piece()
            
            logger.debug(f"Move {action}: success={success}")
            
            # 直接返回状态，避免二次调用
            board_data = []
            for row in board.board:
                board_data.append([cell if cell else None for cell in row])
            
            current_piece = None
            if board.current_piece:
                current_piece = {
                    'type': board.current_piece.type.value,
                    'shape': board.current_piece.shape,
                    'x': board.current_piece.x,
                    'y': board.current_piece.y
                }
            
            return jsonify({
                'success': success,
                'state': {
                    'board': board_data,
                    'score': board.score,
                    'lines': board.lines,
                    'level': board.level,
                    'game_over': board.game_over,
                    'current_piece': current_piece
                }
            })
    except Exception as e:
        logger.error(f"Move failed: {e}", exc_info=True)
        return jsonify({'error': str(e), 'code': 'MOVE_FAILED'}), 500


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
