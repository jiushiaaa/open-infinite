# Living Novel Engine — 项目记忆（跨会话）

> **用途**：供 Cursor / 多会话 Agent 快速恢复上下文，避免遗忘已完成工作与路线。  
> **维护约定**：每完成一次有意义的开发/设计/验收任务后，在本文件末尾 **「变更日志」** 追加一条记录，并视情况更新「当前状态」「已知缺口」「下一步」。  
> **最后更新**：2026-05-29（v0.6.5 多 Agent 推演工程可靠性）

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

**参考项目**（已吸收精华，源码目录已删除）：

- **WenShape** → 长篇上下文工程（facts、summaries、BM25 概念）
- **webnovel-writer** → genre templates、story_contract
- **MiroFish** → 预研，v0.6 再考虑多 Agent

详见：`docs/research/open-source-essence-absorption.md`

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
| **测试基线** | `269 passed`（2026-05-29） |
| **官方下一版** | **v0.7** 产品级 React/Vite Web App（普通用户入口） |
| **再下一版** | v0.8+ 按触发条件评估 Zep / OASIS / CAMEL / LangGraph |

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

→ v0.7     产品级 React/Vite Web App（普通用户入口）
→ v0.8+    Zep / OASIS / CAMEL / LangGraph 局部 runner / 向量库、多 provider、完整 MasterSetting 工作台
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

### v0.7 产品级前端（机制稳定后）

- 新建独立 `ui/`，推荐 React + Vite + TypeScript
- Web 内完成导入小说、编辑世界锚定、发起干预、选择分支、续章、阅读世界线
- 复用现有 engine / browser API，不重写推演核心
- `lne browse` 继续保留为开发者只读 viewer
- 目标是让普通用户不接触 CLI

### 刻意不做（短期）

- vector embedding / 外部向量库 / reranker
- jieba 依赖（当前正则分词）
- browse 内直接写操作（intervene/resume）— 产品化时并入 v0.7 Web App
- 完整 WenShape 式作者工作台

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
