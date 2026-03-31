// AI 俄罗斯方块 - 客户端预测优化版
// 核心思路：游戏逻辑在客户端运行，服务端仅用于持久化和 AI 功能

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const BOARD_WIDTH = 10;
const BOARD_HEIGHT = 20;
const CELL_SIZE = canvas.width / BOARD_WIDTH;

// 7 种经典方块
const PIECES = {
    'I': { shape: [[1,1,1,1]], color: [0, 243, 255] },
    'O': { shape: [[1,1],[1,1]], color: [255, 243, 0] },
    'T': { shape: [[0,1,0],[1,1,1]], color: [170, 0, 255] },
    'S': { shape: [[0,1,1],[1,1,0]], color: [0, 255, 65] },
    'Z': { shape: [[1,1,0],[0,1,1]], color: [255, 0, 60] },
    'J': { shape: [[1,0,0],[1,1,1]], color: [0, 0, 255] },
    'L': { shape: [[0,0,1],[1,1,1]], color: [255, 128, 0] }
};

const PIECE_KEYS = Object.keys(PIECES);

// 游戏状态
let game = {
    board: null,
    currentPiece: null,
    nextPiece: null,
    score: 0,
    lines: 0,
    level: 1,
    gameOver: false,
    running: false,
    paused: false
};

// 游戏循环控制
let lastTime = 0;
let dropCounter = 0;
let dropInterval = 1000;
let animationId = null;

// 触摸手势
let touchStartX = 0, touchStartY = 0, touchStartTime = 0;
const SWIPE_THRESHOLD = 30;
const TAP_THRESHOLD = 10;

// 音效（简化版）
const SoundManager = {
    enabled: true,
    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    },
    play(name) {
        // 简化：暂不实现
    }
};

// ========== 核心游戏逻辑 ==========

function createEmptyBoard() {
    return Array(BOARD_HEIGHT).fill(null).map(() => Array(BOARD_WIDTH).fill(null));
}

function getRandomPiece() {
    const key = PIECE_KEYS[Math.floor(Math.random() * PIECE_KEYS.length)];
    const piece = PIECES[key];
    return {
        type: key,
        shape: piece.shape.map(row => [...row]),
        color: piece.color,
        x: Math.floor((BOARD_WIDTH - piece.shape[0].length) / 2),
        y: 0
    };
}

function rotatePiece(piece) {
    const rows = piece.shape.length;
    const cols = piece.shape[0].length;
    const rotated = Array(cols).fill(null).map(() => Array(rows).fill(null));
    
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            rotated[c][rows - 1 - r] = piece.shape[r][c];
        }
    }
    return rotated;
}

function isValidPosition(board, piece, offsetX = 0, offsetY = 0) {
    const newShape = piece.shape;
    const newX = piece.x + offsetX;
    const newY = piece.y + offsetY;
    
    for (let row = 0; row < newShape.length; row++) {
        for (let col = 0; col < newShape[row].length; col++) {
            if (newShape[row][col]) {
                const boardX = newX + col;
                const boardY = newY + row;
                
                // 边界检查
                if (boardX < 0 || boardX >= BOARD_WIDTH || boardY >= BOARD_HEIGHT) {
                    return false;
                }
                
                // 碰撞检查（只检查已固定的方块）
                if (boardY >= 0 && board[boardY][boardX]) {
                    return false;
                }
            }
        }
    }
    return true;
}

function mergePieceToBoard(board, piece) {
    const newBoard = board.map(row => [...row]);
    piece.shape.forEach((row, rowIndex) => {
        row.forEach((cell, colIndex) => {
            if (cell) {
                const boardY = piece.y + rowIndex;
                const boardX = piece.x + colIndex;
                if (boardY >= 0 && boardY < BOARD_HEIGHT && boardX >= 0 && boardX < BOARD_WIDTH) {
                    newBoard[boardY][boardX] = piece.type;
                }
            }
        });
    });
    return newBoard;
}

function clearLines(board) {
    let linesCleared = 0;
    const newBoard = [];
    
    for (let y = 0; y < BOARD_HEIGHT; y++) {
        if (!board[y].every(cell => cell !== null)) {
            newBoard.push([...board[y]]);
        } else {
            linesCleared++;
        }
    }
    
    while (newBoard.length < BOARD_HEIGHT) {
        newBoard.unshift(Array(BOARD_WIDTH).fill(null));
    }
    
    return { newBoard, linesCleared };
}

