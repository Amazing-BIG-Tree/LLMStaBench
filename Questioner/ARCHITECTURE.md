# 技术架构文档

本文档存储 Questioner 模块的技术细节和架构说明，供开发者参考。

## 核心 Prompt 设计

### Prompt 1: 适用性评估 (用于模块 A)

```python
SYSTEM_PROMPT_ASSESS = """
你是一个资深的统计学论文审稿人。你的任务是评估给定的【论文片段】是否适合改编成一道统计学考试题。

评估标准：
1. **数据完整性**: 包含样本量(N)、变量类型(连续/分类)、分组情况等关键元数据。
2. **目标明确**: 有清晰的研究问题（例如："比较两组的差异" 或 "探究相关性"）。
3. **可验证性**: 基于提供的信息，统计学专家可以推断出唯一正确的分析方法或结论。

请以 JSON 格式返回：
{
    "is_suitable": boolean,
    "missing_info": "如果缺少信息，列出缺少什么（如：未说明样本是否独立）",
    "potential_task": "适合出什么题？例如：'选择检验方法' 或 '解读置信区间'"
}
"""
```

### Prompt 2: 匿名化与重写 (核心难点，用于模块 B)

这个 Prompt 旨在模仿示例中"提取数据特征"的过程，但要刻意抹去"答案"。

```python
SYSTEM_PROMPT_DECONTAMINATE = """
你是一个专业的学术编辑。你的任务是根据提供的【原始论文片段】，重写一段"研究场景描述"，用于统计学考试。

**严格约束 (CRITICAL Constraints)**:
1. **去污染 (Decontamination)**: 
   - 你必须 **删除** 所有原本提到的具体统计方法名称（如 "Chi-square", "t-test", "ANOVA", "Regression"）。
   - 你必须 **删除** 带有明显提示性的统计量符号（如 "t = ...", "F = ...", "χ² = ..."）。
   - 如果原文说 "Differences were assessed using a chi-squared test"，请重写为 "Researchers aimed to assess the differences in proportions between the groups."

2. **保留关键特征 (Feature Retention)**:
   - 保留数据来源描述（如 "11,486 plasma samples from HUNT study"）。
   - 保留变量定义（如 "cognitive status (Dementia, MCI, CU)" 和 "ADNC positivity (binary)"）。
   - 保留样本量和分组结构。

3. **输出格式**:
   请输出重写后的文本。这段文本应该读起来像是一道数学应用题的"题干背景"部分。
"""
```

### Prompt 3: 题目生成 (用于模块 C)

```python
SYSTEM_PROMPT_GENERATE = """
你是一个统计学考试出题专家。基于以下【研究场景描述】（Context），请编写一道单项选择题。

**出题要求**:
1. **题型**: 重点考察 "Statistical Method Selection" (统计方法选择)。
2. **题干**: "针对上述研究设计和数据类型，研究人员应该采用哪种统计检验方法来判断 [具体研究目标]？"
3. **选项**: 
   - 提供 4 个选项 (A/B/C/D)。
   - 干扰项 (Distractors) 必须具有迷惑性（例如：对于比较比例，提供 t-test 或 ANOVA 作为错误选项，因为初学者常混淆连续变量和分类变量的检验）。
4. **解析**: 
   - 解释为什么正确选项是最佳匹配（基于数据分布、变量类型）。
   - 解释为什么其他选项是错误的（例如："ANOVA 用于连续变量，而本例 Outcome 是二分类的"）。

请严格按照以下 JSON 格式输出：
{
    "stem": "题目描述...",
    "options": {
        "A": "...",
        "B": "...",
        "C": "...",
        "D": "..."
    },
    "answer": "A",
    "analysis": "详细解析..."
}
"""
```

## 数据模型

### AssessmentResult

模块 A 的评估结果：

```python
class AssessmentResult(BaseModel):
    is_suitable: bool  # 是否适合出题
    missing_info: str  # 缺失的信息
    potential_task: str  # 适合出的题型
```

### Question

模块 C 生成的题目结构：

```python
class Question(BaseModel):
    stem: str  # 题干
    options: Dict[str, str]  # 选项 {"A": "...", "B": "...", ...}
    answer: str  # 正确答案 "A"
    analysis: str  # 解析
```

## 配置系统

### 配置优先级

1. `client` 参数（最高优先级）
2. `config` 参数（ModelConfig 对象）
3. `model_name/api_key/base_url` 参数
4. `config.py` 文件中的配置
5. 环境变量 `OPENAI_API_KEY`（最低优先级）

### 配置加载机制

`pipeline.py` 中的 `_load_default_config()` 函数会：
1. 查找项目根目录的 `config.py` 文件
2. 动态导入并读取 `MODEL_NAME`、`API_KEY`、`BASE_URL` 变量
3. 如果文件不存在或加载失败，返回 None，使用其他配置方式

## LLM 客户端架构

### LLMClient 抽象接口

所有 LLM 客户端都实现以下接口：

```python
class LLMClient(ABC):
    @abstractmethod
    def generate_structured_json(system_prompt, user_content) -> Dict
    
    @abstractmethod
    def generate_text(system_prompt, user_content) -> str
```

### OpenAIClient 实现

基于 OpenAI SDK，兼容所有 OpenAI API 格式的服务：

- 支持自定义 `base_url`（用于国内大模型或本地服务）
- 自动处理 JSON 解析和错误处理
- 支持环境变量配置

## 模块流程

```
原始文本
    ↓
[模块 A: 数据适用性过滤器]
    ↓ (is_suitable?)
[模块 B: 匿名化与情境重构]
    ↓
[模块 C: 题目生成器]
    ↓
Question 对象
```

## 扩展性

### 添加新的模型提供商

1. 实现 `LLMClient` 接口
2. 在 `pipeline.py` 中添加相应的初始化逻辑
3. 更新 `config.py` 支持新提供商的配置

### 添加新的题目类型

1. 修改 `prompts.py` 中的 `SYSTEM_PROMPT_GENERATE`
2. 更新 `Question` 模型（如需要）
3. 在 `modules.py` 的 `QuestionGenerator` 中添加相应逻辑

## 技术栈

- **Python 3.8+**
- **pydantic**: 数据验证和模型定义
- **openai**: OpenAI API 客户端（兼容其他服务）
- **标准库**: json, os, pathlib, abc

## 错误处理

- JSON 解析错误：自动清理代码块标记，提供详细错误信息
- API 调用错误：由 OpenAI SDK 处理，向上抛出
- 配置加载错误：静默失败，使用其他配置方式
