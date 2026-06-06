# 未终章

未终章（Unfinale）是 `open-infinite` 的叙事引擎与本地产品工作台。本文只负责 `engine/` 的运行、API 和 artifact 说明；当前事实、文档分层和历史收口请分别看 [`../memory.md`](../memory.md)、[`../docs/index.md`](../docs/index.md) 与 [`../docs/project-changelog.md`](../docs/project-changelog.md)。

当前主线是 **World Sandbox Loop / 世界沙盘改造**，不是继续扩 provider、Graph、检索评测、发行或商业化面板。S1-S9 已形成第一版产品链路：世界沙盘、主观记忆、《天命书》、干预投放、L5 觉醒/模因传播、因果债具象化、世界自演、多视角正文、作者采纳、连续阅读、确认入卷、Reviewer 局部重写采纳和编辑后定稿都已有 additive service/API/UI/artifact/tests；世界沙盘页运行台已重组为“写事件 / 可选干预 / 启动推演”控制台，并前置到首屏。

最近产品化入口：

| 能力 | 当前状态 | 继续深入 |
| --- | --- | --- |
| 世界书架入口 | `StoryEntryPage` 已用 `storyShelfFocus` 按故事来源和运行次数推导“待确认天命 / 已有沙盘结果”、推荐下一步、来源和世界线运行数；首屏推荐世界面板会按导入优先、已有沙盘结果次之、原顺序兜底选择最该进入的世界，并展示推荐理由、状态、主动作和指标；故事卡主按钮会进入天命书或卷宗阅读，同时保留世界沙盘、天命书、卷宗阅读、作者采纳台和机制档案入口 | 更完整 `WorldWorkspaceShell`、跨页面视觉 QA |
| 世界内导航语境 | `AppShell` 已在所有世界内路由下方显示“当前位置”纸面条，按锚定、天命书、沙盘、阅读、长线卷、角色卷、势力卷、事件卷、世界线、检查点、多视角、作者台和机制档案说明页面职责；同时提供“定界 / 运行 / 阅读 / 采纳”世界体验轨道、全局“继续阅读”、主动作/次动作，以及“正文 / 正史 / 锚点 / 角色 / 势力 / 事件 / 长线 / 世界线”卷宗速览盘；移动端壳层已压缩，390px/360px 下 9 个顶栏入口、4 个阶段和 8 个卷宗入口均保留且无水平溢出 | 更完整 `WorldWorkspaceShell`、跨页面视觉 QA |
| 世界锚定页 | `WorldAnchorPage` 已把世界启动、最近阅读续航、世界状态条、世界卷宗总览、世界脉搏、当前旅程状态、锚定轻编辑、视觉资产、基线回放、实体别名和角色探针组织成进入某世界后的第一房间；桌面中栏展示世界内地图、当前正文/角色/伏笔/运行脉搏和下一步状态，移动端在品牌后前置“当前阶段 / 下一步 / 世界脉搏”状态条，并在启动卡后保留紧凑总览，势力标签可进入势力卷 | 完整 `WorldWorkspaceShell`、账号级阅读进度 |
| 角色个人卷页 | `CharacterVolumePage` / `#/world/<slug>/worldlines/<worldline_id>/characters/<character_id>` 已复用 `dossier-reading` 与 `subjective-memory`，把单个角色的个人卷正文、主观记忆链、误会、未知正史、秘密可见性和证据锚点组织成可读页面；移动端首屏已有“读立场 / 查记忆 / 换角色 / 作者台”导读条；锚定页、沙盘页、多视角页和卷宗阅读页都有入口 | 跨章角色长线阅读、跨卷证据联动 |
| 势力卷页 | `FactionVolumePage` / `#/world/<slug>/worldlines/<worldline_id>/factions/<faction_id>` 已复用世界锚定、`dossier-reading` 与 `worldline_state`，把势力卷正文、势力目录、因果压力域、最近 ledger 和证据锚点组织成可读页面；移动端首屏已有“看站位 / 查代偿 / 换势力 / 作者台”导读条；锚定页、多视角页和卷宗阅读页都有入口 | 跨章势力长线阅读、跨卷证据联动 |
| 事件多视角详情页 | `GET /api/stories/<slug>/worldlines/<worldline_id>/events/<event_id>/perspectives` 与 `EventPerspectivePage` / `#/world/<slug>/worldlines/<worldline_id>/events/<event_id>/perspectives` 已复用 `dossier-reading` 与 `character_lens_volumes`，把同一事件的节拍、正文、信息差、误读列表、证据链和去卷宗阅读/角色卷/世界线/长线卷/作者台动作组织成独立页面；移动端首屏已有“读事件 / 看信息差 / 查证据 / 作者台”导读条 | 更深跨章误会网络 |
| 跨事件长线卷 | `GET /api/stories/<slug>/worldlines/<worldline_id>/longline-reading` 与 `LonglineReadingPage` / `#/world/<slug>/worldlines/<worldline_id>/longline` 已复用 `dossier-reading`、`worldline_dossier`、连续阅读场景、卷宗、确认入卷和证据链，把事件、误会、角色记忆、势力压力和作者承接组织成可点击长线时间线，并已新增阅读进度、多事件索引、误会回收台、未解线索跳转和移动端“读长线 / 按事件追 / 回收误会 / 作者台”首屏导读条 | 更深跨章误会网络、跨章节回收 |
| 卷宗阅读页 | `GET /api/stories/<slug>/worldlines/<worldline_id>/dossier-reading` 与 `DossierReadingPage` 已让用户默认读连续正文；连续正文已按场景展示阅读进度、认知偏差、冲突转折、段内证据锚点、当前场景导读条和可点击误会图谱，并可切换世界正史卷、主锚点卷、角色个人卷、势力卷、事件多视角和确认稿；移动端首屏已有“开始读正文 / 查卷宗 / 作者台”导读条；阅读类路由会写入前端本机最近阅读续航，锚定页和 AppShell 都能一键回到最近阅读位置 | 更深跨章误会网络、账号级用户阅读进度持久化 |
| 世界线档案页 | `GET /api/stories/<slug>/worldlines/<worldline_id>/dossier` 与 `WorldlineDossierPage` 已让用户首屏理解分支状态、因果债、检查点、自演任务、代偿域和下一步动作，并可进入长线卷；移动端 hero 后新增“回放 / 看代偿 / 看任务 / 长线卷”承接导读条 | 醒来报告文学化、跨章节回收 |
| 检查点回放页 | `GET /api/world-autopilot-runs/<run_id>/checkpoints/<checkpoint_id>` 与 `CheckpointReplayPage` 已让用户首屏理解本轮大事件、角色记忆、因果代偿和连续阅读出口；移动端 hero 后新增“继续读 / 看记忆 / 看代偿 / 作者台”醒来导读条，可直接进入连续阅读、角色记忆、具象代偿或作者采纳台 | 醒来报告文学化、长线阅读进度 |
| 自演结果可读入口 | `autopilot_report.readable_entry` 与 `GET /api/world-autopilot-runs/<run_id>/readable-entry` 已把最近检查点、角色个人卷、事件多视角和连续阅读串起来 | 更强醒来报告文学节奏和长线阅读进度 |
| Reviewer 局部重写采纳 | `POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-rewrites` 已写 `accepted_local_rewrites.json` / `next_chapter_draft_revised.md` / `edited_final_chapter.json`，确认入卷可自动采用编辑后定稿并携带已采纳改写 ids | 更强真实语义 Reviewer、整章风格润色 |
| 作者采纳台 | `AuthorAdoptionPage` 首屏四步中枢已前置写入采纳台、生成草稿、采纳局部改写、确认入卷和回世界沙盘动作；移动端中枢压缩后保留“写入采纳台 / 调整材料 / 回世界沙盘”，并可直接滚到采纳材料表单 | 可回滚对照、真实模型编辑器、作者定稿质量门 |
| 真实 LLM 策略建议 | `llm_decision_mode=advisory` 会写 `agent_decision_advisory.json`，展示采信、欺骗、传播、反抗和临场判断 | 多轮策略规划、长期关系/势力博弈 |

