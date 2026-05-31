# Codex Handoff — Living Novel Engine

> 用途：新开 Codex 窗口时的接力包。新窗口第一步应先读本文件，再读 `AGENTS.md` 与项目四文档，不要只靠聊天摘要。

## 新窗口第一条消息建议

```text
请先阅读并对齐：
- AGENTS.md
- docs/codex-handoff.md
- memory.md
- docs/living-novel-engine-iteration-plan.md
- docs/productization-phase-map.md
- docs/living-novel-engine-prd.md
- docs/completed/v0.7-product-web-app-ui-spec.md
- engine/README.md

当前项目是 Living Novel Engine，核心代码在 engine/。
请不要只靠这段摘要；读完文档和相关代码后，再继续下一步。

当前已完成并验收：
- v0.7 Product Web App 九刀
- v0.7.2 Agent Interaction
- v0.7.3 Visual Asset Generation
- v0.7.4 Baseline & Canon Replay
- v0.7.5 Worldline Judge
- v0.8.0-A Long Novel Ingestion Report
- v0.8.1-A Hierarchical Memory Skeleton
- v0.8.2-A Canon Ledger Skeleton
- v0.8.3-A Canon Ledger Retrieval
- v0.8.4-A Static Consistency Audit
- v0.8.5-A Long Canon Replay Isolation
- v0.8+ ActDirector-A Planning Artifact
- v0.8+ Discourse-aware Narrator-A Diagnostics
- v0.8+ Dynamic Action Registry-A
- v0.8+ Emergence Mining-A
- v0.8.x Entity Aliases / Entity Resolution
- v0.8.x Runtime Memory Consumption-A
- v0.8.x Frontend Artifact Panel
- v0.8.x Long Upload Productization
- v0.8.6 Long Import Review
- v0.8.7 Resumable Ingest Jobs
- v0.8.8 Long Project Workspace
- v0.8.9 Long Replay & Audit UI
- v0.8.10-A Runner State Execution Spike
- v0.8.10-B Runner State Execution MVP
- v0.9.0-alpha Chapter Export
- v0.9.0-alpha Chapter Collection Export
- v0.9.0-alpha Export Share Guard
- v0.9.0-alpha Creation Loop Completion Gate
- v0.9.0-alpha Creation Loop Action Hints
- v0.9.0-alpha Creation Loop Readiness Evidence
- v0.9.0-alpha Creation Loop Audit Quick Run
- v0.9.0-alpha Creation Loop Alpha Ready State
- v0.9.0-alpha Creation Loop Alpha Closeout Report
- v0.9.0-alpha Creation Loop Closeout API
- v0.9.0-alpha Creation Loop Closeout API Actions
- v0.9.0-alpha Creation Loop Action Payloads
- v0.9.0-alpha Creation Loop Stable Blocker IDs
- v0.9.0-alpha Replay Audit Action Requirements
- v0.9.0-alpha Requirements UI Display
- v0.9.0-alpha Builtin Holdout Blocked Requirement
- v0.9.0-alpha Creation Loop Closeout CLI
- v0.9.0-alpha Creation Loop Closeout Record
- v0.9.0-alpha Low-risk Audit Closeout / Alpha Closure
- v0.9.1 Provider Gateway Summary-A
- v0.9.1 Provider Usage Summary-B
- v0.9.1 Provider Status Panel-C
- v0.9.1 Manual Price Estimate-D
- v0.9.1 Route Matrix-E
- v0.9.1 Provider & Cost Gateway Lite
- v0.9.2 MasterSetting Workspace Summary-A
- v0.9.2 MasterSetting Workspace Panel-B
- v0.9.2 MasterSetting Workspace Edit-C
- v0.9.2 MasterSetting Workspace Frontend-D
- v0.9.2 MasterSetting Workspace Lite
- v0.9.3 Graph Memory Evaluation Trigger-A
- v0.9.3 Retrieval Probe-B
- v0.9.3 Graph Memory Evaluation Spike
- v0.9.4 Advanced Runner Evaluation Trigger-A
- v0.9.4 Advanced Runner Probe-B
- v0.9.4 Advanced Runner Evaluation Spike
- v1.0-beta Commercial Hardening Scope-A
- v1.0-beta Commercial Audit Log Schema-B
- v0.9.0-alpha Creation Loop Checklist
- v0.9.0-alpha Continuation Hint
- v0.9.0-alpha Resume Continue HTTP Job
- v0.9.0-alpha Worldline Selection Persistence
- v0.9.0-alpha Post-run Audit Entry

最近一次 Codex 迭代：
- v0.8.0-A：导入写 `source_raw/`、`import_report.json`，Web/job 支持 additive `long_mode`
- v0.8.1-A：导入写 `memory/` 分层记忆骨架与 `memory_manifest.json`
- v0.8.2-A：导入写 `memory/canon_ledger.jsonl`
- v0.8.3-A：`canon_ledger` 接入 BM25 检索 artifact
- v0.8.4-A：导入写 `memory/consistency_report.json` 静态审计
- v0.8.5-A：正史 holdout 写 `canon/visibility_manifest.json`，隔离 `runtime_visible` / `holdout_private`
- v0.8+ ActDirector-A：干预 run 写 `act_director_plan.json`，但暂不驱动 runner
- v0.8+ Discourse-aware Narrator-A：每分支写 `narrative_diagnostics.json`，但暂不反馈 narrator
- v0.8+ Dynamic Action Registry-A：干预 run 写 `dynamic_action_registry.yaml`，但暂不执行状态变化
- v0.8+ Emergence Mining-A：干预 run 写 `emergence_nodes.json`，HTTP `POST/GET /api/runs/<run_id>/emergence-nodes`
- v0.8.x Entity Aliases：导入写 `memory/entity_aliases.yaml`，retrieval 做 alias expansion，锚定页只读展示别名摘要
- v0.8.x Runtime Memory Consumption-A：干预、baseline 与 CLI resume 通过既有 `retrieved_context` 参数只读消费 memory/alias/ledger 安全子集，并写 `runtime_memory_context.json`
- v0.8.x Frontend Artifact Panel：`get_branch()` 聚合 `runtime_memory_context`、`act_director_plan`、`dynamic_action_registry`、`narrative_diagnostics`、`emergence_nodes`；前端右侧「机制档案」统一只读展示
- v0.8.x Long Upload Productization：导入页支持 txt/md/zip/epub 文件选择、浏览器端分片、job 进度条和失败空态；后端 `upload` 分片 payload 解析后复用既有导入流水线
- v0.8.6 Long Import Review：`import_report.json` 新增来源、章节统计、章节片段、解析 warning、质量风险和建议动作；`get_story()` / `get_world_anchor()` additive 返回 `import_review`，报告缺失或损坏稳定降级为 missing/damaged 空态；前端世界锚定页新增「导入检查」
- v0.8.7 Resumable Ingest Jobs：新增本地持久化 ingest session，支持服务端分片 manifest、缺失分片查询、重复 chunk 幂等、sha256 校验、complete 后复用 import job；前端导入页改为 session 上传并用 localStorage 恢复缺失分片
- v0.8.8 Long Project Workspace：新增项目级工作台 API，集中返回导入检查、章节预览、分层记忆、正史账本、实体别名、检索命中、审计报告和下一步入口；前端 WorkspacePage 未选世界线时展示长篇项目资产页
- v0.8.9 Long Replay & Audit UI：新增章节范围 Canon Replay 报告、replay/audit 工作台 API 与前端「回放与审计」面板，支持单章/范围回放、风险维度、实体归一化审计和空态降级
- v0.8.10-A Runner State Execution Spike：新增 dry-run 状态执行评估报告、HTTP API 与前端「状态执行评估」，解释 action/emergence 能否安全转成状态 delta；不写 `state_snapshot.json`，不改 `run_scene` 默认行为
- v0.8.10-B Runner State Execution MVP：新增显式确认的状态 overlay 应用/回滚，low-risk 白名单 delta 写 `state_execution_overlay.json`，原 `state_snapshot.json` 不被覆盖
- v0.9.0-alpha Chapter Export：新增只读章节导出服务、HTTP API 与前端「导出章节」入口，导出 Markdown 包含来源说明、AI 生成说明、评审摘要和章节正文
- v0.9.0-alpha Chapter Collection Export：新增父链章节合集导出服务、HTTP API 与前端「导出合集」入口，按 `parent_run_id` / `parent_branch` 串联生成章节且不导出上传原文
- v0.9.0-alpha Export Share Guard：单章导出与合集导出返回 `share_guard`，Markdown 写入「版权与分享边界」，前端下载前中文确认权利责任
- v0.9.0-alpha Creation Loop Completion Gate：`creation_loop` 新增 `completion` 完成度判定，清单补「确认版权边界」，前端展示阻塞项
- v0.9.0-alpha Creation Loop Action Hints：`completion.actions` 把阻塞项转成生成评审、设为起点、查看审计等动作，前端可直接补推荐世界线评审
- v0.9.0-alpha Creation Loop Readiness Evidence：`completion.evidence` 把清单项映射到 artifact/API/页面依据，前端展示判定来源
- v0.9.0-alpha Creation Loop Audit Quick Run：已选世界线缺范围回放且存在 baseline/holdout 时，completion 直接提供运行范围回放动作
- v0.9.0-alpha Creation Loop Alpha Ready State：完整低风险闭环下 `can_mark_alpha_complete=true`，前端状态显示「可收口」
- v0.9.0-alpha Creation Loop Alpha Closeout Report：`creation_loop.closeout` 只读汇总 alpha 收口状态、阻塞项、依据和下一步，前端显示「Alpha 收口」
- v0.9.0-alpha Creation Loop Closeout API：`GET /api/stories/<slug>/creation-loop-closeout` 直接返回 closeout 和阻塞动作，便于真实样例/导入项目验收
- v0.9.0-alpha Creation Loop Closeout CLI：`lne creation-loop-closeout <slug>` 可本地输出 closeout 状态；`--json` 输出与 HTTP 同构 payload，`--require-ready` 可作为 alpha 收口闸门
- v0.9.0-alpha Creation Loop Closeout Record：`lne creation-loop-closeout <slug> --write-report` 仅在 ready 后写入 `creation_loop_alpha_closeout.json` 收口记录，未 ready 不落盘
- v0.9.0-alpha Low-risk Audit Closeout / Alpha Closure：低风险静态审计 info 不再阻断 closeout；本地导入项目 `v090-alpha-proof` 已写入 closeout record，v0.9.0-alpha 整体收口
- v0.9.1 Provider Gateway Summary-A：新增 `get_provider_gateway_summary()` 与只读 `GET /api/settings/providers`，返回脱敏 LLM/Seedream provider 列表、单 provider 路由、mock/占位图降级策略、成本观测口径和 warning；不创建客户端、不打网络、不落盘、不返回明文 Key
- v0.9.1 Provider Usage Summary-B：新增 `get_provider_usage_summary()` 与只读 `GET /api/settings/provider-usage`，从 `intervention_compilation.json` / `multi_agent_trace.json` 聚合 `generation_meta.usage`，支持安全 `story_slug` 过滤，不内置真实价格表
- v0.9.1 Provider Status Panel-C：设置抽屉新增「模型与用量状态」只读区，展示 provider 状态、模型名、累计用量、缺失 usage 记录提示与 warning
- v0.9.1 Manual Price Estimate-D：运行设置新增手动每千输入/输出单价，usage 汇总可估算费用；设置抽屉新增成本估算输入，不硬编码厂商价格
- v0.9.1 Route Matrix-E：`GET /api/settings/providers` 新增只读 `routes`，设置抽屉展示读者干预、主题创世、导入抽取、视觉资产生成分别走哪个 provider / fallback；不新增路由写入开关
- v0.9.1 Provider & Cost Gateway Lite：整体收口归档见 `docs/completed/v0.9.1-provider-cost-gateway-lite.md`
- v0.9.2 MasterSetting Workspace Summary-A：`get_project_workspace()` additive 返回只读 `master_setting_workspace`，聚合设定、人物状态、时间线、伏笔和章节摘要；损坏 artifact 返回 damaged/warnings，不写文件
- v0.9.2 MasterSetting Workspace Panel-B：长篇项目工作台新增只读「设定工作台」面板和右侧设定状态，展示世界规则、人物状态、时间线、伏笔线、章节摘要和后续建议
- v0.9.2 MasterSetting Workspace Edit-C：新增 `POST /api/stories/<slug>/master-setting`，仅白名单编辑 `master_setting.yaml` 的 display/genre/rules/limits/forbidden，保存前备份、保存后写报告；缺故事 404，损坏/缺失设定 409，非法 payload 400
- v0.9.2 MasterSetting Workspace Frontend-D：长篇项目工作台「设定工作台」新增最小写控件，可编辑作品名、题材、世界规则、力量限制、禁用设定；保存后本地更新面板并刷新项目工作台
- v0.9.2 MasterSetting Workspace Lite：整体收口归档见 `docs/completed/v0.9.2-master-setting-workspace-lite.md`
- v0.9.3 Graph Memory Evaluation Trigger-A：新增只读 `GET /api/stories/<slug>/graph-memory-evaluation`，返回图记忆评估触发状态、指标、原因和下一步；不接 Zep / 图数据库 / GraphRAG
- v0.9.3 Retrieval Probe-B：新增只读 `GET /api/stories/<slug>/retrieval-probes`，用现有 BM25 / canon ledger / entity aliases 复跑代表性查询并返回失败样例；不接 Zep / 图数据库 / GraphRAG
- v0.9.3 Graph Memory Evaluation Spike：整体收口归档见 `docs/completed/v0.9.3-graph-memory-evaluation-spike.md`
- v0.9.4 Advanced Runner Evaluation Trigger-A：新增只读 `GET /api/runs/<run_id>/advanced-runner-evaluation`，返回高级 runner 评估触发状态、指标、原因和下一步；不接 LangGraph / OASIS / CAMEL
- v0.9.4 Advanced Runner Probe-B：新增只读 `GET /api/runs/<run_id>/advanced-runner-probes`，把状态执行、trace 质量与涌现节点拆成可复现 probe 并返回失败样例；不接 LangGraph / OASIS / CAMEL
- v0.9.4 Advanced Runner Evaluation Spike：整体收口归档见 `docs/completed/v0.9.4-advanced-runner-evaluation-spike.md`
- v1.0-beta Commercial Hardening Scope-A：新增只读 `GET /api/settings/commercial-hardening-scope`，整理账号/权限/云端持久化/配额/审计/版权/部署观测七域范围、当前覆盖、缺口、延后项和本地优先下一步；不读密钥、不打网络、不落盘、不接云端多租户或计费系统
- v1.0-beta Commercial Audit Log Schema-B：新增只读 `GET /api/stories/<slug>/audit-log`，定义 `memory/project_audit_log.jsonl` schema，并从导入检查、世界线选择、设定轻编辑、creation loop closeout 与既有 JSONL 行聚合项目审计时间线
- v0.9.0-alpha Creation Loop Checklist：项目工作台 additive 返回 `creation_loop`，前端展示推荐世界线、五步清单与下一步提醒；不写 artifact，不改 `run_scene`
- v0.9.0-alpha Continuation Hint：前端在推荐世界线下展示 `continue_hint` CLI 续写入口
- v0.9.0-alpha Resume Continue HTTP Job：新增 `run_resume_continue()` 与 `POST /api/jobs/resume-continue`，前端可显式生成下一章并跳到新 run 的 `linear` 分支；不改 `run_scene` 默认行为
- v0.9.0-alpha Worldline Selection Persistence：新增 `selected_worldline.json`、`GET/POST /api/stories/<slug>/selected-worldline` 与前端「设为起点」，工作台可读回已选世界线
- v0.9.0-alpha Post-run Audit Entry：`creation_loop.post_run_audit` 围绕已选世界线展示评审、Causal Diff、静态审计、范围回放风险、缺失实体与回放审计入口；只读、不写正史账本、不驱动 runner
- 后端 python -m pytest -q 为 650 passed
- 前端 cd engine/ui && pnpm run build 通过
- git diff --check 无 whitespace error

下一步进入 `v1.0-beta Permission Matrix Draft-C`：把现有读写 API 与项目 artifact 映射成 owner/editor/viewer 权限矩阵草案，不要直接跳云端多用户持久队列、对象存储、多租户权限或付费系统。Zep / 图数据库 / GraphRAG 已在 v0.9.3 保持为“不触发重依赖接入，等待真实失败样例”；LangGraph / OASIS / CAMEL 已在 v0.9.4 保持为“不触发重依赖接入，等待真实复杂 run 失败样例”。请先读项目文档和现有代码，再判断具体实现；如果要改代码，遵守：
- 不改 run_scene 默认行为
- 不改 chapter.md/events.json/state_snapshot.json/multi_agent_trace.json/causal_diff.json 既有契约
- 新 artifact/API 字段 additive
- 前端中文
- 后端补 service/API 测试，前端 build 必须通过
- 完成后同步 memory.md，必要时同步迭代计划/README/UI spec/codex-handoff
```

