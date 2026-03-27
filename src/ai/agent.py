"""
AI 决策引擎 - 基于启发式评估
使用 Harness Engineering 约束确保决策质量
"""
import sys
import os
from typing import List, Tuple, Optional
from dataclasses import dataclass
import time

sys.path.insert(0, os.path.dirname(__file__))

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from board import GameBoard
from pieces import Piece
from harness.guardrails import Guardrails
from harness.monitors import Monitors

@dataclass
class MoveEvaluation:
    """移动评估结果"""
    move: str
    score: float
    details: dict


class AIAgent:
    """AI 决策代理"""
    
    def __init__(self, board: GameBoard, monitor: Monitors = None):
        self.board = board
        self.monitor = monitor or Monitors()
        
        # 启发式权重
        self.weights = {
            'height': -1.0,      # 越低越好
            'holes': -5.0,       # 空洞越少越好
            'bumpiness': -0.5,   # 越平越好
            'lines': 2.0,        # 消除行数越多越好
            'complete_lines': 1.0  # 完整行奖励
        }
    
    def decide_move(self) -> str:
        """决定下一步行动"""
        if self.board.current_piece is None:
            return "down"
        
        start_time = time.time()
        
        # 搜索所有可能的位置和旋转
        best_move = self._search_best_move()
        
        decision_time = time.time() - start_time
        
        # Guardrail: AI 决策超时检查
        result = Guardrails.validate_ai_decision_time(decision_time)
        if not result.passed:
            self.monitor.record_guardrail_trigger('ai_timeout', 'warning')
            return "down"  # 超时默认下落
        
        return best_move
    
    def _search_best_move(self) -> str:
        """搜索最佳移动"""
        best_score = float('-inf')
        best_move = "down"
        
        piece = self.board.current_piece
        
        # 尝试所有旋转状态
        for rotation in range(4):
            # 尝试所有水平位置
            for x in range(self.board.width - piece.width + 1):
                # 模拟放置
                evaluation = self._evaluate_position(x, rotation)
                
                if evaluation > best_score:
                    best_score = evaluation
                    # 计算需要的移动
                    dx = x - piece.x
                    if dx < 0:
                        best_move = "left"
                    elif dx > 0:
                        best_move = "right"
                    else:
                        best_move = "down"
            
            # 准备下一次旋转
            piece.apply_rotation()
        
        return best_move
    
    def _evaluate_position(self, target_x: int, rotation: int) -> float:
        """评估指定位置的得分"""
        # 模拟放置后的面板状态
        simulated_board = self._simulate_placement(target_x, rotation)
        
        if simulated_board is None:
            return float('-inf')  # 非法位置
        
        # 计算启发式分数
        score = 0.0
        
        # 1. 堆叠高度（越低越好）
        height = self._calculate_height(simulated_board)
        score += self.weights['height'] * height
        
        # 2. 空洞数量（越少越好）
        holes = self._calculate_holes(simulated_board)
        score += self.weights['holes'] * holes
        
        # 3. 不平整度（越平越好）
        bumpiness = self._calculate_bumpiness(simulated_board)
        score += self.weights['bumpiness'] * bumpiness
        
        # 4. 可消除行数（越多越好）
        lines = self._calculate_clearable_lines(simulated_board)
        score += self.weights['lines'] * lines
        
        # 5. 完整行奖励
        complete = self._count_complete_lines(simulated_board)
        score += self.weights['complete_lines'] * complete
        
        return score
    
    def _simulate_placement(self, target_x: int, rotation: int) -> Optional[List[List[str]]]:
        """模拟方块放置后的面板"""
        # 深拷贝当前面板
        simulated = [row[:] for row in self.board.board]
        piece = self.board.current_piece
        
        # 应用旋转
        temp_shape = [row[:] for row in piece.shape]
        for _ in range(rotation):
            rows = len(temp_shape)
            cols = len(temp_shape[0])
            rotated = [[False for _ in range(rows)] for _ in range(cols)]
            for r in range(rows):
                for c in range(cols):
                    if temp_shape[r][c]:
                        rotated[c][rows - 1 - r] = True
            temp_shape = rotated
        
        # 找到最终 y 位置
        y = 0
        while True:
            # 检查是否可以继续下落
            can_drop = True
            
            for row_idx, row in enumerate(temp_shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        check_x = target_x + col_idx
                        check_y = y + row_idx + 1
                        
                        # 边界检查
                        if check_y >= self.board.height or check_y < 0:
                            can_drop = False
                            break
                        
                        # 碰撞检查
                        if 0 <= check_y < self.board.height and 0 <= check_x < self.board.width:
                            if simulated[check_y][check_x] is not None:
                                can_drop = False
                                break
                
                if not can_drop:
                    break
            
            if not can_drop:
                break
            
            y += 1
        
        # 检查放置是否合法
        for row_idx, row in enumerate(temp_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    place_x = target_x + col_idx
                    place_y = y + row_idx
                    
                    # 越界检查
                    if place_x < 0 or place_x >= self.board.width:
                        return None
                    if place_y < 0 or place_y >= self.board.height:
                        return None
                    
                    # 碰撞检查
                    if place_y >= 0 and simulated[place_y][place_x] is not None:
                        return None
        
        # 放置方块
        for row_idx, row in enumerate(temp_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    place_y = y + row_idx
                    if place_y >= 0:
                        simulated[place_y][target_x + col_idx] = 'simulated'
        
        return simulated
    
    def _calculate_height(self, board: List[List[str]]) -> int:
        """计算堆叠高度"""
        for y in range(self.board.height):
            if any(board[y][x] is not None for x in range(self.board.width)):
                return self.board.height - y
        return 0
    
    def _calculate_holes(self, board: List[List[str]]) -> int:
        """计算空洞数量（被方块覆盖的空格）"""
        holes = 0
        for x in range(self.board.width):
            found_block = False
            for y in range(self.board.height):
                if board[y][x] is not None:
                    found_block = True
                elif found_block and board[y][x] is None:
                    holes += 1
        return holes
    
    def _calculate_bumpiness(self, board: List[List[str]]) -> int:
        """计算表面不平整度"""
        heights = []
        for x in range(self.board.width):
            for y in range(self.board.height):
                if board[y][x] is not None:
                    heights.append(self.board.height - y)
                    break
            else:
                heights.append(0)
        
        bumpiness = sum(abs(heights[i] - heights[i+1]) for i in range(len(heights)-1))
        return bumpiness
    
    def _calculate_clearable_lines(self, board: List[List[str]]) -> int:
        """计算可消除的行数"""
        clearable = 0
        for y in range(self.board.height):
            if all(board[y][x] is not None for x in range(self.board.width)):
                clearable += 1
        return clearable
    
    def _count_complete_lines(self, board: List[List[str]]) -> int:
        """计算完整行数量"""
        return self._calculate_clearable_lines(board)


if __name__ == "__main__":
    # 测试代码
    print("🤖 测试 AI 决策引擎\n")
    
    from board import GameBoard
    from harness.monitors import Monitors
    
    monitor = Monitors(game_id="ai_test")
    board = GameBoard(monitor)
    board.spawn_piece()
    
    agent = AIAgent(board, monitor)
    
    print(f"当前方块：{board.current_piece.type.value}")
    print(f"面板尺寸：{board.width}x{board.height}")
    print()
    
    # 测试决策
    for i in range(5):
        start = time.time()
        move = agent.decide_move()
        duration = time.time() - start
        
        print(f"决策 {i+1}: {move} (耗时：{duration:.3f}s)")
    
    print("\n✅ AI 决策引擎正常！")
