# Living Novel Engine — Phase 0

Phase 0 交付一个 **CLI 编排引擎**：内置原创样例世界，用户施加干预，系统生成 2-3 条世界线（JSON + Markdown），并支持沿选定世界线续章与再干预。

## 版本表

| 版本 | 能力 | 状态 |
|------|------|------|
| Phase 0 Alpha | `intervene` / `compare` / 内置样例《天荒城残夜》/ mock + LLM | 已收口 |
| Phase 0 Beta | 状态渲染、三分支钳制、玉简锁、章节兜底 | 已收口 |
| v0.1.1 | 快照 location、正史锁、墨青烟称谓、退魂铃来源 | 已收口 |
| v0.1.2 | `resume continue` → `linear/` 续章 | 已收口 |
| v0.1.3 | `resume intervene` → 续章上再三分叉 | 已收口 |
| v0.2 | 文本导入与世界锚定（PR-A + PR-B + PR-C） | 已收口 |
| v0.2 PR-A | `import-novel` + `validate-project` + `--force` 覆盖保护 | 已收口 |
| v0.2 PR-B | `load_story` + imported `intervene` + 天荒城规则隔离 | 已收口 |
| v0.2 PR-C | 真实 LLM 双 pass 抽取（world + character） | 已收口 |
| v0.2.1 | imported 项目 `resume continue` / `resume intervene` | 已收口 |
| v0.2.2 | 精华固化：genre_templates / facts.jsonl / summaries / story_contract | 已收口 |
| v0.4 | 只读世界线浏览器 `lne browse` | 已收口 |
| v0.4.1 | 边界加固：路径校验抽出、树排序稳定、前端不白屏 | 已收口 |
| v0.3.0 | Context Retrieval Lite：BM25 + 距离衰减 + prompt 注入 | 已收口 |
| v0.3.1 | 检索 artifact：`retrieval_context.json` + source_weight + VolumeBrief | 已收口 |
| v0.4.2 | browse 展示检索记忆（事实/摘要/合约命中）+ 阅读体验 polish | 已收口 |
| v0.5 | 第四面墙：干预记忆账本、角色觉察分数、分级表现注入 | 已收口 |
| v0.5.1 | 第四面墙关闭语义：`LNE_FOURTH_WALL=0` 不累积/不落盘/不泄漏 snapshot | 已收口 |
| v0.6.0 | Scene Runner Adapter：可插拔 `SceneRunner` + 注册表，默认 `lightweight` | 已收口 |
| v0.6.4 | `multi_agent_llm` runner：OpenAI-compatible 小模型推演 `MultiAgentTrace`（非默认、隐私加固、无 API 回退 stub） | 已收口 |
| v0.6.5 | 多 Agent 推演工程可靠性：generation_meta + trace 质量校验 + 有限重试 + token usage | 已收口 |
| v0.7.1-A | Intervention Compiler 最小闭环：自由输入 -> 结构化干预 + 动态分支轴 | 已收口 |
| v0.7.1-B | LLM Compiler：真实 LLM 编译 + fallback + 规则改写安全兜底 | 已收口 |
| v0.7.1-C | Causal Diff 后端数据：`causal_diff.json` 段落级 old/new diff | 已收口 |
| v0.7 | Product Web App：React/Vite 普通用户入口，Web 导入/创世/锚定/干预/Causal Diff/设置/异步 Job | 已收口 |
| v0.7.2 | Agent Interaction：CharacterAction / CharacterProbe / InterventionGuardrail | 已收口 |
| v0.7.3 | Visual Asset Generation：Seedream 5.0 Lite 封面/角色头像/场景图（增强层，可降级占位） | 已收口 |
| v0.7.4 | Baseline & Canon Replay：无干预基线 + 正史 holdout + deterministic 回放评估 | 已收口 |
| v0.7.5 | Worldline Judge：世界线评分、故事弧、转折点、anti-slop、emergence_score | 已收口 |
| v0.8.0-A | Long Novel Ingestion Report：`source_raw/`、`import_report.json`、`long_mode` | 已收口 |
| v0.8.1-A | Hierarchical Memory Skeleton：`memory/` 分层记忆骨架与 manifest | 已收口 |
| v0.8.2-A | Canon Ledger Skeleton：`memory/canon_ledger.jsonl` 统一正史账本 | 已收口 |
| v0.8.3-A | Canon Ledger Retrieval：账本进入 BM25 检索 artifact | 已收口 |
| v0.8.4-A | Static Consistency Audit：`memory/consistency_report.json` 导入级静态审计 | 已收口 |
| v0.8.5-A | Long Canon Replay Isolation：`runtime_visible` / `holdout_private` manifest | 已收口 |
| v0.8+ ActDirector-A | `act_director_plan.json`：抽象干预到角色动作计划 artifact | 已收口 |
| v0.8+ Discourse-aware Narrator-A | `narrative_diagnostics.json`：分支正文节奏/转折/张力诊断 | 已收口 |
| v0.8+ Dynamic Action Registry-A | `dynamic_action_registry.yaml`：从动作计划沉淀可复用动作别名注册表 | 已收口 |
| v0.8+ Emergence Mining-A | `emergence_nodes.json`：run 级涌现节点汇总与 API | 已收口 |
| v0.8.x Entity Aliases | `memory/entity_aliases.yaml`：实体别名骨架与检索归一化 | 已收口 |
| v0.8.x Runtime Memory Consumption-A | `runtime_memory_context.json`：运行时只读消费 memory/alias/ledger 安全子集 | 已收口 |
| v0.8.x Frontend Artifact Panel | 右侧「机制档案」统一展示运行记忆、动作计划、动作注册表、叙事诊断、涌现节点 | 已收口 |
| v0.8.x Long Upload Productization | txt/md/zip/epub 文件导入、浏览器端分片、job 进度与失败空态 | 已收口 |
| v0.8.6 | Long Import Review：导入报告细化、章节预览、导入质量空态、失败空态收束 | 已收口 |
| v0.8.7 | Resumable Ingest Jobs：服务端分片 session、断点续传/恢复、hash 校验 | 已收口 |
| v0.8.8 | Long Project Workspace：长篇项目详情页与项目资产展示 | 已收口 |
| v0.8.9 | Long Replay & Audit UI：长篇回放与一致性审计 UI | 已收口 |
| v0.8.10-A | Runner State Execution Spike：opt-in 状态执行 dry-run 评估 | 已收口 |
| v0.8.10-B | Runner State Execution MVP：最小 opt-in 状态写入与回滚 | 已收口 |
| v0.9.0-alpha | Long Novel Creation Loop：上传、记忆、分支运行、审计、选择世界线、导出 | 已整体收口，见 `../docs/completed/v0.9.0-alpha-long-creation-loop.md` |
| v0.9.1 | Provider & Cost Gateway Lite：多 provider 配置、模型路由、成本/用量估算、失败回退 | 进行中：provider 摘要、usage、设置展示、手动估算已收口 |
| v0.9.2 | MasterSetting Workspace Lite：项目级设定/人物/时间线/道具/伏笔/章节摘要工作台 | 待长篇项目页稳定后 |
| v0.9.3 | Graph Memory Evaluation Spike：评估 Zep / 图数据库 / GraphRAG 是否增强现有 ledger 检索 | 待 50+ 章或百万字召回不足时触发 |
| v0.9.4 | Advanced Runner Evaluation Spike：评估 LangGraph 局部 runner、OASIS/CAMEL 可选 runner | 待 v0.8.10 状态执行层不足时触发 |
| v1.0-beta | Commercial Hardening：账号、权限、云端持久化、配额、审计日志、版权提示、部署观测 | 待真实外部用户/团队长期使用 |

