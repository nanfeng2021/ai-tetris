# Tag Naming Skill

## 📋 定义

Git Tag 命名规范，确保版本标签的一致性和可追溯性。

## 🎯 触发场景

- ✅ 发布新版本时
- ✅ 创建预发布版本
- ✅ 标记重要里程碑
- ✅ CI/CD 自动打 Tag

## 📏 Tag 命名格式

### 标准格式

```
v<MAJOR>.<MINOR>.<PATCH>[-<PRERELEASE>]
```

### 组成部分

| 部分 | 说明 | 示例 |
|------|------|------|
| **前缀** | 必须为小写 `v` | `v` |
| **版本号** | 语义化版本 | `5.1.0` |
| **预发布** | 可选，用 `-` 连接 | `-beta.1` |

## ✅ 正确示例

### 正式版本

```bash
✅ v1.0.0          # 首次稳定发布
✅ v5.1.0          # 标准版本
✅ v10.2.3         # 多位数版本号
✅ v123.456.789    # 大版本号
```

### 预发布版本

```bash
✅ v5.0.0-alpha.1      # Alpha 测试版
✅ v5.0.0-beta.1       # Beta 测试版
✅ v5.0.0-rc.1         # Release Candidate
✅ v5.0.0-rc.2         # 第二个 RC
✅ v5.0.0-beta.12      # 第 12 个 beta 版
```

### 带元数据（不推荐但允许）

```bash
✅ v1.0.0+20260401     # 构建日期
✅ v1.0.0+sha.abc123   # 提交 hash
```

## ❌ 错误示例

```bash
❌ 1.0.0           # 缺少 v 前缀
❌ version-1.0.0   # 错误的前缀
❌ Version-1.0.0   # 错误的前缀
❌ V1.0.0          # 应该小写 v
❌ v1.0            # 缺少 PATCH
❌ v1              # 缺少 MINOR 和 PATCH
❌ v1.0.0.1        # 超过 3 位
❌ v1.0.0-beta1    # 缺少点号
❌ v1.0.0.beta.1   # 应该用连字符
❌ release-1.0.0   # 错误的前缀
❌ tags/v1.0.0     # 不应包含 refs/tags/
```

## 🔧 Git Tag 操作

### 创建 Tag

```bash
# 轻量级 Tag (不推荐)
git tag v1.0.0

# 注解型 Tag (推荐)
git tag -a v1.0.0 -m "Release version 1.0.0"

# 详细信息的注解 Tag
git tag -a v1.0.0 -m "Release version 1.0.0

New features:
- Feature 1
- Feature 2

Bug fixes:
- Fix 1
- Fix 2

Closes #123"
```

### 查看 Tag

```bash
# 列出所有 Tag
git tag -l

# 匹配特定模式
git tag -l "v5.*"

# 查看 Tag 详情
git show v1.0.0

# 查看 Tag 的签名
git tag -v v1.0.0
```

### 推送 Tag

```bash
# 推送单个 Tag
git push origin v1.0.0

# 推送所有 Tag
git push origin --tags

# 删除远程 Tag
git push origin --delete v1.0.0
```

### 删除 Tag

```bash
# 删除本地 Tag
git tag -d v1.0.0

# 删除远程 Tag
git push origin :refs/tags/v1.0.0
```

## 🚀 自动化打 Tag 流程

### GitHub Actions 自动打 Tag

```yaml
name: Create Release Tag

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version (e.g., v5.1.0)'
        required: true
        type: string

jobs:
  create-tag:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate version format
        run: |
          if ! echo "${{ github.event.inputs.version }}" | grep -qE "^v[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+(\.[0-9]+)?)?$"; then
            echo "❌ Invalid version format"
            exit 1
          fi
          echo "✅ Valid version: ${{ github.event.inputs.version }}"
      
      - name: Create tag
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git tag -a ${{ github.event.inputs.version }} -m "Release ${{ github.event.inputs.version }}"
          git push origin ${{ github.event.inputs.version }}
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: ${{ github.event.inputs.version }}
          generate_release_notes: true
```

### 基于分支自动打 Tag

```yaml
name: Auto Tag on Release Branch

on:
  push:
    branches:
      - 'release/*'

jobs:
  auto-tag:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Extract version from branch
        id: version
        run: |
          BRANCH_NAME=${GITHUB_REF#refs/heads/}
          VERSION=${BRANCH_NAME#release/}
          echo "version=$VERSION" >> $GITHUB_OUTPUT
      
      - name: Validate and create tag
        run: |
          VERSION="${{ steps.version.outputs.version }}"
          
          # Add 'v' prefix if missing
          if [[ ! $VERSION =~ ^v ]]; then
            VERSION="v$VERSION"
          fi
          
          # Validate format
          if ! echo "$VERSION" | grep -qE "^v[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+(\.[0-9]+)?)?$"; then
            echo "❌ Invalid version format in branch name"
            exit 1
          fi
          
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git tag -a "$VERSION" -m "Auto-tag from release branch"
          git push origin "$VERSION"
```

## 📊 Tag 命名决策树

```
开始
│
├─ 是正式版本？
│  ├─ Yes → vMAJOR.MINOR.PATCH
│  └─ No → 继续
│
├─ 是 Alpha 测试？
│  ├─ Yes → vMAJOR.MINOR.PATCH-alpha.N
│  └─ No → 继续
│
├─ 是 Beta 测试？
│  ├─ Yes → vMAJOR.MINOR.PATCH-beta.N
│  └─ No → 继续
│
├─ 是 Release Candidate?
│  ├─ Yes → vMAJOR.MINOR.PATCH-rc.N
│  └─ No → 检查格式错误
│
└─ 验证通过 → 创建 Tag
```

## 🔍 常见错误及修复

### 错误 1: 忘记 v 前缀

```bash
# ❌ 错误
git tag 1.0.0

# ✅ 修复
git tag -d 1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"
```

### 错误 2: Tag 格式不正确

```bash
# ❌ 错误
git tag version-1.0.0

# ✅ 修复
git tag -d version-1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"
```

### 错误 3: 推送了错误的 Tag

```bash
# 删除本地和远程 Tag
git tag -d v1.0.0-bad
git push origin :refs/tags/v1.0.0-bad

# 重新创建正确的 Tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 📚 最佳实践

1. **始终使用注解型 Tag** - `git tag -a` 比轻量级 Tag 包含更多信息
2. **写有意义的 Tag 信息** - 包含版本亮点和变更摘要
3. **只使用小写 v 前缀** - 保持一致性
4. **不要重复使用 Tag** - 每个 Tag 应该指向唯一的提交
5. **及时推送 Tag** - 创建后立即推送到远程
6. **保护重要 Tag** - 在 GitHub 设置中启用 Tag 保护

## 🎓 参考资源

- [Git Tag Basics](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- [Semantic Versioning](https://semver.org/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

**版本**: v1.0.0  
**维护者**: 南风 (nanfeng2021)  
**最后更新**: 2026-04-01
