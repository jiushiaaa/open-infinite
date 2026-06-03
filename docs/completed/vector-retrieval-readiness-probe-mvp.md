# Embedding / Vector Retrieval Readiness Probe MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第九刀，向量检索接入前的只读召回压力评估。  
> 范围：聚合导入规模、检索语料、canon ledger、entity aliases、现有 BM25 retrieval probe 与可选失败样本；不生成 embedding，不接向量库，不写 artifact。

## 1. 目标

本 MVP 用于回答“现在是否真的需要 embedding / 向量库”。它不直接接 Qdrant、Milvus、Pinecone、Weaviate、GraphRAG、Zep 或 reranker，而是先把现有 BM25 + canon ledger + entity aliases 的状态、规模压力和失败证据展示清楚。

## 2. 已完成

- 新增 service：`living_novel_engine.service.get_vector_retrieval_readiness()`。
- 新增 API：`GET /api/stories/{slug}/vector-retrieval-readiness`。
- 新增前端 client：`api.getVectorRetrievalReadiness()`。
- 新增前端类型：`VectorRetrievalReadinessReport`、`VectorRetrievalReadinessSignal`、`VectorRetrievalCandidateLayer`。
- 长篇项目工作台新增「向量检索就绪」只读面板，展示：
  - 章节数、字数、检索语料规模。
  - BM25 账本探针命中率。
  - `memory/retrieval_failure_samples.jsonl` 中的换说法召回失败样本。
  - 别名覆盖与账本实体覆盖。
  - Embedding、向量库、reranker、GraphRAG/Zep 的候选状态。

## 3. API 契约

返回核心字段：

```json
{
  "version": "embedding-vector-readiness-probe-mvp",
  "mode": "read_only_vector_retrieval_readiness",
  "status": "ready | attention | monitor | triggered",
  "summary": {
    "chapter_count": 55,
    "character_count": 1200000,
    "corpus_item_count": 42,
    "retrieval_probe_hit_rate": 1.0,
    "saved_failure_sample_count": 0,
    "writes_artifacts": false,
    "external_services_required": false,
    "uses_embedding": false,
    "uses_vector_store": false,
    "uses_reranker": false,
    "plaintext_key_returned": false
  },
  "signals": [],
  "candidate_layers": [],
  "failure_samples": [],
  "boundaries": [],
  "next_steps": []
}
```

状态含义：

- `ready`：当前 BM25 + ledger + aliases 仍够用。
- `attention`：先修复 canon ledger、entity aliases 或探针样本，不把基础记忆缺口误判为向量需求。
- `monitor`：项目规模或语料规模进入监控，但尚无明确 BM25 失败证据。
- `triggered`：已有 BM25 探针弱命中或本地失败样本，可进入 mockable embedding / 向量检索 spike。

## 4. 安全边界

- 不读取 `.env` 或明文密钥。
- 不调用真实 LLM、embedding provider、Seedream 或外部 HTTP 服务。
- 不生成 embedding，不创建向量索引，不连接向量库。
- 不写 `retrieval_failure_samples.jsonl` 或任何项目 artifact；该文件若存在仅作为人工/后续工具保存的失败样本读取。
- 不替换 `retrieve_context()`、不改变 `run_scene` 默认行为，不影响既有 `retrieval_context.json` 和 Prompt Budget Pack。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_vector_retrieval_readiness.py -q
python -m pytest engine\tests\test_vector_retrieval_readiness.py engine\tests\test_api_contract.py -q
cd engine\ui
pnpm.cmd run build
cd ..
python -m pytest -q
```

当前后端全量基线：`803 passed`。

## 6. 后续状态

`Embedding Evaluation Samples MVP` 已在后续第十刀收口，见 `embedding-evaluation-samples-mvp.md`。`Retrieval Failure Sample Authoring MVP`、`Memory CLI MVP`、`Retrieval Sample Export Pack MVP`、`Embedding Mock Evaluation Report MVP`、`Retrieval Sample Replay Report MVP`、`Retrieval Sample Migration Pack MVP`、`Cross Project Retrieval Samples Index MVP`、`Retrieval Samples Trend Snapshot MVP`、`GraphRAG / Zep Trigger Evidence MVP`、`Graph Memory Spike Design Pack MVP`、`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已在后续第十一至二十五刀收口，见 `retrieval-failure-sample-authoring-mvp.md`、`memory-cli-mvp.md`、`retrieval-sample-export-pack-mvp.md`、`embedding-mock-evaluation-report-mvp.md`、`retrieval-sample-replay-report-mvp.md`、`retrieval-sample-migration-pack-mvp.md`、`cross-project-retrieval-samples-index-mvp.md`、`retrieval-samples-trend-snapshot-mvp.md`、`graph-memory-trigger-evidence-mvp.md`、`graph-memory-spike-design-pack-mvp.md`、`graph-memory-shadow-compare-pack-mvp.md`、`graph-memory-shadow-case-matrix-mvp.md`、`graph-memory-provider-boundary-matrix-mvp.md`、`graph-memory-offline-shadow-replay-plan-mvp.md` 与 `graph-memory-offline-shadow-replay-report-mvp.md`。后续建议进入 `Graph Memory Provider Spike Fixture Pack MVP`：继续不接真实 provider，只做单 provider dry-run 前置包。
