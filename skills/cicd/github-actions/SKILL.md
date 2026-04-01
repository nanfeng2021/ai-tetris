# GitHub Actions Skill

## 📋 定义

GitHub Actions 工作流编写规范，确保 CI/CD 流程的一致性、安全性和可维护性。

## 🎯 触发场景

- ✅ 创建新的 CI/CD 工作流
- ✅ 优化现有工作流程
- ✅ 添加新的自动化任务
- ✅ 安全审计和合规检查

## 📏 工作流结构

### 基本格式

```yaml
name: 工作流名称

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 1 * * 1'
  workflow_dispatch:
    inputs:
      param:
        description: '参数说明'
        required: false

env:
  KEY_VARIABLE: value

jobs:
  job-id:
    name: Display Name
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
```

### 触发条件规范

#### Push 事件

```yaml
on:
  push:
    branches:
      - main
      - develop
      - 'release/*'
    tags:
      - 'v*'
    paths:
      - 'src/**'
      - 'tests/**'
    paths-ignore:
      - '**.md'
      - 'docs/**'
```

#### Pull Request 事件

```yaml
on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
    paths:
      - 'src/**'
```

#### 定时任务

```yaml
on:
  schedule:
    # 每周一凌晨 1 点 (UTC)
    - cron: '0 1 * * 1'
    # 每天凌晨 2 点
    - cron: '0 2 * * *'
```

#### 手动触发

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: '部署环境'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production
      debug:
        description: '启用调试模式'
        required: false
        type: boolean
        default: false
```

## 🔧 Job 配置规范

### 基本 Job

```yaml
jobs:
  lint:
    name: 🔍 Code Quality
    runs-on: ubuntu-latest
    timeout-minutes: 15
    
    env:
      PYTHON_VERSION: '3.11'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run linting
        run: |
          black --check src/
          flake8 src/
```

### 依赖 Job

```yaml
jobs:
  test:
    name: 🧪 Unit Tests
    runs-on: ubuntu-latest
    needs: [lint]  # 等待 lint 完成
    
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
        os: [ubuntu-latest, macos-latest]
      fail-fast: false
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Run tests
        run: pytest tests/ --cov=src
```

### 条件执行

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    # 或
    if: startsWith(github.ref, 'refs/tags/v')
    # 或
    if: github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'production'
```

## 📦 常用 Actions

### 官方 Actions

```yaml
steps:
  # 代码检出
  - uses: actions/checkout@v4
    with:
      fetch-depth: 0  # 获取所有历史用于版本计算
  
  # Python 环境
  - uses: actions/setup-python@v5
    with:
      python-version: '3.11'
      cache: 'pip'
  
  # Node.js 环境
  - uses: actions/setup-node@v4
    with:
      node-version: '18'
      cache: 'npm'
  
  # 缓存
  - uses: actions/cache@v4
    with:
      path: ~/.cache/pip
      key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      restore-keys: |
        ${{ runner.os }}-pip-
  
  # 上传产物
  - uses: actions/upload-artifact@v4
    if: always()
    with:
      name: test-results
      path: junit/*.xml
      retention-days: 7
  
  # 下载产物
  - uses: actions/download-artifact@v4
    with:
      name: test-results
      path: ./results
```

### 社区 Actions

```yaml
steps:
  # Docker 构建
  - uses: docker/setup-buildx-action@v3
  - uses: docker/build-push-action@v5
    with:
      push: true
      tags: user/app:latest
  
  # GitHub Release
  - uses: softprops/action-gh-release@v1
    with:
      generate_release_notes: true
  
  # 代码覆盖率
  - uses: codecov/codecov-action@v3
    with:
      file: ./coverage.xml
      flags: unittests
  
  # 发送通知
  - uses: slackapi/slack-github-action@v1
    with:
      payload: |
        {
          "text": "Deployment successful!"
        }
```

## 🔒 安全最佳实践

### 1. 权限最小化

```yaml
permissions:
  contents: read
  packages: write
  security-events: write
```

### 2. 保护 Secrets

```yaml
steps:
  - name: Use secret
    run: echo "Using secret"
    env:
      API_KEY: ${{ secrets.API_KEY }}
  
  # ❌ 错误：不要在日志中打印 secrets
  - run: echo ${{ secrets.API_KEY }}  # 禁止！
  
  # ✅ 正确：使用环境变量
  - run: ./script.sh
    env:
      API_KEY: ${{ secrets.API_KEY }}
```

### 3. 固定 Action 版本

```yaml
# ✅ 正确：使用具体版本
- uses: actions/checkout@v4.1.1

# ❌ 避免：使用 latest tag
- uses: actions/checkout@latest

# ❌ 避免：使用主分支
- uses: actions/checkout@main
```

### 4. 验证 PR 来源

```yaml
on:
  pull_request_target:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    if: github.event.pull_request.head.repo.full_name == github.repository
    steps:
      # 安全地处理 PR
```

## 📊 工作流示例

### 完整 CI/CD Pipeline

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  lint:
    name: 🔍 Code Quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - run: pip install black flake8 isort mypy
      - run: black --check src/ tests/
      - run: isort --check-only src/ tests/
      - run: flake8 src/ tests/
      - run: mypy src/

  test:
    name: 🧪 Unit Tests
    runs-on: ubuntu-latest
    needs: lint
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest tests/ --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3

  security:
    name: 🔒 Security Scan
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python
      - uses: github/codeql-action/analyze@v3

  build:
    name: 🐳 Docker Build
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.event_name == 'push'
    permissions:
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    name: 🚀 Deploy
    runs-on: ubuntu-latest
    needs: build
    if: startsWith(github.ref, 'refs/tags/v')
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Production
        run: ./deploy.sh
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

## 🎓 最佳实践

1. **保持工作流简洁** - 每个 Job 只做一件事
2. **使用矩阵构建** - 并行测试多个环境
3. **缓存依赖** - 加速构建过程
4. **设置超时时间** - 防止无限运行
5. **失败时通知** - 集成 Slack/邮件通知
6. **定期清理产物** - 避免存储溢出
7. **文档化工作流** - 在 README 中说明
8. **测试工作流** - 使用 `workflow_dispatch` 测试

---

**版本**: v1.0.0  
**维护者**: 南风 (nanfeng2021)  
**参考**: [GitHub Actions 官方文档](https://docs.github.com/en/actions)
