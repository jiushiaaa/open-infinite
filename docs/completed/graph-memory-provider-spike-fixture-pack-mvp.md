# Graph Memory Provider Spike Fixture Pack MVP 收口说明

日期：2026-06-01

## 目标

把 `Graph Memory Offline Shadow Replay Report` 继续收束成真实 GraphRAG、Zep、Temporal Memory provider spike 前的 dry-run 前置包。该前置包只描述单 provider、单项目、单 fixture 的输入、预期输出、成本/隐私/回滚 checklist、人工验收项和 no-go 条件，不创建真实 provider 配置。

本切片继续保持本地、只读、可回滚：

- 不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不写项目 artifact，不改变 `run_scene` 默认行为。
- 不覆盖 `canon_ledger.jsonl`、`state_snapshot.json`、`retrieval_context.json` 或既有检索上下文。
- 不读取、不返回、不记录明文 Key。

## 本次新增

### Service

新增 `living_novel_engine.service.get_graph_memory_provider_spike_fixture_pack(slug, projects_dir=None, now=None)`。

报告字段包括：

- `summary`：来源 replay report 状态、provider fixture 数、选中 fixture 数、待人工复核数和安全边界。
- `fixture_gate`：`fixture_pack_ready`、`collect_more_evidence` 或 `deferred`。
- `provider_fixture_packs`：按 GraphRAG、Zep、Temporal Memory 聚合 dry-run fixture、成本 guardrail、隐私 guardrail、回滚 checklist、manual acceptance 和 no-go 条件。
- `fixture`：单 provider、单项目、单 fixture 的 dry-run 输入，包含来源 case、baseline chain、预期输出和失败降级说明。
- `decision`：是否需要先人工复核，再决定是否创建真实 provider 配置。
- `no_go_conditions`、`boundaries`、`next_steps` 和 `content_json`。

### HTTP API

新增：

```text
GET /api/stories/<slug>/graph-memory-provider-spike-fixture-pack
```

状态约定：

- 坏 `slug` 返回 `400`。
- 项目不存在返回 `404`。
- 正常项目返回只读报告；小项目或证据不足时返回明确 `deferred` / `needs_more_evidence`，不抛 500。

### CLI

新增：

```powershell
lne memory graph-fixture-pack <slug> --json
```

未加 `--json` 时输出 `content_json`，方便无人值守脚本保存或人工复查。

### 前端

项目工作台新增 `Graph 记忆 Provider Spike 前置包` 面板，展示：

- 前置包状态、候选服务、选中 fixture 和待复核数量。
- GraphRAG / Zep 的 dry-run fixture、来源 case 和候选收益说明。
- manual review checklist、no-go 条件和“不连接外部服务”的边界说明。

可见文案保持中文。缺失/暂缓状态显示为空态或说明，不白屏。

### API Contract / Typed Client

`get_api_contract()` 新增：

- endpoint：`/api/stories/{slug}/graph-memory-provider-spike-fixture-pack`
- typed client method：`getGraphMemoryProviderSpikeFixturePack`
- response type：`GraphMemoryProviderSpikeFixturePackReport`

当前契约计数更新为：

- `endpoint_count=47`
- `openapi_path_count=46`
- `typed_client_method_count=46`

前端 `engine/ui/src/api/client.ts` 和 `types.ts` 已同步新增类型与方法。

## 验收

Focused tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_fixture_pack.py tests/test_api_contract.py -q
```

结果：`7 passed`。

邻近回归：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_spike_fixture_pack.py tests/test_graph_memory_offline_shadow_replay_report.py tests/test_graph_memory_offline_shadow_replay_plan.py tests/test_graph_memory_provider_boundary_matrix.py tests/test_graph_memory_shadow_case_matrix.py tests/test_graph_memory_shadow_compare_pack.py tests/test_graph_memory_spike_design_pack.py tests/test_v093_graph_memory_trigger.py tests/test_api_contract.py -q
```

结果：`34 passed`。

前端：

```powershell
cd D:\AI\open-infinite\engine\ui
pnpm.cmd run build
```

结果：通过。

浏览器烟测：

- 使用临时 `.local-run/graph-fixture-pack-smoke` fixture。
- 后端指向临时 `LNE_PROJECTS_DIR`，`LLM_API_KEY` / `SEEDREAM_API_KEY` 清空，`LNE_MOCK=1`。
- 打开 `http://localhost:5173/#/workspace/graph-fixture-pack-smoke-large`。
- 已确认页面出现 `Graph 记忆 Provider Spike 前置包`、`前置包就绪`、`候选服务 2`、`选中 fixture 2`、`待复核 2`、GraphRAG/Zep dry-run fixture、`不能要求真实付费 Key` no-go 和“不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM”边界。
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

结果：后端 `807 passed`；前端 build 通过；`git diff --check` 通过。

## 边界复核

- 路径安全：HTTP `slug` 经 `safe_id` 校验。
- 只读性：service 只消费 offline replay report，不写任何项目文件。
- 外部服务：没有 provider、HTTP client、embedding、GraphRAG、Zep、向量库或 reranker 调用。
- Key 安全：测试注入 fake key 并断言报告文本不包含密钥片段、环境变量名或临时路径。
- 旧契约：未改 `run_scene`，未改既有 artifact schema，新增 API/UI/type 字段均 additive。

## 下一刀建议

`Graph Memory Provider Spike Readiness Gate MVP`：

- 基于 fixture pack、no-go、成本/隐私/回滚 checklist 和人工验收项输出只读 readiness gate。
- 标记是否仍应 `blocked`、`needs_more_evidence`、`ready_for_manual_opt_in_review`，并列出继续暂缓原因。
- 继续不创建真实 provider 配置、不读取真实 Key、不调用外部 GraphRAG、Zep、Temporal Memory、embedding provider、向量库或 reranker。
