# Graph Memory Provider Spike Readiness Gate MVP 收口说明

日期：2026-06-01

## 目标

把 `Graph Memory Provider Spike Fixture Pack` 继续收束成真实 GraphRAG、Zep、Temporal Memory provider spike 前的只读就绪门禁。该门禁只判断 fixture pack 是否足够进入人工 opt-in 复核，输出阻塞原因、人工验收项、no-go 条件和继续暂缓理由，不创建真实 provider 配置。

本切片继续保持本地、只读、可回滚：

- 不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不写项目 artifact，不改变 `run_scene` 默认行为。
- 不覆盖 `canon_ledger.jsonl`、`state_snapshot.json`、`retrieval_context.json` 或既有检索上下文。
- 不读取、不返回、不记录明文 Key。
- 即使 gate 为 `ready_for_manual_opt_in_review`，`real_provider_config_allowed` 仍为 `false`。

## 本次新增

### Service

新增 `living_novel_engine.service.get_graph_memory_provider_spike_readiness_gate(slug, projects_dir=None, now=None)`。

报告字段包括：

- `summary`：来源 fixture pack 状态、provider 数、ready/blocked 数、外部调用和真实配置边界。
- `readiness_gate`：`ready_for_manual_opt_in_review`、`needs_more_evidence`、`blocked` 或 `deferred`，并显式说明 `real_provider_config_allowed=false`。
- `provider_rows`：按 GraphRAG、Zep、Temporal Memory 展示 fixture、manual review、blockers、no-go 和 recommendation。
- `readiness_checks`：fixture scope、cost guardrails、privacy guardrails、rollback plan、manual acceptance、no-go review。
- `decision`：下一步是否只能进入人工复核，不得自动创建真实配置。
- `no_go_conditions`、`boundaries`、`next_steps` 和 `content_json`。

### HTTP API

新增：

```text
GET /api/stories/<slug>/graph-memory-provider-spike-readiness-gate
```

状态约定：

- 坏 `slug` 返回 `400`。
- 项目不存在返回 `404`。
- 正常项目返回只读报告；小项目或证据不足时返回明确 `deferred` / `needs_more_evidence`，不抛 500。

### CLI

新增：

```powershell
lne memory graph-readiness-gate <slug> --json
```

未加 `--json` 时输出 `content_json`，方便无人值守脚本保存或人工复查。

### 前端

项目工作台新增 `Graph 记忆 Provider Spike 就绪门禁` 面板，展示：

- gate 状态、ready provider 数、blocked provider 数、真实配置禁止状态。
- GraphRAG / Zep readiness row、来源 fixture、人工复核项和建议。
- readiness checks、no-go 条件和“不连接外部服务”的边界说明。

可见文案保持中文。缺失/暂缓状态显示为空态或说明，不白屏。

### API Contract / Typed Client

`get_api_contract()` 新增：

- endpoint：`/api/stories/{slug}/graph-memory-provider-spike-readiness-gate`
- typed client method：`getGraphMemoryProviderSpikeReadinessGate`
- response type：`GraphMemoryProviderSpikeReadinessGateReport`

当前契约计数更新为：

- `endpoint_count=48`
- `openapi_path_count=47`
- `typed_client_method_count=47`

前端 `engine/ui/src/api/client.ts` 和 `types.ts` 已同步新增类型与方法。

### 邻近稳定性修复

全量测试暴露 Windows 下带 body 的坏 ID `POST` 偶发 `ConnectionAbortedError [WinError 10053]`。根因是本地 HTTP server 对无效路径参数提前返回 `400` 时没有消费未读 request body。

本次在 `BrowserHandler` 公共层新增未读 POST body drain：

- `_read_body_json()` 标记 body 已消费。
- `_send_json(status>=400)` 在 POST 且 body 未读时先丢弃未读 body。
- 正常成功路径和业务 handler 不变。

该修复保持语义不变：坏 ID 仍返回 `400`，只是避免 Windows 客户端在响应返回时被连接中止。

## 验收

Focused tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_readiness_gate.py tests/test_api_contract.py -q
```

结果：`7 passed`。

坏请求稳定性回归：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_v092_master_setting_update.py::test_master_setting_update_http_statuses tests/test_v075_worldline_judge.py::TestHttp::test_bad_branch_id_400 -q
```

结果：单次 `2 passed`；随后 5 轮循环复跑均为 `2 passed`。

邻近回归：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_readiness_gate.py tests/test_graph_memory_provider_spike_fixture_pack.py tests/test_graph_memory_offline_shadow_replay_report.py tests/test_graph_memory_offline_shadow_replay_plan.py tests/test_graph_memory_provider_boundary_matrix.py tests/test_graph_memory_shadow_case_matrix.py tests/test_graph_memory_shadow_compare_pack.py tests/test_graph_memory_spike_design_pack.py tests/test_v093_graph_memory_trigger.py tests/test_api_contract.py -q
```

结果：`38 passed`。

浏览器烟测：

- 使用临时 `.local-run/graph-readiness-gate-smoke` fixture。
- 后端指向临时 `LNE_PROJECTS_DIR`，`LLM_API_KEY` / `SEEDREAM_API_KEY` 清空，`LNE_MOCK=1`。
- 打开 `http://localhost:5173/#/workspace/graph-readiness-gate-smoke-large`。
- 已确认页面出现 `Graph 记忆 Provider Spike 就绪门禁`、`可人工复核`、ready count `2`、blocked count `0`、`真实配置 禁止`、GraphRAG/Zep、`不能要求真实付费 Key` no-go 和“不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM”边界。
- 临时服务和 fixture 已清理。

全量基线：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm.cmd run build

cd D:\AI\open-infinite
git diff --check
```

结果：后端 `811 passed`；前端 build 通过；`git diff --check` 通过，只有既有 CRLF 提示。

## 边界复核

- 路径安全：HTTP `slug` 经 `safe_id` 校验。
- 只读性：service 只消费 fixture pack，不写任何项目文件。
- 外部服务：没有 provider、HTTP client、embedding、GraphRAG、Zep、向量库或 reranker 调用。
- Key 安全：测试注入 fake key 并断言报告文本不包含密钥片段、环境变量名或临时路径。
- 旧契约：未改 `run_scene`，未改既有 artifact schema，新增 API/UI/type 字段均 additive。

## 下一刀建议

`Graph Memory Provider Spike Runbook MVP`：

- 基于 readiness gate 输出只读人工 opt-in runbook。
- 把 dry-run 输入、验收步骤、回滚步骤、暂停条件、no-go 和证据引用整理成可复核 SOP。
- 继续不创建真实 provider 配置、不读取真实 Key、不调用外部 GraphRAG、Zep、Temporal Memory、embedding provider、向量库或 reranker。
