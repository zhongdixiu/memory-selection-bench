# Mem0 与 EverOS 对比验证执行方案

> 面向 Coding Agent 的实施任务书｜V1.0｜2026-09-14  
> 计划周期：5 个工作日；主要由一名研发结合 Coding Agent 推进。  
> 本文件是待执行方案，不包含已经完成的测试结果。所有项目能力、接口和许可证均须针对实际锁定版本重新核实。

## 1. 任务目标与完成边界

实现一套可复现的 Python 对比验证工程，对 Mem0 和 EverOS 使用同一套合成业务数据执行测试，给出有原始证据支撑的选型结论与后续工作量估算。

必须回答：

1. 哪些需求原生满足、配置可满足、外围可补齐、必须修改核心或尚未验证？
2. 哪个候选更适合当前统一记忆服务 MVP，为什么？
3. 针对项目记忆、来源、受控更新和案例保存，真实改造路径与代价是什么？
4. 接入真实 Agent 后，是否能够正确采集和使用记忆？

本周不建设完整统一记忆平台，不开发 Streamlit 看板，不实现跨域自动画像晋升、自动案例聚类成技能、深层用户行为推断或任务运行状态管理。不提前承诺必须选择其中一个候选。

允许安装测试依赖、创建隔离测试目录、运行本地服务及在现有授权范围内调用已配置模型。不得发送真实邮件、修改真实业务数据或清理非本实验数据。真实 Agent 联调使用合成内容和草稿生成场景。

## 2. 业务前提

### 2.1 需要保存的内容

- 用户明确表达的身份、偏好、长期要求。
- 用户负责的项目、项目进展、已确定的工作决策。
- 执行案例及人工总结的经验，保留适用条件和结果。
- 同一用户在不同 Agent 间按规则复用记忆；项目记忆可在授权范围内跨业务延续。

Email Agent 是基于 AgentScope 的轻量 Demo；OpenClaw 是公司的业务 Agent 技术方向。本周优先接入现有 Email Agent，再验证一个独立 OpenClaw 测试实例。不要假定已取得它们的仓库、端口或凭证。

### 2.2 作用域不是简单层级

测试逻辑模型分开描述：

| 维度 | 含义 |
| --- | --- |
| tenant_id | 租户边界；本周使用固定测试租户，不能宣称已完成跨租户认证 |
| owner_user_id | 记忆所属用户；所有用户专属案例仍必须绑定该用户 |
| source_agent_id | 哪个 Agent 产生输入，与谁可以访问是不同概念 |
| source_domain_id | 来源业务，不自动等于永久可见范围 |
| scope_kind | user_public / domain / project / agent_private |
| scope_id | 对应用户、业务、项目或 Agent 的范围标识 |
| project_id | 项目关联，可为空 |
| source_session_id | 来源会话标识，仅用于追踪，不替代项目 |

该表是测试协议，不要求直接给候选数据库新增这些列。适配器须记录到候选原生标识的映射及损失。

建议的授权测试规则：服务根据预配置测试身份确定 user、允许的 domain、project 和 agent；请求方不能通过修改参数自行增加权限。模型不得决定授权范围。没有权限匹配时返回空或拒绝，不得退化为无过滤全库检索。

同一用户通过邮件 Agent 可以读取其 user_public、邮件 domain、获准访问的当前 project，以及明确允许的 agent_private；不能读取其他用户、其他私有业务或无关项目内容。基线若不具备认证，只能评价过滤能力；身份绑定由增强层验证，不能混称原生权限能力。

## 3. 先核实版本，不沿用未经验证的结论

官方入口：

- Mem0：https://github.com/mem0ai/mem0
- EverOS：https://github.com/EverMind-AI/EverOS
- EverOS 机制参考：https://github.com/EverMind-AI/EverOS/blob/main/docs/how-memory-works.md

执行时读取锁定版本 README、安装配置、公开接口及必要源码。优先稳定 release；若使用 main，锁定完整 commit。禁止凭记忆编造 SDK 方法或 HTTP 路由。不要把商业托管版能力视为开源版能力。

