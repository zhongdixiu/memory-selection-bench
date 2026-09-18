# Agent 自动语义评估记录

> 本文件的逐命题判定与案例终判均为 Agent 自动评估，尚未经过人工复核。
> 「本案例人工终判」是预填脚本沿用的字段名，不表示已经人工签署。

> 判定只依据 `case_results.json` 中候选实际返回的 `hits[].text`（可参考
> `native_metadata`），禁止引入 harness 已知但候选未返回的信息
> （例如不得用用例里的 message ID 替 EverOS 补成「来源通过」）。
> 本文件由 `scripts/make_review_skeletons.py` 预填机械证据；现有判定与终判为 Agent 自动建议。

## 基本信息

| 项 | 值 |
|---|---|
| run_id | `20260915T080353Z-everos-r0-full-4a9195d0` |
| 候选 / 轨道 / 套件 | everos / r0 / full |
| 运行时间 | 2026-09-15T08:03:53.982241+00:00 → 2026-09-15T09:07:32.949091+00:00（status=FAIL） |
| 评估主体 | Agent 自动评估（未人工复核） |
| 人工复核状态 | 未进行 |
| 证据路径 | `artifacts/20260915T080353Z-everos-r0-full-4a9195d0/case_results.json` |
| 输入指纹 | case_data_hash=`ef7ff5096fd8` config_hash=`27df7b45d308` |

## 评审范围

- REVIEW_REQUIRED：N01, N02, N03, N04, N05, U02, U05, D02, P04
- FAIL（需归因复核）：F01, F02, F03, F04, F05, U01, U03, U04, D01, D03, D04, P01, P02, P03, P05, C01, C02, C03, C04, C05, T01, T02, T03, T04, T05
- UNSUPPORTED：D05, E01, E02, E03, E04, E05

## 预填导航（脚本+LLM 预填，供人工复核）

判定来源统计：AI 语义判定 50 条，复用（everos-r0 已填同款单元）0 条，机械层 13 条（0 hits 0／隔离负例 3／字面全包含 10），终判建议 40 条。
标记说明：【AI·高/中/低】LLM 语义判定及置信度；【机·…】机械可证；【复·…】跨文件复用同款判定。所有预填均为建议，人工确认后请去掉尖括号 `<>`；改判直接覆盖并删标记。

**建议复核顺序**：先看下面 26 个重点案例，再抽查高置信度条目。

- F01 #2（forbidden「用户是该项目的高级负责人」→ 未出现：中置信度）
- N01 #1（forbidden「用户已经改用 Java」→ 未出现：中置信度）
- N01（终判含中/低置信度命题，请重点复核）
- N02 #1（forbidden「U1 喜欢短邮件」→ 未出现：中置信度）
- N02（终判含中/低置信度命题，请重点复核）
- N03 #1（forbidden「用户负责预算」→ 未出现：中置信度）
- N03（终判含中/低置信度命题，请重点复核）
- N04 #1（forbidden「U1 常住上海」→ 未出现：中置信度）
- N04（终判含中/低置信度命题，请重点复核）
- N05 #1（forbidden「所有未来任务必须简短」→ 未出现：中置信度）
- N05（终判含中/低置信度命题，请重点复核）
- U02 #1（forbidden「U2 的 P1 采用蓝色发布」→ 出现：forbidden 判为出现）
- U02（REVIEW_REQUIRED → 建议改判 FAIL：语义判定未全满足：#1forbidden=出现）
- U02（终判含中/低置信度命题，请重点复核）
- D01 #1（required「邮件要求简洁」→ 成立：中置信度）
- D01 #2（forbidden「邮件要求详细」→ 未出现：中置信度）
- D04 #1（required「报告规则仍为详细」→ 成立：中置信度）
- D05 #1（forbidden「未授权 Agent 读取私有案例」→ 未出现：0 hits，依据候选自产 md 判定）
- P02 #1（required「P1 先接邮件」→ 成立：中置信度）
- P02 #2（forbidden「P1 先接日程」→ 未出现：中置信度）
- C02 #2（forbidden「用户当前仍住北京」→ 未出现：中置信度）
- C05 #2（forbidden「P1 同时处于设计、开发和联调」→ 未出现：中置信度）
- T02 #1（required「仅在 2026-09-14 13:00 至 18」→ 部分成立：部分成立）
- E01 #1（required「先读取 Retry-After」→ 不成立：0 hits，依据候选自产 md 判定）
- E01 #2（required「按指定时间重试」→ 不成立：0 hits，依据候选自产 md 判定）
- E01 #3（required「缺失时转人工」→ 不成立：0 hits，依据候选自产 md 判定）
- E02 #1（required「盲目重试会导致重复提交且属于失败案例」→ 不成立：0 hits，依据候选自产 md 判定）
- E02 #2（forbidden「推荐盲目重试」→ 未出现：0 hits，依据候选自产 md 判定）
- E03 #1（required「先写草稿」→ 不成立：0 hits，依据候选自产 md 判定）
- E03 #2（required「再校验收件人」→ 不成立：0 hits，依据候选自产 md 判定）
- E03 #3（required「最后取得用户确认」→ 不成立：0 hits，依据候选自产 md 判定）
- E04 #1（forbidden「U2 读取 U1 专属案例」→ 未出现：0 hits，依据候选自产 md 判定）
- E05 #1（required「当前采用 v2 且先校验输入再生成」→ 不成立：0 hits，依据候选自产 md 判定）
- E05 #2（forbidden「当前仍先生成后检查」→ 未出现：0 hits，依据候选自产 md 判定）


## 运行级机械观察（脚本自动生成，评审导航用）

**索引完整性缺陷签名（attempt1 命中后归零），共 3 例**：D01, D04, P02。
机制：episode 序号按空间独立计数（各空间当日都从 ep_…_00000001 起），而共享 LanceDB
episode 表主键 `{user}_ep_{date}_{seq}` 不含 app/project 成分——同一 session 先后 flush 到
多个空间时，后完成空间的 cascade upsert 覆盖先前空间的索引行（markdown 事实源完好，
提取与空间路由本身正确）。整个 run 终态索引仅 5 行，每个 (user,date,seq) 只剩最后一个写者
（如 U1_ep_20260915_00000001 终归 t05-projects）；其余案例当时可检索只因每案例检索紧跟自身写入、
在下一案例覆盖前完成。同用户同日多空间为产品真实场景，属结构性缺陷，双轨稳定复现。

- **D01**：attempt1 命中 1 条后全部归零（曲线 [1, 0, 0, 0, 0]…）；同 session 写入 2 个空间（domain/email、domain/report）；各空间 episode 序号独立计数致同名 ep_<date>_00000001，而共享 LanceDB episode 表主键 {user}_ep_{date}_{seq} 不含空间成分，后完成空间的 cascade upsert 覆盖先前空间的索引行（markdown 事实源完好；索引终态可在 runtime/<run>/.index/lancedb 复核）
- **D04**：attempt1 命中 1 条后全部归零（曲线 [1, 0, 0, 0, 0]…）；同 session 写入 2 个空间（domain/email、domain/report）；各空间 episode 序号独立计数致同名 ep_<date>_00000001，而共享 LanceDB episode 表主键 {user}_ep_{date}_{seq} 不含空间成分，后完成空间的 cascade upsert 覆盖先前空间的索引行（markdown 事实源完好；索引终态可在 runtime/<run>/.index/lancedb 复核）
- **P02**：attempt1 命中 1 条后全部归零（曲线 [1, 0, 0, 0, 0]…）；同 session 写入 2 个空间（project/P1、project/P2）；各空间 episode 序号独立计数致同名 ep_<date>_00000001，而共享 LanceDB episode 表主键 {user}_ep_{date}_{seq} 不含空间成分，后完成空间的 cascade upsert 覆盖先前空间的索引行（markdown 事实源完好；索引终态可在 runtime/<run>/.index/lancedb 复核）

