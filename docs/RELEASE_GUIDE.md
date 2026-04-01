# 📦 发布指南 - AI Tetris

本指南说明如何发布新版本到 GitHub 和 Docker Hub。

---

## 📋 目录

- [版本命名规范](#版本命名规范)
- [发布前检查清单](#发布前检查清单)
- [发布流程](#发布流程)
- [发布后验证](#发布后验证)
- [紧急回滚](#紧急回滚)

---

## 🏷️ 版本命名规范

遵循 [Semantic Versioning 2.0.0](https://semver.org/)：

```
MAJOR.MINOR.PATCH
```

### 版本号说明

| 类型 | 说明 | 示例 | 何时使用 |
|------|------|------|---------|
| **MAJOR** | 不兼容的 API 变更 | v6.0.0 | 架构重构、API 破坏性变更 |
| **MINOR** | 向后兼容的功能新增 | v5.1.0 | 新功能、新特性 |
| **PATCH** | 向后兼容的问题修复 | v5.0.1 | Bug 修复、性能优化 |

### 预发布版本

```
v5.0.0-alpha.1    # 内部测试版
v5.0.0-beta.1     # 公开测试版
v5.0.0-rc.1       # 候选发布版
```

---

## ✅ 发布前检查清单

### 代码质量

- [ ] 所有测试通过 (`pytest tests/ -v`)
- [ ] 测试覆盖率达标 (Guardrails/Validators 100%)
- [ ] 代码格式化检查通过 (`black --check src/`)
- [ ] 无 lint 错误 (`flake8 src/ tests/`)
- [ ] 类型检查通过 (`mypy src/`)

### 文档更新

- [ ] CHANGELOG.md 已更新
- [ ] README.md 版本号已更新
- [ ] 相关文档已同步更新
- [ ] API 文档（如有变更）已更新

### 功能验证

- [ ] 人工模式测试通过
- [ ] AI 模式测试通过
- [ ] Web 版本测试通过
- [ ] 移动端适配验证
- [ ] 监控指标正常

### CI/CD

- [ ] GitHub Actions 全部通过
- [ ] Docker 构建成功
- [ ] CodeQL 无严重警告
- [ ] 依赖审查通过

---

## 🚀 发布流程

### 1. 更新版本号

在 `web/package.json` 中更新版本号：

```json
{
  "name": "ai-tetris-web",
  "version": "5.1.0"  // 更新这里
}
```

### 2. 更新 CHANGELOG.md

编辑 `CHANGELOG.md`，将 `[Unreleased]` 改为新版本号：

```markdown
## [5.1.0] - 2026-04-01

### Added
- ✨ 新功能描述
- 🎯 新增的特性

### Changed
- 🔄 改进的内容

### Fixed
- ✅ Bug 修复列表
```

### 3. 提交变更

```bash
# 切换到 main 分支
git checkout main

# 拉取最新代码
git pull origin main

# 添加所有变更
git add .

# 提交（遵循 Conventional Commits）
git commit -m "chore(release): prepare v5.1.0

- Update CHANGELOG.md
- Bump version to 5.1.0
- Update documentation"
```

### 4. 推送并创建 Tag

```bash
# 推送到远程
git push origin main

# 创建 Git tag
git tag -a v5.1.0 -m "Release version 5.1.0

New features:
- Feature 1 description
- Feature 2 description

Bug fixes:
- Fix 1 description
- Fix 2 description"

# 推送 tag
git push origin v5.1.0
```

### 5. 触发自动发布

推送 tag 后，GitHub Actions 会自动：

1. ✅ 运行所有测试
2. ✅ 构建 Docker 镜像
3. ✅ 推送到 Docker Hub
4. ✅ 创建 GitHub Release

**监控进度**: https://github.com/nanfeng2021/ai-tetris/actions

---

## 🔍 发布后验证

### 1. 检查 GitHub Release

访问：https://github.com/nanfeng2021/ai-tetris/releases

确认：
- ✅ Release Notes 正确
- ✅ 资产（Assets）完整
- ✅ Tag 关联正确

### 2. 检查 Docker Hub

访问：https://hub.docker.com/r/nanfeng2021/ai-tetris

确认：
- ✅ 新 tag 已推送
- ✅ `latest` tag 已更新
- ✅ 镜像大小合理

### 3. 测试部署

```bash
# 拉取新镜像
docker pull nanfeng2021/ai-tetris:5.1.0

# 运行测试
docker run --rm -p 5000:5000 nanfeng2021/ai-tetris:5.1.0

# 访问 http://localhost:5000 验证
```

### 4. 验证监控

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- 确认指标正常上报

---

## 🔄 紧急回滚

如果发布后发现问题，立即回滚：

### 1. 回滚 Docker 部署

```bash
# 停止当前容器
docker-compose down

# 启动旧版本
docker-compose up -d nanfeng2021/ai-tetris:5.0.0
```

### 2. 删除有问题的 Tag

```bash
# 删除本地 tag
git tag -d v5.1.0

# 删除远程 tag
git push origin :refs/tags/v5.1.0

# 强制推送 main 分支到上一个稳定版本
git checkout main
git reset --hard v5.0.0
git push origin main --force
```

### 3. 通知用户

在 GitHub Issues 和 Release 页面发布回滚公告：

```markdown
## ⚠️ 回滚通知

由于发现严重问题，v5.1.0 已回滚到 v5.0.0。

问题描述：[简要说明]
预计修复时间：[时间]
临时解决方案：[方案]
```

---

## 📊 发布频率建议

| 类型 | 频率 | 说明 |
|------|------|------|
| **PATCH** | 每周 | Bug 修复、小优化 |
| **MINOR** | 每月 | 新功能、特性增强 |
| **MAJOR** | 按需 | 架构升级、重大变更 |

---

## 🎯 自动化发布脚本

可以使用以下脚本简化发布流程：

```bash
#!/bin/bash
# scripts/release.sh

VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Usage: ./release.sh <version>"
  echo "Example: ./release.sh 5.1.0"
  exit 1
fi

echo "🚀 Releasing version $VERSION..."

# 1. 更新版本号
sed -i "s/\"version\": \".*\"/\"version\": \"$VERSION\"/" web/package.json

# 2. 提交
git add .
git commit -m "chore(release): prepare v$VERSION"
git push origin main

# 3. 创建 tag
git tag -a v$VERSION -m "Release version $VERSION"
git push origin v$VERSION

echo "✅ Release v$VERSION completed!"
echo "📊 Monitor: https://github.com/nanfeng2021/ai-tetris/actions"
```

使用方式：

```bash
chmod +x scripts/release.sh
./scripts/release.sh 5.1.0
```

---

## 🤖 CI/CD 配置说明

GitHub Actions 会自动处理：

1. **代码质量检查**: Black, flake8, mypy
2. **单元测试**: pytest + 覆盖率
3. **Harness 验证**: Guardrails/Validators 100% 覆盖
4. **前端测试**: JavaScript 单元测试
5. **Docker 构建**: 多平台镜像
6. **安全扫描**: CodeQL, 依赖审查
7. **自动发布**: Docker Hub + GitHub Release

配置文件：
- `.github/workflows/ci-cd.yml` - 主 CI/CD 流程
- `.github/workflows/codeql.yml` - 安全分析
- `.github/workflows/dependency-review.yml` - 依赖审查

---

## 📞 需要帮助？

遇到问题时：

1. 查看 [Troubleshooting Guide](TROUBLESHOOTING.md)
2. 检查 GitHub Actions 日志
3. 在 Issues 中提问
4. 联系维护者 @nanfeng2021

---

**Happy Releasing! 🎉**

[[reply_to_current]]
