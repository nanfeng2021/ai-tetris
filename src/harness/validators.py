"""
Harness Engineering 验证器
检查游戏状态的一致性和正确性
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"

@dataclass
class ValidationResult:
    status: ValidationStatus
    validator: str
    message: str
    details: Optional[dict] = None

class Validators:
    """游戏状态验证器集合"""
    
    @staticmethod
    def validate_board_dimensions(board: List[List[str]], 
                                  expected_width: int = 10, 
                                  expected_height: int = 20) -> ValidationResult:
        """验证面板尺寸"""
        if len(board) != expected_height:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                validator="board_height",
                message=f"面板高度错误：期望{expected_height}, 实际{len(board)}",
                details={"expected": expected_height, "actual": len(board)}
            )
        
        for i, row in enumerate(board):
            if len(row) != expected_width:
                return ValidationResult(
                    status=ValidationStatus.FAILED,
                    validator="board_width",
                    message=f"第{i}行宽度错误：期望{expected_width}, 实际{len(row)}",
                    details={"row": i, "expected": expected_width, "actual": len(row)}
                )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            validator="board_dimensions",
            message="面板尺寸正确"
        )
    
    @staticmethod
    def validate_piece_shape(piece_shape: List[List[bool]]) -> ValidationResult:
        """验证方块形状合法性"""
        if not piece_shape or not piece_shape[0]:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                validator="piece_shape",
                message="方块形状不能为空",
                details={"shape": piece_shape}
            )
        
        # 检查是否为矩形
        width = len(piece_shape[0])
        for i, row in enumerate(piece_shape):
            if len(row) != width:
                return ValidationResult(
                    status=ValidationStatus.FAILED,
                    validator="piece_shape",
                    message=f"方块形状不规则：第{i}行长度不一致",
                    details={"row": i, "expected": width, "actual": len(row)}
                )
        
        # 检查是否至少有一个方块
        has_block = any(cell for row in piece_shape for cell in row)
        if not has_block:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                validator="piece_shape",
                message="方块必须至少包含一个单元格",
                details={"shape": piece_shape}
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            validator="piece_shape",
            message="方块形状合法"
        )
    
    @staticmethod
    def validate_game_progress(score: int, lines: int, level: int, 
                              elapsed_time: float) -> ValidationResult:
        """验证游戏进度合理性"""
        # 分数不能为负
        if score < 0:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                validator="score_validation",
                message="分数不能为负数",
                details={"score": score}
            )
        
        # 行数不能为负
        if lines < 0:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                validator="lines_validation",
                message="消除行数不能为负数",
                details={"lines": lines}
            )
        
        # 等级必须>=1
        if level < 1:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                validator="level_validation",
                message="等级必须>=1",
                details={"level": level}
            )
        
        # 检查分数与行数的关系（粗略验证）
        # 假设每行至少 100 分
        expected_min_score = lines * 100
        if score < expected_min_score * 0.5:  # 允许 50% 误差
            return ValidationResult(
                status=ValidationStatus.WARNING,
                validator="score_lines_consistency",
                message=f"分数与行数不匹配：{score} < {expected_min_score}",
                details={"score": score, "expected_min": expected_min_score}
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            validator="game_progress",
            message="游戏进度正常",
            details={"score": score, "lines": lines, "level": level}
        )
    
    @staticmethod
    def validate_move_sequence(moves: List[str]) -> ValidationResult:
        """验证移动序列合法性"""
        valid_moves = {'left', 'right', 'down', 'rotate', 'drop'}
        
        for i, move in enumerate(moves):
            if move not in valid_moves:
                return ValidationResult(
                    status=ValidationStatus.FAILED,
                    validator="move_sequence",
                    message=f"非法移动指令：{move}",
                    details={"index": i, "move": move, "valid": list(valid_moves)}
                )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            validator="move_sequence",
            message=f"移动序列合法，共{len(moves)}步"
        )

def run_all_validators(**kwargs) -> List[ValidationResult]:
    """运行所有相关的验证器"""
    results = []
    
    if 'board' in kwargs:
        results.append(Validators.validate_board_dimensions(kwargs['board']))
    
    if 'piece_shape' in kwargs:
        results.append(Validators.validate_piece_shape(kwargs['piece_shape']))
    
    if 'score' in kwargs and 'lines' in kwargs and 'level' in kwargs:
        results.append(Validators.validate_game_progress(
            kwargs['score'], kwargs['lines'], kwargs['level'],
            kwargs.get('elapsed_time', 0)
        ))
    
    if 'moves' in kwargs:
        results.append(Validators.validate_move_sequence(kwargs['moves']))
    
    return results
