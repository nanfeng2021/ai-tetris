"""
Harness Engineering 监控器
Prometheus 指标 + 实时监控
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
import time
from datetime import datetime
from typing import Dict, Optional

# 创建独立的注册表
registry = CollectorRegistry()

# ========== Counter 指标（累计计数）==========

# 游戏次数
GAMES_TOTAL = Counter(
    'tetris_games_total',
    'Total number of games played',
    ['mode'],  # human/ai
    registry=registry
)

# 消除行数
LINES_CLEARED_TOTAL = Counter(
    'tetris_lines_cleared_total',
    'Total lines cleared',
    ['level'],
    registry=registry
)

# Guardrail 触发次数
GUARDRAIL_TRIGGERS = Counter(
    'tetris_guardrail_triggers_total',
    'Total guardrail triggers',
    ['rule', 'severity'],
    registry=registry
)

# 验证失败次数
VALIDATION_FAILURES = Counter(
    'tetris_validation_failures_total',
    'Total validation failures',
    ['validator'],
    registry=registry
)

# 游戏结束原因
GAME_OVER_REASON = Counter(
    'tetris_game_over_total',
    'Total game overs',
    ['reason'],  # stacked/max_level/timeout
    registry=registry
)

# ========== Histogram 指标（延迟分布）==========

# 游戏时长
GAME_DURATION = Histogram(
    'tetris_game_duration_seconds',
    'Game duration',
    buckets=[60, 120, 300, 600, 1800, 3600, float('inf')],
    registry=registry
)

# AI 决策延迟
AI_DECISION_LATENCY = Histogram(
    'tetris_ai_decision_seconds',
    'AI decision latency',
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
    registry=registry
)

# 方块下落延迟
PIECE_DROP_LATENCY = Histogram(
    'tetris_piece_drop_seconds',
    'Piece drop latency',
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0],
    registry=registry
)

# ========== Gauge 指标（瞬时值）==========

# 当前分数
CURRENT_SCORE = Gauge(
    'tetris_current_score',
    'Current game score',
    ['game_id'],
    registry=registry
)

# 当前等级
CURRENT_LEVEL = Gauge(
    'tetris_current_level',
    'Current game level',
    ['game_id'],
    registry=registry
)

# 当前行数
CURRENT_LINES = Gauge(
    'tetris_current_lines',
    'Current lines cleared',
    ['game_id'],
    registry=registry
)

# 在线玩家数
ACTIVE_PLAYERS = Gauge(
    'tetris_active_players',
    'Number of active players',
    registry=registry
)

# AI 状态
AI_STATUS = Gauge(
    'tetris_ai_status',
    'AI agent status (1=running, 0=stopped)',
    ['agent_id'],
    registry=registry
)


class Monitors:
    """监控指标管理器"""
    
    def __init__(self, game_id: str = "default"):
        self.game_id = game_id
        self.start_time = None
    
    def start_game(self, mode: str = "human"):
        """开始新游戏"""
        GAMES_TOTAL.labels(mode=mode).inc()
        ACTIVE_PLAYERS.inc()
        self.start_time = time.time()
    
    def end_game(self, reason: str, score: int, lines: int, level: int):
        """结束游戏"""
        if self.start_time:
            duration = time.time() - self.start_time
            GAME_DURATION.observe(duration)
        
        GAME_OVER_REASON.labels(reason=reason).inc()
        ACTIVE_PLAYERS.dec()
        
        # 清理 Gauge
        try:
            CURRENT_SCORE.remove(self.game_id)
            CURRENT_LEVEL.remove(self.game_id)
            CURRENT_LINES.remove(self.game_id)
        except:
            pass
    
    def update_score(self, score: int):
        """更新分数"""
        CURRENT_SCORE.labels(game_id=self.game_id).set(score)
    
    def update_level(self, level: int):
        """更新等级"""
        CURRENT_LEVEL.labels(game_id=self.game_id).set(level)
    
    def update_lines(self, lines: int, level: int):
        """更新行数"""
        CURRENT_LINES.labels(game_id=self.game_id).set(lines)
        LINES_CLEARED_TOTAL.labels(level=str(level)).inc()
    
    def record_ai_decision(self, duration: float):
        """记录 AI 决策延迟"""
        AI_DECISION_LATENCY.observe(duration)
        if duration > 2.0:
            GUARDRAIL_TRIGGERS.labels(rule='ai_timeout', severity='warning').inc()
    
    def record_guardrail_trigger(self, rule: str, severity: str = "info"):
        """记录 Guardrail 触发"""
        GUARDRAIL_TRIGGERS.labels(rule=rule, severity=severity).inc()
    
    def record_validation_failure(self, validator: str):
        """记录验证失败"""
        VALIDATION_FAILURES.labels(validator=validator).inc()
    
    def record_piece_drop(self, duration: float):
        """记录方块下落延迟"""
        PIECE_DROP_LATENCY.observe(duration)
    
    def set_ai_status(self, agent_id: str, running: bool = True):
        """设置 AI 状态"""
        AI_STATUS.labels(agent_id=agent_id).set(1 if running else 0)
    
    def get_metrics(self) -> str:
        """获取 Prometheus 格式的指标"""
        return generate_latest(registry).decode('utf-8')


# 全局监控实例
global_monitor = Monitors()

def get_monitor() -> Monitors:
    """获取全局监控实例"""
    return global_monitor
