// AI 俄罗斯方块 - 优化版（客户端预测 + 服务端验证）
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const BOARD_WIDTH = 10;
const BOARD_HEIGHT = 20;
const CELL_SIZE = canvas.width / BOARD_WIDTH;

// 方块定义（7 种经典类型）
const PIECE_TYPES = {
    'I': { shape: [[1,1,1,1]], color: [0, 243, 255] },
    'O': { shape: [[1,1],[1,1]], color: [255, 243, 0] },
    'T': { shape: [[0,1,0],[1,1,1]], color: [170, 0, 255] },
    'S': { shape: [[0,1,1],[1,1,0]], color: [0, 255, 65] },
    'Z': { shape: [[1,1,0],[0,1,1]], color: [255, 0, 60] },
    'J': { shape: [[1,0,0],[1,1,1]], color: [0, 0, 255] },
    'L': { shape: [[0,0,1],[1,1,1]], color: [255, 128, 0] }
};

const COLORS = {
    'I': [0, 243, 255],
    'O': [255, 243, 0],
    'T': [170, 0, 255],
    'S': [0, 255, 65],
    'Z': [255, 0, 60],
    'J': [0, 0, 255],
    'L': [255, 128, 0]
};

// 音效管理器
const SoundManager = {

let gameState = null;
let gameLoop = null;
let lastTime = 0;
let dropCounter = 0;
let isPaused = false;
let isGameRunning = false;
let lastRenderedState = null;
let lastMoveTime = 0;
const MOVE_THROTTLE = 80; // 移动节流 (ms) - 降低延迟

// 触摸手势支持
let touchStartX = 0;
let touchStartY = 0;
let touchStartTime = 0;
let touchHandled = false;
const SWIPE_THRESHOLD = 30; // 滑动阈值 (px)
const TAP_THRESHOLD = 10;   // 点击阈值 (px)
const LONG_PRESS_TIME = 300; // 长按时间 (ms)

function getCellSize() {
    return canvas.width / BOARD_WIDTH;
}

// 游戏区域触摸事件（支持滑动手势）
const gameArea = document.getElementById('gameArea');

gameArea.addEventListener('touchstart', (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!isGameRunning || isPaused) return;
    
    const touch = e.touches[0];
    touchStartX = touch.clientX;
    touchStartY = touch.clientY;
    touchStartTime = Date.now();
    touchHandled = false;
}, { passive: false });

gameArea.addEventListener('touchmove', (e) => {
    e.preventDefault();
    e.stopPropagation();
}, { passive: false });

gameArea.addEventListener('touchend', handleTouchGesture, { passive: false });

function handleTouchGesture(e) {
    e.preventDefault();
    e.stopPropagation();
    
    if (!isGameRunning || isPaused) return;
    
    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchStartX;
    const deltaY = touch.clientY - touchStartY;
    const deltaTime = Date.now() - touchStartTime;
    
    // 判断是点击还是滑动
    if (Math.abs(deltaX) < TAP_THRESHOLD && Math.abs(deltaY) < TAP_THRESHOLD && deltaTime < LONG_PRESS_TIME) {
        // 短促点击 = 旋转
        console.log('👆 点击 - 旋转方块');
        sendMove('rotate');
        return;
    }
    
    // 滑动手势
    if (Math.abs(deltaX) > Math.abs(deltaY)) {
        // 水平滑动
        if (deltaX > SWIPE_THRESHOLD) {
            console.log('➡️ 右滑 - 右移');
            sendMove('right');
        } else if (deltaX < -SWIPE_THRESHOLD) {
            console.log('⬅️ 左滑 - 左移');
            sendMove('left');
        }
    } else {
        // 垂直滑动
        if (deltaY > SWIPE_THRESHOLD) {
            console.log('⬇️ 下滑 - 加速下落');
            sendMove('down');
        } else if (deltaY < -SWIPE_THRESHOLD) {
            console.log('⬆️ 上滑 - 旋转方块');
            sendMove('rotate');
        }
    }
}

// 弹窗控制
function showHelpModal() {
    document.getElementById('helpModal').style.display = 'flex';
}

function closeHelpModal(event) {
    if (event.target.id === 'helpModal') {
        document.getElementById('helpModal').style.display = 'none';
    }
}

function closeHelpModalBtn() {
    document.getElementById('helpModal').style.display = 'none';
}

// 按钮触摸处理
function handleTouch(event, action) {
    event.preventDefault();
    event.stopPropagation();
    
    if (action === 'start') {
        initGame();
    } else if (action === 'stop') {
        stopGame();
    } else if (action === 'pause') {
        togglePause();
    } else if (action === 'help') {
        showHelpModal();
    } else if (action === 'sound') {
        const enabled = SoundManager.toggle();
        document.getElementById('soundBtn').textContent = enabled ? '🔊' : '🔇';
    }
}

