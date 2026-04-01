# AI Tetris - Code Specification Skills

> 代码规范技能集合 - 确保项目质量和一致性

## 📋 Skills 列表

| Skill | 说明 | 触发场景 |
|-------|------|---------|
| **[commit-message](./commit-message/)** | Commit Message 规范检查 | 提交代码时 |
| **[versioning](./versioning/)** | 语义化版本命名规范 | 发布新版本时 |
| **[tag-naming](./tag-naming/)** | Git Tag 命名规范 | 创建 Tag 时 |
| **[branch-naming](./branch-naming/)** | 分支命名规范 | 创建分支时 |
| **[code-review](./code-review/)** | Code Review 检查清单 | PR/MR 审查时 |
| **[harness-compliance](./harness-compliance/)** | Harness Engineering 合规检查 | 代码审查时 |

## 🎯 使用方式

### 本地使用

```bash
# 运行所有规范检查
./scripts/check-specs.sh

# 单独检查 commit message
./scripts/check-commit.sh "feat: add new feature"

# 检查版本号格式
./scripts/check-version.sh "v5.1.0"
```

### CI/CD 集成

在 GitHub Actions 中自动执行：

```yaml
- name: Check Code Specifications
  run: |
    ./scripts/check-specs.sh --all
```

### Pre-commit Hook

```bash
# 安装 pre-commit hooks
npm install -g @commitlint/cli husky
npx husky install

# 添加 commit message 检查
npx husky add .husky/commit-msg 'npx --no -- commitlint -e $GIT_PARAMS'
```

## 📚 规范详情

### 1. Commit Message 规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具配置

**示例**:
```bash
✅ feat(ai): add genetic algorithm for decision optimization
✅ fix(game): resolve collision detection bug
❌ Added new stuff
❌ Fixed bug
```

### 2. 版本命名规范

遵循 [Semantic Versioning 2.0.0](https://semver.org/)：

```
MAJOR.MINOR.PATCH
```

**规则**:
- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复

**示例**:
```bash
✅ v5.1.0     # 新功能
✅ v5.0.1     # Bug 修复
✅ v6.0.0     # 破坏性变更
✅ v5.0.0-beta.1  # 预发布版本
❌ 5.1        # 缺少 PATCH
❌ v5.1       # 缺少 PATCH
```

### 3. Tag 命名规范

```
v<MAJOR>.<MINOR>.<PATCH>[-<PRERELEASE>]
```

**规则**:
- 必须以 `v` 开头
- 遵循语义化版本
- 预发布版本用 `-` 连接

**示例**:
```bash
✅ v5.1.0
✅ v5.0.0-beta.1
✅ v5.0.0-rc.2
❌ 5.1.0      # 缺少 v
❌ version-5.1.0  # 格式错误
```

### 4. 分支命名规范

```
<type>/<description>
```

**Type 类型**:
- `feature`: 新功能
- `fix`: Bug 修复
- `hotfix`: 紧急修复
- `release`: 发布准备
- `docs`: 文档更新
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 其他

**示例**:
```bash
✅ feature/add-multiplayer-mode
✅ fix/collision-detection-bug
✅ hotfix/security-patch
✅ release/v5.1.0
❌ my-new-feature  # 缺少 type
❌ feature/Add_New_Feature  # 应该用小写和连字符
```

### 5. Code Review 检查清单

#### 代码质量
- [ ] 代码通过所有测试
- [ ] 新增测试覆盖新功能
- [ ] 无 lint 错误
- [ ] 类型检查通过
- [ ] 代码格式化符合规范

#### Harness Engineering
- [ ] Guardrails 覆盖率 100%
- [ ] Validators 覆盖率 100%
- [ ] Monitors 指标完整
- [ ] 错误处理完善

#### 文档
- [ ] README 已更新
- [ ] CHANGELOG 已更新
- [ ] API 文档同步
- [ ] 注释清晰准确

#### 安全
- [ ] 无硬编码敏感信息
- [ ] 输入验证完善
- [ ] 依赖项安全审查通过

### 6. Harness Engineering 合规检查

#### Guardrails (约束规则)
```python
✅ def validate_move(board, piece, x, y):
       if not is_within_bounds(x, y):
           return False, "Move out of bounds"
       return True, "Valid move"

❌ def move(piece, x, y):  # 缺少验证
       piece.x = x
       piece.y = y
```

#### Validators (验证器)
```python
✅ def validate_game_state(state):
       assert state.score >= 0
       assert state.level > 0

❌ # 缺少状态验证
```

#### Monitors (监控器)
```python
✅ GAME_DURATION.observe(duration)
   LINES_CLEARED.labels(level=level).inc()

❌ # 缺少监控指标
```

## 🔧 脚本工具

### check-specs.sh

运行所有规范检查：

```bash
#!/bin/bash
# scripts/check-specs.sh

echo "🔍 Running code specification checks..."

# 1. Check commit messages
echo "Checking commit messages..."
git log --oneline -10 | while read commit; do
  if ! echo "$commit" | grep -qE "^(feat|fix|docs|style|refactor|test|chore)\("; then
    echo "❌ Invalid commit message: $commit"
    exit 1
  fi
done
echo "✅ Commit messages OK"

# 2. Check version format
if [ -f "web/package.json" ]; then
  VERSION=$(node -p "require('./web/package.json').version")
  if ! echo "$VERSION" | grep -qE "^v?[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+(\.[0-9]+)?)?$"; then
    echo "❌ Invalid version format: $VERSION"
    exit 1
  fi
  echo "✅ Version format OK ($VERSION)"
fi

# 3. Check branch naming
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "develop" ]; then
  if ! echo "$BRANCH" | grep -qE "^(feature|fix|hotfix|release|docs|refactor|test|chore)/"; then
    echo "⚠️  Warning: Branch name doesn't follow convention: $BRANCH"
  else
    echo "✅ Branch naming OK"
  fi
fi

echo "✅ All specification checks passed!"
```

### check-commit.sh

验证单个 commit message：

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
  exit 0
else
  echo "❌ Invalid commit message"
  echo ""
  echo "Expected format: <type>(<scope>): <subject>"
  echo ""
  echo "Examples:"
  echo "  ✅ feat(ai): add genetic algorithm"
  echo "  ✅ fix(game): resolve collision bug"
  echo "  ❌ Added new stuff"
  exit 1
fi
```

### check-version.sh

验证版本号格式：

```bash
#!/bin/bash
# scripts/check-version.sh

VERSION="$1"

if [ -z "$VERSION" ]; then
  echo "Usage: ./check-version.sh '<version>'"
  exit 1
fi

PATTERN="^v?[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+(\.[0-9]+)?)?$"

if echo "$VERSION" | grep -qE "$PATTERN"; then
  echo "✅ Valid version format"
  exit 0
else
  echo "❌ Invalid version format: $VERSION"
  echo ""
  echo "Expected format: MAJOR.MINOR.PATCH[-prerelease]"
  echo ""
  echo "Examples:"
  echo "  ✅ v5.1.0"
  echo "  ✅ 5.0.1"
  echo "  ✅ v5.0.0-beta.1"
  echo "  ❌ 5.1"
  echo "  ❌ version-5.1.0"
  exit 1
fi
```

## 📖 参考资源

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Harness Engineering Practice Guide](https://my.feishu.cn/docx/Ko7sdF8fIoxME7xJWCGc96YVnJb)

---

**维护者**: 南风 (nanfeng2021)  
**最后更新**: 2026-04-01  
**版本**: v1.0.0
