# Retrieval Samples Trend Snapshot MVP 收口说明

> 日期：2026-06-01  
> 范围：后续增强第十八刀，跨项目检索样本趋势快照。

## 收口结论

Retrieval Samples Trend Snapshot MVP 已收口。系统新增只读 service/API/CLI/设置页面板，复用 Cross Project Retrieval Samples Index 的本地索引结果，输出样本覆盖、词面缺口、空样本项目、blocked 项目和重型检索触发暂缓信号。

该切片不写趋势 artifact、不生成 embedding、不创建向量索引、不连接向量库 / GraphRAG / Zep / reranker，也不读取或返回明文 Key。

## 已完成

- Service：`get_retrieval_samples_trend_snapshot(projects_dir=None, now=None)` 返回 `summary`、`trend_gate`、`signals`、`project_trends`、`records`、`manifest` 与 `content_json`。
- API：`GET /api/settings/retrieval-samples-trend-snapshot` 返回同一份只读趋势快照。
- CLI：`lne memory trend-snapshot --json` 输出同一份只读趋势快照，适合无人值守脚本和本地诊断使用。
- API Contract / Typed Client：本地契约清单新增 `getRetrievalSamplesTrendSnapshot`，Graph Memory Offline Shadow Replay Report 接续完成后当前计数为 `endpoint_count=46`、`openapi_path_count=45`、`typed_client_method_count=45`。
- UI：设置抽屉新增「样本趋势快照」面板，展示词面缺口/已覆盖、空样本/损坏、趋势信号和项目趋势桶。
- 测试：新增 `tests/test_retrieval_samples_trend_snapshot.py`，覆盖 service、空项目、HTTP、CLI、密钥/路径不泄漏。

## 验证

- Focused：`python -m pytest tests/test_retrieval_samples_trend_snapshot.py tests/test_api_contract.py tests/test_cross_project_retrieval_samples_index.py -q` -> `11 passed`。
- 前端：`cd engine/ui && pnpm.cmd run build` 通过。
- 浏览器烟测：本地后端 + Vite 下打开设置抽屉，确认「样本趋势快照」面板显示词面缺口、空样本、重型检索暂缓信号与项目趋势桶。
- 全量基线：Graph Memory Offline Shadow Replay Report 接续完成后 `python -m pytest -q` -> `803 passed`；`cd engine/ui && pnpm run build` 通过；根目录 `git diff --check` 通过。

## 边界

- 不读取、不返回、不记录 `LLM_API_KEY` / `SEEDREAM_API_KEY` 明文或环境变量名。
- 不写 `projects/` 或 `outputs/` 下的趋势 artifact。
- 不改变 `retrieve_context`、`run_scene` 或任何既有 artifact 契约。
- 不把趋势快照当成真实 embedding / GraphRAG / Zep 接入开关；它只提供触发证据。

## 下一步建议

`GraphRAG / Zep Trigger Evidence MVP`、`Graph Memory Spike Design Pack MVP`、`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP`、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已接续收口。下一刀建议做 `Graph Memory Provider Spike Fixture Pack MVP`：基于 offline replay report 做 provider spike fixture pack，不默认接真实外部服务。
