# Branch Naming Skill

## 📋 定义

Git 分支命名规范，确保分支名称清晰、一致且易于管理。

## 🎯 触发场景

- ✅ 创建新功能分支
- ✅ Bug 修复分支
- ✅ 发布准备分支
- ✅ 紧急修复分支

## 📏 分支命名格式

```
<type>/<description>
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feature` | 新功能开发 | `feature/add-multiplayer` |
| `fix` | Bug 修复 | `fix/collision-detection` |
| `hotfix` | 生产环境紧急修复 | `hotfix/security-patch` |
| `release` | 发布准备 | `release/v5.1.0` |
| `docs` | 文档更新 | `docs/update-readme` |
| `refactor` | 代码重构 | `refactor/harness-validation` |
| `test` | 测试相关 | `test/add-guardrail-tests` |
| `chore` | 其他杂项 | `chore/update-deps` |

### Description 规则

- 使用小写字母
- 单词间用连字符 `-` 连接
- 简洁明了，不超过 3-4 个单词
- 可以包含 Issue 编号

## ✅ 正确示例

```bash
✅ feature/add-multiplayer-mode
✅ fix/collision-detection-bug
✅ hotfix/security-patch-2026
✅ release/v5.1.0
✅ docs/update-installation-guide
✅ refactor/simplify-validator-logic
✅ test/add-edge-case-tests
✅ chore/upgrade-flask-version
✅ feature/game-ui-improvements
✅ fix/issue-123-crash-on-startup
```

## ❌ 错误示例

```bash
❌ my-new-feature      # 缺少 type
❌ Feature/AddStuff    # 应该小写
❌ fix_FixBug          # 应该用连字符
❌ bugfix              # 缺少描述
❌ feature/            # 缺少描述
❌ FEATURE/add-stuff   # type 应该小写
❌ fix/this-is-a-very-long-branch-name-that-is-hard-to-read
                      # 描述太长
```

---

**版本**: v1.0.0  
**维护者**: 南风 (nanfeng2021)
