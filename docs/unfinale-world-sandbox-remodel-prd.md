# 未终章世界沙盘改造 PRD

> 版本：2026-06-04
> 目的：把当前项目从“工程化能力不断堆叠”纠偏为“小说世界沙盘 / 活体小说运行时”。  
> 适用范围：后续新会话、`/goal` 长任务、前端重构、API/service 新切片。  
> 事实入口：本文件定义当前改造方向；历史完成状态仍以 `../memory.md`、`docs/living-novel-engine-iteration-plan.md` 和 `engine/README.md` 为准。

## 0. 2026-06-04 实现收口口径

截至 2026-06-04，本 PRD 的 v1-v8 已经完成 **第一版可运行闭环**：

```text
世界沙盘轮次
  -> 角色主观记忆链
  -> 《天命书》
  -> 干预预编译读取《天命书》
  -> 世界线代偿
  -> 世界自演
  -> 多视角活体小说 brief
  -> 作者采纳台
```

这里的“完成”必须按第一版口径理解：

- 已有本地 deterministic service、HTTP API、前端页面、artifact 和测试。
- 已经能让用户看到角色行动、角色个人记忆、天命书、世界自演报告、多视角 brief 和作者采纳账本。
- 尚未达到完整愿景中的“真实高智商多 Agent 长期博弈、LLM 深度推理、L5 觉醒反抗、模因污染、复杂世界状态机和章节级正文自动推进”。

后续默认方向不再是继续补 v1-v8 的“有没有”问题，而是进入 **世界沙盘闭环强化**：

```text
把 deterministic 第一版
  -> 升级为记忆驱动、天命书驱动、可持续状态驱动、可产出章节 brief 的活体小说运行时。
```

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

## 4. 当前实现状态与剩余缺口

第一版已经补齐“有没有”的主链路缺口，但多数能力仍是本地 deterministic / brief / report 级实现。后续不要再把下表第一列当作未做项；真正未完成的是第二阶段深度。

| 能力 | 第一版已完成 | 仍未完成的深度 |
| --- | --- | --- |
| 《天命书》 artifact | 已有 `projects/<slug>/tianming.json`，支持生成、读取、轻量确认；S3 第一刀已加入吸引子权重/类别、多锚点、四档合约压力和 L4/L5/AU 世界线快照；旧版已确认天命书会保守补齐 S3 宪法字段并保留既有吸引子。 | 仍需从长篇全文和章节上下文中做更准确的 AI 预抽取；叙事吸引子和锚点压力还需要随世界线演化动态更新。 |
| 角色主观记忆链 | 已有 `subjective_memory.jsonl`，每个角色/世界线独立追加，下一轮会读取上一条记忆。 | 仍需支持误会、秘密、压抑记忆、世界线残影、觉醒度、外在行动/真实意图分离和长期召回策略。 |
| 沙盘轮次 artifact | 已有 `sandbox_rounds.jsonl` 和 `sandbox_summary.json`。 | 目前行动是 deterministic 模板，不是真正 LLM 多 Agent 高智商博弈；尚未接入多轮复杂目标、势力资源和策略欺骗。 |
| 干预编译器 | 已有读取《天命书》的预编译 API，输出类型、层级、兼容性、转译、分支轴和因果债；L4/L5/AU 会写世界线《天命书》快照且不覆盖根文件。 | 目前主要靠关键词规则；仍需完整实现类型 x 层级 x 转译矩阵、用户确认界面和普通分支/AU 的后续落地执行。 |
| 世界线代偿 | 已有 `tianming_delta.json`，解释锚点转移、候选承载者、因果债和世界内压力。 | 代偿目前是报告，不会持续驱动后续世界状态；仍需让代偿压力进入后续沙盘轮次、角色关系和章节 brief。 |
| 世界自演 | 已有 `autopilot_report.json` 和 checkpoints，支持轮数、事件、时间、锚点变化目标。 | 目前自演只是连续调用沙盘轮次；仍需真正运行到阶段变化、支持睡眠式长时任务、暂停/恢复/回放和失败恢复。 |
| 多视角活体小说 | 已有 `character_lens_briefs.json`，能生成世界正史卷、主锚点卷、角色个人卷、势力卷和事件多视角 brief。 | 仍需从 brief 升级为可读章节正文，支持角色连续个人卷、事件证据链、误会图谱和跨卷宗跳转。 |
| 作者采纳台 | 已有 `author_adoption_ledger.jsonl`、`author_adoption_record.json`、`author_adoption_brief.md`。 | 仍需把采纳结果反哺下一章 brief、原大纲差异、Reviewer 修订和后续世界线继续运行。 |
| UI 信息架构 | 已新增世界沙盘、天命书、多视角、作者采纳台页面和入口。 | 仍未完整拆出 `WorldWorkspaceShell`、世界正史卷、主锚点卷、角色页、事件页、世界线页、检查点页和机制档案页。 |

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

