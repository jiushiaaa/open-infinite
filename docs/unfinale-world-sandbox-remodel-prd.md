# 未终章世界沙盘改造 PRD

> 版本：2026-06-03  
> 目的：把当前项目从“工程化能力不断堆叠”纠偏为“小说世界沙盘 / 活体小说运行时”。  
> 适用范围：后续新会话、`/goal` 长任务、前端重构、API/service 新切片。  
> 事实入口：本文件定义当前改造方向；历史完成状态仍以 `../memory.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md` 为准。

## 1. 改造结论

未终章不需要推倒重做。当前项目已经有大量可复用底座：

- 导入、主题创世、世界锚定。
- 世界线、干预编译、Causal Diff。
- 多 Agent runner / trace。
- runtime memory、canon ledger、entity aliases、retrieval。
- Reader Panel、Worldline Judge、Reviewer 式质量检查。
- Web UI、API、CLI 和本地启动链路。

真正跑偏的是优先级：项目过去把大量精力继续投向 provider、Graph Memory、检索评测、OpenAPI、发行准备、商业化边界等支撑层，导致“角色真的会自己行动、世界会自演、角色有主观记忆、读者干预有后果”这些最核心的产品体验没有被放到第一顺位。

后续改造主线必须回到：

```text
导入故事世界
  -> 生成并确认《天命书》
  -> 启动世界沙盘
  -> 多角色按主观记忆行动
  -> 每轮写入角色主观记忆
  -> 世界状态和锚点发生变化
  -> 读者自由干预，干预编译器解释并投放变量
  -> 世界自演并生成检查点
  -> 以主线卷、角色个人卷、事件多视角渲染成可读文本
```

## 2. 主导航决策

主导航采用：

> 世界书架 -> 世界内部卷宗

不采用：

> 沙盘 / 阅读 / 干预 / 作者 四大工作区

原因：

- 产品本质是“进入一个正在运行的小说世界”，而不是操作一个 AI 写作 SaaS。
- 沙盘、阅读、干预、作者都只是进入同一个世界的不同方式，不应该割裂成四个顶层产品。
- 按世界组织导航，能让用户自然理解“同一个事件可以被世界正史、主锚点、角色个人卷、势力卷和事件多视角共同观察”。

推荐信息架构：

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
      -> 作者采纳台（作者模式可见或突出）
      -> 机制档案（支撑层）
      -> 设置（支撑层）
