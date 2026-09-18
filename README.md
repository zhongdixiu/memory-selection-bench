# Memory Selection Bench

Mem0 与 EverOS 的可复现对比验证控制器。当前已完成 40 用例、R0/R1/P-native 轨道、两个候选适配器、公共 rerank、Email Agent 接入 worker 和在线运行。`reports/` 包含 Agent 自动语义评估形成的暂定结论，尚未人工复核；执行与证据边界见 [docs/runbook.md](docs/runbook.md)。

## 运行

一次性安装（editable，之后 `memory-bench` 命令在任意目录可用，无需 PYTHONPATH）：

```bash
cd /home/zhongdixiu/codes/MemoryBench/memory-selection-bench
/home/zhongdixiu/miniforge3/bin/python -m pip install -e .
```

密钥写入项目根目录 `.env`（参考 `.env.example`，已被 git 忽略）：`memory-bench` 启动时自动加载；已在 shell 中 export 的同名变量优先于文件值。不便安装时可在项目根目录 `export PYTHONPATH=src` 后用 `python -m memory_bench` 等价执行。

```bash
memory-bench doctor --config configs/bench.yaml --live
memory-bench validate-cases --config configs/bench.yaml
memory-bench smoke --candidate all --config configs/bench.yaml
memory-bench run --candidate all --track r0 --suite decision --config configs/bench.yaml
memory-bench run --candidate all --track r1 --suite decision --config configs/bench.yaml
memory-bench probe --candidate all --config configs/bench.yaml
memory-bench integrate --candidate all --track r0 --config configs/bench.yaml
memory-bench report --config configs/bench.yaml
/home/zhongdixiu/miniforge3/bin/python scripts/audit_auto_reports.py
```

只有两候选 decision R0/R1 均完成门禁后再把 `--suite decision` 改为 `--suite full`。`memory-bench report` 会覆盖已改写的结论文件；已有报告时只运行 `scripts/audit_auto_reports.py` 做结构核对。测试命令：

```bash
/home/zhongdixiu/miniforge3/bin/python -m pytest -q
```

设计、证据边界和 Agent 接入说明见 [docs/experiment-design.md](docs/experiment-design.md) 与 [docs/agent-integration.md](docs/agent-integration.md)；运行产物（manifest/case_results/events 等）的字段字典与人工评审速查见 [docs/artifacts-format.md](docs/artifacts-format.md)；从零执行全流程的分步手册（含门禁、预期结果、故障处置）见 [docs/runbook.md](docs/runbook.md)。
