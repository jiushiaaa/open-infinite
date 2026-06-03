# GraphRAG / Zep Trigger Evidence MVP 收口说明

> 日期：2026-06-01  
> 范围：后续增强第十九刀，重型记忆接入前的本地只读触发证据。

## 收口结论

GraphRAG / Zep Trigger Evidence MVP 已收口。系统新增只读 service/API/CLI/项目工作台面板，把 v0.9.3 图记忆触发评估、retrieval probe、跨项目样本趋势，以及本地 canon ledger、entity aliases、关系/因果/状态信号聚合成一份可复核证据。

该切片只判断是否值得进入 GraphRAG、Zep 或 Temporal Memory spike；不连接 GraphRAG/Zep/图数据库/向量库/reranker，不调用真实 embedding 或 LLM，不写 artifact，也不读取或返回明文 Key。

## 已完成

- Service：`get_graph_memory_trigger_evidence(slug, projects_dir=None, now=None)` 返回 `summary`、`trigger_gate`、`signals`、`candidate_layers`、`records`、`manifest` 与 `content_json`。
- API：`GET /api/stories/<slug>/graph-memory-trigger-evidence` 返回同一份只读触发证据；坏 slug 返回 400，缺项目返回 404。
- CLI：`lne memory graph-trigger <slug> --json` 输出同一份只读证据，适合无人值守脚本和本地诊断使用。
- API Contract / Typed Client：本地契约清单新增 `getGraphMemoryTriggerEvidence`，Graph Memory Offline Shadow Replay Report 接续完成后当前计数为 `endpoint_count=46`、`openapi_path_count=45`、`typed_client_method_count=45`。
- UI：项目工作台新增「GraphRAG / Zep 触发证据」面板，展示 Graph 状态、趋势样本、词面缺口、关系/因果/状态信号、候选层和边界提醒。
- 测试：新增 `tests/test_graph_memory_trigger_evidence.py`，覆盖 service、非触发项目、HTTP、CLI、密钥/路径不泄漏。

## 验证

- Focused：`python -m pytest tests/test_graph_memory_trigger_evidence.py tests/test_api_contract.py tests/test_v093_graph_memory_trigger.py -q` -> `10 passed`。
- 前端：`cd engine/ui && pnpm.cmd run build` 通过。
- 浏览器烟测：本地后端 + Vite 下打开项目工作台，确认「GraphRAG / Zep 触发证据」面板显示可做探针、趋势样本、词面缺口、GraphRAG/Zep 候选层和外部服务暂缓边界。
- 全量基线：Graph Memory Offline Shadow Replay Report 接续完成后 `python -m pytest -q` -> `803 passed`；`cd engine/ui && pnpm run build` 通过；根目录 `git diff --check` 通过。

## 边界

- 不读取、不返回、不记录 `LLM_API_KEY` / `SEEDREAM_API_KEY` 明文或环境变量名。
- 不写 `projects/` 或 `outputs/` 下的 trigger evidence artifact。
- 不改变 `retrieve_context`、`run_scene`、`canon_ledger.jsonl`、`state_snapshot.json` 或任何既有 artifact 契约。
- 不把 trigger evidence 当成真实 GraphRAG / Zep / Temporal Memory 接入开关；它只提供 spike 前证据。

## 下一步建议

`Graph Memory Spike Design Pack MVP`、`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP` 与 `Graph Memory Provider Boundary Matrix MVP` 已接续收口。下一刀建议做 `Graph Memory Provider Spike Fixture Pack MVP`：基于 offline replay report 整理 provider spike fixture pack，继续保持只读、mockable、无外部服务依赖。