命名边界：面向用户和文档的产品名为“未终章 / Unfinale”；Python 包、CLI、artifact 路径和环境变量前缀仍沿用 LNE / `living_novel_engine`。

本 README 不承担当前下一刀来源。判断下一步时先读 `memory.md` 与世界沙盘 PRD。

## 当前状态

| 项 | 状态 |
| --- | --- |
| 后端 | Python package + `lne` CLI + 本地 HTTP API |
| 前端 | `engine/ui` React + Vite 产品工作台 |
| 入口边界 | 前端是产品入口，API 是能力层，CLI 是工程外壳；用户级功能优先走 Web UI + API |
| 当前收口 | v1.0-local 与后续增强四十五刀已作为支撑层收口；World Sandbox Loop S1-S9 与世界入口旅程状态、沙盘运行台、最近阅读/自演/检查点/Reviewer 产品化入口已完成第一版 |
| 后端验证基线 | `python -m pytest -q` -> `951 passed` |
| 前端验证基线 | `cd engine/ui && pnpm run build` 通过 |
| 当前迭代点 | 世界沙盘闭环体验打磨；多轮策略规划、长正文质量、更深跨章误会回收、更强 Reviewer 和整章风格润色是主线，真实检索 provider 和向量检索 Pipeline 只作为支撑层 |

