# Commit Message Skill

## 📋 定义

检查和规范 Git Commit Message 格式，确保遵循 [Conventional Commits](https://www.conventionalcommits.org/) 标准。

## 🎯 触发场景

- ✅ 执行 `git commit` 时
- ✅ 创建 Pull Request 时
- ✅ CI/CD 流程中的代码质量检查
- ✅ 发布新版本前的提交历史审查

## 📏 规范规则

### 基本格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型（必须）

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(ai): add genetic algorithm` |
| `fix` | Bug 修复 | `fix(game): resolve collision bug` |
| `docs` | 文档更新 | `docs(readme): update installation guide` |
| `style` | 代码格式（不影响功能） | `style(format): apply black formatting` |
| `refactor` | 重构 | `refactor(harness): simplify validator logic` |
| `test` | 测试相关 | `test(guardrails): add edge case tests` |
| `chore` | 构建/工具配置 | `chore(deps): upgrade flask version` |

### Scope 范围（可选）

表示影响的功能模块：

- `ai` - AI 决策引擎
- `game` - 游戏核心逻辑
- `harness` - Harness Engineering 组件
- `web` - Web 前端
- `ui` - 用户界面
- `config` - 配置文件
- `deps` - 依赖管理
- `ci` - CI/CD 配置
- `docs` - 文档

### Subject 主题（必须）

- 使用祈使句、现在时态
- 首字母小写
- 不以句号结尾
- 长度不超过 50 个字符

### Body 正文（可选）

- 详细描述改动动机
- 说明与之前行为的差异
- 每行不超过 72 个字符

### Footer 页脚（可选）

- 关联 Issue: `Closes #123`
- 破坏性变更: `BREAKING CHANGE: ...`
- Co-authored-by: `Co-authored-by: Name <email>`

## ✅ 正确示例

```bash
✅ feat(ai): add genetic algorithm for decision optimization

- Implement genetic algorithm for weight tuning
- Add population management and mutation logic
- Update AI agent to use evolved weights

Closes #45

✅ fix(game): resolve collision detection bug

Fixed issue where blocks would pass through existing pieces
when rotating near the right wall.

Fixes #123

✅ docs(readme): update installation guide

Added detailed steps for Docker setup and troubleshooting.

✅ style(format): apply black formatting to src/

Automated code formatting using black v23.1.0.
No functional changes.

✅ refactor(harness): simplify validator logic

Reduced complexity by extracting common validation rules
into reusable helper functions.

BREAKING CHANGE: Validator API changed from validate() to check()

✅ test(guardrails): add edge case tests

Added tests for boundary conditions and negative coordinates.
Increased coverage to 100%.

✅ chore(deps): upgrade flask to v2.3.0

Security update addressing CVE-2023-XXXXX.
```

## ❌ 错误示例

```bash
❌ Added new feature
   - 缺少 type 和 scope
   - 不符合 Conventional Commits 格式

❌ fix: fixed bug
   - 缺少具体的 scope
   - 描述过于模糊

❌ FEAT: ADD NEW STUFF
   - 应该使用小写
   - 描述不专业

❌ fix(game):fixed collision
   - 冒号后需要空格

❌ feat: add new feature.
   - subject 不应以句号结尾

❌ fix(game): Resolve collision detection bug and improve performance
   
   This commit fixes the bug and also makes things faster.
   - Body 描述不够具体
   - 应该分别提交不同目的的改动
```

## 🔧 自动化工具

### Pre-commit Hook

```bash
#!/bin/bash
# .husky/commit-msg

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

PATTERN="^(feat|fix|docs|style|refactor|test|chore)(\([a-z-]+\))?: .+"

if ! echo "$COMMIT_MSG" | grep -qE "$PATTERN"; then
  echo "❌ Invalid commit message format!"
  echo ""
  echo "Expected: <type>(<scope>): <subject>"
  echo ""
  echo "Examples:"
  echo "  ✅ feat(ai): add genetic algorithm"
  echo "  ✅ fix(game): resolve collision bug"
  exit 1
fi
```

### GitHub Actions

```yaml
name: Check Commit Messages

on: [push, pull_request]

jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install commitlint
        run: npm install -g @commitlint/config-conventional
      
      - name: Validate commit messages
        run: |
          npx commitlint --from HEAD~${{ github.event.pull_request.commits }} --to HEAD --verbose
```

### 本地脚本

```bash
#!/bin/bash
# scripts/check-commit.sh

MESSAGE="$1"

if [ -z "$MESSAGE" ]; then
  echo "Usage: ./check-commit.sh '<commit-message>'"
  exit 1
fi

PATTERN="^(feat|fix|docs|style|refactor|test|chore)(\([a-z-]+\))?: .+"

if echo "$MESSAGE" | grep -qE "$PATTERN"; then
  echo "✅ Valid commit message"
  
  # Extract type
  TYPE=$(echo "$MESSAGE" | sed -E 's/^([a-z]+).*/\1/')
  echo "Type: $TYPE"
  
  # Extract scope (if present)
  if echo "$MESSAGE" | grep -qE '\([a-z-]+\)'; then
    SCOPE=$(echo "$MESSAGE" | sed -E 's/^[a-z]+\(([a-z-]+)\).*/\1/')
    echo "Scope: $SCOPE"
  fi
  
  exit 0
else
  echo "❌ Invalid commit message"
  echo ""
  echo "Expected format: <type>(<scope>): <subject>"
  echo ""
  echo "Valid types: feat, fix, docs, style, refactor, test, chore"
  exit 1
fi
```

## 📊 检查清单

在提交前自查：

- [ ] Type 是否正确？(feat/fix/docs/style/refactor/test/chore)
- [ ] Scope 是否具体且小写？
- [ ] Subject 是否使用祈使句？
- [ ] Subject 首字母是否小写？
- [ ] Subject 是否不以句号结尾？
- [ ] 冒号后是否有空格？
- [ ] Body 是否详细说明了改动原因？
- [ ] 是否关联了相关 Issue？
- [ ] 是否有 BREAKING CHANGE（如有必要）？

## 🎓 学习资源

- [Conventional Commits 官网](https://www.conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)
- [Commit Message Best Practices](https://cbea.ms/git-commit/)
- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)

---

**版本**: v1.0.0  
**维护者**: 南风 (nanfeng2021)  
**最后更新**: 2026-04-01
