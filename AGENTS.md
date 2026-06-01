# 未终章 Agent Instructions

本文件是 Codex / 其他代码 Agent 进入 `D:\AI\open-infinite` 时的项目级约定。若系统级指令与本文件冲突，以系统级指令为准；若项目文档互相冲突，以 `memory.md` 的最新收口状态为准。

## 用户背景

用户以个人开发者身份探索 AI 叙事项目。当前仓库 `D:\AI\open-infinite` 的核心项目是 **未终章（Unfinale）**，代码集中在 `engine/`。技术缩写、Python 包、CLI 和环境变量前缀仍沿用 LNE / `living_novel_engine`，不要在代码层面机械改名。

默认使用中文沟通。用户偏好：先读项目事实和现有代码，再做判断；不要靠聊天摘要臆测；实现要闭环到测试和文档同步。

## 会话开始必读

只要任务与 未终章、`engine/`、版本路线、产品 UI、API、测试或文档有关，开始动手前先阅读并对齐：

- `memory.md`
- `docs/living-novel-engine-iteration-plan.md`
- `docs/productization-phase-map.md`
- `docs/living-novel-engine-prd.md`
- `docs/completed/v0.7-product-web-app-ui-spec.md`
- `engine/README.md`
- 如存在接力任务，再读 `docs/codex-handoff.md`

读取重点：

- `memory.md`：当前状态、测试基线、已知缺口、文档索引
- `docs/project-changelog.md`：完整历史变更日志；仅在追溯版本过程或补历史记录时读取，避免新会话入口过重
- `docs/living-novel-engine-iteration-plan.md`：版本路线和下一刀范围
- `docs/productization-phase-map.md`：技术 MVP、产品化 MVP、长篇产品化、商业化加固的阶段归类
- `docs/living-novel-engine-prd.md`：产品定位和用户流程
- `docs/completed/v0.7-product-web-app-ui-spec.md`：已收口的 Web UI 风格和交互边界
- `engine/README.md`：CLI/API/输出结构/验收命令

事实优先级：

1. `memory.md`
2. `docs/living-novel-engine-iteration-plan.md`
3. `engine/README.md`
4. `docs/living-novel-engine-prd.md`
5. 聊天摘要

## 当前硬约束

