# Graph Memory Provider Spike Manual Mock Adapter Review MVP

> 日期：2026-06-03  
> 范围：基于 mock-compatible adapter 规格生成只读人工复核包与合规检查。  
> 状态：已收口；本刀后按用户要求暂停继续开发。

## 做了什么

- 新增 `get_graph_memory_provider_spike_manual_mock_adapter_review()`，从 mock-compatible adapter 规格派生人工复核包。
- 新增只读 API：`GET /api/stories/<slug>/graph-memory-provider-spike-manual-mock-adapter-review`。
- 新增 CLI：`lne memory graph-manual-mock-adapter-review <slug> --json`。
- 项目工作台新增「Graph 记忆 Provider Spike Manual Mock Adapter Review」面板，展示复核行、合规检查、阻断计数、暂停建议和边界说明。
- OpenAPI / Typed Client contract 新增 endpoint、类型和 `getGraphMemoryProviderSpikeManualMockAdapterReview()`。

## 报告内容

- `review_rows`：按 adapter spec 展示 provider、service target、required methods、fixture bindings、人工复核提示和 mock-only 安全边界。
- `compliance_checks`：检查 local mock only、禁止真实 provider call、禁止明文 Key、禁止 artifact write、contract methods 完整性。
- `manual_mock_adapter_review`：只读复核包状态、计数、保存禁止状态和暂停标记。
- `decision`：明确建议人工复核后暂停继续开发，不自动进入真实 provider 链路。

## 边界

- 不保存人工复核结论。
- 不创建真实 provider adapter 或真实 provider 配置。
- 不写项目 artifact。
- 不读取、不返回、不记录明文 Key。
- 不调用 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不替换 BM25、canon ledger、entity aliases、retrieval_context 或 `run_scene` 默认行为。

## 验证

- `python -m pytest tests/test_graph_memory_provider_spike_manual_mock_adapter_review.py -q` -> `4 passed`
- `python -m pytest tests/test_api_contract.py -q` -> `3 passed`
- `cd engine/ui && pnpm.cmd run build` 通过

## 暂停点

本刀完成后暂停继续开发。恢复时先由用户明确下一步；不要自动接真实 provider、生产向量库、GraphRAG、Zep 或外部 embedding provider。
