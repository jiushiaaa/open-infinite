# Graph Memory Spike Design Pack MVP 收口说明

> 日期：2026-06-01  
> 范围：后续增强第二十刀，重型记忆 spike 前的只读设计包。

## 收口结论

Graph Memory Spike Design Pack MVP 已收口。系统新增只读 service/API/CLI/项目工作台面板，把 GraphRAG / Zep Trigger Evidence 转成可执行的 spike 设计包：候选层、试验输入、验收门槛、回退策略和 no-go 条件。

该切片不连接 GraphRAG/Zep/图数据库/向量库/reranker，不调用真实 embedding 或 LLM，不写 artifact，也不改变 BM25、canon ledger、entity aliases、retrieval_context 或 `run_scene` 默认行为。

## 已完成

- Service：`get_graph_memory_spike_design_pack(slug, projects_dir=None, now=None)` 返回 `summary`、`design_gate`、`layer_plans`、`experiment_inputs`、`acceptance_gates`、`rollback_plan`、`no_go_conditions`、`manifest` 与 `content_json`。
- API：`GET /api/stories/<slug>/graph-memory-spike-design-pack` 返回同一份只读设计包；坏 slug 返回 400，缺项目返回 404。
- CLI：`lne memory graph-design <slug> --json` 输出同一份只读设计包，适合无人值守脚本和本地诊断使用。
- API Contract / Typed Client：本地契约清单新增 `getGraphMemorySpikeDesignPack`；Graph Memory Offline Shadow Replay Report 接续完成后当前计数为 `endpoint_count=46`、`openapi_path_count=45`、`typed_client_method_count=45`。
- UI：项目工作台新增「Graph 记忆设计包」面板，展示设计包状态、候选层、试验输入、验收门槛、no-go 条件和外部服务暂缓边界。
- 测试：新增 `tests/test_graph_memory_spike_design_pack.py`，覆盖 service、非触发项目、HTTP、CLI、密钥/路径不泄漏。

## 验证

- Focused：`python -m pytest tests/test_graph_memory_spike_design_pack.py tests/test_api_contract.py tests/test_graph_memory_trigger_evidence.py -q` -> `11 passed`。
- 前端：`cd engine/ui && pnpm.cmd run build` 通过。
- 浏览器烟测：本地后端 + Vite 下打开项目工作台，确认「Graph 记忆设计包」面板显示设计包就绪、GraphRAG/Zep 候选、试验输入、验收门槛、no-go 条件和外部服务暂缓边界。
- 全量基线：Graph Memory Offline Shadow Replay Report 接续完成后 `python -m pytest -q` -> `803 passed`；`cd engine/ui && pnpm run build` 通过；根目录 `git diff --check` 通过。

## 边界

- 不读取、不返回、不记录 `LLM_API_KEY` / `SEEDREAM_API_KEY` 明文或环境变量名。
- 不写 `projects/` 或 `outputs/` 下的 spike design artifact。
- 不改变 `retrieve_context`、`run_scene`、`canon_ledger.jsonl`、`state_snapshot.json` 或任何既有 artifact 契约。
- 不把设计包当成真实 GraphRAG / Zep / Temporal Memory 接入开关；它只提供 shadow compare 前的本地方案。

## 后续状态

`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 与 `Graph Memory Offline Shadow Replay Plan MVP` 已接续收口。下一刀建议做 `Graph Memory Provider Spike Fixture Pack MVP`：把人工复核结果整理成 provider spike fixture pack，继续不接真实外部服务。
