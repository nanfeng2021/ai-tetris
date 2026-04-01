# AI Tetris - CI/CD Skills

> CI/CD 流程规范技能集合 - 自动化测试、构建和部署

## 📋 Skills 列表

| Skill | 说明 | 触发场景 |
|-------|------|---------|
| **[github-actions](./github-actions/)** | GitHub Actions 工作流规范 | CI/CD 配置 |
| **[workflow-steps](./workflow-steps/)** | 标准工作流程步骤 | Job 定义 |
| **[artifact-management](./artifact-management/)** | 构建产物管理 | Docker 镜像、Release |
| **[environment-config](./environment-config/)** | 环境配置管理 | 多环境部署 |
| **[security-scan](./security-scan/)** | 安全扫描规范 | CodeQL、依赖审查 |
| **[performance-benchmark](./performance-benchmark/)** | 性能基准测试 | 性能监控 |

## 🎯 使用方式

### 本地测试

```bash
# 运行所有 CI/CD 检查
./scripts/run-cicd-checks.sh

# 单独测试某个 Job
./scripts/test-workflow.sh lint
```

### GitHub Actions 集成

在 `.github/workflows/` 中定义工作流：

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    uses: ./.github/workflows/jobs/lint.yml
  
  test:
    uses: ./.github/workflows/jobs/test.yml
```

## 📚 规范详情

### 1. GitHub Actions 规范

#### 工作流文件结构

```yaml
name: 工作流名称

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 1 * * 1'  # 每周一凌晨 1 点

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'

jobs:
  job-name:
    name: 显示名称
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: 步骤名称
        run: echo "Hello"
```

#### 最佳实践

- ✅ 使用固定版本的 actions (e.g., `@v4`)
- ✅ 设置超时时间 (`timeout-minutes: 30`)
- ✅ 使用缓存加速 (`actions/cache@v4`)
- ✅ 失败时上传产物 (`actions/upload-artifact@v4`)
- ✅ 敏感信息使用 Secrets

### 2. 标准工作流程步骤

#### Code Quality Job

```yaml
lint:
  name: 🔍 Code Quality
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install black flake8 isort mypy
    
    - name: Check formatting
      run: black --check src/ tests/
    
    - name: Check imports
      run: isort --check-only src/ tests/
    
    - name: Lint
      run: flake8 src/ tests/
    
    - name: Type check
      run: mypy src/
```

#### Unit Tests Job

```yaml
test:
  name: 🧪 Unit Tests
  runs-on: ubuntu-latest
  needs: lint
  steps:
    - uses: actions/checkout@v4
    
    - uses: actions/setup-python@v5
    
    - name: Install dependencies
      run: pip install -r requirements.txt pytest pytest-cov
    
    - name: Run tests
      run: pytest tests/ --cov=src --cov-report=xml
    
    - uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 3. 构建产物管理

#### Docker 镜像

```yaml
docker-build:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - uses: docker/setup-buildx-action@v3
    
    - uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: user/app:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

#### GitHub Release

```yaml
release:
  runs-on: ubuntu-latest
  if: startsWith(github.ref, 'refs/tags/')
  steps:
    - uses: actions/checkout@v4
    
    - uses: softprops/action-gh-release@v1
      with:
        generate_release_notes: true
```

### 4. 环境配置

#### 多环境部署

```yaml
deploy:
  runs-on: ubuntu-latest
  needs: test
  environment: 
    name: production
    url: https://example.com
  steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Production
      run: ./deploy.sh
      env:
        API_KEY: ${{ secrets.PROD_API_KEY }}
```

#### 环境变量管理

```yaml
env:
  APP_ENV: production
  LOG_LEVEL: info

jobs:
  deploy:
    environment: production
    steps:
      - run: echo "Deploying to $APP_ENV"
```

### 5. 安全扫描

#### CodeQL

```yaml
codeql:
  runs-on: ubuntu-latest
  permissions:
    security-events: write
  steps:
    - uses: actions/checkout@v4
    
    - uses: github/codeql-action/init@v3
      with:
        languages: python, javascript
    
    - uses: github/codeql-action/analyze@v3
```

#### 依赖审查

```yaml
dependency-review:
  runs-on: ubuntu-latest
  if: github.event_name == 'pull_request'
  steps:
    - uses: actions/checkout@v4
    
    - uses: actions/dependency-review-action@v4
      with:
        fail-on-severity: moderate
```

### 6. 性能基准

```yaml
benchmark:
  runs-on: ubuntu-latest
  if: github.event_name == 'workflow_dispatch'
  steps:
    - uses: actions/checkout@v4
    
    - uses: actions/setup-python@v5
    
    - name: Run benchmarks
      run: pytest tests/ --benchmark-only --benchmark-json=bench.json
    
    - uses: benchmark-action/github-action-benchmark@v1
      with:
        tool: 'pytest'
        output-file-path: bench.json
```

## 🔧 脚本工具

### run-cicd-checks.sh

```bash
#!/bin/bash
# scripts/run-cicd-checks.sh

echo "🔍 Running CI/CD checks..."

# 1. Code Quality
echo "Checking code quality..."
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
mypy src/

# 2. Unit Tests
echo "Running tests..."
pytest tests/ --cov=src

# 3. Build Docker
echo "Building Docker image..."
docker build -t ai-tetris:test .

echo "✅ All CI/CD checks passed!"
```

### test-workflow.sh

```bash
#!/bin/bash
# scripts/test-workflow.sh

WORKFLOW="$1"

if [ -z "$WORKFLOW" ]; then
  echo "Usage: ./test-workflow.sh <workflow-name>"
  exit 1
fi

echo "Testing workflow: $WORKFLOW"

# Simulate GitHub Actions runner
case "$WORKFLOW" in
  lint)
    black --check src/ tests/
    isort --check-only src/ tests/
    flake8 src/ tests/
    ;;
  test)
    pytest tests/ --cov=src
    ;;
  *)
    echo "Unknown workflow: $WORKFLOW"
    exit 1
    ;;
esac
```

## 📖 参考资源

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Awesome Actions](https://github.com/sdras/awesome-actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

---

**维护者**: 南风 (nanfeng2021)  
**最后更新**: 2026-04-01  
**版本**: v1.0.0
