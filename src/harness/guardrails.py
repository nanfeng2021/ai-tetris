"""
Harness Engineering 约束规则
定义游戏的所有边界和限制
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


class GuardrailType(Enum):
    BOUNDARY = "boundary_check"
    COLLISION = "collision_detection"
    GAME_STATE = "game_state_validation"
    AI_DECISION = "ai_decision_timeout"
    STUCK_DETECTION = "stuck_detection"


@dataclass
class GuardrailResult:
    passed: bool
    rule: GuardrailType
    message: str
    severity: str = "info"  # info/warning/critical


class Guardrails:
    """游戏约束规则集合"""

    @staticmethod
    def validate_boundary(
        x: int,
        y: int,
        piece_width: int,
        piece_height: int,
        board_width: int = 10,
        board_height: int = 20,
    ) -> GuardrailResult:
        """边界检查：方块不能穿墙"""
        if x < 0 or x + piece_width > board_width:
            return GuardrailResult(
                passed=False,
                rule=GuardrailType.BOUNDARY,
                message=f"水平越界：x={x}, width={piece_width}",
                severity="warning",
            )
        if y < 0 or y + piece_height > board_height:
            return GuardrailResult(
                passed=False,
                rule=GuardrailType.BOUNDARY,
                message=f"垂直越界：y={y}, height={piece_height}",
                severity="warning",
            )
        return GuardrailResult(passed=True, rule=GuardrailType.BOUNDARY, message="边界检查通过")

    @staticmethod
    def validate_collision(board: List[List[str]], piece, x: int, y: int) -> GuardrailResult:
        """碰撞检测：方块不能重叠"""
        for row_idx, row in enumerate(piece.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    board_x = x + col_idx
                    board_y = y + row_idx

                    if 0 <= board_y < len(board) and 0 <= board_x < len(board[0]):
                        if board[board_y][board_x]:
                            return GuardrailResult(
                                passed=False,
                                rule=GuardrailType.COLLISION,
                                message=f"碰撞检测失败：({board_x}, {board_y})",
                                severity="warning",
                            )

        return GuardrailResult(passed=True, rule=GuardrailType.COLLISION, message="碰撞检测通过")

    @staticmethod
    def validate_game_state(score: int, lines: int, level: int) -> GuardrailResult:
        """游戏状态验证：数据一致性"""
        if score < 0:
            return GuardrailResult(
                passed=False,
                rule=GuardrailType.GAME_STATE,
                message=f"分数异常：{score}",
                severity="critical",
            )
        if lines < 0:
            return GuardrailResult(
                passed=False,
                rule=GuardrailType.GAME_STATE,
                message=f"行数异常：{lines}",
                severity="critical",
            )
        if level < 1:
            return GuardrailResult(
                passed=False,
                rule=GuardrailType.GAME_STATE,
                message=f"等级异常：{level}",
                severity="critical",
            )

        return GuardrailResult(passed=True, rule=GuardrailType.GAME_STATE, message="游戏状态正常")

    @staticmethod
    def validate_ai_decision_time(decision_time: float, timeout: float = 2.0) -> GuardrailResult:
        """AI 决策超时检查"""
        if decision_time > timeout:
            return GuardrailResult(
                passed=False,
                rule=GuardrailType.AI_DECISION,
                message=f"AI 决策超时：{decision_time:.2f}s > {timeout}s",
                severity="warning",
            )
        return GuardrailResult(
            passed=True,
            rule=GuardrailType.AI_DECISION,
            message=f"AI 决策耗时：{decision_time:.2f}s",
        )

    @staticmethod
    def detect_stuck(
        last_move_time: float, current_time: float, timeout: float = 5.0
    ) -> GuardrailResult:
        """卡死检测：超过 5 秒无有效移动"""
        elapsed = current_time - last_move_time
        if elapsed > timeout:
            return GuardrailResult(
                passed=False,
                rule=GuardrailType.STUCK_DETECTION,
                message=f"检测到卡死：{elapsed:.2f}s 无移动",
                severity="critical",
            )
        return GuardrailResult(
            passed=True, rule=GuardrailType.STUCK_DETECTION, message="游戏正常进行"
        )


# 快捷函数
def run_all_guardrails(**kwargs) -> List[GuardrailResult]:
    """运行所有相关的 Guardrail 检查"""
    results = []

    # 根据传入参数决定运行哪些检查
    if "x" in kwargs and "y" in kwargs:
        results.append(
            Guardrails.validate_boundary(
                kwargs["x"],
                kwargs["y"],
                kwargs.get("piece_width", 1),
                kwargs.get("piece_height", 1),
            )
        )

    if "board" in kwargs and "piece" in kwargs:
        results.append(
            Guardrails.validate_collision(
                kwargs["board"], kwargs["piece"], kwargs["x"], kwargs["y"]
            )
        )

    if "score" in kwargs:
        results.append(
            Guardrails.validate_game_state(
                kwargs.get("score", 0), kwargs.get("lines", 0), kwargs.get("level", 1)
            )
        )

    return results