仍然后置：云端多用户持久队列、真实对象存储 adapter、真实认证、硬配额执行、商业计费系统、webhook、GraphRAG/Zep、高级 runner 默认替换，以及 hybrid vector 是否默认替换 BM25。

## 当前纠偏主线

后续开发不要继续默认扩 Graph/provider/检索评测/工程看板，也不要继续往 `WorkspacePage.tsx` 堆只读面板。下一批代码应把现有导入、世界锚定、干预编译、多 Agent、记忆、世界线和章节渲染能力重新组织成“世界书架 -> 世界内部卷宗”：

```text
世界书架
  -> 导入故事世界 / 新建世界
  -> 天命书
  -> 世界沙盘
  -> 世界正史卷
  -> 主锚点卷
  -> 角色个人卷
  -> 势力卷
  -> 事件多视角
  -> 世界线 / 检查点
  -> 作者采纳台
```

首批目标 artifact 以 additive 方式加入，不破坏既有 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json` 契约：

- `projects/<slug>/tianming.json`
- `projects/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective_memory.jsonl`
- `outputs/<run_id>/sandbox_rounds.jsonl`
- `outputs/<run_id>/agent_decision_advisory.json`
- `outputs/<run_id>/subjective_memory_delta.json`
- `outputs/<run_id>/autopilot_report.json`
- `outputs/<run_id>/checkpoints/checkpoint_*.json`
- `outputs/<run_id>/character_lens_briefs.json`
- `outputs/<run_id>/character_lens_volumes.json`
- `projects/<slug>/author_adoption_ledger.jsonl`
- `outputs/<run_id>/author_adoption_record.json`
- `outputs/<run_id>/author_adoption_brief.md`
- `outputs/<run_id>/next_chapter_brief.json`
- `outputs/<run_id>/next_chapter_draft.json`
- `outputs/<run_id>/next_chapter_draft.md`
- `outputs/<run_id>/accepted_local_rewrites.json`
- `outputs/<run_id>/next_chapter_draft_revised.md`
- `outputs/<run_id>/draft_revision_pack.json`
- `outputs/<run_id>/continuous_reading_chapter.json`
- `outputs/<run_id>/continuous_reading_chapter.md`
- `projects/<slug>/worldlines/<worldline_id>/worldline_state.json`

已实现第一版：

- `POST /api/stories/<slug>/sandbox/run`：输入 `major_event` 与可选 `worldline_id`，生成本地单轮沙盘；可选 `intervention_content` / `intervention_target` / `intervention_projection_mode` 会先读取《天命书》编译为本轮干预约束；显式传 `llm_decision_mode=advisory` 时会调用真实 LLM 生成逐角色决策建议并写 `agent_decision_advisory.json`，默认仍不调用外部模型。
- `GET /api/sandbox-runs/<run_id>`：读取沙盘轮次结果。
- `GET /api/stories/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective-memory`：读取某角色在某世界线上的主观记忆链。
- `POST /api/stories/<slug>/tianming/generate`：从本地设定派生 `tianming.json` 草案。
- `GET /api/stories/<slug>/tianming`：读取天命书。
- `POST /api/stories/<slug>/tianming/confirm`：用 `confirm=true` 轻量确认天命书。
- `POST /api/stories/<slug>/tianming/intervention-compile`：读取天命书并预编译自由干预，支持可选 `projection_mode=immersive|wild_au`，输出类型、层级、兼容性、转译策略、Divergent/AU、分支轴和因果债。
- L4/L5/AU 干预预编译会写 `projects/<slug>/worldlines/<worldline_id>/tianming_snapshot.json`，返回 `worldline_tianming_snapshot`，根 `tianming.json` 不被覆盖。
- 旧版已确认 `tianming.json` 会在生成或读取时补齐 S3 宪法字段，同时保留既有吸引子。
- `POST /api/stories/<slug>/narrative-compensation/run`：生成世界线代偿 delta，解释锚点转移、候选承载者、因果债扩散和世界内压力。
- `POST /api/stories/<slug>/world-autopilot/run`：连续运行沙盘轮次，支持轮数、事件、时间、锚点变化、因果债爆发或角色觉醒目标，生成世界自演报告与检查点；可传 `resume_from_run_id` / `resume_from_checkpoint` 从检查点接续。
- `GET /api/stories/<slug>/worldlines/<worldline_id>/worldline-state`：读取可持续世界线状态。
- `GET /api/stories/<slug>/worldlines/<worldline_id>/dossier`：聚合世界线状态、天命审计、自演任务和检查点，供世界线档案页展示。
- `GET /api/stories/<slug>/worldlines/<worldline_id>/dossier-reading`：聚合连续阅读稿、确认稿、跨卷宗 trail、多视角卷宗和世界线 dossier，供世界内部卷宗阅读页展示；不新增持久 artifact。
- `GET /api/stories/<slug>/worldlines/<worldline_id>/longline-reading`：聚合连续阅读场景、卷宗、检查点、确认入卷和证据链，供跨事件长线卷展示阅读进度、多事件索引、误会回收台、未解线索和下一步动作；不新增持久 artifact。
- `GET /api/stories/<slug>/worldlines/<worldline_id>/events/<event_id>/perspectives`：聚合事件多视角正文、场景节拍、信息差、误读列表和证据链，供事件详情页展示；不新增持久 artifact。
- `GET /api/world-autopilot-runs/<run_id>/readable-entry`：读取或复算自演报告的可读世界线入口，返回最近检查点、角色个人卷、事件多视角、连续阅读路由以及状态变化/记忆/因果债摘要。
- `GET /api/stories/<slug>/worldlines/<worldline_id>/world-autopilot/tasks/<task_id>`：读取自演任务进度。
- `POST /api/stories/<slug>/worldlines/<worldline_id>/world-autopilot/tasks/<task_id>/pause|resume`：暂停或恢复本地自演任务状态。
- `GET /api/world-autopilot-runs/<run_id>/checkpoints/<checkpoint_id>`：回放自演检查点。
- `POST /api/stories/<slug>/character-lens/generate`：从同一事件生成世界正史卷、主锚点卷、角色个人卷、势力卷和事件多视角 brief。
- `POST /api/stories/<slug>/author-adoption`：作者采纳、部分采纳、另开分支或导出 brief，写入本地采纳账本，并生成 `next_chapter_brief.writing_plan` / `feed_forward` 作为下一章生成和后续沙盘入口；另开分支会创建作者分支世界线状态。
- `POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-draft`：把作者采纳后的下一章 brief、世界线状态和具象代偿生成可读下一章草稿，并同步生成连续阅读稿与 S8 卷宗引用；`mock=true` deterministic，`mock=false` 显式走真实 LLM smoke。
- `POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-rewrites`：把作者选中的 Reviewer 局部重写建议写入 `accepted_local_rewrites.json` / `next_chapter_draft_revised.md` / `edited_final_chapter.json` / `edited_final_chapter.md`，并 additive 反哺 `next_chapter_draft.json`、确认入卷和下一轮沙盘入口。
- `POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-confirmation`：把作者编辑后的草稿确认入卷，写入确认记录、Markdown 正文和跨卷宗阅读链，并回写世界线状态与下一轮沙盘入口。
- `projects/<slug>/tianming.json`：叙事吸引子、题材约束、锚点状态、合约压力和候选天命承载者。
- `outputs/<run_id>/tianming_delta.json`：世界线代偿报告。
- `outputs/<run_id>/autopilot_report.json`：世界自演报告，包含目标、状态、停止原因、停止证据、沙盘运行、最终阶段、醒来时间线、`narrative_timeline`、失败恢复信息、检查点索引和 `readable_entry` 可读世界线入口；每个 checkpoint 额外带 `scene_beats` 与 `chapter_seed`。
- `outputs/<run_id>/checkpoints/checkpoint_*.json`：每轮自演检查点，记录大事件、锚点压力、因果债、角色记忆变化和后续剧情可能性，可作为失败恢复入口。
- `worldline_dossier`：只读 API 聚合，不新增持久 artifact；读取世界线状态、自演任务和检查点，驱动世界线页与检查点回放页。
- `outputs/<run_id>/character_lens_briefs.json`：多视角活体小说 brief，记录世界正史卷、主锚点卷、角色个人卷、势力卷和事件多视角。
- `outputs/<run_id>/character_lens_volumes.json`：多视角正文，记录世界正史卷、主锚点卷、角色个人卷、势力卷和事件多视角的可读正文、`novel_scene_plan` 和证据链。
- `projects/<slug>/author_adoption_ledger.jsonl`：作者采纳账本，记录采纳、部分采纳、另开分支或导出 brief。
- `outputs/<run_id>/author_adoption_record.json`：单次作者采纳记录和原大纲 vs 沙盘涌现剧情对照。
- `outputs/<run_id>/author_adoption_brief.md`：可交给后续章节 brief 或人工整理的采纳说明。
- `outputs/<run_id>/next_chapter_brief.json`：作者采纳后的下一章 brief、伏笔保留项、原大纲差异、Reviewer 建议和后续沙盘入口；`writing_plan` 面向作者阅读，`feed_forward.chapter_generation_inputs` 面向章节生成，`feed_forward.sandbox_continuation_inputs` 面向后续世界沙盘运行。
- `outputs/<run_id>/next_chapter_draft.json`：作者采纳后的下一章正文草稿、证据链、Reviewer 检查和局部修订包引用。
- `outputs/<run_id>/next_chapter_draft.md`：可阅读的下一章正文导出，不覆盖正史 `chapter.md`。
- `outputs/<run_id>/draft_revision_pack.json`：下一章草稿的局部修订包，包含确认前 gate、语义 Reviewer、局部改写建议、编辑应用预览 `editorial_revision_draft` 和证据引用。
- `outputs/<run_id>/accepted_local_rewrites.json`：作者勾选采纳的 Reviewer 局部重写，包含原问题、修改意图、建议改写、影响角色/世界状态、证据链、编辑后定稿摘要和 feeds。
- `outputs/<run_id>/next_chapter_draft_revised.md`：带已采纳局部重写清单的兼容修订稿，不覆盖原草稿 Markdown 或正史。
- `outputs/<run_id>/edited_final_chapter.json` / `edited_final_chapter.md`：把已采纳局部重写应用成可确认正文；确认入卷未传手动正文时会自动采用它，并记录 `edit_source=auto_reviewer_final`。
- `outputs/<run_id>/continuous_reading_chapter.json`：连续阅读稿结构，包含阅读场景、阅读流、下一章钩子、来源 S8 场景计划 `story_beat_source`、卷宗和证据 refs。
- `outputs/<run_id>/continuous_reading_chapter.md`：按场景连续阅读的章节稿，正文先读、证据后查，不覆盖正史 `chapter.md`。
- `outputs/<run_id>/confirmed_chapter_entry.json`：作者确认入卷后的章节记录、证据链、Reviewer 检查和后续沙盘入口。
- `outputs/<run_id>/confirmed_chapter.md`：作者确认后的可读正文导出，不覆盖正史 `chapter.md`。
- `outputs/<run_id>/confirmed_chapter_reading_trail.json`：确认稿跨卷宗阅读链，引用世界线状态、来源采纳记录、世界正史卷、角色个人卷和事件多视角证据。
- `dossier_reading`：只读 API 聚合，不新增持久 artifact；读取连续阅读稿、确认稿、阅读链、多视角卷宗和世界线 dossier，驱动卷宗阅读页默认正文阅读、卷宗切换、误会图谱和折叠证据链。
- `longline_reading`：只读 API 聚合，不新增持久 artifact；读取连续阅读场景、卷宗、检查点、确认入卷和证据链，驱动长线卷的跨事件时间线、阅读进度、多事件索引、误会回收台、五条发酵线、未解线索和下一步动作。
- `projects/<slug>/worldlines/<worldline_id>/worldline_state.json`：干预、快照审计、因果债、锚点状态、候选承载者、模因污染传播、具象代偿和作者采纳结果的后续沙盘输入；另开作者分支时会写入新分支状态和来源世界线，不覆盖根正史。
- `outputs/<run_id>/sandbox_rounds.jsonl`：逐行记录本轮角色意图、决策输入、外在行动、真实意图、风险、行动结果、冲突、信息传播和世界状态 delta。
- `outputs/<run_id>/agent_decision_advisory.json`：显式启用 `llm_decision_mode=advisory` 时写入，记录真实 LLM 对逐角色采信、欺骗、传播、反抗、临场判断、信任移动和记忆种子的建议；失败时沙盘保留 deterministic 行动。
- `outputs/<run_id>/intervention_constraint.json`：当本轮沙盘带干预文本时写入，记录天命书编译出的投放方式、异物入侵标记、法则吸收、分支轴、因果债、世界线快照和普通干预不覆盖根天命书边界。
- `outputs/<run_id>/sandbox_summary.json`：聚合本轮摘要、边界和下一步故事可能性。
- `outputs/<run_id>/subjective_memory_delta.json`：聚合本轮写入的角色主观记忆，包含主观感知、内心想法、推测动机、误会、未知正史、秘密可见性、L5 高维真相、命痕和模因传播采信证据。
- `projects/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective_memory.jsonl`：角色自己的连续主观记忆链，下一轮行动和冲突会读取上一轮记忆/误会。

## 快速开始

推荐从仓库根目录使用本地启动脚本：

```powershell
cd D:\AI\open-infinite
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start-local.ps1
```

脚本会检查 Python、Node.js、pnpm，准备 `engine/.venv`，安装依赖，启动后端 `lne browse` 和 Vite 前端，并打开 `http://127.0.0.1:5173/`。日志写入根目录 `.local-run/`。

