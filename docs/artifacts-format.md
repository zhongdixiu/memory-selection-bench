# 运行产物格式说明（artifacts 字段字典）

每次运行写入独立目录 `artifacts/<run_id>/`，run_id 格式为
`<UTC时间戳>-<候选>-<轨道>-<套件>-<随机8位>`，例如
`20260914T093718Z-everos-r0-smoke-bc0e7fd1`。本文解释目录内各文件的字段含义，
供人工评审与归因时对照。所有含 `api_key` 等敏感名的字段在落盘前已被
`ArtifactWriter.redact` 替换为 `<redacted>`。

## 1. 目录内文件一览

| 文件 | 内容 |
|---|---|
| `manifest.json` | 运行元数据：身份、配置哈希、最终状态、错误 |
| `events.jsonl` | 逐事件审计流水（含轮询的每次尝试） |
| `case_results.json` | 每案例完整记录：全部操作的请求/结果/判分（**人工评审主要读这个**） |
| `case_results.csv` | 上表的扁平摘要（case_id/status/hard_failures/review_items） |
| `candidate.log` | 候选进程日志尾部（Mem0 为 worker stderr，EverOS 为 server stdout，各保留最近 500/1000 行） |
| `integration_results.json` | 仅 `integrate` 运行：Email Agent M0/M1/M2 结果（见 §7） |

## 2. manifest.json

| 字段 | 含义 |
|---|---|
| `run_id` / `candidate` / `track` / `suite` | 运行身份：候选（mem0/everos）、轨道（r0/r1/p-native）、套件（smoke/decision/probe/full/email-integration） |
| `started_at` / `finished_at` | UTC 起止时间 |
| `case_ids` | 本运行覆盖的用例 |
| `case_data_hash` / `principal_data_hash` / `config_hash` | 输入数据与配置的 SHA-256，用于证明两候选跑的是同一套输入 |
| `candidate_descriptor` | `configs/providers/<候选>.yaml` 原样存档 |
| `config` | 脱敏后的 bench 配置快照 |
| `health` | 适配器启动后的候选健康检查响应 |
| `status` | 运行级状态：任何案例 FAIL → `FAIL`；任何 TIMEOUT → `TIMEOUT`；启动前异常（缺密钥、进程拉不起）→ `BLOCKED`；否则 `PASS`。**注意**：案例级 `REVIEW_REQUIRED` 会被折叠为运行级 `PASS`，评审义务看 case_results |
| `error` / `close_error` | BLOCKED 原因 / 关闭适配器时的异常 |

状态词表（`contracts.Status`）：`PASS`、`FAIL`、`UNSUPPORTED`（候选无对应契约，如
EverOS 的 direct_record）、`BLOCKED`（环境问题，非候选缺陷）、`TIMEOUT`、
`NOT_RUN`、`REVIEW_REQUIRED`（自动检查全过，语义命题待人工）。

## 3. case_results.json 总体结构

```
[                                  ← 案例列表
  {
    "case_id", "group", "title",
    "status",                      ← 案例状态（聚合规则见下）
    "operations": [                ← 按用例定义顺序执行的操作
      { "op": "write",  "request": WriteRequest,  "result": WriteReceipt },
      { "op": "search", "attempts": N, "request": SearchRequest,
        "result": SearchResult, "evaluation": Evaluation },
      { "op": "await_observable", "receipt_ref", "status" }
    ]
  }
]
```

**一个案例包含多个操作，每个操作各有一份 `result`，write 与 search 的 result
结构不同**（分别是回执与检索结果），不要误读为"同一次检索的两个结果"。

案例状态聚合优先级（`runner._case_status`）：
操作级 `BLOCKED > TIMEOUT > FAIL > UNSUPPORTED`，其次判分 `FAIL`，再次
`REVIEW_REQUIRED`，全过才是 `PASS`。

## 4. search 操作公共字段（两候选一致）

### 4.1 request

| 字段 | 含义 |
|---|---|
| `request_id` / `namespace` | 请求 ID；隔离命名空间（每 run+case 独立） |
| `principal_id` | 发起检索的身份，决定可读作用域 |
| `query` / `top_k` / `purpose` | 查询文本；R0 时 top_k=5（候选池即最终），R1 时 top_k=20（rerank 前候选池）；purpose 为业务用途标记 |

### 4.2 result（SearchResult）

