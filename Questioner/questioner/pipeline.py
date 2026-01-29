"""
对外暴露的高层封装，方便在项目中直接调用。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Tuple

from .config import ModelConfig
from .llm_client import LLMClient, OpenAIClient
from .models import AssessmentResult, Question
from .modules import QuestionerPipeline


def _load_default_config():
    """
    从项目根目录的 config.py 文件加载默认配置。
    如果文件不存在或加载失败，返回 None。
    """
    try:
        # 尝试从项目根目录加载 config.py
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config.py"
        
        if config_path.exists():
            # 动态导入配置模块
            import importlib.util
            spec = importlib.util.spec_from_file_location("user_config", config_path)
            if spec and spec.loader:
                config_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config_module)
                
                # 读取配置变量
                model_name = getattr(config_module, "MODEL_NAME", None)
                api_key = getattr(config_module, "API_KEY", None)
                base_url = getattr(config_module, "BASE_URL", None)
                
                if model_name:
                    return ModelConfig(
                        model_name=model_name,
                        api_key=api_key,
                        base_url=base_url if base_url else None,
                    )
    except Exception:
        # 如果加载失败，静默返回 None，使用其他方式
        pass
    return None


def generate_question_from_text(
    raw_text: str,
    *,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    config: Optional[ModelConfig] = None,
    client: Optional[LLMClient] = None,
) -> Tuple[AssessmentResult, Optional[str], Optional[Question]]:
    """
    从一段原始论文文本（可以包含对图表的文字描述）生成一道单项选择题。

    流程：
    1. 模块 A: 适用性评估；
    2. 模块 B: 匿名化与情境重构；
    3. 模块 C: 题目生成（JSON）。

    参数：
    - raw_text: 论文片段或"统计图表 + 描述文本"的文字部分。
    - model_name: 模型名称。必须指定（除非使用 `config` 或 `client` 参数）。
        例如 "gpt-4", "qwen-plus", "glm-4" 等。
    - api_key: API Key。如果不传，则从环境变量 `OPENAI_API_KEY` 读取。
    - base_url: API 基础 URL。用于指定不同的 API 端点：
        - OpenAI 官方: 默认（无需指定）
        - 国内大模型: 如 "https://dashscope.aliyuncs.com/compatible-mode/v1"（通义千问）
        - 本地服务: 如 "http://localhost:8000/v1"
    - config: 使用 `ModelConfig` 对象配置模型。如果提供此参数，将忽略 `model_name`、`api_key`、`base_url`。
    - client: 直接传入一个已初始化的 `LLMClient` 实例。如果提供此参数，将忽略其他所有参数。

    示例：
    ```python
    # 方式 1: 直接指定参数（推荐用于快速测试）
    assessment, cleaned, question = generate_question_from_text(
        text,
        model_name="gpt-4",
        api_key="sk-..."
    )

    # 方式 2: 使用 ModelConfig（推荐用于生产环境，便于管理多个配置）
    from questioner import ModelConfig, generate_question_from_text
    
    config = ModelConfig(
        model_name="qwen-plus",
        api_key="your-api-key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    assessment, cleaned, question = generate_question_from_text(
        text, config=config
    )

    # 方式 3: 使用自定义客户端（最灵活）
    from questioner import OpenAIClient, generate_question_from_text
    
    custom_client = OpenAIClient(
        model_name="your-model",
        api_key="your-key",
        base_url="http://localhost:8000/v1"
    )
    assessment, cleaned, question = generate_question_from_text(
        text, client=custom_client
    )
    ```
    """
    参数：
    - raw_text: 论文片段或"统计图表 + 描述文本"的文字部分。
    - model_name: 模型名称。如果不指定，将从 config.py 文件读取。
    - api_key: API Key。如果不指定，将从 config.py 或环境变量读取。
    - base_url: API 基础 URL。如果不指定，将从 config.py 读取。
    - config: 使用 `ModelConfig` 对象配置模型（优先级最高）。
    - client: 直接传入 `LLMClient` 实例（优先级最高）。

    配置优先级（从高到低）：
    1. client 参数
    2. config 参数
    3. model_name/api_key/base_url 参数
    4. config.py 文件中的配置
    5. 环境变量 OPENAI_API_KEY
    """
    if client is not None:
        # 优先级最高：直接使用提供的 client
        pipeline = QuestionerPipeline(client)
    elif config is not None:
        # 优先级第二：使用 ModelConfig 对象
        client = OpenAIClient(
            model_name=config.model_name,
            api_key=config.api_key,
            base_url=config.base_url,
        )
        pipeline = QuestionerPipeline(client)
    else:
        # 优先级第三：使用参数或从 config.py 读取
        default_config = _load_default_config()
        
        # 如果参数未指定，使用配置文件中的值
        final_model_name = model_name or (default_config.model_name if default_config else None)
        final_api_key = api_key if api_key is not None else (default_config.api_key if default_config else None)
        final_base_url = base_url if base_url is not None else (default_config.base_url if default_config else None)
        
        if not final_model_name:
            raise ValueError(
                "必须指定 model_name，或在 config.py 文件中设置 MODEL_NAME，"
                "或使用 config/client 参数。"
            )
        
        client = OpenAIClient(
            model_name=final_model_name,
            api_key=final_api_key,
            base_url=final_base_url,
        )
        pipeline = QuestionerPipeline(client)

    return pipeline.run(raw_text)