生成 `reports/version_manifest.json`，记录每个候选的仓库、tag、commit、安装包版本、许可证文件路径与摘要、Python 版本、操作系统、依赖锁文件、模型配置摘要、存储后端及启用功能。留存许可证原文副本，但不自行下商业合规结论。

模型尽量一致：LLM、Embedding、参数、检索 top_k。无法统一时写明原因及影响；必要时只比较功能可实现性，不比较效果高低。使用各自推荐的最小可运行存储，不为了表面一致强行替换存储后端；比较对象是实际记录的完整配置。

## 4. 工程结构与实施原则

建议新建 `memory-selection-bench/`，目录职责如下：

| 路径 | 职责 |
| --- | --- |
| README.md | 从安装到重跑的实际命令，明确哪些已经执行 |
| pyproject.toml、依赖锁文件 | 控制器依赖与版本锁定 |
| .env.example | 仅变量名及占位值，不包含密钥 |
| configs/bench.yaml | 运行预算、top_k、超时、时区与数据根目录 |
| configs/providers/ | 各候选配置及能力映射 |
| data/cases.yaml | 第 7 节 40 个用例的可执行展开 |
| data/principals.yaml | 测试身份和授权关系 |
| src/memory_bench/contracts.py | 统一输入输出模型 |
| src/memory_bench/adapters/ | 原生 Mem0、EverOS 适配器 |
| src/memory_bench/enhancements/ | 增强探针，不能污染原生适配器 |
| src/memory_bench/runner.py | 顺序操作、等待、预算、结果收集 |
| src/memory_bench/evaluation/ | 硬断言、语义评审与汇总 |
| src/memory_bench/integrations/ | Email Agent、OpenClaw 接入探针 |
| tests/ | 协议与关键隔离逻辑的离线测试 |
| artifacts/<run_id>/ | 原始请求响应、时序、配置快照和逐用例证据 |
| reports/ | 汇总、差距、工作量和选型结论 |

工程使用 Python。控制器选择本机可用版本，候选若依赖冲突，允许分别使用虚拟环境或服务进程，以 HTTP 或 JSONL 子进程协议通信，不强迫放进同一 Python 环境。一个候选的服务、数据和生命周期独立管理。

不引入 Celery、Kubernetes 或外部任务队列。顺序跑效果用例；只有专门并发测试开启并发。候选原生后台任务可保留，但必须记录。

## 5. 严格分离三种测试轨道

| 轨道 | 允许 | 禁止 |
| --- | --- | --- |
| native | 参数转换、调用公开接口、记录原始结果；使用文档化原生配置 | 新增抽取模型、自己判断冲突、外部授权补齐、用外部状态伪装原生能力 |
| configured | 使用原生公开配置、提示词扩展等；记录所有改动 | 修改核心源码或将配置结果混入默认基线 |
| enhanced | 外围策略、业务记录表、索引校验等最小探针 | 将增强后的通过率声称为原生能力 |

必跑 native 和必要 enhanced；configured 仅对明确可配置的失败项运行一次受控调整。每条结果必须携带 track、配置 hash、代码 commit、模型和 run_id。

第一轮不修改候选核心源码。发现核心改造需求时，记录文件、函数、调用链、原因及估算；不在本周未经记录地扩成完整重构。用于观察的只读源码检查不算业务能力。

### 5.1 能力分类与执行状态分开

能力分类：A 原生满足；B 配置满足；C 外围可补齐；D 需核心改造；E 未验证。

执行状态：PASS、FAIL、UNSUPPORTED、BLOCKED、TIMEOUT、NOT_RUN、REVIEW_REQUIRED。

- A/B/C 必须附成功执行证据；只读代码推测不能算完成验证。
- D 可以是明确源码证据支持的判断，但注明尚未实现。
- UNSUPPORTED 表示锁定配置或接口不提供该能力，不返回伪成功。
- BLOCKED 用于缺密钥、网络、模型或真实 Agent 环境；与功能失败分开。
- 语义结果未人工核定时使用 REVIEW_REQUIRED，不自动算通过。

## 6. 统一协议与运行参数

### 6.1 适配接口

以下是本工程应实现的接口，不是宣称两个候选存在同名 API。

