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

**测试基线**：`pytest -q` → **245 passed**（2026-05-29）。

### Run 分支产物

除 `chapter.md` / `events.json` / `state_snapshot.json` / `summary.md` 外，imported 项目在检索时会额外写入：

```text
outputs/run_xxx/branch_a/retrieval_context.json
```

字段：`query`、`current_chapter`、`prompt_block`、`items[]`（含 `id`、`source`、`score`、`text`、`chapter`、`evidence`）。builtin 样例不写此文件。

v0.4.2 起，`lne browse` 在分支阅读器新增「检索记忆」标签页：按 `source`（合约 / 正史事实 / 章节摘要 / 卷摘要）分组展示本章生成引用的命中项与分数，世界线树的分支节点也会显示「检索 N」角标。

> 注意：当前浏览器是开发者/演示用 viewer，技术栈为 Python stdlib HTTP + 原生 HTML/CSS/JS。真正面向普通用户的产品级前端计划放在 v0.7，倾向新建 React + Vite + TypeScript 的独立 `ui/`，把导入、干预、续章和世界线浏览都做成可点击流程。

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

产物目录：`projects/<slug>/`（`world.yaml`、`characters.yaml`、`canon_chapter.md` 等）。详见 [v0.2-import-novel-mvp.md](../docs/v0.2-import-novel-mvp.md)。

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
│   └── state_snapshot.json  # 完整状态快照
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
| v0.6.4 | `multi_agent_llm`：OpenAI-compatible API 小模型推演，不本地部署 |
| v0.6.5 | 并发、重试、成本控制、trace 质量评估 |
| v0.7 | 产品级 React/Vite Web App |
| v0.8+ | Zep / OASIS / CAMEL / 向量库 / 多 provider / 完整工作台（按规模触发评估） |
