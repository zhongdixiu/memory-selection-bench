# Memory Selection Bench

Mem0 与 EverOS 的可复现对比验证控制器。当前已完成 40 用例、R0/R1/P-native 轨道、两个候选适配器、公共 rerank、Email Agent 接入 worker 和报告生成；真实模型效果实验尚未执行，当前原因是控制器进程未配置模型密钥。

## 运行

```bash
cd /home/zhongdixiu/codes/MemoryBench/memory-selection-bench
export PYTHONPATH=src
export DASHSCOPE_API_KEY='...'
export SILICONFLOW_API_KEY='...'
```

也可以把密钥写入项目根目录 `.env`（参考 `.env.example`，已被 git 忽略）：`memory-bench` 命令启动时会自动加载该文件；已在 shell 中 export 的同名变量优先于文件值。

```bash
/home/zhongdixiu/miniforge3/bin/python -m memory_bench doctor --config configs/bench.yaml --live
/home/zhongdixiu/miniforge3/bin/python -m memory_bench validate-cases --config configs/bench.yaml
/home/zhongdixiu/miniforge3/bin/python -m memory_bench smoke --candidate all --config configs/bench.yaml
/home/zhongdixiu/miniforge3/bin/python -m memory_bench run --candidate all --track r0 --suite decision --config configs/bench.yaml
/home/zhongdixiu/miniforge3/bin/python -m memory_bench run --candidate all --track r1 --suite decision --config configs/bench.yaml
/home/zhongdixiu/miniforge3/bin/python -m memory_bench probe --candidate all --config configs/bench.yaml
/home/zhongdixiu/miniforge3/bin/python -m memory_bench integrate --candidate all --track r0 --config configs/bench.yaml
/home/zhongdixiu/miniforge3/bin/python -m memory_bench report --config configs/bench.yaml
```

只有两候选 decision R0/R1 均完成门禁后再把 `--suite decision` 改为 `--suite full`。测试命令：

```bash
/home/zhongdixiu/miniforge3/bin/python -m pytest -q
```

设计、证据边界和 Agent 接入说明见 [docs/experiment-design.md](docs/experiment-design.md) 与 [docs/agent-integration.md](docs/agent-integration.md)；运行产物（manifest/case_results/events 等）的字段字典与人工评审速查见 [docs/artifacts-format.md](docs/artifacts-format.md)。