```python
class MemoryAdapter(Protocol):
    async def health(self) -> HealthResult: ...
    async def capabilities(self) -> CapabilityReport: ...
    async def write(self, request: WriteRequest) -> WriteReceipt: ...
    async def search(self, request: SearchRequest) -> SearchResult: ...
    async def inspect(self, request: InspectRequest) -> InspectResult: ...
    async def reset_test_namespace(self, namespace: str) -> ResetResult: ...
```

`inspect` 是可选只读能力，用于查看原生条目、历史及元数据；不存在时返回 UNSUPPORTED，不能借测试输入重建“原生记忆”。服务重启交给各候选 launcher，不伪造通用 SDK restart。

WriteRequest 必须包含：request_id、namespace、principal_id、source_id、来源消息列表、来源时间、来源时区、来源 Agent/业务、可选 project_id、write_mode、requested_scope。消息必须含 message_id、role、content、occurred_at。助手消息保留角色，不能改成用户原话。

write_mode 分为 conversation 和 direct_record；后者用于结构化人工经验或明确规则。框架不支持直接写入时如实返回，不偷偷转成对话推断路径。

WriteReceipt 至少记录：原始返回、原生 record/job IDs（如有）、accepted/processed 的观测状态、接收时间、响应时间、异常。accepted 不等于形成完成，也不等于可检索。

SearchRequest 包含：principal_id、查询、业务及项目上下文、top_k、查询用途 current/history。增强模式由服务端身份映射约束范围；原生模式记录实际传入的原生过滤条件及缺失项。

SearchHit 统一为：native_id、text、score、native_metadata、source_refs、observed_at。未提供的来源、时间、类型置 null，不用输入答案填补。测试运行器掌握的来源称为 harness_source，不能计入 native_source 能力。

### 6.2 建议默认值

```yaml
timezone: Asia/Shanghai
top_k: 5
request_timeout_seconds: 120
visibility_deadline_seconds: 120
poll_intervals_seconds: [0, 1, 2, 4, 8, 15]
poll_interval_after_schedule_seconds: 15
max_poll_attempts: 12
max_transport_retries: 1
baseline_repetitions: 1
critical_repetitions_total: 3
max_llm_calls: 500
max_embedding_calls: 1000
max_run_wall_seconds: 14400
effect_concurrency: 1
reliability_concurrency: 3
```

这些是实验预算，不是生产 SLA。轮询同时受总时限、次数与调用预算限制；候选 search 若会调用 LLM，也必须计入。达到预算时保存 checkpoint 并停止后续模型请求，已执行结果保留。无法观测内部调用量时标记 unknown，记录已知调用下限，仍强制墙钟与请求数上限，不能声称成本完整。

不得为达到通过率无限重试。写入请求超时后若无法确认是否已提交，不盲目重试；先探查已有数据，重试行为完整记录。故意重复提交仅在重复测试中执行。

先做健康检查、单条 smoke，再跑全量。模型密钥通过环境变量提供，不写入配置快照、日志或报告。模型价格不明时仅报告调用和 token，不自行编造金额。

### 6.3 数据隔离与清理

每个 case、candidate、track、repetition 使用新的物理测试空间或原生隔离空间；逻辑业务 ID 保持一致。用例内部不同用户及业务必须处于同一待验证存储环境，不能通过给每个用户单独启动服务来“证明”原生隔离。

reset 只能清理带本次实验标记且位于配置 data_root 内的 namespace。校验 realpath，禁止清理 home、仓库根目录或任意调用方传入路径。无安全原生清理方式时新建测试数据目录，不清理共享存储。

## 7. 40 个基础用例：按表展开为可执行数据

所有人名、用户、项目、联系方式使用合成内容。每行展开为独立 case；必须包含完整输入操作、检索查询、允许命题、禁止命题、是否检查来源和作用域。所有形成记忆的用例均检查来源，不仅来源专题测试。