### 产品化阶段说明

完整口径见 `../docs/productization-phase-map.md`。当前判断如下：

| 阶段 | 归类 | 说明 |
|------|------|------|
| v0.1-v0.3 | 技术 MVP | CLI、导入、检索、续章等核心链路已成立 |
| v0.4-v0.6.5 | 研发/机制 MVP | 浏览器 viewer、第四面墙、runner、多 Agent 机制可审计可演示 |
| v0.7-v0.7.5 | 短中篇产品化 MVP | React Web App 把普通用户主闭环跑通 |
| v0.8.0-A-v0.8.5-A | 长篇引擎底座 MVP | 长篇 memory/canon/retrieval/audit/holdout 已落盘并可读取 |
| v0.8+ A-slices | 机制接缝与解释层 MVP | action、diagnostics、registry、emergence、aliases、runtime memory 已可解释，不默认强执行 |
| v0.8.6-v0.8.10 | 长篇产品化收束 | 把长篇底座做成上传、检查、管理、审计、回放、继续创作工作流 |
| v0.9.0-alpha | 长篇产品闭环 | 已整体收口：上传/创建 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出 -> closeout record |
| v0.9.1-v1.0-beta | 增强与商业化 | provider/cost、MasterSetting、图记忆/advanced runner 评估，以及商业级加固 |

**测试基线**：`pytest -q` → **626 passed**（2026-06-01，v0.9.1 Manual Price Estimate-D 后完整回归通过）；`engine/ui` 执行 `pnpm run build` 通过。

### Run 分支产物

除 `chapter.md` / `events.json` / `state_snapshot.json` / `summary.md` 外，imported 项目在检索时会额外写入：

```text
outputs/run_xxx/branch_a/retrieval_context.json
outputs/run_xxx/branch_a/runtime_memory_context.json
```

字段：`query`、`current_chapter`、`prompt_block`、`items[]`（含 `id`、`source`、`score`、`text`、`chapter`、`evidence`）。v0.8.3 起，`memory/canon_ledger.jsonl` 会以 `canon_ledger` source 进入同一 artifact，账本命中项额外带 `entities`、`ledger_type`、`confidence`。v0.8.x 起，`memory/entity_aliases.yaml` 会被 retrieval 读取并用于 query/doc alias expansion，命中项可 additive 带 `resolved_entities`。builtin 样例不写此文件。

`runtime_memory_context.json` 是 v0.8.x Runner Consumption-A 的只读审计 artifact：它记录本次生成实际注入的运行时记忆层（`consumed_layers`）、实体别名状态、归一化命中的实体、降级 warnings 与嵌套的 retrieval artifact。它通过既有 `retrieved_context` 参数进入角色 Agent 与 narrator，不改变 `run_scene` 默认行为；`entity_aliases.yaml` 缺失或损坏时只写 warning，不阻断生成。

v0.4.2 起，`lne browse` 在分支阅读器新增「检索记忆」标签页：按 `source`（合约 / 正史事实 / 章节摘要 / 卷摘要）分组展示本章生成引用的命中项与分数，世界线树的分支节点也会显示「检索 N」角标。v0.8.x 起，React 产品前端右侧解释面板新增「机制档案」标签页，统一只读展示 `runtime_memory_context.json`、`act_director_plan.json`、`dynamic_action_registry.yaml`、`narrative_diagnostics.json` 与 `emergence_nodes.json`；缺失或损坏 artifact 显示空态，不影响正文阅读。

v0.7.1-C 起，干预分支还会写入：

```text
outputs/run_xxx/branch_a/causal_diff.json
```

该文件保存段落级 `old_text` / `new_text` 因果差异块，以及 `status=proposed`、`lineage_type`、`diff_mode`、`affected_scope` 等字段，为 v0.7 产品前端的「时空 Diff / 确立 / 抹除 / 回滚」交互做数据预留。

v0.8+ ActDirector-A 起，每次干预 run 根目录还会写入：

```text
outputs/run_xxx/act_director_plan.json
```

该文件是 `InterventionCompilation -> CharacterActionPlan` 的 deterministic 规划 artifact，只用于审计和后续 runner 接入；当前不驱动 `run_scene`，不改变旧 `events.json` / `state_snapshot.json` / `chapter.md`。

v0.8+ Dynamic Action Registry-A 起，每次干预 run 根目录还会写入：

```text
outputs/run_xxx/dynamic_action_registry.yaml
```

该文件从 `act_director_plan.json` 汇总动作类型、中文别名、前置条件、效果、失败原因、修复建议、风险等级和来源 step；当前仅作审计/后续 runner 接入，不执行状态变化。

v0.8+ Emergence Mining-A 起，每次干预 run 根目录还会写入：

```text
outputs/run_xxx/emergence_nodes.json
```

该文件从 `intervention.json`、`intervention_compilation.json`、`dynamic_action_registry.yaml`、分支 `causal_diff.json`、`worldline_judgement.json`、`narrative_diagnostics.json` 中汇总候选涌现节点，字段含 `node_type`、`score`、`source_artifacts`、`status` 与 `recommendation`。API：`POST /api/runs/<run_id>/emergence-nodes` 重新挖掘，`GET /api/runs/<run_id>/emergence-nodes` 读取报告；当前不做社区推荐或模板市场。

v0.8.10-A Runner State Execution Spike 起，每次干预 run 可 opt-in 写入：

```text
outputs/run_xxx/runner_state_execution_report.json
```

该文件是状态执行层的 dry-run 评估报告，读取 `act_director_plan.json`、`dynamic_action_registry.yaml` 与 `emergence_nodes.json`，输出候选状态变化、gate 状态、阻断原因、warnings 与 MVP 前置清单。API：`POST /api/runs/<run_id>/state-execution-evaluate` 生成/覆盖评估，`GET /api/runs/<run_id>/state-execution-report` 读取报告；缺报告 404、损坏报告 400、缺必要 artifact 409。该报告不写 `state_snapshot.json`，不改 `run_scene` 默认行为，不自动应用 action/emergence 到真实状态。

