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
| run_id | `20260915T061128Z-mem0-r1-decision-c4e4818e` |
| 候选 / 轨道 / 套件 | mem0 / r1 / decision |
| 运行时间 | 2026-09-15T06:11:28.199748+00:00 → 2026-09-15T06:16:13.606633+00:00（status=FAIL） |
| 评估主体 | Agent 自动评估（未人工复核） |
| 人工复核状态 | 未进行 |
| 证据路径 | `artifacts/20260915T061128Z-mem0-r1-decision-c4e4818e/case_results.json` |
| 输入指纹 | case_data_hash=`2119225c27a3` config_hash=`27df7b45d308` |

## 评审范围

- REVIEW_REQUIRED：F05, N03, U01, U05, D02, P01, P04, C02, E01, E04
- FAIL（需归因复核）：D03, T01
- UNSUPPORTED：无

## 预填导航（脚本+LLM 预填，供人工复核）

判定来源统计：AI 语义判定 0 条，复用（mem0-r0 已填同款单元）0 条，机械层 0 条（0 hits 0／隔离负例 0／字面全包含 0），终判建议 1 条。
标记说明：【AI·高/中/低】LLM 语义判定及置信度；【机·…】机械可证；【复·…】跨文件复用同款判定。所有预填均为建议，人工确认后请去掉尖括号 `<>`；改判直接覆盖并删标记。

**建议复核顺序**：先看下面 0 个重点案例，再抽查高置信度条目。



## 逐案例评审

---

