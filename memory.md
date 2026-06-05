# 未终章 - 项目记忆（跨会话）

> **用途**：供 Codex / Cursor / 多会话 Agent 快速恢复项目事实，避免重复劳动或把历史待办误判成当前任务。
> **维护约定**：本文件只保留“当前事实、路线、边界、入口索引”；完整历史变更日志已迁移到 `docs/project-changelog.md`。每次有意义的开发/设计/验收任务结束后，请把状态同步到本文对应章节，并将历史记录追加到变更日志文档末尾；每完成一个独立切片都必须即时追加 changelog，不等无人值守总收口再补。
> **最后更新**：2026-06-06（文档治理与入口纠偏）。当前事实：World Sandbox Loop / 世界沙盘改造 S1-S9 已有第一版可运行链路；最近几刀分别完成卷宗阅读页产品化、世界自演结果页可读入口、Reviewer 局部重写采纳和自动编辑后定稿。后续默认继续深化真实 LLM 多 Agent 策略、长正文/连续阅读质量、正文内证据锚点/误会图谱、更强真实语义 Reviewer 和整章风格润色，不回 provider、GraphRAG、检索评测、OpenAPI、发行或商业化主线。
> **文档治理口径**：本文件只写当前事实和真实未做项；完整历史见 `docs/project-changelog.md`，文档分类见 `docs/index.md`，已收口专项见 `docs/completed/README.md`。旧文档若和本文冲突，以本文为准。

2026-06-06 卷宗阅读页产品化已完成第一版：新增 `dossier_reading` service 与 `GET /api/stories/<slug>/worldlines/<worldline_id>/dossier-reading`，只读聚合同一世界线的 `continuous_reading_chapter`、`confirmed_chapter.md`、`confirmed_chapter_reading_trail`、S8 `character_lens_volumes` 和 `worldline_dossier`；前端新增 `DossierReadingPage` / `#/world/<slug>/worldlines/<worldline_id>/reading`，默认进入连续阅读正文态，可切换世界正史卷、主锚点卷、角色个人卷、事件多视角和确认正文，认知偏差可见，证据链默认折叠。该刀不新增持久 artifact，不破坏既有 API/artifact，不改 `run_scene` 默认行为；后续仍需正文内锚点跳转、独立角色/势力页、误会图谱和真实长文文风控制。

2026-06-06 世界自演结果页 -> 可读世界线入口已完成第一版：`autopilot_report.json` 新增 additive `readable_entry`，并新增 `GET /api/world-autopilot-runs/<run_id>/readable-entry`；检查点回放 API 同步返回同一入口。世界沙盘页的“昨夜世界演化报告”现在直接展示“醒来从这里读”，可跳最近关键检查点、角色个人卷、事件多视角和连续阅读，并在结果页解释为什么世界状态变了、谁记住了什么、哪条因果债在发酵；世界线档案页也可直接进入连续阅读/角色个人卷/事件多视角，卷宗阅读路由支持 `/reading/<tab>` 精准落卷。该刀不新增持久 artifact，不改旧字段，不往 `WorkspacePage` 继续堆面板；后续仍需正文内证据锚点、角色/势力独立页和误会图谱。

2026-06-06 Reviewer 局部重写 -> 作者采纳台 -> 编辑后定稿 -> 下一章入口链已收口第一版：`author_chapter_rewrite_application` service 与 `POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-rewrites` 支持作者在采纳台勾选 `draft_revision_pack.json` 中的片段级建议，生成 `accepted_local_rewrites.json` / `next_chapter_draft_revised.md`，并新增 `edited_final_chapter.json` / `edited_final_chapter.md`。`edited_final_chapter` 会把选中的建议应用为可确认正文，不再把审稿清单当正文；`next_chapter_draft.json` additive 记录已采纳局部改写、`chapter_text_with_accepted_rewrites` 和 `edited_final_chapter` 摘要。若作者确认入卷时未继续手改，`author_chapter_confirmation` 会自动读取 `edited_final_chapter.json`，并把 `edit_source=auto_reviewer_final`、已采纳改写 ids 和定稿 artifact 写入 `confirmed_chapter_entry.json`、`continuation_effect.next_sandbox_entry` 和 `worldline_state.confirmed_chapter_entry`。UI 仍保持古风纸面风格，局部建议展示原问题、修改意图、建议改写、影响范围和采纳方向；采纳后正文编辑框优先显示编辑后定稿。后续仍需真实长文文风、更强语义 Reviewer 和自动整章风格润色。

2026-06-06 文档治理收口：已扫描 `docs/` 根层、`docs/completed/`、论文/品牌/原型资产、根 README、`AGENTS.md`、`engine/README.md` 与 `engine/ui/README.md`。当前不批量移动历史文档，避免破坏既有链接；采用“入口事实层 -> 当前主线层 -> 路线/阶段层 -> 历史归档层 -> 支撑层索引 -> 研究/品牌/原型资产 -> 运行说明层”的分层口径。下一次开工应先读 `AGENTS.md`、本文、`docs/index.md`、世界沙盘 PRD、AI 对齐清单、迭代计划和 `engine/README.md`；`docs/completed/`、`project-changelog.md`、`docs/后续增强清单.md` 与 `docs/distribution-phase-plan.md` 只用于追溯或用户明确点名，不作为默认下一刀来源。

