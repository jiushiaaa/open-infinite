# Living Novel Engine — 项目记忆（跨会话）

> **用途**：供 Cursor / 多会话 Agent 快速恢复上下文，避免遗忘已完成工作与路线。  
> **维护约定**：每完成一次有意义的开发/设计/验收任务后，在本文件末尾 **「变更日志」** 追加一条记录，并视情况更新「当前状态」「已知缺口」「下一步」。  
> **最后更新**：2026-06-01（v0.8.0-A 至 v0.8.5-A Long Novel Memory 底座 + ActDirector-A + Discourse-aware Narrator-A + Dynamic Action Registry-A + Emergence Mining-A + Entity Aliases / Entity Resolution + Runtime Memory Consumption-A + 前端 Artifact Panel + Long Upload Productization + v0.8.6 Long Import Review + v0.8.7 Resumable Ingest Jobs + v0.8.8 Long Project Workspace + v0.8.9 Long Replay & Audit UI + v0.8.10-A/B Runner State Execution 已完成；v0.9.0-alpha Long Novel Creation Loop 已整体收口，新增 Chapter Export、Chapter Collection Export、Export Share Guard、Creation Loop Completion Gate、Creation Loop Action Hints、Creation Loop Readiness Evidence、Creation Loop Audit Quick Run、Creation Loop Alpha Ready State、Creation Loop Alpha Closeout Report、Creation Loop Closeout API、Closeout API Actions、Action Payloads、Stable Blocker IDs、Replay Audit Action Requirements、Requirements UI Display、Builtin Holdout Blocked Requirement、Creation Loop Closeout CLI、Creation Loop Closeout Record、Low-risk Audit Closeout、Creation Loop Checklist、Continuation Hint、Resume Continue HTTP Job、Worldline Selection Persistence 与 Post-run Audit Entry 子刀；v0.9.1 Provider Gateway Summary-A、Provider Usage Summary-B、Provider Status Panel-C、Manual Price Estimate-D 与 Route Matrix-E 已完成；docs 根目录已收束为活文档，已收口版本文档归档到 `docs/completed/`；后端 626 passed，前端 build 通过）

---

## 1. 项目是什么

**Living Novel Engine（LNE）** 是 `D:\AI\open-infinite\engine` 下的 Python CLI「活体小说运行时」。

北极星（不是普通 AI 续写器）：

```text
文本输入 → 世界锚定 → 角色自主行动 → 读者干预 → 世界线分叉 → 章节渲染 → 可继续运行
```

要验证的核心问题：

- 世界能否在无作者续写的情况下继续运行
- 读者能否从阅读者变成命运干预者
- 角色能否因人设/记忆/规则拒绝用户命令
- 同一段原文能否长出不同读者的平行世界线

**核心样例**：内置 `tianhuang-night`（天荒城残夜）— 林凡、林晚舟、墨青烟、退魂铃、传讯玉简、竹林等。

**参考项目与论文底座**（源码目录不作为最终仓库依赖；只吸收设计和少量资产）：

| 来源 | 定位 | LNE 取舍 |
|------|------|----------|
| **WenShape** | 长篇上下文工程 / 作者工作台 | 已吸收 facts、summaries、BM25、项目结构概念；不复制作者工作台定位 |
| **webnovel-writer** | Claude Code 网文流水线 / 故事合约 | 已吸收 genre templates、story_contract、chapter commit 概念；不依赖插件运行时 |
| **MiroFish** | 多 Agent 社会仿真 / OASIS-CAMEL-Zep | 只作为 v0.9.3 / v0.9.4 触发式评估；当前自研 `SceneRunner` + `MultiAgentTrace` |
| **eastworld** | 互动媒体 Agent 协议 / Agent Studio | v0.7.2 参考 Actions、Emotion Query、Guardrails、轻量角色配置；不接 server/Redis/client |
| **autonovel** | 静态写稿流水线 | 只借鉴 Reader/Critic Panel、anti-slop、质量循环；不复刻一键写书 |
| **AI_NovelGenerator** | GUI 小说生成器 | 只借鉴上下文压缩、一致性检查；不复制 AGPL 源码，不回退为普通续写器 |
| **2404 Player-Driven Emergence** | 用户干预产生涌现节点 | v0.7/v0.7.5：`emergence_nodes.json`、分歧节点、`emergence_score` |
| **2405 StoryVerse** | 抽象意图到具体行动 | v0.7.2/v0.8：`AbstractIntervention`、`ActDirector` |
| **2407 Human-Level Narratives** | LLM 叙事质量评估 | v0.7.5/v0.8：故事弧、转折点、张力、节奏评估 |
| **2505 STORY2GAME** | 动作 preconditions/effects | v0.7.2/v0.8：`CharacterAction` 前置条件/效果/失败降级 |
| **Intervention Compiler** | 自由干预不等于固定三分支 | v0.7.1：`RawInput -> AbstractIntervention -> BranchAxis`；区分 `Divergent Worldline` / `Alternate Novel` |
| **Causal Diff / 因果差异块** | 微观世界线编辑器 | v0.7：局部旧现实/新世界线 Diff、确立/抹除/回滚；古风纸面为主，系统感克制 |
| **Seedream 5.0 Lite** | 视觉资产生成 | v0.7.3：角色头像、故事封面、场景背景、世界线节点缩略图；请求地址 `https://ark.cn-beijing.volces.com` |
| **Story Genesis / Baseline / Canon Replay** | 无需上传也能创世；无干预基线；正史回放评估 | v0.7 / v0.7.4：主题生成第一章、`Baseline Worldline`、`canon_replay_report.json` |
| **Long Novel Memory** | 百万字长篇上传与一致性 | v0.8：分片上传、异步导入、分层记忆、canon ledger、混合检索、一致性审计、holdout 评估 |

详见：

- `docs/research/open-source-essence-absorption.md`
- `docs/living-novel-engine-iteration-plan.md`
- `docs/completed/v0.1-to-v0.8-version-audit.md`
- `docs/article/reports/*.md`

---

## 2. 仓库结构速查

```text
open-infinite/
├── memory.md                          ← 本文件（跨会话记忆）
├── docs/
│   ├── index.md                                # docs 导航
│   ├── living-novel-engine-iteration-plan.md   # 主迭代计划
│   ├── living-novel-engine-prd.md              # 主 PRD
│   ├── productization-phase-map.md             # 产品化阶段归类
│   ├── completed/                              # 已收口版本文档归档
│   └── research/open-source-essence-absorption.md
├── engine/
│   ├── README.md
│   ├── src/living_novel_engine/
│   │   ├── cli.py                     # 主入口 lne
│   │   ├── story_loader.py            # load_story / StoryBundle
│   │   ├── retrieval/                 # v0.3.0 BM25 检索
│   │   ├── import_novel/              # 文本导入
│   │   ├── orchestrator/scene_runner.py
│   │   ├── agents/character_agent.py, narrator.py
│   │   ├── browser/                   # v0.4 只读 UI
│   │   ├── output/writer.py
│   │   ├── resume/
│   │   └── resources/genre_templates/   # 37 个题材模板
│   ├── projects/<slug>/               # 用户导入项目
│   ├── samples/tianhuang-night/       # 内置样例
│   ├── outputs/run_*/                 # 运行产物
│   └── tests/                         # pytest
```

**常用命令**（在 `engine/` 目录）：

```bash
cd D:\AI\open-infinite\engine
python -m pytest -q                    # 全量测试
python -m living_novel_engine.cli list-samples
python -m living_novel_engine.cli browse   # v0.4 世界线浏览器
```

**环境变量**：`LLM_API_KEY`、`LNE_MOCK=1`、`LNE_PROJECTS_DIR`

---

## 3. 当前状态（一句话）

