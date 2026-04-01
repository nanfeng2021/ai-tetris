"""
测试 Guardrails 约束规则
"""

import sys
sys.path.insert(0, "/root/.openclaw/workspace/ai-tetris/src")

from harness.guardrails import Guardrails, run_all_guardrails


def test_boundary_check():
    """测试边界检查"""
    print("=" * 50)
    print("测试 1: 边界检查")
    print("=" * 50)

    # 正常位置
    result = Guardrails.validate_boundary(2, 3, 2, 2)
    assert result.passed, f"应该通过：{result.message}"
    print(f"✅ 正常位置：{result.message}")

    # 左边界越界
    result = Guardrails.validate_boundary(-1, 3, 2, 2)
    assert not result.passed, "应该失败：左边界越界"
    print(f"✅ 左边界越界检测到：{result.message}")

    # 右边界越界
    result = Guardrails.validate_boundary(9, 3, 2, 2)
    assert not result.passed, "应该失败：右边界越界"
    print(f"✅ 右边界越界检测到：{result.message}")

    # 底部越界
    result = Guardrails.validate_boundary(2, 19, 2, 2)
    assert not result.passed, "应该失败：底部越界"
    print(f"✅ 底部越界检测到：{result.message}")

    print()


def test_collision_check():
    """测试碰撞检测"""
    print("=" * 50)
    print("测试 2: 碰撞检测")
    print("=" * 50)

    # 创建空面板
    board = [[None for _ in range(10)] for _ in range(20)]

    # 定义简单方块 (2x2)
    class Piece:
        shape = [[True, True], [True, True]]

    # 无碰撞
    result = Guardrails.validate_collision(board, Piece(), 2, 3)
    assert result.passed, f"应该通过：{result.message}"
    print(f"✅ 无碰撞：{result.message}")

    # 放置一个障碍物
    board[5][5] = "red"

    # 碰撞检测
    result = Guardrails.validate_collision(board, Piece(), 4, 4)
    assert not result.passed, "应该失败：有碰撞"
    print(f"✅ 碰撞检测到：{result.message}")

    print()


def test_game_state_validation():
    """测试游戏状态验证"""
    print("=" * 50)
    print("测试 3: 游戏状态验证")
    print("=" * 50)

    # 正常状态
    result = Guardrails.validate_game_state(1000, 5, 2)
    assert result.passed, f"应该通过：{result.message}"
    print(f"✅ 正常状态：{result.message}")

    # 负分数
    result = Guardrails.validate_game_state(-100, 5, 2)
    assert not result.passed, "应该失败：负分数"
    print(f"✅ 负分数检测到：{result.message}")

    # 负行数
    result = Guardrails.validate_game_state(1000, -5, 2)
    assert not result.passed, "应该失败：负行数"
    print(f"✅ 负行数检测到：{result.message}")

    # 等级为 0
    result = Guardrails.validate_game_state(1000, 5, 0)
    assert not result.passed, "应该失败：等级为 0"
    print(f"✅ 等级异常检测到：{result.message}")

    print()


def test_ai_decision_timeout():
    """测试 AI 决策超时"""
    print("=" * 50)
    print("测试 4: AI 决策超时检查")
    print("=" * 50)

    # 正常耗时
    result = Guardrails.validate_ai_decision_time(0.5)
    assert result.passed, f"应该通过：{result.message}"
    print(f"✅ 正常耗时：{result.message}")

    # 超时
    result = Guardrails.validate_ai_decision_time(3.0)
    assert not result.passed, "应该失败：超时"
    print(f"✅ 超时检测到：{result.message}")

    print()


def test_stuck_detection():
    """测试卡死检测"""
    print("=" * 50)
    print("测试 5: 卡死检测")
    print("=" * 50)

    import time

    current = time.time()

    # 正常移动
    result = Guardrails.detect_stuck(current - 2.0, current)
    assert result.passed, f"应该通过：{result.message}"
    print(f"✅ 正常移动：{result.message}")

    # 卡死 (>5 秒)
    result = Guardrails.detect_stuck(current - 6.0, current)
    assert not result.passed, "应该失败：卡死"
    print(f"✅ 卡死检测到：{result.message}")

    print()


def test_run_all_guardrails():
    """测试批量运行 Guardrails"""
    print("=" * 50)
    print("测试 6: 批量运行 Guardrails")
    print("=" * 50)

    results = run_all_guardrails(x=2, y=3, piece_width=2, piece_height=2)
    assert len(results) >= 1, "应该至少有一个结果"
    print(f"✅ 批量运行完成，共{len(results)}个检查结果")

    for r in results:
        status = "✅" if r.passed else "❌"
        print(f"  {status} {r.rule.value}: {r.message}")

    print()


if __name__ == "__main__":
    print("\n🧪 开始测试 Guardrails 约束规则\n")

    try:
        test_boundary_check()
        test_collision_check()
        test_game_state_validation()
        test_ai_decision_timeout()
        test_stuck_detection()
        test_run_all_guardrails()

        print("=" * 50)
        print("✅ 所有 Guardrails 测试通过！")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 未知错误：{e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
