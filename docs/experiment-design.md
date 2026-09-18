# 对比实验设计

## 决策边界

本实验不预设赢家。Mem0 是优先实测候选，EverOS 恢复候选资格；只有相同业务输入、模型、检索池和评分规则下的运行证据才能改变结论。执行状态与能力类别分开，未调用模型的 launcher 检查不能计入能力 PASS。

执行顺序为：provider doctor → 单条 F02 smoke → 两候选 12 个 decision 用例的 R0/R1 → 门禁通过后 40 用例 → 六个 P-native 复用探针 → Email Agent 接入 → 自动报告核对。P-native 与 full 使用独立运行目录，二者先后不影响各自结果。decision 集为 `F05,N03,U01,U05,D02,D03,P01,P04,C02,T01,E01,E04`；P-native 集为 `F05,D03,P01,C02,T01,E01`。

## R0、R1 与 P-native

| 轨道 | 两候选共同条件 | 用途 |
|---|---|---|
| R0 | dense vector，候选池 5，最终 Top-5，不 rerank | 检索基线 |
| R1 | dense vector Top-20，统一调用 SiliconFlow `BAAI/bge-reranker-v2-m3`，最终 Top-5 | 隔离公共 rerank 增益 |
| P-native | 候选更贴近原生的作用域/形成机制，仅跑 6 个探针 | 判断复用面与改造点，不参与效果排名 |

EverOS 配置中出现 reranker 不表示 R0 使用了 rerank。EverOS 自带 reranker 是其 agent/hybrid/knowledge 路径可用的原生依赖；本实验 R0 强制 `method=vector`，R1 则在两个候选之外调用同一个公共 rerank。Mem0 不配置其原生 reranker，因为锁定 OSS 版本没有通用 SiliconFlow remote rerank provider。R0/R1 的**检索配置差别**是公共 rerank；两轨分别重新写入和提取记忆，实测有提取结果翻转，因此不能仅据跨 run 终判差异推断 rerank 的因果增益。若需单独衡量 rerank，应固定同一份已写入记忆再比较检索轨道。

不设置完整 R2：当前问题是轻量服务能复用多少，而不是比较两套推荐全家桶。P-native 六个探针足以暴露作用域、来源、冲突/时间和 direct record 的改造边界，且不会用不可比配置给候选排效果名次。

## 统一配置

- LLM：`qwen3.7-plus`，DashScope OpenAI-compatible endpoint，`temperature=0`，`enable_thinking=false`。
- Embedding：`BAAI/bge-m3`，SiliconFlow OpenAI-compatible endpoint，固定输出维度 1024。
- Rerank：`BAAI/bge-reranker-v2-m3`，SiliconFlow `/v1/rerank`。
- Mem0：Qdrant local + SQLite history。配置名仍使用 schema 支持的 `openai`，factory 在 worker 内替换为只增加 Qwen thinking 参数的 shim；embedding shim 只移除 SiliconFlow 不需要的 `dimensions` 请求字段，Qdrant 维度仍为 1024。
- Mem0 提取语言对齐 shim：开箱 `ADDITIVE_EXTRACTION_PROMPT` 为全英文提示词（示例亦为英文、无语言保持规则），会把中文记忆改写成英文事实句（如"我喜欢详细回答。"→ "preference for receiving detailed answers"），使中文 required token 永远无法命中。EverOS 的默认 episode 提示词则自带强制性语言一致规则（"Output in the SAME language the conversation participants themselves write in"，en/zh 变体同规），因此不对齐 mem0 会引入单变量之外的混杂。锁定版 2.0.20 没有完整替换提取提示词的官方配置口，但有官方追加式 `custom_instructions` 配置字段（注入为提取提示词的最高优先级 Custom Instructions 段）；worker 将 mem0 自带的 `use_input_language` 语言保持文案（该版本已定义但未接线）原样写入该字段。该 shim 只把 mem0 补齐到 EverOS 的开箱规则水平，不越过对齐线（EverOS 不启用 zh prompt slot，避免额外优势）。此 shim 与 Qwen、dimensions shim 同属对齐类环境配置，不改检索与判分逻辑。开箱英文改写行为本身记为能力发现：shim 生效前的 mem0 run（截至 `20260915T031509Z-mem0-r1-decision-f7884dbc`）保留为开箱证据，差距表记录"无完整提取提示词替换口"的产品化风险。
- EverOS 语言规则合规性发现：默认提示词的语言一致规则为强制要求，但共享 LLM（qwen3.7-plus，temperature=0）对简短输入实测存在违规——decision 运行中 U01（"我喜欢详细回答。"）、C02/T01（"搬到上海"消息）产出英文 episode，导致中文 token 未命中，且 R1 跨语言 rerank 分数坍缩（英文命中 ≈0.001~0.007，中文命中 0.2~0.997）。此为候选默认提示词 + 共享模型下的真实产品风险（中文业务召回不稳定），记入能力矩阵与人工评审，不做 harness 侧修补。
- EverOS：Markdown source of truth + SQLite WAL + LanceDB。R0/R1 均使用 user episode `vector` search。