2026-06-06 第二层路线文档瘦身：`docs/living-novel-engine-iteration-plan.md` 已从历史阶段长表改为当前路线判断，只保留世界沙盘主线、已闭环等级、官方下一步、后置项、下一刀选择规则和验收命令；旧长版仍在 `docs/completed/living-novel-engine-iteration-plan-legacy-2026-06-01.md`。`docs/codex-handoff.md` 也已从支撑层长表收束为新窗口最小接力包，避免新会话被 Graph/provider/retrieval 历史清单带偏。

2026-06-06 支撑层清单瘦身：`docs/后续增强清单.md` 已从逐刀长待办改为“LNE 支撑层与后置增强索引”，只保留已收口分组、触发式增强规则、研究参考和追溯入口。它现在用于证明 provider、Graph、检索、OpenAPI、发行、商业化等能力已作为支撑层收口，或在用户明确点名时判断触发条件；不能从中挑选默认下一刀。

2026-06-06 主 PRD 瘦身：`docs/living-novel-engine-prd.md` 已从混有 v0.8/v0.9/v1.0 和 Graph/provider 长历史的综合长文，收束为当前产品 PRD；只保留定位、主体验、用户价值、已闭环、真实未做项、后置边界和验收口径。历史逐刀细节回指 `docs/project-changelog.md`、`docs/completed/README.md` 和 `docs/后续增强清单.md`。

---

## 1. 当前状态（先读）

| 项 | 当前事实 |
| --- | --- |
| 项目 | 未终章（Unfinale）；技术缩写、Python 包、CLI 与环境变量前缀仍沿用 LNE / `living_novel_engine`，核心代码在 `D:\AI\open-infinite\engine` |
| 北极星 | 文本输入 -> 世界锚定 -> 角色自主行动 -> 读者干预 -> 世界线分叉 -> 章节渲染 -> 可继续运行 |
| 当前完成度 | v0.7 短中篇产品化 MVP、v0.8 长篇底座 MVP、v0.9.0-alpha 长篇共创闭环、v0.9.1-v0.9.4 触发式增强、v1.0-beta 本地优先商业化边界、v1.0-local 本地模型配置与一键运行脚本均已收口；后续增强 Runtime Preflight 至 Graph Memory Provider Spike Manual Mock Adapter Review MVP 共四十五刀已收口；Retrieval Provider Real Connectivity MVP、Vector Retrieval Pipeline MVP、World Sandbox Loop v1-v8（Sandbox Round、Subjective Memory Chain、Tianming Book、Intervention Compiler、Narrative Compensation、World Autopilot、Character Lens Novel、Author Adoption Desk）已收口 |
| 产品入口边界 | 前端是产品入口，API 是能力层，CLI 是工程外壳；用户级功能必须优先通过 Web UI + API 完成，CLI 只服务开发者、本地服务启动、自动化验收、批处理和无人值守复跑 |
| 测试基线 | `cd engine && python -m pytest -q` -> `947 passed`；`cd engine/ui && pnpm run build` 通过 |
| 官方下一步 | **真实模型决策 + 长正文质量 + 更强 Reviewer**：S4 后半与 S5/S6/S7/S8/S9 已形成一条可继续运行的产品链路，新增 `worldline_state.json`、`consequence_state` 六域代偿、自演任务状态、检查点回放、因果债/觉醒停止条件、失败后检查点恢复、多视角正文、下一章 brief、正式下一章草稿、作者确认入卷、确认稿跨卷宗阅读链和 `draft_revision_pack.json` 局部修订包；采纳/部分采纳/另开分支已能生成 `writing_plan` 与 `feed_forward` 并影响章节生成或后续沙盘入口；世界线/检查点独立页已补第一版 dossier 与回放入口；S1 已新增显式 opt-in 的真实 LLM 逐角色决策建议，产出 `agent_decision_advisory.json` 并进入沙盘行动/主观记忆/UI；S8/S9 已新增 `continuous_reading_chapter.json` / `continuous_reading_chapter.md`，并已通过 `dossier-reading` API 与卷宗阅读页组织成默认小说阅读入口；Reviewer 局部重写已可由作者勾选、生成编辑后定稿并反哺确认入卷和下一轮入口；下一步优先加强多轮策略规划、长期关系/势力博弈、长正文文风质量、正文内锚点跳转/误会图谱、更强真实语义 Reviewer 和整章风格润色；不默认回到 provider/Graph/检索评测主线 |
| 当前主导航决策 | 一级按“世界书架”组织；进入某世界后使用“天命书、世界沙盘、世界正史卷、主锚点卷、角色个人卷、势力卷、事件多视角、世界线、检查点、作者采纳台”。“沙盘/阅读/干预/作者”是场景能力，不做一级工作区 |
| 支撑层边界 | GraphRAG/Zep、provider spike、真实向量检索、OpenAPI、发行、计费、对象存储、认证都已降为支撑层；除非用户明确要求，不继续扩展这些方向 |

