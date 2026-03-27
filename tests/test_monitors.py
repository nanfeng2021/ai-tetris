"""
测试 Monitors 监控指标
"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/ai-tetris/src')

from harness.monitors import Monitors, get_monitor, GAMES_TOTAL, LINES_CLEARED_TOTAL

def test_monitor_creation():
    """测试监控器创建"""
    print("=" * 50)
    print("测试 1: 监控器创建")
    print("=" * 50)
    
    monitor = Monitors(game_id="test_game_001")
    assert monitor is not None, "监控器创建失败"
    assert monitor.game_id == "test_game_001", "game_id 设置错误"
    print(f"✅ 监控器创建成功，game_id={monitor.game_id}")
    
    print()

def test_start_game():
    """测试开始游戏"""
    print("=" * 50)
    print("测试 2: 开始游戏")
    print("=" * 50)
    
    monitor = Monitors(game_id="test_game_002")
    monitor.start_game(mode="human")
    
    # 检查指标是否增加
    metrics = monitor.get_metrics()
    assert 'tetris_games_total' in metrics, "游戏次数指标未更新"
    print(f"✅ 开始游戏成功，指标已记录")
    
    print()

def test_update_score():
    """测试分数更新"""
    print("=" * 50)
    print("测试 3: 分数更新")
    print("=" * 50)
    
    monitor = Monitors(game_id="test_game_003")
    monitor.update_score(500)
    
    metrics = monitor.get_metrics()
    assert 'tetris_current_score' in metrics, "分数指标未更新"
    assert '500.0' in metrics, "分数值不正确"
    print(f"✅ 分数更新成功：500")
    
    monitor.update_score(1000)
    metrics = monitor.get_metrics()
    assert '1000.0' in metrics, "分数值更新不正确"
    print(f"✅ 分数更新成功：1000")
    
    print()

def test_update_level_and_lines():
    """测试等级和行数更新"""
    print("=" * 50)
    print("测试 4: 等级和行数更新")
    print("=" * 50)
    
    monitor = Monitors(game_id="test_game_004")
    monitor.update_level(3)
    monitor.update_lines(10, 3)
    
    metrics = monitor.get_metrics()
    assert 'tetris_current_level' in metrics, "等级指标未更新"
    assert 'tetris_current_lines' in metrics, "行数指标未更新"
    print(f"✅ 等级和行数更新成功：level=3, lines=10")
    
    print()

def test_record_ai_decision():
    """测试 AI 决策延迟记录"""
    print("=" * 50)
    print("测试 5: AI 决策延迟记录")
    print("=" * 50)
    
    monitor = Monitors(game_id="test_game_005")
    
    # 正常延迟
    monitor.record_ai_decision(0.5)
    print(f"✅ 记录 AI 决策延迟：0.5s")
    
    # 超时延迟 (应该触发 Guardrail)
    monitor.record_ai_decision(3.0)
    print(f"✅ 记录 AI 决策延迟：3.0s (超时)")
    
    metrics = monitor.get_metrics()
    assert 'tetris_ai_decision_seconds' in metrics, "AI 延迟指标未更新"
    print(f"✅ AI 决策指标已记录")
    
    print()

def test_guardrail_triggers():
    """测试 Guardrail 触发记录"""
    print("=" * 50)
    print("测试 6: Guardrail 触发记录")
    print("=" * 50)
    
    monitor = Monitors(game_id="test_game_006")
    
    monitor.record_guardrail_trigger('boundary_check', 'warning')
    monitor.record_guardrail_trigger('collision_detection', 'critical')
    
    metrics = monitor.get_metrics()
    assert 'tetris_guardrail_triggers_total' in metrics, "Guardrail 指标未更新"
    print(f"✅ Guardrail 触发记录成功")
    
    print()

def test_end_game():
    """测试结束游戏"""
    print("=" * 50)
    print("测试 7: 结束游戏")
    print("=" * 50)
    
    monitor = Monitors(game_id="test_game_007")
    monitor.start_game(mode="ai")
    monitor.update_score(2000)
    monitor.update_level(5)
    monitor.update_lines(20, 5)
    
    # 模拟游戏结束
    import time
    time.sleep(0.1)  # 短暂等待
    monitor.end_game(reason='stacked', score=2000, lines=20, level=5)
    
    metrics = monitor.get_metrics()
    assert 'tetris_game_over_total' in metrics, "游戏结束指标未更新"
    assert 'tetris_game_duration_seconds' in metrics, "游戏时长指标未更新"
    print(f"✅ 游戏结束记录成功，原因：stacked")
    
    print()

def test_get_metrics():
    """测试获取 Prometheus 格式指标"""
    print("=" * 50)
    print("测试 8: 获取 Prometheus 格式指标")
    print("=" * 50)
    
    monitor = Monitors(game_id="test_game_008")
    monitor.start_game(mode="human")
    monitor.update_score(1500)
    monitor.update_level(4)
    monitor.update_lines(15, 4)
    
    metrics = monitor.get_metrics()
    
    # 检查指标格式
    assert isinstance(metrics, str), "指标应该是字符串"
    assert len(metrics) > 0, "指标不应该为空"
    assert 'tetris_' in metrics, "指标应该包含 tetris_ 前缀"
    
    print(f"✅ Prometheus 格式指标生成成功")
    print(f"   指标长度：{len(metrics)} 字符")
    print(f"   示例:\n{metrics[:500]}...")
    
    print()

if __name__ == "__main__":
    print("\n🧪 开始测试 Monitors 监控指标\n")
    
    try:
        test_monitor_creation()
        test_start_game()
        test_update_score()
        test_update_level_and_lines()
        test_record_ai_decision()
        test_guardrail_triggers()
        test_end_game()
        test_get_metrics()
        
        print("=" * 50)
        print("✅ 所有 Monitors 测试通过！")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败：{e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 未知错误：{e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