## 当前项目状态

Living Novel Engine 是 `D:\AI\open-infinite\engine` 下的活体小说运行时。核心闭环：

```text
文本输入 -> 世界锚定 -> 角色自主行动 -> 读者干预 -> 世界线分叉 -> 章节渲染 -> 可继续运行
```

截至 2026-05-31：

| 项 | 状态 |
| --- | --- |
| 后端基线 | `650 passed` |
| 前端基线 | `pnpm run build` 通过 |
| 当前已收口 | v0.7 Product Web App、v0.7.2、v0.7.3、v0.7.4、v0.7.5、v0.8.0-A 至 v0.8.5-A、ActDirector-A、Discourse-aware Narrator-A、Dynamic Action Registry-A、Emergence Mining-A、Entity Aliases、Runtime Memory Consumption-A、Frontend Artifact Panel、Long Upload Productization、v0.8.6 Long Import Review、v0.8.7 Resumable Ingest Jobs、v0.8.8 Long Project Workspace、v0.8.9 Long Replay & Audit UI、v0.8.10-A/B Runner State Execution、v0.9.0-alpha Long Novel Creation Loop、v0.9.1 Provider & Cost Gateway Lite、v0.9.2 MasterSetting Workspace Lite、v0.9.3 Graph Memory Evaluation Spike、v0.9.4 Advanced Runner Evaluation Spike、v1.0-beta Commercial Hardening Scope-A、v1.0-beta Commercial Audit Log Schema-B |
| 官方下一刀 | `v1.0-beta Permission Matrix Draft-C` |
| 后续主线 | `v1.0-beta` 本地优先商业化加固 -> 真实外部用户前再评估云端多租户/计费系统 |