普通用户入口是 `http://127.0.0.1:5173/` 的产品工作台；CLI 只作为本地服务启动、开发者验收、批处理复跑和 JSON 导出的工程工具。后续用户级功能应优先通过前端调用 API 完成，不要求用户复制命令行。

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

DASHSCOPE_API_KEY=your_dashscope_key
LNE_EMBEDDING_MODEL=text-embedding-v3
LNE_EMBEDDING_DIMENSION=1024
LNE_ZILLIZ_URI=https://your-cluster.zillizcloud.com:19530
LNE_ZILLIZ_TOKEN=your_zilliz_token
LNE_ZILLIZ_COLLECTION=unfinale_memory
LNE_RERANK_MODEL=gte-rerank-v2
LNE_RERANK_TOP_N=5
# 可选：让 run/resume 运行时消费真实向量链路
LNE_RETRIEVAL_STRATEGY=hybrid_vector
```

密钥边界：

- 未配置 `LLM_API_KEY` 或设置 `LNE_MOCK=1` 时，文字链路走本地 mock / deterministic fallback。
- 未配置 `SEEDREAM_API_KEY` 或设置 `LNE_VISUAL_ASSETS=0` 时，视觉资产稳定降级为占位，不阻塞文字主流程。
- 检索增强 provider 使用百炼 `text-embedding-v3`、Zilliz Cloud 和百炼 `gte-rerank-v2`；项目工作台可显式构建 Zilliz 索引并做检索预览。默认 BM25 检索不被替换，只有设置 `LNE_RETRIEVAL_STRATEGY=hybrid_vector` 后，run/resume 运行时才消费真实向量链路。
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
| `DASHSCOPE_API_KEY` | 百炼通用密钥，可被 embedding / reranker 复用 |
| `LNE_EMBEDDING_API_KEY` | 百炼 embedding 独立密钥；未填时复用 `DASHSCOPE_API_KEY` |
| `LNE_EMBEDDING_BASE_URL` | 百炼 OpenAI-compatible embedding 地址 |
| `LNE_EMBEDDING_MODEL` | embedding 模型，默认 `text-embedding-v3` |
| `LNE_EMBEDDING_DIMENSION` | embedding 维度，默认 `1024` |
| `LNE_ZILLIZ_URI` | Zilliz Cloud cluster endpoint |
| `LNE_ZILLIZ_TOKEN` | Zilliz Cloud API key 或 `user:password` token |
| `LNE_ZILLIZ_COLLECTION` | 检索增强 collection 名，默认 `unfinale_memory` |
| `LNE_RERANK_API_KEY` | 百炼 reranker 独立密钥；未填时复用 `DASHSCOPE_API_KEY` |
| `LNE_RERANK_ENDPOINT` | 百炼 text-rerank HTTP endpoint |
| `LNE_RERANK_MODEL` | reranker 模型，默认 `gte-rerank-v2` |
| `LNE_RERANK_TOP_N` | reranker 返回条数，默认 `5` |
| `LNE_RETRIEVAL_STRATEGY=hybrid_vector` | 显式让运行时使用百炼 embedding + Zilliz + 百炼 rerank；未设置时保持 BM25 |

## 开发者常用命令

以下命令用于开发、调试、自动化验收、批处理和无人值守复跑。普通用户功能入口应放在前端；CLI 命令只做同一套 service/API 能力的薄封装，不作为用户主流程。

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

# 检索失败样本采集与复跑
lne memory add-sample <slug> --query "她必须追查那个遗失的关键物证" --entity mo_qing_yan --entity retreat_bell --reason "换说法未命中" --chapter 2
lne memory samples <slug> --json --require-candidate
lne memory export-samples <slug> --json
lne memory mock-report <slug> --json --require-candidate
lne memory replay-report <slug> --json --require-clean
lne memory migration-pack <slug> --json
lne memory index-samples --json
lne memory trend-snapshot --json
lne memory graph-trigger <slug> --json
lne memory graph-design <slug> --json
lne memory graph-shadow <slug> --json
lne memory graph-cases <slug> --json
lne memory graph-boundaries <slug> --json
lne memory graph-replay-plan <slug> --json
lne memory graph-replay-report <slug> --json
lne memory graph-fixture-pack <slug> --json
lne memory graph-readiness-gate <slug> --json
lne memory graph-runbook <slug> --json
lne memory graph-result-template <slug> --json
lne memory graph-mock-result <slug> --json
lne memory graph-review-gate <slug> --json
lne memory graph-manual-approval-pack <slug> --json
lne memory graph-approval-evidence-checklist <slug> --json
lne memory graph-opt-in-evidence-snapshot <slug> --json
lne memory graph-opt-in-no-go-matrix <slug> --json
lne memory graph-opt-in-operator-checklist <slug> --json
lne memory graph-opt-in-review-packet <slug> --json
lne memory graph-opt-in-decision-ledger-preview <slug> --json
lne memory graph-opt-in-final-readiness-summary <slug> --json
lne memory graph-opt-in-human-signoff-schema <slug> --json
lne memory graph-opt-in-config-draft <slug> --json
lne memory graph-local-provider-contract <slug> --json
lne memory graph-single-fixture-dry-run-harness <slug> --json
lne memory graph-mock-compatible-adapter <slug> --json
lne memory graph-manual-mock-adapter-review <slug> --json
```