### 1.0 闭环等级（避免下一轮被旧文档带偏）

| 等级 | 当前结论 | 还能继续深入的地方 |
| --- | --- | --- |
| 已闭环支撑层 | v0.7-v1.0-local、后续增强四十五刀、真实 retrieval provider 和 opt-in Vector Retrieval Pipeline 都有 service/API/UI/CLI 或文档证据、测试和变更记录；它们现在是支撑层，不是默认主线 | 只有用户明确要求时，再评估默认 hybrid vector、GraphRAG/Zep、发行安装包、云端队列、对象存储、认证或计费 |
| 世界沙盘 S1-S9 第一版闭环 | 《天命书》、沙盘轮次、主观记忆、干预投放、L5 觉醒/模因传播、因果债具象化、自演检查点、多视角正文、作者采纳、连续阅读和确认入卷已形成 additive 链路 | 多轮策略规划、长期关系/势力博弈、真实模型误判/欺骗的稳定性、代偿长期发酵仍需继续打磨 |
| 产品化阅读入口第一版 | `dossier-reading`、卷宗阅读页、世界自演 `readable_entry` 和世界线/检查点/角色/事件跳转已让用户能从结果页进入小说化阅读 | 正文内证据锚点、角色/势力独立页、误会图谱、长篇阅读节奏和跨章节回收仍需深入 |
| 作者采纳闭环第一版 | Reviewer 片段级建议可在作者采纳台勾选，写入 `accepted_local_rewrites.json`、`next_chapter_draft_revised.md` 与 `edited_final_chapter.json`，确认入卷可自动采用编辑后定稿并反哺下一轮入口 | 真实语义 Reviewer、自动整章风格润色和文风一致性仍需深化 |

判断“下一刀”时，先以本节和 `docs/unfinale-world-sandbox-remodel-prd.md` 为准；不要从旧变更日志或 Graph/provider 历史面板里直接捞待办。

注意：World Sandbox Loop 的“已收口”是第一版产品链路闭环口径，证明 service/API/UI/artifact/tests 与小样本真实 LLM smoke 能把世界沙盘、觉醒传播、自演、连续阅读、作者采纳、局部重写和编辑后定稿串起来；但这不等于完整愿景已经完成。真实高智商多 Agent 决策、长期心理记忆、L5 觉醒反抗、代偿持续驱动、无人值守自演体验、多视角长正文、真实语义 Reviewer 和整章文风润色仍是后续深化方向。

后续迭代纪律：工程实现可以继续小步安全推进，但产品完成标准不能再停在“最小切片闭环”。一次 S1-S9 切片只有在用户能真实感到对应能力成立时才算通过，例如角色决策真的被记忆改变、干预真的进入下一轮沙盘、代偿压力真的持续影响世界状态、采纳真的反哺下一章 brief。`有 API / 有测试 / 有页面 / 有 artifact` 只能算底线，不等于产品能力完成。当前正在进行的 S1-S9 先不打断；等该轮完成后，下一轮复盘和第三轮迭代必须按这个口径验收。真实模型/API 可在用户明确允许时作为 opt-in smoke 或 LLM runner 联调使用，但默认 pytest 仍应保留 deterministic/mockable 基线，避免外网与额度依赖污染常规验证。

真实模型验收口径：用户已明确允许在本项目测试中调用其真实接入的模型 API。后续涉及叙事生成、Agent 决策、章节 brief、多视角正文、Reviewer 或视觉生成质量的切片，不能只用 mock/deterministic 测试宣布体验合格；应在常规 mock 回归之外，使用 `.env` 中已配置的真实 `LLM_API_KEY` / `SEEDREAM_API_KEY` 做小样本 smoke，并记录真实输出质量、失败原因和是否回退。单元测试仍应 mock-safe、可复现；真实 API smoke 是产品验收补充，不打印明文 key，不做大规模消耗，不把真实外网调用塞进默认全量 pytest。

远程同步纪律：后续 AI 完成一个独立切片并通过对应验证后，不能只停在本地工作树；应提交并推送到远程仓库，除非用户明确说暂不提交/暂不推送。推送前必须先检查 `git status`，只提交本轮自己负责的文件；如果工作树混有用户或另一轮 AI 的未完成改动，不能把脏状态混推，应先隔离提交范围、说明阻塞或等待当前长任务收口。没有远程、无上游分支、认证失败或网络失败时，要在收尾里明确说明未推送原因和下一步。

### 1.1 当前纠偏主线（最高优先级）

当前项目不是要继续证明 provider、检索、Graph Memory 或商业化边界，而是要把已完成的底座重新拉回最初愿望：

```text
小说不是一本写完的静态文本，
而是一个会运行、能被观察、可被干预、会分叉、角色可能反抗的故事世界。
```

后续所有开发默认服务这七件事：

```text
世界会运行。
角色会自主。
角色会记得。
干预有后果。
角色可能反抗。
世界会代偿。
章节来自世界演化。
```

首批改造目标：