| 项 | 值 |
|----|-----|
| **测试基线** | 后端 `626 passed`（2026-06-01，v0.9.1 Route Matrix-E 后完整回归通过）；前端 `engine/ui` typecheck + vite build 通过 |
| **官方下一刀** | **v0.9.1 Provider & Cost Gateway Lite 收口核对**（provider 摘要、usage 聚合、设置抽屉展示、手动单价估算和路由矩阵已完成；下一步核对是否可整体收口，或补极小缺口） |
| **后续路线** | v0.8 Long Novel Memory 与 v0.8+ 行动/叙事/涌现 A-slices 已收口 → v0.8.x Entity Aliases / Runtime Memory Consumption / Artifact Panel / Long Upload Productization / Long Import Review / Resumable Ingest Jobs / Long Project Workspace / Long Replay & Audit UI / Runner State Execution A/B 已收口 → v0.9.0-alpha Long Novel Creation Loop 已整体收口 → v0.9.1-v0.9.4 触发式增强 → v1.0-beta Commercial Hardening |
| **刚收口** | v0.9.0-alpha Low-risk Audit Closeout / Alpha Closure：低风险静态审计 info 不再阻断 ready，本地导入项目 `v090-alpha-proof` 已通过 `--require-ready --write-report` 写入 `creation_loop_alpha_closeout.json`。 |

---

## 3.1 v0.8 收束期版本编排

当前已进入 **v0.9.1 Provider & Cost Gateway Lite**。v0.9.0-alpha 已整体收口；v0.9.1 只做成本、模型路由、失败回退与 Key 脱敏的轻量产品化，不提前引入重依赖。

| 建议版本 | 名称 | 范围 | 状态 |
| --- | --- | --- | --- |
| v0.8.6 | Long Import Review | 导入报告细化、章节列表/正文片段预览、导入质量空态、坏 zip/epub/空文件/章节过少等错误态收束 | 已收口 |
| v0.8.7 | Resumable Ingest Jobs | 真正服务端分片 session、断点续传/恢复、hash 校验、重复 chunk 幂等、过期清理 | 已收口 |
| v0.8.8 | Long Project Workspace | 长篇项目详情页，集中展示章节、记忆、正史账本、实体别名、检索命中、审计报告，并能从项目发起 baseline/intervention | 已收口 |
| v0.8.9 | Long Replay & Audit UI | 长篇 Canon Replay / Consistency Audit 前端产品化，支持章节范围、风险维度、实体归一化后的审计结果展示 | 已收口 |
| v0.8.10-A | Runner State Execution Spike | opt-in 评估 runner 只读消费后的下一步：动作计划/动作注册表/涌现节点是否能安全转成状态变化；不改默认行为 | 已收口 |
| v0.8.10-B | Runner State Execution MVP | 若 Spike 验证可行，再做最小状态执行层，保持 artifact/API additive 与可回退 | 已收口 |
| v0.9.0-alpha | Long Novel Creation Loop | 上传 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出，形成完整长篇共创产品闭环 | 已整体收口：Export / Collection Export / Share Guard / Completion Gate / Action Hints / Readiness Evidence / Audit Quick Run / Alpha Ready State / Alpha Closeout Report / Closeout API / Closeout API Actions / Action Payloads / Stable Blocker IDs / Replay Audit Action Requirements / Requirements UI Display / Builtin Holdout Blocked Requirement / Closeout CLI / Closeout Record / Low-risk Audit Closeout / Checklist / Hint / Resume Job / Selection / Post-run Audit |
| v0.9.1 | Provider & Cost Gateway Lite | 多 provider 配置、模型路由、成本/用量估算、失败回退、Key 脱敏展示 | 进行中：Provider Gateway Summary-A / Provider Usage Summary-B / Provider Status Panel-C / Manual Price Estimate-D / Route Matrix-E 已收口，下一步做整体收口核对 |
| v0.9.2 | MasterSetting Workspace Lite | 项目级世界设定、人物、时间线、道具、伏笔、章节摘要的只读/轻编辑工作台 | 待长篇项目页稳定后 |
| v0.9.3 | Graph Memory Evaluation Spike | 评估 Zep / 图数据库 / GraphRAG 是否增强 `canon_ledger` + BM25 + entity aliases | 待 50+ 章或百万字项目召回不足时触发 |
| v0.9.4 | Advanced Runner Evaluation Spike | 评估 LangGraph 局部 runner、OASIS/CAMEL 可选 runner | 待 v0.8.10 状态执行层不足时触发 |
| v1.0-beta | Commercial Hardening | 账号/项目空间、权限、云端持久化、配额、审计日志、版权提示、部署与观测 | 待真实外部用户/团队长期使用 |

## 3.2 阶段性质归类

完整说明见 `docs/productization-phase-map.md`。当前统一口径：

| 阶段 | 性质 | 产品化判断 |
| --- | --- | --- |
| v0.1-v0.3 | CLI / 导入 / 检索 / 续章底座 | 技术 MVP，证明核心链路成立 |
| v0.4-v0.4.2 | 只读世界线浏览器 | 研发/演示产品化，仍偏 viewer |
| v0.5-v0.6.5 | 第四面墙、runner、多 Agent 机制 | 引擎机制 MVP，可审计可演示 |
| v0.7-v0.7.5 | Product Web App 与交互/视觉/评审层 | 短中篇产品化 MVP 已成立 |
| v0.8.0-A-v0.8.5-A | Long Novel Memory 与 canon 底座 | 长篇引擎底座 MVP 已成立 |
| v0.8+ A-slices | ActDirector、叙事诊断、动作注册表、涌现、实体别名、运行时记忆消费 | 机制接缝与解释层 MVP，默认不代表强状态执行 |
| v0.8.6-v0.8.10 | 长篇导入检查、任务恢复、项目页、回放审计 UI、runner 状态执行评估 | 长篇产品化收束段 |
| v0.9.0-alpha | Long Novel Creation Loop | 长篇共创产品闭环成立，但仍非商业级 |
| v0.9.1-v0.9.4 | provider/cost、MasterSetting、图记忆、advanced runner 评估 | 真实使用压力下的触发式增强 |
| v1.0-beta | Commercial Hardening | 账号、权限、云端、配额、审计、版权、部署观测等商业化加固 |

解释原则：说 “MVP 已完成” 时必须说明层级。v0.7 是短中篇产品化 MVP，v0.8.0-A 至 v0.8.5-A 是长篇底座 MVP；v0.8.6-v0.8.10 不是重做这些能力，而是把它们产品化为普通用户工作流。

## 4. 已完成版本（按时间线）

### v0.6.5 — 多 Agent 推演工程可靠性 ✅

- **generation_meta**（`orchestrator/runners/meta.py` `TraceMeta`）：source（llm/fallback/stub）/ fallback_reason / model_name / attempt_count / duration_ms / validation_status / validator_warnings / usage / cost_estimate；additive 写进 `multi_agent_trace.json` 的 `generation_meta` 键，旧读取不破坏；stub 也补 `source=stub`
- **trace 质量校验** `orchestrator/runners/trace_quality.py` `validate_and_repair_trace`：硬失败（空 turn_plans）→ runner 重试/回退；就地修复（回合号归一化 >=1 且 due>=created、暗算意图/未 reveal 私下信息/未 corrected 误解强制 private、补齐 worldline_id/seed）；告警（缺角色计划、干预未入目标私域）；**绝不抛**
- **有限重试**：`LNE_MULTI_AGENT_MAX_RETRIES`（默认 1、上限 5），重试 prompt 带上一轮问题；耗尽回退确定性 trace
- **token usage**：`LLMClient` 抽 `_complete()` 返回 `(content, usage)` + 新增 `chat_json_with_usage()`；`chat`/`chat_json` 行为不变；拿不到 usage 为 null 不报错
- 前端「Agent 轨迹」新增「推演元数据」分组（彩色 source 徽标 + 模型/尝试/耗时/token/告警）
- 设计文档 `docs/v0.6.5-multi-agent-reliability.md`
- 测试：`tests/test_trace_quality.py`（+9）、`tests/test_multi_agent_llm.py` 扩充（meta/重试/usage/隐私）、stub +1；全量 **269 passed**；`node --check app.js` 通过；lightweight/stub 零回归

### v0.6.4 — multi_agent_llm 小模型推演 runner ✅