## 8.5 第一版闭环后的后续迭代

v1-v8 的第一版已经证明“世界沙盘链路能跑起来”。后续迭代不要再重复做“生成一个报告/面板”的同类工作，而要让这些报告开始互相驱动，形成真正的活体小说运行时。

### S1-S9 的完成判定

后续仍然采用小步工程实现：先改局部、先验证、保持 additive、保护既有 artifact/API。这是为了降低风险，不是为了把阶段目标降级成最小 MVP。

S1-S9 的完成标准必须从“最小闭环成立”升级为“产品能力成立”：

- `service/API/UI/artifact/tests` 齐全，只代表工程底线通过。
- 用户能真实感到对应能力发生，才代表该阶段可以收口。
- 每完成一个小闭环后，默认继续向下一层深化，直到该阶段验收项全部成立。
- 若当前一轮 S1-S9 已经在执行，不中途打断；待该轮完成后统一按本标准复盘，不合格项进入第三轮迭代。
- 涉及叙事生成、Agent 决策、章节 brief、多视角正文、Reviewer 或视觉质量时，不能只看 mock/deterministic 结果；若 `.env` 已配置真实模型 key，必须补小样本真实 API smoke，观察真实输出是否支撑产品体验。

举例：

- S1 不是“沙盘能跑一轮”，而是角色行动真的被主观记忆、欲望、关系和《天命书》压力改变。
- S4 不是“干预编译器能输出报告”，而是用户确认的干预真的能进入下一轮沙盘并改变世界线。
- S6 不是“生成代偿说明”，而是因果债、锚点转移和候选天命承载者真的持续影响后续世界状态。
- S8 不是“生成多视角 brief”，而是角色个人卷和世界正史卷能作为可读正文连续展开，并能追溯到沙盘事实。
- S9 不是“写入作者采纳账本”，而是采纳结果真的能反哺下一章 brief、伏笔调整和后续沙盘。

### S1：沙盘轮次从模板行动升级为 Agent 决策

当前状态：

- 已收口 S1 第一刀 `Agent Decision Deepening MVP`：`sandbox_rounds.jsonl` 的角色行动新增 `decision_mode`、`decision_inputs`、`visible_action`、`true_intent`、`expected_outcome`、`risk`、`memory_influence` 和 `action_outcome`。
- 每个 deterministic 行动会读取角色欲望、恐惧、上一轮主观记忆、关系/秘密/资源信号和《天命书》压力；第二轮行动可因上一轮 `new_belief` / `anomaly_delta` 改为假意服从、隐瞒、试探结盟或背叛旧约等策略。
- 世界沙盘 UI 已在角色行动卡展示外在行动、真实意图、决策输入、预期/风险和行动结果；不改 `run_scene` 默认行为，不调用外部 provider。
- 仍未完成：LLM runner opt-in、复杂长期关系图、真正高智商多步欺骗和跨轮策略规划；这些进入后续 S1/S2/S5 深化，不计作 v1-v8 第一版重复工作。

目标：

- 每个角色读取自己的主观记忆、欲望、恐惧、关系、秘密、资源和《天命书》压力后再决策。
- 支持 LLM runner opt-in，但默认仍保留 deterministic fallback。
- 角色行动允许失败、误判、假意服从、隐瞒、联盟和背叛。

验收：

- 同一大事件下，不同角色会因为记忆和利益不同产生明显不同策略。
- 第二轮行动不只是引用上一条记忆文案，而是被上一轮信任、异常感或误会改变。
- 高智商角色可以生成“外在行动”和“真实意图”两个字段。

### S2：主观记忆链升级为长期心理与信息差模型

当前状态：

