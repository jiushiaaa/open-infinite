# Retrieval Sample Export Pack MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第十三刀，检索失败样本的只读导出包。  
> 范围：新增 service/API/UI/CLI，把本地失败样本与 BM25 vs mock semantic oracle 评估整理为 Markdown `content_md` 与 JSON manifest；不写 artifact，不调用真实 embedding provider，不创建向量索引，不连接外部服务。

## 1. 背景

失败样本已经能在工作台追加，也能通过 `lne memory samples` 复跑候选检查。下一步需要把这些样本变成可迁移、可复盘的评测证据，而不是继续停留在单项目 JSONL。Retrieval Sample Export Pack MVP 做的是只读导出包：把同一套评估结果整理成 Markdown 和 manifest，方便后续做批量 replay report 或 mock evaluation report。

## 2. 已完成

- 新增 `get_retrieval_sample_export_pack(slug)`，复用 `get_embedding_evaluation_samples`，返回 `status`、`summary`、`manifest`、`content_md`、`warnings` 和边界说明。
- 新增 `GET /api/stories/<slug>/retrieval-sample-export-pack`，坏 slug 返回 400，缺项目返回 404。
- 新增前端 typed client `getRetrievalSampleExportPack` 与类型 `RetrievalSampleExportPackReport`。
- 项目工作台的 Embedding 样本评估面板新增「预览导出包」按钮，展示导出文件名、状态、样本数、词面缺口和 Markdown 预览。
- CLI 新增 `lne memory export-samples <slug> [--json]`，默认输出 Markdown，`--json` 输出完整报告。
- OpenAPI / Typed Client 契约清单已由后续 Graph Memory Offline Shadow Replay Report MVP 更新为 `endpoint_count=46`、`openapi_path_count=45`、`typed_client_method_count=45`。

## 3. 边界

- 不写 `memory/retrieval_failure_samples.jsonl`，不生成新 artifact。
- 不生成 embedding，不接 Qdrant / Milvus / Pinecone / Weaviate。
- 不连接 GraphRAG、Zep、reranker 或长期记忆服务。
- 不读取、不返回、不记录明文 Key。
- 不替换 `retrieve_context`，不改变 `run_scene` 默认行为。

## 4. 验证

```powershell
cd D:\AI\open-infinite\engine
python -m pytest engine\tests\test_retrieval_sample_export_pack.py -q
python -m pytest engine\tests\test_retrieval_sample_export_pack.py engine\tests\test_memory_cli.py engine\tests\test_retrieval_failure_samples.py engine\tests\test_embedding_evaluation_samples.py engine\tests\test_api_contract.py -q
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

浏览器烟测：临时项目 `export-pack-ui` 打开 `/#/workspace/export-pack-ui`，点击「预览导出包」后，页面显示 `export-pack-ui-retrieval-samples.md`、状态「可导出」、失败 query 和 `canon_ledger:canon_000001`。

当前后端全量基线：`803 passed`。

## 5. 下一刀

`Embedding Mock Evaluation Report MVP` 已在后续第十四刀收口，见 `embedding-mock-evaluation-report-mvp.md`：失败样本可生成 candidate gate、分桶样本和 Markdown 对照报告。`Retrieval Sample Replay Report MVP` 已在后续第十五刀收口，见 `retrieval-sample-replay-report-mvp.md`。`Retrieval Sample Migration Pack MVP` 已在后续第十六刀收口，见 `retrieval-sample-migration-pack-mvp.md`。`Cross Project Retrieval Samples Index MVP`、`Retrieval Samples Trend Snapshot MVP`、`GraphRAG / Zep Trigger Evidence MVP`、`Graph Memory Spike Design Pack MVP`、`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已在后续第十七至二十五刀收口，见 `cross-project-retrieval-samples-index-mvp.md`、`retrieval-samples-trend-snapshot-mvp.md`、`graph-memory-trigger-evidence-mvp.md`、`graph-memory-spike-design-pack-mvp.md`、`graph-memory-shadow-compare-pack-mvp.md`、`graph-memory-shadow-case-matrix-mvp.md`、`graph-memory-provider-boundary-matrix-mvp.md`、`graph-memory-offline-shadow-replay-plan-mvp.md` 与 `graph-memory-offline-shadow-replay-report-mvp.md`。后续 `Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已收口，下一刀建议进入 `Graph Memory Provider Spike Fixture Pack MVP`，继续不接真实 provider。
