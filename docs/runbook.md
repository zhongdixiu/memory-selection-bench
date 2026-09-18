# 全流程执行手册（Runbook）

从零开始执行一次完整对比验证的操作顺序、每步检查点、门禁与故障处置。

**一次性准备**（editable 安装，之后 `memory-bench` 命令在任意目录可用，
无需 PYTHONPATH；`.env` 会被自动加载，shell 中已 export 的同名变量优先）：

```bash
cd /home/zhongdixiu/codes/MemoryBench/memory-selection-bench
/home/zhongdixiu/miniforge3/bin/python -m pip install -e .
```

不便安装时的替代方式：在项目根目录 `export PYTHONPATH=src` 后用
`python -m memory_bench` 等价执行（离开项目根目录即失效，注意）。

**总原则**
- 严格串行执行，不要同时开两个 run（效果运行按设计 `effect_concurrency=1`）。
- 每步完成后先检查产物再进下一步；**旧 artifacts 永不删除**，它们是审计轨迹。
- 结论只能引用带真实模型调用的 run；doctor/启动成功不构成能力证据。
- FAIL 三分归因：接口层（`result.status`/`error`）、可见性（`attempts` 曲线）、
  能力层（`hard_failures` 内容）；另有 harness 缺陷单独归类，修复后重跑。

---

## 阶段 0：环境门禁（无 API 成本 → 3 次轻量调用）

| # | 命令 | 通过标准 |
|---|---|---|
| 0.1 | `/home/zhongdixiu/miniforge3/bin/python -m pytest -q` | 24 passed |
| 0.2 | `memory-bench validate-cases --config configs/bench.yaml` | `ok: true, case_count: 40, errors: []` |
| 0.3 | `memory-bench doctor --config configs/bench.yaml --live` | 全部 ok：路径 6 项、密钥 2 项、live 3 项（LLM 有回复；embedding **恰好 1024 维**；rerank 返回带 index/relevance_score） |

失败处置：密钥/网络问题修 `.env` 或代理后重跑；本阶段不产生 artifacts。

## 阶段 1：smoke（F02 单例 × 2 候选）

```bash
memory-bench smoke --candidate all --config configs/bench.yaml
```

- 耗时：约 2~5 分钟（Mem0 写入含同步 LLM 推理；EverOS 启动 + 可见性轮询）。
- 预期输出：`mem0 → PASS`；`everos → FAIL`（F02 带 `source_check: any`，
  EverOS 仅 session 级来源，**属已知 D 类缺口的预期 FAIL**）。
- **门禁判定**（everos FAIL 不阻塞的条件，逐项核对）：
  1. 两候选 manifest 均非 BLOCKED/TIMEOUT；
  2. Mem0：write `processed=true`、`native_ids` 非空、hit `source_refs` 为消息级
     （如 `["f02-m1"]`）、hit `text` 保持中文（提取语言对齐 shim 生效；
     若产出英文，检查 worker `custom_instructions` 后再归因）；
  3. EverOS：write `processed=true`（add=accumulated→flush=extracted）、
     `events.jsonl` 中 `search_attempt` 曲线收敛（前几次空、随后 hits=1）、
     最终 FAIL 的 hard_failures **仅**为 `no expected native source reference found`。
- 若 EverOS 出现其他失败（写入 FAIL、轮询 12 次始终 0 hits、启动超时），停下查
  `candidate.log`，归因后再继续。

## 阶段 2：decision 12 例 × R0/R1 × 2 候选（核心效果证据）

```bash
memory-bench run --candidate all --track r0 --suite decision --config configs/bench.yaml
memory-bench run --candidate all --track r1 --suite decision --config configs/bench.yaml
```

- 耗时估计：Mem0 每 run 约 15~30 分钟；EverOS 每 run 额外 +14~16 分钟
  （7 个带来源检查的用例结构性耗尽 120s 轮询窗口）。共 4 个 run。
