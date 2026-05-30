# Codex Handoff — Living Novel Engine

> 用途：新开 Codex 窗口时的接力包。新窗口第一步应先读本文件，再读 `AGENTS.md` 与项目四文档，不要只靠聊天摘要。

## 新窗口第一条消息建议

```text
请先阅读并对齐：
- AGENTS.md
- docs/codex-handoff.md
- memory.md
- docs/living-novel-engine-iteration-plan.md
- docs/living-novel-engine-prd.md
- docs/v0.7-product-web-app-ui-spec.md
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
- 后端 python -m pytest -q 为 573 passed
- 前端 cd engine/ui && pnpm run build 通过
- git diff --check 无 whitespace error

下一步进入 v0.8 收束整理：断点续传/恢复、导入报告细化，或 runner 状态执行层评估。请先读项目文档和现有代码，再判断具体实现；如果要改代码，遵守：
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
| 后端基线 | `573 passed` |
| 前端基线 | `pnpm run build` 通过 |
| 当前已收口 | v0.7 Product Web App、v0.7.2、v0.7.3、v0.7.4、v0.7.5、v0.8.0-A 至 v0.8.5-A、ActDirector-A、Discourse-aware Narrator-A、Dynamic Action Registry-A、Emergence Mining-A、Entity Aliases、Runtime Memory Consumption-A、Frontend Artifact Panel、Long Upload Productization |
| 官方下一版 | v0.8 收束整理 / 断点续传与恢复 / runner 状态执行层评估 |
| 后续主线 | 断点续传与恢复、导入报告细化、runner 状态执行层评估 |

## 资料位置

- 主 PRD：`D:\AI\open-infinite\docs\living-novel-engine-prd.md`
- docs 导航：`D:\AI\open-infinite\docs\index.md`
- v0.1-v0.8 版本审计：`D:\AI\open-infinite\docs\v0.1-to-v0.8-version-audit.md`
- 已完成的 PRD 与专项版本文档：`D:\AI\open-infinite\docs\prd`
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

- 真正断点续传/恢复、持久化 ingest job
- LLM 细粒度事件抽取、scene 级切分
- 向量库、embedding、reranker（entity alias resolution 第一刀已完成）
- runner 消费 action plan、dynamic action registry 或 emergence nodes，并执行状态变化
- 运行后写回审计、长篇 holdout 批量评估 UI

下一刀建议：优先断点续传/恢复和导入报告细化，或转向 runner consumption 的状态执行层。

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
- 未做：runner 消费动作计划/动作注册表/涌现节点并改变状态；跨 run 涌现聚类；真正断点续传/恢复。

## v0.8.x Long Upload Productization 收口摘要

- 后端 `import_novel_from_payload()` 新增 additive `upload` 入参：`filename/total_size/chunks[{index,data_b64}]`，支持 txt/md 文本拆章、zip 内 txt/md 章节、epub 内 html/xhtml 章节。
- `/api/import-novel` 与 `/api/jobs/import-novel` 均可传 `upload`；同步接口错误返回 400/409，异步 job 失败返回 `status=failed + error`，不白屏、不 500。
- 前端导入页支持 txt/md/zip/epub 文件选择、浏览器端分片、文件摘要、job 进度条、失败空态和重试；未选文件时保留原粘贴 3-10 章模式。
- 未做：真正多请求断点续传/恢复、持久化 ingest job、epub spine 精排、角色抽取置信度和时间线风险增强。

## 每次任务完成后的收口清单

- 后端相关：`cd engine && python -m pytest -q`
- 前端相关：`cd engine/ui && pnpm run build`
- 代码清洁：`git diff --check`
- 文档：更新 `memory.md` 变更日志
- 若路线/README/UI spec 发生事实变化，同步对应文档
- 最终回答说明改了什么、验证结果、未做边界
