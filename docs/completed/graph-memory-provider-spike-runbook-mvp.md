# Graph Memory Provider Spike Runbook MVP 收口说明

日期：2026-06-01

## 目标

把 `Graph Memory Provider Spike Readiness Gate` 继续收束为真实 GraphRAG、Zep、Temporal Memory provider spike 前的只读人工 SOP。Runbook 只回答“如果人工决定做 opt-in dry-run，应按什么步骤准备、执行、复核、暂停和回滚”，不创建真实 provider 配置，也不把任何外部服务接入默认链路。

本切片继续保持本地、只读、可回滚：

- 不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不写项目 artifact，不改变 `run_scene` 默认行为。
- 不覆盖 `canon_ledger.jsonl`、`state_snapshot.json`、`retrieval_context.json` 或既有检索上下文。
- 不读取、不返回、不记录明文 Key。
- 即使状态为 `ready_for_manual_dry_run`，`real_provider_config_allowed` 仍为 `false`。

## 本次新增

### Service

新增 `living_novel_engine.service.get_graph_memory_provider_spike_runbook(slug, projects_dir=None, now=None)`。

报告字段包括：

- `summary`：来源 readiness gate 状态、provider 数、ready/blocked 数、外部调用和真实配置边界。
- `runbook`：`ready_for_manual_dry_run`、`needs_more_evidence`、`blocked` 或 `deferred`，并显式说明 `manual_only=true`、`real_provider_config_allowed=false`。
- `provider_runbooks`：按 GraphRAG、Zep、Temporal Memory 展示人工 dry-run 输入、步骤、验收、回滚、暂停条件、证据引用和 no-go。
- `manual_review_checklist`：人工复核前必须确认的成本、隐私、回滚、验收和 no-go 项。
- `decision`：只允许进入人工 dry-run SOP 复核，不允许自动创建真实配置。
- `no_go_conditions`、`boundaries`、`next_steps`、`manifest` 和 `content_json`。

### HTTP API

新增：

```text
GET /api/stories/<slug>/graph-memory-provider-spike-runbook
```

状态约定：

- 坏 `slug` 返回 `400`。
- 项目不存在返回 `404`。
- 正常项目返回只读报告；小项目或证据不足时返回明确 `deferred` / `needs_more_evidence`，不抛 500。

### CLI

新增：

```powershell
lne memory graph-runbook <slug> --json
```

未加 `--json` 时输出 `content_json`，方便无人值守脚本保存或人工复查。

### 前端

项目工作台新增 `Graph 记忆 Provider Spike Runbook` 面板，展示：

- SOP 状态、ready provider 数、blocked provider 数、真实配置禁止状态。
- GraphRAG / Zep runbook、分阶段步骤、验收、回滚和暂停条件。
- manual checklist、no-go 条件和“不连接外部服务”的边界说明。

可见文案保持中文。缺失/暂缓状态显示为空态或说明，不白屏。

### API Contract / Typed Client

`get_api_contract()` 新增：

- endpoint：`/api/stories/{slug}/graph-memory-provider-spike-runbook`
- typed client method：`getGraphMemoryProviderSpikeRunbook`
- response type：`GraphMemoryProviderSpikeRunbookReport`

当前契约计数更新为：

- `endpoint_count=49`
- `openapi_path_count=48`
- `typed_client_method_count=48`

前端 `engine/ui/src/api/client.ts` 和 `types.ts` 已同步新增类型与方法。

## 验收

Focused tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_runbook.py tests/test_api_contract.py -q
```

结果：`7 passed`。

邻近回归：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_runbook.py tests/test_graph_memory_provider_spike_readiness_gate.py tests/test_graph_memory_provider_spike_fixture_pack.py tests/test_graph_memory_offline_shadow_replay_report.py tests/test_graph_memory_offline_shadow_replay_plan.py tests/test_graph_memory_provider_boundary_matrix.py tests/test_graph_memory_shadow_case_matrix.py tests/test_graph_memory_shadow_compare_pack.py tests/test_graph_memory_spike_design_pack.py tests/test_v093_graph_memory_trigger.py tests/test_api_contract.py -q
```

结果：`42 passed`。

浏览器烟测：

- 使用临时 `.local-run/graph-runbook-smoke` fixture。
- 后端指向临时 `LNE_PROJECTS_DIR`，`LLM_API_KEY` / `SEEDREAM_API_KEY` 清空，`LNE_MOCK=1`。
- 打开 `http://localhost:5173/#/workspace/graph-fixture-pack-large`。
- 已确认页面出现 `Graph 记忆 Provider Spike Runbook`、`可人工 dry-run`、`SOP 步骤 12`、`真实配置 禁止`、`锁定 dry-run 输入`、`人工执行离线 dry-run`、`复核成本、隐私和 no-go`、`演练回滚`、`不能要求真实付费 Key` no-go 和“不自动连接外部服务”的边界。
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

结果：后端 `815 passed`；前端 build 通过；`git diff --check` 通过，只有既有 CRLF 提示。

## 边界复核

- 路径安全：HTTP `slug` 经 `safe_id` 校验。
- 只读性：service 只消费 readiness gate，不写任何项目文件。
- 外部服务：没有 provider、HTTP client、embedding、GraphRAG、Zep、向量库或 reranker 调用。
- Key 安全：测试注入 fake key 并断言报告文本不包含密钥片段、环境变量名或临时路径。
- 旧契约：未改 `run_scene`，未改既有 artifact schema，新增 API/UI/type 字段均 additive。

## 下一刀建议

`Graph Memory Provider Spike Dry-run Result Template MVP`：

- 基于 runbook 输出只读人工 dry-run 结果记录模板。
- 把对比字段、暂停/升级判定、人工确认项和证据引用固定下来。
- 继续不创建真实 provider 配置、不读取真实 Key、不调用外部 GraphRAG、Zep、Temporal Memory、embedding provider、向量库或 reranker。
