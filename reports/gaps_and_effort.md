# 差距与改造量记录

| 项目 | Mem0 | EverOS |
|---|---|---|
| 统一身份与作用域 | 通过 benchmark metadata + 受控 filter 组合映射 | 通过 app/project 物理分区 + 受控读取空间映射 |
| 原生逐消息来源 | metadata 可保留 message IDs，需验证推理更新后的继承行为 | 搜索原生暴露 session，逐消息来源需扩展 |
| direct record | `infer=false` 可用 | memory/add 无对应契约，当前标记 UNSUPPORTED |
| 公共 rerank | benchmark 外置 SiliconFlow rerank | benchmark 外置 SiliconFlow rerank |
| Agent 接入 | 同一 Email Agent bridge | 同一 Email Agent bridge |

## 源码落点

- Mem0：`mem0/memory/main.py` 的 add/search 生命周期、`mem0/llms/openai.py` 的请求参数、`mem0/embeddings/openai.py` 的维度参数；首轮不修改这些文件，shim 位于 benchmark worker。
- EverOS：`src/everos/entrypoints/api/routes/memorize.py`、`memory/search/dto.py` 与 search manager；逐消息来源/direct record 若要原生化会进入核心 DTO 和持久化链。
- Email Agent：`service.py` 的 router/prefetch/context injection/log_interaction 与 `honcho_memory/service.py` 接口；当前采用外部 worker，不修改源码。

## 初步工作量区间（乐观/通常/悲观，人日）

以下只是源码检查后的低置信估算，必须由 P-native 和联调实耗校正；不同模块存在重叠，不能直接求和承诺总工期。

| 模块 | Mem0 | EverOS | 置信度/依据 |
|---|---:|---:|---|
| 身份与作用域服务 | 2/4/7 | 3/6/10 | 低；两者均无生产认证，EverOS 还需跨 app/project 编排 |
| 逐消息来源链 | 2/4/7 | 5/9/15 | 低；Mem0 可携 metadata，EverOS 搜索 DTO 目前为 session 级 |
| 项目共享与隔离 | 1/3/5 | 2/4/7 | 低；均已有映射原型，需补写权限与审计 |
| 版本/来源时间/as-of | 5/9/15 | 5/10/18 | 低；两者都不能直接满足全部固定时间用例 |
| 案例 direct record | 2/4/7 | 4/8/14 | 低；Mem0 有 infer=false，EverOS 无公开等价写入契约 |
| Email Agent 产品化适配 | 2/4/7 | 2/4/7 | 中低；真实注入点已定位、worker 已启动 |
| 恢复、幂等与回归 | 3/6/10 | 3/6/10 | 低；可靠性运行尚未执行 |

因此目前不能支持“2～3 周完成统一平台”的承诺；只能在效果、P-native 与 Agent 结果齐全后重新划定 MVP 复用边界。
