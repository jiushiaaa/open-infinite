# 未终章 - 变更日志

> 本文从仓库根目录 `memory.md` 迁移而来，用于保留完整历史记录；`memory.md` 只保留当前事实、路线、边界和入口索引。后续新增变更日志请追加到本文末尾。

## 13. 变更日志

### 2026-05-28 — v0.3.0 Context Retrieval Lite 收口

- **做了什么**：
  - 新建 `retrieval/`（BM25、decay、context_loader、retriever）
  - `StoryBundle.project_dir`；`run_scene` / `character_agent` / `narrator` 注入 `retrieved_context`
  - CLI 三处命令在 imported 项目上做检索
  - `writer.py` 扩展 ChapterBrief 字段 + `volume_001.yaml` 占位
  - 新增测试 29 个；更新 `living-novel-engine-iteration-plan.md`、`engine/README.md`
- **测试**：174 passed
- **文件**：`engine/src/living_novel_engine/retrieval/*`，`cli.py`，`scene_runner.py`，`character_agent.py`，`narrator.py`，`story_loader.py`，`import_novel/writer.py`，`tests/test_bm25.py`，`tests/test_context_retrieval.py`，`tests/test_retrieval_injection.py`
- **未做（记入 §6）**：检索 artifact 落盘、`source_weight`、分层检索、摘要内容质量
- **下一刀建议**：v0.3.1

### 2026-05-28 — 创建 memory.md

- **做了什么**：初始化本跨会话记忆文件，汇总 v0.1–v0.3.0 完成项、缺口与路线
- **下一刀建议**：v0.3.1

### 2026-05-28 — v0.3.1 封板小修：intervene 检索章节号

- **做了什么**：
  - `StoryBundle.intervention_chapter()` 从 `import_meta.json` 推导锚点章（anchor_index+1 → chapter_count → 1）
  - 初次 `intervene` 不再写死 `current_chapter=1`
  - PRD / iteration plan / memory 状态同步
- **测试**：183 passed（+1）
- **下一刀建议**：v0.4.2 browse 展示 retrieval_context.json

### 2026-05-29 — v0.4.2 browse 展示检索记忆 收口

- **做了什么**：
  - `indexer.get_branch` 返回 `retrieval`；`BranchSummary` 增 `has_retrieval` / `retrieval_count`，树分支节点带 `retrieval_count`
  - 前端 reader-toolbar 新增「检索记忆」标签页，`renderRetrieval` 按 source 分组展示命中（合约/事实/章节摘要/卷摘要 + 分数 + evidence）
  - 章节视图底部命中提示；世界线树「检索 N」角标；header → v0.4.2
  - 损坏/缺失 retrieval_context.json 优雅降级
- **测试**：188 passed（+5，`tests/test_browser_retrieval.py`）
- **文件**：`browser/indexer.py`、`browser/static/{app.js,index.html,style.css}`、`tests/test_browser_retrieval.py`、`engine/README.md`、`docs/living-novel-engine-iteration-plan.md`
- **下一刀建议**：v0.5 第四面墙（干预记忆、角色觉察、反抗命运）

### 2026-05-29 — v0.4.2 文档状态同步（PRD + iteration plan）

- **做了什么**：PRD 当前版本 → v0.4.2；主线 B 路线补 v0.4.2 已完成 + v0.5 下一步；8.7 触发条件表 v0.4.2 标为已完成
- **文件**：`docs/living-novel-engine-prd.md`、`docs/living-novel-engine-iteration-plan.md`
- **下一刀建议**：v0.5 第四面墙

### 2026-05-29 — 产品级前端排期补充

- **做了什么**：明确当前 `lne browse` 是开发者/演示 viewer，不是最终普通用户前端；新增 v0.7 Product Web App 路线
- **决策**：v0.5/v0.6 继续优先验证核心机制，v0.7 再新建 React + Vite + TypeScript `ui/`，把导入、干预、续章、世界线浏览做成可点击流程
- **文件**：`docs/living-novel-engine-iteration-plan.md`、`docs/living-novel-engine-prd.md`、`engine/README.md`、`memory.md`
- **下一刀建议**：仍然是 v0.5 第四面墙

### 2026-05-29 — v0.5 第四面墙机制收口

- **做了什么**：
  - 新建 `fourth_wall/`（`ledger.py` 账本+触发器+打分+持久化，`prompts.py` 分级提示）
  - 4 触发器 + 5 级觉察（none/unsettled/suspicious/aware/defiant），分数跨 lineage 累积、钳制 [0,1]、场景/广域弱外溢
  - 接入 `character_agent`（决策 prompt + mock 内心独白）、`narrator`（放开第四面墙约束 + mock 旁白）、`scene_runner`（透传 ledger）、`state_snapshot`（写各角色 awareness + 顶层 fourth_wall 段）
  - `writer.py` 写 run 级 `fourth_wall.json` + `load_run_ledger`；CLI 三命令累积/透传账本；`LNE_FOURTH_WALL` 开关
  - 端到端 mock 验证：软低语→unsettled(0.24)，续章透传后强重复干预→defiant(1.0)，正文出现「我知道你在看着」反抗旁白
- **测试**：205 passed（+17，`tests/test_fourth_wall.py`）
- **文件**：`fourth_wall/*`、`agents/{character_agent,narrator}.py`、`orchestrator/{scene_runner,state_snapshot}.py`、`output/writer.py`、`cli.py`、`tests/test_fourth_wall.py`
- **下一刀建议**：v0.6 Deep Simulation / MiroFish 多 Agent runner（先做 runner adapter）

### 2026-05-29 — v0.5.1 第四面墙关闭语义收口

- **做了什么**：
  - `LNE_FOURTH_WALL=0` 语义收紧：不累积、不传 ledger、`should_persist_ledger` 不写 `fourth_wall.json`、snapshot 无 fourth_wall 字段
  - `load_lineage_ledger` 沿父链继承关闭前账本，关闭期干预不计入未来
  - CLI 抽出 `_fw_prepare_intervention` / `_fw_load_for_resume` / `_fw_resume_intervene`
  - 修 iteration plan 过期缺口与「默认开启」口径
- **测试**：208 passed（+3）
- **文件**：`fourth_wall/ledger.py`、`output/writer.py`、`cli.py`、`scene_runner.py`、`state_snapshot.py`、`tests/test_fourth_wall.py`、文档
- **下一刀建议**：v0.6 runner adapter

### 2026-05-29 — v0.6.0 Scene Runner Adapter 收口

- **做了什么**：
  - 新建 `orchestrator/runners/`：`base.py`（`SceneRequest` + `SceneRunner` ABC + `RunnerError`）、`lightweight.py`（搬迁原 run_scene 实现 + helpers）、`__init__.py`（注册表 + `dispatch_scene` + env `LNE_SCENE_RUNNER`）
  - `scene_runner.run_scene` 改为薄包装：构造 `SceneRequest` → `dispatch_scene`；新增 `runner_name` 可选参数
  - `SimulationResult.runner_name`；`events.json` 加 `"runner"`（additive）
  - 选择优先级：显式参数 > env > 默认 lightweight；dispatcher 以 `runner.name` 权威标记结果
- **测试**：218 passed（+10，`tests/test_scene_runner_adapter.py`）；搬迁零回归
- **文件**：`orchestrator/runners/*`、`orchestrator/scene_runner.py`、`orchestrator/__init__.py`、`models/events.py`、`output/writer.py`、`tests/test_scene_runner_adapter.py`
- **下一刀建议**：v0.6.x 在 adapter 上实现真正多 Agent runner（先定 runner 内部协议：角色计划/私下信息/误解/延迟行动），保持 SimulationResult 契约

### 2026-05-29 — v0.6.1 Multi-Agent Runner Protocol（设计 + 骨架）

- **做了什么**：
  - 新建设计文档 `docs/v0.6.1-multi-agent-runner-protocol.md`：目标（角色计划/私下信息/误解/延迟行动/关系传播）+ 不做（不接外部服务/不引依赖/不改 outputs 旧格式/不接入默认 runner）+ 输出契约不变性约束 + v0.6.2 投影路线预告
  - 新建 `orchestrator/runners/protocol.py`（仅 pydantic，未接入运行）：`AgentIntent`/`PrivateKnowledge`/`Misunderstanding`/`DelayedAction`/`RelationshipSignal`/`AgentTurnPlan`/`MultiAgentTrace`
  - 硬规则落在协议上：私有/误解默认 private 且未 reveal；`revealable_knowledge()`/`correctable_misunderstandings()` 供 v0.6.2 投影过滤；`DelayedAction.due_round`+`is_due()`
  - 修文档漂移：`engine/README.md` 路线表 v0.3 → Context Retrieval Lite
- **测试**：227 passed（+9，`tests/test_multi_agent_protocol.py`：序列化往返 / due_round / 私有不泄漏 / 协议未接入默认 runner）；lightweight 零回归
- **文件**：`docs/v0.6.1-multi-agent-runner-protocol.md`、`engine/src/living_novel_engine/orchestrator/runners/protocol.py`、`engine/tests/test_multi_agent_protocol.py`、`engine/README.md`、文档
- **下一刀建议**：v0.6.2 写 `multi_agent_stub` runner，消费协议产出可解释 trace 并投影回 `SimulationResult`（私有/误解默认不进 events.json，仅 reveal/corrected 才公开）

### 2026-05-29 — v0.6.2 multi_agent_stub runner

- **做了什么**：
  - 新建 `orchestrator/runners/projection.py`：`build_demo_trace`（确定性构造可解释 `MultiAgentTrace`）+ `project_trace`（trace→`AcceptedEvent`/`StateDelta`，强制 reveal/corrected/due_round 规则）+ `apply_relationship_signals`
  - 新建 `orchestrator/runners/multi_agent_stub.py`：`MultiAgentStubRunner`，消费协议→投影→复用 `build_state_snapshot`+`render_chapter`→附 `multi_agent_trace`；纯结构化、不接 LLM/外部服务
  - `SimulationResult` 增 additive `multi_agent_trace: dict|None`；`writer._write_branch_outputs` 写 `multi_agent_trace.json`（仅当非空）
  - 注册为非默认 runner（`lightweight` 仍默认）；`believe` 种子公开回应低语，其余种子私下信息不泄漏到 events/正文
- **测试**：239 passed（+12，`tests/test_multi_agent_stub.py`：公开/私有投影、due_round、reveal、契约、artifact 落盘）；lightweight 零回归
- **文件**：`orchestrator/runners/{projection,multi_agent_stub}.py`、`orchestrator/runners/__init__.py`、`orchestrator/__init__.py`、`models/events.py`、`output/writer.py`、`tests/test_multi_agent_stub.py`、文档
- **下一刀建议**：v0.6.3 先把 `multi_agent_trace.json` 接入 browse 可视化；v0.6.4 再做自研 `multi_agent_llm`

### 2026-05-29 — v0.6.3 multi_agent_trace 可视化

- **做了什么**：
  - `browser/indexer.py`：`get_branch` 读分支 `multi_agent_trace.json`（缺失→None / 损坏→{}，不抛）；`BranchSummary` + 树分支节点增 `has_multi_agent_trace`/`multi_agent_trace_count`（additive）
  - 抽 `_read_optional_json`/`_list_len_in_json` helper，消除重复并把 `get_branch`/`_scan_branch` 复杂度压回阈值内
  - 前端「Agent 轨迹」标签页：分组展示 public/private 意图、私下信息（revealed）、误解（corrected）、延迟行动（executed/due_round）、关系信号；空态不白屏；树「轨迹 N」角标
  - 修文档漂移：README `multi_agent_stub` 示例补 `tianhuang-night` slug；协议文档「真正推理循环」→ v0.6.3+
- **测试**：245 passed（+6，`tests/test_browser_multi_agent_trace.py`：有/无 trace、损坏不抛、summary/tree 标记）；`node --check app.js` 通过
- **文件**：`browser/indexer.py`、`browser/static/{index.html,app.js,style.css}`、`tests/test_browser_multi_agent_trace.py`、`engine/README.md`、`docs/v0.6.1-multi-agent-runner-protocol.md`、文档
- **下一刀建议**：v0.6.4 自研 `multi_agent_llm` runner：通过 OpenAI-compatible API 调小模型输出 `MultiAgentTrace` JSON；不本地部署，不引入 Zep/OASIS/CAMEL；Zep/OASIS/CAMEL 放到 v0.8+ 按触发条件评估

### 2026-05-29 — 外部多 Agent / 记忆依赖取舍

- **MiroFish 源码观察**：LLM 主路径是 OpenAI SDK 兼容 API（`LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL_NAME`），示例推荐 DashScope `qwen-plus`，不要求本地部署；另有 `LLM_BOOST_*` 支持并行模拟加速。
- **Zep Cloud**：MiroFish 用它做图谱/记忆；LNE 当前已有 `world.yaml`、`characters.yaml`、`story_contract.yaml`、`facts.jsonl`、summaries、snapshots、retrieval、fourth_wall、multi_agent_trace 等叙事专用记忆层，短期不接 Zep。
- **OASIS / CAMEL**：适合 Twitter/Reddit 式群体环境与 `LLMAction()` / `env.step()`；LNE 是小说场景推演，先吸收 action loop / trace log 思想，不把它们变成主线依赖。
- **LangGraph 取舍**：MiroFish 主线不是 LangGraph；webnovel-writer 更像 Claude Code 写作流水线；WenShape 更像上下文工程 / 作者工作台。LNE 前期先用自研精简智能体协议（`SceneRunner` + `MultiAgentTrace` + `project_trace`），中后期如出现角色并行思考、裁判、审计、反思/重试、多轮共识等复杂状态流转，再局部引入 LangGraph 作为某个 runner 的内部实现。
- **路线**：v0.6.4 自研 `multi_agent_llm`（API 小模型，不本地部署）→ v0.6.5 并发/重试/成本/质量评估 → v0.9.3 / v0.9.4 再按“长篇记忆崩 / 群体仿真需求强 / 状态流转复杂化”评估 Zep / OASIS / CAMEL / LangGraph。

### 2026-05-29 — v0.6.4 multi_agent_llm 小模型推演 runner

- **做了什么**：
  - 抽出共享装配层 `orchestrator/runners/assembly.py`（`build_result_from_trace`：trace→`project_trace`→`apply_relationship_signals`→`build_state_snapshot`+`render_chapter`→`SimulationResult`），stub 与 llm runner 共用、输出严格同构；stub 重构为复用该层，行为不变
  - 新建 `orchestrator/runners/multi_agent_llm.py`：`MultiAgentLLMRunner`（非默认）；`generate_trace` 用 `LLMClient.chat_json` 让小模型一次性输出 `MultiAgentTrace`（OpenAI-compatible，不本地部署、不引依赖）
  - 健壮回退：mock/无 API/异常/非法 JSON/空 turn_plans → 确定性 `build_demo_trace`（不抛）；隐私加固 `_sanitize_trace`：未 reveal 私下信息、未 corrected 误解、暗算类公开意图强制非公开 + due_round 归一化 + 补齐 worldline_id/seed
  - 注册并导出 `MultiAgentLLMRunner`；设计文档 `docs/v0.6.4-multi-agent-llm-runner.md`
- **测试**：254 passed（+9，`tests/test_multi_agent_llm.py`：注册非默认 / mock 回退 / FakeLLM 真实路径 / 隐私加固不泄漏 / 契约 / 异常回退）；lightweight + stub 零回归
- **文件**：`orchestrator/runners/{assembly,multi_agent_llm,multi_agent_stub}.py`、`orchestrator/runners/__init__.py`、`orchestrator/__init__.py`、`tests/test_multi_agent_llm.py`、`docs/v0.6.4-multi-agent-llm-runner.md`、文档
- **下一刀建议**：v0.6.5 工程化——并发 / 重试 / 成本控制 / trace 质量评估与 fallback 策略；同一场景 ≥5 角色推演的稳定性

### 2026-05-29 — v0.6.5 多 Agent 推演工程可靠性

- **做了什么**：
  - 新建 `orchestrator/runners/meta.py`（`TraceMeta`）+ `trace_quality.py`（`validate_and_repair_trace`：硬失败/就地修复/告警，绝不抛）
  - `multi_agent_llm.generate_trace` 改返回 `(trace, TraceMeta)`：有限重试（`LNE_MULTI_AGENT_MAX_RETRIES` 默认 1）、validator 硬失败/异常重试带问题反馈、耗尽回退；记录 source/model/attempt/duration/usage/warnings
  - `LLMClient` 抽 `_complete()` 返回 `(content, usage)` + 新增 `chat_json_with_usage()`；`chat`/`chat_json` 行为不变；新增 `_extract_usage`
  - `assembly.build_result_from_trace` 接收 `generation_meta` 写进 `multi_agent_trace.generation_meta`；stub 也补 `source=stub`
  - 前端「Agent 轨迹」新增「推演元数据」分组（`renderTraceMeta`，彩色 source 徽标）
  - 设计文档 `docs/v0.6.5-multi-agent-reliability.md`
- **测试**：269 passed（+15：`tests/test_trace_quality.py` +9、`test_multi_agent_llm.py` 扩充、stub +1）；`node --check app.js` 通过；lightweight/stub 零回归
- **文件**：`orchestrator/runners/{meta,trace_quality,multi_agent_llm,multi_agent_stub,assembly}.py`、`llm/client.py`、`browser/static/app.js`、`tests/{test_trace_quality,test_multi_agent_llm,test_multi_agent_stub}.py`、`docs/v0.6.5-multi-agent-reliability.md`、文档
- **下一刀建议**：转向 v0.7 Product Web App（React/Vite 产品级前端，普通用户入口）；runner 侧暂不再深挖，接真实模型后若发现稳定性缺口再补

<!-- 以下由后续会话追加 -->

### 2026-05-29 — 开源项目与论文调研并入路线

- **做了什么**：
  - 将 WenShape / webnovel-writer / MiroFish / eastworld / autonovel / AI_NovelGenerator 的定位、可借鉴点和明确不做项写入项目记忆
  - 将四篇论文报告写入项目记忆：2404 用户驱动涌现、2405 StoryVerse 抽象意图、2407 叙事质量与故事弧、2505 STORY2GAME 动作可执行化
  - 当时更新官方路线：v0.7 Product Web App → v0.7.2 Agent Interaction → v0.7.5 Worldline Judge → v0.8+ 行动 / 叙事 / 涌现主线（现已完成 A-slices，下一步转入 v0.8.x 收束）
  - 明确短期仍保持 LNE 自研 `SceneRunner` + `MultiAgentTrace` 路线，外部项目只吸收机制与设计，不把源码并入仓库
- **测试**：未运行，文档/记忆更新
- **文件**：`memory.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/article/reports/*.md`
- **下一刀建议**：v0.7 Product Web App；实现前先为 v0.7.2 / v0.7.5 的 `CharacterAction`、`AbstractIntervention`、`worldline_judgement.json` 预留 API 与数据结构兼容位

### 2026-05-29 — 干预编译器、Seedream 与创世模式路线补充

- **做了什么**：
  - 将“自由干预不等于固定三分支”写入路线：`believe/doubt/reject` 仅适用于信息型低语；强制行动、物品注入、规则改写应先转 `AbstractIntervention`，再生成动态 `BranchAxis`
  - 增加 `Divergent Worldline` 与 `Alternate Novel / AU Worldline` 区分：前者在原世界规则内偏离，后者改写题材、时代、战力或核心前提
  - 将 Seedream 5.0 Lite 视觉资产排入 v0.7.3：角色头像、故事封面、场景背景、世界线节点缩略图；请求地址 `https://ark.cn-beijing.volces.com`
  - 将三入口产品流写入 v0.7 / v0.7.4：导入小说、主题创世、内置样例；用户不上传小说也可输入主题/题材/主角/大概内容生成第一章和故事世界
  - 增加 `Baseline Worldline` 与 `Canon Replay Evaluation`：无高维干预时角色自然发展；完结文本可把后续章节作为 holdout，评估无干预续写是否接近原作
- **测试**：未运行，文档/记忆更新
- **文件**：`docs/living-novel-engine-iteration-plan.md`、`docs/living-novel-engine-prd.md`、`memory.md`
- **下一刀建议**：先让 Cursor 继续按 v0.7 Product Web App / v0.7.1 Intervention Compiler 做设计或实现；若还不急前端，则优先落 `AbstractIntervention` 数据结构和 `Baseline Worldline` CLI 原型

### 2026-05-29 — v0.8 Long Novel Memory 路线补充

- **做了什么**：
  - 将“百万字到数百万字长篇支撑”升级为 v0.8 主线，而不是泛泛的商业化增强
  - 明确不靠超长 prompt，而靠分片上传、异步导入、分层记忆、canon ledger、混合检索、一致性审计和隐藏评估集
  - 吸收参考项目机制：WenShape 的事实/摘要/章节绑定检索，webnovel-writer 的 contract/commit/projection，AI_NovelGenerator 的角色状态/全局摘要/一致性审校，autonovel 的分层设定和 propagation debts
  - 规划 v0.8.0-v0.8.5：Long Novel Ingestion、Hierarchical Memory、Canon Ledger、Hybrid Retrieval、Consistency Audit、Long Canon Replay Evaluation
- **测试**：未运行，文档/记忆更新
- **文件**：`docs/living-novel-engine-iteration-plan.md`、`docs/living-novel-engine-prd.md`、`memory.md`
- **下一刀建议**：继续把剩余产品/技术路线聊清楚；全部确认后再正式进入开发，优先从 v0.7.1 或 v0.8.0 中选择第一刀

### 2026-05-29 — v0.7 UI 交互原则与 Causal Diff 路线补充

- **做了什么**：
  - 明确 UI 不走纯赛博极客风：主体为古风 / 墨水屏 / 纸面阅读，高维系统感只在关键时刻克制出现
  - 将 `Causal Diff / 因果差异块` 写入 v0.7 核心交互：用户在正文局部施加干预后，展示“被抹去的旧现实”和“新凝聚的世界线”，并提供确立、抹除、回滚、查看因果差异
  - 将干预后角色状态增量、克制第四面墙高亮、Agent 轨迹 warning、剧情张力弧线写入 PRD 与迭代计划，并明确优先级
- **测试**：未运行，文档/记忆更新
- **文件**：`docs/living-novel-engine-iteration-plan.md`、`docs/living-novel-engine-prd.md`、`memory.md`
- **下一刀建议**：继续确认剩余产品交互；正式开发 v0.7 时优先实现 Causal Diff 与回滚心理安全感

### 2026-05-29 — v0.7.1-A Intervention Compiler 最小闭环收口

- **做了什么**：
  - 新建 `intervention_compiler/` 模块：`models.py`（`AbstractIntervention`/`Compatibility`/`Realization`/`BranchAxisItem`/`AffectedScope`/`InterventionCompilation`）、`classifier.py`（四类干预关键词分类，规则改写优先级最高）、`branch_axes.py`（各类型本次专属分支轴模板）、`compiler.py`（mock/规则版 `compile_intervention`：分类→AbstractIntervention→兼容性→落地→动态轴→lineage_type→affected_scope，绝不接真实 LLM）
  - 四类干预产出不同 `branch_axis`：信息型=相信/怀疑/拒绝，强制行动=主动改道/被迫延迟/抗拒命运压力/干预失败但觉察异常，资源注入=合理吸收/降级转译/拒绝/开启异设，规则改写=拒绝/转译/另开 Alternate Novel
  - 规则改写（系统/AK47/穿越者）默认 `lineage_type=alternate_novel`、`compatibility=incompatible/high`、`realization.in_world=False`，并扫描 `world.rules` 标记冲突（天荒城“禁止未声明设定”规则命中）
  - `worldline_brancher.build_branch_specs_from_compilation`：动态轴映射到稳定 branch_a/b/c，`branch_seed=stance` 驱动既有 runner，保持 CLI/browse/测试兼容；空轴回退固定三分支
  - `output/writer` 增 `compilation` 可选参数，写 `intervention_compilation.json`（None 时不写，向后兼容）；`cli intervene` / `resume intervene` 接入 compiler、打印理解结果与分支轴、落盘 artifact
- **测试**：290 passed（+21，`tests/test_intervention_compiler.py`：分类/四类轴/lineage/兼容性/affected_scope/spec 映射/artifact 落盘+向后兼容）；既有 269 零回归；CLI 端到端 mock 验证 AK47 用例
- **文件**：`intervention_compiler/{__init__,models,classifier,branch_axes,compiler}.py`、`orchestrator/worldline_brancher.py`、`output/writer.py`、`cli.py`、`tests/test_intervention_compiler.py`
- **下一刀建议**：v0.7.1-B（compiler 接真实 LLM + 更细 compatibility reason + AU story_contract 差异）；之后 v0.7.1-C Causal Diff 数据预留，再开 v0.7 Web App

### 2026-05-29 — v0.7.1-B Intervention Compiler LLM 增强收口

- **做了什么**：
  - 新建 `intervention_compiler/llm_compiler.py`：`compile_intervention_with_llm()`（不改 v0.7.1-A `compile_intervention()` 接口）+ `LLMCompilationDraft` schema；复用 `LLMClient.chat_json_with_usage`，不引新依赖
  - 系统 prompt 要求 LLM 把 compatibility.reasons 归类到 6 维冲突（题材/时代/战力/人设/资源/信息可见性），contract_conflicts 引用 world.rules + character boundaries
  - **稳定回退**：`llm=None` / mock / 不可用 → rule-based（source=rule_based）；调用异常/非法 JSON/必填字段缺失 → rule-based（source=fallback，记录 fallback_reason 进 notes + generation_meta）
  - **就地修复**：LLM 草稿稀疏（branch_axis 空、intent/desired_effect/affected_scope 缺省）→ 用 rule-based 结果补齐，source 仍 llm，notes 标注修复字段；stance 非法（非 believe/doubt/reject）按序归一
  - **rule_rewrite 安全兜底** `_reconcile_safety`：classifier 或 LLM 任一识别为 rule_rewrite，即强制 `intervention_type=rule_rewrite` + `lineage_type=alternate_novel` + `realization.in_world=False` + `compatibility=incompatible/high`，分支轴缺 reject/translate/alternate 则替换为 rule-based 安全轴；`generation_meta.reconciled=True`
  - 新建 `intervention_compiler/meta.py`（`CompilationMeta`，沿用 v0.6.5 `TraceMeta` 约定）；`InterventionCompilation` 增 `generation_meta` 字段、`source` 语义改 rule_based/llm/fallback、`compiler_version` → v0.7.1-B（均 additive，旧 artifact 兼容）
  - CLI `intervene` / `resume intervene` 改调 `compile_intervention_with_llm(..., llm=llm)`，`_report_compilation` 打印 `source=` 与回退/兜底提示
- **测试**：303 passed（+13，`tests/test_intervention_compiler_llm.py`：LLM 成功+meta、finer reasons、非法 JSON 回退、必填缺失回退、无 API/None 回退、稀疏修复、AK47/系统/穿越者安全兜底、draft schema、rule-based 仍工作）；既有 290 零回归；CLI mock 端到端验证 source=rule_based + generation_meta 落盘
- **文件**：`intervention_compiler/{llm_compiler,meta,compiler,models,__init__}.py`、`cli.py`、`tests/test_intervention_compiler_llm.py`
- **下一刀建议**：v0.7.1-C Causal Diff 后端数据预留（affected_scope 已有，补 old_text/new_text 局部 diff 与确立/抹除/回滚数据位）；之后再开 v0.7 Product Web App。可选：AU story_contract 差异显式落盘

### 2026-05-29 — v0.7.1-C Causal Diff 后端数据预留收口

- **做了什么**：
  - 新建 `causal_diff/` 模块：`models.py`（`CausalDiffArtifact`/`CausalDiffBlock`/`DiffAnchor`/`DiffStatus`=proposed/accepted/rejected/reverted/`DiffOp`/`DiffMode`，含 accepted_at/rejected_at/reverted_from/parent_diff_id 生命周期预留）、`builder.py`（stdlib `difflib.SequenceMatcher` 段落级 diff，**不接 LLM、不改正文**）
  - `build_causal_diff`：old_text 存在→replace/insert/delete 块（带 anchor.chapter/old_index/new_index）；old_text 缺失→稳定空结构（blocks=[] + reason），结构永远稳定；`diff_mode` 按 lineage 选 local_divergence / broad_rewrite / alternate_novel_seed；intervention_summary 摘要 type/compatibility/realization/branch_axis/lineage_type；affected_scope 直接取自 compilation
  - `output/writer`：`_write_branch_outputs` 增 `old_text`/`compilation` 参数，仅 compilation 非空时写 `branch/causal_diff.json`（new_text=最终 chapter_text）；`write_run_output` 增 `old_text`（CLI 传 `bundle.canon_chapter`），`write_resume_intervene_output` 用 `parent.chapter_text`；resume continue 无 compilation 不写（向后兼容）
  - `browser/indexer`：additive `has_causal_diff`/`causal_diff_count`（复用 `_list_len_in_json` 读 blocks）、`get_branch` 返回 `causal_diff`、树节点暴露同字段；缺失/损坏优雅降级
  - alternate_novel / rule_rewrite（AK47/系统/穿越者）标记 `diff_mode=alternate_novel_seed`，不伪装成普通局部修改
- **测试**：317 passed（+14，`tests/test_causal_diff.py`：builder 段落 diff / old_text 缺失稳定空结构 / alternate_novel_seed / 生命周期预留 / intervene 写盘 / 无 compilation 不写 / resume intervene 用 parent.chapter_text / browser additive + 损坏降级）；既有 303 零回归；CLI mock 端到端验证 causal_diff.json 落盘
- **文件**：`causal_diff/{__init__,models,builder}.py`、`output/writer.py`、`cli.py`、`browser/indexer.py`、`tests/test_causal_diff.py`
- **下一刀建议**：v0.7 Product Web App（React/Vite），把 `intervention_compilation.json` + `causal_diff.json` 接成「系统理解 / 本次分支轴 / 时空 Diff 块 / 确立·抹除·回滚」交互；accept/reject/revert 命令在该阶段实现。可选：AU story_contract 差异显式落盘

### 2026-05-29 — v0.7 Product Web App 第一刀（只读阅读工作台骨架）

- **做了什么**：
  - 新建独立前端工程 `engine/ui/`（React 18 + Vite 5 + TypeScript，仅依赖 react/react-dom，无 router/状态库）。打通**只读链路**：故事入口 → 阅读工作台 → 选择 run/branch → 展示 chapter / state / retrieval / agent trace / intervention_compilation / causal_diff。
  - **复用 `lne browse` 只读端点**（vite proxy 转发 `/api`→8765），不另起世界状态、不替换 browse。后端唯一改动：`indexer.get_run` additive 暴露 `intervention_compilation`（run 级 artifact）。
  - 三栏阅读工作台：左 `WorldlineTree`（run/branch 树，Δ/◇/❖ 角标 + AU 标记 + **动态分支 label**），中 `ChapterReader`（正文 / 时空 Diff 双标签 + 古风小说排版 + AU 提示条 + 干预输入抽屉占位），右 `RightPanel` 四标签（干预编译 / 状态 / 检索记忆 / Agent 轨迹）。
  - **Causal Diff 为核心展示**：`CausalDiffView` 渲染「被抹去的旧现实」（低饱和朱砂底+删除线）与「新凝聚的世界线」（低饱和玉绿底+轻量打字机），解释条（影响角色/地点/世系），操作区 `确立/抹除/回滚` 按钮 disabled 标「即将支持」（后端命令未接，不假装可写回）。
  - **branch_a/b/c 只是目录 ID**：`branchLabels.ts` 按 `STABLE_BRANCH_IDS` 顺序映射到 `intervention_compilation.branch_axis[i].label/outcome/lineage_type`；linear/旧 run 回退 events.theme，不绑「相信/怀疑/拒绝」。
  - 视觉：古风纸面设计令牌（宣纸暖白、墨黑、朱砂、玉青、低饱和金 + 极淡纸纹 + 宋体正文），克制系统感；强反馈动效可在顶栏切换且响应 `prefers-reduced-motion`。
  - 降级：缺 artifact = 「该分支尚未生成该资料」空态，不白屏；坏 JSON / 无后端连接 → 温和错误 + 重试；右栏标签各自处理缺失。
- **测试/验证**：后端 `317 passed` 零回归（additive get_run）；前端 `npm run build`（tsc -b typecheck + vite build）通过；直连后端端到端验证新版 intervene run → API 返回 `intervention_compilation`（动态 axis label：主动改道/被迫延迟/抗拒命运压力/干预失败但觉察异常）+ `causal_diff`（status=proposed, 2 blocks, local_divergence）+ state_snapshot。
- **文件**：`engine/ui/`（package.json/tsconfig*/vite.config.ts/index.html/README.md + `src/` 全套组件与样式）、`engine/src/living_novel_engine/browser/indexer.py`（get_run additive）。
- **边界（第一刀未做，留待下一刀）**：自由干预实际生成 `POST /api/interventions`（输入抽屉与按钮已占位）、accept/reject/revert 后端命令、世界锚定页完整实现、导入/创世入口、Seedream 视觉资产（v0.7.3）。
- **下一刀建议**：v0.7 第二刀——接 `POST /api/interventions` + `resume continue/intervene` 生成链路（同步或 job 轮询），让干预输入抽屉真正发起生成并实时展示 compilation→分支轴→Causal Diff；随后做世界锚定页与 accept/reject/revert。

### 2026-05-29 — v0.7 第二刀 Web 内自由干预生成链路

- **做了什么**：
  - 新建 `service/`（`service/intervene.py`）：把 `intervene_cmd` 核心流程抽成 **console-free** 的 `run_intervention(...)`（load_story→audit→compile(LLM/规则)→branch specs→retrieval→fourth wall→run_scene 每分支→write_run_output），返回 `InterventionServiceResult`（run_id/run_dir/branch_ids/compilation/llm_mock/...）；入参非法抛 `InterventionRequestError`。CLI 与 Web API **共用同一编排，不复制推演代码**。
  - `cli.intervene_cmd` 重构为调用 `run_intervention` 后仅做 console 报告；删除已无用的 `_fw_prepare_intervention`（resume 命令仍用其余 helper）。CLI 输出无测试断言，零回归。
  - `browser/server.py` 新增 **additive** `do_POST` → `POST /api/interventions`（不破坏 `lne browse` 只读 GET）：读 JSON（story_slug/target/content/mock/runner_name/intervention_type/branches/rounds），`story_slug` 过 `safe_id`，复用 `run_intervention`；`InterventionRequestError`→400、坏 JSON→400、其它→500；成功返回 `run_id/branch_ids/primary_branch/intervention_compilation/llm_mock/fallback_reason` + **刷新后的世界线树 tree**（前端免二次请求即可定位新分支）。`do_OPTIONS` 加 POST。
  - 前端 `api/client.ts` 抽 `parseOk` + 新增 `postJson`/`api.postIntervention`；`types.ts` 加 `InterventionRequest`/`InterventionResponse`。`InterventionComposer` 接真实请求：目标角色下拉（取自当前 `state_snapshot.characters`，缺失时手填）、loading 三阶段提示（编译干预/推演世界线/写入 Causal Diff，克制不刷屏）、成功后 `onGenerated`→`setSel(新 run, branch_a)` + `tree.reload()`、失败显示可读错误不白屏。`WorkspacePage` 提供 `extractCharacters` + `handleGenerated`。
  - 保持古风纸面风格；不做 accept/reject/revert，不做导入/创世。
- **测试/验证**：后端 `327 passed`（+10，`tests/test_web_intervention_api.py`：service mock 成功/缺 content/缺 target/未知 story/未知角色 + HTTP POST 成功（返回树含新 run）/缺 content 400/未知角色 400/坏 JSON 400/GET 只读不回归）；既有 317 零回归；前端 `pnpm run build`（tsc -b + vite build）通过；**live 端到端**：经 Vite proxy `POST /api/interventions` → 200，run_id + primary_branch=branch_a + 3 分支 + 刷新树（3 roots）+ 3 条动态分支轴。
- **文件**：`service/{__init__,intervene}.py`、`cli.py`（intervene_cmd 重构）、`browser/server.py`（do_POST）、`engine/ui/src/api/{client,types}.ts`、`engine/ui/src/components/{InterventionComposer.tsx,composer.css,WorkspacePage.tsx}`、`tests/test_web_intervention_api.py`。
- **下一刀建议**：v0.7 第三刀——accept/reject/revert（后端命令写回 causal_diff 状态 + Diff 操作按钮启用）；世界锚定页；导入/创世 Web 入口；可选 job 轮询/流式进度。

### 2026-05-29 — v0.7 第三刀 Causal Diff 确立/抹除/回滚

- **做了什么**：
  - `causal_diff/models.py`：`CausalDiffBlock` additive 增 `status: DiffStatus | None`（块级采纳状态，旧 artifact 读取兼容）。
  - 新建 `service/diff_actions.py`（console-free）：`apply_diff_action(outputs_dir, run_id, branch_id, action, block_id?)`。**读原始 dict 原地改键再 dump，保留全部旧字段**；accept→`status=accepted`+`accepted_at`、reject→`status=rejected`+`rejected_at`、revert→`status=reverted`+`reverted_from=diff_id`；传 `block_id` 时**只改该块 status、不动 artifact 级**。**不改 chapter.md/state_snapshot.json、不删 run、不做文本合并**。错误：`DiffActionError`（未知 action/block_id/坏 JSON→400）、`DiffNotFoundError`（缺文件→404）。
  - `browser/server.py` 新增 additive `POST /api/diffs/action`（`run_id`/`branch_id` 过 `safe_id`，`DiffNotFoundError`→404、`DiffActionError`→400），返回 `{causal_diff: 更新后 artifact}`；GET 只读链路不受影响。
  - 前端：`client.ts` 加 `postDiffAction`，`types.ts` 加 `DiffActionKind`/请求响应类型 + `CausalDiffBlock.status?`。`CausalDiffView` 操作区升级为**真实 artifact 级动作**（确立/抹除/回滚→accept/reject/revert），处理中按钮显示「处理中…」、成功后 `onChanged`→`branch.reload()` 刷新、状态 badge 随 status 变色（accepted 玉青 / rejected 朱砂 / reverted 靛蓝）、失败显示克制错误不白屏，并标注「仅记录世界线取舍，不改写正文」。移除每块的 disabled 占位按钮。`ChapterReader`/`WorkspacePage` 透传 `onBranchReload`。
- **测试/验证**：后端 `339 passed`（+12，`tests/test_causal_diff_actions.py`：service accept/reject/revert(指向 diff_id)/块级仅改/未知 block 400/坏 action 400/缺 diff 404 + HTTP accept 200 写回/缺 diff 404/坏 action 400/路径穿越 400/GET 不回归）；既有 327 零回归；前端 `pnpm run build` 通过；**live**：经后端 `POST /api/diffs/action` accept→status=accepted+accepted_at、revert→status=reverted+reverted_from=自身 diff_id。
- **文件**：`causal_diff/models.py`、`service/{__init__,diff_actions}.py`、`browser/server.py`、`engine/ui/src/api/{client,types}.ts`、`engine/ui/src/components/{CausalDiffBlock.tsx,causalDiff.css,ChapterReader.tsx,WorkspacePage.tsx}`、`tests/test_causal_diff_actions.py`。
- **小后续（不阻塞）**：diff action 的 `mock`/严格布尔解析、`rounds`/`mock` 移入前端设置；block 级写回目前仅 service 支持，UI 暂只做 artifact 级。
- **下一刀建议**：v0.7 第四刀——世界锚定页 或 导入/创世 Web 入口（择一先做，避免一次铺太散）；可选 job 轮询/流式进度。

### 2026-05-29 — v0.7 第四刀 World Anchor 世界锚定页

- **做了什么**：
  - 后端 `browser/indexer.py` 新增 `get_world_anchor(slug)`（+辅助 `_resolve_story_path`/`_anchor_characters`/`_anchor_open_threads`/`_anchor_summaries`）：projects 优先于同名 sample 定位故事，返回 `slug`/`source_kind`/`display_name`/`divergence_point`、`world`（display_name/source_type/canonical_place_name/worldline_policy/scene_description/current_chapter/rules/locations/factions/timeline）、`characters`（id/name/narrative_role/gender/present_in_scene/persona{traits,desires,fears,boundaries}/current_state{location,emotion,resources}/memory/relationships/address_rules）、`story_contract`（缺→null）、`open_threads`（缺→[]，回落 world.open_threads）、`summaries`（缺目录→[]）、`run_count`。**缺文件不抛 500**；imported 经 `intervention_chapter_from_project` 得 `current_chapter`，builtin 为 null。
  - `browser/server.py` 新增 additive `GET /api/stories/<slug>/anchor`（在通用 `/api/stories/<slug>` 路由**之前**匹配 `/anchor` 后缀，`safe_id` 过滤；缺故事经 `FileNotFoundError`→404、坏 slug→400）；不改既有 GET 契约。
  - 前端：`routing.ts` 加 `#/anchor/<slug>` 路由；`App.tsx`/`AppShell.tsx` 接入（顶栏 workspace↔anchor 互跳）；`StoryEntryPage` 故事卡底部加「进入阅读 / 世界锚定」双入口；`client.ts`+`types.ts` 加 `getWorldAnchor`/`WorldAnchor` 等类型。
  - 新建 `WorldAnchorPage.tsx`+`worldAnchor.css`：三栏古风纸面——左（故事摘要 facts / 此刻场景 / 世界合约占位 / 进入阅读）、中（世界规则 朱金边条 / 地点 / 势力 / 开放伏笔 / 章节摘要，缺即空态）、右（角色卡：人设边界用朱砂边条强调「为何不会无条件服从」+ 当前状态/性格/欲望/恐惧/持有）。各区块均带「编辑即将支持」占位，**不假装能保存**。
- **测试/验证**：后端 `346 passed`（+7，`tests/test_world_anchor.py`：indexer builtin 成功/imported（tmp 项目，current_chapter 由 anchor_idx+1 推得）/缺故事 FileNotFoundError + HTTP anchor builtin 200/缺故事 404/路径穿越 400/普通 GET 不回归）；既有 339 零回归；前端 `pnpm run build`（tsc -b + vite build）通过。HTTP 集成测试经 `start_browser_server` 真实命中 `do_GET`。
- **文件**：`browser/{indexer,server}.py`、`engine/ui/src/{routing.ts,App.tsx,api/{client,types}.ts}`、`engine/ui/src/components/{AppShell.tsx,StoryEntryPage.tsx,storyEntry.css,WorldAnchorPage.tsx,worldAnchor.css}`、`tests/test_world_anchor.py`。
- **边界**：未做文件上传 / 主题创世 / YAML 保存 / Seedream（均为占位）。
- **下一刀建议**：导入小说 Web 入口 或 主题创世 Web 入口（二者都会落到此锚定页做确认）；轻编辑→真实 YAML 保存可后续接。

### 2026-05-29 — v0.7 第五刀 导入小说 Web 入口

- **做了什么**：
  - 新建 `service/import_novel.py`（console-free）：`import_novel_from_payload(name, chapters[{filename,content}], genre, mock, force, projects_dir?)`。**复用现有流水线**——`_build_split_chapters` 由 payload 直接构造 `SplitChapter`（按 filename 排序、`_extract_title` 取标题，镜像目录导入，不复制拆分逻辑）→ `mock_extract`/`llm_extract`（无 API Key 自动退化 mock）→ `write_project`（传 `projects_dir` 落盘）→ `validate_project`（warnings/errors 并入返回）。章节数限 3–10。错误：`ImportRequestError`（坏 slug/章节越界/内容空→400）、`ProjectExistsError`（同名存在且 force=False→409）。返回 `story_slug`/`display_name`/`character_count`/`chapter_count`/`anchor_chapter_index`/`extraction_mode`/`warnings`。
  - `service/__init__.py` 导出上述符号。
  - `browser/server.py` 新增 additive `POST /api/import-novel`（`name` 过 `safe_id`，`projects_dir=indexer.projects_dir()`；`ProjectExistsError`→409、`ImportRequestError`→400、`TypeError/ValueError`→400），返回含 `anchor_hash=#/anchor/<slug>`；GET 契约不变。**writer 与 browser 的 projects_dir 同源**（均 `engine_root/projects`，都认 `LNE_PROJECTS_DIR`），故导入后 `/api/stories` 与 `/anchor` 立即可读。
  - 前端：`routing.ts` 加 `#/import`；`App.tsx` 接入；首页「导入小说」卡片**启用**（→ `#/import`）；`client.ts`+`types.ts` 加 `postImportNovel`/`ImportNovelRequest`/`ImportNovelResponse`。
  - 新建 `ImportNovelPage.tsx`+`importNovel.css`：项目名（slug 实时校验）、题材、mock（默认 on）、force（默认 off）开关、3–10 章动态文本框（增/删，首行作标题）；提交时五段克制进度（拆分/抽取世界/抽取角色/写入/校验）；成功 `navigate(#/anchor/<slug>)`；**409 显示「项目已存在」+「开启覆盖后重试」按钮**；错误内联不白屏。未做拖拽/multipart（粘贴文本即可）。
- **测试/验证**：后端 `357 passed`（+11，`tests/test_web_import_api.py`：service mock 成功/force=False 409/force=True 覆盖/<3 章 400/坏 slug 400/导入后 anchor 可读 + HTTP 导入 200/导入后 anchor+stories 立即可见/重复 409/<3 章 400/坏 slug 400）；既有 346 零回归；前端 `pnpm run build`（tsc -b + vite）通过；a11y label 关联告警已修。
- **文件**：`service/{__init__,import_novel}.py`、`browser/server.py`、`engine/ui/src/{routing.ts,App.tsx,api/{client,types}.ts}`、`engine/ui/src/components/{StoryEntryPage.tsx,ImportNovelPage.tsx,importNovel.css}`、`tests/test_web_import_api.py`。
- **边界**：未做主题创世 / Seedream / 真正 YAML 编辑保存 / 百万字上传（仍 v0.2 级 3–10 章小闭环）。
- **下一刀建议**：主题创世 Web 入口（生成首章+初始世界+角色，复用世界锚定确认）；或世界锚定轻编辑→YAML 保存（先补 YAML parse 健康检查/降级，防手改坏文件 500）。

### 2026-05-29 — v0.7 第六刀 主题创世 Web 入口

- **做了什么**：
  - 新建 `service/story_genesis.py`（console-free）：`generate_story(name, premise, genre, protagonist_hint, style_hint, mock, force, projects_dir?)`。用户不上传文本，只给题材/主题/主角/风格 → 生成初始世界+角色+第一章。**复用** `write_project`（anchor_chapter_index=0 单章）+ `validate_project`，项目结构与 import-novel 同构；额外写 `genesis_meta.json`（additive，不影响 import_meta.json/indexer）。`_mock_draft` **deterministic**（吸收 premise/protagonist/style，便于测试）；`_llm_draft` 复用 `LLMClient.chat_json_with_usage`（pydantic `_GenesisDraft` 结构化输出），无 key / mock=true / 异常时安全退化 mock。错误：`GenesisRequestError`（坏 slug/空 premise→400）、`GenesisProjectExistsError`（同名存在且 force=False→409）。world.source_type=`genesis`。
  - `service/__init__.py` 导出上述符号。
  - `browser/server.py` 新增 additive `POST /api/story-genesis`（`name` 过 `safe_id`，`projects_dir=indexer.projects_dir()`；409/400 映射），返回含 `generation_mode`/`anchor_hash=#/anchor/<slug>`；GET 契约不变。创世后 `/api/stories` 与 `/anchor` 立即可读。
  - 前端：`routing.ts` 加 `#/genesis`；`App.tsx` 接入；首页「主题创世」卡片**启用**；`client.ts`+`types.ts` 加 `postStoryGenesis`/`StoryGenesisRequest`/`StoryGenesisResponse`。
  - 新建 `GenesisPage.tsx`+`genesis.css`（古风纸面，朱砂强调区别于导入页玉青）：项目名（slug 实时校验）、主题（必填 textarea）、题材、主角提示、文风偏好（可空）、mock（默认 on）/force（默认 off）；提交时五段克制进度（构思世界/生成人物/写入首章/生成合约/校验锚定）；成功 `navigate(#/anchor/<slug>)`；409 显示「项目已存在」+「开启覆盖后重试」；错误内联不白屏。
- **测试/验证**：后端 `368 passed`（+11，`tests/test_web_story_genesis_api.py`：service mock 成功（结构同构+genesis_meta）/deterministic 首章一致/force=False 409/force 覆盖/坏 slug 400/空 premise 400/创世后 anchor 可读 + HTTP 创世 200 且 anchor 可读/重复 409/空 premise 400/坏 slug 400）；既有 357 零回归；前端 `pnpm run build`（tsc -b + vite）通过；新文件 lint 干净。
- **文件**：`service/{__init__,story_genesis}.py`、`browser/server.py`、`engine/ui/src/{routing.ts,App.tsx,api/{client,types}.ts}`、`engine/ui/src/components/{StoryEntryPage.tsx,GenesisPage.tsx,genesis.css}`、`tests/test_web_story_genesis_api.py`。
- **边界**：未做文件上传 / Seedream / YAML 编辑保存 / accept-reject-revert 新行为 / LangGraph·Zep·OASIS·CAMEL；只做「主题创世 → 项目落盘 → 世界锚定确认」最小闭环。
- **产品入口现状**：两条完整路径已通——**导入已有小说**（第五刀）+ **从主题创世**（第六刀），都落到世界锚定页确认。
- **下一刀建议**：世界锚定轻编辑→YAML 保存（先补 YAML parse 健康检查/降级，防手改坏文件 500）；或真实 LLM 接入设置（mock/rounds 移入前端设置）、流式/job 进度。

### 2026-05-29 — v0.7 第七刀 世界锚定轻编辑 + YAML 安全保存

- **做了什么**：
  - 新建 `service/project_health.py`（console-free）：`check_project_health(slug, projects_dir?)` 逐个 parse `world/characters/open_threads/story_contract.yaml`，**解析失败不抛 500** 而是定位到具体文件（`files: {name: ok|missing|error}`）+ 跑 `validate_project` 合并 errors/warnings；`status` = error（任一 YAML 损坏或 validate hard error）/ warning / ok。`resolve_story_path(slug, projects_dir?)` 与 indexer 同义但可显式传 projects_dir（便于测试）。
  - 新建 `service/anchor_update.py`（console-free）：`update_world_anchor(slug, patch, projects_dir?)`。**仅白名单字段**：`world.rules`/`world.scene_description`、`characters[].persona.{boundaries,traits}`、`characters[].current_state.{location,emotion}`、`open_threads[]`（任意其它字段忽略，不允许任意 YAML 写入）。**写前严格 parse**（任一损坏→`AnchorUpdateError`→400，不写任何文件）；**先备份**到 `projects/<slug>/backups/<ts>/` 再写；用 `writer._write_yaml` 写回保持格式；**写后 `validate_project` + `check_project_health`**（即便 hard error 也已保存，由 health.status 标注）。内置样例→`AnchorReadOnlyError`→400；缺故事→`FileNotFoundError`→404；无白名单字段→400。
  - `service/__init__.py` 导出 health/update 符号。
  - `browser/server.py`：GET `/api/stories/<slug>/health`（在 `/anchor` 后缀路由之后、通用 `<slug>` 之前；`safe_id`），POST `/api/stories/<slug>/anchor`（`_handle_anchor_update`，404/400 映射，返回 `{anchor: indexer.get_world_anchor(slug), health, changed, backup}`）；GET 既有契约不变。
  - 前端：`types.ts` 加 `ProjectHealth`/`AnchorPatch`/`AnchorUpdateResponse`/`HealthStatus`；`client.ts` 加 `getProjectHealth`/`updateWorldAnchor`。`WorldAnchorPage` 重写为支持**轻编辑模式**：左栏健康徽标（正常/有警告/YAML 损坏）+「编辑锚定/保存锚定/放弃修改」+ 损坏文件列表（损坏时禁编辑、内置样例只读）；中栏世界规则（增删改行）/此刻场景（textarea）/开放伏笔（title+status+desc 增删改）；右栏角色卡边界（增删改行）+ location/emotion。保存成功后刷新 anchor+health 并提示「锚定已保存」；不暴露 raw YAML textarea。
- **测试/验证**：后端 `383 passed`（+15）：`tests/test_project_health.py`（正常 ok、world 损坏不 500 且定位、characters 损坏定位、缺故事 404）+ `tests/test_web_anchor_update_api.py`（service：patch 成功写回+备份、无白名单字段 400、坏 YAML 拒绝、缺故事 404、内置只读；HTTP：health 200、坏 slug 400、POST patch 成功反映 anchor、坏 slug 400、缺故事 404、坏 YAML 400）；既有 368 零回归；前端 `pnpm run build`（tsc -b + vite）通过；新文件 lint 仅余 SonarQube 风格告警（array-index key/只读 props/复杂度/重复字面量，与既有组件同模式，非阻塞）。
- **文件**：`service/{__init__,project_health,anchor_update}.py`、`browser/server.py`、`engine/ui/src/api/{client,types}.ts`、`engine/ui/src/components/{WorldAnchorPage.tsx,worldAnchor.css}`、`tests/{test_project_health,test_web_anchor_update_api}.py`。
- **边界**：未做完整 YAML IDE / 多人协作 / 版本 diff UI / 改 chapter.md·outputs·worldline / Seedream / 长篇检索增强。
- **下一刀建议**：真实 LLM 接入设置（mock/rounds 移入前端设置）；或流式/job 进度；可选 `source_type=genesis` 在浏览器层做「创世」徽标。
- **补丁（同日核查）**：用户发现写前严格 parse 漏了 `story_contract.yaml`，已在 `anchor_update.py` 补 `_load_strict(story_contract.yaml)` + 新增 service/HTTP 两个覆盖；基线由 `383` → `385 passed`。

### 2026-05-29 — v0.7 第八刀 真实 LLM / 运行设置面板

- **做了什么**：
  - 新建 `service/runtime_settings.py`（console-free）：`RuntimeSettings`（`llm_api_key_present`/`masked_key`/`llm_base_url`/`llm_model_name`/`default_mock`/`default_rounds`/`default_runner`/`available_runners`/`seedream_enabled=False`）。所有写入**只进当前 Python 进程环境变量**（`LLM_API_KEY`/`LLM_BASE_URL`/`LLM_MODEL_NAME`/`LNE_MOCK`/`LNE_DEFAULT_ROUNDS`/`LNE_SCENE_RUNNER`），**不落盘、不返回明文 Key**（仅 `masked_key` 留尾 4 位）。`update_runtime_settings(patch)`：空 `api_key` 设为空串以清除（避免 .env 经 `load_dotenv(override=False)` 再注入）；`default_rounds` 限 1–12，越界 `SettingsError`→400；`default_runner` 须在 `available_runners()`，否则 400。`default_mock/rounds/runner()` 供生成入口回退（无 key 时 `default_mock` 默认 True）。`test_connectivity(mock)`：mock→available True 不调模型；无 key→available False；真实 key 发 1-token ping，任何异常一律 catch 降级 available False，**不抛 500**。
  - `browser/server.py`：GET `/api/settings/runtime`（返回脱敏设置）；POST `/api/settings/runtime`（`_handle_settings_update`，`SettingsError`→400）；POST `/api/settings/runtime/test`（`_handle_settings_test`）。**`_handle_intervention/_handle_import_novel/_handle_story_genesis` 改为：body 含 `mock/rounds/runner_name` 则显式优先，缺省回退 `default_mock/rounds/runner()`**。GET/既有 POST 契约不变。
  - 前端：`types.ts` 加 `RuntimeSettings`/`RuntimeSettingsPatch`/`ConnectivityResult`/`RunnerName`；`client.ts` 加 `getRuntimeSettings`/`updateRuntimeSettings`/`testConnectivity`。新建 `SettingsDrawer.tsx`+`settings.css`（顶栏「设置」抽屉：API Key 输入框只显「已配置 ••••尾4位/未配置」+「清除」、Base URL、Model、默认 mock、默认 rounds 1–12、默认 runner 下拉、测试连接；面向普通用户文案）。`AppShell` 顶栏加「设置」按钮 + 抽屉。`InterventionComposer/GenesisPage/ImportNovelPage` 挂载时读 `getRuntimeSettings().default_mock` 初始化 mock（仍可局部覆盖）；composer 去掉硬编码 `rounds:2`，改由后端用设置默认。
- **测试/验证**：后端 `400 passed`（+15）：`tests/test_runtime_settings_api.py`（service：默认设置、写入+脱敏不回显明文、空 key 清除、rounds 越界 400、runner 非法 400/合法、默认值回读、无 key 连通性 unavailable、mock 连通性 available；HTTP：GET 200、POST 不回显明文、rounds 400、runner 400、test 无 key unavailable、intervention 缺 mock 时回退设置默认 mock=True 端到端成功）；既有 385 零回归；前端 `pnpm run build`（tsc -b + vite）通过；lint 仅余 SonarQube 风格告警（复杂度/重复字面量/只读 props/嵌套三元/role 提示，与既有组件同模式，非阻塞）。
- **文件**：`service/{__init__,runtime_settings}.py`、`browser/server.py`、`engine/ui/src/api/{client,types}.ts`、`engine/ui/src/components/{SettingsDrawer.tsx,settings.css,AppShell.tsx,InterventionComposer.tsx,composer.css,GenesisPage.tsx,ImportNovelPage.tsx}`、`tests/test_runtime_settings_api.py`。
- **边界**：未做云端账号 / 持久化 API Key / 多 provider gateway / Seedream 正式接入 / 流式 job 队列。
- **下一刀建议**：流式/job 进度（长推演不阻塞），或真实 LLM 端到端体验打磨；可选 `source_type=genesis` 创世徽标、diff 写回严格布尔解析。

### 2026-05-29 — v0.7 第九刀 异步 Job / 进度轮询

- **做了什么**：
  - 新建 `service/jobs.py`（console-free 通用基础设施）：`JobRecord`（`job_id`/`kind`/`status` queued|running|succeeded|failed/`progress` 0–100/`stage`/`created_at`/`updated_at`/`result`/`error`）+ `JobStore`（`threading.Lock` + `ThreadPoolExecutor(max_workers=2)`，`OrderedDict` 保留最近 100、`_evict_locked` 清理最旧）。`submit(kind, runner)` 接收 `runner(update)->dict` 回调，业务逻辑由调用方复用既有 service 拼装，**本模块不复制推演/导入/创世逻辑**；runner 抛任何异常→job `failed`+`error`，不外抛。进程级单例 `JOBS`。
  - `browser/server.py`：POST `/api/jobs/intervention|import-novel|story-genesis`（各自构造 runner 闭包复用 `run_intervention`/`import_novel_from_payload`/`generate_story`，沿用第八刀的 `default_mock/rounds/runner` 回退；result dict 与同步 API 同构，返回 `202 {job_id,status}`）；GET `/api/jobs/<id>`（`safe_id`，未知 404、非法 400，**失败 job 也 200+error 不抛 500**）。既有同步 API 全部保留。
  - 前端：`types.ts` 加 `JobStatus`/`JobSubmitResponse`/`JobRecord<T>`；`client.ts` 加 `postJob{Intervention,ImportNovel,StoryGenesis}`/`getJob<T>`（保留旧同步方法）。新建 `api/jobs.ts`：`pollJob<T>(jobId,onProgress,shouldStop,800ms)`（succeeded→resolve result、failed→reject error、`shouldStop` 静默中止）+ `JobCancelled`。`InterventionComposer`/`ImportNovelPage`/`GenesisPage` 改走 job：提交→202→轮询显示 `stage` 文案→成功跳转/选分支；用 `stoppedRef` 在卸载时停轮询避免 setState on unmounted；import/genesis 的「项目已存在」改由 error 文案含「已存在」判定（同步 API 的 409 改成 job error）。
- **测试/验证**：后端 `410 passed`（+10）：`tests/test_jobs_api.py`（service：JobStore 成功/失败捕获/未知 kind/超量清理最旧；HTTP：intervention job 202→轮询 succeeded 有 run_id、import job 成功后 anchor 可读、genesis job 成功后 anchor 可读、缺 content→job failed 且 error 可读、未知 job 404、非法 job_id 400）。一处偶发 `ConnectionAbortedError`（`test_web_anchor_update_api` 的 HTTP fixture Windows 套接字关闭竞态，与本刀无关，复跑全绿）。前端 `pnpm run build`（tsc -b + vite）通过；lint 仅余 SonarQube 风格告警（只读 props/label 关联/不必要断言，与既有同模式，非阻塞）。
- **文件**：`service/{__init__,jobs}.py`、`browser/server.py`、`engine/ui/src/api/{types,client,jobs}.ts`、`engine/ui/src/components/{InterventionComposer,ImportNovelPage,GenesisPage}.tsx`、`tests/test_jobs_api.py`。
- **边界**：未做 SSE / WebSocket / 持久化队列 / 多用户隔离 / 云端部署 / 改输出目录结构。
- **下一刀建议**：真实 LLM 端到端体验打磨；或 `source_type=genesis` 创世徽标、diff 写回严格布尔解析、推荐榜启用。

### 2026-05-29 — v0.7.2 Agent Interaction 收口

- **做了什么**：
  - **InterventionGuardrail**：新建 `intervention/guardrail.py`（`evaluate_guardrail` + `InterventionGuardrailResult`/`GuardrailCheck`，六维 genre/time_power/persona/world_rule/visibility/strength，复用 classifier + world.rules + character.boundaries，deterministic、不调 LLM、**不改 contract_audit**）+ `service/intervention_guardrail.py`（load_story→evaluate）+ `POST /api/interventions/guardrail`。规则改写型 `allowed=False` 并提示另开 Alternate Novel；其余只解释不阻断 `run_intervention`。
  - **CharacterProbe**：新建 `service/character_probe.py`（belief/emotion/desires/fears/boundaries/known/unknown/fourth_wall_awareness+level/likely_intervention_response/obedience_risk/resistance_level/explanation）+ `GET /api/stories/<slug>/characters/<char_id>/probe`（可选 run_id/branch_id 叠加 state_snapshot、intervention_text 预测反应）。deterministic、无 LLM；故事/角色缺失 404；快照损坏不 500；中文解释"角色不会无条件服从"。
  - **CharacterAction 增强**：`models/events.py` additive 增 `action_id/action_label/preconditions/effects/failure_reason/repair_suggestions/risk/visibility`，全部默认空值；旧构造与旧 artifact 完全兼容；**未接入 runner 主链路**。
  - **Web UI**：`CharacterProbePanel.tsx`+`characterProbe.css`（世界锚定页角色卡折叠探针）；`InterventionComposer` 加「预检干预」按钮 + `GuardrailNote`（解释世界为何抵抗 + 更合理方式，不阻断提交）；`AgentTracePanel` 加结构化动作只读段（缺字段空态正常）；`api/{client,types}.ts` 加 guardrail/probe 类型与方法。
- **测试**：442 passed（+32）：`tests/test_intervention_guardrail.py`（evaluate 五类 + service 三类 + HTTP 五类）、`tests/test_character_probe.py`（service 八类含快照叠加/损坏降级/imported + HTTP 五类）、`tests/test_character_action_additive.py`（+3 旧构造/新字段/dump 往返）、`tests/test_v072_contract_unchanged.py`（+2 lightweight 契约不变 + 新字段不泄漏 events/snapshot）；既有 410 零回归；前端 `pnpm run build`（tsc -b + vite）通过。
- **文件**：`intervention/{guardrail,__init__}.py`、`service/{__init__,intervention_guardrail,character_probe}.py`、`browser/server.py`、`models/events.py`、`engine/ui/src/api/{client,types}.ts`、`engine/ui/src/components/{CharacterProbePanel.tsx,characterProbe.css,WorldAnchorPage.tsx,InterventionComposer.tsx,composer.css,AgentTracePanel.tsx}`、`tests/test_{intervention_guardrail,character_probe,character_action_additive,v072_contract_unchanged}.py`、文档。
- **明确未做**：runner 主链路重构、LangGraph、Seedream（v0.7.3）、Baseline/Canon Replay（v0.7.4）、Worldline Judge（v0.7.5）、Long Novel Memory（v0.8）、`AbstractIntervention -> CharacterActionSequence` 实例化、真实 LLM 探针、CharacterAction 接入 trace 实际产出。
- **下一刀建议**：v0.7.3 Seedream Visual Assets（角色头像/封面/场景图，未配置 API Key 时降级占位图）。

### 2026-05-29 — 路线与文档整理（v0.7 主闭环封存）

- **做了什么**：
  - 将 `memory.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/living-novel-engine-prd.md`、`docs/completed/v0.7-product-web-app-ui-spec.md`、`engine/README.md` 从旧的 v0.7.1-C / 317 passed / “v0.7 下一步”口径同步为当前实际状态：**v0.7 Product Web App 九刀已收口，测试基线 410 passed，下一步进入 v0.7.2 Agent Interaction**。
  - 清理已过期缺口：Web 导入、主题创世、Causal Diff 操作、世界锚定页、运行设置、异步 Job 不再标为待做。
  - 将 v0.7.4 重新聚焦为 Baseline Worldline / Canon Replay；其中 Story Genesis Mode 标为已完成前置。
  - 保留 v0.7.3 Seedream 5.0 Lite、v0.7.5 Worldline Judge、v0.8 Long Novel Memory 的正式排期。
- **测试**：文档更新，无需跑 pytest；如后续提交前需要，可按 `cd engine && python -m pytest -q` 与 `cd engine/ui && pnpm run build` 复验。
- **下一刀建议**：v0.7.2 Agent Interaction 第一刀，先做 `CharacterAction` / `CharacterProbe` / `InterventionGuardrail` 的数据结构与只读展示，不急着重构 runner。

### 2026-05-30 — 优化 Cursor 项目记忆规则（四文档上下文）

- **做了什么**：
  - 重写 `.cursor/rules/project-memory.mdc`：标题从单一 `memory.md` 改为「LNE 四文档上下文」；明确四份文档职责表、并行读取要求、按任务类型的重点章节、事实优先级；强调任务结束只写 `memory.md`。
  - 用户 @`memory.md` 或说「先读 memory」时仍须读完整四文档。
- **测试**：规则/文档更新，无代码变更。
- **文件**：`.cursor/rules/project-memory.mdc`、`memory.md`

### 2026-05-30 — v0.7.3 Visual Asset Generation 收口（Seedream 视觉资产增强层）

- **做了什么**：
  - 新建 `visual_assets/` 包：`models.py`（`VisualAssets`/`AssetEntry`，additive artifact 契约，仅存相对路径+元数据）、`store.py`（artifact 读写 + 图片落盘 + 安全路径解析，缺/损坏降级 status none）、`seedream_client.py`（`SeedreamSettings`/`SeedreamClient`/`ImageResult`，import 不读网络，无 Key/关闭/异常稳定降级，兼容解析 b64_json/url，不泄漏 Key）、`prompt_builder.py`（封面/角色/场景/世界线节点中文 prompt，克制无 AI 味）。
  - 新建 `service/visual_assets.py`：`get_visual_assets` / `generate_visual_assets`（force=false 不重复 ready、mock 或无 Key→placeholder 不打外网）/ `resolve_asset_path`（禁穿越）；视觉资产目录统一落 `projects/<slug>/`（gitignored，内置样例也不污染 samples/）。
  - `browser/server.py` 加三路由：`GET /api/stories/<slug>/visual-assets`、`POST .../visual-assets/generate`、`GET /api/stories/<slug>/assets/<rel>`（路径安全：穿越 403、缺失 404、坏 slug 400、缺故事 404）；注册 webp mime。
  - `service/runtime_settings.py` additive 增 Seedream 字段（enabled/key_present/masked/base_url/model）+ patch 写入 `SEEDREAM_*`/`LNE_VISUAL_ASSETS`（不落盘、不回显明文）。
  - Web UI：`VisualAssetPanel.tsx`+`visualAssets.css`（`AssetImage`/`CharacterAvatar`/`VisualAssetsControls`/`StoryCoverThumb`）；`WorldAnchorPage` 左栏封面+生成/重新生成区、角色卡头像；`StoryEntryPage` 书架封面缩略；`SettingsDrawer` Seedream 区块；`api/{client,types}.ts` 加视觉资产类型/方法/`assetUrl`。无图古风占位、加载失败回退、布局稳定，中文文案。
  - `.env.example` 补 Seedream 变量说明。
- **测试**：482 passed（+37）：`tests/test_visual_assets.py`（prompt_builder / store 含损坏与穿越 / seedream client fake 含无 Key·mock·b64·异常 fallback / service 含 mock·fake ready·force / HTTP 含 GET·POST·资产服务·路径穿越 403）；既有 445 零回归；前端 `pnpm run build`（tsc -b + vite）通过。
- **文件**：`visual_assets/{__init__,models,store,seedream_client,prompt_builder}.py`、`service/{__init__,visual_assets,runtime_settings}.py`、`browser/server.py`、`engine/ui/src/api/{client,types}.ts`、`engine/ui/src/components/{VisualAssetPanel.tsx,visualAssets.css,WorldAnchorPage.tsx,StoryEntryPage.tsx,SettingsDrawer.tsx}`、`engine/.env.example`、`tests/test_visual_assets.py`、文档。
- **明确未做**：真实线上批量生成队列；世界线节点缩略图真正绑定 run/branch 生成（仅预留 artifact 字段 + UI 占位）；图片版权/公开分享策略；真人/影视角色复刻（明确不做）；Baseline/Canon Replay（v0.7.4）、Worldline Judge（v0.7.5）、Long Novel Memory（v0.8）。**未做真实联调**（无外网，测试全走 fake/mock；真实 Seedream 联调见 README smoke checklist）。
- **下一刀建议**：v0.7.4 Baseline & Canon Replay（无干预基线 + 正史回放），不要继续堆视觉功能。

### 2026-05-30 — v0.7.4 Baseline & Canon Replay 收口

- **做了什么**：
  - **Baseline Worldline**：`orchestrator/worldline_brancher.build_baseline_spec()`（branch_id=`baseline`、branch_seed=`linear`，复用 resume continue 无新干预语义）；新建 `baseline/{models,__init__}.py`（`BaselineReport`/`CharacterStateChange`，version v0.7.4）；新建 `service/baseline.py`（`generate_baseline`：缺 from_run/from_branch→从故事锚定状态推进一章，有则从 parent 快照续；`get_baseline_report`）；`output/writer.py` 加 `write_baseline_output`（写 `meta.json`+`baseline_report.json`+`baseline/`{chapter/events/state_snapshot/summary}+`baseline_meta.json`，**显式不写 intervention.json/causal_diff.json**）。缺故事透传 FileNotFoundError→404。
  - **Canon Holdout + Replay**：新建 `canon_replay/{models,evaluator,__init__}.py`（`HoldoutManifest`/`HoldoutChapter`/`ReplayScores`/`CanonReplayReport` + deterministic `evaluate_replay`：lexical=字级 bigram Jaccard、entity=角色/地点/势力命中、thread=开放伏笔标题命中、length_ratio、state_consistency=baseline 快照角色是否仍现身，加权 overall）；新建 `service/canon_replay.py`（`write_holdout`/`get_holdout`：仅 imported/genesis 可写、builtin 只读、force=False 同章 409、文件名由章号派生防穿越；`run_canon_replay`/`get_canon_replay_report`：读 baseline chapter + holdout，写 `canon_replay_report.json`）。**不打 LLM、holdout 文本只进 evaluator**。
  - **API（6 个，全 additive）**：`POST /api/stories/<slug>/baseline`、`GET /api/runs/<run_id>/baseline`、`GET/POST /api/stories/<slug>/canon/holdout`、`POST /api/stories/<slug>/canon/replay`、`GET /api/runs/<run_id>/canon-replay`。坏 slug 400、缺故事 404、builtin 写 holdout 400、同章 409、缺 baseline/holdout 404、损坏 artifact 400，**不 500**。
  - **基础设施修正**：`writer._outputs_dir()` 改为优先读 `LNE_OUTPUTS_DIR`（与 `browser.paths.outputs_dir()` 对齐；默认值不变，既有 monkeypatch 测试不受影响），让 baseline/replay 服务与 server/indexer 输出根一致、测试可隔离。
  - **Web UI**：新建 `BaselineCanonPanel.tsx`+`baselineCanon.css`（世界锚定页左栏区块）：holdout 状态（builtin 只读提示 / imported 录入 textarea）、生成无干预基线、章节下拉 + 运行正史回放、基线摘要（自然发展/角色状态/触及伏笔）、回放评分条（总分 + 5 分项 + 解释 + 缺失实体/伏笔 + 警告）；中文文案，强调"基线不是原作、回放仅本地评估"；`api/{client,types}.ts` 加 6 方法 + 全套类型。
- **测试**：520 passed（+37，`tests/test_v074_baseline_canon_replay.py`：baseline service builtin/imported/缺故事/坏参数/无 intervention.json artifact/GET report；holdout 读写/409/force 覆盖/builtin 只读/空内容/非法章号/坏 slug/文件名派生防穿越；evaluator 分数范围/实体命中缺失/相同文本高分/空文本告警；replay service 写盘/缺 baseline/缺 holdout/坏章号/GET；HTTP baseline·holdout·replay 全流程 + 404/400/409）；随后 Codex 兜底补 service 层 id 安全校验和 holdout UI 默认不覆盖，复验为 **526 passed**；前端 `pnpm run build`（tsc -b + vite）通过。
- **文件**：`baseline/{__init__,models}.py`、`canon_replay/{__init__,models,evaluator}.py`、`service/{__init__,baseline,canon_replay}.py`、`orchestrator/worldline_brancher.py`、`output/writer.py`、`browser/server.py`、`engine/ui/src/api/{client,types}.ts`、`engine/ui/src/components/{BaselineCanonPanel.tsx,baselineCanon.css,WorldAnchorPage.tsx}`、`tests/test_v074_baseline_canon_replay.py`、文档。
- **明确未做**：Worldline Judge（v0.7.5）、Long Novel Memory（v0.8）、LLM 语义评估、百万字 holdout、版权/公开分享策略、baseline↔intervention 并排偏离对比 UI、run-detail 页持久化展示 baseline/replay 报告（当前在锚定页生成时即时展示，报告可经 GET API 读回）。
- **下一刀建议**：v0.7.5 Worldline Judge（`worldline_judgement.json`：persona consistency / contract risk / branch diversity / narrative momentum / emotional payoff / anti-slop / continuation potential + emergence_score + story arc/turning points）。

### 2026-05-30 — Codex 接力迁移文档

- **做了什么**：
  - 新增 `AGENTS.md`：沉淀 Codex 项目级规则、会话开始必读、硬约束、验证命令、Cursor 迁移原则，并补充资料索引（`docs/completed`、`docs/article`、`Reference_projects`）。
  - 新增 `docs/codex-handoff.md`：新窗口第一条消息模板、当前版本状态、v0.7.5 Worldline Judge 建议边界、每刀收口清单。
  - 新增 `docs/codex-migration-guide.md`：说明 `.cursor/rules`、`.cursor/skills` 与 Codex skills/plugins 的迁移对应关系，避免整包复制通用技能造成上下文噪音。
  - 同步当前基线与入口路径：v0.7.4 经 Codex 兜底后后端 `526 passed`、前端 build 通过；主 PRD 入口为 `docs/living-novel-engine-prd.md`，已完成专项 PRD 存在 `docs/completed/`。
- **测试**：文档迁移为主；执行 `git diff --check` 验证无 whitespace error。
- **文件**：`AGENTS.md`、`.cursor/rules/project-memory.mdc`、`docs/codex-handoff.md`、`docs/codex-migration-guide.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/living-novel-engine-prd.md`、`docs/completed/v0.7-product-web-app-ui-spec.md`、`engine/README.md`、`memory.md`。
- **下一刀建议**：新开 Codex 窗口后按 `docs/codex-handoff.md` 接力，进入 v0.7.5 Worldline Judge。

### 2026-05-30 — v0.7.5 Worldline Judge 收口

- **做了什么**：
  - 新增 `worldline_judge/{models,evaluator}.py`：deterministic 分支评审，输出 `worldline_judgement.json`，覆盖角色一致性、合约风险、分支差异、叙事动量、情绪兑现、anti-slop、续写潜力、`emergence_score`、故事弧、转折点、张力与“推荐继续 / 谨慎继续 / 建议归档”。
  - 新增 `service/worldline_judge.py` + HTTP `POST/GET /api/runs/<run_id>/branches/<branch_id>/worldline-judgement`，所有 run_id/branch_id/story_slug 走安全校验；缺报告 404，损坏 artifact 400；不打 LLM、不改 runner、不写回正文或 state_snapshot。
  - 前端工作台右侧新增「世界线评审」标签页，可读取/生成报告，中文展示总分、推荐、故事弧、维度评分、优势/警告/建议/转折点。
- **测试**：`tests/test_v075_worldline_judge.py` 9 passed；`engine/ui pnpm run build` 通过；完整后端 `python -m pytest -q` 为 535 passed。
- **文件**：`worldline_judge/{__init__,models,evaluator}.py`、`service/{__init__,worldline_judge}.py`、`browser/server.py`、`engine/ui/src/api/{client,types}.ts`、`engine/ui/src/components/{RightPanel,WorkspacePage,WorldlineJudgePanel,worldlineJudge.css}.tsx`、`tests/test_v075_worldline_judge.py`、文档。
- **明确未做**：LLM 语义评审、run 级聚合评审、`compare.md` 汇总、`emergence_nodes.json` 持久化、discourse-aware narrator、Long Novel Memory。
- **下一刀建议**：v0.8 Long Novel Memory 第一刀，先做百万字导入的分片/异步导入与结构化导入报告，不急着接向量库。

### 2026-05-30 — v0.8.0-A Long Novel Ingestion Report

- **做了什么**：
  - 新增 `import_novel/report.py`：构造 `import_report.json`（version `v0.8.0`），统计总章节、总字数、前 20 章可体验范围、`partial_ready`、疑似乱码章节、重复章名、缺章编号，以及每章 `source_raw_path` / `source_path`。
  - `write_project()` 统一写入 `source_raw/` 和 `import_report.json`；即使走 CLI / 旧 writer 路径也有导入报告。`source/`、`canon_chapter.md`、`facts.jsonl`、`summaries/` 等既有契约不变。
  - `service.import_novel_from_payload()` 新增 additive `long_mode`：默认仍保持 3-10 章小闭环；`long_mode=True` 时允许最多 200 章，生成导入报告摘要并合并风险 warnings。
  - `/api/import-novel` 与 `/api/jobs/import-novel` 接收 `long_mode` 并返回 `import_report` 摘要；前端类型 `ImportNovelRequest/Response` additive 增字段，现有 UI 不受影响。
- **测试**：新增 `tests/test_v080_long_ingestion.py`（4 passed：25 章 long mode、旧 10 章限制、乱码/重复/缺章风险、job 返回报告摘要）；导入/job 相关回归 `tests/test_v080_long_ingestion.py tests/test_web_import_api.py tests/test_import_mock.py tests/test_jobs_api.py -q` 为 **39 passed**。
- **明确未做**：当时未做前端分片上传、断点续传、epub/zip、后台部分索引、角色抽取置信度、时间线风险、entity index / vector index；其中前端分片上传与 epub/zip 已于 2026-05-31 补齐。
- **下一刀建议**：v0.8.1 Hierarchical Memory 第一刀，先写 `memory/` 目录骨架、`master_setting.yaml`、chapter/volume briefs 镜像和 `memory_manifest.json`，继续不改 runner。

### 2026-05-30 — v0.8.1-A Hierarchical Memory Skeleton

- **做了什么**：
  - 新增 `import_novel/memory_writer.py`：导入时生成 `projects/<slug>/memory/` 分层记忆骨架，包含 `memory_manifest.json`、`master_setting.yaml`、`volumes/volume_*.yaml`、`chapters/chapter_*.yaml`、`character_states/*.yaml`、`timeline.yaml`、`plot_threads.yaml`、`propagation_debts.yaml`。
  - `write_project()` 在写完 `import_report.json` 后统一调用 `write_hierarchical_memory()`；CLI、Web 同步导入、异步 job 导入都能得到同一套 memory artifact。
  - 记忆骨架只镜像 world/characters/source/source_raw/open_threads，不进入 runner prompt，不改变 `chapter.md`、`events.json`、`state_snapshot.json` 等运行产物契约。
- **测试**：新增 `tests/test_v081_hierarchical_memory.py`（2 passed：manifest/layers 文件存在、chapter/character/timeline/threads/debts 可审计）；导入/检索相关回归曾出现一次 Windows HTTP socket 超时，复跑失败单测通过。
- **明确未做**：LLM 章节摘要重写、scene 级切分、角色状态随后续 run 自动投影、审计反馈写入、runner 消费 memory 层。
- **下一刀建议**：v0.8.2 Canon Ledger 第一刀，把 `facts.jsonl` 镜像/升级为 `memory/canon_ledger.jsonl`，记录 event/state/relationship/thread 的统一字段，为后续审计和 GraphRAG 留迁移口。

### 2026-05-30 — v0.8.2-A Canon Ledger Skeleton

- **做了什么**：
  - `import_novel/memory_writer.py` 新增 `memory/canon_ledger.jsonl`，并在 `memory_manifest.json` 登记 `canon_ledger` layer。
  - 账本记录统一字段：`id/type/chapter/scene/entities/statement/truth_status/source_ref/confidence/valid_from/valid_until`；当前 deterministic 来源包括章节事件、角色状态、角色关系、开放伏笔。
  - 旧 `canon/facts.jsonl` 保持不变，现有 BM25 检索仍走原链路；新 ledger 作为 v0.8 一致性审计、混合检索、GraphRAG/Zep 迁移口。
- **测试**：新增 `tests/test_v082_canon_ledger.py`（2 passed）；前三刀导入/分层记忆/账本/导入 API/检索回归 `57 passed`。
- **明确未做**：从 LLM 抽取细粒度事件、valid_until 自动更新、ledger 查询 API、ledger 参与 prompt、死亡/道具/时间线冲突审计。
- **下一刀建议**：v0.8.3 Hybrid Retrieval 第一刀，先让 context loader 读取 `memory/canon_ledger.jsonl` 并以 `canon_ledger` source 进入检索语料，增加 entity boost，但不引入向量库。

### 2026-05-30 — v0.8.3-A Canon Ledger Retrieval

- **做了什么**：
  - `retrieval/context_loader.py` 新增 `CanonLedgerItem` 与 `_load_canon_ledger()`，从 `memory/canon_ledger.jsonl` 读取统一正史账本；缺失/损坏时空列表降级。
  - `retrieval/retriever.py` 将账本记录作为 `canon_ledger` source 纳入 BM25 语料，source weight 1.1；命中项保留 `entities`、`ledger_type`、`confidence`，并合并进 prompt 的“正史事实”块。
  - 不引入向量库、embedding、reranker，也不改变 builtin 样例的无检索行为。
- **测试**：`tests/test_context_retrieval.py` 新增 loader/retriever 覆盖；检索/导入/浏览相关回归 `39 passed`。
- **明确未做**：entity alias resolution、向量检索、reranker、prompt budget pack、ledger 与旧 facts 去重。
- **下一刀建议**：v0.8.4 Consistency Audit 第一刀，基于 `canon_ledger` 与导入报告做 deterministic 静态审计，先输出 `memory/consistency_report.json`，不接 LLM。

### 2026-05-30 — v0.8.4-A Static Consistency Audit

- **做了什么**：
  - 新增 `import_novel/consistency_audit.py`，导入时生成 `memory/consistency_report.json`，并在 `memory_manifest.json` 登记 `consistency_report` layer。
  - 报告字段覆盖 `persona_drift`、`timeline_conflicts`、`resource_conflicts`、`contract_violations`、`forgotten_threads`、`repair_suggestions`、summary issue_count/risk_level。
  - 当前为 deterministic 导入级静态审计：把 `import_report` 的缺章/重复章名/乱码转成 timeline/resource 风险；检查 canon ledger 是否为空；把 open_threads 登记为待追踪伏笔。不打 LLM，不接 runner。
- **测试**：新增 `tests/test_v084_consistency_audit.py`（2 passed）；v0.8 导入/记忆/账本/审计/检索/导入 API 回归 `61 passed`。
- **明确未做**：运行后写回审计、角色漂移检测、道具/死亡/地点同时性冲突、LLM 语义审计、前端审计面板。
- **下一刀建议**：v0.8.5 Long Canon Replay Evaluation 可复用 v0.7.4 holdout/replay，下一步应先做“长篇 runtime_visible / holdout_private manifest 隔离”，而不是让 holdout 进入检索。

### 2026-05-30 — v0.8.5-A Long Canon Replay Isolation

- **做了什么**：
  - `service/canon_replay.write_holdout()` 保留旧 `canon/holdout/chapter_*.md`，同时镜像私有章节到 `holdout_private/chapter_*.md`。
  - 新增 `canon/visibility_manifest.json`：`runtime_visible` 指向 `source/` 可见章节，`holdout_private` 指向 evaluator-only 私有章节，并写明不得进入 retrieval / character_agent / narrator / multi_agent_runner prompt。
  - `get_holdout()` additive 返回 `visibility_manifest` 摘要；旧 holdout/replay API 结构保持可用。
  - 检索测试确认用 holdout 私有文本查询时，不会进入 `retrieval_context.prompt_block` 或 items。
- **测试**：新增 `tests/test_v085_long_canon_replay.py`（3 passed）；Canon Replay / 检索回归 `68 passed`。
- **明确未做**：更复杂的隐藏评估集切分策略、按章节比例自动划分 runtime/holdout、长篇 replay 批量评估 UI、版权/分享策略。
- **下一刀建议**：进入 v0.8+ ActDirector 第一刀，先做 deterministic `AbstractIntervention -> CharacterActionPlan` 规划 artifact，不接 runner 主链路。

### 2026-05-30 — v0.8+ ActDirector-A Planning Artifact

- **做了什么**：
  - 新增 `act_director/` 包：`CharacterActionPlan` / `ActionPlanStep` / `plan_character_actions()`。
  - `plan_character_actions()` 将 `InterventionCompilation` 的 `AbstractIntervention`、`branch_axis`、`compatibility` 转成可审计动作计划；每个 step 含 `preconditions`、`effects`、`failure_reason`、`repair_suggestions`、`risk`、`visibility`、`rationale`。
  - `service.run_intervention()` 在写 run 产物后额外写 `act_director_plan.json`，并在 `InterventionServiceResult.extra["act_director_plan"]` 返回摘要。该 artifact 不驱动 `run_scene`，不改变 events/state/chapter 旧契约。
- **测试**：新增 `tests/test_v086_act_director.py`（3 passed）；干预编译/LLM fallback/Web intervention/CharacterAction 回归 `50 passed`。
- **明确未做**：runner 消费 action plan、把 CharacterAction 写入 `multi_agent_trace` 实际产出、前端 ActDirector 面板、LLM action planner。
- **下一刀建议**：Discourse-aware Narrator-A，先给分支产物新增 `narrative_diagnostics.json` 或扩展 Worldline Judge 的节奏/转折建议，而不是直接重写 narrator。

### 2026-05-30 — v0.8+ Discourse-aware Narrator-A Diagnostics

- **做了什么**：
  - 新增 `narrative_diagnostics/` 包：`analyze_narrative()` 输出 `narrative_diagnostics` artifact，包含 char/sentence/paragraph/dialogue/turning/pacing metrics、tension_curve、warnings、suggestions。
  - `output.writer._write_branch_outputs()` 在每个分支写 `narrative_diagnostics.json`；baseline 分支也会获得该诊断。该 artifact 只做写后诊断，不改变 narrator prompt、不改正文。
- **测试**：新增 `tests/test_v087_narrative_diagnostics.py`（2 passed）；输出写盘/干预/基线/检索相关回归 `62 passed`。
- **明确未做**：outline -> turning points -> chapter 两阶段 narrator、分支故事弧规划、前端诊断面板、诊断结果反馈到下一轮生成。
- **下一刀建议**：Dynamic Action Registry-A，先生成 `dynamic_action_registry.yaml` / action alias registry，不接 runner 执行。

### 2026-05-30 — v0.8+ Dynamic Action Registry-A

- **做了什么**：
  - 新增 `dynamic_action_registry/` 包：`DynamicActionRegistry` / `ActionRegistryEntry` / `build_action_registry()`。
  - `build_action_registry()` 从 `CharacterActionPlan` 汇总动作类型、中文别名、前置条件、效果、失败原因、修复建议、风险等级、来源 step 与分支轴，形成 `dynamic_action_registry.yaml`。
  - `service.run_intervention()` 在写 `act_director_plan.json` 后同步写 run 根目录 `dynamic_action_registry.yaml`，并在 `InterventionServiceResult.extra["dynamic_action_registry"]` 返回摘要。该 artifact 只作审计与后续 runner 接入，不执行状态变化、不改变旧产物契约。
- **测试**：新增 `tests/test_v088_dynamic_action_registry.py`（2 passed）。
- **明确未做**：runner 消费动态动作注册表、动作 cooldown/cost、跨 run 的项目级动作模板沉淀、前端动作注册表面板。
- **下一刀建议**：Emergence Mining-A，先从 intervention/causal_diff/worldline_judgement/narrative_diagnostics/action_registry 汇总 `emergence_nodes.json`，不做社区推荐系统。

### 2026-05-30 — v0.8+ Emergence Mining-A

- **做了什么**：
  - 新增 `emergence_mining/` 包：`EmergenceReport` / `EmergenceNode` / `mine_emergence_nodes()` / `write_emergence_nodes()`。
  - `mine_emergence_nodes()` 从 run 目录读取 `intervention.json`、`intervention_compilation.json`、`dynamic_action_registry.yaml`、分支 `causal_diff.json`、`worldline_judgement.json`、`narrative_diagnostics.json`，汇总候选涌现节点、来源 artifact、分值、状态和建议。
  - `service.run_intervention()` 每次干预后自动写 run 根目录 `emergence_nodes.json`，并在 `InterventionServiceResult.extra["emergence_nodes"]` 返回摘要。
  - 新增 `service/emergence_mining.py` 与 HTTP `POST/GET /api/runs/<run_id>/emergence-nodes`；run_id 走安全校验，缺 run/report 返回 404，坏报告返回 400。
- **测试**：新增 `tests/test_v089_emergence_mining.py`（4 passed，含 HTTP 生成干预后读取/重建涌现节点）。
- **明确未做**：跨 run 聚类、涌现节点推荐系统、世界线模板市场、前端涌现节点面板、将高价值节点自动反馈给下一轮生成。
- **下一刀建议**：收束 v0.1-v0.8 文档总览与未做项，再考虑 entity aliases / runner consumption / 前端 artifact 面板。

### 2026-05-30 — docs 目录导航整理

- **做了什么**：
  - 新增 `docs/index.md`，整理 `docs/` 根层文档、`completed/` 收口归档、`article/` 论文资料、`article/reports/` 论文研读报告、`research/` 参考项目吸收报告的职责和推荐读取顺序。
  - 在 `AGENTS.md` 与 `docs/codex-handoff.md` 的资料索引中补充 `docs/index.md`，方便新会话快速定位文档。
- **测试**：文档导航更新；执行 `git diff --check` 验证格式。

### 2026-05-30 — v0.8.x Entity Aliases / Entity Resolution

- **做了什么**：
  - 新增 `entity_aliases.py`，提供 `build_entity_aliases()`、`write_entity_aliases()`、`load_entity_aliases()` 和轻量 query/doc expansion；缺失返回 `missing`，损坏返回 `damaged`，不抛 500。
  - `write_hierarchical_memory()` 在导入时写 `memory/entity_aliases.yaml`，并在 `memory_manifest.json` 登记 `entity_aliases` layer；别名骨架从 characters、world locations/factions 与 canon ledger entities deterministic 生成。
  - `retrieval/context_loader.py` 读取 alias index；`retrieval/retriever.py` 对 query 与 corpus 文本做别名扩展，canon ledger 命中项 additive 返回 `resolved_entities`，避免同一角色/地点/物品多名称导致召回断裂。
  - `consistency_report.json` 的 summary additive 写 `entity_alias_count`；世界锚定 API/UI 只读展示实体别名状态、数量和样例，不允许编辑。
- **测试**：新增 `tests/test_v08x_entity_aliases.py`（4 passed：导入写 alias + manifest + audit count、损坏降级、检索别名归一化、锚定 API 摘要）；邻近回归 `37 passed`；完整后端 `python -m pytest -q` 为 **565 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **明确未做**：LLM/NER 实体抽取、人工别名编辑器、跨 run 写回别名、向量检索/reranker；前端 artifact 面板已于 2026-05-31 收束。
- **下一刀建议**：runner consumption 第一刀，先让运行时只读消费 memory/alias/ledger 的安全子集，保持 additive 与可回退；随后做前端 artifact 面板。

### 2026-05-30 — v0.8.x Runtime Memory Consumption-A

- **做了什么**：
  - 新增 `runtime_memory.py`，把 `memory/entity_aliases.yaml` 状态、query 实体归一化、`retrieve_context()` 结果与 consumed layers 打包为只读运行时记忆上下文。
  - `service.run_intervention()`、baseline 服务与 CLI resume 复用该上下文，把 `ctx.as_prompt_block()` 继续通过既有 `retrieved_context` 参数注入角色 Agent / narrator；不改 `run_scene` 默认行为。
  - 分支目录 additive 写 `runtime_memory_context.json`，保留 `query/current_chapter/prompt_block/consumed_layers/entity_aliases/resolved_query_entities/warnings/retrieval`；`entity_aliases.yaml` 缺失或损坏降级为 warning，不阻断生成。
- `browser.indexer.get_branch()` additive 返回 `runtime_memory_context`；当时 React 右侧解释面板新增「运行记忆」标签页，2026-05-31 已收束进「机制档案」统一只读面板。
- **测试**：新增 `tests/test_v08x_runtime_memory_context.py`（3 passed：上下文构建、损坏降级、干预产物/API 读取）；相关回归 64 passed；完整后端 `python -m pytest -q` 为 **568 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **明确未做**：`act_director_plan.json` / `dynamic_action_registry.yaml` / `emergence_nodes.json` 驱动 runner 实际状态变化、运行后审计写回；完整 artifact 总览面板与长篇分片上传/epub/zip 已于 2026-05-31 补齐。
- **下一刀建议**：前端 artifact 面板收束，把运行记忆、动作计划、动作注册表、叙事诊断、涌现节点做成统一只读解释面板；随后推进长篇上传产品化。

### 2026-05-31 — v0.8.x Frontend Artifact Panel 收束

- **做了什么**：
  - `browser.indexer.get_branch()` additive 返回 `act_director_plan`、`dynamic_action_registry`、`narrative_diagnostics`、`emergence_nodes`，与既有 `runtime_memory_context` 一起成为分支详情的统一解释层数据源；缺失/损坏 artifact 保持空态或 `{}`/`None` 降级，不抛 500。
  - React 右侧面板新增「机制档案」tab，收束运行记忆、动作计划、动作注册表、叙事诊断、涌现节点五类 v0.8 artifacts；原「运行记忆」独立 tab 合并进统一只读解释层。
- **测试**：新增 `tests/test_v08x_artifact_panel.py`（2 passed：artifact bundle 暴露、损坏降级）；完整后端 `python -m pytest -q` 为 **570 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **明确未做**：runner 消费动作计划/动作注册表/涌现节点并改变状态；真正断点续传/恢复；运行后一致性审计写回。
- **下一刀建议**：进入长篇上传产品化，先做前端分片/epub/zip 导入体验与 job 进度/失败空态，不急着接向量库。

### 2026-05-31 — v0.8.x Long Upload Productization

- **做了什么**：
  - `import_novel_from_payload()` 新增 additive `upload` 入参，支持 base64 分片还原并解析 txt/md、zip 内 txt/md、epub 内 html/xhtml 章节；损坏上传返回明确导入错误，异步 job 进入 failed/error，不抛 500。
  - React 导入页新增 txt/md/zip/epub 文件选择、浏览器端分片、上传文件摘要、job 进度条和失败空态/重试；未选文件时保留原 3-10 章粘贴模式。
- **测试**：新增 `tests/test_v08x_long_upload_product.py`（3 passed：txt 分片导入、zip 章节导入、epub job 成功 + 损坏 zip failed）；导入相关回归 `28 passed`；完整后端 `python -m pytest -q` 为 **573 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **明确未做**：真正多请求断点续传/恢复、持久化 ingest job、epub 目录 spine 精排、角色抽取置信度、时间线风险增强、向量库。
- **下一刀建议**：`v0.8.6 Long Import Review`，先做导入报告细化、章节列表/正文片段预览、导入质量空态与失败空态收束；断点续传/恢复顺延为 `v0.8.7`，runner 状态执行层评估顺延为 `v0.8.10-A/B`。

### 2026-05-31 — v0.8.6-v0.9.0-alpha 路线重排

- **做了什么**：
  - 明确当前仍在 v0.8.x 收束段，不直接跳 v0.9。
  - 将下一刀排为 `v0.8.6 Long Import Review`：导入报告细化、章节预览、导入质量空态、失败空态收束。
  - 将后续排期明确为 `v0.8.7 Resumable Ingest Jobs`、`v0.8.8 Long Project Workspace`、`v0.8.9 Long Replay & Audit UI`、`v0.8.10-A/B Runner State Execution`，再进入 `v0.9.0-alpha Long Novel Creation Loop`。
- **测试**：文档路线同步；执行 `git diff --check` 验证格式。
- **文件**：`memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/living-novel-engine-prd.md`、`docs/completed/v0.7-product-web-app-ui-spec.md`、`engine/README.md`。
- **下一刀建议**：新窗口从 `v0.8.6 Long Import Review` 开始，先扫描导入页、import report service/API、项目详情读取链路和失败空态测试。

### 2026-05-31 — v0.9+ 商业化增强排期拆分

- **做了什么**：
  - 将 PRD 里笼统的 `v0.9+ 商业化增强` 拆成产品闭环、轻量网关、轻量工作台、图记忆评估、复杂 runner 评估、商业化加固六层。
  - 明确 `v0.9.0-alpha` 只做长篇共创闭环，不默认接 Zep / 图数据库 / OASIS / CAMEL / LangGraph。
  - 将多 provider gateway 排为 `v0.9.1 Provider & Cost Gateway Lite`，完整 MasterSetting 排为 `v0.9.2 MasterSetting Workspace Lite`，Zep/图数据库排为 `v0.9.3 Graph Memory Evaluation Spike`，LangGraph/OASIS/CAMEL 排为 `v0.9.4 Advanced Runner Evaluation Spike`，真正商业化加固排为 `v1.0-beta`。
- **测试**：文档路线同步；执行 `git diff --check` 验证格式。
- **文件**：`memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、`docs/living-novel-engine-prd.md`、`docs/living-novel-engine-iteration-plan.md`、`engine/README.md`。
- **下一刀建议**：仍从 `v0.8.6 Long Import Review` 开始；不要因 v0.9+ 段落提前引入重依赖。

### 2026-05-31 — 产品化阶段归类文档化

- **做了什么**：
  - 新增 `docs/productization-phase-map.md`，统一解释技术 MVP、研发/机制 MVP、短中篇产品化 MVP、长篇底座 MVP、长篇产品化收束、v0.9.0-alpha 产品闭环、v0.9.1+ 触发式增强、v1.0-beta 商业化加固。
  - 在 `docs/living-novel-engine-iteration-plan.md`、`docs/living-novel-engine-prd.md`、`docs/codex-handoff.md`、`engine/README.md`、`docs/index.md`、`AGENTS.md` 中补充或链接该口径。
  - 明确 “MVP 已完成” 必须带限定语：v0.7-v0.7.5 是短中篇产品化 MVP；v0.8.0-A 至 v0.8.5-A 是长篇引擎底座 MVP；v0.8.6-v0.8.10 是长篇产品化收束；v0.9.0-alpha 才是长篇共创产品闭环成立，但仍不是商业级平台。
- **测试**：文档口径同步；执行 `git diff --check` 验证格式。
- **下一刀建议**：新窗口继续从 `v0.8.6 Long Import Review` 开始，不提前引入 Zep / 图数据库 / OASIS / CAMEL / LangGraph。

### 2026-05-31 — docs 根目录收束与 completed 归档

- **做了什么**：
  - 新建 `docs/completed/`，把已收口版本文档归档：`v0.1-to-v0.8-version-audit.md`、`v0.2-import-novel-mvp.md`、`v0.4-worldline-browser-release.md`、`v0.6.1-multi-agent-runner-protocol.md`、`v0.6.4-multi-agent-llm-runner.md`、`v0.6.5-multi-agent-reliability.md`、`v0.7-product-web-app-ui-spec.md`。
  - `docs/` 根目录收束为活文档与入口文档：`index.md`、`codex-handoff.md`、`codex-migration-guide.md`、`living-novel-engine-iteration-plan.md`、`living-novel-engine-prd.md`、`productization-phase-map.md`。
  - 同步 `AGENTS.md`、`docs/index.md`、`docs/codex-handoff.md`、主 PRD、主迭代计划、`engine/README.md` 中的路径，避免新窗口或 AI 读到已失效的旧位置。
- **测试**：文档目录重构；执行 `git diff --check` 验证格式。
- **下一刀建议**：仍从 `v0.8.6 Long Import Review` 开始；已收口资料如需追溯，从 `docs/completed/` 读取。

### 2026-05-31 — v0.8.6 Long Import Review

- **做了什么**：
  - `import_report.json` 升级为 `v0.8.6` additive 报告，新增 `source`、`chapter_stats`、章节 `preview`、`parsing_warnings`、`quality_risks`、`recommended_actions`；`summarize_import_report()` 同步返回风险与建议动作。
  - `browser.indexer.get_story()` / `get_world_anchor()` 新增 `import_review`，报告缺失或损坏时不抛 500，而是从 `source/` 章节生成预览并返回 `missing` / `damaged` 空态。
  - React 世界锚定页新增「导入检查」区，展示来源、章节数、平均字数、风险提示、章节片段和下一步建议；坏 zip / epub / 空文件 / 章节过少返回更明确的 400 或 job failed 错误。
- **测试**：新增 `tests/test_v086_long_import_review.py`（4 passed）；导入相关回归 `22 passed`；完整后端 `python -m pytest -q` 为 **577 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **明确未做**：真正多请求断点续传/恢复、持久化 ingest job、epub spine 精排、角色抽取置信度、时间线语义风险增强、向量库、runner 状态执行。
- **下一刀建议**：进入 `v0.8.7 Resumable Ingest Jobs`，做服务端分片 session、断点续传/恢复、hash 校验、重复 chunk 幂等与过期清理。

### 2026-05-31 — v0.8.7 Resumable Ingest Jobs

- **做了什么**：
  - 新增 `service/ingest_sessions.py`，以本地持久化 manifest + chunk 文件实现导入上传 session：创建 session、查询缺失分片、写入分片、重复 chunk 幂等、chunk/full-file sha256 校验、缺片/冲突/过期清晰降级。
  - 新增 HTTP 接口：`POST /api/ingest-sessions`、`GET /api/ingest-sessions/<session_id>`、`POST /api/ingest-sessions/<session_id>/chunks`、`POST /api/ingest-sessions/<session_id>/complete`；complete 后复用既有 `import_novel_from_payload()` 与 import job，不改导入 artifact 契约。
  - React 导入页改为 session 上传：创建或恢复 localStorage 里的 session id，只补传缺失分片，逐片计算 sha256，上传完成后触发 complete job 并进入世界锚定页。
- **测试**：新增 `tests/test_v087_resumable_ingest_jobs.py`（4 passed）；导入/job 回归 `28 passed`；完整后端 `python -m pytest -q` 为 **581 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **明确未做**：云端多用户持久队列、对象存储、跨设备恢复、分片并发上传、前端 session 列表管理、epub spine 精排、长篇项目资产页。
- **下一刀建议**：进入 `v0.8.8 Long Project Workspace`，做长篇项目详情页，集中展示章节、记忆、正史账本、实体别名、检索命中与审计报告，并提供从项目发起 baseline/intervention 的入口。

### 2026-05-31 — v0.8.8 Long Project Workspace

- **做了什么**：
  - 新增 `browser.indexer.get_project_workspace()` 与 `GET /api/stories/<slug>/project-workspace`，把导入检查、章节预览、分层记忆 manifest、`canon_ledger.jsonl`、`entity_aliases.yaml`、最近运行检索命中和 `consistency_report.json` 聚合成项目级只读工作台数据。
  - 章节、记忆、正史账本、审计报告缺失或损坏时返回 `missing` / `damaged` 空态和中文 warning，不抛 500；HTTP slug 继续走 `safe_id`，非法 slug 返回 400，缺失项目返回 404。
  - React `WorkspacePage` 在未选择世界线时展示长篇项目工作台：项目指标、导入风险、下一步建议、章节片段、分层记忆、正史样例、检索命中、审计风险和世界锚定/继续阅读入口；选中世界线后保留原阅读、右侧机制档案与干预体验。
- **测试**：新增 `tests/test_v088_long_project_workspace.py`（3 passed）；完整后端 `python -m pytest -q` 为 **584 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **明确未做**：长篇 Canon Replay / Consistency Audit 的专门 UI、章节范围 replay、运行后审计写回、runner 状态执行层。
- **下一刀建议**：进入 `v0.8.9 Long Replay & Audit UI`，把长篇 Canon Replay 与 Consistency Audit 做成可按章节范围、风险维度、实体别名归一化查看的前端工作流。

### 2026-05-31 — v0.8.9 Long Replay & Audit UI

- **做了什么**：
  - 新增 `run_canon_replay_range()`，支持按章节范围批量运行正史回放，写 `outputs/<baseline_run_id>/canon_replay_range_report.json`，汇总平均分、风险等级、弱章、风险维度和实体归一化审计。
  - 新增 HTTP 接口：`GET /api/stories/<slug>/replay-audit` 聚合 baseline、range replay、静态审计维度、实体别名和下一步建议；`POST /api/stories/<slug>/canon/replay-range` 执行范围回放。slug/run/branch 均走 `safe_id`，非法、缺失、冲突降级为 400/404/409 或前端空态。
  - React 「回放与审计」面板支持 holdout 状态、单章回放、章节范围回放、风险维度、实体审计和空态提示，文案保持中文纸面风格。
- **测试**：新增 `tests/test_v089_long_replay_audit_ui.py`（3 passed）；Canon Replay 回归 `46 passed`；完整后端 `python -m pytest -q` 为 **587 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **明确未做**：runner 状态执行层、运行后审计写回、LLM 语义 replay、云端批量队列和向量库。
- **下一刀建议**：进入 `v0.8.10-A Runner State Execution Spike`，opt-in 评估动作计划、动作注册表、涌现节点是否能安全转成状态变化；继续不改 `run_scene` 默认行为。

### 2026-05-31 — v0.8.10-A Runner State Execution Spike

- **做了什么**：
  - 新增 `runner_state_execution_report.json` dry-run 报告，读取 `act_director_plan.json`、`dynamic_action_registry.yaml` 与 `emergence_nodes.json`，生成候选状态变化、gate 状态、阻断原因、warnings 与 MVP 前置清单。
  - 新增 HTTP 接口：`POST /api/runs/<run_id>/state-execution-evaluate` 生成评估，`GET /api/runs/<run_id>/state-execution-report` 读取报告；run id 走安全校验，缺失报告 404、损坏报告 400、缺必要 artifact 409。
  - `get_branch()` additive 返回 `runner_state_execution_report`；React 右侧「机制档案」新增「状态执行评估」区，可生成/重评估报告并展示候选变化、阻断与安全说明。
- **测试**：新增 `tests/test_v0810_runner_state_execution.py`（4 passed）；相关机制回归 `15 passed`；默认 runner 契约回归 `12 passed`；完整后端 `python -m pytest -q` 为 **591 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **明确未做**：不写 `state_snapshot.json`，不改变 `run_scene` 默认行为，不把 action/emergence 自动应用到真实状态；运行后审计写回、LLM 语义 replay、向量库和云端队列仍留后续。
- **下一刀建议**：进入 `v0.8.10-B Runner State Execution MVP`，仅在 opt-in 下把白名单、低风险 dry-run delta 最小写入可回滚状态层，并补审计/回滚/冲突测试。

### 2026-05-31 — v0.8.10-B Runner State Execution MVP

- **做了什么**：
  - 新增 `apply_runner_state_execution()`：必须 `confirm=True` 才会从 dry-run 报告里挑选 `executable`、`low` risk、白名单字段的 delta，按分支写入 `state_execution_overlay.json`。
  - 新增 `rollback_runner_state_execution()`：移除 overlay 并写 `runner_state_execution_rollback_report.json`，同时把 apply 报告标记为 `rolled_back`；原 `state_snapshot.json` 不被覆盖。
  - 新增 HTTP 接口 `POST /api/runs/<run_id>/state-execution-apply` 与 `POST /api/runs/<run_id>/state-execution-rollback`；未确认 400，缺评估/应用报告 404，无可应用候选 409，坏 id 400。
  - `get_branch()` additive 返回 `state_execution_overlay`、`runner_state_execution_apply_report`、`runner_state_execution_rollback_report`；前端「状态执行评估」区新增应用低风险状态与回滚覆盖层按钮。
- **测试**：`tests/test_v0810_runner_state_execution.py` 扩充至 8 passed；相邻机制/runner 契约回归 `31 passed`；完整后端 `python -m pytest -q` 为 **595 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **明确未做**：overlay 暂不驱动下一轮 runner 自动消费；运行后审计写回、LLM 语义 replay、向量库、云端队列和真实多用户权限仍留后续。
- **下一刀建议**：进入 `v0.9.0-alpha Long Novel Creation Loop`，把上传/创建、项目资产、分支运行、审计、世界线选择和章节导出串成第一条长篇共创产品闭环。

### 2026-05-31 — v0.9.0-alpha Chapter Export

- **做了什么**：
  - 新增 `service/chapter_export.py`：`build_chapter_export()` 只读读取所选 run/branch 的 `chapter.md`、`intervention.json`、`intervention_compilation.json`、`events.json`、`worldline_judgement.json`、`causal_diff.json` 与 `state_execution_overlay.json`，生成 Markdown 导出 payload。
  - 新增 HTTP `GET /api/runs/<run_id>/branches/<branch_id>/chapter-export`；run/branch id 走 `safe_id`，坏 id 返回 400，缺章节返回 404；接口不写 artifact、不改 `chapter.md`、不改 `state_snapshot.json` 与 `run_scene` 默认行为。
  - React 阅读工作台新增「导出章节」按钮，下载当前世界线 Markdown，内容包含导出信息、来源说明、AI 生成说明、世界线评审摘要和章节正文；无正文时禁用，失败显示中文错误。
- **测试**：新增 `tests/test_v090_long_creation_loop.py`（3 passed：导出内容、坏 id/缺章节、HTTP 状态）；完整后端 `python -m pytest -q` 为 **598 passed**；前端 `pnpm run build` 通过。
- **明确未做**：还未把 v0.9.0-alpha 整条路径标记为完成；尚未做“选择世界线”持久化、运行后审计写回、章节合集/多章导出、公开分享、版权工作流、provider/cost gateway。
- **下一刀建议**：继续 v0.9.0-alpha，做“世界线选择/继续创作清单”子刀：把 Worldline Judge、Causal Diff 状态、Replay/Audit 与导出状态聚合成项目级 creation loop checklist，帮助用户决定继续哪条线。

### 2026-05-31 — v0.9.0-alpha Creation Loop Checklist

- **做了什么**：
  - `get_project_workspace()` 版本提升为 `v0.9.0-alpha`，additive 返回 `creation_loop`，包含推荐世界线、候选分支、导入/分支/评审/审计/导出五步清单和中文下一步。
  - `creation_loop` 只读扫描既有 run/branch artifact：`chapter.md`、`worldline_judgement.json`、`causal_diff.json`、`state_execution_overlay.json` 与 child run 关系；不写新 artifact，不改 `run_scene` 默认行为。
  - React 长篇项目工作台新增「创作闭环」区，展示推荐继续世界线、清单状态和下一步提醒，可打开推荐分支继续阅读/导出。
- **测试**：`tests/test_v090_long_creation_loop.py` 扩充到 4 passed；`tests/test_v088_long_project_workspace.py` 确认 HTTP additive 字段；相邻测试 7 passed；完整后端 `python -m pytest -q` 为 **599 passed**；前端 `pnpm run build` 通过。
- **明确未做**：还未做“选择世界线”持久化、运行后审计写回、自动继续生成下一章、多章节合集导出、公开分享、版权工作流、provider/cost gateway。
- **下一刀建议**：继续 v0.9.0-alpha，做“选中世界线 -> 继续生成/续写入口”子刀：基于 creation_loop 推荐分支给出明确续写入口或 job 状态，不改 `run_scene` 默认行为。

### 2026-05-31 — v0.9.0-alpha Continuation Hint

- **做了什么**：前端「创作闭环」推荐世界线下新增 `续写入口` 命令展示，直接露出 `creation_loop.recommended.continue_hint`（例如 `lne resume continue <run_id> --branch <branch_id> --mock`）。
- **边界**：这不是 HTTP 续写 job，只是把已有 CLI 续写入口产品化展示；不写新 artifact，不改 `run_scene` 默认行为，不接真实外网。
- **测试**：`tests/test_v090_long_creation_loop.py` 断言推荐分支包含 `continue_hint`；完整后端仍为 **599 passed**；前端 `pnpm run build` 通过。
- **下一刀建议**：若继续 v0.9.0-alpha，可抽取 `resume continue` service 并新增 opt-in HTTP job；这会牵涉 CLI 逻辑复用、父链安全校验和 job 轮询，不宜和纯展示混在一刀。

### 2026-05-31 — v0.9.0-alpha Resume Continue HTTP Job

- **做了什么**：
  - 新增 `service/resume_continue.py`：抽出 console-free `run_resume_continue()`，复用父快照投影、`build_continuation_spec()`、runtime memory 检索、第四面墙 lineage 账本与 `write_resume_output()`，生成新的 `linear` 子 run。
  - 新增异步 HTTP job：`POST /api/jobs/resume-continue`，body 为 `run_id`、`branch_id`、可选 `rounds/mock/runner_name`；run/branch 走 `safe_id`，坏 id 直接 400，业务失败进入 job failed。
  - React「创作闭环」区新增「生成下一章」按钮，沿推荐世界线触发续写 job，成功后自动跳到新 run 的 `linear` 分支；保留 CLI `续写入口` 作为可复制备选。
  - `resume.loader` 尊重 `LNE_OUTPUTS_DIR`，保证 HTTP job 与测试隔离目录能读取父 run；默认输出目录不变。
- **测试**：新增/扩充 v0.9.0-alpha 与 job 测试，覆盖 service 写出 `linear`、坏 id、HTTP job 成功与分支读取；完整后端 `python -m pytest -q` 为 **602 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：不改 `run_scene` 默认行为，不写 `intervention.json`，不覆盖父分支 `chapter.md/events.json/state_snapshot.json`；仍未做“选择世界线”持久化、运行后审计写回、多章导出、分享/版权工作流和 provider/cost gateway。
- **下一刀建议**：继续 v0.9.0-alpha，做“运行后审计/选择世界线状态”子刀：把续写后的 `linear` 与父分支在项目工作台中形成可复盘的选择记录或审计入口。

### 2026-05-31 — v0.9.0-alpha Worldline Selection Persistence

- **做了什么**：
  - 新增 `service/worldline_selection.py`：`select_worldline()` / `get_selected_worldline()` 校验 story/run/branch，确认 run 属于当前 story 后写 `selected_worldline.json` additive 记录。
  - 新增 HTTP 接口：`GET/POST /api/stories/<slug>/selected-worldline`，坏 slug/run/branch 返回 400，缺故事或分支返回 404，损坏选择记录降级为 `damaged` 空态。
  - `get_project_workspace()` 的 `creation_loop` 读取 `selected` 并给候选分支标记 `is_selected`；React「创作闭环」新增「设为起点」按钮和“已选起点”展示。
- **测试**：`tests/test_v090_long_creation_loop.py` 扩充到 7 passed，覆盖 service 持久化、workspace 聚合、HTTP 状态和坏 id；完整后端 `python -m pytest -q` 为 **604 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：选择记录只作为项目工作台状态，不改变推荐排序、不驱动 runner、不改 `chapter.md/events.json/state_snapshot.json`；仍未做运行后审计写回、多章导出、分享/版权工作流和 provider/cost gateway。
- **下一刀建议**：继续 v0.9.0-alpha，做“运行后审计写回/选择后审计入口”子刀：围绕已选世界线展示审计状态、缺口与下一步操作，而不是引入重依赖。

### 2026-05-31 — v0.9.0-alpha Post-run Audit Entry

- **做了什么**：
  - `creation_loop.post_run_audit` additive 聚合已选世界线、世界线评审、Causal Diff、静态一致性审计和章节范围回放摘要，返回风险等级、缺失实体、下一步动作与 `#/anchor/<slug>` 回放审计入口。
  - `creation_loop.checklist` 增加「选择后审计」步骤；React「创作闭环」区展示选择后审计状态、范围回放状态、风险等级和缺失实体，并提供「查看回放与审计」按钮。
  - 保持只读入口，不写正史账本、不驱动 runner、不改既有 run artifact。
- **测试**：`tests/test_v090_long_creation_loop.py` 扩充到 8 passed；完整后端 `python -m pytest -q` 为 **605 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：仍未做多章节合集导出、公开分享/版权工作流、provider/cost gateway；运行后审计尚未写回正史账本或驱动下一轮 runner。
- **下一刀建议**：继续 v0.9.0-alpha，做“多章节合集导出/闭环收口”子刀：基于已选世界线和 child run lineage 导出连续章节合集，继续保持只读、additive、不过度商业化。

### 2026-05-31 — v0.9.0-alpha Chapter Collection Export

- **做了什么**：
  - 新增 `build_chapter_collection_export()` 与 `GET /api/runs/<run_id>/branches/<branch_id>/chapter-collection-export`，沿 `meta.parent_run_id` / `meta.parent_branch` 导出父链章节合集。
  - React 阅读区新增「导出合集」按钮，与「导出章节」并列；成功/失败局部中文提示。
  - 合集只读，不写 artifact，不改 runner，不导出上传原作全文或 holdout 私有正文；父链缺失时安全截断并返回 warning。
- **测试**：`tests/test_v090_long_creation_loop.py` 扩充到 10 passed；完整后端 `python -m pytest -q` 为 **607 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：仍未做公开分享/版权工作流、provider/cost gateway；运行后审计仍未写回正史账本或驱动下一轮 runner。
- **下一刀建议**：继续 v0.9.0-alpha，做“导出版权/分享前检查”或“v0.9.0-alpha 闭环验收清单”小刀，不跳商业化重构。

### 2026-05-31 — v0.9.0-alpha Export Share Guard

- **做了什么**：
  - 单章导出与合集导出新增 additive `share_guard`，返回私用允许、公开分享不默认放行、分享前需确认权利来源等机器可读边界。
  - Markdown 导出新增「版权与分享边界」段落，强调仅本地个人评估、公开分享/发布/商用前需确认授权，不公开分发受保护原文或可替代原作阅读的内容。
  - React 阅读区点击「导出章节」或「导出合集」时先弹出中文确认；取消则不生成下载文件。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 guard 红灯，再补实现到 10 passed；完整后端 `python -m pytest -q` 为 **607 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：不新增公开分享发布入口，不写 artifact，不改 runner；provider/cost gateway 和云端商业化能力仍后置。
- **下一刀建议**：继续 v0.9.0-alpha，做“闭环验收清单/完成度判定”小刀，确认上传 -> 审计 -> 选择 -> 续写 -> 导出的用户路径是否可标记 alpha 收口。

### 2026-05-31 — v0.9.0-alpha Creation Loop Completion Gate

- **做了什么**：
  - `creation_loop.checklist` 新增「确认版权边界」步骤，把 Export Share Guard 纳入长篇共创闭环。
  - 新增 additive `creation_loop.completion`，返回 `done_count`、`total_count`、`blocking_ids`、`blocking_labels`、`summary` 和 `can_mark_alpha_complete`。
  - React「创作闭环」区顶部展示闭环完成度、summary 和最多三个待处理项。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 `export_share_guard` 与 `completion` 红灯，再补实现到 10 passed；完整后端 `python -m pytest -q` 为 **607 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：只读判定，不写 artifact，不自动宣告版本完成；仍需根据 completion 阻塞项做最终 alpha 收口判断。
- **下一刀建议**：若 completion 已只剩风险项，做 v0.9.0-alpha 收口判定文档/轻量验收；如果仍有 todo，则优先补齐 todo，而不是进入 v0.9.1。

### 2026-05-31 — v0.9.0-alpha Creation Loop Action Hints

- **做了什么**：
  - `creation_loop.completion.actions` additive 返回阻塞项动作：生成世界线评审、设为下一章起点、查看回放与审计。
  - React「创作闭环」完成度区展示快捷动作；「生成世界线评审」复用既有 `POST /api/runs/<run_id>/branches/<branch_id>/worldline-judgement` 并刷新工作台。
  - 真实 completion 的 todo 不再只是文字，能直接引导用户补评审、选起点或进入审计。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 `completion.actions` 红灯，再补实现到 **11 passed**；完整后端 `python -m pytest -q` 为 **608 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：不新增新 runner 行为，不写额外 artifact，不替代回放审计本身；公开分享发布、provider/cost gateway 仍后置。
- **下一刀建议**：继续围绕 completion 剩余 todo 做轻量推进，优先让“回放审计 / 选择后审计”从跳转变成更明确的工作台闭环，而不是进入 v0.9.1。

### 2026-05-31 — v0.9.0-alpha Creation Loop Readiness Evidence

- **做了什么**：
  - `creation_loop.completion.evidence` additive 返回每个清单项的判定来源：artifact、API、页面 hash 或当前状态。
  - React「创作闭环」完成度区新增「判定依据」，用中文展示依据类型，具体 ref 仅作为悬停 title。
  - 判定依据不暴露绝对路径，只指向相对 artifact 名称、API path 或前端 route hash。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 `completion.evidence` 红灯，再补实现到 **11 passed**；完整后端 `python -m pytest -q` 为 **608 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：只读解释层，不写 artifact，不改变 runner 或 completion 判定；v0.9.0-alpha 仍未因该字段自动宣告整体完成。
- **下一刀建议**：继续围绕 completion 的真实剩余阻塞推进，优先把“回放审计/选择后审计”做成更直接的工作台闭环；若样例能达到 ready，再做 alpha 收口验收。

### 2026-05-31 — v0.9.0-alpha Creation Loop Audit Quick Run

- **做了什么**：
  - `completion.actions` 在已选世界线缺范围回放、且存在 baseline/holdout 时返回 `run_replay_range`。
  - action payload 复用既有 `POST /api/stories/<slug>/canon/replay-range`：`baseline_run_id`、`baseline_branch_id`、`chapter_start`、`chapter_end`。
  - React「创作闭环」完成度区可直接运行范围回放，成功后刷新工作台，让「选择后审计」状态即时更新。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 `run_replay_range` 红灯，再补实现到 **12 passed**；完整后端 `python -m pytest -q` 为 **609 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：不新增 API，不改 runner；只触发现有 `canon_replay_range_report.json` 写入链路；公开分享发布、provider/cost gateway 仍后置。
- **下一刀建议**：继续围绕 completion ready 条件做 alpha 收口验收，检查样例/导入项目是否能从工作台走到 `can_mark_alpha_complete=true`。

### 2026-05-31 — v0.9.0-alpha Creation Loop Alpha Ready State

- **做了什么**：
  - 新增 ready fixture：clean 导入审计、候选世界线、世界线评审、Causal Diff、低风险范围回放、已选起点、章节导出和版权 guard 全部满足时，`completion.status=ready` 且 `can_mark_alpha_complete=true`。
  - React「创作闭环」标题状态在 ready 时显示「可收口」，避免只显示“可继续”。
  - 测试同时确认 ready 状态下 `blocking_ids=[]`、`actions=[]`。
- **测试**：补 `tests/test_v090_long_creation_loop.py` ready-state 覆盖到 **13 passed**；完整后端 `python -m pytest -q` 为 **610 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：不自动修改版本号、不写发布 artifact、不跳 v0.9.1；只是提供可验证的 alpha ready 状态。
- **下一刀建议**：若要正式收口 v0.9.0-alpha，下一步应做 docs/README 中的 alpha 收口声明与真实样例验收记录；公开分享、provider/cost gateway 仍不进本阶段。

### 2026-05-31 — v0.9.0-alpha Creation Loop Alpha Closeout Report

- **做了什么**：
  - `creation_loop.closeout` additive 返回 `creation_loop_alpha_closeout`，把 completion 的 ready 状态、阻塞项、判定依据和下一步收口建议整理成正式只读验收报告。
  - React「创作闭环」区新增「Alpha 收口」面板：ready 时显示「可收口」，否则显示「待补齐」和剩余阻塞。
  - closeout 只从现有 checklist/completion/evidence 派生，不写 artifact、不改变 runner、不自动把版本标为完成。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 `creation_loop.closeout` 红灯，再补实现到 **13 passed**；完整后端 `python -m pytest -q` 为 **610 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：仍不新增公开分享发布、provider/cost gateway、审计写回正史账本或 overlay 驱动下一轮 runner。
- **下一刀建议**：用真实样例或导入项目跑到 `closeout.status=ready` 后，再做 v0.9.0-alpha 文档收口；否则继续补 `remaining_blockers`，不要跳 v0.9.1。

### 2026-05-31 — v0.9.0-alpha Creation Loop Closeout API

- **做了什么**：
  - 新增只读 `GET /api/stories/<slug>/creation-loop-closeout`，直接返回 `story_slug`、`version` 和 `closeout`，复用项目工作台的 `creation_loop.closeout`。
  - slug 继续走 `safe_id`，非法 slug 返回 400；接口不写 artifact、不改 workspace 主结构、不改 runner。
  - 补 HTTP ready fixture：导入项目在 clean audit、评审、Causal Diff、低风险范围回放、已选起点、章节导出和版权 guard 满足时，接口返回 `closeout.status=ready`。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 closeout HTTP 接口红灯，再补实现到 **14 passed**；完整后端 `python -m pytest -q` 为 **611 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：这是自动验收入口，不是版本发布按钮；不新增公开分享、provider/cost gateway 或审计写回。
- **下一刀建议**：用该接口对真实样例/导入项目做收口记录；若样例仍 `not_ready`，优先补真实阻塞项。

### 2026-05-31 — v0.9.0-alpha Creation Loop Closeout API Actions

- **做了什么**：
  - `GET /api/stories/<slug>/creation-loop-closeout` 额外返回 `completion_status` 与 `actions`，复用 `creation_loop.completion.actions`。
  - ready 项目返回空 actions；not_ready 项目返回可执行/可跳转动作，例如生成世界线评审、设为起点、查看回放与审计。
  - 字段仍只读，不写 artifact、不执行动作、不改变 project workspace 主结构。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 `completion_status/actions` 红灯，再补实现到 **15 passed**；完整后端 `python -m pytest -q` 为 **612 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：只给自动化和 UI 提示提供动作清单，不自动代表用户选择，不直接调用 LLM 或写入审计结果。
- **下一刀建议**：用 actions 对本地 `tianhuang-night` 或导入项目逐项补齐阻塞；如果仍无法 ready，再记录真实阻塞原因。

### 2026-05-31 — v0.9.0-alpha Creation Loop Action Payloads

- **做了什么**：
  - `completion.actions` 中的 `select_worldline` 现在带 `payload`：`run_id`、`branch_id`、`note`，调用者可直接 POST 到 `/api/stories/<slug>/selected-worldline`。
  - `worldline_judgement` action 现在带 `payload`：`story_slug`，调用者可直接 POST 到 `/api/runs/<run_id>/branches/<branch_id>/worldline-judgement`。
  - 前端类型把 `ProjectCreationLoopAction.payload` 扩展为 `CanonReplayRangeRequest | WorldlineSelectionRequest | WorldlineJudgementRequest`，兼容范围回放、设为起点和生成评审三类动作。
  - 这些 payload 只描述建议动作，不自动选择世界线、不自动生成评审。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 `select_worldline.payload` 红灯，再补实现到 **15 passed**；完整后端 `python -m pytest -q` 为 **612 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：不改选择 API、不写 artifact、不代表用户已确认；仍需调用方显式 POST。
- **下一刀建议**：继续补齐 closeout actions 中其他动作的可执行参数或对本地样例执行阻塞清单。

### 2026-05-31 — v0.9.0-alpha Creation Loop Stable Blocker IDs

- **做了什么**：
  - `creation_loop.closeout` 新增 additive `remaining_blocker_ids`，与 `completion.blocking_ids` 保持一致。
  - 保留原有 `remaining_blockers` 中文 label，前端类型同步新增字段；UI 展示不变。
  - 该字段用于 closeout API 和自动化验收稳定识别阻塞项，避免脚本解析中文文案。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 `remaining_blocker_ids` 红灯，再补实现到 **15 passed**。
- **边界**：不执行动作、不写 artifact、不改变 ready 判定。
- **下一刀建议**：继续对真实样例执行 closeout actions，或补充无法自动执行的 `replay_audit` 阻塞解释。

### 2026-05-31 — v0.9.0-alpha Replay Audit Action Requirements

- **做了什么**：
  - `replay_audit` action 新增 additive `requirements`，列出无法直接运行范围回放时缺少的前置条件。
  - 当前可识别 `selected_worldline`、`baseline_run`、`canon_holdout`；如果已有范围回放但仍有风险，则提示 `review_replay_risk`。
  - 前端类型同步新增 `ProjectCreationLoopActionRequirement`，UI 展示不变。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 `replay_audit.requirements` 红灯，再补实现到 **15 passed**。
- **边界**：只读解释，不生成 baseline、不写 holdout、不执行范围回放、不改变 closeout ready 判定。
- **下一刀建议**：用真实样例按 action payload 补齐评审与起点后，继续检查是否能进入范围回放 quick run。

### 2026-05-31 — v0.9.0-alpha Requirements UI Display

- **做了什么**：
  - React「创作闭环」完成度区在 action 带 `requirements` 时显示「审计前置」。
  - requirements 最多展示前三项中文 label，详情保留在 hover title；按钮行为不变。
  - CSS 保持 v0.7 工作台克制纸面风格，移动端左对齐。
- **测试**：完整后端 `python -m pytest -q` 为 **612 passed**；前端 `pnpm run build` 通过；Vite 首页 HTTP 200；`git diff --check` 通过。
- **边界**：只展示现有 API 字段，不新增按钮、不自动执行 action。

### 2026-05-31 — v0.9.0-alpha Builtin Holdout Blocked Requirement

- **做了什么**：
  - `replay_audit.requirements` 在缺少 holdout 时会读取 story source kind。
  - builtin 样例（如 `tianhuang-night`）无法录入 holdout 时，`canon_holdout.status` 从 `missing` 改为 `blocked`。
  - detail 明确提示“内置样例只读，需导入长篇项目后录入 holdout 章节”。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因 builtin holdout 仍为 `missing` 红灯，再补实现到 **16 passed**；完整后端 `python -m pytest -q` 为 **613 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：不改变 imported 项目的 holdout 流程，不自动导入项目、不写 holdout。

### 2026-06-01 — v0.9.0-alpha Creation Loop Closeout CLI

- **做了什么**：
  - 新增 `lne creation-loop-closeout <slug>`，复用项目工作台的 `creation_loop.closeout` 只读判定，在本地 CLI 输出 closeout 状态、阻塞 id、阻塞动作与下一步。
  - 支持 `--json` 输出与 HTTP closeout 接口同构的 `story_slug/version/completion_status/actions/closeout` payload。
  - 支持 `--require-ready`：当 `closeout.can_close_alpha=false` 时以退出码 1 失败，可作为导入项目 alpha 收口闸门。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 CLI 命令红灯，再补实现到 **18 passed**；完整后端 `python -m pytest -q` 为 **615 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：CLI 只读，不写 artifact、不执行 action、不替代用户选择、不改变 `run_scene` 默认行为；v0.9.0-alpha 仍需真实/导入项目跑到 ready 后再整体收口。

### 2026-06-01 — v0.9.0-alpha Creation Loop Closeout Record

- **做了什么**：
  - `lne creation-loop-closeout <slug>` 新增 `--write-report`。
  - 当 `creation_loop.closeout.can_close_alpha=true` 时，CLI 会在导入项目目录写入 additive `creation_loop_alpha_closeout.json`。
  - 记录包含 `story_slug`、`version`、`completion_status`、`actions`、`closeout` 与 `created_at`，可作为 alpha 收口闸门通过后的本地证据。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因缺少 `--write-report` 红灯，再补实现到 **19 passed**；完整后端 `python -m pytest -q` 为 **616 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：未 ready 时不写报告；builtin 样例无项目目录时不可写；不执行 action、不替代用户选择、不改变 `run_scene` 默认行为。

### 2026-06-01 — v0.9.0-alpha Low-risk Audit Closeout / Alpha Closure

- **做了什么**：
  - 修正 `creation_loop` ready 判定：静态一致性审计里 `risk_level=low` 的 info 提示不再阻断 `replay_audit` / `post_run_audit` / closeout ready。
  - 中高风险静态审计、范围回放中高风险、缺失实体、缺评审、缺选择、缺导出仍会阻断 alpha closeout。
  - 新增 `docs/completed/v0.9.0-alpha-long-creation-loop.md`，记录 v0.9.0-alpha 收口范围、证明、边界与下一步。
  - 本地导入项目 `v090-alpha-proof` 已跑通 `lne creation-loop-closeout v090-alpha-proof --require-ready --write-report --json`，结果 `ready_count=7/7`、`remaining_blocker_ids=[]`，并写入 `creation_loop_alpha_closeout.json`。
- **测试**：先让 `tests/test_v090_long_creation_loop.py` 因低风险 info 审计仍阻断 ready 红灯，再补实现到 **20 passed**；完整后端 `python -m pytest -q` 为 **617 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：未做公开分享发布、provider/cost gateway、云端队列、对象存储、向量库、overlay 自动驱动下一轮 runner、运行后审计写回正史账本；这些进入 v0.9.1+ 或更后阶段。

### 2026-06-01 — v0.9.1 Provider Gateway Summary-A

- **做了什么**：
  - `service/runtime_settings.py` 新增 `get_provider_gateway_summary()`，把当前进程内 LLM 与 Seedream 设置解释成只读 provider 列表、单 provider 路由状态、降级策略、成本观测口径和 warning。
  - 新增 `GET /api/settings/providers`，返回 `version=v0.9.1-provider-cost-lite`、`routing`、`providers`、`cost_policy` 与 `warnings`；不创建客户端、不打网络、不落盘。
  - 响应只含脱敏尾号与 base_url/model，不返回明文 Key，也不暴露环境变量名；未配置或 mock 时明确标记降级到本地 mock/占位图。
- **测试**：先让 `tests/test_runtime_settings_api.py` 因缺少 `get_provider_gateway_summary` 红灯，再补实现到 **19 passed**；完整后端 `python -m pytest -q` 为 **620 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：当前只做 provider/cost gateway 的只读摘要与成本观测口径，不改 LLM/Seedream 调用链，不引入真实价格表，不改 `run_scene` 默认行为。
- **下一刀建议**：继续 v0.9.1 的成本聚合或模型路由配置，让已有 `generation_meta.usage` 能在项目/运行维度汇总展示。

### 2026-06-01 — v0.9.1 Provider Usage Summary-B

- **做了什么**：
  - `service/runtime_settings.py` 新增 `get_provider_usage_summary(story_slug=None)`，只读扫描 `outputs/run_*/intervention_compilation.json` 与分支 `multi_agent_trace.json` 中的 `generation_meta.usage`。
  - 新增 `GET /api/settings/provider-usage`，支持可选 `story_slug` 过滤并走 `safe_id` 校验；非法 story slug 返回 400。
  - 汇总返回 `totals`、`by_provider`、前 50 条 usage record、缺失 usage 的 meta 计数，以及 `price_table_not_configured` 的空成本估算。
- **测试**：先让 `tests/test_runtime_settings_api.py` 因缺少 `get_provider_usage_summary` 红灯，再补实现到 **23 passed**；完整后端 `python -m pytest -q` 为 **624 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：只聚合已有 usage metadata，不读取 Key、不打网络、不内置真实价格，不改变任何 run artifact 或模型调用链。
- **下一刀建议**：继续 v0.9.1 的模型路由/价格表配置，或把 provider gateway 与 usage 汇总接入设置页的中文可视化。

### 2026-06-01 — v0.9.1 Provider Status Panel-C

- **做了什么**：
  - 前端类型与 API client 新增 `ProviderGatewaySummary` / `ProviderUsageSummary`、`getProviderGateway()` 与 `getProviderUsage()`。
  - `SettingsDrawer` 新增「模型与用量状态」只读区，展示主文本模型和视觉模型的配置/启用状态、模型名、累计用量、输入/输出用量、缺失 usage 记录提示和 provider warning。
  - 保存设置或清除文本模型密钥后，会刷新 provider 状态；不新增任何 Key 持久化或配置写入。
- **测试/验证**：前端 `pnpm run build` 通过；本地启动 `lne browse` + Vite，HTTP 冒烟确认首页 200、`/api/settings/providers` 200、`/api/settings/provider-usage` 200；后端基线仍为 **624 passed**。
- **边界**：仅设置抽屉可视化，不新增价格表、不新增模型路由写入，不读取或展示明文 Key。
- **下一刀建议**：继续 v0.9.1 的价格表配置或路由策略配置；若先做 UI，则保持只读/脱敏。

### 2026-06-01 — v0.9.1 Manual Price Estimate-D

- **做了什么**：
  - 运行设置新增 `llm_input_cost_per_1k` / `llm_output_cost_per_1k`，只写当前进程环境变量，不落盘。
  - `GET /api/settings/providers` 的 `cost_policy` 返回手动单价和 `price_table_status`。
  - `GET /api/settings/provider-usage` 在用户配置单价后，用已有 prompt/completion 用量估算费用；未配置时保持 `estimated_total=null`。
  - 设置抽屉新增「成本估算」输入区，用户可手动填写每千输入/输出单价，用量区显示估算金额。
- **测试/验证**：先让设置测试因缺少单价字段与估算红灯，再补实现到 **25 passed**；两个旧 HTTP bad-id 失败单独复跑通过；完整后端目标基线 **626 passed**；前端 `pnpm run build` 通过。
- **边界**：不硬编码厂商价格，不联网查价，不写项目 artifact，不改变模型调用链；估算只供本机粗略参考。
- **下一刀建议**：继续 v0.9.1 的模型路由配置，明确不同生成入口使用哪个 provider / runner。

### 2026-06-01 — v0.9.1 Route Matrix-E

- **做了什么**：
  - `GET /api/settings/providers` 新增 `routes`，列出读者干预生成、主题创世、导入抽取、视觉资产生成四个入口当前对应的 provider、mode、runner 与 fallback。
  - 设置抽屉「模型与用量状态」新增路由矩阵行，让用户看到每个入口走主文本模型、本地模拟、Seedream、占位图或关闭状态。
- **测试/验证**：设置测试扩充 route 断言后仍为 **25 passed**；前端 `pnpm run build` 通过；完整后端目标基线仍为 **626 passed**。
- **边界**：只读展示路由，不新增路由写入开关，不改变默认 mock / runner / Seedream 调用行为。
- **下一刀建议**：核对 v0.9.1 是否已满足 docs 中的多 provider 配置、模型路由、成本/用量估算、失败回退与 Key 脱敏展示，若满足则做 v0.9.1 收口文档。

### 2026-06-01 — v0.9.1 Provider & Cost Gateway Lite 收口

- **做了什么**：
  - 新增 `docs/completed/v0.9.1-provider-cost-gateway-lite.md`，归档 Provider Gateway Summary-A、Provider Usage Summary-B、Provider Status Panel-C、Manual Price Estimate-D 与 Route Matrix-E 的目标、完成范围、收口证明、边界和验证命令。
  - `docs/index.md` 登记 v0.9.1 收口文档；路线、PRD、handoff、README、UI spec 和本文件同步推进到 v0.9.2。
- **测试/验证**：文档归档切片仍跑完整门禁：后端 **626 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：v0.9.1 Lite 已收口，但仍不做持久化 Key、完整商业网关、可写路由策略、厂商价格表、云端队列、对象存储或多租户配置中心。
- **下一刀建议**：进入 v0.9.2 MasterSetting Workspace Lite，先做项目工作台中设定/人物/时间线/道具/伏笔/章节摘要的只读聚合，再评估最小轻编辑。

### 2026-06-01 — v0.9.2 MasterSetting Workspace Summary-A

- **做了什么**：
  - `get_project_workspace()` 新增 additive `master_setting_workspace`，从现有 `memory/` artifact 只读聚合 `master_setting.yaml`、`character_states/`、`timeline.yaml`、`plot_threads.yaml` 和 `chapters/`。
  - payload 返回 `summary`、`sections`、`world`、`characters`、`timeline`、`plot_threads`、`chapter_briefs`、`capabilities`、`next_steps` 与 `warnings`，作为后续前端面板/轻编辑的数据底座。
  - 损坏的 `master_setting.yaml` 降级为 `status=damaged` 与 warning；人物、时间线、伏笔、章节摘要仍尽量展示，不让工作台 500。
- **测试/验证**：先写红灯测试确认缺少 `master_setting_workspace`，实现后 `tests/test_v088_long_project_workspace.py` 为 **4 passed**；完整后端 **627 passed**，前端 `pnpm run build` 通过。
- **边界**：只读聚合，不写 artifact，不改导入结构，不改 runner，不做完整作者工作台。
- **下一刀建议**：把 `master_setting_workspace` 接到长篇项目工作台前端，展示设定概览、人物状态、时间线、伏笔和章节摘要；之后再评估最小轻编辑。

### 2026-06-01 — v0.9.2 MasterSetting Workspace Panel-B

- **做了什么**：
  - React 长篇项目工作台新增「设定工作台」只读面板，消费 `master_setting_workspace` 展示世界规则/限制/地点/势力、人物状态、时间线、伏笔线、章节摘要与后续建议。
  - 右侧项目资产面板新增「设定状态」，帮助用户在未选世界线时确认设定资料是否 ready/missing/damaged。
  - 对 `unknown` 结构化条目增加前端展示格式化，避免世界设定中对象/数组样例直接显示为英文占位或 `[object Object]`。
- **测试/验证**：前端 `pnpm run build` 已通过；完整后端、前端构建、浏览器冒烟与 diff check 在本刀提交前运行。
- **边界**：仍为只读展示，不写 `memory/` artifact，不做完整作者工作台，不改 runner。
- **下一刀建议**：继续 v0.9.2 最小轻编辑，优先做只改 `master_setting.yaml` 的安全保存/校验/回滚；或若不急编辑，则进入 v0.9.3 触发条件复核。

### 2026-06-01 — v0.9.2 MasterSetting Workspace Edit-C

- **做了什么**：
  - 新增 `service.master_setting_update.update_master_setting()`，允许对 `memory/master_setting.yaml` 的 `display_name`、`genre`、`world_rules`、`power_system_limits`、`forbidden_additions` 做白名单轻编辑。
  - 新增 `POST /api/stories/<slug>/master-setting`，slug 先走 `safe_id`；缺故事 404，损坏/缺失 `master_setting.yaml` 409，非法 payload 400。
  - 保存前备份原 `memory/master_setting.yaml` 到 `backups/<timestamp>/memory/master_setting.yaml`，保存后写 `memory/master_setting_update_report.json`，说明 changed、backup 与不同步 `world.yaml` / runner artifact 的边界。
- **测试/验证**：先补红灯测试，focused `tests/test_v092_master_setting_update.py` 为 **5 passed**；完整门禁本刀提交前运行。
- **边界**：不编辑人物状态、时间线、伏笔、章节摘要，不同步 `world.yaml`，不改 runner，不做完整作者工作台；前端写控件由 Frontend-D 子刀接入。
- **下一刀建议**：接前端最小写控件（只提交上述白名单字段）并刷新项目工作台，或若认为 v0.9.2 Lite 已够用，则做 v0.9.2 收口归档。

### 2026-06-01 — v0.9.2 MasterSetting Workspace Frontend-D

- **做了什么**：
  - 前端类型和 API client 新增 `MasterSettingPatch`、`MasterSettingUpdateResponse` 与 `updateMasterSetting()`，只提交后端白名单字段。
  - 长篇项目工作台「设定工作台」新增最小写控件：作品名、题材、世界规则、力量限制、禁用设定；保存后本地更新面板，再刷新项目工作台。
  - 后端工作台 payload 将 ready 的 MasterSetting 标记为 `mode=lite_edit`、`can_edit=true`，继续保持缺失/损坏时只读空态。
- **测试/验证**：前端 `pnpm run build` 通过；focused `tests/test_v092_master_setting_update.py` 为 **5 passed**；本地临时项目浏览器冒烟确认编辑、保存、成功提示、新标题和规则内容同屏可见，console 无 warn/error。
- **边界**：仍只编辑 `master_setting.yaml` 的 display/genre/rules/limits/forbidden，不编辑人物状态、时间线、伏笔、章节摘要，不同步 `world.yaml`，不改 runner。
- **下一刀建议**：做 v0.9.2 Lite 收口复核与归档；若发现 MasterSetting Lite 已满足当前长篇闭环需要，再进入 v0.9.3 Graph Memory Evaluation Spike 的触发条件复核。

### 2026-06-01 — v0.9.2 MasterSetting Workspace Lite 收口

- **做了什么**：
  - 新增 `docs/completed/v0.9.2-master-setting-workspace-lite.md`，归档 Summary-A、Panel-B、Edit-C 与 Frontend-D 的目标、完成范围、收口证明、边界和验证命令。
  - `docs/index.md` 登记 v0.9.2 收口文档；路线、PRD、handoff、README、UI spec、AGENTS 和本文件同步推进到 v0.9.3 触发条件复核。
- **测试/验证**：收口文档切片仍需跑完整门禁：后端 **632 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：v0.9.2 Lite 已收口，但仍不做完整作者工作台、人物/时间线/伏笔/章节摘要编辑、`world.yaml` 同步、图数据库、云端队列或商业级项目空间。
- **下一刀建议**：进入 v0.9.3 Graph Memory Evaluation Spike 的触发条件复核；若当前样例规模不足以证明 BM25/ledger/aliases 召回失败，则先记录“不触发”，不要提前引入 Zep 或图数据库。

### 2026-06-01 — v0.9.3 Graph Memory Evaluation Trigger-A

- **做了什么**：
  - 新增 `service.graph_memory_evaluation.evaluate_graph_memory_trigger()`，只读检查导入规模、`memory/canon_ledger.jsonl`、`memory/entity_aliases.yaml` 与 `memory/consistency_report.json`。
  - 新增 `GET /api/stories/<slug>/graph-memory-evaluation`，slug 先走 `safe_id`；非法 slug 400，缺故事 404。
  - 返回 `status=not_triggered|monitor|triggered`、章节/字数/账本/别名/审计指标、触发原因、阈值和中文 next steps。
- **测试/验证**：先写红灯测试确认服务入口缺失，补实现后 `tests/test_v093_graph_memory_trigger.py` 为 **3 passed**；完整门禁为后端 **635 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接 Zep、图数据库、GraphRAG、embedding、向量库或 reranker；不写 artifact，不替换现有 BM25 / canon ledger / entity aliases，不改 runner。
- **下一刀建议**：继续 v0.9.3 Retrieval Probe-B，补代表性查询评测样本和失败样例收集；只有评测证明召回不足，才进入真正图记忆 spike。

### 2026-06-01 — v0.9.3 Graph Memory Evaluation Retrieval Probe-B / 收口

- **做了什么**：
  - 新增 `service.retrieval_probe.evaluate_retrieval_probes()`，从 canon ledger 与 entity aliases 自动生成代表性查询样本，并复用现有 `retrieve_context()` 检查期望 source、item 和实体是否命中。
  - 新增 `GET /api/stories/<slug>/retrieval-probes`，slug 先走 `safe_id`；非法 slug 400，缺故事 404。
  - 新增 `docs/completed/v0.9.3-graph-memory-evaluation-spike.md`，将 Trigger-A 与 Probe-B 收口为“当前不触发重依赖接入”的证据链。
- **测试/验证**：先写红灯测试确认服务入口缺失，补实现后 `tests/test_v093_retrieval_probe.py` 为 **3 passed**；完整门禁为后端 **638 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接 Zep、图数据库、GraphRAG、embedding、向量库或 reranker；不写新 run artifact，不替换 `retrieval_context.json` / `runtime_memory_context.json`，不改 runner。
- **下一刀建议**：进入 v0.9.4 Advanced Runner Evaluation Trigger-A，先复核 v0.8.10 状态执行层是否真的不足；没有明确 runner 缺口时，不提前接 LangGraph、OASIS 或 CAMEL。

### 2026-06-01 — v0.9.4 Advanced Runner Evaluation Trigger-A

- **做了什么**：
  - 新增 `service.advanced_runner_evaluation.evaluate_advanced_runner_trigger()`，只读检查 `runner_state_execution_report.json`、分支 `multi_agent_trace.json` 与 `emergence_nodes.json`。
  - 新增 `GET /api/runs/<run_id>/advanced-runner-evaluation`，run_id 先走安全校验；非法 run_id 400，缺 run 404。
  - 返回 `not_triggered` / `insufficient_data` / `triggered`、状态执行候选 backlog、trace warning、私域复杂度、high-value emergence 和中文 next steps。
- **测试/验证**：先写红灯测试确认服务入口缺失，补实现后 `tests/test_v094_advanced_runner_trigger.py` 为 **3 passed**；完整门禁为后端 **641 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接 LangGraph、OASIS、CAMEL；不写 artifact，不替换现有 runner，不改 `run_scene` 默认行为或既有 run artifact 契约。
- **下一刀建议**：继续 v0.9.4 Advanced Runner Probe-B，补代表性复杂 run 样例和失败样例；只有真实复杂状态流转证明自研 runner 不足时，才进入 LangGraph/OASIS/CAMEL spike。

### 2026-06-01 — v0.9.4 Advanced Runner Probe-B / 收口

- **做了什么**：
  - 新增 `evaluate_advanced_runner_probes()` 与 `GET /api/runs/<run_id>/advanced-runner-probes`，把状态执行候选、trace 质量、涌现节点拆成可复现 probe。
  - 复杂 run 会收集 `state_execution_backlog`、`trace_repair_warnings`、`high_value_emergence` 等失败样例；简单 run 返回 `pass`。
  - 新增 `docs/completed/v0.9.4-advanced-runner-evaluation-spike.md`，将 Trigger-A 与 Probe-B 收口为“当前不触发高级 runner 重依赖接入”的证据链。
- **测试/验证**：`tests/test_v094_advanced_runner_trigger.py` 扩充为 **5 passed**；完整门禁为后端 **643 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接 LangGraph、OASIS、CAMEL；不写 artifact，不替换现有 runner，不改 `run_scene` 默认行为或既有 run artifact 契约。
- **下一刀建议**：进入 v1.0-beta Commercial Hardening Scope-A，先做范围复核和本地优先的商业化边界整理；不要直接跳云端多用户持久队列、对象存储、多租户权限或付费系统。

### 2026-06-01 — v1.0-beta Commercial Hardening Scope-A

- **做了什么**：
  - 新增 `service.commercial_hardening.get_commercial_hardening_scope()`，只读整理账号与项目空间、权限模型、云端持久化、配额与成本、审计日志、版权分享边界、部署观测七个商业化域。
  - 新增 `GET /api/settings/commercial-hardening-scope`，返回 `v1.0-beta-commercial-hardening-scope-a` 报告、当前覆盖、缺口、本地优先下一步、平台化下一步、延后项与下一刀候选。
  - 新增 `docs/completed/v1.0-beta-commercial-hardening-scope-a.md`，明确本刀不进入云端多租户、对象存储、数据库、持久队列或计费系统。
- **测试/验证**：先写红灯测试确认 service/API 缺失，补实现后 `tests/test_runtime_settings_api.py` 为 **27 passed**；完整门禁为后端 **645 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不读/回显密钥，不创建客户端，不打网络，不落盘，不改 `run_scene` 默认行为，不改变既有 artifact 契约。
- **下一刀建议**：进入 `v1.0-beta Commercial Audit Log Schema-B`，先做本地 `project_audit_log.jsonl` schema 与只读聚合，继续保持 additive、本地优先、不接云端不可篡改存储。

### 2026-06-01 — v1.0-beta Commercial Audit Log Schema-B

- **做了什么**：
  - 新增 `service.commercial_audit_log.get_project_audit_log()`，定义本地 `memory/project_audit_log.jsonl` 事件 schema。
  - 新增 `GET /api/stories/<slug>/audit-log`，slug 先走安全校验；非法 slug 400，缺项目 404。
  - 只读聚合 `import_report.json`、`selected_worldline.json`、`memory/master_setting_update_report.json`、`creation_loop_alpha_closeout.json` 与现有 `memory/project_audit_log.jsonl` 行，生成项目审计时间线；坏 JSONL 行降级为 warning。
  - 新增 `docs/completed/v1.0-beta-commercial-audit-log-schema-b.md`，明确本刀只定义 schema/聚合，不让写操作追加日志。
- **测试/验证**：先写红灯测试确认 service/API 缺失，补实现后 `tests/test_v100_commercial_audit_log.py` 为 **5 passed**；完整门禁为后端 **650 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不写 `project_audit_log.jsonl`，不接账号、权限系统、对象存储、数据库、队列、计费或不可篡改审计存储，不改 `run_scene` 或既有 artifact 契约。
- **下一刀建议**：进入 `v1.0-beta Permission Matrix Draft-C`，把现有读写 API 和项目 artifact 映射成 owner/editor/viewer 权限矩阵草案，继续只读、不接认证系统。

### 2026-06-01 — v1.0-beta Permission Matrix Draft-C

- **做了什么**：
  - 新增 `service.commercial_permissions.get_permission_matrix_draft()`，返回 owner/editor/viewer 三角色权限矩阵草案。
  - 新增 `GET /api/settings/permission-matrix`，只读列出项目工作台、设定轻编辑、世界线选择、生成动作、审计日志、章节导出等资源的当前 endpoint 与角色权限。
  - 报告明确 `enforcement.mode=not_enforced`，避免误判为已接认证或服务端权限拦截。
  - 新增 `docs/completed/v1.0-beta-permission-matrix-draft-c.md`，归档权限矩阵草案、边界和验证。
- **测试/验证**：先写红灯测试确认 service/API 缺失，补实现后 `tests/test_v100_permission_matrix.py` 为 **2 passed**；完整门禁为后端 **652 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接真实账号、团队空间、认证 provider 或请求上下文；不新增权限拦截，不改变现有 API 行为，不写 artifact。
- **下一刀建议**：进入 `v1.0-beta Project Copyright Statement-D`，补项目级版权/来源声明 schema，让导出权限和 share guard 有明确权利依据，继续不提供公开发布入口。

### 2026-06-01 — v1.0-beta Project Copyright Statement-D

- **做了什么**：
  - 新增 `service.copyright_statement.get_project_copyright_statement()` / `write_project_copyright_statement()`，项目级版权/来源声明落本地 `memory/project_copyright_statement.json`。
  - 新增 `GET/POST /api/stories/<slug>/copyright-statement`；非法 slug 返回 400，缺项目 404，内置样例写入返回 409，损坏 artifact 降级为 `status=damaged` warning。
  - 单章导出与合集导出的 `share_guard` 新增 additive `rights_basis`，Markdown「版权与分享边界」写入声明状态、来源标题、权利状态和声明用途。
  - 新增 `docs/completed/v1.0-beta-project-copyright-statement-d.md`，归档 schema、边界和验证。
- **测试/验证**：先写红灯测试确认 service/API 缺失，补实现后 `tests/test_v100_copyright_statement.py` 为 **7 passed**；导出回归 `tests/test_v090_long_creation_loop.py tests/test_v100_copyright_statement.py` 为 **27 passed**；完整门禁为后端 **659 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不开放公开分享/发布/商用入口，不接平台版权审核、风控、云端存储或法律判断；不读/回显密钥，不改 `run_scene` 或既有 artifact 契约。
- **下一刀建议**：进入 `v1.0-beta Quota & Observability Lite-E`，基于现有 provider usage、job 状态和本地 artifact 做配额/观测口径，不接真实计费系统或云端监控平台。

### 2026-06-01 — v1.0-beta Quota & Observability Lite-E

- **做了什么**：
  - 新增 `service.quota_observability.get_quota_observability_lite()`，只读汇总 provider usage、内存 job 状态、软配额口径与观测缺口。
  - 新增 `GET /api/settings/quota-observability`，支持安全 `story_slug` 过滤；非法 story slug 返回 400。
  - `JobStore` 新增 additive `snapshot()` 与 `max_jobs`，仅用于观测当前进程内 job 状态。
  - 新增 `docs/completed/v1.0-beta-quota-observability-lite-e.md`，归档本地配额/观测口径、边界和验证。
- **测试/验证**：先写红灯测试确认 service/API 缺失，补实现后 `tests/test_v100_quota_observability.py` 为 **2 passed**；运行设置回归 `tests/test_runtime_settings_api.py tests/test_v100_quota_observability.py` 为 **29 passed**；完整门禁为后端 **661 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不执行硬配额，不阻断生成请求，不接真实计费、余额、账单、支付、云端监控、日志平台、告警系统或多租户账号；不读/回显密钥，不写 artifact。
- **下一刀建议**：后续 `v1.0-beta Local Deployment Readiness-F` 已收口；v1.0-beta 后续商业化加固需继续拆成明确小刀，不直接接云端托管、多租户账号、对象存储或商业计费。

### 2026-06-01 — v1.0-beta Local Deployment Readiness-F

- **做了什么**：
  - 新增 `service.deployment_readiness.get_local_deployment_readiness()`，只读汇总本地后端 HTTP 入口、前端静态资源、运行环境脱敏、本地数据目录、API 冒烟计划、运行步骤和验证步骤。
  - 新增 `GET /api/settings/deployment-readiness`，返回当前本地服务入口、静态资源/目录状态、脱敏 key 状态、`external_services_required=false` 和本地观测入口。
  - 新增 `docs/completed/v1.0-beta-local-deployment-readiness-f.md`，归档本地部署就绪清单、边界和验证。
- **测试/验证**：先写红灯测试确认 service/API 缺失，补实现后 `tests/test_v100_deployment_readiness.py` 为 **2 passed**；运行设置/配额/部署邻近回归为 **31 passed**；完整门禁为后端 **663 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接云端托管、对象存储、多用户账号、商业计费、外部监控、告警系统或自动部署脚本；不打网络、不落盘、不改 `run_scene`。
- **下一刀建议**：v1.0-beta 后续商业化加固需要先拆出明确小刀；不要直接进入云端多租户、对象存储或计费系统的大重构。

### 2026-06-01 — v1.0-beta Cloud Persistence Boundary-G

- **做了什么**：
  - 新增 `service.cloud_persistence_boundary.get_cloud_persistence_boundary()`，只读映射本地 `projects/`、`outputs/`、`_ingest_sessions/` 相关 artifact 到未来平台资源。
  - 新增 `GET /api/settings/cloud-persistence-boundary`，返回 `migration.mode=not_started`、`external_services_required=false`、本地 inventory、resource map、retention policy、readiness checks 和 deferred actions。
  - 新增 `docs/completed/v1.0-beta-cloud-persistence-boundary-g.md`，归档云端持久化迁移边界、保留规则和验证。
- **测试/验证**：先写红灯测试确认 service/API 缺失，补实现后 `tests/test_v100_cloud_persistence_boundary.py` 为 **2 passed**；商业化相邻回归为 **33 passed**；完整门禁为后端 **665 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接对象存储、数据库、持久队列、跨设备恢复、云端账号或团队空间；不上传文件、不迁移数据、不写 artifact、不改 `run_scene`。
- **下一刀建议**：继续 v1.0-beta 本地优先商业化加固，可拆“账号/项目空间迁移边界”或“审计日志写入策略”小刀；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta Account Project Space Boundary-H

- **做了什么**：
  - 新增 `service.account_project_space.get_account_project_space_boundary()`，只读定义本地账号语义、项目空间清单和未来团队归属迁移边界。
  - 新增 `GET /api/settings/account-project-space-boundary`，返回 `account_model.mode=local_single_operator`、本地 inventory、project spaces、future metadata fields、migration boundaries 和 deferred actions。
  - 新增 `docs/completed/v1.0-beta-account-project-space-boundary-h.md`，归档账号/项目空间边界、未做项和验证。
- **测试/验证**：先写红灯测试确认 service/API 缺失，补实现后 `tests/test_v100_account_project_space_boundary.py` 为 **2 passed**；商业化相邻回归为 **42 passed**；完整门禁为后端 **667 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接真实账号、团队空间、认证 provider、成员邀请、跨设备同步或请求级 ACL；不新增权限拦截、不写 artifact、不迁移项目、不改 `run_scene`。
- **下一刀建议**：继续 v1.0-beta 本地优先商业化加固，可拆“审计日志写入策略”或“项目删除/保留策略”小刀；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta Audit Log Append Policy-I

- **做了什么**：
  - 新增 `append_project_audit_log_event()`，白名单追加本地 `memory/project_audit_log.jsonl`，不覆盖既有 artifact。
  - 新增 `POST /api/stories/<slug>/audit-log/events`，坏 payload 400、缺项目 404、内置样例只读 409。
  - `metadata` 会丢弃疑似密钥字段或密钥值；`GET /api/stories/<slug>/audit-log` 继续聚合追加后的 JSONL 行。
  - 权限矩阵草案同步把审计日志资源更新为 `read + append`，但仍 `enforcement.mode=not_enforced`。
  - 新增 `docs/completed/v1.0-beta-audit-log-append-policy-i.md`，归档审计日志追加策略、边界和验证。
- **测试/验证**：先写红灯测试确认 service/API 缺失，补实现后 `tests/test_v100_audit_log_append_policy.py` 为 **6 passed**；商业化相邻回归为 **44 passed**；权限同步回归为 **13 passed**；完整门禁为后端 **673 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接真实账号、团队空间、认证 provider、请求级 ACL、云端不可篡改审计存储、对象存储、数据库或队列；不自动为所有写操作补审计，不改 `run_scene`。
- **下一刀建议**：继续 v1.0-beta 本地优先商业化加固，可拆“项目删除/保留策略”或“审计事件接入关键写操作”小刀；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta Project Retention Policy-J

- **做了什么**：
  - 新增 `get_project_retention_policy()` / `write_project_retention_policy()`，本地读写 `memory/project_retention_policy.json`。
  - 新增 `GET/POST /api/stories/<slug>/retention-policy`，坏 slug 400、缺项目 404、内置样例只读 409。
  - 策略覆盖项目、上传原文、生成产物、holdout、审计日志和 ingest 分片的保留口径；写入后追加 `retention_policy_reviewed` 审计事件。
  - 新增 `docs/completed/v1.0-beta-project-retention-policy-j.md`，归档策略字段、边界和验证。
- **测试/验证**：先写红灯测试确认 service/API 缺失，补实现后 `tests/test_v100_project_retention_policy.py` 为 **7 passed**；邻近回归为 **29 passed**；完整门禁为后端 **680 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不实际删除项目目录、上传原文、生成产物、holdout 或审计日志；不接对象存储、数据库、持久队列、真实账号、团队空间或请求级 ACL；不改 `run_scene`。
- **下一刀建议**：继续 v1.0-beta 本地优先商业化加固，可拆“审计事件接入关键写操作”或“设置页商业化状态总览”小刀；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta Copyright Audit Hook-K

- **做了什么**：
  - `write_project_copyright_statement()` 成功保存 `memory/project_copyright_statement.json` 后追加 `rights_reviewed` 审计事件。
  - `GET /api/stories/<slug>/audit-log` 可聚合该事件，metadata 包含版权声明 artifact path 与 license status。
  - 新增 `docs/completed/v1.0-beta-copyright-audit-hook-k.md`，归档审计 hook、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 `rights_reviewed`，补实现后 focused 为 **1 passed**；版权/审计/保留策略相邻回归为 **26 passed**；完整门禁为后端 **681 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接真实账号、团队空间、认证 provider、请求级 ACL、云端不可篡改审计存储、对象存储、数据库或队列；不把所有写操作一次性接入审计，不改 `run_scene`。
- **下一刀建议**：MasterSetting Audit Hook-L 已收口；后续继续 v1.0-beta 本地优先商业化加固，可继续把世界线选择或状态 overlay apply/rollback 接入审计日志；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta MasterSetting Audit Hook-L

- **做了什么**：
  - `update_master_setting()` 成功保存 `memory/master_setting.yaml` 与 `memory/master_setting_update_report.json` 后追加 `master_setting_updated` 审计事件。
  - `GET /api/stories/<slug>/audit-log` 可聚合该 JSONL 事件，metadata 包含设定 artifact path、报告 path 与 changed 字段。
  - 审计追加白名单新增 `master_setting_updated`，用于真实设定保存事件。
  - 新增 `docs/completed/v1.0-beta-master-setting-audit-hook-l.md`，归档审计 hook、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 JSONL `master_setting_updated`，补实现后 focused 为 **1 passed**；设定/审计/权限相邻回归为 **19 passed**；完整门禁为后端 **682 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接真实账号、团队空间、认证 provider、请求级 ACL、云端不可篡改审计存储、对象存储、数据库或队列；不把所有写操作一次性接入审计，不同步 `world.yaml` 或 runner artifact，不改 `run_scene`。
- **下一刀建议**：Worldline Selection Audit Hook-M 已收口；后续继续 v1.0-beta 本地优先商业化加固，可继续把状态 overlay apply/rollback 接入审计日志，或做设置页商业化状态总览；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta Worldline Selection Audit Hook-M

- **做了什么**：
  - `select_worldline()` 成功保存 `selected_worldline.json` 后追加 `worldline_selected` 审计事件。
  - `GET /api/stories/<slug>/audit-log` 可聚合该 JSONL 事件，metadata 包含 selection artifact path、run_id、branch_id 与 branch_label。
  - 审计追加白名单新增 `worldline_selected`，用于真实世界线选择事件。
  - builtin 样例仍保持既有 outputs 选择记录语义，审计追加冲突会降级跳过。
  - 新增 `docs/completed/v1.0-beta-worldline-selection-audit-hook-m.md`，归档审计 hook、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 JSONL `worldline_selected`，补实现后 focused 为 **1 passed**；创作闭环/审计/追加策略相邻回归为 **31 passed**；完整门禁为后端 **682 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接真实账号、团队空间、认证 provider、请求级 ACL、云端不可篡改审计存储、对象存储、数据库或队列；不改变推荐世界线排序，不驱动 runner，不自动写正史账本，不改 `run_scene`。
- **下一刀建议**：State Execution Audit Hook-N 已收口；后续继续 v1.0-beta 本地优先商业化加固，可做设置页商业化状态总览或审计日志 UI/导出聚合；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta State Execution Audit Hook-N

- **做了什么**：
  - `apply_runner_state_execution()` 成功写入状态执行覆盖层和 `runner_state_execution_apply_report.json` 后追加 `state_execution_applied` 审计事件。
  - `rollback_runner_state_execution()` 成功写入 `runner_state_execution_rollback_report.json` 后追加 `state_execution_rolled_back` 审计事件。
  - 审计追加白名单新增 `state_execution_applied` 与 `state_execution_rolled_back`。
  - builtin 样例保持既有状态执行语义，审计追加冲突会降级跳过。
  - 新增 `docs/completed/v1.0-beta-state-execution-audit-hook-n.md`，归档审计 hook、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 JSONL 状态执行事件，补实现后 focused 为 **1 passed**；状态执行/审计/追加策略相邻回归为 **20 passed**；完整门禁为后端 **683 passed**，前端 `pnpm run build` 通过，`git diff --check` 通过。
- **边界**：不接真实账号、团队空间、认证 provider、请求级 ACL、云端不可篡改审计存储、对象存储、数据库或队列；不改变状态执行 eligibility、候选筛选、overlay 写入和回滚规则；不让 overlay 自动驱动下一轮 runner，不改 `run_scene`。
- **下一刀建议**：Commercial Status Overview-O 已收口；后续继续 v1.0-beta 本地优先商业化加固，可做审计日志 UI/导出聚合或设置页本地 smoke checklist；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta Commercial Status Overview-O

- **做了什么**：
  - 新增 `get_commercial_status_overview()` 与 `GET /api/settings/commercial-status-overview`。
  - 设置抽屉新增「商业化状态总览」只读区，展示本地已就绪、需留意、平台化暂缓数量和逐域状态。
  - 总览聚合商业化范围、provider/cost、配额观测、权限矩阵、账号/项目空间、云端持久化、本地部署、审计与版权边界。
  - 接口只返回摘要证据，不返回明文 Key 或环境变量名，不写 artifact、不创建模型客户端、不打外网。
  - 新增 `docs/completed/v1.0-beta-commercial-status-overview-o.md`，归档 UI/API、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 `get_commercial_status_overview`，补实现后 focused 为 **2 passed**；设置/商业化相邻回归为 **35 passed**；前端 `pnpm run build` 通过；本地后端 + Vite HTTP 冒烟通过；完整门禁为后端 **685 passed**，`git diff --check` 通过。
- **边界**：不接真实账号、团队空间、认证 provider、请求级 ACL、云端迁移、对象存储、数据库、队列或计费系统；不改变 provider 路由、默认 mock、状态执行规则或 `run_scene`。
- **下一刀建议**：继续 v1.0-beta 本地优先商业化加固，可做审计日志 UI/导出聚合，或补设置页本地 smoke checklist；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta Audit Log UI & Export-P

- **做了什么**：
  - 新增 `export_project_audit_log()` 与 `GET /api/stories/<slug>/audit-log/export`。
  - 项目工作台新增「项目审计日志」只读区，展示事件数、来源产物、最近事件、warning 和下一步。
  - 前端可下载本地 Markdown 审计日志，导出前会用中文确认分享边界。
  - 导出内容不包含事件 `metadata`，避免手工 JSONL 残留敏感字段进入 Markdown。
  - 新增 `docs/completed/v1.0-beta-audit-log-ui-export-p.md`，归档 UI/API、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 `export_project_audit_log`，补实现后 focused 为 **3 passed**；审计/商业化相邻回归为 **16 passed**；前端 `pnpm run build` 通过；完整门禁为后端 **688 passed**，`git diff --check` 通过。
- **边界**：不写新 artifact，不覆盖 `memory/project_audit_log.jsonl`；不提供公开分享、版权审批、真实账号、请求级 ACL、云端不可篡改审计存储、对象存储、数据库或计费；不改变 `run_scene`。
- **下一刀建议**：继续 v1.0-beta 本地优先商业化加固，可补设置页本地 smoke checklist，或继续拆版权审批/部署观测类小刀；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta Settings Local Smoke Checklist-Q

- **做了什么**：
  - 新增 `get_settings_local_smoke_checklist()` 与 `GET /api/settings/local-smoke-checklist`。
  - 设置抽屉新增「本地冒烟清单」只读区，展示待核对路径数、外部服务需求、前 6 条本地核对路径和运行步骤。
  - 清单覆盖首页、故事列表、运行设置、provider、用量、配额观测、本地部署就绪、商业化状态总览、项目工作台和审计日志导出。
  - 接口只生成 checklist，不主动执行 HTTP 请求、不绑定端口、不落盘、不打外网、不读取或展示明文密钥。
  - 新增 `docs/completed/v1.0-beta-settings-local-smoke-checklist-q.md`，归档 UI/API、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 `get_settings_local_smoke_checklist`，补实现后 focused 为 **2 passed**；设置/商业化相邻回归为 **33 passed**；前端 `pnpm run build` 通过；完整门禁为后端 **690 passed**，`git diff --check` 通过。
- **边界**：不接真实部署、认证、对象存储、云端观测或计费；不改变 `run_scene`。
- **下一刀建议**：Release Preflight Checklist-R 已收口；后续继续 v1.0-beta 本地优先商业化加固，可继续拆版权审批或部署观测；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta Release Preflight Checklist-R

- **做了什么**：
  - 新增 `get_release_preflight_checklist()` 与 `GET /api/settings/release-preflight`。
  - 设置抽屉新增「发布前检查」只读区，展示已具备/需留意数量和前 6 条检查项。
  - 清单聚合本地部署就绪、本地冒烟、商业化状态总览、权限矩阵草案，以及项目级版权声明、保留策略和审计导出入口。
  - 未传 `story_slug` 时，项目级项降级为“选择具体项目后核对”；非法 `story_slug` 返回 400。
  - 新增 `docs/completed/v1.0-beta-release-preflight-checklist-r.md`，归档 UI/API、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 `get_release_preflight_checklist`，补实现后 focused 为 **3 passed**；设置/商业化相邻回归为 **29 passed**；前端 `pnpm run build` 通过；完整门禁为后端 **693 passed**，`git diff --check` 通过。
- **边界**：不执行真实发布、不主动打请求、不写 artifact、不打外网、不读取或展示明文密钥；不接真实认证、对象存储、云端观测、不可篡改审计或计费；不改变 `run_scene`。
- **下一刀建议**：Rights Approval Checklist-S 已收口；后续继续 v1.0-beta 本地优先商业化加固，可继续拆部署观测或认证/对象存储边界小刀；不要直接进入云端多租户、对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta Rights Approval Checklist-S

- **做了什么**：
  - 新增 `get_rights_approval_checklist()` 与 `GET /api/stories/<slug>/rights-approval-checklist`。
  - 清单聚合项目版权/来源声明、授权确认、local export 许可、`rights_reviewed` 审计事件和公开发布保护项。
  - 长篇项目工作台「项目审计日志」区新增「版权审批检查」只读面板，展示已具备/需留意数量、前 4 条检查项和中文下一步。
  - `story_slug` 继续走 `safe_id`；非法 slug 返回 400，缺项目返回 404；输出不包含明文密钥或环境变量名。
  - 新增 `docs/completed/v1.0-beta-rights-approval-checklist-s.md`，归档 UI/API、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 `get_rights_approval_checklist`，补实现后 focused 为 **4 passed**；版权/审计相邻回归为 **15 passed**；前端 `pnpm run build` 通过；完整门禁为后端 **697 passed**，`git diff --check` 通过。
- **边界**：只读检查版权审批准备度，不执行真实审批、不开放公开发布、不写 artifact、不打外网、不接真实认证、对象存储、云端不可篡改审计或计费；不改变 `run_scene`。
- **下一刀建议**：Deployment Observability Checklist-T 已收口；后续继续 v1.0-beta 本地优先商业化加固，可拆认证边界或对象存储 adapter 边界小刀；不要直接进入云端多租户或商业计费系统。

### 2026-06-01 — v1.0-beta Deployment Observability Checklist-T

- **做了什么**：
  - 新增 `get_deployment_observability_checklist()` 与 `GET /api/settings/deployment-observability`。
  - 清单聚合本地部署就绪、本地冒烟、配额用量、内存 job、项目审计时间线、版权审批检查和发布前检查。
  - 设置抽屉新增「部署观测清单」只读区，展示已具备/需留意数量、云端观测状态、前 6 条信号和中文下一步。
  - `story_slug` 可选且继续走 `safe_id`；非法 `story_slug` 返回 400；输出不包含明文密钥或环境变量名。
  - 新增 `docs/completed/v1.0-beta-deployment-observability-checklist-t.md`，归档 UI/API、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 `get_deployment_observability_checklist`，补实现后 focused 为 **3 passed**；部署/发布/配额相邻回归为 **10 passed**；前端 `pnpm run build` 通过；完整门禁为后端 **700 passed**，`git diff --check` 通过。
- **边界**：只读聚合本地观测证据，不 tail 日志、不写 artifact、不打外网、不接云端观测、对象存储、持久队列、真实认证或计费；不改变 `run_scene`。
- **下一刀建议**：Auth Boundary Checklist-U 已收口；后续继续 v1.0-beta 本地优先商业化加固，可拆对象存储 adapter 边界小刀；不要直接进入云端多租户或商业计费系统。

### 2026-06-01 — v1.0-beta Auth Boundary Checklist-U

- **做了什么**：
  - 新增 `get_auth_boundary_checklist()` 与 `GET /api/settings/auth-boundary`。
  - 清单聚合账号/项目空间边界、权限矩阵草案、请求级 ACL 缺口、项目空间映射和部署观测边界。
  - 设置抽屉新增「认证边界清单」只读区，展示已具备/需留意数量、认证执行状态、检查项和中文下一步。
  - 输出明确 `auth_enforced=false` 与 `external_services_required=false`，不包含明文密钥或环境变量名。
  - 新增 `docs/completed/v1.0-beta-auth-boundary-checklist-u.md`，归档 UI/API、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 `get_auth_boundary_checklist`，补实现后 focused 为 **2 passed**；账号/权限/部署观测相邻回归为 **9 passed**；前端 `pnpm run build` 通过；完整门禁为后端 **702 passed**，`git diff --check` 通过。
- **边界**：只读定义认证接入边界，不创建用户、不接登录 provider、不执行 ACL、不写 artifact、不打外网、不接云端多租户或计费；不改变 `run_scene`。
- **下一刀建议**：Object Storage Boundary Checklist-V 已收口；后续继续 v1.0-beta 本地优先商业化加固，可拆计费 adapter 边界或真实配额 guardrail 前置清单；不要直接进入云端多租户或商业计费系统。

### 2026-06-01 — v1.0-beta Object Storage Boundary Checklist-V

- **做了什么**：
  - 新增 `get_object_storage_boundary_checklist()` 与 `GET /api/settings/object-storage-boundary`。
  - 清单聚合云端持久化边界、本地 artifact 盘点、资源映射、原文/holdout 私有隔离、项目保留策略输入、认证边界和本地部署护栏。
  - 设置抽屉新增「对象存储边界」只读区，展示已具备/需留意数量、远端写入状态、前 6 条检查项和中文下一步。
  - 输出明确 `adapter_implemented=false`、`remote_writes_enabled=false` 与 `external_services_required=false`，不包含明文密钥或环境变量名。
  - 新增 `docs/completed/v1.0-beta-object-storage-boundary-checklist-v.md`，归档 UI/API、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 `get_object_storage_boundary_checklist`，补实现后 focused 为 **2 passed**；对象存储/云端持久化/认证/部署/保留策略相邻回归为 **15 passed**；前端 `pnpm run build` 通过；完整门禁为后端 **704 passed**，`git diff --check` 通过。
- **边界**：只读定义对象存储 adapter 前置边界，不创建 bucket、不生成签名 URL、不上传文件、不写 artifact、不打外网、不接真实对象存储、云端多租户或计费；不改变 `run_scene`。
- **下一刀建议**：Quota Enforcement Boundary Checklist-W 已收口；后续可拆计费 adapter 边界或真实配额 guardrail 前置清单；不要直接进入云端多租户或商业计费系统。

### 2026-06-01 — v1.0-beta Quota Enforcement Boundary Checklist-W

- **做了什么**：
  - 新增 `get_quota_enforcement_boundary_checklist()` 与 `GET /api/settings/quota-enforcement-boundary`。
  - 清单聚合配额观测、provider usage、内存 job、认证边界和部署观测，明确软配额已可读、硬配额 guardrail 与账单 adapter 仍未接入。
  - 设置抽屉新增「配额执行边界」只读区，展示已具备/需留意数量、硬配额状态、前 6 条检查项和中文下一步。
  - 输出明确 `enforcement_enabled=false`、`hard_limits_enabled=false` 与 `external_billing_required=false`，不包含明文密钥或环境变量名。
  - 新增 `docs/completed/v1.0-beta-quota-enforcement-boundary-checklist-w.md`，归档 UI/API、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 `get_quota_enforcement_boundary_checklist`，补实现后 focused 为 **2 passed**；配额/认证/部署观测相邻回归为 **9 passed**；前端 `pnpm run build` 通过；完整门禁为后端 **706 passed**，`git diff --check` 通过。
- **边界**：只读定义配额执行前置边界，不拦截生成/导入/导出/视觉生成请求，不写 quota state，不接真实计费、余额、账单、支付、云端监控或告警系统；不改变 `run_scene`。
- **下一刀建议**：继续 v1.0-beta 本地优先商业化加固，可拆计费 adapter 边界或真实配额 guardrail 前置清单；不要直接进入云端多租户、真实对象存储或商业计费系统。

### 2026-06-01 — v1.0-beta Billing Adapter Boundary Checklist-X

- **做了什么**：
  - 新增 `get_billing_adapter_boundary_checklist()` 与 `GET /api/settings/billing-adapter-boundary`。
  - 清单聚合 provider usage / 成本估算、配额执行边界、认证边界、计费身份、支付 provider adapter、发票退款轨迹和计费写入边界。
  - 设置抽屉新增「计费边界」只读区，展示已具备/需留意数量、计费写入状态、前 6 条检查项和中文下一步。
  - 输出明确 `adapter_implemented=false`、`billing_writes_enabled=false` 与 `external_billing_required=false`，不包含明文密钥或环境变量名。
  - 新增 `docs/completed/v1.0-beta-billing-adapter-boundary-checklist-x.md`，归档 UI/API、边界和验证。
- **测试/验证**：先写红灯测试确认缺少 `get_billing_adapter_boundary_checklist`，补实现后 focused 为 **2 passed**；计费/配额/认证/部署观测相邻回归为 **35 passed**；前端 `pnpm run build` 通过；完整门禁为后端 **708 passed**，`git diff --check` 通过。
- **边界**：只读定义计费 adapter 前置边界，不创建 customer/subscription/checkout/webhook，不写余额、账单、套餐、欠费、发票、退款或支付状态，不打外网、不读取明文密钥；不改变 `run_scene`。
- **下一刀建议**：继续 v1.0-beta 本地优先商业化加固，可拆真实硬配额 guardrail 前置清单、webhook/idempotency 边界或认证执行前置清单；不要直接进入云端多租户、真实对象存储、真实认证或商业计费系统。

### 2026-06-01 — v1.0-local Model Configuration UX

- **做了什么**：
  - 新增 `get_model_configuration_summary()` 与 `GET /api/settings/model-configuration`，把文本模型、连接测试、默认推演、视觉模型和密钥边界汇成只读、脱敏的模型配置摘要。
  - 设置抽屉新增「模型配置状态」，用户可直接看到当前是本地模拟还是真实模型、文本/视觉模型是否就绪、下一步该如何配置。
  - 保存设置或清除文本模型密钥后刷新模型配置状态和 provider 状态。
  - 按用户最新规划，当前不再继续推进商业化/计费实现；设置抽屉撤下「计费边界」可见区与成本估算输入，用量区只保留 token 统计。
  - 新增 `docs/completed/v1.0-local-model-configuration-ux.md` 与 `docs/distribution-phase-plan.md`，把未来三条使用路径排期为：本地 clone、GitHub Release 安装包、服务器在线体验。
- **测试/验证**：先写红灯测试确认缺少 `get_model_configuration_summary` 与 HTTP endpoint；补实现后 focused 为 **2 passed**，运行设置相邻回归合计 **29 passed**；后端完整回归 **710 passed**；前端 `pnpm run build` 通过；`git diff --check` 通过。
- **边界**：不改 `run_scene` 默认行为；不新增真实认证、真实计费、真实配额拦截、线上多用户或安装包实现；不在前端存储或回显 API Key 明文。
- **暂停说明**：按用户要求，本刀完成、验证、提交推送后暂停继续目标任务；后续不再自动开商业化/计费下一刀。

### 2026-06-01 — v1.0-local Model Configuration UI + Local Run Scripts

- **做了什么**：
  - `GET /api/settings/model-configuration` additive 返回 `text_model_presets`、`visual_model_presets` 与 `form_guidance`，覆盖 OpenAI 兼容、DeepSeek、通义千问、火山方舟、Seedream 和自定义接口模板；仍不返回明文 Key 或环境变量名。
  - 设置抽屉新增「常用接口模板」「使用真实文本模型生成」「视觉模型模板」和视觉密钥清除按钮，用户可以在页面里配置自己的文本/视觉模型。
  - 新增 `scripts/start-local.ps1` 与 `scripts/start-local.sh`，支持检查依赖、创建 `engine/.venv`、安装后端/前端依赖、启动后端 `lne browse` 与 Vite 前端并打开本地入口。
  - 新增 `docs/completed/v1.0-local-run-scripts.md`，并同步 `distribution-phase-plan.md`、README、UI spec、PRD、阶段图与路线图；安装包和服务器在线体验继续后置。
- **测试/验证**：focused 为 **5 passed**；后端完整回归 **713 passed**；前端 `pnpm run build` 通过；本地 HTTP smoke 通过（Vite 首页 200，模型配置 API 返回 5 个文本模板、2 个视觉模板、`save_scope=process_only`、`plaintext_key_returned=false`）。Windows `powershell ... scripts\start-local.ps1 -CheckOnly -NoBrowser` 与 `pwsh ... -CheckOnly -NoBrowser` 均通过；macOS shell 脚本在当前 Windows 环境因 WSL 不可用无法执行 `bash -n`，由静态测试覆盖脚本内容和密钥边界；`git diff --check` 通过。
- **边界**：不改 `run_scene` 默认行为；不内置 Python/Node runtime；不生成 Release 安装包；不接腾讯云部署、真实认证、对象存储或计费；脚本不读取、写入或打印用户模型密钥。
- **暂停说明**：这两件事完成、验证、提交推送后暂停，不继续开新刀。

### 2026-06-01 — 品牌命名收口：未终章 / Unfinale

- **做了什么**：
  - 将面向用户与文档的产品名从 Living Novel Engine / 活体小说引擎收口为 **未终章**，英文名为 **Unfinale**。
  - 新增 `docs/brand/`，包含 `unfinale-logo.svg`、`unfinale-icon.svg` 与 imagegen 轻量概念稿 `unfinale-logo-concept-light.png`。
  - 同步入口文档、PRD、路线图、阶段图、README、接力包、UI spec、论文报告与 completed 归档中的产品命名表述。
  - 明确命名边界：代码包、CLI、artifact、环境变量和技术缩写仍沿用 LNE / `living_novel_engine`，避免把品牌更新误扩散成代码层 rename。
- **测试/验证**：本次只改文档与品牌资产；验证 `rg "Living Novel|living novel|活体小说" --glob "*.md"` 后，旧名只保留在 `memory.md` 与本日志的品牌迁移说明中；前端页面暂不改。
- **边界**：不改 `engine/ui` 页面源码，不改 API/CLI/package 名，不改 `run_scene` 默认行为。

### 2026-06-03 — 后续增强自主迭代总账补记：Runtime Preflight 至 Graph Memory Provider Spike Opt-in Final Readiness Summary

- **补记原因**：用户指出本轮自主迭代完成了大量独立切片，但此前未按约定逐刀追加到 `docs/project-changelog.md`；本条补记过去 39h 的主要交付，并强化后续规则：每完成一个独立切片都必须即时追加本文件末尾，不等总收口再补。
- **做了什么**：
  - 完成后续增强产品化链路：Runtime Preflight、Projection Health、Reader Panel / Adversarial Revision Lab、Prompt Budget Pack、LLM Profile Assignment、Cards Workspace、OpenAPI / Typed Client、Bundled Release Readiness。
  - 完成长篇记忆增强的检索评测链路：Embedding / Vector Retrieval Readiness Probe、Embedding Evaluation Samples、Retrieval Failure Sample Authoring、Memory CLI、Retrieval Sample Export Pack、Embedding Mock Evaluation Report、Retrieval Sample Replay Report、Retrieval Sample Migration Pack、Cross Project Retrieval Samples Index、Retrieval Samples Trend Snapshot。
  - 完成 GraphRAG / Zep 触发式证据链路：GraphRAG / Zep Trigger Evidence、Graph Memory Spike Design Pack、Graph Memory Shadow Compare Pack、Graph Memory Shadow Case Matrix、Graph Memory Provider Boundary Matrix。
  - 完成 Graph Memory provider spike dry-run 前置链路：Offline Shadow Replay Plan / Report、Provider Spike Fixture Pack、Readiness Gate、Runbook、Dry-run Result Template、Mock Result Report、Review Gate、Manual Approval Pack、Manual Approval Evidence Checklist。
  - 完成 Graph Memory provider opt-in 人工复核链路：Opt-in Evidence Snapshot、Opt-in No-go Matrix、Opt-in Operator Checklist、Opt-in Review Packet、Opt-in Decision Ledger Preview、Opt-in Final Readiness Summary。
  - 最新一刀新增 `graph_memory_provider_spike_opt_in_final_readiness_summary` 只读 service/API/CLI/UI，把 decision ledger preview 收束为最终就绪摘要、未签收字段、阻塞原因、真实 provider 继续禁止边界和下一步人工签收材料。
- **测试/验证**：
  - 最新一刀 focused tests 为 **7 passed**，Graph Memory 邻近回归为 **87 passed**。
  - 前端 `cd engine/ui && pnpm run build` 通过。
  - HTTP/CLI smoke 通过，确认最终摘要 API 与 CLI 都返回 ready 状态、未签收/阻塞计数、`real_provider_ready=false`、`real_provider_config_allowed=false`，且不返回明文 Key。
  - 后端完整门禁 `cd engine && python -m pytest -q` 为 **859 passed**。
  - `git diff --check` 通过，仅保留 Windows CRLF 提示。
- **边界**：
  - 所有新增链路保持 additive，只读优先；不改 `run_scene` 默认行为，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`、`canon_ledger.jsonl`。
  - 不接真实生产向量库、GraphRAG、Zep、外部 embedding provider 或 reranker；Graph 记忆相关功能全部保持触发式、mockable、dry-run/read-only。
  - 不读取或打印明文 API Key；测试隔离真实 `.env`，HTTP-facing slug 继续走安全校验，失败降级为 400/404 或前端空态。
- **暂停点**：按用户要求，本刀完成后暂停，不继续自动开新刀；恢复后建议先做 `Graph Memory Provider Spike Opt-in Human Signoff Schema Draft MVP`，仍保持只读、本地边界和真实 provider 禁止。

### 2026-06-03 — Graph Memory Provider Spike Opt-in Human Signoff Schema Draft MVP

- **做了什么**：
  - 新增 `get_graph_memory_provider_spike_opt_in_human_signoff_schema_draft()`，基于 final readiness summary 派生只读人工签收 schema 草案。
  - 新增 `GET /api/stories/<slug>/graph-memory-provider-spike-opt-in-human-signoff-schema-draft`，坏 slug 返回 400，缺项目返回 404。
  - 新增 `lne memory graph-opt-in-human-signoff-schema <slug> --json`，用于命令行查看 schema 草案。
  - 项目工作台新增「Graph 记忆 Provider Spike Opt-in 人工签收 Schema」面板，展示 schema 状态、字段数、必填数、保存签收禁止状态、字段校验规则和下一步建议。
  - 本地 API contract / typed client 新增 `getGraphMemoryProviderSpikeOptInHumanSignoffSchemaDraft`，OpenAPI skeleton endpoint count 更新为 61、path count 更新为 60、typed client method count 更新为 60。
  - 新增 `docs/completed/graph-memory-provider-spike-opt-in-human-signoff-schema-draft-mvp.md`，并同步 `memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、路线图、阶段图、PRD、README、docs index、completed index 与后续增强清单。
- **测试/验证**：
  - RED：新增 focused tests 后，service、HTTP、CLI、API contract 入口缺失导致 **6 failed / 1 passed**。
  - GREEN：`python -m pytest tests\test_graph_memory_provider_spike_opt_in_human_signoff_schema_draft.py tests\test_api_contract.py -q` -> **7 passed**。
  - 相邻回归：PowerShell 展开 `tests\test_graph_memory*.py` 加 `tests\test_api_contract.py` -> **91 passed**。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过。
- **边界**：
  - 只读生成 schema draft，不保存签名、签收值、风险确认、回滚确认或最终结论。
  - 不写项目 artifact、不写决策账本、不创建真实 provider 配置、不调用外部服务、不读取明文 Key。
  - 不改 `run_scene` 默认行为，不接生产向量库、GraphRAG、Zep、外部 embedding provider 或 reranker。
- **下一刀建议**：`Graph Memory Provider Spike Opt-in Config Draft MVP`，基于签收 schema 草案只读生成本地 opt-in 配置草案、字段映射和 adapter 边界；继续不保存配置、不读取明文 Key、不创建真实 provider 配置。

### 2026-06-03 — Graph Memory Provider Spike Opt-in Config and Adapter Slices MVP

- **做了什么**：
  - 新增 `get_graph_memory_provider_spike_opt_in_config_draft()`，基于 human signoff schema draft 生成只读 opt-in 配置草案、字段映射和 adapter 边界。
  - 新增 `get_graph_memory_provider_spike_local_provider_contract()`，基于配置草案生成本地 provider contract、adapter boundary 和 mock-only 方法约束。
  - 新增 `get_graph_memory_provider_spike_single_fixture_dry_run_harness()`，基于本地 contract 生成单 fixture dry-run harness；只允许 `local_mock_only`。
  - 新增 `get_graph_memory_provider_spike_mock_compatible_adapter()`，基于 dry-run harness 生成 mock-compatible adapter 规格、方法要求和 validation cases。
  - 新增四个 API：`graph-memory-provider-spike-opt-in-config-draft`、`graph-memory-provider-spike-local-provider-contract`、`graph-memory-provider-spike-single-fixture-dry-run-harness`、`graph-memory-provider-spike-mock-compatible-adapter`。
  - 新增四个 CLI：`lne memory graph-opt-in-config-draft`、`graph-local-provider-contract`、`graph-single-fixture-dry-run-harness`、`graph-mock-compatible-adapter`。
  - 项目工作台新增四个只读面板；OpenAPI / Typed Client contract 新增四个 endpoint 和 client method。
  - 新增 `docs/completed/graph-memory-provider-spike-opt-in-config-and-adapter-slices-mvp.md`，并同步 memory、路线图、阶段图、PRD、README、handoff、docs index、completed index 与后续增强清单。
- **测试/验证**：
  - RED：新增 focused tests 后，service、HTTP、CLI 入口缺失导致 **5 failed**。
  - GREEN：`python -m pytest tests/test_graph_memory_provider_spike_opt_in_config_and_adapter_slices.py tests/test_api_contract.py -q` -> **8 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 后端完整门禁：第二次 `cd engine && python -m pytest -q` -> **868 passed**；第一次全量出现两个旧 HTTP 测试 socket timeout，两个 focused 复跑均通过，第二次全量未复现。
- **边界**：
  - 不保存配置、不保存签收值、不写项目 artifact。
  - 不读取、不返回、不记录明文 Key。
  - 不创建真实 provider 配置或真实 adapter，不调用外部服务。
  - 不接生产向量库、GraphRAG、Zep、外部 embedding provider、reranker 或真实 LLM。
  - 不改 `run_scene` 默认行为，不替换 BM25、canon ledger、entity aliases 或 retrieval_context。
- **下一刀建议**：`Graph Memory Provider Spike Manual Mock Adapter Review MVP`，基于 mock-compatible adapter 规格做人工复核包与合规检查；继续不保存真实配置、不读取明文 Key、不创建真实 provider 配置。

### 2026-06-03 — CLI / Frontend Product Boundary Documentation

- **做了什么**：
  - 将产品入口边界固化到 `memory.md`、`AGENTS.md`、`engine/README.md`、路线图、阶段图、PRD、handoff 和后续增强清单：前端是产品入口，API 是能力层，CLI 是工程外壳。
  - 明确导入、配置、创作、干预、评审、导出、样本采集和 Graph Memory 证据查看等用户级能力必须优先通过 Web UI + API 完成。
  - 将 CLI 定位为开发者、本地服务启动、自动化验收、批处理、JSON 输出和无人值守复跑的薄封装，不承载独立业务规则，也不作为普通用户唯一入口。
- **测试/验证**：
  - 文档-only 更新；运行 `git diff --check`。
- **边界**：
  - 不改代码、不改 API 契约、不改 `run_scene` 默认行为。
  - 不移除现有 CLI；只调整后续产品/工程分工和文档口径。

### 2026-06-03 — Graph Memory Provider Spike Manual Mock Adapter Review MVP

- **做了什么**：
  - 新增 `get_graph_memory_provider_spike_manual_mock_adapter_review()`，基于 mock-compatible adapter 规格生成只读人工复核包。
  - 新增 `GET /api/stories/<slug>/graph-memory-provider-spike-manual-mock-adapter-review`，坏 slug 返回 400，缺项目返回 404。
  - 新增 `lne memory graph-manual-mock-adapter-review <slug> --json`，用于命令行查看复核包。
  - 项目工作台新增「Graph 记忆 Provider Spike Manual Mock Adapter Review」面板，展示复核行、合规检查、阻断计数、暂停建议和边界说明。
  - 本地 API contract / typed client 新增 `getGraphMemoryProviderSpikeManualMockAdapterReview`，OpenAPI skeleton endpoint count 更新为 66、path count 更新为 65、typed client method count 更新为 65。
  - 新增 `docs/completed/graph-memory-provider-spike-manual-mock-adapter-review-mvp.md`，并同步 `memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、路线图、阶段图、PRD、README、docs index、completed index 与后续增强清单。
- **测试/验证**：
  - RED：新增 API contract 断言后，缺新 path / typed client method 导致 `tests/test_api_contract.py` **2 failed / 1 passed**。
  - GREEN：`python -m pytest tests/test_api_contract.py -q` -> **3 passed**。
  - Focused：`python -m pytest tests/test_graph_memory_provider_spike_manual_mock_adapter_review.py -q` -> **4 passed**。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过。
  - 完整门禁：`cd engine && python -m pytest -q` -> **872 passed**；`git diff --check` 通过，仅有 Windows CRLF 提示。
- **边界**：
  - 只读生成 manual mock adapter review，不保存人工复核结论。
  - 不创建真实 provider adapter 或真实 provider 配置，不写项目 artifact。
  - 不读取、不返回、不记录明文 Key。
  - 不调用 GraphRAG、Zep、图数据库、向量库、reranker、embedding provider 或真实 LLM。
  - 不改 `run_scene` 默认行为，不替换 BM25、canon ledger、entity aliases 或 retrieval_context。
- **暂停点**：按用户要求，本刀完成后暂停继续开发；恢复时先由用户明确下一步。

### 2026-06-03 — Retrieval Provider Real Connectivity MVP

- **做了什么**：
  - 新增/完善 `retrieval_provider_configuration`，默认接入百炼 `text-embedding-v3`、Zilliz Cloud、百炼 `gte-rerank-v2`。
  - 百炼 embedding smoke 使用 OpenAI-compatible `/embeddings` 与 `dimensions=1024`；百炼 reranker smoke 改为官方 text-rerank HTTP payload；Zilliz smoke 使用 `pymilvus.MilvusClient(uri, token)` 只读列集合。
  - 新增 `GET /api/settings/retrieval-provider-configuration` 和 `POST /api/settings/retrieval-provider/test`；`mock=true` 不打外网，`mock=false` 才显式调用真实 provider。
  - 设置抽屉新增「检索增强 Provider」面板，脱敏展示 embedding、Zilliz、reranker 配置状态和本地契约 smoke。
  - `engine/.env.example`、`engine/README.md`、`memory.md`、路线图、阶段图和 PRD 同步新增真实检索 provider 变量与当前边界。
- **测试/验证**：
  - RED：新增 provider tests 后，默认 reranker 仍为 `qwen3-rerank`、缺 DashScope HTTP rerank 调用、缺可 mock 的 Zilliz client 导入点，`tests/test_retrieval_provider_configuration.py` **4 failed / 1 passed**。
  - GREEN：`python -m pytest tests\test_retrieval_provider_configuration.py -q` -> **5 passed**。
  - HTTP RED/GREEN：新增设置端点测试后先因路由缺失失败；补路由后 `python -m pytest tests\test_browser_server.py::test_retrieval_provider_configuration_endpoint_is_secret_safe tests\test_browser_server.py::test_retrieval_provider_mock_smoke_endpoint_is_local_only -q` -> **2 passed**。
  - Focused：`python -m pytest tests\test_retrieval_provider_configuration.py tests\test_browser_server.py::test_retrieval_provider_configuration_endpoint_is_secret_safe tests\test_browser_server.py::test_retrieval_provider_mock_smoke_endpoint_is_local_only -q` -> **7 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
- **边界**：
  - 不创建 Zilliz collection、不写入 embedding、不保存 rerank 结果、不写项目 artifact。
  - 不替换默认 BM25 / canon ledger / entity aliases 检索链路，不改 `run_scene` 默认行为。
  - 设置页和 API 只返回脱敏状态，不返回明文 Key；真实 provider smoke 必须由用户显式触发。
- **下一步建议**：基于真实 retrieval failure samples 做 opt-in 离线索引/检索对照；收益明确后再决定是否写入 Zilliz collection 或接入默认检索。

### 2026-06-03 — Vector Retrieval Pipeline MVP

- **做了什么**：
  - 新增 `vector_retrieval_pipeline` service，支持把项目检索语料 embedding 后写入 Zilliz Cloud collection，并用百炼 embedding + Zilliz search + 百炼 rerank 返回混合检索结果。
  - 新增 `POST /api/stories/<slug>/vector-retrieval/index` 与 `POST /api/stories/<slug>/vector-retrieval/search`；坏 slug 返回 400，缺项目返回 404，provider 配置缺失返回 400。
  - `runtime_memory.build_runtime_memory_context()` 新增 `LNE_RETRIEVAL_STRATEGY=hybrid_vector` opt-in；未设置时继续走 BM25，provider 失败时回退 BM25。
  - OpenAPI / typed client contract 新增 `buildVectorRetrievalIndex` 与 `searchVectorRetrieval`。
  - 项目工作台新增「真实向量检索」面板，可显式构建/刷新索引并做检索预览，不展示明文 Key。
  - 同步 `engine/.env.example`、`engine/README.md`、`memory.md`、路线图、阶段图、PRD 和 handoff。
- **测试/验证**：
  - RED/GREEN：新增 `tests/test_vector_retrieval_pipeline.py` 先定义 Zilliz 写入、混合检索/rerank、runtime opt-in；补实现后通过。
  - Focused：`python -m pytest tests\test_vector_retrieval_pipeline.py tests\test_api_contract.py tests\test_browser_server.py::test_vector_retrieval_index_endpoint tests\test_browser_server.py::test_vector_retrieval_search_endpoint -q` -> **8 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 真实 smoke：`v090-alpha-proof` 写入 `unfinale_memory` 20 条，检索 `退魂铃在哪里响过` 返回 `retrieval_mode=hybrid_vector_rerank`、5 条结果，embedding、Zilliz 和 reranker 均参与，`plaintext_key_returned=false`。
- **边界**：
  - 默认 BM25 / canon ledger / entity aliases 不被替换；运行时必须显式设置 `LNE_RETRIEVAL_STRATEGY=hybrid_vector`。
  - 不写 run artifact，不保存 rerank 结果，不返回明文 Key。
  - 不接 GraphRAG、Zep、图数据库、云端多租户或计费系统。
- **下一步建议**：用真实失败样本复跑 hybrid vector 收益，确认是否把 `hybrid_vector` 作为某些项目的推荐策略；默认替换 BM25 仍需另行确认。

### 2026-06-03 — 后续增强清单同步补记

- **做了什么**：
  - 同步 `docs/后续增强清单.md`，把 Embedding、Zilliz、Reranker 从“未接入/后续接入”更新为“真实 provider 与 Vector Retrieval Pipeline 已显式可用”。
  - 更新 A/B/C/I/J 区块，明确后续工作不再是“接入向量库/reranker”，而是基于真实失败样本做 hybrid vector replay、默认启用建议和 GraphRAG/Zep 继续评估。
- **验证**：`git diff --check` 通过，仅有 Windows CRLF 提示。
- **边界**：文档-only 更新；不改代码、不改 API、不改 `run_scene` 默认行为。

### 2026-06-03 — World Sandbox Remodel 产品纠偏文档

- **做了什么**：
  - 新增 `docs/unfinale-world-sandbox-remodel-prd.md`，明确后续最高优先级切换为 World Sandbox Loop / 世界沙盘改造。
  - 确认主导航采用“世界书架 -> 世界内部卷宗”，不采用“沙盘 / 阅读 / 干预 / 作者”四大一级工作区。
  - 在 `docs/unfinale-product-vision-correction-draft.md` 补充主导航决策和 UI 信息架构。
  - 在 `memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、`docs/index.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/living-novel-engine-prd.md`、`docs/productization-phase-map.md`、`docs/后续增强清单.md` 同步纠偏口径。
  - 明确 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费、对象存储、认证和工程健康报告全部降为支撑层，除非用户明确要求不继续扩张。
  - 梳理现有代码接入关系：导入/创世/世界锚定、干预编译、多 Agent runner、runtime memory、fourth_wall、worldline judge、Reader Panel 和现有 UI 如何服务《天命书》、沙盘轮次、主观记忆链、世界自演、多视角活体小说和作者采纳台。
- **验证**：
  - 文档-only 更新；运行 `git diff --check`。
- **边界**：
  - 不改代码、不改 API、不改 `run_scene` 默认行为。
  - 不删除历史已收口文档；只调整入口优先级和后续执行口径。

### 2026-06-03 — World Sandbox Remodel 入口一致性审计

- **做了什么**：
  - 重新扫描根目录入口、`docs/` 根层文档、`engine/README.md` 和关键接力文档中的“当前迭代点 / 下一步 / provider / Graph / 世界沙盘”相关表述。
  - 修正 `memory.md` 旧“当前自主迭代点”，明确下一刀是 World Sandbox Loop / 世界沙盘改造，不再默认继续 provider、Graph Memory、真实向量检索评测或工程化面板。
  - 修正 `engine/README.md`，把真实检索 provider 和 Vector Retrieval Pipeline 标记为支撑层，并补充当前纠偏主线、目标前端骨架和目标 artifact。
  - 新增 `docs/unfinale-ai-development-alignment-checklist.md`，作为后续 AI 开工前自检清单，要求每刀都服务角色行动、主观记忆、世界变化或可读叙事产物。
  - 同步 `README.md`、`AGENTS.md`、`docs/index.md`、`docs/codex-handoff.md` 和 `memory.md` 的读取顺序，确保新会话会优先读世界沙盘 PRD、产品纠偏草稿和 AI 对齐清单。
- **验证**：
  - 文档-only 更新；运行 `git diff --check`。
  - 运行关键词扫描，确认根入口和关键 docs 的“当前迭代点 / 当前最高优先级”已指向世界沙盘改造。
- **边界**：
  - 不改代码、不改 API、不改 `run_scene` 默认行为。
  - 不删除历史 provider / Graph / 检索评测收口文档；仅把它们从当前主线降为支撑层和历史证据。

### 2026-06-04 — World Sandbox Round MVP

- **做了什么**：
  - 新增 `world_sandbox` service，输入故事世界 slug 和大事件后，本地 deterministic 生成一轮角色行动、冲突、信息传播、世界状态 delta 与后续故事可能性。
  - 新增 `POST /api/stories/<slug>/sandbox/run` 与 `GET /api/sandbox-runs/<run_id>`；HTTP-facing slug/run_id 继续走安全校验，坏 slug/run_id 返回 400，缺项目返回 404。
  - 新增 artifact：`outputs/<run_id>/sandbox_rounds.jsonl` 与 `sandbox_summary.json`；不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
  - 前端新增独立 `WorldSandboxPage`，从“世界书架 -> 世界沙盘”进入，展示角色意图、行动、行动理由、记忆种子、冲突、信息传播、世界状态变化和后续故事可能性；未继续往 `WorkspacePage.tsx` 堆工程支撑面板。
  - 同步 `memory.md`、路线图、世界沙盘 PRD 与 `engine/README.md`，把下一刀切到角色主观记忆链。
- **测试/验证**：
  - RED：新增 `tests/test_world_sandbox.py` 后先因 `living_novel_engine.service.world_sandbox` 缺失失败。
  - GREEN：`cd engine && python -m pytest tests\test_world_sandbox.py -q` -> **3 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
- **边界**：
  - 不改 `run_scene` 默认行为；不引入外部服务、provider、GraphRAG/Zep、向量库或 reranker。
  - 新 artifact/API/UI 均为 additive。
- **下一刀建议**：`Subjective Memory Chain MVP`，基于 `sandbox_rounds.jsonl` 为每个角色/世界线写入 `subjective_memory.jsonl`，并让下一轮行动能引用各自的主观记忆。

### 2026-06-04 — Subjective Memory Chain MVP

- **做了什么**：
  - 扩展 `world_sandbox` service：每轮沙盘成功后，为每个行动角色追加 `projects/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective_memory.jsonl`。
  - 新增 run 侧 `subjective_memory_delta.json`，聚合本轮写入的“看到什么、做了什么、形成什么新认知、情绪/信任/异常感变化”。
  - 下一轮沙盘行动会读取该角色最后一条主观记忆，并把 `previous_subjective_memory` 展示在角色行动卡片中。
  - 新增 `GET /api/stories/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective-memory`；坏 slug/worldline/character id 返回 400，缺项目返回 404。
  - 世界沙盘页新增“角色个人卷雏形”，可点击角色查看自己的主观记忆链，而不是全局正史摘要。
  - 同步 `memory.md`、路线图、世界沙盘 PRD 与 `engine/README.md`，把下一刀切到《天命书》。
- **测试/验证**：
  - RED：新增 v2 测试后先因 `get_character_subjective_memory` 缺失失败。
  - GREEN：`cd engine && python -m pytest tests\test_world_sandbox.py -q` -> **4 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
- **边界**：
  - 不改 `run_scene` 默认行为；不覆盖既有核心 artifact。
  - 角色 ID 写入路径前会收敛为 HTTP-safe identifier，中文角色名保留在展示字段中。
  - 不引入 GraphRAG/Zep、向量库、provider 或真实外部服务。
- **下一刀建议**：`Tianming Book MVP`，生成并轻量确认 `projects/<slug>/tianming.json`，字段至少覆盖 narrative_attractors、genre_constraints、anchor_status、contract_pressure、replacement_anchor_candidates。

### 2026-06-04 — Tianming Book MVP

- **做了什么**：
  - 新增 `tianming` service，基于本地 `world.yaml`、`characters.yaml`、`open_threads.yaml` deterministic 派生 `projects/<slug>/tianming.json` 草案。
  - `tianming.json` 覆盖 `narrative_attractors`、`genre_constraints`、`anchor_status`、`contract_pressure`、`replacement_anchor_candidates`，并明确普通干预不能永久改写《天命书》。
  - 新增 `GET /api/stories/<slug>/tianming`、`POST /api/stories/<slug>/tianming/generate`、`POST /api/stories/<slug>/tianming/confirm`；坏 slug 返回 400，缺项目或缺天命书返回 404。
  - 前端新增“世界内部卷宗 · 天命书”页，可生成草案、查看叙事吸引子/题材约束/候选承载者/干预边界，并用一个按钮轻量确认；不做复杂表单。
  - 同步 `memory.md`、路线图、世界沙盘 PRD 与 `engine/README.md`，把下一刀切到干预编译器读取《天命书》。
- **测试/验证**：
  - RED：新增 `tests/test_tianming.py` 后先因 `living_novel_engine.service.tianming` 缺失失败。
  - GREEN：`cd engine && python -m pytest tests\test_tianming.py -q` -> **3 passed**。
  - 相邻回归：`python -m pytest tests\test_tianming.py tests\test_world_sandbox.py -q` -> **7 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
- **边界**：
  - 不调用外部模型/provider，不接 GraphRAG/Zep，不改 `run_scene` 默认行为。
  - 轻量确认只切换 `tianming.json` 状态和时间戳，不引入复杂表单或永久改写普通干预。
- **下一刀建议**：`Intervention Compiler Reads Tianming MVP`，每次自由干预先读取《天命书》，输出干预类型、层级、兼容性、转译策略、Divergent/AU 判断、分支轴和因果债。

### 2026-06-04 — Intervention Compiler Reads Tianming MVP

- **做了什么**：
  - 新增 `tianming_intervention_compiler` service，读取 `tianming.json` 后对自由干预做 deterministic 预编译。
  - 输出干预类型、层级、兼容性、转译策略、Divergent/AU 判断、分支轴、因果债、审计提示和“不改写天命书”边界。
  - 新增 `POST /api/stories/<slug>/tianming/intervention-compile`；坏 slug 返回 400，缺天命书/缺项目返回 404，空 content 返回 400。
  - 前端“天命书”页新增干预预编译模块，可输入目标角色和自由干预，用卷内注解展示类型、层级、世界线判断、因果债、转译策略和分支轴。
  - 同步 `memory.md`、路线图、世界沙盘 PRD 与 `engine/README.md`，把下一刀切到世界线代偿。
- **测试/验证**：
  - RED：新增 `tests/test_tianming_intervention_compiler.py` 后先因 `living_novel_engine.service.tianming_intervention_compiler` 缺失失败。
  - GREEN：`cd engine && python -m pytest tests\test_tianming_intervention_compiler.py -q` -> **3 passed**。
  - 相邻回归：`python -m pytest tests\test_tianming_intervention_compiler.py tests\test_tianming.py -q` -> **6 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
- **边界**：
  - 不调用 `run_scene`，不写 run artifact，不改写 `tianming.json`。
  - 不引入外部模型/provider、GraphRAG/Zep、向量库或 reranker。
- **下一刀建议**：`Narrative Compensation MVP`，支持锚点转移、候选天命承载者、因果债扩散和失锚世界线，生成 `tianming_delta.json` 并在 UI 解释世界内代偿证据。

### 2026-06-04 — Narrative Compensation MVP

- **做了什么**：
  - 新增 `narrative_compensation` service，读取《天命书》后根据失锚、拒绝、摆烂、离场等触发事件生成世界线代偿。
  - 新增 `outputs/<run_id>/tianming_delta.json`，记录锚点稳定/转移/失锚、候选天命承载者评分、因果债扩散和世界内压力事件。
  - 新增 `POST /api/stories/<slug>/narrative-compensation/run`；坏 slug 返回 400，缺天命书/缺项目返回 404，空 trigger_event 返回 400。
  - 前端“天命书”页新增“世界线代偿”模块，可输入触发事件并展示锚点转移、候选承载者、因果债和政治/关系/势力/环境压力。
  - 同步 `memory.md`、路线图、世界沙盘 PRD 与 `engine/README.md`，把下一刀切到世界自演。
- **测试/验证**：
  - RED：新增 `tests/test_narrative_compensation.py` 后先因 `living_novel_engine.service.narrative_compensation` 缺失失败。
  - GREEN：`cd engine && python -m pytest tests\test_narrative_compensation.py -q` -> **3 passed**。
  - 相邻回归：`python -m pytest tests\test_narrative_compensation.py tests\test_tianming_intervention_compiler.py tests\test_tianming.py -q` -> **9 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
- **边界**：
  - 不做系统管理员式抹杀；代偿压力通过政治、关系、势力和环境自然涌现。
  - 不调用 `run_scene`，不覆盖 `tianming.json`，不引入外部 provider。
- **下一刀建议**：`World Autopilot MVP`，支持运行到轮数、事件、时间或锚点变化，输出 `autopilot_report.json` 和检查点。

### 2026-06-04 — World Autopilot MVP

- **做了什么**：
  - 新增 `world_autopilot` service，连续复用世界沙盘轮次和主观记忆链，生成世界自演报告。
  - 新增 `outputs/<run_id>/autopilot_report.json` 与 `outputs/<run_id>/checkpoints/checkpoint_*.json`，记录运行目标、停止原因、沙盘 run、锚点压力、因果债和后续剧情可能性。
  - 支持 `rounds`、`event`、`time`、`anchor_change` 四种自演目标；事件/时间目标会写入报告 objective 字段并给出 `target_event_reached` 或 `time_limit_reached`。
  - 新增 `POST /api/stories/<slug>/world-autopilot/run`；坏 slug 返回 400，空 seed_event 返回 400，缺项目返回 404。
  - 前端“世界沙盘”页新增“世界自演”控制，可选择运行到轮数、事件、时间或锚点变化，并展示“昨夜世界演化报告”和检查点列表。
  - 同步 `memory.md`、路线图、世界沙盘 PRD 与 `engine/README.md`，把下一刀切到多视角活体小说。
- **测试/验证**：
  - RED：新增事件/时间目标测试后先因 `run_world_autopilot()` 不支持 `stop_event` 失败。
  - GREEN：`cd engine && python -m pytest tests\test_world_autopilot.py -q` -> **4 passed**。
  - 完整后端、前端 build 与 `git diff --check` 待本刀最终验证重新执行。
- **边界**：
  - 不调用 `run_scene`，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 不引入外部模型/provider、GraphRAG/Zep、向量库或真实队列。
  - 自演 UI 进入既有“世界沙盘”页，不继续往 `WorkspacePage.tsx` 堆工程支撑面板。
- **下一刀建议**：`Character Lens Novel MVP`，同一事件读取沙盘轮次、检查点和主观记忆，生成世界正史卷、角色个人卷、势力卷或事件多视角的第一版可读文本。

### 2026-06-04 — Character Lens Novel MVP

- **做了什么**：
  - 新增 `character_lens` service，把同一 `source_event` 转成多视角活体小说 brief。
  - 新增 `outputs/<run_id>/character_lens_briefs.json`，覆盖世界正史卷、主锚点卷、角色个人卷、势力卷和事件多视角。
  - 角色个人卷读取 `subjective_memory.jsonl` 的最新主观记忆，证据源标记为 `subjective_memory`，不是把全局正史摘要换文风。
  - 新增 `POST /api/stories/<slug>/character-lens/generate`；坏 slug 返回 400，空 source_event 返回 400，缺项目返回 404。
  - 前端新增“世界内部卷宗 · 多视角活体小说”页，可输入事件、指定角色个人卷，并展示五类卷宗 brief 与事件多视角角色 voice。
  - 同步 `memory.md`、路线图、世界沙盘 PRD 与 `engine/README.md`，把下一刀切到作者采纳台。
- **测试/验证**：
  - RED：新增 `tests/test_character_lens_novel.py` 后先因 `living_novel_engine.service.character_lens` 缺失失败。
  - GREEN：`cd engine && python -m pytest tests\test_character_lens_novel.py -q` -> **3 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 完整后端、最终前端 build 与 `git diff --check` 待本刀最终验证重新执行。
- **边界**：
  - 不调用 `run_scene`，不覆盖既有章节、事件、状态快照或世界线 artifact。
  - 不引入外部模型/provider、GraphRAG/Zep、向量库或真实队列。
  - 新 UI 按“世界内部卷宗”新增独立页面，不继续往 `WorkspacePage.tsx` 堆工程支撑面板。
- **下一刀建议**：`Author Adoption Desk MVP`，作者模式下把沙盘涌现剧情标记为采纳、部分采纳、另开分支或导出 brief，并支持原大纲 vs 沙盘涌现剧情对照。

### 2026-06-04 — Author Adoption Desk MVP

- **做了什么**：
  - 新增 `author_adoption` service，记录作者对沙盘涌现剧情的采纳决策。
  - 支持 `adopted`、`partial`、`new_branch`、`export_brief` 四种决策；采纳只追加账本，不自动覆盖正史或原大纲。
  - 新增 `projects/<slug>/author_adoption_ledger.jsonl`、`outputs/<run_id>/author_adoption_record.json` 和 `outputs/<run_id>/author_adoption_brief.md`。
  - 支持从 `character_lens_briefs.json` 读取沙盘/多视角涌现材料，也支持作者手动输入 `sandbox_summary`。
  - 新增 `POST /api/stories/<slug>/author-adoption`；坏 slug 返回 400，非法 decision 返回 400，缺项目返回 404。
  - 前端新增“世界内部卷宗 · 作者采纳台”页，可并排编辑原大纲与沙盘涌现剧情，选择采纳、部分采纳、另开分支或导出 brief，并展示账本/导出产物。
  - 同步 `memory.md`、路线图、世界沙盘 PRD 与 `engine/README.md`，标记 World Sandbox Loop v1-v8 第一版闭环已形成。
- **测试/验证**：
  - RED：新增 `tests/test_author_adoption.py` 后先因 `living_novel_engine.service.author_adoption` 缺失失败。
  - GREEN：`cd engine && python -m pytest tests\test_author_adoption.py -q` -> **3 passed**。
  - 完整后端、最终前端 build、浏览器 smoke 与 `git diff --check` 待最终验证重新执行。
- **边界**：
  - 不调用 `run_scene`，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json` 或原大纲。
  - 不引入外部模型/provider、GraphRAG/Zep、向量库或真实队列。
  - 新 UI 是世界内部卷宗独立页面，不继续往 `WorkspacePage.tsx` 堆工程支撑面板。
- **下一步建议**：进入世界沙盘闭环体验打磨：采纳后章节 brief、角色个人卷正文质量、事件多视角证据链和世界内部卷宗之间的连续跳转。

### 2026-06-04 — World Sandbox Loop 文档收口与后续深化路线

- **做了什么**：
  - 对照 `docs/unfinale-ai-development-alignment-checklist.md`、`docs/unfinale-product-vision-correction-draft.md`、`docs/unfinale-world-sandbox-remodel-prd.md` 与当前代码实现，确认 v1-v8 已有本地 deterministic service/API/UI/artifact/tests 第一版。
  - 修正 `docs/unfinale-world-sandbox-remodel-prd.md` 的旧“当前缺口”段落，避免继续把已落地的 `tianming.json`、`subjective_memory.jsonl`、`sandbox_rounds.jsonl`、`autopilot_report.json`、`character_lens_briefs.json` 和作者采纳账本误判为未做。
  - 在 PRD 中新增 S1-S9 后续深化路线：Agent 决策加深、主观记忆心理模型、动态《天命书》、干预执行投放、L5 觉醒反抗、代偿持续驱动、自演任务化、多视角正文和作者采纳反哺章节 brief。
  - 更新 `docs/unfinale-ai-development-alignment-checklist.md`，把第一批 artifact/API 从“建议优先落地”改为“已落地 + 仍需补强”，并新增后续默认迭代判断。
  - 更新 `docs/unfinale-product-vision-correction-draft.md`，在愿景草稿顶部加入 2026-06-04 实现收口，明确当前只是结构化第一版，不等于完整愿景完成。
  - 同步 `memory.md` 与 `AGENTS.md`，强调 v1-v8 已收口是第一版本地闭环口径，后续不要从 v1 重做，也不要回到 provider/Graph/检索评测主线。
- **验证**：
  - 文档-only 更新；运行 `git diff --check`。
- **边界**：
  - 不改代码、不改 API、不改 `run_scene` 默认行为。
  - 不删除历史讨论内容，只给讨论稿和 PRD 增加当前实现状态与后续深化口径。

### 2026-06-04 — S1-S9 产品能力验收口径补充

- **做了什么**：
  - 将用户确认的新纪律写入 `memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、`docs/unfinale-world-sandbox-remodel-prd.md` 和 `docs/unfinale-ai-development-alignment-checklist.md`。
  - 明确小步切片只是工程推进方式，不再把“最小闭环”当作产品完成标准。
  - 明确 `service/API/UI/artifact/tests` 齐全只是工程底线，S1-S9 必须验收到用户能真实感到角色被记忆驱动、干预进入世界、代偿持续影响状态、多视角正文可读、作者采纳反哺下一章 brief。
  - 明确当前正在执行的 S1-S9 先不打断，待完成后按该口径复盘；若未全部达标，第三轮迭代从未达标项继续深化。
- **边界**：
  - 文档-only 更新，不改代码、不改 API、不影响当前正在运行的开发任务。

### 2026-06-04 — S1 Agent Decision Deepening MVP

- **做了什么**：
  - 将世界沙盘行动从固定姿态模板加深为 `deterministic_agent_decision`：每个角色行动读取角色欲望、恐惧、上一轮主观记忆、关系信号、秘密信号、资源信号和《天命书》压力。
  - `sandbox_rounds.jsonl` 的角色行动新增 `decision_inputs`、`visible_action`、`true_intent`、`expected_outcome`、`risk`、`memory_influence` 和 `action_outcome`，同时保留旧 `intent/action/reason/stance` 字段兼容既有读取链路。
  - `subjective_memory_delta.json` 和角色 `subjective_memory.jsonl` 追加记录本轮决策输入、真实意图、风险和行动结果，为 S2 主观心理与信息差模型留证据。
  - 世界沙盘 UI 在角色行动卡展示外在行动、真实意图、决策输入、预期/风险和行动结果；不改 `WorkspacePage.tsx`，不新增工程支撑面板。
  - 同步 `memory.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md` 和 `engine/README.md`，把下一刀切到 S2 主观记忆心理与信息差模型。
- **测试/验证**：
  - RED：新增 `test_second_round_decision_changes_with_subjective_memory`，先因旧行动记录缺少 `decision_mode` 失败。
  - GREEN：`cd engine && python -m pytest tests\test_world_sandbox.py -q` -> **5 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 浏览器 smoke：打开 `http://127.0.0.1:5173/#/world/my-story/sandbox`，运行一轮后确认页面出现“角色行动链 / 真实意图 / 决策输入 / 上一轮记忆 / 天命压力”。
- **边界**：
  - 不调用 `run_scene`，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 不引入 GraphRAG/Zep、检索评测、发行、计费或工程健康面板。
  - 用户已允许真实 API 用于测试和联调；本刀仍保持默认 deterministic/mockable 基线，真实模型 runner smoke 留到显式 opt-in 小刀。
- **下一刀建议**：`S2 Subjective Memory Psychology MVP`，让同一事件至少两个角色写出互相矛盾但各自合理的主观记忆，区分已知事实、误以为的事实、真实意图、秘密可见性和异常感权重。

### 2026-06-04 — S2 Subjective Memory Psychology MVP

- **做了什么**：
  - 将角色 `subjective_memory.jsonl` 从“看到/做了/新认知”加深为主观心理与信息差记录，新增 `perceived_event`、`inner_thought`、`inferred_motive`、`emotional_impact`、`trust_shift`、`anomaly_weight`、`secret_visibility`、`known_truths`、`misbeliefs`、`unknown_canon_facts`、`suppressed_memory`、`worldline_residue` 和 `awareness_level`。
  - 同一大事件会被不同角色写成互相矛盾但各自合理的主观记忆；下一轮沙盘冲突会读取上一轮 `misbeliefs`，让误会成为冲突来源。
  - 世界沙盘 UI 的“角色个人卷雏形”新增主观感知、内心想法、推测动机、误会、未知正史、秘密可见性和异常权重展示。
  - 同步 `memory.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md` 和 `engine/README.md`，把下一刀切到 S3《天命书》世界线宪法或 S2 深层召回/误会图谱。
- **测试/验证**：
  - RED：新增 `test_subjective_memories_record_contradictory_perspectives`，先因旧记忆缺少 `perceived_event` 失败。
  - GREEN：`cd engine && python -m pytest tests\test_world_sandbox.py -q` -> **6 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 浏览器 smoke：打开 `http://127.0.0.1:5173/#/world/my-story/sandbox`，运行一轮后确认页面出现“角色个人卷雏形 / 主观感知 / 内心想法 / 推测动机 / 误会 / 未知正史 / 秘密可见性”。
- **边界**：
  - 不调用 `run_scene`，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 不引入 GraphRAG/Zep、检索评测、发行、计费或工程健康面板。
  - 仍保持 deterministic/mockable 基线；真实模型 runner smoke 留到显式 opt-in 小刀。
- **下一刀建议**：`S3 Tianming Worldline Constitution MVP`，将《天命书》升级为多叙事吸引子、多锚点、压力等级和世界线快照；或继续 S2 深层召回/误会图谱。

### 2026-06-04 — 真实模型 smoke 验收口径补充

- **做了什么**：
  - 将用户确认的真实 API 测试偏好写入 `memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/unfinale-world-sandbox-remodel-prd.md` 和 `engine/README.md`。
  - 明确 mock/deterministic 测试仍作为单元测试、契约测试和回归测试底线。
  - 明确涉及 Agent 决策、叙事生成、章节 brief、多视角正文、Reviewer 或视觉质量的切片，若 `.env` 已配置真实 key，应额外做小样本真实模型 smoke。
  - 明确真实 smoke 需要记录真实输出质量、失败原因和回退情况，但不得打印明文 key，不做大规模消耗，也不塞进默认全量 pytest。
- **边界**：
  - 文档-only 更新；本次不主动调用真实 API，不影响当前正在运行的开发任务。

### 2026-06-04 — 独立切片提交与远程推送纪律补充

- **做了什么**：
  - 将用户指出的“AI 修改完成后没有及时推送远程”问题写入 `memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、`docs/unfinale-ai-development-alignment-checklist.md` 和 `docs/unfinale-world-sandbox-remodel-prd.md`。
  - 明确独立切片完成并验证通过后，默认要提交并推送远程，除非用户明确要求暂不提交或暂不推送。
  - 明确推送前必须检查 `git status`，只提交本轮负责的文件，不能混入用户改动或另一轮 AI 的未完成改动。
  - 明确无远程、无上游、认证失败、网络失败或当前长任务尚未形成可验证 checkpoint 时，要说明未推送原因。
- **边界**：
  - 文档-only 更新；当前工作树存在其他开发改动时，本条规则不要求立即混推半成品。

### 2026-06-04 — S3 Tianming Worldline Constitution MVP

- **做了什么**：
  - 将根 `tianming.json` 从静态草案加深为世界线宪法雏形，新增 `constitution_schema_version`。
  - `narrative_attractors` 新增权重和类别，并保留 deterministic fallback 吸引子；`anchor_status.anchors` 新增角色、势力、谜团、地点多锚点；`contract_pressure.pressure_tiers` 新增轻微压力、重大压力、时代压力和世界崩坏压力四档。
  - 旧版已确认 `tianming.json` 在生成或读取时会保守补齐 S3 宪法字段，并保留既有吸引子，避免旧项目页面缺少权重/多锚点/压力四档。
  - `compile_intervention_against_tianming()` 和 `POST /api/stories/<slug>/tianming/intervention-compile` 支持 `worldline_id`；L4/L5 或 AU 干预会写 `projects/<slug>/worldlines/<worldline_id>/tianming_snapshot.json`，并返回 `worldline_tianming_snapshot`。
  - 世界线快照只写新 artifact，不覆盖根 `tianming.json`；快照合约压力会升级到时代或世界崩坏档。
  - 天命书页新增投放世界线输入、吸引子权重/类别、多锚点、四档压力和世界线快照展示；可见文案保持中文。
  - 同步 `memory.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/unfinale-product-vision-correction-draft.md` 和 `engine/README.md`，把下一刀切到 S4 干预可执行投放或 S2 深层召回。
- **测试/验证**：
  - RED：新增 S3 字段和世界线快照测试后，先因根天命书缺少宪法字段、编译器不写快照失败；补旧版已确认天命书升级断言后，先因旧吸引子被替换失败。
  - GREEN：`cd engine && python -m pytest tests\test_tianming.py tests\test_tianming_intervention_compiler.py -q` -> **9 passed**。
  - 浏览器 smoke：打开 `http://127.0.0.1:5173/#/world/my-story/tianming`，生成天命书后确认页面出现权重、多锚点、四档压力；Chrome headless + CDP 提交 L5 干预到 `reader_cdp_ui` 后确认 DOM 出现 `worldlines/reader_cdp_ui/tianming_snapshot.json` 和“根天命书未被覆盖”。
  - 完整后端、前端 build 与 `git diff --check` 在最终收口时重新执行。
- **边界**：
  - 不调用 `run_scene`，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。
  - S3 第一刀仍是 deterministic/mockable 基线；动态吸引子、锚点转移后自动刷新、作者确认/审计和后续沙盘消费留给后续 S3/S4/S6 深化。
- **下一刀建议**：`S4 Intervention Execution Injection MVP`，让干预编译结果成为下一轮沙盘约束，支持沉浸模式 / 暴走 AU 模式，并让普通干预进入 Divergent Worldline。

### 2026-06-04 — S4 Intervention Execution Constraint MVP

- **做了什么**：
  - `run_sandbox_round()` 新增可选 `intervention_content`、`intervention_target` 和 `intervention_constraint`，无干预时保持旧沙盘路径。
  - `POST /api/stories/<slug>/sandbox/run` 可接收本轮干预文本，先读取《天命书》并复用干预编译器，生成 `intervention_constraint.json`。
  - `sandbox_rounds.jsonl` 新增 `intervention_constraint`；角色 `decision_inputs` 新增干预约束、分支轴、因果债和投放对象；角色行动、行动结果、冲突原因、信息流和 `world_state_delta.intervention_effects` 会体现本轮干预。
  - 世界沙盘页新增可选“本轮干预 / 投放对象”输入，并在结果区展示法则吸收、命运线、因果债和投放结果。
  - 同步 `memory.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md` 和 `engine/README.md`，把下一刀切到 S4 沉浸/AU 投放确认或 S5 觉醒反抗。
- **测试/验证**：
  - RED：新增 `test_sandbox_round_consumes_tianming_intervention_as_executable_constraint` 和 HTTP 断言后，先因 `run_sandbox_round()` 不接受 `intervention_content`、响应缺少 `intervention_constraint` 失败。
  - GREEN：`cd engine && python -m pytest tests\test_world_sandbox.py tests\test_tianming_intervention_compiler.py -q` -> **11 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
- **边界**：
  - 不调用 `run_scene`，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 普通干预只作为本轮沙盘约束和 Divergent Worldline 压力，不覆盖根 `tianming.json`。
  - 不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。
  - S4 第一刀仍是 deterministic/mockable 基线；沉浸模式 / 暴走 AU 模式确认、分支继续运行和 L4/L5 快照审计留给后续切片。
- **下一刀建议**：继续 S4 的沉浸模式 / 暴走 AU 模式确认与分支继续运行，或进入 `S5 L5 Awareness and Resistance MVP`，让角色能拒绝、假意服从、欺骗读者或传播高维真相。

### 2026-06-05 — S4 Immersive / Wild AU Projection MVP

- **做了什么**：
  - `compile_intervention_against_tianming()` 新增 `projection_mode=immersive|wild_au`，默认 `immersive` 保持旧调用兼容。
  - `POST /api/stories/<slug>/tianming/intervention-compile` 支持 `projection_mode`；AK47、枪、子弹、热武器等会被标记为 `foreign_object_intrusion`。
  - 沉浸模式把 AK47 等异物本土化重释为雷鸣弩、连珠雷火机关或等价神器，生成 Divergent Worldline，不写世界线快照。
  - 暴走 AU 模式保留异物入侵，生成 AU 判断与 `worldlines/<worldline_id>/tianming_snapshot.json`，并保持根 `tianming.json` 不被覆盖。
  - `run_sandbox_round()` 和 `POST /api/stories/<slug>/sandbox/run` 新增 `intervention_projection_mode`；投放模式进入 `intervention_constraint.json`、角色 `decision_inputs` 和 `world_state_delta.intervention_effects`。
  - 天命书页和世界沙盘页新增“沉浸模式 / 暴走 AU”选择，结果区展示投放方式、异物入侵提示和世界线天命书快照。
  - 同步 `memory.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/unfinale-product-vision-correction-draft.md` 和 `engine/README.md`，把下一刀切到 S4 分支持续运行 / 快照审计确认或 S5 觉醒反抗。
- **测试/验证**：
  - RED：新增 `test_ak47_intervention_can_choose_immersive_translation_or_wild_au`、HTTP `projection_mode=wild_au` 断言和 `test_sandbox_round_can_project_intervention_as_wild_au_constraint` 后，先因函数不接受 `projection_mode` / `intervention_projection_mode` 失败。
  - GREEN：`cd engine && python -m pytest tests\test_tianming_intervention_compiler.py tests\test_world_sandbox.py -q` -> **13 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
- **边界**：
  - 不调用 `run_scene`，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 暴走 AU 只写世界线《天命书》快照，不覆盖根《天命书》；快照审计确认和分支持久继续运行仍留给后续 S4。
  - 不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。
- **下一刀建议**：继续 S4 的分支持续运行、L4/L5 世界线快照审计确认和多轮分支追踪，或进入 `S5 L5 Awareness and Resistance MVP`。

### 2026-06-05 — S4-S9 Continuous Worldline Productization

- **做了什么**：
  - 新增 `worldline_state` service 与 `projects/<slug>/worldlines/<worldline_id>/worldline_state.json`，把来源干预、沉浸/AU 投放、L4/L5/AU 快照审计状态、因果债、锚点状态、候选天命承载者、模因污染和作者采纳结果绑定为可继续运行的世界线状态。
  - `run_sandbox_round()` 会在同一世界线后续轮次读取 `worldline_state.json`；若没有新干预，也会继续消费旧干预约束、天命书快照审计状态、因果债和分支承接。
  - L5 干预会让角色行动和主观记忆写入高维觉醒、命痕、反抗行为、异常感、模因污染；角色可假意服从、拒绝、欺骗读者、保护他人或继续使命，世界以关系网/势力/环境代偿而非管理员重置。
  - 世界状态 delta 新增分支承接、代偿效果和模因污染；因果债先压向当前锚点，再外溢到关系网、势力和环境，候选承载者上位或失败有欲望、资源、能力和阻力解释。
  - 世界自演新增本地任务状态、进度、暂停/恢复和 checkpoint replay；`autopilot_report.json` 新增“醒来可读”的 overnight report。
  - 多视角活体小说从 `character_lens_briefs.json` 扩展为 `character_lens_volumes.json`，生成世界正史卷、主锚点卷、角色个人卷和事件多视角正文，并带沙盘轮次、主观记忆、世界状态 delta、干预/因果债证据链。
  - 作者采纳台新增 `next_chapter_brief.json`、原大纲差异、伏笔调整和 Reviewer 建议，并把下一章 brief 回写 `worldline_state.json`，后续沙盘可读取采纳结果。
  - 新增 API：`GET /api/stories/<slug>/worldlines/<worldline_id>/worldline-state`、自演任务查询/暂停/恢复、`GET /api/world-autopilot-runs/<run_id>/checkpoints/<checkpoint_id>`。
  - 前端世界沙盘页展示世界线承接、快照审计、因果债、下一轮继续、L5 命痕/反抗、模因传播和自演任务进度；多视角页展示正文卷宗；作者采纳台展示下一章可写方案、伏笔调整和 Reviewer 建议。
  - 同步 `memory.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：新增世界线状态持续、L5 觉醒反抗、自演任务/检查点回放、多视角正文证据链、作者采纳反哺测试，先分别因缺 `worldline_state.json`、缺 `awareness`、缺自演 `task`、缺 `character_lens_volumes`、缺 `next_chapter_brief` 失败。
  - GREEN：`cd engine && python -m pytest tests\test_world_sandbox.py tests\test_world_autopilot.py tests\test_character_lens_novel.py tests\test_author_adoption.py -q` -> **23 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 真实模型 smoke：使用 `.env` 中 `LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1` 与 `LLM_MODEL_NAME=qwen3.5-plus`，不打印明文 key；模型判断 L5 假意服从/保护同伴、世界内因果债代偿和沈冰月误判形成的信息差基本成立，提示风险是“因果债若表现太抽象，危机感易稀释”。
- **边界**：
  - 不调用 `run_scene`，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 新 artifact/API/UI 字段均 additive；默认 pytest 仍 mock-safe，真实模型 smoke 不进入默认测试。
  - 不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。
- **下一刀建议**：
  - 把因果债从文字解释具象为可持续的地点、资源、伤势、舆论、势力行动和环境变化。
  - 补世界线页/检查点页独立 UI 与采纳后章节生成入口。
  - 在 opt-in 小样本里继续接真实 LLM 多 Agent 决策和多视角长正文质量控制。

### 2026-06-05 — S6 Materialized Consequence State

- **做了什么**：
  - 新增 `worldline_state.consequence_state`，把因果债从抽象文字说明具象为地点、资源、伤势、舆论、势力和环境六个世界内域，并保留近轮 ledger。
  - 后续 `sandbox/run` 会读取同一世界线的具象代偿，写入角色 `decision_inputs.worldline_consequences`，并在 `world_state_delta.consequence_state` 中展示继承后果。
  - 世界自演 checkpoint 和 overnight report 新增具象代偿状态，醒来报告能说明世界为何变化，而不只显示因果债等级。
  - 多视角正文读取 `consequence_state`，世界正史卷会写出封锁、资源扣押、伤势/梦魇、舆论、势力追索和环境异象；evidence chain 新增 `consequence_state_refs`。
  - 作者采纳后的 `next_chapter_brief.json` 新增 `materialized_consequences`，并回写 `worldline_state.next_chapter_brief`，下一章方案必须延续这些世界内代价。
  - 世界沙盘页新增「具象代偿账」展示，用户可看到因果债落到哪些世界域上。
  - 同步 `memory.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：新增世界线具象代偿、多视角 evidence、作者采纳 materialized consequences、自演 checkpoint 断言后，先分别因缺 `consequence_state`、缺 `consequence_state_refs`、缺 `materialized_consequences`、checkpoint 缺字段失败。
  - GREEN：`cd engine && python -m pytest tests\test_world_sandbox.py tests\test_world_autopilot.py tests\test_character_lens_novel.py tests\test_author_adoption.py -q` -> **25 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **922 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - `git diff --check` 通过，仅有 CRLF 提示。
  - 真实模型 smoke：使用 `.env` 中 `LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1` 与 `LLM_MODEL_NAME=qwen3.5-plus`，不打印明文 key；模型判断六域映射让债务具象为叙事阻力，因果债已内化为世界内后果，风险是多视角卷宗和下一章 brief 需要持续显化多个域，避免代价感知断裂。
- **边界**：
  - 不调用 `run_scene`，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 新 artifact/API/UI 字段均 additive；默认 pytest 仍 mock-safe。
  - 不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。
- **下一刀建议**：
  - 补世界线页/检查点页独立 UI 与采纳后章节生成入口。
  - 在 opt-in 小样本里继续接真实 LLM 多 Agent 决策和多视角长正文质量控制。

### 2026-06-05 — Worldline Dossier / Checkpoint Replay Pages

- **做了什么**：
  - 新增 `worldline_dossier` service 与 `GET /api/stories/<slug>/worldlines/<worldline_id>/dossier`，只读聚合 `worldline_state.json`、天命快照审计、自演任务和 autopilot checkpoints。
  - dossier 返回下一步动作：继续沙盘、管理自演任务、回放最新检查点，帮助用户理解“这条世界线下一轮如何继续”。
  - 前端新增 `#/world/<slug>/worldlines/<worldline_id>` 世界线档案页，展示来源干预、投放方式、快照审计、因果债、下一轮读取字段、具象代偿、自演任务、暂停/恢复和检查点列表。
  - 前端新增 `#/world/<slug>/worldlines/<worldline_id>/checkpoints/<run_id>/<checkpoint_id>` 检查点回放页，展示大事件、世界阶段、谁记住了什么、具象代偿和后续可写方向。
  - 世界沙盘页和自演检查点卡片新增跳转入口；顶栏新增“世界线”入口，不再只把世界线状态藏在沙盘结果区。
  - 同步 `memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/unfinale-product-vision-correction-draft.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：新增 `tests/test_worldline_dossier.py` 后，先因缺 `living_novel_engine.service.worldline_dossier` 失败。
  - GREEN：`cd engine && python -m pytest tests/test_worldline_dossier.py -q` -> **2 passed**。
  - Focused：`cd engine && python -m pytest tests/test_world_autopilot.py tests/test_worldline_dossier.py -q` -> **7 passed**；`cd engine && python -m pytest tests/test_world_sandbox.py tests/test_worldline_dossier.py tests/test_v075_worldline_judge.py -q` -> **22 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 浏览器：本地打开 `#/world/v090-alpha-proof/worldlines/main`，确认世界线页标题、分支状态和下一步区域可见；截图保存到 `.local-run/worldline-dossier-page.png`（不提交）。
- **边界**：
  - dossier 是只读聚合，不写新 artifact，不覆盖根《天命书》，不调用 `run_scene`。
  - 新 API/UI 字段均 additive；坏 slug/worldline 返回 400，缺项目返回 404。
  - 本刀是页面与聚合入口，不涉及新的叙事生成质量调用；真实模型 smoke 仍沿用上一刀 S6 的结果，本刀未额外消耗。
  - 不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。
- **下一刀建议**：
  - 接作者采纳后的正式章节生成入口。
  - 在 opt-in 小样本里继续接真实 LLM 多 Agent 决策和多视角长正文质量控制。

### 2026-06-05 — S9 Author Chapter Draft Entry

- **做了什么**：
  - 新增 `author_chapter_draft` service，把作者采纳 run 的 `author_adoption_record.json`、`next_chapter_brief.json`、世界线状态和具象代偿生成为正式下一章草稿。
  - 新增 artifact：`outputs/<run_id>/next_chapter_draft.json` 和 `outputs/<run_id>/next_chapter_draft.md`，包含章节正文、采纳/brief/世界线证据链、Reviewer 检查和边界说明。
  - `author-chapter-draft-v1.1` 会在上游缺少六域代偿时，从下一章沙盘入口派生一条世界内代偿证据，避免默认作者台草稿出现“延续世界内具象代偿”待补。
  - 新增 API：`POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-draft`；坏 slug/run_id 返回 400，缺采纳 run 返回 404，默认 `mock=true` 保持 deterministic。
  - 作者采纳台新增“生成下一章草稿”按钮，展示可读正文、导出 artifact、证据链和 Reviewer 检查，让 S9 从 brief 进入正文入口。
  - 同步 `memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/unfinale-product-vision-correction-draft.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：新增 `test_author_chapter_draft_turns_adoption_brief_into_readable_chapter` 后，先因缺 `living_novel_engine.service.author_chapter_draft` 失败。
  - GREEN：`cd engine && python -m pytest tests/test_author_adoption.py -q` -> **5 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - API smoke：本地 HTTP 后端返回 `version=author-chapter-draft-v1.1`，默认作者采纳路径包含派生 `materialized_consequences`，Reviewer 四项均通过。
  - 真实模型 smoke：使用 `.env` 中真实 LLM 配置，不打印明文 key；`mock=False` 返回 `generated_by=llm`，生成 1101 字正文，命中赵轩、沈冰月、信息差和世界代偿检查，Reviewer checklist 全部通过。
- **边界**：
  - 章节草稿只写入作者采纳 run 目录，不覆盖正史 `chapter.md`，不调用 `run_scene`，不破坏既有核心 artifact。
  - 新 API/UI/artifact 均 additive；默认 pytest 仍 mock-safe，真实模型 smoke 不进入默认测试。
  - 不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。
- **下一刀建议**：
  - 继续真实 LLM 多 Agent 决策 smoke，让沙盘行动从模板进一步变成角色策略博弈。
  - 增加作者可编辑确认、局部重写和正式入卷入口。
  - 加强多视角/章节长正文质量控制与跨卷宗连续阅读。

### 2026-06-05 — S9 Author Chapter Confirmation Entry

- **做了什么**：
  - 新增 `author_chapter_confirmation` service，把作者采纳 run 的 `author_adoption_record.json`、`next_chapter_brief.json` 和 `next_chapter_draft.json` 确认为正式入卷记录。
  - 新增 artifact：`outputs/<run_id>/confirmed_chapter_entry.json` 和 `outputs/<run_id>/confirmed_chapter.md`，包含作者编辑后的正文、证据链、Reviewer 检查、确认备注和下一轮沙盘入口。
  - 新增世界线状态回写：`worldline_state.confirmed_chapter_entry`、`confirmed_chapter_entries` 和 `continuation_inputs`；`branch_state.next_round_reads` 新增 `confirmed_chapter_entry`，后续沙盘可读取确认后的章节入口。
  - 新增 API：`POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-confirmation`；坏 slug/run_id 返回 400，缺采纳 run 或缺草稿返回 404。
  - 作者采纳台新增草稿编辑区、确认备注和“确认入卷”按钮，确认后展示入卷 artifact、世界线状态、下一轮沙盘入口和 Reviewer 检查。
  - 同步 `memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/unfinale-product-vision-correction-draft.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：新增 `test_author_chapter_confirmation_formalizes_edited_text_for_worldline` 和 HTTP 确认入卷断言后，先因缺 `living_novel_engine.service.author_chapter_confirmation` 失败。
  - GREEN：`cd engine && python -m pytest tests/test_author_adoption.py -q` -> **6 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **926 passed**。第一次 5 分钟超时未得出结论，第二次用更长超时通过。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 真实模型 smoke：复用上一刀真实 LLM 草稿生成链路；确认环节不调用模型，只用真实模型生成的正文加作者编辑文本确认入卷，Reviewer 全通过，确认结果写入世界线状态并生成后续沙盘入口。
- **边界**：
  - 确认入卷只写入作者采纳 run 目录和 `worldline_state.json`，不覆盖正史 `chapter.md`，不调用 `run_scene`，不破坏既有核心 artifact。
  - 新 API/UI/artifact 均 additive；默认 pytest 仍 mock-safe，真实模型 smoke 不进入默认测试。
  - 不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。
- **下一刀建议**：
  - 继续真实 LLM 多 Agent 决策 smoke，让沙盘行动从模板进一步变成角色策略博弈。
  - 加强章节草稿/确认稿的局部重写、更强 Reviewer 和长正文质量控制。
  - 补跨卷宗连续阅读，让确认后的章节能跳回世界正史卷、角色个人卷和事件多视角证据。

### 2026-06-05 — S9 Confirmed Chapter Reading Trail

- **做了什么**：
  - `author_chapter_confirmation` 新增 `confirmed_chapter_reading_trail.json`，在作者确认入卷时把确认稿、`worldline_state.json`、来源作者采纳记录和来源 `character_lens_volumes.json` 串成跨卷宗阅读链。
  - 阅读链会记录来源 lens run、来源 sandbox run、世界正史卷、角色个人卷、事件多视角、角色个人卷事件节点数和证据 refs；缺少来源 lens run 时降级为 partial，不阻断确认入卷。
  - `confirmed_chapter_entry.json` 的 `evidence_chain` 和 `artifacts` 新增 reading trail 字段，Reviewer 增加“可回读世界正史卷、角色个人卷和事件多视角”检查。
  - 作者采纳台的确认结果区新增“跨卷宗阅读链”，展示来源沙盘、阅读链状态、每个卷宗入口、角色事件节点数和证据引用。
  - 同步 `memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/unfinale-product-vision-correction-draft.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：新增 `test_author_chapter_confirmation_links_back_to_cross_volume_evidence` 后，先因确认报告缺少 `confirmed_chapter_reading_trail` 失败。
  - GREEN：`cd engine && python -m pytest tests/test_author_adoption.py -q` -> **7 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **927 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 真实模型 smoke：使用 `.env` 中真实 LLM 配置，不打印明文 key；生成真实下一章草稿后确认入卷，reading trail 为 ready，包含世界正史卷、角色个人卷和事件多视角，Reviewer 全通过。
  - UI 验收：`pnpm run build` 已覆盖作者采纳台新增类型与渲染路径。尝试用 in-app Browser 打开本地 Vite 页面时，`127.0.0.1`、`localhost` 与 `[::1]` 均被客户端以 `ERR_BLOCKED_BY_CLIENT` 拦截；本刀未拿到可用浏览器截图，后续若需视觉复核可在浏览器可访问本地端口后补测。
- **边界**：
  - 只写作者采纳 run 目录和 `worldline_state.json`；不覆盖正史 `chapter.md`，不调用 `run_scene`，不破坏既有核心 artifact。
  - 新 API/UI/artifact 字段均 additive；默认 pytest 仍 mock-safe，真实模型 smoke 不进入默认测试。
  - 不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。
- **下一刀建议**：
  - 继续真实 LLM 多 Agent 决策 smoke，让沙盘行动从模板进一步变成角色策略博弈。
  - 加强章节草稿/确认稿的局部重写、更强 Reviewer 和长正文质量控制。
  - 把 reading trail 从证据列表升级为正文内跳转阅读，直接打开世界正史卷、角色个人卷和事件多视角对应段落。

### 2026-06-05 — S5 L5 Meme Propagation Memory MVP

- **做了什么**：
  - 在 `world_sandbox` 中补齐 L5 高维真相传播链：直接觉醒者写入命痕、反抗行为和模因污染后，会向其他角色传播“我是小说人物/被高维操控”的真相。
  - 新增 `meme_propagation` additive 字段，记录传播来源、真相载荷、采信/存疑/拒信、可信度、人设/关系/上一轮记忆/异常感信号和反应类型。
  - 同一份传播证据写入 `sandbox_rounds.jsonl`、`subjective_memory_delta.json`、角色 `subjective_memory.jsonl`、`worldline_state.meme_contamination.propagation` 和 `information_flow`。
  - 世界沙盘页和角色个人卷雏形新增命痕回声、觉醒度、传播来源、是否采信、可信度、采信原因和反应展示。
  - 同步 `memory.md`、`AGENTS.md`、`docs/codex-handoff.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：新增 `test_l5_meme_truth_propagates_with_belief_reactions_in_subjective_memory` 后，先因没有 `meme_propagation.status=received` 失败。
  - GREEN：`cd engine && python -m pytest tests/test_world_sandbox.py -q` -> **13 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
- **边界**：
  - 本刀不调用 LLM、不改 `run_scene` 默认行为，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 当前采信判断仍是 deterministic 规则版，证明传播证据链和主观记忆写入成立；真实 LLM 心理推演、长期思想瘟疫演化和跨轮政治/宗门/战争压力仍需后续深化。
  - 不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。

### 2026-06-05 — S9 Author Adoption Feed-forward Pack

- **做了什么**：
  - `author_adoption` service 对 `adopted`、`partial`、`new_branch` 三种采纳结果生成更完整的 `next_chapter_brief.json`，新增 `writing_plan` 和 `feed_forward`。
  - `writing_plan` 输出可读下一章 brief、原大纲差异、伏笔调整、具象代偿延续和 Reviewer/人工修订建议；`feed_forward` 输出 `chapter_generation_inputs`、`sandbox_continuation_inputs` 和 `next_round_reads`，让后续章节生成和世界沙盘继续入口有明确可审计输入。
  - 部分采纳会保留 `manual_review_points` 和 `unresolved_conflicts`；另开分支会创建新的作者分支 `worldline_state.json`，后续入口指向作者分支，来源世界线和根正史不被覆盖。
  - 作者采纳台新增“原大纲 vs 沙盘涌现剧情 vs 下一章可写方案”三栏展示，并显示反哺状态、作者分支、后续读取清单和 Reviewer 提醒。
  - 同步 `memory.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/codex-handoff.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：新增 `test_author_adoption_decisions_build_distinct_chapter_feed_forward` 后，先因 `next_chapter_brief` 缺少 `writing_plan` 失败。
  - GREEN：`cd engine && python -m pytest tests/test_author_adoption.py -q` -> **8 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **930 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过，仅有 Windows 换行提示。
  - 真实模型 smoke：临时项目执行 adopted 决策后调用 `generate_author_chapter_draft(..., mock=False)`；`next_chapter_brief` 含 `writing_plan` / `feed_forward`，真实 LLM 生成 995 字正文，Reviewer 全通过，未打印明文 key。
- **边界**：
  - 新 service/API/UI/artifact 字段均 additive；不改 `run_scene` 默认行为，不覆盖 `chapter.md`、根正史或既有核心 artifact。
  - 本刀聚焦 S9 采纳结果反哺，不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。

### 2026-06-05 — S9 Draft Revision Pack

- **做了什么**：
  - `author_chapter_draft` 从 `author-chapter-draft-v1.1` 升级到 `author-chapter-draft-v1.2`，生成下一章草稿时同步输出 `draft_revision_pack.json`。
  - `next_chapter_draft.json` 新增 `revision_pack`，包含确认前 gate、局部改写建议、建议改法、对应段落、证据引用和边界说明。
  - 作者采纳台草稿编辑区新增“局部修订包”，在作者点击“确认入卷”前展示可确认/需修订状态、修订摘要、局部改写建议和证据引用。
  - 同步 `memory.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：先在 `test_author_chapter_draft_turns_adoption_brief_into_readable_chapter` 中要求 `revision_pack` 与 `draft_revision_pack.json`，测试因缺少 `revision_pack` 失败。
  - GREEN：`cd engine && python -m pytest tests/test_author_adoption.py -q` -> **8 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **930 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过，仅有 Windows 换行提示。
  - 真实模型 smoke：临时项目执行 adopted 决策后调用 `generate_author_chapter_draft(..., mock=False)`；真实 LLM 生成 1047 字正文，Reviewer 4 项全通过，`revision_pack.status=ready`，包含 3 条局部改写建议，未打印明文 key。
  - UI smoke：启动本地后端与 Vite，打开 `#/world/my-story/author`，执行“写入采纳台 -> 生成下一章草稿”；页面出现“局部修订包”、确认 gate 和建议内容，控制台无 error。烟测后已停止 5173/5174/8765 本地服务。
- **边界**：
  - 修订包只写作者采纳 run 目录，不自动改写草稿正文，不覆盖正史 `chapter.md`，不调用 `run_scene`。
  - 新字段、artifact 和 UI 均 additive；默认 pytest 仍 mock-safe，真实 LLM smoke 不进入默认测试。
  - 本刀聚焦 S9 语义 Reviewer / 局部重写第一刀，不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。

### 2026-06-06 — S1 LLM Agent Decision Advisory

- **做了什么**：
  - `world_sandbox` 新增显式 opt-in 的 `llm_decision_mode=advisory`，默认 `deterministic` 不变；不改 `run_scene` 默认行为。
  - 启用后会把本轮角色 baseline、决策输入、主观记忆、干预约束和世界线状态批量交给真实 LLM，生成逐角色决策建议，并写入 `outputs/<run_id>/agent_decision_advisory.json`。
  - 角色行动新增 `llm_decision_advisory`，包含采信/存疑、欺骗或隐瞒、传播或压住信息、反抗或顺势利用、临场判断、信任移动和记忆种子；命中角色的 `visible_action`、`true_intent`、`expected_outcome`、`risk` 和主观记忆种子会被 advisory 覆盖，同时保留 deterministic baseline。
  - `POST /api/stories/<slug>/sandbox/run` 接收 `llm_decision_mode` / `llm_decision_mock` 字段；非法模式返回 400，不静默忽略。
  - 世界沙盘页新增“启用真实模型决策建议”勾选项，并在本地产物、模型决策建议区和角色行动卡展示 advisory 状态与五类决策字段。
  - 同步 `memory.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：新增 `test_llm_decision_advisory_overlays_character_choices` 后，先因 `run_sandbox_round()` 不支持 `llm_decision_mode` 失败。
  - GREEN：`cd engine && python -m pytest tests/test_world_sandbox.py -q` -> **14 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **931 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 真实模型 smoke：临时项目显式启用 `llm_decision_mode=advisory`；真实 LLM 返回 `ready`，命中 3 个角色，首个角色包含 `belief_update`、`deception_strategy`、`propagation_choice`、`resistance_choice`、`situational_judgement` 五类字段，未打印明文 key。
- **边界**：
  - 新参数、artifact、API 字段和 UI 均 additive；默认沙盘仍走 deterministic，不调用真实模型。
  - advisory 是单轮决策建议层，不是完整 LLM runner；失败或无 key 时降级保留 deterministic 行动。
  - 本刀聚焦 S1 真实模型决策第一刀，不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。
- **下一刀建议**：
  - 继续 S1/S2/S5：让 advisory 跨轮结算，形成长期关系图、势力资源和失败/误判后的后续策略。
  - 继续 S8/S9：提升长正文质量、正文内跳转阅读和更深层 Reviewer/局部重写。

### 2026-06-06 — S8/S9 Continuous Reading Chapter

- **做了什么**：
  - `author_chapter_draft` 在生成 `next_chapter_draft.json` / `next_chapter_draft.md` 与 `draft_revision_pack.json` 时，同步输出 `continuous_reading_chapter.json` / `continuous_reading_chapter.md`。
  - 连续阅读稿读取来源作者采纳记录、`next_chapter_brief.json`、具象代偿和 S8 `character_lens_volumes.json`，把世界正史卷、角色个人卷、事件多视角和草稿正文编排成 4 个以上阅读场景、阅读流、下一章钩子和卷宗证据。
  - `POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-draft` 继续返回同一草稿 report，新增 `continuous_reading_chapter` 与 artifacts 字段；缺少来源 lens run 时降级为 partial，不阻断草稿生成。
  - 作者采纳台草稿区新增“连续阅读稿”，展示来源沙盘、阅读流、分场正文、S8 卷宗引用和证据 refs，让 S8/S9 产物更像可连续阅读的章节而不是素材集合。
  - 同步 `memory.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-product-vision-correction-draft.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/codex-handoff.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：在 `test_author_chapter_draft_turns_adoption_brief_into_readable_chapter` 中先要求 `continuous_reading_chapter` 与 `continuous_reading_chapter.json/md`，测试因缺少 artifact 字段失败。
  - GREEN：`cd engine && python -m pytest tests/test_author_adoption.py -q` -> **8 passed**。
  - S8 focused：`cd engine && python -m pytest tests/test_character_lens_novel.py -q` -> **5 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **931 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 真实模型 smoke：临时项目执行 S8 lens -> S9 adopted -> `generate_author_chapter_draft(..., mock=False)`；真实 LLM 生成 1160 字正文，`continuous_reading_chapter.status=ready`，`scene_count=5`，绑定来源 lens run，未打印明文 key。
- **边界**：
  - 新 artifact、API 字段和 UI 均 additive；不改 `run_scene` 默认行为，不覆盖正史 `chapter.md` 或既有核心 artifact。
  - 连续阅读稿是第一版编排层，不等于长正文质量完全完成；真实文风控制、章节级长文规划、正文内跳转和更强语义 Reviewer 仍需继续深化。
  - 本刀聚焦 S8/S9 长正文与连续阅读第一刀，不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。

### 2026-06-06 — S7 World Autopilot Unattended Recovery

- **做了什么**：
  - `world_autopilot` service 补强无人值守自演：`objective_type` 支持 `causal_debt` 和 `awakening`，因果债爆发或角色 L5 觉醒会写入 `stop_condition` 并提前停止。
  - `autopilot_report.json` 新增 `status`、`stop_condition`、`recovery`、`failure`、醒来时间线、记忆变化列表和 checkpoint recovery，不再只给最终 summary。
  - 本地任务文件保存原始请求、进度、失败原因和最近可恢复检查点；中途失败时保留已写 checkpoint，调用 resume 会从最近 checkpoint 生成接续报告。
  - HTTP API 透传 `resume_from_run_id` / `resume_from_checkpoint`；检查点回放返回恢复提示。
  - 世界沙盘页新增因果债爆发/角色觉醒自演目标，昨夜世界演化报告展示进度刷新、暂停、恢复、停止证据、失败原因、醒来时间线和检查点回放；世界线档案任务卡展示失败与恢复检查点。
  - 同步 `memory.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md`。
- **测试/验证**：
  - RED：新增 S7 focused tests 后，先分别因 `causal_debt` 未真正停止、异常直接抛出且没有失败恢复任务而失败。
  - GREEN：`cd engine && python -m pytest tests/test_world_autopilot.py -q` -> **7 passed**。
- **边界**：
  - 新字段、API 参数和 UI 均 additive；不改 `run_scene` 默认行为，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 当前恢复是本地任务文件 + checkpoint 的第一版，不是跨进程后台队列或真实长时守护。
  - 本刀只收口 S7 世界自演产品化，不接 GraphRAG/Zep、provider spike、真实向量检索评测、OpenAPI、发行、计费或工程健康面板。

### 2026-06-06 — A/B/C World Sandbox Quality Deepening

- **做了什么**：
  - A：`world_sandbox` 的 LLM advisory 新增策略互动字段与 `strategy_board`，记录角色算计对象、策略、私有目的、筹码、误判、风险、预期世界影响和下一轮 hook。
  - A：策略互动写回角色行动、`subjective_memory.jsonl`、`information_flow` 的 `llm_strategy_probe` 和 `world_state_delta.strategy_game_effects`，世界沙盘 UI 展示“算计对象 / 策略 / 误判 / 结果”。
  - B：`continuous_reading_chapter.json` 升级为 v2，默认小说阅读、证据默认收起，并新增视角 tab、每场视角、认知偏差、冲突转折、证据开关、伏笔/回收线和章节悬念。
  - B：作者采纳台连续阅读稿展示默认阅读模式、证据状态、视角入口和每场认知偏差，仍保持正文先读、证据后查。
  - C：`draft_revision_pack.json` 升级为 v2，新增语义 Reviewer，按人物动机、冲突张力、世界代偿入文、视角清晰度和记忆消费给出审稿优先级。
  - C：局部改写建议新增原问题、修改意图、建议改写、影响角色、影响世界状态和采纳方向；作者采纳台展示语义审稿和采纳方向，反哺下一章草稿与确认入卷。
  - 同步 `memory.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-product-vision-correction-draft.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/codex-handoff.md`、`engine/README.md` 和本 changelog。
- **测试/验证**：
  - RED：新增 `test_llm_decision_advisory_builds_strategy_board_and_world_effects`，先因缺少 `strategy_interaction_count` 失败。
  - RED：新增 `test_continuous_reading_packet_tracks_viewpoints_bias_and_evidence_toggle`，先因缺少 `default_mode` 失败。
  - RED：新增 `test_revision_pack_contains_semantic_reviewer_and_adoption_direction`，先因缺少 `semantic_reviewer` 失败。
  - GREEN：`cd engine && python -m pytest tests/test_world_sandbox.py::test_llm_decision_advisory_builds_strategy_board_and_world_effects tests/test_world_sandbox.py::test_llm_decision_advisory_overlays_character_choices -q` -> **2 passed**。
  - GREEN：`cd engine && python -m pytest tests/test_author_adoption.py::test_continuous_reading_packet_tracks_viewpoints_bias_and_evidence_toggle tests/test_author_adoption.py::test_revision_pack_contains_semantic_reviewer_and_adoption_direction tests/test_author_adoption.py::test_author_chapter_draft_turns_adoption_brief_into_readable_chapter -q` -> **3 passed**。
  - Focused：`cd engine && python -m pytest tests/test_world_sandbox.py -q` -> **15 passed**。
  - Focused：`cd engine && python -m pytest tests/test_author_adoption.py -q` -> **10 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **936 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过，仅有 Windows 换行提示。
  - 真实 LLM smoke：临时项目显式启用 `llm_decision_mode=advisory` 与 `generate_author_chapter_draft(..., mock=False)`；advisory 返回 `ready` / `real_llm`，`strategy_interactions=2`；草稿由 LLM 生成 1202 字，连续阅读 v2 为 ready、5 场，语义 Reviewer ready，局部改写 3 条；未打印明文 key。
  - UI smoke：重启本地后端与 Vite，打开 `#/world/my-story/author`，执行“写入采纳台 -> 生成下一章草稿”；页面可见“连续阅读稿”“默认：小说阅读”“世界正史卷/角色个人卷/事件多视角”“语义审稿”“建议采纳后确认入卷”，控制台无 error。烟测后已停止 8765/5173 本地服务。
- **边界**：
  - 新字段、artifact 内容和 UI 展示均 additive；不改 `run_scene` 默认行为，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 默认 pytest 仍 mock-safe；真实 LLM smoke 只做小样本质量验收，不打印明文 key，不进入默认全量测试。
  - 本刀只做用户限定的真实 LLM 多 Agent 策略博弈、长正文/连续阅读、语义 Reviewer/局部重写；不接 GraphRAG/Zep、provider spike、检索评测、OpenAPI、发行、商业化或工程面板。

### 2026-06-06 — S5/S8/S9 Real E2E Smoke and Meme Readout

- **做了什么**：
  - 用本地真实模型 key 跑了一条小样本端到端世界线：生成并确认《天命书》 -> L5 干预沙盘 + `llm_decision_mode=advisory` -> 世界演化 -> S8 多视角正文 -> S9 作者采纳 -> 真实 LLM 下一章草稿 / 连续阅读稿 -> 作者确认入卷。
  - smoke 记录写入 `engine/.local-run/real-e2e-s5-s8-s9-20260606_021128/real_e2e_smoke_report.md` 和 `.json`，未打印明文 key。
  - 真实输出确认：S5 中赵轩 L5 觉醒，沈冰月与韩无归收到模因传播并分别采信/存疑；S8 生成世界正史卷、角色个人卷和事件多视角；S9 生成 1090 字真实 LLM 正文、连续阅读 v2、语义 Reviewer、3 条局部重写建议和确认入卷回写。
  - 首个暴露的问题：模因传播底层 artifact 具备 `belief_payload`、`belief_decision`、`credibility_score` 和 `reaction`，但对烟测/阅读报告不够直观，容易看成“传播状态有了但真相/采信/反应为空”。
  - 修复：新增 `meme_propagation_readout`，把传播记录归一成真相载荷、采信状态、采信标签、采信原因、可信度、反应类型、反应标签、反应说明和可读摘要；写入角色行动、主观记忆和 `world_state_delta.meme_contamination.propagation_readouts`。
  - 世界沙盘 UI 的角色行动卡、命痕回声和个人卷回读优先展示 readout，同时保留旧 `meme_propagation` 字段兼容。
  - 同步 `memory.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-product-vision-correction-draft.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/codex-handoff.md`、`engine/README.md` 和本 changelog。
- **测试/验证**：
  - RED：新增 `test_l5_meme_propagation_exposes_readable_truth_status_and_reaction`，先因缺少 `meme_propagation_readout` 失败。
  - GREEN：`cd engine && python -m pytest tests/test_world_sandbox.py::test_l5_meme_propagation_exposes_readable_truth_status_and_reaction -q` -> **1 passed**。
  - Focused：`cd engine && python -m pytest tests/test_world_sandbox.py -q` -> **16 passed**。
  - Focused：`cd engine && python -m pytest tests/test_world_sandbox.py::test_l5_meme_propagation_exposes_readable_truth_status_and_reaction tests/test_world_sandbox.py::test_l5_meme_truth_propagates_with_belief_reactions_in_subjective_memory tests/test_author_adoption.py::test_author_chapter_draft_turns_adoption_brief_into_readable_chapter -q` -> **3 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **937 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过，仅有 Windows 换行提示。
- **边界**：
  - 新字段 additive；不改 `run_scene` 默认行为，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 真实 smoke 只做小样本质量验收，不打印明文 key，不进入默认全量 pytest。
  - 本刀只修 S5/S8/S9 主线体验证据，不接 GraphRAG/Zep、provider spike、检索评测、OpenAPI、发行、商业化或工程面板。

### 2026-06-06 — Narrative Timeline / Scene Plan / Editorial Preview

- **做了什么**：
  - 针对真实 smoke 后仍偏结构占位的三个问题继续补强：世界演化像账本、S8/S9 仍有卷宗说明痕迹、Reviewer 只有建议清单。
  - `world_autopilot` 新增 `overnight_report.narrative_timeline`；每个 checkpoint 新增 `scene_beats` 与 `chapter_seed`，把自演结果整理成开场钩子、人物误判、代偿显形、冲突升级和下一章悬念。
  - `character_lens_volumes.json` 新增 `novel_scene_plan` 与 `reading_mode`，让 S8 多视角卷宗提供可被章节生成消费的故事节拍，证据默认收起。
  - `continuous_reading_chapter.json` 新增 `story_beat_source`，阅读 sections 优先消费 S8 `novel_scene_plan` 并记录 `source_beat_type`；缺少场景计划时才回退到草稿段落切片。
  - `draft_revision_pack.json` 新增 `editorial_revision_draft`，把语义 Reviewer 的局部建议合成为作者可预览、可手动采纳、不覆盖 `next_chapter_draft.md` / `confirmed_chapter.md` / `chapter.md` 的编辑应用稿。
  - 前端类型同步新增自演小说节拍、S8 scene plan、连续阅读来源和 Reviewer 编辑预览；世界沙盘页展示“小说节拍”，作者采纳台展示 S8 场景来源、source beat 和编辑应用预览。
  - 真实 smoke 首轮在 `engine/.local-run/real-narrative-optimization-smoke-20260606_031403/` 暴露自演 hook 有“赵轩先把赵轩”、双句号和模板拼接痕迹；随后补 focused 回归并修复动作片段清洗。
  - 真实 smoke 复测写入 `engine/.local-run/real-narrative-optimization-smoke-20260606_031833/`，S5 真实 LLM 觉醒传播、世界演化小说节拍、S8 场景计划、S9 真实草稿连续阅读和 Reviewer 预览均通过，未打印明文 key。
- **测试/验证**：
  - RED：新增 `test_world_autopilot_writes_novelistic_scene_beats_for_downstream_chapters`，先因缺少 `narrative_timeline` 失败。
  - RED：新增 `test_character_lens_outputs_scene_plan_for_novel_reading`，先因缺少 `novel_scene_plan` 失败。
  - RED：新增 `test_continuous_reading_consumes_s8_scene_plan_as_story_beats`，先因缺少 `story_beat_source` 失败。
  - RED：新增 `test_revision_pack_builds_editorial_preview_draft_without_overwriting_author_text`，先因缺少 `editorial_revision_draft` 失败。
  - RED：新增 `test_world_autopilot_scene_hook_removes_template_duplication`，先因 hook 中出现角色名重复失败。
  - GREEN：`cd engine && python -m pytest tests/test_world_autopilot.py -q` -> **9 passed**。
  - GREEN：`cd engine && python -m pytest tests/test_character_lens_novel.py -q` -> **6 passed**。
  - GREEN：`cd engine && python -m pytest tests/test_author_adoption.py -q` -> **12 passed**。
  - Focused combined：新增 narrative / S8 / S9 / Reviewer 4 条测试 -> **4 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **942 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过，仅有 Windows 换行提示。
  - 页面 smoke：本轮工具未暴露 in-app Browser；尝试本地 Vite HTTP smoke 时 dev server 未在检查窗口内接受连接，已停止尝试，最终以前端 production build 作为 UI 编译验证。
- **边界**：
  - 新字段和 UI 展示均 additive；保留旧 `timeline`、旧 continuous reading 字段和旧 revision 建议，不覆盖既有核心 artifact。
  - Reviewer 只生成编辑应用预览，仍由作者手动采纳和确认入卷；不自动覆盖正史。
  - 本刀继续服务世界沙盘主线，不接 GraphRAG/Zep、provider spike、检索评测、OpenAPI、发行、商业化或工程面板。

### 2026-06-06 — Dossier Reading Page Productization

- **做了什么**：
  - 新增 `dossier_reading` service 与 `GET /api/stories/<slug>/worldlines/<worldline_id>/dossier-reading`，只读聚合同一世界线最新 `continuous_reading_chapter`、确认稿、`confirmed_chapter_reading_trail`、S8 `character_lens_volumes` 和 `worldline_dossier`。
  - 前端新增 `DossierReadingPage` 与 `#/world/<slug>/worldlines/<worldline_id>/reading`，默认进入连续阅读正文态，不再把连续阅读继续堆在 Workspace 或 JSON 面板。
  - 页面可切换“连续阅读 / 世界正史卷 / 主锚点卷 / 角色个人卷 / 事件多视角 / 确认正文”，并显示每个视角的认知偏差。
  - 证据链默认折叠在正文之后，保留来源 artifact refs 和 `confirmed_chapter_reading_trail` 分区，服务“先读小说、再查证据”的阅读体验。
  - 顶栏与世界线页新增卷宗阅读入口；前端类型和 API client 同步新增 `DossierReadingReport`。
  - 同步 `memory.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-product-vision-correction-draft.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/codex-handoff.md`、`engine/README.md` 和本 changelog。
- **测试/验证**：
  - RED：新增 `test_dossier_reading_prefers_novel_mode_and_keeps_evidence_folded`，先因缺少 `living_novel_engine.service.dossier_reading` 失败。
  - GREEN：`cd D:\AI\open-infinite && python -m pytest engine/tests/test_dossier_reading.py -q` -> **2 passed**。
  - Focused：`python -m pytest engine/tests/test_dossier_reading.py engine/tests/test_worldline_dossier.py engine/tests/test_author_adoption.py::test_continuous_reading_packet_tracks_viewpoints_bias_and_evidence_toggle engine/tests/test_author_adoption.py::test_author_chapter_confirmation_links_back_to_cross_volume_evidence -q` -> **6 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **944 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过，仅有 Windows 换行提示。
  - HTTP smoke：在 `.local-run/dossier-page-smoke` 生成临时样本，启动 `lne browse` 与 Vite，`/dossier-reading` 返回 `ready`、默认 `continuous_reading`、四类卷宗齐全、证据默认折叠；Vite 新 hash route 返回 200。
- **边界**：
  - 本刀不新增持久 artifact，只读聚合既有 continuous reading、confirmed chapter、reading trail、多视角卷宗和 worldline dossier。
  - 不改变 `run_scene` 默认行为，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json` 或 `causal_diff.json`。
  - 浏览器插件未暴露本地页面截图工具，Playwright 也不在本地依赖中；本轮以 production build 和 HTTP route/API smoke 验证前端可达性。

### 2026-06-06 — World Autopilot Readable Entry

- **做了什么**：
  - 针对“世界自演结果页 -> 可读世界线入口”补闭环：`autopilot_report.json` 新增 additive `readable_entry`，把最近关键检查点、角色个人卷、事件多视角和连续阅读整理成“醒来从这里读”的入口包。
  - 新增 `GET /api/world-autopilot-runs/<run_id>/readable-entry`，可在页面刷新后只读复算同一入口；checkpoint replay API 同步返回 `readable_entry`，用户从检查点页也能继续进卷宗阅读。
  - 世界沙盘结果页新增醒来阅读入口区，展示四个阅读动作，并在同屏说明“为什么世界状态变了 / 谁记住了什么 / 哪条因果债在发酵”。
  - 世界线档案页新增连续阅读、角色个人卷、事件多视角直达按钮；卷宗阅读路由支持 `#/world/<slug>/worldlines/<worldline_id>/reading/<tab>`，原 `/reading` 默认行为保持兼容。
  - 同步前端类型、API client、结果页/检查点页/世界线页 UI 和 `memory.md`、世界沙盘 PRD、愿景纠偏、AI 对齐清单、路线图、`engine/README.md`、`docs/codex-handoff.md`。
- **测试/验证**：
  - RED：新增 `test_world_autopilot_report_exposes_wake_reading_entry`，先因缺少 `get_world_autopilot_readable_entry` 失败。
  - GREEN：`cd D:\AI\open-infinite && python -m pytest engine/tests/test_world_autopilot.py::test_world_autopilot_report_exposes_wake_reading_entry -q` -> **1 passed**。
  - Focused：`python -m pytest engine/tests/test_world_autopilot.py -q` -> **10 passed**。
  - Focused combined：`python -m pytest engine/tests/test_world_autopilot.py engine/tests/test_dossier_reading.py engine/tests/test_worldline_dossier.py -q` -> **14 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **945 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - UI smoke：临时启动 Vite，`http://127.0.0.1:5177/#/world/autopilot-http/worldlines/main/reading/character_volume` 返回 200 且包含 React root；随后已停止临时进程。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过，仅有 Windows 换行提示。
- **边界**：
  - 新字段和 API 均 additive；不新增独立持久 artifact，不改旧 `autopilot_report` 字段含义，不改 `run_scene` 默认行为。
  - 本刀不往 `WorkspacePage` 继续堆面板，只在世界沙盘结果页、世界线页、检查点页和卷宗阅读路由内组织入口。

### 2026-06-06 — Reviewer Rewrite Adoption Loop

- **做了什么**：
  - 针对“Reviewer 局部重写 -> 作者采纳台 -> 下一章草稿”补闭环：新增 `author_chapter_rewrite_application` service，读取 `draft_revision_pack.json` 的片段级建议，按作者选择生成 `accepted_local_rewrites.json` 与 `next_chapter_draft_revised.md`。
  - 新增 `POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-rewrites`，保持 identifier 安全校验与 400/404 降级。
  - `next_chapter_draft.json` additive 写入 `accepted_local_rewrites` 与 `chapter_text_with_accepted_rewrites`，保留原 `chapter_text` 和原 Markdown 草稿不变。
  - 作者采纳台新增勾选式局部重写卡片、采纳备注和“采纳选中改写到修订稿”动作；每条建议展示原问题、修改意图、建议改写、影响范围、采纳方向和证据 refs，采纳后自动把修订稿放回作者编辑区。
  - 确认入卷会读取已采纳局部重写，并把 artifact / rewrite ids 写入 `confirmed_chapter_entry.json`、`continuation_effect.next_sandbox_entry` 和 `worldline_state.confirmed_chapter_entry.accepted_rewrite_ids`。
  - 同步 UI types/API client、`memory.md`、世界沙盘 PRD、愿景纠偏、AI 对齐清单、路线图、`engine/README.md`、`docs/codex-handoff.md` 和本 changelog。
- **测试/验证**：
  - RED：新增 `test_author_can_apply_selected_rewrites_to_draft_and_confirmation_entry`，先因缺少 `living_novel_engine.service.author_chapter_rewrite_application` 失败。
  - GREEN：`cd D:\AI\open-infinite && python -m pytest engine/tests/test_author_adoption.py::test_author_can_apply_selected_rewrites_to_draft_and_confirmation_entry -q` -> **1 passed**。
  - Focused/API：`python -m pytest engine/tests/test_author_adoption.py -q` -> **13 passed**，覆盖 service、HTTP `/chapter-rewrites`、确认入卷和安全坏 id。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 完整后端：`cd engine && python -m pytest -q` -> **946 passed**。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过，仅有既有换行提示。
- **边界**：
  - 本刀只做 Reviewer 局部重写采纳链，不改 `run_scene` 默认行为，不覆盖 `chapter.md`、原 `next_chapter_draft.md`、确认稿或正史。
  - 采纳动作仍由作者显式选择；这不是自动编辑后定稿，也不新增 Graph/provider/检索评测/工程面板方向。

### 2026-06-06 — Documentation Governance Sweep

- **做了什么**：
  - 深度扫描入口文档、路线文档、归档目录、后置支撑清单和近期代码落地状态，确认 `dossier_reading`、`readable_entry`、`accepted_local_rewrites`、`agent_decision_advisory`、`continuous_reading_chapter`、`meme_propagation_readout` 等近期主线能力均已在 service/API/UI/types/tests 中存在。
  - 重写 `AGENTS.md`，把它从过期历史状态表收束为 Agent 入口规则：必读顺序、世界沙盘最高主线、闭环等级、硬约束、验证与文档治理。
  - 重写 `docs/index.md`，建立当前主线、当前事实、历史归档、支撑层 backlog、后置发行路径、研究资产的文档分层，并明确不要从 `completed/` 或 changelog 旧条目直接派生下一刀。
  - 压缩 `memory.md` 顶部超长状态摘要，新增“闭环等级”表和当前真实未做项前置：真实 LLM 多 Agent 策略、长正文/连续阅读、Reviewer 自动编辑后定稿、世界线阅读入口深化。
  - 同步 `README.md`、`docs/completed/README.md`、`docs/unfinale-world-sandbox-remodel-prd.md`、`docs/unfinale-product-vision-correction-draft.md`、`docs/unfinale-ai-development-alignment-checklist.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/living-novel-engine-prd.md`、`docs/productization-phase-map.md`、`docs/后续增强清单.md`、`docs/distribution-phase-plan.md`、`docs/codex-handoff.md` 和 `engine/README.md`，统一说明哪些是当前事实、哪些是支撑层、哪些只是历史或后置路径。
- **验证**：
  - 项目事实扫描：`rg` 确认近期世界沙盘产品化能力在代码、类型和测试中均有落地。
  - 过期口径扫描：入口文档已移除 929/944/945 等旧基线；changelog 和 legacy/completed 中保留旧基线作为历史记录。
  - `git diff --check` 通过，仅有 Windows 换行提示。
- **边界**：
  - 不移动或重写 `docs/completed/` 的历史专项正文，不篡改 `docs/project-changelog.md` 的旧验收记录；通过 `docs/index.md` 和 `completed/README.md` 做逻辑归类。
  - 不改代码、不改 artifact 契约、不改变 `run_scene` 默认行为。

### 2026-06-06 — Documentation Governance Second Pass

- **做了什么**：
  - 继续复扫根层和非归档文档，重点检查会把下一轮带回 Workspace、支撑层 backlog 或状态长表的残留入口。
  - 精简 `engine/README.md` 第一屏，把它重新定位为 API / artifact / 运行手册；当前事实和路线判断回指 `memory.md`、`docs/index.md` 和世界沙盘 PRD。
  - 给 `memory.md` 的阶段收口总览与当前产品/工程能力两节补跳读说明，明确这些长表用于确认历史能力，不用于派生当前下一刀。
  - 更新 `docs/image/README.md`，说明旧 UI 原型只能取信息架构，不应把“主工作台堆面板”当当前实现方向。
- **验证**：
  - 过期基线扫描无命中。
  - `git diff --check` 通过，仅有 Windows 换行提示。
- **边界**：
  - 本轮仍是 docs-only，不改代码、不移动历史归档、不改变 artifact/API 契约。

### 2026-06-06 — Reviewer Edited Final Chapter Loop

- **做了什么**：
  - 针对“Reviewer 局部重写 -> 作者采纳台 -> 下一章草稿”仍缺自动编辑后定稿的问题补闭环。
  - `author_chapter_rewrite_application` 在生成 `accepted_local_rewrites.json` / `next_chapter_draft_revised.md` 的同时新增 `edited_final_chapter.json` / `edited_final_chapter.md`，把作者勾选的片段级建议应用成可确认正文，而不是把审稿清单追加进正文。
  - `next_chapter_draft.json` additive 写入 `edited_final_chapter` 摘要和 artifact，保留原 `chapter_text`、原 Markdown 草稿、确认稿和正史不变。
  - `author_chapter_confirmation` 在作者没有传手动 `edited_chapter_text` 时自动读取 `edited_final_chapter.json`，并把 `edit_source=auto_reviewer_final`、已采纳改写 ids 和 `edited_final_chapter` artifact 写入 `confirmed_chapter_entry.json`、`continuation_effect.next_sandbox_entry` 和 worldline state。
  - 作者采纳台采纳局部重写后，正文编辑框优先显示编辑后定稿；确认时若用户未继续手改，前端让服务端自动消费定稿 artifact。
  - 同步 `memory.md`、`AGENTS.md`、世界沙盘 PRD、愿景纠偏、AI 对齐清单、路线图、`engine/README.md`、`docs/codex-handoff.md` 和本 changelog。
- **测试/验证**：
  - RED：新增 `test_author_rewrites_create_auto_edited_final_and_confirmation_uses_it`，先因缺少 `edited_final_chapter` 失败。
  - GREEN：`cd engine && python -m pytest tests/test_author_adoption.py::test_author_rewrites_create_auto_edited_final_and_confirmation_uses_it -q` -> **1 passed**。
  - Focused：`cd engine && python -m pytest tests/test_author_adoption.py -q` -> **14 passed**。
  - 完整后端：`cd engine && python -m pytest -q` -> **947 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
- **边界**：
  - 本刀仍要求作者显式勾选要采纳的局部重写；自动化只发生在“已采纳建议 -> 编辑后定稿 -> 未手改时确认入卷”之间。
  - 新 artifact 和 API 字段均 additive；不改 `run_scene` 默认行为，不覆盖 `chapter.md`、原 `next_chapter_draft.md`、确认稿或正史。
  - 这不是更强真实语义 Reviewer 或整章风格润色；后续质量深化仍需真实模型 smoke 观察。

### 2026-06-06 — Documentation Governance Full Triage

- **做了什么**：
  - 按用户要求复扫 `AGENTS.md`、`memory.md`、根 README、`docs/` 根层、`docs/completed/`、论文/品牌/原型资产、`engine/README.md` 和 `engine/ui/README.md`，确认文档物理目录不需要大搬迁；采用逻辑分层避免破坏历史链接。
  - `memory.md` 新增本轮文档治理收口，明确下一次开工读取顺序和“入口事实层 -> 当前主线层 -> 路线/阶段层 -> 历史归档层 -> 支撑层 backlog -> 研究/品牌/原型资产 -> 运行说明层”的归类口径。
  - `AGENTS.md` 增加统一文档状态标签：当前事实、当前主线、路线/阶段、历史归档、支撑层/后置、研究/资产，避免下一轮从旧专项或支撑层清单派生任务。
  - `docs/index.md` 明确本次不合并 `completed/` 历史专项的原因，并把“自动编辑后定稿”从未完成项中移除，改为“整章风格润色、真实语义 Reviewer 和真实模型编辑器”。
  - `docs/completed/README.md` 明确世界沙盘 S1-S9 当前主线暂不归入 completed；旧归档只作追溯，不承担下一刀来源。
  - `docs/productization-phase-map.md`、`docs/living-novel-engine-prd.md`、`docs/后续增强清单.md`、`docs/codex-handoff.md` 和根 README 同步最新第一版闭环状态。
  - `engine/ui/README.md` 从旧 v0.7 只读骨架重写为当前前端工作台说明，列出世界沙盘、世界线/检查点、卷宗阅读和作者采纳台等真实页面、路由和边界。
  - `docs/unfinale-world-sandbox-remodel-prd.md` 补充已落地的卷宗阅读路由，并标注角色个人卷/事件多视角第一版由 `DossierReadingPage` tab 承载。
- **验证**：
  - 文档/代码事实扫描：`rg --files docs`、`rg` 搜索近期 artifact/API/UI/test 关键词，确认当前 S7/S8/S9 与 Reviewer 链路确有落地。
  - 过期口径扫描：`rg "自动编辑后定稿|946 passed|第一刀不做|只读链路"`；命中只剩历史 changelog 或明确已完成/后续整章润色语境。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过，仅有 Windows 换行提示。
- **边界**：
  - 本轮 docs-only，不改产品代码、不移动 `docs/completed/` 文件、不改旧 changelog 历史事实、不改变 artifact/API 契约或 `run_scene` 默认行为。

### 2026-06-06 — Route And Handoff Documentation Slimming

- **做了什么**：
  - 继续沿文档治理目标处理第二层路线文档，防止新会话读完入口后又被历史长表带回支撑层。
  - 重写 `docs/living-novel-engine-iteration-plan.md`：从旧的阶段/支撑层长表改为当前路线判断，保留世界沙盘主线、已闭环等级、当前官方下一步、后置项、下一刀选择规则、验收命令和归档索引；历史长版继续指向 `docs/completed/living-novel-engine-iteration-plan-legacy-2026-06-01.md`。
  - 重写 `docs/codex-handoff.md`：从新窗口长接力表收束为最小接力包，去掉后续增强四十五刀和 Graph/provider/retrieval 的长表，保留当前事实速记、最近世界沙盘链路、真实未做项、执行纪律和验证命令。
  - 同步 `memory.md`，记录第二层路线/接力文档瘦身结果。
- **验证**：
  - 过期路线扫描：`rg "Graph Memory|Embedding|Retrieval|后续增强第|真实向量|provider spike|当前暂停|下一刀建议"` 在新路线图/接力包中只剩“已收口支撑层/不默认继续”的必要边界说明。
  - 过期基线扫描：入口文档无 `946 passed`、`945 passed`、`944 passed`、`929 passed` 或“自动编辑后定稿未做”残留。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过，仅有 Windows 换行提示。
- **边界**：
  - 本轮仍是 docs-only，不移动历史归档、不改旧 changelog 记录、不改变代码、artifact、API 或 `run_scene` 默认行为。

### 2026-06-06 — Support Layer Index Slimming

- **做了什么**：
  - 继续处理会把下一轮带回支撑层的文档入口，重写 `docs/后续增强清单.md`。
  - 将原逐刀长待办收束为“LNE 支撑层与后置增强索引”：只保留当前边界、已收口支撑能力分组、触发式增强规则、研究参考和追溯入口。
  - 同步 `memory.md` 与 `docs/index.md`，把“支撑层待办”统一改成“支撑层索引”，明确它不能作为默认下一刀来源；`memory.md` 的后续增强四十五刀逐条长表和支撑层 API/CLI 长清单也压缩为分组摘要，完整细节回指 changelog 和支撑层索引。
- **验证**：
  - 过期口径扫描：`rg` 检查入口文档中的旧基线、旧下一刀、Graph/provider/retrieval 误导口径和“待办”标签。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮仍是 docs-only，不移动历史归档、不改代码、不改变 artifact/API 契约或 `run_scene` 默认行为。

### 2026-06-06 — Frontend World Journey Shell Pass

- **做了什么**：
  - 将 `StoryEntryPage` 从历史版本入口改为“未终章 · 世界书架”，新增“确认天命 -> 运行沙盘 -> 阅读卷宗 -> 采纳续写”主旅程，并让故事卡默认进入天命书。
  - 将 `AppShell` 改为“未终章 / 世界沙盘”品牌与世界内卷宗导航，统一露出锚定、天命书、沙盘、阅读、世界线、多视角、作者台和机制档案，移除推荐榜占位。
  - 将 `WorkspacePage` 降级为“世界正史与机制档案”，保留旧正史、机制档案和支撑层入口，同时增加天命书、运行沙盘和卷宗阅读主动作。
  - 将 `WorldAnchorPage` 的下一步接到天命书；在 `WorldSandboxPage` 空态增加从事件到正文的世界回路导引。
  - 同步 `memory.md`、`engine/ui/README.md` 与 `docs/living-novel-engine-iteration-plan.md`，明确这是前端入口/导航第一轮改造，不代表完整愿景完成。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
  - 入口词扫描：确认用户可见入口不再残留“活体小说引擎”“推荐榜”“CLI 跑一次”“阅读工作台”等旧心智。
- **边界**：
  - 本轮不改后端、不删功能、不改变 API/artifact 契约、不改 `run_scene` 默认行为；支撑层仍保留在机制档案与设置入口。

### 2026-06-06 — Main PRD Current-State Rewrite

- **做了什么**：
  - 重写 `docs/living-novel-engine-prd.md`，把它从混有 v0.8/v0.9/v1.0、检索、Graph/provider 和商业化边界长历史的综合文档，收束为当前产品 PRD。
  - 新 PRD 只保留产品定位、用户价值、主体验、当前已闭环、真实未做项、明确后置项、非目标、验收口径和文档指路。
  - 同步 `memory.md` 与 `docs/index.md`，明确历史逐刀细节回指 `project-changelog.md`、`completed/README.md` 和支撑层索引。
- **验证**：
  - 入口层过期口径扫描：确认主 PRD 不再包含旧 Graph/provider 长端点清单、旧 v0.8/v0.9 待办段或旧下一刀建议。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮仍是 docs-only；不改变产品代码、artifact/API 契约、历史 changelog 事实或 `run_scene` 默认行为。

### 2026-06-06 — Product Vision Correction Slimming

- **做了什么**：
  - 重写 `docs/unfinale-product-vision-correction-draft.md`，把讨论期 2000 多行长记录收束为愿景与设计原则文档。
  - 保留原始愿望、双入口、一套底层、领域记忆模型、角色主观记忆链、《天命书》、干预、代偿、章节观察镜头、Reviewer、当前第一版成立体验、仍需深挖的深水区、UI 方向和不再默认扩张的支撑层。
  - 同步 `memory.md` 与 `docs/index.md`，明确讨论期 v1-v12 节奏和长 UI 描述不再作为当前执行路线。
- **验证**：
  - 入口层扫描：确认愿景纠偏稿不再包含旧 v1-v12 长接力、旧工程面板路线、Graph/provider 继续扩张或旧“下一刀”口径。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮仍是 docs-only；不改变产品代码、artifact/API 契约、历史 changelog 事实或 `run_scene` 默认行为。

### 2026-06-06 — Phase Map And Alignment Checklist Slimming

- **做了什么**：
  - 重写 `docs/productization-phase-map.md`，从阶段长表和支撑层历史摘要收束为技术 MVP、产品化 MVP、世界沙盘第一版、完整产品能力、当前深化方向和后置排期原则。
  - 重写 `docs/unfinale-ai-development-alignment-checklist.md`，从超长状态补充记录收束为开工前自检清单：是否服务世界运行、角色自主、主观记忆、干预后果、章节生成和小说阅读体验。
  - 同步 `memory.md`，记录这两个入口文档不再复制 S1-S9 长状态流水或支撑层逐刀历史。
- **验证**：
  - 非归档根层扫描：检查旧基线、旧下一刀、Graph/provider 扩张、后续增强逐刀历史和支撑层待办标签。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮仍是 docs-only；不改变产品代码、artifact/API 契约、历史 changelog 事实或 `run_scene` 默认行为。

### 2026-06-06 — World Sandbox PRD Current-State Rewrite

- **做了什么**：
  - 重写 `docs/unfinale-world-sandbox-remodel-prd.md`，把多日实现流水和长状态记录收束为当前 S1-S9 执行说明。
  - 新文档保留目标、硬边界、世界内部卷宗主导航、第一版闭环表、核心 artifact/API、前端页面、S1-S9 后续验收和完成标准。
  - 同步 `memory.md`，明确历史进展回指 changelog，当前执行以世界沙盘 PRD 的稳定结构为准。
- **验证**：
  - 非归档根层扫描：检查旧基线、旧下一刀、Graph/provider 扩张、后续增强逐刀历史和支撑层待办标签。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮仍是 docs-only；不改变产品代码、artifact/API 契约、历史 changelog 事实或 `run_scene` 默认行为。

### 2026-06-06 — Entry Terminology Cleanup

- **做了什么**：
  - 清理 `AGENTS.md`、`memory.md` 与 `engine/README.md` 中残留的具体 Graph/provider spike 标签，统一改为“重型 provider 试验”“Graph/长期记忆支撑层”或“mock 复核链”。
  - 目的不是改变历史事实，而是让下一次入口扫描不会把支撑层名称误读成当前下一刀。
- **验证**：
  - 根入口与 docs 非归档扫描：检查旧基线、旧下一刀、Graph/provider 扩张、后续增强逐刀历史和支撑层待办标签。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮仍是 docs-only；不改变产品代码、artifact/API 契约、历史 changelog 事实或 `run_scene` 默认行为。

### 2026-06-06 — Memory Current-State Audit

- **做了什么**：
  - 按用户要求深度扫描 `memory.md` 当前状态段、入口文档、路线文档、近期代码/API/UI/tests 和验证基线。
  - 确认卷宗阅读页、自演可读入口、Reviewer 局部重写、编辑后定稿、真实 LLM advisory、连续阅读稿等近期主线能力均有 service/API/UI/types/tests 证据。
  - 将 `memory.md` 中残留的 `World Sandbox Loop v1-v8` 与“当前正在进行的 S1-S9”旧表述收束为 `World Sandbox Loop S1-S9 第一版已收口，后续继续深化体验`。
- **验证**：
  - 后端：`cd engine && python -X utf8 -m pytest -q` -> **947 passed**。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮只做 `memory.md` 当前状态口径修正和 changelog 记录；不改产品代码、artifact/API 契约、历史旧条目或 `run_scene` 默认行为。

### 2026-06-06 — Frontend First-Run QA Polish

- **做了什么**：
  - 将前端浏览器标题从旧“阅读工作台”改为“未终章 · 世界书架”。
  - 修正 `TianmingPage` 对后端“天命书不存在”响应的判断：内置样例没有天命书时展示可生成空态，而不是错误页。
  - 收紧世界书架入口的移动端宽度约束，保证真实 390px 设备度量下标题、说明文案和四步旅程自然换行。
  - 同步 `memory.md`、`engine/ui/README.md` 与 `docs/living-novel-engine-iteration-plan.md`，记录这是首屏 QA 修正，不代表完整 UI 愿景完成。
- **验证**：
  - Chrome DevTools 设备度量截图：390px 移动端 `StoryEntryPage` 无水平溢出；桌面 `TianmingPage` 缺失天命书时展示“生成天命书草案”空态。
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不删路由、不改变 API/artifact 契约；只处理真实首屏使用和理解上的 QA 问题。

### 2026-06-06 — World Runway Guidance Layer

- **做了什么**：
  - 新增 `WorldRunway` 复用导览组件，用同一套古风纸面 UI 呈现“当前位置 / 三步理解路径 / 下一步行动”。
  - 接入 `DossierReadingPage`：导览从“读正文 -> 查卷宗 -> 写下一章”组织连续阅读、证据和作者采纳入口。
  - 接入 `WorldlineDossierPage`：导览从“看状态 -> 回放检查点 -> 进入阅读”组织世界线状态、检查点和继续沙盘入口。
  - 接入 `CheckpointReplayPage`：导览从“回看变化 -> 读后续 -> 写入下一章”把检查点接回阅读、沙盘和作者采纳。
  - 接入 `AuthorAdoptionPage`：导览从“比较差异 -> 采纳并改写 -> 确认入卷”解释作者工作流。
  - 同步 `memory.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是世界内导览层第一版。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Chrome DevTools 设备度量截图：桌面卷宗阅读、世界线档案、作者采纳台均出现 `WorldRunway`；390px 移动端卷宗阅读无水平溢出。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不删任何页面或路由、不改变 API/artifact 契约；只统一世界内理解路径和行动入口。

### 2026-06-06 — World Anchor Startup And Mobile Preservation

- **做了什么**：
  - `WorldAnchorPage` 左栏新增“世界启动”行动卡，把天命书、世界沙盘和卷宗阅读前置到锚定页首屏。
  - `worldAnchor.css` 将窄屏布局从隐藏左栏/右栏改为纵向排布，移动端继续保留视觉资产、基线与正史回放、实体别名、世界合约、角色卡和角色探针。
  - 同步 `memory.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是锚定页启动体验与移动端保功能切片。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Chrome DevTools 设备度量截图：桌面锚定页显示启动卡；390px 移动端 `documentElement.scrollWidth === innerWidth`，左栏/右栏 `display=block`，4 张角色卡仍在页面流中。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不删旧入口、不改变 API/artifact 契约；只提升锚定页启动路径和移动端功能保留。

### 2026-06-06 — World Sandbox Runway Guidance

- **做了什么**：
  - `WorldSandboxPage` 接入 `WorldRunway`，把“投放事件 -> 观察角色 -> 进入阅读”的路径前置到世界沙盘首屏。
  - 空态下主行动聚焦运行台、天命书和卷宗阅读；已有沙盘或自演结果时，主行动切到卷宗阅读、世界线档案和多视角卷。
  - 补充沙盘页移动端按钮栅格、内边距和滚动定位约束，避免首屏操作按钮把页面撑宽。
  - 同步 `memory.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是沙盘运行导览切片。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Chrome headless 截图：桌面沙盘首屏显示运行导览；390px 移动端沙盘页按钮栅格换行，沙盘页本体无水平溢出。
  - HTTP smoke：`http://localhost:5174/#/world/my-story/sandbox` 返回 200 并加载前端 root。
- **边界**：
  - 本轮不改后端、不删旧入口、不改变 API/artifact 契约；只提升沙盘页的理解路径、下一步行动和移动端可用性。

### 2026-06-06 — Mobile World Navigation Tray

- **做了什么**：
  - `appShell.css` 将窄屏下的世界内部顶栏导航从横向滚动改成可换行卷宗盘。
  - 保留锚定、天命书、沙盘、阅读、世界线、多视角、作者台和机制档案 8 个入口，并保留动效与设置按钮。
  - 桌面顶栏仍保持原一行布局；移动端只调整排列和密度，不改变路由或功能。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Chrome 精确 390px 设备模拟：`documentElement.scrollWidth === innerWidth`，`world-nav` 内容不溢出，8 个导航按钮文字不截断。
  - Chrome headless 桌面截图：1366px 顶栏保持一行世界卷宗导航。
  - HTTP smoke：`http://localhost:5174/#/world/my-story/sandbox` 返回 200 并加载前端 root。
- **边界**：
  - 本轮不改后端、不删入口、不改变 API/artifact 契约；只修正跨页面移动端导航可见性和可用性。

### 2026-06-06 — Dossier Reading Cover Card

- **做了什么**：
  - `DossierReadingPage` 的正文卡顶部新增“当前阅读卷”题签，按当前 tab 展示标题、阅读理由/偏差、场景数、证据数和下一章钩子。
  - 题签新增世界线、继续沙盘和作者台行动入口；`WorldRunway` 的“读正文”步骤会滚动到正文卡。
  - 移动端将正文卡排在卷宗目录前，让用户先读正文，再查目录、认知偏差和证据链。
  - 同步 `memory.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是阅读体验切片。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Chrome 桌面截图：卷宗阅读页显示卷首题签、三枚行动按钮和阅读统计。
  - Chrome 精确 390px 设备模拟：`documentElement.scrollWidth === innerWidth`，正文卡存在，行动按钮不截断，正文卡排在卷宗目录前。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不删 tab、不改变 API/artifact 契约；只提升卷宗阅读页的阅读上下文、下一步行动和移动端阅读顺序。

### 2026-06-06 — Author Adoption Workflow Command Center

- **做了什么**：
  - `AuthorAdoptionPage` 首屏新增“当前下一步”工作流中枢，把对照、入账、修订、入卷四步状态和主行动前置。
  - 顶部按钮直接复用现有写入采纳台、生成草稿、采纳局部改写、确认入卷和回世界沙盘动作；原有表单、三栏对照、Reviewer、连续阅读、编辑后定稿和确认入卷展示全部保留。
  - 移动端把主按钮排在步骤卡片前，确保作者能在首屏内先执行下一步，再查看完整流程。
  - 同步 `memory.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是作者采纳台体验切片。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Chrome 精确 390px 设备模拟：作者采纳台无水平溢出，主操作按钮在首屏内，四步状态卡存在。
  - UI smoke：启动本地后端与 Vite，打开 `#/world/my-story/author`，执行“写入采纳台 -> 生成下一章草稿”；页面依次切到“生成下一章草稿”和“先采纳选中改写”，无页面错误。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不删旧入口、不改变路由/API/artifact 契约；只提升作者采纳台的首屏理解、下一步行动和移动端可用性。

### 2026-06-06 — Tianming Constitution Command Cover

- **做了什么**：
  - `TianmingPage` 首屏新增“当前下一步”宪法封面，把生成草案、确认根天命、干预预编译和进入沙盘四步前置。
  - 封面摘要展示天命书状态、当前锚点、合约压力、叙事吸引子数量、多锚点数量和风险说明，让用户先理解“天命书是世界宪法”。
  - 顶部动作直接复用现有生成草案、确认天命、跳转世界沙盘和滚动到干预预编译模块；原有吸引子、锚点、压力、候选承载者、干预边界、干预预编译和世界线代偿全部保留。
  - 同步 `memory.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是天命书入口理解切片。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Chrome 精确 390px 设备模拟：天命书页无水平溢出，主操作按钮在首屏内，四步状态卡存在。
  - UI smoke：启动本地后端与 Vite，打开 `#/world/my-story/tianming`，执行“生成草案 -> 确认天命”；页面依次切到“确认这卷天命”和“进入世界沙盘”，无页面错误。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不删旧入口、不改变路由/API/artifact 契约；只提升天命书页的首屏理解、下一步行动和移动端可用性。

### 2026-06-06 — Character Lens Workflow Command Center

- **做了什么**：
  - `CharacterLensPage` 首屏新增“当前下一步”工作流中枢，把选择观察点、生成五类卷宗、阅读信息差和送入作者台四步前置。
  - 空态主行动直接生成多视角；生成后主行动切到卷宗阅读，并保留作者采纳台和世界沙盘出口。
  - 中枢摘要展示 lens run、artifact、brief 数、正文卷数、角色立场数和来源事件；原有事件材料表单、brief、世界正史卷、主锚点卷、角色卷、势力卷和事件多视角展示全部保留。
  - 同步 `memory.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是多视角页体验切片。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Chrome 桌面与精确 390px 设备模拟：多视角页无水平溢出，移动端主操作按钮在首屏内，四步状态卡存在。
  - UI smoke：启动本地后端与 Vite，打开 `#/world/my-story/lens`，执行“生成多视角”；页面切到“进入卷宗阅读”，并显示卷宗阅读、作者采纳台和世界沙盘出口，无页面错误。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不删旧入口、不改变路由/API/artifact 契约；只提升多视角页的首屏理解、下一步行动和移动端可用性。

### 2026-06-06 — Worldline Dossier Workflow Command Center

- **做了什么**：
  - `WorldlineDossierPage` 首屏新增“当前下一步”工作流中枢，把确认分支状态、查看代偿、回放最近变化和进入连续正文四步前置。
  - 无检查点时主行动是继续沙盘；有检查点时主行动会切到回放最近检查点，同时保留卷宗阅读、多视角和沙盘出口。
  - 中枢摘要展示世界线状态、中文因果债等级、检查点数、自演任务数、代偿域数量和来源承接材料；原有分支状态、下一轮行动、具象代偿账、自演任务、检查点和最近世界推进模块全部保留。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是世界线档案体验切片。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Chrome 桌面：1366px 页面无水平溢出，世界线中枢位于首屏上方。
  - Chrome 精确 390px 设备模拟：世界线页无水平溢出，主操作按钮在首屏内，按钮顺序为继续沙盘、卷宗阅读、多视角，因果债等级显示中文。
  - UI smoke：打开 `#/world/my-story/worldlines/main`，点击中枢里的“卷宗阅读”，页面进入 `#/world/my-story/worldlines/main/reading`，无页面错误。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不删旧入口、不改变路由/API/artifact 契约；只提升世界线档案页的首屏理解、下一步行动和移动端可用性。

### 2026-06-06 — Checkpoint Replay Wake Command Center

- **做了什么**：
  - `CheckpointReplayPage` 首屏新增“醒来回放”工作流中枢，把确认大事件、查看角色记忆、承接因果代偿和进入连续正文四步前置。
  - 主行动直接复用 `readable_entry.primary_actions` 进入连续阅读；同时保留返回世界线、继续沙盘和作者采纳台出口。
  - 中枢摘要展示本轮编号、角色记忆数、后续可能数、世界阶段、世界线和因果债；原有状态变化解释、记忆变化、具象代偿、后续可写方向、`WorldRunway` 和详细回放模块全部保留。
  - 移动端压紧同类世界线命令中枢的操作按钮间距，并让长 badge 自动换行，避免检查点阶段文本撑宽页面。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是检查点回放体验切片。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Chrome 桌面：1366px 检查点页无水平溢出，醒来回放中枢位于首屏上方，主行动为“继续下一段正文”。
  - Chrome 精确 390px 设备模拟：检查点页无水平溢出，四枚操作按钮全部在首屏内。
  - UI smoke：打开 `#/world/my-story/worldlines/main/checkpoints/autopilot_20260606_210329_1a8810/checkpoint_001`，点击“继续下一段正文”，页面进入 `#/world/my-story/worldlines/main/reading/continuous_reading`，无页面错误。
- **边界**：
  - 本轮不改后端、不删旧入口、不改变路由/API/artifact 契约；只提升检查点回放页的首屏理解、下一步行动和移动端可用性。

### 2026-06-06 — Workspace Archive Command Center

- **做了什么**：
  - `WorkspacePage` 的“世界正史与机制档案”首屏新增档案工作流中枢，把定界、运行、阅读和追溯四步前置。
  - 中枢主动作直接进入天命书、世界沙盘、卷宗阅读；有旧分支时保留查看旧分支，暂无旧分支时显示禁用态。
  - 顶部指标从旧的支撑层计数改为“可读章节、运行记录、记忆/正史、需留意”，并补充每项含义，降低用户误把机制档案当主线工作区的成本。
  - 原有导入检查、运行前体检、向量检索、Graph 支撑层、创作闭环、设定、角色卡、项目审计、章节片段和 artifact 网格全部保留。
  - 同步 `memory.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是机制档案体验切片。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - Chrome 桌面：1366px 机制档案页无水平溢出，档案中枢位于首屏上方，四个动作可见。
  - Chrome 精确 390px 设备模拟：机制档案页无水平溢出，天命书和运行沙盘主动作在首屏内。
  - UI smoke：打开 `#/workspace/my-story`，点击“天命书”“运行沙盘”“卷宗阅读”，分别进入 `#/world/my-story/tianming`、`#/world/my-story/sandbox` 和 `#/world/my-story/worldlines/main/reading`。
- **边界**：
  - 本轮不改后端、不新增支撑层面板、不改变路由/API/artifact 契约；只提升旧机制档案入口的首屏理解、下一步行动和移动端可用性。

### 2026-06-06 — Import And Genesis Intake Command Centers

- **做了什么**：
  - `ImportNovelPage` 首屏新增“开卷前台”，把命名世界、放入正文、抽取世界和进入锚定四步前置。
  - 导入页新增首屏主动作：导入并锚定、选择文件、填写章节；原有文件上传、可恢复分片、章节粘贴、mock/真实模型、允许覆盖、错误提示和 job polling 全部保留。
  - `GenesisPage` 首屏新增“无稿创世台”，把命名世界、写下冲突、补足手感和进入锚定四步前置。
  - 创世页新增首屏主动作：创世并锚定、填写主题、返回书架；原有主题创世、主角/文风提示、mock/真实模型、允许覆盖、错误提示和 job polling 全部保留。
  - 移动端只调整展示顺序：先给出主动作，再展示完整流程卡，避免用户在入口页先读完所有状态卡才能操作。
  - 同步 `memory.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是导入/创世入口体验切片。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 后端：`cd engine && python -m pytest -q` -> `947 passed`。
  - Chrome 桌面与精确 390px 设备模拟：导入页和创世页无水平溢出，开卷中枢存在，空表单主按钮保持禁用。
  - Chrome 精确 390px 设备模拟复查：移动端主动作位于流程卡之前，`scrollWidth === clientWidth`。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不删旧入口、不改变路由/API/artifact 契约；只提升导入小说页与主题创世页的首屏理解、下一步行动和移动端可用性。

### 2026-06-06 — Dossier Reading Evidence Anchors

- **做了什么**：
  - `DossierReadingPage` 连续阅读态改为按 `continuous_reading.reading_sections` 分场景渲染正文，每一场展示场景标题、视角/叙事角色、认知偏差和冲突转折。
  - 侧栏新增“阅读进度”书签和进度条，点击场景可跳转并高亮当前正文段落。
  - 正文场景内新增证据锚点，直接展示该场对应的 `evidence_refs` / `evidence_mode.refs`，不再只把证据集中在底部折叠区。
  - 连续阅读态新增关联卷宗卡片，前置展示跨卷宗引用的标题、摘要和证据数量；原有卷宗 tab、认知偏差列表、底部证据面板、世界线/沙盘/作者台动作全部保留。
  - 修复 `0 && <...>` 条件渲染导致“0 条证据”在正文里显示成裸 `0` 的阅读瑕疵。
  - 同步 `memory.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是卷宗阅读正文证据锚点切片。
- **验证**：
  - 前端：`cd engine/ui && pnpm run build` 通过。
  - 后端：`cd engine && python -m pytest -q` -> `947 passed`。
  - Chrome 桌面与精确 390px 设备模拟：`#/world/my-story/worldlines/main/reading` 无水平溢出，5 个阅读场景、4 个段内证据锚点和阅读进度书签均可见。
  - UI smoke：点击第二个阅读书签后，侧栏 active 项和正文高亮均切到“二、各怀半句真话”；裸 `0` 不再出现。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不改变 API/artifact 契约、不删旧卷宗 tab 或底部证据面板；只提升卷宗阅读页的正文内证据、阅读进度和移动端可用性。

### 2026-06-06 — Dossier Reading Misbelief Map

- **做了什么**：
  - `DossierReadingPage` 将原静态认知偏差列表升级为“误会图谱”，按 `perspective_biases` 展示来源、卷宗/场景标签、误会说明和证据数量。
  - 误会节点现在可点击：正文场景节点会定位并高亮对应阅读段落，卷宗节点保留切换到对应 tab 的能力。
  - 章节定位从贴顶滚动改为阅读中心优先；用户主动点击误会节点或阅读书签时会短暂锁定目标，避免移动端被相邻段落抢走当前高亮。
  - 保留原有连续阅读正文、卷宗 tab、确认正文、底部证据面板、世界线/沙盘/作者台动作和所有路由。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把误会图谱第一版从待办改为当前事实。
- **验证**：
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过。
  - 后端：`cd engine && python -m pytest -q` -> `947 passed`。
  - Chrome 桌面与精确 390px 设备模拟：`#/world/my-story/worldlines/main/reading` 显示 5 条误会节点，无水平溢出。
  - UI smoke：点击第二条误会节点后正文高亮切到“二、各怀半句真话”；点击第一条后回到“一、雨声入局”；桌面和移动端均通过。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不改变 API/artifact 契约、不新增持久 artifact；只提升卷宗阅读页的误会理解、点击定位和移动端阅读稳定性。

### 2026-06-06 — World Anchor Dossier Gateway

- **做了什么**：
  - `WorldAnchorPage` 新增“世界卷宗总览”，把天命书、世界沙盘、卷宗阅读、世界线、多视角和作者台组织成“定界 -> 运行 -> 阅读 -> 采纳”的世界内地图。
  - 每个入口展示用途说明、当前读数和可点击动作，并复用现有路由；总览头部保留“机制档案”出口。
  - 桌面端在中栏显示完整卷宗地图；移动端在“世界启动”卡后显示紧凑总览，避免用户先被视觉资产和旧机制信息淹没。
  - 原有“世界启动”行动卡、编辑锚定、视觉资产、基线回放、实体别名、世界合约、角色卡和角色探针全部保留。
  - 同步 `memory.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录这是世界内部卷宗壳的第一步。
- **验证**：
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过。
  - 后端：`cd engine && python -m pytest -q` -> `947 passed`。
  - Chrome 桌面与精确 390px 设备模拟：`#/anchor/my-story` 仅显示一套可见总览，6 个入口齐全，无水平溢出；移动端总览起点位于首屏内。
  - UI smoke：点击“卷宗阅读”进入 `#/world/my-story/worldlines/main/reading`；点击“机制档案”进入 `#/workspace/my-story`。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改后端、不新增路由、不改变 API/artifact 契约；只提升世界锚定页的理解路径和跨页面入口组织。

### 2026-06-06 — Character Volume Dossier Page

- **做了什么**：
  - 新增 `CharacterVolumePage` 与 `#/world/<slug>/worldlines/<worldline_id>/characters/<character_id>` 路由，作为世界内部“角色个人卷”独立页面。
  - 页面复用既有 `dossier-reading` 与 `subjective-memory` API，展示单个角色的个人卷正文、主观记忆链、误会、未知正史、秘密可见性、卷内证据和去沙盘/多视角/作者台动作。
  - 没有 `character_lens_volumes` 正文时，会用主观记忆兜底生成当前角色索引，并显示明确空态，不让用户误以为角色资料不存在。
  - 锚定页角色卡、卷宗阅读角色卷、多视角角色卷和沙盘角色行动卡都新增进入角色个人卷的入口；原有查看个人记忆、卷宗 tab、生成多视角和作者采纳动作全部保留。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，记录角色个人卷独立页第一版已收口。
- **验证**：
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过。
  - Chrome 桌面：`#/world/my-story/worldlines/main/characters/zhao_xuan` 显示“赵轩”、角色个人卷、主观记忆链和 5 条记忆，无水平溢出，顶栏激活“角色卷”。
  - Chrome 精确 390px 设备模拟：角色卷页无水平溢出，角色名、主动作、导览和主观记忆链可见。
  - UI smoke：`#/anchor/my-story` 的角色卡“角色个人卷”按钮能进入 `#/world/my-story/worldlines/main/characters/zhao_xuan`。
- **边界**：
  - 本轮不改后端、不新增持久 artifact、不改变 API/artifact 契约；只把已有角色卷与主观记忆能力组织成可理解、可进入的产品页面。

### 2026-06-06 — Faction Volume Dossier Page

- **做了什么**：
  - `character_lens_volumes.json` 新增 additive `faction_volume` 正文卷，使用同一份沙盘轮次、主观记忆、世界状态 delta 和 `consequence_state` 证据链，不改变既有四类卷宗字段。
  - `dossier-reading` 聚合新增势力卷 tab、中文标签和认知偏差说明，卷宗阅读页可切到“势力卷”并进入独立势力卷页面。
  - 新增 `FactionVolumePage` 与 `#/world/<slug>/worldlines/<worldline_id>/factions/<faction_id>` 路由，聚合世界锚定、卷宗阅读和 `worldline_state`，展示势力卷正文、势力目录、因果压力域、最近 ledger、卷内证据和去沙盘/多视角/作者台动作。
  - 世界锚定页的势力标签、多视角页的势力卷正文/brief、卷宗阅读页的势力卷和顶栏导航都能进入势力卷；无正文时显示明确空态。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把势力卷独立页第一版从待办改为当前事实。
- **验证**：
  - Focused 后端：`python -m pytest -q engine\tests\test_character_lens_novel.py engine\tests\test_dossier_reading.py` -> `8 passed`。
  - 后端全量：`cd engine && python -m pytest -q` -> `947 passed`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过。
  - Chrome 桌面与精确 390px 设备模拟：`#/world/my-story/worldlines/main/factions/苍澜派` 显示势力卷标题、势力目录、阅读正文区域、势力代偿面板和 `WorldRunway`，无水平溢出。
  - UI smoke：`#/anchor/my-story` 的势力标签可进入 `#/world/my-story/worldlines/main/factions/苍澜派`。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改 `run_scene` 默认行为，不新增持久 artifact 类型，不破坏既有 API/artifact 契约；只把势力卷从已有多视角能力补成可读、可进入、可理解的产品页面。

### 2026-06-07 — Event Perspective Dossier Page

- **做了什么**：
  - 新增只读 `event_perspective` service 与 `GET /api/stories/<slug>/worldlines/<worldline_id>/events/<event_id>/perspectives`，复用 `dossier-reading`、`character_lens_volumes`、`novel_scene_plan`、信息差和证据链，不新增持久 artifact。
  - `dossier-reading` 的 volume tab additive 透传 `evidence_chain`、`information_gap` 和 `novel_scene_plan`，让事件页能追到源沙盘 run、场景节拍和证据。
  - 新增 `EventPerspectivePage` 与 `#/world/<slug>/worldlines/<worldline_id>/events/<event_id>/perspectives` 路由，把同一事件组织成事件节拍、当前片段、事件多视角正文、信息差、误读列表、证据链和去卷宗阅读/角色卷/世界线/作者台动作。
  - 卷宗阅读页的事件多视角 tab 和多视角生成页的事件正文卡都能进入事件详情页；顶栏会显示“事件卷”。
  - 前端入口补充空 data favicon，消除本地浏览器默认请求 `/favicon.ico` 的 404 控制台噪声。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把事件详情页从基础待办改为当前事实。
- **验证**：
  - Red/green focused 后端：先跑 `python -m pytest -q engine\tests\test_event_perspective.py`，确认缺 `event_perspective` 模块失败；实现后同命令通过。
  - 相邻链路：`python -m pytest -q engine\tests\test_character_lens_novel.py engine\tests\test_dossier_reading.py engine\tests\test_event_perspective.py` -> `10 passed`。
  - 后端全量：`cd engine && python -m pytest -q` -> `949 passed`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过。
  - Chrome 桌面与精确 390px 设备模拟：`#/world/my-story/worldlines/main/events/main/perspectives` 显示事件节拍、信息差、下一步、事件多视角正文和证据链，无水平溢出、无 console error、无 4xx。
  - UI smoke：从 `#/world/my-story/worldlines/main/reading/event_multi_perspective` 点击“事件详情”可进入 `#/world/my-story/worldlines/main/events/main/perspectives`。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改 `run_scene` 默认行为，不新增持久 artifact，不破坏既有 API/artifact 契约；只把已有事件多视角从 tab 补成可读、可进入、可理解的产品页面。

### 2026-06-07 — Longline Reading Dossier Page

- **做了什么**：
  - 新增只读 `longline_reading` service 与 `GET /api/stories/<slug>/worldlines/<worldline_id>/longline-reading`，复用 `dossier-reading`、`worldline_dossier`、连续阅读场景、多视角卷宗、确认入卷、事件信息差和证据链，不新增持久 artifact。
  - 新增 `LonglineReadingPage` 与 `#/world/<slug>/worldlines/<worldline_id>/longline` 路由，把同一世界线组织成长线时间线、当前长线节点、误会/角色记忆/势力压力/事件裂缝/作者承接五条发酵线、证据链和下一步动作。
  - 顶栏新增“长线卷”；世界线页、卷宗阅读页和事件详情页都能进入长线卷，事件详情页的下一步也会返回长线阅读。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把跨事件长线卷从待办改为当前事实，并把后续重点收束到多事件索引、跨章误会回收、长线阅读进度和长正文节奏。
- **验证**：
  - Red/green focused 后端：先跑 `python -m pytest -q engine\tests\test_longline_reading.py`，确认缺 `longline_reading` 模块失败；实现后同命令 -> `2 passed`。
  - 相邻链路：`python -m pytest -q engine\tests\test_longline_reading.py engine\tests\test_event_perspective.py engine\tests\test_dossier_reading.py` -> `6 passed`。
  - 后端全量：`cd engine && python -m pytest -q` -> `951 passed`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome 桌面与精确 390px 设备模拟：`#/world/my-story/worldlines/main/longline` 显示长线时间线、当前节点、发酵线、下一步和证据链，无水平溢出、无 console error、无 4xx；点击第二个时间线节点能切换当前节点。
  - UI smoke：从 `#/world/my-story/worldlines/main/events/main/perspectives` 点击“长线卷”可进入 `#/world/my-story/worldlines/main/longline`。
- **边界**：
  - 本轮不改 `run_scene` 默认行为，不新增持久 artifact，不破坏既有 API/artifact 契约；只把已有世界线材料组织成用户能读懂、能跳转、能继续推进的跨事件长线卷。

### 2026-06-07 — Longline Progress And Event Index

- **做了什么**：
  - `longline_reading` 只读聚合包新增 additive `reading_progress`、`event_index` 和 `open_threads`，不新增持久 artifact。
  - `LonglineReadingPage` 首屏新增“长线阅读进度、按事件追长线、未解线索”三块纸面面板，让用户先看自己读到哪、有哪些事件、哪些线仍需追踪。
  - 多事件索引按钮可定位对应长线节点；未解线索可跳回卷宗阅读、角色卷、势力卷、事件详情或作者台，保留原有长线时间线、五条发酵线、证据链和下一步动作。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把长线阅读进度与多事件索引从待办改为当前事实。
- **验证**：
  - Red/green focused 后端：先补 `engine\tests\test_longline_reading.py` 断言新字段，确认缺 `reading_progress` 失败；实现后同命令 -> `2 passed`。
  - 相邻链路：`python -m pytest -q engine\tests\test_longline_reading.py engine\tests\test_event_perspective.py engine\tests\test_dossier_reading.py` -> `6 passed`。
  - 后端全量：`cd engine && python -m pytest -q` -> `951 passed`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome 桌面与精确 390px 设备模拟：`#/world/my-story/worldlines/main/longline` 显示长线阅读进度、按事件追长线、未解线索、长线时间线和正在发酵的线，无水平溢出；点击第二个事件索引可切换当前长线节点，点击未解线索可跳回世界内页面。
- **边界**：
  - 本轮不改 `run_scene` 默认行为，不新增持久 artifact，不破坏既有 API/artifact 契约；只把已有长线材料补成更易理解、更可操作的阅读状态和事件索引。

### 2026-06-07 — Longline Misbelief Recovery Desk

- **做了什么**：
  - `longline_reading` 只读聚合包新增 additive `misbelief_recovery`，从已有 `perspective_biases` 整理误会来源事件、牵动角色、证据数量、三步回收路径和去卷宗/作者台动作。
  - `LonglineReadingPage` 首屏新增“误会回收台 / 把误会写回下一章”纸面面板，让用户能先核对误会来源，再把它送到作者采纳台承接下一章。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把长线卷误会回收台从待办改为当前事实，同时保留“更深跨章误会网络/跨章节回收”作为后续。
- **验证**：
  - Red/green focused 后端：先补 `engine\tests\test_longline_reading.py` 断言新字段，确认缺 `misbelief_recovery` 失败；实现后同命令 -> `2 passed`。
  - 相邻链路：`python -m pytest -q engine\tests\test_longline_reading.py engine\tests\test_event_perspective.py engine\tests\test_dossier_reading.py` -> `6 passed`。
  - 后端全量：`cd engine && python -m pytest -q` -> `951 passed`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome 桌面与精确 390px 设备模拟：`#/world/my-story/worldlines/main/longline` 显示误会回收台、回卷宗核对、送到作者台、长线阅读进度和按事件追长线，无水平溢出；点击第二个事件索引可切换当前长线节点，点击“回卷宗核对”进入 `#/world/my-story/worldlines/main/reading`。
  - Diff：`cd D:\AI\open-infinite && git diff --check` 通过。
- **边界**：
  - 本轮不改 `run_scene` 默认行为，不新增持久 artifact，不破坏既有 API/artifact 契约；只把已有误会材料补成用户能理解、能核对、能继续写下一章的回收台。

### 2026-06-07 — Local Recent Reading Resume

- **做了什么**：
  - 前端新增 `readingProgress` helper 与 `check:reading-progress` 轻量检查脚本，识别卷宗阅读、长线卷、角色卷、势力卷、事件卷和检查点回放等阅读类路由，并写入浏览器本机 `localStorage`。
  - `App` 在阅读类路由变化时自动记录最近阅读位置；`WorldAnchorPage` 的“世界启动”区在有记录时显示“从上次读到的地方继续”续读卡和“继续阅读”主动作。
  - 保留原有天命书、世界沙盘、卷宗阅读、世界卷宗总览、视觉资产、基线回放、角色卡、编辑锚定和所有路由入口；没有本机记录时锚定页保持原启动文案。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把“本机最近阅读续航”记为当前事实，同时把跨设备/账号级阅读进度继续保留为后续。
- **验证**：
  - Red/green helper：先跑 `tsc ... src\readingProgress.ts && node scripts\check-reading-progress.mjs`，确认缺 helper 失败；实现后 `pnpm.cmd run check:reading-progress` -> `reading progress helper ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome 桌面与精确 390px 设备模拟：先访问 `#/world/my-story/worldlines/main/longline`，确认 `localStorage.unfinale.recentReading.v1` 写入“继续读长线卷”；再访问 `#/anchor/my-story`，显示“从上次读到的地方继续 / 继续读长线卷 / 继续阅读”，无水平溢出，点击“继续阅读”回到长线卷。
- **边界**：
  - 本轮不改后端、不新增 API 或持久 artifact，不做账号/跨设备同步；只把本地产品体验补成回来后不迷路的第一版续读能力。

### 2026-06-07 — World Anchor Journey Status

- **做了什么**：
  - 前端新增 `worldJourney` helper 与 `check:world-journey` 轻量检查脚本，按沙盘运行次数、角色数、伏笔数、章节号和本机最近阅读记录推导世界锚定页的当前旅程状态。
  - `WorldAnchorPage` 的世界卷宗总览新增“当前旅程”纸面面板，把天命书、世界沙盘、卷宗阅读和作者台标成“下一步 / 可用 / 待生成”，并提供“确认天命 / 进入卷宗阅读 / 继续阅读”等推荐主动作。
  - 保留原有世界启动卡、最近阅读续航、世界卷宗总览、视觉资产、基线回放、角色卡、编辑锚定和全部现有路由；该刀不新增后端 API，不改 artifact。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把“世界锚定页旅程状态”记为当前事实。
- **验证**：
  - Red/green helper：先跑 `tsc ... src\worldJourney.ts && node scripts\check-world-journey.mjs`，确认缺 helper 失败；实现后 `pnpm.cmd run check:world-journey` -> `world journey helper ok`。
  - 相邻 helper：`pnpm.cmd run check:reading-progress` -> `reading progress helper ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome 桌面与精确 390px 设备模拟：`#/anchor/my-story` 只有一套可见旅程面板、4 个阶段可见、主动作跳到 `#/world/my-story/tianming`，且无水平溢出、无运行时异常。
- **边界**：
  - 本轮不改后端、不新增 API 或持久 artifact；只把世界入口的“我现在该做什么”补成第一版可扫读状态与主动作。

### 2026-06-07 — AppShell World Route Context

- **做了什么**：
  - 前端新增 `worldRouteContext` helper 与 `check:world-route-context` 轻量检查脚本，按世界内路由输出当前位置、页面职责、主动作和次动作。
  - `AppShell` 在顶栏下方新增纸面“当前位置”条，覆盖锚定、天命书、世界沙盘、卷宗阅读、跨事件长线卷、角色卷、势力卷、事件卷、世界线、检查点、多视角、作者台和机制档案等世界内页面。
  - 主动作/次动作全部复用已有路由，不新增后端 API、不改 artifact、不删现有顶栏导航；移动端位置条会换行并把动作按钮排成等宽栅格。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把 AppShell 世界位置条记为当前事实。
- **验证**：
  - Red/green helper：先跑 `pnpm.cmd run check:world-route-context`，确认缺 `src/worldRouteContext.ts` 失败；实现后同命令 -> `world route context helper ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：桌面访问 `#/world/my-story/sandbox` 显示“当前位置 · 运行 / 世界沙盘 / 进入卷宗阅读”，点击主动作进入 `#/world/my-story/worldlines/main/reading`；390px 移动端访问 `#/world/my-story/worldlines/main/characters/zhao_xuan` 显示“当前位置 · 角色卷 / 角色个人卷 / 继续沙盘”，`mobileOverflow=0`。
- **边界**：
  - 本轮只改前端壳层理解、样式和路由动作，不新增后端 API、不改变持久 artifact、不宣布完整 `WorldWorkspaceShell` 已完成。

### 2026-06-07 — Dossier Reading Focus Bar

- **做了什么**：
  - 前端新增 `dossierReadingFocus` helper 与 `check:dossier-reading-focus` 轻量检查脚本，按连续阅读场景、当前场景、证据数量和误会数量推导当前阅读导读状态。
  - `DossierReadingPage` 连续阅读态新增“当前阅读场景导读”纸面条，显示当前场次、场景标题、视角/叙事角色、本场/全卷证据和误会数量。
  - 导读条提供“上一场 / 下一场 / 看证据 / 追误会”动作；上一场/下一场复用既有分场景滚动定位，看证据/追误会滚到已有证据链和误会图谱。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把卷宗阅读当前场景导读条记为当前事实。
- **验证**：
  - Red/green helper：先跑 `pnpm.cmd run check:dossier-reading-focus`，确认缺 `src/dossierReadingFocus.ts` 失败；实现后同命令 -> `dossier reading focus helper ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：桌面访问 `#/world/my-story/worldlines/main/reading` 显示 `01 / 05` 导读条，点击“下一场”切到 `02 / 05`，点击“看证据”滚到证据区；390px 移动端导读条完整显示“上一场 / 下一场 / 看证据 / 追误会”，`mobileOverflow=0`。
- **边界**：
  - 本轮只改前端阅读交互和样式，不新增后端 API、不改变持久 artifact、不删现有卷宗目录、误会图谱或证据链。

### 2026-06-07 — Story Shelf Next-Step Guide

- **做了什么**：
  - 前端新增 `storyShelfFocus` helper 与 `check:story-shelf-focus` 轻量检查脚本，按故事来源和世界线运行次数推导“待确认天命 / 已有沙盘结果”、推荐下一步、来源和运行数。
  - `StoryEntryPage` 的最近故事卡新增阶段说明、来源/运行数指标和主按钮；未运行世界主动作进入天命书，已有沙盘结果主动作进入卷宗阅读。
  - 保留旧的世界沙盘、天命书、卷宗阅读、作者采纳台和机制档案入口；本轮不新增后端 API、不改 artifact、不删旧路由。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把世界书架下一步导览记为当前事实。
- **验证**：
  - Red/green helper：先跑 `pnpm.cmd run check:story-shelf-focus`，确认缺 `src/storyShelfFocus.ts` 失败；实现后同命令 -> `story shelf focus helper ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：桌面访问 `#/` 显示 3 张故事卡，第一张故事卡显示“待确认天命 / 确认天命”，旧 5 个入口仍可见，点击主按钮进入 `#/world/my-story/tianming`；390px 移动端故事卡显示阶段、主按钮和 5 个入口，`mobileOverflow=0`。

### 2026-06-07 — AppShell World Experience Track

- **做了什么**：
  - `worldRouteContext` 在原有当前位置、页面职责和主动作/次动作之外，新增 `stages` 语义，统一返回“定界 / 运行 / 阅读 / 采纳”四段世界体验轨道。
  - `AppShell` 的世界内位置条新增可点击阶段轨道，当前阶段高亮；四段分别跳到天命书、世界沙盘、卷宗阅读和作者台。
  - 保留原有顶栏世界导航、当前位置说明、主动作/次动作、设置和动效按钮；本轮不新增后端 API、不改 artifact、不删旧路由。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把世界体验轨道记为当前事实。
- **验证**：
  - Red/green helper：先扩展 `check:world-route-context` 断言 `stages`，确认缺字段失败；实现后同命令 -> `world route context helper ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：桌面访问 `#/world/my-story/sandbox` 显示“定界 / 运行 / 阅读 / 采纳”四段轨道且“运行”高亮，点击“阅读”进入 `#/world/my-story/worldlines/main/reading`；390px 移动端访问角色个人卷时“阅读”高亮、轨道宽度 366px、`mobileOverflow=0`。

### 2026-06-07 — AppShell Global Reading Resume

- **做了什么**：
  - `readingProgress` 新增 `shouldShowRecentReading` helper，区分当前 hash 和同一世界最近阅读 hash，避免用户已经在续读位置时重复显示按钮。
  - `AppShell` 在世界位置条动作区新增全局“继续阅读”；用户从沙盘、世界线、作者台等世界内页面都能回到本机最近读到的卷宗、长线卷、角色卷、势力卷、事件卷或检查点。
  - 移动端位置条动作栅格改为自适应三按钮布局，保留原主动作/次动作、体验轨道、顶栏导航、锚定页续读和全部既有路由。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把 AppShell 全局续读入口记为当前事实。
- **验证**：
  - Red/green helper：先扩展 `check:reading-progress` 断言 `shouldShowRecentReading`，确认缺 export 失败；实现后 `pnpm.cmd run check:reading-progress` -> `reading progress helper ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：先访问 `#/world/my-story/worldlines/main/longline` 写入最近阅读，再到 `#/world/my-story/sandbox` 显示“继续阅读 / 进入卷宗阅读 / 查看世界线”，按钮 title 为“继续读长线卷 · main”，点击回到 `#/world/my-story/worldlines/main/longline`；390px 移动端三枚动作按钮完整可见，`mobileOverflow=0`。
- **边界**：
  - 本轮不改后端、不新增 API 或持久 artifact，不做账号/跨设备同步；只复用浏览器 localStorage，把同一世界内的“回到刚才读哪儿”补到全局壳层。

### 2026-06-07 — AppShell Dossier Quick Switch

- **做了什么**：
  - `worldRouteContext` 新增 `dossiers` 语义，统一输出“正文 / 正史 / 锚点 / 角色 / 势力 / 事件 / 长线 / 世界线”八个卷宗入口、目标路由和当前高亮。
  - `AppShell` 在世界位置条下方新增全局卷宗速览盘；桌面展示短标签与卷宗全名，390px 移动端压成两行短标签，避免继续增高世界壳层。
  - 保留原有顶栏导航、世界体验轨道、主动作/次动作、全局继续阅读和所有页面路由；本轮不新增后端 API、不改 artifact。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把 AppShell 卷宗速览盘记为当前事实。
- **验证**：
  - Red/green helper：先扩展 `check:world-route-context` 断言 `dossiers`，确认缺字段失败；实现后 `pnpm.cmd run check:world-route-context` -> `world route context helper ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：桌面访问 `#/world/my-story/sandbox` 显示 8 个卷宗入口，点击“事件”进入 `#/world/my-story/worldlines/main/reading/event_multi_perspective`；访问 `#/world/my-story/worldlines/main/reading/character_volume` 时“角色”高亮；390px 移动端 8 个短标签完整可见，`mobileOverflow=0`。
- **边界**：
  - 这是 `WorldWorkspaceShell` 的壳层切片，不代表完整世界内部工作区完成；角色/势力跨章长线阅读、跨章节回收和更深误会网络仍需继续。

### 2026-06-07 — AppShell Mobile Shell Density

- **做了什么**：
  - 新增 `check:app-shell-mobile-layout` 检查脚本，锁定 640px 以下世界导航、体验轨道和窄屏 override 的密度规则，避免移动端又把世界入口撑成三行以上。
  - `appShell.css` 压缩移动端顶栏、按钮、体验轨道、动作区和位置条间距；9 个世界入口保持两行直接可见，4 个“定界 / 运行 / 阅读 / 采纳”阶段保持一行，8 个卷宗入口保持两行短标签。
  - 保留原有顶栏导航、世界位置条、体验轨道、主动作/次动作、全局继续阅读、卷宗速览盘和所有路由；本轮不新增后端 API、不改 artifact。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把 AppShell 移动端壳层压缩记为当前事实。
- **验证**：
  - Red/green helper：先跑 `pnpm.cmd run check:app-shell-mobile-layout`，确认当前 CSS 因世界导航 4/3/2 列、阶段两行而失败；实现后同命令 -> `AppShell mobile layout keeps world navigation compact and complete.`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：访问 `#/world/my-story/sandbox`，390px 与 360px 均显示 9 个顶栏入口、4 个阶段和 8 个卷宗入口，`overflow=0`；390px 主标题起点从约 524px 提前到 417px。
- **边界**：
  - 本轮只改前端壳层 CSS 与检查脚本，不新增世界能力、不改变 API/artifact 契约、不删任何入口。

### 2026-06-07 — Sandbox Runner Step Console

- **做了什么**：
  - 新增 `check:sandbox-runner-ux` 检查脚本，锁定沙盘运行台必须有专属产品壳、三步轨道、可选干预分组和“启动一轮推演”主动作。
  - `WorldSandboxPage` 的本轮运行面板从普通表单重组为“写事件 / 可选干预 / 启动推演”三步控制台；默认只要求用户写大事件。
  - 读者干预、投放对象和投放方式收进可选折叠区；真实模型决策建议、事件输入、启动按钮和原 `runRound` 请求字段全部保留。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把沙盘运行台分步化记为当前事实。
- **验证**：
  - Red/green helper：先跑 `pnpm.cmd run check:sandbox-runner-ux`，确认旧运行台缺结构失败；实现后同命令 -> `sandbox runner ux structure ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：桌面与 390px 访问 `#/world/my-story/sandbox` 均显示“写事件 / 可选干预 / 启动推演”、主按钮“启动一轮推演”；点击可选干预后 textarea 可见，展开前后 `overflow=0`。
- **边界**：
  - 本轮只改前端沙盘页 JSX/CSS 和检查脚本，不新增后端 API、不改变 `POST /api/stories/<slug>/sandbox/run` 请求字段、不改 artifact。

### 2026-06-07 — World Anchor Pulse Strip

- **做了什么**：
  - `worldJourney` 新增 `deriveWorldPulse`，把当前正文、可行动角色、开放伏笔和沙盘运行次数整理成四个可扫读的世界状态项。
  - `WorldAnchorPage` 在世界卷宗总览中新增“世界脉搏”卡片条，让用户进入某个世界后先看见世界活到哪一步，再选择天命书、沙盘、卷宗阅读、世界线、多视角或作者台。
  - 移动端复用紧凑卷宗总览，保留原世界启动卡、本机续读、旅程状态、编辑锚定、视觉资产、角色栏、势力入口和所有旧路由。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把世界脉搏记为当前事实。
- **验证**：
  - Red/green helper：先扩展 `check:world-journey` 断言 `deriveWorldPulse`，确认缺 export 失败；实现后 `pnpm.cmd run check:world-journey` -> `world journey helper ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：桌面与 390px 访问 `#/anchor/my-story` 均只有 4 张可见脉搏卡，显示当前正文、可行动角色、开放伏笔和沙盘运行；桌面只显示 full gateway，390px 只显示 compact gateway，`overflow=0`。
- **边界**：
  - 本轮只改前端状态推导、锚定页 JSX/CSS 和检查脚本，不新增后端 API、不改变 artifact，不删除编辑锚定、视觉资产、角色栏或既有入口。

### 2026-06-07 — Story Shelf Spotlight

- **做了什么**：
  - `storyShelfFocus` 新增 `deriveStoryShelfSpotlight`，按“导入世界优先、已有沙盘结果次之、原顺序兜底”的规则选择世界书架首屏推荐对象。
  - `StoryEntryPage` 首屏新增推荐世界面板，展示推荐理由、阶段、来源、世界线运行数、主动作和常用去向；桌面放在右侧，390px 移动端排在流程卡前。
  - 推荐面板封面改为横幅预览比例，避免手机首屏被封面占满；旧的内置样例、导入小说、主题创世、最近故事卡，以及世界沙盘、天命书、卷宗阅读、作者采纳台、机制档案入口全部保留。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把世界书架推荐世界面板记为当前事实。
- **验证**：
  - Red/green helper：先扩展 `check:story-shelf-focus` 断言 `deriveStoryShelfSpotlight`，确认缺 export 失败；实现后 `pnpm.cmd run check:story-shelf-focus` -> `story shelf focus helper ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：桌面与 390px 访问 `#/` 均显示 1 个推荐面板、3 张启动卡和 3 个故事卡组；390px 推荐主按钮在首屏内，点击进入 `#/world/my-story/tianming`，且 `overflow=0`。
- **边界**：
  - 本轮只改前端入口理解、样式和检查脚本，不新增后端 API、不改变 artifact，不删任何旧入口。

### 2026-06-07 — Sandbox Hero Runner

- **做了什么**：
  - `WorldSandboxPage` 将现有“写事件 / 可选干预 / 启动推演”运行台从导览层下方提升到首屏 hero；桌面在右侧，移动端排在标题说明后、导览之前。
  - 默认路径调整为先写大事件并立即可点“启动一轮推演”；读者干预、投放对象、投放方式和真实模型建议仍保留在可选区。
  - `check:sandbox-runner-ux` 增加顺序约束，锁定运行台必须出现在 `WorldRunway` 前，并补 hero 运行台样式 marker。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把沙盘页首屏运行台前置记为当前事实。
- **验证**：
  - Red/green helper：先扩展 `check:sandbox-runner-ux`，确认旧布局因运行台在导览后、缺 hero 样式而失败；实现后同命令 -> `sandbox runner ux structure ok`。
  - 前端：`cd engine/ui && pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：桌面与 390px 访问 `#/world/my-story/sandbox` 均只有 1 个运行台且在导览前；390px 下“启动一轮推演”按钮完整进入 844px 首屏（bottom=823），展开可选干预后仍 `overflow=0`；天命书、多视角、世界线和机制档案入口仍保留。
- **边界**：
  - 本轮只改前端沙盘页 JSX/CSS 和检查脚本，不新增后端 API、不改变 `POST /api/stories/<slug>/sandbox/run` 请求字段、不改 artifact。

### 2026-06-07 — Dossier Reading Mobile Guide

- **做了什么**：
  - 新增 `check:dossier-reading-ux` 检查脚本，锁定卷宗阅读移动端导读条存在、位于 `WorldRunway` 前，并只在移动/平板宽度显示。
  - `DossierReadingPage` 在移动端首屏新增“开始读正文 / 查卷宗 / 作者台”三步导读条；桌面仍保持原阅读工作台。
  - 三个入口分别复用现有滚动/路由：开始读正文滚到正文卡，查卷宗滚到卷宗目录，作者台进入作者采纳台。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把卷宗阅读移动端导读条记为当前事实。
- **验证**：
  - Red/green helper：先新增 `check:dossier-reading-ux`，确认旧阅读页因缺移动端导读条失败；实现后同命令 -> `dossier reading ux structure ok`。
  - 阅读 helper：`pnpm.cmd run check:dossier-reading-focus` -> `dossier reading focus helper ok`。
  - Chrome CDP smoke：390px 访问 `#/world/my-story/worldlines/main/reading`，导读条在首屏内且 display 为 `grid`；点击“开始读正文”后正文卡进入可见区，点击“查卷宗”后卷宗目录进入可见区，点击“作者台”进入 `#/world/my-story/author`；页面宽度保持 390px。
- **边界**：
  - 本轮只改前端卷宗阅读页 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `dossier-reading` 契约、不改 artifact。

### 2026-06-07 — Author Adoption Mobile Actions

- **做了什么**：
  - 新增 `check:author-adoption-ux` 检查脚本，锁定作者采纳台顶部中枢必须有“调整材料”动作、动作位于 `WorldRunway` 前，并在移动端使用紧凑两列动作布局。
  - `AuthorAdoptionPage` 顶部中枢新增“调整材料”，可直接滚到采纳决策、原大纲、沙盘涌现剧情和作者备注表单。
  - `authorAdoption.css` 压缩 620px 以下 hero、中枢文案、四步卡片和动作按钮布局；原采纳、生成草稿、采纳局部改写、确认入卷、回沙盘、表单和 Reviewer 区域全部保留。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把作者采纳台移动端材料入口记为当前事实。
- **验证**：
  - Red/green helper：先新增 `check:author-adoption-ux`，确认旧作者台因缺材料入口失败；实现后同命令 -> `author adoption ux structure ok`。
  - Chrome CDP smoke：390px 访问 `#/world/my-story/author`，中枢动作显示“写入采纳台 / 调整材料 / 回世界沙盘”，动作区域 bottom 从 851 降到 760；页面业务内容无水平溢出；点击“调整材料”后采纳材料表单进入可见区。
- **边界**：
  - 本轮只改前端作者采纳页 JSX/CSS、检查脚本和文档，不新增后端 API、不改变采纳、草稿、Reviewer、确认入卷契约，不改 artifact。

### 2026-06-07 — Longline Mobile Guide

- **做了什么**：
  - 新增 `check:longline-reading-ux` 检查脚本，锁定长线卷移动端导读条存在、位于 `WorldRunway` 前，并只在移动/平板宽度显示。
  - `LonglineReadingPage` 在移动端首屏新增“读长线 / 按事件追 / 回收误会 / 作者台”四格导读条；桌面仍保持原长线工作台。
  - 四个入口分别复用现有滚动/路由：读长线滚到长线阅读进度，按事件追滚到多事件索引，回收误会滚到误会回收台，作者台进入作者采纳台。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把长线卷移动端导读条记为当前事实。
- **验证**：
  - Red/green helper：先新增 `check:longline-reading-ux`，确认旧长线页因缺移动端导读条失败；实现后同命令 -> `longline reading ux structure ok`。
  - Chrome CDP smoke：390px 访问 `#/world/my-story/worldlines/main/longline`，导读条在首屏内且 display 为 `grid`；点击“读长线 / 按事件追 / 回收误会”分别把阅读进度、多事件索引和误会回收台带入可见区，点击“作者台”进入 `#/world/my-story/author`；页面宽度保持 390px，业务内容无水平溢出。
- **边界**：
  - 本轮只改前端长线卷 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `longline-reading` 契约、不改 artifact。

### 2026-06-07 — World Anchor Status Ribbon

- **做了什么**：
  - 新增 `check:world-anchor-status-ribbon` 检查脚本，锁定世界锚定页必须有“当前阶段 / 下一步 / 世界脉搏”状态条，并复用 `worldJourney` 与 `deriveWorldPulse`。
  - `WorldAnchorPage` 新增 `WorldStatusRibbon`：桌面显示在世界卷宗总览顶部，移动端额外前置到品牌和“世界启动”之间，让用户进入某世界后先知道世界现在到哪、下一步该做什么。
  - 状态条的主动作复用当前旅程推荐：有本机最近阅读时继续阅读，有沙盘结果时进入卷宗阅读，否则确认天命；原世界启动卡、紧凑卷宗总览、视觉资产、基线回放、实体别名、编辑锚定、角色栏和所有旧入口全部保留。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把世界锚定页状态条记为当前事实。
- **验证**：
  - Red/green helper：先新增 `check:world-anchor-status-ribbon`，确认旧锚定页因缺状态条失败；实现后同命令 -> `world anchor status ribbon structure ok`。
  - 旅程 helper：`pnpm.cmd run check:world-journey` -> `world journey helper ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：390px 访问 `#/anchor/my-story`，状态条位于 468-726px 首屏内，点击“下一步”进入最近阅读；1366px 桌面状态条位于中栏总览顶部；两种宽度 `scrollWidth === clientWidth` 且无业务内容水平溢出。
- **边界**：
  - 本轮只改前端锚定页 JSX/CSS、检查脚本和文档，不新增后端 API、不改 artifact，不删除既有世界锚定、视觉资产、基线回放、实体别名、角色栏或卷宗入口。

### 2026-06-07 — Event Perspective Mobile Guide

- **做了什么**：
  - 新增 `check:event-perspective-ux` 检查脚本，锁定事件多视角移动端导读条存在、位于 `WorldRunway` 前，并只在移动端显示。
  - `EventPerspectivePage` 在移动端首屏新增“读事件 / 看信息差 / 查证据 / 作者台”四格导读条；桌面仍保持原事件三栏工作台。
  - 四个入口分别复用现有滚动/路由：读事件滚到当前事件，看信息差滚到信息差，查证据滚到证据链，作者台进入作者采纳台。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把事件多视角移动端导读条记为当前事实。
- **验证**：
  - Red/green helper：先新增 `check:event-perspective-ux`，确认旧事件页因缺直接滚动导读失败；实现后同命令 -> `event perspective ux structure ok`。
  - 相邻阅读导读检查：`pnpm.cmd run check:longline-reading-ux` -> `longline reading ux structure ok`；`pnpm.cmd run check:dossier-reading-ux` -> `dossier reading ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：390px 访问 `#/world/my-story/worldlines/main/events/main/perspectives`，导读条位于 653-706px 首屏内且 display 为 `grid`；点击“看信息差 / 查证据”分别把信息差和证据链带入可见区；1366px 桌面导读条隐藏，两个尺寸均无水平溢出。
- **边界**：
  - 本轮只改前端事件页 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `event-perspective` 契约、不改 artifact。

### 2026-06-07 — Character Volume Mobile Guide

- **做了什么**：
  - 新增 `check:character-volume-ux` 检查脚本，锁定角色个人卷移动端导读条存在、位于 `WorldRunway` 前，并只在移动端显示。
  - `CharacterVolumePage` 在移动端首屏新增“读立场 / 查记忆 / 换角色 / 作者台”四格导读条；桌面仍保持原角色卷工作台。
  - 四个入口分别复用现有滚动/路由：读立场滚到当前角色，查记忆滚到主观记忆链，换角色滚到角色目录，作者台进入作者采纳台。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把角色个人卷移动端导读条记为当前事实。
- **验证**：
  - Red/green helper：先新增 `check:character-volume-ux`，确认旧角色卷因缺直接滚动导读失败；实现后同命令 -> `character volume ux structure ok`。
  - 相邻阅读导读检查：`pnpm.cmd run check:event-perspective-ux` -> `event perspective ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：390px 访问 `#/world/my-story/worldlines/main/characters/zhao_xuan`，导读条位于 592-646px 首屏内且 display 为 `grid`；点击“查记忆 / 换角色”分别把主观记忆链和角色目录带入可见区；1366px 桌面导读条隐藏，两个尺寸均无水平溢出。
- **边界**：
  - 本轮只改前端角色卷 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `dossier-reading` 或 `subjective-memory` 契约、不改 artifact。

### 2026-06-07 — Faction Volume Mobile Guide

- **做了什么**：
  - 新增 `check:faction-volume-ux` 检查脚本，锁定势力卷移动端导读条存在、位于 `WorldRunway` 前，并只在移动端显示。
  - `FactionVolumePage` 在移动端首屏新增“看站位 / 查代偿 / 换势力 / 作者台”四格导读条；桌面仍保持原势力卷工作台。
  - 四个入口分别复用现有滚动/路由：看站位滚到当前势力，查代偿滚到势力代偿状态，换势力滚到势力目录，作者台进入作者采纳台。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把势力卷移动端导读条记为当前事实。
- **验证**：
  - Red/green helper：先新增 `check:faction-volume-ux`，确认旧势力卷因缺直接滚动导读失败；实现后同命令 -> `faction volume ux structure ok`。
  - 相邻阅读导读检查：`pnpm.cmd run check:character-volume-ux` -> `character volume ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：390px 访问 `#/world/my-story/worldlines/main/factions/苍澜派`，导读条位于 592-646px 首屏内且 display 为 `grid`；点击“查代偿 / 换势力”分别把势力代偿和势力目录带入可见区；1366px 桌面导读条隐藏，两个尺寸均无水平溢出。
- **边界**：
  - 本轮只改前端势力卷 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `dossier-reading` 或 `worldline-state` 契约、不改 artifact。

### 2026-06-07 — Checkpoint Replay Mobile Guide

- **做了什么**：
  - 新增 `check:checkpoint-replay-ux` 检查脚本，锁定检查点回放移动端醒来导读条存在、位于完整工作流中枢和 `WorldRunway` 前，并只在移动端显示。
  - `CheckpointReplayPage` 在移动端 hero 后新增“继续读 / 看记忆 / 看代偿 / 作者台”四格导读条；桌面仍保持原检查点回放工作台。
  - 四个入口分别复用现有路由/滚动：继续读进入连续阅读，看记忆滚到角色记忆，看代偿滚到具象代偿，作者台进入作者采纳台。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把检查点回放移动端醒来导读条记为当前事实。
- **验证**：
  - Red/green helper：先新增 `check:checkpoint-replay-ux`，确认旧检查点页因缺移动端导读条失败；收紧顺序约束后再次确认导读条不能落在完整工作流中枢之后；实现后同命令 -> `checkpoint replay ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：390px 访问 `#/world/my-story/worldlines/main/checkpoints/autopilot_20260606_210329_1a8810/checkpoint_001`，导读条位于 573-767px 首屏内且 display 为 `grid`，位于完整醒来中枢和 `WorldRunway` 前；点击“看记忆 / 看代偿”分别把角色记忆和具象代偿带入可见区；页面宽度保持 390px，无业务内容横向溢出。
- **边界**：
  - 本轮只改前端检查点回放 JSX/CSS、检查脚本和文档，不新增后端 API、不改变自演检查点或 `readable_entry` 契约、不改 artifact。

### 2026-06-07 — Worldline Dossier Mobile Guide

- **做了什么**：
  - 新增 `check:worldline-dossier-ux` 检查脚本，锁定世界线档案移动端承接导读条存在、位于完整工作流中枢和 `WorldRunway` 前，并只在移动端显示。
  - `WorldlineDossierPage` 在移动端 hero 后新增“回放 / 看代偿 / 看任务 / 长线卷”四格导读条；桌面仍保持原世界线档案工作台。
  - 四个入口分别复用现有路由/滚动：回放最近检查点（无检查点时进入沙盘）、看代偿滚到具象代偿账、看任务滚到自演任务/检查点区，长线卷进入长线阅读。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把世界线移动端承接导读条记为当前事实。
- **验证**：
  - Red/green helper：先新增 `check:worldline-dossier-ux`，确认旧世界线页因缺移动端导读条失败；实现后同命令 -> `worldline dossier ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：390px 访问 `#/world/my-story/worldlines/main`，导读条位于 573-743px 首屏内且 display 为 `grid`，位于完整工作流中枢和 `WorldRunway` 前；点击“看代偿 / 看任务”分别把具象代偿账和自演任务/检查点区带入可见区；页面宽度保持 390px，无业务内容横向溢出。
- **边界**：
  - 本轮只改前端世界线页 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `worldline_dossier` 契约、不改 artifact。

### 2026-06-07 — Character Lens Mobile Guide

- **做了什么**：
  - 新增 `check:character-lens-ux` 检查脚本，锁定多视角页移动端分镜导读条存在、位于完整工作流中枢前，并只在移动端显示。
  - `CharacterLensPage` 在移动端 hero 后新增“生成 / 改事件 / 读卷宗 / 作者台”四格导读条；生成后主按钮会切换为“看结果”，桌面仍保持原多视角工作台。
  - 四个入口分别复用现有操作/路由/滚动：生成多视角、滚到事件材料表单、进入卷宗阅读、进入作者采纳台。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把多视角移动端分镜导读条记为当前事实。
- **验证**：
  - Red/green helper：先新增 `check:character-lens-ux`，确认旧多视角页因缺移动端导读条失败；实现后同命令 -> `character lens ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：390px 访问 `#/world/my-story/lens`，导读条位于 689-841px 首屏内且 display 为 `grid`，位于完整工作流中枢前；点击“改事件”把事件材料表单带入可见区；页面宽度保持 390px，无业务内容横向溢出。
- **边界**：
  - 本轮只改前端多视角页 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `character_lens` 契约、不改 artifact。

### 2026-06-07 — Tianming Mobile Constitution Guide

- **做了什么**：
  - 新增 `check:tianming-mobile-guide` 检查脚本，锁定天命书移动端宪法速断条存在、位于完整工作流中枢前，并只在移动端显示。
  - `TianmingPage` 在移动端 hero 后新增“生成/确认/沙盘 / 看锚点 / 投干预 / 去沙盘”四格速断条；桌面仍保持原天命书工作台。
  - 主按钮随状态生成草案、确认根天命或进入沙盘；辅助入口分别滚到锚点/状态区、干预预编译区，或直接进入世界沙盘。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把天命书移动端宪法速断条记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:tianming-mobile-guide` -> `tianming mobile guide structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：390px 访问 `#/world/my-story/tianming`，速断条位于 640-788px 首屏内且 display 为 `grid`，位于完整工作流中枢前；真实坐标点击“投干预”把干预预编译区带入可见区；页面宽度保持 390px，无业务内容横向溢出。
- **边界**：
  - 本轮只改前端天命书 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `tianming`、干预编译或 narrative compensation 契约、不改 artifact。

### 2026-06-07 — Workspace Archive Mobile Guide

- **做了什么**：
  - 新增 `check:workspace-archive-ux` 检查脚本，锁定机制档案移动端导读条存在、位于完整档案中枢前，并只在移动端显示。
  - `WorkspacePage` 在移动端首屏新增“天命书 / 沙盘 / 读卷宗 / 查证据”导读条；桌面仍保持原机制档案工作台。
  - 四个入口分别复用现有路由/滚动：进入天命书、进入世界沙盘、进入卷宗阅读、滚到运行/记忆证据指标区。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把机制档案移动端导读条记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:workspace-archive-ux` -> `workspace archive ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome CDP smoke：390px 访问 `#/workspace/my-story`，导读条位于 631-782px 且 display 为 `grid`，位于完整档案中枢前；真实坐标点击“查证据”把证据指标区带入可见区；页面宽度保持 390px，无水平溢出。
- **边界**：
  - 本轮只改前端机制档案 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 archive、settings、Graph 或 retrieval 契约、不改 artifact。

### 2026-06-07 — Dossier Reading Afterglow Actions

- **做了什么**：
  - `DossierReadingPage` 在连续阅读正文、关联卷宗之后和证据附录之前新增“读完之后，世界还在继续”余波承接台。
  - 四个入口分别复用现有功能：回看误会图谱、追踪跨事件长线卷、继续一轮世界沙盘、把涌现剧情送到作者采纳台。
  - 扩展 `check:dossier-reading-ux`，锁定承接台位于证据附录之前、包含四个动作，并在窄屏下折为单列。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把卷宗阅读余波承接台记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:dossier-reading-ux` -> `dossier reading ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - `git diff --check` 通过；仅有 Windows CRLF 提示。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - `git diff --check` 通过；仅有 Windows CRLF 提示。
- **边界**：
  - 本轮只改前端卷宗阅读 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `dossier-reading` 契约、不改 artifact。

### 2026-06-07 — Sandbox Round Result Bridge

- **做了什么**：
  - `WorldSandboxPage` 在单轮沙盘结果出现后、干预约束/世界线/角色行动链等细节前新增“本轮已发生”结果承接台。
  - 承接台汇总本轮事件、角色行动数、主观记忆数、因果债、锚点压力、资源变化、秘密流动和最先被推到台前的角色，让用户先理解世界如何消化这一轮。
  - 四个入口复用既有路由/滚动：读成正文进入卷宗阅读，看世界线进入世界线档案，生成多视角进入多视角页，再推一轮回到运行台。
  - 扩展 `check:sandbox-runner-ux`，锁定结果承接台必须出现在角色行动链前、包含四个动作，并在移动端折叠动作布局。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把沙盘结果承接台记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:sandbox-runner-ux` -> `sandbox runner ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - `git diff --check` 通过；仅有 Windows CRLF 提示。
- **边界**：
  - 本轮只改前端沙盘页 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `POST /api/stories/<slug>/sandbox/run` 请求字段、不改 artifact。

### 2026-06-07 — Sandbox Next-Round Handoff

- **做了什么**：
  - `WorldSandboxPage` 将“后续剧情可能性”从静态卡片升级为下一轮承接入口。
  - 每条可能性新增“作为下一轮事件”动作，点击后把标题和 brief 回填到首屏运行台的大事件输入框，并滚回运行台。
  - 回填时会清空上一轮临时干预内容和投放对象，避免用户在折叠的可选干预区里误重复投放旧干预；页面会显示“已放入运行台”反馈。
  - 扩展 `check:sandbox-runner-ux`，锁定后续可能性可回填下一轮、提示不沿用上轮临时干预，并覆盖窄屏动作布局。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把沙盘下一轮承接记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:sandbox-runner-ux` -> `sandbox runner ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端沙盘页 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `POST /api/stories/<slug>/sandbox/run` 请求字段、不改 artifact。

### 2026-06-07 — Sandbox Strategy Board

- **做了什么**：
  - `WorldSandboxPage` 在“本轮已发生”结果承接台之后、角色行动链之前新增“策略棋盘”。
  - 当真实模型 advisory 写出 `strategic_interaction` 时，策略棋盘会把谁在算计谁、策略、私下目的、筹码、误判、风险和预期世界影响整理为可扫读卡片，让用户先看懂本轮博弈，再进入角色明细。
  - 原有角色行动链里的模型临场判断、采信、欺骗、传播、反抗和策略明细仍保留。
  - 扩展 `check:sandbox-runner-ux`，锁定策略棋盘必须位于结果总览和角色行动链之间，并覆盖平板/移动端单列布局。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把沙盘策略棋盘记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:sandbox-runner-ux` -> `sandbox runner ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端沙盘页 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `POST /api/stories/<slug>/sandbox/run` 请求字段、不改 artifact。

### 2026-06-07 — Dossier Reading Mode Switch

- **做了什么**：
  - `DossierReadingPage` 顶部新增“读小说 / 查卷宗”模式切换。
  - 默认“读小说”模式隐藏卷宗侧栏并居中正文，保留卷首题签、当前场景导读、证据锚点、余波承接台和行动入口。
  - “查卷宗”模式恢复卷宗目录、阅读进度、误会图谱和 tab 切换；移动端导读条的“开始读正文 / 查卷宗”也接入同一模式。
  - 扩展 `check:dossier-reading-ux`，锁定模式状态、布局切换、侧栏保留和移动端响应式。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把卷宗阅读模式切换记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:dossier-reading-ux` -> `dossier reading ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端卷宗阅读 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `dossier-reading` 契约、不改 artifact。

### 2026-06-07 — Author Adoption Desk Switch

- **做了什么**：
  - `AuthorAdoptionPage` 顶部工作流中枢新增“写作台 / 审稿台”模式切换。
  - 默认写作台保留采纳决策、原大纲、沙盘涌现剧情和作者备注，方便先把材料写清楚。
  - 采纳记录、生成草稿、采纳局部改写或确认入卷后自动切到审稿台，聚焦采纳结果、下一章草稿、Reviewer 局部重写、编辑后定稿和确认入卷。
  - “调整材料”动作会回到写作台；审稿台隐藏材料区但不移除任何原有表单、Reviewer、确认入卷或路由能力。
  - 扩展 `check:author-adoption-ux`，锁定工作台模式状态、布局切换、材料区保留和窄屏样式。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把作者采纳台工作台模式切换记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:author-adoption-ux` -> `author adoption ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - `git diff --check` 通过；仅有 Windows CRLF 提示。
- **边界**：
  - 本轮只改前端作者采纳 JSX/CSS、检查脚本和文档，不新增后端 API、不改变采纳/草稿/Reviewer/确认入卷契约、不改 artifact。
### 2026-06-07 — Dossier Reading Chapter Rail

- **做了什么**：
  - `DossierReadingPage` 在连续阅读正文卡内、当前场景导读条之前新增“本卷场景”横向阅读轨道。
  - 读小说模式隐藏卷宗侧栏时，用户仍能看到整卷场景结构、当前进度、每场视角和证据数；点击任一场景会定位到对应正文段落。
  - 移动端轨道改为横向滚动，不挤压正文；查卷宗模式原有侧栏阅读进度、误会图谱、卷宗 tab、证据链和作者台入口全部保留。
  - 扩展 `check:dossier-reading-ux`，锁定轨道位置、场景跳转、移动端横向滚动和原侧栏保留。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff，把卷宗阅读本卷场景轨道记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:dossier-reading-ux` -> `dossier reading ux structure ok`。
- **边界**：
  - 本轮只改前端卷宗阅读 JSX/CSS、检查脚本和文档，不新增后端 API、不改变 `dossier-reading` 契约、不改 artifact。

### 2026-06-07 — AppShell World Workspace Summary

- **做了什么**：
  - `worldRouteContext` 为所有世界内路由新增 `workspaceSummary`，统一输出当前环节、承接世界线、下一步动作和为什么做。
  - `AppShell` 的世界位置条新增“当前环节 / 承接世界线 / 下一步为什么做”三枚纸面信息签，帮助用户跨天命书、沙盘、阅读、长线、角色/势力/事件卷、世界线、检查点、多视角、作者台和机制档案时理解自己在世界旅程中的位置。
  - 保留原有顶栏世界导航、“定界 / 运行 / 阅读 / 采纳”体验轨道、全局继续阅读、主次动作和八个卷宗速览入口；移动端总览改为单列，不挤掉既有入口。
  - 扩展 `check:world-route-context` 和 `check:app-shell-mobile-layout`，锁定工作区总览语义、移动端布局和既有导航不丢。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff，把 AppShell 世界工作区总览记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:world-route-context` -> `world route context helper ok`。
  - Focused helper：`pnpm.cmd run check:app-shell-mobile-layout` -> `AppShell mobile layout keeps world navigation compact and complete.`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端共享壳层、路由语境 helper、样式、检查脚本和文档，不新增后端 API、不改变世界线/阅读/作者采纳路由契约、不改 artifact。

### 2026-06-07 — Checkpoint Replay Mode Switch

- **做了什么**：
  - `CheckpointReplayPage` 顶部醒来回放中枢新增“读报告 / 查证据”模式切换。
  - 默认“读报告”模式隐藏回放摘要、角色记忆和具象代偿证据区，聚焦“从这个检查点继续读”和“下一步可写方向”。
  - “查证据”模式恢复回放摘要、角色记忆和具象代偿；移动端“看记忆 / 看代偿”会先切到查证据再滚动到对应区块。
  - 扩展 `check:checkpoint-replay-ux`，锁定模式状态、布局切换、移动端证据入口和证据区保留。
  - 同步 `memory.md`、`engine/README.md`、`engine/ui/README.md`、世界沙盘 PRD、路线图和 handoff，把检查点回放模式切换记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:checkpoint-replay-ux` -> `checkpoint replay ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - `git diff --check` 通过；仅有 Windows CRLF 提示。
- **边界**：
  - 本轮只改前端检查点回放 JSX、共用世界线 CSS、检查脚本和文档，不新增后端 API、不改变自演检查点或 `readable_entry` 契约、不改 artifact。

### 2026-06-07 — AppShell World Journey Pointers

- **做了什么**：
  - `AppShell` 顶栏下方的“当前环节 / 承接世界线 / 下一步为什么做”三枚世界工作区总览信息签从静态说明升级为可点击旅程指针。
  - “当前环节”会回到当前旅程阶段入口，“承接世界线”进入世界线档案，“下一步为什么做”直接执行当前页面语义里的主动作。
  - 保留原有顶栏世界导航、“定界 / 运行 / 阅读 / 采纳”体验轨道、全局继续阅读、主次动作和八个卷宗速览入口；移动端仍按单列压缩，不挤掉既有功能。
  - 扩展 `check:app-shell-mobile-layout`，锁定工作区总览必须保持可点击旅程指针、下一步必须执行 `primaryRoute`、世界线签必须进入世界线档案。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff，把 AppShell 世界旅程指针记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:app-shell-mobile-layout` -> `AppShell mobile layout keeps world navigation compact and complete.`。
  - Focused helper：`pnpm.cmd run check:world-route-context` -> `world route context helper ok`。
- **边界**：
  - 本轮只改前端共享壳层 JSX/CSS、检查脚本和文档，不新增后端 API、不改变世界线/阅读/作者采纳路由契约、不改 artifact。

### 2026-06-07 — Story Shelf Journey Pulse

- **做了什么**：
  - `storyShelfFocus` 为推荐世界新增 `journeyPulse`，按“天命 / 沙盘 / 阅读 / 采纳”输出入口首屏可理解的世界旅程状态。
  - `StoryEntryPage` 推荐进入卡新增四枚可点击旅程状态签：未运行世界突出“天命 / 下一步 / 确认边界”，已运行世界突出“阅读 / 现在读 / 看后果”，同时可直达沙盘或作者采纳台。
  - 保留原有推荐世界选择规则、主按钮、指标、封面、世界沙盘、天命书、卷宗阅读、作者采纳台和机制档案入口。
  - 扩展 `check:story-shelf-focus`，锁定 fresh/running 两类世界的四段旅程脉冲语义、推荐卡结构和移动端两列布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff，把世界书架推荐世界续行台记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:story-shelf-focus` -> `story shelf focus helper ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端入口 helper、故事书架 JSX/CSS、检查脚本和文档，不新增后端 API、不改变故事列表 API、不改 artifact。

### 2026-06-07 — AppShell World Pulse Bar

- **做了什么**：
  - `worldRouteContext` 为所有世界内路由新增 `continuitySignals`，统一输出“记忆 / 代偿 / 正文 / 写作”四类世界连续性信号。
  - `AppShell` 在工作区总览和体验轨道之间新增“世界脉搏”纸面条；四枚信号均可点击，分别接回卷宗阅读、世界线档案、长线卷和作者采纳台。
  - 桌面保持四列扫读，移动端压成两列，不挤掉原有顶栏世界导航、工作区总览、体验轨道、全局续读、主次动作和八个卷宗速览入口。
  - 扩展 `check:app-shell-mobile-layout`，锁定世界脉搏条必须渲染、四类信号必须可点击且移动端不强撑高行。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff，把 AppShell 世界脉搏条记为当前事实。
- **验证**：
  - Focused helper：`pnpm.cmd run check:app-shell-mobile-layout` -> `AppShell mobile layout keeps world navigation compact and complete.`。
  - Focused helper：`pnpm.cmd run check:world-route-context` -> `world route context helper ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端共享壳层、route context、样式、检查脚本和文档，不新增后端 API、不改变世界线/阅读/作者采纳路由契约、不改 artifact。

### 2026-06-07 — WorldRunway Next-Step Handoff

- **做了什么**：
  - `WorldRunway` 会从传入 `actions` 中自动提取 `primary` 动作，渲染为“建议先做”承接卡。
  - 其它 actions 保留为次出口，避免页面原有世界线、卷宗、作者台、沙盘等入口丢失。
  - 共享升级覆盖世界沙盘、卷宗阅读、角色个人卷、势力卷、事件多视角、长线卷、世界线档案、检查点回放和作者采纳台。
  - 新增 `check:world-runway-ux`，锁定 primary handoff、secondary action 保留、桌面三栏和移动端不强撑高行。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - Focused helper：`pnpm.cmd run check:world-runway-ux` -> `WorldRunway next-step handoff structure ok.`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端共享导览组件、样式、检查脚本和文档，不新增后端 API、不改变路由契约、不改 artifact、不删页面原有按钮。

### 2026-06-07 — AppShell Current Task Handoff

- **做了什么**：
  - `AppShell` 在世界工作区总览和世界脉搏之间新增“当前任务”承接条。
  - 承接条把“建议先做”、`primaryActionLabel`、`workspaceSummary.why`、全局继续阅读、主动作和次动作放在同一纸面行。
  - 移动端任务条先显示下一步理由，再用自适应紧凑动作保留继续阅读、主动作和次动作，不挤掉顶栏、世界脉搏、体验轨道或卷宗速览盘。
  - 扩展 `check:app-shell-mobile-layout`，锁定任务条存在、主动作与理由绑定、桌面一行扫读和移动端自适应动作。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:app-shell-mobile-layout`，确认缺少当前任务条时失败。
  - Focused helper：`pnpm.cmd run check:app-shell-mobile-layout` -> `AppShell mobile layout keeps world navigation compact and complete.`。
  - Route helper：`pnpm.cmd run check:world-route-context` -> `world route context helper ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端共享壳层 JSX/CSS、壳层检查脚本和文档，不新增后端 API、不改变路由契约、不改 artifact、不删任何世界入口。

### 2026-06-07 — WorldWorkspaceShell Journey Bus

- **做了什么**：
  - 新增共享 `WorldWorkspaceShell` 组件，`AppShell` 不再直接承载世界位置区 JSX，而是把 `worldRouteContext`、本机最近阅读和下一步动作交给统一世界工作区壳渲染。
  - 在原有当前位置、世界工作区总览、当前任务条、世界脉搏、体验轨道和卷宗速览盘之外，新增“世界旅程总线”。
  - 旅程总线把“定界 / 运行 / 阅读 / 采纳”四段变成稳定可点击扫读行，当前阶段标出“当前所在”，其它阶段标出“可随时进入”。
  - 保留原有顶栏世界导航、全局继续阅读、主次动作、世界脉搏、体验轨道和八个卷宗速览入口；移动端旅程总线压成两列，不挤掉既有功能。
  - 扩展 `check:app-shell-mobile-layout`，锁定 AppShell 必须委托 `WorldWorkspaceShell`、共享壳必须保留阶段和卷宗导航、旅程总线必须桌面四列/移动端两列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:app-shell-mobile-layout`，确认缺少 `WorldWorkspaceShell` 与旅程总线时失败。
  - Focused helper：`pnpm.cmd run check:app-shell-mobile-layout` -> `AppShell mobile layout keeps world navigation compact and complete.`。
  - Route helper：`pnpm.cmd run check:world-route-context` -> `world route context helper ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端共享壳层组件、样式、壳层检查脚本和文档，不新增后端 API、不改变路由契约、不改 artifact、不删任何世界入口；完整 `WorldWorkspaceShell` 仍需继续承接跨页面视觉 QA 和更深世界状态提示。

### 2026-06-07 — WorldWorkspaceShell State Handoffs

- **做了什么**：
  - `worldRouteContext` 为所有世界内路由新增 `stateHandoffs`，统一输出“正在承接 / 会留下 / 下一处看见”三段状态预告。
  - `WorldWorkspaceShell` 在当前任务条和世界脉搏之间新增三枚可点击状态预告签，解释当前页面正在消费什么、会把后果写到哪里、沿建议动作能在哪里看见结果。
  - 沙盘页会提示“事件与干预 -> 记忆与代偿 -> 进入卷宗阅读”；角色卷会提示主观记忆、误会和秘密怎样回到下一轮行动；作者台会提示采纳结果如何反哺下一章入口。
  - 桌面状态预告保持三列扫读，移动端压成单列，不挤掉顶栏世界导航、旅程总线、当前任务条、世界脉搏、体验轨道和卷宗速览入口。
  - 扩展 `check:world-route-context`，锁定沙盘和角色卷状态预告语义；扩展 `check:app-shell-mobile-layout`，锁定共享壳必须渲染状态预告、桌面三列、移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:world-route-context` 和 `pnpm.cmd run check:app-shell-mobile-layout`，确认缺少 `stateHandoffs` 与状态预告行时失败。
  - Route helper：`pnpm.cmd run check:world-route-context` -> `world route context helper ok`。
  - Focused helper：`pnpm.cmd run check:app-shell-mobile-layout` -> `AppShell mobile layout keeps world navigation compact and complete.`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端语义 helper、共享壳层组件、样式、壳层检查脚本和文档，不新增后端 API、不改变路由契约、不改 artifact、不删任何世界入口。

### 2026-06-07 — Worldline State Continuity Rail

- **做了什么**：
  - `WorldlineDossierPage` 在世界线工作流总览之后、`WorldRunway` 之前新增“状态接力台”。
  - 接力台把角色记忆、因果代偿、最近检查点和下一轮入口整理成四枚可点击承接卡。
  - 四枚入口复用既有页面数据与路由，可进入长线卷、具象代偿账、检查点回放、任务区或继续沙盘。
  - 桌面保持四列扫读，760px 以下折为单列，不移除原有移动端“回放 / 看代偿 / 看任务 / 长线卷”导读条、工作流总览、`WorldRunway` 或页面深部证据区。
  - 扩展 `check:worldline-dossier-ux`，锁定状态接力台位置、四类语义、真实字段引用和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:worldline-dossier-ux`，确认缺少状态接力台时失败。
  - Focused helper：`pnpm.cmd run check:worldline-dossier-ux` -> `worldline dossier ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端世界线页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 worldline dossier 契约、不改 artifact。

### 2026-06-07 — Longline Cross-Chapter Recovery Orchestrator

- **做了什么**：
  - `LonglineReadingPage` 在 `WorldRunway` 后、长线阅读状态区前新增“跨章回收台”。
  - 回收台把当前张力、首要误会、活跃线索和下一章钩子整理成四枚可点击承接卡。
  - 四枚入口复用既有 `current_tension`、`misbelief_recovery`、`open_threads`、`next_chapter_hook`、路由与滚动动作，可看当前节点、回收误会、追线索或送到作者台。
  - 桌面保持四列扫读，820px 以下折为单列；原有移动端导读条、长线阅读进度、多事件索引、误会回收台、未解线索、时间线和证据区全部保留。
  - 扩展 `check:longline-reading-ux`，锁定回收台位置、四类语义、真实字段引用和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:longline-reading-ux`，确认缺少跨章回收台时失败。
  - Focused helper：`pnpm.cmd run check:longline-reading-ux` -> `longline reading ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端长线卷 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `longline-reading` 契约、不改 artifact。

### 2026-06-07 — Character Memory Handoff Rail

- **做了什么**：
  - `CharacterVolumePage` 在 `WorldRunway` 后、三栏长阅读布局前新增“记忆接力台”。
  - 接力台把当前立场、最新主观记忆、首要误会和下一轮行动整理成四枚可点击承接卡。
  - 四枚入口复用既有 `activeTab`、`latestMemory`、`memoryStats`、`misbeliefs`、`memory_influence`、滚动动作和作者台路由，可读立场、查主观记忆、回看误会或把角色弧送到作者台。
  - 桌面保持四列扫读，760px 以下折为单列；原有移动端“读立场 / 查记忆 / 换角色 / 作者台”导读条、角色目录、角色卷正文、主观记忆链和证据区全部保留。
  - 扩展 `check:character-volume-ux`，锁定记忆接力台位置、四类语义、真实字段引用和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:character-volume-ux`，确认缺少记忆接力台时失败。
  - Focused helper：`pnpm.cmd run check:character-volume-ux` -> `character volume ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端角色个人卷 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `dossier-reading` / `subjective-memory` 契约、不改 artifact。

### 2026-06-07 — Faction Pressure Handoff Rail

- **做了什么**：
  - `FactionVolumePage` 在 `WorldRunway` 后、三栏势力阅读布局前新增“势力压力接力台”。
  - 接力台把当前站位、代偿压力、最近 ledger 和下一轮秩序整理成四枚可点击承接卡。
  - 四枚入口复用既有 `activeVolume`、`domain`、`latestLedger`、`primaryImpact`、`consequence`、滚动动作和作者台路由，可读势力卷封面、查势力代偿、看最近记录或把势力压力送到作者台。
  - 桌面保持稳定扫读网格，760px 以下折为单列；原有移动端“看站位 / 查代偿 / 换势力 / 作者台”导读条、势力目录、势力正文、因果压力域、最近 ledger 和证据区全部保留。
  - 扩展 `check:faction-volume-ux`，锁定压力接力台位置、四类语义、真实字段引用和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:faction-volume-ux`，确认缺少压力接力台时失败。
  - Focused helper：`pnpm.cmd run check:faction-volume-ux` -> `faction volume ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端势力卷 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `dossier-reading` / `worldline-state` 契约、不改 artifact。

### 2026-06-07 — Event Gap Handoff Rail

- **做了什么**：
  - `EventPerspectivePage` 在 `WorldRunway` 后、三栏事件阅读布局前新增“事件信息差接力台”。
  - 接力台把事件现场、信息差、首要误读和送入下一章整理成四枚可点击承接卡。
  - 四枚入口复用既有 `activeBeat`、`gap`、`primaryBias`、`report.evidence_panel`、`report.next_actions`、滚动动作和下一步路由，可读事件封面、看信息差、查谁误读了它或把信息差送到作者台。
  - 桌面保持稳定扫读网格，820px 以下折为单列；原有移动端“读事件 / 看信息差 / 查证据 / 作者台”导读条、事件节拍、事件正文、信息差、误读列表、下一步动作和证据区全部保留。
  - 扩展 `check:event-perspective-ux`，锁定信息差接力台位置、四类语义、真实字段引用和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:event-perspective-ux`，确认缺少信息差接力台时失败。
  - Focused helper：`pnpm.cmd run check:event-perspective-ux` -> `event perspective ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端事件多视角 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `event-perspective` 契约、不改 artifact。

### 2026-06-07 — Checkpoint Wake Handoff Rail

- **做了什么**：
  - `CheckpointReplayPage` 在 `WorldRunway` 后、检查点回放详情前新增“检查点醒来接力台”。
  - 接力台把醒来大事、角色记忆、代偿压力和接回正文整理成四枚可点击承接卡。
  - 四枚入口复用既有 `report.checkpoint`、`report.readable_entry`、`primaryMemory`、`primaryCompensation`、滚动动作和作者台路由，可读醒来报告、查看角色记忆、查看具象代偿或继续读这一轮。
  - 桌面保持稳定扫读网格，760px 以下折为单列；原有移动端“继续读 / 看记忆 / 看代偿 / 作者台”导读条、醒来回放中枢、读报告/查证据模式、回放摘要、记忆变化、具象代偿和后续可写方向全部保留。
  - 扩展 `check:checkpoint-replay-ux`，锁定醒来接力台位置、四类语义、真实字段引用和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:checkpoint-replay-ux`，确认缺少醒来接力台时失败。
  - Focused helper：`pnpm.cmd run check:checkpoint-replay-ux` -> `checkpoint replay ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端检查点回放 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变自演检查点或 `readable_entry` 契约、不改 artifact。

### 2026-06-07 — Autopilot Overnight Wake Brief

- **做了什么**：
  - `WorldSandboxPage` 的世界自演结果报告内新增“昨夜世界醒来台”。
  - 醒来台把昨夜发生、角色记忆、世界变化原因和继续阅读入口整理成四枚可点击承接卡。
  - 四枚入口复用既有 `overnight_report`、`overnightMemory`、`overnightContinuation`、`autopilotReport.readable_entry` 和时间线滚动动作，可直接继续卷宗阅读或查看昨夜时间线。
  - 原有任务进度、刷新/暂停/恢复、停止证据、中断原因、恢复检查点、`WakeReadingEntry`、醒来时间线、小说节拍和检查点回放列表全部保留。
  - 扩展 `check:sandbox-runner-ux`，锁定醒来台位置、四类语义、真实字段引用和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:sandbox-runner-ux`，确认缺少昨夜醒来台时失败。
  - Focused helper：`pnpm.cmd run check:sandbox-runner-ux` -> `sandbox runner ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端沙盘页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `world-autopilot` / `readable_entry` 契约、不改 artifact。

### 2026-06-07 — Author Confirmation Handoff Rail

- **做了什么**：
  - `AuthorAdoptionPage` 在确认入卷详情前新增“确认入卷接力台”。
  - 接力台把已成正史、反哺下一轮、Reviewer 定稿和回到世界整理成四段可行动承接。
  - 三个动作复用既有卷宗阅读路由、阅读链滚动和世界沙盘路由，可读确认正文、查看 reading trail 或继续沙盘。
  - 接力台直接消费 `confirmation.artifacts`、`confirmation.continuation_effect.next_sandbox_entry`、`confirmation.reading_trail`、`confirmation.edit_source` 和 `confirmation.accepted_local_rewrites`；原有确认详情、Reviewer 检查和跨卷宗阅读链全部保留。
  - 扩展 `check:author-adoption-ux`，锁定接力台位置、四类语义、真实字段引用和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:author-adoption-ux`，确认缺少接力台时失败。
  - Focused helper：`pnpm.cmd run check:author-adoption-ux` -> `author adoption ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端作者采纳 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变采纳、草稿、Reviewer 或确认入卷契约，不改 artifact。

### 2026-06-07 — Tianming Confirmation Handoff Rail

- **做了什么**：
  - `TianmingPage` 在天命书确认后、详情面板前新增“天命生效接力台”。
  - 接力台把世界宪法已生效、锚点承压、干预边界和沙盘就绪整理成四段可行动承接。
  - 四个动作复用既有世界沙盘路由、干预预编译滚动、锚点压力滚动和世界锚定路由，可直接进入沙盘、投放干预、看锚点压力或回世界入口。
  - 接力台直接消费 `book.artifact`、`book.anchor_status`、`book.contract_pressure.pressure_tiers`、`book.mutation_policy` 和 `book.narrative_attractors`；原有宪法封面、移动端速断条、吸引子、锚点、压力、候选承载者、干预预编译和世界线代偿全部保留。
  - 扩展 `check:tianming-mobile-guide`，锁定接力台位置、四类语义、真实字段引用和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:tianming-mobile-guide`，确认缺少接力台时失败。
  - Focused helper：`pnpm.cmd run check:tianming-mobile-guide` -> `tianming mobile guide structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端天命书 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `tianming`、干预编译或 narrative compensation 契约，不改 artifact。

### 2026-06-07 — Sandbox Strategy Continuation Rail

- **做了什么**：
  - `WorldSandboxPage` 在策略棋盘之后、干预约束和角色行动链等密集证据前新增“下一轮暗线承接”。
  - 当真实模型 advisory 写出 `strategic_interaction` 时，暗线承接会把角色算计、可能误判和世界影响整理成可继续发酵的下一轮事件种子。
  - 用户可一键“作为下一轮暗线”回填到首屏运行台，并自动清空上一轮临时干预内容和投放对象，避免旧干预被误重复投放。
  - 接力台复用既有 `strategyInteractions`、`item.misread`、`item.effect`、`item.hook` 和运行台 state；原有结果承接台、策略棋盘、干预约束、角色行动链、后续剧情可能性和世界自演报告全部保留。
  - 扩展 `check:sandbox-runner-ux`，锁定接力台位置、真实字段引用、回填 helper、清空旧干预和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:sandbox-runner-ux`，确认缺少暗线承接台时失败。
  - Focused helper：`pnpm.cmd run check:sandbox-runner-ux` -> `sandbox runner ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端沙盘页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `POST /api/stories/<slug>/sandbox/run` 字段，不改 artifact。

### 2026-06-07 — Dossier Reading Continuity Rail

- **做了什么**：
  - `DossierReadingPage` 在连续阅读态的当前场景导读条之后、正文段落之前新增“续读签”。
  - 续读签把当前正在读的场景、下一场、本场误会和 `continuity_threads` 承接线集中到正文前。
  - 用户可直接读下一场、回到本场或追本场误会，不必在侧栏、sticky 导读和读后承接台之间来回找。
  - 接力信息复用既有 `continuous_reading.reading_sections`、`continuity_threads`、`chapter_cliffhanger`、误会图谱和滚动/作者台动作；原有“读小说 / 查卷宗”切换、本卷场景轨道、当前场景导读条、误会图谱、正文证据锚点和读完余波承接台全部保留。
  - 扩展 `check:dossier-reading-ux`，锁定续读签位置、真实字段引用、继续/追误会动作和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:dossier-reading-ux`，确认缺少续读签时失败。
  - Focused helper：`pnpm.cmd run check:dossier-reading-ux` -> `dossier reading ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端卷宗阅读 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `dossier-reading` 契约，不改 artifact。

### 2026-06-07 — Story Card Journey Pulse

- **做了什么**：
  - `StoryEntryPage` 的每张最近故事卡新增“天命 / 沙盘 / 阅读 / 采纳”四段可点击旅程脉冲。
  - 旅程脉冲复用既有 `focus.journeyPulse`，未运行世界突出“下一步确认边界”，已运行世界突出“现在读”。
  - 用户不必只依赖推荐世界卡，也能从任意故事卡直接进入天命书、世界沙盘、卷宗阅读或作者采纳台。
  - 旅程签位于故事卡主打开按钮之外、推荐主按钮之前，避免嵌套按钮；原有推荐主按钮、世界沙盘、天命书、卷宗阅读、作者采纳台和机制档案入口全部保留。
  - 扩展 `check:story-shelf-focus`，锁定故事卡必须复用 `journeyPulse`、旅程签位置、真实导航函数和移动端两列布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:story-shelf-focus`，确认缺少故事卡旅程脉冲时失败。
  - Focused helper：`pnpm.cmd run check:story-shelf-focus` -> `story shelf focus helper ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端故事书架 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 story list 契约，不改 artifact。

### 2026-06-07 — Open World Onboarding Journey Rails

- **做了什么**：
  - `ImportNovelPage` 在开卷前台和详细表单之间新增“开卷旅程”接力条。
  - `GenesisPage` 在无稿创世台和详细表单之间新增“创世旅程”接力条。
  - 导入页把素材状态接到世界锚定、天命书、世界沙盘和卷宗阅读；创世页把世界雏形接到世界锚定、天命书和世界沙盘。
  - 两页接力条复用现有 `slugOk`、`sourceLabel` / `premiseReady`、`mock`、`canSubmit` 和 `submit`，并保留选择文件、填写章节、填写主题和返回书架动作。
  - 新增 `check:open-world-onboarding-ux`，锁定接力条位置、四段旅程、真实 state 引用和移动端两列布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:open-world-onboarding-ux`，确认缺少开卷/创世旅程接力条时失败。
  - Focused helper：`pnpm.cmd run check:open-world-onboarding-ux` -> `open-world onboarding journey rails ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端导入/创世 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变导入、创世、job polling、路由或 artifact 契约。

### 2026-06-07 — Author Reviewer Quality Gate

- **做了什么**：
  - `AuthorAdoptionPage` 在局部修订包摘要和局部改写列表之间新增“Reviewer 质检门”。
  - 质检门把阻断/高优先级审稿项、已选局部改写、自动定稿预览和入卷判断组织成四枚可扫读卡。
  - 用户可在进入密集局部改写列表前直接采纳选中改写，或滚到正文编辑区检查自动定稿。
  - 质检门直接消费 `draft.revision_pack.semantic_reviewer.review_items`、`editorial_revision_draft.status`、`selectedRewriteCount`、`localizedRewriteCount`、`confirmation_gate.author_action` 与现有 `applySelectedRewrites` / `scrollToPageItem`。
  - 扩展 `check:author-adoption-ux`，锁定质检门位置、真实字段引用、四类语义、主动作和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:author-adoption-ux`，确认缺少 Reviewer 质检门时失败。
  - Focused helper：`pnpm.cmd run check:author-adoption-ux` -> `author adoption ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端作者采纳页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变采纳、草稿、Reviewer、确认入卷或 artifact 契约。

### 2026-06-07 — Author Final Draft Comparison Rail

- **做了什么**：
  - `AuthorAdoptionPage` 在作者修订稿编辑框之后、确认入卷动作之前新增“定稿对照台”。
  - 对照台并排展示原始草稿、当前定稿、入卷质量门，并提供“采用 Reviewer 定稿 / 恢复原草稿 / 回看局部改写”动作。
  - 当前定稿来源会根据编辑框内容判断：若用户恢复原草稿，不再误标为 Reviewer 编辑后定稿。
  - 对照台直接消费 `draft.chapter_text`、`editedChapterText`、`rewriteApplication.edited_final_chapter.final_chapter_text` 和 `edited_final_chapter.quality_gate`。
  - 扩展 `check:author-adoption-ux`，锁定对照台位置、真实字段引用、回滚动作、质量门和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:author-adoption-ux`，确认缺少定稿对照台时失败。
  - Focused helper：`pnpm.cmd run check:author-adoption-ux` -> `author adoption ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端作者采纳页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变采纳、草稿、Reviewer、确认入卷或 artifact 契约；整章风格润色和真实模型编辑器仍是后续深化。

### 2026-06-07 — Sandbox Intervention Consequence Preview

- **做了什么**：
  - `WorldSandboxPage` 在首屏运行台的可选干预之后新增“干预后果预演台”。
  - 预演台会随读者干预、投放对象和投放方式实时解释投放对象、沉浸/AU 投放方式、世界会怎样吸收，以及运行后应从哪里观察后果。
  - 后果观察点明确接到角色主观记忆、世界线代偿和多视角正文，让用户在启动推演前就知道“干预不是按钮，而是会被世界消化的变量”。
  - 预演台提供“添加/调整干预”和“清空干预”动作；无干预时也会说明只运行大事件仍会写入角色行动、主观记忆和世界线变化。
  - 扩展 `check:sandbox-runner-ux`，锁定预演台语义、控制 helper、清空动作和移动端单列布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:sandbox-runner-ux`，确认缺少干预后果预演台时失败。
  - Focused helper：`pnpm.cmd run check:sandbox-runner-ux` -> `sandbox runner ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改前端沙盘页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `POST /api/stories/<slug>/sandbox/run` 字段，不改 artifact。

### 2026-06-07 — Story Shelf Vitality Foyer

- **做了什么**：
  - `StoryEntryPage` 的推荐世界卡新增“世界魅力前厅”，放在推荐理由之后、旅程脉冲之前。
  - `storyShelfFocus` 新增 `vitalitySignals`，按 `runCount` 输出“世界会运行 / 角色会记得 / 干预有后果 / 章节来自演化”四枚活性信号。
  - 未运行世界显示待启动、待写入、待投放、待生成；已运行世界显示已运行轮数、可回看、可追踪、可写下一章。
  - 推荐世界卡不再只给用户按钮和指标，而是先解释这个世界为什么值得继续、下一轮运行会把后果写到哪里。
  - `check:story-shelf-focus` 锁定活性信号语义、推荐卡渲染、移动端单列和检查脚本临时目录清理。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:story-shelf-focus`，确认缺少 `vitalitySignals` 时失败。
  - Focused helper：`pnpm.cmd run check:story-shelf-focus` -> `story shelf focus helper ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - 浏览器 DOM：`http://localhost:5178/` 下 `.entry__spotlight-vitality` 渲染 4 张活性信号卡。
- **边界**：
  - 本轮只改前端故事书架 helper、JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 story list 契约，不改 artifact。

### 2026-06-07 — Author Chapter Polish Radar

- **做了什么**：
  - `AuthorAdoptionPage` 在作者修订稿编辑框之后、定稿对照台之前新增“章节质感雷达”。
  - 雷达复用 `draft.reviewer_checklist`、语义 Reviewer review items、已选局部改写、当前定稿来源和 `edited_final_chapter.quality_gate`。
  - 四枚信号分别解释“读感节奏 / 角色动机 / 世界入文 / 入卷准备”，让作者先判断这章是否像一章可读小说，再进入原稿/定稿对照。
  - 雷达动作可直达 Reviewer 细节、正文编辑、确认入卷；有高优先级改写已选且尚未应用时，可直接采纳高优先级改写。
  - 扩展 `check:author-adoption-ux`，锁定质感雷达语义、真实字段引用、动作入口、与定稿对照台的位置关系和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:author-adoption-ux`，确认缺少章节质感雷达时失败。
  - Focused helper：`pnpm.cmd run check:author-adoption-ux` -> `author adoption ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - 浏览器 UI 流程：在 `http://localhost:5178/#/world/my-story/author` 执行“写入采纳台 -> 生成下一章草稿”，`.adoption-polish-radar` 渲染 4 张质感信号卡，并显示 Reviewer、采纳改写、正文编辑和确认入卷动作。
- **边界**：
  - 本轮只改前端作者采纳页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变采纳、草稿、Reviewer、确认入卷或 artifact 契约；真实整章模型润色仍是后续深化。

### 2026-06-07 — Sandbox Event Entry Preview

- **做了什么**：
  - `WorldSandboxPage` 在首屏运行台的大事件输入之后、可选干预之前新增“事件入局预演台”。
  - 预演台用“谁会先动 / 世界怎样记账 / 干预怎样入局 / 跑完先看哪里”四枚信号解释当前大事件如何进入角色行动、主观记忆、因果债和世界线状态。
  - 预演台会随 `majorEvent.trim()`、是否存在读者干预和投放方式变化；无干预时说明角色会按事件、旧记忆和利益行动，有干预时说明干预会如何贴着事件进入角色判断。
  - 新增“修改事件”和“让读者干预入局 / 调整干预”动作，分别聚焦大事件输入和干预输入；原有启动推演、可选干预、清空干预、真实模型 advisory、结果承接、策略棋盘、自演结果和阅读出口全部保留。
  - 扩展 `check:sandbox-runner-ux`，锁定事件入局预演台语义、位置、真实状态引用和移动端单列布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:sandbox-runner-ux`，确认缺少事件入局预演台时失败。
  - Focused helper：`pnpm.cmd run check:sandbox-runner-ux` -> `sandbox runner ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome UI smoke：`http://localhost:5178/#/world/my-story/sandbox` 桌面下预演台渲染 4 张信号卡；两个动作分别聚焦干预输入和事件输入；390px 下无水平溢出，4 张信号卡单列。
- **边界**：
  - 本轮只改前端沙盘页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `POST /api/stories/<slug>/sandbox/run` 字段，不改 artifact。

### 2026-06-07 — Worldline Compensation Compass

- **做了什么**：
  - `WorldlineDossierPage` 在状态接力台之后、`WorldRunway` 之前新增“代偿罗盘”。
  - 罗盘复用 `worldline_dossier` 里已有的 `state.consequence_state.summary`、`ledger`、`next_round_hint` 和代偿域数据。
  - 四枚信号分别解释“最近代价 / 承压领域 / 下一轮提示 / 从这里继续看”，让用户先理解世界为什么会继续变，再去读密集世界线状态。
  - 罗盘动作可直接看详细代偿账、回放最近检查点或进入长线卷；没有检查点时会回到继续沙盘。
  - 扩展 `check:worldline-dossier-ux`，锁定罗盘位置、真实字段引用、桌面四列和移动端单列布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:worldline-dossier-ux`，确认缺少代偿罗盘时失败。
  - Focused helper：`pnpm.cmd run check:worldline-dossier-ux` -> `worldline dossier ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome UI smoke：`http://localhost:5178/#/world/my-story/worldlines/main` 桌面下罗盘渲染 4 张信号卡，位于状态接力台之后、世界内部导览之前；“看详细代偿账”能滚到代偿区；390px 下无水平溢出且 4 张信号卡单列。
- **边界**：
  - 本轮只改前端世界线档案页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `worldline_dossier` / `worldline_state` 字段，不改 artifact。

### 2026-06-07 — World Anchor Awakening Foyer

- **做了什么**：
  - `WorldAnchorPage` 在桌面中栏的世界卷宗总览之前新增“世界苏醒台”，移动端在状态条之后渲染紧凑版。
  - 苏醒台复用 `deriveWorldJourney`、`deriveWorldPulse`、本机 `recentReading`、`data.run_count`、首个角色和首条开放伏笔。
  - 四枚信号分别解释“世界醒着吗 / 谁会行动 / 哪条伏笔牵引 / 从哪里继续”，让用户进入世界后先判断这个世界是否已经活起来。
  - 动作可直接执行推荐下一步、进入世界沙盘或查看世界线；最近阅读存在时仍接回本机续读位置。
  - 扩展 `check:world-anchor-status-ribbon`，锁定苏醒台位置、真实字段引用、桌面四列、移动端紧凑版和单列布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:world-anchor-status-ribbon`，确认缺少世界苏醒台时失败。
  - Focused helper：`pnpm.cmd run check:world-anchor-status-ribbon` -> `world anchor status ribbon structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome UI smoke：`http://localhost:5178/#/anchor/my-story` 桌面下苏醒台渲染 4 张信号卡，位于世界卷宗总览之前；“看世界线”跳到 `#/world/my-story/worldlines/main`；390px 下桌面版隐藏、紧凑版显示、4 张信号卡单列且无水平溢出。
- **边界**：
  - 本轮只改前端锚定页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `world-anchor` 字段，不改 artifact，不删编辑锚定、视觉资产、基线回放、世界启动、卷宗总览、角色栏或角色探针。

### 2026-06-07 — World Chronicle And Anchor Volume Pages

- **做了什么**：
  - 新增 `WorldVolumePage`，把世界正史卷和主锚点卷从卷宗阅读 tab 提升为独立世界内部页面。
  - 新增路由 `#/world/<slug>/worldlines/<worldline_id>/chronicle` 与 `#/world/<slug>/worldlines/<worldline_id>/anchors`，并接入 `App.tsx`、`routing.ts`、`worldRouteContext.ts` 和全局续读记录。
  - 页面复用现有 dossier-reading API 的 `world_chronicle` / `anchor_volume` tab 数据，不新增后端 API、artifact 或字段契约。
  - 页面包含移动端导读条、`WorldRunway`、正史/锚点接力台、正文证据锚点、世界线状态和回卷宗阅读/继续沙盘/作者台动作；没有 volume tab 时显示明确空态。
  - `DossierReadingPage` 对应 tab 新增“世界正史卷 / 主锚点卷”独立入口，AppShell 卷宗速览盘的正史和锚点入口也直达独立页。
  - 新增 `check:world-volume-ux`，并扩展 `check:world-route-context`、`check:reading-progress` 覆盖新路由和全局续读语义。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:world-volume-ux`，确认缺少 `WorldVolumePage.tsx` 时失败。
  - Focused helper：`pnpm.cmd run check:world-volume-ux` -> `world volume ux structure ok`。
  - 路由上下文：`pnpm.cmd run check:world-route-context` -> `world route context helper ok`。
  - 续读记录：`pnpm.cmd run check:reading-progress` -> `reading progress helper ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Chrome UI smoke：`http://localhost:5178/#/world/my-story/worldlines/main/chronicle` 桌面下渲染“世界正史卷”、接力台和阅读区，正史页动作可切到 `#/world/my-story/worldlines/main/anchors`；390px 下“主锚点卷”移动端导读条显示、布局无水平溢出。当前本地样本没有 volume tab，smoke 验证的是空态和页面结构。
- **边界**：
  - 本轮只改前端路由、页面、壳层上下文、续读 helper、结构检查脚本和文档，不新增后端 API、不改变 `dossier-reading` 响应契约、不改 artifact。

### 2026-06-07 — Longline Cross-Chapter Continuation Map

- **做了什么**：
  - `LonglineReadingPage` 在“跨章回收台”之后、长线阅读状态区之前新增“跨章承接地图”。
  - 地图把当前阅读节点、来源事件、误会余波和下一轮去向连成可点击因果链，让用户读长线时知道这段内容怎样继续推动世界。
  - 地图复用现有 `activeEntry`、`activeEvent`、`primaryMisbelief`、`current_tension`、`open_threads` 和 `next_actions`，不新增后端 API 或 artifact。
  - “现在读到”可把当前长线节点带回视口；“来源事件”可定位事件索引；“误会余波”回到误会回收路径；“下一轮去向”执行现有下一步动作或送作者台。
  - 扩展 `check:longline-reading-ux`，锁定地图语义、位置、真实字段引用、桌面稳定网格和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:longline-reading-ux`，确认缺少 `longline-continuation-map` 时失败。
  - Focused helper：`pnpm.cmd run check:longline-reading-ux` -> `longline reading ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - In-app Browser smoke：`http://127.0.0.1:5180/#/world/my-story/worldlines/main/longline` 桌面 1366px 下地图渲染 4 个节点、位于阅读状态区之前、使用 5 列稳定网格；点击“现在读到”后当前长线节点进入视口；390px 下地图单列且无水平溢出。
- **边界**：
  - 本轮只改前端长线卷 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `longline-reading` 响应契约、不改 artifact。

### 2026-06-07 — Worldline Fermentation Ledger

- **做了什么**：
  - `WorldlineDossierPage` 在“代偿罗盘”之后、`WorldRunway` 之前新增“世界发酵账”。
  - 发酵账把最近三条 `state.consequence_state.ledger`、前四个代偿域、`state.consequence_state.next_round_hint` 和 `nextRoundReads` 组织成“最近写入 / 承压域 / 下一轮会消费”的可行动路径。
  - 用户进入世界线页后不仅能理解世界为什么继续变，也能看见哪些代价会被下一轮角色行动消费，并可直接去长线卷或详细代偿账。
  - 扩展 `check:worldline-dossier-ux`，锁定发酵账语义、位置、真实字段引用、桌面稳定三列和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:worldline-dossier-ux`，确认缺少 `worldline-fermentation-ledger` 时失败。
  - Focused helper：`pnpm.cmd run check:worldline-dossier-ux` -> `worldline dossier ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Repo：`git diff --check` 通过；仅有 Windows CRLF 提示。
  - In-app Browser smoke：`http://localhost:5180/#/world/my-story/worldlines/main` 桌面下发酵账渲染在代偿罗盘之后、世界内部导览之前，使用三列布局；“去长线卷”唯一且能跳到 `#/world/my-story/worldlines/main/longline`；390px 下发酵账单列、按钮稳定且无水平溢出。
- **边界**：
  - 本轮只改前端世界线档案页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `worldline_dossier` / `worldline_state` 字段，不改 artifact。

### 2026-06-07 — Author Chapter Revision Route

- **做了什么**：
  - `AuthorAdoptionPage` 在作者修订稿编辑框之后、章节质感雷达之前新增“整章修订路线”。
  - 路线把“先看风险 / 再收改写 / 然后磨正文 / 最后入卷”整理成四张可点击步骤卡。
  - 四步复用现有 `urgentReviewerItems`、`selectedRewriteCount`、`localizedRewriteCount`、`finalTextSource`、`currentFinalPreview` 和 `edited_final_chapter.quality_gate`，不新增后端字段。
  - 动作可直接跳到 Reviewer 质检门、采纳已选局部改写、回到正文编辑或去确认入卷，让作者知道定稿前应该先处理什么。
  - 扩展 `check:author-adoption-ux`，锁定修订路线的语义、位置、真实状态引用、桌面四列和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:author-adoption-ux`，确认缺少 `revisionRouteSteps` 时失败。
  - Focused helper：`pnpm.cmd run check:author-adoption-ux` -> `author adoption ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - In-app Browser smoke：`http://localhost:5173/#/world/demo/author` 可打开作者采纳台，首屏工作流中枢可见且无前端白屏或告警；当前后端未运行，因此草稿态可视化由 focused helper 和构建覆盖。
- **边界**：
  - 本轮只改前端作者采纳页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变采纳、草稿、Reviewer、确认入卷或 artifact 契约。

### 2026-06-07 — Character Memory Arc

- **做了什么**：
  - `CharacterVolumePage` 在“记忆接力台”和长阅读布局之间新增“角色记忆弧线”。
  - 记忆弧线取最近四段主观记忆，把来源事件、上一段主观记忆、新信念、信任变化、异常感和下一次预期整理成连续卡片。
  - 用户读角色卷时能从“最新记忆”继续看见角色信念怎样逐步变化，并可直接看完整记忆链或回沙盘验证。
  - 扩展 `check:character-volume-ux`，锁定记忆弧线位置、真实字段引用、桌面四列和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:character-volume-ux`，确认缺少 `memoryArcSignals` 时失败。
  - Focused helper：`pnpm.cmd run check:character-volume-ux` -> `character volume ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Repo：`git diff --check` 通过；仅有 Windows CRLF 提示。
  - In-app Browser smoke：`http://localhost:5181/#/world/v090-alpha-proof/worldlines/branch_a/characters/han_wu_gui` 可打开角色卷，桌面空态、记忆接力台和移动端导读条正常，无控制台 error；390px 下无水平溢出。当前后端样本没有主观记忆，记忆弧线按预期不渲染，完整数据态由 focused helper 和构建覆盖。
- **边界**：
  - 本轮只改前端角色卷 JSX/CSS、结构检查脚本和文档，不新增后端 API，不改变 `dossier-reading` / `subjective-memory` 响应契约，不改 artifact。

### 2026-06-07 — Faction Pressure Arc

- **做了什么**：
  - `FactionVolumePage` 在“势力压力接力台”和长阅读布局之间新增“势力代偿弧线”。
  - 代偿弧线取最近四条 `consequence_state.ledger`，把来源事件、债务分数、承压领域、资源/秘密压力和 `next_round_hint` 整理成连续卡片。
  - 用户读势力卷时能从最近记录继续看见势力压力怎样逐步改写下一轮秩序，并可直接看完整代偿账或回沙盘验证。
  - 扩展 `check:faction-volume-ux`，锁定代偿弧线位置、真实字段引用、桌面四列和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:faction-volume-ux`，确认缺少 `factionPressureArcSignals` 时失败。
  - Focused helper：`pnpm.cmd run check:faction-volume-ux` -> `faction volume ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Repo：`git diff --check` 通过；仅有 Windows CRLF 提示。
  - In-app Browser smoke：`http://localhost:5181/#/world/my-story/worldlines/main/factions/%E8%8B%8D%E6%BE%9C%E6%B4%BE` 可打开势力卷，代偿弧线渲染 3 段 ledger、操作按钮可见、无控制台 error；390px 下弧线单列且无水平溢出。
- **边界**：
  - 本轮只改前端势力卷 JSX/CSS、结构检查脚本和文档，不新增后端 API，不改变 `dossier-reading` / `worldline-state` 响应契约，不改 artifact。

### 2026-06-07 — Event Misread Arc

- **做了什么**：
  - `EventPerspectivePage` 在“事件信息差接力台”和三栏事件阅读布局之间新增“事件误读弧线”。
  - 误读弧线从既有 `perspective_biases`、`information_gap` 和 `next_actions` 派生最近四条信号，把谁看错了、正史裂缝、偏差怎样发酵和下一步回收整理成连续卡片。
  - 用户读事件卷时能从信息差继续看见同一事件怎样分裂成不同角色的下一次判断，并可直接看全部误读或去长线卷回收。
  - 扩展 `check:event-perspective-ux`，锁定误读弧线位置、真实字段引用、桌面四列和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:event-perspective-ux`，确认缺少 `eventMisreadArcSignals` 时失败。
  - Focused helper：`pnpm.cmd run check:event-perspective-ux` -> `event perspective ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Repo：`git diff --check` 通过；仅有 Windows CRLF 提示。
  - In-app Browser smoke：`http://127.0.0.1:5184/#/world/my-story/worldlines/main/events/main/perspectives` 可打开事件卷，真实数据下误读弧线渲染 4 张卡片，操作按钮可见、无控制台 error；390px 下弧线单列且无水平溢出。
- **边界**：
  - 本轮只改前端事件多视角 JSX/CSS、结构检查脚本和文档，不新增后端 API，不改变 `event-perspective` 响应契约，不改 artifact。

### 2026-06-07 — World Volume Continuity Arc

- **做了什么**：
  - `WorldVolumePage` 在“正史/锚点接力台”和三栏阅读布局之间新增“世界卷承接弧线”。
  - 承接弧线复用既有 `continuous_reading`、`continuity_threads`、`consequence_state.ledger`、`next_round_hint`、相邻卷和 `evidence_panel`，整理出“卷内事实 / 相邻卷牵引 / 代偿落点 / 下一步回收”四张卡。
  - 用户读世界正史卷或主锚点卷时能理解这卷如何从事实、锚点压力和 ledger 代偿接回下一章，并可直接查卷内证据或去长线卷回收。
  - 扩展 `check:world-volume-ux`，锁定承接弧线位置、真实字段引用、桌面四列和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:world-volume-ux`，确认缺少 `worldVolumeContinuitySteps` 时失败。
  - Focused helper：`pnpm.cmd run check:world-volume-ux` -> `world volume ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - In-app Browser smoke：`http://127.0.0.1:5185/#/world/my-story/worldlines/main/chronicle` 桌面下渲染 4 步承接弧线且无控制台 error；`/anchors` 桌面下承接弧线可见，“去长线卷回收”能跳到 `#/world/my-story/worldlines/main/longline`；390px 下承接弧线单列且无水平溢出。
- **边界**：
  - 本轮只改前端世界卷 JSX/CSS、结构检查脚本和文档，不新增后端 API，不改变 `dossier-reading` 响应契约，不改 artifact。

### 2026-06-07 — Longline Entity Lanes

- **做了什么**：
  - `LonglineReadingPage` 在“跨章承接地图”和长线阅读状态区之间新增“角色与势力追踪带”。
  - 追踪带从既有 `timeline_entries.affected_characters`、`timeline_entries.affected_factions`、`misbelief_recovery.items` 和 `evidence_refs` 派生最多四张可点击追踪卡。
  - 用户读长线卷时可以按角色记忆或势力压力继续追“谁还带着后果往前走”，并一键把当前长线阅读焦点切到对应节点。
  - 扩展 `check:longline-reading-ux`，锁定追踪带语义、位置、真实字段引用、桌面四列和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:longline-reading-ux`，确认缺少 `buildLonglineEntityLanes` 时失败。
  - Focused helper：`pnpm.cmd run check:longline-reading-ux` -> `longline reading ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - In-app Browser smoke：`http://127.0.0.1:5186/#/world/my-story/worldlines/main/longline` 真实数据下渲染 2 张角色追踪卡，桌面四列网格、点击追踪焦点和无水平溢出均正常；390px 下追踪带单列、移动导览显示且无水平溢出；浏览器日志无应用错误。
- **边界**：
  - 本轮只改前端长线卷 JSX/CSS、结构检查脚本和文档，不新增后端 API，不改变 `longline-reading` 响应契约，不改 artifact。

### 2026-06-07 — Longline Entity Focus Panel

- **做了什么**：
  - `LonglineReadingPage` 的“角色与势力追踪带”新增选中态和“角色/势力追踪上下文台”。
  - 追踪卡现在不只跳到首个节点，还会展开该角色/势力线的摘要、沿线节点、牵连误会、证据读数和“继续追这个节点”动作。
  - 移动端追踪卡改为自然流式布局，并把主操作提前到标题后，避免按钮在 390px 视口里被卡到下边界。
  - 扩展 `check:longline-reading-ux`，锁定 `activeEntityLaneId`、`selectedEntityLane`、`focusEntityLane`、上下文台语义、桌面分栏和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:longline-reading-ux`，确认缺少 `LonglineEntityLaneEntry` / 追踪上下文台时失败。
  - Focused helper：`pnpm.cmd run check:longline-reading-ux` -> `longline reading ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - Repo：`git diff --check` 通过；仅有 Windows CRLF 提示。
  - In-app Browser smoke：`http://127.0.0.1:5187/#/world/my-story/worldlines/main/longline` 真实数据下桌面点击追踪卡会打开上下文台、卡片进入选中态、展示 5 个沿线节点和 5 条牵连误会；切到 390px 后追踪卡和上下文台均为单列且无水平溢出；浏览器 error/warning 日志为空。
- **边界**：
  - 本轮只改前端长线卷 JSX/CSS、结构检查脚本和文档，不新增后端 API，不改变 `longline-reading` 响应契约，不改 artifact。

### 2026-06-07 — Longline Misbelief Network

- **做了什么**：
  - `LonglineReadingPage` 在长线阅读状态区和“误会回收台”之间新增“跨章误会网络图”。
  - 网络图从既有 `misbelief_recovery.items` 派生最多六个可切换误会节点，默认选中待回收误会。
  - 选中详情把当前误会、误会来源、牵动角色、证据数量、回收步骤、回卷宗核对和送到作者台动作放在同一屏。
  - 用户读长线卷时能先理解一条误会怎样从来源事件拖到下一章，再决定回卷宗核对或送作者台。
  - 扩展 `check:longline-reading-ux`，锁定误会网络图的数据派生、选中态、位置、桌面三栏和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:longline-reading-ux`，确认缺少 `buildLonglineMisbeliefNetwork` 时失败。
  - Focused helper：`pnpm.cmd run check:longline-reading-ux` -> `longline reading ux structure ok`。
  - API smoke：`GET http://127.0.0.1:8765/api/stories/my-story/worldlines/main/longline-reading` -> 200。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - In-app Browser smoke：`http://127.0.0.1:5188/#/world/my-story/worldlines/main/longline` 真实数据下桌面渲染 5 个误会节点，网络图位于误会回收卡片之前，点击第二个节点会切换详情且无水平溢出；390px 下网络图和详情单列、移动导读显示、浏览器 error/warning 日志为空。
- **边界**：
  - 本轮只改前端长线卷 JSX/CSS、结构检查脚本和文档，不新增后端 API，不改变 `longline-reading` 响应契约，不改 artifact。

### 2026-06-07 — Author Adoption Recovery Queue

- **做了什么**：
  - `AuthorAdoptionPage` 在“下一章可写方案”之后、草稿输出之前新增“跨章回收清单”。
  - 清单从既有 `next_chapter_brief.conflict_focus`、`feed_forward.sandbox_continuation_inputs.major_event`、`feed_forward.next_round_reads`、`writing_plan.manual_review_points` 和草稿状态派生五类行动：冲突回收、下一轮事件、回读材料、人工复核、正文落点。
  - 用户写入采纳记录后，可直接跳回 brief、长线卷、世界沙盘、草稿或 Reviewer 质检门，先判断下一章必须回收什么，再生成/修订正文。
  - 扩展 `check:author-adoption-ux`，锁定清单的数据来源、位置、行动跳转、桌面四列和移动端单列。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:author-adoption-ux`，确认缺少 `chapterRecoveryQueue` 时失败。
  - Focused helper：`pnpm.cmd run check:author-adoption-ux` -> `author adoption ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - In-app Browser smoke：`http://localhost:5182/#/world/my-story/author` 真实提交后渲染 5 张跨章回收卡；同一结果缩到 390px 后卡片为单列 `290px`，`scrollWidth` 等于 `clientWidth`，无水平溢出；浏览器 error/warning 日志为空。
- **边界**：
  - 本轮只改前端作者采纳页 JSX/CSS、结构检查脚本和文档，不新增后端 API，不改变采纳、草稿、Reviewer、确认入卷或 artifact 契约。

### 2026-06-07 — WorldWorkspaceShell Mobile Drawer

- **做了什么**：
  - `WorldWorkspaceShell` 在桌面继续完整展开世界旅程总线、工作区总览、当前任务、状态预告、世界脉搏、体验轨道和卷宗速览。
  - 640px 以下把完整世界导航收进“展开世界导航”折叠区，让手机首屏先显示当前位置、当前任务、主动作和页面正文。
  - 折叠区展开后仍保留 4 个旅程入口、4 个体验阶段、4 个世界脉搏和 8 个卷宗入口，功能不减。
  - 扩展 `check:app-shell-mobile-layout`，锁定桌面完整导航、移动端默认折叠、任务条位于折叠导航之前，以及移动端抽屉展开后的入口完整性。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:app-shell-mobile-layout`，确认缺少移动端折叠导航时失败。
  - Focused helper：`pnpm.cmd run check:app-shell-mobile-layout` -> `AppShell mobile layout keeps world navigation compact and complete.`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - In-app Browser smoke：`http://localhost:5183/#/world/demo-world/author` 在 390px 下默认折叠世界导航，任务条在折叠区前，作者台标题进入首屏；点击“展开世界导航”后 4 个旅程入口、4 个阶段、4 个脉搏和 8 个卷宗入口均存在；无水平溢出，浏览器 error 日志为空。
- **边界**：
  - 本轮只改共享壳层组件、AppShell 样式、移动布局检查脚本和文档，不新增后端 API，不改变路由、阅读、作者采纳或 artifact 契约。

### 2026-06-07 — WorldWorkspaceShell Sandbox Runner Primary Action

- **做了什么**：
  - `worldRouteContext` 在沙盘路由下把共享壳层当前任务从“进入卷宗阅读”改为“启动一轮推演”。
  - 沙盘页主动作现在留在 `#/world/<slug>/sandbox`，并通过 `primaryTargetId="sandbox-runner"` 指向运行台；“进入卷宗阅读”降为次动作保留。
  - `WorldWorkspaceShell` 新增同路由锚点动作，支持普通 `scrollIntoView` 和 `.sandbox-page` 这类内部滚动容器。
  - `WorldSandboxPage` 的运行台暴露稳定 `id="sandbox-runner"`。
  - 扩展 `check:world-route-context`、`check:sandbox-runner-ux` 和 `check:app-shell-mobile-layout`，锁定沙盘页当前任务语义、运行台稳定锚点和内部滚动容器支持。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:world-route-context`，确认沙盘主路由仍指向卷宗阅读时失败。
  - RED：先运行 `pnpm.cmd run check:sandbox-runner-ux`，确认运行台缺少稳定 `id="sandbox-runner"` 时失败。
  - RED：先运行 `pnpm.cmd run check:app-shell-mobile-layout`，确认壳层不支持主动作锚点和内部滚动容器时失败。
  - Focused helpers：`pnpm.cmd run check:world-route-context`、`pnpm.cmd run check:sandbox-runner-ux`、`pnpm.cmd run check:app-shell-mobile-layout` 均通过。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - In-app Browser smoke：`http://localhost:5183/#/world/my-story/sandbox` 在 390px 干净标签页下，当前任务主按钮文案为“启动一轮推演”；点击后 URL 仍为沙盘路由，`.sandbox-page` 从 `scrollTop 0` 滚到 `130`，运行台与页面容器顶部距离约 `0.28px`；无水平溢出，浏览器 error 日志为空。
- **边界**：
  - 本轮只改前端路线语义、共享壳层滚动 helper、沙盘运行台锚点、结构检查脚本和文档；不新增后端 API，不改变 hash 路由契约，不改变 `POST /api/stories/<slug>/sandbox/run` 字段，不改 artifact。

### 2026-06-07 — WorldAnchorPage Continuation Deck

- **做了什么**：
  - `WorldAnchorPage` 新增“世界续行台”，把此刻世界、被推到台前、牵引伏笔和建议先做集中成四枚可扫读卡。
  - 续行台复用既有 `deriveWorldJourney`、本机 `recentReading`、`data.world.scene_description`、`data.divergence_point`、首个角色和首条开放伏笔，不新增后端字段。
  - 桌面左栏显示紧凑续行台，中心栏在世界苏醒台和世界卷宗总览之间显示完整续行台；移动端显示紧凑版并隐藏完整版本。
  - 三个动作分别执行推荐下一步、进入世界沙盘或读世界线；在工作台壳层中主动作会进入 `#/world/<slug>/tianming` 等世界内路由。
  - 扩展 `check:world-anchor-status-ribbon`，锁定续行台存在、桌面顺序、移动端紧凑版、字段来源、两列桌面布局和移动端单列布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:world-anchor-status-ribbon`，确认缺少世界续行台时失败。
  - Focused helper：`pnpm.cmd run check:world-anchor-status-ribbon` -> `world anchor status ribbon structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - 后端：`cd engine && python -X utf8 -m pytest -q` -> `951 passed`。
  - Repo：`git diff --check` 通过；仅有 Windows CRLF 提示。
  - In-app Browser smoke：`http://localhost:5183/#/anchor/my-story` 在 1280px 下紧凑续行台和完整续行台均渲染，完整续行台位于苏醒台与卷宗总览之间且无水平溢出；390px 下紧凑版显示、完整版本隐藏、无水平溢出，点击主按钮进入 `#/world/my-story/tianming`；浏览器 error 日志为空。
- **边界**：
  - 本轮只改前端锚定页 JSX/CSS、结构检查脚本和文档；不新增后端 API，不改变 `world-anchor` 响应契约，不改 artifact，不删除世界启动、世界苏醒台、世界卷宗总览、视觉资产、编辑锚定、角色栏或角色探针。

### 2026-06-07 — TianmingPage Next Round Brief

- **做了什么**：
  - `TianmingPage` 在确认后的“天命生效接力台”和详细天命面板之间新增“下一轮启动简报”。
  - 简报复用既有 `tianming.json` 字段，把下一轮会消费的主锚点、当前压力档、首个叙事吸引子和候选天命承载者整理成四枚可扫读卡。
  - 简报提供“启动世界沙盘 / 先投放干预 / 看锚点压力”三项动作，分别复用现有沙盘导航、干预编译滚动和锚点详情滚动。
  - 旧接力台中的同名“看锚点压力”按钮改为“查看锚点压力”，避免同屏重复 accessible name；既有锚点滚动功能保留。
  - 扩展 `check:tianming-mobile-guide`，锁定简报位置、真实字段来源、三项动作、桌面 summary/detail split 和移动端单列布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:tianming-mobile-guide`，确认缺少 `tianming-next-round-brief` 时失败。
  - Focused helper：`pnpm.cmd run check:tianming-mobile-guide` -> `tianming mobile guide structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - 后端：`cd engine && python -X utf8 -m pytest -q` -> `951 passed`。
  - In-app Browser smoke：`http://localhost:5183/#/world/my-story/tianming` 在 1280px 下简报位于接力台和详细面板之间，四张卡读取真实数据，点击“启动世界沙盘”进入 `#/world/my-story/sandbox`；390px 下简报和卡片均为单列，三个按钮等宽，无水平溢出，浏览器 error 日志为空。
- **边界**：
  - 本轮只改前端天命书 JSX/CSS、结构检查脚本和文档；不新增后端 API，不改变 `tianming.json`、干预编译、世界线代偿或沙盘 artifact 契约，不删除生成、确认、锚点、压力档、候选承载者、干预预编译或代偿面板。

### 2026-06-07 — WorldSandbox Event Seed Deck

- **做了什么**：
  - `WorldSandboxPage` 在运行台步骤之后、大事件输入之前新增“事件种子台”。
  - 事件种子台从当前锚点、`worldline_state.continuation_inputs.major_event_hint`、`consequence_state.next_round_hint`、代偿域、最近 ledger、后续剧情可能性和首条策略暗线派生三枚可扫读种子。
  - 用户点击“放入事件”会把对应种子写入 `majorEvent` 草稿，并显示“已放入运行台”反馈；下方读者干预草稿不被自动清空，仍由用户自己决定是否调整。
  - 扩展 `check:sandbox-runner-ux`，锁定事件种子台的位置、字段来源、回填 helper、反馈和移动端折叠样式。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:sandbox-runner-ux`，确认缺少 `sandbox-event-seeds` 时失败。
  - Focused helper：`pnpm.cmd run check:sandbox-runner-ux` -> `sandbox runner ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - 本轮工具面未暴露 in-app Browser 控制；未做桌面/移动真实截图 smoke，后续有浏览器工具时需补视口验收。
- **边界**：
  - 本轮只改前端沙盘页 JSX/CSS、结构检查脚本和文档；不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 请求字段，不改 `sandbox_rounds.jsonl`、`worldline_state.json` 或其它沙盘 artifact。

### 2026-06-07 — DossierReading Chapter Compass

- **做了什么**：
  - `DossierReadingPage` 在“续读签”之后、连续正文之前新增“本章读感罗盘”。
  - 罗盘从 `continuous_reading.reading_flow`、当前场景误会和 `chapter_cliffhanger` 派生“开场钩子 / 转折压力 / 误会燃料 / 下一章悬念”四枚阅读前信号。
  - 用户进入正文前可以先理解这一章为什么值得读、哪里会转折、误会怎样驱动下一轮，以及读完后接向哪里。
  - 罗盘提供“进入正文”和“看阅读节奏”动作，分别复用既有正文场景滚动和阅读节奏区块。
  - 扩展 `check:dossier-reading-ux`，锁定罗盘位置、真实字段来源、动作和移动端单列布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:dossier-reading-ux`，确认缺少 `dossier-reading-compass` 时失败。
  - Focused helper：`pnpm.cmd run check:dossier-reading-ux` -> `dossier reading ux structure ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
  - 后端：`cd engine && python -X utf8 -m pytest -q` -> `951 passed`。
  - Repo：`git diff --check` 通过；仅有 Windows CRLF 提示。
  - HTTP smoke：`http://localhost:5183/#/world/my-story/worldlines/root/reading` 返回 200。
  - 本轮工具面未暴露 in-app Browser 控制；未做桌面/移动真实截图 smoke，后续有浏览器工具时需补视口验收。
- **边界**：
  - 本轮只改前端卷宗阅读 JSX/CSS、结构检查脚本和文档；不新增后端 API，不改变 `dossier-reading` 响应契约，不改 artifact。

### 2026-06-07 — StoryEntry Route Chooser

- **做了什么**：
  - `StoryEntryPage` 的三张开卷入口卡新增“适合谁”和四段路径提示。
  - 内置样例标为“适合：我想先确认产品手感”，路径为“样例世界 -> 天命书 -> 沙盘轮次 -> 卷宗阅读”。
  - 导入小说标为“适合：我已有小说章节”，路径为“章节文本 -> 世界锚定 -> 天命书 -> 沙盘轮次”。
  - 主题创世标为“适合：我只有题材和冲突”，路径为“主题念头 -> 创世草案 -> 世界锚定 -> 天命书”。
  - 扩展 `check:story-shelf-focus`，锁定入口卡适用场景、路径文案、四段桌面布局和窄屏两列布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:story-shelf-focus`，确认缺少 `start-card__fit` / `start-card__route` 时失败。
  - Focused helper：`pnpm.cmd run check:story-shelf-focus` -> `story shelf focus helper ok`。
  - 完整验证结果见本轮收口。
- **边界**：
  - 本轮只改前端世界书架 JSX/CSS、结构检查脚本和文档；不新增后端 API，不改变导入、创世、样例、路由或 artifact，不删除既有世界沙盘、天命书、卷宗阅读、作者采纳台和机制档案入口。

### 2026-06-08 — WorldWorkspaceShell Focus Band

- **做了什么**：
  - `WorldWorkspaceShell` 把原本分散在工作区总览和当前任务条里的当前环节、承接世界线、建议先做、下一步理由、继续阅读、主动作和次动作合并成“世界扫读带”。
  - 扫读带前置到旅程总线、状态预告、世界脉搏、体验轨道和卷宗速览之前，让用户先判断“我在哪、现在为什么先做这一步、点哪里继续”。
  - 原“当前环节 / 承接世界线 / 下一步为什么做”工作区总览降级为“旅程入口 / 世界线档案 / 为什么建议这步”的轻量旅程指针，仍可点击回当前阶段、世界线档案或主动作。
  - 下方旅程总线、状态预告、世界脉搏、体验轨道、卷宗速览、全局续读、同路由锚点滚动和移动端“展开世界导航”全部保留。
  - 扩展 `check:app-shell-mobile-layout`，锁定扫读带必须在 dense 导航之前、桌面三列扫读结构、低噪声纸面对比和移动端保功能布局。
  - 同步 `memory.md`、世界沙盘 PRD、路线图、`engine/README.md`、`engine/ui/README.md` 和 handoff。
- **验证**：
  - RED：先运行 `pnpm.cmd run check:app-shell-mobile-layout`，确认缺少 `world-workspace-shell__focus-band`、扫读文案和三列结构时失败。
  - Focused helper：`pnpm.cmd run check:app-shell-mobile-layout` -> `AppShell mobile layout keeps world navigation compact and complete.`。
  - 路由语境：`pnpm.cmd run check:world-route-context` -> `world route context helper ok`。
  - 前端：`pnpm.cmd run build` 通过；保留既有 Vite 大 chunk 提醒。
- **边界**：
  - 本轮只改共享壳层组件、AppShell 样式、结构检查脚本和文档；不新增后端 API，不改变路由 hash、阅读进度、作者采纳、沙盘请求字段或任何 artifact。