v0.8.10-B Runner State Execution MVP 起，用户可显式确认后写入可回滚的状态覆盖层：

```text
outputs/run_xxx/runner_state_execution_apply_report.json
outputs/run_xxx/runner_state_execution_rollback_report.json
outputs/run_xxx/branch_a/state_execution_overlay.json
```

应用接口 `POST /api/runs/<run_id>/state-execution-apply` 要求 body 含 `{"confirm": true}`，只会应用 dry-run 报告中 `gate_status=executable`、`risk=low` 且字段在白名单内的 delta；不确认返回 400，缺评估报告 404，无可应用候选 409。回滚接口 `POST /api/runs/<run_id>/state-execution-rollback` 同样要求确认，会移除分支 overlay 并写 rollback 报告。该 MVP 仍不覆盖原 `state_snapshot.json`，而是用 `state_execution_overlay.json` 表达“下一层状态”，因此不破坏旧契约，也不改变 `run_scene` 默认行为。

v0.9.0-alpha Chapter Export 起，选中的世界线章节可通过只读导出接口生成 Markdown：

```text
GET /api/runs/<run_id>/branches/<branch_id>/chapter-export
```

返回 JSON 包含 `filename`、`content_type`、`content_md`、`share_guard` 与 `metadata`。导出内容会包含来源说明、AI 生成说明、版权与分享边界、世界线评审摘要和章节正文；服务不会写回 `chapter.md`，不会导出上传原作全文或 holdout 私有正文，也不改变 `run_scene` 默认行为。坏 id 返回 400，缺章节返回 404。前端阅读区提供「导出章节」按钮，下载前会用中文确认版权与分享边界。

v0.9.0-alpha Chapter Collection Export 起，当前分支可沿 `meta.parent_run_id` / `meta.parent_branch` 父链导出连续章节合集：

```text
GET /api/runs/<run_id>/branches/<branch_id>/chapter-collection-export
```

合集按父链顺序合并生成章节，包含来源说明、AI 生成说明、版权与分享边界、每节来源 run/branch 与安全截断 warning；它只读，不导出上传原作全文，不写 artifact。前端阅读区提供「导出合集」按钮，下载前会用同一份 `share_guard` 做中文确认。

v0.9.0-alpha Creation Loop Checklist 起，长篇项目工作台 API 会 additive 返回项目级创作闭环清单：

```text
GET /api/stories/<slug>/project-workspace
```

新增 `creation_loop` 字段包含 `recommended` 推荐世界线、`candidates` 候选分支、导入/分支/评审/审计/选择后审计/导出/版权边界 `checklist`、`completion` 完成度判定、阻塞项 `actions`、`closeout` alpha 收口报告和中文 `next_steps`。`closeout.remaining_blocker_ids` 提供稳定阻塞项 id，`remaining_blockers` 保留中文 label；`replay_audit` action 的 `requirements` 会说明一键范围回放缺少已选起点、baseline 或 holdout，builtin 样例无法录入 holdout 时标为 `blocked`。该字段只读扫描既有 run/branch artifact，不写新文件，也不改变 `run_scene` 默认行为。前端项目工作台新增「创作闭环」区，可打开推荐分支继续阅读或导出，展示 alpha 闭环完成度、审计前置条件，并对缺失评审、未选起点、未审计等阻塞项提供快捷动作。

直接验收 alpha 收口状态可调用：

```text
GET /api/stories/<slug>/creation-loop-closeout
```

返回 JSON 包含 `story_slug`、`version`、`completion_status`、`actions` 和 `closeout`。该接口复用项目工作台的只读判定，slug 走安全校验，非法 slug 返回 400；它不写 artifact、不执行动作，也不是发布按钮。`worldline_judgement` action 会携带 `story_slug` payload，`select_worldline` action 会携带 `run_id`、`branch_id`、`note` payload，范围回放 action 会携带既有 replay range payload。

不启动浏览器服务时，可用本地 CLI 做同一类收口验收：

```bash
lne creation-loop-closeout <slug>
lne creation-loop-closeout <slug> --json
lne creation-loop-closeout <slug> --require-ready
lne creation-loop-closeout <slug> --require-ready --write-report
```

`--json` 输出与 HTTP closeout 同构的 `story_slug/version/completion_status/actions/closeout`；`--require-ready` 在 `closeout.can_close_alpha=false` 时以退出码 1 失败。`--write-report` 只在 ready 时向导入项目写入 additive `creation_loop_alpha_closeout.json`，未 ready 不落盘；该报告用于记录本地 alpha 收口证据，不执行 action、不改变 `run_scene` 默认行为。

v0.9.0-alpha 收口后，`risk_level=low` 的静态审计 info 提示不会阻断 ready；中高风险静态审计、范围回放中高风险、缺失实体、缺评审、缺选择或缺导出仍会阻断 closeout。

前端还会显示 `creation_loop.recommended.continue_hint` 作为 CLI 续写入口，例如 `lne resume continue <run_id> --branch <branch_id> --mock`。v0.9.0-alpha Resume Continue HTTP Job 起，项目工作台也可通过显式按钮触发：

```text
POST /api/jobs/resume-continue
body: {"run_id": "...", "branch_id": "...", "mock": true}
```

该 job 会沿父 run/branch 生成新的 `linear` 子 run，返回 `run_id`、`branch_id`、父链信息与刷新后的世界线树。run/branch id 走安全校验，坏 id 返回 400；业务错误进入 job failed。生成仍走 `write_resume_output()`，不写 `intervention.json`，不改变 `run_scene` 默认行为。

v0.9.0-alpha Worldline Selection Persistence 起，项目工作台还可持久化“下一章起点”：

```text
GET  /api/stories/<slug>/selected-worldline
POST /api/stories/<slug>/selected-worldline
body: {"run_id": "...", "branch_id": "...", "note": "..."}
```

选择记录写入 `selected_worldline.json`（imported/genesis 项目写在项目目录，builtin 样例写在 outputs 的 story selection 区），并通过 `creation_loop.selected` 读回。它只标记用户选择，不驱动 runner、不改变推荐排序、不改既有 run artifact。

v0.9.0-alpha Post-run Audit Entry 起，`creation_loop.post_run_audit` 会围绕已选世界线聚合选择状态、世界线评审、Causal Diff、静态一致性审计和章节范围回放摘要，返回 `status`、`risk_level`、`missing_entities`、`next_actions` 与回放审计入口。该字段只读，不写入正史账本，不驱动 runner。

v0.8+ Discourse-aware Narrator-A 起，每个分支还会写入：

```text
outputs/run_xxx/branch_a/narrative_diagnostics.json
```

该文件统计正文长度、句段、对话标记、转折标记、pacing、tension curve，并给出写后 warnings/suggestions；当前只做诊断，不重写 narrator。

