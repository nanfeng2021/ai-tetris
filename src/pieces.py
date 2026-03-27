"""
俄罗斯方块 - 7 种经典方块定义
每种方块都有独特的形状和颜色
"""
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum

class PieceType(Enum):
    """7 种经典方块类型"""
    I = "I"      # 长条
    O = "O"      # 方块
    T = "T"      # T 型
    S = "S"      # S 型
    Z = "Z"      # Z 型
    J = "J"      # J 型
    L = "L"      # L 型

# 方块颜色 (RGB)
PIECE_COLORS = {
    PieceType.I: (0, 243, 255),   # 青色
    PieceType.O: (255, 243, 0),   # 黄色
    PieceType.T: (170, 0, 255),   # 紫色
    PieceType.S: (0, 255, 65),    # 绿色
    PieceType.Z: (255, 0, 60),    # 红色
    PieceType.J: (0, 0, 255),     # 蓝色
    PieceType.L: (255, 128, 0),   # 橙色
}

# 方块初始形状
PIECE_SHAPES = {
    PieceType.I: [
        [True, True, True, True]
    ],
    PieceType.O: [
        [True, True],
        [True, True]
    ],
    PieceType.T: [
        [False, True, False],
        [True, True, True]
    ],
    PieceType.S: [
        [False, True, True],
        [True, True, False]
    ],
    PieceType.Z: [
        [True, True, False],
        [False, True, True]
    ],
    PieceType.J: [
        [True, False, False],
        [True, True, True]
    ],
    PieceType.L: [
        [False, False, True],
        [True, True, True]
    ],
}

@dataclass
class Piece:
    """方块类"""
    type: PieceType
    shape: List[List[bool]]
    x: int  # 在游戏面板中的 x 坐标
    y: int  # 在游戏面板中的 y 坐标
    color: Tuple[int, int, int]
    
    @classmethod
    def create(cls, piece_type: PieceType) -> 'Piece':
        """创建新方块"""
        return cls(
            type=piece_type,
            shape=[row[:] for row in PIECE_SHAPES[piece_type]],  # 深拷贝
            x=3,  # 初始居中
            y=0,
            color=PIECE_COLORS[piece_type]
        )
    
    def rotate(self) -> List[List[bool]]:
        """顺时针旋转 90 度（不修改原状态）"""
        rows = len(self.shape)
        cols = len(self.shape[0])
        
        # 创建旋转后的新形状
        rotated = [[False for _ in range(rows)] for _ in range(cols)]
        
        for r in range(rows):
            for c in range(cols):
                if self.shape[r][c]:
                    rotated[c][rows - 1 - r] = True
        
        return rotated
    
    def apply_rotation(self):
        """应用旋转到当前方块"""
        self.shape = self.rotate()
    
    def get_cells(self) -> List[Tuple[int, int]]:
        """获取所有单元格的绝对坐标"""
        cells = []
        for row_idx, row in enumerate(self.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    cells.append((self.x + col_idx, self.y + row_idx))
        return cells
    
    @property
    def width(self) -> int:
        """方块宽度"""
        return len(self.shape[0]) if self.shape else 0
    
    @property
    def height(self) -> int:
        """方块高度"""
        return len(self.shape)


class PieceFactory:
    """方块工厂 - 负责生成随机方块"""
    
    def __init__(self):
        self.bag = []  # 使用 bag 系统保证公平性
    
    def get_next_piece(self) -> Piece:
        """获取下一个方块"""
        if not self.bag:
            # 填充 bag（7 种方块各一个）
            self.bag = list(PieceType)
            import random
            random.shuffle(self.bag)
        
        piece_type = self.bag.pop()
        return Piece.create(piece_type)
    
    def reset(self):
        """重置 bag"""
        self.bag = []


def get_all_pieces_info() -> List[dict]:
    """获取所有方块的详细信息"""
    pieces = []
    for piece_type in PieceType:
        piece = Piece.create(piece_type)
        pieces.append({
            'type': piece_type.value,
            'shape': piece.shape,
            'color': piece.color,
            'width': piece.width,
            'height': piece.height
        })
    return pieces


if __name__ == "__main__":
    # 测试代码
    print("🧱 7 种经典俄罗斯方块\n")
    
    factory = PieceFactory()
    
    for i in range(14):  # 显示 14 个方块（2 轮）
        piece = factory.get_next_piece()
        print(f"{i+1:2d}. {piece.type.value:2s} - 颜色：{piece.color} - 尺寸：{piece.width}x{piece.height}")
        
        if i == 6:
            print("\n   (第一轮结束，第二轮开始)\n")
    
    print("\n✅ 方块系统正常！")
