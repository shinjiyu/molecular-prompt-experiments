"""
Long CoT 分子结构提示词工程对比实验 - 真实 API 版本

使用 GLM-5 API 进行真实实验
"""

from __future__ import print_function
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# 实验配置
EXPERIMENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(EXPERIMENT_DIR, 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

# GLM-5 API 配置
API_KEY = os.getenv('ZAI_API_KEY', '3ec7bff16b6de647728ace1e8d727a14.cu5ZWvYYAiUzb76N')

# 实验问题集（5个问题）
PROBLEMS = [
    {
        "id": "MATH-001",
        "category": "数学",
        "question": "一个袋子里有5个红球和3个蓝球，连续取出3个球（不放回），求至少有2个红球的概率",
        "answer": "计算正确",
    },
    {
        "id": "LOGIC-001",
        "category": "逻辑",
        "question": '岛上只有说真话和说假话的人，遇到三个人A、B、C，A说"B是说假话的"，B说"C是说假话的"，C说"A和B都是说假话的"。问各是什么人？',
        "answer": "A说真话，B说假话，C说假话",
    },
    {
        "id": "CS-001",
        "category": "常识",
        "question": "为什么下雨后经常能看到彩虹？",
        "answer": "解释正确",
    },
    {
        "id": "CODE-001",
        "category": "代码",
        "question": """以下 Python 代码想计算斐波那契数列第10项，但结果错误，请找出 bug 并解释：
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
print(fib(10))  # 期望输出 55""",
        "answer": "代码正确，输出55",
    },
    {
        "id": "STRATEGY-001",
        "category": "策略",
        "question": "一个初创公司有100万预算，需要在用户增长和产品研发之间分配，请给出建议",
        "answer": "开放性答案",
    },
]

# 7组提示词模板
TEMPLATES = {
    "baseline": {
        "name": "基线（Baseline）",
        "prompt": """请解决以下问题：

{question}
""",
    },
    
    "cot_basic": {
        "name": "普通CoT（CoT-Basic）",
        "prompt": """请一步步分析以下问题，给出详细的推理过程：

{question}
""",
    },
    
    "covalent": {
        "name": "共价键（Covalent）",
        "prompt": """【目标】构建严密的逻辑链条，每一步都有明确的逻辑依据

请按以下公理化方法进行推理：

1. **定义公理层**
   - 列出已知事实和前提（不需要证明）
   - 标记为 [AXIOM]

2. **构建定理层**
   - 每个推理步骤必须引用前面的事实
   - 使用格式：[STEP-N] 因为 [引用], 所以 [结论]
   
3. **保持因果链完整性**
   - 如果某一步骤无法找到依据，标记 [GAP] 并说明
   - 不允许跳跃式推理

现在请解决以下问题：
{question}
""",
    },
    
    "hydrogen": {
        "name": "氢键（Hydrogen）",
        "prompt": """【目标】在每个关键步骤后主动寻找错误

采用"怀疑一切"的思维方式：

每完成一个推理步骤后，立即进行"反审计"：
1. 【假设反转】如果这个结论是错的，可能因为什么？
2. 【边界测试】这个结论在什么情况下不成立？
3. 【量级检查】结果的数量级是否合理？

【格式】
推理步骤: [内容]
├─ 反审计 1: [假设反转] ...
├─ 反审计 2: [边界测试] ...
└─ 反审计 3: [量级检查] ...
   └─ 结论: [继续/修正/回退]

只有当三个反审计都通过时，才能进入下一步。

现在请解决以下问题：
{question}
""",
    },
    
    "vanderwaals": {
        "name": "范德华键（VanDerWaals）",
        "prompt": """【目标】同时探索两条不同的推理路径，对比结果

对于此问题，请同时构建两条独立的推理路径：

【路径 A】（常规/直接方法）
├─ 步骤A1: ...
├─ 步骤A2: ...
└─ 结论A: ...

【路径 B】（替代/逆向方法）
├─ 步骤B1: ...
├─ 步骤B2: ...
└─ 结论B: ...

【对比分析】
├─ 结论一致性: [A和B是否得到相同结果]
├─ 复杂度对比: [哪条路径更简洁]
├─ 可靠性对比: [哪条路径更不易出错]
└─ 最终选择: [选择哪条路径的结论，为什么]

如果两条路径结论不同，分析差异原因并解决。

现在请解决以下问题：
{question}
""",
    },
    
    "c_plus_h": {
        "name": "共价+氢键（C+H）",
        "prompt": """【目标】构建严密的逻辑链，并在关键节点进行反思验证

采用"推进-检查"循环模式：

【Phase 1: 推进】（构建2-3步逻辑链）
→ 步骤N: [基于前序步骤的逻辑推理]
→ 步骤N+1: ...

【Phase 2: 检查】（对上述步骤进行反思）
→ 检查点:
   ├─ 逻辑连贯性: [步骤间是否合理衔接]
   ├─ 前提可靠性: [是否依赖未经证实的前提]
   └─ 结论合理性: [中间结论是否合理]

【Phase 3: 决策】
→ 如果检查通过 → 继续 Phase 1
→ 如果发现问题 → 回退并修正

循环直到得到最终答案。

现在请解决以下问题：
{question}
""",
    },
    
    "full": {
        "name": "完整分子（Full）",
        "prompt": """【目标】构建具有稳定分子结构的完整推理过程

将推理过程建模为分子结构，包含三种化学键：

【结构规划】
├─ Deep Reasoning (共价键): ~60% - 主干推理
├─ Self-Reflection (氢键): ~20% - 关键节点验证
└─ Self-Exploration (范德华键): ~20% - 分支探索

【执行框架】

1. 【初始化】建立推理起点
   → 明确问题、定义变量、列出已知条件

2. 【主干扩展】（Deep Reasoning）
   → 构建连续的逻辑链
   → 格式：[D-N] 因为 [依据], 所以 [结论]

3. 【关键节点验证】（Self-Reflection）
   → 在重要结论处暂停执行反审计
   → 格式：[R-N] 验证 [D-M]...

4. 【分支探索】（Self-Exploration）
   → 在不确定性高的节点探索多个方向
   → 格式：[E-N] 替代路径: ...

5. 【收敛整合】
   → 主线推理收敛到答案
   → 验证最终答案
   → 给出置信度评估

现在请解决以下问题：
{question}
""",
    },
}


def call_glm5_api(prompt, temperature=0.7):
    """调用 GLM-5 API"""
    try:
        # 尝试使用 zhipuai SDK
        from zhipuai import ZhipuAI
        
        client = ZhipuAI(api_key=API_KEY)
        
        start_time = time.time()
        
        response = client.chat.completions.create(
            model="glm-5",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        return {
            "text": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens,
            "response_time_ms": elapsed_ms,
            "success": True,
        }
    except ImportError:
        # 如果没有 SDK，使用 requests
        import requests
        
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        
        data = {
            "model": "glm-5",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        
        start_time = time.time()
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            return {
                "text": result["choices"][0]["message"]["content"],
                "tokens_used": result["usage"]["total_tokens"],
                "response_time_ms": elapsed_ms,
                "success": True,
            }
        else:
            return {
                "text": f"API Error: {response.status_code}",
                "tokens_used": 0,
                "response_time_ms": elapsed_ms,
                "success": False,
                "error": response.text,
            }
    except Exception as e:
        return {
            "text": f"Error: {str(e)}",
            "tokens_used": 0,
            "response_time_ms": 0,
            "success": False,
            "error": str(e),
        }


def evaluate_response(response_text, problem):
    """评估响应质量"""
    # 简化的评估逻辑
    
    # 计算推理步数
    steps = len([line for line in response_text.split('\n') 
                 if line.strip() and ('步骤' in line or line.startswith('[') or 
                                      '因为' in line or '所以' in line)])
    
    # 响应长度
    length = len(response_text)
    
    # 是否包含答案关键词（简化版）
    has_answer = len(response_text) > 100
    
    return {
        "steps": steps,
        "length": length,
        "has_answer": has_answer,
    }


def run_experiment():
    """运行完整实验"""
    print("="*80)
    print("Long CoT 分子结构提示词工程对比实验 - 真实 API")
    print("="*80)
    print(f"API Key: {API_KEY[:20]}...")
    print(f"问题数: {len(PROBLEMS)}")
    print(f"模板数: {len(TEMPLATES)}")
    print(f"总测试数: {len(PROBLEMS) * len(TEMPLATES)}")
    print("="*80)
    
    results = []
    
    template_keys = list(TEMPLATES.keys())
    
    for i, problem in enumerate(PROBLEMS):
        print(f"\n[{i+1}/{len(PROBLEMS)}] 问题 {problem['id']} ({problem['category']})")
        print("-"*80)
        
        for j, template_key in enumerate(template_keys):
            template = TEMPLATES[template_key]
            print(f"  [{j+1}/{len(template_keys)}] {template['name']}...", end=" ", flush=True)
            
            # 格式化提示词
            prompt = template['prompt'].format(question=problem['question'])
            
            # 调用 API
            api_result = call_glm5_api(prompt, temperature=0.7)
            
            if api_result['success']:
                # 评估响应
                eval_result = evaluate_response(api_result['text'], problem)
                
                result = {
                    "experiment_id": f"EXP-{datetime.now().strftime('%Y%m%d%H%M%S')}-{problem['id']}-{template_key}",
                    "timestamp": datetime.now().isoformat(),
                    "model": "glm-5",
                    "problem_id": problem['id'],
                    "problem_category": problem['category'],
                    "template_type": template_key,
                    "template_name": template['name'],
                    "question": problem['question'],
                    "response_text": api_result['text'],
                    "tokens_used": api_result['tokens_used'],
                    "response_time_ms": round(api_result['response_time_ms'], 2),
                    "evaluation": eval_result,
                }
                
                results.append(result)
                print(f"✓ (Tokens: {api_result['tokens_used']}, Time: {api_result['response_time_ms']:.0f}ms)")
            else:
                print(f"✗ Error: {api_result.get('error', 'Unknown')}")
            
            # 避免 API 限流
            time.sleep(0.5)
    
    # 保存结果
    output_file = os.path.join(RESULTS_DIR, f"raw_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*80)
    print(f"实验完成！结果已保存到: {output_file}")
    print(f"成功: {len(results)}/{len(PROBLEMS) * len(TEMPLATES)}")
    
    return results, output_file


def analyze_results(results):
    """分析实验结果"""
    
    # 按模板分组
    by_template = {}
    for r in results:
        key = r['template_type']
        if key not in by_template:
            by_template[key] = []
        by_template[key].append(r)
    
    # 计算统计信息
    analysis = []
    
    for template_key, template_results in by_template.items():
        n = len(template_results)
        
        stats = {
            "模板": TEMPLATES[template_key]['name'],
            "样本数": n,
            "平均Token数": sum(r['tokens_used'] for r in template_results) / n,
            "平均响应时间(ms)": sum(r['response_time_ms'] for r in template_results) / n,
            "平均推理步数": sum(r['evaluation']['steps'] for r in template_results) / n,
            "平均响应长度": sum(r['evaluation']['length'] for r in template_results) / n,
        }
        
        analysis.append(stats)
    
    return analysis


def generate_report(results, analysis, output_file):
    """生成 Markdown 报告"""
    
    report = f"""# Long CoT 分子结构提示词工程对比实验报告

> 实验时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 模型：GLM-5
> API Key：{API_KEY[:20]}...

## 一、实验概述

### 实验目标
验证不同"分子结构"提示词模板对推理质量的影响。

### 实验设计
- **问题数**：{len(PROBLEMS)}
- **模板数**：{len(TEMPLATES)}
- **总测试数**：{len(results)}

### 问题集
"""
    
    for problem in PROBLEMS:
        report += f"- **{problem['id']}** ({problem['category']}): {problem['question'][:50]}...\n"
    
    report += "\n### 模板集\n"
    
    for key, template in TEMPLATES.items():
        report += f"- **{template['name']}** ({key})\n"
    
    report += "\n## 二、实验结果\n\n"
    report += "### 汇总统计\n\n"
    report += "| 模板 | 样本数 | 平均Token数 | 平均响应时间(ms) | 平均推理步数 | 平均响应长度 |\n"
    report += "|------|--------|-------------|------------------|--------------|-------------|\n"
    
    for stats in analysis:
        report += f"| {stats['模板']} | {stats['样本数']} | "
        report += f"{stats['平均Token数']:.1f} | {stats['平均响应时间(ms)']:.0f} | "
        report += f"{stats['平均推理步数']:.1f} | {stats['平均响应长度']:.0f} |\n"
    
    report += "\n### 详细结果\n\n"
    
    for i, result in enumerate(results, 1):
        report += f"#### 测试 {i}: {result['problem_id']} - {result['template_name']}\n\n"
        report += f"- **问题**: {result['question'][:100]}...\n"
        report += f"- **Token数**: {result['tokens_used']}\n"
        report += f"- **响应时间**: {result['response_time_ms']:.0f}ms\n"
        report += f"- **推理步数**: {result['evaluation']['steps']}\n"
        report += f"- **响应长度**: {result['evaluation']['length']} 字符\n\n"
        report += f"**响应内容**:\n\n```\n{result['response_text'][:500]}...\n```\n\n"
        report += "---\n\n"
    
    report += """## 三、关键发现

### 1. 模板效果对比

（待补充具体发现）

### 2. Token 消耗分析

（待补充）

### 3. 推理步数分析

（待补充）

## 四、结论与建议

（待补充）

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    report_file = os.path.join(RESULTS_DIR, f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"分析报告已生成: {report_file}")
    
    return report_file


def main():
    """主程序"""
    # 运行实验
    results, output_file = run_experiment()
    
    # 分析结果
    analysis = analyze_results(results)
    
    # 生成报告
    report_file = generate_report(results, analysis, output_file)
    
    # 打印简要统计
    print("\n" + "="*80)
    print("实验结果摘要")
    print("="*80)
    
    for stats in analysis:
        print(f"\n{stats['模板']}:")
        print(f"  平均Token数: {stats['平均Token数']:.1f}")
        print(f"  平均响应时间: {stats['平均响应时间(ms)']:.0f}ms")
        print(f"  平均推理步数: {stats['平均推理步数']:.1f}")
    
    print("\n" + "="*80)
    print("文件输出:")
    print(f"  原始结果: {output_file}")
    print(f"  分析报告: {report_file}")
    print("="*80)


if __name__ == "__main__":
    main()