`GET /api/runs/<run_id>/branches/<branch_id>` 会 additive 返回这些解释性 artifact：`runtime_memory_context`、`act_director_plan`、`dynamic_action_registry`、`narrative_diagnostics`、`emergence_nodes`、`runner_state_execution_report`、`runner_state_execution_apply_report`、`runner_state_execution_rollback_report`、`state_execution_overlay`。这些字段仅供右侧解释层展示和显式操作；缺失返回 `null`，损坏 JSON 返回 `{}`、损坏 YAML 返回 `null`，前端保持空态，不改变 `chapter.md` / `events.json` / `state_snapshot.json` / `multi_agent_trace.json` / `causal_diff.json` 既有契约。

> 注意：`lne browse` 的旧浏览器仍保留为开发者/演示 viewer；面向普通用户的产品级前端已在 v0.7 落到 `engine/ui/`（React + Vite + TypeScript），负责导入、创世、锚定、干预、世界线浏览、设置与异步 Job。

### v0.5 第四面墙机制

多次/强烈/违背人设的干预会让角色逐渐察觉「外部力量」，并在正文中流露怀疑、追问、抗拒乃至反过来利用干预。

- **干预记忆账本** `fourth_wall.json`（写在每个 run 根目录）：记录每次干预痕迹（`InterventionTrace`）与各角色累积觉察（`CharacterAwareness`）。账本随世界线 lineage 累积：`resume continue` 透传、`resume intervene` 累加。
- **四类触发器**：`impossible_information`（低语/梦境等"不可能正常获知"的渠道）、`repeated_rescue`（同一角色被反复干预）、`personality_violation`（合约审计判定高抗拒或违规）、`fate_reversal`（强干预 / 高合约风险）。
- **五级觉察**：`none → unsettled → suspicious → aware → defiant`。分数钳制 [0,1]；场景/广域可见的干预会让在场旁观者也产生较弱觉察。
- **影响行为**：≥unsettled 注入角色决策 prompt；≥suspicious 放开 narrator「不要打破第四面墙」约束并按等级允许表现。`state_snapshot.json` 中各角色含 `fourth_wall_awareness` / `fourth_wall_level`，顶层含 `fourth_wall` 摘要。
- **可关闭**：设 `LNE_FOURTH_WALL=0`（或 `off`/`false`）**完全关闭**第四面墙——不累积干预、不写 `fourth_wall.json`、不向 snapshot 写入觉察字段、不注入决策/叙事。关闭期干预不计入未来 lineage；重新开启后沿父链继承关闭前的账本（`load_lineage_ledger`）。

```bash
# 软低语：觉察缓慢上升（unsettled）
lne intervene tianhuang-night --target lin_wan_zhou --content "今晚不要去城外竹林" --mock
# 续章透传账本，再施加强干预 → 觉察可升至 aware/defiant，正文出现角色对虚空的追问/反抗
lne resume continue <run_id> --branch branch_a --mock
lne resume intervene <continue_run_id> --branch linear --target lin_wan_zhou --content "她必须立刻离开" --mock
```

### v0.6.0 推演 Runner Adapter

把「单 prompt 多角色轮询」从硬编码实现抽象为可插拔组件，为后续多 Agent 推演留好接缝；默认行为与 v0.5 完全一致。

- `orchestrator/runners/`：`SceneRequest`（统一参数包）、`SceneRunner`（ABC）、注册表（`register_runner` / `get_runner` / `available_runners` / `dispatch_scene`）。
- 默认 runner `lightweight` 即原 `run_scene` 实现；`scene_runner.run_scene` 现为薄包装，构造 `SceneRequest` 后交注册表分发。
- 选择优先级：`run_scene(..., runner_name=...)` 显式参数 > 环境变量 `LNE_SCENE_RUNNER` > 默认 `lightweight`。
- **输出契约不变**：`SimulationResult` 仅 additive 增 `runner_name`，`events.json` 增 `"runner"` 字段，contract / retrieval / browser 既有读取不受影响。
- 新增 runner 只需实现 `SceneRunner.run(request) -> SimulationResult` 并 `register_runner(...)`，无需改任何调用方。

### v0.6.1 Multi-Agent Runner Protocol（协议骨架，未接入运行）

为未来多 Agent runner 定义「内部中间产物」协议，但 **不改变默认行为**：`lightweight` 仍是默认 runner，协议未进入 `dispatch_scene` 默认路径。

- `orchestrator/runners/protocol.py`（仅 pydantic）：`AgentIntent` / `PrivateKnowledge` / `Misunderstanding` / `DelayedAction` / `RelationshipSignal` / `AgentTurnPlan` / `MultiAgentTrace`。
- 支持角色计划、私下信息、误解、延迟行动（`due_round`）、关系传播。
- **硬规则**：私下信息 / 误解默认 `visibility=private` 且未 reveal；只有 `revealed=True` / `corrected=True` 才允许投影成公开事件（`revealable_knowledge()` / `correctable_misunderstandings()`）。
- 设计与投影路线详见 `docs/v0.6.1-multi-agent-runner-protocol.md`；v0.6.2 已由 `multi_agent_stub` runner 消费并映射回 `AcceptedEvent` / `StateDelta` / `state_snapshot`。

### v0.6.2 multi_agent_stub runner（协议→投影→契约）

第一个多 Agent 系 runner：用协议确定性地构造可解释 `MultiAgentTrace`，再投影回既有契约，最后复用 narrator 渲染章节。**非默认**，需显式选择。

```bash
# 经环境变量启用（默认仍是 lightweight）
LNE_SCENE_RUNNER=multi_agent_stub lne intervene tianhuang-night --target lin_wan_zhou --content "今晚不要去城外竹林" --mock
```

- `orchestrator/runners/projection.py`：`build_demo_trace`（构造 trace）+ `project_trace`（trace → `AcceptedEvent` / `StateDelta`）+ `apply_relationship_signals`。
- **投影硬规则**：仅 `visibility=public` 的意图、`revealed=True` 的私下信息、`corrected=True` 的误解、`due_round<=max_rounds` 的延迟行动才进公开事件；私有/未到期项只留在 trace。
- `believe` 种子下目标公开回应低语（reveal+correct）；其余种子低语**不泄漏**到 `events.json` 与正文。
- 输出 additive：`SimulationResult.multi_agent_trace`（dict）+ 分支目录写 `multi_agent_trace.json`；`lightweight` 恒为 `None` 且不写该文件，契约不变。

### v0.6.3 Agent 轨迹可视化（`lne browse`）

`lne browse` 新增「Agent 轨迹」标签页，读取分支目录下的 `multi_agent_trace.json` 并分组展示，便于调试/演示多 Agent 推演：

