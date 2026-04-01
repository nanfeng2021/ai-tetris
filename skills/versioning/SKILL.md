# Versioning Skill

## 📋 定义

语义化版本命名规范，遵循 [Semantic Versioning 2.0.0](https://semver.org/) 标准。

## 🎯 触发场景

- ✅ 发布新版本时
- ✅ 更新 `package.json` 或 `pyproject.toml`
- ✅ 创建 Git Tag
- ✅ 编写 CHANGELOG
- ✅ Docker 镜像标签管理

## 📏 版本号格式

```
MAJOR.MINOR.PATCH[-PRERELEASE]
```

### 版本号组成

| 部分 | 说明 | 何时递增 |
|------|------|---------|
| **MAJOR** (主版本号) | 重大变更 | 不兼容的 API 变更 |
| **MINOR** (次版本号) | 功能新增 | 向后兼容的功能 |
| **PATCH** (修订号) | 问题修复 | 向后兼容的 Bug 修复 |
| **PRERELEASE** (预发布) | 测试版本 | 可选，用于 alpha/beta/rc |

### 递增规则

```
初始开发版：0.1.0
首次发布：1.0.0

新功能 → MINOR+1:  1.0.0 → 1.1.0
Bug 修复 → PATCH+1: 1.1.0 → 1.1.1
破坏性变更 → MAJOR+1: 1.1.1 → 2.0.0
```

## ✅ 正确示例

### 正式版本

```bash
✅ v1.0.0      # 首次稳定发布
✅ v1.2.3      # 标准版本号
✅ v5.1.0      # 新功能发布
✅ v5.0.1      # Bug 修复
✅ v6.0.0      # 破坏性变更
```

### 预发布版本

```bash
✅ v5.0.0-alpha.1    # 内部测试版 1
✅ v5.0.0-alpha.2    # 内部测试版 2
✅ v5.0.0-beta.1     # 公开测试版 1
✅ v5.0.0-beta.2     # 公开测试版 2
✅ v5.0.0-rc.1       # 候选发布版 1
✅ v5.0.0-rc.2       # 候选发布版 2
```

### 带构建元数据

```bash
✅ v1.0.0+20260401        # 带构建日期
✅ v1.0.0+sha.5114f85     # 带提交 hash
✅ v1.0.0-alpha.1+exp.sha.5114f85  # 完整格式
```

## ❌ 错误示例

```bash
❌ 5.1           # 缺少 PATCH
❌ v5.1          # 缺少 PATCH
❌ version-5.1.0 # 前缀错误
❌ 5.1.0.1       # 超过 3 位（不含预发布）
❌ v1.0          # 缺少 PATCH
❌ 1.0.0-beta    # 预发布应有编号
❌ v1.0.0-beta1  # 缺少点号
❌ V1.0.0        # 应该小写 v
```

## 🚀 版本发布流程

### 1. 确定版本类型

**问自己**:
- 是否有破坏性变更？ → **MAJOR**
- 是否新增向后兼容的功能？ → **MINOR**
- 是否只是 Bug 修复？ → **PATCH**

### 2. 更新版本号

**Python 项目** (`pyproject.toml`):
```toml
[project]
version = "5.1.0"
```

**Node.js 项目** (`package.json`):
```json
{
  "version": "5.1.0"
}
```

### 3. 更新 CHANGELOG

```markdown
## [5.1.0] - 2026-04-01

### Added
- ✨ New feature description

### Changed
- 🔄 Improved existing functionality

### Fixed
- ✅ Bug fix description
```

### 4. 提交并打 Tag

```bash
# 提交版本变更
git add .
git commit -m "chore(release): prepare v5.1.0"

# 创建 annotated tag
git tag -a v5.1.0 -m "Release version 5.1.0

New features:
- Feature 1
- Feature 2

Bug fixes:
- Fix 1
- Fix 2"

# 推送
git push origin main
git push origin v5.1.0
```

## 📊 版本决策树

```
开始
│
├─ 有破坏性变更？
│  └─ Yes → MAJOR++ (v6.0.0)
│  └─ No → 继续
│
├─ 有新功能？
│  └─ Yes → MINOR++ (v5.1.0)
│  └─ No → 继续
│
├─ 有 Bug 修复？
│  └─ Yes → PATCH++ (v5.0.1)
│  └─ No → 不需要发版
│
└─ 是测试版？
   └─ Yes → 添加预发布标签 (v5.1.0-beta.1)
```

## 🔧 自动化工具

### 版本检查脚本

```bash
#!/bin/bash
# scripts/check-version.sh

VERSION="$1"

if [ -z "$VERSION" ]; then
  echo "Usage: ./check-version.sh '<version>'"
  exit 1
fi

# 语义化版本正则
PATTERN="^v?[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+(\.[0-9]+)?)?(\+[a-zA-Z0-9.]+)?$"

if echo "$VERSION" | grep -qE "$PATTERN"; then
  echo "✅ Valid version format: $VERSION"
  
  # 解析版本号
  if [[ $VERSION =~ ^v?([0-9]+)\.([0-9]+)\.([0-9]+)(-(.+))?$ ]]; then
    MAJOR="${BASH_REMATCH[1]}"
    MINOR="${BASH_REMATCH[2]}"
    PATCH="${BASH_REMATCH[3]}"
    PRERELEASE="${BASH_REMATCH[5]}"
    
    echo "  MAJOR: $MAJOR"
    echo "  MINOR: $MINOR"
    echo "  PATCH: $PATCH"
    [ -n "$PRERELEASE" ] && echo "  PRERELEASE: $PRERELEASE"
  fi
  
  exit 0
else
  echo "❌ Invalid version format: $VERSION"
  echo ""
  echo "Expected: MAJOR.MINOR.PATCH[-prerelease][+build]"
  echo ""
  echo "Examples:"
  echo "  ✅ v5.1.0"
  echo "  ✅ 5.0.1"
  echo "  ✅ v5.0.0-beta.1"
  echo "  ✅ 1.0.0+build.123"
  exit 1
fi
```

### 自动版本升级脚本

```bash
#!/bin/bash
# scripts/bump-version.sh

BUMP_TYPE="$1"  # major, minor, or patch

if [ -z "$BUMP_TYPE" ]; then
  echo "Usage: ./bump-version.sh <major|minor|patch>"
  exit 1
fi

# 获取当前版本
CURRENT_VERSION=$(node -p "require('./web/package.json').version" 2>/dev/null || \
                  grep '^version' pyproject.toml | cut -d'"' -f2)

if [ -z "$CURRENT_VERSION" ]; then
  echo "❌ Could not detect current version"
  exit 1
fi

# 去除 'v' 前缀
CURRENT_VERSION=${CURRENT_VERSION#v}

# 解析版本号
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# 递增版本号
case "$BUMP_TYPE" in
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    ;;
  patch)
    PATCH=$((PATCH + 1))
    ;;
  *)
    echo "❌ Invalid bump type: $BUMP_TYPE"
    echo "Valid types: major, minor, patch"
    exit 1
    ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"

echo "Current version:  $CURRENT_VERSION"
echo "New version:      $NEW_VERSION"
echo ""
read -p "Continue? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  # 更新 package.json
  if [ -f "web/package.json" ]; then
    sed -i "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" web/package.json
    echo "✅ Updated web/package.json"
  fi
  
  # 更新 pyproject.toml
  if [ -f "pyproject.toml" ]; then
    sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    echo "✅ Updated pyproject.toml"
  fi
  
  # 提交变更
  git add .
  git commit -m "chore(release): bump version to v$NEW_VERSION"
  
  echo ""
  echo "✅ Version bumped to v$NEW_VERSION"
  echo "Run 'git push' to publish"
else
  echo "Aborted"
fi
```

### GitHub Actions 自动版本管理

```yaml
name: Release

on:
  workflow_dispatch:
    inputs:
      bump_type:
        description: 'Version bump type'
        required: true
        default: 'patch'
        type: choice
        options:
          - major
          - minor
          - patch

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Bump version
        run: |
          npm install -g standard-version
          npx standard-version --release-as ${{ github.event.inputs.bump_type }}
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: v${{ env.NEW_VERSION }}
          generate_release_notes: true
```

## 📚 版本发布策略

### 快速发布周期

适合敏捷开发：

```
周一: v5.1.0-alpha.1   (内部测试)
周三: v5.1.0-beta.1    (公开测试)
周五: v5.1.0-rc.1      (候选发布)
下周一: v5.1.0         (正式发布)
```

### 长期支持 (LTS)

```
v5.0.0 (LTS) - 支持 2 年
  ├─ v5.0.1 (Bug 修复)
  ├─ v5.0.2 (Bug 修复)
  └─ v5.1.0 (新功能，非 LTS)

v6.0.0 (LTS) - 下一代 LTS
```

### 并行版本

```
Stable: v5.1.0
Beta:   v6.0.0-beta.1
Alpha:  v7.0.0-alpha.1
```

## 🎓 最佳实践

1. **从 1.0.0 开始** - 首个稳定版本应该是 1.0.0，不是 0.1.0
2. **不要跳过版本号** - 按顺序递增，不要从 1.0.0 直接到 2.0.0
3. **预发布要编号** - beta.1, beta.2, 不是 beta1, beta2
4. **BUILD 元数据不参与比较** - 1.0.0+build1 == 1.0.0+build2
5. **破坏性变更必须升 MAJOR** - 这是 semver 的核心
6. **文档同步更新** - 每个版本都要更新 CHANGELOG

---

**版本**: v1.0.0  
**维护者**: 南风 (nanfeng2021)  
**最后更新**: 2026-04-01
