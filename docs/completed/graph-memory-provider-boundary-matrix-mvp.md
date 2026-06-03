# Graph Memory Provider Boundary Matrix MVP 收口说明

日期：2026-06-01

## 目标

把 `Graph Memory Shadow Case Matrix` 进一步收束成真实 GraphRAG、Zep、Temporal Memory provider spike 前的只读边界矩阵，先把 opt-in 条件、成本、隐私、数据同步、回滚、测试和验收说清楚，再决定是否值得接任何重型服务。

本切片继续保持本地、只读、可回滚：

- 不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不写项目 artifact，不改变 `run_scene` 默认行为。
- 不覆盖 `canon_ledger.jsonl`、`state_snapshot.json` 或既有检索上下文。
- 不读取、不返回、不记录明文 Key。

## 本次新增

### Service

新增 `living_novel_engine.service.get_graph_memory_provider_boundary_matrix(slug, projects_dir=None, now=None)`。

报告字段包括：

- `summary`：来源 case matrix 状态、候选 provider 数、边界类别数、矩阵格数、高风险格数和安全边界。
- `boundary_gate`：`ready_for_boundary_review`、`collect_more_evidence` 或 `deferred`。
- `providers`：GraphRAG、Zep、Temporal Memory 的候选状态、试验理由、风险、回滚和暂缓原因。
- `boundary_categories`：显式开关、成本边界、隐私边界、数据同步、回滚策略、测试夹具、验收门槛和失败降级。
- `boundary_cells`：每个 provider x 每个边界类别的要求、风险等级、验收证据和 no-go 信号。
- `no_go_conditions`、`boundaries`、`next_steps` 和 `content_json`。

### HTTP API

新增：

```text
GET /api/stories/<slug>/graph-memory-provider-boundary-matrix
```

状态约定：

- 坏 `slug` 返回 `400`。
- 项目不存在返回 `404`。
- 正常项目返回只读报告；小项目或证据不足时返回明确 `deferred` / `needs_more_evidence`，不抛 500。

### CLI

新增：

```powershell
lne memory graph-boundaries <slug> --json
```

未加 `--json` 时输出 `content_json`，方便无人值守脚本保存或人工复查。

### 前端

项目工作台新增 `Graph 记忆 Provider 边界` 面板，展示：

- 边界状态、候选服务数、边界格数和高风险格数。
- GraphRAG / Zep 的显式开关、成本边界、隐私边界和验收要求。
- no-go 条件、失败降级和“不连接外部服务”的边界说明。

可见文案保持中文。缺失/暂缓状态显示为空态或说明，不白屏。

### API Contract / Typed Client

`get_api_contract()` 新增：

- endpoint：`/api/stories/{slug}/graph-memory-provider-boundary-matrix`
- typed client method：`getGraphMemoryProviderBoundaryMatrix`
- response type：`GraphMemoryProviderBoundaryMatrixReport`

当前契约计数更新为：

- `endpoint_count=46`
- `openapi_path_count=45`
- `typed_client_method_count=45`

前端 `engine/ui/src/api/client.ts` 和 `types.ts` 已同步新增类型与方法。

## 验收

Focused tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_boundary_matrix.py tests/test_api_contract.py -q
```

结果：`7 passed`。

邻近回归：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_provider_boundary_matrix.py tests/test_graph_memory_shadow_case_matrix.py tests/test_graph_memory_shadow_compare_pack.py tests/test_graph_memory_spike_design_pack.py tests/test_graph_memory_trigger_evidence.py tests/test_api_contract.py -q
```

结果：`23 passed`。

前端：

```powershell
cd D:\AI\open-infinite\engine\ui
pnpm.cmd run build
```

结果：通过。

浏览器烟测：

- 使用临时 `.local-run/graph-boundary-smoke` fixture。
- 后端指向临时 `LNE_PROJECTS_DIR`，`LLM_API_KEY` / `SEEDREAM_API_KEY` 清空，`LNE_MOCK=1`。
- 打开 `http://localhost:5173/#/workspace/graph-boundary-smoke-large`。
- 已确认页面出现 `Graph 记忆 Provider 边界`、`边界就绪`、`候选服务2`、`边界格16`、`高风险4`、`GraphRAG / 显式开关`、`GraphRAG / 成本边界`、`隐私边界`、no-go 条件和“不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM”边界。
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

结果：后端 `803 passed`；前端 build 通过；`git diff --check` 通过。

## 边界复核

- 路径安全：HTTP `slug` 经 `safe_id` 校验。
- 只读性：service 只消费 case matrix 报告，不写任何项目文件。
- 外部服务：没有 provider、HTTP client、embedding、GraphRAG、Zep、向量库或 reranker 调用。
- Key 安全：测试注入 fake key 并断言报告文本不包含密钥片段、环境变量名或临时路径。
- 旧契约：未改 `run_scene`，未改既有 artifact schema，新增 API/UI/type 字段均 additive。

## 下一刀建议

`Graph Memory Offline Shadow Replay Plan MVP` 已接续收口，见 `graph-memory-offline-shadow-replay-plan-mvp.md`。下一刀建议 `Graph Memory Provider Spike Fixture Pack MVP`：

- 基于 replay plan 生成 deterministic/mockable 的 per-case replay 结果、收益判断、失败降级和人工复核结论。
- 继续不运行真实 GraphRAG、Zep、Temporal Memory、embedding provider、向量库或 reranker。
- 仍保持只读，不创建 provider 配置、不写项目 artifact、不改变默认检索链路。