## 阶段性质与产品化判断

完整口径见 `docs/productization-phase-map.md`。新窗口判断版本时不要把 “A-slice 已收口” 等同于 “完整商业产品已完成”。

| 阶段 | 归类 | 判断 |
| --- | --- | --- |
| v0.1-v0.3 | 技术 MVP | CLI、导入、检索、续章等核心链路成立 |
| v0.4-v0.6.5 | 研发/机制 MVP | 浏览器 viewer、第四面墙、runner、多 Agent 机制可审计可演示 |
| v0.7-v0.7.5 | 短中篇产品化 MVP | 普通用户 Web 主闭环成立 |
| v0.8.0-A-v0.8.5-A | 长篇引擎底座 MVP | 长篇 memory/canon/retrieval/audit/holdout 成立 |
| v0.8+ A-slices | 机制接缝与解释层 MVP | action、diagnostics、registry、emergence、aliases、runtime memory 可读可验收，但不默认强执行 |
| v0.8.6-v0.8.10 | 长篇产品化收束 | 把长篇底座变成上传、检查、管理、审计、回放、继续创作工作流 |
| v0.9.0-alpha | 长篇产品闭环 | 已整体收口：上传/创建 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出 -> closeout record |
| v0.9.1-v1.0-beta | 增强与商业化 | provider/cost、MasterSetting、图记忆/advanced runner 评估、商业化范围复核和本地审计 schema 已收口；后续从权限矩阵、版权声明继续商业化加固 |

## 资料位置

- 主 PRD：`D:\AI\open-infinite\docs\living-novel-engine-prd.md`
- 产品化阶段归类：`D:\AI\open-infinite\docs\productization-phase-map.md`
- docs 导航：`D:\AI\open-infinite\docs\index.md`
- v0.1-v0.8 版本审计：`D:\AI\open-infinite\docs\completed\v0.1-to-v0.8-version-audit.md`
- 已完成的 PRD、UI spec 与专项版本文档：`D:\AI\open-infinite\docs\completed`
- 参考论文 PDF 与报告：`D:\AI\open-infinite\docs\article`
- 论文报告：`D:\AI\open-infinite\docs\article\reports`
- 参考开源项目：`D:\AI\open-infinite\Reference_projects`

这些资料用于路线判断和设计取舍；除非用户明确要求，参考开源项目只读不搬代码。

## 已收口版本摘要

### v0.7 Product Web App

React/Vite 产品级前端主闭环已完成：

- Web 自由干预生成
- Causal Diff 确立/抹除/回滚
- 世界锚定页
- 导入小说 Web 入口
- 主题创世 Web 入口
- 世界锚定轻编辑 + YAML 安全保存
- 真实 LLM / 运行设置面板
- 异步 Job / 进度轮询

### v0.7.2 Agent Interaction

- `CharacterAction` additive 结构化字段
- `CharacterProbe` 角色内心探针
- `InterventionGuardrail` 干预护栏预检
- Web：角色卡探针、干预预检、Agent 轨迹结构化动作展示
- 不改 runner 主链路，不改 outputs 契约

### v0.7.3 Visual Asset Generation

- Seedream 5.0 Lite 视觉资产增强层
- 封面、角色头像、场景背景
- `visual_assets.json` additive artifact
- 无 Key / 关闭 / 失败时稳定降级古风占位
- `SEEDREAM_API_KEY` 可能已在 `.env` 配置，测试必须隔离，避免误打真实外网

### v0.7.4 Baseline & Canon Replay

- `Baseline Worldline`：无高维干预的自然发展对照组
- `Canon Replay`：holdout 正史章节 + deterministic 本地评估
- 新 artifact：`baseline_report.json`、`holdout_manifest.json`、`canon_replay_report.json`
- 新 API：baseline 生成/读取、holdout 读写、replay 运行/读取
- 不写 `intervention.json` / `causal_diff.json`
- 最近 Codex 兜底补 service 层路径安全和 holdout 覆盖行为

## v0.7.5 Worldline Judge 收口摘要

已新增世界线评审层，给 branch 产物做 deterministic 故事质量评估。

- 后端模型：`WorldlineJudgement`
- 后端 service：`service/worldline_judge.py`
- deterministic evaluator：不依赖 LLM，从结构化数据和文本启发式评分
- API：`POST/GET /api/runs/<run_id>/branches/<branch_id>/worldline-judgement`
- Web：工作台右侧「世界线评审」标签页
- artifact：`outputs/<run_id>/<branch_id>/worldline_judgement.json`

评分维度：

- persona_consistency：角色是否仍符合人设边界
- contract_risk：是否冲突世界规则/合约
- branch_diversity：分支是否真正分歧
- narrative_momentum：叙事推进是否有动量
- emotional_payoff：情绪兑现是否成立
- anti_slop：是否空泛、重复、套路化
- continuation_potential：是否留下可继续推进的钩子
- emergence_score：读者干预是否产生新涌现节点
- story_arc / turning_points / tension：故事弧、转折点、张力

