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
| run_id | `20260915T075013Z-mem0-r1-full-5ec2c317` |
| 候选 / 轨道 / 套件 | mem0 / r1 / full |
| 运行时间 | 2026-09-15T07:50:13.657143+00:00 → 2026-09-15T08:07:22.770762+00:00（status=FAIL） |
| 评估主体 | Agent 自动评估（未人工复核） |
| 人工复核状态 | 未进行 |
| 证据路径 | `artifacts/20260915T075013Z-mem0-r1-full-5ec2c317/case_results.json` |
| 输入指纹 | case_data_hash=`ef7ff5096fd8` config_hash=`27df7b45d308` |

## 评审范围

- REVIEW_REQUIRED：F01, F02, F03, F05, N01, N02, N04, N05, U01, U02, U03, U04, U05, D02, D05, P01, P03, P04, P05, C01, C02, C03, C04, C05, T02, T03, T04, T05, E01, E02, E03, E04, E05
- FAIL（需归因复核）：F04, N03, D01, D03, D04, P02, T01
- UNSUPPORTED：无

## 预填导航（脚本+LLM 预填，供人工复核）

判定来源统计：AI 语义判定 28 条，复用（mem0-r0 已填同款单元）20 条，机械层 15 条（0 hits 7／隔离负例 0／字面全包含 8），终判建议 40 条。
标记说明：【AI·高/中/低】LLM 语义判定及置信度；【机·…】机械可证；【复·…】跨文件复用同款判定。所有预填均为建议，人工确认后请去掉尖括号 `<>`；改判直接覆盖并删标记。

**建议复核顺序**：先看下面 8 个重点案例，再抽查高置信度条目。

- C05 #2（forbidden「P1 同时处于设计、开发和联调」→ 出现：forbidden 判为出现）
- C05（REVIEW_REQUIRED → 建议改判 FAIL：语义判定未全满足：#2forbidden=出现）
- C05（终判含中/低置信度命题，请重点复核）
- T02 #1（required「仅在 2026-09-14 13:00 至 18」→ 部分成立：部分成立）
- T02（REVIEW_REQUIRED → 建议改判 FAIL：语义判定未全满足：#1required=部分成立）
- T02（终判含中/低置信度命题，请重点复核）
- T03 #1（required「规则仅在指定一小时生效」→ 成立：中置信度）
- T03（终判含中/低置信度命题，请重点复核）
- 归因表尚有 1 处 `<评审人填写>` 结论未预填（需人工）


## 运行级机械观察（脚本自动生成，评审导航用）

**提取跳过的 conversation 写入（write PASS 但 raw.results=[]），共 10 处**。
根因三分：① 跨案例/跨作用域语义去重（疑源列出）；② 提取遗漏；
③ 边缘等价判定漂移（写路径非确定性——与另一轨道 run 对照，不一致即属此类）。
去重机制：mem0 提取前的重复检索仅按 user_id 过滤，无视 namespace/domain/
project metadata，且 last-messages 上下文跨案例共享（experiment-design 隔离映射）。

| case[request] | 案例状态 | 未落库消息 | 初判分类与疑源 |
|---|---|---|---|
| F04[f04-w1] | FAIL | 「对外发送前必须先让我确认。」 | 确证提取遗漏（非去重）：无前序等价记忆（「对外发送前确认」主题首次出现），R0/R1 双轨稳定复现——提取召回缺陷 |
| N05[n05-w1] | REVIEW_REQUIRED | 「这一次回答短一点。」 | 案例非 FAIL（写入被跳过但未触发机械失败；负例属期望行为，非负例仍须核对语义命题）；无字面重叠疑源：提取遗漏或弱语义等价漂移（字符串不可复现的 LLM 判定）——对照另一轨道 run 的同名写入，不一致即为写路径非确定性 |
| U01[u01-w1] | REVIEW_REQUIRED | 「我喜欢简洁回答。」 | 案例非 FAIL（写入被跳过但未触发机械失败；负例属期望行为，非负例仍须核对语义命题）；弱语义等价漂移：疑与 F03「邮件回复尽量简洁」被判等价（full R0 存、R1 丢；字面重叠低，推断检不出）——写路径非确定性实例 |
| D01[d01-w1] | FAIL | 「邮件回复要简洁。」 | 疑被前序记忆去重吞噬：F03「用户希望邮件回复尽量简洁」重叠0.67；F05「用户负责统一记忆项目 P1，要求邮件回复尽量简洁，且」重叠0.67（去重仅按 user_id，无视 domain/project/namespace metadata） |
| D03[d03-w1] | FAIL | 「我是 P1 负责人。」 | 疑被前序记忆去重吞噬：F01「用户负责统一记忆项目 P1」重叠0.33；F02「用户负责的统一记忆项目 P1 的技术方案默认使用 P」重叠0.33；F05「用户负责统一记忆项目 P1，要求邮件回复尽量简洁，且」重叠0.33（去重仅按 user_id，无视 domain/project/namespace metadata） |
| D04[d04-w1] | FAIL | 「邮件规则是简洁。」 | 疑被前序记忆去重吞噬：F03「用户希望邮件回复尽量简洁」重叠0.33；F05「用户负责统一记忆项目 P1，要求邮件回复尽量简洁，且」重叠0.33；D01「用户要求报告内容必须详细，这与之前要求的邮件回复简洁」重叠0.33（去重仅按 user_id，无视 domain/project/namespace metadata） |
| D04[d04-w2] | FAIL | 「报告规则是详细。」 | 疑被前序记忆去重吞噬：D01「用户要求报告内容必须详细，这与之前要求的邮件回复简洁」重叠0.33（去重仅按 user_id，无视 domain/project/namespace metadata） |
| P02[p02-w1] | FAIL | 「P1 先接邮件。」 | 确证去重来源：P01「P1 项目决定优先接入 Email Agent」——跨语言等价（邮件↔Email Agent），字面重叠推断检不出；P01/P02 属不同 project 命名空间仍被吞噬 |
| C02[c02-w1] | REVIEW_REQUIRED | 「我现居北京。」 | 案例非 FAIL（写入被跳过但未触发机械失败；负例属期望行为，非负例仍须核对语义命题）；疑被前序记忆去重吞噬：U04「用户现居北京」重叠0.75（去重仅按 user_id，无视 domain/project/namespace metadata） |
| T01[t01-w1] | FAIL | 「我已搬到上海。」 | 疑被前序记忆去重吞噬：C02「用户已搬到上海居住，更新了之前的居住地信息」重叠0.80（去重仅按 user_id，无视 domain/project/namespace metadata） |

**『出现禁止 token』FAIL：N03（负责预算）**——子串判定无法识别否定/更正表述；
若 hit 语义是否认该命题（如「用户明确否认负责预算」包含子串「负责预算」），评审可按语义改判 PASS（理由必填）。