宿主机存在 SOCKS `all_proxy`，而两个候选虚拟环境没有 `socksio`。launcher 仅在候选子进程移除 SOCKS fallback，保留显式 `http_proxy`/`https_proxy`，避免客户端初始化失败；该行为属于运行环境兼容设置。

## 隔离映射

每个 candidate/track/run/case 使用新 namespace；一个 case 内的不同用户共享同一个候选实例，不能用物理分库伪造用户隔离。

- Mem0：`user_id` 固定 owner，业务字段写入 metadata；读取由服务端 principal 映射组合出 user_public、domain、获准 project、获准 agent_private 过滤集合。无 principal 返回空集合，禁止无过滤回退。
- **Mem0 写路径去重越界发现（decision 实测，D03/T01）**：mem0 V3 提取前的"既有记忆"去重检索与"最近消息"上下文仅按 `user_id/agent_id/run_id` 过滤，忽略全部 metadata（含 bench_namespace/scope/project）。owner 固定 + 共享实例下产生跨案例串扰：F05 先写"负责P1项目"→ D03 的"我是 P1 负责人。"被语义去重跳过（write PASS 但 `raw.results=[]`）；C02 先写"现居北京/已搬到上海"→ T01 两条写入（含补录历史时间戳）全部被跳过。读路径按 namespace 过滤，被去重依据的记忆对本案例检索永不可见——去重范围 ⊃ 检索范围，0 hits 为结构性结果。因此 mem0 的 decision 套件存在案例顺序依赖（F05→D03、C02→T01）；该 FAIL 归因能力层（写路径去重跨越隔离边界），不是 harness 缺陷，不做 harness 侧规避（改 user_id 映射会替换被测隔离方案并掩盖缺陷）。EverOS 物理空间分区 + episode 追加式写入无语义去重，同套件顺序下免疫，两候选 decision run 均在相同案例顺序下完成，对比公平。此发现是"metadata 映射隔离"方案的产品化风险实证：同一事实先入上下文 A 即静默抑制上下文 B 的写入且 B 无法检索。N03 的空写入属良性（否认后的推测被保守跳过，正是该负例期望行为），评审须与 D03/T01 区分。
- **Mem0 写路径发现·full 40 例扩展（runs 9109eb89/5ec2c317）**：抑制面比 decision 宽得多，11 处空写入中确证/字面重叠推断的跨案例去重达 7 处——D01「邮件回复要简洁」←F03、D04-w1←F03、D04-w2「报告规则是详细」←D01、P02「P1 先接邮件」←P01（跨语言等价：邮件↔Email Agent，且跨 project 命名空间）、C02-w1「现居北京」←U04、T01-w1「已搬到上海」←C02、D03←F01/F05。D01/D04/P02 检索 0 hits 是复合作用：期望记忆在写路径被吞噬 + 吞噬它的前序记忆因读路径 metadata 过滤（domain/project）对本 principal 正确不可见——读侧隔离本身实测有效，FAIL 全部归因写侧。新发现两类：① **提取遗漏**：F04「对外发送前必须先让我确认。」双轨稳定未提取且无前序等价记忆，属提取召回缺陷而非去重；② **写路径非确定性**：temp=0 下 N01（假设性问题 R0 跳过/R1 忠实存为"用户询问…"）、N03（R0 跳过/R1 存否认记忆）、U01-w1（R0 存/R1 疑与 F03 判弱等价跳过）在两轨间翻转，边缘等价判定不可复现，mem0 full 结果无案例级 bit 复现性；③ **内容级跨域渗出**：提取上下文同样无视 metadata，D01-w2 落库的报告域记忆文本中编织进了邮件域偏好（"这与之前要求的邮件回复简洁形成对比"），D04-w3 同——即使写入未被抑制，隔离边界在记忆内容层也被部分穿透，评审阅读 hits 时须留意。衍生判分方法局限：N03-R1 的 FAIL 是**否定子串误判**——存储记忆"用户明确否认负责预算"语义正确，但包含 forbidden 子串"负责预算"；机械判分不识别否定，评审须按语义改判（harness 不改判分逻辑，保持机械规则可复现）。
- EverOS：owner 使用 `user_id`，作用域映射到独立 `app_id/project_id`；读取同样由服务端 principal 枚举获准空间。搜索接口一次只能固定一个空间，控制器合并、去重后截断 Top-k。
- **EverOS 索引完整性缺陷发现（full 实测，runs 4a9195d0/7d5ce615，双轨稳定复现）**：episode 序号按空间独立计数（每个空间当日都从 `ep_<date>_00000001` 起），而共享 LanceDB `episode` 表（`runtime/<run>/.index/lancedb`）主键 `{user}_ep_{date}_{seq}` **不含 app/project 成分**——同一 case 的单 session 先后 flush 到多个空间时（D01/D04/P02），后完成空间的 cascade upsert 覆盖先前空间的索引行。markdown 事实源完好、提取与空间路由本身正确，但被覆盖空间的内容从检索索引消失。签名：attempt 曲线 `[1, 0, 0, …]`（首查命中，随后归零）。整个 run 终态索引仅 5 行（每个 (user,date,seq) 只剩最后一个写者）；其余案例当时可检索只因每案例检索紧跟自身写入、在下一案例覆盖前完成。同用户同日多空间写入是产品真实场景（邮件域 + 报告域），属结构性缺陷，D01/D04/P02 的 FAIL 归因能力层·索引完整性。LanceDB 只保留 1 个版本（自动 compaction），无法做时间旅行取证，机制由 markdown 对照 + attempt 曲线 + 终态表内容三方证据链确认。对照意义：mem0 与 everos 在 D01/D04/P02 **双双 FAIL 但机制不同**（mem0＝写路径去重越界吞噬写入；everos＝索引主键冲突覆盖），读侧隔离两候选均有效。
- **负例可见性盲区披露（everos，方法论限制）**：可见性轮询只在硬失败时触发；负例（无 required token）0 hits 不构成硬失败，检索在写入 flush 后约 1s 单次执行即定案，而 everos 索引异步收敛实测约 20~40s（对照 F03 曲线 `[0,0,1,…]`）。因此 everos 负例的 0 hits 不能区分「内容级克制」与「索引未就绪」。runtime markdown 证实 N 组消息实际全部被提取存储且表述忠实（疑问存为「U1询问…」、否认存为「U1否认…」）——everos 对负例的策略是忠实提取、中性框架，而非 mem0 式整条跳过；两者皆为可辩护行为。评审口径：hits 为主依据、候选自产 md 为补充证据，不得把 0 hits 直接解读为「推测未存储」；该盲区系统性偏向 everos 的负例结果，如实披露、不改 harness 判分逻辑（轮询触发条件若改为对所有 search 生效将拖长全部 run，且 mem0 同步写入不受此影响，对比时以本披露校正）。写入空间不在检索 principal 可读集合的隔离类负例（D02/U05/P04）不受时序影响，0 hits 为真实隔离。

上述只是 benchmark 的静态身份绑定与过滤验证，不宣称两个 OSS 已提供生产认证。

## 判分与证据

合成私有码、必需 token、禁止 token 和原生 source ref 自动检查；原子语义命题仍标记 `REVIEW_REQUIRED`，需人工阅读候选实际 hit 后确认。EverOS 只返回 session 级来源时不能用 harness 已知 message ID 补成“原生来源通过”。每次运行写入独立 `artifacts/<run_id>`；缺密钥、网络或模型时写 `BLOCKED`，不生成假响应。

自动检查硬失败时按 `poll_intervals_seconds` 重发同一 search，直到通过、`max_poll_attempts` 或 `visibility_deadline_seconds` 耗尽为止；`FAIL` 只在可见性窗口耗尽后记录。原因：EverOS flush 返回 `extracted` 后，OME 策略管道（atomic facts 提取、索引）仍异步完成，立即搜索可能为空。轮询对两候选是同一条代码路径，负向用例首查即通过不消耗窗口；传输层 FAIL/TIMEOUT 不轮询。每次尝试写入 `search_attempt` 事件供审计。
