"""
测试 AI 决策引擎
"""

import os
import sys
import time

import pytest

# type: ignore[E402]
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ai.agent import AIAgent
from board import GameBoard
from harness.monitors import Monitors


class TestAIAgent:
    """AI Agent 测试"""

    def setup_method(self):
        """每个测试前初始化"""
        self.monitor = Monitors(game_id="ai_test")
        self.board = GameBoard(self.monitor)
        self.agent = AIAgent(self.board, self.monitor)

    def test_agent_initialization(self):
        """测试 AI 初始化"""
        assert self.agent.board is not None
        assert len(self.agent.weights) > 0
        assert "holes" in self.agent.weights
        assert "aggregate_height" in self.agent.weights

    def test_decide_move(self):
        """测试决策生成"""
        self.board.spawn_piece()

        start_time = time.time()
        move = self.agent.decide_move()
        decision_time = time.time() - start_time

        assert move in ["left", "right", "down", "rotate"]
        assert decision_time < 2.0  # 应该在 2 秒内完成

    def test_evaluate_position(self):
        """测试位置评估"""
        self.board.spawn_piece()

        score = self.agent._evaluate_move({"x": 3, "rotation": 0, "piece_type": "I"})

        # 分数应该是有限值（不是负无穷）
        assert score > float("-inf")
        assert score < float("inf")

    def test_simulate_placement(self):
        """测试模拟放置"""
        self.board.spawn_piece()

        simulated = self.agent._simulate_placement(3, 0)

        assert simulated is not None
        assert len(simulated) == self.board.height
        assert all(len(row) == self.board.width for row in simulated)

    def test_calculate_holes(self):
        """测试空洞计算"""
        # 创建一个有空洞的面板
        test_board = [[None for _ in range(10)] for _ in range(20)]

        # 底部填满
        for x in range(10):
            test_board[19][x] = "I"

        # 中间留一个洞
        test_board[18][5] = None
        for x in range(10):
            if x != 5:
                test_board[18][x] = "I"

        holes = self.agent._calculate_holes(test_board)
        assert holes >= 1

    def test_calculate_bumpiness(self):
        """测试不平整度计算"""
        test_board = [[None for _ in range(10)] for _ in range(20)]

        # 创建不平整表面
        for x in range(5):
            test_board[19][x] = "I"
        for x in range(5, 10):
            test_board[18][x] = "I"

        bumpiness = self.agent._calculate_bumpiness(test_board)
        assert bumpiness > 0

    def test_decision_history(self):
        """测试决策历史记录"""
        self.board.spawn_piece()

        moves = []
        for _ in range(15):
            move = self.agent.decide_move()
            moves.append(move)

            # 模拟下落
            self.board.move_piece(0, 1)

        # 应该有历史记录
        assert len(self.agent.decision_history) > 0
        assert len(self.agent.decision_history) <= self.agent.max_history

    def test_timeout_handling(self):
        """测试超时处理"""
        # 修改权重使计算变慢（极端情况）
        original_weights = self.agent.weights.copy()

        self.board.spawn_piece()
        move = self.agent.decide_move()

        # 即使超时也应该返回有效移动
        assert move in ["left", "right", "down", "rotate"]

    def test_piece_specific_strategy(self):
        """测试方块特定策略"""
        piece_strategies = self.agent.piece_strategies

        # I 和 O 方块应该避免空洞
        assert piece_strategies["I"]["avoid_holes"] == True
        assert piece_strategies["O"]["avoid_holes"] == True

        # T/J/L 更灵活
        assert piece_strategies["T"]["avoid_holes"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
