# 能力验证矩阵

> **状态：Agent 自动评估的暂定矩阵，未经过人工复核。**
> 本文件综合 12 个真实模型调用 run 与 8 份 Agent 语义评估。`memory-bench report` 会用占位模板覆盖本文件；原始机械状态仍以 artifacts 为准。

**评级口径**（A～C 只能由成功 run 的实测证据确认）：

- **A**：实测证据完整，链路可直接复用，无需改造
- **B**：实测可用，但存在已知轻微缺陷或需运维/使用约束
- **C**：部分可用，存在明确核心缺口，需改造后才能达标
- **D**：接口/调用链存在明确核心缺口（源码 + 实测双重确认）
- **E**：尚未完成在线验证

## 能力矩阵（实测评级）

| 能力 | Mem0 | EverOS | 当前证据（run_id + 评审终判） |
|---|---|---|---|
| Dense Top-k 检索 | **A** | **C** | Mem0：decision 双轨 9/12 PASS，probe 的 F05/P01/C02/E01 有 hits（`20260917T074937Z-mem0-p-native-probe-686b6efa`）；full 自动语义终判 32/40，其余失败包括写入缺失与时间/状态表达问题，不能直接归因于 dense 检索。EverOS：正向检索可返回语义内容，但索引完整性缺陷影响召回；full 的 8 个 PASS 均为负例或隔离例，N01～N05 的即时 0 hits 不能证明已完成内容级判断。probe D03/P01 有持续 0 hits（`20260917T075434Z-everos-p-native-probe-a6565e50`）；R1 的英文 episode 分数很低（`20260915T032601Z-everos-r1-decision-152458ed`） |
| 用户/域/项目隔离 | **C** | **C** | Mem0：读路径隔离实测有效（full 跨域/跨项目负例 D02/U05/P04 对无权 principal 正确不可见，双轨一致）；**写路径推理去重仅按 user_id、无视 metadata 边界**，跨案例静默抑制写入：full D01/D03/D04/P02/T01 FAIL（`20260915T074744Z-mem0-r0-full-9109eb89` / `20260915T075013Z-mem0-r1-full-5ec2c317`），probe 原生轨道 D03/T01 write EMPTY（ids=0）复现（686b6efa）→ 非 bench 环境特有。EverOS：app/project 物理分区 + 读取空间映射有效；**LanceDB 索引主键 `{user}_ep_{date}_{seq}` 不含空间成分**，同 session 多空间写入后写者覆盖先写者索引行（markdown 事实源完好）：full D01/D04/P02 FAIL（`20260915T080353Z-everos-r0-full-4a9195d0`）、Email 任务 A 端到端复现（831c6799）、probe D03/P01 0 hits 变体（a6565e50） |
| 逐消息原生来源 | **B** | **D** | Mem0：metadata 保留 message IDs，decision F05（同段多事实及逐条来源）双轨 PASS（6f171eca / c4e4818e），probe F05 hits 携带来源正常（686b6efa）；推理更新后的来源继承行为仍需产品化验证。EverOS：搜索 DTO 仅暴露 session 级来源，decision F05 Agent 自动终判 FAIL（来源缺失，双轨），probe F05 FAIL「来源不完整」（a6565e50）实测确证需扩展核心 DTO |
| direct_record | **B** | **D** | Mem0：`infer=false` 契约可用，decision E01（正向限流案例保真）双轨 PASS，probe E01 hits 正常（686b6efa）；T01 写失败系去重越界连带（见隔离行），非 direct_record 机制缺陷。EverOS：memory/add 无对应契约，E01 UNSUPPORTED（decision 双轨 + probe a6565e50 一致）→ 需新增公开写入契约 |
| 公共 R1 rerank | **A** | **A** | 外置 SiliconFlow rerank 作为 benchmark 公共组件已在双方 R1 run 成功执行（c4e4818e / 152458ed / 5ec2c317 / 7d5ce615）；此评级只表示调用链可用。修正自动语义判定后，双方 R0/R1 各自的 FAIL 集合相同；但两轨重新写入和提取记忆，不能据此断言 rerank 没有效果。量化增益需固定同一记忆快照再比较 |
| Email Agent M0/M1/M2 | **B** | **C** | Mem0（`20260917T075118Z-mem0-r0-email-23637687`）：按回答语义 A/B/C 为 3/3，严格 token 检查为 5/6 个 M1/M2 回答；C-M1 用“转为人工处理”表达了“转人工”，且注入上下文包含该规则。EverOS（`20260917T075230Z-everos-r0-email-831c6799`）：按语义 B/C 为 2/3，严格 token 检查为 3/6；A-M1/M2 未取得 P1 决策，只返回 shared 空间内容。双方 `bridge_writes=[]`；本次每条 preseed 写入约 Mem0 2.4～3.4s、EverOS 6.2～7.8s；任务 `elapsed_ms` 不含预取检索 |
| 写路径确定性与提取忠实（补充维度） | **C** | **B** | Mem0：temp=0 下双轨提取仍翻转（N01/N03/U01-w1，9109eb89 vs 5ec2c317），无案例级复现性；F04（对外发送确认规则）双轨稳定提取遗漏。EverOS：full 中受支持的 conversation 写入未观察到提取遗漏，已返回内容的负例/假设/否认/第三方引述框架忠实（疑问存为「U1询问…」、否认存为「U1否认…」）；C03 双轨语言翻转是已观察到的写路径非确定实例 |
| 时间感知 / as-of（补充维度） | **C** | **C** | Mem0：C05 返回三个均称“当前”的阶段；T02 将 2026-09-14 下午误写为 2026-09-15 下午；T03 的一小时窗口在双轨正确保留；T01 因写入抑制 FAIL。EverOS：episode 有时间戳演进、C05 未出现三阶段并列，但 T01～T05 双轨仍 FAIL。两候选均未满足完整 as-of 要求 |
| 中文语言合规（补充维度） | **B**（依赖 shim） | **C** | Mem0：开箱将中文记忆改写为英文（提取提示词无语言保持规则）；bench 经披露用追加式 custom_instructions 做语言对齐 shim，对齐后中文召回实测通过；锁定版无完整提取提示词替换配置口。EverOS：默认提示词自带强制语言一致规则，但共享 LLM（qwen3.7-plus，temp=0）对简短输入实测违规产英文 episode（U01/C01/C02/T01/C05/T02 渗漏面），叠加 R1 跨语言 rerank 坍缩 → 中文业务召回不稳定（见 docs/experiment-design.md 语言合规发现） |

