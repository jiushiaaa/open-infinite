# 未终章

未终章（Unfinale）是 `open-infinite` 的叙事引擎与本地产品工作台。当前已经从早期 Phase 0 CLI 演进到 v1.0-local：支持小说导入、长篇记忆、读者干预、多世界线生成、审计评估、章节导出、模型配置和本地一键运行。

命名边界：面向用户和文档的产品名为“未终章 / Unfinale”；Python 包、CLI、artifact 路径和环境变量前缀仍沿用 LNE / `living_novel_engine`。

当前事实、版本状态和暂停点以根目录 [`../memory.md`](../memory.md) 为准；历史版本细节在 [`../docs/completed/`](../docs/completed/README.md)。

## 当前状态

| 项 | 状态 |
| --- | --- |
| 后端 | Python package + `lne` CLI + 本地 HTTP API |
| 前端 | `engine/ui` React + Vite 产品工作台 |
| 当前收口 | v1.0-local Model Configuration UX + Local Run Scripts |
| 后端验证基线 | `python -m pytest -q` -> `713 passed` |
| 前端验证基线 | `cd engine/ui && pnpm run build` 通过 |
| 当前暂停点 | 等待本地试用反馈；不继续默认开新刀 |

仍然后置：云端多用户持久队列、真实对象存储 adapter、真实认证、硬配额执行、商业计费系统、webhook、向量库/GraphRAG、高级 runner 默认替换。

## 快速开始

推荐从仓库根目录使用本地启动脚本：

```powershell
cd D:\AI\open-infinite
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start-local.ps1
```

脚本会检查 Python、Node.js、pnpm，准备 `engine/.venv`，安装依赖，启动后端 `lne browse` 和 Vite 前端，并打开 `http://127.0.0.1:5173/`。日志写入根目录 `.local-run/`。

只检查环境、不启动服务：

```powershell
cd D:\AI\open-infinite
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start-local.ps1 -CheckOnly -NoBrowser
```

macOS / Linux:

```bash
cd /path/to/open-infinite
bash scripts/start-local.sh
bash scripts/start-local.sh --check-only --no-browser
```

## 手动安装

```powershell
cd D:\AI\open-infinite\engine
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
```

前端：

```powershell
cd D:\AI\open-infinite\engine\ui
pnpm install
pnpm run build
```

## 配置

复制 `engine/.env.example` 为 `engine/.env`，按需填写：

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

SEEDREAM_API_KEY=your_seedream_key
SEEDREAM_BASE_URL=https://ark.cn-beijing.volces.com
SEEDREAM_MODEL=seedream-5-0-lite
SEEDREAM_PATH=/api/v3/images/generations
LNE_VISUAL_ASSETS=1
```

密钥边界：

- 未配置 `LLM_API_KEY` 或设置 `LNE_MOCK=1` 时，文字链路走本地 mock / deterministic fallback。
- 未配置 `SEEDREAM_API_KEY` 或设置 `LNE_VISUAL_ASSETS=0` 时，视觉资产稳定降级为占位，不阻塞文字主流程。
- 设置页和 API 只返回脱敏状态，不回显明文 Key。

常用环境变量：

| 变量 | 作用 |
| --- | --- |
| `LNE_MOCK=1` | 强制 mock 模型调用 |
| `LNE_SCENE_RUNNER=lightweight` | 默认 runner，保持旧行为 |
| `LNE_SCENE_RUNNER=multi_agent_stub` | 使用确定性多 Agent stub |
| `LNE_SCENE_RUNNER=multi_agent_llm` | 使用 OpenAI-compatible LLM 多 Agent runner，非默认 |
| `LNE_FOURTH_WALL=0` | 关闭第四面墙账本与注入 |
| `LNE_PROJECTS_DIR` | 覆盖项目目录，测试/临时运行常用 |
| `LNE_OUTPUTS_DIR` | 覆盖输出目录，测试/临时运行常用 |

## 常用命令

```powershell
cd D:\AI\open-infinite\engine

# 查看样例和项目
lne list-samples
lne show-sample tianhuang-night
lne list-projects
lne show-project <slug>
lne validate-project <slug>

# 内置样例干预，mock 不需要 API Key
lne intervene tianhuang-night --target lin_wan_zhou --content "今晚不要去城外竹林" --mock
lne compare outputs\run_YYYYMMDD_HHMMSS

# 沿世界线续写
lne resume continue <run_id> --branch branch_a --mock
lne resume intervene <continue_run_id> --branch linear --target lin_fan --content "告诉林晚舟，她身后的影子来自乱葬岗" --mock

# 导入自己的小说
lne import-novel tests\fixtures\mini_novel --name my-story --mock
lne validate-project my-story
lne intervene my-story --target zhao_xuan --content "今夜不要去归云斋" --mock

# 本地后端/API viewer
lne browse --host 127.0.0.1 --port 8765 --no-open

# v0.9.0-alpha 长篇闭环验收
lne creation-loop-closeout <slug> --json --require-ready --write-report
```

`browse` 启动的是本地后端和旧只读 viewer；普通用户产品入口在 `engine/ui`，通过 Vite 访问。

## 前端开发

```powershell
cd D:\AI\open-infinite\engine
lne browse --host 127.0.0.1 --port 8765 --no-open

cd D:\AI\open-infinite\engine\ui
$env:LNE_API_TARGET='http://127.0.0.1:8765'
pnpm run dev -- --host 127.0.0.1 --port 5173
```

打开 `http://127.0.0.1:5173/`。

前端主要能力：

- 书架、导入、主题创世、世界锚定轻编辑。
- 阅读工作台、读者干预、动态分支轴、Causal Diff、世界线评审。
- 长篇项目工作台、导入检查、设定工作台、回放与审计、章节导出。
- 设置抽屉：运行设置、模型配置、provider 状态、usage/成本估算、商业化边界只读清单。

