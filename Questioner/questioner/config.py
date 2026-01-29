"""
模型配置管理模块，方便用户自定义和管理多个模型配置。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class ModelConfig:
    """
    模型配置类，用于存储单个模型的配置信息。

    示例：
    ```python
    # OpenAI 官方服务
    config = ModelConfig(
        model_name="gpt-4",
        api_key="sk-...",
        base_url=None  # 使用默认 OpenAI 端点
    )

    # 国内大模型（通义千问）
    config = ModelConfig(
        model_name="qwen-plus",
        api_key="sk-...",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    # 本地部署的模型
    config = ModelConfig(
        model_name="your-model",
        api_key="dummy-key",
        base_url="http://localhost:8000/v1"
    )
    ```
    """

    model_name: str
    """模型名称，例如 "gpt-4", "qwen-plus", "glm-4" 等"""

    api_key: Optional[str] = None
    """
    API Key。
    如果为 None，将从环境变量 `OPENAI_API_KEY` 读取。
    对于某些本地服务，可能不需要真实的 key，可以传入 "dummy-key" 等占位符。
    """

    base_url: Optional[str] = None
    """
    API 基础 URL。
    如果为 None，将使用 OpenAI 官方端点 (https://api.openai.com/v1)。
    对于其他服务，请指定对应的端点，例如：
    - 通义千问: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    - 智谱 GLM: "https://open.bigmodel.cn/api/paas/v4"
    - 本地服务: "http://localhost:8000/v1"
    """

    def to_dict(self) -> dict:
        """转换为字典格式，方便序列化或传递给其他函数。"""
        return {
            "model_name": self.model_name,
            "api_key": self.api_key,
            "base_url": self.base_url,
        }

    @classmethod
    def from_dict(cls, config_dict: dict) -> ModelConfig:
        """从字典创建配置对象。"""
        return cls(
            model_name=config_dict["model_name"],
            api_key=config_dict.get("api_key"),
            base_url=config_dict.get("base_url"),
        )


def load_configs_from_json(json_path: str | Path) -> Dict[str, ModelConfig]:
    """
    从 JSON 文件加载多个模型配置。

    参数：
    - json_path: JSON 文件路径

    JSON 文件格式示例：
    ```json
    {
      "models": {
        "openai_gpt4": {
          "model_name": "gpt-4",
          "api_key": "sk-...",
          "base_url": null
        },
        "qwen_plus": {
          "model_name": "qwen-plus",
          "api_key": "sk-...",
          "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
        }
      },
      "default": "openai_gpt4"
    }
    ```

    返回：
    - 字典，键为配置名称，值为 ModelConfig 对象

    示例：
    ```python
    configs = load_configs_from_json("config.json")
    default_config = configs["openai_gpt4"]
    ```
    """
    json_path = Path(json_path)
    if not json_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    models_dict = data.get("models", {})
    configs = {}
    for name, config_dict in models_dict.items():
        configs[name] = ModelConfig.from_dict(config_dict)

    return configs


def get_default_config_from_json(json_path: str | Path) -> Optional[ModelConfig]:
    """
    从 JSON 文件加载默认配置。

    参数：
    - json_path: JSON 文件路径

    返回：
    - 默认的 ModelConfig 对象，如果未指定默认配置则返回 None

    示例：
    ```python
    default_config = get_default_config_from_json("config.json")
    if default_config:
        assessment, cleaned, question = generate_question_from_text(
            text, config=default_config
        )
    ```
    """
    json_path = Path(json_path)
    if not json_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    default_name = data.get("default")
    if not default_name:
        return None

    models_dict = data.get("models", {})
    if default_name not in models_dict:
        raise ValueError(f"默认配置 '{default_name}' 在配置文件中不存在")

    return ModelConfig.from_dict(models_dict[default_name])