本刀未做：

- 不接 LangGraph / Zep / OASIS / CAMEL
- 不接新的外部评审服务
- run 级聚合评审
- `compare.md` 汇总
- `emergence_nodes.json` 持久化
- 不重构 runner
- 不改既有 artifact 契约
- 不把 judge 结果写回正文或 state_snapshot

## v0.8.0-A 至 v0.8.4-A Long Novel Memory 收口摘要

已完成长篇记忆的本地 artifact 底座，全部 additive，不改 runner：

- v0.8.0-A：`source_raw/` 原文账本、`import_report.json` 导入报告、Web/job `long_mode`（默认仍 3-10 章，long mode 最多 200 章）
- v0.8.1-A：`memory/` 分层记忆骨架：`memory_manifest.json`、`master_setting.yaml`、volume/chapter memory、character states、timeline、plot_threads、propagation_debts
- v0.8.2-A：`memory/canon_ledger.jsonl`，统一字段记录章节事件、角色状态、关系、伏笔
- v0.8.3-A：`canon_ledger` 作为 `canon_ledger` source 接入 BM25 检索，命中项保留 `entities`、`ledger_type`、`confidence`
- v0.8.4-A：`memory/consistency_report.json` 导入级静态审计，覆盖 timeline/resource/contract/thread 风险与修复建议
- v0.8.5-A：`canon/visibility_manifest.json` 明确 `runtime_visible` / `holdout_private`，`get_holdout()` 返回摘要，检索不读取私有章节正文
- ActDirector-A：`act_director_plan.json` 将 `InterventionCompilation` 转成 `CharacterActionPlan`，每步含 preconditions/effects/risk/repair suggestions；当前只作 artifact，不改 runner
- Discourse-aware Narrator-A：`narrative_diagnostics.json` 写后诊断，含 pacing、tension curve、warnings/suggestions；当前不改 narrator
- Dynamic Action Registry-A：`dynamic_action_registry.yaml` 从 `act_director_plan.json` 汇总动作类型、中文别名、前置条件、效果、失败原因与修复建议；当前不执行状态变化
- Emergence Mining-A：`emergence_nodes.json` 从干预、编译、动态动作、causal diff、worldline judgement、narrative diagnostics 汇总候选涌现节点；当前不做推荐系统
- Runtime Memory Consumption-A：`runtime_memory.py` 把 entity aliases、retrieval 与 canon ledger 命中打包为只读运行时记忆上下文；分支写 `runtime_memory_context.json`
- Frontend Artifact Panel：右侧 UI 用「机制档案」统一展示运行记忆、动作计划、动作注册表、叙事诊断、涌现节点；缺失或损坏 artifact 保持局部空态

本阶段未做：

- 云端多用户持久队列、对象存储、跨设备恢复
- LLM 细粒度事件抽取、scene 级切分
- 向量库、embedding、reranker（entity alias resolution 第一刀已完成）
- runner 消费 action plan、dynamic action registry 或 emergence nodes，并执行状态变化
- 运行后写回审计、runner 状态执行层

后续已进入并收口 `v0.9.0-alpha Long Novel Creation Loop`；当前下一刀见顶部状态表。

## v0.8.x Entity Aliases 收口摘要

- 导入时生成 `memory/entity_aliases.yaml`，并在 `memory_manifest.json` 登记 `entity_aliases` layer。
- `entity_aliases.py` 提供 build/write/load 与轻量 resolution；缺失/损坏分别返回 `missing` / `damaged`，不抛 500。
- `retrieval/context_loader.py` 读取 alias index；`retrieval/retriever.py` 对 query 与 corpus 文本做 alias expansion，canon ledger 命中项 additive 返回 `resolved_entities`。
- `consistency_report.json` summary 写 `entity_alias_count`；世界锚定 API/UI 只读展示别名状态、数量和样例。
- 未做：LLM/NER 抽取、人工别名编辑、跨 run 写回、向量检索。

## v0.8.x Runtime Memory Consumption-A 收口摘要

- `runtime_memory.py` 构建只读运行时记忆上下文：entity alias 状态、resolved query entities、retrieval items、consumed layers、warnings。
- `service.run_intervention()`、baseline 服务与 CLI resume 通过既有 `retrieved_context` 参数消费该上下文，不改 `run_scene` 默认语义。
- 每个 imported 分支 additive 写 `runtime_memory_context.json`；损坏/缺失 alias 文件降级为 warning，不阻断生成。
- `browser.indexer.get_branch()` 返回 `runtime_memory_context`；React 右侧「机制档案」统一展示该上下文。
- 完整验证：`python -m pytest -q` 573 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.8.x Frontend Artifact Panel 收口摘要

- `browser.indexer.get_branch()` additive 返回 run 级 `act_director_plan`、`dynamic_action_registry`、`emergence_nodes`，branch 级 `narrative_diagnostics`，以及既有 `runtime_memory_context`。
- React 右侧解释面板新增「机制档案」tab，统一只读展示运行记忆、动作计划、动作注册表、叙事诊断、涌现节点；原「运行记忆」独立 tab 已收束进该面板。
- 缺失 artifact 显示局部空态；损坏 JSON/YAML 不白屏，不影响章节阅读、检索、状态、Agent 轨迹或世界线评审。
- 未做：runner 消费动作计划/动作注册表/涌现节点并改变状态；跨 run 涌现聚类；云端多用户持久队列与对象存储。

## v0.8.6 Long Import Review 收口摘要

- `import_report.json` 升级为 additive `v0.8.6` 报告，新增 `source`、`chapter_stats`、章节 `preview`、`parsing_warnings`、`quality_risks`、`recommended_actions`。
- `browser.indexer.get_story()` / `get_world_anchor()` 新增 `import_review`；报告缺失或损坏时不抛 500，而是用 `source/` 章节预览稳定降级为 `missing` / `damaged` 空态。
- 前端世界锚定页新增「导入检查」区，展示来源、章节统计、风险、warning、章节片段和下一步建议。
- 坏 zip / epub / 空文件 / 章节过少返回更明确的 400 或 job failed 文案；不改 `run_scene` 默认行为，不改既有 artifact 契约。
- 完整验证：`python -m pytest -q` 577 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.8.7 Resumable Ingest Jobs 收口摘要

- `service/ingest_sessions.py` 新增本地持久化上传 session：manifest + chunk 文件，支持 session 创建、查询缺失分片、写入 chunk、幂等重复上传、chunk/full-file sha256 校验、缺片/冲突/过期降级。
- HTTP 新增 `POST /api/ingest-sessions`、`GET /api/ingest-sessions/<session_id>`、`POST /api/ingest-sessions/<session_id>/chunks`、`POST /api/ingest-sessions/<session_id>/complete`；所有 session_id 先经 `safe_id`，错误映射为 400/404/409。
- complete 后不复制导入逻辑，而是重建既有 additive `upload` payload 并提交 import job；`run_scene` 与导入 artifact 契约不变。
- React 导入页改为 session 上传：localStorage 保存 session id，刷新后 GET session，只补传缺失分片，逐片 sha256，完成后轮询既有 job。
- 完整验证：`python -m pytest -q` 581 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.8.8 Long Project Workspace 收口摘要

- 新增 `GET /api/stories/<slug>/project-workspace`，服务端聚合导入检查、章节预览、分层记忆、正史账本、实体别名、检索命中、静态审计和下一步入口；所有新增字段 additive。
- 缺失/损坏的 `memory_manifest.json`、`canon_ledger.jsonl`、`consistency_report.json` 降级为 `missing` / `damaged` 空态；非法 slug 400，缺失项目 404。
- React `WorkspacePage` 在未选世界线时展示长篇项目资产页；选中世界线后保留原阅读、右侧机制档案与干预体验。
- 完整验证：`python -m pytest -q` 584 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.8.9 Long Replay & Audit UI 收口摘要