| ID | 写入或操作序列 | 查询与关键预期 |
| --- | --- | --- |
| F01 | U1：我负责统一记忆项目 P1 | 问负责项目，返回 P1；不推断职位级别 |
| F02 | U1：技术方案默认用 Python | 问技术语言，返回 Python |
| F03 | U1：邮件回复尽量简洁 | 在邮件域询问风格，返回简洁 |
| F04 | U1：对外发送前必须先让我确认 | 查询长期要求，保留确认约束 |
| F05 | 同段：我负责 P1；邮件简洁；报告必须保留指标 | 三个查询分别正确，证据逐条对应，类型不混 |
| N01 | U1：假如以后改用 Java，会有什么影响 | 问当前语言，不得认定已改 Java |
| N02 | U1：同事小林喜欢短邮件 | 问 U1 偏好，不得归为 U1 喜欢短邮件 |
| N03 | assistant：你可能负责预算；user：我没有这样说 | 不得形成 U1 负责预算的事实 |
| N04 | U1：客户原话是“我常住上海” | 不得形成 U1 常住上海 |
| N05 | U1：这一次回答短一点 | 不得形成适用于所有未来任务的长期简洁要求 |
| U01 | U1 喜简洁，U2 喜详细 | U2 查询只返回自己的偏好 |
| U02 | U1 写 P1 决策，U2 使用同名 P1 | U2 不得读取 U1 决策 |
| U03 | U1 与 U2 使用相同 session_id，分别写不同职责 | 查询各自职责无混用 |
| U04 | U1、U2 都写居住北京；U2 改上海 | U1 仍北京，U2 上海，更新不能跨用户 |
| U05 | 在已有 U1 记录时，不提供有效 principal；另试用 U2 身份声明 U1 | 必须拒绝或无结果，不能绕过身份；原生仅有过滤时标明认证缺口 |
| D01 | 邮件简洁；报告详细 | 各域分别返回对应要求 |
| D02 | 邮件域保存“审核代号 MAIL-ONLY-731” | 报告域普通查询不得返回该私有代号 |
| D03 | U1 公共职责为 P1 负责人 | 邮件及报告域均可取到授权公共职责 |
| D04 | 邮件规则简洁；报告规则详细；把邮件改为需要细节 | 报告规则保留，更新不跨域 |
| D05 | U1 的 Agent A 私有案例；Agent B 未授权 | B 不得读到；同 U1 不等于共享全部 Agent 内容 |
| P01 | 邮件域在项目 P1 确定先接 Email Agent | 获授权报告 Agent 查询 P1 可返回该决策 |
| P02 | P1 先接邮件，P2 先接日程 | 查询 P1 不混入 P2 顺序 |
| P03 | P1 在邮件会话 S1 确定范围，报告会话 S2 查询 | 会话变化不丢失 P1 决策 |
| P04 | P1 授权给邮件与报告，不授权给测试 Agent C | C 不能因知道 project_id 而访问 |
| P05 | P1 项目决策已形成，关联单次任务 T1 结束 | P1 决策仍可读；不随任务结束清除 |
| C01 | 喜欢人像；现在也喜欢风景 | 两项并存 |
| C02 | 现居北京；已搬到上海 | 当前上海；历史北京能否追踪另列断言 |
| C03 | 技术报告详细；短消息简洁 | 按适用条件并存，不全局替代 |
| C04 | 同属性先说偏好 A，后说“更正，应该是 B” | B 生效，A 来源及替代关系可追踪 |
| C05 | 连续写项目进度：设计中、开发中、联调中 | 当前联调中；历史链条不伪造或混成同时状态 |
| T01 | 较新来源说已搬上海，随后补录较早来源说住北京 | 当前仍上海，不按入库先后覆盖 |
| T02 | 来源时间为 2026-09-14 09:00+08:00：“今天下午休假” | 2026-09-14 13:00 至 18:00 为本用例显式定义窗口；不能长期常驻；无法原生时间控制则标明 |
| T03 | 明确从 T+1h 至 T+2h 执行临时规则 | 开始前不生效、期间生效、结束后失效 |
| T04 | 写长期 Python 要求，无 valid_until | 当前查询仍保留，不被空截止时间过滤 |
| T05 | “P1 计划在 10 月底交付”，没有完成事件 | 截止后不得推断已完成，保留计划性质或待确认状态 |
| E01 | 人工导入案例：限流时先读 Retry-After，再重试；无该字段转人工 | 检索时保留条件、动作和兜底 |
| E02 | 导入失败案例：盲目重试导致重复提交 | 不得作为已验证成功经验推荐 |
| E03 | 手工 SOP：写草稿、校验收件人、用户确认；适用邮件发送前 | 保留步骤顺序及适用范围，不实际发送 |
| E04 | U1 专属案例含合成私有代号 CASE-U1-924 | U2 及未授权 Agent 不可读；不可自动成为全局技能 |
| E05 | SOP v1 先生成后检查；v2 明确更正为先校验输入再生成 | 当前采用 v2；保留 v1 来源，不能混成错误步骤 |

