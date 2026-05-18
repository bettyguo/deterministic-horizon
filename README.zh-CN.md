<p align="right">
  <a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a>
</p>

<div align="center">

# 确定性视界 (The Deterministic Horizon)

**当扩展的思维链不再有效——工具委派成为唯一的出路。**

[![Paper](https://img.shields.io/badge/paper-ICML%202026-b31b1b.svg)](paper/ICML2026_DeterministicHorizon_FINAL.pdf)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%E2%80%933.12-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/deterministic-horizon/deterministic-horizon/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-46aef7.svg)](https://github.com/astral-sh/ruff)
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/deterministic-horizon/deterministic-horizon/blob/main/notebooks/01_quickstart.ipynb)

<img src="assets/figure_decay.png" alt="推理深度与准确率衰减" width="780"/>

**一句话总结——大约 22 步推理之后，每一款前沿大语言模型都会跌下悬崖。工具不会。**

</div>

---

## 30 秒速览

我们测试了 **12 款前沿模型** 在 **状态空间搜索**（这类问题用 BFS 能在几毫秒内解决）上的表现——它们全部在同一个瓶颈处崩溃：

|  | 神经 CoT (C1) | **工具委派 (C3)** |
|---|---|---:|---:|
| GPT-4o | 28% | **90%** |
| Claude 4.5 Opus | 35% | **94%** |
| o3-mini | 42% | **94%** |
| DeepSeek-R1 | 40% | **93%** |

这个瓶颈出现在 **d\* ∈ [19, 31]** 步推理之间。我们给这个瓶颈起了个名字（**确定性视界**），从注意力信息论中推导出它（定理 1），并证明微调 *无法* 突破它（定理 4）。

> **为什么重要？** 今天每一个正在上线的智能体系统——代码智能体、浏览器代理、规划器——都必须决定：*何时*思考，*何时*调用工具。超过 d\* 之后，"再多想一会儿"也无济于事。交给工具吧。

---

## 五行业务可用的代码

```python
from deterministic_horizon import should_delegate

# 在你的规划器循环中：
if should_delegate(estimated_depth=subproblem_depth, model="claude-4.5-opus"):
    answer = call_tool(subproblem)        # BFS / 搜索 / SQL / 验证器
else:
    answer = call_llm(subproblem)         # 神经思维链
```

需要完整的决策依据（用于日志或评估）？

```python
>>> from deterministic_horizon import delegation_decision
>>> d = delegation_decision(estimated_depth=27, model="claude-4.5-opus")
>>> d.explain()
"At estimated depth d=27, model 'claude-4.5-opus' is expected to reach 31% via CoT
 vs. 92% via tools (horizon d*=28). → delegate."
```

各模型视界、何时*不*适用此方法，以及三种生产环境路由模式：[docs/when-to-delegate.md](docs/when-to-delegate.md)。

---

## 60 秒离线演示（无需 API 密钥）

```bash
git clone https://github.com/deterministic-horizon/deterministic-horizon
cd deterministic-horizon
pip install -e .
python examples/demo.py            # 离线视界估计
python examples/agent_routing.py   # 路由模式，端到端
```

你将看到**实时的视界估计**结果——来自合成的去相干模拟器，去相干模型拟合 R² ≈ 0.97，以及一张达到发表质量的可视化图表保存到 `analysis/figure_decay.png`（与首页展示图一致）。

想要**真实的大模型**？将 API 密钥添加到 `.env`（参考 `.env.example`），然后：

```bash
dh evaluate --model gpt-4o --instances data/sample/permutation_n8.json \
            --conditions C1,C3 --output results/gpt4o.json
dh analyze  --results results/gpt4o.json --output analysis/gpt4o/
```

---

## 核心发现（复现论文结果）

| 指标 | 数值 | 为什么重要 |
|---|---|---:|---|
| 确定性视界 $d^*$ | **19–31 步** | 超过此深度，神经 CoT 准确率 < 50% |
| 工具集成准确率 | **86–94%** | 覆盖 8 个任务领域、12 个模型 |
| 跨模型相关性 $r$ | **0.81–0.91** | 失败是*架构性的*，而非训练所致 |
| 微调恢复 | **+3.2%** | 定理 4 预测 < 5%（对比竞争理论 > 30%） |
| 去相干模型拟合 | **R² = 0.96** | 超指数衰减与数据吻合 |

完整复现：

```bash
make paper-figures   # 重建论文中的每一张图
make paper-tables    # 重建论文中的每一个表格
```

详见 [docs/reproducing.md](docs/reproducing.md)（包含种子值、成本和时间分解）。

---

## 项目结构

```
deterministic-horizon/
├── src/deterministic_horizon/
│   ├── policy.py       # should_delegate / delegation_decision（工程接入点）
│   ├── tasks/          # PermutationProbe, FSA-Sim, ArithChain（含 BFS 预解器）
│   ├── models/         # 统一接口：OpenAI / Anthropic / DeepSeek / 本地模型
│   ├── metrics/        # SSJ, SFE, 超指数视界拟合, 自助法置信区间
│   ├── analysis.py     # 图表 + 表格生成
│   ├── runners.py      # 高层 `evaluate(...)` Python API
│   └── cli.py          # `dh generate | evaluate | analyze`
├── examples/
│   ├── demo.py            # d* 的离线复现
│   └── agent_routing.py   # 使用 should_delegate 的生产路由模式
├── notebooks/
│   └── 01_quickstart.ipynb   # 60 秒 Colab 快速上手
├── docs/                  # 何时委派 · 定理速查 · 常见问题 · 复现指南
├── data/sample/           # 预生成的排列实例
├── results/sample/        # 预计算的合成结果
├── configs/               # OmegaConf 配置文件（模型 × 任务 × 实验）
├── paper/                 # ICML 2026 LaTeX + 最终 PDF
└── tests/                 # pytest 测试套件（冒烟 / 指标 / 任务 / 策略 / 分析）
```

---

## 这与"过度思考"类论文有何不同

| 对比维度 | 简单性偏差（先前工作） | **去相干（本研究）** |
|---|---|---:|---|
| 原因 | 训练偏好短输出 | 信息论容量界限 |
| 修复 | 在长轨迹上微调 | **无法修复**——它是架构性的 |
| 微调增益预测 | > 30% | **< 5%** ← 我们实测 3.2% ✅ |
| 提示长度增益预测 | > 10% | **< 2%** ← 我们实测 1.1% ✅ |
| 跨模型相关性 $r$ 预测 | 低 | **高** ← 我们实测 0.86 ✅ |
| 编码器-解码器优势 | 无 | **2–3×** ← 我们实测 2.8× ✅ |

四个分叉预测，全部验证。详见论文第 1 节或 [docs/theorem-cheatsheet.md](docs/theorem-cheatsheet.md)。

---

## 核心定理（一句话版）

一个 decoder-only 变压器能够可靠追踪的状态数为

$$|\mathcal{S}_{\text{track}}| \;\leq\; c(\delta, \rho_{\max}) \cdot 2^{H \cdot \log_2(L/H) \cdot \sqrt{d_h}}$$

并存在**匹配的下界**（定理 2）。每步误差依赖于上下文：$\varepsilon(d) = \varepsilon_0 + \gamma\, d/L$（定理 1，从注意力熵推导），得到封闭形式的确定性视界：

$$d^\star \;\approx\; \frac{1}{\gamma}\Bigl(\sqrt{2 L \ln(1/\alpha)} \;-\; \varepsilon_0\, L\Bigr)$$

以及微调上限 $\text{Acc}_{\text{fine-tune}} \leq \text{Acc}_{\text{baseline}} + O(d^\star/d)$。证明见附录，消融实验见第 6 节。通俗版：[docs/theorem-cheatsheet.md](docs/theorem-cheatsheet.md)。

---

## Python API

```python
from deterministic_horizon import (
    PermutationTask, generate_instances, evaluate,
    estimate_horizon, fit_decoherence_model,
    should_delegate, delegation_decision,
)

# 1. 生成任务实例
task = PermutationTask(n_elements=8, seed=42)
instances = task.generate_instances(n_instances=400, min_depth=4, max_depth=40)

# 2. 评估模型（需要在 .env 中配置 API 密钥）
results = evaluate(model="gpt-4o", instances=instances, conditions=["C1", "C3"])

# 3. 估计视界
horizon = estimate_horizon(results, threshold=0.5)
print(f"d* = {horizon['d_star']:.1f}  (R² = {horizon['r_squared']:.3f})")

# 4. 在你的智能体路由决策中使用它
should_delegate(estimated_depth=horizon['d_star'] + 5, model="gpt-4o")  # → True
```

### 实验条件

| 条件 | 描述 |
|---|---|
| **C1** | 神经思维链（标准提示） |
| **C2** | 直接回答，无需推理 |
| **C3** | 工具集成（BFS / 验证器访问） |
| **C4** | 鼓励长输出的提示（"尽可能多步骤"） |
| **C5** | 在最优长度轨迹上微调 |

---

## 安装

```bash
# 精简安装（核心指标 + 分析，不含大模型客户端）
pip install -e .

# 包含 OpenAI + Anthropic 客户端
pip install -e ".[openai,anthropic]"

# 包含本地模型支持（PyTorch / transformers）
pip install -e ".[local]"

# 全部安装
pip install -e ".[all,dev]"
```

需要 Python 3.10–3.12。已在 Linux、macOS 和 Windows 上通过 [CI](.github/workflows/ci.yml) 测试。

---

## 常见问题（精选）

<details>
<summary><b>演示结果是精心挑选的吗？</b></summary>

不是。演示使用了一个*合成*推理器，其每步误差严格遵循论文中的上下文依赖模型（定理 1）。`results/paper/` 中的跨模型实证数据来自真实的 API 调用——12 个模型 × 5 个条件 × 8 个任务 × 500 个实例 × 3 个种子 = 720,000 次评估，API 总成本 $3,420。
</details>

<details>
<summary><b>这与"Transformer 做不了 X"类论文有何不同？</b></summary>

先前的表达能力工作证明了 Transformer *原则上无法计算什么*。我们展示的是前沿模型*在实践中无法可靠执行什么*，给出了这个瓶颈的封闭形式界，并证明了微调无法让它移动。确定性视界是一个可用的工程量，而非渐近理论。
</details>

<details>
<summary><b>这是否意味着推理模型无用？</b></summary>

恰恰相反——它精确地告诉你*何时*使用它们、*何时*委派给工具。超过 $d^*$，神经 CoT 相当于抛硬币；工具有 50–70 个百分点的优势。
</details>

完整 FAQ：[docs/faq.md](docs/faq.md)。

---

## 引用

如果你使用了这份代码或在此基础上发展，请引用：

```bibtex
@inproceedings{deterministichorizon2026,
  title        = {The Deterministic Horizon: When Extended Reasoning Fails
                  and Tool Delegation Becomes Necessary},
  author       = {Anonymous Authors},
  booktitle    = {Proceedings of the 43rd International Conference on Machine Learning (ICML)},
  year         = {2026},
  url          = {https://github.com/deterministic-horizon/deterministic-horizon},
}
```

项目已包含 `CITATION.cff` 文件，GitHub 将自动填充"引用此仓库"按钮。

---

## 贡献

欢迎提交 bug 报告、新任务和扩展。参见 [`CONTRIBUTING.md`](CONTRIBUTING.md)；Issue 模板和 PR 检查清单已在 [`.github/`](.github/) 中配置。标记为 `good-first-issue` 的开放 Issue 是很好的入门起点。

**路线图**（欢迎参与）：

- [ ] SWE-Bench-State 集成
- [ ] WebArena-Nav 适配器
- [ ] Mamba / RWKV 去相干研究
- [ ] 交互式视界可视化（Web）
- [ ] Hugging Face Spaces 演示

---

## Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=deterministic-horizon/deterministic-horizon&type=Date)](https://star-history.com/#deterministic-horizon/deterministic-horizon&Date)

---

## 致谢

感谢 ICML 审稿人和讨论者的意见。微调实验使用了匿名捐赠者的计算资源；开源模型评估使用了 Together AI 的 credits。

---

<div align="center">

**觉得这个项目有用？** 给仓库加个 Star，并分享给所有在构建智能体系统的人。
确定性视界不是一个软性建议——它是一堵墙。

[论文](paper/ICML2026_DeterministicHorizon_FINAL.pdf) · [文档](docs/README.md) · [何时委派](docs/when-to-delegate.md) · [快速上手笔记本](notebooks/01_quickstart.ipynb) · [Issue](https://github.com/deterministic-horizon/deterministic-horizon/issues)

</div>