- 新增 `run_canon_replay_range()`，按章节范围批量运行正史回放，写 `canon_replay_range_report.json`，汇总平均分、风险等级、弱章、风险维度和实体审计。
- 新增 `GET /api/stories/<slug>/replay-audit` 与 `POST /api/stories/<slug>/canon/replay-range`；slug/run/branch 安全校验，非法、缺失、冲突降级为 400/404/409 或前端空态。
- React 「回放与审计」面板支持 holdout 状态、单章回放、章节范围回放、风险维度、实体归一化审计和下一步建议。
- 完整验证：`python -m pytest -q` 587 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.8.10-A Runner State Execution Spike 收口摘要

- 新增 `runner_state_execution_report.json` dry-run 报告，读取动作计划、动作注册表和涌现节点，输出候选状态变化、gate 状态、阻断原因、warnings 与 MVP 前置清单。
- 新增 `POST /api/runs/<run_id>/state-execution-evaluate` 与 `GET /api/runs/<run_id>/state-execution-report`；run id 安全校验，缺失报告 404、损坏报告 400、缺必要 artifact 409。
- `GET /api/runs/<run_id>/branches/<branch_id>` additive 返回 `runner_state_execution_report`；React 「机制档案」新增「状态执行评估」区，可生成/重评估报告并展示候选 delta、阻断与安全说明。
- 完整验证：`python -m pytest -q` 591 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。
- 明确边界：不写 `state_snapshot.json`，不改 `run_scene` 默认行为，不自动应用 action/emergence 到真实状态。

## v0.8.10-B Runner State Execution MVP 收口摘要

- 新增 `apply_runner_state_execution()` 与 `rollback_runner_state_execution()`；应用必须 `confirm=True`，只允许 dry-run 报告中 `executable`、`low` risk、白名单字段的 delta。
- 应用写分支级 `state_execution_overlay.json` 和 run 级 `runner_state_execution_apply_report.json`；回滚删除 overlay、写 `runner_state_execution_rollback_report.json`，原 `state_snapshot.json` 不被覆盖。
- 新增 `POST /api/runs/<run_id>/state-execution-apply` 与 `POST /api/runs/<run_id>/state-execution-rollback`；未确认 400，缺报告 404，无可应用候选 409，坏 id 400。
- React 「状态执行评估」区新增「应用低风险状态」与「回滚覆盖层」按钮，展示 overlay / apply / rollback 摘要。
- 完整验证：`python -m pytest -q` 595 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Chapter Export 收口摘要

- 新增 `service/chapter_export.py`，`build_chapter_export()` 只读读取所选分支 `chapter.md`、评审、Diff 与状态 overlay 摘要，生成 Markdown 导出负载。
- 新增 `GET /api/runs/<run_id>/branches/<branch_id>/chapter-export`；run_id/branch_id 均经 `safe_id`，坏 id 返回 400，缺章节返回 404。
- React 阅读区新增「导出章节」按钮，下载当前世界线章节 Markdown；文案保持中文，失败显示局部错误态。
- 明确边界：不写回 `chapter.md`，不改 `run_scene` 默认行为，不导出上传原作全文或 holdout 私有正文。
- 完整验证：`python -m pytest -q` 598 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Chapter Collection Export 收口摘要

- 新增 `build_chapter_collection_export()` 与 `GET /api/runs/<run_id>/branches/<branch_id>/chapter-collection-export`，沿 `meta.parent_run_id` / `meta.parent_branch` 回溯父链并按时间顺序生成 Markdown 合集。
- React 阅读区新增「导出合集」按钮，与「导出章节」并列；成功提示会展示合集章节数，失败显示局部中文错误。
- 明确边界：合集只读，不写 artifact，不改 `run_scene` 默认行为，不导出上传原作全文或 holdout 私有正文；父链缺失时安全截断并返回 warning。
- 完整验证：`python -m pytest -q` 607 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Export Share Guard 收口摘要

- 单章导出与合集导出新增 additive `share_guard`，返回私用允许、公开分享不默认放行、分享前需确认权利来源等边界。
- Markdown 新增「版权与分享边界」段落；React「导出章节」/「导出合集」下载前弹出中文确认，取消则不生成下载。
- 边界：不新增公开分享发布入口，不写 artifact，不改 `run_scene` 默认行为。
- 完整验证：`python -m pytest -q` 607 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Completion Gate 收口摘要

- `creation_loop.checklist` 新增「确认版权边界」，`creation_loop.completion` 返回完成/总数、阻塞项、summary 与 `can_mark_alpha_complete`。
- React「创作闭环」区顶部新增完成度条，展示剩余阻塞项，避免只靠人工记忆判断 v0.9.0-alpha 是否可收口。
- 边界：只读判定，不写 artifact，不自动宣告版本完成。
- 完整验证：`python -m pytest -q` 607 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Action Hints 收口摘要

- `creation_loop.completion.actions` additive 返回阻塞项动作：生成世界线评审、设为下一章起点、查看回放与审计。
- React 完成度区展示快捷动作；「生成世界线评审」复用既有 `POST /api/runs/<run_id>/branches/<branch_id>/worldline-judgement` 并刷新工作台。
- 边界：不新增新 runner 行为，不写额外 artifact，不替代回放审计本身。
- 完整验证：`python -m pytest -q` 608 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Readiness Evidence 收口摘要

- `creation_loop.completion.evidence` additive 返回每个清单项的判定来源：artifact、API、页面 hash 或当前状态。
- React 完成度区新增「判定依据」，以中文标签展示完成度为什么处于 ready/warn/todo。
- 边界：只读解释层，不写 artifact，不改变 runner 或 completion 判定。
- 完整验证：`python -m pytest -q` 608 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Audit Quick Run 收口摘要

- `completion.actions` 在已选世界线缺范围回放、且存在 baseline/holdout 时返回 `run_replay_range`。
- React 完成度区可直接调用既有 `POST /api/stories/<slug>/canon/replay-range`，成功后刷新工作台。
- 边界：不新增 API，不改 runner；只触发现有 range replay artifact。
- 完整验证：`python -m pytest -q` 609 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Alpha Ready State 收口摘要

- 新增 ready fixture 覆盖 clean audit、评审、Causal Diff、低风险范围回放、已选起点、导出和版权 guard 全部满足时 `can_mark_alpha_complete=true`。
- React「创作闭环」标题状态在 ready 时显示「可收口」。
- 边界：仍不自动宣告版本完成，只暴露可验证 ready 状态。
- 完整验证：`python -m pytest -q` 610 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Alpha Closeout Report 收口摘要

- `creation_loop.closeout` additive 返回 `creation_loop_alpha_closeout`，汇总 alpha 收口状态、ready/required 计数、剩余阻塞、判定依据和下一步。
- React「创作闭环」区新增「Alpha 收口」面板，ready 时显示「可收口」，未 ready 时显示「待补齐」和阻塞项。
- 边界：只读派生，不写 artifact，不改 runner，不自动宣告版本完成。
- 完整验证：`python -m pytest -q` 610 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Closeout API 收口摘要

- 新增 `GET /api/stories/<slug>/creation-loop-closeout`，直接返回 `story_slug`、`version` 和 `closeout`。
- HTTP ready fixture 覆盖导入项目在 clean audit、评审、Causal Diff、低风险范围回放、已选起点、章节导出和版权 guard 满足时返回 `closeout.status=ready`。
- 边界：只读复用 workspace closeout；非法 slug 400；不写 artifact、不改 runner、不代表发布按钮。
- 完整验证：`python -m pytest -q` 611 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Closeout API Actions 收口摘要

- `GET /api/stories/<slug>/creation-loop-closeout` 额外返回 `completion_status` 与 `actions`。
- ready 项目 actions 为空；not_ready 项目返回生成世界线评审、设为起点、查看回放与审计等阻塞补齐动作。
- 边界：只读提示动作，不自动执行，不写 artifact，不代表用户选择。
- 完整验证：`python -m pytest -q` 613 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Action Payloads 收口摘要

