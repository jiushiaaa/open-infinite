# 未终章世界沙盘改造 PRD

> 用途：定义当前世界沙盘主线的产品目标、能力边界、S1-S9 深化方向和验收口径。最新完成事实以 `../memory.md` 为准；文档分层以 `index.md` 为准；API/artifact 细节以 `../engine/README.md` 为准。

## 1. 目标

把未终章从“工程能力不断堆叠”纠偏为“小说世界沙盘 / 活体小说运行时”：

```text
导入 / 创世
  -> AI 预抽并确认《天命书》
  -> 多 Agent 世界沙盘轮次
  -> 每个角色写入独立主观记忆链
  -> 世界状态、锚点、因果债和代偿变化
  -> 世界自演生成检查点
  -> 读者自由干预经干预编译器投放
  -> 多视角活体小说与连续阅读
  -> 作者采纳、局部重写、编辑后定稿、确认入卷
```

当前 S1-S9 已形成第一版产品链路。后续不再补“有没有”，而是打磨：

- 真实 LLM 多 Agent 策略博弈。
- 长正文/连续阅读读感。
- 正文内证据锚点和误会图谱。
- 更强真实语义 Reviewer。
- 整章风格润色和真实模型编辑器。

## 2. 不变硬边界

- 不改 `run_scene` 默认行为。
- 不破坏既有 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 新 artifact、API 字段和 UI 读取都保持 additive。
- HTTP-facing identifier 必须安全校验；失败返回明确 400/404/409；坏 artifact 降级为空态、需留意或需修复，不白屏、不 500。
- 前端中文，古风纸面、克制系统感。
- 前端是产品入口，API 是能力层，CLI 是工程外壳。
- 不继续扩 provider、GraphRAG/Zep、检索评测、OpenAPI、发行、计费或工程面板，除非用户明确点名且它直接服务世界沙盘体验。

## 3. 主导航

一级按世界组织：

```text
世界书架
  -> 某个故事世界
      -> 天命书
      -> 世界沙盘
      -> 世界正史卷
      -> 主锚点卷
      -> 角色个人卷
      -> 势力卷
      -> 事件多视角
      -> 世界线
      -> 检查点
      -> 作者采纳台
```

“沙盘 / 阅读 / 干预 / 作者”是场景能力，不做一级工作区。旧 `WorkspacePage.tsx` 只保留支撑层或过渡入口，不继续堆主体验面板。

## 4. 当前已闭环第一版

| 模块 | 第一版状态 | 仍需深化 |
| --- | --- | --- |
| S1 多 Agent 沙盘 | `sandbox_rounds.jsonl`、沙盘 API/UI、显式 opt-in `llm_decision_mode=advisory`、`agent_decision_advisory.json` 已有 | 多轮策略规划、长期关系/势力博弈、失败/误判结算、真实模型稳定性 |
| S2 主观记忆链 | 角色按世界线写 `subjective_memory.jsonl`，包含误会、秘密、异常感、L5 真相和传播证据 | 长期召回、记忆压缩/遗忘、误会图谱、角色不知道的正史事实对照 |
| S3 天命书 | `tianming.json`、吸引子、锚点、压力、候选承载者、世界线快照第一版已有 | 动态更新、角色反向改写条件、快照审计确认 |
| S4 干预投放 | 干预编译器读取《天命书》，普通干预进入沙盘约束，L4/L5/AU 写世界线快照 | 分支持久继续运行、干预后的多轮追踪 |
| S5 觉醒/模因 | L5 觉醒写入角色命痕、反抗、模因传播和 `meme_propagation_readout` | 真实心理博弈、思想瘟疫长期演化、假意服从和反向利用 |
| S6 代偿状态 | `worldline_state.json` 与 `consequence_state` 六域代偿被下一轮沙盘、自演、正文和 brief 消费 | 可累积状态机、真实 LLM 决策消费、代偿长期发酵 |
| S7 世界自演 | `autopilot_report.json`、checkpoints、任务状态、暂停/恢复、`readable_entry` 已有 | 醒来报告文学化、长时运行守护、中断自动恢复 |
| S8 多视角正文 | `character_lens_volumes.json`、`novel_scene_plan`、世界正史卷/主锚点卷/角色个人卷/事件多视角第一版已有 | 角色/势力独立卷、正文内证据锚点、跨章节回收 |
| S9 作者采纳 | `next_chapter_brief`、草稿、连续阅读、局部重写采纳、编辑后定稿、确认入卷和 reading trail 已有 | 更强 Reviewer、整章风格润色、真实模型编辑器 |

