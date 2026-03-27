# 🎮 AI 俄罗斯方块 - Harness Engineering 实践

> 基于 Harness Engineering 范式构建的智能俄罗斯方块游戏
> 
> 🔒 约束驱动 | ✅ 验证优先 | 📊 实时监控 | 🔄 自动修复

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Harness Engineering](https://img.shields.io/badge/Harness-Engineering-green)]()

## ✨ 特性

### 🎮 游戏功能
- 🧱 经典俄罗斯方块玩法
- 🤖 AI 自动对战模式
- 📊 实时得分/等级/行数统计
- 🎨 现代化 UI 界面
- ⌨️ 键盘/鼠标双控制

### 🔒 Harness Engineering
- **Guardrails**: 移动合法性验证、碰撞检测
- **Validators**: 游戏状态一致性检查
- **Monitors**: Prometheus 指标 + 实时日志
- **Auto-Fix**: 卡死检测 + 自动重置

### 📈 监控指标
- 游戏时长
- 消除行数
- 平均得分
- AI 决策延迟
- Guardrail 触发次数

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动游戏

```bash
# 人工模式
python src/game.py --mode human

# AI 模式
python src/game.py --mode ai

# 带监控
python src/game.py --mode ai --monitor
```

### 3. 查看监控面板

```bash
# 启动 Prometheus
docker-compose up prometheus

# 访问 http://localhost:9090
```

## 📁 项目结构

```
ai-tetris/
├── src/
│   ├── game.py              # 游戏主循环
│   ├── board.py             # 游戏面板（带验证）
│   ├── pieces.py            # 方块定义
│   ├── ai/
│   │   ├── agent.py         # AI 决策引擎
│   │   └── evaluator.py     # 局面评估器
│   ├── harness/
│   │   ├── guardrails.py    # 约束规则
│   │   ├── validators.py    # 验证器
│   │   └── monitors.py      # 监控指标
│   └── ui/
│       └── renderer.py      # 渲染引擎
├── tests/
│   ├── test_guardrails.py   # Guardrail 测试
│   ├── test_validators.py   # 验证器测试
│   └── test_game.py         # 游戏逻辑测试
├── config/
│   └── settings.yaml        # 游戏配置
├── scripts/
│   ├── train_ai.sh          # AI 训练脚本
│   └── auto_fix.py          # 自动修复脚本
├── docker-compose.yml       # Docker 编排
├── requirements.txt         # Python 依赖
└── README.md                # 项目说明
```

## 🎯 Harness Engineering 实践

### 1. Guardrails（约束规则）

```python
# 方块不能穿墙
def validate_move(board, piece, x, y):
    if x < 0 or x + piece.width > BOARD_WIDTH:
        return False  # 越界
    if y + piece.height > BOARD_HEIGHT:
        return False
    if check_collision(board, piece, x, y):
        return False  # 碰撞
    return True
```

### 2. Validators（验证器）

```python
# 游戏状态一致性检查
def validate_game_state(state):
    assert state.score >= 0, "分数不能为负"
    assert state.lines >= 0, "行数不能为负"
    assert state.level > 0, "等级必须>0"
    assert len(state.board) == BOARD_HEIGHT, "面板高度错误"
```

### 3. Monitors（监控器）

```python
# Prometheus 指标
GAME_DURATION = Histogram('tetris_game_duration_seconds', '游戏时长')
LINES_CLEARED = Counter('tetris_lines_cleared_total', '消除行数', ['level'])
AI_DECISION_LATENCY = Histogram('tetris_ai_decision_seconds', 'AI 决策延迟')
GUARDRAIL_TRIGGERS = Counter('tetris_guardrail_triggers_total', 'Guardrail 触发', ['rule'])
```

### 4. Auto-Fix（自动修复）

```python
# 卡死检测 + 自动重置
async def detect_and_fix(game):
    if game.no_valid_moves() for 5_seconds:
        logger.warning("检测到卡死，触发重置")
        await auto_reset(game)
        GUARDRAIL_TRIGGERS.labels(rule='stuck_detection').inc()
```

## 🧪 测试覆盖率要求

| 模块 | 最低覆盖率 | 关键测试 |
|------|-----------|---------|
| Guardrails | 100% | 所有边界条件 |
| Validators | 100% | 状态一致性 |
| Game Logic | 95% | 核心玩法 |
| AI Agent | 90% | 决策逻辑 |
| UI | 80% | 渲染正确性 |

运行测试：
```bash
pytest tests/ --cov=src --cov-report=html
```

## 🛠️ 配置说明

编辑 `config/settings.yaml`:

```yaml
game:
  board_width: 10
  board_height: 20
  initial_speed: 1.0  # 秒/格
  speed_increment: 0.1

ai:
  enabled: true
  decision_timeout: 2.0  # 秒
  evaluation_depth: 3  # 搜索深度

monitoring:
  prometheus_enabled: true
  metrics_port: 9090
  log_level: INFO
```

## 📊 监控仪表板

访问 `http://localhost:9090` 查看：

- 📈 实时游戏指标
- 🎯 AI 决策质量
- 🔒 Guardrail 触发统计
- ⚡ 性能延迟分布

## 🤖 AI 训练

```bash
# 使用强化学习训练 AI
./scripts/train_ai.sh --episodes 10000

# 加载预训练模型
python src/game.py --mode ai --model pretrained_v1
```

## 🐳 Docker 部署

```bash
# 一键启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

## 🎮 操作说明

### 人工模式
- ← → : 左右移动
- ↑ : 旋转
- ↓ : 加速下落
- Space : 直接掉落
- P : 暂停
- R : 重新开始

### AI 模式
- 自动决策，无需操作
- 观看 AI 如何玩转俄罗斯方块

## 📖 相关文档

- [Harness Engineering 实践指南](https://my.feishu.cn/docx/Ko7sdF8fIoxME7xJWCGc96YVnJb)
- [俄罗斯方块 AI 算法详解](docs/ai-algorithm.md)
- [监控指标说明](docs/metrics.md)

## 🏆 高分榜

| 模式 | 最高分 | 保持者 | 日期 |
|------|--------|--------|------|
| Human | 9999 | - | - |
| AI | 99999 | AI-v1 | 2026-03-28 |

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👤 作者

南风 (nanfeng2021)

---

**🎮 Happy Gaming! Harness Engineering Powered!**
