# Graph Memory Provider Spike Opt-in Human Signoff Schema Draft MVP

> 收口日期：2026-06-03
> 范围：后续增强第四十刀，Graph Memory Provider Spike opt-in 人工签收 schema 草案。

## 做了什么

- 新增只读 service：`get_graph_memory_provider_spike_opt_in_human_signoff_schema_draft()`。
- 新增 HTTP API：`GET /api/stories/<slug>/graph-memory-provider-spike-opt-in-human-signoff-schema-draft`。
- 新增 CLI：`lne memory graph-opt-in-human-signoff-schema <slug> --json`。
- 项目工作台新增「Graph 记忆 Provider Spike Opt-in 人工签收 Schema」面板。
- 本地 API contract 与 typed client 新增 `getGraphMemoryProviderSpikeOptInHumanSignoffSchemaDraft`。

## 输出内容

- `schema_draft`：只读 schema 草案状态、字段数量、保存禁止状态和真实 provider 禁止状态。
- `schema_sections`：按 provider / service target 分组的签收字段定义。
- `schema_fields`：从 final readiness summary 的未签收字段派生，包含字段名、标签、必填状态、来源字段、校验规则和输入存储边界。
- `validation_rules`：当前只定义非空人工文本和禁止自动 provider 配置两类规则。
- `schema_materials`、`manual_review_checklist`、`no_go_conditions`、`boundaries`：供人工复核和下一刀配置草案使用。

## 边界

- 不保存签名、签收值、风险确认、回滚确认或最终结论。
- 不写项目 artifact，不写决策账本，不创建真实 provider 配置。
- 不调用 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不读取、不返回、不记录明文 Key。
- 不改变 `run_scene` 默认行为，不替换 BM25、canon ledger、entity aliases 或 retrieval context。

## 验证

- RED：新增 focused tests 后，service、HTTP、CLI、API contract 入口缺失导致 6 failed / 1 passed。
- GREEN：`python -m pytest tests\test_graph_memory_provider_spike_opt_in_human_signoff_schema_draft.py tests\test_api_contract.py -q` -> 7 passed。
- 相邻回归：`python -m pytest <test_graph_memory*.py> tests\test_api_contract.py -q` -> 91 passed。
- 前端：`cd engine/ui && pnpm.cmd run build` 通过。

## 下一刀建议

进入 `Graph Memory Provider Spike Opt-in Config Draft MVP`：基于签收 schema 草案只读生成本地 opt-in 配置草案、字段映射和 adapter 边界，仍不保存配置、不读取明文 Key、不连接真实 provider。
