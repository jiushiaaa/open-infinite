# Living Novel Engine — 项目记忆（跨会话）

> **用途**：供 Cursor / 多会话 Agent 快速恢复上下文，避免遗忘已完成工作与路线。  
> **维护约定**：每完成一次有意义的开发/设计/验收任务后，在本文件末尾 **「变更日志」** 追加一条记录，并视情况更新「当前状态」「已知缺口」「下一步」。  
> **最后更新**：2026-05-29（路线整理：v0.7 Product Web App 九刀已收口；下一步进入 v0.7.2 Agent Interaction）

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
| **MiroFish** | 多 Agent 社会仿真 / OASIS-CAMEL-Zep | 只作为 v0.8+ 可选评估；当前自研 `SceneRunner` + `MultiAgentTrace` |
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
- `docs/article/reports/*.md`

---

## 2. 仓库结构速查

```text
open-infinite/
├── memory.md                          ← 本文件（跨会话记忆）
├── docs/
│   ├── living-novel-engine-iteration-plan.md   # 主迭代计划
│   ├── v0.2-import-novel-mvp.md
│   ├── v0.4-worldline-browser-release.md
│   ├── prd/living-novel-engine-prd.md
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
| **测试基线** | 后端 `410 passed`（2026-05-29，+10 异步 Job）；前端 `engine/ui` typecheck + vite build 通过 |
| **官方下一版** | **v0.7.2 Agent Interaction**：CharacterAction / CharacterProbe / InterventionGuardrail / 轻量角色配置 |
| **后续路线** | v0.7.3 Seedream Visual Assets → v0.7.4 Baseline & Canon Replay → v0.7.5 Worldline Judge → v0.8 Long Novel Memory |

---

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
| 角色动作未结构化为可执行动作 | 目前 trace/event 仍偏叙事事件；需吸收 eastworld + STORY2GAME，补 `CharacterAction`、preconditions/effects、失败原因、降级建议 | v0.7.2 |
| 视觉资产未接入 | 产品 UI 需要角色头像、故事封面、场景背景、世界线节点缩略图；用户已有 Seedream API | v0.7.3 |
| ~~创世入口未做~~ | **v0.7 第六刀已解决**：`POST /api/story-genesis` + `GenesisPage`，主题输入可生成第一章和同构项目并跳转世界锚定页 | — |
| 无干预基线未显式化 | 需要 `Baseline Worldline` 作为“角色自然发展”对照组 | v0.7.4 |
| 正史回放评估未做 | 完结文本可用后续章节作 holdout，评估无干预续写接近原作程度 | v0.7.4 |
| 百万字上传未做 | 当前 import-novel 面向 3-10 章；不支持分片上传、异步导入、断点恢复和导入报告 | v0.8.0 |
| 长篇分层记忆未做 | 当前 briefs/facts 可撑短中篇，但 100 万字以上需要 master_setting / volumes / chapters / scenes / character_states / timeline | v0.8.1 |
| 正史账本未升级 | `facts.jsonl` 还不够表达事件、状态、关系、资源、时间线、伏笔和有效期 | v0.8.2 |
| 长篇混合检索未做 | 当前 BM25 lite 缺 entity boost、prompt budget pack、可选 vector/rerank 和百万字级评估 | v0.8.3 |
| 长篇一致性审计未做 | 需要系统化发现角色漂移、时间线冲突、资源矛盾、合约越界和伏笔遗忘 | v0.8.4 |
| ~~干预缺“抽象意图”中间层~~ | **v0.7.1-A/B 已解决编译层**：已有 `AbstractIntervention` / compatibility / dynamic BranchAxis；仍缺把抽象意图转为可执行 `CharacterActionSequence` | v0.7.2 / v0.8 |
| 世界线缺质量评审 | 需要 `Worldline Judge` 评估角色一致性、合约风险、涌现价值、故事弧、转折点、张力、AI 腔 | v0.7.5 |
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
→ v0.7.2   Agent Interaction：CharacterAction / CharacterProbe / InterventionGuardrail
→ v0.7.3   Visual Asset Generation：Seedream 5.0 Lite 角色头像/封面/场景图
→ v0.7.4   Baseline & Canon Replay：无干预基线 + 正史回放（创世入口已完成前置）
→ v0.7.5   Worldline Judge：世界线评分、故事弧、转折点、anti-slop、emergence_score
→ v0.8     Long Novel Memory：百万字上传、分层记忆、canon ledger、混合检索、一致性审计
→ v0.8+    ActDirector / Discourse-aware Narrator / Dynamic Action Registry / Emergence Mining
→ v0.8+    Zep / OASIS / CAMEL / LangGraph 局部 runner / 向量库、多 provider、完整 MasterSetting 工作台（按触发条件）
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
- [ ] **v0.8+ 可选评估** Zep / 图数据库（长篇记忆崩时）、OASIS / CAMEL（群体仿真需求强时）、LangGraph 局部 runner（复杂状态流转明显增强时）
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

### v0.7.2 Agent Interaction（eastworld + StoryVerse + STORY2GAME）

- [ ] `CharacterAction`：角色结构化动作，不只是自然语言事件
- [ ] `CharacterProbe`：查询角色相信/怀疑/恐惧/第四面墙觉察等内心状态
- [ ] `InterventionGuardrail`：干预进入 `contract_audit` 前先做题材、时代、战力、人设边界检查
- [ ] `AbstractIntervention`：读者输入先转高层意图，再实例化为动作序列
- [ ] `CharacterAction` 增加 `preconditions` / `effects` / `failure_reason` / `repair_suggestions`
- [ ] UI 轻量角色配置：核心信念、欲望、恐惧、已知/未知信息、可执行动作、口癖、合约边界

### v0.7.3 Visual Asset Generation（Seedream 5.0 Lite）

- [ ] 接入 Seedream API：`https://ark.cn-beijing.volces.com`
- [ ] 建议环境变量：`SEEDREAM_API_KEY`、`SEEDREAM_BASE_URL`、`SEEDREAM_MODEL`、`LNE_VISUAL_ASSETS`
- [ ] 生成角色头像：从 `characters.yaml` / style_hint / genre template 生成稳定人物概念图
- [ ] 生成故事封面：从 `world.yaml` / `story_contract.yaml` 生成项目封面
- [ ] 生成场景背景：从章节地点、时间、氛围、世界线状态生成阅读背景或插图
- [ ] 生成世界线节点缩略图：正史节点、涌现节点、Alternate Novel 节点
- [ ] 本地缓存到 `projects/<slug>/assets/` 或 `outputs/<run_id>/<branch>/assets/`，记录 prompt/model/source_refs/file/created_at
- [ ] 未配置 API Key 或调用失败时稳定降级为占位图，不影响文字主流程
- [ ] 不做真人/影视角色复刻，不把视觉资产纳入 story contract 正史判断

