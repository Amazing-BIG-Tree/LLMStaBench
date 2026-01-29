from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, Field


class AssessmentResult(BaseModel):
    """模块 A 的评估结果模型。"""

    is_suitable: bool = Field(..., description="该片段是否适合出统计学题")
    missing_info: str = Field(
        "", description="如果不适合或信息不足，这里列出缺失或不清楚的关键信息"
    )
    potential_task: str = Field(
        "", description="基于该片段，大致适合出的题型说明"
    )


class Question(BaseModel):
    """模块 C 生成的单项选择题结构。"""

    stem: str = Field(..., description="题干内容")
    options: Dict[str, str] = Field(
        ...,
        description="四个选项，键通常为 'A'、'B'、'C'、'D'",
        min_length=4,
        max_length=4,
    )
    answer: str = Field(..., description="正确答案的选项 key，例如 'A'")
    analysis: str = Field(..., description="详细解析")

