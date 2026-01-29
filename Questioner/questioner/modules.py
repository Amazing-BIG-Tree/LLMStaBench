"""
三个核心子模块的具体实现：
- 模块 A: 数据适用性过滤器
- 模块 B: 匿名化与情境重构
- 模块 C: 题目生成器
"""

from __future__ import annotations

from typing import Optional

from .llm_client import LLMClient
from .models import AssessmentResult, Question
from .prompts import (
    SYSTEM_PROMPT_ASSESS,
    SYSTEM_PROMPT_DECONTAMINATE,
    SYSTEM_PROMPT_GENERATE,
)


class DataQualityFilter:
    """模块 A: 判断文本片段是否适合出题。"""

    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def assess(self, raw_text: str) -> AssessmentResult:
        """
        调用 LLM，对 `raw_text` 进行评估，返回 `AssessmentResult`。
        """
        payload = raw_text.strip()
        json_result = self._client.generate_structured_json(
            system_prompt=SYSTEM_PROMPT_ASSESS,
            user_content=payload,
        )
        return AssessmentResult.model_validate(json_result)


class ScenarioRewriter:
    """模块 B: 匿名化与情境重构。"""

    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def rewrite(self, raw_text: str) -> str:
        """
        对原始论文片段做去方法名、去统计量符号等“去污染”处理，并重写为题干背景。
        """
        payload = raw_text.strip()
        cleaned_context = self._client.generate_text(
            system_prompt=SYSTEM_PROMPT_DECONTAMINATE,
            user_content=payload,
        )
        return cleaned_context


class QuestionGenerator:
    """模块 C: 在 `Cleaned_Context` 基础上生成单选题 JSON。"""

    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def generate(self, cleaned_context: str) -> Question:
        """
        基于已经匿名化的研究场景描述生成标准单选题。
        """
        payload = cleaned_context.strip()
        json_result = self._client.generate_structured_json(
            system_prompt=SYSTEM_PROMPT_GENERATE,
            user_content=payload,
        )
        return Question.model_validate(json_result)


class QuestionerPipeline:
    """
    将三个子模块串联起来的流水线：

    1. 先用 DataQualityFilter 判断是否适合出题；
    2. 如果适合，则用 ScenarioRewriter 做匿名化与情境重构；
    3. 最后用 QuestionGenerator 生成标准单选题 JSON。
    """

    def __init__(self, client: LLMClient) -> None:
        """
        初始化流水线。

        参数：
        - client: 实现了 `LLMClient` 接口的客户端实例（如 `OpenAIClient`）。
        """
        self._client = client
        self.filter = DataQualityFilter(self._client)
        self.rewriter = ScenarioRewriter(self._client)
        self.generator = QuestionGenerator(self._client)

    def run(self, raw_text: str) -> tuple[AssessmentResult, Optional[str], Optional[Question]]:
        """
        整体执行一次流水线。

        返回：
        - assessment: 模块 A 评估结果
        - cleaned_context: 若通过则为重写后的题干背景，否则为 None
        - question: 若通过则为生成的单选题，否则为 None
        """
        assessment = self.filter.assess(raw_text)
        if not assessment.is_suitable:
            return assessment, None, None

        cleaned_context = self.rewriter.rewrite(raw_text)
        question = self.generator.generate(cleaned_context)
        return assessment, cleaned_context, question