## 5. 核心 artifact

已落地的世界沙盘主线 artifact 包括：

```text
projects/<slug>/tianming.json
projects/<slug>/worldlines/<worldline_id>/tianming_snapshot.json
projects/<slug>/worldlines/<worldline_id>/worldline_state.json
projects/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective_memory.jsonl
projects/<slug>/author_adoption_ledger.jsonl

outputs/<run_id>/sandbox_rounds.jsonl
outputs/<run_id>/agent_decision_advisory.json
outputs/<run_id>/intervention_constraint.json
outputs/<run_id>/subjective_memory_delta.json
outputs/<run_id>/tianming_delta.json
outputs/<run_id>/autopilot_report.json
outputs/<run_id>/checkpoints/checkpoint_*.json
outputs/<run_id>/character_lens_briefs.json
outputs/<run_id>/character_lens_volumes.json
outputs/<run_id>/author_adoption_record.json
outputs/<run_id>/author_adoption_brief.md
outputs/<run_id>/next_chapter_brief.json
outputs/<run_id>/next_chapter_draft.json
outputs/<run_id>/next_chapter_draft.md
outputs/<run_id>/draft_revision_pack.json
outputs/<run_id>/accepted_local_rewrites.json
outputs/<run_id>/next_chapter_draft_revised.md
outputs/<run_id>/edited_final_chapter.json
outputs/<run_id>/edited_final_chapter.md
outputs/<run_id>/continuous_reading_chapter.json
outputs/<run_id>/continuous_reading_chapter.md
outputs/<run_id>/confirmed_chapter_entry.json
outputs/<run_id>/confirmed_chapter.md
outputs/<run_id>/confirmed_chapter_reading_trail.json
```

聚合型只读 API 产物：

- `worldline_dossier`：聚合世界线状态、自演任务和检查点。
- `dossier_reading`：聚合连续阅读稿、确认稿、reading trail、多视角卷宗和世界线 dossier。
- `readable_entry`：把自演结果页、检查点、角色个人卷、事件多视角和连续阅读串成醒来入口。

## 6. 核心 API

已落地的主线 API 包括：

```text
GET  /api/stories/<slug>/tianming
POST /api/stories/<slug>/tianming/generate
POST /api/stories/<slug>/tianming/confirm
POST /api/stories/<slug>/tianming/intervention-compile

POST /api/stories/<slug>/sandbox/run
GET  /api/sandbox-runs/<run_id>
GET  /api/stories/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective-memory

POST /api/stories/<slug>/narrative-compensation/run
POST /api/stories/<slug>/world-autopilot/run
GET  /api/world-autopilot-runs/<run_id>/readable-entry
GET  /api/world-autopilot-runs/<run_id>/checkpoints/<checkpoint_id>
GET  /api/stories/<slug>/worldlines/<worldline_id>/worldline-state
GET  /api/stories/<slug>/worldlines/<worldline_id>/dossier
GET  /api/stories/<slug>/worldlines/<worldline_id>/dossier-reading

POST /api/stories/<slug>/character-lens/generate
POST /api/stories/<slug>/author-adoption
POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-draft
POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-rewrites
POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-confirmation
```

仍可继续补强：

- `GET /api/stories/<slug>/events/<event_id>/perspectives`：读取既有事件多视角和证据链，而不是每次生成新 brief。
- `GET /api/stories/<slug>/character-lens/<character_id>`：读取某角色连续个人卷。
- 世界自演后台队列、长时运行守护和中断自动恢复。

## 7. 前端页面

当前已经具备：

- 世界沙盘页。
- 天命书页：首屏宪法封面前置生成草案、确认根天命、干预预编译和进入沙盘四步，并展示当前锚点、合约压力、吸引子/锚点统计和风险说明。
- 世界线档案页：首屏工作流中枢前置确认分支状态、查看代偿、回放最近变化和进入连续正文；无检查点时主行动为继续沙盘，有检查点时主行动切到回放最近检查点。
- 检查点回放页。
- 卷宗阅读页：默认连续阅读，卷首题签解释当前阅读卷、偏差/悬念、证据数和下一步行动；移动端先呈现正文卡，再呈现卷宗目录。
- 多视角活体小说页：首屏工作流中枢前置选择观察点、生成五类卷宗、阅读信息差和送入作者台，生成后可直接进入卷宗阅读、作者采纳台或回世界沙盘。
- 作者采纳台：首屏工作流中枢前置对照、入账、修订、入卷状态和下一步动作，并保留采纳、草稿、局部重写、编辑后定稿、确认入卷全链路。
- 世界内导览层 `WorldRunway`，在世界沙盘、卷宗阅读、世界线档案、检查点回放和作者采纳台统一呈现当前位置、理解路径和下一步行动。
- 世界沙盘页运行导览：把“投放事件 -> 观察角色 -> 进入阅读”的使用路径前置到首屏；空态聚焦运行台，出结果后引导到卷宗阅读、世界线档案和多视角卷。
- 世界锚定页启动卡与移动端保功能布局：天命书、世界沙盘和卷宗阅读在锚定首屏可见，窄屏不再隐藏视觉/审计/角色功能。

