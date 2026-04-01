# Harness Compliance Skill

## 📋 定义

Harness Engineering 合规性检查，确保代码符合约束驱动开发范式。

## 🎯 触发场景

- ✅ 新模块开发
- ✅ 架构审查
- ✅ 代码质量审计
- ✅ 安全合规检查

## 📏 三层架构要求

### 1. Guardrails (约束规则) - 必须 100% 覆盖

**要求**:
- 所有外部输入必须验证
- 所有状态变更必须合法
- 所有操作必须有边界检查

**示例**:
```python
✅ def validate_move(board, piece, x, y):
       if not is_within_bounds(x, y):
           return False, "Move out of bounds"
       if has_collision(board, piece, x, y):
           return False, "Collision detected"
       return True, "Valid move"

❌ def move(piece, x, y):  # 缺少验证
       piece.x = x
       piece.y = y
```

### 2. Validators (验证器) - 必须 100% 覆盖

**要求**:
- 所有状态必须一致性验证
- 所有不变量必须断言检查
- 所有数据必须完整性验证

**示例**:
```python
✅ def validate_game_state(state):
       assert state.score >= 0, "Score cannot be negative"
       assert state.level > 0, "Level must be positive"
       assert len(state.board) == BOARD_HEIGHT, "Invalid board height"

❌ # 缺少状态验证
```

### 3. Monitors (监控器) - 关键指标必须监控

**要求**:
- 性能指标必须记录
- 业务指标必须追踪
- 异常事件必须告警

**示例**:
```python
✅ GAME_DURATION.observe(duration)
   LINES_CLEARED.labels(level=level).inc()
   GUARDRAIL_TRIGGERS.labels(rule='collision').inc()
   AI_DECISION_LATENCY.observe(decision_time)

❌ # 缺少监控指标
```

## 🔍 合规检查清单

### Guardrails 检查

- [ ] 所有 API 入口有输入验证
- [ ] 所有写操作有权限检查
- [ ] 所有外部调用有超时控制
- [ ] 所有资源使用有限制
- [ ] 所有异常有捕获和处理

### Validators 检查

- [ ] 核心状态有一致性验证
- [ ] 业务规则有断言保护
- [ ] 数据完整性和参照完整性
- [ ] 事务边界清晰
- [ ] 回滚机制完善

### Monitors 检查

- [ ] 关键性能指标 (KPI) 已定义
- [ ] 业务指标已追踪
- [ ] 错误率监控已配置
- [ ] 延迟分布已记录
- [ ] 告警阈值已设置

## 📊 合规评分

| 维度 | 权重 | 达标线 | 当前状态 |
|------|------|--------|---------|
| Guardrails | 40% | 100% | ⬜ |
| Validators | 35% | 100% | ⬜ |
| Monitors | 25% | 90% | ⬜ |
| **总分** | 100% | **95%** | **待评估** |

---

**版本**: v1.0.0  
**维护者**: 南风 (nanfeng2021)  
**参考**: [Harness Engineering 实践指南](https://my.feishu.cn/docx/Ko7sdF8fIoxME7xJWCGc96YVnJb)