## 运行状态汇总（harness 机械口径）

该表混合 smoke、decision、full 与 probe 的原始机械状态，只用于产物盘点，不作为候选通过率或 Agent 自动语义终判。`REVIEW_REQUIRED` 的自动语义结果见下表。

| 候选 | 轨道 | PASS | FAIL | UNSUPPORTED | BLOCKED | REVIEW_REQUIRED |
|---|---:|---:|---:|---:|---:|---:|
| everos | p-native | 0 | 5 | 1 | 0 | 0 |
| everos | r0 | 0 | 32 | 8 | 0 | 13 |
| everos | r1 | 0 | 31 | 8 | 0 | 13 |
| mem0 | p-native | 0 | 2 | 0 | 0 | 4 |
| mem0 | r0 | 0 | 8 | 0 | 0 | 45 |
| mem0 | r1 | 0 | 9 | 0 | 0 | 43 |

## Agent 自动语义终判统计（未人工复核）

| 套件 / 候选 | R0 | R1 | 主要限制 |
|---|---:|---:|---|
| decision / Mem0 | 9 PASS、3 FAIL | 9 PASS、3 FAIL | D03、C02、T01 失败 |
| decision / EverOS | 4 PASS、8 FAIL | 4 PASS、8 FAIL | 来源、语言和写入契约缺口 |
| full / Mem0 | 32 PASS、8 FAIL | 32 PASS、8 FAIL | 5 例去重越界、F04 提取遗漏、C05/T02 时间与状态表达 |
| full / EverOS | 8 PASS、32 FAIL | 8 PASS、32 FAIL | R0 有 16 例仅因来源检查失败，6 例写入契约不支持；通过项全为负例或隔离例 |

P-native probe 只作复用面证据：Mem0 2 FAIL、4 REVIEW_REQUIRED；EverOS 5 FAIL、1 UNSUPPORTED。Email 接入按回答语义为 Mem0 3/3、EverOS 2/3；严格 token 检查分别为 5/6、3/6 个 M1/M2 回答，详见 `integration_report.md`。
