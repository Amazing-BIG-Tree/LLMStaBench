"""
模型配置示例文件。

你可以：
1. 复制此文件为 `config.py`（注意：不要提交到版本控制）
2. 修改其中的配置为你自己的 API Key 和模型信息
3. 在代码中导入并使用

或者直接在代码中创建 `ModelConfig` 对象。
"""

from questioner import ModelConfig

# ============================================================================
# 配置示例：OpenAI 官方服务
# ============================================================================
OPENAI_GPT4 = ModelConfig(
    model_name="gpt-4",
    api_key="sk-your-openai-api-key",  # 替换为你的 API Key
    base_url=None,  # 使用 OpenAI 官方端点
)

OPENAI_GPT35 = ModelConfig(
    model_name="gpt-3.5-turbo",
    api_key="sk-your-openai-api-key",
    base_url=None,
)

# ============================================================================
# 配置示例：国内大模型
# ============================================================================

# 通义千问（阿里云）
QWEN_PLUS = ModelConfig(
    model_name="qwen-plus",
    api_key="sk-your-dashscope-api-key",  # 替换为你的 DashScope API Key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

QWEN_TURBO = ModelConfig(
    model_name="qwen-turbo",
    api_key="sk-your-dashscope-api-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 智谱 GLM（需要根据实际 API 文档调整）
GLM_4 = ModelConfig(
    model_name="glm-4",
    api_key="your-zhipu-api-key",
    base_url="https://open.bigmodel.cn/api/paas/v4",
)

# 文心一言（需要根据实际 API 文档调整）
ERNIE_BOT_4 = ModelConfig(
    model_name="ernie-bot-4",
    api_key="your-baidu-api-key",
    base_url="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat",
)

# ============================================================================
# 配置示例：本地部署的模型
# ============================================================================

# vLLM 本地服务
LOCAL_VLLM = ModelConfig(
    model_name="your-local-model-name",
    api_key="dummy-key",  # 本地服务可能不需要真实的 key
    base_url="http://localhost:8000/v1",
)

# Ollama 本地服务（如果配置了 OpenAI 兼容接口）
LOCAL_OLLAMA = ModelConfig(
    model_name="llama2",
    api_key="dummy-key",
    base_url="http://localhost:11434/v1",  # 需要 Ollama 配置 OpenAI 兼容接口
)

# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    from questioner import generate_question_from_text

    sample_text = """
    研究人员在三组受试者中比较某种二分类结局的比例差异。
    每组样本量约为 200 人，组别分别为 A、B 和 C。
    """

    # 使用配置对象
    assessment, cleaned, question = generate_question_from_text(
        sample_text,
        config=QWEN_PLUS,  # 或使用其他配置
    )

    if question:
        print(f"题目: {question.stem}")
        print(f"答案: {question.answer}")