- 不改 `run_scene` 默认行为，除非用户明确要求进入 runner 重构。
- 不破坏既有 artifact 契约：`chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 新增 artifact、API 字段、前端读取字段默认 additive。
- 后端 HTTP-facing identifier 必须走安全校验，不能把未经校验的 slug/run_id/branch_id 拼到文件路径。
- 失败要降级为明确的 400/404/409 或前端空态，不白屏、不 500。
- 前端产品文案默认中文；不要出现英文占位词。
- 视觉风格保持 v0.7 的古风纸面、克制系统感，不做营销落地页。
- `Reference_projects/` 与外部项目只作参考，不直接复制源码或引入依赖，除非用户明确要求。
- 不泄漏 API Key；设置页或日志只能展示脱敏尾号。
- 用户在 `.env` 中可能已经配置真实 `SEEDREAM_API_KEY` / `LLM_API_KEY`。测试要隔离环境，避免误打真实外网。

## 当前版本状态

截至 2026-06-01，当前收口状态以 `memory.md` 为准；本文件只保留 Agent 决策所需的高层摘要：

| 阶段 | 当前状态 |
| --- | --- |
| v0.7 | 短中篇产品化 Web App、Agent Interaction、Visual Asset、Baseline/Canon Replay、Worldline Judge 均已收口 |
| v0.8 | 长篇导入、分层记忆、正史账本、混合检索、审计、ActDirector、Narrator diagnostics、Dynamic Action Registry、Emergence Mining、Entity Alias、Runtime Memory Consumption、Artifact Panel、Long Upload Productization 均已收口 |
| v0.9.0-alpha | Long Novel Creation Loop 已整体收口，覆盖续写、世界线选择、审计、章节/合集导出、closeout API/CLI/record |
| v0.9.1-v0.9.4 | Provider/Cost、MasterSetting Workspace、Graph Memory Evaluation Spike、Advanced Runner Evaluation Spike 均已收口 |
| v1.0-beta | 本地优先商业化边界从 Scope-A 到 Billing Adapter Boundary-X 均已收口 |
| v1.0-local | Model Configuration UX 与 Local Run Scripts 已收口 |

当前验证基线：后端 `cd engine && python -m pytest -q` 为 `713 passed`；前端 `cd engine/ui && pnpm run build` 通过。

官方下一步：按用户要求，真实用户模型配置 UI 与本地一键运行脚本完成后暂停，等待用户本地试用反馈。后续排期仅在用户确认后进入 GitHub Release 安装包、内置 runtime、腾讯云/服务器在线体验等发行路径；真实外部用户前不默认做云端多租户、对象存储、认证或计费系统。

### 当前边界备忘

- 长篇导入已写入 `source_raw/`、`import_report.json`、`memory/`、`canon_ledger.jsonl`、`consistency_report.json`。
- `canon_ledger`、entity aliases 与 runtime memory 已进入只读检索/展示链路；正史 holdout 通过 `canon/visibility_manifest.json` 隔离。
- 干预 run 会写 `act_director_plan.json`、`narrative_diagnostics.json`、`dynamic_action_registry.yaml`、`emergence_nodes.json`，但这些机制产物暂不自动驱动 runner。
- 状态执行 overlay 可显式 apply/rollback，但不覆盖 `state_snapshot.json`，也不自动喂回下一轮 runner。
- 设置页已有脱敏 provider 状态、usage、route matrix、模型配置和本地运行脚本；不读取或打印明文密钥。
- 仍未做：云端多用户持久队列、真实对象存储 adapter、向量库/GraphRAG、overlay 自动消费、运行后审计写入正史账本。
- v1.0-beta 后续不默认接 Zep / 图数据库 / OASIS / CAMEL / LangGraph；这些按 v0.9.3 / v0.9.4 的触发式 spike 处理。

## 资料索引

- 已完成的 PRD、UI spec 及版本专项文档存储在 `D:\AI\open-infinite\docs\completed`。
- 参考论文 PDF 与论文解读报告存储在 `D:\AI\open-infinite\docs\article`，其中报告在 `D:\AI\open-infinite\docs\article\reports`。
- 参考开源项目存储在 `D:\AI\open-infinite\Reference_projects`，仅作设计参考和取舍分析，默认不直接复制源码、不引入依赖。
- `docs` 资料导航见 `D:\AI\open-infinite\docs\index.md`，用于快速定位 PRD、专项版本文档、论文报告和研究资料。
- 完整历史变更日志见 `D:\AI\open-infinite\docs\project-changelog.md`，仅在追溯过程或追加历史记录时读取。
- 当前主 PRD 入口是 `D:\AI\open-infinite\docs\living-novel-engine-prd.md`；专项 PRD、UI spec 和历史版本说明放在 `docs\completed`。
- v0.1-v0.8 历史审计快照见 `D:\AI\open-infinite\docs\completed\v0.1-to-v0.8-version-audit.md`；该文档不承担当前待办来源。

## 开发流程

默认流程：

1. 读上述文档和相关代码。
2. 用现有模式实现，保持改动局部。
3. 补 service / API / 前端类型和 UI 测试，测试规模随风险调整。
4. 跑验证命令。
5. 同步 `memory.md` 当前状态；若有历史记录需要追加，同步 `docs/project-changelog.md`；必要时同步迭代计划、README、UI spec。

常用验证：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

Windows 注意：

- `rg` 若不可用或被系统拦截，用 `Get-ChildItem` / `Select-String` / `Get-Content`。
- PowerShell 没有原生 `tail` / `printf`，不要把 Linux shell 命令硬套过来。

## Cursor 迁移说明

`.cursor/rules/project-memory.mdc` 的核心规则已迁移到本文件和 `docs/codex-handoff.md`。`.cursor/skills/` 里多数是通用 Claude/Cursor 技能包；在 Codex 中优先使用已安装的 Codex skills/plugins：

- 前端：Build Web Apps / Vercel 相关 skills
- 文档：Documents / Presentations / Spreadsheets
- OpenAI：OpenAI Developers
- 方法论：Superpowers

不要把 `.cursor/skills/` 整包复制进 Codex 上下文；需要某个具体工作流时，再按 `docs/codex-migration-guide.md` 选择性迁移。