- 已收口 S2 第一刀 `Subjective Memory Psychology MVP`：角色 `subjective_memory.jsonl` 与 `subjective_memory_delta.json` 新增 `perceived_event`、`inner_thought`、`inferred_motive`、`emotional_impact`、`trust_shift`、`anomaly_weight`、`secret_visibility`、`known_truths`、`misbeliefs`、`unknown_canon_facts`、`suppressed_memory`、`worldline_residue` 和 `awareness_level`。
- 同一大事件会被不同角色写成互相矛盾但各自合理的主观记忆；下一轮沙盘冲突会读取上一轮 `misbeliefs`，让误会成为冲突来源，而不是系统硬造冲突。
- 世界沙盘 UI 的“角色个人卷雏形”已展示主观感知、内心想法、推测动机、误会、未知正史、秘密可见性和异常权重。
- 仍未完成：长期召回策略、记忆压缩/遗忘、压抑记忆的后续爆发、误会图谱页面、角色不知道哪些正史事实的对照页；这些进入 S2 后续或 S8 事件多视角证据链。

目标：

- 记忆块增加 `perceived_event`、`inner_thought`、`inferred_motive`、`emotional_impact`、`trust_shift`、`anomaly_weight`、`secret_visibility`。
- 支持记忆压缩、创伤压抑、遗忘、世界线残影和跨轮回既视感。
- 角色查询页能区分“他知道的事实”和“他误以为的事实”。

验收：

- 同一事件至少两个角色写出相互矛盾但各自合理的主观记忆。
- 下一轮能因为误会产生冲突，而不是系统脚本硬造冲突。
- 用户能查看某角色不知道哪些正史事实。

### S3：《天命书》从静态草案升级为世界线宪法

当前状态：

- 已收口 S3 第一刀 `Tianming Worldline Constitution MVP`：根 `tianming.json` 新增 `constitution_schema_version`，`narrative_attractors` 支持权重和类别，`anchor_status.anchors` 支持角色/势力/谜团/地点多锚点，`contract_pressure.pressure_tiers` 支持轻微压力、重大压力、时代压力和世界崩坏压力。
- 已存在的旧版已确认 `tianming.json` 会在生成/读取时保守补齐 S3 宪法字段；既有吸引子不会被迁移过程丢弃。
- `POST /api/stories/<slug>/tianming/intervention-compile` 支持 `worldline_id`；L4/L5 或 AU 干预会写 `projects/<slug>/worldlines/<worldline_id>/tianming_snapshot.json`，并在返回值中给出 `worldline_tianming_snapshot`，根 `tianming.json` 不被覆盖。
- 天命书页可查看吸引子权重/类别、多锚点和四档压力，并可指定“投放世界线”触发世界线天命书快照展示。
- 仍未完成：吸引子随世界线演化动态重排、锚点类型覆盖物品/地点/谜团的真实抽取、锚点转移后自动刷新世界线宪法，以及 L4/L5 快照的作者确认/审计工作流。

目标：

- `narrative_attractors` 支持多条带权重的大势/爽点承诺。
- `anchor_status` 支持角色、势力、物品、地点、谜团等多锚点。
- `contract_pressure` 分轻微压力、重大压力、时代压力、世界崩坏压力。
- L4/L5 干预或锚点转移后，生成世界线《天命书》快照，而不是覆盖根《天命书》。

验收：

- 三国类项目能同时表达“汉室衰微、天下归一、士族崛起、英雄退场”等多条吸引子。
- 爽文项目能表达“主角升级反馈回路、反派送经验、奇遇倾斜”等爽点吸引子。
- 干预编译器能解释某次干预为什么被本土化重释、转入 AU 或产生高因果债。

### S4：干预编译器从预检报告升级为可执行投放

当前状态：

- 已收口 S4 第一刀 `Intervention Execution Constraint MVP`：`POST /api/stories/<slug>/sandbox/run` 可选接收 `intervention_content` 与 `intervention_target`，即时读取《天命书》并复用干预编译器生成本轮 `intervention_constraint.json`。
- 编译结果会写入 `sandbox_rounds.jsonl` 的 `intervention_constraint`，并进入角色 `decision_inputs`、外在行动、行动结果、冲突原因、信息流和 `world_state_delta.intervention_effects`；普通干预不会覆盖根 `tianming.json`。
- 世界沙盘页已新增可选“本轮干预 / 投放对象”输入和“已投放干预约束”结果区，用户能看到法则吸收、分支轴、因果债和投放结果。
- 仍未完成：沉浸模式 / 暴走 AU 模式的明确确认流、用户确认后的分支持久继续运行、L4/L5 世界线快照审计确认、干预投放后的多轮分支追踪。

目标：

