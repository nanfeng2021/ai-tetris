"""
测试 Validators 验证器
"""

import sys

# type: ignore[E402]
sys.path.insert(0, "/root/.openclaw/workspace/ai-tetris/src")

from harness.validators import ValidationStatus, Validators, run_all_validators


def test_board_dimensions():
    """测试面板尺寸验证"""
    print("=" * 50)
    print("测试 1: 面板尺寸验证")
    print("=" * 50)

    # 正常面板 (10x20)
    board = [[None for _ in range(10)] for _ in range(20)]
    result = Validators.validate_board_dimensions(board)
    assert result.status == ValidationStatus.PASSED, f"应该通过：{result.message}"
    print(f"✅ 正常面板：{result.message}")

    # 高度错误
    board_wrong = [[None for _ in range(10)] for _ in range(15)]
    result = Validators.validate_board_dimensions(board_wrong)
    assert result.status == ValidationStatus.FAILED, "应该失败：高度错误"
    print(f"✅ 高度错误检测到：{result.message}")

    # 宽度错误
    board_wrong2 = [[None for _ in range(8)] for _ in range(20)]
    result = Validators.validate_board_dimensions(board_wrong2)
    assert result.status == ValidationStatus.FAILED, "应该失败：宽度错误"
    print(f"✅ 宽度错误检测到：{result.message}")

    print()


def test_piece_shape():
    """测试方块形状验证"""
    print("=" * 50)
    print("测试 2: 方块形状验证")
    print("=" * 50)

    # 正常方块 (2x2)
    piece = [[True, True], [True, True]]
    result = Validators.validate_piece_shape(piece)
    assert result.status == ValidationStatus.PASSED, f"应该通过：{result.message}"
    print(f"✅ 正常方块：{result.message}")

    # 空方块
    piece_empty = []
    result = Validators.validate_piece_shape(piece_empty)
    assert result.status == ValidationStatus.FAILED, "应该失败：空方块"
    print(f"✅ 空方块检测到：{result.message}")

    # 不规则形状
    piece_irregular = [[True, True], [True]]
    result = Validators.validate_piece_shape(piece_irregular)
    assert result.status == ValidationStatus.FAILED, "应该失败：不规则形状"
    print(f"✅ 不规则形状检测到：{result.message}")

    # 全空方块
    piece_all_empty = [[False, False], [False, False]]
    result = Validators.validate_piece_shape(piece_all_empty)
    assert result.status == ValidationStatus.FAILED, "应该失败：全空方块"
    print(f"✅ 全空方块检测到：{result.message}")

    print()


def test_game_progress():
    """测试游戏进度验证"""
    print("=" * 50)
    print("测试 3: 游戏进度验证")
    print("=" * 50)

    # 正常进度
    result = Validators.validate_game_progress(1000, 5, 2, 120.0)
    assert result.status == ValidationStatus.PASSED, f"应该通过：{result.message}"
    print(f"✅ 正常进度：{result.message}")

    # 负分数
    result = Validators.validate_game_progress(-100, 5, 2, 120.0)
    assert result.status == ValidationStatus.FAILED, "应该失败：负分数"
    print(f"✅ 负分数检测到：{result.message}")

    # 负行数
    result = Validators.validate_game_progress(1000, -5, 2, 120.0)
    assert result.status == ValidationStatus.FAILED, "应该失败：负行数"
    print(f"✅ 负行数检测到：{result.message}")

    # 等级为 0
    result = Validators.validate_game_progress(1000, 5, 0, 120.0)
    assert result.status == ValidationStatus.FAILED, "应该失败：等级为 0"
    print(f"✅ 等级异常检测到：{result.message}")

    # 分数与行数不匹配 (警告)
    result = Validators.validate_game_progress(100, 10, 1, 60.0)
    assert result.status == ValidationStatus.WARNING, "应该警告：分数过低"
    print(f"✅ 分数异常警告：{result.message}")

    print()


def test_move_sequence():
    """测试移动序列验证"""
    print("=" * 50)
    print("测试 4: 移动序列验证")
    print("=" * 50)

    # 正常移动序列
    moves = ["left", "right", "down", "rotate", "drop"]
    result = Validators.validate_move_sequence(moves)
    assert result.status == ValidationStatus.PASSED, f"应该通过：{result.message}"
    print(f"✅ 正常移动序列：{result.message}")

    # 非法移动
    moves_invalid = ["left", "jump", "right"]
    result = Validators.validate_move_sequence(moves_invalid)
    assert result.status == ValidationStatus.FAILED, "应该失败：非法移动"
    print(f"✅ 非法移动检测到：{result.message}")

    # 空序列
    moves_empty = []
    result = Validators.validate_move_sequence(moves_empty)
    assert result.status == ValidationStatus.PASSED, "应该通过：空序列合法"
    print(f"✅ 空序列：{result.message}")

    print()


def test_run_all_validators():
    """测试批量运行 Validators"""
    print("=" * 50)
    print("测试 5: 批量运行 Validators")
    print("=" * 50)

    board = [[None for _ in range(10)] for _ in range(20)]
    piece = [[True, True], [True, True]]

    # 测试 1: 基本验证
    results = run_all_validators(board=board, piece_shape=piece, score=1000, lines=5, level=2)
    assert len(results) >= 3, f"应该至少有 3 个结果，实际{len(results)}"
    print(f"✅ 基本验证：共{len(results)}个验证结果")

    # 测试 2: 移动序列验证
    results = run_all_validators(moves=["LEFT", "RIGHT", "ROTATE"])
    assert len(results) >= 1, "应该有移动序列验证结果"
    print(f"✅ 移动序列验证：共{len(results)}个验证结果")

    for r in results:
        status_icon = (
            "✅"
            if r.status == ValidationStatus.PASSED
            else ("⚠️" if r.status == ValidationStatus.WARNING else "❌")
        )
        print(f"  {status_icon} {r.validator}: {r.message}")

    print()


if __name__ == "__main__":
    print("\n🧪 开始测试 Validators 验证器\n")

    try:
        test_board_dimensions()
        test_piece_shape()
        test_game_progress()
        test_move_sequence()
        test_run_all_validators()

        print("=" * 50)
        print("✅ 所有 Validators 测试通过！")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 未知错误：{e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)
