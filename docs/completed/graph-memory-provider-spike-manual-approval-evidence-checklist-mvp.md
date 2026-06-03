# Graph Memory Provider Spike Manual Approval Evidence Checklist MVP 收口说明

日期：2026-06-02

## 目标

把 `Graph Memory Provider Spike Manual Approval Pack` 继续收束为只读审批证据核对表。核对表只回答“审批材料里哪些证据齐备、哪些签收仍待人工完成、哪些材料缺口会阻止真实 provider”，不保存签名，也不创建真实 provider 配置。

本切片继续保持本地、只读、可回滚：

- 不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不写项目 artifact，不改变 `run_scene` 默认行为。
- 不覆盖 `canon_ledger.jsonl`、`state_snapshot.json`、`retrieval_context.json` 或既有检索上下文。
- 不保存人工签名，不把待签收项标记为已完成。
- 不读取、不返回、不记录明文 Key。

## 本次新增

### Service

新增 `living_novel_engine.service.get_graph_memory_provider_spike_manual_approval_evidence_checklist(slug, projects_dir=None, now=None)`。

报告字段包括：

- `summary`：来源 approval pack 状态、核对项数、待签收数、材料缺口数、回滚材料缺口数和安全边界。
- `evidence_checklist`：`evidence_checklist_ready` / `needs_more_evidence` / `blocked` / `deferred`。
- `checklist_items`：按 provider 输出证据状态、待签收项、材料缺口、回滚缺口、可用材料和证据引用。
- `decision`：只允许人工核对证据，不允许自动创建真实配置。
- `manual_review_checklist`、`no_go_conditions`、`boundaries`、`next_steps`、`manifest` 和 `content_json`。

### HTTP API

新增：

```text
GET /api/stories/<slug>/graph-memory-provider-spike-manual-approval-evidence-checklist
```

状态约定：

- 坏 `slug` 返回 `400`。
- 项目不存在返回 `404`。
- 正常项目返回只读报告；小项目或证据不足时返回明确 `deferred` / `needs_more_evidence`，不抛 500。

### CLI

新增：

```powershell
lne memory graph-approval-evidence-checklist <slug> --json
```

未加 `--json` 时输出 `content_json`，方便无人值守脚本保存或人工复查。

### 前端

项目工作台新增 `Graph 记忆 Provider Spike 审批证据核对表` 面板，展示：

- 核对表状态、待签收数、材料缺口数和真实配置禁止状态。
- provider 核对项、待签收项、可用材料和 evidence status。
- decision、人工核对 checklist、no-go 条件和“不连接外部服务”的边界说明。

可见文案保持中文。缺失/暂缓状态显示为空态或说明，不白屏。

### API Contract / Typed Client

`get_api_contract()` 新增：

- endpoint：`/api/stories/{slug}/graph-memory-provider-spike-manual-approval-evidence-checklist`
- typed client method：`getGraphMemoryProviderSpikeManualApprovalEvidenceChecklist`
- response type：`GraphMemoryProviderSpikeManualApprovalEvidenceChecklistReport`

当前契约计数更新为：

- `endpoint_count=54`
- `openapi_path_count=53`
- `typed_client_method_count=53`

前端 `engine/ui/src/api/client.ts` 和 `types.ts` 已同步新增类型与方法。

## 验收

RED tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_manual_approval_evidence_checklist.py tests/test_api_contract.py -q
```

初始结果：`6 failed, 1 passed`，失败点集中在缺 service/export、HTTP route、CLI、API contract 与 typed client。

Focused tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_manual_approval_evidence_checklist.py tests/test_api_contract.py -q
```

结果：`7 passed`。

邻近回归：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_manual_approval_evidence_checklist.py tests/test_graph_memory_provider_spike_manual_approval_pack.py tests/test_graph_memory_provider_spike_review_gate.py tests/test_graph_memory_provider_spike_mock_result_report.py tests/test_graph_memory_provider_spike_dry_run_result_template.py tests/test_graph_memory_provider_spike_runbook.py tests/test_graph_memory_provider_spike_readiness_gate.py tests/test_graph_memory_provider_spike_fixture_pack.py tests/test_graph_memory_offline_shadow_replay_report.py tests/test_graph_memory_offline_shadow_replay_plan.py tests/test_graph_memory_provider_boundary_matrix.py tests/test_graph_memory_shadow_case_matrix.py tests/test_graph_memory_shadow_compare_pack.py tests/test_graph_memory_spike_design_pack.py tests/test_graph_memory_trigger_evidence.py tests/test_api_contract.py -q
```

结果：`63 passed`。

前端构建：

```powershell
cd D:\AI\open-infinite\engine\ui
pnpm.cmd run build
```

结果：通过。

本地 smoke：

- 使用临时 `.local-run/graph-approval-evidence-api-smoke` / `.local-run/graph-approval-evidence-cli-smoke` fixture。
- 后端指向临时 `LNE_PROJECTS_DIR`，`LLM_API_KEY` / `SEEDREAM_API_KEY` 清空，`LNE_MOCK=1`。
- `GET /api/stories/graph-fixture-pack-large/graph-memory-provider-spike-manual-approval-evidence-checklist` 返回 `ready_for_manual_approval_evidence_checklist`、`evidence_checklist_ready`、`checklist_item_count=2`、`pending_signoff_count=8`、`material_gap_count=0`、`writes_artifacts=false`、`external_services_required=false`、`real_provider_config_allowed=false`、`plaintext_key_returned=false`。
- `lne memory graph-approval-evidence-checklist graph-fixture-pack-large --json` 返回同一 ready 路径摘要。
- 前端 build 产物包含 `Graph 记忆 Provider Spike 审批证据核对表`、`核对表就绪`、`待人工签收`、`材料齐，待签收`、`仅可核对证据`、`真实配置` 等文案。
- service 源码安全扫描未发现 env/key 读取、外部 HTTP client、写文件或目录创建。
- 临时服务和 fixture 已清理。

全量基线：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite
git diff --check
```

结果：后端 `835 passed`；`git diff --check` 通过，只有既有 CRLF 提示。

## 边界复核

- 路径安全：HTTP `slug` 经 `safe_id` 校验。
- 只读性：service 只消费 manual approval pack，不写任何项目文件。
- 外部服务：没有 provider、HTTP client、embedding、GraphRAG、Zep、向量库或 reranker 调用。
- Key 安全：测试注入 fake key 并断言报告文本不包含密钥片段、环境变量名或临时路径；service 源码安全扫描未发现 env/key 读取。
- 旧契约：未改 `run_scene`，未改既有 artifact schema，新增 API/UI/type 字段均 additive。

## 下一刀建议

`Graph Memory Provider Spike Opt-in Evidence Snapshot MVP`：

- 基于 approval evidence checklist 输出只读 opt-in 证据快照。
- 聚合阻塞项摘要、签收待办、材料缺口和继续暂缓真实 provider 的条件。
- 继续不创建真实 provider 配置、不保存人工签名、不读取真实 Key、不调用外部 GraphRAG、Zep、Temporal Memory、embedding provider、向量库或 reranker。
