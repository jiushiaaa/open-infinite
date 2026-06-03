# Graph Memory Provider Spike Dry-run Result Template MVP 收口说明

日期：2026-06-01

## 目标

把 `Graph Memory Provider Spike Runbook` 继续收束为真实 GraphRAG、Zep、Temporal Memory provider spike 前的只读人工结果记录模板。该模板只回答“人工执行 dry-run 后应该记录哪些字段、如何对比、何时暂停、何时另开真实 opt-in spike”，不保存结果本身，也不创建真实 provider 配置。

本切片继续保持本地、只读、可回滚：

- 不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不写项目 artifact，不改变 `run_scene` 默认行为。
- 不覆盖 `canon_ledger.jsonl`、`state_snapshot.json`、`retrieval_context.json` 或既有检索上下文。
- 不读取、不返回、不记录明文 Key。
- 即使状态为 `ready_for_manual_result_recording`，`result_write_allowed=false` 且 `real_provider_config_allowed=false`。

## 本次新增

### Service

新增 `living_novel_engine.service.get_graph_memory_provider_spike_dry_run_result_template(slug, projects_dir=None, now=None)`。

报告字段包括：

- `summary`：来源 runbook 状态、provider 模板数、结果字段数、外部调用和真实配置边界。
- `template`：`ready_for_manual_result_recording`、`needs_more_evidence`、`blocked` 或 `deferred`，并显式说明 `manual_only=true`、`result_write_allowed=false`、`real_provider_config_allowed=false`。
- `provider_result_templates`：按 GraphRAG、Zep、Temporal Memory 展示结果字段、对比轴、验收记录、暂停/升级判定、回滚确认和证据引用。
- `manual_review_checklist`：填写结果模板前必须确认的基线、候选输出、收益、风险和 no-go 项。
- `decision`：只允许人工记录 dry-run 结果，不允许自动创建真实配置。
- `no_go_conditions`、`boundaries`、`next_steps`、`manifest` 和 `content_json`。

### HTTP API

新增：

```text
GET /api/stories/<slug>/graph-memory-provider-spike-dry-run-result-template
```

状态约定：

- 坏 `slug` 返回 `400`。
- 项目不存在返回 `404`。
- 正常项目返回只读报告；小项目或证据不足时返回明确 `deferred` / `needs_more_evidence`，不抛 500。

### CLI

新增：

```powershell
lne memory graph-result-template <slug> --json
```

未加 `--json` 时输出 `content_json`，方便无人值守脚本保存或人工复查。

### 前端

项目工作台新增 `Graph 记忆 Provider Spike 结果模板` 面板，展示：

- 模板状态、可记录 provider 数、结果字段数、写入结果禁止状态。
- GraphRAG / Zep 结果模板、关键字段、暂停/升级选项和验收记录。
- no-go 条件和“不连接外部服务”的边界说明。

可见文案保持中文。缺失/暂缓状态显示为空态或说明，不白屏。

### API Contract / Typed Client

`get_api_contract()` 新增：

- endpoint：`/api/stories/{slug}/graph-memory-provider-spike-dry-run-result-template`
- typed client method：`getGraphMemoryProviderSpikeDryRunResultTemplate`
- response type：`GraphMemoryProviderSpikeDryRunResultTemplateReport`

当前契约计数更新为：

- `endpoint_count=50`
- `openapi_path_count=49`
- `typed_client_method_count=49`

前端 `engine/ui/src/api/client.ts` 和 `types.ts` 已同步新增类型与方法。

## 验收

RED tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_dry_run_result_template.py tests/test_api_contract.py -q
```

初始结果：`6 failed, 1 passed`，失败点集中在缺 service、HTTP route、CLI、API contract 与 typed client。

Focused tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_dry_run_result_template.py tests/test_api_contract.py -q
```

结果：`7 passed`。

邻近回归：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_dry_run_result_template.py tests/test_graph_memory_provider_spike_runbook.py tests/test_graph_memory_provider_spike_readiness_gate.py tests/test_graph_memory_provider_spike_fixture_pack.py tests/test_graph_memory_offline_shadow_replay_report.py tests/test_graph_memory_offline_shadow_replay_plan.py tests/test_graph_memory_provider_boundary_matrix.py tests/test_graph_memory_shadow_case_matrix.py tests/test_graph_memory_shadow_compare_pack.py tests/test_graph_memory_spike_design_pack.py tests/test_v093_graph_memory_trigger.py tests/test_api_contract.py -q
```

结果：`46 passed`。

前端构建：

```powershell
cd D:\AI\open-infinite\engine\ui
pnpm.cmd run build
```

结果：通过。

本地 smoke：

- 使用临时 `.local-run/graph-result-template-smoke` fixture。
- 后端指向临时 `LNE_PROJECTS_DIR`，`LLM_API_KEY` / `SEEDREAM_API_KEY` 清空，`LNE_MOCK=1`。
- `GET /api/stories/graph-fixture-pack-large/graph-memory-provider-spike-dry-run-result-template` 返回 `ready_for_manual_result_recording`、`provider_template_count=2`、`required_result_field_count=22`、`result_write_allowed=false`、`real_provider_config_allowed=false`。
- 前端 build 产物包含 `Graph 记忆 Provider Spike 结果模板`、`本地基线摘要`、`暂停：命中 no-go`、`另开真实 opt-in spike` 等文案。
- in-app browser attach 连续超时，未宣称视觉浏览器烟测通过；本轮以 API smoke + build artifact 文案检查作为 fallback。
- 临时服务和 fixture 已清理，8765 / 5173 无监听。

全量基线：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite
git diff --check
```

结果：后端 `819 passed`；`git diff --check` 通过，只有既有 CRLF 提示。

## 边界复核

- 路径安全：HTTP `slug` 经 `safe_id` 校验。
- 只读性：service 只消费 runbook，不写任何项目文件。
- 外部服务：没有 provider、HTTP client、embedding、GraphRAG、Zep、向量库或 reranker 调用。
- Key 安全：测试注入 fake key 并断言报告文本不包含密钥片段、环境变量名或临时路径。
- 旧契约：未改 `run_scene`，未改既有 artifact schema，新增 API/UI/type 字段均 additive。

## 下一刀建议

`Graph Memory Provider Spike Mock Result Report MVP`：

- 基于 result template 与既有 mock replay 输出生成只读填充样例。
- 把收益/风险判定、人工复核摘要、暂停/升级建议和证据引用报告化。
- 继续不创建真实 provider 配置、不保存人工结果、不读取真实 Key、不调用外部 GraphRAG、Zep、Temporal Memory、embedding provider、向量库或 reranker。
