"""
示例：如何从 JSON 文件加载模型配置。
"""

from questioner import (
    generate_question_from_text,
    get_default_config_from_json,
    load_configs_from_json,
)

# 示例文本
SAMPLE_TEXT = """
研究人员在三组受试者中比较某种二分类结局的比例差异。
每组样本量约为 200 人，组别分别为 A、B 和 C。
"""


def example_load_from_json():
    """示例：从 JSON 文件加载配置"""
    print("=" * 60)
    print("示例：从 JSON 文件加载配置")
    print("=" * 60)

    # 方式 1: 加载所有配置
    configs = load_configs_from_json("config_example.json")
    print(f"已加载 {len(configs)} 个配置:")
    for name in configs.keys():
        print(f"  - {name}")

    # 使用特定配置
    qwen_config = configs.get("qwen_plus")
    if qwen_config:
        assessment, cleaned, question = generate_question_from_text(
            SAMPLE_TEXT, config=qwen_config
        )
        if question:
            print(f"\n使用配置: {qwen_config.model_name}")
            print(f"题目: {question.stem[:50]}...")

    # 方式 2: 直接获取默认配置
    default_config = get_default_config_from_json("config_example.json")
    if default_config:
        print(f"\n默认配置: {default_config.model_name}")
        # assessment, cleaned, question = generate_question_from_text(
        #     SAMPLE_TEXT, config=default_config
        # )


if __name__ == "__main__":
    # 注意：需要先创建 config_example.json 文件（或复制并修改）
    try:
        example_load_from_json()
    except FileNotFoundError:
        print("请先创建配置文件 config.json，或使用 config_example.json 作为模板")