async function initGame() {
    console.log('🚀 开始初始化游戏...');
    try {
        SoundManager.init();
        console.log('🔊 音效系统已初始化');
        
        const response = await fetch('/api/init', { method: 'POST' });
        console.log('📡 API 响应状态:', response.status);
        
        const data = await response.json();
        console.log('📦 API 返回数据:', data);
        
        if (data.success) {
            if (data.session_id) {
                localStorage.setItem('tetris_session', data.session_id);
                localStorage.setItem('tetris_init_time', Date.now().toString());
                console.log('💾 Session 已保存:', data.session_id);
            }
            
            document.getElementById('gameOver').style.display = 'none';
            document.getElementById('pauseOverlay').style.display = 'none';
            isPaused = false;
            isGameRunning = true;
            lastRenderedState = null;
            
            console.log('✅ 游戏状态已重置');
            console.log('▶️ 启动游戏循环...');
            startGameLoop();
            SoundManager.play('drop');
            
            console.log('🎉 游戏初始化完成！');
        } else {
            console.error('❌ 初始化失败:', data);
        }
    } catch (error) {
        console.error('❌ 初始化异常:', error);
    }
}

function stopGame() {
    if (gameLoop) {
        cancelAnimationFrame(gameLoop);
        gameLoop = null;
    }
    isPaused = false;
    isGameRunning = false;
    document.getElementById('pauseOverlay').style.display = 'none';
}

function togglePause() {
    if (!isGameRunning || !gameState || gameState.game_over) return;
    
    isPaused = !isPaused;
    const pauseOverlay = document.getElementById('pauseOverlay');
    
    if (isPaused) {
        pauseOverlay.style.display = 'block';
        if (gameLoop) {
            cancelAnimationFrame(gameLoop);
            gameLoop = null;
        }
    } else {
        pauseOverlay.style.display = 'none';
        lastTime = performance.now();
        startGameLoop();
    }
}

async function fetchGameState(retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);
            
            const response = await fetch('/api/state', { 
                signal: controller.signal,
                headers: { 'Cache-Control': 'no-cache' }
            });
            clearTimeout(timeoutId);
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            gameState = await response.json();
            return gameState;
        } catch (error) {
            console.warn(`Fetch state failed (attempt ${i+1}/${retries}):`, error.message);
            if (i === retries - 1) {
                console.error('All fetch attempts failed');
                return null;
            }
            await new Promise(resolve => setTimeout(resolve, 100 * Math.pow(2, i)));
        }
    }
    return null;
}

function render(state) {
    const CELL_SIZE = getCellSize();
    
    // 快速检查：先比较简单字段
    if (!lastRenderedState || 
        lastRenderedState.score !== state.score || 
        lastRenderedState.lines !== state.lines ||
        lastRenderedState.level !== state.level ||
        lastRenderedState.game_over !== state.game_over) {
        // 分数/行数/等级变化，需要渲染
    } else if (lastRenderedState.current_piece && state.current_piece &&
        lastRenderedState.current_piece.x === state.current_piece.x &&
        lastRenderedState.current_piece.y === state.current_piece.y &&
        lastRenderedState.current_piece.type === state.current_piece.type) {
        // 方块位置没变，跳过渲染
        return;
    } else if (!lastRenderedState.current_piece && !state.current_piece) {
        // 都没有方块，跳过
        return;
    }
    
    // 深度复制状态用于下次比较
    lastRenderedState = {
        score: state.score,
        lines: state.lines,
        level: state.level,
        game_over: state.game_over,
        current_piece: state.current_piece ? {
            x: state.current_piece.x,
            y: state.current_piece.y,
            type: state.current_piece.type
        } : null
    };
    
    // 清空画布
    ctx.fillStyle = '#0a0a0f';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 绘制网格
    ctx.strokeStyle = '#1e1e32';
    for (let x = 0; x <= BOARD_WIDTH; x++) {
        ctx.beginPath();
        ctx.moveTo(x * CELL_SIZE, 0);
        ctx.lineTo(x * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE);
        ctx.stroke();
    }
    for (let y = 0; y <= BOARD_HEIGHT; y++) {
        ctx.beginPath();
        ctx.moveTo(0, y * CELL_SIZE);
        ctx.lineTo(BOARD_WIDTH * CELL_SIZE, y * CELL_SIZE);
        ctx.stroke();
    }
    
    // 绘制已固定的方块
    if (state.board) {
        for (let y = 0; y < BOARD_HEIGHT; y++) {
            for (let x = 0; x < BOARD_WIDTH; x++) {
                if (state.board[y][x]) {
                    drawCell(x, y, COLORS[state.board[y][x]], CELL_SIZE);
                }
            }
        }
    }
    
    // 绘制当前下落的方块
    if (state.current_piece) {
        const color = COLORS[state.current_piece.type];
        state.current_piece.shape.forEach((row, rowIndex) => {
            row.forEach((cell, colIndex) => {
                if (cell) {
                    const x = state.current_piece.x + colIndex;
                    const y = state.current_piece.y + rowIndex;
                    if (y >= 0) drawCell(x, y, color, CELL_SIZE);
                }
            });
        });
    }
    
    // 检测行数变化
    if (gameState && state.lines > gameState.lines) {
        const linesCleared = state.lines - gameState.lines;
        if (linesCleared > 0) {
            SoundManager.play('clear');
            console.log(`✅ 消除 ${linesCleared} 行`);
        }
    }
    
    // 更新 UI
    document.getElementById('score').textContent = state.score || 0;
}