继续深化方向：

- `WorldWorkspaceShell`：统一世界内部卷宗壳。
- 世界正史卷 / 主锚点卷独立页面。
- 角色个人卷连续阅读页。
- 势力卷。
- 事件多视角详情页。
- 正文内证据锚点与误会图谱。
- 机制档案页，把旧工程面板收纳为支撑层。

## 8. S1-S9 后续验收

### S1：真实 LLM 多 Agent 策略博弈

验收重点：

- 每个角色有私有目标、主观信息差、风险判断和信任/怀疑变化。
- 多角色之间形成博弈，而不是各自生成说明。
- 欺骗、隐瞒、试探、临场改判、反抗或妥协能影响传播、采信、世界状态或章节素材。
- UI/API 能看见谁在算计谁、为什么、结果改变了什么。

### S2：长期主观记忆心理模型

验收重点：

- 记忆会改变下一轮行动。
- 角色知道与不知道的事实可区分。
- 误会、秘密、创伤、信任和怀疑可持续发酵。

### S3：动态天命书与锚点

验收重点：

- 天命书不是静态配置，而能解释锚点变化、因果债、候选承载者和世界线快照。
- L4/L5/AU 改写必须经过确认和审计。
- UI 首屏能让用户理解“天命书是世界宪法”，并直接完成生成、确认和进入沙盘。

### S4：干预可执行投放

验收重点：

- 干预进入角色决策和世界状态，而不是停在预检说明。
- 普通干预、前提改写、元叙事污染和 AU 有不同代价与分支策略。

### S5：觉醒、反抗和模因污染

验收重点：

- 角色可以因 L5 干预产生命痕和高维认知。
- 觉醒角色可以拒绝、假意服从、欺骗、保护他人或反向利用读者。
- 高维真相传播会影响其他角色的信念、关系和世界舆论。

### S6：代偿持续状态

验收重点：

- 因果债落到地点、资源、伤势、舆论、势力和环境。
- 代偿进入下一轮沙盘、自演检查点、多视角正文和下一章 brief。
- 锚点失稳时世界继续寻找承载者，而不是停止。

### S7：无人值守世界自演

验收重点：

- 用户可以睡前启动，醒来从结果页直接读懂发生了什么。
- 每个检查点说明大事件、谁记住了什么、世界状态为何改变。
- 失败或中断可以从最近检查点恢复。
- 世界线页首屏能说明当前分支是否可继续、因果债有多重、最近应回放检查点还是继续沙盘。

### S8：多视角正文与连续阅读

验收重点：

- 默认像读小说。
- 世界正史卷、主锚点卷、角色个人卷、势力卷和事件多视角存在认知差异。
- 证据链折叠展示，不打断阅读。
- 角色个人卷能跨事件持续阅读。
- UI 首屏能让用户理解“同一事件会分裂成不同角色立场”，并直接完成生成、阅读卷宗和送入作者采纳台。

### S9：作者采纳和定稿闭环

验收重点：

- 作者能把沙盘涌现剧情转成下一章 brief、草稿和确认入卷正文。
- Reviewer 给出片段级问题、修改意图、建议改写和影响范围。
- 采纳的局部重写能生成编辑后定稿，并反哺下一轮沙盘入口。
- UI 首屏能让作者判断当前处在对照、入账、修订还是入卷，并能直接执行下一步。
- 后续继续补整章风格润色和真实模型编辑器。

## 9. 完成标准

每个切片完成时，不只看工程件是否存在，还要回答：

```text
用户是否能真实感到角色被记忆驱动？
干预是否进入世界并留下后果？
世界状态是否持续变化？
角色是否可能反抗或曲解用户？
章节是否来自世界演化？
作者是否能把审稿意见转成可写材料？
```

如果答案不充分，记录为“第一版已闭环，但仍需深入”，不要宣布完整愿景完成。
