"""
StatBench Questioner 模块。

核心功能：
- 模块 A: 数据适用性过滤器 (Data Quality Filter)
- 模块 B: 匿名化与情境重构 (Decontamination & Scenario Reconstruction)
- 模块 C: 题目生成器 (Question Generator)

推荐从 `pipeline.generate_question_from_text` 入口使用。
"""

from .models import AssessmentResult, Question
from .pipeline import generate_question_from_text

__all__ = ["AssessmentResult", "Question", "generate_question_from_text"]