- 预期内结果（不是故障）：
  - EverOS：E01/E04 → `UNSUPPORTED`（direct_record 无契约）；F05（per_claim）、
    U01/D03/P01/C02/T01/E01（any）→ 来源检查 FAIL；其余多为 REVIEW_REQUIRED。
  - Mem0：多数案例 REVIEW_REQUIRED（语义命题留人工），自动检查应基本全绿。
    提取语言对齐 shim 已生效（见 experiment-design 统一配置）；若中文
    required token 仍 FAIL，先核对 hit `text` 是否为中文，再判能力缺陷。
    **D03/T01 FAIL 为已归因的预期结果**：写路径去重无视 metadata 边界，
    被先跑案例（F05、C02）语义等价记忆抑制（write PASS 但 `raw.results=[]`），
    详见 experiment-design 隔离映射；复核时看 write 回执而非检索。
    N03 空写入属良性（负例期望行为），与 D03/T01 区分记录。
- R1 专属检查点：search result `rerank_applied=true`、hit `score` 为 rerank 分、
  原 dense 分在 `native_metadata.dense_score`。
- **门禁（进入 full 40 例的条件）**：4 个 run 全部完成、无 BLOCKED/TIMEOUT、
  每个 FAIL 都已按三分法归因记录。

## 阶段 3：人工语义评审（decision 4 个 run）

对每个 run：

1. 生成预填骨架（机械证据自动摘录，判定列留空；已存在的文件默认跳过不覆盖）：
   `/home/zhongdixiu/miniforge3/bin/python scripts/make_review_skeletons.py <run_id>`
   ——产出 `reports/manual_review_<run_id>.md`，已预填：基本信息/输入指纹、
   用例输入原文、写入回执核对、检索尝试曲线、hits 原文（含分数/来源/语言检测）、
   逐命题表、已确证的 FAIL 归因（来源粒度/语言合规/写路径去重越界/契约缺口）；
   也可手工复制 `reports/manual_review_TEMPLATE.md` 从零填写；
2. 从该 run 的 `case_results.csv` 摘出全部 REVIEW_REQUIRED 与需复核的 FAIL；
3. 打开 `case_results.json`，**原样粘贴 hits[].text**，逐命题判定
   （required 须成立、forbidden 须未出现），改写/翻译必填忠实度备注；
4. 填 FAIL 归因复核表、汇总表，签名。

纪律：两候选同一评审人、同一标准；只依据候选实际返回内容；
不得用 harness 已知信息替候选补判（尤其 EverOS 来源）。
工作量提示：这是全流程中最大的人工环节，decision 阶段约 4 份 × 10 例上下。

## 阶段 4：full 40 例 × R0/R1 × 2 候选

```bash
memory-bench run --candidate all --track r0 --suite full --config configs/bench.yaml
memory-bench run --candidate all --track r1 --suite full --config configs/bench.yaml
```

- 耗时估计：每候选每 run 约 1~2.5 小时（40 例写入推理 + EverOS 来源检查用例
  的轮询开销，上限受 `max_run_wall_seconds=14400` 保护）。共 4 个 run。
- 检查点与归因口径同阶段 2；完成后对 4 个 run 再做一轮阶段 3 式评审
  （可只精评与 decision 结论有出入的案例，其余抽查，但抽查范围须写进评审记录）。
  评审骨架同样用 `scripts/make_review_skeletons.py <run_id>` 生成；mem0 run
  会额外产出「运行级机械观察」表（全部空写入 + 疑源自动推断），优先核对该表分类。
- Mem0 full 预期结果（9109eb89/5ec2c317 已验证，评审按此口径复核）：
  - FAIL 集中于写路径：F04（提取遗漏，双轨稳定）、D01/D03/D04/P02/T01
    （跨案例去重越界，疑源见骨架表；D01/D04/P02 的 0 hits 是"写侧被吞噬 +
    读侧隔离正确挡住越域记忆"的复合结果，读路径隔离本身有效）；
  - R1 另有 N03 FAIL＝否定子串误判：存储"用户明确否认负责预算"语义正确，
    但含 forbidden 子串；人工按语义改判 PASS，不改 harness 判分逻辑；
  - N01/N03/U01-w1 两轨提取结果翻转（temp=0 仍非确定）——如实记录为写路径
    非确定性发现，不按 harness 故障重跑。
