# Retrieval Sample Migration Pack MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第十六刀，检索失败样本的只读迁移评测集包。  
> 范围：新增 service/API/UI/CLI，把 replay case 整理为稳定 retrieval eval records、manifest 与 `content_json`；不写迁移包 artifact，不调用真实 embedding provider，不创建向量索引，不连接外部服务。

## 1. 背景

Retrieval Sample Replay Report 已能输出当前检索 case report。第十六刀继续向产品化推进：把仍有断言目标的 case 规整成稳定评测输入，让后续检索策略、跨项目索引或真实 embedding spike 有可复跑的 records，而不是继续依赖临时报告。

## 2. 已完成

- 新增 `get_retrieval_sample_migration_pack(slug)`，复用 replay report，返回 `summary`、`migration_gate`、`records`、`manifest`、`content_json`、`warnings` 和边界说明。
- 新增 `GET /api/stories/<slug>/retrieval-sample-migration-pack`，坏 slug 返回 400，缺项目返回 404。
- 新增前端 typed client `getRetrievalSampleMigrationPack` 与类型 `RetrievalSampleMigrationPackReport`。
- 项目工作台的 Embedding 样本评估面板新增「生成迁移包」按钮，展示状态、Gate、record 数、跳过数和 JSON 预览。
- CLI 新增 `lne memory migration-pack <slug> [--json]`。
- OpenAPI / Typed Client 契约清单已由后续 Graph Memory Offline Shadow Replay Report MVP 更新为 `endpoint_count=46`、`openapi_path_count=45`、`typed_client_method_count=45`。

## 3. Gate 口径

- `ready`：存在可迁移 eval records，可作为后续检索策略对照输入。
- `needs_samples`：暂无失败样本。
- `needs_migratable_cases`：有 case，但缺少可断言目标项。
- `blocked`：样本损坏或存在无效 case。

## 4. 边界

- 不写 `memory/retrieval_failure_samples.jsonl`，不生成 migration pack artifact。
- 不生成 embedding，不接 Qdrant / Milvus / Pinecone / Weaviate。
- 不连接 GraphRAG、Zep、reranker 或长期记忆服务。
- 不读取、不返回、不记录明文 Key。
- 不替换 `retrieve_context`，不改变 `run_scene` 默认行为。

## 5. 验证

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests\test_retrieval_sample_migration_pack.py -q
python -m pytest tests\test_retrieval_sample_migration_pack.py tests\test_retrieval_sample_replay_report.py tests\test_embedding_mock_evaluation_report.py tests\test_retrieval_sample_export_pack.py tests\test_memory_cli.py tests\test_retrieval_failure_samples.py tests\test_embedding_evaluation_samples.py tests\test_api_contract.py -q
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

浏览器烟测：临时项目 `migration-pack-ui` 打开 `/#/workspace/migration-pack-ui`，点击「生成迁移包」后，页面显示「迁移包：可迁移」、Gate 通过、`Records：1`、`migration-pack-ui-retrieval-eval-001` 和 `canon_ledger:canon_000001`。

当前后端全量基线：`803 passed`。

## 6. 下一刀

`Cross Project Retrieval Samples Index MVP`、`Retrieval Samples Trend Snapshot MVP`、`GraphRAG / Zep Trigger Evidence MVP`、`Graph Memory Spike Design Pack MVP`、`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已在后续第十七至二十五刀收口，见 `cross-project-retrieval-samples-index-mvp.md`、`retrieval-samples-trend-snapshot-mvp.md`、`graph-memory-trigger-evidence-mvp.md`、`graph-memory-spike-design-pack-mvp.md`、`graph-memory-shadow-compare-pack-mvp.md`、`graph-memory-shadow-case-matrix-mvp.md`、`graph-memory-provider-boundary-matrix-mvp.md`、`graph-memory-offline-shadow-replay-plan-mvp.md` 与 `graph-memory-offline-shadow-replay-report-mvp.md`。后续 `Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已收口，下一刀建议进入 `Graph Memory Provider Spike Fixture Pack MVP`：继续不接真实 provider，先把单 provider dry-run fixture、成本/隐私/回滚和人工验收清单做成前置包。
