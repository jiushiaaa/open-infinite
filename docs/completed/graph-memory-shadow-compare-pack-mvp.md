# Graph Memory Shadow Compare Pack MVP 收口说明

> 日期：2026-06-01  
> 范围：后续增强第二十一刀，重型记忆候选层的本地只读 shadow 对照包。

## 收口结论

Graph Memory Shadow Compare Pack MVP 已收口。系统新增只读 service/API/CLI/项目工作台面板，把 Graph Memory Spike Design Pack 与本地 eval records 转成 GraphRAG、Zep、Temporal Memory 候选层的 shadow 对照：候选收益、风险分、样本案例、验收结果、回退策略和 no-go 条件。

该切片不连接 GraphRAG/Zep/图数据库/向量库/reranker，不调用真实 embedding 或 LLM，不写 artifact，也不改变 BM25、canon ledger、entity aliases、retrieval_context 或 `run_scene` 默认行为。

## 已完成

- Service：`get_graph_memory_shadow_compare_pack(slug, projects_dir=None, now=None)` 返回 `summary`、`shadow_gate`、`comparisons`、`sample_cases`、`acceptance_results`、`no_go_conditions`、`manifest` 与 `content_json`。
- API：`GET /api/stories/<slug>/graph-memory-shadow-compare-pack` 返回同一份只读对照包；坏 slug 返回 400，缺项目返回 404。
- CLI：`lne memory graph-shadow <slug> --json` 输出同一份只读对照包，适合无人值守脚本和本地诊断使用。
- API Contract / Typed Client：本地契约清单新增 `getGraphMemoryShadowComparePack`；Graph Memory Offline Shadow Replay Report 接续完成后当前计数为 `endpoint_count=46`、`openapi_path_count=45`、`typed_client_method_count=45`。
- UI：项目工作台新增「Graph 记忆 Shadow 对照」面板，展示对照状态、候选层、样本、最高收益、验收结果、no-go 条件和外部服务暂缓边界。
- 测试：新增 `tests/test_graph_memory_shadow_compare_pack.py`，覆盖 service、非触发项目、HTTP、CLI、密钥/路径不泄漏。

## 验证

- RED：新增 focused tests 后先确认缺少 `get_graph_memory_shadow_compare_pack` 入口导致失败。
- Focused：`python -m pytest tests/test_graph_memory_shadow_compare_pack.py tests/test_api_contract.py tests/test_graph_memory_spike_design_pack.py tests/test_graph_memory_trigger_evidence.py -q` -> `15 passed`。
- 前端：`cd engine/ui && pnpm.cmd run build` 通过。
- 浏览器烟测：本地后端 + Vite 下打开项目工作台，确认「Graph 记忆 Shadow 对照」面板显示对照就绪、GraphRAG/Zep 候选、样本案例、验收结果、no-go 条件和外部服务暂缓边界。
- 全量基线：`python -m pytest -q` -> `803 passed`；`cd engine/ui && pnpm run build` 通过；根目录 `git diff --check` 通过。

## 边界

- 不读取、不返回、不记录 `LLM_API_KEY` / `SEEDREAM_API_KEY` 明文或环境变量名。
- 不写 `projects/` 或 `outputs/` 下的 shadow compare artifact。
- 不改变 `retrieve_context`、`run_scene`、`canon_ledger.jsonl`、`state_snapshot.json` 或任何既有 artifact 契约。
- 不把 shadow compare 当成真实 GraphRAG / Zep / Temporal Memory 接入开关；它只提供真实 opt-in spike 前的本地证据层。

## 下一步建议

后续 `Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已收口。下一刀建议做 `Graph Memory Provider Spike Fixture Pack MVP`：把人工复核结果整理成 provider spike fixture pack，继续不接真实外部服务。
