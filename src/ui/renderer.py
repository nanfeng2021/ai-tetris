"""
Pygame 图形渲染器
提供现代化的游戏界面
"""
import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from pieces import PieceType, PIECE_COLORS, BOARD_WIDTH, BOARD_HEIGHT

# 颜色定义
COLORS = {
    'background': (10, 10, 20),
    'grid': (30, 30, 50),
    'text': (255, 255, 255),
    'neon_cyan': (0, 243, 255),
    'neon_pink': (255, 0, 255),
    'neon_green': (0, 255, 65),
}

# 单元格大小
CELL_SIZE = 30
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 50

# 信息面板位置
INFO_PANEL_X = GRID_OFFSET_X + BOARD_WIDTH * CELL_SIZE + 30


class GameRenderer:
    """游戏渲染器"""
    
    def __init__(self, board):
        self.board = board
        self.screen = None
        self.clock = None
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        
    def init(self):
        """初始化 Pygame"""
        pygame.init()
        
        # 计算窗口尺寸
        width = INFO_PANEL_X + 250
        height = GRID_OFFSET_Y + BOARD_HEIGHT * CELL_SIZE + 50
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AI 俄罗斯方块 - Harness Engineering")
        
        self.clock = pygame.time.Clock()
        
        # 加载字体
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        print(f"✅ Pygame 初始化成功：{width}x{height}")
    
    def render(self):
        """渲染一帧"""
        # 清屏
        self.screen.fill(COLORS['background'])
        
        # 绘制网格背景
        self._draw_grid()
        
        # 绘制已锁定的方块
        self._draw_locked_pieces()
        
        # 绘制当前方块
        if self.board.current_piece:
            self._draw_current_piece()
        
        # 绘制下一个方块
        self._draw_next_piece()
        
        # 绘制信息面板
        self._draw_info_panel()
        
        # 绘制游戏结束提示
        if self.board.game_over:
            self._draw_game_over()
        
        # 更新显示
        pygame.display.flip()
    
    def _draw_grid(self):
        """绘制网格"""
        for x in range(BOARD_WIDTH + 1):
            pygame.draw.line(
                self.screen,
                COLORS['grid'],
                (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y),
                (GRID_OFFSET_X + x * CELL_SIZE, GRID_OFFSET_Y + BOARD_HEIGHT * CELL_SIZE),
                1
            )
        
        for y in range(BOARD_HEIGHT + 1):
            pygame.draw.line(
                self.screen,
                COLORS['grid'],
                (GRID_OFFSET_X, GRID_OFFSET_Y + y * CELL_SIZE),
                (GRID_OFFSET_X + BOARD_WIDTH * CELL_SIZE, GRID_OFFSET_Y + y * CELL_SIZE),
                1
            )
        
        # 绘制边框
        pygame.draw.rect(
            self.screen,
            COLORS['neon_cyan'],
            (GRID_OFFSET_X - 2, GRID_OFFSET_Y - 2,
             BOARD_WIDTH * CELL_SIZE + 4, BOARD_HEIGHT * CELL_SIZE + 4),
            2
        )
    
    def _draw_locked_pieces(self):
        """绘制已锁定的方块"""
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board.board[y][x]:
                    piece_type = self.board.board[y][x]
                    color = PIECE_COLORS.get(PieceType(piece_type), COLORS['text'])
                    self._draw_cell(x, y, color)
    
    def _draw_current_piece(self):
        """绘制当前方块"""
        piece = self.board.current_piece
        color = piece.color
        
        for cell_x, cell_y in piece.get_cells():
            if 0 <= cell_y < BOARD_HEIGHT and 0 <= cell_x < BOARD_WIDTH:
                self._draw_cell(cell_x, cell_y, color)
    
    def _draw_cell(self, x, y, color):
        """绘制单个单元格"""
        rect = pygame.Rect(
            GRID_OFFSET_X + x * CELL_SIZE + 1,
            GRID_OFFSET_Y + y * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2
        )
        
        # 填充
        pygame.draw.rect(self.screen, color, rect)
        
        # 高光效果
        highlight_rect = pygame.Rect(
            GRID_OFFSET_X + x * CELL_SIZE + 3,
            GRID_OFFSET_Y + y * CELL_SIZE + 3,
            CELL_SIZE - 6,
            CELL_SIZE - 6
        )
        lighter_color = tuple(min(255, c + 50) for c in color)
        pygame.draw.rect(self.screen, lighter_color, highlight_rect)
    
    def _draw_next_piece(self):
        """绘制下一个方块预览"""
        # 标题
        title = self.font_medium.render("NEXT", True, COLORS['text'])
        self.screen.blit(title, (INFO_PANEL_X, GRID_OFFSET_Y))
        
        if self.board.next_piece:
            piece = self.board.next_piece
            color = piece.color
            
            # 计算居中位置
            preview_size = max(piece.width, piece.height)
            start_x = INFO_PANEL_X + (100 - preview_size * CELL_SIZE) // 2
            start_y = GRID_OFFSET_Y + 50
            
            for row_idx, row in enumerate(piece.shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(
                            start_x + col_idx * CELL_SIZE,
                            start_y + row_idx * CELL_SIZE,
                            CELL_SIZE - 2,
                            CELL_SIZE - 2
                        )
                        pygame.draw.rect(self.screen, color, rect)
    
    def _draw_info_panel(self):
        """绘制信息面板"""
        y_offset = GRID_OFFSET_Y + 200
        
        # 分数
        score_text = self.font_medium.render("SCORE", True, COLORS['neon_cyan'])
        self.screen.blit(score_text, (INFO_PANEL_X, y_offset))
        
        score_value = self.font_large.render(str(self.board.score), True, COLORS['text'])
        self.screen.blit(score_value, (INFO_PANEL_X, y_offset + 40))
        
        # 行数
        y_offset += 120
        lines_text = self.font_medium.render("LINES", True, COLORS['neon_green'])
        self.screen.blit(lines_text, (INFO_PANEL_X, y_offset))
        
        lines_value = self.font_large.render(str(self.board.lines), True, COLORS['text'])
        self.screen.blit(lines_value, (INFO_PANEL_X, y_offset + 40))
        
        # 等级
        y_offset += 120
        level_text = self.font_medium.render("LEVEL", True, COLORS['neon_pink'])
        self.screen.blit(level_text, (INFO_PANEL_X, y_offset))
        
        level_value = self.font_large.render(str(self.board.level), True, COLORS['text'])
        self.screen.blit(level_value, (INFO_PANEL_X, y_offset + 40))
        
        # 操作说明
        y_offset += 120
        controls = [
            "Controls:",
            "← → : Move",
            "↑ : Rotate",
            "↓ : Soft Drop",
            "Space : Hard Drop",
            "P : Pause",
            "Q : Quit"
        ]
        
        for i, line in enumerate(controls):
            text = self.font_small.render(line, True, COLORS['text'])
            self.screen.blit(text, (INFO_PANEL_X, y_offset + i * 25))
    
    def _draw_game_over(self):
        """绘制游戏结束"""
        # 半透明遮罩
        overlay = pygame.Surface((BOARD_WIDTH * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (GRID_OFFSET_X, GRID_OFFSET_Y))
        
        # GAME OVER 文字
        game_over_text = self.font_large.render("GAME OVER", True, COLORS['neon_pink'])
        text_rect = game_over_text.get_rect(center=(
            GRID_OFFSET_X + BOARD_WIDTH * CELL_SIZE // 2,
            GRID_OFFSET_Y + BOARD_HEIGHT * CELL_SIZE // 2 - 30
        ))
        self.screen.blit(game_over_text, text_rect)
        
        # 最终分数
        final_score = self.font_medium.render(
            f"Score: {self.board.score}",
            True,
            COLORS['text']
        )
        score_rect = final_score.get_rect(center=(
            GRID_OFFSET_X + BOARD_WIDTH * CELL_SIZE // 2,
            GRID_OFFSET_Y + BOARD_HEIGHT * CELL_SIZE // 2 + 30
        ))
        self.screen.blit(final_score, score_rect)
    
    def get_events(self):
        """处理事件"""
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append(('quit', None))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    events.append(('left', None))
                elif event.key == pygame.K_RIGHT:
                    events.append(('right', None))
                elif event.key == pygame.K_UP:
                    events.append(('rotate', None))
                elif event.key == pygame.K_DOWN:
                    events.append(('down', None))
                elif event.key == pygame.K_SPACE:
                    events.append(('drop', None))
                elif event.key == pygame.K_p:
                    events.append(('pause', None))
                elif event.key == pygame.K_q:
                    events.append(('quit', None))
        
        return events
    
    def tick(self, fps=60):
        """控制帧率"""
        self.clock.tick(fps)
    
    def cleanup(self):
        """清理 Pygame"""
        pygame.quit()
        print("✅ Pygame 已清理")


if __name__ == "__main__":
    # 测试代码
    from board import GameBoard
    from harness.monitors import Monitors
    
    monitor = Monitors(game_id="render_test")
    board = GameBoard(monitor)
    board.spawn_piece()
    
    renderer = GameRenderer(board)
    renderer.init()
    
    running = True
    while running:
        events = renderer.get_events()
        for event_type, _ in events:
            if event_type == 'quit':
                running = False
            elif event_type == 'left':
                board.move_piece(-1, 0)
            elif event_type == 'right':
                board.move_piece(1, 0)
            elif event_type == 'rotate':
                board.rotate_piece()
            elif event_type == 'down':
                board.move_piece(0, 1)
        
        renderer.render()
        renderer.tick(60)
    
    renderer.cleanup()
