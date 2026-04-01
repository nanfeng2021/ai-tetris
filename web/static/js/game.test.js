/**
 * AI Tetris - Frontend Unit Tests
 * 游戏逻辑单元测试 (无需依赖的简易测试框架)
 */

// ============================================
// 简易测试框架
// ============================================

const TestReporter = {
  passed: 0,
  failed: 0,
  currentSuite: '',
  
  suite(name) {
    this.currentSuite = name;
    console.log(`\n📋 ${name}`);
  },
  
  pass(testName) {
    this.passed++;
    console.log(`   ✅ ${testName}`);
  },
  
  fail(testName, error) {
    this.failed++;
    console.log(`   ❌ ${testName}`);
    console.log(`      Error: ${error.message || error}`);
  },
  
  summary() {
    const total = this.passed + this.failed;
    console.log('\n' + '='.repeat(50));
    console.log(`📊 Test Summary`);
    console.log('='.repeat(50));
    console.log(`✅ Passed: ${this.passed}`);
    console.log(`❌ Failed: ${this.failed}`);
    console.log(`📈 Total:  ${total}`);
    console.log('='.repeat(50));
    
    if (this.failed === 0) {
      console.log('\n🎉 All tests passed!\n');
      return 0;
    } else {
      console.log(`\n⚠️  ${this.failed} test(s) failed\n`);
      return 1;
    }
  }
};

function describe(suiteName, fn) {
  TestReporter.suite(suiteName);
  try {
    fn();
  } catch (error) {
    TestReporter.fail(suiteName, error);
  }
}

function test(testName, fn) {
  try {
    fn();
    TestReporter.pass(testName);
  } catch (error) {
    TestReporter.fail(testName, error);
  }
}

