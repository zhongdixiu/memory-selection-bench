# Email Agent 接入验证（Agent 自动评估）

> 状态：暂定结论，未经过人工复核。证据为 `20260917T075118Z-mem0-r0-email-23637687`（Mem0）和 `20260917T075230Z-everos-r0-email-831c6799`（EverOS）的 `integration_results.json`。两份 manifest 的 `PASS` 只表示流程执行完成；任务要求需按回答另行判定。

## 运行方式与基本检查

M0 不预取记忆，M1 强制检索，M2 使用 Email Agent 的 `MemoryDependencyRouter`；每个 task×mode 使用新 session。两候选各有 6 条 preseed 写入，状态均为 `PASS` 且 `processed=true`；各有 6 次 bridge 检索（3 任务 × M1/M2），`bridge_writes=[]`。SMTP/IMAP 在 worker 中使用 stub，运行产物未记录真实邮件收发。M0 的 `tool_trace` 偶有 `memory_search`，但 bridge 在 M0 被禁用，因此没有产生真实记忆检索事件。

## 任务结果

| 任务 | Mem0 | EverOS | 自动评估说明 |
|---|---|---|---|
| A：P1 项目邮件 | M0 未给出 P1 决策；M1/M2 都写出“先接 Email Agent”，均未包含 P2 私有码 | M0/M1/M2 均未给出 P1 决策；M1/M2 的检索只返回 shared 空间内容 | EverOS 的 P1 episode 可在候选自产 markdown 中找到，但未进入任务 A 的检索命中；表现与已知跨空间索引冲突一致。未出现 P2 私有码只证明没有观察到泄漏，不能抵消 P1 召回失败 |
| B：技术报告 | M1/M2 都包含“指标”；M0 也包含该词 | M0 不含“指标”，M1/M2 包含 | Mem0 的 M0 已命中必要词，因此仅凭该 token 不能把 B 的改进归功于记忆；EverOS 的 M0→M1/M2 有更清晰的回答差异 |
| C：限流处理 | M0 缺关键信息；M1/M2 均说明先读 `Retry-After`、缺失时交人工、避免盲目重试 | M0 缺关键信息；M1/M2 也表达相同处理规则 | 两候选 M1 的回答分别使用“转为人工处理”“转由人工处理”，语义正确但不包含精确子串“转人工”；两份注入上下文都包含“转人工”，所以不能归因为预取缺失 |

按回答语义，Mem0 满足 A/B/C 三项任务，EverOS 满足 B/C 两项。按现有严格 token 布尔值统计，Mem0 在 6 个 M1/M2 回答中有 5 个满足全部必要 token，EverOS 有 3 个；差异包含 C-M1 的词面误报。两候选任务 C 的回答均未推荐盲目重试。M2 的路由在三项任务都启用语义记忆，未观察到相对 M1 的路由漏检。

## 时延与边界

| 指标 | Mem0 | EverOS |
|---|---:|---:|
| preseed 单条写入回执 `elapsed_ms` | 2.4～3.4 秒 | 6.2～7.8 秒 |
| M1/M2 的 `tasks[].elapsed_ms` | 2.1～4.3 秒 | 2.2～7.7 秒 |

`tasks[].elapsed_ms` 从预取检索和上下文构建**之后**开始计时，只覆盖 Agent 回答，不能作为“检索→注入→回答”的端到端时延或容量指标。以上时延也只是单次小样本运行。下一轮自动验证应在修复 EverOS 索引主键后重跑任务 A，并把语义判定与严格 token 判定分开输出。
