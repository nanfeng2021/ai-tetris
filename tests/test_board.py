"""
测试游戏面板核心逻辑
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from board import GameBoard, BOARD_WIDTH, BOARD_HEIGHT
from pieces import PieceType
from harness.monitors import Monitors


class TestGameBoard:
    """游戏面板测试"""
    
    def setup_method(self):
        """每个测试前初始化"""
        self.monitor = Monitors(game_id="test")
        self.board = GameBoard(self.monitor)
    
    def test_reset_board(self):
        """测试重置面板"""
        # 先进行一些操作
        self.board.spawn_piece()
        self.board.move_piece(0, 5)
        
        # 重置
        self.board.reset()
        
        # 验证
        assert all(all(cell is None for cell in row) for row in self.board.board)
        assert self.board.score == 0
        assert self.board.lines == 0
        assert self.board.level == 1
        assert not self.board.game_over
    
    def test_spawn_piece(self):
        """测试生成方块"""
        piece = self.board.spawn_piece()
        
        assert piece is not None
        assert piece.type in PieceType
        assert 0 <= piece.x < BOARD_WIDTH
        assert piece.y >= 0
    
    def test_move_piece_left(self):
        """测试左移"""
        self.board.spawn_piece()
        original_x = self.board.current_piece.x
        
        success = self.board.move_piece(-1, 0)
        
        if original_x > 0:
            assert success
            assert self.board.current_piece.x == original_x - 1
        else:
            assert not success
    
    def test_move_piece_right(self):
        """测试右移"""
        self.board.spawn_piece()
        original_x = self.board.current_piece.x
        
        success = self.board.move_piece(1, 0)
        
        if original_x < BOARD_WIDTH - self.board.current_piece.width:
            assert success
            assert self.board.current_piece.x == original_x + 1
        else:
            assert not success
    
    def test_move_piece_down(self):
        """测试下落"""
        self.board.spawn_piece()
        original_y = self.board.current_piece.y
        
        success = self.board.move_piece(0, 1)
        
        assert success
        assert self.board.current_piece.y == original_y + 1
    
    def test_rotate_piece(self):
        """测试旋转"""
        self.board.spawn_piece()
        original_shape = [row[:] for row in self.board.current_piece.shape]
        
        success = self.board.rotate_piece()
        
        # 大多数情况下应该能旋转（除非在边界）
        if success:
            assert self.board.current_piece.shape != original_shape
    
    def test_hard_drop(self):
        """测试直接掉落"""
        self.board.spawn_piece()
        original_y = self.board.current_piece.y
        
        distance = self.board.hard_drop()
        
        assert distance > 0
        assert self.board.current_piece.y == original_y + distance
    
    def test_lock_piece(self):
        """测试锁定方块"""
        self.board.spawn_piece()
        self.board.hard_drop()
        
        piece_type = self.board.current_piece.type.value
        self.board.lock_piece()
        
        # 验证方块已固定到面板
        locked = False
        for y, row in enumerate(self.board.board):
            for x, cell in enumerate(row):
                if cell == piece_type:
                    locked = True
                    break
        
        assert locked
        assert self.board.current_piece is None  # 锁定后当前方块应为 None
    
    def test_clear_lines(self):
        """测试消除行"""
        # 手动填充一行
        for x in range(BOARD_WIDTH):
            self.board.board[BOARD_HEIGHT - 1][x] = 'I'
        
        lines_before = self.board.lines
        self.board.spawn_piece()
        self.board.hard_drop()
        self.board.lock_piece()
        
        assert self.board.lines > lines_before
    
    def test_game_over_by_stack(self):
        """测试堆叠导致游戏结束"""
        # 填充顶部几行
        for y in range(3):
            for x in range(BOARD_WIDTH):
                self.board.board[y][x] = 'I'
        
        self.board.spawn_piece()
        
        # 如果出生点被占，应该游戏结束
        if not self.board._is_valid_position(self.board.current_piece, 0, 0):
            assert self.board.game_over
    
    def test_score_update(self):
        """测试分数更新"""
        score_before = self.board.score
        
        # 填充一行并消除
        for x in range(BOARD_WIDTH):
            self.board.board[BOARD_HEIGHT - 1][x] = 'I'
        
        self.board.spawn_piece()
        self.board.hard_drop()
        self.board.lock_piece()
        
        assert self.board.score > score_before
    
    def test_level_up(self):
        """测试升级"""
        # 模拟消除 10 行
        initial_level = self.board.level
        
        for _ in range(10):
            for x in range(BOARD_WIDTH):
                self.board.board[BOARD_HEIGHT - 1][x] = 'I'
            
            self.board.spawn_piece()
            self.board.hard_drop()
            self.board.lock_piece()
        
        assert self.board.level > initial_level


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
