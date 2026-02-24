# Long CoT 分子结构提示词工程对比实验

> 基于 arXiv:2601.06002v2 《The Molecular Structure of Thought: Mapping the Topology of Long Chain-of-Thought Reasoning》

## 📋 项目概述

本项目旨在通过系统性实验，验证论文提出的"分子结构"理论在提示词工程中的有效性。我们将推理过程类比为化学键：

- **共价键（Covalent）= Deep Reasoning** - 强逻辑连接，形成推理主干
- **氢键（Hydrogen）= Self-Reflection** - 反思验证，创建远程链接
- **范德华力（Van der Waals）= Self-Exploration** - 弱桥接，探索新方向

## 🎯 实验目标

1. **验证结构化提示词的有效性**：对比7种不同模板的推理质量
2. **找出最优键分布**：确定 Deep Reasoning、Reflection、Exploration 的最佳比例
3. **建立模板选择指南**：为不同类型问题推荐最合适的模板

## 📊 实验设计

### 问题集（5类）

| ID | 类别 | 难度 | 问题 |
|----|------|------|------|
| MATH-001 | 数学 | 中等 | 概率计算（红球蓝球） |
| LOGIC-001 | 逻辑 | 中等 | 骑士与无赖谜题 |
| CS-001 | 常识 | 简单 | 彩虹形成原理 |
| CODE-001 | 代码 | 简单 | 斐波那契数列 bug |
| STRATEGY-001 | 策略 | 中等 | 初创公司预算分配 |

### 模板集（7组）

| 组别 | 名称 | 核心特性 |
|------|------|----------|
| 1 | 基线（Baseline） | 直接提问，无结构引导 |
| 2 | 普通CoT（CoT-Basic） | "请一步步分析" |
| 3 | 共价键（Covalent） | 公理化推理，强逻辑链 |
| 4 | 氢键（Hydrogen） | 负反馈回路，自我验证 |
| 5 | 范德华键（VanDerWaals） | 双路径对比，探索替代方案 |
| 6 | 共价+氢键（C+H） | 推进-检查循环 |
| 7 | 完整分子（Full） | 三种键整合，完整推理框架 |

### 评估指标

- **正确性**：答案是否正确
- **推理步数**：推理链的长度
- **Token 消耗**：API 调用的 token 数
- **响应时间**：API 响应时间
- **逻辑连贯性**：步骤间逻辑关系是否合理

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests zhipuai
```

### 2. 配置 API Key

```bash
export ZAI_API_KEY="your_zhipu_api_key"
```

或直接在 `run_real_experiment.py` 中修改 `API_KEY` 变量。

### 3. 运行实验

```bash
cd /root/.openclaw/workspace/molecular-prompt-experiments
python3 run_experiment.py
```

### 4. 查看结果

- 原始结果：`results/raw_results_*.json`
- 分析报告：`results/analysis_*.md`

## 📁 项目结构

```
molecular-prompt-experiments/
├── README.md                    # 本文档
├── run_experiment.py            # 主实验脚本
├── results/                     # 实验结果
│   ├── raw_results_*.json      # 原始 API 响应
│   ├── analysis_*.md           # 分析报告
│   └── summary.csv             # 汇总表格（实验后生成）
├── prompt-templates/            # 提示词模板
│   ├── baseline.md             # 基线模板
│   ├── covalent.md             # 共价键模板
│   ├── hydrogen.md             # 氢键模板
│   ├── vanderwaals.md          # 范德华键模板
│   ├── c_plus_h.md             # 组合模板
│   └── full.md                 # 完整分子模板
├── docs/                        # 文档
│   ├── RESEARCH_REPORT.md      # 研究报告
│   ├── EXPERIMENTAL_DESIGN.md  # 实验设计
│   └── METHODOLOGY.md          # 方法论
└── scripts/                     # 辅助脚本
    ├── analyze_results.py      # 结果分析脚本
    └── generate_charts.py      # 图表生成脚本
```

## 📈 预期结果

### 假设 1：结构化提示词优于非结构化

```
完整分子（Full） > C+H > 单一模板 > 基线（Baseline）
```

### 假设 2：不同问题类型适配不同模板

| 问题类型 | 预期最优模板 |
|----------|--------------|
| 数学 | 共价键（强逻辑） |
| 逻辑 | C+H（逻辑+验证） |
| 常识 | 普通CoT |
| 代码 | C+H（逻辑+验证） |
| 策略 | 范德华键（探索） |

### 假设 3：最优键分布

- Deep Reasoning（共价键）：50-70%
- Self-Reflection（氢键）：15-25%
- Self-Exploration（范德华键）：10-20%

## ⚠️ 当前状态

**状态**：实验框架已就绪，等待 API 余额充值

**说明**：由于智谱 AI API 余额不足（错误码：1113），当前无法执行真实 API 调用。实验脚本已完全准备好，充值后可直接运行。

**演示数据**：`results/demo_results.json` 包含模拟数据，用于展示实验流程。

## 🔬 实验流程

1. **准备阶段**：加载问题集和模板
2. **执行阶段**：对每个问题应用每个模板（5×7=35次调用）
3. **评估阶段**：自动评估响应质量
4. **分析阶段**：生成对比报告和可视化
5. **总结阶段**：提炼最佳实践

## 📚 参考文献

1. Chen, Q., et al. (2026). *The Molecular Structure of Thought: Mapping the Topology of Long Chain-of-Thought Reasoning*. arXiv:2601.06002v2.
2. Wei, J., et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. NeurIPS.
3. Wang, X., et al. (2022). *Self-Consistency Improves Chain of Thought Reasoning*. arXiv.

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📮 联系方式

- 项目主页：https://github.com/shinjiyu/molecular-prompt-experiments
- 问题反馈：https://github.com/shinjiyu/molecular-prompt-experiments/issues

---

**最后更新**：2026-02-24
**实验状态**：待执行（API 余额不足）