function drawCell(x, y, color, size) {
    ctx.fillStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
    ctx.fillRect(x * size + 1, y * size + 1, size - 2, size - 2);
    
    ctx.fillStyle = `rgb(${Math.min(255, color[0] + 50)}, ${Math.min(255, color[1] + 50)}, ${Math.min(255, color[2] + 50)})`;
    ctx.fillRect(x * size + 4, y * size + 4, size - 8, size - 8);
}

const COLORS = {
    'I': [0, 243, 255],
    'O': [255, 243, 0],
    'T': [170, 0, 255],
    'S': [0, 255, 65],
    'Z': [255, 0, 60],
    'J': [0, 0, 255],
    'L': [255, 128, 0]
};

async function sendMove(action) {
    if (!isGameRunning || isPaused) return null;
    
    // 节流：防止过快发送请求
    const now = Date.now();
    if (now - lastMoveTime < MOVE_THROTTLE) {
        return null;
    }
    lastMoveTime = now;
    
    try {
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache'
            },
            body: JSON.stringify({ action })
        });
        
        const result = await response.json();
        
        if (result && result.success !== false) {
            // 立即更新本地状态，无需等待下次 fetch
            if (result.state) {
                gameState = result.state;
                render(gameState);
            }
            
            if (action === 'left' || action === 'right' || action === 'down') {
                SoundManager.play('move');
            } else if (action === 'rotate') {
                SoundManager.play('rotate');
            } else if (action === 'drop') {
                SoundManager.play('drop');
            }
        }
        
        return result;
    } catch (error) {
        console.warn('Send move failed:', error.message);
        return null;
    }
}

function startGameLoop() {
    if (gameLoop) cancelAnimationFrame(gameLoop);
    
    lastTime = performance.now();
    dropCounter = 0;
    gameState = null;
    let fetchCounter = 0;
    const FETCH_INTERVAL = 3; // 每 3 次移动 fetch 一次完整状态
    
    console.log('🎮 游戏循环已启动');
    
    function update(time) {
        if (!isGameRunning || isPaused) return;
        
        const deltaTime = time - lastTime;
        lastTime = time;
        
        dropCounter += deltaTime;
        
        const currentDropInterval = Math.max(100, 1000 - ((gameState?.level || 1) - 1) * 100);
        
        if (dropCounter > currentDropInterval) {
            sendMove('down');
            dropCounter = 0;
            fetchCounter++;
            
            // 定期同步完整状态（防止本地状态漂移）
            if (fetchCounter >= FETCH_INTERVAL) {
                fetchGameState().then(state => {
                    if (state) {
                        gameState = state;
                        render(state);
                        if (state.game_over) {
                            console.log('💀 游戏结束');
                            endGame(state);
                        }
                    }
                });
                fetchCounter = 0;
            }
        }
        
        if (isGameRunning && !isPaused) {
            gameLoop = requestAnimationFrame(update);
        }
    }
    
    gameLoop = requestAnimationFrame(update);
}

function endGame(state) {
    isGameRunning = false;
    document.getElementById('finalScore').textContent = state.score || 0;
    document.getElementById('finalLines').textContent = state.lines || 0;
    document.getElementById('finalLevel').textContent = state.level || 1;
    document.getElementById('gameOver').style.display = 'block';
    SoundManager.play('gameOver');
    
    if (gameLoop) {
        cancelAnimationFrame(gameLoop);
        gameLoop = null;
    }
}

// 键盘控制
document.addEventListener('keydown', async (e) => {
    if (!isGameRunning || isPaused || !gameState || gameState.game_over) return;
    
    switch(e.key) {
        case 'ArrowLeft':
            await sendMove('left');
            break;
        case 'ArrowRight':
            await sendMove('right');
            break;
        case 'ArrowUp':
            await sendMove('rotate');
            break;
        case 'ArrowDown':
            await sendMove('down');
            break;
        case ' ':
            await sendMove('drop');
            break;
        case 'p':
        case 'P':
            togglePause();
            break;
    }
});

// 初始渲染空面板
render({
    board: Array(BOARD_HEIGHT).fill().map(() => Array(BOARD_WIDTH).fill(null)),
    score: 0,
    lines: 0,
    level: 1,
    game_over: false,
    current_piece: null
});

console.log('🎮 AI Tetris loaded - Click game area to rotate!');
