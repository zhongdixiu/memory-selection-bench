# 能力验证矩阵

A～C 只能由成功执行证据确认；当前源码证据不足以把能力填成通过。D 表示接口/调用链已有明确核心缺口，E 表示尚未完成在线验证。

| 能力 | Mem0 | EverOS | 当前证据 |
|---|---|---|---|
| Dense Top-k 检索 | E | E | launcher 已启动，模型调用未执行 |
| 用户/域/项目隔离 | E | E | 映射与离线过滤测试通过，真实存储结果待跑 |
| 逐消息原生来源 | E | D | Mem0 metadata 待实测；EverOS 搜索 DTO 仅返回 session_id |
| direct_record | E | D | Mem0 `infer=false` 待实测；EverOS memory/add 仅接受消息 |
| 公共 R1 rerank | E | E | MockTransport 契约测试通过，SiliconFlow 待调用 |
| Email Agent M0/M1/M2 | E | E | 真实入口 worker 启动通过，模型任务待跑 |

## 运行状态汇总

该表只汇总可复现产物；`REVIEW_REQUIRED` 仍需人工语义判分。

| 候选 | 轨道 | PASS | FAIL | UNSUPPORTED | BLOCKED | REVIEW_REQUIRED |
|---|---:|---:|---:|---:|---:|---:|
| everos | r0 | 0 | 0 | 0 | 1 | 0 |
| mem0 | r0 | 0 | 0 | 0 | 1 | 0 |
