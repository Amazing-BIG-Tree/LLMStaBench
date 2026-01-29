"""
对外暴露的高层封装，方便在项目中直接调用。
"""

from __future__ import annotations

from typing import Optional, Tuple

from .llm_client import GeminiClient
from .models import AssessmentResult, Question
from .modules import QuestionerPipeline


def generate_question_from_text(
    raw_text: str,
    *,
    api_key: Optional[str] = None,
) -> Tuple[AssessmentResult, Optional[str], Optional[Question]]:
    """
    从一段原始论文文本（可以包含对图表的文字描述）生成一道单项选择题。

    流程：
    1. 模块 A: 适用性评估；
    2. 模块 B: 匿名化与情境重构；
    3. 模块 C: 题目生成（JSON）。

    参数：
    - raw_text: 论文片段或“统计图表 + 描述文本”的文字部分。
    - api_key: 可选。如果不传，则从环境变量 `GEMINI_API_KEY` 读取。
    """
    client = GeminiClient(api_key=api_key) if api_key is not None else GeminiClient()
    pipeline = QuestionerPipeline(client)
    return pipeline.run(raw_text)