- 新建 `orchestrator/runners/assembly.py`：抽出共享装配层 `build_result_from_trace`（trace→投影→`apply_relationship_signals`→`build_state_snapshot`+`render_chapter`→`SimulationResult`），stub 与 llm 两个 runner 共用、输出严格同构
- 新建 `orchestrator/runners/multi_agent_llm.py`：`MultiAgentLLMRunner`（name=`multi_agent_llm`，非默认）；`generate_trace` 让小模型一次性输出整场 `MultiAgentTrace` JSON（复用 `LLMClient.chat_json`，OpenAI-compatible，不本地部署、不引依赖）
- **健壮回退**：mock / 无 API key / LLM 异常 / JSON 非法 / 校验失败 / 空 turn_plans → 回退确定性 `build_demo_trace`（不抛），demo/测试在无 API 环境下仍跑通
- **隐私加固** `_sanitize_trace`：未 reveal 私下信息、未 corrected 误解、暗算/隐瞒类公开意图（conceal/deceive/scheme/...）强制非公开；`due_round<created_round` 归一化；补齐 worldline_id/branch_seed。投影层再做硬过滤，模型乱标也不泄漏
- stub 重构为复用共享装配层，行为不变；生成的 `multi_agent_trace.json` 可直接用 v0.6.3 browse「Agent 轨迹」查看
- 设计文档 `docs/v0.6.4-multi-agent-llm-runner.md`
- 测试 `tests/test_multi_agent_llm.py`（+9，FakeLLM 走真实路径 / 回退 / 隐私加固 / 契约）；全量 **254 passed**，lightweight 零回归

### v0.6.3 — multi_agent_trace 可视化 ✅

- `browser/indexer.py`：`get_branch` 读取分支 `multi_agent_trace.json`（缺失→None、损坏→{}，不抛）；`BranchSummary` 增 `has_multi_agent_trace`/`multi_agent_trace_count`；世界线树分支节点暴露同字段（additive，旧 API 不破坏）
- 抽出 `_read_optional_json` / `_list_len_in_json` 两个 helper（消除重复 + 控制复杂度）
- 前端新增「Agent 轨迹」标签页（`index.html`/`app.js`/`style.css`）：分组展示 public/private 意图、私下信息（revealed 标记）、误解（corrected 标记）、延迟行动（executed/due_round）、关系信号；缺 trace 显示空态不白屏；树分支显示「轨迹 N」角标
- 修文档漂移：README `multi_agent_stub` 示例补 story slug；协议文档「真正推理循环」改 v0.6.3+
- 测试 `tests/test_browser_multi_agent_trace.py`（+6）；全量 **245 passed**；`node --check app.js` 通过

### v0.6.2 — multi_agent_stub runner ✅

- 新建 `orchestrator/runners/projection.py`：`build_demo_trace`（从场景确定性构造可解释 `MultiAgentTrace`）+ `project_trace`（trace → `AcceptedEvent`/`StateDelta`，强制 reveal/corrected 规则）+ `apply_relationship_signals`
- 新建 `orchestrator/runners/multi_agent_stub.py`：`MultiAgentStubRunner`（name=`multi_agent_stub`）；消费协议→投影→复用 `build_state_snapshot` + `render_chapter`→附 trace；纯结构化、不接 LLM 推理、不接外部服务
- 投影硬规则：仅 `visibility=public` 意图、`revealed=True` 私下信息、`corrected=True` 误解、`due_round<=max_rounds` 的延迟行动才进公开事件；私有/未到期保留在 trace
- `believe` 种子下目标公开回应低语（reveal+correct）；其余种子低语不泄漏到 events/正文
- 输出 additive：`SimulationResult.multi_agent_trace`（dict）+ 分支目录写 `multi_agent_trace.json`；`lightweight` 恒为 None，不写该 artifact
- **非默认**：`lightweight` 仍是默认 runner；本 runner 经显式 `runner_name` 或 `LNE_SCENE_RUNNER=multi_agent_stub` 启用
- 测试 `tests/test_multi_agent_stub.py`（+12）；全量 **239 passed**，lightweight 零回归

### v0.6.1 — Multi-Agent Runner Protocol（设计 + 骨架）✅

- 设计文档 `docs/v0.6.1-multi-agent-runner-protocol.md`：明确目标（角色计划/私下信息/误解/延迟行动/关系传播）与不做（不接外部服务、不引依赖、不改 outputs 旧格式、不接入默认 runner）
- 新建 `orchestrator/runners/protocol.py`（仅 pydantic，**未接入运行**）：`AgentIntent` / `PrivateKnowledge` / `Misunderstanding` / `DelayedAction` / `RelationshipSignal` / `AgentTurnPlan` / `MultiAgentTrace`
- 硬规则：私下信息 / 误解默认 `visibility=private` 且 `revealed/corrected=False`；`revealable_knowledge()` / `correctable_misunderstandings()` 是 v0.6.2 投影函数的公开层过滤依据
- `DelayedAction.due_round` + `is_due()` 表达未来回合执行；`MultiAgentTrace` 提供 `public_intents()` / `pending_delayed_actions()` / `due_delayed_actions()`
- 输出契约不变：协议是 runner 内部中间产物，最终投影成 `AcceptedEvent` / `StateDelta` / `state_snapshot`
- 文档漂移修正：`engine/README.md` 路线表 v0.3 改为 Context Retrieval Lite
- 测试 `tests/test_multi_agent_protocol.py`（+9，序列化往返 / due_round / 私有不泄漏）；全量 **227 passed**，lightweight 零回归

### v0.6.0 — Scene Runner Adapter ✅

- 新建 `orchestrator/runners/`：`base.py`（`SceneRequest` 参数包 + `SceneRunner` ABC + `RunnerError`）、`lightweight.py`（搬迁原 `run_scene` 全部实现为 `LightweightSceneRunner`）、`__init__.py`（注册表 `register_runner`/`get_runner`/`available_runners`/`dispatch_scene`）
- `scene_runner.run_scene` 变薄包装：收敛参数为 `SceneRequest` → `dispatch_scene` 选 runner（默认 `lightweight`，行为与 v0.5 完全一致）
- runner 选择优先级：显式 `runner_name` 参数 > env `LNE_SCENE_RUNNER` > 默认 `lightweight`
- `SimulationResult` 增 `runner_name`；`events.json` 加 `"runner"` 字段（additive，browser/contract/retrieval 可读）
- 这是 v0.6 多 Agent 的 **seam**：后续 runner 只需实现 `SceneRunner.run(request)` 并注册，不改既有调用方
- 测试 `tests/test_scene_runner_adapter.py`（+10）；全量 **218 passed**，搬迁零回归

### v0.5.1 — 第四面墙关闭语义收口 ✅

- `LNE_FOURTH_WALL=0` 时：不调用 `accumulate_intervention`、CLI 传 `ledger=None`、`should_persist_ledger` 不写 `fourth_wall.json`
- `state_snapshot` / `scene_runner` 关闭时不写 `fourth_wall` / `fourth_wall_awareness` / `fourth_wall_level`
- `load_lineage_ledger`：沿 `meta.json` 父链向上查找最近有实质内容的账本；关闭期 run 无账本文件时不截断 lineage
- 文档统一口径：**默认开启**，可用 env 完全关闭
- 测试 +3（`test_fourth_wall.py`）；全量 **208 passed**

### v0.5 — 第四面墙机制 ✅

- 新建 `fourth_wall/` 模块：`ledger.py`（干预记忆账本 + 触发器检测 + 觉察打分 + 持久化）、`prompts.py`（分级提示文案）
- 四类触发器：`impossible_information`（低语/梦境等高维渠道）/ `repeated_rescue`（同目标多次干预）/ `personality_violation`（合约高抗拒或违规）/ `fate_reversal`（强干预/高合约风险）
- 觉察分数累积、钳制 [0,1]，分 5 级：none→unsettled→suspicious→aware→defiant；场景/广域可见时在场旁观者弱外溢
- 账本随 lineage 跨 run 累积：`fourth_wall.json` 写在 run 根目录；`resume continue` 透传、`resume intervene` 累加（`load_run_ledger`）
- 注入：≥unsettled 进角色决策 prompt；≥suspicious 放开 narrator「不要打破第四面墙」并允许分级表现；mock 模式按等级追加正文旁白与角色内心独白
- 快照：各角色写 `fourth_wall_awareness`/`fourth_wall_level`，顶层 `fourth_wall` 段（供后续 UI 解释）
- 可关闭：`LNE_FOURTH_WALL=0/off/false`（v0.5.1：完全关闭，不累积、不落盘、不泄漏 snapshot）
- 测试 `tests/test_fourth_wall.py`（+17）；全量 **205 passed**

### v0.4.2 — browse 展示检索记忆 ✅