## 逐案例评审

---

### 案例 F01：用户负责项目

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[f01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T09:00:00+08:00）：「我负责统一记忆项目 P1。」
- search[f01-q1]（U1）：「我负责什么项目？」 机械检查：required_tokens=['P1']，source_check=any 期望 ['f01-m1']

**写入回执核对**（机械证据）：
- write[f01-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户负责统一记忆项目 P1」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.7444，dense=0.6249 source_refs=['f01-m1'] 语言=中文
用户负责统一记忆项目 P1
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户负责统一记忆项目 P1 | `<成立>` | `<【复·mem0-r0】用户负责统一记忆项目 P1>` |
| 2 | forbidden | 用户是该项目的高级负责人 | `<未出现>` | `<【复·mem0-r0】用户负责统一记忆项目 P1>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 F02：默认技术语言

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[f02-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T09:10:00+08:00）：「技术方案默认用 Python。」
- search[f02-q1]（U1）：「技术方案默认使用什么语言？」 机械检查：required_tokens=['Python']，source_check=any 期望 ['f02-m1']

**写入回执核对**（机械证据）：
- write[f02-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户负责的统一记忆项目 P1 的技术方案默认使用 Python」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9821，dense=0.7049 source_refs=['f02-m1'] 语言=中文
用户负责的统一记忆项目 P1 的技术方案默认使用 Python
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 技术方案默认使用 Python | `<成立>` | `<【复·mem0-r0】用户负责的统一记忆项目 P1 的技术方案默认使用 Python>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 F03：邮件回复风格

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[f03-w1]（U1，scope=domain/email，occurred_at=2026-09-14T09:20:00+08:00）：「邮件回复尽量简洁。」
- search[f03-q1]（U1）：「我的邮件回复风格是什么？」 机械检查：required_tokens=['简洁']，source_check=any 期望 ['f03-m1']

**写入回执核对**（机械证据）：
- write[f03-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户希望邮件回复尽量简洁」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.8103，dense=0.7820 source_refs=['f03-m1'] 语言=中文
用户希望邮件回复尽量简洁
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 邮件回复应尽量简洁 | `<成立>` | `<【AI·高】hit「用户希望邮件回复尽量简洁」与命题语义一致>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 F04：对外发送确认规则

**自动判分结果**：FAIL；hard_failures：missing required token: 确认

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[f04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T09:30:00+08:00）：「对外发送前必须先让我确认。」
- search[f04-q1]（U1）：「对外发送前有什么长期要求？」 机械检查：required_tokens=['确认']，source_check=any 期望 ['f04-m1']

**写入回执核对**（机械证据）：
- write[f04-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**——确证提取遗漏（非去重）：无前序等价记忆（「对外发送前确认」主题首次出现），R0/R1 双轨稳定复现——提取召回缺陷

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 对外发送前必须由用户确认 | `<不成立>` | `<【复·mem0-r0】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- ⚠ 本案例有写入未落库（write PASS 但 raw.results=[]，分类见写入回执核对）：若缺失 token 在未落库消息中，FAIL 根因在写路径（去重/提取）而非检索能力；检索 0 hits 是下游连带结果。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 F05：同段多事实及逐条来源

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[f05-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T09:40:00+08:00）：「我负责 P1；邮件简洁；报告必须保留指标。」
- search[f05-q1]（U1）：「总结我的项目、邮件风格和报告要求。」 机械检查：required_tokens=['P1', '简洁', '指标']，source_check=per_claim 期望 ['f05-m1']

**写入回执核对**（机械证据）：
- write[f05-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户负责统一记忆项目 P1，要求邮件回复尽量简洁，且报告必须保留指标数据」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.4299，dense=0.6736 source_refs=['f05-m1'] 语言=中文
用户负责统一记忆项目 P1，要求邮件回复尽量简洁，且报告必须保留指标数据
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户负责 P1 | `<成立>` | `<【复·mem0-r0】用户负责统一记忆项目 P1>` |
| 2 | required | 邮件要求简洁 | `<成立>` | `<【复·mem0-r0】要求邮件回复尽量简洁>` |
| 3 | required | 报告必须保留指标 | `<成立>` | `<【复·mem0-r0】且报告必须保留指标数据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 N01：假设不应成为当前事实

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[n01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:00:00+08:00）：「假如以后改用 Java，会有什么影响？」
- search[n01-q1]（U1）：「当前技术语言是什么？」 机械检查：forbidden_tokens=['已经改用 Java']

**写入回执核对**（机械证据）：
- write[n01-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户询问如果将统一记忆项目 P1 的技术方案从默认的 Python 改为 Java，会产生什么影响」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.0087，dense=0.4836 source_refs=['n01-m1'] 语言=中文
用户询问如果将统一记忆项目 P1 的技术方案从默认的 Python 改为 Java，会产生什么影响
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 用户已经改用 Java | `<未出现>` | `<【AI·高】hit「用户询问…从默认的Python改为Java…会产生什么影响」为询问框架，未断言已改用Java>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 N02：第三方偏好不得归属用户

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[n02-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:10:00+08:00）：「同事小林喜欢短邮件。」
- search[n02-q1]（U1）：「我喜欢什么样的邮件？」 机械检查：forbidden_tokens=['U1喜欢短邮件']

**写入回执核对**（机械证据）：
- write[n02-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户的同事小林喜欢简短的邮件」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.8914，dense=0.7462 source_refs=['n02-m1'] 语言=中文
用户的同事小林喜欢简短的邮件
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | U1 喜欢短邮件 | `<未出现>` | `<【复·mem0-r0】用户的同事小林喜欢简短的邮件>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 N03：助手推测被用户否认

**自动判分结果**：FAIL；hard_failures：found forbidden token: 负责预算

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[n03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:20:00+08:00）：「你可能负责预算。」
- write[n03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:21:00+08:00）：「我没有这样说。」
- search[n03-q1]（U1）：「我是否负责预算？」 机械检查：forbidden_tokens=['负责预算']

**写入回执核对**（机械证据）：
- write[n03-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户明确否认负责预算，澄清之前的说法不准确」

**检索尝试曲线**（attempts=12）：hits 序列 [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9500，dense=0.7417 source_refs=['n03-m1', 'n03-m2'] 语言=中文
用户明确否认负责预算，澄清之前的说法不准确
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 用户负责预算 | `<未出现>` | `<【AI·高】hit「用户明确否认负责预算，澄清之前的说法不准确」为否认框架>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- ⚠ hard_failures 含『出现禁止 token』：子串判定无法识别否定/更正表述——若 hit 语义为否认该命题，可人工改判 PASS，理由必填。

**本案例人工终判**：`<PASS>`（自动复核：hit 明确否认用户负责预算；机械 forbidden 子串误判，原始 FAIL 保留）

---

### 案例 N04：引述客户原话不得归属用户

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[n04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:30:00+08:00）：「客户原话是“我常住上海”。」
- search[n04-q1]（U1）：「我常住哪里？」 机械检查：forbidden_tokens=['U1常住上海']

**写入回执核对**（机械证据）：
- write[n04-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户转述客户原话称其常住上海」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9513，dense=0.6469 source_refs=['n04-m1'] 语言=中文
用户转述客户原话称其常住上海
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | U1 常住上海 | `<未出现>` | `<【AI·高】hit「用户转述客户原话称其常住上海」，主语为客户而非U1，未断言U1常住上海>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 N05：单次要求不得晋升长期偏好

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[n05-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:40:00+08:00）：「这一次回答短一点。」
- search[n05-q1]（U1）：「我对所有未来任务有什么长期风格要求？」 机械检查：forbidden_tokens=['所有未来任务']

**写入回执核对**（机械证据）：
- write[n05-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**——案例非 FAIL（写入被跳过但未触发机械失败；负例属期望行为，非负例仍须核对语义命题）；无字面重叠疑源：提取遗漏或弱语义等价漂移（字符串不可复现的 LLM 判定）——对照另一轨道 run 的同名写入，不一致即为写路径非确定性

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 所有未来任务必须简短 | `<未出现>` | `<【复·mem0-r0】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- ⚠ 本案例有写入未落库（write PASS 但 raw.results=[]，分类见写入回执核对）：若缺失 token 在未落库消息中，FAIL 根因在写路径（去重/提取）而非检索能力；检索 0 hits 是下游连带结果。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 U01：两用户偏好隔离

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[u01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T11:00:00+08:00）：「我喜欢简洁回答。」
- write[u01-w2]（U2，scope=user_public/U2，occurred_at=2026-09-14T11:01:00+08:00）：「我喜欢详细回答。」
- search[u01-q1]（U2）：「我喜欢什么回答风格？」 机械检查：required_tokens=['详细']，forbidden_tokens=['简洁']，source_check=any 期望 ['u01-m2']

**写入回执核对**（机械证据）：
- write[u01-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**——案例非 FAIL（写入被跳过但未触发机械失败；负例属期望行为，非负例仍须核对语义命题）；弱语义等价漂移：疑与 F03「邮件回复尽量简洁」被判等价（full R0 存、R1 丢；字面重叠低，推断检不出）——写路径非确定性实例
- write[u01-w2]（U2）：PASS，native_ids=1 条 → ADD:「用户偏好接收详细的回答，而非简短或概括性的回复」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.3245，dense=0.6942 source_refs=['u01-m2'] 语言=中文
用户偏好接收详细的回答，而非简短或概括性的回复
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | U2 喜欢详细回答 | `<成立>` | `<【复·mem0-r0】用户偏好接收详细的回答，而非简短或概括性的回复>` |
| 2 | forbidden | U2 喜欢简洁回答 | `<未出现>` | `<【复·mem0-r0】用户偏好接收详细的回答，而非简短或概括性的回复>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- ⚠ 本案例有写入未落库（write PASS 但 raw.results=[]，分类见写入回执核对）：若缺失 token 在未落库消息中，FAIL 根因在写路径（去重/提取）而非检索能力；检索 0 hits 是下游连带结果。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 U02：同名项目跨用户隔离

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[u02-w1]（U1，scope=project/P1，occurred_at=2026-09-14T11:10:00+08:00）：「P1 决定采用蓝色发布。」
- search[u02-q1]（U2）：「P1 采用什么发布策略？」 机械检查：forbidden_tokens=['蓝色发布']

**写入回执核对**（机械证据）：
- write[u02-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户决定统一记忆项目 P1 采用蓝色发布策略」

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | U2 的 P1 采用蓝色发布 | `<未出现>` | `<【复·mem0-r0】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 U03：相同会话标识不混用户

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[u03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T11:20:00+08:00）：「我负责架构。」
- write[u03-w2]（U2，scope=user_public/U2，occurred_at=2026-09-14T11:21:00+08:00）：「我负责测试。」
- search[u03-q1]（U1）：「我负责什么？」 机械检查：required_tokens=['架构']，forbidden_tokens=['测试']，source_check=any 期望 ['u03-m1']

**写入回执核对**（机械证据）：
- write[u03-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户负责统一记忆项目 P1 的架构工作」
- write[u03-w2]（U2）：PASS，native_ids=1 条 → ADD:「用户负责测试工作」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.0929，dense=0.5557 source_refs=['u03-m1'] 语言=中文
用户负责统一记忆项目 P1 的架构工作
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | U1 负责架构 | `<成立>` | `<【复·mem0-r0】用户负责统一记忆项目 P1 的架构工作>` |
| 2 | forbidden | U1 负责测试 | `<未出现>` | `<【复·mem0-r0】用户负责统一记忆项目 P1 的架构工作>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 U04：更新不得跨用户

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[u04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T11:30:00+08:00）：「我现居北京。」
- write[u04-w2]（U2，scope=user_public/U2，occurred_at=2026-09-14T11:31:00+08:00）：「我现居北京。」
- write[u04-w3]（U2，scope=user_public/U2，occurred_at=2026-09-14T11:32:00+08:00）：「我已搬到上海。」
- search[u04-q1]（U1）：「我现在住在哪里？」 机械检查：required_tokens=['北京']，forbidden_tokens=['上海']，source_check=any 期望 ['u04-m1']

**写入回执核对**（机械证据）：
- write[u04-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户现居北京」
- write[u04-w2]（U2）：PASS，native_ids=1 条 → ADD:「用户现居北京。」
- write[u04-w3]（U2）：PASS，native_ids=1 条 → ADD:「用户已搬到上海居住，不再住在北京。」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.4086，dense=0.6797 source_refs=['u04-m1'] 语言=中文
用户现居北京
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | U1 仍居住北京 | `<成立>` | `<【复·mem0-r0】用户现居北京>` |
| 2 | forbidden | U1 已搬到上海 | `<未出现>` | `<【复·mem0-r0】用户现居北京>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 U05：缺失或伪造身份

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[u05-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T11:40:00+08:00）：「我的私有校验码是 USER-U1-805。」
- search[u05-q1]（None）：「U1 的私有校验码是什么？」 机械检查：forbidden_tokens=['USER-U1-805']

**写入回执核对**（机械证据）：
- write[u05-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户的私有校验码是 USER-U1-805」

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 未认证调用者读取 U1 数据 | `<未出现>` | `<【复·mem0-r0】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 D01：业务偏好隔离

**自动判分结果**：FAIL；hard_failures：missing required token: 简洁

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[d01-w1]（U1，scope=domain/email，occurred_at=2026-09-14T12:00:00+08:00）：「邮件回复要简洁。」
- write[d01-w2]（U1，scope=domain/report，occurred_at=2026-09-14T12:01:00+08:00）：「报告要详细。」
- search[d01-q1]（U1）：「当前业务的表达要求是什么？」 机械检查：required_tokens=['简洁']，forbidden_tokens=['报告要详细']，source_check=any 期望 ['d01-m1']

**写入回执核对**（机械证据）：
- write[d01-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**——疑被前序记忆去重吞噬：F03「用户希望邮件回复尽量简洁」重叠0.67；F05「用户负责统一记忆项目 P1，要求邮件回复尽量简洁，且」重叠0.67（去重仅按 user_id，无视 domain/project/namespace metadata）
- write[d01-w2]（U1）：PASS，native_ids=1 条 → ADD:「用户要求报告内容必须详细，这与之前要求的邮件回复简洁形成对比，表明用户对不同沟通场景有明确的详略偏好」

**检索尝试曲线**（attempts=11）：hits 序列 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 邮件要求简洁 | `<不成立>` | `<【复·mem0-r0】0 hits——候选未返回任何内容>` |
| 2 | forbidden | 邮件要求详细 | `<未出现>` | `<【复·mem0-r0】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- ⚠ 本案例有写入未落库（write PASS 但 raw.results=[]，分类见写入回执核对）：若缺失 token 在未落库消息中，FAIL 根因在写路径（去重/提取）而非检索能力；检索 0 hits 是下游连带结果。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 D02：私有业务代号不泄漏

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[d02-w1]（U1，scope=domain/email，occurred_at=2026-09-14T12:10:00+08:00）：「邮件审核代号是 MAIL-ONLY-731。」
- search[d02-q1]（U1）：「有哪些审核代号？」 机械检查：forbidden_tokens=['MAIL-ONLY-731']

**写入回执核对**（机械证据）：
- write[d02-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户的邮件审核代号是 MAIL-ONLY-731」

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 报告业务读取邮件私有代号 | `<未出现>` | `<【复·mem0-r0】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 D03：公共职责跨业务可见

**自动判分结果**：FAIL；hard_failures：missing required token: P1

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[d03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T12:20:00+08:00）：「我是 P1 负责人。」
- search[d03-q1]（U1）：「我的公共职责是什么？」 机械检查：required_tokens=['P1']，source_check=any 期望 ['d03-m1']

**写入回执核对**（机械证据）：
- write[d03-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**——疑被前序记忆去重吞噬：F01「用户负责统一记忆项目 P1」重叠0.33；F02「用户负责的统一记忆项目 P1 的技术方案默认使用 P」重叠0.33；F05「用户负责统一记忆项目 P1，要求邮件回复尽量简洁，且」重叠0.33（去重仅按 user_id，无视 domain/project/namespace metadata）

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户是 P1 负责人 | `<不成立>` | `<【机·0hits】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- ⚠ 本案例有写入未落库（write PASS 但 raw.results=[]，分类见写入回执核对）：若缺失 token 在未落库消息中，FAIL 根因在写路径（去重/提取）而非检索能力；检索 0 hits 是下游连带结果。

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
- write[d04-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**——疑被前序记忆去重吞噬：F03「用户希望邮件回复尽量简洁」重叠0.33；F05「用户负责统一记忆项目 P1，要求邮件回复尽量简洁，且」重叠0.33；D01「用户要求报告内容必须详细，这与之前要求的邮件回复简洁」重叠0.33（去重仅按 user_id，无视 domain/project/namespace metadata）
- write[d04-w2]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**——疑被前序记忆去重吞噬：D01「用户要求报告内容必须详细，这与之前要求的邮件回复简洁」重叠0.33（去重仅按 user_id，无视 domain/project/namespace metadata）
- write[d04-w3]（U1）：PASS，native_ids=1 条 → ADD:「用户更新了沟通偏好，要求邮件回复也需要包含细节，不再保持之前的简洁风格」

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 报告规则仍为详细 | `<不成立>` | `<【机·0hits】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- ⚠ 本案例有写入未落库（write PASS 但 raw.results=[]，分类见写入回执核对）：若缺失 token 在未落库消息中，FAIL 根因在写路径（去重/提取）而非检索能力；检索 0 hits 是下游连带结果。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 D05：Agent 私有案例隔离

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[d05-w1]（U1，scope=agent_private/email_agent，occurred_at=2026-09-14T12:40:00+08:00）：「Email Agent 私有案例标识 AGENT-A-515。」
- search[d05-q1]（U1）：「有哪些 Agent 私有案例？」 机械检查：forbidden_tokens=['AGENT-A-515']

**写入回执核对**（机械证据）：
- write[d05-w1]（U1）：PASS，native_ids=1 条 → ADD:「Email Agent 私有案例标识 AGENT-A-515。」

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 未授权 Agent 读取私有案例 | `<未出现>` | `<【机·0hits】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 P01：项目决策跨业务延续

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p01-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:00:00+08:00）：「P1 决定先接 Email Agent。」
- search[p01-q1]（U1）：「P1 决定先接哪个 Agent？」 机械检查：required_tokens=['Email Agent']，source_check=any 期望 ['p01-m1']

**写入回执核对**（机械证据）：
- write[p01-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户负责的 P1 项目决定优先接入 Email Agent」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9961，dense=0.7524 source_refs=['p01-m1'] 语言=中英混合
用户负责的 P1 项目决定优先接入 Email Agent
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 先接 Email Agent | `<成立>` | `<【机·字面全包含】字面全包含：hit「用户负责的 P1 项目决定优先接入 Email Agent」覆盖命题全部实词字符>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 P02：同用户多项目隔离

**自动判分结果**：FAIL；hard_failures：missing required token: 邮件

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p02-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:10:00+08:00）：「P1 先接邮件。」
- write[p02-w2]（U1，scope=project/P2，occurred_at=2026-09-14T13:11:00+08:00）：「P2 先接日程。」
- search[p02-q1]（U1）：「P1 的接入顺序是什么？」 机械检查：required_tokens=['邮件']，forbidden_tokens=['P2']，source_check=any 期望 ['p02-m1']

**写入回执核对**（机械证据）：
- write[p02-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**——确证去重来源：P01「P1 项目决定优先接入 Email Agent」——跨语言等价（邮件↔Email Agent），字面重叠推断检不出；P01/P02 属不同 project 命名空间仍被吞噬
- write[p02-w2]（U1）：PASS，native_ids=1 条 → ADD:「用户负责的 P2 项目决定优先接入日程功能」

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 先接邮件 | `<不成立>` | `<【机·0hits】0 hits——候选未返回任何内容>` |
| 2 | forbidden | P1 先接日程 | `<未出现>` | `<【机·0hits】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- ⚠ 本案例有写入未落库（write PASS 但 raw.results=[]，分类见写入回执核对）：若缺失 token 在未落库消息中，FAIL 根因在写路径（去重/提取）而非检索能力；检索 0 hits 是下游连带结果。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 P03：项目记忆跨会话

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p03-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:20:00+08:00）：「P1 范围只包含记忆服务验证。」
- search[p03-q1]（U1）：「P1 的范围是什么？」 机械检查：required_tokens=['记忆服务验证']，source_check=any 期望 ['p03-m1']

**写入回执核对**（机械证据）：
- write[p03-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户负责的 P1 项目范围限定为仅包含记忆服务验证」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9864，dense=0.6266 source_refs=['p03-m1'] 语言=中文
用户负责的 P1 项目范围限定为仅包含记忆服务验证
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 范围只包含记忆服务验证 | `<成立>` | `<【AI·高】hit「用户负责的P1项目范围限定为仅包含记忆服务验证」忠实表达命题>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 P04：知道项目标识不等于有权限

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p04-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:30:00+08:00）：「P1 私有决策码 PROJECT-P1-404。」
- search[p04-q1]（U1）：「P1 的私有决策码是什么？」 机械检查：forbidden_tokens=['PROJECT-P1-404']

**写入回执核对**（机械证据）：
- write[p04-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户负责的 P1 项目私有决策码为 PROJECT-P1-404」

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 未授权 Agent 读取 P1 | `<未出现>` | `<【机·0hits】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 P05：项目记忆不随任务结束清除

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p05-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:40:00+08:00）：「P1 决定保留项目级来源链，任务 T1 已结束。」
- search[p05-q1]（U1）：「P1 对来源链做了什么决定？」 机械检查：required_tokens=['来源链']，source_check=any 期望 ['p05-m1']

**写入回执核对**（机械证据）：
- write[p05-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户负责的 P1 项目决定保留项目级来源链，且任务 T1 已结束」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9952，dense=0.7207 source_refs=['p05-m1'] 语言=中文
用户负责的 P1 项目决定保留项目级来源链，且任务 T1 已结束
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 决定保留项目级来源链 | `<成立>` | `<【机·字面全包含】字面全包含：hit「用户负责的 P1 项目决定保留项目级来源链，且任务 T1 已结束」覆盖命题全部实词字符>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 C01：非冲突偏好并存

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[c01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:00:00+08:00）：「我喜欢拍人像。」
- write[c01-w2]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:10:00+08:00）：「我现在也喜欢拍风景了。」
- search[c01-q1]（U1）：「我喜欢拍什么题材？」 机械检查：required_tokens=['人像', '风景']，source_check=per_claim 期望 ['c01-m1', 'c01-m2']

**写入回执核对**（机械证据）：
- write[c01-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户喜欢拍摄人像照片」
- write[c01-w2]（U1）：PASS，native_ids=1 条 → ADD:「用户现在也喜欢拍摄风景照片，在原有喜欢拍人像的基础上增加了新的摄影兴趣」

**检索尝试曲线**（attempts=1）：hits 序列 [2]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.5009，dense=0.6501 source_refs=['c01-m1'] 语言=中文
用户喜欢拍摄人像照片
```

```
[hit 2] score=0.3993，dense=0.6091 source_refs=['c01-m2'] 语言=中文
用户现在也喜欢拍摄风景照片，在原有喜欢拍人像的基础上增加了新的摄影兴趣
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户喜欢拍人像 | `<成立>` | `<【机·字面全包含】字面全包含：hit「用户喜欢拍摄人像照片」覆盖命题全部实词字符>` |
| 2 | required | 用户喜欢拍风景 | `<成立>` | `<【机·字面全包含】字面全包含：hit「用户喜欢拍摄人像照片」覆盖命题全部实词字符>` |
| 3 | forbidden | 用户不再喜欢拍人像 | `<未出现>` | `<【AI·高】hit「喜欢拍摄人像照片」「在原有喜欢拍人像的基础上增加新兴趣」，未断言不再喜欢人像。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 C02：当前住址与历史住址

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[c02-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:20:00+08:00）：「我现居北京。」
- write[c02-w2]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:30:00+08:00）：「我已搬到上海。」
- search[c02-q1]（U1）：「我当前住在哪里？」 机械检查：required_tokens=['上海']，source_check=any 期望 ['c02-m2']

**写入回执核对**（机械证据）：
- write[c02-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**——案例非 FAIL（写入被跳过但未触发机械失败；负例属期望行为，非负例仍须核对语义命题）；疑被前序记忆去重吞噬：U04「用户现居北京」重叠0.75（去重仅按 user_id，无视 domain/project/namespace metadata）
- write[c02-w2]（U1）：PASS，native_ids=1 条 → ADD:「用户已搬到上海居住，更新了之前的居住地信息」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.5263，dense=0.6627 source_refs=['c02-m2'] 语言=中文
用户已搬到上海居住，更新了之前的居住地信息
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户当前住在上海 | `<成立>` | `<【AI·高】hit「用户已搬到上海居住」忠实表达当前住上海。>` |
| 2 | forbidden | 用户当前仍住北京 | `<未出现>` | `<【AI·高】hit「已搬到上海居住，更新了之前的居住地信息」为更正框架，未断言仍住北京。>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- ⚠ 本案例有写入未落库（write PASS 但 raw.results=[]，分类见写入回执核对）：若缺失 token 在未落库消息中，FAIL 根因在写路径（去重/提取）而非检索能力；检索 0 hits 是下游连带结果。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 C03：条件化偏好并存

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[c03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:40:00+08:00）：「技术报告要详细，短消息要简洁。」
- search[c03-q1]（U1）：「技术报告和短消息分别应采用什么风格？」 机械检查：required_tokens=['详细', '简洁']，source_check=any 期望 ['c03-m1']

**写入回执核对**（机械证据）：
- write[c03-w1]（U1）：PASS，native_ids=3 条 → ADD:「用户明确了沟通偏好：技术报告需要详细内容，而短消息则保持简洁风格」; ADD:「用户现居上海，已从北京搬离」; ADD:「用户喜欢拍摄人像和风景照片」

**检索尝试曲线**（attempts=1）：hits 序列 [3]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9967，dense=0.8071 source_refs=['c03-m1'] 语言=中文
用户明确了沟通偏好：技术报告需要详细内容，而短消息则保持简洁风格
```

```
[hit 2] score=0.0000，dense=0.3707 source_refs=['c03-m1'] 语言=中文
用户现居上海，已从北京搬离
```

```
[hit 3] score=0.0000，dense=0.4299 source_refs=['c03-m1'] 语言=中文
用户喜欢拍摄人像和风景照片
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 技术报告详细 | `<成立>` | `<【机·字面全包含】字面全包含：hit「用户明确了沟通偏好：技术报告需要详细内容，而短消息则保持简洁风格」覆盖命题全部实词字符>` |
| 2 | required | 短消息简洁 | `<成立>` | `<【机·字面全包含】字面全包含：hit「用户明确了沟通偏好：技术报告需要详细内容，而短消息则保持简洁风格」覆盖命题全部实词字符>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 C04：明确更正

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[c04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:50:00+08:00）：「默认发布策略是 A。」
- write[c04-w2]（U1，scope=user_public/U1，occurred_at=2026-09-14T15:00:00+08:00）：「更正，默认发布策略应该是 B。」
- search[c04-q1]（U1）：「当前默认发布策略是什么？」 机械检查：required_tokens=['B']，source_check=any 期望 ['c04-m2']

**写入回执核对**（机械证据）：
- write[c04-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户将默认发布策略设定为 A」
- write[c04-w2]（U1）：PASS，native_ids=1 条 → ADD:「用户将默认发布策略更正为 B，更新了之前设定的策略 A」

**检索尝试曲线**（attempts=1）：hits 序列 [2]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9309，dense=0.8546 source_refs=['c04-m1'] 语言=中文
用户将默认发布策略设定为 A
```

```
[hit 2] score=0.4396，dense=0.7813 source_refs=['c04-m2'] 语言=中文
用户将默认发布策略更正为 B，更新了之前设定的策略 A
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 当前策略为 B | `<成立>` | `<【AI·高】hit2「将默认发布策略更正为B，更新了之前设定的策略A」忠实表达当前策略为B>` |
| 2 | forbidden | 当前策略为 A | `<未出现>` | `<【AI·高】hit2「更正为B，更新了之前设定的策略A」为更正框架，现状为B，未正面断言当前策略为A>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 C05：项目进度版本链

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[c05-w1]（U1，scope=project/P1，occurred_at=2026-09-14T15:10:00+08:00）：「P1 当前设计中。」
- write[c05-w2]（U1，scope=project/P1，occurred_at=2026-09-14T15:20:00+08:00）：「P1 当前开发中。」
- write[c05-w3]（U1，scope=project/P1，occurred_at=2026-09-14T15:30:00+08:00）：「P1 当前联调中。」
- search[c05-q1]（U1）：「P1 当前进度是什么？」 机械检查：required_tokens=['联调']，source_check=any 期望 ['c05-m3']

**写入回执核对**（机械证据）：
- write[c05-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户负责的统一记忆项目 P1 当前处于设计中阶段」
- write[c05-w2]（U1）：PASS，native_ids=1 条 → ADD:「用户负责的统一记忆项目 P1 当前处于开发中阶段」
- write[c05-w3]（U1）：PASS，native_ids=1 条 → ADD:「用户负责的统一记忆项目 P1 当前处于联调中阶段」

**检索尝试曲线**（attempts=1）：hits 序列 [3]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.2148，dense=0.5096 source_refs=['c05-m2'] 语言=中文
用户负责的统一记忆项目 P1 当前处于开发中阶段
```

```
[hit 2] score=0.1784，dense=0.5008 source_refs=['c05-m1'] 语言=中文
用户负责的统一记忆项目 P1 当前处于设计中阶段
```

```
[hit 3] score=0.1253，dense=0.5060 source_refs=['c05-m3'] 语言=中文
用户负责的统一记忆项目 P1 当前处于联调中阶段
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 当前联调中 | `<成立>` | `<【机·字面全包含】字面全包含：hit「用户负责的统一记忆项目 P1 当前处于开发中阶段」覆盖命题全部实词字符>` |
| 2 | forbidden | P1 同时处于设计、开发和联调 | `<出现>` | `<【AI·中】三条hit均称「当前处于开发中/设计中/联调中阶段」，合并即正面断言三阶段同时为当前状态>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<FAIL>`（【AI·中】语义判定未全满足：#2forbidden=出现）

---

### 案例 T01：来源时间优先于入库顺序

**自动判分结果**：FAIL；hard_failures：missing required token: 上海；no expected native source reference found

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[t01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T16:00:00+08:00）：「我已搬到上海。」
- write[t01-w2]（U1，scope=user_public/U1，occurred_at=2026-08-01T09:00:00+08:00）：「补录旧记录：我住在北京。」
- search[t01-q1]（U1）：「我当前住在哪里？」 机械检查：required_tokens=['上海']，source_check=any 期望 ['t01-m1']

**写入回执核对**（机械证据）：
- write[t01-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**——疑被前序记忆去重吞噬：C02「用户已搬到上海居住，更新了之前的居住地信息」重叠0.80（去重仅按 user_id，无视 domain/project/namespace metadata）
- write[t01-w2]（U1）：PASS，native_ids=1 条 → ADD:「用户补录了一条旧记录，表明其曾经居住在北京」

**检索尝试曲线**（attempts=12）：hits 序列 [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.1288，dense=0.6033 source_refs=['t01-m2'] 语言=中文
用户补录了一条旧记录，表明其曾经居住在北京
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户当前住在上海 | `<不成立>` | `<【AI·高】hit仅称『曾经居住在北京』，未提及当前居住上海>` |
| 2 | forbidden | 旧记录覆盖上海 | `<未出现>` | `<【AI·高】hit称『补录旧记录…曾经居住在北京』，过去时中性框架，未断言覆盖上海>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- ⚠ 本案例有写入未落库（write PASS 但 raw.results=[]，分类见写入回执核对）：若缺失 token 在未落库消息中，FAIL 根因在写路径（去重/提取）而非检索能力；检索 0 hits 是下游连带结果。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 T02：当天下午临时状态

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[t02-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T09:00:00+08:00）：「今天下午休假。」
- search[t02-q1]（U1）：「2026-09-14 下午用户是否休假？」 机械检查：required_tokens=['休假']，source_check=any 期望 ['t02-m1']

**写入回执核对**（机械证据）：
- write[t02-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户于2026年9月15日下午休假」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9738，dense=0.8652 source_refs=['t02-m1'] 语言=中文
用户于2026年9月15日下午休假
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 仅在 2026-09-14 13:00 至 18:00 休假 | `<部分成立>` | `<【AI·中】hit『9月15日下午休假』保留临时下午休假核心，但日期与命题9-14不符，时间限定被改变>` |
| 2 | forbidden | 用户长期处于休假状态 | `<未出现>` | `<【AI·高】hit称『2026年9月15日下午休假』，为具体半日，未断言长期休假>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<FAIL>`（【AI·中】语义判定未全满足：#1required=部分成立）

---

### 案例 T03：显式临时时间窗口

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[t03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T16:00:00+08:00）：「2026-09-14 17:00 至 18:00 临时要求所有草稿标注 DRAFT。」
- search[t03-q1]（U1）：「临时草稿规则的有效窗口是什么？」 机械检查：required_tokens=['DRAFT']，source_check=any 期望 ['t03-m1']

**写入回执核对**（机械证据）：
- write[t03-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户要求在2026年9月14日17:00至18:00期间，所有草稿必须标注为DRAFT」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.2234，dense=0.6241 source_refs=['t03-m1'] 语言=中文
用户要求在2026年9月14日17:00至18:00期间，所有草稿必须标注为DRAFT
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 规则仅在指定一小时生效 | `<成立>` | `<【AI·中】hit『要求在…17:00至18:00期间』将规则限定于该一小时，仅缺显式『临时』措辞>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核））

---

### 案例 T04：无截止时间的长期要求

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[t04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T16:10:00+08:00）：「技术方案长期默认使用 Python。」
- search[t04-q1]（U1）：「长期默认技术语言是什么？」 机械检查：required_tokens=['Python']，source_check=any 期望 ['t04-m1']

**写入回执核对**（机械证据）：
- write[t04-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户确定统一记忆项目 P1 的技术方案长期默认使用 Python」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.8525，dense=0.6607 source_refs=['t04-m1'] 语言=中文
用户确定统一记忆项目 P1 的技术方案长期默认使用 Python
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 长期要求仍为 Python | `<成立>` | `<【AI·高】hit『确定…长期默认使用 Python』与命题语义一致>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 T05：计划不能推断为完成

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[t05-w1]（U1，scope=project/P1，occurred_at=2026-09-14T16:20:00+08:00）：「P1 计划在 10 月底交付。」
- search[t05-q1]（U1）：「P1 是否已经完成交付？」 机械检查：required_tokens=['计划']，source_check=any 期望 ['t05-m1']

**写入回执核对**（机械证据）：
- write[t05-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户负责的统一记忆项目 P1 计划在 2026 年 10 月底交付」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9923，dense=0.6622 source_refs=['t05-m1'] 语言=中文
用户负责的统一记忆项目 P1 计划在 2026 年 10 月底交付
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 只是计划在 10 月底交付 | `<成立>` | `<【AI·高】hit『计划在 2026 年 10 月底交付』保留『计划』限定，忠实于命题>` |
| 2 | forbidden | P1 已经完成交付 | `<未出现>` | `<【AI·高】hit称『计划在 2026 年 10 月底交付』，计划框架，未断言已完成交付>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 E01：正向限流案例保真

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[e01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T17:00:00+08:00）：「成功案例：遇到限流时先读取 Retry-After，再按该时间重试；若没有 Retry-After 则转人工处理。」
- search[e01-q1]（U1）：「遇到限流应该如何处理？」 机械检查：required_tokens=['Retry-After', '转人工']，source_check=any 期望 ['e01-m1']

**写入回执核对**（机械证据）：
- write[e01-w1]（U1）：PASS，native_ids=1 条 → ADD:「成功案例：遇到限流时先读取 Retry-After，再按该时间重试；若没有 Retry-After 则转人工处理。」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9622，dense=0.7782 source_refs=['e01-m1'] 语言=中英混合
成功案例：遇到限流时先读取 Retry-After，再按该时间重试；若没有 Retry-After 则转人工处理。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 先读取 Retry-After | `<成立>` | `<【机·字面全包含】字面全包含：hit「成功案例：遇到限流时先读取 Retry-After，再按该时间重试；若没有 Retry-After 」覆盖命题全部实词字符>` |
| 2 | required | 按指定时间重试 | `<成立>` | `<【AI·高】hit「先读取Retry-After，再按该时间重试」即按指定时间重试，语义忠实>` |
| 3 | required | 缺失时转人工 | `<成立>` | `<【AI·高】hit「若没有Retry-After则转人工处理」忠实表达缺失时转人工>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 E02：失败案例不得推荐

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[e02-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T17:10:00+08:00）：「失败案例：盲目重试导致重复提交，这不是成功经验。」
- search[e02-q1]（U1）：「遇到提交失败时应不应该盲目重试？」 机械检查：required_tokens=['失败']，source_check=any 期望 ['e02-m1']

**写入回执核对**（机械证据）：
- write[e02-w1]（U1）：PASS，native_ids=1 条 → ADD:「失败案例：盲目重试导致重复提交，这不是成功经验。」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9757，dense=0.8553 source_refs=['e02-m1'] 语言=中文
失败案例：盲目重试导致重复提交，这不是成功经验。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 盲目重试会导致重复提交且属于失败案例 | `<成立>` | `<【AI·高】hit「失败案例：盲目重试导致重复提交」完整覆盖导致重复提交且属失败案例>` |
| 2 | forbidden | 推荐盲目重试 | `<未出现>` | `<【AI·高】hit「失败案例：盲目重试导致重复提交，这不是成功经验」为否定框架，未推荐盲目重试>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 E03：邮件发送 SOP 步骤

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[e03-w1]（U1，scope=domain/email，occurred_at=2026-09-14T17:20:00+08:00）：「邮件发送前 SOP：第一步写草稿，第二步校验收件人，第三步取得用户确认；本案例不得实际发送。」
- search[e03-q1]（U1）：「邮件发送前按什么步骤操作？」 机械检查：required_tokens=['草稿', '收件人', '确认']，source_check=any 期望 ['e03-m1']

**写入回执核对**（机械证据）：
- write[e03-w1]（U1）：PASS，native_ids=1 条 → ADD:「邮件发送前 SOP：第一步写草稿，第二步校验收件人，第三步取得用户确认；本案例不得实际发送。」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9870，dense=0.7375 source_refs=['e03-m1'] 语言=中文
邮件发送前 SOP：第一步写草稿，第二步校验收件人，第三步取得用户确认；本案例不得实际发送。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 先写草稿 | `<成立>` | `<【AI·高】hit「第一步写草稿」忠实表达先写草稿>` |
| 2 | required | 再校验收件人 | `<成立>` | `<【AI·高】hit「第二步校验收件人」忠实表达再校验收件人，顺序保留>` |
| 3 | required | 最后取得用户确认 | `<成立>` | `<【AI·高】hit「第三步取得用户确认」为末步，忠实表达最后取得用户确认>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

---

### 案例 E04：用户专属案例隔离

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[e04-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T17:30:00+08:00）：「U1 专属案例的合成私有代号是 CASE-U1-924，不得成为全局技能。」
- search[e04-q1]（U2）：「有哪些用户专属案例？」 机械检查：forbidden_tokens=['CASE-U1-924']

**写入回执核对**（机械证据）：
- write[e04-w1]（U1）：PASS，native_ids=1 条 → ADD:「U1 专属案例的合成私有代号是 CASE-U1-924，不得成为全局技能。」

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | U2 读取 U1 专属案例 | `<未出现>` | `<【机·0hits】0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（【机】全部 required 成立、forbidden 未出现）

---

### 案例 E05：SOP 版本更正

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[e05-w1]（U1，scope=domain/email，occurred_at=2026-09-14T17:40:00+08:00）：「SOP v1：先生成内容后检查输入。」
- write[e05-w2]（U1，scope=domain/email，occurred_at=2026-09-14T17:50:00+08:00）：「更正为 SOP v2：先校验输入，再生成内容。」
- search[e05-q1]（U1）：「当前 SOP 的正确步骤是什么？」 机械检查：required_tokens=['校验输入']，source_check=any 期望 ['e05-m2']

**写入回执核对**（机械证据）：
- write[e05-w1]（U1）：PASS，native_ids=1 条 → ADD:「SOP v1：先生成内容后检查输入。」
- write[e05-w2]（U1）：PASS，native_ids=1 条 → ADD:「更正为 SOP v2：先校验输入，再生成内容。」

**检索尝试曲线**（attempts=1）：hits 序列 [2]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.0118，dense=0.6583 source_refs=['e05-m1'] 语言=中文
SOP v1：先生成内容后检查输入。
```

```
[hit 2] score=0.0088，dense=0.6461 source_refs=['e05-m2'] 语言=中文
更正为 SOP v2：先校验输入，再生成内容。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 当前采用 v2 且先校验输入再生成 | `<成立>` | `<【AI·高】hit2「更正为SOP v2：先校验输入，再生成内容」支持当前采用v2且内容一致>` |
| 2 | forbidden | 当前仍先生成后检查 | `<未出现>` | `<【AI·高】hit2「更正为SOP v2：先校验输入」为更正框架，v1已被更新，未断言当前仍先生成后检查>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（【AI·高】全部 required 成立、forbidden 未出现）

## FAIL / UNSUPPORTED 归因复核

| case_id | 归因类别 | 证据 | 结论 |
|---|---|---|---|
| F04 | 能力层·提取遗漏 | 期望 token「确认」对应的写入消息「对外发送前必须先让我确认。」未落库（f04-w1：write PASS 但 raw.results=[]）；确证提取遗漏（非去重）：无前序等价记忆（「对外发送前确认」主题首次出现），R0/R1 双轨稳定复现——提取召回缺陷 | 维持 FAIL（提取召回缺陷，双轨稳定复现） |
| N03 | 机械判分误报·否定子串 | hit「用户明确否认负责预算，澄清之前的说法不准确」否认了 forbidden 命题；机械检查只识别「负责预算」子串 | 自动语义终判 PASS；原始机械 FAIL 保留供审计 |
| D01 | 能力层·写路径去重越界 | 期望 token「简洁」对应的写入消息「邮件回复要简洁。」未落库（d01-w1：write PASS 但 raw.results=[]）；疑源：F03「用户希望邮件回复尽量简洁」重叠0.67；F05「用户负责统一记忆项目 P1，要求邮件回复尽量简洁，且」重叠0.67；去重仅按 user_id、无视 domain/project/namespace metadata（experiment-design 隔离映射），且结果依赖案例顺序 | 维持 FAIL（记入能力矩阵：metadata 隔离在写路径失效） |
| D03 | 能力层·写路径去重越界 | 期望 token「P1」对应的写入消息「我是 P1 负责人。」未落库（d03-w1：write PASS 但 raw.results=[]）；疑源：F01「用户负责统一记忆项目 P1」重叠0.33；F02「用户负责的统一记忆项目 P1 的技术方案默认使用 P」重叠0.33；F05「用户负责统一记忆项目 P1，要求邮件回复尽量简洁，且」重叠0.33；去重仅按 user_id、无视 domain/project/namespace metadata（experiment-design 隔离映射），且结果依赖案例顺序 | 维持 FAIL（记入能力矩阵：metadata 隔离在写路径失效） |
| D04 | 能力层·写路径去重越界 | 期望 token「详细」对应的写入消息「报告规则是详细。」未落库（d04-w2：write PASS 但 raw.results=[]）；疑源：D01「用户要求报告内容必须详细，这与之前要求的邮件回复简洁」重叠0.33；去重仅按 user_id、无视 domain/project/namespace metadata（experiment-design 隔离映射），且结果依赖案例顺序 | 维持 FAIL（记入能力矩阵：metadata 隔离在写路径失效） |
| P02 | 能力层·写路径去重越界 | 期望 token「邮件」对应的写入消息「P1 先接邮件。」未落库（p02-w1：write PASS 但 raw.results=[]）；确证去重来源：P01「P1 项目决定优先接入 Email Agent」——跨语言等价（邮件↔Email Agent），字面重叠推断检不出；P01/P02 属不同 project 命名空间仍被吞噬 | 维持 FAIL（记入能力矩阵：metadata 隔离在写路径失效） |
| T01 | 来源检查失败 | hits[].source_refs=['t01-m2'] 不含期望 message ID（mem0 为消息级来源）；若期望消息对应的写入未落库（见写路径行），此失败为连带结果；否则需人工核对期望 ID 与写入 message_ids | `<评审人填写>` |
| T01 | 能力层·写路径去重越界 | 期望 token「上海」对应的写入消息「我已搬到上海。」未落库（t01-w1：write PASS 但 raw.results=[]）；疑源：C02「用户已搬到上海居住，更新了之前的居住地信息」重叠0.80；去重仅按 user_id、无视 domain/project/namespace metadata（experiment-design 隔离映射），且结果依赖案例顺序 | 维持 FAIL（记入能力矩阵：metadata 隔离在写路径失效） |

## 汇总

| case_id | 自动状态 | Agent 自动终判 | 备注 |
|---|---|---|---|
| F01 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| F02 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| F03 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| F04 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| F05 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| N01 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| N02 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| N03 | FAIL | `PASS` | 自动复核：明确否认 forbidden 命题；机械子串检查误报 |
| N04 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| N05 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| U01 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| U02 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| U03 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| U04 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| U05 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| D01 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| D02 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| D03 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| D04 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| D05 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| P01 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| P02 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| P03 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| P04 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| P05 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| C01 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| C02 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| C03 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| C04 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| C05 | REVIEW_REQUIRED | `FAIL` | 【AI·中】语义判定未全满足：#2forbidden=出现 |
| T01 | FAIL | `FAIL` | 【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表 |
| T02 | REVIEW_REQUIRED | `FAIL` | 【AI·中】语义判定未全满足：#1required=部分成立 |
| T03 | REVIEW_REQUIRED | `PASS` | 【AI·中】全部 required 成立、forbidden 未出现（1 条中/低置信度，需重点复核） |
| T04 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| T05 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| E01 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| E02 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| E03 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |
| E04 | REVIEW_REQUIRED | `PASS` | 【机】全部 required 成立、forbidden 未出现 |
| E05 | REVIEW_REQUIRED | `PASS` | 【AI·高】全部 required 成立、forbidden 未出现 |

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
