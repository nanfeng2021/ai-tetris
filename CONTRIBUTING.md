# Contributing to AI Tetris

首先，感谢你愿意为这个项目做出贡献！🎉

AI Tetris 是一个基于 **Harness Engineering** 范式构建的智能俄罗斯方块游戏，我们欢迎各种形式的贡献。

## 📋 目录

- [行为准则](#行为准则)
- [我能贡献什么？](#我能贡献什么)
- [开发环境设置](#开发环境设置)
- [提交代码流程](#提交代码流程)
- [代码规范](#代码规范)
- [测试要求](#测试要求)
- [提问与反馈](#提问与反馈)

---

## 🤝 行为准则

本项目采用 [Contributor Covenant](https://www.contributor-covenant.org/) 行为准则。请保持友好、尊重和包容的社区氛围。

---

## 💡 我能贡献什么？

### 1. 报告 Bug 🐛
- 使用 GitHub Issues
- 提供详细的重现步骤
- 附上截图或日志（如适用）

### 2. 提出新功能 ✨
- 先在 Issue 中讨论想法
- 说明使用场景和必要性
- 我们会评估后给出反馈

### 3. 改进文档 📚
- 修正错别字或语法错误
- 补充缺失的说明
- 添加示例代码

### 4. 提交代码 🚀
- 修复已知 Issue
- 实现新功能
- 优化性能
- 增加测试覆盖率

### 5. Harness Engineering 相关 🔒
- 新增 Guardrails（约束规则）
- 完善 Validators（验证器）
- 扩展 Monitors（监控指标）
- 改进 Auto-Fix 机制

---

## 🛠️ 开发环境设置

### 1. Fork & Clone

```bash
# Fork 项目到个人账号
# 然后克隆到本地
git clone https://github.com/YOUR_USERNAME/ai-tetris.git
cd ai-tetris
```

### 2. 创建虚拟环境

```bash
# Python 3.11+
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装开发工具

```bash
# 代码格式化工具
pip install black flake8 isort

# 测试工具
pip install pytest pytest-cov

# 类型检查
pip install mypy
```

### 4. 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 查看测试覆盖率
pytest tests/ --cov=src --cov-report=html
```

### 5. 启动开发服务器

```bash
# 人工模式
python src/game.py --mode human

# AI 模式
python src/game.py --mode ai

# Web 版本
python web/server.py
```

---

## 📝 提交代码流程

### 1. 创建分支

```bash
# 从 main 分支创建新分支
git checkout -b feature/your-feature-name

# 或者修复 bug
git checkout -b fix/issue-123
```

### 分支命名规范：
- `feature/xxx` - 新功能
- `fix/xxx` - Bug 修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构
- `test/xxx` - 测试相关
- `chore/xxx` - 其他改动

### 2. 进行修改

遵循 [代码规范](#代码规范)，确保：
- ✅ 代码通过所有测试
- ✅ 新增测试覆盖新功能
- ✅ 更新相关文档

### 3. 提交变更

```bash
# 添加修改的文件
git add .

# 提交（遵循 Commit Message 规范）
git commit -m "feat: add new AI evaluation algorithm"
```

### Commit Message 规范：

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具配置

**示例：**
```
feat(ai): add genetic algorithm for decision optimization

- Implement genetic algorithm for weight tuning
- Add population management and mutation logic
- Update AI agent to use evolved weights

Closes #45
```

### 4. 推送到远程

```bash
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request

1. 访问你的 Fork 仓库
2. 点击 "Compare & pull request"
3. 填写 PR 描述：
   - 改动目的
   - 实现方案
   - 测试情况
   - 相关 Issue 链接
4. 等待 Code Review

---

## 📏 代码规范

### Python 代码

遵循 [PEP 8](https://pep8.org/) 风格指南：

```python
# ✅ 好的写法
def calculate_score(lines: int, level: int) -> int:
    """计算得分"""
    base_scores = {1: 100, 2: 300, 3: 500, 4: 800}
    return base_scores.get(lines, 0) * level

# ❌ 避免的写法
def calcScore(l,lvl):return l*100*lvl
```

### 格式化命令

```bash
# 自动格式化代码
black src/ tests/

# 排序 import
isort src/ tests/

# 检查代码风格
flake8 src/ tests/ --max-line-length=100

# 类型检查
mypy src/ --ignore-missing-imports
```

### Harness Engineering 规范

#### Guardrails
```python
# ✅ 必须有清晰的验证逻辑和错误信息
def validate_move(board, piece, x, y):
    if not is_within_bounds(x, y):
        return False, "Move out of bounds"
    if has_collision(board, piece, x, y):
        return False, "Collision detected"
    return True, "Valid move"
```

#### Validators
```python
# ✅ 状态验证必须全面
def validate_game_state(state):
    assert state.score >= 0, "Score cannot be negative"
    assert state.level > 0, "Level must be positive"
    assert len(state.board) == BOARD_HEIGHT, "Invalid board height"
```

#### Monitors
```python
# ✅ 关键指标必须记录
GAME_DURATION.observe(duration)
LINES_CLEARED.labels(level=state.level).inc()
GUARDRAIL_TRIGGERS.labels(rule='collision').inc()
```

---

## 🧪 测试要求

### 覆盖率标准

| 模块 | 最低覆盖率 | 必测项 |
|------|-----------|--------|
| Guardrails | 100% | 所有边界条件 |
| Validators | 100% | 状态一致性 |
| Game Logic | 95% | 核心玩法 |
| AI Agent | 90% | 决策逻辑 |
| UI | 80% | 渲染正确性 |

### 编写测试

```python
# tests/test_guardrails.py
import pytest
from src.harness.guardrails import validate_move

def test_validate_move_out_of_bounds():
    """测试越界检测"""
    board = create_empty_board()
    piece = create_test_piece('I')
    
    # 左边界外
    is_valid, reason = validate_move(board, piece, -1, 5)
    assert not is_valid
    assert "out of bounds" in reason.lower()
    
    # 右边界外
    is_valid, reason = validate_move(board, piece, BOARD_WIDTH, 5)
    assert not is_valid
```

### 运行测试

```bash
# 运行特定测试
pytest tests/test_guardrails.py -v

# 运行并生成覆盖率报告
pytest tests/ --cov=src --cov-report=html --cov-report=term

# 查看 HTML 报告
open htmlcov/index.html
```

---

## ❓ 提问与反馈

### 遇到问题？

1. **查看文档**: [README.md](README.md), [docs/](docs/)
2. **搜索 Issues**: 可能已经有人问过
3. **新建 Issue**: 详细描述问题

### 联系方式

- **GitHub Issues**: [提交 Issue](https://github.com/nanfeng2021/ai-tetris/issues)
- **Discussions**: [参与讨论](https://github.com/nanfeng2021/ai-tetris/discussions)

---

## 🎯 当前需要帮助的地方

查看 [Good First Issues](https://github.com/nanfeng2021/ai-tetris/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) 开始你的贡献之旅！

### 高优先级任务：
- [ ] 添加前端单元测试 (`web/static/js/game.test.js`)
- [ ] 配置 GitHub Actions CI/CD
- [ ] 添加 Grafana 仪表板配置
- [ ] 完善移动端适配

---

## 📚 资源

- [Harness Engineering 实践指南](https://my.feishu.cn/docx/Ko7sdF8fIoxME7xJWCGc96YVnJb)
- [Python 最佳实践](https://docs.python-guide.org/)
- [Testing Pyramid](https://martinfowler.com/bliki/TestPyramid.html)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

再次感谢你的贡献！🐕

**旺财提示**: 第一次贡献可能会有点紧张，这很正常！我们会认真 review 每一行代码，帮助你快速成长。有任何问题随时在 Issue 中提问！

[[reply_to_current]]