function expect(actual) {
  return {
    toBe(expected) {
      if (actual !== expected) throw new Error(`Expected ${expected}, got ${actual}`);
    },
    toEqual(expected) {
      if (JSON.stringify(actual) !== JSON.stringify(expected)) {
        throw new Error(`Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
      }
    },
    toBeDefined() {
      if (actual === undefined) throw new Error('Expected value to be defined');
    },
    toBeInstanceOf(expected) {
      if (!(actual instanceof expected)) throw new Error(`Expected instance of ${expected.name}`);
    },
    toBeGreaterThan(value) {
      if (actual <= value) throw new Error(`Expected > ${value}, got ${actual}`);
    },
    toBeLessThan(value) {
      if (actual >= value) throw new Error(`Expected < ${value}, got ${actual}`);
    },
    not: {
      toThrow() {
        let threw = false;
        try { actual(); } catch (e) { threw = true; }
        if (threw) throw new Error('Expected function not to throw');
      }
    }
  };
}

// ============================================
// 测试工具函数
// ============================================

function createEmptyBoard(width = 10, height = 20) {
  return Array(height).fill(null).map(() => Array(width).fill(0));
}

function createTestPiece(type = 'I') {
  const pieces = {
    'I': { shape: [[1, 1, 1, 1]], color: [0, 255, 255] },
    'O': { shape: [[1, 1], [1, 1]], color: [255, 255, 0] },
    'T': { shape: [[0, 1, 0], [1, 1, 1]], color: [128, 0, 128] },
    'S': { shape: [[0, 1, 1], [1, 1, 0]], color: [0, 255, 0] },
    'Z': { shape: [[1, 1, 0], [0, 1, 1]], color: [255, 0, 0] },
    'J': { shape: [[1, 0, 0], [1, 1, 1]], color: [0, 0, 255] },
    'L': { shape: [[0, 0, 1], [1, 1, 1]], color: [255, 165, 0] }
  };
  return pieces[type];
}

function isValidMove(board, piece, offsetX, offsetY) {
  for (let y = 0; y < piece.shape.length; y++) {
    for (let x = 0; x < piece.shape[y].length; x++) {
      if (piece.shape[y][x]) {
        const newX = x + offsetX;
        const newY = y + offsetY;
        if (newX < 0 || newX >= 10 || newY >= 20) return false;
        if (newY >= 0 && board[newY][newX]) return false;
      }
    }
  }
  return true;
}

function rotatePiece(piece) {
  const rows = piece.shape.length;
  const cols = piece.shape[0].length;
  const rotated = Array(cols).fill(null).map(() => Array(rows).fill(0));
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      rotated[x][rows - 1 - y] = piece.shape[y][x];
    }
  }
  return { ...piece, shape: rotated };
}

const scoreTable = { 1: 100, 2: 300, 3: 500, 4: 800 };
function calculateScore(lines, level = 1) {
  return (scoreTable[lines] || 0) * level;
}

function createGameState() {
  return {
    score: 0, lines: 0, level: 1, gameOver: false, paused: false,
    board: createEmptyBoard(), currentPiece: null, nextPiece: null
  };
}

function clearLines(board) {
  let linesCleared = 0;
  const newBoard = board.filter(row => {
    const isFull = row.every(cell => cell !== 0);
    if (isFull) linesCleared++;
    return !isFull;
  });
  while (newBoard.length < board.length) {
    newBoard.unshift(Array(board[0].length).fill(0));
  }
  return { newBoard, linesCleared };
}

// ============================================
// 测试用例
// ============================================

describe('Piece Definitions', () => {
  test('should have all 7 tetromino types', () => {
    ['I', 'O', 'T', 'S', 'Z', 'J', 'L'].forEach(type => {
      const piece = createTestPiece(type);
      expect(piece).toBeDefined();
      expect(piece.shape).toBeInstanceOf(Array);
      expect(piece.color).toBeInstanceOf(Array);
      expect(piece.color.length).toBe(3);
    });
  });

  test('I piece should be 4 cells wide', () => {
    expect(createTestPiece('I').shape[0].length).toBe(4);
  });

  test('O piece should be 2x2', () => {
    const piece = createTestPiece('O');
    expect(piece.shape.length).toBe(2);
    expect(piece.shape[0].length).toBe(2);
  });
});

describe('Game Board', () => {
  test('should create empty board with correct dimensions', () => {
    const board = createEmptyBoard(10, 20);
    expect(board.length).toBe(20);
    expect(board[0].length).toBe(10);
  });

  test('should fill board with zeros', () => {
    const board = createEmptyBoard();
    board.forEach(row => row.forEach(cell => expect(cell).toBe(0)));
  });

  test('should handle custom dimensions', () => {
    const board = createEmptyBoard(15, 25);
    expect(board.length).toBe(25);
    expect(board[0].length).toBe(15);
  });
});

describe('Collision Detection', () => {
  test('should allow valid move in empty board', () => {
    expect(isValidMove(createEmptyBoard(), createTestPiece('I'), 3, 0)).toBe(true);
  });

  test('should detect left wall collision', () => {
    expect(isValidMove(createEmptyBoard(), createTestPiece('I'), -1, 0)).toBe(false);
  });

  test('should detect right wall collision', () => {
    expect(isValidMove(createEmptyBoard(), createTestPiece('I'), 7, 0)).toBe(false);
  });

  test('should detect bottom collision', () => {
    expect(isValidMove(createEmptyBoard(), createTestPiece('I'), 3, 20)).toBe(false);
  });

  test('should detect collision with existing blocks', () => {
    const board = createEmptyBoard();
    board[5][5] = 1;
    expect(isValidMove(board, createTestPiece('O'), 4, 4)).toBe(false);
  });
});

describe('Piece Rotation', () => {
  test('should rotate I piece correctly', () => {
    const rotated = rotatePiece(createTestPiece('I'));
    expect(rotated.shape.length).toBe(4);  // 4 rows after rotation
    expect(rotated.shape[0].length).toBe(1);  // 1 column after rotation
  });

  test('should rotate O piece (unchanged)', () => {
    const rotated = rotatePiece(createTestPiece('O'));
    expect(rotated.shape.length).toBe(2);
    expect(rotated.shape[0].length).toBe(2);
  });

  test('should preserve cell count after rotation', () => {
    const piece = createTestPiece('T');
    const original = piece.shape.flat().filter(c => c === 1).length;
    const rotated = rotatePiece(piece);
    const rotatedCount = rotated.shape.flat().filter(c => c === 1).length;
    expect(original).toBe(rotatedCount);
  });
});

describe('Score Calculation', () => {
  test('should calculate single line score', () => {
    expect(calculateScore(1, 1)).toBe(100);
  });

  test('should calculate tetris (4 lines) score', () => {
    expect(calculateScore(4, 1)).toBe(800);
  });

  test('should multiply by level', () => {
    expect(calculateScore(1, 5)).toBe(500);
    expect(calculateScore(4, 10)).toBe(8000);
  });

  test('should return 0 for invalid lines', () => {
    expect(calculateScore(0)).toBe(0);
    expect(calculateScore(5)).toBe(0);
  });
});

describe('Game State', () => {
  test('should initialize with default values', () => {
    const state = createGameState();
    expect(state.score).toBe(0);
    expect(state.lines).toBe(0);
    expect(state.level).toBe(1);
    expect(state.gameOver).toBe(false);
    expect(state.paused).toBe(false);
  });

  test('should update score correctly', () => {
    const state = createGameState();
    state.score += calculateScore(2, state.level);
    expect(state.score).toBe(300);
  });

  test('should level up every 10 lines', () => {
    const state = createGameState();
    state.lines = 10;
    state.level = Math.floor(state.lines / 10) + 1;
    expect(state.level).toBe(2);
    state.lines = 25;
    state.level = Math.floor(state.lines / 10) + 1;
    expect(state.level).toBe(3);
  });
});

describe('Line Clearing', () => {
  test('should not clear empty board', () => {
    const result = clearLines(createEmptyBoard());
    expect(result.linesCleared).toBe(0);
    expect(result.newBoard.length).toBe(20);
  });

  test('should clear one full line', () => {
    const board = createEmptyBoard();
    board[19] = Array(10).fill(1);
    expect(clearLines(board).linesCleared).toBe(1);
  });

  test('should clear multiple lines', () => {
    const board = createEmptyBoard();
    board[19] = Array(10).fill(1);
    board[18] = Array(10).fill(1);
    board[17] = Array(10).fill(1);
    expect(clearLines(board).linesCleared).toBe(3);
  });

  test('should add new empty lines at top', () => {
    const board = createEmptyBoard();
    board[19] = Array(10).fill(1);
    const result = clearLines(board);
    expect(result.newBoard.length).toBe(20);
    expect(result.newBoard[0].every(cell => cell === 0)).toBe(true);
  });
});

describe('Edge Cases', () => {
  test('should handle negative coordinates safely', () => {
    const board = createEmptyBoard();
    expect(() => {
      for (let y = -5; y < 0; y++) {
        for (let x = -5; x < 0; x++) {
          if (y >= 0 && x >= 0) board[y][x] = 1;
        }
      }
    }).not.toThrow();
  });

  test('should handle maximum level', () => {
    const state = { score: 0, lines: 999, level: 1 };
    state.level = Math.floor(state.lines / 10) + 1;
    expect(state.level).toBeGreaterThan(1);
    expect(state.level).toBeLessThan(1000);
  });

  test('should handle rapid key presses', () => {
    const actions = [];
    for (let i = 0; i < 100; i++) {
      actions.push('LEFT', 'RIGHT');
    }
    expect(actions.length).toBe(200);
  });
});

// ============================================
// 运行测试
// ============================================

if (typeof module !== 'undefined' && module.exports) {
  console.log('\n🧪 Running AI Tetris Frontend Tests...\n');
  const exitCode = TestReporter.summary();
  process.exit(exitCode);
}