`browse` 启动的是本地后端和旧只读 viewer；普通用户产品入口在 `engine/ui`，通过 Vite 访问。若某项能力会影响用户理解、选择或操作，优先补前端 + API 入口，再视自动化需要补 CLI。

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
- 长篇项目工作台、导入检查、设定工作台、设定卡片、向量检索就绪、真实向量检索、Embedding 样本评估、失败样本采集、GraphRAG/Zep 触发证据、Graph 记忆设计包、Graph 记忆 Shadow 对照、Graph 记忆 Provider 边界、离线 Replay、Provider Spike 前置包、Readiness Gate、Runbook、结果模板、Mock 结果报告、Review Gate、Manual Approval Pack、Opt-in Review Packet、Decision Ledger Preview、Final Readiness Summary、Human Signoff Schema Draft、Config Draft、Local Provider Contract、Single Fixture Dry-run Harness、Mock-compatible Adapter、Manual Mock Adapter Review、回放与审计、章节导出。
- 分支右栏：机制档案、投影健康、读者评审、上下文包、状态、检索记忆、Agent 轨迹、世界线评审。
- 设置抽屉：运行设置、模型配置、任务模型画像、接口契约、发行准备、provider 状态、usage/成本估算、商业化边界只读清单。

产品纠偏后的前端目标态：