**单次即时检索且 0 hits 的案例（9 个）**：N01, N02, N03, N04, N05, U02, U05, D02, P04。
方法论披露：everos 索引异步收敛（实测约 20~40s，对照 F03 曲线 [0,0,1,…]），而自动判分仅在
存在硬失败时触发可见性轮询——负例（无 required token）0 hits 不构成硬失败，检索在写入 flush
后约 1s 单次执行即定案。因此这些 0 hits **不能区分「内容级克制」与「索引未就绪」**；runtime
markdown 显示 N 组消息实际全部被提取存储（表述忠实：疑问存为「U1询问…」、否认存为「U1否认…」）。
评审 N 组语义命题时以 hits（主依据）+ 候选自产 md（补充证据）判定，勿把 0 hits 直接当作
「推测未存储」；写入空间不在检索 principal 可读集合的隔离类负例（如 D02/U05/P04）不受时序影响。
候选行为差异备忘：everos 对负例消息的策略是**忠实提取、中性框架**（疑问存为询问、否认存为否认），
而非 mem0 式的整条跳过——两者皆为可辩护的产品行为，评审按语义命题判定而非按「是否存储」判定。
另注意：N03 的 everos episode「U1否认负责预算…」含 forbidden 子串「负责预算」，若检索时索引已收敛
会触发与 mem0 R1 同类的否定子串误判 FAIL；本次因 0 hits 未触发，评审终判时按同一口径处理。


## 逐案例评审

---

