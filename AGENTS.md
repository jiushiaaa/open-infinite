# Living Novel Engine Agent Instructions

本文件是 Codex / 其他代码 Agent 进入 `D:\AI\open-infinite` 时的项目级约定。若系统级指令与本文件冲突，以系统级指令为准；若项目文档互相冲突，以 `memory.md` 的最新收口状态为准。

## 用户背景

用户在湖州云梯科技担任 AI 产品经理实习，主要负责 AI 课堂和 AI 作文业务；同时以个人开发者身份探索 AI 叙事项目。当前仓库 `D:\AI\open-infinite` 的核心项目是 **Living Novel Engine**，代码集中在 `engine/`。

默认使用中文沟通。用户偏好：先读项目事实和现有代码，再做判断；不要靠聊天摘要臆测；实现要闭环到测试和文档同步。

## 会话开始必读

只要任务与 Living Novel Engine、`engine/`、版本路线、产品 UI、API、测试或文档有关，开始动手前先阅读并对齐：

- `memory.md`
- `docs/living-novel-engine-iteration-plan.md`
- `docs/productization-phase-map.md`
- `docs/living-novel-engine-prd.md`
- `docs/completed/v0.7-product-web-app-ui-spec.md`
- `engine/README.md`
- 如存在接力任务，再读 `docs/codex-handoff.md`

读取重点：

- `memory.md`：当前状态、测试基线、已知缺口、变更日志
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

截至 2026-05-31：

- v0.7 Product Web App 九刀已收口。
- v0.7.2 Agent Interaction 已收口。
- v0.7.3 Visual Asset Generation 已收口。
- v0.7.4 Baseline & Canon Replay 已收口，并经 Codex 兜底补安全边界。
- v0.7.5 Worldline Judge 已收口。
- v0.8.0-A 至 v0.8.5-A Long Novel Memory 底座已收口。
- v0.8+ ActDirector-A planning artifact 已收口。
- v0.8+ Discourse-aware Narrator-A diagnostics artifact 已收口。
- v0.8+ Dynamic Action Registry-A 已收口。
- v0.8+ Emergence Mining-A 已收口。
- v0.8.x Entity Aliases / Entity Resolution 已收口。
- v0.8.x Runtime Memory Consumption-A 已收口。
- v0.8.x Frontend Artifact Panel 已收口。
- v0.8.x Long Upload Productization 已收口。
- v0.8.6 Long Import Review 已收口。
- v0.8.7 Resumable Ingest Jobs 已收口。
- 当前后端验证基线：`581 passed`。
- 当前前端验证基线：`cd engine/ui && pnpm run build` 通过。
- 官方下一版：`v0.8.8 Long Project Workspace`，先做长篇项目详情页，集中展示章节、记忆、正史账本、实体别名、检索命中和审计报告。
- 后续排期：`v0.8.9 Long Replay & Audit UI` → `v0.8.10-A/B Runner State Execution` → `v0.9.0-alpha Long Novel Creation Loop` → `v0.9.1-v0.9.4` 触发式增强 → `v1.0-beta` 商业化加固。

最近一次 Codex 迭代：

- 长篇导入写入 `source_raw/`、`import_report.json`、`memory/`、`canon_ledger.jsonl`、`consistency_report.json`。
- `canon_ledger` 已接入 BM25 检索 artifact，source 为 `canon_ledger`。
- 正史 holdout 已写 `canon/visibility_manifest.json`，明确 `runtime_visible` / `holdout_private` 隔离。
- 干预 run 会写 `act_director_plan.json`，但该计划暂不驱动 runner。
- 分支会写 `narrative_diagnostics.json`，但诊断暂不反馈到 narrator。
- 干预 run 会写 `dynamic_action_registry.yaml` 与 `emergence_nodes.json`，但暂不执行状态变化、不做推荐系统。
- 干预、baseline 与 CLI resume 会通过既有 `retrieved_context` 参数只读消费 memory/alias/ledger 安全子集，并写分支 `runtime_memory_context.json`。
- 前端右侧「机制档案」已统一只读展示运行记忆、动作计划、动作注册表、叙事诊断、涌现节点。
- 前端导入页已支持 txt/md/zip/epub 文件选择、浏览器端分片、job 进度条与失败空态；后端 upload payload 会解析分片并复用既有导入流水线。
- `import_report.json` 已升级为 v0.8.6 导入检查报告，包含来源、章节统计、章节片段、解析 warning、质量风险和建议动作；`get_story()` / `get_world_anchor()` 返回 `import_review`，报告缺失或损坏会降级为空态。
- 前端世界锚定页已新增「导入检查」，展示来源、章节数、正文片段、风险提示和下一步建议；坏 zip / epub / 空文件 / 章节过少错误态已收束为明确 400 或前端失败空态。
- 前端导入页已接入服务端 ingest session：可查询缺失分片、重复 chunk 幂等、hash 校验、localStorage 恢复续传，complete 后复用既有 import job。
- 仍未做云端多用户持久队列、对象存储、向量库、runner 消费 action/emergence 层并执行状态变化、批量长篇 replay UI。
- 当前仍属于 v0.8.x 收束期，不要直接跳 v0.9；v0.9.0-alpha 应在 v0.8.8-v0.8.10 收口后再开启，且不默认接 Zep / 图数据库 / OASIS / CAMEL / LangGraph。

## 资料索引

- 已完成的 PRD、UI spec 及版本专项文档存储在 `D:\AI\open-infinite\docs\completed`。
- 参考论文 PDF 与论文解读报告存储在 `D:\AI\open-infinite\docs\article`，其中报告在 `D:\AI\open-infinite\docs\article\reports`。
- 参考开源项目存储在 `D:\AI\open-infinite\Reference_projects`，仅作设计参考和取舍分析，默认不直接复制源码、不引入依赖。
- `docs` 资料导航见 `D:\AI\open-infinite\docs\index.md`，用于快速定位 PRD、专项版本文档、论文报告和研究资料。
- 当前主 PRD 入口是 `D:\AI\open-infinite\docs\living-novel-engine-prd.md`；专项 PRD、UI spec 和历史版本说明放在 `docs\completed`。
- v0.1-v0.8 已完成能力与未做项总览见 `D:\AI\open-infinite\docs\completed\v0.1-to-v0.8-version-audit.md`。

## 开发流程

默认流程：

1. 读上述文档和相关代码。
2. 用现有模式实现，保持改动局部。
3. 补 service / API / 前端类型和 UI 测试，测试规模随风险调整。
4. 跑验证命令。
5. 同步 `memory.md` 变更日志；必要时同步迭代计划、README、UI spec。

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
