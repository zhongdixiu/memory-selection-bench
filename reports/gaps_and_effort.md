# 差距与改造量记录

> **状态：Agent 自动分析草稿，未人工复核。工作量区间由 Agent 参考 P-native probe（`20260917T074937Z-mem0-p-native-probe-686b6efa` / `20260917T075434Z-everos-p-native-probe-a6565e50`）与 Email integrate（`20260917T075118Z-mem0-r0-email-23637687` / `20260917T075230Z-everos-r0-email-831c6799`）的运行证据调整，属于规划估计而非已测量开发工时。**

| 项目 | Mem0 | EverOS |
|---|---|---|
| 统一身份与作用域 | 通过 benchmark metadata + 受控 filter 组合映射；读路径隔离实测有效（full 套件中跨域/跨项目记忆对无权 principal 正确不可见），但写路径推理去重仅按 user_id（无视 metadata 边界），实测跨案例静默抑制写入且命名空间内永不可检索：decision F05→D03、C02→T01；full 扩展至 D01←F03、D04←F03/D01、P02←P01（跨语言等价且跨 project）、C02←U04、T01←C02；**probe 原生轨道 D03/T01 write EMPTY（ids=0）复现 → 缺陷在 mem0 核心 add 去重流程，与 harness 适配层无关**，产品化需解决去重作用域 | 通过 app/project 物理分区 + 受控读取空间映射；episode 追加式写入无语义去重，免疫跨案例语义串扰；但 full 实测**索引完整性缺陷**：episode 序号按空间独立计数而共享 LanceDB 主键 {user}_ep_{date}_{seq} 不含空间成分，同 session 多空间写入时后写者覆盖先写者索引行（markdown 事实源完好），D01/D04/P02 因此 FAIL（签名 attempt 曲线 [1,0,0,…]，双轨稳定）；**Email 任务 A 的 P1 episode 存于 markdown，但 M1/M2 仅检索到 shared 空间内容，表现与索引冲突一致（831c6799）；probe D03/P01 持续 0 hits 的具体机制仍需单独确认（a6565e50）**，产品化需在主键中加入空间成分并迁移既有索引 |
| 写路径确定性与提取召回 | temp=0 下边缘等价判定仍翻转（full R0/R1 对照：N01、N03、U01-w1 提取结果不一致），无案例级复现性；F04 指令类偏好（发送前须确认）双轨稳定提取遗漏 | full 中受支持的 conversation 写入未观察到提取遗漏；负例/假设/否认/第三方引述消息的已返回内容框架忠实（疑问存为「U1询问…」、否认存为「U1否认…」）；C03 双轨语言翻转（R0 中文 episode/R1 英文）为唯一写路径非确定实例；英文 episode 渗漏面 U01/C01/C02/T01/C05/T02（共享 LLM 违反默认提示词的语言一致规则） |
| 原生逐消息来源 | **实测可用**：metadata 保留 message IDs，decision F05（同段多事实及逐条来源）双轨 PASS，probe 原生轨道 F05 hits 携带来源正常（686b6efa）；推理更新后的来源继承行为已随 full 40 例覆盖未见退化 | 搜索 DTO 仅 session 级，decision F05 双轨 Agent 自动终判 FAIL（来源缺失），probe F05 FAIL「来源不完整」实测确证（a6565e50）；原生化需扩展核心 DTO 与持久化链 |
| direct record | `infer=false` 可用：decision E01（正向限流案例保真）双轨 PASS，probe E01 hits 正常；T01 写失败系去重越界连带，非 direct_record 机制缺陷 | memory/add 无对应契约，E01 UNSUPPORTED（decision 双轨 + probe 一致实测确证），需新增公开写入契约 |
| 提取语言行为 | 开箱将中文记忆改写为英文（提示词无语言保持规则）；锁定版无完整提取提示词替换配置口，仅追加式 custom_instructions（bench 经披露用其做语言对齐 shim） | 默认提示词自带强制语言一致规则，无需对齐；但共享 LLM 对简短输入实测违规产生英文 episode（U01/C02/T01），中文业务召回不稳定 |
| 公共 rerank | benchmark 外置 SiliconFlow rerank；R1 双轨完成，修正 N04/N03 语义误判后与 R0 的终判 FAIL 集合相同；两轨重新写入记忆，不能据此量化 rerank 增益 | benchmark 外置 SiliconFlow rerank；R1 与 R0 的终判 FAIL 集合相同；两轨重新写入记忆，不能据此量化 rerank 增益；英文 episode 的 rerank 分数很低（0.001~0.007 vs 0.2~0.997） |
| Agent 接入 | 同一 Email Agent bridge；**端到端实测通过（23637687）**：按回答语义 A/B/C 为 3/3 任务满足，严格 token 检查为 5/6 个 M1/M2 回答满足、forbidden 未出现、bridge_writes=[]（防污染有效）；preseed 写延迟 2.4~3.4s/条，任务应答 M0/M1/M2 约 9.5/3.9/3.6s（A）、5.7/3.8/4.3s（B）、4.0/2.4/2.1s（C）；遗留：C-M1 回答用「转为人工处理」表达相同语义，且注入上下文含「转人工」；严格子串检查误报，不属于预取注入缺失 | 同一 Email Agent bridge；**按回答语义 2/3 任务满足（831c6799），严格 token 检查为 3/6 个 M1/M2 回答满足**：B/C 任务 M1/M2 按回答语义满足，A 任务 M1/M2 未取回 P1 决策，只返回 shared 空间内容；表现与已知索引冲突一致；preseed 写延迟 6.2~7.8s/条（add+flush，约为 mem0 的 2~3 倍），任务应答 M1/M2 约 7.3/7.7s（A）、5.2/4.0s（B）、2.2/3.3s（C）；bridge 已执行预期调用；A 任务失败表现与候选索引缺陷一致，待修复后验证 |

