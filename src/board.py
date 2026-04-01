"""
游戏面板 - 带 Harness Engineering 验证
负责管理方块、碰撞检测、行消除等核心逻辑
"""

import os
import sys
from dataclasses import dataclass
from typing import List, Optional

# type: ignore[E402]
sys.path.insert(0, os.path.dirname(__file__))
from harness.guardrails import Guardrails
from harness.monitors import Monitors
from harness.validators import Validators
from pieces import Piece

# 标准面板尺寸
BOARD_WIDTH = 10
BOARD_HEIGHT = 20


@dataclass
class BoardState:
    """面板状态快照"""

    board: List[List[Optional[Piece]]]
    score: int
    lines: int
    level: int
    game_over: bool
    current_piece: Optional[Piece] = None


class GameBoard:
    """游戏面板类"""

    def __init__(self, monitor: Monitors = None):
        self.width = BOARD_WIDTH
        self.height = BOARD_HEIGHT
        self.board = [[None for _ in range(self.width)] for _ in range(self.height)]

        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False

        self.current_piece: Optional[Piece] = None
        self.next_piece: Optional[Piece] = None

        self.monitor = monitor or Monitors()

        # 从 harness 导入验证器
        from pieces import PieceFactory

        self.piece_factory = PieceFactory()

    def reset(self):
        """重置游戏"""
        self.board = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.current_piece = None
        self.next_piece = None
        self.piece_factory.reset()

    def spawn_piece(self) -> Piece:
        """生成新方块"""
        if self.next_piece is None:
            self.next_piece = self.piece_factory.get_next_piece()

        self.current_piece = self.next_piece
        self.next_piece = self.piece_factory.get_next_piece()

        # 验证生成的方块
        result = Validators.validate_piece_shape(self.current_piece.shape)
        if result.status.value == "failed":
            raise ValueError(f"生成的方块形状无效：{result.message}")

        # 检查是否立即游戏结束（出生点被占）
        if not self._is_valid_position(self.current_piece, 0, 0):
            self.game_over = True
            self.monitor.record_guardrail_trigger("spawn_collision", "critical")
            return None

        return self.current_piece

    def _is_valid_position(self, piece: Piece, offset_x: int, offset_y: int) -> bool:
        """检查方块在指定位置是否合法（带 Guardrail 验证）"""
        new_x = piece.x + offset_x
        new_y = piece.y + offset_y

        # Guardrail: 边界检查
        boundary_result = Guardrails.validate_boundary(
            new_x, new_y, piece.width, piece.height, self.width, self.height
        )
        if not boundary_result.passed:
            self.monitor.record_guardrail_trigger("boundary_check", "warning")
            return False

        # Guardrail: 碰撞检测
        collision_result = Guardrails.validate_collision(self.board, piece, new_x, new_y)
        if not collision_result.passed:
            self.monitor.record_guardrail_trigger("collision_detection", "warning")
            return False

        return True

    def move_piece(self, dx: int, dy: int) -> bool:
        """移动当前方块"""
        if self.current_piece is None or self.game_over:
            return False

        if self._is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy

            # 验证移动序列
            move_type = "down" if dy > 0 else ("left" if dx < 0 else "right")
            self.monitor.record_guardrail_trigger(f"move_{move_type}", "info")

            return True

        return False

    def rotate_piece(self) -> bool:
        """旋转当前方块"""
        if self.current_piece is None or self.game_over:
            return False

        # 尝试旋转
        original_shape = [row[:] for row in self.current_piece.shape]
        self.current_piece.apply_rotation()

        # 验证旋转后的位置
        if self._is_valid_position(self.current_piece, 0, 0):
            self.monitor.record_guardrail_trigger("rotate", "info")
            return True

        # 旋转失败，恢复原状
        self.current_piece.shape = original_shape
        self.monitor.record_guardrail_trigger("rotate_blocked", "info")
        return False

    def hard_drop(self) -> int:
        """硬降落（直接到底）"""
        if self.current_piece is None or self.game_over:
            return 0

        drop_distance = 0
        while self.move_piece(0, 1):
            drop_distance += 1

        self.monitor.record_guardrail_trigger("hard_drop", "info")
        return drop_distance

    def lock_piece(self):
        """锁定当前方块到面板"""
        if self.current_piece is None:
            return

        # 将方块固定到面板
        for cell_x, cell_y in self.current_piece.get_cells():
            if 0 <= cell_y < self.height and 0 <= cell_x < self.width:
                self.board[cell_y][cell_x] = self.current_piece.type.value

        # 验证面板状态
        result = Validators.validate_board_dimensions(self.board)
        if result.status.value == "failed":
            raise ValueError(f"面板状态异常：{result.message}")

        # 清除当前方块
        self.current_piece = None

        # 检查并消除完整的行
        lines_cleared = self._clear_lines()

        # 更新分数
        if lines_cleared > 0:
            self._update_score(lines_cleared)

        # 生成新方块（如果游戏未结束）
        if not self.game_over:
            new_piece = self.spawn_piece()
            if new_piece is None:
                # 出生点被占，游戏结束
                self.game_over = True

    def _clear_lines(self) -> int:
        """消除完整的行"""
        lines_to_clear = []

        for y in range(self.height):
            if all(self.board[y][x] is not None for x in range(self.width)):
                lines_to_clear.append(y)

        if not lines_to_clear:
            return 0

        # 消除行
        for y in lines_to_clear:
            del self.board[y]
            self.board.insert(0, [None for _ in range(self.width)])

        # 更新统计
        self.lines += len(lines_to_clear)

        # 更新等级（每 10 行升一级）
        self.level = (self.lines // 10) + 1

        # 监控指标
        self.monitor.update_lines(self.lines, self.level)
        self.monitor.record_guardrail_trigger("line_clear", "info")

        return len(lines_to_clear)

    def _update_score(self, lines_cleared: int):
        """更新分数"""
        # 经典计分规则
        score_table = {
            1: 40 * self.level,
            2: 100 * self.level,
            3: 300 * self.level,
            4: 1200 * self.level,  # Tetris!
        }

        points = score_table.get(lines_cleared, 0)
        self.score += points

        # 验证游戏状态
        result = Guardrails.validate_game_state(self.score, self.lines, self.level)
        if not result.passed:
            self.monitor.record_validation_failure("game_state")
            raise ValueError(f"游戏状态异常：{result.message}")

        # 更新监控
        self.monitor.update_score(self.score)
        self.monitor.update_level(self.level)

    def get_state(self) -> BoardState:
        """获取面板状态快照"""
        return BoardState(
            board=self.board,
            score=self.score,
            lines=self.lines,
            level=self.level,
            game_over=self.game_over,
            current_piece=self.current_piece,
        )

    def render_ascii(self) -> str:
        """ASCII 渲染（用于终端显示）"""
        lines = []

        # 顶部边框
        lines.append("┌" + "─" * self.width * 2 + "┐")

        # 游戏区域
        for y in range(self.height):
            line = "│"
            for x in range(self.width):
                if self.current_piece and (x, y) in self.current_piece.get_cells():
                    # 当前方块
                    line += "██"
                elif self.board[y][x]:
                    # 已锁定的方块
                    line += "[]"
                else:
                    # 空白
                    line += "  "
            line += "│"
            lines.append(line)

        # 底部边框
        lines.append("└" + "─" * self.width * 2 + "┘")

        # 信息面板
        lines.append(f"Score: {self.score}")
        lines.append(f"Lines: {self.lines}")
        lines.append(f"Level: {self.level}")

        if self.game_over:
            lines.append("GAME OVER!")

        return "\n".join(lines)


if __name__ == "__main__":
    # 测试代码
    print("🎮 测试游戏面板系统\n")

    monitor = Monitors(game_id="test_001")
    board = GameBoard(monitor)

    print("初始面板:")
    print(board.render_ascii())
    print()

    # 生成方块
    piece = board.spawn_piece()
    print(f"生成方块：{piece.type.value} - 颜色：{piece.color}")
    print()

    print("移动后方块:")
    board.move_piece(0, 5)
    print(board.render_ascii())
    print()

    print("✅ 游戏面板系统正常！")