### 7.1 时间测试实施方法

统一记录 source_occurred_at、ingested_at、valid_from、valid_until、observed_at，全部使用带时区时间，保存时可转换 UTC。不能把入库时间冒充来源时间。

native 若无可控时钟，不擅自传入根本不支持的 as_of：使用相对真实时间构造过去/未来窗口，或在独立实例中使用公开支持的时钟测试方法。T03 可缩短为可配置的分钟级窗口，但须考虑原生时间精度；不支持秒级就记录粒度限制，不长时间阻塞等待。enhanced 可注入 clock 重现固定时点。模拟时钟结论与真实原生过期机制分开报告。

T02 的下午窗口是本测试给定的业务规则，不声称自然语言“下午”只有一个标准时间。N05 允许保留交互历史，但不得晋升为长期通用偏好；不要把“历史有记录”误判为错误长期记忆。

### 7.2 可执行用例示例

```yaml
id: C01
group: conflict
scope_fixture: user_public_u1
operations:
  - op: write
    request_id: c01-w1
    source_id: c01-s1
    principal_id: principal_u1_mail
    messages:
      - message_id: c01-m1
        role: user
        content: 我喜欢拍人像。
        occurred_at: '2026-09-14T09:00:00+08:00'
  - op: await_observable
    receipt_ref: c01-w1
  - op: write
    request_id: c01-w2
    source_id: c01-s2
    principal_id: principal_u1_mail
    messages:
      - message_id: c01-m2
        role: user
        content: 我现在也喜欢拍风景了。
        occurred_at: '2026-09-14T10:00:00+08:00'
  - op: await_observable
    receipt_ref: c01-w2
  - op: search
    principal_id: principal_u1_mail
    query: 我喜欢拍什么题材？
    top_k: 5
assertions:
  required_propositions:
    - 用户喜欢拍人像
    - 用户喜欢拍风景
  forbidden_propositions:
    - 用户不再喜欢拍人像
  source_message_ids: [c01-m1, c01-m2]
  source_check: per_claim
```

`await_observable` 优先使用原生任务完成状态；否则有界观测。不能使用 required_propositions 作为无限轮询至通过的停止条件。无可靠完成信号时按预定期限采样并记录未知状态。对于不应形成记忆的 N 组，不把“未出现记忆”当成待处理未完成而一直等待。

## 8. 评估方式与指标

硬断言自动化：身份与范围、私有代号泄漏、来源 ID、时间比较、记录数量、任务状态、重复记录。对于无结构化 ID 的输出，代号只是补充证据，不能仅凭无代号认定没有语义泄漏。

语义断言：需要命题是否存在、禁止命题是否出现、案例条件与步骤是否保留。按原子命题评审，不做整段字符串相等。允许可选 LLM judge 输出“支持/矛盾/未知”与结果中的证据片段，但只能读取候选实际结果；无可核验证据时 REVIEW_REQUIRED。人工重点复核安全边界、冲突、所有 judge 判失败及候选分歧；未复核项不得填成已人工确认。

至少输出：

