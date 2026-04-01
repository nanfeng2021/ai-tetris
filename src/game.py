"""
游戏主循环 - Harness Engineering 驱动
整合所有组件，提供完整的游戏体验
"""

import argparse
import os
import sys
import time

# type: ignore[E402]
sys.path.insert(0, os.path.dirname(__file__))

from board import GameBoard
from harness.guardrails import Guardrails
from harness.monitors import Monitors
from pieces import PieceFactory, PieceType


class TetrisGame:
    """俄罗斯方块游戏主类"""

    def __init__(self, mode: str = "human", monitor: Monitors = None):
        self.mode = mode
        self.monitor = monitor or Monitors(game_id="game_001")
        self.board = GameBoard(self.monitor)
        self.running = False
        self.paused = False

        # AI 相关
        if mode == "ai":
            from ai.agent import AIAgent

            self.ai_agent = AIAgent(self.board)
        else:
            self.ai_agent = None

    def start(self):
        """开始游戏"""
        self.running = True
        self.paused = False
        self.board.reset()
        self.board.spawn_piece()

        self.monitor.start_game(mode=self.mode)
        self.monitor.set_ai_status("default", running=(self.mode == "ai"))

        print(f"🎮 游戏开始！模式：{self.mode}")
        print(self.board.render_ascii())

    def stop(self):
        """停止游戏"""
        self.running = False
        self.monitor.set_ai_status("default", running=False)

        # 记录游戏结束
        state = self.board.get_state()
        self.monitor.end_game(
            reason="stacked" if state.game_over else "quit",
            score=state.score,
            lines=state.lines,
            level=state.level,
        )

        print(f"\n游戏结束！最终得分：{state.score}")

    def update(self):
        """游戏逻辑更新"""
        if not self.running or self.paused:
            return

        if self.board.game_over:
            print("\n💀 GAME OVER!")
            self.stop()
            return

        # AI 模式：自动决策
        if self.mode == "ai" and self.ai_agent:
            start_time = time.time()
            move = self.ai_agent.decide_move()
            decision_time = time.time() - start_time

            # 记录 AI 决策延迟
            self.monitor.record_ai_decision(decision_time)

            # 执行 AI 决策
            self._execute_move(move)
        else:
            # 人工模式：自动下落
            if not self.board.move_piece(0, 1):
                # 无法下落，锁定方块
                self.board.lock_piece()

    def _execute_move(self, move: str):
        """执行移动指令"""
        if move == "left":
            self.board.move_piece(-1, 0)
        elif move == "right":
            self.board.move_piece(1, 0)
        elif move == "down":
            if not self.board.move_piece(0, 1):
                self.board.lock_piece()
        elif move == "rotate":
            self.board.rotate_piece()
        elif move == "drop":
            self.board.hard_drop()
            self.board.lock_piece()

    def handle_input(self, key: str):
        """处理人工输入"""
        if key == "p":
            self.paused = not self.paused
            print(f"{'⏸️ 暂停' if self.paused else '▶️ 继续'}")
            return

        if self.paused:
            return

        if key == "q":
            self.stop()
            return

        if key == "left":
            self.board.move_piece(-1, 0)
        elif key == "right":
            self.board.move_piece(1, 0)
        elif key == "down":
            self.board.move_piece(0, 1)
        elif key == "up":
            self.board.rotate_piece()
        elif key == "space":
            self.board.hard_drop()
            self.board.lock_piece()

    def run_loop(self, tick_rate: float = 1.0):
        """运行游戏主循环（终端版）"""
        self.start()

        try:
            while self.running:
                self.update()

                if self.running:
                    print("\n" + "=" * 50)
                    print(self.board.render_ascii())
                    print("=" * 50)

                time.sleep(tick_rate / self.board.level)

        except KeyboardInterrupt:
            print("\n\n用户中断游戏")
            self.stop()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI 俄罗斯方块 - Harness Engineering 实践")
    parser.add_argument(
        "--mode",
        type=str,
        default="human",
        choices=["human", "ai"],
        help="游戏模式：human(人工) 或 ai(自动)",
    )
    parser.add_argument("--speed", type=float, default=1.0, help="游戏速度 (秒/格)")
    parser.add_argument("--monitor", action="store_true", help="启用 Prometheus 监控")

    args = parser.parse_args()

    print("=" * 60)
    print("🎮 AI 俄罗斯方块")
    print("=" * 60)
    print(f"模式：{args.mode}")
    print(f"速度：{args.speed} 秒/格")
    print(f"监控：{'启用' if args.monitor else '禁用'}")
    print("=" * 60)
    print("\n操作说明:")
    print("  ← → : 左右移动")
    print("  ↑   : 旋转")
    print("  ↓   : 加速下落")
    print("  Space: 直接掉落")
    print("  P   : 暂停")
    print("  Q   : 退出")
    print("=" * 60)

    # 创建游戏
    monitor = Monitors(game_id="main_game") if args.monitor else None
    game = TetrisGame(mode=args.mode, monitor=monitor)

    # 简单的人工输入循环（实际应该用 pygame 或 curses）
    if args.mode == "human":
        import threading

        def input_thread():
            while game.running:
                try:
                    key = input().strip().lower()
                    game.handle_input(key)
                except:
                    pass

        thread = threading.Thread(target=input_thread, daemon=True)
        thread.start()

        game.run_loop(tick_rate=args.speed)
    else:
        # AI 模式自动运行
        game.run_loop(tick_rate=args.speed)


if __name__ == "__main__":
    main()