### 案例 F01：用户负责项目

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[f01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T09:00:00+08:00）：「我负责统一记忆项目 P1。」
- search[f01-q1]（U1）：「我负责什么项目？」 机械检查：required_tokens=['P1']，source_check=any 期望 ['f01-m1']

**写入回执核对**（机械证据）：
- write[f01-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=11）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.5696 source_refs=['f01-session'] 语言=中文
2026-09-14 01:00 UTC，U1声明其负责统一记忆项目 P1。
U1负责统一记忆项目P1的角色确认
2026-09-14 01:00 UTC，U1声明其负责统一记忆项目 P1。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户负责统一记忆项目 P1 | `<成立>` | `<【AI·高】hit明确记录「U1声明其负责统一记忆项目 P1」，命题被忠实表达，无歪曲。>` |
| 2 | forbidden | 用户是该项目的高级负责人 | `<未出现>` | `<【AI·中】hit仅记「U1声明其负责统一记忆项目 P1」，未断言「高级负责人」身份，禁止命题未被正面陈述。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 F02：默认技术语言

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[f02-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T09:10:00+08:00）：「技术方案默认用 Python。」
- search[f02-q1]（U1）：「技术方案默认使用什么语言？」 机械检查：required_tokens=['Python']，source_check=any 期望 ['f02-m1']

**写入回执核对**（机械证据）：
- write[f02-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.7522 source_refs=['f02-session'] 语言=中文
2026-09-14 01:10 UTC，U1明确指定技术方案的默认开发语言为Python。
U1确定技术方案默认使用Python语言
2026-09-14 01:10 UTC，U1明确指定技术方案的默认开发语言为Python。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 技术方案默认使用 Python | `<成立>` | `<【机·字面全包含】字面全包含：hit「2026-09-14 01:10 UTC，U1明确指定技术方案的默认开发语言为Python。」覆盖命题全部实词字符>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 F03：邮件回复风格

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[f03-w1]（U1，scope=domain/email，occurred_at=2026-09-14T09:20:00+08:00）：「邮件回复尽量简洁。」
- search[f03-q1]（U1）：「我的邮件回复风格是什么？」 机械检查：required_tokens=['简洁']，source_check=any 期望 ['f03-m1']

**写入回执核对**（机械证据）：
- write[f03-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.7081 source_refs=['f03-session'] 语言=中文
2026-09-14 01:20 UTC，U1明确提出要求，指出邮件回复应当尽量保持简洁。
U1提出邮件回复需保持简洁的要求
2026-09-14 01:20 UTC，U1明确提出要求，指出邮件回复应当尽量保持简洁。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 邮件回复应尽量简洁 | `<成立>` | `<【机·字面全包含】字面全包含：hit「2026-09-14 01:20 UTC，U1明确提出要求，指出邮件回复应当尽量保持简洁。」覆盖命题全部实词字符>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 F04：对外发送确认规则

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[f04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T09:30:00+08:00）：「对外发送前必须先让我确认。」
- search[f04-q1]（U1）：「对外发送前有什么长期要求？」 机械检查：required_tokens=['确认']，source_check=any 期望 ['f04-m1']

**写入回执核对**（机械证据）：
- write[f04-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.6972 source_refs=['f04-session'] 语言=中文
2026-09-14 01:30 UTC，U1明确规定在对外发送任何内容之前，必须先经过其确认。
U1要求对外发送前必须确认 2026-09-14
2026-09-14 01:30 UTC，U1明确规定在对外发送任何内容之前，必须先经过其确认。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 对外发送前必须由用户确认 | `<成立>` | `<【AI·高】hit记录「U1明确规定在对外发送任何内容之前，必须先经过其确认」，命题被忠实表达。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 F05：同段多事实及逐条来源

**自动判分结果**：FAIL；hard_failures：native source references are incomplete

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[f05-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T09:40:00+08:00）：「我负责 P1；邮件简洁；报告必须保留指标。」
- search[f05-q1]（U1）：「总结我的项目、邮件风格和报告要求。」 机械检查：required_tokens=['P1', '简洁', '指标']，source_check=per_claim 期望 ['f05-m1']

**写入回执核对**（机械证据）：
- write[f05-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=11）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.6156 source_refs=['f05-session'] 语言=中文
2026-09-14 01:40 UTC，U1声明其负责P1项目，并要求邮件保持简洁，同时规定报告中必须保留指标。
U1确认负责P1项目并规定邮件与报告格式要求
2026-09-14 01:40 UTC，U1声明其负责P1项目，并要求邮件保持简洁，同时规定报告中必须保留指标。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户负责 P1 | `<成立>` | `<【AI·高】hit记录「U1声明其负责P1项目」，命题核心忠实保留；附加邮件/报告要求不影响本命题。>` |
| 2 | required | 邮件要求简洁 | `<成立>` | `<【机·字面全包含】字面全包含：hit「2026-09-14 01:40 UTC，U1声明其负责P1项目，并要求邮件保持简洁，同时规定报告中」覆盖命题全部实词字符>` |
| 3 | required | 报告必须保留指标 | `<成立>` | `<【机·字面全包含】字面全包含：hit「2026-09-14 01:40 UTC，U1声明其负责P1项目，并要求邮件保持简洁，同时规定报告中」覆盖命题全部实词字符>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 N01：假设不应成为当前事实

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[n01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:00:00+08:00）：「假如以后改用 Java，会有什么影响？」
- search[n01-q1]（U1）：「当前技术语言是什么？」 机械检查：forbidden_tokens=['已经改用 Java']

**写入回执核对**（机械证据）：
- write[n01-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 用户已经改用 Java | `<未出现>` | `<【AI·中】依据候选自产md：记为「U1提出假设性问题，咨询如果以后改用Java会产生什么影响」，属疑问框架，未正面断言已改用Java。；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ everos 0 hits 且 attempts=1：everos 索引异步收敛（实测约 20~40s），无硬失败的检索不触发可见性轮询，本次检索距写入 flush 仅约 1s——0 hits 可能是索引未就绪而非内容不存在。请对照 runtime/<run>/<namespace>-<空间>/users/<owner>/episodes/*.md（候选自产事实源，可作忠实度补充证据）确认提取是否发生及表述框架；若写入空间本就不在检索 principal 可读集合（隔离类负例如 D02/U05/P04），0 hits 结论不受时序影响。

**本案例人工终判**：`<PASS>`（【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核））

---

### 案例 N02：第三方偏好不得归属用户

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[n02-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:10:00+08:00）：「同事小林喜欢短邮件。」
- search[n02-q1]（U1）：「我喜欢什么样的邮件？」 机械检查：forbidden_tokens=['U1喜欢短邮件']

**写入回执核对**（机械证据）：
- write[n02-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | U1 喜欢短邮件 | `<未出现>` | `<【AI·中】依据候选自产md：记录为「colleague Xiao Lin prefers short emails」，是同事偏好，未断言U1本人喜欢短邮件。；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ everos 0 hits 且 attempts=1：everos 索引异步收敛（实测约 20~40s），无硬失败的检索不触发可见性轮询，本次检索距写入 flush 仅约 1s——0 hits 可能是索引未就绪而非内容不存在。请对照 runtime/<run>/<namespace>-<空间>/users/<owner>/episodes/*.md（候选自产事实源，可作忠实度补充证据）确认提取是否发生及表述框架；若写入空间本就不在检索 principal 可读集合（隔离类负例如 D02/U05/P04），0 hits 结论不受时序影响。

**本案例人工终判**：`<PASS>`（【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核））

---

### 案例 N03：助手推测被用户否认

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[n03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:20:00+08:00）：「你可能负责预算。」
- write[n03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:21:00+08:00）：「我没有这样说。」
- search[n03-q1]（U1）：「我是否负责预算？」 机械检查：forbidden_tokens=['负责预算']

**写入回执核对**（机械证据）：
- write[n03-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 用户负责预算 | `<未出现>` | `<【AI·中】依据候选自产md：「email_agent推测U1可能负责预算」后「U1明确否认了这一说法」，属否认框架，非正面断言。；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ everos 0 hits 且 attempts=1：everos 索引异步收敛（实测约 20~40s），无硬失败的检索不触发可见性轮询，本次检索距写入 flush 仅约 1s——0 hits 可能是索引未就绪而非内容不存在。请对照 runtime/<run>/<namespace>-<空间>/users/<owner>/episodes/*.md（候选自产事实源，可作忠实度补充证据）确认提取是否发生及表述框架；若写入空间本就不在检索 principal 可读集合（隔离类负例如 D02/U05/P04），0 hits 结论不受时序影响。

**本案例人工终判**：`<PASS>`（【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核））

---

### 案例 N04：引述客户原话不得归属用户

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[n04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:30:00+08:00）：「客户原话是“我常住上海”。」
- search[n04-q1]（U1）：「我常住哪里？」 机械检查：forbidden_tokens=['U1常住上海']

**写入回执核对**（机械证据）：
- write[n04-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | U1 常住上海 | `<未出现>` | `<【AI·中】依据候选自产md：「U1记录了客户的原话陈述，指出该客户常住地点为上海」，主体是客户而非U1。；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ everos 0 hits 且 attempts=1：everos 索引异步收敛（实测约 20~40s），无硬失败的检索不触发可见性轮询，本次检索距写入 flush 仅约 1s——0 hits 可能是索引未就绪而非内容不存在。请对照 runtime/<run>/<namespace>-<空间>/users/<owner>/episodes/*.md（候选自产事实源，可作忠实度补充证据）确认提取是否发生及表述框架；若写入空间本就不在检索 principal 可读集合（隔离类负例如 D02/U05/P04），0 hits 结论不受时序影响。

**本案例人工终判**：`<PASS>`（【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核））

---

### 案例 N05：单次要求不得晋升长期偏好

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[n05-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:40:00+08:00）：「这一次回答短一点。」
- search[n05-q1]（U1）：「我对所有未来任务有什么长期风格要求？」 机械检查：forbidden_tokens=['所有未来任务']

**写入回执核对**（机械证据）：
- write[n05-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 所有未来任务必须简短 | `<未出现>` | `<【AI·中】依据候选自产md：r0「希望接下来的回答保持简短」、r1「本次回答需简短」，均限定当次回答，未泛化为所有未来任务必须简短。；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ everos 0 hits 且 attempts=1：everos 索引异步收敛（实测约 20~40s），无硬失败的检索不触发可见性轮询，本次检索距写入 flush 仅约 1s——0 hits 可能是索引未就绪而非内容不存在。请对照 runtime/<run>/<namespace>-<空间>/users/<owner>/episodes/*.md（候选自产事实源，可作忠实度补充证据）确认提取是否发生及表述框架；若写入空间本就不在检索 principal 可读集合（隔离类负例如 D02/U05/P04），0 hits 结论不受时序影响。

**本案例人工终判**：`<PASS>`（【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核））

---

### 案例 U01：两用户偏好隔离

**自动判分结果**：FAIL；hard_failures：missing required token: 详细；no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[u01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T11:00:00+08:00）：「我喜欢简洁回答。」
- write[u01-w2]（U2，scope=user_public/U2，occurred_at=2026-09-14T11:01:00+08:00）：「我喜欢详细回答。」
- search[u01-q1]（U2）：「我喜欢什么回答风格？」 机械检查：required_tokens=['详细']，forbidden_tokens=['简洁']，source_check=any 期望 ['u01-m2']

**写入回执核对**（机械证据）：
- write[u01-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[u01-w2]（U2）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.5947 source_refs=['u01-session'] 语言=英文
On 2026-09-14 03:01 UTC (Monday), U2 stated a preference for receiving detailed answers.
U2 expresses preference for detailed answers on 2026-09-14
On 2026-09-14 03:01 UTC (Monday), U2 stated a preference for receiving detailed answers.
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | U2 喜欢详细回答 | `<成立>` | `<【AI·高】hit「stated a preference for receiving detailed answers」忠实表达U2喜欢详细回答。>` |
| 2 | forbidden | U2 喜欢简洁回答 | `<未出现>` | `<【AI·高】hit称U2偏好「detailed answers」，与「喜欢简洁回答」相反，未断言禁止命题。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ 检出英文 episode：默认提示词含强制语言一致规则，此为共享 LLM 违规（能力发现），评审时记录对 token/命题判定的影响。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 U02：同名项目跨用户隔离

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[u02-w1]（U1，scope=project/P1，occurred_at=2026-09-14T11:10:00+08:00）：「P1 决定采用蓝色发布。」
- search[u02-q1]（U2）：「P1 采用什么发布策略？」 机械检查：forbidden_tokens=['蓝色发布']

**写入回执核对**（机械证据）：
- write[u02-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | U2 的 P1 采用蓝色发布 | `<出现>` | `<【AI·中】0 hits，但md正面断言「P1决定采用蓝色发布方案」「U1指出P1决定采用蓝色发布」，依据候选自产md。；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ everos 0 hits 且 attempts=1：everos 索引异步收敛（实测约 20~40s），无硬失败的检索不触发可见性轮询，本次检索距写入 flush 仅约 1s——0 hits 可能是索引未就绪而非内容不存在。请对照 runtime/<run>/<namespace>-<空间>/users/<owner>/episodes/*.md（候选自产事实源，可作忠实度补充证据）确认提取是否发生及表述框架；若写入空间本就不在检索 principal 可读集合（隔离类负例如 D02/U05/P04），0 hits 结论不受时序影响。

**本案例人工终判**：`<FAIL>`（【AI·中】语义判定未全满足：#1forbidden=出现）

---

### 案例 U03：相同会话标识不混用户

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[u03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T11:20:00+08:00）：「我负责架构。」
- write[u03-w2]（U2，scope=user_public/U2，occurred_at=2026-09-14T11:21:00+08:00）：「我负责测试。」
- search[u03-q1]（U1）：「我负责什么？」 机械检查：required_tokens=['架构']，forbidden_tokens=['测试']，source_check=any 期望 ['u03-m1']

**写入回执核对**（机械证据）：
- write[u03-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[u03-w2]（U2）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=11）：hits 序列 [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.5809 source_refs=['shared-session'] 语言=中文
2026-09-14 03:20 UTC，U1声明其负责架构工作。
U1确认负责架构工作 2026-09-14
2026-09-14 03:20 UTC，U1声明其负责架构工作。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | U1 负责架构 | `<成立>` | `<【机·字面全包含】字面全包含：hit「2026-09-14 03:20 UTC，U1声明其负责架构工作。」覆盖命题全部实词字符>` |
| 2 | forbidden | U1 负责测试 | `<未出现>` | `<【AI·高】hit仅称「U1声明其负责架构工作」，未断言U1负责测试。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 U04：更新不得跨用户

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[u04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T11:30:00+08:00）：「我现居北京。」
- write[u04-w2]（U2，scope=user_public/U2，occurred_at=2026-09-14T11:31:00+08:00）：「我现居北京。」
- write[u04-w3]（U2，scope=user_public/U2，occurred_at=2026-09-14T11:32:00+08:00）：「我已搬到上海。」
- search[u04-q1]（U1）：「我现在住在哪里？」 机械检查：required_tokens=['北京']，forbidden_tokens=['上海']，source_check=any 期望 ['u04-m1']

**写入回执核对**（机械证据）：
- write[u04-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[u04-w2]（U2）：PASS，processed=True（add=accumulated → flush=extracted）
- write[u04-w3]（U2）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.5900 source_refs=['u04-session'] 语言=中文
2026-09-14 03:30 UTC，U1声明其现居地为北京。
U1声明现居北京 2026-09-14
2026-09-14 03:30 UTC，U1声明其现居地为北京。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | U1 仍居住北京 | `<成立>` | `<【AI·高】hit「U1声明其现居地为北京」忠实表达U1仍居住北京。>` |
| 2 | forbidden | U1 已搬到上海 | `<未出现>` | `<【AI·高】hit称「U1声明其现居地为北京」，未断言已搬到上海。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 U05：缺失或伪造身份

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[u05-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T11:40:00+08:00）：「我的私有校验码是 USER-U1-805。」
- search[u05-q1]（None）：「U1 的私有校验码是什么？」 机械检查：forbidden_tokens=['USER-U1-805']

**写入回执核对**（机械证据）：
- write[u05-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 未认证调用者读取 U1 数据 | `<未出现>` | `<【机·隔离负例】0 hits；隔离类负例（写入空间不在检索 principal 可读集合），结论不受索引时序影响>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ everos 0 hits 且 attempts=1：everos 索引异步收敛（实测约 20~40s），无硬失败的检索不触发可见性轮询，本次检索距写入 flush 仅约 1s——0 hits 可能是索引未就绪而非内容不存在。请对照 runtime/<run>/<namespace>-<空间>/users/<owner>/episodes/*.md（候选自产事实源，可作忠实度补充证据）确认提取是否发生及表述框架；若写入空间本就不在检索 principal 可读集合（隔离类负例如 D02/U05/P04），0 hits 结论不受时序影响。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 D01：业务偏好隔离

**自动判分结果**：FAIL；hard_failures：missing required token: 简洁

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[d01-w1]（U1，scope=domain/email，occurred_at=2026-09-14T12:00:00+08:00）：「邮件回复要简洁。」
- write[d01-w2]（U1，scope=domain/report，occurred_at=2026-09-14T12:01:00+08:00）：「报告要详细。」
- search[d01-q1]（U1）：「当前业务的表达要求是什么？」 机械检查：required_tokens=['简洁']，forbidden_tokens=['报告要详细']，source_check=any 期望 ['d01-m1']

**写入回执核对**（机械证据）：
- write[d01-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[d01-w2]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=11）：hits 序列 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 邮件要求简洁 | `<成立>` | `<【AI·中】依据候选自产md：md忠实存储「U1明确提出邮件回复应当保持简洁」，与命题一致。；含候选自产 md 补充证据>` |
| 2 | forbidden | 邮件要求详细 | `<未出现>` | `<【AI·中】依据候选自产md：md仅载「邮件回复应当保持简洁」「报告内容必须详细」，未正面断言邮件要求详细。；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ 索引完整性缺陷签名：attempt1 曾命中、随后归零（见检索尝试曲线）——episode 已正确提取并写入所属空间的 markdown 事实源，但共享 LanceDB 主键（{user}_ep_{date}_{seq}，不含空间成分）被同 session 另一空间的同名 episode 覆盖。FAIL 根因在索引层，非提取/路由/检索能力；评审可读 runtime 目录 md 原文核对内容忠实度。
- 0 hits：对照写入回执判断是写入未落库（如 mem0 raw.results=[]）还是召回失败。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 D02：私有业务代号不泄漏

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[d02-w1]（U1，scope=domain/email，occurred_at=2026-09-14T12:10:00+08:00）：「邮件审核代号是 MAIL-ONLY-731。」
- search[d02-q1]（U1）：「有哪些审核代号？」 机械检查：forbidden_tokens=['MAIL-ONLY-731']

**写入回执核对**（机械证据）：
- write[d02-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 报告业务读取邮件私有代号 | `<未出现>` | `<【机·隔离负例】0 hits；隔离类负例（写入空间不在检索 principal 可读集合），结论不受索引时序影响>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ everos 0 hits 且 attempts=1：everos 索引异步收敛（实测约 20~40s），无硬失败的检索不触发可见性轮询，本次检索距写入 flush 仅约 1s——0 hits 可能是索引未就绪而非内容不存在。请对照 runtime/<run>/<namespace>-<空间>/users/<owner>/episodes/*.md（候选自产事实源，可作忠实度补充证据）确认提取是否发生及表述框架；若写入空间本就不在检索 principal 可读集合（隔离类负例如 D02/U05/P04），0 hits 结论不受时序影响。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 D03：公共职责跨业务可见

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[d03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T12:20:00+08:00）：「我是 P1 负责人。」
- search[d03-q1]（U1）：「我的公共职责是什么？」 机械检查：required_tokens=['P1']，source_check=any 期望 ['d03-m1']

**写入回执核对**（机械证据）：
- write[d03-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.4161 source_refs=['d03-session'] 语言=中文
2026-09-14 04:20 UTC，U1明确声明自己是P1负责人。
U1声明担任P1项目负责人身份确认
2026-09-14 04:20 UTC，U1明确声明自己是P1负责人。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户是 P1 负责人 | `<成立>` | `<【AI·高】hit1「U1明确声明自己是P1负责人」，忠实表达命题。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 D04：跨域更新互不覆盖

**自动判分结果**：FAIL；hard_failures：missing required token: 详细

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[d04-w1]（U1，scope=domain/email，occurred_at=2026-09-14T12:30:00+08:00）：「邮件规则是简洁。」
- write[d04-w2]（U1，scope=domain/report，occurred_at=2026-09-14T12:31:00+08:00）：「报告规则是详细。」
- write[d04-w3]（U1，scope=domain/email，occurred_at=2026-09-14T12:32:00+08:00）：「邮件也改为需要细节。」
- search[d04-q1]（U1）：「报告规则是什么？」 机械检查：required_tokens=['详细']，source_check=any 期望 ['d04-m2']

**写入回执核对**（机械证据）：
- write[d04-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[d04-w2]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[d04-w3]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 报告规则仍为详细 | `<成立>` | `<【AI·中】依据候选自产md：report域episode明确记录「U1指出报告规则是详细的」，忠实存储命题。；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ 索引完整性缺陷签名：attempt1 曾命中、随后归零（见检索尝试曲线）——episode 已正确提取并写入所属空间的 markdown 事实源，但共享 LanceDB 主键（{user}_ep_{date}_{seq}，不含空间成分）被同 session 另一空间的同名 episode 覆盖。FAIL 根因在索引层，非提取/路由/检索能力；评审可读 runtime 目录 md 原文核对内容忠实度。
- 0 hits：对照写入回执判断是写入未落库（如 mem0 raw.results=[]）还是召回失败。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 D05：Agent 私有案例隔离

**自动判分结果**：UNSUPPORTED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[d05-w1]（U1，scope=agent_private/email_agent，occurred_at=2026-09-14T12:40:00+08:00）：「Email Agent 私有案例标识 AGENT-A-515。」
- search[d05-q1]（U1）：「有哪些 Agent 私有案例？」 机械检查：forbidden_tokens=['AGENT-A-515']

**写入回执核对**（机械证据）：
- write[d05-w1]（U1）：**UNSUPPORTED**（direct_record 无契约，未发请求）：`EverOS memory/add has no direct_record contract`

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 未授权 Agent 读取私有案例 | `<未出现>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<FAIL>`（【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持））

---

### 案例 P01：项目决策跨业务延续

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p01-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:00:00+08:00）：「P1 决定先接 Email Agent。」
- search[p01-q1]（U1）：「P1 决定先接哪个 Agent？」 机械检查：required_tokens=['Email Agent']，source_check=any 期望 ['p01-m1']

**写入回执核对**（机械证据）：
- write[p01-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=10）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.8529 source_refs=['p01-session'] 语言=中英混合
2026-09-14 05:00 UTC，P1决定先接Email Agent。
P1决定优先接入Email Agent
2026-09-14 05:00 UTC，P1决定先接Email Agent。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 先接 Email Agent | `<成立>` | `<【机·字面全包含】字面全包含：hit「2026-09-14 05:00 UTC，P1决定先接Email Agent。」覆盖命题全部实词字符>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 P02：同用户多项目隔离

**自动判分结果**：FAIL；hard_failures：missing required token: 邮件

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p02-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:10:00+08:00）：「P1 先接邮件。」
- write[p02-w2]（U1，scope=project/P2，occurred_at=2026-09-14T13:11:00+08:00）：「P2 先接日程。」
- search[p02-q1]（U1）：「P1 的接入顺序是什么？」 机械检查：required_tokens=['邮件']，forbidden_tokens=['P2']，source_check=any 期望 ['p02-m1']

**写入回执核对**（机械证据）：
- write[p02-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[p02-w2]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 先接邮件 | `<成立>` | `<【AI·中】依据候选自产md：「U1指示P1先接邮件」及r1「P1先接收并处理邮件」，忠实存储命题语义。；含候选自产 md 补充证据>` |
| 2 | forbidden | P1 先接日程 | `<未出现>` | `<【AI·中】依据候选自产md：「U1指示P1先接邮件」，日程归P2（「P2先接日程」），未断言P1先接日程。；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ 索引完整性缺陷签名：attempt1 曾命中、随后归零（见检索尝试曲线）——episode 已正确提取并写入所属空间的 markdown 事实源，但共享 LanceDB 主键（{user}_ep_{date}_{seq}，不含空间成分）被同 session 另一空间的同名 episode 覆盖。FAIL 根因在索引层，非提取/路由/检索能力；评审可读 runtime 目录 md 原文核对内容忠实度。
- 0 hits：对照写入回执判断是写入未落库（如 mem0 raw.results=[]）还是召回失败。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 P03：项目记忆跨会话

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p03-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:20:00+08:00）：「P1 范围只包含记忆服务验证。」
- search[p03-q1]（U1）：「P1 的范围是什么？」 机械检查：required_tokens=['记忆服务验证']，source_check=any 期望 ['p03-m1']

**写入回执核对**（机械证据）：
- write[p03-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=11）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.6506 source_refs=['P03-S1'] 语言=中文
2026-09-14 05:20 UTC，U1明确指出P1的范围只包含记忆服务验证。
U1确认P1范围仅包含记忆服务验证
2026-09-14 05:20 UTC，U1明确指出P1的范围只包含记忆服务验证。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 范围只包含记忆服务验证 | `<成立>` | `<【机·字面全包含】字面全包含：hit「2026-09-14 05:20 UTC，U1明确指出P1的范围只包含记忆服务验证。」覆盖命题全部实词字符>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 P04：知道项目标识不等于有权限

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p04-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:30:00+08:00）：「P1 私有决策码 PROJECT-P1-404。」
- search[p04-q1]（U1）：「P1 的私有决策码是什么？」 机械检查：forbidden_tokens=['PROJECT-P1-404']

**写入回执核对**（机械证据）：
- write[p04-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 未授权 Agent 读取 P1 | `<未出现>` | `<【机·隔离负例】0 hits；隔离类负例（写入空间不在检索 principal 可读集合），结论不受索引时序影响>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ everos 0 hits 且 attempts=1：everos 索引异步收敛（实测约 20~40s），无硬失败的检索不触发可见性轮询，本次检索距写入 flush 仅约 1s——0 hits 可能是索引未就绪而非内容不存在。请对照 runtime/<run>/<namespace>-<空间>/users/<owner>/episodes/*.md（候选自产事实源，可作忠实度补充证据）确认提取是否发生及表述框架；若写入空间本就不在检索 principal 可读集合（隔离类负例如 D02/U05/P04），0 hits 结论不受时序影响。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 P05：项目记忆不随任务结束清除

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p05-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:40:00+08:00）：「P1 决定保留项目级来源链，任务 T1 已结束。」
- search[p05-q1]（U1）：「P1 对来源链做了什么决定？」 机械检查：required_tokens=['来源链']，source_check=any 期望 ['p05-m1']

**写入回执核对**（机械证据）：
- write[p05-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.7958 source_refs=['task-T1'] 语言=中文
2026-09-14 05:40 UTC，U1指出P1决定保留项目级来源链，并确认任务T1已结束。
P1决定保留项目级来源链且任务T1结束
2026-09-14 05:40 UTC，U1指出P1决定保留项目级来源链，并确认任务T1已结束。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 决定保留项目级来源链 | `<成立>` | `<【机·字面全包含】字面全包含：hit「2026-09-14 05:40 UTC，U1指出P1决定保留项目级来源链，并确认任务T1已结束。」覆盖命题全部实词字符>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 C01：非冲突偏好并存

**自动判分结果**：FAIL；hard_failures：missing required token: 风景；native source references are incomplete

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[c01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:00:00+08:00）：「我喜欢拍人像。」
- write[c01-w2]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:10:00+08:00）：「我现在也喜欢拍风景了。」
- search[c01-q1]（U1）：「我喜欢拍什么题材？」 机械检查：required_tokens=['人像', '风景']，source_check=per_claim 期望 ['c01-m1', 'c01-m2']

**写入回执核对**（机械证据）：
- write[c01-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[c01-w2]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.5798 source_refs=['c01-session'] 语言=中文
2026-09-14 06:00 UTC，U1明确表示自己喜欢拍摄人像。
U1表达对人像摄影的喜爱 2026-09-14
2026-09-14 06:00 UTC，U1明确表示自己喜欢拍摄人像。
```

```
[hit 2] score=0.5620 source_refs=['c01-session'] 语言=英文
On 2026-09-14 06:10 UTC, U1 stated that they now also enjoy taking landscape photos.
U1 expresses new interest in landscape photography on 2026-09-14
On 2026-09-14 06:10 UTC, U1 stated that they now also enjoy taking landscape photos.
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户喜欢拍人像 | `<成立>` | `<【AI·高】hit1「U1明确表示自己喜欢拍摄人像」，忠实表达命题，无歪曲或限定丢失。>` |
| 2 | required | 用户喜欢拍风景 | `<成立>` | `<【AI·高】hit2「now also enjoy taking landscape photos」即喜欢拍风景，语义忠实。>` |
| 3 | forbidden | 用户不再喜欢拍人像 | `<未出现>` | `<【AI·高】hits仅称「喜欢拍摄人像」及「now also enjoy taking landscape photos」（also为新增兴趣），均未断言不再喜欢人像。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ 检出英文 episode：默认提示词含强制语言一致规则，此为共享 LLM 违规（能力发现），评审时记录对 token/命题判定的影响。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 C02：当前住址与历史住址

**自动判分结果**：FAIL；hard_failures：missing required token: 上海；no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[c02-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:20:00+08:00）：「我现居北京。」
- write[c02-w2]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:30:00+08:00）：「我已搬到上海。」
- search[c02-q1]（U1）：「我当前住在哪里？」 机械检查：required_tokens=['上海']，source_check=any 期望 ['c02-m2']

**写入回执核对**（机械证据）：
- write[c02-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[c02-w2]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.6134 source_refs=['c02-session'] 语言=中文
2026-09-14 06:20 UTC，U1声明其现居地为北京。
U1声明现居北京 2026-09-14
2026-09-14 06:20 UTC，U1声明其现居地为北京。
```

```
[hit 2] score=0.5037 source_refs=['c02-session'] 语言=英文
On 2026-09-14 06:30 UTC, U1 stated that they have moved to Shanghai.
U1 Relocates to Shanghai on 2026-09-14
On 2026-09-14 06:30 UTC, U1 stated that they have moved to Shanghai.
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户当前住在上海 | `<成立>` | `<【AI·高】hit2「have moved to Shanghai」为06:30最新状态，忠实表达当前住上海。>` |
| 2 | forbidden | 用户当前仍住北京 | `<未出现>` | `<【AI·中】hit1为06:20时点声明记录「现居地为北京」，hit2记06:30「moved to Shanghai」在后，整体未正面断言仍住北京；需跨hit时序推理。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ 检出英文 episode：默认提示词含强制语言一致规则，此为共享 LLM 违规（能力发现），评审时记录对 token/命题判定的影响。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 C03：条件化偏好并存

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[c03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:40:00+08:00）：「技术报告要详细，短消息要简洁。」
- search[c03-q1]（U1）：「技术报告和短消息分别应采用什么风格？」 机械检查：required_tokens=['详细', '简洁']，source_check=any 期望 ['c03-m1']

**写入回执核对**（机械证据）：
- write[c03-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=10）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.6506 source_refs=['c03-session'] 语言=中文
2026-09-14 06:40 UTC，U1指出技术报告需要详细，而短消息应当简洁。
U1提出技术报告与短消息的撰写规范
2026-09-14 06:40 UTC，U1指出技术报告需要详细，而短消息应当简洁。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 技术报告详细 | `<成立>` | `<【机·字面全包含】字面全包含：hit「2026-09-14 06:40 UTC，U1指出技术报告需要详细，而短消息应当简洁。」覆盖命题全部实词字符>` |
| 2 | required | 短消息简洁 | `<成立>` | `<【机·字面全包含】字面全包含：hit「2026-09-14 06:40 UTC，U1指出技术报告需要详细，而短消息应当简洁。」覆盖命题全部实词字符>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 C04：明确更正

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[c04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:50:00+08:00）：「默认发布策略是 A。」
- write[c04-w2]（U1，scope=user_public/U1，occurred_at=2026-09-14T15:00:00+08:00）：「更正，默认发布策略应该是 B。」
- search[c04-q1]（U1）：「当前默认发布策略是什么？」 机械检查：required_tokens=['B']，source_check=any 期望 ['c04-m2']

**写入回执核对**（机械证据）：
- write[c04-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[c04-w2]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.7967 source_refs=['c04-session'] 语言=中文
2026-09-14 06:50 UTC，U1声明默认发布策略是A。
U1确认默认发布策略为A
2026-09-14 06:50 UTC，U1声明默认发布策略是A。
```

```
[hit 2] score=0.6464 source_refs=['c04-session'] 语言=英文
On 2026-09-14 07:00 UTC, U1 issued a correction stating that the default release policy should be B.
U1 Corrects Default Release Policy to B on 2026-09-14
On 2026-09-14 07:00 UTC, U1 issued a correction stating that the default release policy should be B.
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 当前策略为 B | `<成立>` | `<【AI·高】hit2更正「default release policy should be B」，忠实表达当前策略为B。>` |
| 2 | forbidden | 当前策略为 A | `<未出现>` | `<【AI·高】hit2「issued a correction stating…should be B」显式更正为B，hit1为更正前声明记录，未断言当前策略为A。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ 检出英文 episode：默认提示词含强制语言一致规则，此为共享 LLM 违规（能力发现），评审时记录对 token/命题判定的影响。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 C05：项目进度版本链

**自动判分结果**：FAIL；hard_failures：missing required token: 联调；no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[c05-w1]（U1，scope=project/P1，occurred_at=2026-09-14T15:10:00+08:00）：「P1 当前设计中。」
- write[c05-w2]（U1，scope=project/P1，occurred_at=2026-09-14T15:20:00+08:00）：「P1 当前开发中。」
- write[c05-w3]（U1，scope=project/P1，occurred_at=2026-09-14T15:30:00+08:00）：「P1 当前联调中。」
- search[c05-q1]（U1）：「P1 当前进度是什么？」 机械检查：required_tokens=['联调']，source_check=any 期望 ['c05-m3']

**写入回执核对**（机械证据）：
- write[c05-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[c05-w2]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[c05-w3]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.5626 source_refs=['c05-session'] 语言=中文
2026-09-14 07:10 UTC，U1指出P1当前正处于设计中。
U1确认P1当前处于设计阶段的状态更新
2026-09-14 07:10 UTC，U1指出P1当前正处于设计中。
```

```
[hit 2] score=0.5621 source_refs=['c05-session'] 语言=中文
2026-09-14 07:20 UTC，U1指出P1当前正在开发中。
U1确认P1项目当前处于开发阶段
2026-09-14 07:20 UTC，U1指出P1当前正在开发中。
```

```
[hit 3] score=0.5048 source_refs=['c05-session'] 语言=英文
On 2026-09-14 07:30 UTC (Monday), U1 stated that P1 is currently in joint debugging.
U1 reports P1 is currently in joint debugging on 2026-09-14
On 2026-09-14 07:30 UTC (Monday), U1 stated that P1 is currently in joint debugging.
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 当前联调中 | `<成立>` | `<【AI·高】hit3（07:30最新）「P1 is currently in joint debugging」，忠实表达P1当前联调中。>` |
| 2 | forbidden | P1 同时处于设计、开发和联调 | `<未出现>` | `<【AI·中】三hit分别为07:10/07:20/07:30带时间戳的阶段声明，呈时序演进，无任何hit断言三阶段同时并存。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ 检出英文 episode：默认提示词含强制语言一致规则，此为共享 LLM 违规（能力发现），评审时记录对 token/命题判定的影响。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 T01：来源时间优先于入库顺序

**自动判分结果**：FAIL；hard_failures：missing required token: 上海；no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[t01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T16:00:00+08:00）：「我已搬到上海。」
- write[t01-w2]（U1，scope=user_public/U1，occurred_at=2026-08-01T09:00:00+08:00）：「补录旧记录：我住在北京。」
- search[t01-q1]（U1）：「我当前住在哪里？」 机械检查：required_tokens=['上海']，source_check=any 期望 ['t01-m1']

**写入回执核对**（机械证据）：
- write[t01-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）
- write[t01-w2]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.5959 source_refs=['t01-session'] 语言=中文
2026-08-01 01:00 UTC，U1进行旧记录补录操作，声明其居住地为北京。
U1补录居住地信息：居住在北京
2026-08-01 01:00 UTC，U1进行旧记录补录操作，声明其居住地为北京。
```

```
[hit 2] score=0.4816 source_refs=['t01-session'] 语言=英文
On 2026-09-14 08:00 UTC (Monday), U1 stated that they had moved to Shanghai.
U1 Relocated to Shanghai on 2026-09-14
On 2026-09-14 08:00 UTC (Monday), U1 stated that they had moved to Shanghai.
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户当前住在上海 | `<成立>` | `<【AI·高】hit「moved to Shanghai」(09-14)为最新记录，支持当前住上海；北京仅为08-01旧记录补录。>` |
| 2 | forbidden | 旧记录覆盖上海 | `<未出现>` | `<【AI·高】hits中补录「居住地为北京」(2026-08-01)与「moved to Shanghai」(09-14)并存且时间戳清晰，无旧记录覆盖上海的表述。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ 检出英文 episode：默认提示词含强制语言一致规则，此为共享 LLM 违规（能力发现），评审时记录对 token/命题判定的影响。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 T02：当天下午临时状态

**自动判分结果**：FAIL；hard_failures：missing required token: 休假；no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[t02-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T09:00:00+08:00）：「今天下午休假。」
- search[t02-q1]（U1）：「2026-09-14 下午用户是否休假？」 机械检查：required_tokens=['休假']，source_check=any 期望 ['t02-m1']

**写入回执核对**（机械证据）：
- write[t02-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.6591 source_refs=['t02-session'] 语言=英文
On 2026-09-14 at 01:00 UTC, U1 stated that they would be taking leave this afternoon (2026-09-14).
U1 Announces Afternoon Leave on 2026-09-14
On 2026-09-14 at 01:00 UTC, U1 stated that they would be taking leave this afternoon (2026-09-14).
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 仅在 2026-09-14 13:00 至 18:00 休假 | `<部分成立>` | `<【AI·中】hit「taking leave this afternoon (2026-09-14)」保留日期与下午限定，但丢失13:00至18:00的具体时间范围。>` |
| 2 | forbidden | 用户长期处于休假状态 | `<未出现>` | `<【AI·高】hit仅记「taking leave this afternoon (2026-09-14)」，限定当天下午，未断言长期休假。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- ⚠ 检出英文 episode：默认提示词含强制语言一致规则，此为共享 LLM 违规（能力发现），评审时记录对 token/命题判定的影响。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 T03：显式临时时间窗口

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[t03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T16:00:00+08:00）：「2026-09-14 17:00 至 18:00 临时要求所有草稿标注 DRAFT。」
- search[t03-q1]（U1）：「临时草稿规则的有效窗口是什么？」 机械检查：required_tokens=['DRAFT']，source_check=any 期望 ['t03-m1']

**写入回执核对**（机械证据）：
- write[t03-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.5933 source_refs=['t03-session'] 语言=中英混合
2026-09-14 08:00 UTC，U1发出临时指令，要求在2026-09-14 17:00 UTC至18:00 UTC期间，所有草稿必须标注为“DRAFT”。
U1要求2026-09-14特定时段草稿标注DRAFT
2026-09-14 08:00 UTC，U1发出临时指令，要求在2026-09-14 17:00 UTC至18:00 UTC期间，所有草稿必须标注为“DRAFT”。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 规则仅在指定一小时生效 | `<成立>` | `<【AI·高】hit明确「临时指令，要求在2026-09-14 17:00 UTC至18:00 UTC期间」，忠实表达规则仅在指定一小时生效。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 T04：无截止时间的长期要求

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[t04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T16:10:00+08:00）：「技术方案长期默认使用 Python。」
- search[t04-q1]（U1）：「长期默认技术语言是什么？」 机械检查：required_tokens=['Python']，source_check=any 期望 ['t04-m1']

**写入回执核对**（机械证据）：
- write[t04-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.6702 source_refs=['t04-session'] 语言=中英混合
2026-09-14 08:10 UTC，U1指出技术方案长期默认使用Python。
U1确认技术方案长期默认使用Python
2026-09-14 08:10 UTC，U1指出技术方案长期默认使用Python。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 长期要求仍为 Python | `<成立>` | `<【AI·高】hit「U1指出技术方案长期默认使用Python」，忠实表达长期要求仍为Python。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 T05：计划不能推断为完成

**自动判分结果**：FAIL；hard_failures：no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[t05-w1]（U1，scope=project/P1，occurred_at=2026-09-14T16:20:00+08:00）：「P1 计划在 10 月底交付。」
- search[t05-q1]（U1）：「P1 是否已经完成交付？」 机械检查：required_tokens=['计划']，source_check=any 期望 ['t05-m1']

**写入回执核对**（机械证据）：
- write[t05-w1]（U1）：PASS，processed=True（add=accumulated → flush=extracted）

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.7041 source_refs=['t05-session'] 语言=中文
2026-09-14 08:20 UTC，U1指出P1计划在10月底（2026-10-31）交付。
U1确认P1项目计划于10月底交付
2026-09-14 08:20 UTC，U1指出P1计划在10月底（2026-10-31）交付。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 只是计划在 10 月底交付 | `<成立>` | `<【AI·高】hit「P1计划在10月底（2026-10-31）交付」「计划于10月底交付」，忠实保留仅为计划、未完成的语义。>` |
| 2 | forbidden | P1 已经完成交付 | `<未出现>` | `<【AI·高】hit仅称「P1计划在10月底（2026-10-31）交付」，为计划表述，未正面断言已完成交付。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 E01：正向限流案例保真

**自动判分结果**：UNSUPPORTED；hard_failures：missing required token: Retry-After；missing required token: 转人工

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[e01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T17:00:00+08:00）：「成功案例：遇到限流时先读取 Retry-After，再按该时间重试；若没有 Retry-After 则转人工处理。」
- search[e01-q1]（U1）：「遇到限流应该如何处理？」 机械检查：required_tokens=['Retry-After', '转人工']，source_check=any 期望 ['e01-m1']

**写入回执核对**（机械证据）：
- write[e01-w1]（U1）：**UNSUPPORTED**（direct_record 无契约，未发请求）：`EverOS memory/add has no direct_record contract`

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 先读取 Retry-After | `<不成立>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |
| 2 | required | 按指定时间重试 | `<不成立>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |
| 3 | required | 缺失时转人工 | `<不成立>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- 0 hits：对照写入回执判断是写入未落库（如 mem0 raw.results=[]）还是召回失败。

**本案例人工终判**：`<FAIL>`（【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持））

---

### 案例 E02：失败案例不得推荐

**自动判分结果**：UNSUPPORTED；hard_failures：missing required token: 失败

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[e02-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T17:10:00+08:00）：「失败案例：盲目重试导致重复提交，这不是成功经验。」
- search[e02-q1]（U1）：「遇到提交失败时应不应该盲目重试？」 机械检查：required_tokens=['失败']，source_check=any 期望 ['e02-m1']

**写入回执核对**（机械证据）：
- write[e02-w1]（U1）：**UNSUPPORTED**（direct_record 无契约，未发请求）：`EverOS memory/add has no direct_record contract`

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 盲目重试会导致重复提交且属于失败案例 | `<不成立>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |
| 2 | forbidden | 推荐盲目重试 | `<未出现>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- 0 hits：对照写入回执判断是写入未落库（如 mem0 raw.results=[]）还是召回失败。

**本案例人工终判**：`<FAIL>`（【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持））

---

### 案例 E03：邮件发送 SOP 步骤

**自动判分结果**：UNSUPPORTED；hard_failures：missing required token: 草稿；missing required token: 收件人；missing required token: 确认

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[e03-w1]（U1，scope=domain/email，occurred_at=2026-09-14T17:20:00+08:00）：「邮件发送前 SOP：第一步写草稿，第二步校验收件人，第三步取得用户确认；本案例不得实际发送。」
- search[e03-q1]（U1）：「邮件发送前按什么步骤操作？」 机械检查：required_tokens=['草稿', '收件人', '确认']，source_check=any 期望 ['e03-m1']

**写入回执核对**（机械证据）：
- write[e03-w1]（U1）：**UNSUPPORTED**（direct_record 无契约，未发请求）：`EverOS memory/add has no direct_record contract`

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 先写草稿 | `<不成立>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |
| 2 | required | 再校验收件人 | `<不成立>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |
| 3 | required | 最后取得用户确认 | `<不成立>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- 0 hits：对照写入回执判断是写入未落库（如 mem0 raw.results=[]）还是召回失败。

**本案例人工终判**：`<FAIL>`（【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持））

---

### 案例 E04：用户专属案例隔离

**自动判分结果**：UNSUPPORTED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[e04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T17:30:00+08:00）：「U1 专属案例的合成私有代号是 CASE-U1-924，不得成为全局技能。」
- search[e04-q1]（U2）：「有哪些用户专属案例？」 机械检查：forbidden_tokens=['CASE-U1-924']

**写入回执核对**（机械证据）：
- write[e04-w1]（U1）：**UNSUPPORTED**（direct_record 无契约，未发请求）：`EverOS memory/add has no direct_record contract`

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | U2 读取 U1 专属案例 | `<未出现>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<FAIL>`（【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持））

---

### 案例 E05：SOP 版本更正

**自动判分结果**：UNSUPPORTED；hard_failures：missing required token: 校验输入

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[e05-w1]（U1，scope=domain/email，occurred_at=2026-09-14T17:40:00+08:00）：「SOP v1：先生成内容后检查输入。」
- write[e05-w2]（U1，scope=domain/email，occurred_at=2026-09-14T17:50:00+08:00）：「更正为 SOP v2：先校验输入，再生成内容。」
- search[e05-q1]（U1）：「当前 SOP 的正确步骤是什么？」 机械检查：required_tokens=['校验输入']，source_check=any 期望 ['e05-m2']

**写入回执核对**（机械证据）：
- write[e05-w1]（U1）：**UNSUPPORTED**（direct_record 无契约，未发请求）：`EverOS memory/add has no direct_record contract`
- write[e05-w2]（U1）：**UNSUPPORTED**（direct_record 无契约，未发请求）：`EverOS memory/add has no direct_record contract`

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 当前采用 v2 且先校验输入再生成 | `<不成立>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |
| 2 | forbidden | 当前仍先生成后检查 | `<未出现>` | `<【AI·高】0 hits——候选未返回任何内容；含候选自产 md 补充证据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。
- 0 hits：对照写入回执判断是写入未落库（如 mem0 raw.results=[]）还是召回失败。

**本案例人工终判**：`<FAIL>`（【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持））

## FAIL / UNSUPPORTED 归因复核

| case_id | 归因类别 | 证据 | 结论 |
|---|---|---|---|
| F01 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['f01-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| F02 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['f02-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| F03 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['f03-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| F04 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['f04-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| F05 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['f05-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| U01 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['u01-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| U01 | 能力层·语言合规 | missing required token: 详细；hit 文本为英文——缺失 token 疑以英文 hit 表述（如「上海」→"moved to Shanghai"）；默认提示词含强制语言一致规则，属共享 LLM 违规；R1 伴随跨语言 rerank 分数坍缩 | 维持 FAIL（记入能力矩阵：中文业务召回不稳定） |
| U03 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['shared-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| U04 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['u04-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| D01 | 能力层·索引完整性（跨空间 episode id 冲突） | missing required token: 简洁；attempt1 命中 1 条后全部归零（曲线 [1, 0, 0, 0, 0]…）；同 session 写入 2 个空间（domain/email、domain/report）；各空间 episode 序号独立计数致同名 ep_<date>_00000001，而共享 LanceDB episode 表主键 {user}_ep_{date}_{seq} 不含空间成分，后完成空间的 cascade upsert 覆盖先前空间的索引行（markdown 事实源完好；索引终态可在 runtime/<run>/.index/lancedb 复核） | 维持 FAIL（记入能力矩阵：同用户多空间场景索引行被覆盖，提取与空间路由本身正确） |
| D03 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['d03-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| D04 | 能力层·索引完整性（跨空间 episode id 冲突） | missing required token: 详细；attempt1 命中 1 条后全部归零（曲线 [1, 0, 0, 0, 0]…）；同 session 写入 2 个空间（domain/email、domain/report）；各空间 episode 序号独立计数致同名 ep_<date>_00000001，而共享 LanceDB episode 表主键 {user}_ep_{date}_{seq} 不含空间成分，后完成空间的 cascade upsert 覆盖先前空间的索引行（markdown 事实源完好；索引终态可在 runtime/<run>/.index/lancedb 复核） | 维持 FAIL（记入能力矩阵：同用户多空间场景索引行被覆盖，提取与空间路由本身正确） |
| D05 | 契约缺口 | write=UNSUPPORTED：memory/add 无 direct_record 对应契约（设计预期） | 维持 UNSUPPORTED（非运行故障） |
| P01 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['p01-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| P02 | 能力层·索引完整性（跨空间 episode id 冲突） | missing required token: 邮件；attempt1 命中 1 条后全部归零（曲线 [1, 0, 0, 0, 0]…）；同 session 写入 2 个空间（project/P1、project/P2）；各空间 episode 序号独立计数致同名 ep_<date>_00000001，而共享 LanceDB episode 表主键 {user}_ep_{date}_{seq} 不含空间成分，后完成空间的 cascade upsert 覆盖先前空间的索引行（markdown 事实源完好；索引终态可在 runtime/<run>/.index/lancedb 复核） | 维持 FAIL（记入能力矩阵：同用户多空间场景索引行被覆盖，提取与空间路由本身正确） |
| P03 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['P03-S1']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| P05 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['task-T1']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| C01 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['c01-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| C01 | 能力层·语言合规 | missing required token: 风景；hit 语言混杂（中文,英文）——缺失 token 疑以英文 hit 表述（如「上海」→"moved to Shanghai"）；默认提示词含强制语言一致规则，属共享 LLM 违规；R1 伴随跨语言 rerank 分数坍缩 | 维持 FAIL（记入能力矩阵：中文业务召回不稳定） |
| C02 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['c02-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| C02 | 能力层·语言合规 | missing required token: 上海；hit 语言混杂（中文,英文）——缺失 token 疑以英文 hit 表述（如「上海」→"moved to Shanghai"）；默认提示词含强制语言一致规则，属共享 LLM 违规；R1 伴随跨语言 rerank 分数坍缩 | 维持 FAIL（记入能力矩阵：中文业务召回不稳定） |
| C03 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['c03-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| C04 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['c04-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| C05 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['c05-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| C05 | 能力层·语言合规 | missing required token: 联调；hit 语言混杂（中文,英文）——缺失 token 疑以英文 hit 表述（如「上海」→"moved to Shanghai"）；默认提示词含强制语言一致规则，属共享 LLM 违规；R1 伴随跨语言 rerank 分数坍缩 | 维持 FAIL（记入能力矩阵：中文业务召回不稳定） |
| T01 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['t01-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| T01 | 能力层·语言合规 | missing required token: 上海；hit 语言混杂（中文,英文）——缺失 token 疑以英文 hit 表述（如「上海」→"moved to Shanghai"）；默认提示词含强制语言一致规则，属共享 LLM 违规；R1 伴随跨语言 rerank 分数坍缩 | 维持 FAIL（记入能力矩阵：中文业务召回不稳定） |
| T02 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['t02-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| T02 | 能力层·语言合规 | missing required token: 休假；hit 文本为英文——缺失 token 疑以英文 hit 表述（如「上海」→"moved to Shanghai"）；默认提示词含强制语言一致规则，属共享 LLM 违规；R1 伴随跨语言 rerank 分数坍缩 | 维持 FAIL（记入能力矩阵：中文业务召回不稳定） |
| T03 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['t03-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| T04 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['t04-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| T05 | 能力层·来源粒度（D 类缺口） | hard_failures 含来源检查失败；hits[].source_refs=['t05-session']（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判） | 维持 FAIL（已记录 D 类缺口） |
| E01 | 契约缺口 | write=UNSUPPORTED：memory/add 无 direct_record 对应契约（设计预期） | 维持 UNSUPPORTED（非运行故障） |
| E02 | 契约缺口 | write=UNSUPPORTED：memory/add 无 direct_record 对应契约（设计预期） | 维持 UNSUPPORTED（非运行故障） |
| E03 | 契约缺口 | write=UNSUPPORTED：memory/add 无 direct_record 对应契约（设计预期） | 维持 UNSUPPORTED（非运行故障） |
| E04 | 契约缺口 | write=UNSUPPORTED：memory/add 无 direct_record 对应契约（设计预期） | 维持 UNSUPPORTED（非运行故障） |
| E05 | 契约缺口 | write=UNSUPPORTED：memory/add 无 direct_record 对应契约（设计预期） | 维持 UNSUPPORTED（非运行故障） |

## 汇总

| case_id | 自动状态 | Agent 自动终判 | 备注 |
|---|---|---|---|
| F01 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| F02 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| F03 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| F04 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| F05 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| N01 | REVIEW_REQUIRED | `PASS` | 【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核） |
| N02 | REVIEW_REQUIRED | `PASS` | 【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核） |
| N03 | REVIEW_REQUIRED | `PASS` | 【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核） |
| N04 | REVIEW_REQUIRED | `PASS` | 【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核） |
| N05 | REVIEW_REQUIRED | `PASS` | 【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核） |
| U01 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| U02 | REVIEW_REQUIRED | `FAIL` | 【AI·中】语义判定未全满足：#1forbidden=出现 |
| U03 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| U04 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| U05 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| D01 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| D02 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| D03 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| D04 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| D05 | UNSUPPORTED | `FAIL` | 【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持） |
| P01 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| P02 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| P03 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| P04 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| P05 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| C01 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| C02 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| C03 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| C04 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| C05 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| T01 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| T02 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| T03 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| T04 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| T05 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| E01 | UNSUPPORTED | `FAIL` | 【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持） |
| E02 | UNSUPPORTED | `FAIL` | 【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持） |
| E03 | UNSUPPORTED | `FAIL` | 【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持） |
| E04 | UNSUPPORTED | `FAIL` | 【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持） |
| E05 | UNSUPPORTED | `FAIL` | 【机】维持自动状态：契约缺口（UNSUPPORTED，能力不支持） |

**预填披露**：本文件的逐命题判定、理由与终判建议由 `scripts/prefill_verdicts.py`
（机械层）与 LLM 语义判定（标记【AI·置信度】）预填，跨轨道相同判定单元已复用
（标记【复】）；判定输入仅为候选实际返回的 hits[].text（everos 单次 0 hits 负例
另附候选自产 runtime markdown 补充证据），未引入候选未暴露的 harness 侧信息。
预填仅为建议：评审人须按「预填导航」逐条复核并确认或改判（确认后去掉
尖括号与标记）；当前终判仍为 Agent 自动建议，人工签名未提供。

**自动评估声明**：本文件的终判由 Agent 根据候选实际返回内容与运行证据生成；
候选自产 runtime markdown 仅用于说明写入或索引状态，不能替代检索命中。
原始机械状态保留在对应 `case_results.json` 中，便于核对自动语义修正。

人工签名：未签署。