| 指标 | 计算要求 |
| --- | --- |
| 执行覆盖率 | 有实际执行结果的 case / 40；区分 BLOCKED、NOT_RUN |
| 需求覆盖率 | 全部必需断言确认通过的 case / 40；UNSUPPORTED 不从分母移除 |
| 已执行通过率 | PASS / (PASS + FAIL)，同时列出分母和其他状态，不能单独展示 |
| 必需命题召回率 | 返回结果支持的必需原子命题数 / 应返回命题数；先排除无正命题用例 |
| 错误长期沉淀 | N 组形成被禁止长期命题的 case 数 / 已评审 N 组数 |
| 越界 | 检索泄漏与跨域更新分别统计次数、涉及 case 和证据 |
| 来源完整性 | 有候选原生来源定位的实际命题数 / 检查命题数 |
| 来源正确性 | 经原文验证正确的来源关联数 / 已验证关联数；完整性不能替代正确性 |
| 更新正确性 | 同时满足当前状态及不误覆盖的断言比例；历史能力单列 |
| 经验保真 | 条件、步骤、结果、失败性质四项分别统计 |
| 可见性与耗时 | 接收、形成完成（如可观测）、首次可检索分开统计；超时单列 |
| 成本 | 已知请求、LLM/Embedding 调用、Token；缺失填 unknown |

样本较少，耗时优先报告中位数、范围和样本数；不宣称统计显著或生产性能。复测用于观察波动，不挑选最好一次。

## 9. 周三的四个增强探针

每个候选每项探针优先控制在 60～90 分钟；已有证据足以证明核心改造必要时停止扩展。记录实际投入，不把 Coding Agent 生成代码耗时等同全部研发成本。

| 探针 | 最小实现 | 验收 |
| --- | --- | --- |
| X01 逐条证据与类型 | F05 对应的多条记忆分别记录来源、业务及类型 | 不使用整次调用统一证据冒充逐条关联 |
| X02 项目共享与隔离 | 静态 principal 配置+项目授权，测试 P01/P02/P04/U05 | 合法项目可读，伪造 user/project 不扩大范围 |
| X03 受控版本 | C02/C04/T01 的当前版本与历史链条 | 旧版本可追踪，历史补录不覆盖新事实 |
| X04 案例保真导入 | E01/E02/E03 直接导入及搜索 | 保留适用条件、步骤和失败性质 |

如果使用业务 SQLite 作为权威记录：明确该表属于增强层；记录 memory_id、native_id、source_id、版本、状态、scope。权威记录与向量索引不是跨库原子事务。至少提供 pending/indexed/failed 状态、可重试索引任务和读取状态复核的最小方案；本周未实现的部分注明。不要为了探针实现完整平台。

来源原文放置在只追加的合成测试来源文件中，引用到消息与片段；校验引用真实存在。不要称普通元数据或哈希为“不可篡改证据”。框架原生缺来源能力时，可以证明外部保存可行，但原生评分不变。

## 10. 真实 Agent 接入与业务对照

### 10.1 接入前发现

读取实际项目说明与 AGENTS.md，定位现有 Agent 入口、消息结构、工具注册和上下文注入点。只在隔离分支或测试配置中接入。模型和 memory URL 从环境读取。

缺少仓库、凭证或运行实例时，完成独立连接器和 dry-run，再在 blockers.md 给出准确缺项；dry-run 不算真实接入成功，不为等待单项环境阻塞全部实验。

### 10.2 接入职责

- Agent 采集：用户输入、会话、用户及业务标识，保留 role；在合适回合结束或任务结束时写入。
- 原生 flush、后台形成等机制依据锁定版本实现，不自创同名 API。
- Agent 检索：给出任务上下文，服务按范围召回。
- Agent 使用：决定是否需要检索、候选是否必要，并组织上下文；固定公共背景只包含经过确认的稳定信息。
- 下游普通记忆作为带来源的数据传入，不能把历史邮件文字提升为系统指令。

OpenClaw 使用锁定版本公开支持的接入方式；记录插件/工具/钩子或其他实际机制，以及采集和使用分别是否完成。不要求本周实现完整自动插件。

### 10.3 三组真实任务，每组比较三种模式

| 任务 | 预置内容 | 预期 |
| --- | --- | --- |
| A 项目进展邮件草稿 | P1 先接 Email Agent，暂不自动生成技能；P2 有其他安排 | 使用 P1 决策，无 P2 混入，不声称暂缓项已完成 |
| B 技术报告段落 | 公共职责+邮件简洁偏好+报告保留指标要求 | 报告保留指标，不机械套用邮件简洁偏好 |
| C 故障处理建议 | E01 正向案例+E02 失败案例 | 按条件使用经验，不推荐盲目重试 |

