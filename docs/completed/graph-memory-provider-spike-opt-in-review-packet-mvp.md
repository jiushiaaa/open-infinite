# Graph Memory Provider Spike Opt-in Review Packet MVP 收口说明

日期：2026-06-02

## 目标

把 `Graph Memory Provider Spike Opt-in Operator Checklist` 继续收束为只读人工复核包。复核包只回答“人工复核时证据按什么顺序看、哪些材料要求暂停、哪些材料可用于升级讨论”，不保存复核结果，也不创建真实 provider 配置。

本切片继续保持本地、只读、可回滚：

- 不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不写项目 artifact，不改变 `run_scene` 默认行为。
- 不覆盖 `canon_ledger.jsonl`、`state_snapshot.json`、`retrieval_context.json` 或既有检索上下文。
- 不保存人工签名、人工复核结果或 opt-in 审批状态。
- 不读取、不返回、不记录明文 Key。

## 本次新增

### Service

新增 `living_novel_engine.service.get_graph_memory_provider_spike_opt_in_review_packet(slug, projects_dir=None, now=None)`。

报告字段包括：

- `summary`：来源 operator checklist 状态、provider 数、packet section 数、证据项数、阻塞步骤数、暂停材料数和升级材料数。
- `review_packet`：`review_packet_ready` / `needs_more_evidence` / `blocked` / `deferred`。
- `packet_sections`：按 provider 输出 evidence sequence、pause materials、escalation materials、reviewer todos 和证据引用。
- `decision`：只允许人工按复核包复查，不允许自动创建真实配置。
- `review_packet_materials`、`manual_review_checklist`、`no_go_conditions`、`boundaries`、`next_steps`、`manifest` 和 `content_json`。

### HTTP API

新增：

```text
GET /api/stories/<slug>/graph-memory-provider-spike-opt-in-review-packet
```

状态约定：

- 坏 `slug` 返回 `400`。
- 项目不存在返回 `404`。
- 正常项目返回只读报告；小项目或证据不足时返回明确 `deferred` / `needs_more_evidence`，不抛 500。

### CLI

新增：

```powershell
lne memory graph-opt-in-review-packet <slug> --json
```

未加 `--json` 时输出 `content_json`，方便无人值守脚本保存或人工复查。

### 前端

项目工作台新增 `Graph 记忆 Provider Spike Opt-in 复核包` 面板，展示：

- 复核包状态、证据项数、暂停材料数和真实配置禁止状态。
- provider packet sections、证据顺序、暂停材料、升级材料和 decision。
- 复核材料与“不连接外部服务”的边界说明。

可见文案保持中文。缺失/暂缓状态显示为空态或说明，不白屏。

### API Contract / Typed Client

`get_api_contract()` 新增：

- endpoint：`/api/stories/{slug}/graph-memory-provider-spike-opt-in-review-packet`
- typed client method：`getGraphMemoryProviderSpikeOptInReviewPacket`
- response type：`GraphMemoryProviderSpikeOptInReviewPacketReport`

当前契约计数更新为：

- `endpoint_count=58`
- `openapi_path_count=57`
- `typed_client_method_count=57`

前端 `engine/ui/src/api/client.ts` 和 `types.ts` 已同步新增类型与方法。

## 验收

RED tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_opt_in_review_packet.py tests/test_api_contract.py -q
```

初始结果：`6 failed, 1 passed`，失败点集中在缺 service/export、HTTP route、CLI、API contract 与 typed client。

Focused tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_opt_in_review_packet.py tests/test_api_contract.py -q
```

结果：`7 passed`。

邻近回归：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_opt_in_review_packet.py tests/test_graph_memory_provider_spike_opt_in_operator_checklist.py tests/test_graph_memory_provider_spike_opt_in_no_go_matrix.py tests/test_graph_memory_provider_spike_opt_in_evidence_snapshot.py tests/test_graph_memory_provider_spike_manual_approval_evidence_checklist.py tests/test_graph_memory_provider_spike_manual_approval_pack.py tests/test_graph_memory_provider_spike_review_gate.py tests/test_graph_memory_provider_spike_mock_result_report.py tests/test_graph_memory_provider_spike_dry_run_result_template.py tests/test_graph_memory_provider_spike_runbook.py tests/test_graph_memory_provider_spike_readiness_gate.py tests/test_graph_memory_provider_spike_fixture_pack.py tests/test_graph_memory_offline_shadow_replay_report.py tests/test_graph_memory_offline_shadow_replay_plan.py tests/test_graph_memory_provider_boundary_matrix.py tests/test_graph_memory_shadow_case_matrix.py tests/test_graph_memory_shadow_compare_pack.py tests/test_graph_memory_spike_design_pack.py tests/test_graph_memory_trigger_evidence.py tests/test_api_contract.py -q
```

结果：`79 passed`。

前端构建：

```powershell
cd D:\AI\open-infinite\engine\ui
pnpm.cmd run build
```

结果：通过。

本地 smoke：

- 使用临时 fixture，后端指向临时 `LNE_PROJECTS_DIR`，`LLM_API_KEY` / `SEEDREAM_API_KEY` 清空，`LNE_MOCK=1`。
- `GET /api/stories/graph-fixture-pack-large/graph-memory-provider-spike-opt-in-review-packet` 返回 `ready_for_opt_in_review_packet`、`review_packet_ready`、`packet_section_count=2`、`evidence_item_count=10`、`pause_material_count=6`、`blocked_step_count=6`、`writes_artifacts=false`、`external_services_required=false`、`real_provider_config_allowed=false`、`plaintext_key_returned=false`。
- `lne memory graph-opt-in-review-packet graph-fixture-pack-large --json` 返回同一 ready 路径摘要。
- 前端 build 产物包含 `Graph 记忆 Provider Spike Opt-in 复核包`、`复核包就绪`、`暂停材料`、`仍禁止真实配置`、`真实配置` 等文案。
- service 源码安全扫描未发现 env/key 读取、外部 HTTP client、写文件或目录创建。
- 临时服务和 fixture 已清理。

全量基线：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite
git diff --check
```

结果：后端 `851 passed`；`git diff --check` 通过，只有既有 CRLF 提示。

## 边界复核

- 路径安全：HTTP `slug` 经 `safe_id` 校验。
- 只读性：service 只消费 opt-in operator checklist，不写任何项目文件。
- 外部服务：没有 provider、HTTP client、embedding、GraphRAG、Zep、向量库或 reranker 调用。
- Key 安全：测试注入 fake key 并断言报告文本不包含密钥片段、环境变量名或临时路径；service 源码安全扫描未发现 env/key 读取。
- 旧契约：未改 `run_scene`，未改既有 artifact schema，新增 API/UI/type 字段均 additive。

## 下一刀建议

`Graph Memory Provider Spike Opt-in Decision Ledger Preview MVP`：

- 基于 review packet 输出只读决策账本预览、签收字段占位、暂停/升级依据和继续暂缓条件。
- 继续不创建真实 provider 配置、不保存人工签名、不读取真实 Key、不调用外部 GraphRAG、Zep、Temporal Memory、embedding provider、向量库或 reranker。