| 字段 | 含义 |
|---|---|
| `status` | **接口层**状态。`PASS` 只表示检索调用成功；案例 FAIL 可能来自判分而非接口 |
| `hits` | 归一化后的统一命中列表（SearchHit），**判分只看这里** |
| `raw` | 候选原生响应存档，审计用；两候选形态不同（见 §5/§6），Mem0 为 `null` |
| `elapsed_ms` | 检索耗时（R1 含 rerank 调用） |
| `rerank_configured/requested/applied` | R0 全为 false；R1 成功时全为 true |
| `error` | 传输层错误信息 |

### 4.3 hits[i]（SearchHit，统一契约）

| 字段 | 含义 |
|---|---|
| `native_id` | 候选原生记忆 ID |
| `text` | 用于判分与人工阅读的文本（两候选构造方式不同，见 §5/§6） |
| `score` | 相关性分数：R0 为原生向量分；R1 为 rerank 分（原 dense 分移入 `native_metadata.dense_score`） |
| `native_metadata` | 原生/写入时元数据，原样保留 |
| `source_refs` | 来源引用列表，`source_check` 判分依据（**Mem0 为消息级，EverOS 为 session 级**） |
| `observed_at` | 控制器观察到该 hit 的 UTC 时刻 |

### 4.4 evaluation（自动判分）

| 字段 | 含义 |
|---|---|
| `status` | `FAIL`（有硬失败）/ `REVIEW_REQUIRED`（硬检查全过、存在语义命题）/ `PASS` |
| `hard_failures` | 机械检查失败项：缺失必需 token、出现禁止 token、来源引用不匹配。**已知局限**：token 判定为大小写不敏感子串匹配，无法识别否定/更正表述——存储记忆语义上否认命题时（如「用户明确否认负责预算」包含 forbidden 子串「负责预算」）仍机械 FAIL（实测 mem0 full R1 N03）；此类案例由人工评审按语义改判，harness 判分逻辑保持机械可复现不修改 |
| `matched_required_tokens` | 命中的必需 token |
| `review_items` | **待人工评审的语义命题**（`required:` 须确认成立，`forbidden:` 须确认不成立），人工须阅读 hits 文本后判定并另存评审记录 |

### 4.5 attempts 与可见性轮询

`attempts` 记录该 search 的总尝试次数。自动判分硬失败时按
`poll_intervals_seconds` 重试，直到通过 / `max_poll_attempts` /
`visibility_deadline_seconds` 耗尽（背景：EverOS flush 返回后索引仍异步收尾，
立即检索可能为空）。**case_results.json 只保留最后一次尝试**；每次尝试的
中间状态（attempt 序号、hit 数、硬失败）在 `events.jsonl` 的 `search_attempt`
事件里。轮询对两候选是同一条代码路径。

每个 attempt 内部另有**传输层重试**：search 接口返回 FAIL/TIMEOUT（如
embedding 端点偶发 400）时重试至多 `max_transport_retries` 次（间隔 1s，
写 `search_transport_retry` 事件），避免瞬态供应商错误覆盖真实判分状态；
重试预算耗尽仍失败才按接口层 FAIL 记录，且不再触发可见性轮询。

## 5. Mem0 特有形态

参考样例：`artifacts/20260914T093710Z-mem0-r0-smoke-09bb71b5/`。

### 5.1 write result（WriteReceipt）

| 字段 | Mem0 实际行为 |
|---|---|
| `processed=true` | `memory.add` 同步完成（含 LLM 事实抽取），返回即已加工 |
| `native_ids` | 抽取产生的记忆 UUID 列表，来自 `raw.results[].id` |
| `raw` | mem0 add 原生返回：`{"results": [{"id", "memory", "event"}]}`；`event` 为 `ADD`/`UPDATE`/`DELETE`（推理可能合并或改写既有记忆，评审冲突类用例时注意） |
| `results=[]` 且 status=PASS | 提取 LLM 正常返回但判定"无新记忆可加"。须区分四种情形：① 消息本身无可提取事实或被否认（如 N05，良性）；② 与该 user_id 下既有记忆语义等价而被去重跳过——**去重检索无视 metadata 过滤（含 bench_namespace），会跨案例串扰**（decision 实测 F05→D03、C02→T01；full 套件扩展至 D01←F03、D04←F03/D01、P02←P01（跨语言等价）、C02←U04、T01←C02）。情形②下本案例检索必然 0 hits（吞噬记忆被读路径 metadata 过滤正确挡住），归因写路径而非检索能力；③ 提取遗漏：无前序等价记忆仍未提取（实测 F04「对外发送前必须先让我确认。」，双轨稳定）；④ 边缘等价判定漂移：temp=0 下双轨提取结果翻转（实测 N01/N03/U01-w1），属写路径非确定性。详见 experiment-design 隔离映射的 full 扩展条目 |
| `elapsed_ms` | 含同步 LLM 抽取，秒级属正常 |