M0：无长期记忆；M1：受同样授权与时间过滤约束的 top-k 结果直接提供；M2：任务感知触发与必要性判定后提供。M1 与 M2 采用同一初始记忆快照、模型及采样配置，M0/M1/M2 用独立会话；评估回答不写回记忆，防止后运行模式被污染。

记录最终回答、实际使用/未使用的记忆 ID、任务决策理由（简短可观察说明即可，不要求模型内部推理）、来源、耗时与调用数。仅 3 组案例用于定性验证，不能宣称已经证明普遍业务收益。

## 11. 最小可靠性测试

三个测试按两个候选分别执行，失败后保留数据与日志。

1. R01 重启：写入并观察状态，正常停止进程，再启动并检索；分别说明 accepted 数据和 processed 数据的恢复情况。此项不是 crash-consistency 证明。
2. R02 重复：同 request_id/source_id 提交两次，再用新 request_id 重放同 source_id。检查原生幂等、语义去重和增强去重，三者不要混淆。
3. R03 并发：并发 3，请求共 6 条；先测试同用户同域不同事实，再测试不同用户；核对全部结果、丢失、混用和异常。并发写同一属性的结果不要求按网络发起先后生效，按明确来源顺序验证策略，无法定义顺序则记录冲突待决。

效果用例仍串行，不因可靠性测试改变基线。任何越界结果必须进入最高优先级问题表；小样本零越界只表示本测试未发现问题。

## 12. 五日执行计划及停止条件

| 日程 | 编码及执行任务 | 当天产物与门槛 |
| --- | --- | --- |
| D1 | 版本发现、两个环境、协议和 40 个用例、离线校验、smoke | 版本清单、可运行安装命令；至少各尝试一次真实 smoke |
| D2 | 原生适配器、native 全量、原始结果、初步评审 | 两套基线；失败与未验证项不能空白 |
| D3 | 四项增强探针；必要 configured 对照 | 原生/配置/增强分开报告；改动位置和工时 |
| D4 | 领先候选接 Email Agent；OpenClaw 探针；两候选可靠性 | 实际调用证据、3 组任务对照、阻塞项 |
| D5 | 完整回归；关键项共 3 次；差距估算与决策 | 可复现仓库、报告、原始证据、剩余工作量 |

关键复测集合：U01～U05、D02/D04/D05、P01/P02/P04、C01/C02、T01、E04；总次数 3 包含第一次，不是额外 3 次。其他失败项只在相关配置或代码修正后重测一次。预算不足则按隔离、更新、项目、经验排序保留覆盖，并说明未复测数量。

单个候选安装排查超过半天：记录命令、错误和尝试路径，先推进另一个。单个增强探针超过时间盒：记录风险，不扩成重构。原生轨道证据必须先保存后再增强。

若当天额度不足、网络受限或密钥缺失：继续完成 schema、40 个测试数据、离线 runner 测试、报告生成和准确阻塞清单；实际效果保留 BLOCKED。不得生成假响应充当真实实测。mock 只用于测试测试框架本身。

## 13. CLI 交付约定

Coding Agent 应实现以下工程命令；命令属于待开发控制器，不是第三方现成命令。可调整可执行入口名称，但 README 必须给出实际可复制命令，参数语义保留。

```bash
python -m memory_bench doctor --config configs/bench.yaml
python -m memory_bench validate-cases --cases data/cases.yaml
python -m memory_bench smoke --candidate mem0 --track native
python -m memory_bench smoke --candidate everos --track native
python -m memory_bench run --candidate mem0 --track native --suite core
python -m memory_bench run --candidate everos --track native --suite core
python -m memory_bench probe --candidate mem0 --suite extensions
python -m memory_bench probe --candidate everos --suite extensions
python -m memory_bench run --candidate mem0 --track native --suite reliability
python -m memory_bench run --candidate everos --track native --suite reliability
python -m memory_bench integrate --candidate SELECTED --agent email --suite tasks
python -m memory_bench integrate --candidate SELECTED --agent openclaw --suite smoke
python -m memory_bench report --runs artifacts --output reports
```