## 源码落点

- Mem0：`mem0/memory/main.py` 的 add/search 生命周期、`mem0/llms/openai.py` 的请求参数、`mem0/embeddings/openai.py` 的维度参数；首轮不修改这些文件，shim 位于 benchmark worker。
- EverOS：`src/everos/entrypoints/api/routes/memorize.py`、`memory/search/dto.py` 与 search manager；逐消息来源/direct record 若要原生化会进入核心 DTO 和持久化链。
- Email Agent：`service.py` 的 router/prefetch/context injection/log_interaction 与 `honcho_memory/service.py` 接口；当前采用外部 worker，不修改源码。

## 工作量区间（乐观/通常/悲观，人日）——Agent 规划估计

不同模块存在重叠（尤其「身份与作用域」与「direct record」「提取质量」），不能直接求和承诺总工期。估计参考了 probe 暴露的复用缺口和 integrate 的运行行为；这些数据未测量实际开发工时，不能推导交付期限。

| 模块 | Mem0 | EverOS | 置信度/校正依据 |
|---|---:|---:|---|
| 身份与作用域服务 | 3/5/8（↑） | 3/6/10（=，置信度低→中） | Mem0 上调：probe 原生轨道复现去重越界 → 修复必须动 mem0 核心 add 去重键（非 worker shim 可解），且静默丢数据要求 40 例全量回归。EverOS 维持：主键修复落点已定位（LanceDB 主键加空间成分），但需索引迁移 + full/email/probe 三处复现面回归 |
| 逐消息来源链 | 2/3/5（↓） | 5/9/15（=，置信度低→中） | Mem0 下调：metadata 方案 decision F05 双轨 PASS + probe hits 正常，实测可用，仅剩产品化审计。EverOS 维持：DTO session 级已被 probe F05「来源不完整」实测确证，需扩展核心 DTO 与持久化链 |
| 项目共享与隔离 | 1/3/5（=，置信度低→中） | 2/4/7（=，置信度低→中） | 两者读隔离均已实测通过（full 负例 D02/U05/P04），仅剩写权限与审计补齐 |
| 版本/来源时间/as-of | 5/9/15（=） | 4/7/12（↓） | Mem0 维持：C05 forbidden 出现（平铺无时间框架）、T02 将期望的 9 月 14 日下午误写为 9 月 15 日下午；T03 的一小时窗口在双轨正确保留；T01 因写入抑制失败。完整 as-of 投影仍需自建。EverOS 下调：episode 带时间戳演进、C05 forbidden 未出现，机制基础已在，只需补时间窗口投影（但 T01~T05 仍 FAIL，不能按达标计） |
| 案例 direct record | 2/4/7（=） | 4/8/14（=，置信度低→中） | Mem0：infer=false 实测可用（decision E01 双轨 PASS + probe hits 正常），修复依赖去重作用域模块（重叠计入）。EverOS：UNSUPPORTED 经 probe 实测确证，需新增公开写入契约 + DTO |
| 提取质量与语言合规（新增） | 3/5/9 | 2/4/7 | Mem0：F04 指令类偏好双轨稳定遗漏 + 原生中文改写英文（当前靠 bench shim 对齐），需提取提示词产品化替换口 + 确定性回归（temp=0 仍翻转）。EverOS：full 中受支持的 conversation 写入未观察到提取遗漏，已返回内容框架忠实，仅需治理英文 episode 渗漏（共享 LLM 违规行为，修复路径不确定——模型侧行为，可能需提示词强化或输出语言校验层） |
| Email Agent 产品化适配 | 2/3/5（↓） | 3/5/8（↑） | Mem0 下调：端到端 3/3 任务通过，C-M1 是严格子串检查误报，不计为注入适配缺陷。EverOS 上调：bridge 本身通过，但任务 A 失败暴露对索引修复的硬依赖，且 preseed 写延迟约 6.2～7.8s/条（约 mem0 2~3 倍）需评估捕获路径吞吐 |
| 恢复、幂等与回归 | 3/6/10（=） | 3/6/10（=） | 低；可靠性运行尚未执行，本项未经任何实测校正 |

