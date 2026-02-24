# 实验执行说明

## 环境要求

- Python 3.6+
- requests 库
- 智谱 AI API Key（GLM-5）

## 配置步骤

### 1. 获取 API Key

访问 [智谱 AI 开放平台](https://open.bigmodel.cn/)，注册并获取 API Key。

### 2. 设置环境变量

```bash
export ZAI_API_KEY="your_api_key_here"
```

或在脚本中直接修改：

```python
API_KEY = "your_api_key_here"
```

### 3. 安装依赖

```bash
pip install requests
```

（可选）安装智谱 AI SDK：

```bash
pip install zhipuai
```

## 运行实验

### 完整实验

```bash
python3 run_experiment.py
```

这将执行：
- 5个问题 × 7个模板 = 35次 API 调用
- 预计耗时：5-10 分钟
- 预计 Token 消耗：~50,000 tokens

### 部分实验（测试用）

修改脚本中的问题集和模板集：

```python
# 只测试前2个问题
results = run_experiment(
    problems=PROBLEMS[:2],
    template_types=["baseline", "full"],
)
```

## 结果文件

### 原始结果

`results/raw_results_YYYYMMDD_HHMMSS.json`

```json
[
  {
    "experiment_id": "EXP-20260224105613-MATH-001-baseline",
    "timestamp": "2026-02-24T10:56:13",
    "model": "glm-5",
    "problem_id": "MATH-001",
    "template_type": "baseline",
    "response_text": "...",
    "tokens_used": 1500,
    "response_time_ms": 3500,
    "evaluation": {
      "steps": 8,
      "length": 1200,
      "has_answer": true
    }
  },
  ...
]
```

### 分析报告

`results/analysis_YYYYMMDD_HHMMSS.md`

包含：
- 汇总统计表格
- 每个模板的平均表现
- 详细结果展示

## 常见问题

### Q: API 返回 "余额不足" 错误（错误码 1113）

A: 访问智谱 AI 控制台充值，或等待免费额度刷新。

### Q: 如何调整实验参数？

A: 修改脚本顶部的配置：

```python
# 调整温度（创造性）
response = call_glm5_api(prompt, temperature=0.7)

# 调整 API 超时时间
response = requests.post(url, headers=headers, json=data, timeout=120)
```

### Q: 如何添加新的问题？

A: 在 `PROBLEMS` 列表中添加：

```python
{
    "id": "NEW-001",
    "category": "新类别",
    "question": "新问题内容",
    "answer": "参考答案",
}
```

### Q: 如何添加新的模板？

A: 在 `TEMPLATES` 字典中添加：

```python
"new_template": {
    "name": "新模板名称",
    "prompt": "模板内容...",
}
```

## 数据分析

### 使用 Python 分析

```python
import json
import pandas as pd

# 加载结果
with open('results/raw_results_*.json') as f:
    results = json.load(f)

# 转换为 DataFrame
df = pd.DataFrame(results)

# 按模板分组统计
stats = df.groupby('template_type').agg({
    'tokens_used': 'mean',
    'response_time_ms': 'mean',
    'evaluation': lambda x: sum(e['steps'] for e in x) / len(x)
})

print(stats)
```

### 生成可视化

```bash
python3 scripts/generate_charts.py
```

这将生成：
- Token 消耗对比图
- 响应时间分布图
- 推理步数对比图

## 注意事项

1. **API 限流**：脚本已添加 0.5 秒延迟，避免触发限流
2. **Token 消耗**：完整实验约消耗 50,000 tokens，注意账户余额
3. **超时处理**：单次调用超时设置为 60 秒，可根据需要调整
4. **错误重试**：当前版本不自动重试，失败会记录错误信息

## 进阶使用

### 批量实验

创建多个问题集，批量运行：

```python
for problem_set in [PROBLEMS_MATH, PROBLEMS_LOGIC, PROBLEMS_CODE]:
    results = run_experiment(problems=problem_set)
    # 保存结果...
```

### A/B 测试

对比两个模板：

```python
results_a = run_experiment(template_types=["baseline"])
results_b = run_experiment(template_types=["full"])
# 对比分析...
```

### 参数调优

测试不同温度值：

```python
for temp in [0.3, 0.5, 0.7, 0.9]:
    results = run_experiment(temperature=temp)
    # 分析效果...
```

---

*文档版本：1.0*
*最后更新：2026-02-24*