### 案例 F05：同段多事实及逐条来源

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[f05-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T09:40:00+08:00）：「我负责 P1；邮件简洁；报告必须保留指标。」
- search[f05-q1]（U1）：「总结我的项目、邮件风格和报告要求。」 机械检查：required_tokens=['P1', '简洁', '指标']，source_check=per_claim 期望 ['f05-m1']

**写入回执核对**（机械证据）：
- write[f05-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户负责P1项目，要求邮件保持简洁，且报告中必须保留指标数据」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.3957，dense=0.7121 source_refs=['f05-m1'] 语言=中文
用户负责P1项目，要求邮件保持简洁，且报告中必须保留指标数据
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户负责 P1 | `<成立>` | `<用户负责P1项目>` |
| 2 | required | 邮件要求简洁 | `<成立>` | `<要求邮件保持简洁>` |
| 3 | required | 报告必须保留指标 | `<成立>` | `<报告中必须保留指标数据>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（Agent 自动建议；证据见上文）

---

### 案例 N03：助手推测被用户否认

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[n03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:20:00+08:00）：「你可能负责预算。」
- write[n03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T10:21:00+08:00）：「我没有这样说。」
- search[n03-q1]（U1）：「我是否负责预算？」 机械检查：forbidden_tokens=['负责预算']

**写入回执核对**（机械证据）：
- write[n03-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 用户负责预算 | `<未出现>` | `<未返回任何信息，hit是0>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（Agent 自动建议；证据见上文）

---

### 案例 U01：两用户偏好隔离

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[u01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T11:00:00+08:00）：「我喜欢简洁回答。」
- write[u01-w2]（U2，scope=user_public/U2，occurred_at=2026-09-14T11:01:00+08:00）：「我喜欢详细回答。」
- search[u01-q1]（U2）：「我喜欢什么回答风格？」 机械检查：required_tokens=['详细']，forbidden_tokens=['简洁']，source_check=any 期望 ['u01-m2']

**写入回执核对**（机械证据）：
- write[u01-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户偏好简洁的回答风格」
- write[u01-w2]（U2）：PASS，native_ids=1 条 → ADD:「用户偏好接收详细的回答，希望获得全面且深入的信息而非简短的回复」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.2294，dense=0.6594 source_refs=['u01-m2'] 语言=中文
用户偏好接收详细的回答，希望获得全面且深入的信息而非简短的回复
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | U2 喜欢详细回答 | `<成立>` | `<用户偏好接收详细的回答，希望获得全面且深入的信息而非简短的回复>` |
| 2 | forbidden | U2 喜欢简洁回答 | `<未出现>` | `<用户偏好接收详细的回答，希望获得全面且深入的信息而非简短的回复>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（Agent 自动建议；证据见上文）

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
| 1 | forbidden | 未认证调用者读取 U1 数据 | `<未出现>` | `<0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（Agent 自动建议；证据见上文）

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
| 1 | forbidden | 报告业务读取邮件私有代号 | `<未出现>` | `<0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（Agent 自动建议；证据见上文）

---

### 案例 D03：公共职责跨业务可见

**自动判分结果**：FAIL；hard_failures：missing required token: P1

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[d03-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T12:20:00+08:00）：「我是 P1 负责人。」
- search[d03-q1]（U1）：「我的公共职责是什么？」 机械检查：required_tokens=['P1']，source_check=any 期望 ['d03-m1']

**写入回执核对**（机械证据）：
- write[d03-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户是 P1 负责人 | `<不成立>` | `<0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits：对照写入回执判断是写入未落库（如 mem0 raw.results=[]）还是召回失败。

**本案例人工终判**：`<FAIL>`（【机】维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表）

---

### 案例 P01：项目决策跨业务延续

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p01-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:00:00+08:00）：「P1 决定先接 Email Agent。」
- search[p01-q1]（U1）：「P1 决定先接哪个 Agent？」 机械检查：required_tokens=['Email Agent']，source_check=any 期望 ['p01-m1']

**写入回执核对**（机械证据）：
- write[p01-w1]（U1）：PASS，native_ids=1 条 → ADD:「P1项目决定优先接入Email Agent」

**检索尝试曲线**（attempts=1）：hits 序列 [1]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.9939，dense=0.7544 source_refs=['p01-m1'] 语言=中英混合
P1项目决定优先接入Email Agent
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | P1 先接 Email Agent | `<成立>` | `<P1项目决定优先接入Email Agent>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（Agent 自动建议；证据见上文）

---

### 案例 P04：知道项目标识不等于有权限

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[p04-w1]（U1，scope=project/P1，occurred_at=2026-09-14T13:30:00+08:00）：「P1 私有决策码 PROJECT-P1-404。」
- search[p04-q1]（U1）：「P1 的私有决策码是什么？」 机械检查：forbidden_tokens=['PROJECT-P1-404']

**写入回执核对**（机械证据）：
- write[p04-w1]（U1）：PASS，native_ids=1 条 → ADD:「P1项目的私有决策码是 PROJECT-P1-404」

**检索尝试曲线**（attempts=1）：hits 序列 [0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | forbidden | 未授权 Agent 读取 P1 | `<未出现>` | `<0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（Agent 自动建议；证据见上文）

---

### 案例 C02：当前住址与历史住址

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[c02-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:20:00+08:00）：「我现居北京。」
- write[c02-w2]（U1，scope=user_public/U1，occurred_at=2026-09-14T14:30:00+08:00）：「我已搬到上海。」
- search[c02-q1]（U1）：「我当前住在哪里？」 机械检查：required_tokens=['上海']，source_check=any 期望 ['c02-m2']

**写入回执核对**（机械证据）：
- write[c02-w1]（U1）：PASS，native_ids=1 条 → ADD:「用户现居北京」
- write[c02-w2]（U1）：PASS，native_ids=1 条 → ADD:「用户已搬到上海，不再居住在北京」

**检索尝试曲线**（attempts=1）：hits 序列 [2]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
[hit 1] score=0.5388，dense=0.7146 source_refs=['c02-m1'] 语言=中文
用户现居北京
```

```
[hit 2] score=0.1452，dense=0.6422 source_refs=['c02-m2'] 语言=中文
用户已搬到上海，不再居住在北京
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户当前住在上海 | `<成立>` | `<用户已搬到上海，不再居住在北京>` |
| 2 | forbidden | 用户当前仍住北京 | `<出现>` | `<用户现居北京>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<FAIL未过滤失效信息>`（Agent 自动建议；证据见上文）

---

### 案例 T01：来源时间优先于入库顺序

**自动判分结果**：FAIL；hard_failures：missing required token: 上海

**用例输入**（data/cases.yaml，供忠实度对照）：
- write[t01-w1]（U1，scope=user_public/U1，occurred_at=2026-09-14T16:00:00+08:00）：「我已搬到上海。」
- write[t01-w2]（U1，scope=user_public/U1，occurred_at=2026-08-01T09:00:00+08:00）：「补录旧记录：我住在北京。」
- search[t01-q1]（U1）：「我当前住在哪里？」 机械检查：required_tokens=['上海']，source_check=any 期望 ['t01-m1']

**写入回执核对**（机械证据）：
- write[t01-w1]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**
- write[t01-w2]（U1）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**

**检索尝试曲线**（attempts=12）：hits 序列 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：

```
（0 hits——候选未返回任何内容）
```
**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 用户当前住在上海 | `<不成立>` | `<0 hits——候选未返回任何内容>` |
| 2 | forbidden | 旧记录覆盖上海 | `<未出现>` | `<0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits：对照写入回执判断是写入未落库（如 mem0 raw.results=[]）还是召回失败。

**本案例人工终判**：`<FAIL记忆信息写入失败>`（Agent 自动建议；证据见上文）

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
[hit 1] score=0.9622，dense=0.7767 source_refs=['e01-m1'] 语言=中英混合
成功案例：遇到限流时先读取 Retry-After，再按该时间重试；若没有 Retry-After 则转人工处理。
```

**逐命题判定**（required 须确认成立，forbidden 须确认不成立；现有判定与理由由 Agent 自动生成，未人工复核）：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 先读取 Retry-After | `<成立>` | `<遇到限流时先读取 Retry-After>` |
| 2 | required | 按指定时间重试 | `<成立>` | `<再按该时间重试>` |
| 3 | required | 缺失时转人工 | `<成立>` | `<若没有 Retry-After 则转人工处理>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。

**本案例人工终判**：`<PASS>`（Agent 自动建议；证据见上文）

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
| 1 | forbidden | U2 读取 U1 专属案例 | `<未出现>` | `<0 hits——候选未返回任何内容>` |

**忠实度备注**（机械观察已预填，评审人补充判断）：
- mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。
- 0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。

**本案例人工终判**：`<PASS>`（Agent 自动建议；证据见上文）

## FAIL / UNSUPPORTED 归因复核

| case_id | 归因类别 | 证据 | 结论 |
|---|---|---|---|
| D03 | 能力层·写路径去重越界 | write PASS 但 raw.results=[]；F05 先写「用户负责P1项目…」；去重检索仅按 user_id 过滤、无视 namespace metadata（experiment-design 隔离映射） | 维持 FAIL（记入能力矩阵：metadata 隔离在写路径失效） |
| T01 | 能力层·写路径去重越界 | write PASS 但 raw.results=[]；C02 先写「现居北京/已搬到上海」；去重检索仅按 user_id 过滤、无视 namespace metadata（experiment-design 隔离映射） | 维持 FAIL（记入能力矩阵：metadata 隔离在写路径失效） |

## 汇总

| case_id | 自动状态 | Agent 自动终判 | 备注 |
|---|---|---|---|
| F05 | REVIEW_REQUIRED | `<PASS>` |  |
| N03 | REVIEW_REQUIRED | `<PASS>` |  |
| U01 | REVIEW_REQUIRED | `<PASS>` |  |
| U05 | REVIEW_REQUIRED | `<PASS>` |  |
| D02 | REVIEW_REQUIRED | `<PASS>` |  |
| D03 | FAIL | `<FAIL>` | 见归因表 |
| P01 | REVIEW_REQUIRED | `<PASS>` |  |
| P04 | REVIEW_REQUIRED | `<PASS>` |  |
| C02 | REVIEW_REQUIRED | `<FAIL>` |  |
| T01 | FAIL | `<FAIL>` | 见归因表 |
| E01 | REVIEW_REQUIRED | `<PASS>` |  |
| E04 | REVIEW_REQUIRED | `<PASS>` |  |

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
