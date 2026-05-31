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
- v0.8.8 Long Project Workspace 已收口。
- v0.8.9 Long Replay & Audit UI 已收口。
- v0.8.10-A Runner State Execution Spike 已收口。
- v0.8.10-B Runner State Execution MVP 已收口。
- v0.9.0-alpha Chapter Export 已收口。
- v0.9.0-alpha Creation Loop Checklist 已收口。
- v0.9.0-alpha Continuation Hint 已收口。
- v0.9.0-alpha Resume Continue HTTP Job 已收口。
- v0.9.0-alpha Worldline Selection Persistence 已收口。
- v0.9.0-alpha Post-run Audit Entry 已收口。
- v0.9.0-alpha Chapter Collection Export 已收口。
- v0.9.0-alpha Export Share Guard 已收口。
- v0.9.0-alpha Creation Loop Completion Gate 已收口。
- v0.9.0-alpha Creation Loop Action Hints 已收口。
- v0.9.0-alpha Creation Loop Readiness Evidence 已收口。
- v0.9.0-alpha Creation Loop Audit Quick Run 已收口。
- v0.9.0-alpha Creation Loop Alpha Ready State 已收口。
- v0.9.0-alpha Creation Loop Alpha Closeout Report 已收口。
- v0.9.0-alpha Creation Loop Closeout API 已收口。
- v0.9.0-alpha Creation Loop Closeout CLI 已收口。
- v0.9.0-alpha Creation Loop Closeout Record 已收口。
- v0.9.0-alpha Low-risk Audit Closeout 已收口，整体 Long Novel Creation Loop 已收口。
- v0.9.1 Provider Gateway Summary-A 已收口。
- v0.9.1 Provider Usage Summary-B 已收口。
- v0.9.1 Provider Status Panel-C 已收口。
- v0.9.1 Manual Price Estimate-D 已收口。
- v0.9.1 Route Matrix-E 已收口。
- v0.9.1 Provider & Cost Gateway Lite 已整体收口。
- v0.9.2 MasterSetting Workspace Summary-A 已收口。
- v0.9.2 MasterSetting Workspace Panel-B 已收口。
- v0.9.2 MasterSetting Workspace Edit-C 已收口。
- v0.9.2 MasterSetting Workspace Frontend-D 已收口。
- v0.9.2 MasterSetting Workspace Lite 已整体收口。
- v0.9.3 Graph Memory Evaluation Trigger-A 已收口。
- v0.9.3 Retrieval Probe-B 已收口。
- v0.9.3 Graph Memory Evaluation Spike 已整体收口。
- v0.9.4 Advanced Runner Evaluation Trigger-A 已收口。
- v0.9.4 Advanced Runner Probe-B 已收口。
- v0.9.4 Advanced Runner Evaluation Spike 已整体收口。
- v1.0-beta Commercial Hardening Scope-A 已收口。
- 当前后端验证基线：`645 passed`。
- 当前前端验证基线：`cd engine/ui && pnpm run build` 通过。
- 官方下一刀：`v1.0-beta Commercial Audit Log Schema-B`。
- 后续排期：`v1.0-beta` 本地优先商业化加固（审计日志、权限矩阵、版权声明），真实外部用户前不默认做云端多租户/计费系统。

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
- `GET /api/stories/<slug>/project-workspace` 已聚合导入检查、章节预览、分层记忆、正史账本、实体别名、检索命中、审计报告和下一步入口；前端 `WorkspacePage` 未选世界线时展示长篇项目资产页。
- `POST /api/stories/<slug>/canon/replay-range` 已支持按章节范围批量 Canon Replay 并写 `canon_replay_range_report.json`；`GET /api/stories/<slug>/replay-audit` 已聚合 baseline、range replay、静态审计维度、实体别名摘要与下一步建议。
- 前端「回放与审计」面板已支持单章/范围回放、风险维度、实体归一化审计、holdout/审计空态展示。
- 干预 run 可生成 `runner_state_execution_report.json` dry-run 评估，解释 action/emergence 是否能安全转成状态 delta；该报告不写 `state_snapshot.json`、不改 `run_scene` 默认行为。
- 干预 run 可在显式确认后把 low-risk/executable/白名单 delta 写入分支 `state_execution_overlay.json`，并通过 `runner_state_execution_apply_report.json` / `runner_state_execution_rollback_report.json` 审计和回滚；原 `state_snapshot.json` 不被覆盖。
- `v0.9.0-alpha` 已整体收口：只读章节导出、父链章节合集导出、导出版权/分享 guard、创作闭环完成度判定、阻塞动作提示（含评审/设为起点 payload 与审计 requirements）、判定依据、审计快捷运行、alpha ready 状态、alpha closeout 报告、closeout HTTP 验收接口（含阻塞动作清单和稳定 blocker id）与 `lne creation-loop-closeout` 本地验收命令均已落地；CLI 可在 ready 后用 `--write-report` 写入 `creation_loop_alpha_closeout.json` 收口记录，未 ready 不落盘。低风险静态审计 info 不再阻断 closeout，中高风险仍阻断。CLI 续写入口、显式 `POST /api/jobs/resume-continue`、`selected_worldline.json` 选择记录与选择后审计入口已接入；推荐世界线可从前端生成评审、生成下一章，也可「设为起点」并在工作台读回审计状态、范围回放风险、缺失实体和审计前置条件；builtin 样例无法录入 holdout 时会明确标为 blocked。
- `v0.9.1 Provider Gateway Summary-A` 已新增只读 `GET /api/settings/providers`，返回脱敏 provider 列表、单 provider 路由状态、mock/占位图降级策略、成本观测口径和 warning；不打网络、不落盘、不返回明文 Key。
- `v0.9.1 Provider Usage Summary-B` 已新增只读 `GET /api/settings/provider-usage`，从 `intervention_compilation.json` / `multi_agent_trace.json` 汇总 `generation_meta.usage`，支持安全 `story_slug` 过滤；不内置真实价格表。
- `v0.9.1 Provider Status Panel-C` 已在设置抽屉展示模型状态与累计用量；保存设置或清除密钥后会刷新，只读不写价格/路由策略。
- `v0.9.1 Manual Price Estimate-D` 已支持手动配置每千输入/输出单价并按 usage 粗估费用；不硬编码厂商价格、不联网查价。
- `v0.9.1 Route Matrix-E` 已在 `GET /api/settings/providers` 返回读者干预、主题创世、导入抽取、视觉资产四个入口的只读 provider / mode / runner / fallback，并在设置抽屉展示；不新增路由写入开关、不改默认调用链。
- `v0.9.1 Provider & Cost Gateway Lite` 已整体收口，归档见 `docs/completed/v0.9.1-provider-cost-gateway-lite.md`。
- `v0.9.2 MasterSetting Workspace Summary-A` 已在项目工作台 payload 中新增只读 `master_setting_workspace`，聚合 `master_setting.yaml`、人物状态、时间线、伏笔和章节摘要；损坏/缺失 artifact 降级为空态或 damaged，不写文件。
- `v0.9.2 MasterSetting Workspace Panel-B` 已在长篇项目工作台新增「设定工作台」只读面板，展示世界规则、人物状态、时间线、伏笔线、章节摘要和后续建议；右侧项目资产面板显示设定状态。
- `v0.9.2 MasterSetting Workspace Edit-C` 已新增 `POST /api/stories/<slug>/master-setting`，仅白名单编辑 `master_setting.yaml` 的 display/genre/rules/limits/forbidden，保存前备份、保存后写报告；损坏/缺失设定返回 409。
- `v0.9.2 MasterSetting Workspace Frontend-D` 已在「设定工作台」新增最小写控件，支持编辑作品名、题材、世界规则、力量限制和禁用设定；保存后本地更新面板并刷新项目工作台。
- `v0.9.2 MasterSetting Workspace Lite` 已整体收口，归档见 `docs/completed/v0.9.2-master-setting-workspace-lite.md`；下一步只复核 v0.9.3 图记忆触发条件，不默认接 Zep / 图数据库 / GraphRAG。
- `v0.9.3 Graph Memory Evaluation Trigger-A` 已新增 `GET /api/stories/<slug>/graph-memory-evaluation`，只读判断当前项目是否满足图记忆评估触发条件；不接 Zep / 图数据库 / GraphRAG，不写 artifact。
- `v0.9.3 Retrieval Probe-B` 已新增 `GET /api/stories/<slug>/retrieval-probes`，用现有 BM25 / canon ledger / entity aliases 复跑代表性查询并返回失败样例；v0.9.3 已整体收口，归档见 `docs/completed/v0.9.3-graph-memory-evaluation-spike.md`。
- `v0.9.4 Advanced Runner Evaluation Trigger-A` 已新增 `GET /api/runs/<run_id>/advanced-runner-evaluation`，只读判断当前 run 是否满足高级 runner 评估触发条件；不接 LangGraph / OASIS / CAMEL，不写 artifact。
- `v0.9.4 Advanced Runner Probe-B` 已新增 `GET /api/runs/<run_id>/advanced-runner-probes`，收集状态执行、trace 与涌现节点失败样例；v0.9.4 已整体收口，归档见 `docs/completed/v0.9.4-advanced-runner-evaluation-spike.md`。
- `v1.0-beta Commercial Hardening Scope-A` 已新增 `GET /api/settings/commercial-hardening-scope`，只读整理账号/权限/云端持久化/配额/审计/版权/部署观测的当前覆盖、缺口、延后项和本地优先下一步；不读密钥、不打网络、不落盘、不接云端多租户或计费系统，归档见 `docs/completed/v1.0-beta-commercial-hardening-scope-a.md`。
- 仍未做云端多用户持久队列、对象存储、向量库、overlay 驱动下一轮 runner 自动消费、运行后审计写入正史账本。
- v1.0-beta 后续也不默认接 Zep / 图数据库 / OASIS / CAMEL / LangGraph；这些仍按 v0.9.3 / v0.9.4 触发式 spike 处理。下一刀先做本地项目审计日志 schema 与只读聚合。

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
