# 对比实验设计

## 决策边界

本实验不预设赢家。Mem0 是优先实测候选，EverOS 恢复候选资格；只有相同业务输入、模型、检索池和评分规则下的运行证据才能改变结论。执行状态与能力类别分开，未调用模型的 launcher 检查不能计入能力 PASS。

执行顺序为：provider doctor → 单条 F02 smoke → 两候选 12 个 decision 用例的 R0/R1 → 六个 P-native 复用探针 → 门禁通过后 40 用例。decision 集为 `F05,N03,U01,U05,D02,D03,P01,P04,C02,T01,E01,E04`；P-native 集为 `F05,D03,P01,C02,T01,E01`。

## R0、R1 与 P-native

| 轨道 | 两候选共同条件 | 用途 |
|---|---|---|
| R0 | dense vector，候选池 5，最终 Top-5，不 rerank | 检索基线 |
| R1 | dense vector Top-20，统一调用 SiliconFlow `BAAI/bge-reranker-v2-m3`，最终 Top-5 | 隔离公共 rerank 增益 |
| P-native | 候选更贴近原生的作用域/形成机制，仅跑 6 个探针 | 判断复用面与改造点，不参与效果排名 |

EverOS 配置中出现 reranker 不表示 R0 使用了 rerank。EverOS 自带 reranker 是其 agent/hybrid/knowledge 路径可用的原生依赖；本实验 R0 强制 `method=vector`，R1 则在两个候选之外调用同一个公共 rerank。Mem0 不配置其原生 reranker，因为锁定 OSS 版本没有通用 SiliconFlow remote rerank provider。这样 R0/R1 的唯一效果变量是公共 rerank，而不是候选各自不同的原生检索栈。

不设置完整 R2：当前问题是轻量服务能复用多少，而不是比较两套推荐全家桶。P-native 六个探针足以暴露作用域、来源、冲突/时间和 direct record 的改造边界，且不会用不可比配置给候选排效果名次。

## 统一配置

- LLM：`qwen3.7-plus`，DashScope OpenAI-compatible endpoint，`temperature=0`，`enable_thinking=false`。
- Embedding：`BAAI/bge-m3`，SiliconFlow OpenAI-compatible endpoint，固定输出维度 1024。
- Rerank：`BAAI/bge-reranker-v2-m3`，SiliconFlow `/v1/rerank`。
- Mem0：Qdrant local + SQLite history。配置名仍使用 schema 支持的 `openai`，factory 在 worker 内替换为只增加 Qwen thinking 参数的 shim；embedding shim 只移除 SiliconFlow 不需要的 `dimensions` 请求字段，Qdrant 维度仍为 1024。
- EverOS：Markdown source of truth + SQLite WAL + LanceDB。R0/R1 均使用 user episode `vector` search。

宿主机存在 SOCKS `all_proxy`，而两个候选虚拟环境没有 `socksio`。launcher 仅在候选子进程移除 SOCKS fallback，保留显式 `http_proxy`/`https_proxy`，避免客户端初始化失败；该行为属于运行环境兼容设置。

## 隔离映射

每个 candidate/track/run/case 使用新 namespace；一个 case 内的不同用户共享同一个候选实例，不能用物理分库伪造用户隔离。

- Mem0：`user_id` 固定 owner，业务字段写入 metadata；读取由服务端 principal 映射组合出 user_public、domain、获准 project、获准 agent_private 过滤集合。无 principal 返回空集合，禁止无过滤回退。
- EverOS：owner 使用 `user_id`，作用域映射到独立 `app_id/project_id`；读取同样由服务端 principal 枚举获准空间。搜索接口一次只能固定一个空间，控制器合并、去重后截断 Top-k。

上述只是 benchmark 的静态身份绑定与过滤验证，不宣称两个 OSS 已提供生产认证。

## 判分与证据

合成私有码、必需 token、禁止 token 和原生 source ref 自动检查；原子语义命题仍标记 `REVIEW_REQUIRED`，需人工阅读候选实际 hit 后确认。EverOS 只返回 session 级来源时不能用 harness 已知 message ID 补成“原生来源通过”。每次运行写入独立 `artifacts/<run_id>`；缺密钥、网络或模型时写 `BLOCKED`，不生成假响应。

自动检查硬失败时按 `poll_intervals_seconds` 重发同一 search，直到通过、`max_poll_attempts` 或 `visibility_deadline_seconds` 耗尽为止；`FAIL` 只在可见性窗口耗尽后记录。原因：EverOS flush 返回 `extracted` 后，OME 策略管道（atomic facts 提取、索引）仍异步完成，立即搜索可能为空。轮询对两候选是同一条代码路径，负向用例首查即通过不消耗窗口；传输层 FAIL/TIMEOUT 不轮询。每次尝试写入 `search_attempt` 事件供审计。
