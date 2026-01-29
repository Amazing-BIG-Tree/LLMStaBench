## StatBench-Questioner 题目生成器

你可以将这部分内容直接粘贴给 Cursor，作为项目的 Context 或 Readme。

### 1. 项目概述
本项目旨在开发一个 Python 流水线（Pipeline），利用 Google Gemini API 处理科学论文中的“统计图表 + 描述文本”数据对（Data Pairs），自动构建用于评估 LLM 统计学能力的单项选择题（MCQ）。

### 2. 核心功能模块
程序需包含三个核心处理阶段，采用串行处理机制。

**模块 A: 数据适用性过滤器 (Data Quality Filter)**
*   **输入**: 原始文本片段 (OCR提取) + 图表路径 (可选)。
*   **任务**: 作为一个“审稿人”，评估输入内容是否包含构建一道统计题所需的必要元素。
*   **判断标准**:
    *   数据来源清晰（如：样本量 N、数据收集方式）。
    *   变量定义明确（如：自变量、因变量类型）。
    *   有明确的统计结论或研究假设。
    *   *拒绝*: 信息残缺、模糊不清、或完全没有统计学内容的片段。
*   **输出**: `Boolean` (是否通过) + `Reason` (原因)。

**模块 B: 匿名化与情境重构 (Decontamination & Scenario Reconstruction)**
*   **核心痛点**: 防止 Data Leakage（数据泄露）。如果题目考察“使用了什么检验方法”，题干中绝不能出现“我们使用了 t-test”这样的字眼，图表中也不能有暗示性的 “t=” 或 “chi-square” 符号。
*   **任务**:
    1.  **特征提取**: 从原始文本中提取纯粹的“数据特征”（Data Features），如：N=100，两组独立，连续变量，方差齐。
    2.  **方法剥离**: 识别并剔除原文中提及的具体统计方法名称、p值具体计算过程。
    3.  **重写**: 基于提取的特征，重写一段“中立”的研究场景描述。将“我们用卡方检验发现...”重写为“研究人员收集了数据（见下表），旨在探究变量A与变量B的关联...”。
*   **输出**: `Cleaned_Context` (清洗后的题干素材)。

**模块 C: 题目生成器 (Question Generator)**
*   **任务**: 基于 `Cleaned_Context`，生成一道标准的单选题。
*   **题目类型 (Task Type)**:
    1.  **Method Selection**: 给定数据场景，选最合适的统计检验方法。
    2.  **Result Interpretation**: 给定统计结果（如CI, OR值），选正确的解读。
    3.  **Assumption Check**: 该分析需要满足什么前提假设？
*   **输出**: 标准 JSON 格式（包含 Stem, Options A-D, Correct Answer, Explanation）。

### 3. 技术架构
*   **API**: `google.generativeai`
*   **Model**: `gemini-1.5-pro` (利用其长文本和多模态能力)
*   **数据验证**: 使用 `pydantic` 库定义 `Question` 和 `Assessment` 的数据类，确保 LLM 返回可解析的 JSON。

### 4. 核心 Prompt 设计 (基于你的 HTML 示例优化)

#### Prompt 1: 适用性评估 (用于模块 A)

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

#### Prompt 2: 匿名化与重写 (核心难点，用于模块 B)

这个 Prompt 旨在模仿你提供的示例中“提取数据特征”的过程，但要刻意抹去“答案”。

```python
SYSTEM_PROMPT_DECONTAMINATE = """
你是一个专业的学术编辑。你的任务是根据提供的【原始论文片段】，重写一段“研究场景描述”，用于统计学考试。

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
   请输出重写后的文本。这段文本应该读起来像是一道数学应用题的“题干背景”部分。
"""
```

#### Prompt 3: 题目生成 (用于模块 C)

这个 Prompt 的设计逻辑参考了你示例中 Gemini 回复的结构（Test Type / Hypotheses / Assumption / Warnings）。

```python
SYSTEM_PROMPT_GENERATE = """
你是一个统计学考试出题专家。基于以下【研究场景描述】（Context），请编写一道单项选择题。

**输入参考示例**:
（这里可以把你的 HTML 示例中 "Goal 1" 的逻辑作为 few-shot 喂进去，告诉模型什么是好的统计分析思路）
*Example Logic*: 
- Data: Binary outcome (ADNC +/-), 3 Groups (Dementia/MCI/CU).
- Goal: Compare proportions.
- Correct Method: Chi-square test.

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