## 产物目录

```text
engine/
├── projects/              # 导入/创世项目与项目级 memory
├── outputs/               # run 输出、分支正文、评审、审计 artifact
├── samples/               # 内置样例
├── src/living_novel_engine/
├── tests/
└── ui/
```

导入项目常见结构：

```text
projects/<slug>/
├── source/                         # 运行时可见章节
├── source_raw/                     # 规范化原文账本
├── import_report.json
├── world.yaml
├── characters.yaml
├── story_contract.yaml
├── visual_assets.json
├── assets/
├── canon/
│   ├── facts.jsonl
│   ├── holdout/
│   └── visibility_manifest.json
└── memory/
    ├── master_setting.yaml
    ├── canon_ledger.jsonl
    ├── consistency_report.json
    ├── entity_aliases.yaml
    ├── project_audit_log.jsonl
    ├── project_copyright_statement.json
    └── project_retention_policy.json
```

一次干预 run 常见结构：

```text
outputs/<run_id>/
├── meta.json
├── intervention.json
├── intervention_compilation.json
├── compare.md
├── act_director_plan.json
├── dynamic_action_registry.yaml
├── emergence_nodes.json
├── runner_state_execution_report.json
├── runner_state_execution_apply_report.json
├── runner_state_execution_rollback_report.json
├── branch_a/
│   ├── chapter.md
│   ├── events.json
│   ├── state_snapshot.json
│   ├── retrieval_context.json
│   ├── runtime_memory_context.json
│   ├── causal_diff.json
│   ├── multi_agent_trace.json
│   ├── narrative_diagnostics.json
│   ├── worldline_judgement.json
│   └── state_execution_overlay.json
├── branch_b/
└── branch_c/
```

不是每个 run 都会拥有上面所有 artifact；缺失或损坏时，前端/API 应显示空态或明确 `400/404/409`，不应白屏或默默 500。

## 核心契约

- 不改变 `run_scene` 默认行为；默认 runner 仍是 `lightweight`。
- 既有核心 artifact 契约保持稳定：`chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 新增字段、API 和 artifact 默认 additive。
- HTTP-facing `slug` / `run_id` / `branch_id` 必须通过安全校验后才能拼路径。
- `source/` 是运行时可见正文；holdout 私有正文只用于 evaluator，不能进入 narrator / retrieval / 角色 agent。
- 状态执行 MVP 只写 `state_execution_overlay.json`，不覆盖原 `state_snapshot.json`。
- Project audit log 当前是本地 JSONL，不代表云端不可篡改审计证明。

## HTTP API 分组

完整路由以 `src/living_novel_engine/browser/server.py` 和测试为准。常用分组：

| 分组 | 典型路径 |
| --- | --- |
| 故事/项目 | `GET /api/stories`、`GET /api/stories/<slug>`、`GET /api/stories/<slug>/project-workspace` |
| 导入/创世/job | `POST /api/import-novel`、`POST /api/story-genesis`、`POST /api/jobs/import-novel`、`GET /api/jobs/<id>` |
| 干预/续写 | `POST /api/interventions`、`POST /api/jobs/intervention`、`POST /api/jobs/resume-continue` |
| run/branch | `GET /api/runs`、`GET /api/runs/<run_id>`、`GET /api/runs/<run_id>/branches/<branch_id>` |
| 评估/审计 | baseline、canon replay、worldline judgement、replay audit、audit log、creation loop closeout |
| 导出 | chapter export、chapter collection export、audit log export |
| 设置 | runtime、providers、provider usage、model configuration、commercial status、preflight/boundary checklists |

API 设计原则：坏 ID 返回 400，缺资源返回 404，状态冲突/不可操作返回 409；密钥只返回脱敏状态。

## 验证

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

真实外部模型 smoke 不是 pytest 的前置条件。需要真实联调时，先确认 `.env` 中 Key 是你想使用的账号，并避免在测试中误打外网。

## 文档索引

| 文档 | 用途 |
| --- | --- |
| [`../AGENTS.md`](../AGENTS.md) | Agent 进入仓库时的项目级规则 |
| [`../memory.md`](../memory.md) | 当前状态、测试基线、暂停点、真实未做项 |
| [`../docs/index.md`](../docs/index.md) | docs 总导航 |
| [`../docs/living-novel-engine-iteration-plan.md`](../docs/living-novel-engine-iteration-plan.md) | 当前路线图 |
| [`../docs/productization-phase-map.md`](../docs/productization-phase-map.md) | 产品化阶段归类 |
| [`../docs/living-novel-engine-prd.md`](../docs/living-novel-engine-prd.md) | 主 PRD |
| [`../docs/completed/README.md`](../docs/completed/README.md) | 已收口专项文档索引 |
| [`../docs/project-changelog.md`](../docs/project-changelog.md) | 从 `memory.md` 迁出的完整历史变更日志 |
| [`../docs/distribution-phase-plan.md`](../docs/distribution-phase-plan.md) | 后续发行路径：本地 clone、GitHub Release、服务器在线体验 |

## 当前后置项

这些不是当前默认实现范围：

- 云端多用户持久队列、对象存储 adapter、真实认证、团队空间、请求级 ACL。
- 硬配额拦截、真实账单、支付、webhook/idempotency、商业计费系统。
- Zep / 图数据库 / GraphRAG / embedding / reranker，除非现有 BM25 + canon ledger + entity aliases 在真实长篇样例中明确不足。
- OASIS / CAMEL / LangGraph，除非现有 runner、trace 与状态执行层无法解释真实复杂样例。
- overlay 自动驱动下一轮 runner、运行后审计写入正史账本、LLM 语义评审和 run 级聚合评审。
