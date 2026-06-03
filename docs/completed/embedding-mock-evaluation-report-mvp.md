# Embedding Mock Evaluation Report MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第十四刀，检索失败样本的 mock embedding 对照报告。  
> 范围：新增 service/API/UI/CLI，把本地失败样本分桶为 `lexical_gap`、`memory_gap`、`already_covered`、`invalid_sample`，输出 candidate gate 与 Markdown report；不写 artifact，不调用真实 embedding provider，不创建向量索引，不连接外部服务。

## 1. 背景

Retrieval Sample Export Pack 已把失败样本整理成 Markdown 与 manifest。第十四刀继续向产品化推进：把“可导出”升级为“可判定”，用 deterministic mock semantic oracle 给出是否值得继续扩大 embedding spike 的 gate，而不是凭单条样本主观判断。

## 2. 已完成

- 新增 `get_embedding_mock_evaluation_report(slug)`，复用导出包和 embedding 样本评估结果，返回 `summary`、`gate`、`buckets`、`report_md`、`warnings` 和边界说明。
- 新增 `GET /api/stories/<slug>/embedding-mock-evaluation-report`，坏 slug 返回 400，缺项目返回 404。
- 新增前端 typed client `getEmbeddingMockEvaluationReport` 与类型 `EmbeddingMockEvaluationReport`。
- 项目工作台的 Embedding 样本评估面板新增「生成对照报告」按钮，展示状态、Gate、样本数、词面缺口和 Markdown 预览。
- CLI 新增 `lne memory mock-report <slug> [--json] [--require-candidate]`。
- OpenAPI / Typed Client 契约清单已由后续 Graph Memory Offline Shadow Replay Report MVP 更新为 `endpoint_count=46`、`openapi_path_count=45`、`typed_client_method_count=45`。

## 3. Gate 口径

- `candidate`：存在至少 1 条 `lexical_gap`，即 BM25 未命中但 mock semantic oracle 能定位目标事实。
- `needs_samples`：暂无失败样本。
- `needs_memory`：存在 `memory_gap`，先补 canon ledger 或 expected_entities。
- `blocked`：样本损坏或必填字段缺失。
- `covered`：样本已被 BM25 覆盖，暂不需要 embedding spike。

## 4. 边界

- 不写 `memory/retrieval_failure_samples.jsonl`，不生成新 artifact。
- 不生成 embedding，不接 Qdrant / Milvus / Pinecone / Weaviate。
- 不连接 GraphRAG、Zep、reranker 或长期记忆服务。
- 不读取、不返回、不记录明文 Key。
- 不替换 `retrieve_context`，不改变 `run_scene` 默认行为。

## 5. 验证

```powershell
cd D:\AI\open-infinite\engine
python -m pytest engine\tests\test_embedding_mock_evaluation_report.py -q
python -m pytest engine\tests\test_embedding_mock_evaluation_report.py engine\tests\test_retrieval_sample_export_pack.py engine\tests\test_memory_cli.py engine\tests\test_retrieval_failure_samples.py engine\tests\test_embedding_evaluation_samples.py engine\tests\test_api_contract.py -q
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

浏览器烟测：临时项目 `mock-report-ui` 打开 `/#/workspace/mock-report-ui`，点击「生成对照报告」后，页面显示「可继续评估」、Gate 通过、失败 query 和 `mock embedding 值得进入下一步评估` 结论。

当前后端全量基线：`803 passed`。

## 6. 下一刀

`Retrieval Sample Replay Report MVP` 已在后续第十五刀收口，见 `retrieval-sample-replay-report-mvp.md`：失败样本可生成当前检索 case report。`Retrieval Sample Migration Pack MVP` 已在后续第十六刀收口，见 `retrieval-sample-migration-pack-mvp.md`。`Cross Project Retrieval Samples Index MVP`、`Retrieval Samples Trend Snapshot MVP`、`GraphRAG / Zep Trigger Evidence MVP`、`Graph Memory Spike Design Pack MVP`、`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已在后续第十七至二十五刀收口，见 `cross-project-retrieval-samples-index-mvp.md`、`retrieval-samples-trend-snapshot-mvp.md`、`graph-memory-trigger-evidence-mvp.md`、`graph-memory-spike-design-pack-mvp.md`、`graph-memory-shadow-compare-pack-mvp.md`、`graph-memory-shadow-case-matrix-mvp.md`、`graph-memory-provider-boundary-matrix-mvp.md`、`graph-memory-offline-shadow-replay-plan-mvp.md` 与 `graph-memory-offline-shadow-replay-report-mvp.md`。后续 `Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已收口，下一刀建议进入 `Graph Memory Provider Spike Fixture Pack MVP`，继续不接真实 provider，先把单 provider dry-run fixture、成本/隐私/回滚和人工验收清单做成前置包。