- 自由输入经过类型识别、层级判断、兼容性审计、转译策略、分支轴生成后，可以进入沙盘轮次。
- 用户可在沉浸模式和暴走 AU 模式之间选择。
- 普通干预生成 Divergent Worldline；前提改写或元叙事改写生成 AU 或世界线《天命书》快照。

验收：

- “告诉她未来大纲”被转译为梦兆/密信/预言，并产生相信、怀疑、隐瞒、试探等分支轴。
- “投放 AK47”在历史/中世纪世界被标记为异物入侵，可选择本土化重释或暴走 AU。
- 用户确认的分支轴能成为下一轮沙盘约束，而不是只停留在说明文本。

### S5：L5 觉醒、角色反抗和模因污染

目标：

- 角色可以知道自己是小说人物，并把这件事写进自己的主观记忆。
- 觉醒不是 bug，不做系统管理员重置；角色可以虚无、反抗、欺骗读者、保护他人或继续完成使命。
- 高觉醒角色可以向其他角色传播高维真相，形成模因污染。

验收：

- 觉醒角色的 `anchor_instability` 或等价字段显著上升。
- 角色可以拒绝普通干预，也可以表面服从、暗中布局。
- “你们都是虚构的”会作为世界内思想瘟疫，引发政治、宗门、关系、战争或社交压力。

### S6：世界线代偿从报告升级为持续状态压力

目标：

- `tianming_delta.json` 的锚点变化、因果债、候选承载者和压力事件进入下一轮沙盘。
- 主角死亡、摆烂、失锚后，世界优先寻找新锚点，而不是停止。
- 当没有合格承载者时，进入群像无主线状态。

验收：

- 当前锚点拒绝主线后，其他角色或势力会因欲望和资源自然补位。
- 因果债会先压向当前锚点，再外溢到关系网和世界环境。
- 候选天命承载者上位失败或成功，都能由能力、欲望、资源和阻力解释。

### S7：世界自演从多轮调用升级为无人值守运行

目标：

- 支持启动、暂停、恢复、查看进度和检查点回放。
- 支持运行到“事件发生 / 时间到达 / 锚点变化 / 因果债爆发 / 角色觉醒”。
- 自演过程能生成阶段性世界摘要、角色记忆变化和可读入口。

验收：

- 用户可以睡前启动自演，醒来看到世界推进到新阶段。
- 每个检查点都能查看发生了什么、谁记住了什么、世界状态为何改变。
- 自演失败或中断后可以从上一个检查点恢复。

### S8：多视角活体小说从 brief 升级为正文与证据链

目标：

- 每个事件可生成世界正史卷、主锚点卷、角色个人卷、势力卷和事件多视角正文。
- 每段正文能追溯到沙盘轮次、角色主观记忆和世界状态 delta。
- 角色个人卷形成连续阅读体验，而不是一次性片段。

验收：

- 同一事件的世界正史和角色个人卷存在真实信息差。
- 角色个人卷能连续阅读 3 个以上事件节点。
- UI 能从正文跳到对应记忆证据和沙盘轮次。

### S9：作者采纳台反哺下一章生成

目标：

- 作者采纳结果生成下一章 brief、伏笔调整、原大纲差异和 Reviewer 修订建议。
- 采纳、部分采纳、另开分支会影响后续沙盘或章节生成入口。
- 作者模式与读者模式共享世界底座，但展示不同操作重点。

验收：

- 采纳一条沙盘涌现剧情后，可以生成可继续写作的下一章 brief。
- 部分采纳能保留作者备注和需要人工确认的冲突点。
- 另开分支能创建作者分支，不覆盖原正史。

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

交付同步规则：

- 长任务可以分多个 checkpoint 推进，但每个可验证独立切片完成后，应及时提交并推送远程，避免新会话拿不到最新代码。
- 推送前必须检查 `git status`，只提交当前切片负责的文件。
- 如果工作树里混有用户或另一轮 AI 的未完成改动，不要混推；先隔离提交范围、说明阻塞，或等当前任务收口后再推。
- 如果无远程、无上游、认证失败或网络失败，必须在最终回复和 changelog/交接文档里说明未推送原因。

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

请先基于现有代码找安全的小步切片，保持 additive，不破坏既有 artifact/API，不改 run_scene 默认行为。注意：小步切片只是工程推进方式，不是产品完成标准。每一刀必须让用户看到角色行动、主观记忆或世界变化；完成一个小闭环后，继续按 S1-S9 深化，直到对应产品能力真实成立。
```