```text
1. 沙盘轮次：sandbox_rounds.jsonl 已有第一版，记录每轮角色意图、行动、冲突、信息传播和世界状态 delta；API 为 `POST /api/stories/<slug>/sandbox/run`，前端入口为“世界书架 -> 世界沙盘”。
2. 主观记忆链：每个角色在每条世界线拥有独立 subjective_memory.jsonl；每轮后写入看到、做了、新认知、情绪/信任/异常感变化，并已扩展 perceived_event、inner_thought、inferred_motive、emotional_impact、trust_shift、anomaly_weight、secret_visibility、misbeliefs、unknown_canon_facts、L5 高维真相、命痕、模因传播来源、是否采信、可信度和反应类型等字段，下一轮行动和冲突会引用上一轮记忆/误会。
3. 《天命书》：tianming.json 已有第一版，并已加深为世界线宪法雏形；`narrative_attractors` 有权重/类别，`anchor_status.anchors` 支持角色/势力/谜团/地点多锚点，`contract_pressure.pressure_tiers` 支持轻微/重大/时代/世界崩坏四档；旧版已确认天命书再次读取或生成时会补齐 S3 字段，同时保留既有吸引子。
4. 干预编译器读天命书并可投放沙盘：自由干预可预编译为干预类型、层级、兼容性、转译策略、Divergent/AU、分支轴和因果债；普通干预不改写 `tianming.json`，L4/L5/AU 可写 `projects/<slug>/worldlines/<worldline_id>/tianming_snapshot.json` 且不覆盖根天命书；`POST /api/stories/<slug>/sandbox/run` 已可选接收干预文本并写 `intervention_constraint.json`，让编译结果成为本轮沙盘约束；新增 `projection_mode` / `intervention_projection_mode` 支持沉浸模式和暴走 AU，AK47 等异物会被标记为异物入侵并可选择本土化重释或保留为 AU 入侵。
5. 世界线代偿：可生成 `tianming_delta.json`，解释锚点稳定/转移/失锚、候选天命承载者、因果债扩散和世界内压力事件。
6. 世界自演：已支持运行到轮数、事件、时间、锚点变化、因果债爆发或角色觉醒，并生成 `autopilot_report.json` 与检查点；报告包含醒来时间线、停止证据和恢复入口，中途失败会记录最近检查点，任务可 resume 生成接续报告。
7. 多视角活体小说：已可把同一事件渲染为世界正史卷、主锚点卷、角色个人卷、势力卷和事件多视角，并写入 `character_lens_briefs.json`。
8. 作者采纳台：已可把沙盘涌现剧情采纳、部分采纳、另开分支或导出 brief，并写入 `author_adoption_ledger.jsonl`；采纳 run 会生成 `next_chapter_brief.json`，其中包含 `writing_plan` 与 `feed_forward`，把原大纲差异、沙盘涌现剧情、下一章可写方案、伏笔调整、Reviewer 建议和后续入口串起来；另开分支会创建作者分支 `worldline_state.json` 且不覆盖根正史。采纳 run 可继续生成 `next_chapter_draft.json`、`next_chapter_draft.md`、`draft_revision_pack.json`、`continuous_reading_chapter.json` 和 `continuous_reading_chapter.md`，作者采纳台会展示确认前 gate、局部改写建议、连续阅读稿、阅读流、下一章钩子和 S8 卷宗引用；作者可勾选 Reviewer 局部重写并生成 `accepted_local_rewrites.json` / `next_chapter_draft_revised.md` / `edited_final_chapter.json`，编辑后定稿会 additive 反哺 `next_chapter_draft.json` 与确认入口；作者可继续手改或直接确认入卷为 `confirmed_chapter_entry.json` / `confirmed_chapter.md`，同时生成 `confirmed_chapter_reading_trail.json`，把确认稿回读到世界正史卷、角色个人卷和事件多视角证据；确认结果会回写世界线状态、已采纳改写 ids、定稿 artifact 和后续沙盘入口。
```

本次纠偏新增入口文档：

- `docs/unfinale-world-sandbox-remodel-prd.md`：后续改造 PRD，写清现有代码如何接入新方向。
- `docs/unfinale-product-vision-correction-draft.md`：产品愿景纠偏草稿，记录《天命书》、干预编译、世界代偿、主观记忆、世界自演、多视角活体小说和 UI 原型。
- `docs/unfinale-ai-development-alignment-checklist.md`：后续 AI 开发对齐检查清单，用于开工前确认这一刀是否服务世界沙盘主线。
- `docs/image/README.md`：UI 原型参考图索引。

---

## 2. 必读入口与事实优先级

新会话或新任务如果涉及 LNE、`engine/`、版本路线、产品 UI、API、测试或文档，先读：

