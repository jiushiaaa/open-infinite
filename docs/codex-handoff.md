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
- v0.9.0-alpha Creation Loop Checklist：项目工作台 additive 返回 `creation_loop`，前端展示推荐世界线、五步清单与下一步提醒；不写 artifact，不改 `run_scene`
- v0.9.0-alpha Continuation Hint：前端在推荐世界线下展示 `continue_hint` CLI 续写入口
- v0.9.0-alpha Resume Continue HTTP Job：新增 `run_resume_continue()` 与 `POST /api/jobs/resume-continue`，前端可显式生成下一章并跳到新 run 的 `linear` 分支；不改 `run_scene` 默认行为
- v0.9.0-alpha Worldline Selection Persistence：新增 `selected_worldline.json`、`GET/POST /api/stories/<slug>/selected-worldline` 与前端「设为起点」，工作台可读回已选世界线
- v0.9.0-alpha Post-run Audit Entry：`creation_loop.post_run_audit` 围绕已选世界线展示评审、Causal Diff、静态审计、范围回放风险、缺失实体与回放审计入口；只读、不写正史账本、不驱动 runner
- 后端 python -m pytest -q 为 608 passed
- 前端 cd engine/ui && pnpm run build 通过
- git diff --check 无 whitespace error

下一步继续推进 `v0.9.0-alpha Long Novel Creation Loop`：Chapter Export、Chapter Collection Export、Export Share Guard、Creation Loop Completion Gate、Creation Loop Action Hints、Creation Loop Checklist、Continuation Hint、Resume Continue HTTP Job、Worldline Selection Persistence 与 Post-run Audit Entry 子刀已收口，仍需根据 completion 判定补齐剩余阻塞后再考虑 alpha 收口；公开分享发布能力不在当前小刀内。`v0.9.0-alpha` 不默认接 Zep / 图数据库 / OASIS / CAMEL / LangGraph；这些重依赖分别后移到 `v0.9.3` / `v0.9.4` spike。请先读项目文档和现有代码，再判断具体实现；如果要改代码，遵守：
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
| 后端基线 | `608 passed` |
| 前端基线 | `pnpm run build` 通过 |
| 当前已收口 | v0.7 Product Web App、v0.7.2、v0.7.3、v0.7.4、v0.7.5、v0.8.0-A 至 v0.8.5-A、ActDirector-A、Discourse-aware Narrator-A、Dynamic Action Registry-A、Emergence Mining-A、Entity Aliases、Runtime Memory Consumption-A、Frontend Artifact Panel、Long Upload Productization、v0.8.6 Long Import Review、v0.8.7 Resumable Ingest Jobs、v0.8.8 Long Project Workspace、v0.8.9 Long Replay & Audit UI、v0.8.10-A/B Runner State Execution、v0.9.0-alpha Chapter Export、v0.9.0-alpha Chapter Collection Export、v0.9.0-alpha Export Share Guard、v0.9.0-alpha Creation Loop Completion Gate、v0.9.0-alpha Creation Loop Action Hints、v0.9.0-alpha Creation Loop Checklist、v0.9.0-alpha Continuation Hint、v0.9.0-alpha Resume Continue HTTP Job、v0.9.0-alpha Worldline Selection Persistence、v0.9.0-alpha Post-run Audit Entry |
| 官方下一版 | `v0.9.0-alpha Long Novel Creation Loop`（进行中） |
| 后续主线 | `v0.9.0-alpha` 长篇创作闭环 -> `v0.9.1-v0.9.4` 触发式增强 -> `v1.0-beta` 商业化加固 |

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
| v0.9.0-alpha | 长篇产品闭环 | 进行中：Chapter Export / Chapter Collection Export / Export Share Guard / Completion Gate / Action Hints / Checklist / Continuation Hint / Resume Continue HTTP Job / Worldline Selection Persistence / Post-run Audit Entry 已走通，完整主链路仍是 alpha |
| v0.9.1-v1.0-beta | 增强与商业化 | provider/cost、MasterSetting、图记忆/advanced runner 评估，以及商业级账号/权限/云端/观测 |

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

下一刀建议：继续 `v0.9.0-alpha Long Novel Creation Loop`，优先抽取 `resume continue` service 并新增 opt-in HTTP job；继续不改 `run_scene` 默认行为。

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
| v0.9.0-alpha | Long Novel Creation Loop | 上传 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出，形成完整长篇共创产品闭环 | 进行中：Chapter Export / Chapter Collection Export / Export Share Guard / Completion Gate / Action Hints / Checklist / Continuation Hint / Resume Continue HTTP Job / Worldline Selection Persistence / Post-run Audit Entry 已收口 |
| v0.9.1 | Provider & Cost Gateway Lite | 多 provider 配置、模型路由、成本/用量估算、失败回退、Key 脱敏展示 | 成本/稳定性触发 |
| v0.9.2 | MasterSetting Workspace Lite | 项目级世界设定、人物、时间线、道具、伏笔、章节摘要的只读/轻编辑工作台 | 长篇项目页稳定后 |
| v0.9.3 | Graph Memory Evaluation Spike | 评估 Zep / 图数据库 / GraphRAG 是否增强现有 ledger 检索 | BM25/ledger 召回不足时触发 |
| v0.9.4 | Advanced Runner Evaluation Spike | 评估 LangGraph 局部 runner、OASIS/CAMEL 可选 runner | v0.8.10 状态执行层不足时触发 |
| v1.0-beta | Commercial Hardening | 账号/项目空间、权限、云端持久化、配额、审计日志、版权提示、部署与观测 | 真实外部用户/团队长期使用时 |

## 每次任务完成后的收口清单

- 后端相关：`cd engine && python -m pytest -q`
- 前端相关：`cd engine/ui && pnpm run build`
- 代码清洁：`git diff --check`
- 文档：更新 `memory.md` 变更日志
- 若路线/README/UI spec 发生事实变化，同步对应文档
- 最终回答说明改了什么、验证结果、未做边界