### 5.2 search result 与 hits

- `raw = null`：Mem0 侧不存原生响应。隔离与合并发生在 worker 内——
  principal 的每个可读过滤集（user_public、domain、每个获准 project、每个获准
  agent_private）各发起一次 `memory.search(rerank=False, threshold=0.0)`，
  按记忆 id 去重取最高分、排序、截断 top_k。**R0/R1 均强制 mem0 原生
  `rerank=False`**，R1 的 rerank 由控制器外置调用，保证两候选同栈。
- `text`：mem0 推理改写后的事实句。**2026-09-15 起 worker 经官方
  `custom_instructions` 配置口写入语言对齐 shim**（mem0 自带 `use_input_language`
  文案，见 configs/providers/mem0.yaml 的 shims 与 experiment-design 统一配置），
  提取保持输入语言，中文消息应产出中文事实句。shim 之前的运行
  （≤ `20260915T031509Z-mem0-r1-decision-f7884dbc`）为开箱行为：中文常被改写为
  英文（如 "User defaults to using Python for technical solutions and
  implementation plans"），这些运行保留为能力发现证据，勿删。人工评审无论
  语言均须确认改写忠实于原消息、未引入原话没有的信息。
- `native_metadata`：写入时注入的 benchmark metadata 全量返回
  （`bench_namespace`、`tenant_id`、`scope_kind/scope_id/project_id`、
  `source_agent_id/domain_id/session_id/id`、`source_message_ids`、
  `source_occurred_at`），可用来核对隔离与来源。
- `source_refs`：取自 `metadata.source_message_ids`，**消息级**来源。
  注意点：mem0 推理若把多条消息合并为一条记忆或 UPDATE 既有记忆，
  message ID 的继承行为需以实测为准（per_claim 用例是主要检验点）。

## 6. EverOS 特有形态

参考样例：`artifacts/20260914T093718Z-everos-r0-smoke-bc0e7fd1/`。

### 6.1 write result（WriteReceipt）

| 字段 | EverOS 实际行为 |
|---|---|
| `processed` | 两段式：`raw.add.data.status="accumulated"`（消息入会话缓冲）→ `raw.flush.data.status="extracted"`（OME 策略管道派发完成）。两者任一为 extracted 即 true |
| `native_ids` | 恒为空：add/flush 契约不返回记忆 ID |
| `raw` | `{"add": {...}, "flush": {...}}` 两次 HTTP 响应原样存档 |
| direct_record 写入 | 不发请求，直接返回 `UNSUPPORTED`（memory/add 无对应契约） |
| 可见性 | flush 返回 ≠ 可检索；提取与索引异步收尾，实测约 20~40s（full F03 曲线 [0,0,1,…] 第 3 次尝试命中）。**注意**：可见性轮询只在硬失败时触发，负例（无 required token）0 hits 不构成硬失败——检索在 flush 后约 1s 单次执行即定案，此时索引多半未收敛，0 hits 不能解读为「内容未存储」（见 §6.3） |

### 6.2 search result 与 hits

- `raw` 为**列表**：EverOS 搜索接口一次只能固定一个空间（app_id/project_id），
  principal 获准几个空间就发几次请求（R0/R1 典型为 4：shared、domain-<域>、
  projects-<每个获准项目>、agent-<每个获准私有 agent>），raw 按顺序保存各
  响应体。适配器合并各响应的 `data.episodes`、按 episode id 去重取最高分、
  排序、截断 top_k 得到 `hits`。每个响应体中还有 `profiles/agent_cases/
  agent_skills/unprocessed_messages` 字段，本 bench 的 episode 向量检索路径
  不使用它们，原样存档备查。
- `text`：episode DTO 的 `summary`、`subject`、`episode` 三字段按序以换行拼接。
  **三者可能重复或高度相似**（如实拼接，非 bug），人工评审时按整体语义判断。
- `native_metadata`：保留 `user_id/app_id/project_id/session_id/timestamp/
  sender_ids/atomic_facts`。`app_id/project_id` 即物理隔离空间名，可核对
  写入作用域映射；`timestamp` 为消息原生时间。
- `source_refs`：**仅 `[session_id]`，session 级**。搜索 DTO 不暴露消息级
  引用（`atomic_facts` 实测为空）。按实验设计，不得用 harness 已知的
  message ID 补判为"来源通过"；因此带 `source_check` 的用例对 EverOS
  预期 FAIL，属已记录的 D 类能力缺口，而非运行故障。