1. `memory.md`：当前事实、边界、测试基线、已知缺口。
2. `docs/index.md`：文档地图，先判断某文档是当前主线、历史归档、支撑层索引还是后置发行路径。
3. `docs/unfinale-world-sandbox-remodel-prd.md`：当前改造 PRD，说明如何把现有代码拉回世界沙盘主线。
4. `docs/unfinale-ai-development-alignment-checklist.md`：后续 AI 开工前自检，避免继续沿旧工程化方向跑偏。
5. `docs/living-novel-engine-iteration-plan.md`：版本路线与官方下一步。
6. `engine/README.md`：CLI/API/输出结构/验收命令。
7. 需要愿景/产品定位时读 `docs/unfinale-product-vision-correction-draft.md` 与 `docs/living-novel-engine-prd.md`。
8. 需要 UI 风格时读 `docs/completed/v0.7-product-web-app-ui-spec.md`。
9. 存在接力任务时再读 `docs/codex-handoff.md`。

事实优先级：`memory.md` > `docs/index.md` > 世界沙盘 PRD > AI 对齐清单 > 主迭代计划 > `engine/README.md` > 主 PRD > 聊天摘要。

完整历史变更日志见 `docs/project-changelog.md`；它是追溯材料，不是当前待办来源。

---

## 3. 阶段收口总览

> 本节是历史阶段与支撑能力索引，供确认“某能力是否已做过”。判断当前下一刀时优先看第 1 节闭环等级和第 6 节真实未做项，不要从本节长表重新派生路线。

### 已收口主阶段

- v0.1-v0.6：CLI 原型、导入、检索、世界线浏览、multi-agent runner 与 trace 可靠性。
- v0.7：产品级 Web App 九刀、Agent Interaction、Visual Asset Generation、Baseline & Canon Replay、Worldline Judge。
- v0.8：长篇导入、分层记忆、正史账本、混合检索、审计、ActDirector、Narrator diagnostics、Dynamic Action Registry、Emergence Mining、Entity Alias、Runtime Memory Consumption、Artifact Panel、Long Upload Productization。
- v0.9.0-alpha：长篇创作闭环，覆盖章节导出、续写、世界线选择、审计入口、closeout API/CLI/record、alpha ready 和 closeout report。
- v0.9.1：Provider & Cost Gateway Lite。
- v0.9.2：MasterSetting Workspace Lite。
- v0.9.3：Graph Memory Evaluation Spike。
- v0.9.4：Advanced Runner Evaluation Spike。
- v1.0-beta：本地优先商业化边界，从 Scope-A 到 Billing Adapter Boundary-X 均已收口。
- v1.0-local：Model Configuration UX 与 Local Run Scripts 已收口。
- 后续增强四十五刀已压缩为支撑层能力组：运行前体检与投影健康、读者/作者质量诊断、Prompt Budget Pack、模型画像、设定卡片、本地 API contract、发行准备、检索失败样本采集/评估/导出/replay/migration、跨项目样本索引、检索趋势快照、GraphRAG/Zep/Temporal Memory 触发证据、shadow/case/provider 边界、离线 replay、manual opt-in 审批包、mock-compatible adapter 和 manual mock adapter review。完整逐刀细节只在 `docs/project-changelog.md` 与 `docs/后续增强清单.md` 追溯。
- Retrieval Provider Real Connectivity MVP 已按用户明确要求收口：百炼 `text-embedding-v3`、Zilliz Cloud、百炼 `gte-rerank-v2` 具备脱敏配置摘要、mock/real smoke 和设置页只读状态。
- Vector Retrieval Pipeline MVP 已按用户明确要求收口：API/UI 可显式构建 Zilliz 索引并做百炼 embedding + Zilliz + 百炼 rerank 检索预览；运行时仍需 `LNE_RETRIEVAL_STRATEGY=hybrid_vector` opt-in，默认 BM25 不被替换。

### 当前自主迭代点

- 产品纠偏已完成；当前自主迭代点是 **World Sandbox Loop / 世界沙盘改造**，不是继续扩 provider、Graph Memory、真实向量检索评测或工程化面板。
- 已完成的真实 embedding、Zilliz、reranker、Graph/provider 证据链、OpenAPI、发行和商业化边界全部保留为支撑层；除非用户明确点名，不作为下一刀默认方向。
- 后续如继续，优先沿 `docs/unfinale-world-sandbox-remodel-prd.md` 打磨 v1-v8 闭环：真实 LLM 决策、章节草稿质量、作者可编辑确认、角色个人卷连续阅读和事件多视角证据链。

---

## 4. 当前产品与工程能力

> 本节记录当前系统能力面，包含大量已降级为支撑层的工程能力。产品主线仍是世界沙盘体验；若只判断下一步，可直接跳到第 6 节。

### 创作闭环

- 可导入 txt/md/zip/epub，服务端 ingest session 支持分片、hash 校验、缺失分片查询、重复 chunk 幂等与 localStorage 恢复续传。
- 长篇导入会写 `source_raw/`、`import_report.json`、`memory/`、`canon_ledger.jsonl`、`consistency_report.json`。
- 世界锚定页展示导入检查、设定工作台、章节预览、分层记忆、正史账本、实体别名、检索命中、审计报告和下一步入口。
- 干预 run 会生成分支产物，并可进入评审、审计、设为起点、生成下一章、章节/合集导出。

### 运行与状态执行