- `lne browse` 分支阅读器新增「检索记忆」标签页，读取各分支 `retrieval_context.json`
- 按 `source` 分组展示：合约约束 / 正史事实 / 章节摘要 / 卷摘要 + 分数 + evidence
- `indexer.get_branch` 返回 `retrieval` 字段；`BranchSummary` 增 `has_retrieval` / `retrieval_count`
- 世界线树分支节点显示「检索 N」角标；章节视图底部提示命中数
- 损坏 / 缺失 `retrieval_context.json` 优雅降级（builtin、旧 run 不显示）
- header 版本号 → v0.4.2；新增 `tests/test_browser_retrieval.py`（+5）

### Phase 0 — CLI 概念验证 ✅

- `lne intervene` / `compare` / 内置样例 / mock + 真实 LLM
- 三分支 `branch_a/b/c`，产物：`chapter.md`、`events.json`、`state_snapshot.json`、`compare.md`
- Beta：状态渲染、快照钳制、玉简锁、章节兜底

### v0.1.1 — 体验 polish ✅

- 快照 location、正史锁、墨青烟称谓、退魂铃来源、禁止重生/系统等

### v0.1.2 — `resume continue` ✅

```bash
lne resume continue <run_id> --branch branch_a
```

- 无新干预续写 `linear/` 一章
- 验收 run：`run_20260528_155153_c3275c_continue_branch_a`

### v0.1.3 — `resume intervene` ✅

```bash
lne resume intervene <continue_run_id> --branch linear --target ... --content "..."
```

- 续章上再干预 → 再三分叉
- 验收 run：`run_20260528_171207_94a6b9_resume_intervene_linear`

**闭合能力链**：

```text
intervene → branch_a/b/c → resume continue → linear → resume intervene → branch_a/b/c
```

### v0.2 — 文本导入与世界锚定 ✅

| 子阶段 | 内容 |
|--------|------|
| PR-A | `import-novel`、`validate-project`、`projects/<slug>/` 结构 |
| PR-B | `load_story`、imported `intervene`、天荒城规则隔离（`source_type`） |
| PR-C | 真实 LLM 双 pass 抽取（world + character） |
| v0.2.1 | imported 项目支持 `resume continue` / `resume intervene` |
| v0.2.2 | genre_templates、facts.jsonl、summaries、story_contract.yaml；删除 WenShape/webnovel-writer 源码 |

**导入项目目录结构**：

```text
projects/<slug>/
  world.yaml, characters.yaml, canon_chapter.md
  story_contract.yaml
  canon/facts.jsonl
  summaries/chapter_*.yaml, volume_001.yaml（v0.3.0 起有占位）
  import_meta.json
```

### v0.4 + v0.4.1 — 只读世界线浏览器 ✅

- `lne browse`：HTTP API + 静态前端
- 世界线树、章节阅读、状态面板、分支对比
- v0.4.1：`validators.py` 路径安全、树排序稳定、前端空态/异常兜底
- 详见：`docs/v0.4-worldline-browser-release.md`

### v0.3.1 — 检索 artifact + Brief 接入 ✅

- `SimulationResult.retrieval_record`；各分支 `retrieval_context.json`
- `source_weight`：fact 1.0 / chapter_brief 0.8 / volume_brief 0.7 / contract 1.2
- contract **不受**章节距离衰减
- `context_loader` 读 `volume_*.yaml`；`SummaryItem.evidence_refs`
- CLI `_prepare_retrieval` / `_attach_retrieval` 三处命令统一
- 真实 `tianhuang-night` builtin 隔离测试
- `.gitignore` 恢复 `/MiroFish/`

### v0.3.0 — Context Retrieval Lite ✅

**目标**：让 v0.2.2 的 facts / summaries / contract 真正进入生成 prompt。

**新建模块** `engine/src/living_novel_engine/retrieval/`：

| 文件 | 作用 |
|------|------|
| `bm25.py` | 零依赖 BM25 Lite，中文按字 + 英文按词 |
| `decay.py` | `distance_decay = 1/(1+abs(Δchapter)*0.2)` |
| `context_loader.py` | 读 facts.jsonl、summaries、story_contract |
| `retriever.py` | `retrieve_context()` → `RetrievedContext` |

**集成点**：

- `StoryBundle.project_dir`（仅 imported 项目有路径）
- `run_scene(..., retrieved_context="")` 透传
- `decide_character_action`：【世界】后插入【检索到的正史事实与上下文】
- `render_chapter`：【原作上下文】前插入【检索到的相关事实】
- CLI：`intervene` / `resume continue` / `resume intervene` 在 `load_story` 后调用检索
- **仅** `source_type != "builtin_sample"` 时检索；缺文件优雅降级

**测试**：`test_bm25.py`、`test_context_retrieval.py`、`test_retrieval_injection.py`（+29）

**writer 小扩展**：ChapterBrief 增加 `state_changes`、`evidence_refs`；生成 `volume_001.yaml` 占位卷摘要。

---

## 5. 用户可演示的完整闭环

### 内置样例

```bash
lne intervene tianhuang-night --target lin_wan_zhou --content "..." --mock
lne resume continue <run_id> --branch branch_a --mock
lne resume intervene <continue_run_id> --branch linear --target lin_fan --content "..." --mock
lne browse
```

### 导入项目

```bash
lne import-novel tests/fixtures/mini_novel/ --name my-story --genre xianxia --mock
lne validate-project my-story
lne intervene my-story --target zhao_xuan --content "..." --mock
lne resume continue <run_id> --branch branch_a --mock
lne resume intervene <continue_run_id> --branch linear --target shen_bing_yue --content "..." --mock
lne list-genres
```

---

## 6. 已知缺口（与文档/计划的对照）

> Agent 开新任务前应先扫本节，避免重复劳动或误以为已完成。