- 公开意图 / 私下意图、私下信息（`revealed` 标记）、误解（`corrected` 标记）、延迟行动（`executed` / `due_round`）、关系信号。
- 世界线树分支节点显示「轨迹 N」角标（N = 角色计划数）。
- 缺 trace 显示空态（仅 multi_agent 系 runner 产出；默认 `lightweight` 不写），损坏 JSON 优雅降级不抛异常。
- 后端 `get_branch` 返回 additive 字段 `multi_agent_trace`（缺失 `None`、损坏 `{}`），旧 API 不变。

### v0.6.4 multi_agent_llm runner（小模型推演）

把 v0.6.2 stub 的确定性 trace 升级为**真正的 LLM 推演**：通过 OpenAI-compatible API 让小模型一次性输出整场 `MultiAgentTrace`，再复用 v0.6.2 投影层与共享装配层产出 `SimulationResult`。**非默认**，不本地部署、不引依赖。

```bash
# 配置 .env：LLM_API_KEY / LLM_BASE_URL / LLM_MODEL_NAME（示例 DashScope qwen-plus）
LNE_SCENE_RUNNER=multi_agent_llm lne intervene tianhuang-night --target lin_wan_zhou --content "今晚不要去城外竹林"

# 无 API key 或加 --mock → 自动回退确定性 trace，仍产出可浏览的 multi_agent_trace.json
LNE_SCENE_RUNNER=multi_agent_llm lne intervene tianhuang-night --target lin_wan_zhou --content "今晚不要去城外竹林" --mock
```

- **共享装配层** `orchestrator/runners/assembly.py`：stub 与 llm runner 共用 `build_result_from_trace`，输出严格同构。
- **健壮回退**：mock / 无 API / LLM 异常 / 非法 JSON / 空 turn_plans → 回退确定性 `build_demo_trace`，不抛。
- **隐私加固**：未 reveal 私下信息、未 corrected 误解、暗算/隐瞒类公开意图强制非公开；模型乱标也不会泄漏到公开事件。
- 详见 `docs/v0.6.4-multi-agent-llm-runner.md`。

### v0.6.5 推演工程可靠性

在 `multi_agent_llm` 上补工程可靠性，不引入新框架/依赖：

- **generation_meta**：每次推演把 source（llm/fallback/stub）/ model_name / attempt_count / duration_ms / validation_status / validator_warnings / usage / cost_estimate 写进 `multi_agent_trace.json` 的 `generation_meta`（additive）。`lne browse`「Agent 轨迹」顶部「推演元数据」分组可区分真 LLM / 回退 / stub。
- **trace 质量校验** `trace_quality.validate_and_repair_trace`：空 turn_plans 硬失败触发重试/回退；就地修复回合号与可见性（私下信息不泄漏的第一道闸）；缺角色计划/干预未入私域记告警；绝不抛。
- **有限重试**：`LNE_MULTI_AGENT_MAX_RETRIES`（默认 1、上限 5），重试 prompt 带上一轮问题；耗尽回退确定性 trace。
- **token usage**：`LLMClient.chat_json_with_usage()` 回传 OpenAI usage（拿不到为 `null`），`chat`/`chat_json` 行为不变。
- 详见 `docs/v0.6.5-multi-agent-reliability.md`。

**验收参考 run**

| 版本 | run_id |
|------|--------|
| v0.1.2 | `run_20260528_155153_c3275c_continue_branch_a` |
| v0.1.3 | `run_20260528_171207_94a6b9_resume_intervene_linear` |

**完整能力链**

```text
lne intervene <sample>  →  branch_a | branch_b | branch_c
lne resume continue <run_id> --branch branch_a  →  linear/
lne resume intervene <continue_run_id> --branch linear  →  branch_a | branch_b | branch_c
```

`WenShape/` 与 `webnovel-writer/` 的可复用资产已吸收至 engine（genre_templates 等），外部源码目录已删除。详见 `docs/research/open-source-essence-absorption.md`。

## 安装

```bash
cd engine
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## 配置

```bash
copy .env.example .env
```

| 变量 | 说明 |
|------|------|
| `LLM_API_KEY` | OpenAI 兼容 API |
| `LLM_BASE_URL` / `LLM_MODEL_NAME` | 模型端点 |
| `LNE_MOCK=1` | 强制 mock |

**未配置 `LLM_API_KEY` 时，CLI 会自动启用 mock**，无需加 `--mock` 即可跑通端到端 demo。

### v0.9.1 Provider & Cost Gateway Lite（进行中）

第一刀已新增只读 provider/cost 摘要，不改变真实调用链：

- `GET /api/settings/providers`：返回 `version=v0.9.1-provider-cost-lite`、`routing`、`providers`、`cost_policy` 与 `warnings`。
- `GET /api/settings/provider-usage`：只读扫描 `intervention_compilation.json` 与 `multi_agent_trace.json` 的 `generation_meta.usage`，返回 token totals、by_provider、records、缺失 usage 计数和空成本估算；可用 `story_slug` 查询参数过滤，非法 slug 返回 400。
- `providers` 当前包含主文本模型（OpenAI-compatible）与 Seedream 视觉模型，字段只展示 `configured`、`active`、`masked_key`、`base_url`、`model`、`fallback` 和 usage 来源。
- `routing` 当前为 `single_provider`，未配置文本密钥或默认 mock 时走 `mock`；未配置/关闭视觉模型时走占位图。
- `cost_policy` 当前只声明从 `generation_meta.usage` 读取 token 用量；手动填写每千输入/输出单价后会估算费用；更复杂路由留给后续 v0.9.1 子刀。
- Web 设置抽屉新增「模型与用量状态」，展示 provider 启用状态、模型名、累计用量、输入/输出用量、缺失 usage 记录提示和 warning；保存设置或清除密钥后会刷新。
- Web 设置抽屉新增「成本估算」，手动填写每千输入/输出单价；不内置厂商价格。

这些接口不创建客户端、不打网络、不落盘，也不返回明文 Key 或环境变量名。

## 快速演示

```bash
lne list-samples
# slug: tianhuang-night  display_name: 天荒城残夜

lne show-sample tianhuang-night

# 无 API Key 也可运行（自动 mock）
lne intervene tianhuang-night ^
  --target lin_wan_zhou ^
  --type whisper ^
  --content "今晚不要去城外竹林，那是墨青烟设的局" ^
  --branches 3 ^
  --rounds 4

# 或显式 mock
lne intervene tianhuang-night --target lin_wan_zhou --content "..." --mock

lne compare outputs/run_YYYYMMDD_HHMMSS

# v0.1.2：沿分支续写一章（无新干预）
lne intervene tianhuang-night --target lin_wan_zhou --content "今晚不要去城外竹林" --mock
lne resume continue run_YYYYMMDD_HHMMSS --branch branch_a --mock
# 新 run 目录：run_*_continue_branch_a/ 含 meta.json、parent_chapter.md、linear/chapter.md