- 一级主导航按“世界书架”组织；进入某个世界后再出现天命书、世界沙盘、正史卷、角色个人卷、势力卷、事件多视角、世界线、检查点和作者采纳台。
- “沙盘 / 阅读 / 干预 / 作者”不是一级工作区，而是同一个世界内部的场景能力。
- `WorkspacePage.tsx` 已承载过多工程支撑面板；后续改造应拆出世界内部卷宗壳和具体页面，不继续堆 Graph/provider/报告 UI。
- 已有检索、Graph/provider、OpenAPI、发行、计费面板保留为支撑层，默认不作为下一刀产品主线。

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
    ├── project_retention_policy.json
    └── retrieval_failure_samples.jsonl   # 可选：本地记录的 BM25 召回失败样本
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
| 故事/项目 | `GET /api/stories`、`GET /api/stories/<slug>`、`GET /api/stories/<slug>/project-workspace`、`GET /api/stories/<slug>/runtime-preflight`、`GET /api/stories/<slug>/cards-workspace`、`GET /api/stories/<slug>/vector-retrieval-readiness`、`POST /api/stories/<slug>/vector-retrieval/index`、`POST /api/stories/<slug>/vector-retrieval/search`、`GET /api/stories/<slug>/embedding-evaluation-samples`、`GET /api/stories/<slug>/retrieval-sample-export-pack`、`GET /api/stories/<slug>/embedding-mock-evaluation-report`、`GET /api/stories/<slug>/retrieval-sample-replay-report`、`GET /api/stories/<slug>/retrieval-sample-migration-pack`、Graph/长期记忆支撑层系列端点（trigger/design/shadow/case/boundary/replay/fixture/readiness/runbook/result/mock/review/approval/opt-in/final/signoff/config/contract/harness/adapter/manual-mock-review）、`GET/POST /api/stories/<slug>/retrieval-failure-samples` |
| 导入/创世/job | `POST /api/import-novel`、`POST /api/story-genesis`、`POST /api/jobs/import-novel`、`GET /api/jobs/<id>` |
| 干预/续写 | `POST /api/interventions`、`POST /api/jobs/intervention`、`POST /api/jobs/resume-continue` |
| 世界沙盘/卷宗 | `POST /api/stories/<slug>/sandbox/run`、`GET /api/sandbox-runs/<run_id>`、`GET /api/stories/<slug>/worldlines/<worldline_id>/worldline-state`、`GET /api/stories/<slug>/worldlines/<worldline_id>/dossier`、`GET /api/stories/<slug>/worldlines/<worldline_id>/dossier-reading`、`GET /api/world-autopilot-runs/<run_id>/readable-entry`、`GET /api/world-autopilot-runs/<run_id>/checkpoints/<checkpoint_id>`、`POST /api/stories/<slug>/author-adoption`、`POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-rewrites` |
| run/branch | `GET /api/runs`、`GET /api/runs/<run_id>`、`GET /api/runs/<run_id>/branches/<branch_id>`、`GET /api/runs/<run_id>/branches/<branch_id>/projection-health`、`GET /api/runs/<run_id>/branches/<branch_id>/reader-panel`、`GET /api/runs/<run_id>/branches/<branch_id>/prompt-budget-pack` |
| 评估/审计 | baseline、canon replay、worldline judgement、replay audit、audit log、creation loop closeout |
| 导出 | chapter export、chapter collection export、audit log export |
| 设置 | runtime、providers、provider usage、model configuration、retrieval provider configuration/test、LLM profile assignment、api contract、retrieval samples index、retrieval samples trend snapshot、packaging readiness、commercial status、preflight/boundary checklists |

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