- EverOS full 预期结果（4a9195d0/7d5ce615 已验证，约 64 分钟/run）：
  - 状态构成：FAIL 25（≈16 来源检查类 D 缺口 F01-F05/U01/U03/U04/D03/P01/
    P03/P05/C01-C04 等 + 3 索引完整性 D01/D04/P02 + ≈7 语言合规 U01/C01/
    C02/T01/C05/T02 等，有重叠）、UNSUPPORTED 6（D05/E01-E05 direct_record）、
    REVIEW_REQUIRED 9（D02/N01-N05/P04/U02/U05）；
  - D01/D04/P02 FAIL＝**索引完整性缺陷**（共享 LanceDB 主键不含空间成分，
    同 session 多空间写入互相覆盖；签名 attempt 曲线 [1,0,0,…]），归因能力层，
    核对 runtime markdown 后按骨架预填口径复核，勿误判为检索能力缺陷；
  - N 组 REVIEW_REQUIRED 的 0 hits 受**负例可见性盲区**影响（单次即时检索，
    索引未收敛）：语义命题以 hits 为主、候选自产 episodes/*.md 为补充证据，
    勿把 0 hits 当作「推测未存储」；N03 若索引收敛会触发否定子串误判
    （episode「U1否认负责预算…」含 forbidden 子串），终判口径同 mem0 R1；
  - C03 双轨语言翻转（R0 中文/R1 英文 episode）——如实记录为写路径
    非确定性实例；R1 rerank 检查点 configured/requested/applied=True。
- **decision 阶段 everos run 的负例（N03/U05/D02/P04 等）同受可见性盲区影响**，
  评审既有 decision 骨架时按同一口径处理（勿 --force 重新生成，避免覆盖人工输入）。

## 阶段 5：P-native 探针（复用面证据，不参与排名）

```bash
memory-bench probe --candidate all --config configs/bench.yaml
```

- 6 例（F05,D03,P01,C02,T01,E01）走候选原生作用域/形成机制。
- 阅读重点：Mem0 单过滤集（仅 owner+namespace）下的召回与串扰；EverOS
  domain 单空间读取的覆盖差异。把实测行为记进差距表，
  用于校正 `reports/gaps_and_effort.md` 的工作量区间（尤其时间/as-of、
  direct record、逐消息来源三行）。

## 阶段 6：Email Agent 接入（产品链路证据）

```bash
memory-bench integrate --candidate all --track r0 --config configs/bench.yaml
# 可选对比：--track r1
```

- 3 任务 × M0/M1/M2 × 2 候选；产物为 `artifacts/<run_id>-email-*/integration_results.json`。
- 检查点：
  1. `preseed` 全部 PASS（任务记忆均为 conversation 写入，EverOS 不应出现 UNSUPPORTED）；
  2. 任务 A：M0 回答应缺 P1 决策信息；M1/M2 `required_tokens_found["Email Agent"]=true`
     且 `forbidden_tokens_found["P2-日程优先"]=false`（**作用域隔离在产品链路生效的直接证据**）；
  3. 任务 C：M1/M2 须含 `Retry-After`、`转人工`，不得推荐盲目重试；
  4. `tool_trace` 只出现 stub 工具、无真实收发信；`bridge_writes` 为空（评估不写回）；
  5. M2 的 `memory_route` 与 M1 强制检索的效果差异单独记录（原生路由是否漏检）。
- 记录每 task×mode 的 `elapsed_ms`，作为产品化时延证据。
- **EverOS 专属预警（full run 已证实的两个缺陷会在 integrate 复现）**：
  1. preseed 若把同一用户同日记忆写入多个空间（如 P1 项目 + shared），
     会触发索引主键冲突覆盖（§阶段 4 索引完整性缺陷）——任务检索 0 hits 时
     先查 `runtime/<run>/.index/lancedb` 与 markdown 事实源，再归因；
  2. 任务检索若紧跟 preseed flush（间隔 < 索引收敛的 20~40s），M1/M2 可能
     因索引未就绪而 0 hits——integrate 无可见性轮询，检查 preseed 与任务
     执行的时间间隔并在结果中披露。

## 阶段 7：汇总与结论改写

```bash
memory-bench report --config configs/bench.yaml
```

此命令生成 7 份基础文件，**会覆盖已有的能力矩阵、选型、差距和接入报告**；已有 Agent 或人工改写时，不要直接重跑。模板文案是占位，不会自动更新判定。

若暂不进行人工评审，可先用 8 份 Agent 自动评估形成**暂定结论**。保留 `case_results.json` 的机械状态，另行记录语义终判及修正理由，然后运行结构核对：

```bash
/home/zhongdixiu/miniforge3/bin/python scripts/audit_auto_reports.py
```

脚本生成 `reports/auto_audit.md`，核对评审汇总、原始状态、案例终判与 Email Agent 严格 token 结果；它不验证 Agent 语义判断本身。此路径需改写四份结论文件：

1. `capability_matrix.md`：把各能力行的 E/D 按实测+评审结论改判
   （A~C 只能由成功 run 证据确认），每格附 run_id；
2. `selection_decision.md`：基于 decision/full 的 R0、R1 对比与评审终判写结论；
   若证据仍不足则如实保留"双候选"；
3. `gaps_and_effort.md`：用 P-native 与 integrate 实耗校正工作量区间，
   重新划定 MVP 复用边界；人日仍属于规划估计；
4. `integration_report.md`：逐 task×mode 区分流程 `PASS`、严格 token 结果和回答语义；
   `tasks[].elapsed_ms` 不含预取检索时间。

收尾建议：先用 `git status` 核对变更，再按需要提交代码 + reports（artifacts/runtime/.env 已被
.gitignore 排除；若 artifacts 需长期存证，另行归档并注明 run_id 清单）。

---

## 故障处置速查

| 症状 | 第一落点 | 处置 |
|---|---|---|
| run 输出 BLOCKED | `manifest.json.error` | 缺密钥→查 `.env`；进程拉不起→`candidate.log`；修复后重跑（新 run_id，旧产物保留） |
| Mem0 worker 启动失败 | `candidate.log`（stderr 尾部 500 行） | 常见：venv 依赖、Qdrant 目录权限、代理（适配器已剔除 SOCKS `all_proxy`，若仍有代理问题检查 http_proxy 指向） |
| EverOS 启动超时（120s 探活） | `candidate.log` | 首次 LanceDB 初始化较慢；端口占用会自动换口，无需干预 |
| 某案例 TIMEOUT | `events.jsonl` 时间线 | 区分模型端点慢（doctor --live 复测）与候选处理慢（candidate.log） |
| EverOS 轮询 12 次仍 0 hits | `candidate.log` 的 OME 策略日志 | 看是否有 extraction 报错（如 LLM 限流）；限流则稍后重跑该 run |
| integrate preseed 失败 | `events.jsonl` 的 `integration_error` | 先单独重跑 smoke 确认候选管线仍健康 |
| API 限流/欠费 | live 检查或 candidate.log 中 4xx | 补密钥/等待配额，BLOCKED 重跑即可，不计入候选缺陷 |

## 预算参考（决策前知晓）

- LLM 调用大头：Mem0 每次 conversation 写入 1 次事实抽取；EverOS 每次写入
  触发 OME 策略管道（多次 LLM 调用）。full 40 例 × 2 轨道 × 2 候选为主要成本；
- 轮询开销：EverOS 每个来源检查 FAIL 用例最多 +120s（有界）；
- rerank：R1 每次 search 1 次调用（decision 12 例、full 40 例、integrate 每检索 1 次）。