# v0.1.3：在续章 linear 上再干预三分叉
lne resume intervene run_YYYYMMDD_continue_branch_a ^
  --branch linear ^
  --target lin_fan ^
  --content "告诉林晚舟，她身后的影子来自乱葬岗" ^
  --mock
```

### v0.2 导入自己的小说

内置测试素材路径（无需自建 `chapters/`）：

```bash
# mock 导入（无需 API Key）
lne import-novel tests/fixtures/mini_novel/ --name my-story --mock
lne validate-project my-story
lne show-project my-story

# 在导入项目上干预（无天荒城样例污染）
lne intervene my-story --target zhao_xuan --content "今夜不要去归云斋" --mock

# v0.2.1：导入项目完整世界线链
lne resume continue <run_id> --branch branch_a --mock
lne resume intervene <continue_run_id> --branch linear --target shen_bing_yue --content "..." --mock

# 真实 LLM 抽取（需 engine/.env 中 LLM_API_KEY）
lne import-novel tests/fixtures/mini_novel/ --name my-story
```

自建章节目录：在 `engine/` 下创建 `chapters/`，每章一个 `.md` 或 `.txt`，再执行 `lne import-novel chapters/ --name <slug>`。已存在同名项目时需加 `--force`。

产物目录：`projects/<slug>/`（`world.yaml`、`characters.yaml`、`canon_chapter.md` 等）。v0.8.0 起导入会额外写入 `source_raw/` 与 `import_report.json`：前者保存规范化后的原文账本，后者记录章节数、总字数、前 20 章可体验范围、疑似乱码、重复章名与缺章编号。v0.8.6 起 `import_report.json` additive 升级为导入检查报告，新增 `source`、`chapter_stats`、章节 `preview`、`parsing_warnings`、`quality_risks`、`recommended_actions`；`get_story()` / `get_world_anchor()` 会返回 `import_review`，报告缺失或损坏时稳定降级为 missing/damaged 空态并尽量从 `source/` 章节生成预览。Web/job 导入可传 `long_mode: true` 以允许 10 章以上、最多 200 章的长篇底座导入；默认小闭环仍保持 3-10 章限制。v0.8.x 起 `/api/import-novel` 与 `/api/jobs/import-novel` 可 additive 传 `upload`：`filename/total_size/chunks[{index,data_b64}]`，后端支持 txt/md 合并文本拆章、zip 内 txt/md 章节、epub 内 html/xhtml 章节；v0.8.7 起新增 `/api/ingest-sessions` 系列接口，支持服务端分片 manifest、查询缺失分片、重复 chunk 幂等、sha256 校验和 complete 后复用既有 import job；导入页会用本地 session id 恢复缺失分片并显示 job 进度和失败空态。v0.8.1 起导入同时写入 `memory/` 分层记忆骨架：`memory_manifest.json`、`master_setting.yaml`、volume/chapter memory、character states、timeline、plot_threads 和 propagation debts。v0.8.2 起还会生成 `memory/canon_ledger.jsonl`，用统一字段记录章节事件、角色状态、关系与伏笔。v0.8.4 起还会生成 `memory/consistency_report.json`，先做导入级静态一致性审计。v0.8.5 起写入正史 holdout 时会生成 `canon/visibility_manifest.json`，把 `source/` 作为 `runtime_visible`，把 `holdout_private/` 明确标记为 evaluator-only。v0.8.x 起导入生成 `memory/entity_aliases.yaml`，作为角色/地点/势力/账本实体的 deterministic 别名骨架；运行干预、baseline 或 CLI resume 时会写分支 `runtime_memory_context.json`，审计本章实际消费的 memory/alias/ledger 安全子集。详见 [v0.2-import-novel-mvp.md](../docs/v0.2-import-novel-mvp.md)。

### 真实 LLM 验收（demo，非 pytest）

配置 `.env` 后去掉 `--mock`，检查：

- 三条世界线主题固定为：**相信干预** / **半信半疑调查** / **拒绝干预/反弹**
- `state_snapshot.json` 含角色位置/情绪、关系变化、伏笔状态、`next_chapter_hook`
- `chapter.md` 约 1500–2500 字（mock 含前情提要 + 第一章节选 + 第十二章节点 + 第十三章演示续写）

## 合约审计输出

`intervention.json` 内 `contract_audit` 字段：

- `allowed` — 是否允许注入
- `risk` — low / medium / high
- `violations` — 违反世界规则或合约项
- `repair_suggestions` — 修改建议
- `expected_character_resistance` — 预期角色抗拒程度

### v0.7.2 Agent Interaction（角色交互解释层）

吸收 eastworld / StoryVerse / STORY2GAME 的经验，给读者一个**只读、deterministic、不调用 LLM** 的解释层；不改变 `run_intervention` 主行为、不重构 runner、所有字段 additive。

- **InterventionGuardrail（干预护栏预检）** `POST /api/interventions/guardrail`
  - 入参：`story_slug`、`content`、可选 `target` / `intervention_type` / `visibility` / `strength`
  - 出参：`allowed` / `risk` / `intervention_type` / `categories[]`（genre/time_power/persona/world_rule/visibility/strength 六维）/ `violations` / `repair_suggestions` / `safer_alternative` / `explanation`
  - 定位：在 `contract_audit` 之前独立解释"世界为何抵抗这次干预，并给出更合理的方式"；规则改写型（AK47/系统/穿越者）`allowed=False` 并提示另开 Alternate Novel，不静默污染原世界线。
- **CharacterProbe（角色内心探针）** `GET /api/stories/<slug>/characters/<char_id>/probe`
  - 可选 query：`run_id` / `branch_id`（叠加 `state_snapshot.json` 的情绪与第四面墙觉察）、`intervention_text`（预测角色对该干预的反应）
  - 出参：`belief_summary` / `current_emotion` / `desires` / `fears` / `boundaries` / `known_information` / `unknown_information` / `fourth_wall_awareness` / `fourth_wall_level` / `likely_intervention_response` / `obedience_risk` / `resistance_level` / `explanation`
  - 用中文解释"角色为什么不会无条件服从用户"。故事/角色缺失 → 404；快照损坏不 500。
- **CharacterAction 结构化字段**：`models/events.py` 的 `CharacterAction` additive 增 `action_id` / `action_label` / `preconditions` / `effects` / `failure_reason` / `repair_suggestions` / `risk` / `visibility`，全部默认空值；第一版未强制接入 runner 主链路，旧构造与旧产物读取完全兼容。
- **Web UI**：世界锚定页角色卡「角色探针」折叠入口；干预输入区「预检干预」按钮；Agent 轨迹页结构化动作（前置/效果/失败/修正）只读展示，缺字段空态正常。
- **未做**（留后续版本）：`AbstractIntervention -> CharacterActionSequence` 实例化、runner 主链路重构、真实 LLM 探针、Baseline/Canon Replay（v0.7.4）、Worldline Judge（v0.7.5）、Long Novel Memory（v0.8）。

### v0.7.3 Visual Asset Generation（Seedream 视觉资产增强层）

视觉资产是**增强层**，不是核心文字运行时依赖：未配置 Key / 生成失败 / 关闭开关时，全程稳定降级为古风占位，**不阻塞导入、创世、干预、世界线浏览**。所有 artifact additive，不改 `run_scene` 与既有 chapter/events/state/trace/diff 契约。

- **artifact** `projects/<slug>/visual_assets.json`（`VisualAssets`：`version/story_slug/provider/status(none|partial|ready|failed)/cover/characters/scenes/worldline_nodes`，每个 `AssetEntry` 仅含 `asset_id/kind/prompt/status/path/created_at/error`，**不含二进制**）；图片落 `projects/<slug>/assets/`（含内置样例，避免污染 git 跟踪的 `samples/`）。
- **API**
  - `GET /api/stories/<slug>/visual-assets`：返回清单；缺 artifact / 损坏 → `status=none` 占位，不 404；坏 slug 400；缺故事 404。
  - `POST /api/stories/<slug>/visual-assets/generate`：入参 `kinds[]`（cover/characters/scenes）、`character_ids[]`、`force`、`mock`；默认 `force=false` 已 ready 不重复生成；`mock=true` 或无 Key → 占位条目、不打外网；Seedream 不可用时 200 + placeholder/failed，不阻塞。
  - `GET /api/stories/<slug>/assets/<rel>`：本地资产静态服务，路径安全校验（穿越 403、缺失 404）。
- **Seedream client**（`visual_assets/seedream_client.py`）：import 不读网络；无 `SEEDREAM_API_KEY` / `LNE_VISUAL_ASSETS=0` → `available=False`；网络/HTTP/格式异常一律捕获返回 `ok=False`；兼容解析 `b64_json` / `url`，无法识别 → failed；不在日志或响应泄漏 Key。
- **环境变量**：`SEEDREAM_API_KEY`、`SEEDREAM_BASE_URL`（默认 `https://ark.cn-beijing.volces.com`）、`SEEDREAM_MODEL`（默认 `seedream-5-0-lite`）、`SEEDREAM_PATH`（默认 `/api/v3/images/generations`，接口不确定时可覆盖）、`LNE_VISUAL_ASSETS=1/0`。
- **Web UI**：世界锚定页封面 + 「生成视觉资产 / 重新生成」、角色卡头像、书架故事卡封面缩略、设置抽屉 Seedream 区块；无图古风占位、加载失败回退、生成中状态反馈、布局稳定，中文文案。
- **未做**：真实线上批量队列；世界线节点缩略图真正绑定 run/branch 生成（仅预留 artifact 字段 + UI 占位）；图片版权/公开分享策略；真人/影视角色复刻（明确不做）。