- `run_scene` 默认行为不变。
- 干预 run 可生成 `runner_state_execution_report.json` dry-run 评估。
- 显式确认后，low-risk/executable/白名单 delta 可写入分支 `state_execution_overlay.json`，并生成 apply/rollback 报告。
- `state_snapshot.json` 不被覆盖；overlay 暂不自动驱动下一轮 runner 消费。

### 记忆、检索与审计

- `canon_ledger` 已进入 BM25 检索 artifact，source 为 `canon_ledger`。
- 正史 holdout 写入 `canon/visibility_manifest.json`，区分 `runtime_visible` / `holdout_private`。
- 干预、baseline 与 CLI resume 通过既有 `retrieved_context` 参数只读消费 memory/alias/ledger 安全子集，并写 `runtime_memory_context.json`。
- 前端“机制档案”只读展示运行记忆、动作计划、动作注册表、叙事诊断、涌现节点。
- 本地审计日志已覆盖版权声明、设定编辑、世界线选择、状态执行 apply/rollback、项目保留策略等关键写操作。

### 设置、本地运行与商业化边界

- 设置抽屉已包含脱敏 provider 状态、usage 汇总、手动价格估算、route matrix、模型配置状态、任务模型画像、本地 API 契约、发行准备和视觉密钥清除。
- `scripts/start-local.ps1` 与 `scripts/start-local.sh` 支持 clone 后检查/安装依赖并启动后端与 Vite 前端。
- 产品入口边界已固定：用户不应被要求复制或理解 CLI 命令；导入、配置、创作、干预、评审、导出、样本采集和 Graph Memory 证据查看等用户级能力都应优先有前端入口并调用同一套 API/service。CLI 只作为开发者、本地服务启动、自动化验收、批处理、JSON 输出和无人值守复跑的薄封装，不承载独立业务规则。
- 支撑层 UI/API 已收口为几类只读或显式 opt-in 能力：运行前体检、投影健康、读者评审、上下文预算包、任务模型画像、接口契约、发行准备、设定卡片、检索样本采集/评估/导出/replay/migration、跨项目样本索引、Graph/长期记忆触发与 mock opt-in 证据包。坏 ID 和缺失项目按 400/404 降级，坏 JSON/缺 artifact 以需留意或需修复展示，不白屏。
- 真实向量检索已具备显式项目工作台入口和 API：可构建 Zilliz 索引，可用百炼 embedding + Zilliz + 百炼 rerank 做检索预览；默认创作检索不被替换，只有 `LNE_RETRIEVAL_STRATEGY=hybrid_vector` 时运行时消费，失败回退 BM25。
- 支撑层 CLI 已覆盖检索样本、mock/replay/migration、跨项目索引、趋势快照和 Graph/长期记忆 opt-in 证据包，定位为无人值守或批处理外壳；普通用户入口仍优先 Web UI + API。
- v1.0-beta 只做本地优先商业化边界和只读/本地写入 artifact；不接真实认证、云端对象存储、队列、计费、不可篡改审计或发布系统。

---

## 5. 关键硬约束

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

---

## 6. 当前真实未做项（不要再把历史已完成项当缺口）

