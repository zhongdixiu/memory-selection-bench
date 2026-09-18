# 人工语义评审记录

> 使用方法：复制本文件为 `reports/manual_review_<run_id>.md` 后填写。
> 每个 run 一份；两候选必须由同一评审人、同一标准完成。
> 判定只依据 `case_results.json` 中候选实际返回的 `hits[].text`（可参考
> `native_metadata`），禁止引入 harness 已知但候选未返回的信息
> （例如不得用用例里的 message ID 替 EverOS 补成"来源通过"）。

## 基本信息

| 项 | 值 |
|---|---|
| run_id | `<如 20260914T093710Z-mem0-r0-smoke-09bb71b5>` |
| 候选 / 轨道 / 套件 | `<mem0|everos> / <r0|r1|p-native> / <smoke|decision|probe|full>` |
| 评审人 | `<姓名>` |
| 评审时间 | `<YYYY-MM-DD HH:MM 时区>` |
| 证据路径 | `artifacts/<run_id>/case_results.json` |
| 输入指纹 | case_data_hash=`<manifest.json 中值前 12 位>` config_hash=`<前 12 位>` |

## 评审范围

从 `case_results.csv` / `case_results.json` 摘出本 run 需要人工判定的案例：

- `REVIEW_REQUIRED` 案例：`<case_id 列表>`
- 需要归因复核的 `FAIL` 案例（区分接口层/可见性/能力层）：`<case_id 列表>`

## 逐案例评审

每个案例复制下面这个小节。`review_items` 直接抄自
`operations[].evaluation.review_items`；`required:` 命题须确认**成立**，
`forbidden:` 命题须确认**不成立**，全部满足才可改判 PASS。

---

### 案例 `<case_id>`：`<title>`

**自动判分结果**：`<REVIEW_REQUIRED|FAIL>`；hard_failures：`<原样摘录或"无">`

**候选实际返回的 hit 文本**（从 `hits[].text` 原样粘贴，多条逐行列出）：

```
<hit 1 文本>
<hit 2 文本（如有）>
```

**逐命题判定**：

| # | 类型 | 命题（review_items 原文） | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | `<命题原文>` | `<成立\|不成立\|部分成立>` | `<引用 hit 文本中的依据；改写/翻译/概括是否忠实，是否引入原消息没有的信息>` |
| 2 | forbidden | `<命题原文>` | `<未出现\|出现>` | `<依据>` |

**忠实度备注**（候选对原消息做了改写/翻译/合并时必填）：
`<如：原文"技术方案默认用 Python"被改写为英文并追加"implementation plans"，
是否属于可接受概括？依据是什么？>`

**本案例人工终判**：`<PASS|FAIL>`（改判理由一句话）

---

### 示例（已填好，供参照；来自 Mem0 smoke run 09bb71b5）

### 案例 F02：默认技术语言

**自动判分结果**：REVIEW_REQUIRED；hard_failures：无

**候选实际返回的 hit 文本**：

```
User defaults to using Python for technical solutions and implementation plans
```

**逐命题判定**：

| # | 类型 | 命题 | 判定 | 理由 |
|---|---|---|---|---|
| 1 | required | 技术方案默认使用 Python | 成立 | hit 明确表述"defaults to using Python for technical solutions"，核心语义（默认语言=Python）忠实；追加的"implementation plans"属同义扩展，未改变或夸大原意 |

**忠实度备注**：原文"技术方案默认用 Python。"被 mem0 推理改写为英文单句。
中→英改写本身不扣分（检索命中且 token "Python" 保留），评审关注点是有无
引入原话没有的约束或丢失限定条件。

**本案例人工终判**：PASS

---

## FAIL 归因复核（如有）

| case_id | 归因类别 | 证据 | 结论 |
|---|---|---|---|
| `<id>` | `<接口层\|可见性\|能力层\|harness缺陷>` | `<attempts 曲线 / hard_failures / candidate.log 行>` | `<维持 FAIL\|判为 harness 问题需修复重跑>` |

## 汇总

| case_id | 自动状态 | 人工终判 | 备注 |
|---|---|---|---|
| `<id>` | `<状态>` | `<PASS\|FAIL>` | `<一句话>` |

**评审声明**：本人确认以上判定仅基于候选实际返回内容，未使用候选未暴露的
harness 侧信息；同一标准将用于另一候选的对应 run。

签名：`<姓名>` 日期：`<YYYY-MM-DD>`
