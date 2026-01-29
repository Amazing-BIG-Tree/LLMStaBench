"""
StatBench Questioner 模块。

核心功能：
- 模块 A: 数据适用性过滤器 (Data Quality Filter)
- 模块 B: 匿名化与情境重构 (Decontamination & Scenario Reconstruction)
- 模块 C: 题目生成器 (Question Generator)

推荐从 `pipeline.generate_question_from_text` 入口使用。

基于 OpenAI API 格式，兼容所有支持该格式的服务：
- OpenAI 官方服务（GPT-4、GPT-3.5 等）
- 国内大模型服务（通义千问、文心一言、智谱 GLM 等）
- 本地部署的模型服务（vLLM、Ollama 等）

支持灵活的模型配置，可通过 `ModelConfig` 类或直接参数自定义。
"""

from .config import (
    ModelConfig,
    get_default_config_from_json,
    load_configs_from_json,
)
from .llm_client import LLMClient, OpenAIClient
from .models import AssessmentResult, Question
from .pipeline import generate_question_from_text

__all__ = [
    "AssessmentResult",
    "Question",
    "generate_question_from_text",
    "ModelConfig",
    "load_configs_from_json",
    "get_default_config_from_json",
    "LLMClient",
    "OpenAIClient",
]