### v0.7.4 Baseline & Canon Replay

- [x] `Story Genesis Mode`：用户只输入主题、题材、主角、大概内容，AI 生成第一章和可运行故事世界（v0.7 第六刀已完成）
- [x] 创世模式产物与 imported project 同构：`source/chapter_001.md`、`world.yaml`、`characters.yaml`、`story_contract.yaml`、`canon_chapter.md`（v0.7 第六刀已完成）
- [ ] `Baseline Worldline`：无高维干预，角色按人设、记忆、世界规则和伏笔压力自然推进
- [ ] `Intervened Worldline`：用户施加变量后产生的世界线；UI 对比 baseline 与 intervention 的偏离
- [ ] `Canon Replay Evaluation`：对完结文本或多章节文本，隐藏后续章节作为 holdout，评估无干预续写是否接近原作
- [ ] 输出 `canon_replay_report.json`：canon_similarity、event_hits、missed_events、character_alignment、notes
- [ ] 注意：只给第一章时只能合理预测后续，不能保证等于原作；导入全本时后续章节不得泄漏给角色和 narrator

### v0.7.5 Worldline Judge（autonovel + 2404/2407 论文）

- [ ] `worldline_judgement.json`：每条分支结构化评分
- [ ] 评估维度：persona consistency、contract risk、branch diversity、narrative momentum、emotional payoff、anti-slop、continuation potential
- [ ] 论文 2404：加入 `emergence_score`，识别高价值涌现节点
- [ ] 论文 2407：加入 story arc、turning points、tension、pacing warnings
- [ ] `compare.md` / Web UI 展示“推荐继续 / 谨慎继续 / 建议归档”

### v0.8+ 论文能力深化

- [ ] `Long Novel Ingestion`：txt/md/epub/zip 分片上传，创建 `ingest_job`，支持进度、失败恢复、部分完成状态
- [ ] `Hierarchical Memory`：`master_setting.yaml`、volume/chapter/scene briefs、character_states、timeline、plot_threads、propagation_debts
- [ ] `Canon Ledger`：把 facts 升级为 event/state/relationship/resource/timeline/foreshadowing 账本，带 source_ref/confidence/valid_from
- [ ] `Hybrid Retrieval`：BM25 + chapter distance decay + entity boost + source weight + optional vector/reranker + prompt budget pack
- [ ] `Consistency Audit`：输出 `consistency_report.json`，检查角色漂移、时间线冲突、资源矛盾、合约越界、伏笔遗忘
- [ ] `Long Canon Replay`：全本导入时隔离 `runtime_visible/` 与 `holdout_private/`，holdout 只给 evaluator，不能泄漏给角色/narrator/retrieval
- [ ] `ActDirector`：协调读者意图、角色仿真、世界状态、故事合约
- [ ] `Discourse-aware Narrator`：outline -> turning points -> chapter，避免章节太平或过早收束
- [ ] `Dynamic Action Registry`：动态注册用户/角色新动作，写入 action registry
- [ ] `Emergence Mining`：沉淀高价值 `emergence_nodes.json`，形成世界线模板或推荐
- [ ] `entity_aliases.yaml` / entity resolution：避免同一物品/地点多名称导致状态断裂

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
- **文件**：`docs/prd/living-novel-engine-prd.md`、`docs/living-novel-engine-iteration-plan.md`
- **下一刀建议**：v0.5 第四面墙