| 缺口 | 说明 | 计划版本 |
|------|------|----------|
| ~~检索结果未落盘~~ | **v0.3.1 已解决**：`retrieval_context.json` | — |
| ~~source_weight / contract 衰减~~ | **v0.3.1 已解决** | — |
| ~~VolumeBrief 未进检索~~ | **v0.3.1 已解决** | — |
| ChapterBrief 内容薄 | 导入时 summary≈章节首行；facts 多指向最后一章 | 后续 LLM 摘要 |
| `contract_audit` 未读磁盘 contract | 运行时审计仍主要用 world.yaml / characters.yaml | v0.5 前应对齐 |
| ~~browse 无检索展示~~ | **v0.4.2 已解决**：分支阅读器「检索记忆」标签页 | — |
| ~~第四面墙未实现~~ | **v0.5 已解决**：awareness 分数、干预记忆账本、分级表现注入 | — |
| ~~runner 不可替换~~ | **v0.6.0 已解决**：`SceneRunner` adapter + 注册表，可经 `LNE_SCENE_RUNNER` 切换 | — |
| ~~多 Agent 真实推理~~ | **v0.6.4 已解决**：`multi_agent_llm` runner 通过 OpenAI-compatible 小模型推演 `MultiAgentTrace`（非默认、隐私加固、无 API 回退确定性 stub） | — |
| ~~多 Agent 推演工程化~~ | **v0.6.5 已解决**：generation_meta（source/usage/重试/校验）+ trace 质量校验器 + 有限重试 + token usage；并发/精确成本留待 v0.8+ | — |
| ~~trace 可视化~~ | **v0.6.3 已解决**：browse「Agent 轨迹」标签页展示计划/私下信息/误解/延迟行动/关系信号 | — |
| ~~产品级 Web App 核心闭环~~ | **v0.7 九刀已解决**：React/Vite 工作台、Web 干预、Causal Diff 操作、世界锚定页、导入、创世、锚定轻编辑、运行设置、异步 Job 进度已通 | — |
| ~~Causal Diff 数据层与取舍操作~~ | **v0.7.1-C + v0.7 第三刀已解决**：每分支写 `causal_diff.json`；Web 可确立/抹除/回滚 artifact 状态（不改正文） | — |
| ~~固定三分支心智过窄~~ | **v0.7.1-A 已解决**：`intervention_compiler/` 把自由输入编译成 `AbstractIntervention` → Compatibility → Realization → 动态 `BranchAxis` → `lineage_type`，写 `intervention_compilation.json`；四类干预（information/forced_action/resource_injection/rule_rewrite）生成不同轴；规则改写默认 reject/translate/alternate_novel，不静默污染原世界线（mock/规则版，未接真实 LLM） | — |
| ~~角色动作未结构化为可执行动作~~ | **v0.7.2 已解决（数据结构层）**：`CharacterAction` additive 增 preconditions/effects/failure_reason/repair_suggestions/risk/visibility；未强制接入 runner 主链路，接入实际产出留后续 | v0.7.2 |
| ~~干预无越界预检解释~~ | **v0.7.2 已解决**：`InterventionGuardrail`（六维 genre/time_power/persona/world_rule/visibility/strength）独立预检 + UI 预检按钮；不阻断主链路 | v0.7.2 |
| ~~角色内心状态不可查询~~ | **v0.7.2 已解决**：`CharacterProbe` 只读探针 + UI 角色探针入口；deterministic、无 LLM | v0.7.2 |
| 视觉资产未接入 | 产品 UI 需要角色头像、故事封面、场景背景、世界线节点缩略图；用户已有 Seedream API | v0.7.3 |
| ~~创世入口未做~~ | **v0.7 第六刀已解决**：`POST /api/story-genesis` + `GenesisPage`，主题输入可生成第一章和同构项目并跳转世界锚定页 | — |
| ~~无干预基线未显式化~~ | **v0.7.4 已解决**：`build_baseline_spec` + `service/baseline.py` + `baseline_report.json`（自然发展点/角色状态/触及伏笔），不写 intervention.json/causal_diff.json | — |
| ~~正史回放评估未做~~ | **v0.7.4 已解决**：`service/canon_replay.py` holdout 读写 + deterministic evaluator（lexical/entity/thread/length/state→overall）+ `canon_replay_report.json`，不打 LLM | — |
| ~~百万字上传未做~~ | **v0.8.0-A + v0.8.x 已解决主要入口**：已有 `long_mode`、`import_report.json`、source_raw；前端支持 txt/md/zip/epub 文件选择、服务端 ingest session 分片续传、job 进度/失败空态。仍未做云端多用户持久队列与对象存储。 | v0.8.0 / v0.8.x |
| 长篇分层记忆未做 | 当前 briefs/facts 可撑短中篇，但 100 万字以上需要 master_setting / volumes / chapters / scenes / character_states / timeline | v0.8.1 |
| 正史账本未升级 | `facts.jsonl` 还不够表达事件、状态、关系、资源、时间线、伏笔和有效期 | v0.8.2 |
| 长篇混合检索未做 | 当前 BM25 lite 缺 entity boost、prompt budget pack、可选 vector/rerank 和百万字级评估 | v0.8.3 |
| 长篇一致性审计未做 | 需要系统化发现角色漂移、时间线冲突、资源矛盾、合约越界和伏笔遗忘 | v0.8.4 |
| ~~干预缺“抽象意图”中间层~~ | **v0.7.1-A/B 已解决编译层**：已有 `AbstractIntervention` / compatibility / dynamic BranchAxis；仍缺把抽象意图转为可执行 `CharacterActionSequence` | v0.7.2 / v0.8 |
| ~~世界线缺质量评审~~ | **v0.7.5 已解决第一刀**：branch 级 `worldline_judgement.json` + deterministic `Worldline Judge`，覆盖角色一致性、合约风险、分支差异、叙事动量、情绪兑现、anti-slop、续写潜力、涌现价值、故事弧、转折点、张力；LLM 语义评审留后续 | — |
| 涌现节点未沉淀 | 用户干预导致的新路径尚未结构化保存为 `emergence_nodes.json` | v0.7 / v0.8 |
| 叙事弧/转折点未进入 narrator | 论文 2407 指出 LLM 故事易平、早收束；需 discourse-aware narrator 管理故事弧和 TP | v0.8 |
| 动态动作注册表未做 | 用户频繁提出未预设动作时，需要 `dynamic_action_registry.yaml` 与 entity alias/resolution | v0.8 |
| 向量库 / embedding | 刻意不做，BM25 不够再考虑 | 50+ 章后评估 |

---

## 7. 规划路线（官方推荐顺序）