**Seedream 真实联调 smoke checklist**（无外网时不要执行，CI/测试全走 fake/mock）：

1. `engine/.env` 填 `SEEDREAM_API_KEY`（及按需 `SEEDREAM_BASE_URL` / `SEEDREAM_MODEL` / `SEEDREAM_PATH`）。
2. `lne browse` 启动后端；前端 `pnpm run dev`。
3. 进入某 imported/genesis 项目世界锚定页，点「生成视觉资产」。
4. 观察 `projects/<slug>/visual_assets.json` 状态变 `ready`、`projects/<slug>/assets/` 落图；UI 显示真实封面/头像。
5. 若线上接口返回格式与默认解析不符（非 `data[0].b64_json` / `data[0].url`），条目变 `failed` 并保留占位；据实调整 `SEEDREAM_PATH` 或在 `_parse` 扩展兼容字段。

### v0.7.4 Baseline & Canon Replay（无干预基线 + 正史回放）

Baseline / Replay 是**评估层**，不是干预主链路依赖。全程不打 LLM、不改 `run_scene` 默认行为、不改既有 chapter/events/state/trace/diff 契约，新 artifact 全部 additive；所有失败降级为明确错误（400/404/409），不白屏、不 500。

- **Baseline Worldline**：角色在无高维干预下按现有世界状态/人设/伏笔压力自然推进一章，作为"干预世界线"的对照组。`build_baseline_spec()`（branch_id=`baseline`、branch_seed=`linear`）；`service/baseline.py` 支持「从故事锚定状态」与「从指定 run/branch 快照续」两种；`write_baseline_output` 写 `meta.json` + `baseline_report.json` + `baseline/`{chapter/events/state_snapshot/summary/baseline_meta}，**不写 `intervention.json` / `causal_diff.json`**。
  - `POST /api/stories/<slug>/baseline`：入参 `rounds`/`mock`/`runner_name`/`from_run_id`/`from_branch_id`；返回 `run_id`/`branch_id`/`story_slug`/`summary`/`report`/`tree`。坏 slug 400、缺故事 404、参数错误 400。
  - `GET /api/runs/<run_id>/baseline`：返回 `baseline_report.json`（不存在 404、损坏 400）。
- **Canon Holdout**：imported/genesis 项目可把完结小说后续章节录为隐藏评估集；builtin 只读。存 `projects/<slug>/canon/holdout/chapter_NNN.md` + `canon/holdout_manifest.json`，**文件名由章号派生，用户不可控制路径**。
  - `GET /api/stories/<slug>/canon/holdout`：返回 manifest + `chapter_count` + `available_chapters`（无 holdout → 空 manifest，不 404）。
  - `POST /api/stories/<slug>/canon/holdout`：入参 `chapters[{chapter,title,content}]`、`force`；builtin 400、同章已存在且 `force=false` 409、空内容/非法章号 400。
- **Canon Replay**：用无干预基线续写章节与某章 holdout 做 deterministic 评估，写 `outputs/<baseline_run_id>/canon_replay_report.json`。评分项（0–1）：`lexical_overlap`（字级 bigram Jaccard）、`entity_overlap`（角色/地点/势力命中）、`thread_overlap`（开放伏笔标题命中）、`length_ratio`、`state_consistency`（baseline 快照角色是否仍现身），加权 `overall`。**不打 LLM，holdout 文本只进 evaluator，不进角色/narrator/retrieval。**
  - `POST /api/stories/<slug>/canon/replay`：入参 `baseline_run_id`/`baseline_branch_id`/`holdout_chapter`；无 baseline run / 无 holdout 404、损坏 artifact 400。
  - `GET /api/runs/<run_id>/canon-replay`：返回报告（不存在 404、损坏 400）。