真实外部模型 smoke 不是默认全量 pytest 的前置条件。单元测试和契约测试应保持 mock-safe、低成本、可复现。

但产品验收不能只看 mock。用户已允许使用 `.env` 中真实接入的模型 API 做小样本 smoke。涉及 Agent 决策、叙事生成、章节 brief、多视角正文、Reviewer 或视觉质量的切片，完成 mock 回归后，应额外调用真实 `LLM_API_KEY` / `SEEDREAM_API_KEY` 链路观察真实输出质量，并记录输出质量、失败原因和是否回退；不得打印明文 key，不做大规模消耗，不把真实外网调用塞进默认全量 pytest。

检索增强可先调用 `POST /api/settings/retrieval-provider/test` 且 `mock=true` 做本地契约检查；改为 `mock=false` 才会尝试百炼 embedding、Zilliz Cloud 和百炼 reranker。项目工作台的「真实向量检索」可显式构建/刷新 Zilliz 索引并做检索预览；只有设置 `LNE_RETRIEVAL_STRATEGY=hybrid_vector` 后，运行时才消费该链路。

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
- Zep / 图数据库 / GraphRAG 默认替换；embedding / Zilliz / reranker 已具备显式配置、smoke、索引写入和检索预览，但默认 BM25 + canon ledger + entity aliases 仍不被替换。
- OASIS / CAMEL / LangGraph，除非现有 runner、trace 与状态执行层无法解释真实复杂样例。
- overlay 自动驱动下一轮 runner、运行后审计写入正史账本、LLM 语义评审和 run 级聚合评审。
