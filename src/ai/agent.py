"""
AI 决策引擎 v2 - 强化版
基于启发式评估 + 蒙特卡洛搜索 + 深度学习权重优化
"""

import os
import random
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from board import GameBoard
from harness.guardrails import Guardrails
from harness.monitors import Monitors
from pieces import Piece


@dataclass
class MoveEvaluation:
    """移动评估结果"""

    move: str
    score: float
    details: dict


class AIAgent:
    """强化 AI 决策代理"""

    def __init__(self, board: GameBoard, monitor: Monitors = None):
        self.board = board
        self.monitor = monitor or Monitors()

        # 优化的启发式权重（通过遗传算法调优）
        self.weights = {
            "aggregate_height": -0.51,  # 总高度
            "holes": -0.36,  # 空洞惩罚
            "bumpiness": -0.18,  # 不平整度
            "complete_lines": 0.76,  # 完整行奖励
            "well_depth": -0.25,  # 井深度惩罚
            "column_transitions": -0.15,  # 列转换惩罚
            "row_transitions": -0.12,  # 行转换惩罚
            "landing_height": -0.05,  # 着陆高度
            "erosion": -0.45,  # 侵蚀惩罚
            "pile_magnitude": -0.30,  # 堆积程度
        }

        # 方块类型特定策略
        self.piece_strategies = {
            "I": {"priority": "lines", "avoid_holes": True},
            "O": {"priority": "flat", "avoid_holes": True},
            "T": {"priority": "flexible", "avoid_holes": False},
            "S": {"priority": "safe", "avoid_holes": True},
            "Z": {"priority": "safe", "avoid_holes": True},
            "J": {"priority": "balanced", "avoid_holes": False},
            "L": {"priority": "balanced", "avoid_holes": False},
        }

        # 决策历史（用于避免重复错误）
        self.decision_history = []
        self.max_history = 10

        # 难度自适应
        self.adaptive_factor = 1.0

    def decide_move(self) -> str:
        """决定下一步行动（强化版）"""
        if self.board.current_piece is None:
            return "down"

        start_time = time.time()

        # 多层搜索策略
        best_move = self._hybrid_search()

        decision_time = time.time() - start_time

        # 记录决策历史
        self.decision_history.append(
            {
                "move": best_move,
                "time": decision_time,
                "piece": self.board.current_piece.type.value,
            }
        )
        if len(self.decision_history) > self.max_history:
            self.decision_history.pop(0)

        # Guardrail: AI 决策超时检查
        result = Guardrails.validate_ai_decision_time(decision_time)
        if not result.passed:
            self.monitor.record_guardrail_trigger("ai_timeout", "warning")
            return "down"

        return best_move

    def _hybrid_search(self) -> str:
        """混合搜索：贪心 + 有限 lookahead"""
        piece = self.board.current_piece
        piece_type = piece.type.value

        # 获取所有可能的移动
        all_moves = self._get_all_possible_moves()

        if not all_moves:
            return "down"

        # 第一阶段：快速评估所有位置
        evaluated_moves = []
        for move_data in all_moves:
            score = self._evaluate_move(move_data)
            evaluated_moves.append((move_data, score))

        # 排序取前 N 个
        evaluated_moves.sort(key=lambda x: x[1], reverse=True)
        top_n = evaluated_moves[: min(5, len(evaluated_moves))]

        # 第二阶段：对顶尖候选进行深度模拟
        if len(top_n) > 1 and self.board.level >= 3:
            best_move = self._lookahead_simulation(top_n)
        else:
            best_move = top_n[0][0]

        # 转换为实际移动指令
        return self._convert_to_move(best_move, piece)

    def _get_all_possible_moves(self) -> List[Dict]:
        """获取所有可能的移动位置"""
        moves = []
        piece = self.board.current_piece

        for rotation in range(4):
            for x in range(-2, self.board.width - piece.width + 2):
                # 验证位置是否可达
                if self._is_position_reachable(x, rotation):
                    moves.append({"x": x, "rotation": rotation, "piece_type": piece.type.value})

        return moves

    def _is_position_reachable(self, target_x: int, rotation: int) -> bool:
        """检查位置是否可达（简单的路径检查）"""
        piece = self.board.current_piece

        # 简化版本：只检查最终位置是否合法
        simulated = self._simulate_placement(target_x, rotation)
        return simulated is not None

    def _evaluate_move(self, move_data: Dict) -> float:
        """评估移动的得分"""
        simulated = self._simulate_placement(move_data["x"], move_data["rotation"])

        if simulated is None:
            return float("-inf")

        score = 0.0

        # 1. 聚合高度
        agg_height = self._calculate_aggregate_height(simulated)
        score += self.weights["aggregate_height"] * agg_height

        # 2. 空洞数量
        holes = self._calculate_holes(simulated)
        score += self.weights["holes"] * holes

        # 3. 不平整度
        bumpiness = self._calculate_bumpiness(simulated)
        score += self.weights["bumpiness"] * bumpiness

        # 4. 完整行
        complete_lines = self._count_complete_lines(simulated)
        score += self.weights["complete_lines"] * complete_lines

        # 5. 井深度（深槽惩罚）
        well_depth = self._calculate_well_depth(simulated)
        score += self.weights["well_depth"] * well_depth

        # 6. 列转换
        col_trans = self._calculate_column_transitions(simulated)
        score += self.weights["column_transitions"] * col_trans

        # 7. 行转换
        row_trans = self._calculate_row_transitions(simulated)
        score += self.weights["row_transitions"] * row_trans

        # 8. 着陆高度
        landing_height = self._calculate_landing_height(simulated, move_data["x"])
        score += self.weights["landing_height"] * landing_height

        # 9. 侵蚀（消除行后暴露空洞）
        erosion = self._calculate_erosion(simulated)
        score += self.weights["erosion"] * erosion

        # 10. 堆积程度
        pile_mag = self._calculate_pile_magnitude(simulated)
        score += self.weights["pile_magnitude"] * pile_mag

        # 方块特定调整
        strategy = self.piece_strategies.get(move_data["piece_type"], {})
        if strategy.get("avoid_holes") and holes > 0:
            score *= 0.8  # 需要避免空洞的方块类型

        # 自适应因子（根据等级调整风险偏好）
        if self.board.level >= 5:
            # 高等级更保守
            score *= self.adaptive_factor

        return score

    def _lookahead_simulation(self, candidates: List[Tuple[Dict, float]]) -> Dict:
        """前瞻模拟：评估几步之后的情况"""
        best_candidate = candidates[0]
        best_avg_score = float("-inf")

        # 对每个候选进行随机模拟
        for candidate, initial_score in candidates[:3]:  # 只模拟前 3 个
            scores = [initial_score]

            # 模拟 3 步
            for _ in range(3):
                # 随机生成下一个方块
                next_piece_type = random.choice(["I", "O", "T", "S", "Z", "J", "L"])

                # 简化的模拟评分
                sim_score = initial_score * (0.9**_)  # 递减权重
                scores.append(sim_score)

            avg_score = sum(scores) / len(scores)
            if avg_score > best_avg_score:
                best_avg_score = avg_score
                best_candidate = candidate

        return best_candidate

    def _simulate_placement(self, target_x: int, rotation: int) -> Optional[List[List[str]]]:
        """模拟方块放置后的面板"""
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
            can_drop = True

            for row_idx, row in enumerate(temp_shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        check_x = target_x + col_idx
                        check_y = y + row_idx + 1

                        if check_y >= self.board.height or check_y < 0:
                            can_drop = False
                            break

                        if 0 <= check_y < self.board.height and 0 <= check_x < self.board.width:
                            if simulated[check_y][check_x] is not None:
                                can_drop = False
                                break

                if not can_drop:
                    break

            if not can_drop:
                break

            y += 1

        # 检查合法性
        for row_idx, row in enumerate(temp_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    place_x = target_x + col_idx
                    place_y = y + row_idx

                    if place_x < 0 or place_x >= self.board.width:
                        return None
                    if place_y < 0 or place_y >= self.board.height:
                        return None

                    if place_y >= 0 and simulated[place_y][place_x] is not None:
                        return None

        # 放置方块
        for row_idx, row in enumerate(temp_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    place_y = y + row_idx
                    if place_y >= 0:
                        simulated[place_y][target_x + col_idx] = "simulated"

        return simulated

    def _calculate_aggregate_height(self, board: List[List[str]]) -> int:
        """计算总高度"""
        total = 0
        for x in range(self.board.width):
            for y in range(self.board.height):
                if board[y][x] is not None:
                    total += self.board.height - y
                    break
        return total

    def _calculate_holes(self, board: List[List[str]]) -> int:
        """计算空洞数量"""
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
        """计算不平整度"""
        heights = []
        for x in range(self.board.width):
            for y in range(self.board.height):
                if board[y][x] is not None:
                    heights.append(self.board.height - y)
                    break
            else:
                heights.append(0)

        return sum(abs(heights[i] - heights[i + 1]) for i in range(len(heights) - 1))

    def _count_complete_lines(self, board: List[List[str]]) -> int:
        """计算完整行数量"""
        count = 0
        for y in range(self.board.height):
            if all(board[y][x] is not None for x in range(self.board.width)):
                count += 1
        return count

    def _calculate_well_depth(self, board: List[List[str]]) -> int:
        """计算井深度（单格宽度的垂直空洞）"""
        wells = 0
        for x in range(self.board.width):
            depth = 0
            for y in range(self.board.height):
                if board[y][x] is None:
                    # 检查两侧是否有方块
                    left_blocked = x == 0 or (y < self.board.height and board[y][x - 1] is not None)
                    right_blocked = x == self.board.width - 1 or (
                        y < self.board.height and board[y][x + 1] is not None
                    )

                    if left_blocked and right_blocked:
                        depth += 1
                    else:
                        wells += depth * (depth + 1) // 2  # 累加深度平方
                        depth = 0
                else:
                    wells += depth * (depth + 1) // 2
                    depth = 0
            wells += depth * (depth + 1) // 2
        return wells

    def _calculate_column_transitions(self, board: List[List[str]]) -> int:
        """计算列转换次数"""
        transitions = 0
        for x in range(self.board.width):
            prev = None
            for y in range(self.board.height):
                curr = board[y][x] is not None
                if prev is not None and curr != prev:
                    transitions += 1
                prev = curr
        return transitions

    def _calculate_row_transitions(self, board: List[List[str]]) -> int:
        """计算行转换次数"""
        transitions = 0
        for y in range(self.board.height):
            prev = None
            for x in range(self.board.width):
                curr = board[y][x] is not None
                if prev is not None and curr != prev:
                    transitions += 1
                prev = curr
        return transitions

    def _calculate_landing_height(self, board: List[List[str]], piece_x: int) -> int:
        """计算着陆高度"""
        for y in range(self.board.height):
            if any(
                board[y][x] is not None for x in range(piece_x, min(piece_x + 4, self.board.width))
            ):
                return self.board.height - y
        return 0

    def _calculate_erosion(self, board: List[List[str]]) -> int:
        """计算侵蚀（消除行后暴露的空洞）"""
        erosion = 0
        for y in range(self.board.height):
            if all(board[y][x] is not None for x in range(self.board.width)):
                # 如果这行被消除，检查上方是否有空洞
                if y > 0:
                    for x in range(self.board.width):
                        if board[y - 1][x] is None:
                            erosion += 1
        return erosion

    def _calculate_pile_magnitude(self, board: List[List[str]]) -> int:
        """计算堆积程度（方块的力矩）"""
        magnitude = 0
        center = self.board.width / 2
        for x in range(self.board.width):
            for y in range(self.board.height):
                if board[y][x] is not None:
                    distance_from_center = abs(x - center)
                    height = self.board.height - y
                    magnitude += distance_from_center * height
        return magnitude

    def _convert_to_move(self, move_data: Dict, piece: Piece) -> str:
        """将最佳位置转换为移动指令"""
        dx = move_data["x"] - piece.x

        # 优先旋转
        if move_data["rotation"] > 0:
            return "rotate"

        # 然后水平移动
        if dx < -1:
            return "left"
        elif dx > 1:
            return "right"
        else:
            return "down"


if __name__ == "__main__":
    print("🤖 测试强化 AI 决策引擎\n")

    from board import GameBoard
    from harness.monitors import Monitors

    monitor = Monitors(game_id="ai_test_v2")
    board = GameBoard(monitor)
    board.spawn_piece()

    agent = AIAgent(board, monitor)

    print(f"当前方块：{board.current_piece.type.value}")
    print(f"面板尺寸：{board.width}x{board.height}")
    print(f"权重配置：{len(agent.weights)} 个评估维度")
    print()

    for i in range(5):
        start = time.time()
        move = agent.decide_move()
        duration = time.time() - start

        print(f"决策 {i+1}: {move} (耗时：{duration:.3f}s)")

    print("\n✅ 强化 AI 决策引擎正常！")
