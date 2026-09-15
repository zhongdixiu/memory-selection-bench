# Agent 接入验证

选择 Email Agent：它已有 `MemoryDependencyRouter`、prefetch/context injection 和 append-turn 接口。benchmark 在控制器完成受控检索，再通过独立 worker 将上下文注入真实 AgentScope Agent，无需修改外部源码。

OpenClaw 本轮不接入：虽然有 memory plugin hooks，但当前目录未安装 node_modules，且接入面明显大于 Email Agent。此判断仅用于缩小验证范围，不构成能力淘汰结论。

M0（无记忆）、M1（强制检索）、M2（使用 Email Agent 原有 MemoryDependencyRouter）使用新 session；捕获写入与新会话召回分离，评估回答不写回，防止实验自身污染记忆。SMTP/IMAP 使用同签名 stub，禁止真实邮箱副作用。

执行记录：
- `20260914T085513Z-everos-r0-email-454ae7ed`：BLOCKED；missing environment variable(s): DASHSCOPE_API_KEY, SILICONFLOW_API_KEY
- `20260914T085513Z-mem0-r0-email-2b6e5067`：BLOCKED；missing environment variable(s): DASHSCOPE_API_KEY, SILICONFLOW_API_KEY
