# Retrieval Sample Replay Report MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第十五刀，检索失败样本的只读复跑 case report。  
> 范围：新增 service/API/UI/CLI，把本地失败样本按当前检索能力复跑成 `still_failing_lexically`、`missing_memory_target`、`covered_by_current_retrieval`、`invalid_case`；不写 replay 历史，不调用真实 embedding provider，不创建向量索引，不连接外部服务。

## 1. 背景

Embedding Mock Evaluation Report 已能判断失败样本是否值得继续扩大 embedding spike。第十五刀继续向产品化推进：把样本从“对照报告”升级为“当前复跑 case report”，让用户看到每条样本在当前 BM25 + canon ledger + entity aliases 链路下仍失败、已覆盖、记忆缺失还是样本无效。

## 2. 已完成

- 新增 `get_retrieval_sample_replay_report(slug)`，复用 embedding 样本评估结果，返回 `summary`、`replay_gate`、`cases`、`report_md`、`warnings` 和边界说明。
- 新增 `GET /api/stories/<slug>/retrieval-sample-replay-report`，坏 slug 返回 400，缺项目返回 404。
- 新增前端 typed client `getRetrievalSampleReplayReport` 与类型 `RetrievalSampleReplayReport`。
- 项目工作台的 Embedding 样本评估面板新增「生成复跑报告」按钮，展示状态、Gate、case 数、仍是词面缺口数量和 Markdown 预览。
- CLI 新增 `lne memory replay-report <slug> [--json] [--require-clean]`。
- OpenAPI / Typed Client 契约清单已由后续 Graph Memory Offline Shadow Replay Report MVP 更新为 `endpoint_count=46`、`openapi_path_count=45`、`typed_client_method_count=45`。

## 3. Gate 口径

- `clean`：全部样本当前已覆盖，没有需要人工处理的 case。
- `needs_samples`：暂无失败样本。
- `needs_review`：存在仍是词面缺口、记忆缺口或无效样本，需要继续评估或修正。
- `blocked`：样本损坏或必填字段缺失。

## 4. 边界

- 不写 `memory/retrieval_failure_samples.jsonl`，不生成 replay 历史 artifact。
- 不生成 embedding，不接 Qdrant / Milvus / Pinecone / Weaviate。
- 不连接 GraphRAG、Zep、reranker 或长期记忆服务。
- 不读取、不返回、不记录明文 Key。
- 不替换 `retrieve_context`，不改变 `run_scene` 默认行为。

## 5. 验证

```powershell
cd D:\AI\open-infinite\engine
python -m pytest engine\tests\test_retrieval_sample_replay_report.py -q
python -m pytest engine\tests\test_retrieval_sample_replay_report.py engine\tests\test_embedding_mock_evaluation_report.py engine\tests\test_retrieval_sample_export_pack.py engine\tests\test_memory_cli.py engine\tests\test_retrieval_failure_samples.py engine\tests\test_embedding_evaluation_samples.py engine\tests\test_api_contract.py -q
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

浏览器烟测：临时项目 `replay-report-ui` 打开 `/#/workspace/replay-report-ui`，点击「生成复跑报告」后，页面显示「复跑报告：可复跑」、Gate 通过、`retrieval-case-001`、`still_failing_lexically` 和失败 query。

当前后端全量基线：`803 passed`。

## 6. 下一刀

`Retrieval Sample Migration Pack MVP` 已在后续第十六刀收口，见 `retrieval-sample-migration-pack-mvp.md`：复跑 case 可整理为稳定 eval records、manifest 与 `content_json`。`Cross Project Retrieval Samples Index MVP`、`Retrieval Samples Trend Snapshot MVP`、`GraphRAG / Zep Trigger Evidence MVP`、`Graph Memory Spike Design Pack MVP`、`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已在后续第十七至二十五刀收口，见 `cross-project-retrieval-samples-index-mvp.md`、`retrieval-samples-trend-snapshot-mvp.md`、`graph-memory-trigger-evidence-mvp.md`、`graph-memory-spike-design-pack-mvp.md`、`graph-memory-shadow-compare-pack-mvp.md`、`graph-memory-shadow-case-matrix-mvp.md`、`graph-memory-provider-boundary-matrix-mvp.md`、`graph-memory-offline-shadow-replay-plan-mvp.md` 与 `graph-memory-offline-shadow-replay-report-mvp.md`。后续 `Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已收口，下一刀建议进入 `Graph Memory Provider Spike Fixture Pack MVP`：继续不接真实 provider，先把单 provider dry-run fixture、成本/隐私/回滚和人工验收清单做成前置包。
