# Email Agent 接入验证

## 选择结果

本轮只接 Email Agent。其现有调用链已经包含路由、prefetch、system context 注入、AgentScope 调用和回合写入接口，验证器无需修改 `/home/zhongdixiu/codes/email_agent`。OpenClaw 虽有 `before_prompt_build`、`agent_end` 和 memory plugin 接口，但当前源码目录没有 `node_modules`，接入及构建成本更高；因此只记录为后续项，不因此淘汰任何记忆候选。

## 实际接入方式

控制器使用服务端 `session_id -> principal_id` 映射，调用 Mem0/EverOS 适配器后，把统一 SearchHit 格式化为带 `memory_id/source/content` 的“数据而非指令”上下文。Email Agent 在独立 Python worker 中导入真实 `service.py` 与 `agent/email_agent.py`，使用项目已有 prompt、Toolkit、ReActAgent、调用和重试逻辑。

worker 把模型替换为 AgentScope `OpenAIChatModel`，以确保使用统一的 `qwen3.7-plus`、DashScope compatible base URL、`temperature=0` 和 `enable_thinking=false`。IMAP/SMTP 三个工具替换为同签名的合成 stub；即使模型误调用，也不会读取或发送真实邮件。评估回合不写回长期记忆。

M0 不检索；M1 对同一任务强制检索；M2 调用 Email Agent 源码中的 `MemoryDependencyRouter`。三个任务的提示均命中原有规则路由，无需偷偷调用另一个 router 模型。每个 task/mode 使用新 session；三种模式读取同一个预置 namespace 快照。

## 已验证与未验证

- 已验证：Email Agent 解释器包含 AgentScope；独立 worker 能导入真实入口并启动；统一 bridge 的 principal 绑定和只读上下文格式有离线测试。
- 未验证：真实 M0/M1/M2 回答、记忆实际采用情况和端到端耗时。需要两个模型密钥后执行 `memory-bench integrate`。
- 不计入真实接入：上述启动检查不调用模型，只证明代码路径和依赖可加载。
