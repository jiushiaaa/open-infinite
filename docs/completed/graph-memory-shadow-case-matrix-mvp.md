# Graph Memory Shadow Case Matrix MVP 收口说明

日期：2026-06-01

## 目标

把 `Graph Memory Shadow Compare Pack` 从“候选层级对照”下钻成“每条 eval case x 每个候选记忆层”的只读矩阵，帮助后续判断 GraphRAG、Zep、Temporal Memory 是否真的值得进入 opt-in provider spike。

本切片继续保持轻量、可回滚、可解释：

- 不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
- 不写项目 artifact，不改变 `run_scene` 默认行为。
- 不覆盖 `canon_ledger.jsonl`、`state_snapshot.json` 或既有检索上下文。
- 不读取、不返回、不记录明文 Key。

## 本次新增

### Service

新增 `living_novel_engine.service.get_graph_memory_shadow_case_matrix(slug, projects_dir=None, now=None)`。

报告字段包括：

- `summary`：来源 shadow compare 状态、case 数、候选层数、矩阵格数、候选格数、本地证据格数和安全边界。
- `case_gate`：`case_matrix_ready`、`collect_more_evidence` 或 `deferred`。
- `layers`：GraphRAG、Zep、Temporal Memory 候选层的状态、决策、收益、风险、缺口和回退策略。
- `cases`：从本地 retrieval eval records 派生的样本 query、baseline 状态和诊断。
- `cells`：每个 case 与候选层的 `status`、`decision`、`evidence_status`、`evidence_refs`、`shadow_question`、`missing_evidence`、收益/风险分。
- `no_go_conditions`、`boundaries`、`next_steps` 和 `content_json`。

### HTTP API

新增：

```text
GET /api/stories/<slug>/graph-memory-shadow-case-matrix
```

状态约定：

- 坏 `slug` 返回 `400`。
- 项目不存在返回 `404`。
- 正常项目返回只读报告；小项目或证据不足时返回明确 `deferred` / `needs_more_evidence`，不抛 500。

### CLI

新增：

```powershell
lne memory graph-cases <slug> --json
```

未加 `--json` 时输出 `content_json`，方便无人值守脚本保存或人工复查。

### 前端

项目工作台新增 `Graph 记忆 Case 矩阵` 面板，展示：

- 矩阵状态、样本数、候选格、本地证据格。
- GraphRAG / Zep / Temporal Memory 的 per-case shadow question。
- 本地证据就绪状态、样本 query、no-go 条件和 provider 禁用边界。

可见文案保持中文。缺失/暂缓状态显示为空态或说明，不白屏。

### API Contract / Typed Client

`get_api_contract()` 新增：

- endpoint：`/api/stories/{slug}/graph-memory-shadow-case-matrix`
- typed client method：`getGraphMemoryShadowCaseMatrix`
- response type：`GraphMemoryShadowCaseMatrixReport`

前端 `engine/ui/src/api/client.ts` 和 `types.ts` 已同步新增类型与方法。

## 验收

Focused tests：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_shadow_case_matrix.py tests/test_api_contract.py -q
```

结果：`7 passed`。

邻近回归：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest tests/test_graph_memory_shadow_case_matrix.py tests/test_graph_memory_shadow_compare_pack.py tests/test_graph_memory_spike_design_pack.py tests/test_graph_memory_trigger_evidence.py tests/test_api_contract.py -q
```

结果：`19 passed`。

前端：

```powershell
cd D:\AI\open-infinite\engine\ui
pnpm.cmd run build
```

结果：通过。

浏览器烟测：

- 使用临时 `.local-run/graph-case-smoke` fixture。
- 后端指向临时 `LNE_PROJECTS_DIR`，`LLM_API_KEY` / `SEEDREAM_API_KEY` 清空，`LNE_MOCK=1`。
- 打开 `http://localhost:5173/#/workspace/graph-case-smoke-large`。
- 已确认页面出现 `Graph 记忆 Case 矩阵`、`矩阵就绪`、`样本 1`、`候选格 2`、`证据格 2`、GraphRAG/Zep shadow question、真实 provider no-go 和“不连接 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM”边界。
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

结果：后续 Graph Memory Offline Shadow Replay Plan MVP 接续完成后，后端全量基线更新为 `803 passed`；前端 build 通过；`git diff --check` 通过。

## 边界复核

- 路径安全：HTTP `slug` 经 `safe_id` 校验。
- 只读性：service 只消费 shadow compare 报告，不写任何项目文件。
- 外部服务：没有 provider、HTTP client、embedding、GraphRAG、Zep、向量库或 reranker 调用。
- Key 安全：测试注入 fake key 并断言报告文本不包含密钥片段、环境变量名或临时路径。
- 旧契约：未改 `run_scene`，未改既有 artifact schema，新增 API/UI/type 字段均 additive。

## 下一刀建议

`Graph Memory Provider Boundary Matrix MVP` 与 `Graph Memory Offline Shadow Replay Plan MVP` 已接续收口，见 `graph-memory-provider-boundary-matrix-mvp.md`、`graph-memory-offline-shadow-replay-plan-mvp.md` 与 `graph-memory-offline-shadow-replay-report-mvp.md`。下一刀建议进入 `Graph Memory Provider Spike Fixture Pack MVP`：

- 基于 provider boundary matrix，整理高收益 case 的离线 shadow replay 输入、验收、回滚和人工复核步骤。
- 对 GraphRAG、Zep、Temporal Memory 分别列出 replay fixture、expected delta、review checklist 和 no-go 门槛。
- 仍保持只读，不连接真实 provider，不创建向量库或图数据库。
