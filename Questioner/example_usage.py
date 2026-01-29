"""
Questioner 模块使用示例：展示如何使用 OpenAI 格式的 API。

兼容所有支持 OpenAI API 格式的服务，包括：
- OpenAI 官方服务（GPT-4、GPT-3.5 等）
- 国内大模型服务（通义千问、文心一言、智谱 GLM 等）
- 本地部署的模型服务（vLLM、Ollama 等）

推荐使用 ModelConfig 来管理模型配置，方便切换和复用。
"""

from questioner import ModelConfig, OpenAIClient, generate_question_from_text

# 示例文本
SAMPLE_TEXT = """
研究人员在三组受试者中比较某种二分类结局（如疾病阳性/阴性）的比例差异。
每组样本量约为 200 人，组别分别为 A、B 和 C，结局为是否发生某种事件（是/否）。
研究使用卡方检验（Chi-square test）进行分析，发现 p < 0.05。
"""


def example_1_use_with_model_config():
    """示例 1: 使用 ModelConfig 配置模型（推荐方式）"""
    print("=" * 60)
    print("示例 1: 使用 ModelConfig 配置模型")
    print("=" * 60)

    # 创建模型配置
    config = ModelConfig(
        model_name="gpt-4",
        api_key="sk-your-api-key",  # 或从环境变量读取（设为 None）
        base_url=None,  # OpenAI 官方端点
    )

    assessment, cleaned_context, question = generate_question_from_text(
        SAMPLE_TEXT, config=config
    )

    if not assessment.is_suitable:
        print(f"不适合出题: {assessment.missing_info}")
    else:
        print(f"适合出题，题型: {assessment.potential_task}")
        print(f"\n匿名化后的题干背景:\n{cleaned_context}\n")
        print(f"题目:\n{question.stem}\n")
        print("选项:")
        for key, value in question.options.items():
            print(f"  {key}. {value}")
        print(f"\n正确答案: {question.answer}")
        print(f"\n解析:\n{question.analysis}\n")


def example_2_use_direct_params():
    """示例 2: 直接使用参数（快速测试）"""
    print("=" * 60)
    print("示例 2: 直接使用参数")
    print("=" * 60)

    assessment, cleaned_context, question = generate_question_from_text(
        SAMPLE_TEXT,
        model_name="gpt-3.5-turbo",  # 必须指定
        api_key="sk-your-api-key",  # 可选，不传则从环境变量读取
        base_url=None,  # 可选
    )

    if question:
        print(f"题目:\n{question.stem}\n")
        print(f"正确答案: {question.answer}\n")


def example_3_use_domestic_model_with_config():
    """示例 3: 使用 ModelConfig 配置国内大模型（推荐）"""
    print("=" * 60)
    print("示例 3: 使用 ModelConfig 配置国内大模型")
    print("=" * 60)

    # 使用 ModelConfig 管理配置，便于复用
    qwen_config = ModelConfig(
        model_name="qwen-plus",
        api_key="sk-your-dashscope-api-key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    assessment, cleaned_context, question = generate_question_from_text(
        SAMPLE_TEXT, config=qwen_config
    )

    if question:
        print(f"题目:\n{question.stem}\n")
        print(f"正确答案: {question.answer}\n")


def example_4_use_local_model():
    """示例 4: 使用本地部署的模型服务"""
    print("=" * 60)
    print("示例 4: 使用本地部署的模型")
    print("=" * 60)

    # 使用 ModelConfig 配置本地模型
    local_config = ModelConfig(
        model_name="your-local-model-name",
        api_key="dummy-key",  # 本地服务可能不需要真实的 key
        base_url="http://localhost:8000/v1",
    )

    assessment, cleaned_context, question = generate_question_from_text(
        SAMPLE_TEXT, config=local_config
    )

    if question:
        print(f"题目:\n{question.stem}\n")
        print(f"正确答案: {question.answer}\n")


def example_5_custom_client():
    """示例 5: 使用自定义客户端（最灵活）"""
    print("=" * 60)
    print("示例 5: 使用自定义客户端")
    print("=" * 60)

    # 创建自定义客户端，可以复用
    custom_client = OpenAIClient(
        model_name="gpt-4",  # 必须指定
        api_key=None,  # 从环境变量读取
        base_url=None,  # 使用默认 OpenAI 端点
    )

    assessment, cleaned_context, question = generate_question_from_text(
        SAMPLE_TEXT,
        client=custom_client,  # 直接传入自定义客户端
    )

    if question:
        print(f"题目:\n{question.stem}\n")
        print(f"正确答案: {question.answer}\n")


def example_6_multiple_configs():
    """示例 6: 管理多个模型配置"""
    print("=" * 60)
    print("示例 6: 管理多个模型配置")
    print("=" * 60)

    # 定义多个配置，方便切换
    configs = {
        "openai_gpt4": ModelConfig(
            model_name="gpt-4",
            api_key=None,  # 从环境变量读取
            base_url=None,
        ),
        "openai_gpt35": ModelConfig(
            model_name="gpt-3.5-turbo",
            api_key=None,
            base_url=None,
        ),
        "qwen": ModelConfig(
            model_name="qwen-plus",
            api_key="sk-your-dashscope-api-key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        ),
        "local": ModelConfig(
            model_name="your-model",
            api_key="dummy-key",
            base_url="http://localhost:8000/v1",
        ),
    }

    # 选择要使用的配置
    selected_config = configs["qwen"]  # 或从配置文件/环境变量读取

    assessment, cleaned_context, question = generate_question_from_text(
        SAMPLE_TEXT, config=selected_config
    )

    if question:
        print(f"使用配置: {selected_config.model_name}")
        print(f"题目: {question.stem}\n")


if __name__ == "__main__":
    # 注意：运行前需要设置环境变量（如果使用环境变量方式）
    # Windows PowerShell: $env:OPENAI_API_KEY = "your-key"
    # Windows CMD: set OPENAI_API_KEY=your-key
    # Linux/Mac: export OPENAI_API_KEY=your-key

    print("\n提示：")
    print("1. 如果使用环境变量，请确保已设置 OPENAI_API_KEY")
    print("2. 推荐使用 ModelConfig 来管理配置，便于切换和复用")
    print("3. 可以参考 config_example.py 文件创建自己的配置文件\n")

    # 运行示例（根据需要取消注释）
    # example_1_use_with_model_config()  # 推荐：使用 ModelConfig
    # example_2_use_direct_params()  # 快速测试：直接传参数
    # example_3_use_domestic_model_with_config()  # 国内大模型
    # example_4_use_local_model()  # 本地部署
    # example_5_custom_client()  # 自定义客户端
    # example_6_multiple_configs()  # 多配置管理

    print("请取消注释上面的示例函数来运行测试")
