# Embedding Evaluation Samples MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第十刀，embedding 接入前的失败样本评估与 mock 对照。  
> 范围：读取 `memory/retrieval_failure_samples.jsonl`，比较现有 BM25 命中与 deterministic mock semantic oracle；不调用真实 embedding provider，不创建向量索引，不写 artifact。

## 1. 目标

本 MVP 用于把“BM25 找不到换说法的相关内容”从直觉变成可评估样本。每条失败样本至少包含 `query` 和 `expected_entities`；系统会用当前 BM25 检索链路复跑，再用期望实体是否能定位到 canon ledger 目标作为 mock semantic oracle，对比是否存在词面召回缺口。

## 2. 已完成

- 新增 service：`living_novel_engine.service.get_embedding_evaluation_samples()`。
- 新增 API：`GET /api/stories/{slug}/embedding-evaluation-samples`。
- 新增前端 client：`api.getEmbeddingEvaluationSamples()`。
- 新增前端类型：`EmbeddingEvaluationSamplesReport`、`EmbeddingEvaluationSample`。
- 长篇项目工作台新增「Embedding 样本评估」只读面板，展示：
  - 样本数、BM25 命中数、mock 命中数、词面缺口数。
  - 样本 schema：必填 `query`、`expected_entities`，可选 `expected_item_id`、`expected_source`、`reason`、`current_chapter`。
  - 每条样本的 `already_covered`、`lexical_gap`、`memory_gap` 或 `invalid_sample` 诊断。

## 3. API 契约

返回核心字段：

```json
{
  "version": "embedding-evaluation-samples-mvp",
  "mode": "read_only_embedding_evaluation_samples",
  "status": "insufficient_samples | candidate | attention | blocked | covered",
  "summary": {
    "sample_count": 1,
    "bm25_hit_count": 0,
    "mock_embedding_hit_count": 1,
    "lexical_gap_count": 1,
    "memory_gap_count": 0,
    "writes_artifacts": false,
    "external_services_required": false,
    "uses_embedding_provider": false,
    "uses_vector_store": false,
    "plaintext_key_returned": false
  },
  "samples": [],
  "sample_schema": {
    "path": "memory/retrieval_failure_samples.jsonl",
    "required": ["query", "expected_entities"]
  },
  "boundaries": [],
  "next_steps": []
}
```

诊断含义：

- `lexical_gap`：BM25 未命中，但期望实体能定位到本地账本目标，可进入 mock embedding 对照。
- `memory_gap`：BM25 未命中，mock oracle 也找不到目标，先补账本或样本实体。
- `already_covered`：当前 BM25 已命中，暂不证明 embedding 有收益。
- `invalid_sample`：样本缺必填字段或 JSONL 损坏，先修复样本。

## 4. 安全边界

- 不读取 `.env` 或明文密钥。
- 不调用真实 LLM、embedding provider、Seedream 或外部 HTTP 服务。
- 不生成 embedding，不创建向量索引，不连接向量库。
- 不写 `retrieval_failure_samples.jsonl`；当前只读取本地已有样本。
- 不替换 `retrieve_context()`、不改变 `run_scene` 默认行为，不影响既有 `retrieval_context.json` 和 Prompt Budget Pack。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_embedding_evaluation_samples.py -q
python -m pytest engine\tests\test_embedding_evaluation_samples.py engine\tests\test_api_contract.py -q
python -m pytest engine\tests\test_embedding_evaluation_samples.py engine\tests\test_vector_retrieval_readiness.py engine\tests\test_v093_retrieval_probe.py engine\tests\test_prompt_budget_pack.py engine\tests\test_api_contract.py -q
cd engine\ui
pnpm.cmd run build
```

浏览器烟测：本地后端 + Vite 下打开 `my-story` 项目工作台，确认「Embedding 样本评估」面板显示待收集空态、样本 schema 与 mock oracle 边界。

当前后端全量基线：`803 passed`。

## 6. 下一刀

`Retrieval Failure Sample Authoring MVP` 已在后续第十一刀收口，见 `retrieval-failure-sample-authoring-mvp.md`：项目工作台可以安全追加本地失败样本，写入后刷新本评估面板。`Memory CLI MVP` 已在后续第十二刀收口，见 `memory-cli-mvp.md`。`Retrieval Sample Export Pack MVP` 已在后续第十三刀收口，见 `retrieval-sample-export-pack-mvp.md`。`Embedding Mock Evaluation Report MVP` 已在后续第十四刀收口，见 `embedding-mock-evaluation-report-mvp.md`。`Retrieval Sample Replay Report MVP` 已在后续第十五刀收口，见 `retrieval-sample-replay-report-mvp.md`。`Retrieval Sample Migration Pack MVP` 已在后续第十六刀收口，见 `retrieval-sample-migration-pack-mvp.md`。`Cross Project Retrieval Samples Index MVP`、`Retrieval Samples Trend Snapshot MVP`、`GraphRAG / Zep Trigger Evidence MVP`、`Graph Memory Spike Design Pack MVP`、`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已在后续第十七至二十五刀收口，见 `cross-project-retrieval-samples-index-mvp.md`、`retrieval-samples-trend-snapshot-mvp.md`、`graph-memory-trigger-evidence-mvp.md`、`graph-memory-spike-design-pack-mvp.md`、`graph-memory-shadow-compare-pack-mvp.md`、`graph-memory-shadow-case-matrix-mvp.md`、`graph-memory-provider-boundary-matrix-mvp.md`、`graph-memory-offline-shadow-replay-plan-mvp.md` 与 `graph-memory-offline-shadow-replay-report-mvp.md`。后续 `Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已收口，下一刀建议进入 `Graph Memory Provider Spike Fixture Pack MVP`，继续不接真实 provider。