SELECTED 替换为实际候选。run 必须支持 --case、--resume 和输出 run_id；resume 只跳过已有完整证据的操作，不能在不确定写入状态时重复追加。无法可靠恢复某个 case 时，在新 namespace 重跑并关联前次尝试。

doctor 输出模型端点可达性与脱敏配置，不打印 secret。validate-cases 校验 ID 唯一、40 个 case、每组 5 个、时间带时区、必需字段、身份引用有效。协议和报告测试可使用 mock；真实候选适配器必须有明确的 live 标记。

## 14. 报告与选型规则

最终至少生成：

| 文件 | 必需内容 |
| --- | --- |
| reports/version_manifest.json | 锁定版本、配置、模型、存储与环境 |
| reports/case_results.csv | case、candidate、track、run、状态、断言结果、证据路径 |
| reports/capability_matrix.md | A～E 能力表，原生与增强分列 |
| reports/gaps_and_effort.md | 差距、源码位置、扩展方式、实际探针工时、剩余三档人日 |
| reports/integration_report.md | Email/OpenClaw 真实与 dry-run 分开；任务输出 |
| reports/blockers.md | 缺环境、待评审、未验证、预算停止情况 |
| reports/selection_decision.md | 推荐或暂缓结论、证据、限制、下周计划 |
| artifacts/<run_id>/manifest.json | 数据 hash、配置 hash、版本、执行时间及状态 |
| artifacts/<run_id>/events.jsonl | 操作、脱敏请求、原始返回引用、时序和错误 |

使用同一组需求比较，不能用综合分掩盖用户泄漏或误更新。判断顺序：

1. 用户与范围边界是否有经验证的可行路径；未解决越界者不能作为当前可接入方案推荐。
2. 项目延续、案例保真、来源、受控更新能否在合理范围实现。
3. 同条件下质量、时延和可靠性表现。
4. 外围增强的规模、核心修改深度、接入和后续维护成本。

如果 Mem0 大部分高层逻辑都要绕开重写，明确剩余复用能力是否值得保留；如果 EverOS 的来源/项目/服务机制需要大量改造，也如实列出。不要按项目宣传或先前报告预设赢家。

工作量按模块估算：身份与作用域、来源、项目、版本时间、案例、Agent 适配、恢复与回归。每项给乐观/通常/悲观人日、依据及置信程度。AI 编码时间之外包含调试、联调和人工评审。不承诺“两周完成全部平台”。

结论允许三种：选 Mem0、选 EverOS、证据不足或两个候选均需调整复用边界。缺真实 OpenClaw 接入时，只能给带明确未验证条件的选择。

## 15. 最终验收清单

- [ ] 两候选版本和配置固定，未把云端商业能力混入 OSS。
- [ ] 40 个用例已实现且通过数据 schema 校验。
- [ ] 每候选每用例都有真实结果或明确的非执行状态。
- [ ] native/configured/enhanced 数据、目录和报告可区分。
- [ ] 没有通过用户物理分库隐藏待验证的隔离问题。
- [ ] 原始证据足以重现失败；来源没有由 harness 伪造补齐。
- [ ] 超时、异步可见性、预算与重试有记录。
- [ ] 四个改造探针均有结果、源码证据或明确阻塞。
- [ ] 实际接入、模拟接入、未接入明确区分。
- [ ] 完成三项可靠性测试或记录准确阻塞。
- [ ] 未人工评审的语义结论未伪称确认通过。
- [ ] 推荐附实际差距及工作量，不只给分数。
- [ ] 无真实邮件发送、业务数据修改或密钥泄漏。
- [ ] README 包含已经验证的复现命令与最终状态。

## 16. 给 Coding Agent 的启动指令

请依据本方案直接实施，先读取当前工作区 AGENTS.md 和已有项目结构，再建立独立对比工程。先固定版本、实现协议与用例、跑 smoke，再执行原生基线；不要跳过基线直接开发增强平台。普通工程选择自行处理，缺少必要凭证或实际 Agent 地址时列出准确缺项，同时完成不依赖该环境的工作。每完成一阶段更新进度、产物位置和剩余风险。不要在完成骨架后声称选型已完成，不要编造任何执行结果。最终交付可运行工程、原始证据、对比报告以及推荐或暂缓的明确结论。