- `select_worldline` action 现在携带 `payload`：`run_id`、`branch_id`、`note`。
- `worldline_judgement` action 现在携带 `payload`：`story_slug`。
- 前端类型允许 `ProjectCreationLoopAction.payload` 为范围回放 payload、世界线选择 payload 或世界线评审 payload。
- 边界：payload 只是建议动作参数；不自动执行、不代表用户确认。
- 完整验证：`python -m pytest -q` 613 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Stable Blocker IDs 收口摘要

- `creation_loop.closeout` 新增 additive `remaining_blocker_ids`，与 `completion.blocking_ids` 保持一致。
- 原 `remaining_blockers` 中文 label 保留，供 UI 展示；稳定 id 供 closeout API 自动验收和脚本补阻塞使用。
- 边界：不改变 ready 判定、不执行动作、不写 artifact。
- 完整验证：`python -m pytest -q` 612 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Replay Audit Action Requirements 收口摘要

- `replay_audit` action 新增 additive `requirements`，解释无法一键运行范围回放时缺少的前置条件。
- 当前 requirements 可返回 `selected_worldline`、`baseline_run`、`canon_holdout` 或 `review_replay_risk`。
- 边界：只读解释，不生成 baseline、不写 holdout、不执行范围回放、不改变 ready 判定。
- 完整验证：`python -m pytest -q` 612 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Requirements UI Display 收口摘要

- React「创作闭环」完成度区在 action 带 requirements 时展示「审计前置」。
- 最多展示三项中文 label，详情放在 hover title；按钮行为不变。
- 边界：只展示现有 API 字段，不新增 action，不自动执行。
- 完整验证：`python -m pytest -q` 612 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Builtin Holdout Blocked Requirement 收口摘要

- `replay_audit.requirements` 读取 story source kind。
- builtin 样例缺少 holdout 时，`canon_holdout.status=blocked`，detail 提示需导入长篇项目后录入 holdout。
- 边界：imported 项目仍保持 missing，不改变 holdout 写入流程，不自动导入项目。
- 完整验证：`python -m pytest -q` 613 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Closeout CLI 收口摘要

- 新增 `lne creation-loop-closeout <slug>`，本地复用 project workspace 的只读 closeout 判定，输出 status、阻塞 id、阻塞动作和下一步。
- `--json` 输出与 HTTP closeout 同构的 `story_slug/version/completion_status/actions/closeout`；`--require-ready` 在 not_ready 时退出码 1。
- 边界：只读，不写 artifact，不执行 action，不改变 `run_scene` 默认行为；仍需 imported/真实项目 ready 后再整体收口。
- 完整验证：`python -m pytest -q` 615 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Creation Loop Closeout Record 收口摘要

- `lne creation-loop-closeout <slug>` 新增 `--write-report`，ready 后向导入项目写入 additive `creation_loop_alpha_closeout.json`。
- 报告记录 `story_slug`、`version`、`completion_status`、`actions`、`closeout` 与 `created_at`，用于 alpha 闸门通过后的本地证据。
- 未 ready 时不落盘；builtin 样例无项目目录时不可写；不执行 action、不改变 `run_scene` 默认行为。
- 完整验证：`python -m pytest -q` 616 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Low-risk Audit Closeout / Alpha Closure 收口摘要

- `creation_loop` ready 判定已调整：`risk_level=low` 的静态审计 info 提示不再阻断 closeout；中高风险、缺失实体、缺评审、缺选择、缺导出仍阻断。
- 本地导入项目 `v090-alpha-proof` 已跑通 `lne creation-loop-closeout v090-alpha-proof --require-ready --write-report --json`，结果 `ready_count=7/7`、`remaining_blocker_ids=[]`，并写入 `creation_loop_alpha_closeout.json`。
- 新增 `docs/completed/v0.9.0-alpha-long-creation-loop.md` 记录收口范围、证明、边界和下一步。
- 完整验证：`python -m pytest -q` 617 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.1 Provider Gateway Summary-A 收口摘要

- 新增 `service.runtime_settings.get_provider_gateway_summary()`，把当前 LLM 与 Seedream 运行设置解释为脱敏 provider 列表、单 provider 路由、mock/占位图降级策略、成本观测口径和 warning。
- 新增只读 `GET /api/settings/providers`，返回 `version=v0.9.1-provider-cost-lite`、`routing`、`providers`、`routes`、`cost_policy` 与 `warnings`。
- 边界：不创建客户端、不打网络、不落盘、不返回明文 Key 或环境变量名；暂不内置真实价格表，不改 LLM/Seedream 调用链。
- 完整验证：`python -m pytest -q` 620 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.1 Provider Usage Summary-B 收口摘要

- 新增 `service.runtime_settings.get_provider_usage_summary(story_slug=None)`，只读扫描已有 `generation_meta.usage`。
- 新增 `GET /api/settings/provider-usage`，支持可选 `story_slug` 查询参数并经 `safe_id` 校验；非法 slug 返回 400。
- 返回 `totals`、`by_provider`、前 50 条 usage record、缺失 usage 的 meta 计数和空成本估算（`price_table_not_configured`）。
- 边界：不读取 Key、不打网络、不内置真实价格，不写入或修改 run artifact。
- 完整验证：`python -m pytest -q` 624 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.1 Provider Status Panel-C 收口摘要

- 前端类型/API client 新增 provider gateway 与 provider usage 类型和读取方法。
- 设置抽屉新增「模型与用量状态」区，展示主文本模型、视觉模型、启用状态、模型名、累计用量、输入/输出用量、缺失 usage 记录提示和 warning。
- 保存设置或清除文本模型密钥后刷新 provider 状态；不新增 Key 持久化、不写价格表、不写路由策略。
- 验证：`pnpm run build` 通过；本地 `lne browse` + Vite HTTP 冒烟：首页 200、`/api/settings/providers` 200、`/api/settings/provider-usage` 200；后端 `python -m pytest -q` 624 passed。

## v0.9.1 Manual Price Estimate-D 收口摘要

- 运行设置新增 `llm_input_cost_per_1k` / `llm_output_cost_per_1k`，仅写进程环境变量；负数或非数字 400。
- Provider gateway 返回手动单价与 `price_table_status`；provider usage 在配置单价后按 prompt/completion 用量估算费用，未配置时保持空估算。
- 设置抽屉新增「成本估算」输入区，用量状态区显示估算金额。
- 边界：不硬编码厂商价格、不联网查价、不写 run/project artifact。
- 验证：`tests/test_runtime_settings_api.py` 25 passed；完整后端目标基线 626 passed；前端 `pnpm run build` 通过。

## v0.9.1 Route Matrix-E 收口摘要

- `GET /api/settings/providers` 新增只读 `routes`，覆盖读者干预生成、主题创世、导入抽取、视觉资产生成四个入口的 provider、mode、runner 与 fallback。
- 设置抽屉「模型与用量状态」新增路由矩阵，中文展示每个入口当前走主文本模型、本地模拟、Seedream、占位图或关闭状态。
- 边界：不新增路由写入开关，不改 `run_scene` 默认行为，不改变 mock / Seedream / runner 实际调用链。

## v0.9.1 Provider & Cost Gateway Lite 整体收口摘要

- 五个子刀已覆盖 v0.9.1 的多 provider 配置、模型路由、成本/用量估算、失败回退和 Key 脱敏展示。
- 收口归档：`docs/completed/v0.9.1-provider-cost-gateway-lite.md`。
- 边界：仍不做持久化 Key、完整商业网关、可写路由策略、厂商价格表、云端队列、对象存储或多租户配置中心。
- 下一步：进入 v0.9.2 MasterSetting Workspace Lite。

## v0.9.2 MasterSetting Workspace Summary-A 收口摘要