function calculateScore(linesCleared, level) {
    const scores = { 1: 40, 2: 100, 3: 300, 4: 1200 };
    return (scores[linesCleared] || 0) * level;
}

// ========== 游戏操作 ==========

function initGame() {
    game.board = createEmptyBoard();
    game.currentPiece = getRandomPiece();
    game.nextPiece = getRandomPiece();
    game.score = 0;
    game.lines = 0;
    game.level = 1;
    game.gameOver = false;
    game.running = true;
    game.paused = false;
    dropInterval = 1000;
    dropCounter = 0;
    lastTime = 0; // 重置为 0，让第一帧计算正确的 deltaTime
    
    document.getElementById('gameOver').style.display = 'none';
    document.getElementById('pauseOverlay').style.display = 'none';
    
    // 异步通知服务端（非阻塞）
    fetch('/api/init', { method: 'POST' }).catch(() => {});
    
    if (animationId) cancelAnimationFrame(animationId);
    gameLoop();
}

function movePiece(dx, dy) {
    if (!game.running || game.paused || game.gameOver || !game.currentPiece) return false;
    
    if (isValidPosition(game.board, game.currentPiece, dx, dy)) {
        game.currentPiece.x += dx;
        game.currentPiece.y += dy;
        SoundManager.play('move');
        return true;
    }
    return false;
}

function rotateCurrentPiece() {
    if (!game.running || game.paused || game.gameOver || !game.currentPiece) return false;
    
    const rotated = rotatePiece(game.currentPiece);
    const originalShape = game.currentPiece.shape;
    game.currentPiece.shape = rotated;
    
    if (!isValidPosition(game.board, game.currentPiece, 0, 0)) {
        // 旋转失败，尝试踢墙（简单版：左右各试一次）
        if (isValidPosition(game.board, game.currentPiece, 1, 0)) {
            game.currentPiece.x += 1;
        } else if (isValidPosition(game.board, game.currentPiece, -1, 0)) {
            game.currentPiece.x -= 1;
        } else {
            game.currentPiece.shape = originalShape;
            return false;
        }
    }
    
    SoundManager.play('rotate');
    return true;
}

function hardDrop() {
    if (!game.running || game.paused || game.gameOver || !game.currentPiece) return 0;
    
    let distance = 0;
    while (movePiece(0, 1)) {
        distance++;
    }
    lockPiece();
    SoundManager.play('drop');
    return distance;
}

function lockPiece() {
    if (!game.currentPiece) return;
    
    game.board = mergePieceToBoard(game.board, game.currentPiece);
    
    const { newBoard, linesCleared } = clearLines(game.board);
    game.board = newBoard;
    
    if (linesCleared > 0) {
        game.lines += linesCleared;
        game.score += calculateScore(linesCleared, game.level);
        game.level = Math.floor(game.lines / 10) + 1;
        dropInterval = Math.max(100, 1000 - (game.level - 1) * 100);
        SoundManager.play('clear');
    }
    
    // 生成新方块
    game.currentPiece = game.nextPiece;
    game.nextPiece = getRandomPiece();
    
    // 重置下落计数器，让新方块等待一个完整的下落周期
    dropCounter = 0;
    lastTime = performance.now();
    
    // 检查游戏是否结束
    if (!isValidPosition(game.board, game.currentPiece, 0, 0)) {
        game.gameOver = true;
        game.running = false;
        endGame();
    }
}

function gameLoop(time) {
    if (!game.running || game.paused) return;
    
    // 第一帧特殊处理：初始化时间，不更新游戏状态
    if (lastTime === 0) {
        lastTime = time || performance.now();
        dropCounter = 0;
    } else {
        const deltaTime = time - lastTime;
        lastTime = time;
        dropCounter += deltaTime;
        
        // 自动下落
        if (dropCounter > dropInterval) {
            if (!movePiece(0, 1)) {
                lockPiece();
            }
            dropCounter = 0;
        }
    }
    
    render();
    animationId = requestAnimationFrame(gameLoop);
}

// ========== 渲染 ==========

function render() {
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
    if (game.board) {
        for (let y = 0; y < BOARD_HEIGHT; y++) {
            for (let x = 0; x < BOARD_WIDTH; x++) {
                if (game.board[y][x]) {
                    drawCell(x, y, COLORS[game.board[y][x]]);
                }
            }
        }
    }
    
    // 绘制当前方块
    if (game.currentPiece) {
        game.currentPiece.shape.forEach((row, rowIndex) => {
            row.forEach((cell, colIndex) => {
                if (cell) {
                    const x = game.currentPiece.x + colIndex;
                    const y = game.currentPiece.y + rowIndex;
                    if (y >= 0) drawCell(x, y, game.currentPiece.color);
                }
            });
        });
    }
    
    // 更新 UI
    document.getElementById('score').textContent = game.score;
}