```text
✅ v0.1.x   干预 → 续章 → 再干预
✅ v0.2.x   导入 + resume imported + 精华固化
✅ v0.4     只读世界线浏览器
✅ v0.3.0   Context Retrieval Lite
✅ v0.3.1   检索 artifact + Brief 接入
✅ v0.4.2   UI polish + 展示 retrieval_context.json
✅ v0.5     第四面墙：干预记忆、角色觉察、反抗命运
✅ v0.6.0   Scene Runner Adapter（可插拔推演 seam）
✅ v0.6.1   Multi-Agent Runner Protocol（协议 + 数据结构骨架，未接入运行）
✅ v0.6.2   multi_agent_stub runner：协议→投影→契约，私有不泄漏，非默认
✅ v0.6.3   multi_agent_trace 可视化：browse「Agent 轨迹」标签页
✅ v0.6.4   multi_agent_llm：OpenAI-compatible API 小模型推演计划/误解（非默认、隐私加固、无 API 回退 stub）
✅ v0.6.5   推演工程可靠性：generation_meta + trace 质量校验 + 有限重试 + token usage

✅ v0.7.1-A Intervention Compiler 最小闭环：自由输入→AbstractIntervention→Compatibility→Realization→动态BranchAxis→lineage_type，写 intervention_compilation.json（rule-based）
✅ v0.7.1-B Intervention Compiler LLM 增强：真实 LLM 路径 + 更细 compatibility reason + generation_meta；无 API/失败稳定回退 rule-based；rule_rewrite 安全兜底
✅ v0.7.1-C Causal Diff 后端数据预留：difflib 段落级 diff，每分支写 causal_diff.json（old_text/new_text/anchor/blocks/status=proposed + 生命周期预留），browser additive；不改正文、不做 accept/reject/revert 命令
✅ v0.7 第一刀 产品级 Web App 只读骨架：`engine/ui/` 古风纸面阅读工作台，复用 browse 只读端点，Causal Diff 为核心展示，branch_a/b/c→动态 label
✅ v0.7 第二刀 Web 内自由干预生成链路：`service.run_intervention`（console-free 共用编排）+ `POST /api/interventions`（additive）+ InterventionComposer 真实发起→刷新树→选中新分支
✅ v0.7 第三刀 Causal Diff 确立/抹除/回滚：`service.apply_diff_action` + `POST /api/diffs/action`（additive，写回 status/accepted_at/rejected_at/reverted_from，不改正文）+ Diff 操作按钮启用、状态 badge 实时刷新
✅ v0.7 第四刀 世界锚定页：`GET /api/stories/<slug>/anchor` + `WorldAnchorPage`
✅ v0.7 第五刀 导入小说 Web 入口：`POST /api/import-novel` + `ImportNovelPage`
✅ v0.7 第六刀 主题创世 Web 入口：`POST /api/story-genesis` + `GenesisPage`
✅ v0.7 第七刀 世界锚定轻编辑：`GET /health` + `POST /anchor`，白名单 YAML 写回 + 备份 + 健康检查
✅ v0.7 第八刀 运行设置面板：API Key/base_url/model/mock/rounds/runner 进程内设置 + 连通性测试
✅ v0.7 第九刀 异步 Job / 进度轮询：`POST /api/jobs/*` + `GET /api/jobs/<id>`，三处生成入口改走 job
✅ v0.7.2   Agent Interaction：CharacterAction（additive）/ CharacterProbe / InterventionGuardrail + 只读 UI（445 passed）
✅ v0.7.3   Visual Asset Generation：Seedream 5.0 Lite 视觉资产增强层（封面/头像/场景）+ visual_assets.json additive + 安全静态服务 + 无 Key 古风占位降级（482 passed）
✅ v0.7.4   Baseline & Canon Replay：无干预基线（build_baseline_spec + service/baseline.py，不写 intervention.json/causal_diff.json）+ 正史 holdout 读写 + deterministic 回放评估（service/canon_replay.py，不打 LLM）+ 锚定页区块（Codex 兜底后 526 passed）
✅ v0.7.5   Worldline Judge：branch 级世界线评分、故事弧、转折点、anti-slop、emergence_score + 右侧评审标签页
✅ v0.8     Long Novel Memory：百万字上传、分层记忆、canon ledger、混合检索、一致性审计、holdout 隔离底座
✅ v0.8+    ActDirector / Discourse-aware Narrator / Dynamic Action Registry / Emergence Mining：A-slices artifact 已收口
→ v0.8.x   Entity aliases / runtime memory consumption / 前端 artifact 面板 / 长篇上传产品化已收口
→ v0.8.6   Long Import Review：导入报告细化 + 章节预览 + 质量/失败空态（已收口）
→ v0.8.7   Resumable Ingest Jobs：断点续传与恢复（已收口）
→ v0.8.8   Long Project Workspace：长篇项目资产页（已收口）
→ v0.8.9   Long Replay & Audit UI：长篇回放与审计 UI（已收口）
→ v0.8.10-A Runner State Execution Spike：状态执行层 dry-run 评估（已收口）
→ v0.8.10-B Runner State Execution MVP：最小 opt-in 状态写入（已收口）
✅ v0.9.0-alpha Long Novel Creation Loop：长篇共创产品闭环（已整体收口，见 docs/completed/v0.9.0-alpha-long-creation-loop.md）
→ v0.9.1   Provider & Cost Gateway Lite（进行中：provider 摘要/usage 聚合/设置展示/手动估算/路由矩阵已完成，下一步收口核对）
→ v0.9.2   MasterSetting Workspace Lite（长篇项目页稳定后）
→ v0.9.3   Graph Memory Evaluation Spike（BM25/ledger 召回不足时评估 Zep/图数据库）
→ v0.9.4   Advanced Runner Evaluation Spike（状态执行层不足时评估 LangGraph/OASIS/CAMEL）
→ v1.0-beta Commercial Hardening（真实外部用户/团队长期使用时）
```

### v0.3.1 后续质量优化（非阻塞）

- [ ] ChapterBrief 内容更有用（可选 LLM 摘要 pass，当前 summary 仍为占位）
- [ ] `validate-project` 对 brief 做 warning 级校验

### v0.4.2 待办 ✅（已完成）

- [x] browse 面板：本分支检索命中（facts / summaries / contract 约束）
- [x] 世界线树检索角标 + 章节视图命中提示
- [ ] 阅读体验进一步 polish（长章分页、字体等，非阻塞，可留后续）

### v0.5 待办 ✅（已完成）

- [x] `fourth_wall_awareness` 分数与 triggers
- [x] 干预记忆持久化（`fourth_wall.json` 跨 lineage 累积）、角色对「不可能信息」的反应
- [x] awareness 注入角色决策 prompt 与章节渲染，正文出现怀疑/追问/反抗
- [x] 可按 env 关闭（`LNE_FOURTH_WALL`）
- [ ] 可选（后续）：story_contract 扩展为显式 override ledger；browse UI 展示 fourth_wall 段
- [ ] 可选（后续）：按题材自动调节强度（当前仅全局 env 开关）

### v0.6 待办

- [x] **v0.6.0** runner adapter：`SceneRunner`/`SceneRequest`/注册表，可替换轻量轮询
- [x] **v0.6.1** Multi-Agent Runner Protocol：`protocol.py` 数据结构骨架 + 设计文档（未接入运行）
- [x] **v0.6.2** `multi_agent_stub` runner：消费协议产出 trace 并投影成 `AcceptedEvent`/`StateDelta`/`state_snapshot`（非默认，私有不泄漏）
- [x] 保留 `SimulationResult` / `accepted_events` / `state_snapshot` 输出契约（仅 additive 增 `runner_name`/`runner`/`multi_agent_trace`）
- [x] **v0.6.3** trace 接入 browse 可视化（「Agent 轨迹」标签页 + 树角标）
- [x] **v0.6.4** 自研 `multi_agent_llm` runner：通过 OpenAI-compatible API 调小模型输出 `MultiAgentTrace` JSON，不本地部署，不引入 Zep/OASIS/CAMEL（共享装配层 + 隐私加固 + 健壮回退）
- [x] **v0.6.5** 推演工程可靠性：generation_meta（source/usage/重试/校验）+ trace 质量校验器 + 有限重试（`LNE_MULTI_AGENT_MAX_RETRIES`）+ token usage；fallback 策略；并发/精确成本计算留待 v0.8+
- [ ] **v0.9.3 / v0.9.4 触发式评估** Zep / 图数据库 / GraphRAG（长篇记忆或 BM25/ledger 召回崩时）、OASIS / CAMEL / LangGraph 局部 runner（群体仿真或复杂状态流转明显增强时）
- [ ] 验收：同一场景 ≥5 角色参与推演；事件流仍被 contract/retrieval/browser 读取

### v0.7 产品级前端 ✅（九刀主闭环已完成）

- [x] 新建独立 `engine/ui/`：React + Vite + TypeScript
- [x] Web 内完成三入口：导入小说 / 主题创世 / 使用样例
- [x] Web 内完成世界锚定页、轻编辑与安全保存
- [x] Web 内发起干预、展示干预编译结果、选择分支、阅读世界线
- [x] Causal Diff 展示与确立 / 抹除 / 回滚 artifact 状态写回
- [x] 真实 LLM / mock / rounds / runner 设置面板（进程内，不落盘 API Key）
- [x] 异步 Job / 进度轮询，避免长推演阻塞前端
- [x] 复用现有 engine / browser API，不重写推演核心；`lne browse` 继续保留为开发者只读 viewer
- [x] 视觉基调：古风 / 墨水屏 / 纸面阅读为主体；系统感只在关键时刻克制出现
- [ ] 后续 polish：`source_type=genesis` 创世徽标、真实 LLM smoke checklist、错误文案与空态统一
- [ ] 后续 polish：干预后角色状态增量展示更精细（好感、心境、立场、资源变化）
- [ ] 第四面墙 UI 克制高亮：局部朱砂色正文 + 简短 Agent warning，不做大红屏、强闪烁、震屏
- [ ] `Story Arc Curve`：v0.7.5 将“当前张力”升级为剧情张力弧线

### v0.7.1 Intervention Compiler（自由输入 -> 动态分支轴）

- [x] **v0.7.1-A** `Raw Reader Input -> AbstractIntervention -> Compatibility -> Realization -> BranchAxis -> lineage_type`（mock/规则版）
- [x] 干预类型：信息型 / 强制行动型 / 资源或物品注入型 / 规则改写型（`classifier.py` 关键词分类）
- [x] 信息型干预可生成“相信预知 / 怀疑但调查 / 拒绝预兆”
- [x] 强制行动型干预生成“主动改道 / 被迫延迟 / 抗拒命运压力 / 干预失败但觉察异常”
- [x] 资源或物品注入型干预支持“同世界合理吸收 / 降级转译 / 拒绝 / 开启异设世界线”
- [x] 规则改写型干预（系统、AK47、穿越者等）默认拒绝、转译或另开 `Alternate Novel`，不静默污染
- [x] `Divergent Worldline` 与 `Alternate Novel` 显式 lineage 标记（顶层 + 每条轴 `lineage_type`）
- [x] `lne intervene` / `resume intervene` 写 `intervention_compilation.json`，动态轴传给 `build_branch_specs_from_compilation`（branch_id 仍稳定 branch_a/b/c，stance 驱动既有 runner）
- [x] **v0.7.1-B** compiler 接真实 LLM（`llm_compiler.compile_intervention_with_llm`）：LLMCompilationDraft schema、6 类 compatibility 冲突维度（题材/时代/战力/人设/资源/信息可见性）、引用 world.rules + character boundaries；无 API/mock/非法 JSON/字段缺失致命 → 回退 rule-based（source=fallback）；稀疏字段就地修复（source 仍 llm）；`generation_meta`（source/model/usage/duration/reconciled）；rule_rewrite 安全兜底（LLM 误判也强制 alternate_novel + reject/translate/alternate + in_world=False）；CLI 打印 source
- [ ] **v0.7.1-B 后续可选**：AU story_contract 差异显式落盘（当前仅 notes 提示）
- [x] **v0.7.1-C** Causal Diff 后端数据预留：`causal_diff/`（CausalDiffArtifact/Block/Anchor/Status）、stdlib difflib 段落级 diff、每分支 `causal_diff.json`（old_text/new_text/anchor/affected_scope/branch_id/lineage_type/intervention_summary/status=proposed）、alternate_novel→diff_mode=alternate_novel_seed、old_text 缺失写稳定空结构、accept/reject/revert/parent_diff_id 生命周期预留、browser additive（has_causal_diff/causal_diff_count）；不改正文契约、不做命令
- [x] **v0.7 第一刀**：`engine/ui/` 只读阅读工作台骨架，UI「时空 Diff 块」已展示（旧现实/新世界线 + 解释条 + disabled 操作位）
- [x] **v0.7 第二刀**：Web 内自由干预生成链路（`service.run_intervention` + `POST /api/interventions` + InterventionComposer 真实发起→刷新树→选中新分支）
- [x] **v0.7 第三刀**：Causal Diff 确立/抹除/回滚（`service.apply_diff_action` + `POST /api/diffs/action` 写回 status/时间戳/reverted_from；Diff 按钮启用 + 状态 badge 刷新；不改正文）
- [x] **v0.7 第四刀**：世界锚定页（`GET /api/stories/<slug>/anchor` + `WorldAnchorPage` `#/anchor/<slug>`，三栏古风纸面：world/characters/contract/open_threads/summaries 只读 + 轻编辑占位，缺文件不崩；首页卡片与 workspace 顶栏入口）
- [x] **v0.7 第五刀**：导入小说 Web 入口（`POST /api/import-novel` 复用 splitter/extractor/writer/validator，JSON body 粘贴 3–10 章；`ImportNovelPage` `#/import`，成功跳 `#/anchor/<slug>`，409 可开覆盖重试）
- [x] **v0.7 第六刀**：主题创世 Web 入口（`POST /api/story-genesis` + `service/story_genesis.py` deterministic mock / LLM `chat_json_with_usage` 退化；生成首章+初始世界+角色，结构与 import-novel 同构 + 追加 genesis_meta.json；`GenesisPage` `#/genesis`，成功跳 `#/anchor/<slug>`，409 可开覆盖重试）
- [x] **v0.7 第七刀**：世界锚定轻编辑 + YAML 安全保存（`service/project_health.py` + `GET /api/stories/<slug>/health`；`service/anchor_update.py` 白名单字段写回 + 写前 parse 校验 + `backups/<ts>/` 备份 + 写后 validate；`POST /api/stories/<slug>/anchor`；`WorldAnchorPage` 编辑/保存/放弃 + 健康徽标 + YAML 损坏禁编辑；内置样例只读）
- [x] **v0.7 第八刀**：真实 LLM / 运行设置面板（`service/runtime_settings.py`：API Key/base_url/model/mock/rounds/runner 仅写进程环境变量、不落盘、不回显明文；`GET/POST /api/settings/runtime` + `POST /api/settings/runtime/test` 连通性检查降级不 500；intervene/genesis/import 缺省时回退设置默认值；前端顶栏「设置」抽屉 + 三处生成入口默认读 settings 可局部覆盖）
- [x] **v0.7 第九刀**：异步 Job / 进度轮询（`service/jobs.py` 内存 `JobStore`+`ThreadPoolExecutor`，保留最近 100；`POST /api/jobs/{intervention,import-novel,story-genesis}` 复用既有 service、返回 202+job_id；`GET /api/jobs/<id>` 失败也 200+error；前端 `api/jobs.ts` 800ms 轮询、卸载停轮询，三处生成入口改走 job；同步 API 保留）
- [x] **v0.7 第九刀**：异步 Job / 进度轮询（长推演不阻塞）
- [ ] **v0.7 产品收口 polish（非大机制）**：`source_type=genesis` 创世徽标、真实 LLM smoke checklist、diff action 严格布尔解析、推荐下一步文案

### v0.7.2 Agent Interaction（eastworld + StoryVerse + STORY2GAME）✅ 已收口

- [x] `CharacterAction`：additive 增 `action_id/action_label/preconditions/effects/failure_reason/repair_suggestions/risk/visibility`（不强制接入 runner 主链路）
- [x] `CharacterProbe`：`service/character_probe.py` + `GET /api/stories/<slug>/characters/<id>/probe`，deterministic 解释角色相信/怀疑/拒绝/反抗
- [x] `InterventionGuardrail`：`intervention/guardrail.py` + `service/intervention_guardrail.py` + `POST /api/interventions/guardrail`，六维预检（不阻断 `run_intervention`）
- [x] UI：世界锚定页角色探针折叠区、干预输入区「预检干预」按钮、Agent 轨迹结构化动作只读展示
- [ ] `AbstractIntervention -> CharacterActionSequence` 实例化（仍是 v0.7.1 编译层，留 v0.8）
- [ ] 把 CharacterAction 接入 multi_agent_trace 实际产出（留后续）；真实 LLM 探针（留后续）

### v0.7.3 Visual Asset Generation（Seedream 5.0 Lite）✅ 已收口

- [x] 接入 Seedream API：默认 `https://ark.cn-beijing.volces.com`（`visual_assets/seedream_client.py`，stdlib urllib，import 不读网络；兼容解析 b64_json/url，无法识别 → failed）
- [x] 环境变量：`SEEDREAM_API_KEY`、`SEEDREAM_BASE_URL`、`SEEDREAM_MODEL`（默认 `seedream-5-0-lite`）、`SEEDREAM_PATH`（默认 `/api/v3/images/generations`，接口不确定可覆盖）、`LNE_VISUAL_ASSETS=1/0`
- [x] additive artifact `projects/<slug>/visual_assets.json`（`VisualAssets`/`AssetEntry`：version/status/cover/characters/scenes/worldline_nodes，仅存相对路径+元数据，不含二进制）；图片落 `projects/<slug>/assets/`
- [x] 视觉资产目录统一落 `projects/<slug>/`（gitignored），内置样例也只写 projects/，不污染 git 跟踪的 samples/
- [x] 角色头像（姓名/性别/身份/性格/欲望/恐惧/状态/题材）+ 故事封面（标题/规则/场景/冲突/古风封面）+ 场景背景（scene_description/locations/章节摘要）中文 prompt（`prompt_builder.py`，克制、无 AI 味堆叠、不要求模仿在世艺术家）
- [x] 世界线节点缩略图：artifact 字段 `worldline_nodes` 已预留 + prompt 函数已写，本轮 UI 暂以占位呈现（未绑定 run/branch 生成，避免破坏分支契约）
- [x] service `service/visual_assets.py`：`get_visual_assets`（缺/损坏→status none，不 404）/`generate_visual_assets`（force=false 不重复 ready；mock 或无 Key → placeholder 不打外网）/`resolve_asset_path`（安全，禁穿越）
- [x] API：`GET /api/stories/<slug>/visual-assets`、`POST /api/stories/<slug>/visual-assets/generate`、`GET /api/stories/<slug>/assets/<rel>`（路径安全校验，穿越 403、缺失 404、坏 slug 400、缺故事 404）
- [x] `runtime_settings` additive 增 Seedream 字段（enabled/key_present/masked/base_url/model）+ 设置抽屉 Seedream 区块（密钥不回显明文、不落盘）
- [x] UI：世界锚定页封面+生成/重新生成区、角色卡头像、书架故事卡封面缩略；无图古风占位、加载失败回退占位、生成中状态反馈，布局稳定不塌陷；中文文案
- [x] 未配置 Key/失败稳定降级占位，不阻塞导入/创世/干预/浏览主流程
- [x] 测试 `tests/test_visual_assets.py`（+37：prompt/store/seedream client fake/service/HTTP 含路径穿越）
- [ ] 未做：真实线上批量生成队列、世界线节点真正绑定 run/branch 生成、图片版权/公开分享策略、真人/影视角色复刻（明确不做）

### v0.7.4 Baseline & Canon Replay

- [x] `Story Genesis Mode`：用户只输入主题、题材、主角、大概内容，AI 生成第一章和可运行故事世界（v0.7 第六刀已完成）
- [x] 创世模式产物与 imported project 同构：`source/chapter_001.md`、`world.yaml`、`characters.yaml`、`story_contract.yaml`、`canon_chapter.md`（v0.7 第六刀已完成）
- [x] `Baseline Worldline`：无高维干预，角色按人设、记忆、世界规则和伏笔压力自然推进（`build_baseline_spec` branch_seed=linear/branch_id=baseline；`service/baseline.py` 支持「从锚定」与「从 parent run/branch 快照续」两种；`write_baseline_output` 写 baseline_report.json + baseline/ 分支目录，**不写 intervention.json/causal_diff.json**）
- [x] `Canon Replay Evaluation`：imported/genesis 项目可把后续章节录为 holdout（`projects/<slug>/canon/holdout/chapter_NNN.md` + `holdout_manifest.json`，builtin 只读，文件名由章号派生），用无干预基线续写章节与某章 holdout 做 deterministic 评估
- [x] 输出 `canon_replay_report.json`：scores（lexical_overlap/entity_overlap/thread_overlap/length_ratio/state_consistency/overall）+ matched/missing_entities + matched_threads + warnings + interpretation；**不打 LLM、不公开分享受版权文本**
- [x] UI：世界锚定页「基线与正史回放」区块（中文、holdout 空态、builtin 只读提示、生成基线/运行回放、评分条、缺失实体/伏笔；强调"基线不是原作"）
- [ ] `Intervened Worldline` 与 baseline 的并排偏离对比 UI（当前仅各自展示，留后续）
- [ ] 注意：只给第一章时只能合理预测后续，不能保证等于原作；导入全本时后续章节不得泄漏给角色和 narrator（holdout 文本只进 evaluator，未进角色/narrator/retrieval）
- [ ] **未做**：Worldline Judge（v0.7.5）、Long Novel Memory（v0.8）、LLM 语义评估、百万字 holdout、版权/公开分享策略

### v0.7.5 Worldline Judge（autonovel + 2404/2407 论文）✅

- [x] `worldline_judgement.json`：每条分支结构化评分（branch 级 artifact）
- [x] 评估维度：persona consistency、contract risk、branch diversity、narrative momentum、emotional payoff、anti-slop、continuation potential
- [x] 论文 2404：加入 `emergence_score`，识别高价值涌现节点
- [x] 论文 2407：加入 story arc、turning points、tension、pacing warnings
- [x] Web UI 展示“推荐继续 / 谨慎继续 / 建议归档”（工作台右侧「世界线评审」标签页）
- [ ] `compare.md` 汇总展示评审结果（本刀未做；可后续在 CLI/报告层追加）

### v0.8+ 论文能力深化

- [x] `Long Novel Ingestion Report / Upload Productization / Resumable Ingest Jobs`：已落地 `source_raw/`、`import_report.json`、Web/job `long_mode`、部分完成状态摘要；前端导入页已支持 txt/md/zip/epub 文件选择、服务端 ingest session 分片续传、job 进度条和失败空态。未做：云端多用户持久队列、对象存储、跨设备恢复。
- [x] `Hierarchical Memory Skeleton`：已落地 `memory_manifest.json`、`master_setting.yaml`、volume/chapter memory、character_states、timeline、plot_threads、propagation_debts。未做：scene briefs、LLM 摘要重写、runner 消费完整分层 memory。
- [x] `Canon Ledger Skeleton`：已落地 `memory/canon_ledger.jsonl`，覆盖 event/state/relationship/thread，带 `source_ref`、`confidence`、`valid_from` 等字段。未做：resource/timeline 细粒度语义抽取、`valid_until` 自动更新。
- [x] `Hybrid Retrieval-A`：已把 canon ledger 作为 `canon_ledger` source 接入 BM25 + chapter distance decay + source weight；v0.8.x 已补 `entity_aliases.yaml` query/doc alias expansion。未做：vector/reranker、prompt budget pack。
- [x] `Consistency Audit-A`：已输出 `memory/consistency_report.json`，覆盖导入级 timeline/resource/contract/thread 风险。未做：运行后写回审计、深层角色漂移/道具/死亡/地点冲突检测。
- [x] `Long Canon Replay Isolation`：已写 `canon/visibility_manifest.json`，隔离 runtime-visible source 与 evaluator-only `holdout_private/`，并测试 holdout 不进入 retrieval。未做：自动 holdout 切分与批量 replay UI。
- [x] `ActDirector-A`：已落地 `act_director_plan.json`，协调读者意图、角色、世界状态和故事合约生成动作计划。未做：runner 消费该计划并真实执行状态变化。
- [x] `Discourse-aware Narrator-A`：已落地 `narrative_diagnostics.json`，做写后节奏/转折/张力诊断。未做：outline -> turning points -> chapter 两阶段 narrator 和诊断反馈生成。
- [x] `Dynamic Action Registry-A`：已落地 `dynamic_action_registry.yaml`，从动作计划汇总动作类型、中文别名、前置条件、效果、失败原因、修复建议。未做：跨 run 项目级动作模板与执行器。
- [x] `Emergence Mining-A`：已落地 `emergence_nodes.json` 与 `POST/GET /api/runs/<run_id>/emergence-nodes`，沉淀 run 级候选涌现节点。未做：跨 run 聚类、世界线模板或推荐系统。
- [x] `entity_aliases.yaml` / entity resolution：导入时生成 deterministic alias skeleton，retrieval/context loader/consistency report/锚定页可读取；损坏别名表降级为空索引。
- [x] `Runtime Memory Consumption-A`：`runtime_memory.py` 将 entity aliases、retrieval、canon ledger 命中打包为只读 prompt block；干预、baseline、CLI resume 会写分支 `runtime_memory_context.json`，UI 右侧新增「运行记忆」只读面板。未做：action plan / dynamic action / emergence 真正驱动 runner 状态变化。

### 刻意不做（短期）

- vector embedding / 外部向量库 / reranker
- jieba 依赖（当前正则分词）
- browse 内直接写操作（intervene/resume）— 产品化时并入 v0.7 Web App
- 完整 WenShape 式作者工作台
- eastworld server / Redis / generated client
- autonovel 式一键生成整本书流水线
- AI_NovelGenerator 式作者参数面板或 AGPL 源码复用

---

## 8. 两条产品主线

### 主线 A：演示 / 连续剧（天荒城）

```text
已完成 UI + 检索注入 + v0.4.2 检索记忆可解释展示 → 下一刀 v0.5 第四面墙
```

### 主线 B：真实用户 / 自有内容（导入书）

```text
已完成导入闭环 + 检索 + 检索记忆展示 → 下一刀 v0.5 第四面墙 → v0.6 深度仿真 → v0.7 产品级前端
```

---

## 9. 关键设计决策（勿随意推翻）

1. **builtin vs imported**：天荒城专属规则仅在 `source_type == "builtin_sample"` 生效；imported 走通用规则。
2. **检索**：零新依赖 BM25；builtin 不检索；缺文件不报错。
3. **三分支**：Phase 0/1 固定 2–3 条世界线，不先做 N 叉。
4. **外部项目**：已吸收资产后删除源码目录，新能力集中在 `engine/`。
5. **合约**：磁盘 `story_contract.yaml` 是长期入口；运行时审计尚未完全对齐。
6. **PR 节奏**：大功能拆 PR（v0.2 的 PR-A/B/C 模式）；先结构后质量。

---

## 10. 重要文件与模块索引

|  Concern | 路径 |
|----------|------|
| CLI 入口 | `engine/src/living_novel_engine/cli.py` |
| 统一加载故事 | `engine/src/living_novel_engine/story_loader.py` |
| 场景编排（薄包装） | `engine/src/living_novel_engine/orchestrator/scene_runner.py` |
| Runner adapter | `orchestrator/runners/`（`base.py` / `lightweight.py` / `__init__.py` 注册表） |
| 天荒城规则 | `orchestrator/scene_rules.py` |
| 角色决策 | `agents/character_agent.py` |
| 章节渲染 | `agents/narrator.py` |
| 检索 | `retrieval/retriever.py` |
| 导入写盘 | `import_novel/writer.py` |
| 续章父快照 | `resume/loader.py` |
| 运行产物 | `output/writer.py` |
| 浏览器 | `browser/` |
| 主计划文档 | `docs/living-novel-engine-iteration-plan.md` |

---

## 11. 验收参考 run_id

| 版本 | run_id |
|------|--------|
| v0.1.2 continue | `run_20260528_155153_c3275c_continue_branch_a` |
| v0.1.3 resume intervene | `run_20260528_171207_94a6b9_resume_intervene_linear` |

---

## 12. Agent 维护说明

**每次任务结束后请追加「变更日志」一条**，格式：

```markdown
### YYYY-MM-DD — 简短标题
- **做了什么**：（1–3 条）
- **测试**：（如 174 passed）
- **文件**：（关键路径）
- **下一刀建议**：（可选，若与 §7 不一致请说明原因）
```

并视情况更新：

- §3 当前状态（测试数、下一版）
- §4 已完成版本（若收口新版本）
- §6 已知缺口（勾选已解决项）
- §7 规划路线（勾选待办）

**不要**在本文件中粘贴大段代码或完整 plan 文件；用路径引用即可。

---

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
