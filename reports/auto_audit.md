# Agent 自动评估结构核对

本文件由 `python scripts/audit_auto_reports.py` 从评审汇总与原始 artifacts 生成。
仅核对结构和计数；不验证 Agent 语义判断是否正确。

| run_id | 候选 | 轨道 | 套件 | PASS | FAIL | 机械 FAIL→语义 PASS |
|---|---|---|---|---:|---:|---|
| `20260915T025720Z-everos-r0-decision-d4fae806` | everos | r0 | decision | 4/12 | 8 | — |
| `20260915T032601Z-everos-r1-decision-152458ed` | everos | r1 | decision | 4/12 | 8 | — |
| `20260915T060401Z-mem0-r0-decision-6f171eca` | mem0 | r0 | decision | 9/12 | 3 | — |
| `20260915T061128Z-mem0-r1-decision-c4e4818e` | mem0 | r1 | decision | 9/12 | 3 | — |
| `20260915T074744Z-mem0-r0-full-9109eb89` | mem0 | r0 | full | 32/40 | 8 | — |
| `20260915T075013Z-mem0-r1-full-5ec2c317` | mem0 | r1 | full | 32/40 | 8 | N03 |
| `20260915T080353Z-everos-r0-full-4a9195d0` | everos | r0 | full | 8/40 | 32 | — |
| `20260915T080722Z-everos-r1-full-7d5ce615` | everos | r1 | full | 8/40 | 32 | — |

## Email Agent 严格 token 检查

| run_id | preseed PASS | M1/M2 严格 token PASS | bridge searches | bridge writes |
|---|---:|---:|---:|---:|
| `20260917T075118Z-mem0-r0-email-23637687` | 6/6 | 5/6 | 6 | 0 |
| `20260917T075230Z-everos-r0-email-831c6799` | 6/6 | 3/6 | 6 | 0 |

## 结构问题

未发现。