function drawCell(x, y, color) {
    ctx.fillStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
    ctx.fillRect(x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2);
    
    ctx.fillStyle = `rgb(${Math.min(255, color[0] + 50)}, ${Math.min(255, color[1] + 50)}, ${Math.min(255, color[2] + 50)})`;
    ctx.fillRect(x * CELL_SIZE + 4, y * CELL_SIZE + 4, CELL_SIZE - 8, CELL_SIZE - 8);
}

// ========== 游戏结束 ==========

function endGame() {
    document.getElementById('finalScore').textContent = game.score;
    document.getElementById('finalLines').textContent = game.lines;
    document.getElementById('finalLevel').textContent = game.level;
    document.getElementById('gameOver').style.display = 'block';
    SoundManager.play('gameOver');
    
    // 异步保存分数到服务端
    fetch('/api/init', { 
        method: 'POST',
        body: JSON.stringify({ score: game.score, lines: game.lines })
    }).catch(() => {});
}

function stopGame() {
    game.running = false;
    game.paused = false;
    if (animationId) cancelAnimationFrame(animationId);
    document.getElementById('pauseOverlay').style.display = 'none';
}

function togglePause() {
    if (!game.running || game.gameOver) return;
    
    game.paused = !game.paused;
    const pauseOverlay = document.getElementById('pauseOverlay');
    
    if (game.paused) {
        pauseOverlay.style.display = 'block';
        if (animationId) cancelAnimationFrame(animationId);
    } else {
        pauseOverlay.style.display = 'none';
        lastTime = performance.now();
        gameLoop();
    }
}

// ========== 输入处理 ==========

const gameArea = document.getElementById('gameArea');

gameArea.addEventListener('touchstart', (e) => {
    e.preventDefault();
    if (!game.running || game.paused) return;
    
    const touch = e.touches[0];
    touchStartX = touch.clientX;
    touchStartY = touch.clientY;
    touchStartTime = Date.now();
}, { passive: false });

gameArea.addEventListener('touchmove', (e) => {
    e.preventDefault();
}, { passive: false });

gameArea.addEventListener('touchend', (e) => {
    e.preventDefault();
    if (!game.running || game.paused) return;
    
    const touch = e.changedTouches[0];
    const deltaX = touch.clientX - touchStartX;
    const deltaY = touch.clientY - touchStartY;
    const deltaTime = Date.now() - touchStartTime;
    
    // 点击 = 旋转
    if (Math.abs(deltaX) < TAP_THRESHOLD && Math.abs(deltaY) < TAP_THRESHOLD && deltaTime < 300) {
        rotateCurrentPiece();
        return;
    }
    
    // 滑动手势
    if (Math.abs(deltaX) > Math.abs(deltaY)) {
        if (deltaX > SWIPE_THRESHOLD) movePiece(1, 0);
        else if (deltaX < -SWIPE_THRESHOLD) movePiece(-1, 0);
    } else {
        if (deltaY > SWIPE_THRESHOLD) movePiece(0, 1);
        else if (deltaY < -SWIPE_THRESHOLD) rotateCurrentPiece();
    }
}, { passive: false });

gameArea.onclick = () => {
    if (game.running && !game.paused) {
        rotateCurrentPiece();
    }
};

// 键盘控制
document.addEventListener('keydown', (e) => {
    if (!game.running || game.paused || game.gameOver) return;
    
    switch(e.key) {
        case 'ArrowLeft': movePiece(-1, 0); break;
        case 'ArrowRight': movePiece(1, 0); break;
        case 'ArrowUp': rotateCurrentPiece(); break;
        case 'ArrowDown': movePiece(0, 1); break;
        case ' ': hardDrop(); break;
        case 'p': case 'P': togglePause(); break;
    }
});

// 按钮处理
function handleTouch(event, action) {
    event.preventDefault();
    if (action === 'start') initGame();
    else if (action === 'stop') stopGame();
    else if (action === 'pause') togglePause();
    else if (action === 'help') showHelpModal();
    else if (action === 'sound') {
        const enabled = SoundManager.toggle();
        document.getElementById('soundBtn').textContent = enabled ? '🔊' : '🔇';
    }
}

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

// 初始化渲染
render();
console.log('🎮 AI Tetris Optimized - Client-side prediction enabled!');