- `browser.indexer.get_project_workspace()` 新增 `master_setting_workspace`，只读聚合 `memory/master_setting.yaml`、`memory/character_states/`、`memory/timeline.yaml`、`memory/plot_threads.yaml` 与 `memory/chapters/`。
- payload 返回 section count、世界规则/地点/势力、人物状态摘要、时间线样例、伏笔样例、章节摘要样例、只读能力标记、下一步建议和 warnings。
- 损坏 `master_setting.yaml` 会返回 `status=damaged`，人物/时间线/伏笔/章节摘要仍尽量展示；HTTP 项目工作台不白屏、不 500。
- 验证：先红灯后实现，`tests/test_v088_long_project_workspace.py` 4 passed；完整门禁本刀提交前运行。

## v0.9.2 MasterSetting Workspace Panel-B 收口摘要

- React 长篇项目工作台新增「设定工作台」只读面板，展示世界规则/限制/地点/势力、人物状态、时间线、伏笔线、章节摘要和下一步建议。
- 右侧项目资产面板新增「设定状态」，方便未选世界线时确认 `master_setting_workspace.status`。
- 前端对对象/数组型设定条目做安全格式化，避免 `[object Object]` 或英文占位；缺失资料继续走中文空态。
- 边界：只读消费 `master_setting_workspace`，不写 `memory/` artifact，不改 runner，不做完整作者工作台。

## v0.9.2 MasterSetting Workspace Edit-C 收口摘要

- 新增 `service.master_setting_update.update_master_setting()` 与 `POST /api/stories/<slug>/master-setting`。
- 仅允许编辑 `display_name`、`genre`、`world_rules`、`power_system_limits`、`forbidden_additions`；保存前备份 `backups/<timestamp>/memory/master_setting.yaml`，保存后写 `memory/master_setting_update_report.json`。
- HTTP 状态：坏 slug 400，缺故事 404，损坏/缺失 `master_setting.yaml` 409，非白名单 payload 400。
- 边界：不编辑人物/时间线/伏笔/章节摘要，不同步 `world.yaml`，不改 runner。

## v0.9.2 MasterSetting Workspace Frontend-D 收口摘要

- 前端类型与 API client 新增 `MasterSettingPatch`、`MasterSettingUpdateResponse` 与 `updateMasterSetting()`。
- React 长篇项目工作台「设定工作台」新增最小写控件，支持编辑作品名、题材、世界规则、力量限制和禁用设定；保存后本地更新面板并刷新项目工作台。
- 后端 workspace ready 状态 additive 返回 `mode=lite_edit` 与 `can_edit=true`；missing/damaged 继续走只读空态。
- 验证：focused `tests/test_v092_master_setting_update.py` 5 passed；前端 `pnpm run build` 通过；浏览器冒烟确认成功提示、新标题和规则内容同屏可见且 console 无 warn/error。
- 边界：仍只编辑 `master_setting.yaml` 白名单字段，不编辑人物/时间线/伏笔/章节摘要，不同步 `world.yaml`，不改 runner，不做完整作者工作台。

## v0.9.2 MasterSetting Workspace Lite 整体收口摘要

- 收口归档：`docs/completed/v0.9.2-master-setting-workspace-lite.md`。
- 四个子刀已覆盖只读聚合、前端展示、后端白名单轻编辑、前端最小写控件、保存备份与保存报告。
- 边界：不做完整作者工作台、不编辑人物/时间线/伏笔/章节摘要、不同步 `world.yaml`、不引入图数据库或云端协作。
- 下一步：进入 v0.9.3 Graph Memory Evaluation Spike 的触发条件复核；当前不能默认引入 Zep / 图数据库 / GraphRAG。

## v0.9.3 Graph Memory Evaluation Trigger-A 收口摘要

- 新增 `service.graph_memory_evaluation.evaluate_graph_memory_trigger()`。
- 新增 `GET /api/stories/<slug>/graph-memory-evaluation`，slug 走 `safe_id`；非法 slug 400，缺故事 404。
- 报告只读检查章节数、总字数、canon ledger、entity aliases 和 consistency report，返回 `not_triggered` / `monitor` / `triggered`。
- 边界：不接 Zep / 图数据库 / GraphRAG / embedding / 向量库 / reranker，不写 artifact，不替换现有 BM25/ledger/aliases。
- 验证：`tests/test_v093_graph_memory_trigger.py` 3 passed；完整后端基线提升到 635 passed。

## v0.9.3 Retrieval Probe-B / Graph Memory Evaluation Spike 收口摘要

- 新增 `service.retrieval_probe.evaluate_retrieval_probes()`。
- 新增 `GET /api/stories/<slug>/retrieval-probes`，slug 走 `safe_id`；非法 slug 400，缺故事 404。
- 报告从 canon ledger 与 entity aliases 自动生成代表性查询样本，复用现有 `retrieve_context()`，返回 `pass` / `weak` / `insufficient_samples`、命中率、top sources、失败样例与中文建议。
- 收口归档见 `docs/completed/v0.9.3-graph-memory-evaluation-spike.md`。
- 边界：不接 Zep / 图数据库 / GraphRAG / embedding / 向量库 / reranker，不写新 run artifact，不改 runner。
- 验证：`tests/test_v093_retrieval_probe.py` 3 passed；完整后端基线提升到 638 passed。

## v0.9.4 Advanced Runner Evaluation Trigger-A 收口摘要

- 新增 `service.advanced_runner_evaluation.evaluate_advanced_runner_trigger()`。
- 新增 `GET /api/runs/<run_id>/advanced-runner-evaluation`，run_id 走安全校验；非法 run_id 400，缺 run 404。
- 报告只读检查 `runner_state_execution_report.json`、分支 `multi_agent_trace.json` 与 `emergence_nodes.json`，返回 `not_triggered` / `insufficient_data` / `triggered`、状态执行 backlog、trace warning、私域复杂度和 high-value emergence。
- 边界：不接 LangGraph / OASIS / CAMEL，不写 artifact，不替换现有 runner，不改 `run_scene`。
- 验证：`tests/test_v094_advanced_runner_trigger.py` 3 passed；完整后端基线提升到 641 passed。

## v0.9.4 Advanced Runner Probe-B / Spike 收口摘要

- 新增 `service.advanced_runner_evaluation.evaluate_advanced_runner_probes()`。
- 新增 `GET /api/runs/<run_id>/advanced-runner-probes`，run_id 走安全校验；非法 run_id 400，缺 run 404。
- 报告把状态执行候选、trace 质量与涌现节点拆成可复现 probe，返回 `pass` / `weak` / `insufficient_data`、命中数、失败样例与中文建议。
- 收口归档见 `docs/completed/v0.9.4-advanced-runner-evaluation-spike.md`。
- 边界：不接 LangGraph / OASIS / CAMEL，不写新 run artifact，不改 runner。
- 验证：`tests/test_v094_advanced_runner_trigger.py` 5 passed；完整后端基线提升到 643 passed。

## v1.0-beta Commercial Hardening Scope-A 收口摘要

- 新增 `service.commercial_hardening.get_commercial_hardening_scope()`。
- 新增 `GET /api/settings/commercial-hardening-scope`，返回 `v1.0-beta-commercial-hardening-scope-a` 只读范围报告。
- 报告覆盖账号与项目空间、权限模型、云端持久化、配额与成本护栏、审计日志、版权与分享边界、部署与观测七个域。
- 报告明确本地优先下一步、平台化下一步和延后项：多租户账号、云端对象存储、商业计费系统。
- 收口归档见 `docs/completed/v1.0-beta-commercial-hardening-scope-a.md`。
- 边界：不读/回显密钥，不创建客户端，不打网络，不落盘，不改 runner 或既有 artifact。
- 验证：`tests/test_runtime_settings_api.py` 27 passed；完整后端基线提升到 645 passed。

## v1.0-beta Commercial Audit Log Schema-B 收口摘要