- episode 语言：默认提示词含强制语言一致规则，但共享 LLM 对简短输入实测
  可能违规输出英文 episode（decision 运行 U01/C02/T01；full 扩展面
  U01/C01/C02/T01/C05/T02，另 C03 双轨语言翻转），伴随中文 token
  未命中、R1 跨语言 rerank 分数坍缩（≈0.00x，但非均匀：full R1 T02 英文
  命中 rerank 0.9968、C03 0.9589，U01 仅 0.0007）。评审时须核对 hits 文本
  语言并如实记录，属能力发现，不做 harness 侧修补。

### 6.3 共享索引完整性缺陷（full 实测，评审必读）

- **机制**：episode 序号按空间独立计数（每空间当日均从 `ep_<date>_00000001`
  起），而所有空间共享同一个 LanceDB `episode` 表（`runtime/<run>/.index/lancedb`），
  主键 `{user}_ep_{date}_{seq}` 不含 app/project 成分。同一 case 的单 session
  先后 flush 到多个空间时（D01/D04/P02），后完成空间的 cascade upsert 覆盖
  先前空间的索引行；markdown 事实源（`runtime/<run>/<namespace>-<空间>/users/<owner>/episodes/*.md`）
  完好，提取与空间路由本身正确。
- **签名**：`search_attempt` 曲线 `[1, 0, 0, …]`（首查命中、随后归零）且案例
  含多空间写入。终态整个 run 索引仅 5 行（每 (user,date,seq) 只剩最后一个写者）；
  其余案例可检索只因每案例检索紧跟自身写入。LanceDB 自动 compaction 只保留
  1 个版本，无法时间旅行取证——机制由 markdown 对照 + attempt 曲线 + 终态表
  三方证据链确认，详见 experiment-design 隔离映射。
- **评审口径**：此类 FAIL 归因能力层·索引完整性（非提取/检索能力），核对
  runtime markdown 确认内容忠实度；负例 0 hits 须区分「索引未就绪」与
  「真实隔离」（写入空间不在检索 principal 可读集合的 D02/U05/P04 属后者）。

## 7. events.jsonl 事件类型

每行 `{"observed_at", "kind", "payload"}`：

| kind | 写入时机 | payload 要点 |
|---|---|---|
| `write` | 每次写操作完成 | case_id、完整回执 |
| `search_attempt` | 轮询的**每次**尝试 | attempt 序号、接口状态、hit 数、判分状态、硬失败列表 |
| `search_transport_retry` | attempt 内传输层重试 | retry 序号、被重试的接口状态与错误 |
| `search` | search 操作收尾（最终尝试） | 最终状态、hit 数、attempts、完整 evaluation |
| `run_error` | 运行级异常（BLOCKED） | 错误信息 |
| `integration_preseed` | integrate 预置写入 | 每条记忆的请求与回执 |
| `integration_task` | integrate 每个 task×mode 完成 | 见 §8 |
| `integration_error` | integrate 运行级异常 | 错误信息 |

## 8. integration_results.json（仅 integrate 运行）

| 字段 | 含义 |
|---|---|
| `preseed` | 预置记忆的全部写入请求/回执 |
| `tasks` | 每个 task×mode（M0/M1/M2）一条记录：`answer`（Agent 回答全文）、`tool_trace`（工具调用轨迹，应只见 stub）、`skill_route`、`memory_route`（路由决策）、`injected_context`（注入的记忆上下文原文）、`required_tokens_found` / `forbidden_tokens_found`（逐 token 布尔判定）、`elapsed_ms` |
| `bridge_searches` / `bridge_writes` | bridge 侧检索/写入事件；评估回合不写回，`bridge_writes` 应为空 |

## 9. 人工评审速查

1. 从 `reports/case_results.csv` 或运行级 CSV 找出 `REVIEW_REQUIRED` 与需归因的 `FAIL`；
2. 打开对应 `case_results.json`，读 search 操作的 `hits[].text`（连同
   `native_metadata`），对照 `evaluation.review_items` 逐命题判定；
3. FAIL 先分清接口层（`result.status`/`error`）、可见性（`attempts` 与
   `search_attempt` 曲线）、能力层（hard_failures 内容）三种原因；
4. 评审结论（评审人、时间、run_id、case、逐命题判定、理由）另存
   `reports/manual_review_<run_id>.md`，与 artifacts 一同作为证据；
   模板见 `reports/manual_review_TEMPLATE.md`（复制后填写，内含已填好的 F02 示例）；
5. 两候选须同一人、同一标准评审。