因此仍不能支持「2~3 周完成统一平台」的承诺；但相比源码检查阶段，边界已可收敛为下面的 MVP 复用划分。

## MVP 复用边界（按实测重新划定）

**Mem0 路线（主选，见 selection_decision.md）**

- 可直接复用：dense 检索链、metadata 读隔离、message-ID 逐消息来源、`infer=false` direct record、外置 SiliconFlow rerank、Email bridge worker 模式（含防污染设计，bridge_writes=[] 实测有效）。
- 前置阻塞项（必须先修并验证）：① 写路径去重作用域（核心 add 去重键加 metadata 边界，静默丢数据不可上线）；② F04 类重要指令偏好稳定提取；③ 将 bench 的语言对齐配置产品化。
- 后续验证：写路径确定性（temp=0 翻转）、C-M1「转人工」子串判分。
- 需自建（两候选皆然）：完整 as-of 时间投影、可靠性/恢复验证。

**EverOS 路线（备选）**

- 可直接复用：受支持 conversation 的 episode 提取忠实度（full 未观察到遗漏，已返回内容框架忠实）、时间戳演进存储、物理分区隔离。
- 前置阻塞项：① LanceDB 主键加空间成分 + 索引迁移（full/email/probe 三处复现）；② direct_record 写入契约；③ 逐消息来源 DTO 扩展；④ 英文 episode 渗漏治理。四项均触及核心链或共享模型行为，改造面明显大于 Mem0 路线。
- 若二期业务权重偏向提取忠实/时间演进，EverOS 在修复验证通过后仍具竞争力。

**运行时延样本（integrate 实测；任务应答时间不含预取检索，不能直接作为端到端容量指标）**

| 指标 | Mem0 | EverOS |
|---|---|---|
| preseed 捕获写入 | 2.4~3.4s/条 | 6.2~7.8s/条（add+flush） |
| 任务应答（M1/M2 典型） | 2.1~4.3s | 2.2~7.7s |
| 任务功能链路 | 按回答语义 A/B/C 满足 | B/C 满足，A 的 P1 记忆未召回 |