| 缺口 | 当前状态 | 下一步触发 |
| --- | --- | --- |
| 真实 LLM 多 Agent 策略仍需深化 | 已有显式 opt-in `llm_decision_mode=advisory`、`agent_decision_advisory.json`、`strategy_board` 和小样本真实 smoke；能看到采信、欺骗、传播、反抗和临场判断 | 需要多轮策略规划、长期关系/势力博弈、稳定误判/隐瞒/试探和更强世界影响时继续 |
| 长正文/连续阅读仍需打磨 | 已有 `continuous_reading_chapter` v2、`dossier-reading` API、卷宗阅读页、确认稿阅读链和世界自演可读入口；默认已像小说阅读而非 JSON 面板 | 需要正文内证据锚点、误会图谱、长篇节奏、跨章伏笔回收和真实文风一致性时继续 |
| Reviewer 整章风格润色仍未完成 | 已有语义 Reviewer、片段级问题、修改意图、建议改写、影响范围、作者勾选采纳、编辑后定稿和定稿自动确认入卷 | 需要从“应用局部建议成定稿”升级为“整章风格一致性润色、可回滚/对照和真实模型编辑器”时继续 |
| 世界线阅读入口仍可深化 | `readable_entry`、世界线页、检查点回放、角色个人卷和事件多视角跳转已能串起醒来阅读 | 需要独立角色/势力卷页面、正文内锚点跳转、跨卷证据联动和用户阅读进度时继续 |
| ChapterBrief 质量仍偏薄 | 导入时可用，但 summary/facts 仍偏规则化，未接真实 LLM 摘要 | 长篇质量明显受限时再做 |
| `contract_audit` 主链路仍偏静态 | 已有多种审计与商业化边界，但运行时 contract 仍未作为主链路强约束 | 出现合约越界误判/漏判时再补 |
| overlay 未自动喂回 runner | 状态执行 overlay 可 apply/rollback，但下一轮 runner 暂不自动消费 overlay | 用户确认需要连续状态演化时再做 |
| 运行后审计未写入正史账本 | Projection Health 可只读说明账本/审计投影状态，但审计日志与 canon ledger 分工仍分离 | 需要“审计结论影响正史”时再做 |
| Reader Panel / Adversarial Revision Lab 深化 | deterministic/mockable 读者面板与修订 brief 已有 | 需要自动改写、Elo 对比、voice fingerprint 或真实 LLM 语义评审时再做 |
| Prompt Budget Pack 深化 | 已有轻量只读预算包、去重、优先级排序和 UI | 需要把预算包真正接入 opt-in prompt 编排或做 reranker 时再做 |
| LLM Profile Assignment 深化 | 已有只读任务画像、温度、预算和降级策略 | 需要 opt-in 保存 profile、版本化或真实模型实验时再做 |
| Cards Workspace 深化 | 已有只读世界卡、角色卡、风格卡入口，世界卡轻编辑复用 MasterSetting 白名单 | 需要独立卡片 artifact、版本化、差异审计或批量编辑时再做 |
| OpenAPI / Typed Client 深化 | 已有只读 API contract、OpenAPI skeleton 与前端 typed client 映射 | 需要字段级 schema、自动生成 client 或外部集成契约时再做 |
| Bundled Release / Desktop Packaging 深化 | 已有只读发行准备清单；安装包、内置 runtime、桌面壳、签名和自动升级仍未做 | 用户本地试用稳定后再做 opt-in packager spike |
| Retrieval Sample Export Pack / Mock Evaluation Report | 已有失败样本工作台、CLI 追加/复跑入口、只读 Markdown/manifest 导出包、mock 对照报告、replay case report 和 migration pack；跨项目样本索引仍未做 | 需要把真实失败 query 跨项目汇总时再做 |
| 云端多用户持久队列/对象存储/认证/计费 | v1.0-beta 已定义边界，但刻意不接真实云端系统 | 外部用户试用或部署路径明确后再做 |
| 生产默认检索替换 / GraphRAG / Zep | 已有 BM25、ledger、alias、probe、Prompt Budget Pack、向量检索就绪探针、mock 样本评估、跨项目趋势快照、GraphRAG/Zep 证据链；已新增百炼 embedding、Zilliz Cloud、百炼 reranker 的显式配置、真实 smoke、Zilliz 写索引、混合检索预览和 opt-in runtime 消费 | 先用真实失败样本评估收益；收益明确后再决定是否默认启用 hybrid vector、接 GraphRAG/Zep 或扩展生产运维能力 |
| 高级 runner 框架 | 已有触发式评估，不默认接 LangGraph/OASIS/CAMEL | probe 证明现有 runner 到瓶颈时再做 |

已完成但历史上曾列为缺口的能力：视觉资产、长篇分层记忆、正史账本、长篇混合检索、长篇一致性审计、抽象干预编译层、Worldline Judge、涌现节点、叙事诊断、动态动作注册表、百万字上传入口、无干预 baseline、正史回放等，均不应再作为当前未做项重复安排。

---

## 7. 主要产物索引

| 类型 | 产物 |
| --- | --- |
| 基础 run | `chapter.md`、`events.json`、`state_snapshot.json`、`meta.json` |
| 分支与干预 | `intervention.json`、`causal_diff.json`、`intervention_compilation.json`、`worldline_judgement.json` |
| 多 Agent | `multi_agent_trace.json`、`generation_meta`、trace quality validator |
| 长篇导入 | `source_raw/`、`import_report.json`、`memory/`、`canon_ledger.jsonl`、`consistency_report.json` |
| 运行记忆 | `runtime_memory_context.json`、`retrieval_context.json` |
| 高级机制 | `act_director_plan.json`、`narrative_diagnostics.json`、`dynamic_action_registry.yaml`、`emergence_nodes.json` |
| 状态执行 | `runner_state_execution_report.json`、`state_execution_overlay.json`、apply/rollback report |
| 创作闭环 | `selected_worldline.json`、`creation_loop_alpha_closeout.json`、章节/合集导出与 share guard |
| 商业化本地边界 | `project_audit_log.jsonl`、`project_copyright_statement.json`、`project_retention_policy.json` |

---

## 8. API / CLI 状态索引

### 已有 API 类型

- 项目与导入：story genesis、文件上传、ingest session、project workspace、world anchor。
- 干预与世界线：run/intervene、causal diff、worldline judgement、worldline selection。
- 回放与审计：baseline、canon replay、replay range、replay audit、post-run audit、audit log 与 export。
- 创作闭环：resume continue job、chapter export、collection export、creation loop closeout。
- 运行前体检：runtime preflight 聚合 import review、master setting、canon ledger、entity aliases、retrieval probe、selected worldline、overlay、copyright、retention、audit log、provider status。
- 向量检索就绪：vector retrieval readiness 聚合导入规模、检索语料、BM25 probe、失败样本、别名覆盖和候选层状态。
- Embedding 样本评估：embedding evaluation samples 读取本地失败样本，对比 BM25 与 mock semantic oracle，区分词面缺口和记忆缺口；失败样本可从项目工作台安全追加。
- 投影健康：projection health 聚合 branch/project 关键投影 artifact 的 ready/attention/blocked 状态。
- 读者评审：reader panel 聚合 deterministic 读者人格、修订问题和 revision brief。
- 上下文预算包：prompt budget pack 对 retrieval_context 做去重、预算分配和 prompt block 压缩。
- API 契约：api contract 显式返回本地 HTTP 契约、OpenAPI skeleton、端点分组和前端 typed client 映射。
- 发行准备：packaging readiness 检查本地脚本、package、前端 dist、发行文档和后置打包目标。
- 设置与 provider：providers、provider usage、manual price estimate、route matrix、model configuration。
- 商业化边界：commercial scope/status、permission matrix、quota/observability、deployment readiness、cloud persistence、account project space、auth/object storage/quota/billing boundary 等。

