# 🔍 游戏页面无反应 - 问题排查指南

**检查时间**: 2026-03-28  
**状态**: 服务器正常运行 ✅

---

## ✅ 已验证的正常项

1. **后端模块**: Python 导入正常
2. **服务器进程**: 运行中 (端口 5000)
3. **API 端点**: `/api/init` 和 `/api/state` 可访问
4. **HTML 文件**: 存在且语法正确
5. **JavaScript**: 语法检查通过
6. **依赖包**: Flask 和 Flask-CORS 已安装

---

## 🎯 可能的原因和解决方案

### 原因 1: 浏览器缓存旧版本代码 ⭐⭐⭐⭐⭐

**症状**: 页面能加载，但点击按钮没反应

**解决方案**:
```
1. 硬刷新页面:
   - Windows/Linux: Ctrl + Shift + R
   - Mac: Cmd + Shift + R

2. 清除浏览器缓存:
   - Chrome: F12 → Network → Disable cache
   - 或设置 → 隐私 → 清除浏览数据

3. 强制重新加载:
   - 按 F12 打开开发者工具
   - 右键刷新按钮 → "清空缓存并硬性重新加载"
```

---

### 原因 2: JavaScript 运行时错误 ⭐⭐⭐⭐

**症状**: 控制台有红色错误信息

**诊断步骤**:
```
1. 按 F12 打开浏览器开发者工具
2. 切换到 Console (控制台) 标签
3. 刷新页面，查看是否有错误
4. 截图错误信息
```

**常见错误**:
- `Uncaught ReferenceError`: 变量未定义
- `Uncaught TypeError`: 类型错误
- `Failed to fetch`: 网络连接问题

---

### 原因 3: 游戏未初始化 ⭐⭐⭐

**症状**: 页面显示空白或灰色面板

**解决方案**:
```
1. 点击顶部 ▶️ 开始按钮
2. 等待 1-2 秒
3. 如果没反应，查看控制台是否有错误
```

**手动测试 API**:
```javascript
// 在浏览器控制台执行
fetch('/api/init', {method: 'POST'})
  .then(r => r.json())
  .then(d => console.log('Init result:', d))
  .catch(e => console.error('Init failed:', e));
```

---

### 原因 4: 网络请求失败 ⭐⭐⭐

**症状**: 控制台显示 "Failed to fetch" 或 "Network error"

**诊断**:
```
1. F12 → Network (网络) 标签
2. 刷新页面
3. 查看是否有红色的请求
4. 点击请求查看详情
```

**解决方案**:
- 检查浏览器地址是否正确 (http://localhost:5000)
- 确认服务器正在运行
- 检查防火墙设置

---

### 原因 5: Canvas 渲染问题 ⭐⭐

**症状**: 页面布局正常但游戏区域空白

**诊断**:
```javascript
// 在控制台执行
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
console.log('Canvas size:', canvas.width, 'x', canvas.height);
console.log('Context:', ctx);

// 测试绘制
ctx.fillStyle = '#ff0000';
ctx.fillRect(0, 0, 50, 50);
console.log('如果看到红色方块，Canvas 正常');
```

---

### 原因 6: 音效系统阻塞 ⭐

**症状**: 其他都正常，但游戏卡住

**解决方案**:
```javascript
// 在控制台禁用音效
SoundManager.enabled = false;
console.log('音效已禁用，刷新页面重试');
```

---

## 🛠️ 快速修复脚本

在浏览器控制台执行以下代码重置游戏：

```javascript
// 1. 重置所有状态
localStorage.removeItem('tetris_session');
localStorage.removeItem('tetris_init_time');

// 2. 重新初始化游戏
fetch('/api/init', {method: 'POST'})
  .then(r => r.json())
  .then(d => {
    console.log('✅ 游戏已重置:', d);
    location.reload(); // 刷新页面
  })
  .catch(e => console.error('❌ 重置失败:', e));
```

---

## 📋 完整诊断流程

### 步骤 1: 基础检查
```bash
# 服务器是否在运行？
curl http://localhost:5000/api/state

# 预期输出：{"error":"Game not initialized"} 或游戏状态
```

### 步骤 2: 浏览器检查
1. F12 打开开发者工具
2. Console 标签 → 是否有错误？
3. Network 标签 → 请求是否成功（状态码 200）？

### 步骤 3: 功能测试
1. 点击 ▶️ 开始按钮
2. 观察控制台输出
3. 查看 Network 标签中的 /api/init 请求

### 步骤 4: 日志检查
```bash
cd /root/.openclaw/workspace/ai-tetris
tail -f logs/web.log
```

---

## 💡 常见错误及解决方案

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `Game not initialized` | 未点击开始按钮 | 点击 ▶️ 开始 |
| `Failed to fetch` | 服务器未启动 | 运行 `python web/server.py` |
| `AudioContext not allowed` | 浏览器限制自动播放 | 先与页面交互（点击任意处） |
| `Uncaught ReferenceError` | 代码有 bug | 查看具体错误，修复 JS |
| 页面空白 | HTML 加载失败 | 检查服务器日志 |

---

## 🚀 重启服务器（终极方案）

如果以上都没用，重启服务器：

```bash
cd /root/.openclaw/workspace/ai-tetris

# 停止现有进程
pkill -f "web/server.py"

# 清理日志
> logs/web.log

# 重新启动
source venv/bin/activate
nohup python3 web/server.py > logs/web.log 2>&1 &

# 验证
sleep 3
curl http://localhost:5000/api/state
```

---

## 📞 需要帮助？

提供以下信息以便诊断：

1. **浏览器控制台截图** (F12 → Console)
2. **网络请求截图** (F12 → Network)
3. **服务器日志**: `tail -50 logs/web.log`
4. **浏览器版本**: Chrome/Firefox/Safari?
5. **操作系统**: Windows/Mac/Linux?

---

_最后更新：2026-03-28_