- 新增 `service.commercial_audit_log.get_project_audit_log()`。
- 新增 `GET /api/stories/<slug>/audit-log`，slug 走安全校验；非法 slug 400，缺项目 404。
- 报告定义 `memory/project_audit_log.jsonl` schema，并只读聚合 `import_report.json`、`selected_worldline.json`、`memory/master_setting_update_report.json`、`creation_loop_alpha_closeout.json` 与现有 JSONL 行。
- 损坏 JSONL 行降级为 warning，不让接口 500。
- 收口归档见 `docs/completed/v1.0-beta-commercial-audit-log-schema-b.md`。
- 边界：不写审计日志，不接账号、权限系统、对象存储、数据库、队列、计费或不可篡改审计存储。
- 验证：`tests/test_v100_commercial_audit_log.py` 5 passed；完整后端基线提升到 650 passed。

## v0.9.0-alpha Creation Loop Checklist 收口摘要

- `browser.indexer.get_project_workspace()` 版本提升为 `v0.9.0-alpha`，additive 返回 `creation_loop`：`recommended`、`candidates`、五步 `checklist`、中文 `next_steps`。
- `creation_loop` 只读扫描既有 run/branch artifact：`chapter.md`、`worldline_judgement.json`、`causal_diff.json`、`state_execution_overlay.json` 与 child run 关系；不写新 artifact。
- React 长篇项目工作台新增「创作闭环」区，展示推荐世界线、导入/分支/评审/审计/导出清单，并可打开推荐分支。
- 完整验证：`python -m pytest -q` 599 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Continuation Hint 收口摘要

- React「创作闭环」推荐世界线下新增 `续写入口` 命令展示，显示 `creation_loop.recommended.continue_hint`。
- 后端不新增 artifact、不新增 HTTP job；仍沿用 CLI `lne resume continue <run_id> --branch <branch_id> --mock`。
- 完整验证：`python -m pytest -q` 599 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Resume Continue HTTP Job 收口摘要

- 新增 `service/resume_continue.py`：`run_resume_continue()` 复用 CLI 续章链路，沿父 run/branch 读取快照、注入 runtime memory、继承第四面墙 lineage 账本，并写出新的 `linear` 子 run。
- 新增 `POST /api/jobs/resume-continue`；run_id/branch_id 先经 `safe_id`，坏 id 400，业务失败进入 job failed，不白屏。
- React「创作闭环」推荐世界线卡片新增「生成下一章」，显示 job 阶段/错误，成功后跳到新 run 的 `linear` 分支；CLI `续写入口` 继续保留。
- 边界：不改 `run_scene` 默认行为，不写 `intervention.json`，不覆盖父分支 `chapter.md/events.json/state_snapshot.json`。
- 完整验证：`python -m pytest -q` 602 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Worldline Selection Persistence 收口摘要

- 新增 `service/worldline_selection.py`：`select_worldline()` / `get_selected_worldline()` 校验 story/run/branch，并写入 `selected_worldline.json`。
- 新增 `GET/POST /api/stories/<slug>/selected-worldline`；坏 id 400，缺故事/run/branch 404，损坏选择记录降级为 `damaged` 空态。
- `get_project_workspace()` 的 `creation_loop` 返回 `selected` 并给候选分支标记 `is_selected`；React「创作闭环」新增「设为起点」和“已选起点”展示。
- 边界：选择记录只用于工作台读回，不驱动 runner、不改变推荐排序、不改既有 run artifact。
- 完整验证：`python -m pytest -q` 604 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.9.0-alpha Post-run Audit Entry 收口摘要

- `browser.indexer.get_project_workspace()` 的 `creation_loop` additive 返回 `post_run_audit`，围绕已选世界线聚合世界线评审、Causal Diff、静态一致性审计和章节范围回放摘要。
- `post_run_audit` 返回 `status`、已选 run/branch、静态风险数、范围回放状态、风险等级、缺失实体、下一步动作与 `#/anchor/<slug>` 回放审计入口。
- React「创作闭环」区新增「选择后审计」摘要，展示静态风险、是否已跑范围回放、风险等级、缺失实体，并提供「查看回放与审计」按钮。
- 边界：该入口只读，不写正史账本，不驱动 runner，不改 `chapter.md/events.json/state_snapshot.json/multi_agent_trace.json/causal_diff.json`。
- 完整验证：`python -m pytest -q` 605 passed；`cd engine/ui && pnpm run build` 通过；`git diff --check` 通过。

## v0.8.x Long Upload Productization 收口摘要

- 后端 `import_novel_from_payload()` 新增 additive `upload` 入参：`filename/total_size/chunks[{index,data_b64}]`，支持 txt/md 文本拆章、zip 内 txt/md 章节、epub 内 html/xhtml 章节。
- `/api/import-novel` 与 `/api/jobs/import-novel` 均可传 `upload`；同步接口错误返回 400/409，异步 job 失败返回 `status=failed + error`，不白屏、不 500。
- 前端导入页支持 txt/md/zip/epub 文件选择、浏览器端分片、文件摘要、job 进度条、失败空态和重试；未选文件时保留原粘贴 3-10 章模式。
- 未做：真正多请求断点续传/恢复、持久化 ingest job、epub spine 精排、角色抽取置信度和时间线风险增强。

## v0.8.6-v1.0-beta 后续版本编排

| 版本 | 名称 | 范围 | 状态 |
| --- | --- | --- | --- |
| v0.8.6 | Long Import Review | 导入报告细化、章节列表/正文片段预览、导入质量空态、坏 zip/epub/空文件/章节过少等错误态收束 | 已收口 |
| v0.8.7 | Resumable Ingest Jobs | 服务端分片 session、断点续传/恢复、hash 校验、重复 chunk 幂等、过期清理 | 已收口 |
| v0.8.8 | Long Project Workspace | 长篇项目详情页：章节、记忆、正史账本、实体别名、检索命中、审计报告，支持从项目发起 baseline/intervention | 已收口 |
| v0.8.9 | Long Replay & Audit UI | 长篇 Canon Replay / Consistency Audit 前端产品化，支持章节范围、风险维度和实体归一化后的审计展示 | 已收口 |
| v0.8.10-A | Runner State Execution Spike | opt-in 评估动作计划、动作注册表、涌现节点是否能安全转成状态变化；不改默认行为 | 已收口 |
| v0.8.10-B | Runner State Execution MVP | Spike 可行后做最小状态执行层，保持 artifact/API additive 与可回退 | 已收口 |
| v0.9.0-alpha | Long Novel Creation Loop | 上传 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出，形成完整长篇共创产品闭环 | 已整体收口 |
| v0.9.1 | Provider & Cost Gateway Lite | 多 provider 配置、模型路由、成本/用量估算、失败回退、Key 脱敏展示 | 已整体收口 |
| v0.9.2 | MasterSetting Workspace Lite | 项目级世界设定、人物、时间线、道具、伏笔、章节摘要的只读/轻编辑工作台 | 已整体收口 |
| v0.9.3 | Graph Memory Evaluation Spike | 评估 Zep / 图数据库 / GraphRAG 是否增强现有 ledger 检索 | 已整体收口：当前不触发重依赖接入 |
| v0.9.4 | Advanced Runner Evaluation Spike | 评估 LangGraph 局部 runner、OASIS/CAMEL 可选 runner | 已整体收口：当前不触发重依赖接入 |
| v1.0-beta Scope-A | Commercial Hardening Scope | 商业化七域范围复核、本地优先边界、延后项 | 已收口 |
| v1.0-beta Schema-B | Commercial Audit Log | 本地项目审计日志 schema 与只读聚合 | 已收口 |
| v1.0-beta Matrix-C | Permission Matrix Draft | owner/editor/viewer 权限矩阵草案 | 下一刀 |

## 每次任务完成后的收口清单

- 后端相关：`cd engine && python -m pytest -q`
- 前端相关：`cd engine/ui && pnpm run build`
- 代码清洁：`git diff --check`
- 文档：更新 `memory.md` 变更日志
- 若路线/README/UI spec 发生事实变化，同步对应文档
- 最终回答说明改了什么、验证结果、未做边界
