# Graph Memory Provider Spike Opt-in Decision Ledger Preview MVP 收口说明

日期：2026-06-03

## 目标

把 `Graph Memory Provider Spike Opt-in Review Packet` 继续收束为只读决策账本预览。这个预览只回答“哪些 provider 行仍被阻塞、人工签收字段应该长什么样、真实 provider 为什么仍不可启用”，不保存签收，也不写入真实决策账本。

本切片继续保持本地、只读、可回滚：

- 不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不写项目 artifact，不改变 `run_scene` 默认行为。
- 不覆盖 `canon_ledger.jsonl`、`state_snapshot.json`、`retrieval_context.json` 或既有检索上下文。
- 不保存人工签名、人工复核结果、审批状态或决策账本。
- 不读取、不返回、不记录明文 Key。

## 本次新增

### Service

新增 `living_novel_engine.service.get_graph_memory_provider_spike_opt_in_decision_ledger_preview(slug, projects_dir=None, now=None)`。

报告字段包括：

- `summary`：来源 review packet 状态、provider 数、ledger row 数、待签收字段数、阻塞行数、暂停材料数，以及只读/禁用真实配置边界。
- `decision_ledger_preview`：`decision_ledger_preview_ready` / `needs_more_evidence` / `blocked` / `deferred`。
- `ledger_rows`：按 provider 输出预览行、决策字段、待签收字段、来源复核包 section 和阻塞原因。
- `decision`：只允许人工继续复查，不允许自动创建真实 provider 配置或保存账本。
- `ledger_preview_materials`、`manual_review_checklist`、`no_go_conditions`、`boundaries`、`next_steps`、`manifest` 和 `content_json`。

### HTTP API

新增：

```text
GET /api/stories/<slug>/graph-memory-provider-spike-opt-in-decision-ledger-preview
```

状态约定：

- 坏 `slug` 返回 `400`。
- 项目不存在返回 `404`。
- 正常项目返回只读报告；小项目或证据不足时返回明确 `deferred` / `needs_more_evidence`，不抛 500。

### CLI

新增：

```powershell
lne memory graph-opt-in-decision-ledger-preview <slug> --json
```

未加 `--json` 时输出 `content_json`，方便无人值守脚本保存或人工复查。

### 前端

项目工作台新增 `Graph 记忆 Provider Spike Opt-in 决策账本预览` 面板，展示：

- 账本预览状态、预览行数、待签收字段数、保存状态和真实配置禁止状态。
- provider ledger rows、决策字段、待签收字段、阻塞行、来源复核包 section 和 decision。
- 决策预览材料与“不连接外部服务”的边界说明。

可见文案保持中文。缺失/暂缓状态显示为空态或说明，不白屏。

### API Contract / Typed Client

`get_api_contract()` 新增：

- endpoint：`/api/stories/{slug}/graph-memory-provider-spike-opt-in-decision-ledger-preview`
- typed client method：`getGraphMemoryProviderSpikeOptInDecisionLedgerPreview`
- response type：`GraphMemoryProviderSpikeOptInDecisionLedgerPreviewReport`

当前契约计数更新为：

- `endpoint_count=59`
- `openapi_path_count=58`
- `typed_client_method_count=58`

前端 `engine/ui/src/api/client.ts` 和 `types.ts` 已同步新增类型与方法。

## 验收

RED tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_opt_in_decision_ledger_preview.py tests/test_api_contract.py -q
```

初始结果：`6 failed, 1 passed`，失败点集中在缺 service/export、HTTP route、CLI、API contract 与 typed client。

Focused tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_opt_in_decision_ledger_preview.py tests/test_api_contract.py -q
```

结果：`7 passed`。

邻近回归：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_opt_in_decision_ledger_preview.py tests/test_graph_memory_provider_spike_opt_in_review_packet.py tests/test_graph_memory_provider_spike_opt_in_operator_checklist.py tests/test_graph_memory_provider_spike_opt_in_no_go_matrix.py tests/test_graph_memory_provider_spike_opt_in_evidence_snapshot.py tests/test_graph_memory_provider_spike_manual_approval_evidence_checklist.py tests/test_graph_memory_provider_spike_manual_approval_pack.py tests/test_graph_memory_provider_spike_review_gate.py tests/test_graph_memory_provider_spike_mock_result_report.py tests/test_graph_memory_provider_spike_dry_run_result_template.py tests/test_graph_memory_provider_spike_runbook.py tests/test_graph_memory_provider_spike_readiness_gate.py tests/test_graph_memory_provider_spike_fixture_pack.py tests/test_graph_memory_offline_shadow_replay_report.py tests/test_graph_memory_offline_shadow_replay_plan.py tests/test_graph_memory_provider_boundary_matrix.py tests/test_graph_memory_shadow_case_matrix.py tests/test_graph_memory_shadow_compare_pack.py tests/test_graph_memory_spike_design_pack.py tests/test_graph_memory_trigger_evidence.py tests/test_api_contract.py -q
```

结果：`83 passed`。

前端构建：

```powershell
cd D:\AI\open-infinite\engine\ui
pnpm.cmd run build
```

结果：通过。

本地 smoke：

- 使用临时 fixture，后端指向临时 `LNE_PROJECTS_DIR`，`LLM_API_KEY` / `SEEDREAM_API_KEY` 清空，`LNE_MOCK=1`。
- `GET /api/stories/graph-fixture-pack-large/graph-memory-provider-spike-opt-in-decision-ledger-preview` 返回 `ready_for_opt_in_decision_ledger_preview`、`decision_ledger_preview_ready`、`ledger_row_count=2`、`pending_signoff_field_count=10`、`blocked_row_count=2`、`pause_material_count=6`、`writes_artifacts=false`、`ledger_write_allowed=false`、`approval_saved=false`、`real_provider_config_allowed=false`、`plaintext_key_returned=false`。
- `lne memory graph-opt-in-decision-ledger-preview graph-fixture-pack-large --json` 返回同一 ready 路径摘要。
- 前端 build 产物包含 `决策账本预览`、`账本预览就绪`、`签收字段`、`未保存`、`仍禁止真实配置`、`真实配置` 等文案。
- service 源码安全扫描未发现 env/key 读取、外部 HTTP client、写文件或目录创建。
- 临时服务和 fixture 已清理。

全量基线：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite
git diff --check
```

结果：后端 `855 passed`；`git diff --check` 通过，只有既有 CRLF 提示。

## 边界复核

- 路径安全：HTTP `slug` 经 `safe_id` 校验。
- 只读性：service 只消费 opt-in review packet，不写任何项目文件。
- 外部服务：没有 provider、HTTP client、embedding、GraphRAG、Zep、向量库或 reranker 调用。
- Key 安全：测试注入 fake key 并断言报告文本不包含密钥片段、环境变量名或临时路径；service 源码安全扫描未发现 env/key 读取。
- 旧契约：未改 `run_scene`，未改既有 artifact schema，新增 API/UI/type 字段均 additive。

## 下一刀建议

`Graph Memory Provider Spike Opt-in Final Readiness Summary MVP`：

- 基于 decision ledger preview 输出只读最终就绪摘要、未签收字段、阻塞原因和继续暂缓条件。
- 继续不创建真实 provider 配置、不保存人工签名、不写决策账本、不读取真实 Key、不调用外部 GraphRAG、Zep、Temporal Memory、embedding provider、向量库或 reranker。
