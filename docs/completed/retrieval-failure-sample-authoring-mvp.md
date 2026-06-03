# Retrieval Failure Sample Authoring MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第十一刀，embedding 接入前的本地失败样本采集入口。  
> 范围：追加 `memory/retrieval_failure_samples.jsonl`，让真实换说法召回失败 query 可被安全记录、校验并复跑；不调用真实 embedding provider，不创建向量索引，不接外部服务。

## 1. 目标

上一刀已经能读取失败样本并做 BM25 vs mock semantic oracle 对照，但样本仍需要人工写 JSONL。本 MVP 补上工作台采集入口：用户在「Embedding 样本评估」面板输入失败查询、期望实体、章节和原因后，后端追加一条规范化 JSONL 样本，再刷新评估结果。

## 2. 已完成

- 新增 service：`living_novel_engine.service.get_retrieval_failure_samples()` 与 `add_retrieval_failure_sample()`。
- 新增 API：`GET /api/stories/{slug}/retrieval-failure-samples` 与 `POST /api/stories/{slug}/retrieval-failure-samples`。
- 新增前端 client：`api.getRetrievalFailureSamples()` 与 `api.addRetrievalFailureSample()`。
- 新增前端类型：`RetrievalFailureSamplesReport`、`RetrievalFailureSampleAppendRequest`、`RetrievalFailureSampleAppendResponse`。
- 项目工作台「Embedding 样本评估」面板新增本地记录表单，追加成功后刷新样本评估。
- API 契约清单同步到 33 个 endpoint、32 个 OpenAPI path、32 个 typed client method。

## 3. 写入契约

追加记录示例：

```json
{
  "schema_version": "retrieval-failure-sample-authoring-mvp",
  "id": "retrieval-sample-20260601160000-xxxxxxxx",
  "created_at": "2026-06-01T16:00:00",
  "query": "她必须追查那个遗失的关键物证",
  "expected_entities": ["mo_qing_yan", "retreat_bell"],
  "expected_item_id": "",
  "expected_source": "canon_ledger",
  "reason": "换说法后 BM25 未命中正史账本",
  "current_chapter": 2,
  "actual_top_sources": []
}
```

校验规则：

- `query` 必填，最长 180 字符。
- `expected_entities` 必填，支持数组或逗号/空白分隔文本，最多 10 项。
- `expected_source` 默认 `canon_ledger`，仅允许本地已知记忆层枚举。
- 文本字段拒绝疑似密钥内容，如 `LLM_API_KEY`、`SEEDREAM_API_KEY`、`OPENAI_API_KEY`、`sk-`、`sd-`、`secret`。
- 内置样例只读，写入返回 409；非法 slug 返回 400；缺项目返回 404。

## 4. 安全边界

- 仅追加本地 `memory/retrieval_failure_samples.jsonl`。
- 不读取 `.env` 或明文密钥。
- 不调用真实 LLM、embedding provider、Seedream 或外部 HTTP 服务。
- 不生成 embedding，不创建向量索引，不连接向量库、GraphRAG、Zep 或 reranker。
- 不替换 `retrieve_context()`，不改变 `run_scene` 默认行为。
- 不修改既有 `canon_ledger.jsonl`、`state_snapshot.json` 或运行分支 artifact。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_retrieval_failure_samples.py -q
python -m pytest engine\tests\test_retrieval_failure_samples.py engine\tests\test_embedding_evaluation_samples.py engine\tests\test_vector_retrieval_readiness.py engine\tests\test_api_contract.py -q
cd engine\ui
pnpm.cmd run build
cd ..
python -m pytest -q
```

浏览器烟测：本地后端 + Vite 使用 `.local-run/browser-smoke-projects/sample-story` 临时项目，打开项目工作台，在「Embedding 样本评估」表单记录失败查询后，面板从“暂无失败样本”刷新为包含该 query 的“词面缺口”样本；页面仍显示未调用真实 embedding provider 的边界。

当前后端全量基线：`803 passed`。

## 6. 下一刀

`Memory CLI MVP` 已在后续第十二刀收口，见 `memory-cli-mvp.md`：命令行可以追加失败样本、复跑样本评估、输出 JSON，并用 `--require-candidate` 进入自动化检查。`Retrieval Sample Export Pack MVP` 已在后续第十三刀收口，见 `retrieval-sample-export-pack-mvp.md`：失败样本可以只读导出为 Markdown 与 manifest。`Embedding Mock Evaluation Report MVP` 已在后续第十四刀收口，见 `embedding-mock-evaluation-report-mvp.md`。`Retrieval Sample Replay Report MVP` 已在后续第十五刀收口，见 `retrieval-sample-replay-report-mvp.md`。`Retrieval Sample Migration Pack MVP` 已在后续第十六刀收口，见 `retrieval-sample-migration-pack-mvp.md`。`Cross Project Retrieval Samples Index MVP`、`Retrieval Samples Trend Snapshot MVP`、`GraphRAG / Zep Trigger Evidence MVP`、`Graph Memory Spike Design Pack MVP`、`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP`、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已在后续第十七至二十五刀收口，见 `cross-project-retrieval-samples-index-mvp.md`、`retrieval-samples-trend-snapshot-mvp.md`、`graph-memory-trigger-evidence-mvp.md`、`graph-memory-spike-design-pack-mvp.md`、`graph-memory-shadow-compare-pack-mvp.md`、`graph-memory-shadow-case-matrix-mvp.md`、`graph-memory-provider-boundary-matrix-mvp.md`、`graph-memory-offline-shadow-replay-plan-mvp.md` 与 `graph-memory-offline-shadow-replay-report-mvp.md`。后续 `Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP`、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已收口，下一刀建议进入 `Graph Memory Provider Spike Fixture Pack MVP`。