- **Web UI**：世界锚定页左栏「基线与正史回放」区块——holdout 状态（builtin 只读提示 / imported 录入）、生成无干预基线、章节下拉 + 运行正史回放、基线摘要（自然发展/角色状态/触及伏笔）、回放评分条（总分 + 5 分项 + 解释 + 缺失实体/伏笔 + 警告）；中文文案，强调"基线不是原作、回放仅本地评估、不代表复刻原作"。
- **输出目录根**：`writer._outputs_dir()` 与 `browser.paths.outputs_dir()` 现统一支持 `LNE_OUTPUTS_DIR`（默认仍为 `engine/outputs`）。
- **未做**：Long Novel Memory（v0.8）、LLM 语义评估、百万字 holdout、版权/公开分享策略、baseline↔intervention 并排偏离对比 UI。

### v0.7.5 Worldline Judge（世界线评审）

Worldline Judge 是**评估层**，不是生成层：读取既有 branch artifact，写出 branch 级 `worldline_judgement.json`，不打 LLM、不改 `run_scene` 默认行为、不改既有 chapter/events/state/trace/diff 契约，也不把评审结果写回正文或 state_snapshot。

- **artifact**：`outputs/<run_id>/<branch_id>/worldline_judgement.json`，字段包括 `recommendation`（推荐继续 / 谨慎继续 / 建议归档）、`scores`、`dimensions`、`story_arc_curve`、`turning_points`、`strengths`、`warnings`、`suggestions`、`interpretation`。
- **评分维度（0–1）**：`persona_consistency`、`contract_risk`（风险值，越低越好）、`branch_diversity`、`narrative_momentum`、`emotional_payoff`、`anti_slop`、`continuation_potential`、`emergence_score`、`story_arc`、`turning_points`、`tension`、`overall`。
- **API**
  - `POST /api/runs/<run_id>/branches/<branch_id>/worldline-judgement`：生成/覆盖该分支评审；body 可传 `story_slug`，缺省时从 `meta.json` / `intervention.json` / `baseline_report.json` 推断。坏 id 400、缺分支/正文 404、损坏 artifact 400。
  - `GET /api/runs/<run_id>/branches/<branch_id>/worldline-judgement`：读取报告；不存在 404、损坏 400。
- **Web UI**：工作台右侧新增「世界线评审」标签页，展示总分、推荐、故事弧、维度评分、优势/警告/建议/转折点；中文文案，强调本地 deterministic 评估、不改正文。
- **未做**：LLM 语义评审、run 级聚合评审、`compare.md` 汇总、`emergence_nodes.json` 持久化、discourse-aware narrator。

## 输出结构

```text
outputs/run_<timestamp>/
├── intervention.json      # 含 contract_audit
├── compare.md
├── branch_a/              # 相信干预
├── branch_b/              # 半信半疑调查
├── branch_c/              # 拒绝干预/反弹
│   ├── events.json
│   ├── summary.md
│   ├── chapter.md
│   ├── state_snapshot.json  # 完整状态快照
│   └── worldline_judgement.json  # v0.7.5 可选评审报告
```

### v0.4 世界线浏览器（只读）

在 `engine/` 目录下启动本地 Web UI，读取 `projects/` 与 `outputs/`：

```bash
lne browse
# 自定义端口：lne browse --port 9000 --no-open
```

界面能力：

- 左侧：故事列表与世界线树（`branch_a` / `branch_b` / `branch_c` / `linear` 及续章子 run）
- 中间：章节正文、分支摘要、`compare.md`
- 右侧：角色状态快照；导入项目的 `story_contract` / `facts` 摘要
- 底部：可复制 CLI 命令继续 `resume continue` / `resume intervene`

**read-only 保证**：浏览器仅读取 `projects/` 与 `outputs/`，不会修改任何引擎数据；
路径参数（run_id / branch_id / story_slug）强校验后再落盘查询，禁止路径穿越。
完整收口说明见 [v0.4-worldline-browser-release.md](../docs/v0.4-worldline-browser-release.md)。

## 测试

```bash
pytest -q
```

仅验证数据结构、状态机与三分支差异；**不要求** mock 模式下第十三章达到 1500 字。

样例 `samples/tianhuang-night/` 阅读顺序：`prologue.md`（前情）→ `canon_opening.md`（第一章）→ `canon_chapter.md`（第十二章·干预节点）。

### v0.1.2 续章 run 结构

```text
outputs/run_<ts>_continue_branch_a/
├── meta.json              # parent_run_id, parent_branch, lineage
├── parent_snapshot.json
├── parent_chapter.md
└── linear/
    ├── events.json
    ├── state_snapshot.json
    ├── chapter.md         # 第十四章
    └── summary.md
```

### v0.1.3 续章干预 run 结构

```text
outputs/run_<ts>_resume_intervene_linear/
├── meta.json              # kind=resume_intervene, lineage, branch_seed_lineage
├── parent_snapshot.json
├── parent_chapter.md
├── intervention.json
├── compare.md
├── branch_a/              # 第十五章 · 相信新干预
├── branch_b/
└── branch_c/
```

## Phase 1+ 衔接

| 阶段 | 接入 |
|------|------|
| v0.1.3 | 续章上再次干预（`resume intervene`）✓ |
| v0.2 | 文本导入 + imported intervene + LLM 抽取 ✓ |
| v0.2.1 | `resume` 支持 imported project ✓ |
| v0.3 | Context Retrieval Lite / 长篇检索增强（BM25 + 距离衰减 + Brief）✓ |
| v0.4 | 只读世界线浏览器 `lne browse` ✓ |
| v0.5 | 第四面墙：干预记忆、角色觉察、反抗命运 ✓ |
| v0.6.0 | Scene Runner Adapter（可插拔推演 seam）✓ |
| v0.6.1 | Multi-Agent Runner Protocol（协议 + 数据结构骨架，未接入运行）✓ |
| v0.6.2 | `multi_agent_stub` runner：协议→投影→契约，私有不泄漏（非默认）✓ |
| v0.6.3 | `multi_agent_trace` 可视化：browse「Agent 轨迹」标签页 ✓ |
| v0.6.4 | `multi_agent_llm`：OpenAI-compatible API 小模型推演，不本地部署 ✓ |
| v0.6.5 | 推演工程可靠性：generation_meta + trace 质量校验 + 有限重试 + token usage ✓ |
| v0.7.1-A/B/C | Intervention Compiler + LLM 编译 + Causal Diff 数据地基 ✓ |
| v0.7 | 产品级 React/Vite Web App（普通用户入口，见 `../docs/completed/v0.7-product-web-app-ui-spec.md`） |
| v0.8.6-v0.8.10 | 长篇导入报告、断点续传、项目页、回放审计 UI、runner 状态执行层评估与最小写入 |
| v0.9.0-alpha | 长篇共创闭环：上传 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出（已整体收口） |
| v0.9.1-v0.9.4 | provider/cost、MasterSetting Lite、Graph Memory spike、Advanced Runner spike（v0.9.1 进行中） |
| v1.0-beta | 商业化加固：账号、权限、云端持久化、配额、审计、版权、部署观测 |