### 2026-05-29 — 产品级前端排期补充

- **做了什么**：明确当前 `lne browse` 是开发者/演示 viewer，不是最终普通用户前端；新增 v0.7 Product Web App 路线
- **决策**：v0.5/v0.6 继续优先验证核心机制，v0.7 再新建 React + Vite + TypeScript `ui/`，把导入、干预、续章、世界线浏览做成可点击流程
- **文件**：`docs/living-novel-engine-iteration-plan.md`、`docs/prd/living-novel-engine-prd.md`、`engine/README.md`、`memory.md`
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
- **路线**：v0.6.4 自研 `multi_agent_llm`（API 小模型，不本地部署）→ v0.6.5 并发/重试/成本/质量评估 → v0.8+ 再按“长篇记忆崩 / 群体仿真需求强 / 状态流转复杂化”评估 Zep / OASIS / CAMEL / LangGraph。

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
  - 更新官方路线：v0.7 Product Web App → v0.7.2 Agent Interaction → v0.7.5 Worldline Judge → v0.8+ ActDirector / Discourse-aware Narrator / Dynamic Action Registry / Emergence Mining
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
- **文件**：`docs/living-novel-engine-iteration-plan.md`、`docs/prd/living-novel-engine-prd.md`、`memory.md`
- **下一刀建议**：先让 Cursor 继续按 v0.7 Product Web App / v0.7.1 Intervention Compiler 做设计或实现；若还不急前端，则优先落 `AbstractIntervention` 数据结构和 `Baseline Worldline` CLI 原型

### 2026-05-29 — v0.8 Long Novel Memory 路线补充

- **做了什么**：
  - 将“百万字到数百万字长篇支撑”升级为 v0.8 主线，而不是泛泛的商业化增强
  - 明确不靠超长 prompt，而靠分片上传、异步导入、分层记忆、canon ledger、混合检索、一致性审计和隐藏评估集
  - 吸收参考项目机制：WenShape 的事实/摘要/章节绑定检索，webnovel-writer 的 contract/commit/projection，AI_NovelGenerator 的角色状态/全局摘要/一致性审校，autonovel 的分层设定和 propagation debts
  - 规划 v0.8.0-v0.8.5：Long Novel Ingestion、Hierarchical Memory、Canon Ledger、Hybrid Retrieval、Consistency Audit、Long Canon Replay Evaluation
- **测试**：未运行，文档/记忆更新
- **文件**：`docs/living-novel-engine-iteration-plan.md`、`docs/prd/living-novel-engine-prd.md`、`memory.md`
- **下一刀建议**：继续把剩余产品/技术路线聊清楚；全部确认后再正式进入开发，优先从 v0.7.1 或 v0.8.0 中选择第一刀

### 2026-05-29 — v0.7 UI 交互原则与 Causal Diff 路线补充

- **做了什么**：
  - 明确 UI 不走纯赛博极客风：主体为古风 / 墨水屏 / 纸面阅读，高维系统感只在关键时刻克制出现
  - 将 `Causal Diff / 因果差异块` 写入 v0.7 核心交互：用户在正文局部施加干预后，展示“被抹去的旧现实”和“新凝聚的世界线”，并提供确立、抹除、回滚、查看因果差异
  - 将干预后角色状态增量、克制第四面墙高亮、Agent 轨迹 warning、剧情张力弧线写入 PRD 与迭代计划，并明确优先级
- **测试**：未运行，文档/记忆更新
- **文件**：`docs/living-novel-engine-iteration-plan.md`、`docs/prd/living-novel-engine-prd.md`、`memory.md`
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

### 2026-05-29 — 路线与文档整理（v0.7 主闭环封存）

- **做了什么**：
  - 将 `memory.md`、`docs/living-novel-engine-iteration-plan.md`、`docs/prd/living-novel-engine-prd.md`、`docs/v0.7-product-web-app-ui-spec.md`、`engine/README.md` 从旧的 v0.7.1-C / 317 passed / “v0.7 下一步”口径同步为当前实际状态：**v0.7 Product Web App 九刀已收口，测试基线 410 passed，下一步进入 v0.7.2 Agent Interaction**。
  - 清理已过期缺口：Web 导入、主题创世、Causal Diff 操作、世界锚定页、运行设置、异步 Job 不再标为待做。
  - 将 v0.7.4 重新聚焦为 Baseline Worldline / Canon Replay；其中 Story Genesis Mode 标为已完成前置。
  - 保留 v0.7.3 Seedream 5.0 Lite、v0.7.5 Worldline Judge、v0.8 Long Novel Memory 的正式排期。
- **测试**：文档更新，无需跑 pytest；如后续提交前需要，可按 `cd engine && python -m pytest -q` 与 `cd engine/ui && pnpm run build` 复验。
- **下一刀建议**：v0.7.2 Agent Interaction 第一刀，先做 `CharacterAction` / `CharacterProbe` / `InterventionGuardrail` 的数据结构与只读展示，不急着重构 runner。
