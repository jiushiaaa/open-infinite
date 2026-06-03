# Graph Memory Provider Spike Opt-in Config and Adapter Slices MVP

> 日期：2026-06-03  
> 范围：Graph Memory Provider Spike Opt-in Config Draft、Local Provider Contract / Adapter Boundary、Single Fixture Dry-run Harness、Mock-compatible Adapter 四刀。  
> 状态：已收口。

## 做了什么

- 新增只读 service/API/CLI/UI 链路：
  - `graph-memory-provider-spike-opt-in-config-draft`
  - `graph-memory-provider-spike-local-provider-contract`
  - `graph-memory-provider-spike-single-fixture-dry-run-harness`
  - `graph-memory-provider-spike-mock-compatible-adapter`
- 这四刀沿 `human signoff schema -> config draft -> local contract -> dry-run harness -> mock adapter` 逐步派生：
  - 本地 opt-in 配置草案、字段映射和 adapter 边界。
  - 本地 provider contract、mock-only 方法约束和 adapter boundary。
  - 单 fixture dry-run harness，限定 `local_mock_only`。
  - mock-compatible adapter 规格、方法实现要求和 validation cases。
- 项目工作台新增四个只读面板，展示状态、计数、首条配置/contract/harness/adapter、边界说明和下一步建议。
- OpenAPI / Typed Client contract 新增四个 endpoint 与四个前端 client method。

## API / CLI

API：

```text
GET /api/stories/<slug>/graph-memory-provider-spike-opt-in-config-draft
GET /api/stories/<slug>/graph-memory-provider-spike-local-provider-contract
GET /api/stories/<slug>/graph-memory-provider-spike-single-fixture-dry-run-harness
GET /api/stories/<slug>/graph-memory-provider-spike-mock-compatible-adapter
```

CLI：

```text
lne memory graph-opt-in-config-draft <slug> --json
lne memory graph-local-provider-contract <slug> --json
lne memory graph-single-fixture-dry-run-harness <slug> --json
lne memory graph-mock-compatible-adapter <slug> --json
```

## 边界

- 不保存配置、不保存签收值、不写项目 artifact。
- 不读取、不返回、不记录明文 Key。
- 不创建真实 provider 配置或真实 adapter。
- 不调用 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不替换 BM25、canon ledger、entity aliases、retrieval_context 或 `run_scene` 默认行为。

## 验证

- `python -m pytest tests/test_graph_memory_provider_spike_opt_in_config_and_adapter_slices.py tests/test_api_contract.py -q` -> `8 passed`
- `cd engine/ui && pnpm run build` 通过

## 接续状态

已接续完成 `Graph Memory Provider Spike Manual Mock Adapter Review MVP`，对 mock adapter 规格生成只读人工复核包与合规检查；仍不接真实 provider。
