# StatBench-Questioner 题目生成器

## 项目概述

本项目旨在开发一个 Python 流水线（Pipeline），利用支持 OpenAI API 格式的大语言模型处理科学论文中的"统计图表 + 描述文本"数据对（Data Pairs），自动构建用于评估 LLM 统计学能力的单项选择题（MCQ）。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置模型（只需修改一个文件）

**首次使用**：复制 `config.example.py` 为 `config.py`：

```bash
cp config.example.py config.py
```

然后编辑 `config.py` 文件，修改以下三个变量：

```python
# 模型名称（必须指定）
MODEL_NAME = "gpt-4"  # 例如: "gpt-4", "qwen-plus", "glm-4" 等

# API Key（可选，如果不设置则从环境变量 OPENAI_API_KEY 读取）
API_KEY = None  # 或直接填入 "sk-your-api-key"

# API 服务器地址（可选）
# OpenAI 官方: None 或 ""
# 国内大模型: "https://dashscope.aliyuncs.com/compatible-mode/v1"（通义千问）
# 本地服务: "http://localhost:8000/v1"
BASE_URL = None
```

**就这么简单！** 修改完这三个变量后，代码会自动使用你配置的模型服务，无需修改其他任何代码。

### 3. 使用示例

```python
from questioner import generate_question_from_text

# 输入文本
raw_text = """
研究人员在三组受试者中比较某种二分类结局的比例差异。
每组样本量约为 200 人，组别分别为 A、B 和 C。
研究使用卡方检验进行分析，发现 p < 0.05。
"""

# 生成题目（自动使用 config.py 中的配置）
assessment, cleaned_context, question = generate_question_from_text(raw_text)

# 检查结果
if not assessment.is_suitable:
    print(f"不适合出题: {assessment.missing_info}")
else:
    print(f"题目: {question.stem}")
    print(f"选项: {question.options}")
    print(f"答案: {question.answer}")
    print(f"解析: {question.analysis}")
```

## 核心功能模块

程序包含三个核心处理阶段，采用串行处理机制。

### 模块 A: 数据适用性过滤器 (Data Quality Filter)

- **输入**: 原始文本片段 (OCR提取) + 图表路径 (可选)
- **任务**: 作为一个"审稿人"，评估输入内容是否包含构建一道统计题所需的必要元素
- **判断标准**:
  - 数据来源清晰（如：样本量 N、数据收集方式）
  - 变量定义明确（如：自变量、因变量类型）
  - 有明确的统计结论或研究假设
  - *拒绝*: 信息残缺、模糊不清、或完全没有统计学内容的片段
- **输出**: `Boolean` (是否通过) + `Reason` (原因)

### 模块 B: 匿名化与情境重构 (Decontamination & Scenario Reconstruction)

- **核心痛点**: 防止 Data Leakage（数据泄露）。如果题目考察"使用了什么检验方法"，题干中绝不能出现"我们使用了 t-test"这样的字眼
- **任务**:
  1. **特征提取**: 从原始文本中提取纯粹的"数据特征"（Data Features），如：N=100，两组独立，连续变量，方差齐
  2. **方法剥离**: 识别并剔除原文中提及的具体统计方法名称、p值具体计算过程
  3. **重写**: 基于提取的特征，重写一段"中立"的研究场景描述
- **输出**: `Cleaned_Context` (清洗后的题干素材)

### 模块 C: 题目生成器 (Question Generator)

- **任务**: 基于 `Cleaned_Context`，生成一道标准的单选题
- **题目类型**:
  1. **Method Selection**: 给定数据场景，选最合适的统计检验方法
  2. **Result Interpretation**: 给定统计结果（如CI, OR值），选正确的解读
  3. **Assumption Check**: 该分析需要满足什么前提假设？
- **输出**: 标准 JSON 格式（包含 Stem, Options A-D, Correct Answer, Explanation）

## 支持的模型服务

本模块基于 OpenAI API 格式，兼容所有支持该格式的服务：

- **OpenAI 官方服务**: GPT-4, GPT-3.5-turbo 等
- **国内大模型**: 通义千问、文心一言、智谱 GLM 等（如果提供 OpenAI 兼容接口）
- **本地部署**: vLLM、Ollama 等（如果配置了 OpenAI 兼容接口）

### 常见模型配置示例

#### OpenAI 官方服务

```python
# config.py
MODEL_NAME = "gpt-4"
API_KEY = "sk-your-openai-api-key"
BASE_URL = None
```

#### 通义千问（阿里云）

```python
# config.py
MODEL_NAME = "qwen-plus"
API_KEY = "sk-your-dashscope-api-key"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
```

#### 本地部署的模型

```python
# config.py
MODEL_NAME = "your-model-name"
API_KEY = "dummy-key"
BASE_URL = "http://localhost:8000/v1"
```

## 高级用法

### 方式 1: 使用配置文件（推荐）

修改 `config.py` 文件即可，代码会自动读取。

### 方式 2: 使用环境变量

如果不修改 `config.py`，可以设置环境变量：

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-your-api-key"

# Linux/Mac
export OPENAI_API_KEY=sk-your-api-key
```

然后在 `config.py` 中设置：

```python
MODEL_NAME = "gpt-4"
API_KEY = None  # 从环境变量读取
BASE_URL = None
```

### 方式 3: 代码中动态指定

如果需要在代码中动态切换模型：

```python
from questioner import generate_question_from_text

# 直接指定参数（会覆盖 config.py 中的配置）
assessment, cleaned, question = generate_question_from_text(
    raw_text,
    model_name="qwen-plus",
    api_key="sk-your-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
```

## 技术架构

- **API 格式**: OpenAI API 兼容格式
- **数据验证**: 使用 `pydantic` 库定义 `Question` 和 `Assessment` 的数据类，确保 LLM 返回可解析的 JSON
- **模型支持**: 所有支持 OpenAI API 格式的模型服务

## 注意事项

1. **配置文件安全**: 
   - `config.py` 已添加到 `.gitignore`，不会被提交到版本控制系统
   - 首次使用时，复制 `config.example.py` 为 `config.py` 并修改配置
2. **模型名称**: 必须指定正确的模型名称，不同服务商的模型名称可能不同
3. **API 端点**: 对于非 OpenAI 官方服务，必须指定正确的 `BASE_URL`

## 项目结构

```
Questioner/
├── config.example.py      # 配置模板（复制为 config.py）
├── config.py              # 配置文件（只需修改这里，不会被提交）
├── Readme.md              # 本文件（使用说明）
├── ARCHITECTURE.md        # 技术架构文档
├── requirements.txt        # 依赖列表
├── questioner/            # 核心模块
│   ├── __init__.py
│   ├── pipeline.py        # 主入口
│   ├── modules.py         # 三个核心模块
│   ├── llm_client.py      # LLM 客户端
│   ├── models.py          # 数据模型
│   ├── prompts.py         # Prompt 定义
│   └── config.py          # 配置类（内部使用）
└── example_usage.py       # 使用示例
```

## 更多信息

- 技术细节和架构说明请参考 `ARCHITECTURE.md`
- 更多使用示例请参考 `example_usage.py`
