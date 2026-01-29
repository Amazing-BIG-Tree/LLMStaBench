"""
封装对 Google Gemini 的调用，便于在各模块中复用。
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import google.generativeai as genai


class GeminiClient:
    """
    对 `google.generativeai` 的一个简单封装。

    使用方式：
    - 通过环境变量 `GEMINI_API_KEY` 提供 API Key。
    - 默认使用模型 `gemini-1.5-pro`。
    """

    def __init__(
        self,
        model_name: str = "gemini-1.5-pro",
        api_key: Optional[str] = None,
    ) -> None:
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "未找到 GEMINI_API_KEY，请在环境变量中设置你的 Google Gemini API Key。"
            )

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name)

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
        response = self._model.generate_content(
            [
                {"role": "system", "parts": [system_prompt]},
                {"role": "user", "parts": [user_content]},
            ]
        )
        text = response.text or ""

        # 简单的 JSON 解析与清洗：去掉可能包裹的代码块标记 ```json ... ```
        cleaned = text.strip()
        if cleaned.startswith("```"):
            # 可能是 ```json\n...\n``` 的形式
            cleaned = cleaned.strip("`")
            # 去掉可能的 "json" 标记
            cleaned = cleaned.replace("json", "", 1).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"无法解析 Gemini 返回的 JSON：{e}\n原始内容:\n{text}") from e

    def generate_text(
        self,
        system_prompt: str,
        user_content: str,
    ) -> str:
        """
        期望 LLM 返回一段纯文本（例如重写后的研究场景描述）。
        """
        response = self._model.generate_content(
            [
                {"role": "system", "parts": [system_prompt]},
                {"role": "user", "parts": [user_content]},
            ]
        )
        return (response.text or "").strip()

