# Graph Memory Provider Spike Review Gate MVP 收口说明

日期：2026-06-02

## 目标

把 `Graph Memory Provider Spike Mock Result Report` 继续收束为只读人工复核门禁。门禁只回答“现有 mock result 是否足以进入人工审批材料准备”，并把 provider review rows、no-go 摘要、暂停/升级分流和真实 provider 继续禁止边界整理出来。

本切片继续保持本地、只读、可回滚：

- 不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不写项目 artifact，不改变 `run_scene` 默认行为。
- 不覆盖 `canon_ledger.jsonl`、`state_snapshot.json`、`retrieval_context.json` 或既有检索上下文。
- 不保存人工结论，不创建真实 provider 配置。
- 不读取、不返回、不记录明文 Key。

## 本次新增

### Service

新增 `living_novel_engine.service.get_graph_memory_provider_spike_review_gate(slug, projects_dir=None, now=None)`。

报告字段包括：

- `summary`：来源 mock result 状态、provider 数、manual review 数、候选收益数和安全边界。
- `review_gate`：`manual_review_gate_ready` / `needs_more_evidence` / `blocked` / `deferred`。
- `provider_reviews`：按 provider 输出复核状态、风险/收益摘要、证据引用、review items 和 gate decision。
- `decision`：只允许人工复核与审批材料准备，不允许自动创建真实配置。
- `manual_review_checklist`、`no_go_conditions`、`boundaries`、`next_steps`、`manifest` 和 `content_json`。

### HTTP API

新增：

```text
GET /api/stories/<slug>/graph-memory-provider-spike-review-gate
```

状态约定：

- 坏 `slug` 返回 `400`。
- 项目不存在返回 `404`。
- 正常项目返回只读报告；小项目或证据不足时返回明确 `deferred` / `needs_more_evidence`，不抛 500。

### CLI

新增：

```powershell
lne memory graph-review-gate <slug> --json
```

未加 `--json` 时输出 `content_json`，方便无人值守脚本保存或人工复查。

### 前端

项目工作台新增 `Graph 记忆 Provider Spike 复核门禁` 面板，展示：

- 门禁状态、复核行数、候选收益数和真实配置禁止状态。
- provider review rows、收益/风险/证据、gate decision 和人工复核项。
- decision、人工复核 checklist、no-go 条件和“不连接外部服务”的边界说明。

可见文案保持中文。缺失/暂缓状态显示为空态或说明，不白屏。

### API Contract / Typed Client

`get_api_contract()` 新增：

- endpoint：`/api/stories/{slug}/graph-memory-provider-spike-review-gate`
- typed client method：`getGraphMemoryProviderSpikeReviewGate`
- response type：`GraphMemoryProviderSpikeReviewGateReport`

当前契约计数更新为：

- `endpoint_count=52`
- `openapi_path_count=51`
- `typed_client_method_count=51`

前端 `engine/ui/src/api/client.ts` 和 `types.ts` 已同步新增类型与方法。

## 验收

RED tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_review_gate.py tests/test_api_contract.py -q
```

初始结果：`6 failed, 1 passed`，失败点集中在缺 service/export、HTTP route、CLI、API contract 与 typed client。

Focused tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_review_gate.py tests/test_api_contract.py -q
```

结果：`7 passed`。

邻近回归：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_review_gate.py tests/test_graph_memory_provider_spike_mock_result_report.py tests/test_graph_memory_provider_spike_dry_run_result_template.py tests/test_graph_memory_provider_spike_runbook.py tests/test_graph_memory_provider_spike_readiness_gate.py tests/test_graph_memory_provider_spike_fixture_pack.py tests/test_graph_memory_offline_shadow_replay_report.py tests/test_graph_memory_offline_shadow_replay_plan.py tests/test_graph_memory_provider_boundary_matrix.py tests/test_graph_memory_shadow_case_matrix.py tests/test_graph_memory_shadow_compare_pack.py tests/test_graph_memory_spike_design_pack.py tests/test_graph_memory_trigger_evidence.py tests/test_api_contract.py -q
```

结果：`55 passed`。

前端构建：

```powershell
cd D:\AI\open-infinite\engine\ui
pnpm.cmd run build
```

结果：通过。

本地 smoke：

- 使用临时 `.local-run/graph-review-gate-smoke` fixture。
- 后端指向临时 `LNE_PROJECTS_DIR`，`LLM_API_KEY` / `SEEDREAM_API_KEY` 清空，`LNE_MOCK=1`。
- `GET /api/stories/graph-fixture-pack-large/graph-memory-provider-spike-review-gate` 返回 `ready_for_manual_review_gate`、`manual_review_gate_ready`、`provider_reviews=2`、`candidate_gain_count=2`、`writes_artifacts=false`、`external_services_required=false`、`real_provider_config_allowed=false`、`plaintext_key_returned=false`。
- `lne memory graph-review-gate graph-fixture-pack-large --json` 返回同一 ready 路径摘要。
- 前端 build 产物包含 `Graph 记忆 Provider Spike 复核门禁`、`门禁就绪`、`需人工复核`、`仅可人工复核`、`真实配置` 等文案。
- in-app browser 等待 webview attach 超时，未宣称视觉浏览器烟测通过；本轮以 API smoke + CLI smoke + build artifact 文案检查作为 fallback。
- 临时服务和 fixture 已清理，8765 / 5173 无监听。

全量基线：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite
git diff --check
```

结果：后端 `827 passed`；`git diff --check` 通过，只有既有 CRLF 提示。

## 边界复核

- 路径安全：HTTP `slug` 经 `safe_id` 校验。
- 只读性：service 只消费 mock result report，不写任何项目文件。
- 外部服务：没有 provider、HTTP client、embedding、GraphRAG、Zep、向量库或 reranker 调用。
- Key 安全：测试注入 fake key 并断言报告文本不包含密钥片段、环境变量名或临时路径；service 源码安全扫描未发现 env/key 读取。
- 旧契约：未改 `run_scene`，未改既有 artifact schema，新增 API/UI/type 字段均 additive。

## 下一刀建议

`Graph Memory Provider Spike Manual Approval Pack MVP`：

- 基于 review gate 输出只读人工审批包。
- 聚合确认项、风险签收、回滚确认、opt-in 前置材料和继续禁止真实配置的边界。
- 继续不创建真实 provider 配置、不保存人工结果、不读取真实 Key、不调用外部 GraphRAG、Zep、Temporal Memory、embedding provider、向量库或 reranker。
