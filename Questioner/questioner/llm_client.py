"""
LLM 客户端实现，基于 OpenAI API 格式。

兼容所有支持 OpenAI API 格式的服务，包括：
- OpenAI 官方服务（GPT-4、GPT-3.5 等）
- 国内大模型服务（如通义千问、文心一言、智谱 GLM 等，如果它们提供 OpenAI 兼容接口）
- 本地部署的模型服务（如 vLLM、Ollama 等）
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class LLMClient(ABC):
    """
    抽象的 LLM 客户端接口，所有具体的模型实现都应该继承此类。

    参考 OpenAI SDK 的设计模式，提供统一的接口：
    - `generate_structured_json()`: 生成并解析 JSON
    - `generate_text()`: 生成纯文本
    """

    @abstractmethod
    def generate_structured_json(
        self,
        system_prompt: str,
        user_content: str,
    ) -> Dict[str, Any]:
        """
        期望 LLM 返回 JSON 字符串，并将其解析为字典。

        - `system_prompt`: 系统角色说明与输出格式约束。
        - `user_content`: 具体的论文片段或研究场景。
        """
        pass

    @abstractmethod
    def generate_text(
        self,
        system_prompt: str,
        user_content: str,
    ) -> str:
        """
        期望 LLM 返回一段纯文本（例如重写后的研究场景描述）。
        """
        pass

    @staticmethod
    def _clean_json_text(text: str) -> str:
        """
        辅助方法：清理可能包裹在代码块标记中的 JSON 文本。
        """
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            # 去掉可能的 "json" 标记
            cleaned = cleaned.replace("json", "", 1).strip()
        return cleaned

    @staticmethod
    def _parse_json(text: str, provider_name: str = "LLM") -> Dict[str, Any]:
        """
        辅助方法：解析 JSON 文本，统一错误处理。
        """
        cleaned = LLMClient._clean_json_text(text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"无法解析 {provider_name} 返回的 JSON：{e}\n原始内容:\n{text}"
            ) from e


class OpenAIClient(LLMClient):
    """
    OpenAI 格式客户端实现。

    兼容所有支持 OpenAI API 格式的服务，包括：
    - OpenAI 官方服务（GPT-4、GPT-3.5 等）
    - 国内大模型服务（如通义千问、文心一言、智谱 GLM 等，如果它们提供 OpenAI 兼容接口）
    - 本地部署的模型服务（如 vLLM、Ollama 等）

    使用方式：
    - `model_name`: 必须指定，例如 "gpt-4", "qwen-plus" 等。
    - `api_key`: 可选。如果为 None，将从环境变量 `OPENAI_API_KEY` 读取。
      如果环境变量也没有，某些服务（如本地部署）可能允许使用占位符。
    - `base_url`: 可选。如果为 None，将使用 OpenAI 官方端点。
      对于其他服务，请指定对应的端点。
    """

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        if OpenAI is None:
            raise ImportError("未安装 openai，请运行: pip install openai")

        if not model_name:
            raise ValueError("model_name 不能为空，请指定要使用的模型名称")

        # 尝试从参数或环境变量获取 API key
        # 如果都没有，允许继续（某些本地服务可能不需要真实的 key）
        api_key = api_key or os.getenv("OPENAI_API_KEY")

        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model_name = model_name

    def generate_structured_json(
        self,
        system_prompt: str,
        user_content: str,
    ) -> Dict[str, Any]:
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},  # 强制 JSON 格式
        )
        text = response.choices[0].message.content or ""
        return self._parse_json(text, provider_name="OpenAI")

    def generate_text(
        self,
        system_prompt: str,
        user_content: str,
    ) -> str:
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        return (response.choices[0].message.content or "").strip()