```

“沙盘 / 阅读 / 干预 / 作者”的处理方式：

```text
沙盘 = 世界沙盘页 + 世界自演控制。
阅读 = 世界正史卷 / 主锚点卷 / 角色个人卷 / 势力卷。
干预 = 全局常驻干预栏 + 干预编译器弹层。
作者 = 作者采纳台 / 原大纲对照 / Reviewer / 导出。
```

一句话原则：

> 主导航按世界组织，功能按场景浮现。

## 3. 当前代码如何接入新方向

### 3.1 可直接复用的现有模块

| 当前模块 | 现有职责 | 改造后位置 |
| --- | --- | --- |
| `ImportNovelPage.tsx` | 导入小说 | 世界书架里的“导入故事世界” |
| `GenesisPage.tsx` | 主题创世 | 世界书架里的“新建世界” |
| `WorldAnchorPage.tsx` | 世界锚定、设定确认 | 升级为《天命书》确认页 |
| `WorkspacePage.tsx` | 项目工作台、阅读、分支、各类面板 | 拆分为世界内部卷宗壳，不再继续堆面板 |
| `WorldlineTree.tsx` | 世界线树 | 世界线页基础 |
| `ChapterReader.tsx` | 正文 / Diff 阅读 | 世界正史卷、主锚点卷的阅读基础 |
| `InterventionComposer.tsx` | 干预输入 | 全局常驻干预栏基础 |
| `CompilationPanel.tsx` | 干预编译结果 | 干预编译器弹层基础 |
| `CausalDiffBlock.tsx` | 旧现实 / 新世界差异 | 事件多视角和世界线偏移说明基础 |
| `RightPanel.tsx` | 右侧机制解释面板 | 改为“机制档案”，不再作为主体验 |
| `CharacterProbePanel.tsx` | 角色探针 | 角色个人卷右侧镜头基础 |
| `AgentTracePanel.tsx` | 多 Agent trace | 沙盘轮次解释基础 |
| `ReaderPanel.tsx` | 读者评审 | 作者采纳台 / Reviewer 支撑 |
| `WorldlineJudgePanel.tsx` | 分支评审 | 世界线页和作者采纳台支撑 |

### 3.2 可作为底层引擎的现有后端

| 当前模块 | 改造用法 |
| --- | --- |
| `import_novel/*` | 继续负责导入、抽取、记忆骨架、正史账本和一致性报告。 |
| `story_loader.py` | 继续加载 `world.yaml`、`characters.yaml`、`story_contract.yaml`，并作为生成《天命书》的输入。 |
| `intervention_compiler/*` | 保留，升级为每次读取《天命书》后再判断类型、层级、转译、分支轴和 AU。 |
| `intervention/guardrail.py` / `contract_audit.py` | 从“干预护栏”升级为“世界法则契合度 / 因果债风险”的支撑规则。 |
| `orchestrator/runners/multi_agent_stub.py` / `multi_agent_llm.py` | 第一版沙盘轮次的基础 runner。 |
| `orchestrator/runners/protocol.py` | 多 Agent trace 和角色行动结构的基础契约。 |
| `runtime_memory.py` | 运行时记忆上下文可复用，但不能替代角色主观记忆链。 |
| `fourth_wall/*` | L5 觉醒、命痕、模因污染和角色反抗的基础。 |
| `worldline_judge/*` | 世界线评审、锚点偏移风险和作者采纳建议。 |
| `causal_diff/*` | 干预后旧现实 / 新世界线差异。 |
| `browser/server.py` | 本地 API 入口继续复用，新增沙盘 API 时保持安全 ID 校验和 400/404/409 降级。 |

### 3.3 必须降级为支撑层的内容

以下能力已经完成或可用，但后续不能再占据主导航和主开发路线：

- GraphRAG / Zep 触发证据、provider spike、mock adapter review。
- 真实向量检索、Zilliz、reranker、embedding 评测面板。
- OpenAPI / typed client 面板。
- 发行准备、商业化边界、计费、权限、对象存储。
- 纯工程健康报告、provider readiness、operator checklist。

它们应该进入：

```text
机制档案
设置
开发者支撑层
```

除非用户明确要求，否则不继续扩展这些方向。

## 4. 当前缺口

当前项目要拉回正规，必须补齐以下主链路缺口：

| 缺口 | 说明 |
| --- | --- |
| 《天命书》 artifact | 当前有 `world.yaml`、`story_contract.yaml`、`anchor_proposal.yaml`，但缺少统一的 `tianming.json`。 |
| 多条带权重叙事吸引子 | 当前故事合约偏静态，没有“历史大势 / 爽点承诺 / 类型承诺”的动态权重。 |
| 角色主观记忆链 | 当前 runtime memory 是运行上下文，不是 Alice/Bob 各自持续增长的主观记忆。 |
| 沙盘轮次 artifact | 当前 multi-agent trace 存在，但缺少“第 N 轮每个角色看到什么、想什么、做什么、记住什么”的稳定结构。 |
| 世界自演 | 当前 run 多数仍是用户触发一次生成，不支持运行到事件、时间、锚点变化或因果债爆发。 |
| 检查点 | 当前有分支和 selected worldline，但缺少 Autopilot 检查点管理。 |
| 世界线代偿 | 当前世界线评审存在，但缺少锚点转移、候选天命承载者、因果债扩散的主链路。 |
| 多视角活体小说 | 当前以主线章节和分支为中心，缺少角色个人卷、势力卷、事件多视角卷。 |
| 作者采纳台 | 当前有评审和导出，但缺少原大纲 vs 沙盘涌现剧情的采纳工作台。 |

## 5. 目标 artifact

后续新增 artifact 必须 additive，不破坏既有 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。

推荐新增：

```text
projects/<slug>/tianming.json
  世界宪法：天道大势、世界法则、当前锚点、因果债、候选天命承载者。

projects/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective_memory.jsonl
  某角色在某世界线上的主观记忆链。

outputs/<run_id>/sandbox_rounds.jsonl
  每轮沙盘行动：角色意图、行动、冲突、信息传播、世界状态 delta。

outputs/<run_id>/subjective_memory_delta.json
  本次 run 写入哪些角色记忆。

outputs/<run_id>/event_materials.json
  事件材料 / 记忆镜片：关键事件如何进入章节 brief、角色个人卷和伏笔。

outputs/<run_id>/tianming_delta.json
  本次 run 是否造成锚点偏移、因果债变化、吸引子权重变化。

outputs/<run_id>/autopilot_report.json
  世界自演报告：运行目标、轮次、检查点、关键变化、可读文本入口。

  outputs/<run_id>/character_lens_briefs.json
    同一事件在不同角色视角中的 brief。

  projects/<slug>/author_adoption_ledger.jsonl
    作者采纳、部分采纳、另开分支或导出 brief 的本地账本。

  outputs/<run_id>/author_adoption_record.json
  outputs/<run_id>/author_adoption_brief.md
    原大纲 vs 沙盘涌现剧情对照和作者采纳 brief。
  ```

第一版可以先把 `subjective_memory.jsonl` 放在 project 下的轻量目录，不急着上 GraphRAG / Zep。只有当本地 JSONL 无法支撑召回和关系推理时，再重新评估图记忆。

## 6. 目标 API

后续 API 继续使用现有本地 HTTP server 模式，所有 slug/run_id/branch_id/worldline_id/character_id 必须安全校验。

推荐新增或升级：

```text
GET /api/stories/<slug>/tianming
  读取《天命书》。

POST /api/stories/<slug>/tianming/confirm
  确认或微调《天命书》。普通导入初始化可写；运行中修改属于 L4/L5 高等级干预。

POST /api/stories/<slug>/sandbox/run
  启动一次沙盘轮次。

POST /api/stories/<slug>/world-autopilot/run
  启动世界自演，可运行到轮数、事件、时间或锚点变化。

GET /api/stories/<slug>/sandbox/runs/<run_id>
  读取沙盘轮次、记忆变化、世界状态 delta、事件材料和自演报告。

GET /api/stories/<slug>/worldlines/<worldline_id>/characters/<character_id>/memories
  读取某角色在某世界线上的主观记忆链。

GET /api/stories/<slug>/events/<event_id>/perspectives
  读取事件多视角：世界正史、角色主观记忆、误会图谱、叙事去向。

GET /api/stories/<slug>/character-lens/<character_id>
  生成或读取角色个人卷片段。

POST /api/stories/<slug>/character-lens/generate
  从同一事件生成世界正史卷、主锚点卷、角色个人卷、势力卷和事件多视角 brief。

POST /api/stories/<slug>/author-adoption
  作者模式下采纳、部分采纳、另开作者分支或导出 brief。
```

第一版不需要全部实现。最小闭环只需要：

```text
GET/POST tianming
POST sandbox/run
GET sandbox/run detail
GET character memories
```

## 7. 目标 UI 骨架

现有 `App.tsx` 的路由只有：

```text
entry
import
genesis
anchor
workspace
```

改造时不要一次性大重写。建议逐步演进：

### 阶段 A：保留现有路由，先改信息架构文案

```text
entry -> 世界书架
anchor -> 天命书
workspace -> 世界内部卷宗首页
```

### 阶段 B：新增世界内部子页

推荐 hash 路由：

```text
#/world/<slug>/tianming
#/world/<slug>/sandbox
#/world/<slug>/chronicle
#/world/<slug>/anchor-volume
#/world/<slug>/characters
#/world/<slug>/characters/<character_id>
#/world/<slug>/events
#/world/<slug>/events/<event_id>
#/world/<slug>/worldlines
#/world/<slug>/checkpoints
#/world/<slug>/author
#/world/<slug>/mechanism
```

### 阶段 C：拆分 `WorkspacePage.tsx`

`WorkspacePage.tsx` 当前承担过多职责。后续不要继续往里面堆功能，应拆成：

```text
WorldWorkspaceShell.tsx
  世界内部卷宗布局。

TianmingPage.tsx
  《天命书》确认与微调。

SandboxPage.tsx
  世界自演控制与轮次报告。

ChroniclePage.tsx
  世界正史卷。

CharacterLensPage.tsx
  角色个人卷和主观记忆。

EventPerspectivePage.tsx
  事件多视角和误会图谱。

WorldlineCompensationPage.tsx
  世界线、锚点代偿、候选天命承载者。

AuthorAdoptionPage.tsx
  作者采纳台。

MechanismArchivePage.tsx
  旧工程面板、Graph/检索/provider/审计等支撑层。
```

## 8. 第一阶段改造路线

### v1：世界沙盘循环 / 单次角色行动轮

目标：输入一个大事件后，至少 3 个角色按自己的欲望、利益、关系和记忆行动。

当前状态：已收口第一版 deterministic 本地沙盘轮次。`POST /api/stories/<slug>/sandbox/run` 会读取项目角色设定，生成 `outputs/<run_id>/sandbox_rounds.jsonl` 与 `sandbox_summary.json`；`GET /api/sandbox-runs/<run_id>` 可读取结果。前端已新增“世界书架 -> 世界沙盘”入口和 `WorldSandboxPage`，展示角色意图、行动、冲突、信息传播、世界状态变化和后续故事可能性。

验收：

- [x] 生成 `sandbox_rounds.jsonl`。
- [x] 每个角色有行动和行动理由。
- [x] 输出世界状态 delta。
- [x] UI 能看到角色行动链。
- [x] 不改 `run_scene` 默认行为，不覆盖 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。

### v2：主观记忆链

目标：每轮后给每个角色分别写入主观记忆。

当前状态：已收口第一版。沙盘轮次成功后，会为每个行动角色追加 `projects/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective_memory.jsonl`，同时在 run 目录写入 `subjective_memory_delta.json`；下一轮行动会读取该角色最后一条主观记忆并展示在行动卡片里。前端世界沙盘页可点击角色查看“角色个人卷雏形”。

验收：

- [x] 同一事件写入至少 2 个角色的不同记忆。
- [x] 下一轮行动能引用上一轮主观记忆。
- [x] UI 能查看某角色记忆，而不是全局正史摘要。
- [x] HTTP 读取路径 `GET /api/stories/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective-memory` 坏 ID 返回 400，缺项目返回 404。

### v3：《天命书》

目标：导入后生成 `tianming.json`，用户必须确认但不填复杂表单。

当前状态：已收口第一版。`POST /api/stories/<slug>/tianming/generate` 会从 `world.yaml`、`characters.yaml`、`open_threads.yaml` 派生本地 deterministic 草案，写入 `projects/<slug>/tianming.json`；`GET /api/stories/<slug>/tianming` 读取；`POST /api/stories/<slug>/tianming/confirm` 用 `confirm=true` 做轻量确认。前端新增“世界内部卷宗 · 天命书”页，可生成草案、查看字段和轻量确认。

验收：

- [x] 包含 `narrative_attractors`、`genre_constraints`、`anchor_status`、`contract_pressure`、`replacement_anchor_candidates`。
- [x] 干预编译器每次读取《天命书》。
- [x] 普通干预不能直接永久改写《天命书》。

### v4：干预编译器升级

目标：自由输入先被编译，再投放进世界。

当前状态：已收口第一版预编译。`POST /api/stories/<slug>/tianming/intervention-compile` 读取 `tianming.json`，输出干预类型、层级、兼容性、转译策略、Divergent/AU 判断、分支轴、因果债和审计提示；不调用 `run_scene`，不写 run artifact，不改写 `tianming.json`。前端“天命书”页新增干预预编译模块，用卷内注解方式展示结果。

验收：

- [x] 信息型、行动约束型、物品注入型、规则改写型能生成不同分支轴。
- [x] 系统、未来大纲信、物品/资源注入能分别触发转译、AU 或因果债提示。
- [x] UI 展示叙事化包装，不直接暴露冷术语。

### v5：世界线代偿与锚点转移

目标：主角死亡、摆烂或觉醒后，世界继续运行。

当前状态：已收口第一版。`POST /api/stories/<slug>/narrative-compensation/run` 读取《天命书》，根据失锚/拒绝/摆烂/离场等触发事件生成 `outputs/<run_id>/tianming_delta.json`，解释锚点状态、候选天命承载者、因果债扩散和世界内压力事件。前端“天命书”页新增世界线代偿模块。

验收：

- [x] 生成 `tianming_delta.json`。
- [x] 候选天命承载者有欲望、能力、资源、风险评分。
- [x] UI 能解释代偿证据。
- [x] 不做“系统管理员强行抹杀”；压力通过政治、关系、势力和环境自然涌现。

### v6：世界自演

目标：用户能设定运行目标，世界自动运行多轮并生成检查点。

当前状态：已收口第一版。`POST /api/stories/<slug>/world-autopilot/run` 会连续复用沙盘轮次和主观记忆链，支持 `rounds`、`event`、`time`、`anchor_change` 四种目标，生成 `outputs/<run_id>/autopilot_report.json` 和 `checkpoints/checkpoint_*.json`。前端世界沙盘页新增“世界自演”控制，可展示昨夜世界演化报告、停止原因和每轮检查点；不调用 `run_scene`，不覆盖既有核心 artifact。

验收：

- [x] 支持运行到轮数 / 事件 / 时间 / 锚点变化。
- [x] 生成 `autopilot_report.json`。
- [x] 生成 checkpoints。
- [x] UI 展示昨夜世界演化报告。

### v7：多视角活体小说

目标：同一事件能以世界正史、主锚点、角色个人卷、势力卷等方式渲染。

当前状态：已收口第一版。`POST /api/stories/<slug>/character-lens/generate` 会基于同一 `source_event` 先运行或读取沙盘轮次，再读取角色主观记忆链，写入 `outputs/<run_id>/character_lens_briefs.json`。前端新增“世界内部卷宗 · 多视角活体小说”页，展示世界正史卷、主锚点卷、角色个人卷、势力卷和事件多视角；角色个人卷的证据来源为 `subjective_memory`。

验收：

- [x] 生成 `character_lens_briefs.json`。
- [x] UI 能查看至少 2 个视角。
- [x] 视角差异来自角色主观记忆，而不是简单改写文风。

### v8：作者采纳台

目标：作者能把沙盘涌现剧情采纳为大纲素材。

当前状态：已收口第一版。`POST /api/stories/<slug>/author-adoption` 支持 `adopted`、`partial`、`new_branch`、`export_brief` 四种决策，写入 `projects/<slug>/author_adoption_ledger.jsonl`，并输出 `author_adoption_record.json` 与 `author_adoption_brief.md`。前端新增“世界内部卷宗 · 作者采纳台”页，可并排编辑原大纲与沙盘涌现剧情，记录采纳方式和作者备注；采纳只追加账本，不自动覆盖正史。

验收：

- [x] 原大纲 / 沙盘涌现剧情并排。
- [x] 支持采纳、部分采纳、另开作者分支、导出作者采纳 brief。
- [x] 作者模式不自动覆盖正史。

## 9. 长任务硬边界

后续 `/goal` 或新会话执行改造时，必须遵守：

```text
不继续扩 provider。
不接 GraphRAG / Zep，除非本地 JSONL 主观记忆链已经被证明不够。
不做云端多用户。
不做计费、对象存储、真实认证。
不继续往 WorkspacePage.tsx 堆工程面板。
不把 CLI 做成普通用户主入口。
不改 run_scene 默认行为。
不破坏既有 artifact。
```

每一刀必须服务以下至少一项：

```text
世界会运行。
角色会自主。
角色会记得。
干预有后果。
角色可能反抗。
世界会代偿。
章节来自世界演化。
```

## 10. 新会话推荐提示词

后续开新会话要改造项目时，可直接使用：

```text
请先阅读并对齐：
- AGENTS.md
- memory.md
- docs/index.md
- docs/codex-handoff.md
- docs/unfinale-world-sandbox-remodel-prd.md
- docs/unfinale-product-vision-correction-draft.md
- docs/living-novel-engine-iteration-plan.md
- docs/living-novel-engine-prd.md
- docs/completed/v0.7-product-web-app-ui-spec.md
- engine/README.md

当前最高优先级不是继续 Graph/provider/检索评测/工程看板，而是把项目改造成“世界书架 -> 世界内部卷宗”的小说世界沙盘：
导入 -> 《天命书》 -> 世界沙盘 -> 主观记忆链 -> 世界自演 -> 多视角活体小说 -> 作者采纳台。

请先基于现有代码找最小可行切片，保持 additive，不破坏既有 artifact/API，不改 run_scene 默认行为。每一刀必须让用户看到角色行动、主观记忆或世界变化。
```