### 常用 CLI / 验收

CLI 定位为工程/自动化工具：可用于本地服务启动、测试门禁、批处理复跑、JSON 导出和开发者验收；用户级流程不以 CLI 作为主入口。若新增能力涉及普通用户理解或操作，先做 Web UI + API，再视需要补 CLI 薄封装。

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

长篇闭环相关 CLI 以 `engine/README.md` 为准，例如 `lne creation-loop-closeout --write-report` 等。

检索失败样本 CLI：

```powershell
lne memory add-sample <slug> --query "..." --entity <entity_id> --reason "..." --chapter 2
lne memory samples <slug> --json --require-candidate
lne memory export-samples <slug> --json
lne memory mock-report <slug> --json --require-candidate
lne memory replay-report <slug> --json --require-clean
lne memory migration-pack <slug> --json
lne memory index-samples --json
```

---

## 9. 文档索引

| 文档 | 用途 |
| --- | --- |
| `AGENTS.md` | Agent 项目规则、硬约束、会话入口 |
| `memory.md` | 当前事实、边界、已知缺口、索引 |
| `docs/project-changelog.md` | 完整历史变更日志 |
| `docs/index.md` | docs 资料导航与推荐读取顺序 |
| `docs/codex-handoff.md` | 新 Codex 窗口接力包 |
| `docs/living-novel-engine-iteration-plan.md` | 主路线图 |
| `docs/productization-phase-map.md` | 阶段边界 |
| `docs/living-novel-engine-prd.md` | 主 PRD |
| `docs/distribution-phase-plan.md` | 后置发行路径 |
| `docs/completed/` | 已收口版本文档、PRD、Release Note、UI spec、工程协议 |
| `docs/article/` | 论文 PDF 与研读报告 |
| `docs/brand/`、`docs/image/` | 品牌资产与 UI 原型参考，不承担待办来源 |
| `engine/README.md`、`engine/ui/README.md` | 后端/API/artifact/验证与当前前端结构说明 |
| `Reference_projects/` | 参考开源项目，仅作设计参考 |

---

## 10. 参考项目与论文吸收边界

已吸收为路线语言的参考方向：

- Player-driven emergence：对应 `emergence_nodes`、分支差异、Worldline Judge。
- StoryVerse / Abstract Act / Act Director：对应 `AbstractIntervention`、compatibility、realization、`act_director_plan.json`。
- Human-Level Narratives / Story Arc / Turning Points：对应 `narrative_diagnostics.json` 与后续 narrator 反馈候选。
- STORY2GAME / Dynamic Action Generation：对应 `dynamic_action_registry.yaml` 与 alias/entity resolution。
- WenShape、webnovel-writer、MiroFish 等开源项目：只作架构与产品启发，不作为已引入依赖。

---

## 11. 决策备忘

- 本地优先：当前更重视单机可运行、可验证、可交付给用户试用，而不是过早云端平台化。
- 长篇路线：先用现有 BM25/ledger/alias/probe 与向量检索就绪探针把百万字底座跑通，再用失败样本和 mockable 对照评估决定是否接 vector/graph/rerank。
- Runner 路线：先保持 `SceneRunner` adapter 与当前 runner 安全边界，高级框架只在 probe 证明必要时引入。
- 商业化路线：v1.0-beta 只定义边界、审计口径和本地 artifact，不伪装成真实多租户 SaaS。
- 发行路线：本地脚本完成后暂停，等本地试用反馈，再决定 GitHub Release、内置 runtime 或服务器在线体验。

---

## 12. Agent 维护说明

- 先读当前章节，再读路线图；旧日志只用于追溯“为什么这么做”，不要把旧待办当当前事实。
- 做完有意义的开发/设计/验收任务后，同步三处：`memory.md` 当前状态、相关路线/README/PRD、`docs/project-changelog.md` 末尾历史记录。独立切片完成即记，不要把多刀合并成一次性补记。
- 不要改写历史变更日志；如历史条目过时，只在 `memory.md` 当前章节修正现状，必要时在新日志条目说明“状态已更新”。
- 若只做文档迁移，验证至少跑 `git diff --check`；若改代码，再按风险跑 pytest / UI build / HTTP smoke。

---

## 13. 历史变更日志索引

完整历史变更日志已迁移到 `docs/project-changelog.md`。本入口文档不再承载完整日志，只保留当前事实、路线、边界和索引，避免新会话启动时被历史过程拖慢。
