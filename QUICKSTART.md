# 🚀 快速开始指南

## 🌐 Web 版本（推荐 - 浏览器可玩）

### 1. 安装依赖

```bash
cd ai-tetris

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 启动 Web 服务器

```bash
# 方式一：直接启动
./venv/bin/python web/server.py

# 方式二：使用管理脚本
./scripts/start-web.sh start
```

### 3. 访问游戏

打开浏览器访问：**http://localhost:5000**

### 4. 外部访问（可选）

```bash
# 启动 Cloudflare 隧道
cloudflared tunnel --url http://localhost:5000
```

会生成一个 `https://xxx.trycloudflare.com` 的临时公网地址。

---

## 🎨 Pygame GUI 版本

```bash
# 确保已安装 pygame
pip install pygame

# 启动 GUI 版本（待实现 gui.py 入口）
python src/ui/gui.py
```

---

## 💻 终端版本

```bash
# 人工模式
./venv/bin/python src/game.py --mode human --speed 1.0

# AI 模式（围观 AI 自己玩）
./venv/bin/python src/game.py --mode ai --speed 0.5
```

---

## 🐳 Docker 部署（生产环境）

```bash
# 一键启动（游戏 + Prometheus + Grafana）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 访问服务
- 游戏：http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (密码：admin)

# 停止服务
docker-compose down
```

---

## 🎮 操作说明

### Web 版本 / Pygame GUI

| 按键 | 功能 |
|------|------|
| ← → | 左右移动 |
| ↑ | 旋转方块 |
| ↓ | 加速下落 |
| Space | 直接掉落到底 |
| P | 暂停/继续 |
| Q | 退出游戏 |

### 终端版本

输入方向单词：`left`, `right`, `down`, `rotate`, `drop`

---

## 📊 监控指标

访问 `http://localhost:9090/metrics` 查看 Prometheus 格式指标：

- `tetris_games_total` - 游戏次数
- `tetris_lines_cleared_total` - 消除行数
- `tetris_current_score` - 当前分数
- `tetris_ai_decision_seconds` - AI 决策延迟
- `tetris_guardrail_triggers_total` - Guardrail 触发统计

---

## 🛠️ 开发模式

```bash
# 运行测试
pytest tests/ -v

# 查看测试覆盖率
pytest tests/ --cov=src --cov-report=html

# 代码格式化
black src/ tests/
```

---

## 📱 移动端适配

Web 版本已支持响应式设计，可在手机浏览器中访问，但推荐使用键盘操作以获得最佳体验。

---

## ❓ 常见问题

### Q: 端口被占用怎么办？
A: 修改 `web/server.py` 中的端口号，或使用 `--port` 参数。

### Q: 如何修改游戏速度？
A: 启动时添加 `--speed` 参数，值越小速度越快（秒/格）。

### Q: AI 太笨了怎么办？
A: 调整 `src/ai/agent.py` 中的权重配置，或使用强化学习训练。

### Q: 如何查看实时日志？
A: 使用 `./scripts/start-web.sh logs` 或 `tail -f logs/web_server.log`

---

**🎮 Happy Gaming!**
