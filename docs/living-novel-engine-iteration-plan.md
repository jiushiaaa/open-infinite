# Living Novel Engine 产品迭代计划

> 版本：2026-05-31（v0.7 Product Web App 九刀 + v0.7.2 Agent Interaction + v0.7.3 Visual Asset Generation + v0.7.4 Baseline & Canon Replay + v0.7.5 Worldline Judge + v0.8.0-A 至 v0.8.5-A Long Novel Memory 底座 + ActDirector-A + Discourse-aware Narrator-A + Dynamic Action Registry-A + Emergence Mining-A + Entity Aliases / Entity Resolution + Runtime Memory Consumption-A + 前端 Artifact Panel + Long Upload Productization + v0.8.6 Long Import Review + v0.8.7 Resumable Ingest Jobs + v0.8.8 Long Project Workspace + v0.8.9 Long Replay & Audit UI + v0.8.10-A/B Runner State Execution 均已收口；v0.9.0-alpha Long Novel Creation Loop 已启动并完成 Chapter Export 子刀）
> 范围：对齐 PRD v0.1-v0.8、仓库根目录 Roadmap、`engine/` 全版本实况。  
> 核心原则：WenShape / webnovel-writer 的可复用资产已吸收至 engine（genre_templates、数据结构概念），外部项目源码目录已删除。后续新能力集中在 `engine/` 编排层和自研 UI/API 层。
> v0.1-v0.8 已完成能力与未做项总览见 `docs/completed/v0.1-to-v0.8-version-audit.md`。

## 1. 产品北极星

Living Novel Engine 不是普通 AI 续写器，而是一个“活体小说运行时”：

```text
文本输入 -> 世界锚定 -> 角色自主行动 -> 读者干预 -> 世界线分叉 -> 章节渲染 -> 可继续运行
```

它要验证的不是“AI 能不能写下一章”，而是：

- 小说世界能否在没有作者继续写作的情况下继续运行。
- 读者能否从阅读者变成命运干预者。
- 角色能否因为人设、记忆、利益和世界规则而拒绝用户命令。
- 同一段原文能否长出不同读者专属的平行世界线。

## 2. 当前状态总览

```text
Phase 0  CLI 概念验证       已收口
    ↓
v0.1.1   体验 polish        已收口
    ↓
v0.1.2   resume continue    已收口
    ↓
v0.1.3   resume intervene   已收口
    ↓
v0.2     文本导入与世界锚定  已收口 · 见 docs/v0.2-import-novel-mvp.md
    ↓
v0.2.1   resume imported    已收口
    ↓
v0.2.2   精华固化           已收口 · 见 docs/research/open-source-essence-absorption.md
    ↓
v0.4     世界线浏览器        已收口 · 见 docs/v0.4-worldline-browser-release.md
    ↓
v0.4.1   边界加固           已收口
    ↓
v0.3.0   Context Retrieval Lite  已收口
    ↓
v0.3.1   检索 artifact + Brief 接入  已收口
    ↓
v0.4.2   UI polish + 检索记忆展示  已收口
    ↓
v0.5     第四面墙机制        干预记忆、角色觉察、反抗命运  已收口
    ↓
v0.6.0   Runner Adapter      可插拔 SceneRunner / 注册表  已收口
    ↓
v0.6.1   Multi-Agent Protocol  协议 + 数据结构骨架（未接入运行）  已收口
    ↓
v0.6.2   multi_agent_stub    消费协议产出 trace 并投影回契约  已收口
    ↓
v0.6.3   trace 可视化        browse「Agent 轨迹」标签页  已收口
    ↓
v0.6.4   multi_agent_llm     OpenAI-compatible API 小模型推演  已收口
    ↓
v0.6.5   推演工程可靠性      generation_meta/质量校验/重试/usage  已收口
    ↓
v0.7.1-A Intervention Compiler 最小闭环  rule-based 编译 + 动态 BranchAxis  已收口
    ↓
v0.7.1-B Intervention Compiler LLM 增强  LLM 编译 + fallback + 安全兜底  已收口
    ↓
v0.7.1-C Causal Diff 后端数据预留  old/new 段落级 diff artifact  已收口
    ↓
v0.7     Product Web App     React/Vite 产品级前端，面向普通用户  已收口 · 见 docs/completed/v0.7-product-web-app-ui-spec.md
    ↓
v0.7.2   Agent Interaction   角色动作/情绪探针/干预护栏/轻量角色配置  已收口（CharacterAction/CharacterProbe/InterventionGuardrail）
    ↓
v0.7.3   Visual Asset Generation  Seedream 5.0 Lite 角色头像/场景图/封面  已收口
    ↓
v0.7.4   Baseline & Canon Replay  无干预基线 + 正史 holdout + deterministic 回放评估  已收口
    ↓
v0.7.5   Worldline Judge     读者/编辑评审团 + 静态流水线项目取舍复盘  已收口
    ↓
v0.8     Long Novel Memory + Action/Discourse/Emergence artifacts  已收口底座
    ↓
v0.8.6   Long Import Review  导入报告细化 / 章节预览 / 失败空态  已收口
    ↓
v0.8.7   Resumable Ingest Jobs  断点续传 / 分片恢复  已收口
    ↓
v0.8.8   Long Project Workspace  长篇项目资产页  已收口
    ↓
v0.8.9   Long Replay & Audit UI  长篇回放与审计 UI  已收口
    ↓
v0.8.10-A Runner State Execution Spike  opt-in 状态执行层评估  已收口
    ↓
v0.8.10-B Runner State Execution MVP    最小状态执行层        已收口
    ↓
v0.9.0-alpha Long Novel Creation Loop   长篇共创闭环        进行中：Chapter Export 已收口
```

当前最重要的判断：

> v0.7 Product Web App 九刀已把普通用户主闭环跑通；v0.7.2 至 v0.7.5 已完成 Agent Interaction、Visual Asset Generation、Baseline & Canon Replay、Worldline Judge。v0.8 已完成 Long Novel Memory artifact 底座、四个 v0.8+ 机制底座、`memory/entity_aliases.yaml` / entity resolution 第一刀、`runtime_memory_context.json` 运行时只读消费第一刀、右侧「机制档案」统一 artifact 解释层、txt/md/zip/epub 长篇上传产品化、**v0.8.6 Long Import Review**、**v0.8.7 Resumable Ingest Jobs**、**v0.8.8 Long Project Workspace**、**v0.8.9 Long Replay & Audit UI**，以及 **v0.8.10-A/B Runner State Execution**：长篇项目已支持项目资产页、章节范围回放、风险维度、实体归一化审计、状态执行 dry-run 评估和显式 opt-in 的状态 overlay 写入/回滚。当前后端基线为 **598 passed**，前端 build 通过。**v0.9.0-alpha Long Novel Creation Loop 已启动**，Chapter Export 子刀已提供只读章节导出 API 与前端导出入口；完整长篇共创闭环尚未整体收口。

## 2.1 阶段性质与产品化程度

完整口径见 `docs/productization-phase-map.md`。本路线图采用以下判断：

| 阶段 | 阶段性质 | 产品化程度 | 当前判断 |
| --- | --- | --- | --- |
| v0.1-v0.3 | CLI、导入、检索、状态与续章底座 | 技术 MVP | 证明核心链路能运行，不是完整产品。 |
| v0.4-v0.4.2 | 只读世界线浏览器与检索展示 | 研发/演示产品化 | 可浏览产物，但仍偏开发者 viewer。 |
| v0.5-v0.6.5 | 第四面墙、SceneRunner、多 Agent 协议/runner | 引擎机制 MVP | 机制可审计、可演示，普通用户入口仍不完整。 |
| v0.7-v0.7.5 | Product Web App + 交互/视觉/评审层 | 短中篇产品化 MVP | 第一轮真正面向普通用户的产品化闭环已成立。 |
| v0.8.0-A-v0.8.5-A | Long Novel Memory、canon、retrieval、audit、holdout | 长篇引擎底座 MVP | 长篇记忆和正史能力成立，但仍偏 artifact/API。 |
| v0.8+ A-slices | ActDirector、Narrator diagnostics、Action Registry、Emergence、Aliases、Runtime Memory | 机制接缝与解释层 MVP | A-slice 已可验收，但默认不代表强状态执行或复杂 runner。 |
| v0.8.6-v0.8.10 | 导入检查、断点任务、项目页、审计 UI、runner 状态执行评估 | 长篇产品化收束 | 把长篇底座变成用户可理解、可修复、可继续创作的工作流。 |
| v0.9.0-alpha | Long Novel Creation Loop | 长篇产品化闭环成立 | 进行中：Chapter Export 已走通；上传/创建 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出整体闭环仍是 alpha。 |
| v0.9.1-v0.9.4 | Provider/Cost、MasterSetting、Graph Memory、Advanced Runner | 真实使用压力增强 | 按成本、召回、设定管理、runner 复杂度触发，不提前重依赖。 |
| v1.0-beta | Commercial Hardening | 商业级/规模化 | 账号、权限、云端持久化、配额、审计、版权、部署观测。 |

因此，“已经完成 MVP”需要带限定语：v0.7 已完成短中篇产品化 MVP，v0.8.0-A 至 v0.8.5-A 已完成长篇底座 MVP；v0.8.6-v0.8.10 是长篇产品化收束，v0.9.0-alpha 才是长篇共创产品闭环成立。

## 3. 已完成能力

| 里程碑 | 内容 | 状态 |
| --- | --- | --- |
| Phase 0 Alpha | CLI、`lne list-samples` / `show-sample` / `intervene` / `compare`、内置样例《天荒城残夜》、三分支、mock + 真实 LLM | 已完成 |
| Phase 0 Beta | 状态渲染器、快照钳制、玉简/示警锁、章节非空兜底 | 已完成 |
| v0.1.1 polish | 快照 `location` 同步、天荒城/玉简措辞、正史锁、重生禁用、退魂铃来源、墨青烟错字修正 | 已完成 |
| v0.1.2 resume continue | `lne resume continue <run_id> --branch branch_a`，父链 `meta.json`，`linear/` 续章 | 已完成 |
| v0.1.3 resume intervene | `lne resume intervene <continue_run_id> --branch linear`，续章上再干预三分叉 | 已完成 |
| v0.2 import-novel | `import-novel` / `validate-project` / `load_story` / imported `intervene` / LLM 抽取 | 已完成 |
| v0.2.1 resume imported | `resume continue` / `resume intervene` 支持 imported projects | 已完成 |
| v0.2.2 精华固化 | genre_templates / facts.jsonl / summaries / story_contract.yaml / absorption report | 已完成 |
| v0.4 世界线浏览器 | `lne browse` 只读 Web UI / HTTP API / 世界线树 / 章节阅读 / 角色状态 / 分支对比 | 已完成 |
| v0.4.1 边界加固 | 路径校验 validators.py / 树排序稳定 / 前端不白屏 / 37 参数化安全测试 | 已完成 |
| v0.3.0 Context Retrieval Lite | BM25 检索 + 章节距离衰减 + facts/summaries/contract 注入 prompt | 已完成 |
| v0.3.1 检索 artifact + Brief | retrieval_context.json 写盘 / source_weight / VolumeBrief 检索 | 已完成 |
| v0.4.2 检索记忆展示 | browse「检索记忆」标签页按 source 分组展示命中与分数 | 已完成 |
| v0.5 第四面墙 | 干预记忆账本 / 四触发器 / 五级觉察 / 决策与渲染注入 / env 开关 | 已完成 |
| v0.5.1 第四面墙关闭语义 | `LNE_FOURTH_WALL=0` 不累积/不落盘/不泄漏 snapshot | 已完成 |
| v0.6.0 Runner Adapter | `SceneRequest` / `SceneRunner` / 注册表 / `dispatch_scene` / env 切换 / 契约 additive | 已完成 |
| v0.6.1 Multi-Agent Protocol | `protocol.py` 数据结构骨架 + 设计文档；私有/误解默认不泄漏；未接入运行 | 已完成 |
| v0.6.2 multi_agent_stub | `projection.py` + `multi_agent_stub` runner；协议→投影→契约；非默认；私有不泄漏 | 已完成 |
| v0.6.3 trace 可视化 | browse「Agent 轨迹」标签页 + 树角标；缺失空态/损坏不抛；additive API | 已完成 |
| v0.6.4 multi_agent_llm | 共享装配层 + 小模型推演 `MultiAgentTrace`；非默认；隐私加固 + 健壮回退 | 已完成 |
| v0.6.5 推演工程可靠性 | generation_meta + trace 质量校验器 + 有限重试 + token usage；不引新依赖 | 已完成 |
| v0.7.1-A Intervention Compiler | rule-based 自由干预编译；`AbstractIntervention` / compatibility / realization / dynamic BranchAxis / affected_scope | 已完成 |
| v0.7.1-B LLM Compiler | 真实 LLM 编译 + rule-based fallback + `generation_meta`；rule_rewrite 安全兜底不污染原世界线 | 已完成 |
| v0.7.1-C Causal Diff | `causal_diff.json` 后端 artifact；段落级 old/new diff；为确立/抹除/回滚预留生命周期字段 | 已完成 |
| v0.7 Product Web App | React/Vite 产品级 Web App；Web 导入/创世/锚定/干预/Causal Diff/设置/异步 Job 主闭环 | 已完成 |
| v0.7.2 Agent Interaction | CharacterAction / CharacterProbe / InterventionGuardrail / 轻量角色配置 UI | 已完成 |
| v0.7.3 Visual Asset Generation | Seedream 视觉资产增强层，封面/头像/场景图，可降级占位 | 已完成 |
| v0.7.4 Baseline & Canon Replay | 无干预基线 + 正史 holdout + deterministic 回放评估 | 已完成 |
| v0.7.5 Worldline Judge | branch 级世界线评分、故事弧、转折点、`emergence_score` | 已完成 |
| v0.8.0-A 至 v0.8.5-A | 长篇导入报告、分层记忆、canon ledger、账本检索、静态审计、holdout 可见性隔离 | 已完成 |
| v0.8+ ActDirector-A | `act_director_plan.json`，抽象干预到角色动作计划 artifact | 已完成 |
| v0.8+ Discourse-aware Narrator-A | `narrative_diagnostics.json`，分支正文节奏/转折/张力诊断 | 已完成 |
| v0.8+ Dynamic Action Registry-A | `dynamic_action_registry.yaml`，动作类型/别名/前置/效果/失败/修复汇总 | 已完成 |
| v0.8+ Emergence Mining-A | `emergence_nodes.json`，run 级候选涌现节点汇总与 API | 已完成 |

**版本收口参考 run（验收用）**

| 版本 | 参考 run_id | 说明 |
| --- | --- | --- |
| v0.1.2 | `run_20260528_155153_c3275c_continue_branch_a` | 从 `branch_a` 无新干预续写 `linear/` |
| v0.1.3 | `run_20260528_171207_94a6b9_resume_intervene_linear` | 从续章 `linear` 再干预，生成第十五章三分叉 |

**测试基线**：`cd engine && python -m pytest -q` → **598 passed**（截至 2026-05-31，v0.9.0-alpha Chapter Export 子刀后完整回归通过）；`cd engine/ui && pnpm run build` 通过。

当前用户可演示的闭环：

```text
# 内置样例
lne intervene tianhuang-night -> branch_a/b/c -> resume continue -> resume intervene

# 导入项目（v0.2 完整链路）
lne import-novel tests/fixtures/mini_novel/ --name my-story --genre xianxia --mock
lne validate-project my-story
lne intervene my-story --target zhao_xuan --content "..." --mock
lne resume continue <run_id> --branch branch_a --mock
lne resume intervene <continue_run_id> --branch linear --target shen_bing_yue --content "..." --mock

# 题材模板
lne list-genres
```

当前刻意未完成的能力：

- ChapterBrief / VolumeBrief 已接入检索语料；摘要内容仍为导入占位，质量提升留后续。
- 检索结果已写入各分支 `retrieval_context.json`，并由 `lne browse`「检索记忆」标签页展示（v0.4.2 完成）。
- 第四面墙数值、干预记忆、override ledger 已在 v0.5 驱动角色决策与章节渲染；browse 展示 fourth_wall 段留后续。
- 多场景长程仿真 / MiroFish OASIS 尚未接入（v0.6）。
- 旧 `lne browse` 仍是研发/演示 viewer；普通用户产品前端已由 v0.7 `engine/ui` 承接。
- embedding / 向量库 / reranker 尚未做，留到 v0.9.3 Graph Memory Evaluation Spike；多 provider gateway 留到 v0.9.1 Provider & Cost Gateway Lite。

## 4. 三个参考项目的定位

### 4.1 WenShape：长篇上下文与文本导入参考

WenShape 是“深度上下文感知的智能体小说创作系统”，更像作者工作台。它的价值不在于读者干预，而在于长篇写作工程化：

- 卷、章节、草稿、摘要的结构化管理。
- 人物卡、世界观卡、文风卡。
- `facts.jsonl` 事实库。
- 章节摘要、证据索引、BM25、实体增强、章节距离衰减。
- 同人导入时的搜索、预览、抓取、proposal、人工确认。
- 多 provider LLM Gateway。

Living Novel Engine 应该吸收它的“长篇上下文骨架”，尤其用于 v0.2：

```text
import-novel
  -> chapters/
  -> cards/characters
  -> cards/world
  -> cards/style
  -> canon/facts.jsonl
  -> summaries/
  -> anchor_proposal.yaml
  -> 用户确认
```

但不要把产品做成另一个作者工作台。我们的差异是：

```text
WenShape：帮助作者更稳定地写长篇
Living Novel Engine：让读者进入长篇，干预命运，生成自己的世界线
```

### 4.2 webnovel-writer：故事合约与网文渲染参考

webnovel-writer 更接近 Claude Code 插件式网文生产系统。它适合提供这些启发：

- Story Contract：世界规则、人设边界、战力体系、伏笔约束。
- Chapter Commit：每章生成后把事件投影回长期状态。
- 题材模板：修仙、都市、玄幻等网文风格提示。
- data-agent 五元组：`accepted_events`、`state_deltas`、`entity_deltas`、`scenes`、`summary_text`。

Living Novel Engine 应借鉴它作为“故事合约层 + 章节状态提交层”，但不直接依赖 Claude Code 插件运行时。

### 4.3 MiroFish：多 Agent 沙盘推演参考

MiroFish 的价值是“角色群体自己动起来”：

- OASIS / CAMEL 多 Agent 调度。
- 虚拟社区与群体仿真。
- 长效记忆、关系、动机和对话。
- 多角色在同一场景里互相影响。

本地源码扫描结论（2026-05-29）：

- MiroFish 的 LLM 调用主路径是 **OpenAI SDK 兼容 API**：`LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL_NAME`，示例推荐 DashScope `qwen-plus`；并不要求本地部署模型。
- 它用 Zep Cloud 做图谱/记忆，用 OASIS / CAMEL 做 Twitter/Reddit 式群体仿真；并支持 `LLM_BOOST_*` 作为并行模拟加速配置。
- OASIS / CAMEL 的主抽象偏社交平台环境（agent graph、active agents、`LLMAction()`、`env.step(actions)`），与 LNE 的小说场景推演有相似处，但不应直接成为主线依赖。

Living Novel Engine 已在 v0.6.0-v0.6.3 建好自研 runner adapter / protocol / projection / trace UI。短期不接 MiroFish，是因为它会增加账号、服务部署、数据同步、环境适配和调试成本；LNE 当前更需要验证“叙事专用多 Agent”是否能提升角色计划、误解、隐瞒、延迟行动和关系传播。

LangGraph 取舍（2026-05-29）：

- MiroFish 本地源码主线不是 LangGraph；多 Agent 沙盘靠 OASIS / CAMEL，报告生成处有 LangChain + Zep 的 ReACT 注释，但不是 LangGraph。
- webnovel-writer 更像 Claude Code 式写作流水线；WenShape 更像长篇上下文工程 / 作者工作台；两者都不是 LangGraph 主线。
- LNE 前期继续使用自研精简智能体协议（`SceneRunner` + `MultiAgentTrace` + `project_trace`），保持叙事契约、输出文件和 resume lineage 可控。
- 中后期如果出现复杂状态流转（角色并行思考、裁判节点、规则审计节点、反思/重试节点、多轮共识），可在 v0.9.4 Advanced Runner Evaluation Spike 局部评估 LangGraph 作为某个 opt-in runner 的内部实现，而不是替换主线协议。

因此后续策略是：

- v0.6.4 已完成自研 `multi_agent_llm` runner：通过 OpenAI-compatible API 调用小模型，不本地部署；输出 `MultiAgentTrace` JSON；复用现有 `project_trace` 与共享装配层。
- v0.6.5 已完成推演工程可靠性：generation_meta、trace 质量校验器、有限重试、token usage；并发与精确成本计算留待 v0.8+。
- v0.9.3 若长篇记忆 / BM25 / canon ledger 召回崩，再评估 Zep / 图数据库 / GraphRAG；v0.9.4 若群体仿真需求很强，再评估 OASIS / CAMEL 作为可选 runner。

### 4.4 autonovel / AI_NovelGenerator：静态写稿流水线，仅保留边角料价值

2026-05-29 新增调研判断：`autonovel` 与 `AI_NovelGenerator` 不应进入 Living Novel Engine 的核心架构。

它们的本质更接近 **Static Pipeline（作者向静态写稿流水线）**：

```text
设定生成 -> 大纲生成 -> 章节扩写 -> 审校/润色 -> 导出
```

而 LNE 的核心是 **Simulation & Interaction（命运沙盘 + 平行宇宙 + 读者高维干预）**：

```text
世界状态 -> 角色动机 -> 多 Agent 推演 -> 读者施加变量 -> 世界线分叉 -> 状态继续运行
```

两类系统的核心交互视角不同：

| 项目 | 核心用户 | 核心问题 | 与 LNE 的关系 |
| --- | --- | --- | --- |
| autonovel | 作者 / 自动写作研究者 | 如何从 seed 自动生产一本完整小说 | 不作为主线，只借鉴评审团与质量循环 |
| AI_NovelGenerator | 普通作者 / GUI 写作用户 | 如何按设定、大纲、章节持续生成文本 | 不作为主线，只借鉴上下文压缩与一致性检查 |
| Living Novel Engine | 读者 / 干预者 / 互动叙事用户 | 如何让小说世界继续运行，并允许读者改变命运 | 主线 |

因此二者的整体参考价值有限，不能把 LNE 拉回“普通 AI 续写器 / 作者工作台”的低维竞争里。后续不深挖其全量架构，不复制源码，不引入运行时依赖。

但它们仍有两个可吸收的组件级经验：

#### 4.4.1 Reader/Critic Panel：转化为 Worldline Judge

`autonovel` 的读者/编辑评审团机制可以转化为 LNE 的世界线评审层。

在三条世界线生成后，不只输出正文，还让若干虚拟评审视角评价：

- 网文编辑：节奏、追读力、爽点、钩子。
- 类型读者：是否想继续看，是否觉得水。
- 故事合约审计员：人设、战力、世界规则是否冲突。
- 命运沙盘观察者：哪条世界线更有继续运行的潜力。

目标不是替作者改稿，而是帮助读者理解：

```text
branch_a：最爽，但合约风险较高
branch_b：最符合角色逻辑，但节奏慢
branch_c：代价最大，后续冲突潜力最高
```

该能力可排到 v0.7 之后，作为 **v0.7.5 Worldline Judge** 或 v0.8 质量层的一部分。

#### 4.4.2 Context Compression：转化为长程沙盘记忆压缩

`AI_NovelGenerator` 一类项目常见的动态摘要、角色状态、剧情要点维护，可以转化为 LNE 的长程上下文压缩。

LNE 不需要复刻普通写作器的章节生成链，但需要处理 100+ 章后的记忆分层：

```text
最近 1-3 章：Tick Memory，即时记忆，高权重注入
最近 10-20 章：Scene Memory，近期局势，摘要注入
更早章节：Background Lore，长期背景，按角色/伏笔检索
不可变设定：Story Contract，永不衰减
```

这与 v0.3 已有的 `facts.jsonl`、`summaries/`、`story_contract.yaml` 一脉相承，后续只需增强压缩策略，不需要改成 NovelGenerator 式“大纲续写器”。

#### 4.4.3 后续研读边界

后续可以开研究文档，但只回答这几个问题：

```text
docs/research/
├── autonovel-static-pipeline-triage.md
└── ai-novel-generator-context-triage.md
```

研读范围：

- 哪些评审指标可转化为 `worldline_judgement.json`。
- 哪些反 AI 腔 / 反水文规则可转化为 narrator 后处理。
- 哪些上下文压缩策略可服务长程沙盘。
- 哪些一致性检查可增强 `contract_audit`。

明确不做：

- 不复刻一键生成整本书流水线。
- 不把 LNE 变成作者参数面板。
- 不把“角色动机驱动”退化成“上文预测下文”。
- 不复制 AGPL / 其他强约束项目源码。

### 4.5 eastworld：互动媒体 Agent 协议与 Agent Studio 参考

2026-05-29 新增调研判断：`eastworld` 比 `autonovel` / `AI_NovelGenerator` 更接近 LNE 的未来方向，但也不应直接接入主线服务。

`eastworld` 的定位是给游戏、视觉小说和互动媒体接入 Generative Agents。它强调的不是“帮作者写完小说”，而是：

- Agent 可以执行用户定义动作，不只是聊天。
- 可以查询 Agent 内心想法和情绪。
- 可以用 guardrails 限制玩家越界输入。
- 用 no-code Agent Studio 配置角色传记、核心信念、口癖、共享世界知识和可执行动作。
- 通过 FastAPI / OpenAPI 暴露小 API 给游戏或前端调用。

这与 LNE 的 `MultiAgentTrace`、第四面墙、干预护栏和 v0.7 Product Web App 有较高相关性。

但 `eastworld` 仍然不适合作为 LNE 的运行时底座：

| 维度 | eastworld | LNE 取舍 |
| --- | --- | --- |
| 产品场景 | 游戏 / 视觉小说 / 互动媒体 Agent 框架 | LNE 是活体小说世界运行时 |
| 核心交互 | 玩家与角色实时互动 | 读者干预世界线，角色消化变量 |
| 技术形态 | FastAPI + Redis + Agent Studio + OpenAPI client | LNE 当前保持本地文件产物 + CLI/API + 自研 runner 协议 |
| 值得吸收 | Actions、Emotion Query、Guardrails、Agent Studio UX | 作为 v0.7.2+ 的交互协议和 UI 参考 |
| 不做 | 直接接入 eastworld server / Redis / client 生成链 | 避免增加服务复杂度和外部源码依赖 |

#### 4.5.1 Agent Actions：转化为角色可执行动作

`eastworld` 的 Agent Actions 可转化为 LNE 的结构化角色动作协议。

当前 LNE 的角色推演已经能生成事件和 trace，但后续可进一步将角色行为标准化为可审计动作：

```json
{
  "character_id": "lin_wan_zhou",
  "action": "investigate",
  "target": "bamboo_forest",
  "reason": "她不完全相信低语，但退魂铃异常让她决定先查证",
  "visibility": "private",
  "risk": "medium"
}
```

可选动作示例：

- `investigate`：调查地点、人物、物品。
- `warn`：提醒或警告某角色。
- `conceal`：隐藏信息。
- `negotiate`：谈判。
- `attack`：攻击或伏击。
- `retreat`：撤退。
- `observe`：暗中观察。
- `seek_ally`：寻找盟友。
- `break_contract`：尝试越界行为，触发合约审计。

价值：

- 角色不再只是“生成一段话”，而是先生成可校验动作。
- `contract_audit` 可以审计动作是否合法。
- Web UI 可以展示“角色为什么这么做”。
- 后续可把动作映射成世界状态变化，而不是直接写正文。

#### 4.5.2 Emotion Query：转化为角色内心探针

`eastworld` 的 Emotion Query 可转化为 LNE 的 `Character Probe`。

用户或系统可以查询：

- 角色有多相信这次干预。
- 角色对某人的信任度、怀疑度、恐惧值。
- 角色是否察觉命运异常。
- 角色是否愿意违背某个约定。
- 角色当前最强烈的欲望或恐惧是什么。

示例输出：

```json
{
  "character_id": "lin_wan_zhou",
  "probe": "belief_in_intervention",
  "score": 0.62,
  "explanation": "她不相信虚空低语本身，但退魂铃异常与旧约时间冲突让她愿意延迟行动。"
}
```

价值：

- 解释角色为何相信、怀疑或拒绝读者干预。
- 强化第四面墙机制的可见性。
- 帮助用户从“命令角色”转向“理解角色”。

#### 4.5.3 Player Guardrails：转化为干预护栏

`eastworld` 的玩家护栏可以转化为 LNE 的 `Intervention Guardrails`。

干预不是用户想写什么就写什么，而必须经过故事合约和题材边界过滤：

- 修仙世界不能无条件投放现代手枪，除非合约允许科技或穿越。
- 练气期角色不能突然获得仙帝战力。
- 用户不能强行让角色爱上仇人，只能制造变量。
- 读者低语不能直接覆盖角色记忆，只能作为感知输入。
- 违背时代、题材、世界规则的干预要降级为梦境、谣言、误解或无效变量。

这可以增强现有 `contract_audit`：

```text
raw intervention
  -> guardrail classify
  -> repair suggestion
  -> contract audit
  -> inject as safe variable
```

#### 4.5.4 Agent Studio：转化为轻量角色配置 UI

`eastworld` 的 Agent Studio 对 v0.7 Product Web App 很有启发，但 LNE 不应做完整作者工作台。

LNE 只需要一个“运行活体小说所需”的轻量配置界面：

- 角色基本信息。
- 核心信念 / 欲望 / 恐惧。
- 角色知道什么、不知道什么。
- 角色可执行动作列表。
- 口癖与说话方式。
- 合约边界。
- 第四面墙觉察开关与阈值。

暂不做：

- 不做游戏引擎 SDK。
- 不做完整 no-code Agent 平台。
- 不接 Redis / eastworld server。
- 不自动生成 OpenAPI client。

#### 4.5.5 后续研读边界

新增研究文档：

```text
docs/research/eastworld-agent-interaction-triage.md
```

研读范围：

- Agent Actions 如何建模为 LNE 的 `CharacterAction`。
- Emotion Query 如何建模为 `CharacterProbe`。
- Player Guardrails 如何增强 `contract_audit`。
- Agent Studio 哪些配置项适合进入 v0.7 Product Web App。
- FastAPI / OpenAPI 的 API 边界是否可借鉴，但不直接复用。

明确不做：

- 不把 eastworld 当作 LNE 后端。
- 不接入 eastworld Redis / server / generated client。
- 不把 LNE 产品方向改成游戏 NPC 框架。
- 不复制源码，只吸收交互协议和 UI 设计。

### 4.5.6 Intervention Compiler：自由干预到动态分支轴

早期内置样例采用 `believe / doubt / reject` 三分支，是为了验证“高维低语 / 预知信息”这种**信息型干预**。它不能成为长期产品规则。

LNE 的真实交互应该是：用户随便输入干预，系统先把它编译成符合世界观的结构化变量，再由角色和世界状态消化。

```text
Raw Reader Input
  -> AbstractIntervention
  -> InterventionGuardrail / Story Contract Audit
  -> In-world Realization
  -> Branch Axis
  -> Worldlines
```

#### 干预类型与分支轴

| 干预类型 | 示例 | 分支轴不应固定为 | 应生成的本次分支轴 |
| --- | --- | --- | --- |
| 信息型干预 | 告诉角色未来会发生某事 | 永远相信 / 怀疑 / 拒绝 | 相信预知 / 怀疑但调查 / 拒绝预兆 |
| 强制行动型干预 | 让角色某时某刻必须做或不做某事 | 相信 / 不信 | 主动改道 / 被迫延迟 / 抗拒命运压力 / 干预失败但觉察异常 |
| 资源或物品注入 | 让角色捡到一件物品 | 相信 / 不信 | 同世界合理吸收 / 降级转译 / 拒绝 / 开启异设世界线 |
| 规则改写型干预 | 赋予系统、现代武器、穿越者身份 | 普通分叉 | 拒绝原世界线 / 转译成本世界规则 / 另开 Alternate Novel |

#### 世界线类型

```text
Divergent Worldline
  在原世界规则内分叉。
  例如：预知梦、低语、谣言、误会、提前示警、角色改变选择。

Alternate Novel / AU Worldline
  改写世界前提、题材规则或基础物理/修炼体系。
  例如：系统降临、AK47 进入中世纪、现代人穿越、主角获得完全不属于原作的外挂。
```

判断规则：

- 如果干预能被世界观自然吸收，优先进入 `Divergent Worldline`。
- 如果干预违反时代、题材、战力或核心合约，但可被转译，先给出降级方案。
- 如果用户坚持改写前提，系统应另开 `Alternate Novel / AU Worldline`，并记录与原 story_contract 的差异，而不是把它伪装成普通分支。
- UI 必须向用户解释：系统理解成了什么 `AbstractIntervention`，为什么生成这些分支轴。

#### 数据结构预留

```json
{
  "abstract_intervention": {
    "intent": "prevent_character_from_entering_trap",
    "input_mode": "free_text",
    "intervention_type": "forced_action",
    "target_refs": ["lin_wan_zhou"],
    "desired_effect": "avoid_bamboo_grove",
    "hard_result": false
  },
  "compatibility": {
    "status": "partial",
    "risk": "medium",
    "reasons": ["角色不知道竹林埋伏", "可通过梦境或道具异常转译"]
  },
  "realization": {
    "mode": "omen_and_delay",
    "description": "退魂铃异常 + 预知梦 + 道心不安"
  },
  "branch_axis": [
    {"id": "avoid", "label": "主动避开"},
    {"id": "investigate", "label": "延迟调查"},
    {"id": "resist", "label": "抗拒预兆，照旧赴约"}
  ],
  "lineage_type": "divergent_worldline"
}
```

排期落点：

- v0.7：产品前端展示“系统理解 / 世界观兼容性 / 本次分支轴”，避免用户误以为只能点固定选项。
- v0.7.1：实现最小 `InterventionCompiler`，替代固定 believe/doubt/reject 的 UI 心智；CLI 可先保持兼容。
- v0.7.2：把 `InterventionCompiler` 接入 `InterventionGuardrail`、`CharacterActionSequence` 与 preconditions/effects。
- v0.8：`ActDirector` 负责将 `AbstractIntervention` 稳定实例化为角色动作序列，并支持 `Alternate Novel` 的新合约差异。

### 4.6 学术论文底座：从“参考项目”升级到“系统机制”

2026-05-29 已完成四篇论文研读，报告位于：

```text
docs/article/reports/
├── 2404.17027v3-player-driven-emergence-report.md
├── 2405.13042v2-storyverse-report.md
├── 2407.13248v2-human-level-narratives-report.md
└── 2505.03547v1-story2game-report.md
```

四篇论文分别补上 LNE 的四个理论与工程缺口：

| 论文 | 回答的问题 | 对 LNE 的系统意义 | 排期落点 |
| --- | --- | --- | --- |
| Player-Driven Emergence in LLM-Driven Game Narrative | 用户自由干预是否会产生有价值的新剧情 | 将读者干预视为涌现节点和玩家欲望路径，而不是噪声 | v0.7 / v0.7.5 |
| StoryVerse | 如何平衡作者/读者意图与角色自主行动 | 引入 `AbstractIntervention` / `ActDirector`，把高层意图实例化为角色动作序列 | v0.7.2 / v0.8 |
| Are LLMs Capable of Generating Human-Level Narratives? | AI 故事为什么容易平、早收束、缺悬念 | 引入故事弧、转折点、张力、节奏评估，增强 `Worldline Judge` | v0.7.5 / v0.8 |
| STORY2GAME | 开放动作如何落到可执行世界状态 | 为 `CharacterAction` 增加 preconditions / effects / failure reason / repair suggestions | v0.7.2 / v0.8 |

#### 4.6.1 Player-Driven Emergence：涌现节点与世界线分歧

核心结论：

> 玩家和 LLM NPC 自由互动时，会创造设计者没有预设的新路径；这些路径反映玩家真实欲望，可作为系统迭代素材。

LNE 吸收方向：

- 新增 `emergence_nodes.json`，记录读者干预产生的非正史新节点。
- 世界线树展示 `canon node` / `emergent node`。
- `compare.md` 或 Web UI 展示每条分支的 `divergence_reason`。
- `Worldline Judge` 增加 `emergence_score`。

建议数据结构：

```json
{
  "node_id": "em_001",
  "source": "reader_intervention",
  "description": "林晚舟派纸鹤探查竹林而不是直接赴约",
  "category": "creative_information_gathering",
  "canon_status": "branch_only",
  "design_value": "high"
}
```

排期：

- v0.7：Web UI 展示分歧节点与分叉原因。
- v0.7.5：`Worldline Judge` 评估分支涌现价值。
- v0.8+：沉淀高价值涌现节点，形成世界线模板或推荐。

> **v0.8+ Emergence Mining-A 已落地（2026-05-30）**：先做 run 级 deterministic `emergence_nodes.json`，不做社区推荐系统。新增 `emergence_mining/` 包，从 `intervention.json`、`intervention_compilation.json`、`dynamic_action_registry.yaml`、分支 `causal_diff.json`、`worldline_judgement.json`、`narrative_diagnostics.json` 汇总候选涌现节点；`run_intervention()` 自动写报告，HTTP `POST/GET /api/runs/<run_id>/emergence-nodes` 支持重建/读取。已验证：`tests/test_v089_emergence_mining.py` 4 passed。

#### 4.6.2 StoryVerse：抽象意图到具体角色动作

核心结论：

> 不要让作者/读者直接指定角色动作，而应先表达高层剧情意图，再由系统结合世界状态实例化为具体角色行动序列。

LNE 吸收方向：

```text
raw reader input
  -> AbstractIntervention
  -> ActDirector
  -> CharacterActionSequence
  -> AcceptedEvents
  -> Chapter
```

建议数据结构：

```json
{
  "intent": "prevent_character_from_entering_trap",
  "target": "lin_wan_zhou",
  "desired_effect": "raise_suspicion",
  "hard_result": false,
  "acceptable_resolutions": ["believe", "investigate", "ignore", "misinterpret"]
}
```

排期：

- v0.7.2：在 `InterventionGuardrail` 后增加 `AbstractIntervention`。
- v0.7.2：将干预意图转为 `CharacterActionSequence`。
- v0.8+：实现轻量 `ActDirector`，协调读者意图、角色仿真、世界状态和故事合约。

> **v0.8+ ActDirector-A 已落地（2026-05-30）**：先做 deterministic planning artifact，不接 runner 主链路。新增 `act_director/` 包，`plan_character_actions()` 将 `InterventionCompilation` 转成 `CharacterActionPlan`，每个 branch axis / target 生成带 `preconditions`、`effects`、`risk`、`visibility`、`repair_suggestions` 的动作计划；`run_intervention()` 写出 `act_director_plan.json` 并在 service result extra 中返回摘要。已验证：`tests/test_v086_act_director.py` 3 passed；干预编译/API/CharacterAction 回归 50 passed。

#### 4.6.3 Human-Level Narratives：故事弧与转折点评审

核心结论：

> LLM 默认生成的故事往往过于正向、过早解决冲突、缺少重大挫败和悬念；显式加入故事弧和转折点规划能显著提升叙事质量。

LNE 吸收方向：

- `Worldline Judge` 增加故事弧类型：
  `Rags to Riches`、`Riches to Rags`、`Man in a Hole`、`Double Man in a Hole`、`Icarus`、`Cinderella`、`Oedipus`。
- 增加五类 turning points：
  `Opportunity`、`Change of Plans`、`Point of No Return`、`Major Setback`、`Climax`。
- 评估每条分支是否太平、是否过早收束、是否缺少重大挫败。
- narrator 加入“不要同章解决全部冲突”的规则。

建议数据结构：

```json
{
  "arc_type": "man_in_a_hole",
  "turning_points": {
    "tp1": "林晚舟收到低语",
    "tp2": "她改变赴约计划",
    "tp3": "她公开违抗旧约",
    "tp4": "纸鹤暴露导致反派提前收网"
  },
  "missing_turning_points": ["climax"],
  "tension_score": 0.74,
  "pacing_warnings": ["tp4_and_tp5_too_close"]
}
```

排期：

- v0.7.5：`worldline_judgement.json` 加入 `narrative_discourse`。
- v0.7.5：`compare.md` 展示每条线的故事弧和张力风险。
- v0.8+：`worldline_brancher` 按不同故事弧生成分支，避免三条线换皮。
- v0.8+：narrator 采用 outline -> turning points -> chapter 的两阶段生成。

> **v0.8+ Discourse-aware Narrator-A 已落地（2026-05-30）**：先做写后诊断 artifact，不重写 narrator。新增 `narrative_diagnostics/` 包，`analyze_narrative()` 统计字数、句数、段落、对话标记、转折标记、pacing 和 tension curve，并给出 warnings/suggestions；`output.writer._write_branch_outputs()` 在每个分支写 `narrative_diagnostics.json`。已验证：`tests/test_v087_narrative_diagnostics.py` 2 passed；输出写盘/干预/基线/检索相关回归 62 passed。

#### 4.6.4 STORY2GAME：动作前置条件与效果

核心结论：

> 开放文本行动不能直接变成正文，必须先变成可检查、可执行、可失败、可降级的动作。

LNE 吸收方向：

- `CharacterAction` 增加 `preconditions` 和 `effects`。
- `InterventionGuardrail` 不只是拦截，还要给 `failure_reason` 和 `repair_suggestions`。
- 动作执行后转为 `StateDelta` / `AcceptedEvent`。
- 动态动作进入 action registry，解决“用户提出系统未预设动作”的情况。

建议数据结构：

```json
{
  "action_id": "act_001",
  "actor_id": "lin_wan_zhou",
  "verb": "investigate",
  "target_refs": ["bamboo_forest"],
  "preconditions": [
    "lin_wan_zhou.has_item(retreat_soul_bell)",
    "bamboo_forest.status != inaccessible"
  ],
  "effects": [
    "thread.trap_exposed += 0.4",
    "lin_wan_zhou.suspicion += 0.3"
  ],
  "failure_reason": null,
  "repair_suggestions": []
}
```

排期：

- v0.7.2：`CharacterAction` 增加 preconditions/effects。
- v0.7.2：越界动作给出失败原因和降级建议。
- v0.8+：增加 `dynamic_action_registry.yaml` 和 `entity_aliases.yaml`。
- v0.8+：做 entity resolution，避免同一物品/地点多名称导致状态断裂。

> **v0.8+ Dynamic Action Registry-A 已落地（2026-05-30）**：先做 deterministic registry artifact，不接 runner 执行层。新增 `dynamic_action_registry/` 包，`build_action_registry()` 从 `CharacterActionPlan` 汇总动作类型、中文别名、前置条件、效果、失败原因、修复建议、风险等级与来源 step；`run_intervention()` 写出 `dynamic_action_registry.yaml` 并在 service result extra 中返回摘要。已验证：`tests/test_v088_dynamic_action_registry.py` 2 passed。

## 5. 版本路线图

### v0.1.2：Resume Continue（已收口 · 2026-05-28）

目标：从“一次干预 demo”升级成“选定世界线后还能继续写下一章”。

第一版只做无新干预续章：

```bash
lne resume continue <run_id> --branch branch_a
```

输入：

- 父 run 的 `intervention.json`
- 目标分支的 `state_snapshot.json`
- 目标分支的 `events.json`
- 目标分支的 `chapter.md`
- 样例世界原始设定

输出建议：

```text
outputs/run_<timestamp>_continue_branch_a/
├── meta.json
├── parent_snapshot.json
├── parent_chapter.md
└── linear/
    ├── events.json
    ├── state_snapshot.json
    ├── chapter.md
    └── summary.md
```

验收标准：

- 能读取父分支状态并生成下一章。
- 新章节不回滚父分支已发生事件。
- 角色位置、情绪、关系、伏笔状态能延续。
- `meta.json` 记录父 run、父 branch、lineage。
- mock 模式可稳定跑测试。
- 真实 LLM 模式章节可读，不出现明显正史冲突。

产品价值：

- 证明世界线不是一次性生成物，而是可继续运行的故事状态。
- 对内/对外 demo 叙事完整度提升最大。

### v0.1.3：Resume Intervene（已收口 · 2026-05-28）

目标：在已选世界线上再次干预，并生成新的分支。

命令设计：

```bash
lne resume intervene <run_id> \
  --branch branch_a \
  --target lin_wan_zhou \
  --type dream_hint \
  --content "梦中有人告诉她，真正的叛徒不在竹林，而在山门"
```

内部流程：

```text
读取父分支状态
  -> 将父分支作为新正史
  -> 解析新干预
  -> 合约审计
  -> 生成 2-3 条子世界线
  -> 输出新的 run
```

验收标准：

- 子 run 能追溯到父 run 和父 branch。
- 分支树可被后续 UI 读取。
- 新干预不是覆盖历史，而是在历史之后注入变量。
- 至少一条分支体现角色相信，一条分支体现怀疑或拒绝。

产品价值：

- 真正形成“选线 -> 再干预 -> 再分叉”的 Living Novel 心智。
- 为 v0.4 世界线浏览器准备数据结构。

### v0.2：Import Novel 与世界锚定（已收口 · 2026-05-28）

目标：让用户上传自己的文本，不再依赖内置样例。

**最小闭环设计文档**：[v0.2-import-novel-mvp.md](./v0.2-import-novel-mvp.md)

这是 WenShape 最值得借鉴的阶段。v0.2 分 PR 交付：**PR-A** 导入+校验；**PR-B** `intervene`（须隔离天荒城硬编码规则）。不复制 WenShape 全量工作台。

命令设计：

```bash
lne import-novel ./my_novel.txt --name my-story
lne show-world my-story
lne intervene my-story --target <character_id> --content "..."
```

最小输入范围：

- 3-10 章 `txt` / `md`
- 或一个合并文本文件
- 用户可补充题材、主角名、当前干预节点

输出结构建议：

```text
projects/<story_slug>/
├── source/
│   ├── chapter_001.md
│   ├── chapter_002.md
│   └── chapter_003.md
├── cards/
│   ├── characters/
│   ├── world/
│   └── style.yaml
├── canon/
│   ├── facts.jsonl
│   └── open_threads.yaml
├── summaries/
│   ├── chapter_001.yaml
│   └── volume_001.yaml
├── anchor_proposal.yaml
├── world.yaml
└── canon_chapter.md
```

功能拆分：

| 模块 | 说明 | WenShape 启发 |
| --- | --- | --- |
| Chapter Splitter | 将合并文本拆成章节 | 卷/章结构 |
| Character Extractor | 抽取角色、人设、关系、当前状态 | 人物卡 |
| World Extractor | 抽取地点、势力、规则、战力体系 | 世界观卡 |
| Fact Extractor | 抽取事实库和证据章节 | `facts.jsonl` |
| Summary Builder | 生成章节摘要和当前局势摘要 | summaries |
| Anchor Proposal | 生成可人工确认的世界锚定草案 | proposal workflow |
| Style Extractor | 抽取文风和题材约束 | style card |

验收标准：

- 用户上传 3-10 章后能生成可编辑项目目录。
- 至少抽取 5 个核心角色、3 个地点/势力、5 条事实、3 个开放伏笔。
- 用户可人工修改 YAML 后再运行 `intervene`。
- 导入失败时输出清晰错误，不吞掉原文。
- 不公开上传或分享受版权保护文本的生成结果。

产品价值：

- 从 demo 进入真实用户场景。
- 支撑“续写断更”和“拯救意难平”两个核心卖点。

### v0.3：Context Retrieval Lite 与长篇上下文增强（v0.3.0 / v0.3.1 已收口）

目标：让 v0.2.2 已生成的 `facts.jsonl`、`summaries/`、`story_contract.yaml` 真正参与角色决策和章节渲染，先解决“长篇上下文不漂”的基础问题。

#### v0.3.1：检索 artifact + Brief 接入（已收口）

- `retrieval_context.json` 写盘；`source_weight`；contract 不衰减
- VolumeBrief 接入检索语料；items 含完整 audit 字段

#### v0.3.0：BM25 lite + 章节距离衰减（已收口）

能力目标：

- 建立轻量检索语料：`canon/facts.jsonl`、`summaries/chapter_*.yaml`、`story_contract.yaml`。
- 实现无新服务依赖的 BM25 lite / 关键词检索。
- 用章节距离衰减给事实加权，越接近当前章节越优先，但世界规则和角色边界不因距离失效。
- 将 `retrieved_context` 注入 `character_agent` 与 narrator prompt。
- 将检索结果写入 run 产物，方便 v0.4.2 UI 展示和人工审计。

建议公式：

```text
score = keyword_score * distance_decay * source_weight
distance_decay = 1 / (1 + abs(current_chapter - item_chapter) * 0.2)
```

验收标准：

- imported project 干预时能从 `facts.jsonl` / `summaries/` 检索到相关角色、地点、伏笔。
- 检索上下文能进入角色决策 prompt 和章节生成 prompt。
- 缺少 facts / summaries / story_contract 时可降级，不影响 v0.1/v0.2/v0.4 既有链路。
- builtin sample 不被 imported project 的检索逻辑污染。
- 测试覆盖：检索排序、章节距离衰减、prompt 注入、缺文件降级、run metadata 写盘。

#### v0.3.1：ChapterBrief / VolumeBrief 轻量版

能力目标：

- 扩展 `summaries/chapter_*.yaml` 为轻量 `ChapterBrief`：
  `chapter`、`title`、`summary`、`key_events`、`characters_present`、`state_changes`、`open_threads`、`evidence_refs`。
- 生成 `summaries/volume_001.yaml` 作为轻量 `VolumeBrief`：
  `chapter_range`、`summary`、`main_conflicts`、`key_facts`、`active_threads`、`character_arcs`。
- 后续导入 20+ 章时，优先检索 VolumeBrief，再回落到 ChapterBrief 和 facts。

暂不做：

- 不做向量数据库、embedding、reranker。
- 不做完整 MasterSetting 作者工作台。
- 不接 Zep Cloud / OASIS / CAMEL 作为主线运行时。
- 不做 UI 美化。
- 不做多 provider gateway。

产品价值：

- 让 v0.2.2 的“精华固化”从静态产物变成运行时能力。
- 为 v0.4.2 展示“角色为什么这样想 / 引擎引用了哪些事实”准备数据。
- 为后续 v0.5 第四面墙与 v0.6 深度仿真提供可信记忆层。

### v0.4：Worldline Browser Web UI（已收口）

目标：让用户不再盯文件夹，而是能阅读、对比、选择和继续世界线。

已提前完成“只读轻 UI”，不必等 v0.3。

页面结构：

```text
左侧：故事/世界线树
中间：章节阅读器
右侧：状态面板
底部或弹窗：分支对比 / compare
```

核心视图：

- Story Home：故事列表、最近 run。
- Reader View：章节正文阅读。
- Worldline Tree：父 run、分支、续章、再次干预节点。
- Compare View：分支摘要、角色命运、关键差异。
- State Panel：角色位置、情绪、关系、伏笔状态。

第一版只读已完成：

- 读取 `outputs/` 和 `projects/`。
- 展示章节、分支和状态。
- 允许复制命令继续运行 CLI。

定位说明：

- v0.4 / v0.4.1 / v0.4.2 的前端是“研发 viewer + 可解释 demo”，技术栈为 stdlib HTTP + 原生 HTML/CSS/JS。
- 它用于验证世界线树、状态、章节、检索记忆这些数据是否可信，不承担最终面向普通用户的产品体验。
- 不在 v0.4 系列里重构 React，是为了避免在核心机制尚未稳定前把时间花在 UI 工程化上。
- 真正普通用户可用的产品级前端单独放到 v0.7。

写操作不继续堆在 v0.4 viewer 内，统一后移到 v0.7 产品级前端：

- 输入干预。
- 点击继续时间流逝。
- 选择某条分支作为 active worldline。

验收标准：

- 能加载现有 run。
- 能展示 parent/child lineage。
- 能对比 branch_a / branch_b / branch_c。
- 能展示角色状态变化。
- UI 不改变引擎数据结构。

产品价值：

- 对内汇报、合作方试用、投资人演示最直观。
- 把“世界线”从文件结构变成用户能感知的产品体验。

### v0.5：Fourth Wall Awareness（已收口 · 2026-05-29）

目标：多次干预后，角色逐渐意识到命运被外部力量触碰。

**实现要点**：

- 新建 `engine/src/living_novel_engine/fourth_wall/`：`ledger.py`（`InterventionTrace` / `CharacterAwareness` / `FourthWallLedger` + 触发器检测 + 打分累积 + 持久化），`prompts.py`（分级提示文案）。
- 四类触发器：`impossible_information`（低语/梦境等高维渠道）、`repeated_rescue`（同目标多次干预）、`personality_violation`（合约高抗拒/违规）、`fate_reversal`（强干预/高合约风险）。
- 五级觉察 `none → unsettled → suspicious → aware → defiant`；分数钳制 [0,1]；场景/广域可见时在场旁观者弱外溢（系数 0.25）。
- 账本随 lineage 累积：`fourth_wall.json` 写在 run 根目录；`resume continue` 透传、`resume intervene` 累加（`load_run_ledger`）。
- 注入：≥unsettled 进角色决策 prompt；≥suspicious 放开 narrator「不要打破第四面墙」并允许分级表现；mock 模式按等级追加正文旁白与角色内心独白；快照写各角色 `fourth_wall_awareness`/`fourth_wall_level` 与顶层 `fourth_wall` 段。
- 可关闭：`LNE_FOURTH_WALL=0/off/false`。
- 测试 `tests/test_fourth_wall.py`（+17）；全量 **205 passed**。

核心字段：

```yaml
fourth_wall_awareness:
  score: 0.0
  triggers:
    - impossible_information
    - repeated_rescue
    - personality_violation
    - fate_reversal
  attitude:
    toward_observer: unknown
```

触发条件：

- 角色获得不可能知道的信息。
- 用户多次在生死节点救同一角色。
- 干预强行违背角色人格。
- 世界线出现过于明显的命运修正。
- 角色记忆中出现无法解释的断裂。

叙事表现：

- 角色怀疑有人安排一切。
- 角色误以为是神、天道、读者、作者、系统。
- 角色拒绝执行“太像剧情安排”的选择。
- 角色向虚空提问。
- 角色主动利用高维干预。

验收标准：

- 多次强干预后 `fourth_wall_awareness` 上升。
- awareness 影响角色决策，而不是只写在状态里。
- 章节正文中能自然出现疑问、抗拒、试探。
- 可按题材关闭或降低强度。

产品价值：

- 这是 Living Novel Engine 最有辨识度的精神内核。
- 读者从“看故事的人”变成故事里的不可见角色。

### v0.6：Deep Simulation / Multi-Agent Runtime

目标：当轻量 `scene_runner` 无法表达多角色计划、误解、延迟行动和关系传播时，引入更深的场景推演层。

#### v0.6.0：Runner Adapter（已收口 · 2026-05-29）

先把「单 prompt 多角色轮询」从硬编码实现抽象为可插拔组件，为后续多 Agent 留接缝，行为零变化。

- 新建 `orchestrator/runners/`：
  - `base.py`：`SceneRequest`（统一参数包，收敛原 16 个 `run_scene` 参数）、`SceneRunner`（ABC，`run(request) -> SimulationResult`）、`RunnerError`。
  - `lightweight.py`：搬迁原 `run_scene` 全部实现为 `LightweightSceneRunner`（含 `_should_terminate` / `_collect_state_deltas` 等 helper）。
  - `__init__.py`：注册表 `register_runner` / `get_runner` / `available_runners` / `dispatch_scene`，默认注册 `lightweight`。
- `scene_runner.run_scene` 改为薄包装：构造 `SceneRequest` → `dispatch_scene`；新增可选 `runner_name`。
- 选择优先级：显式 `runner_name` > env `LNE_SCENE_RUNNER` > 默认 `lightweight`；dispatcher 以 `runner.name` 权威标记结果。
- 输出契约仅 additive：`SimulationResult.runner_name`、`events.json` 增 `"runner"`。
- 测试 `tests/test_scene_runner_adapter.py`（+10），全量 **218 passed**，搬迁零回归。

#### v0.6.1：Multi-Agent Runner Protocol（已收口 · 2026-05-29）

先定义多 Agent runner 的「内部中间产物」协议，再决定自研还是接外部框架；协议 **未接入运行**，默认行为零变化。

- 设计文档 `docs/v0.6.1-multi-agent-runner-protocol.md`：目标 / 不做 / 输出契约不变性约束 / v0.6.2 投影路线预告。
- 新建 `orchestrator/runners/protocol.py`（仅 pydantic）：`AgentIntent` / `PrivateKnowledge` / `Misunderstanding` / `DelayedAction` / `RelationshipSignal` / `AgentTurnPlan` / `MultiAgentTrace`。
- 硬规则：私下信息 / 误解默认 `visibility=private` 且未 reveal；`revealable_knowledge()` / `correctable_misunderstandings()` 是公开层过滤依据；`DelayedAction.due_round` + `is_due()` 表达延迟行动。
- 文档漂移修正：`engine/README.md` 路线表 v0.3 改为 Context Retrieval Lite。
- 测试 `tests/test_multi_agent_protocol.py`（+9），全量 **227 passed**，lightweight 零回归。

#### v0.6.2：multi_agent_stub runner 本体（已收口 · 2026-05-29）

第一个多 Agent 系 runner：用协议确定性地产出可解释 trace，再投影回既有契约，验证「协议→投影」闭环。

- 新建 `orchestrator/runners/projection.py`：
  - `build_demo_trace(request)`：从在场角色 + 干预 + 种子确定性构造 `MultiAgentTrace`。
  - `project_trace(trace, ...)`：trace → `AcceptedEvent` / `StateDelta`，**强制规则**：仅 `visibility=public` 意图、`revealed=True` 私下信息、`corrected=True` 误解、`due_round<=max_rounds` 延迟行动进公开层；就地标记 `executed`。
  - `apply_relationship_signals(trace, char_map)`：关系信号写回角色，供快照体现。
- 新建 `orchestrator/runners/multi_agent_stub.py`：`MultiAgentStubRunner`（消费协议→投影→复用 `build_state_snapshot`+`render_chapter`→附 trace）；纯结构化，不接 LLM 推理、不接外部服务。
- 输出契约：仅 additive 增 `SimulationResult.multi_agent_trace`（dict）+ 分支目录 `multi_agent_trace.json`；`lightweight` 恒为 `None`，不写该 artifact。
- **非默认**：经显式 `runner_name` 或 `LNE_SCENE_RUNNER=multi_agent_stub` 启用。
- 测试 `tests/test_multi_agent_stub.py`（+12），全量 **239 passed**，lightweight 零回归。

#### v0.6.3：multi_agent_trace 可视化（已收口 · 2026-05-29）

让 `lne browse` 能解释多 Agent 推演产物，为后续真实推理调试铺路；不接真实推理、不接 MiroFish、不引依赖。

- 后端 `browser/indexer.py`：`get_branch` 读分支 `multi_agent_trace.json`（缺失→`None`、损坏→`{}`，不抛）；`BranchSummary` + 树分支节点增 `has_multi_agent_trace`/`multi_agent_trace_count`（additive，旧 API 不破坏）；抽 `_read_optional_json`/`_list_len_in_json` helper。
- 前端「Agent 轨迹」标签页：分组展示 public/private 意图、私下信息（`revealed`）、误解（`corrected`）、延迟行动（`executed`/`due_round`）、关系信号；树分支「轨迹 N」角标；缺 trace 空态不白屏。
- 文档漂移修正：README `multi_agent_stub` 示例补 story slug；协议文档「真正推理循环」→ v0.6.3+。
- 测试 `tests/test_browser_multi_agent_trace.py`（+6），全量 **245 passed**；`node --check app.js` 通过。

#### v0.6.4：multi_agent_llm runner（已收口 · 2026-05-29）

- 新建共享装配层 `orchestrator/runners/assembly.py`：`build_result_from_trace`（trace→`project_trace`→`apply_relationship_signals`→`build_state_snapshot`+`render_chapter`→`SimulationResult`），stub 与 llm runner 共用、输出严格同构；`multi_agent_stub` 重构为复用该层，行为不变。
- 新建 `orchestrator/runners/multi_agent_llm.py`：`MultiAgentLLMRunner`（name=`multi_agent_llm`，非默认）；`generate_trace` 用现有 `LLMClient.chat_json` 让小模型一次性输出整场 `MultiAgentTrace` JSON。调用方式采用现有 OpenAI-compatible API（`LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL_NAME`），不本地部署、不引依赖。
- **健壮回退**：mock / 无 API key / LLM 异常 / 非法 JSON / 校验失败 / 空 turn_plans → 回退确定性 `build_demo_trace`（`source="fallback"`），不抛；保证 demo / 测试在无 API 环境下仍跑通。
- **隐私加固**：未 `revealed` 私下信息、未 `corrected` 误解强制 `visibility=private`；暗算/隐瞒类公开意图（conceal/deceive/scheme/...）降级 private；`due_round<created_round` 归一化；补齐 worldline_id/seed（v0.6.5 起此逻辑由 `trace_quality.validate_and_repair_trace` 统一承担）。投影层再做硬过滤——模型乱标也不泄漏。
- 投影层 `project_trace()`、`build_state_snapshot()`、`render_chapter()` 原样复用；继续把 Zep / OASIS / CAMEL 留作 v0.8+ 参考，不在本刀引入新服务/框架依赖。
- 设计文档 `docs/v0.6.4-multi-agent-llm-runner.md`；测试 `tests/test_multi_agent_llm.py`（+9），全量 **254 passed**，lightweight + stub 零回归。

#### v0.6.5：推演工程可靠性（已收口 · 2026-05-29）

- **generation_meta** `orchestrator/runners/meta.py`（`TraceMeta`）：source（llm/fallback/stub）/ fallback_reason / model_name / attempt_count / duration_ms / validation_status / validator_warnings / usage / cost_estimate；`assembly.build_result_from_trace` 以 additive 方式写进 `multi_agent_trace.generation_meta`；stub 也补 `source=stub`。
- **trace 质量校验** `orchestrator/runners/trace_quality.py` `validate_and_repair_trace`：硬失败（空 turn_plans）→ 重试/回退；就地修复（回合号归一化 >=1 且 due>=created、暗算意图/未 reveal 私下信息/未 corrected 误解强制 private、补齐 worldline_id/seed）；告警（缺角色计划、干预未入目标私域）；**绝不抛异常**。
- **有限重试**：`multi_agent_llm.generate_trace` 返回 `(trace, TraceMeta)`；`LNE_MULTI_AGENT_MAX_RETRIES`（默认 1、上限 5）控制重试，重试 prompt 带上一轮问题；耗尽回退确定性 `build_demo_trace`。
- **token usage**：`LLMClient` 抽 `_complete()` 返回 `(content, usage)` + 新增 `chat_json_with_usage()`；`chat`/`chat_json` 行为不变；拿不到 usage 为 `null` 不报错。
- 前端「Agent 轨迹」新增「推演元数据」分组（`renderTraceMeta`，彩色 source 徽标 + 模型/尝试/耗时/token/告警）。
- 设计文档 `docs/v0.6.5-multi-agent-reliability.md`；测试 `tests/test_trace_quality.py`（+9）+ `test_multi_agent_llm.py` 扩充 + stub +1，全量 **269 passed**，`node --check app.js` 通过，lightweight/stub 零回归。
- 刻意不做（留待）：并发、精确价格计算（`cost_estimate` 占位 `null`）→ v0.8+ 按需。

### v0.7：Product Web App / 产品级前端（已收口 · 九刀主闭环）

目标：把当前 CLI + 研发 viewer 升级为普通用户能直接使用的产品入口。

收口状态（2026-05-29）：该目标已通过九刀完成，当前 `engine/ui/` 已支持三入口（样例 / 导入 / 主题创世）、世界锚定与轻编辑、Web 自由干预、Causal Diff 确立 / 抹除 / 回滚、运行设置、异步 Job 进度轮询。`lne browse` 继续作为开发者 viewer 保留，产品前端复用现有 local API，不重写引擎。

推荐技术路线：

- 新建独立 `ui/`，使用 React + Vite + TypeScript。
- 复用现有 `browser` API 或抽出更稳定的 local API server，不重写引擎。
- 保留 `lne browse` 作为开发者调试 viewer；产品前端另起 `lne web` 或独立 dev server。

首版产品体验：

- 视觉基调：以古风 / 墨水屏 / 纸面阅读为主体，高维系统感只在关键事件中克制出现。
- 动效原则：动效服务“因果被改写”的理解，不做过度赛博、过度闪烁、过度震屏；世界线坍缩、红色警告、文字重组都要短、轻、可关闭。
- 三种创建入口：
  - `Import Existing Novel`：上传 3-10 章或已有项目，从用户文本进入活体世界。
  - `Story Genesis Mode`：用户只输入主题、题材、主角、大概内容，由 AI 生成第一章、世界设定、角色卡和初始合约。
  - `Sample World`：使用内置原创样例快速体验。
- 导入小说：选择 txt/md 文件或目录，显示抽取进度与可编辑世界锚定。
- 创世模式：输入“我想看什么故事”，生成第一章和可运行故事世界；不要求用户先上传小说。
- 世界线浏览：产品级世界线树、章节阅读、检索记忆、角色状态。
- 用户干预：在 Web 内输入目标角色与干预内容，先展示干预编译结果，再触发 `intervene`。
- Causal Diff / 因果差异块：用户在章节某段施加干预后，优先展示局部差异，而不是整章粗暴刷新。
  - 被抹去的旧现实：微红底、朱砂边、删除线或墨迹淡出。
  - 新凝聚的世界线：浅青 / 玉绿色底、细边框、流式打字出现。
  - 操作：`确立此界线`、`抹除这次改写`、`回滚到干预前`、`查看因果差异`。
  - 接受后才把该差异正式坍缩为本世界线正史；拒绝则回到干预前状态或重新推演。
- 干预编译预览：展示 `AbstractIntervention`、世界观兼容性、干预进入世界的方式、本次专属 `Branch Axis`，以及 `Divergent Worldline` / `Alternate Novel` 类型。
- 无干预继续：用户可以选择“静观其变”，生成 `Baseline Worldline`，观察角色按人设和世界状态自然发展。
- 选线续章：点击某条分支继续，必要时再干预。
- 运行状态：长任务 loading / error / retry / 日志摘要，不要求用户复制命令。
- 世界线图谱：不把 `branch_a/b/c` 暴露为固定“相信/怀疑/拒绝”，而是显示每次干预实际生成的分歧标签。
- 角色状态增量：推演后在角色状态面板展示变化量，例如好感 `+30 (↑ +5)`、心境 `警惕 -> 平静`，帮助用户感知干预影响。
- 第四面墙提示：角色觉察到叙事篡改时，正文可有克制的朱砂色高亮；Agent 轨迹展示简短 warning。避免大面积红屏、强闪烁或惊吓式动效。
- 剧情张力弧线：`Worldline Judge` 阶段将单点“当前张力”升级为 Story Arc Curve，展示干预前后张力走势。

交互优先级：

| 优先级 | 交互 | 原因 | 排期 |
| --- | --- | --- | --- |
| P0 | `Causal Diff / 因果差异块` + 接受/拒绝/回滚 | 解决“AI 到底改了哪里”和“一键覆盖失控” | v0.7 |
| P1 | 干预后角色状态增量 | 强化“我的一句话改变了角色”的即时反馈 | v0.7 |
| P2 | 克制第四面墙高亮与 Agent warning | 放大角色觉醒时刻，但避免廉价化 | v0.7 / v0.7.2 |
| P3 | 剧情张力弧线 | 世界线质量可视化，适合放进评审层 | v0.7.5 |

当时未放进 v0.5 / v0.6 的原因：

- 现在最稀缺的不是页面框架，而是引擎独特性：第四面墙、深度推演、长篇一致性。
- 过早重构 React 会消耗大量工程时间，却无法弥补核心玩法不够独特的问题。
- 等 v0.5/v0.6 证明“普通续写器做不到的体验”后，再做产品级前端，展示价值会更强。

### v0.7.2：Agent Interaction / 角色交互协议增强

**实现状态（2026-05-29 已收口）**：

- ✅ `InterventionGuardrail`：`intervention/guardrail.py`（`evaluate_guardrail` + `InterventionGuardrailResult` / `GuardrailCheck`，六维 genre/time_power/persona/world_rule/visibility/strength，deterministic、不调 LLM）+ `service/intervention_guardrail.py` + `POST /api/interventions/guardrail`。独立预检解释层，**不阻断** `run_intervention` 主行为；规则改写型干预标记 `allowed=False` 并提示另开异设世界线。
- ✅ `CharacterProbe`：`service/character_probe.py`（belief/emotion/desires/fears/boundaries/known/unknown/fourth_wall/likely_intervention_response/obedience_risk/resistance_level/explanation）+ `GET /api/stories/<slug>/characters/<char_id>/probe`（可选 run_id/branch_id/intervention_text）。deterministic、不调 LLM；故事/角色缺失 404；快照损坏不 500。
- ✅ `CharacterAction` additive 增强：`models/events.py` 增 `action_id/action_label/preconditions/effects/failure_reason/repair_suggestions/risk/visibility`，全部带默认空值；旧构造与旧 artifact 读取完全兼容；**未强制接入 runner 主链路**。
- ✅ Web UI：世界锚定页角色卡「角色探针」折叠入口；干预输入区「预检干预」按钮（调用 guardrail，解释世界为何抵抗并给更合理方式）；Agent 轨迹页结构化动作（前置/效果/失败/修正）只读展示，缺字段空态正常。
- ⛔ 明确未做（留后续版本）：`AbstractIntervention -> CharacterActionSequence` 实例化（仍是 v0.7.1 编译层）、runner 主链路重构、把 CharacterAction 接入 multi_agent_trace 产出、真实 LLM 探针、Seedream（v0.7.3）、Baseline/Canon Replay（v0.7.4）、Worldline Judge（v0.7.5）、Long Novel Memory（v0.8）。

目标：在产品级 Web App 的基础体验跑通后，吸收 `eastworld`、StoryVerse 与 STORY2GAME 的经验，让角色不仅能“生成剧情”，还能以更稳定的结构执行动作、暴露内心探针、接受干预护栏，并让自由输入通过 `InterventionCompiler` 变成本次专属分支轴。

该版本只借鉴 `eastworld` 的交互协议和 Agent Studio 设计，不接入其 server、Redis 或 OpenAPI client。

能力范围：

- `InterventionCompiler`：`Raw Reader Input -> AbstractIntervention -> Compatibility -> Realization -> BranchAxis`。
- `CharacterAction`：角色结构化动作，作为 `MultiAgentTrace` 与 `accepted_events` 之间的中间层。
- `CharacterProbe`：查询角色信任、怀疑、恐惧、第四面墙觉察等内心状态。
- `InterventionGuardrail`：在 `contract_audit` 前先对用户干预做题材、时代、战力、人格边界检查。
- `BranchAxis`：为本次干预动态生成分支标签；信息型干预可用相信/怀疑/拒绝，强制行动型和规则改写型必须生成不同轴。
- Web UI 轻量角色配置：核心信念、欲望、恐惧、口癖、已知/未知信息、可执行动作。
- Agent 轨迹页增强：把“计划/误解/延迟行动”进一步展示为“角色动作 -> 状态变化 -> 章节渲染”。

建议数据结构：

```json
{
  "abstract_intervention": {
    "intent": "prevent_character_from_entering_trap",
    "intervention_type": "forced_action",
    "target_refs": ["lin_wan_zhou"],
    "desired_effect": "avoid_bamboo_forest"
  },
  "lineage_type": "divergent_worldline",
  "branch_axis": [
    {"id": "avoid", "label": "主动避开"},
    {"id": "investigate", "label": "延迟调查"},
    {"id": "resist", "label": "抗拒预兆，照旧赴约"}
  ],
  "character_action": {
    "character_id": "lin_wan_zhou",
    "action": "investigate",
    "target": "bamboo_forest",
    "reason": "她不完全相信低语，但退魂铃异常让她决定先查证",
    "visibility": "private",
    "risk": "medium"
  }
}
```

可选动作：

- `investigate`
- `warn`
- `conceal`
- `negotiate`
- `attack`
- `retreat`
- `observe`
- `seek_ally`
- `break_contract`

验收标准：

- 至少 6 类 `CharacterAction` 可被 trace 生成、投影和 UI 展示。
- `CharacterProbe` 可解释角色为何相信、怀疑或拒绝某次干预。
- `InterventionCompiler` 可区分信息型、强制行动型、资源注入型、规则改写型干预。
- `BranchAxis` 不固定为 believe/doubt/reject，分支名称随干预类型变化。
- `Alternate Novel / AU Worldline` 有显式 lineage 标记和合约差异说明，不静默污染原世界线。
- 越界干预会给出降级建议，而不是直接污染世界状态。
- 不破坏既有 `multi_agent_llm` / `multi_agent_stub` 输出契约。

暂不做：

- 不做完整 no-code Agent 平台。
- 不做游戏引擎 SDK。
- 不接 Redis / eastworld server。
- 不生成 OpenAPI client。
- 不把所有干预都硬塞成相信 / 怀疑 / 拒绝。

产品价值：

- 把“角色像活人”从正文表现推进到结构化行为层。
- 让用户在 Web UI 中能理解角色行动，而不是只读生成结果。
- 为第四面墙、干预护栏和后续复杂多 Agent 推演打基础。

### v0.7.3：Visual Asset Generation / Seedream 视觉资产 ✅ 已收口

> **收口（2026-05-30，482 passed）**：新建 `visual_assets/`（models/store/seedream_client/prompt_builder）+ `service/visual_assets.py` + 三路由 `GET /api/stories/<slug>/visual-assets`、`POST .../visual-assets/generate`、`GET /api/stories/<slug>/assets/<rel>`（安全静态服务）。additive artifact `projects/<slug>/visual_assets.json`（仅相对路径+元数据），图片落 `projects/<slug>/assets/`。无 `SEEDREAM_API_KEY` / `LNE_VISUAL_ASSETS=0` / 生成失败时稳定降级古风占位，不阻塞导入/创世/干预/浏览。UI：世界锚定页封面+生成区、角色卡头像、书架封面缩略、设置抽屉 Seedream 区块。世界线节点缩略图仅预留 artifact 字段 + UI 占位（未绑定 run/branch 生成）。测试 `tests/test_visual_assets.py`（+37，全程 fake/mock，不打外网）。**未做**：真实线上批量队列、世界线节点真正生成、图片版权/分享策略、真人复刻（明确不做）。下一步 v0.7.4 Baseline & Canon Replay。

目标：在产品级 Web App 的阅读与世界线体验稳定后，接入用户已有的 Seedream 生图能力，为故事生成可控、可缓存、可复用的视觉资产。

接入模型：

```text
provider: Seedream
model: Seedream 5.0 Lite
request_base_url: https://ark.cn-beijing.volces.com
```

能力范围：

- 角色头像：根据 `characters.yaml` 的外貌、身份、气质、时代、题材约束生成。
- 故事封面：根据 `world.yaml`、`story_contract.yaml` 和题材模板生成项目封面。
- 场景背景：根据当前章节地点、时间、氛围、世界线状态生成阅读页背景或插图。
- 世界线节点缩略图：为关键分歧节点、涌现节点、Alternate Novel 节点生成小图。
- 视觉资产缓存：写入 `projects/<slug>/assets/` 或 `outputs/<run_id>/<branch>/assets/`，避免每次打开 UI 都重新生图。

建议环境变量：

```text
SEEDREAM_API_KEY=
SEEDREAM_BASE_URL=https://ark.cn-beijing.volces.com
SEEDREAM_MODEL=seedream-5.0-lite
LNE_VISUAL_ASSETS=on/off
```

设计原则：

- 图片是增强沉浸感，不是替代正文；阅读区仍以文字为第一主角。
- 头像和角色视觉必须稳定，不能每章漂移；需要记录 prompt、seed、asset_id、source fields。
- 不直接用受版权保护作品的原图或影视演员脸；导入商业小说时默认生成“原创化概念图”。
- 生图失败不影响干预、推演、续章和阅读；UI 回退到占位图。
- 默认先做手动触发或后台生成，不在每次推演中同步阻塞。

建议数据结构：

```json
{
  "asset_id": "char_lin_wan_zhou_portrait_v1",
  "asset_type": "character_portrait",
  "provider": "seedream",
  "model": "seedream-5.0-lite",
  "prompt": "young cultivator woman, rain night, restrained literary style...",
  "source_refs": ["characters.lin_wan_zhou", "world.genre", "style_hint"],
  "file": "assets/characters/lin_wan_zhou_v1.png",
  "created_at": "2026-05-29T00:00:00+08:00"
}
```

验收标准：

- 可为 imported project 生成至少 3 个角色头像 + 1 张故事封面。
- 可为某个 run/branch 生成 1 张场景背景或世界线节点缩略图。
- 资产有本地缓存和 metadata，重复打开 UI 不重复扣费。
- 未配置 `SEEDREAM_API_KEY` 时稳定降级，不影响测试和主流程。

暂不做：

- 不做复杂图生图 / 换脸 / 影视角色复刻。
- 不做每章自动批量插图。
- 不把视觉资产纳入叙事正史判断；它只是 UI 资产，不参与 contract。

### v0.7.4：Baseline & Canon Replay / 无干预基线与正史回放 ✅ 已收口

> **收口（2026-05-30，Codex 兜底后 526 passed）**：新建 `baseline/{models}`（`BaselineReport`/`CharacterStateChange`）+ `service/baseline.py`（`generate_baseline` 从锚定或 parent 快照续；`get_baseline_report`）+ `orchestrator/worldline_brancher.build_baseline_spec()`（branch_id=`baseline`、branch_seed=`linear`）+ `output/writer.write_baseline_output`（写 `baseline_report.json`+`baseline/` 分支目录，**不写 intervention.json/causal_diff.json**）。新建 `canon_replay/{models,evaluator}` + `service/canon_replay.py`（holdout 读写：仅 imported/genesis 可写、builtin 只读、force=False 同章 409、文件名由章号派生防穿越；deterministic `evaluate_replay`：lexical/entity/thread/length/state→overall，不打 LLM）。6 个 additive API：`POST /api/stories/<slug>/baseline`、`GET /api/runs/<run_id>/baseline`、`GET/POST /api/stories/<slug>/canon/holdout`、`POST /api/stories/<slug>/canon/replay`、`GET /api/runs/<run_id>/canon-replay`。`writer._outputs_dir()` 改为支持 `LNE_OUTPUTS_DIR`（默认不变）。UI：世界锚定页「基线与正史回放」区块（中文、holdout 空态、builtin 只读、生成基线/运行回放、评分条、缺失实体/伏笔）。Codex 兜底补 service 层 `story_slug`/`run_id`/`branch_id` 安全校验，并把 holdout UI 默认覆盖改为 false。测试 `tests/test_v074_baseline_canon_replay.py`（兜底后 43 passed，不打外网/LLM）。**未做**：Worldline Judge（v0.7.5）、Long Novel Memory（v0.8）、LLM 语义评估、百万字 holdout、版权/公开分享策略、baseline↔intervention 并排偏离对比 UI。下一步 v0.7.5 Worldline Judge。

目标：让用户能比较“我不干预时世界会怎样”和“我干预后命运如何偏离”，同时用完结作品或自有文本做引擎质量评估。

#### Baseline Worldline

每个故事世界都应允许生成一条无高维干预的基线：

```text
Baseline Worldline
  无新干预
  -> 角色按人设、记忆、世界规则、资源状态、伏笔压力自主行动
  -> 生成下一章或若干候选走向
```

用途：

- 让用户先看“原世界自然会怎么走”。
- 作为干预世界线的对照组。
- 帮助 UI 展示“干预前 / 干预后”的蝴蝶效应。

产品表达：

```text
无干预基线
  -> 第三章之后，林晚舟仍按原计划赴约

有干预世界线
  -> 用户投放预知梦
  -> 林晚舟延迟赴约 / 派纸鹤探查 / 抗拒预兆
```

#### Story Genesis Mode / 创世模式

用户不必先上传小说，也可以通过主题输入生成一个可运行故事世界：

```text
用户输入主题 / 题材 / 主角设定 / 大概内容
  -> AI 生成第一章
  -> 抽取或同步生成 world.yaml / characters.yaml / story_contract.yaml
  -> 生成 Baseline Worldline
  -> 用户可选择静观其变或施加干预
```

创世模式产物应与 imported project 同构，仍落到 `projects/<slug>/`：

```text
projects/<slug>/
  source/chapter_001.md
  world.yaml
  characters.yaml
  story_contract.yaml
  canon_chapter.md
  canon_opening.md
  generation_meta.json
```

#### Canon Replay Evaluation / 正史回放评估

如果用户上传的是已经完结或已有后续章节的作品，可以用后续章节作为隐藏评估集：

```text
导入完整文本
  -> 运行时只开放第 1 章或前 N 章作为 canon anchor
  -> 无干预生成第 N+1 章走向
  -> 与原作第 N+1 / N+2 章对比
  -> 输出回放评估
```

评估维度：

- 角色行为是否接近原作。
- 关键事件是否命中。
- 伏笔是否延续。
- 情绪与主题是否偏移。
- 是否过早解决冲突或走向套路化。

注意：

- 如果只输入第一章，系统只能合理预测后续，不能保证等于原作。
- 如果导入全本，后续章节只能作为本地评估集，不应在运行时泄漏给角色或 narrator。
- 受版权保护文本默认本地个人评估，不做公开分享。

建议产物：

```json
{
  "baseline_run_id": "run_xxx",
  "holdout_chapters": ["chapter_002", "chapter_003"],
  "canon_similarity": 0.62,
  "event_hits": ["主角收到密信", "师门召回"],
  "missed_events": ["反派提前登场"],
  "character_alignment": 0.78,
  "notes": "角色动机接近原作，但事件推进更保守。"
}
```

验收标准：

- Web UI 有三种入口：导入小说、主题创世、内置样例。
- 创世模式可生成第一章和可运行项目，并复用现有 intervene / resume 链路。
- 任意项目可生成无干预 `Baseline Worldline`。
- 对有后续章节的测试文本，可生成 `canon_replay_report.json`。

### v0.7.5：Worldline Judge / 世界线评审团

目标：在产品级 Web App 跑通后，增加“生成后评估”能力，让用户知道哪条世界线更值得继续。

该版本只吸收 `autonovel` / `AI_NovelGenerator` 的边角料价值，不把它们作为核心架构参考。

能力范围：

- `worldline_judgement.json`：每条分支生成结构化评分。
- `compare.md` 增强：展示每条世界线的角色一致性、冲突潜力、爽点、节奏、合约风险。
- narrator 质量检查：检测 AI 腔、过度解释、重复句式、水文、分支差异不足。
- contract audit 增强：把章节正文、人设、事实库、未解伏笔一起做一致性检查。
- UI 展示：在世界线对比页展示“推荐继续 / 谨慎继续 / 建议归档”。

建议评审维度：

| 维度 | 说明 |
| --- | --- |
| persona_consistency | 角色是否符合人设、记忆、利益和当前情绪 |
| contract_risk | 是否冲突世界规则、战力体系、正史事实 |
| branch_diversity | 三条分支是否真的不同，而不是换皮 |
| narrative_momentum | 下一章是否有明确冲突和继续阅读动力 |
| emotional_payoff | 是否回应了用户干预的情绪期待 |
| anti_slop_score | 是否存在 AI 腔、过度解释、空泛抒情、水文 |
| continuation_potential | 这条世界线后续还能不能继续生长 |

输出示例：

```text
branch_a：推荐继续。角色相信干预，爽点强，后续冲突明确，但合约风险中等。
branch_b：谨慎继续。人物逻辑最稳，但节奏偏慢，需要下一章制造外部压力。
branch_c：建议保留观察。代价最大，第四面墙潜力最高，但短期阅读爽感较低。
```

暂不做：

- 不做 autonovel 式一键生成整本书。
- 不做 NovelGenerator 式作者参数面板。
- 不做多轮自动修稿直到评分达标，先只评审和轻量建议。

产品价值：

- 帮助用户从“我有三条线”进入“我知道该继续哪条线”。
- 把静态写稿项目的评估经验，转化为 LNE 自己的世界线选择体验。
- 为后续导出分支小说、社区分享和高质量续章打基础。

### v0.8：Long Novel Memory / 百万字长篇支撑

目标：让 LNE 能处理 100 万字以上、乃至 200-600 万字的长篇小说导入和世界线推演，并尽量避免角色偏离人设、时间线矛盾、资源凭空出现、伏笔遗忘和章节越写越漂。

核心判断：长篇能力不能靠“扩大上下文窗口”解决。几百万字文本必须拆成可维护的分层记忆、可检索证据、写后投影和一致性审计。

参考项目吸收点：

| 来源 | 可吸收机制 | LNE 落点 |
| --- | --- | --- |
| WenShape | 卷/章结构、事实库、章节摘要、分卷摘要、BM25、实体增强、章节距离衰减、token budget、压缩器 | v0.8.1-v0.8.3 |
| webnovel-writer | `MASTER_SETTING` / Volume / Chapter Contract、accepted `CHAPTER_COMMIT`、projection writers、RAG auto/hybrid | v0.8.1-v0.8.4 |
| AI_NovelGenerator | `global_summary`、`character_state`、`plot_arcs`、一致性审校、向量检索 | v0.8.2-v0.8.4 |
| autonovel | Lore / Characters / Outline / Chapters / Canon 分层、propagation debts、Judge loop | v0.8.1 / v0.8.4 |
| MiroFish | GraphRAG、时序记忆、Agent 长期记忆 | v0.9.3 / v0.9.4 触发式评估，不作为 v0.8 或 v0.9.0-alpha 必选依赖 |

#### v0.8.0：Long Novel Ingestion / 大文件导入

几百万字上传不能走“一次粘贴进文本框”。产品和引擎都要支持异步导入：

```text
用户上传 txt/md/epub/zip
  -> 前端分片上传
  -> 后端创建 ingest_job
  -> 原文落 source_raw/
  -> 流式分章与编码清洗
  -> 每章生成 chapter_brief
  -> 每卷生成 volume_brief
  -> 抽取 canon ledger / character_state / timeline
  -> 建 BM25 / entity index / optional vector index
  -> 生成导入报告与人工修订入口
```

关键约束：

- 上传完成不等于导入完成；导入是后台任务。
- 支持断点续传、失败恢复、进度条、部分完成状态。
- 先导入前 20 章即可开始体验，后续章节继续异步索引。
- 原文保留在 `source_raw/`，运行时不直接把原文整本塞进 prompt。
- 导入报告要展示：章节数、总字数、疑似乱码、重复章节、缺章、角色抽取置信度、时间线风险。

> **v0.8.0-A 已落地（2026-05-30）**：先完成长篇导入底座，不接向量库、不改 runner。`write_project()` 统一写入 `source_raw/` 与 `import_report.json`；Web/job 导入新增 additive `long_mode`，默认仍保持 3-10 章小闭环，`long_mode: true` 时允许最多 200 章；报告记录总章节、总字数、前 20 章可体验范围、`partial_ready`、疑似乱码章节、重复章名、缺章编号与每章 source/raw 路径。`/api/import-novel` 和 `/api/jobs/import-novel` 返回 `import_report` 摘要。已验证：`tests/test_v080_long_ingestion.py` + 导入/job 回归共 39 passed。

> **v0.8.x Long Upload Productization 已落地（2026-05-31）**：在不改变既有 chapters JSON 契约的前提下，`import_novel_from_payload()` 新增 additive `upload` 分片 payload，支持 txt/md 合并文本、zip 内 txt/md 章节、epub 内 html/xhtml 章节。前端导入页新增 txt/md/zip/epub 文件选择、浏览器端分片、文件摘要、job 进度条和失败空态；未选文件时保留 3-10 章粘贴模式。已验证：新增 `tests/test_v08x_long_upload_product.py` 3 passed；完整后端 573 passed，前端 build 通过。未做：真正多请求断点续传/恢复、持久化 ingest job、epub spine 精排。

#### v0.8.1：Hierarchical Memory / 分层记忆

建议目录：

```text
projects/<slug>/
  source_raw/
  source/
  memory/
    master_setting.yaml
    volumes/volume_001.yaml
    chapters/chapter_0001.yaml
    scenes/chapter_0001_scene_01.yaml
    character_states/<character_id>.yaml
    timeline.yaml
    plot_threads.yaml
    propagation_debts.yaml
```

记忆层级：

```text
Contract Layer
  世界规则、人设边界、题材规则、战力上限，永远高优先级

Timeline Layer
  时间、地点、事件顺序、角色同时只能在一个地方

State Layer
  角色状态、关系、资源、伤势、秘密、第四面墙觉察

Retrieval Layer
  facts / summaries / briefs / raw chunks 的相关证据

Audit Layer
  写完后反查人设、时间线、资源、伏笔和合约
```

> **v0.8.1-A 已落地（2026-05-30）**：先完成导入时的分层记忆 artifact 骨架，不让 runner 直接消费。`write_project()` 现在会写 `memory/memory_manifest.json`、`memory/master_setting.yaml`、`memory/volumes/volume_*.yaml`、`memory/chapters/chapter_*.yaml`、`memory/character_states/*.yaml`、`memory/timeline.yaml`、`memory/plot_threads.yaml`、`memory/propagation_debts.yaml`。这些文件镜像当前 world/characters/source/source_raw/open_threads，给后续 canon ledger、混合检索和一致性审计提供稳定目录契约。已验证：`tests/test_v081_hierarchical_memory.py` 2 passed；导入/检索相关回归中该新增 artifact 不改变既有读取契约。

#### v0.8.2：Canon Ledger / 正史账本

把当前 `facts.jsonl` 升级为更细的长篇正史账本：

```json
{
  "id": "event_000123",
  "type": "event|state|relationship|resource|timeline|foreshadowing",
  "chapter": 128,
  "scene": 2,
  "entities": ["lin_fan", "retreat_bell"],
  "statement": "林凡在听雨轩外确认退魂铃已经碎裂。",
  "truth_status": "canon",
  "source_ref": "source/chapter_0128.md#scene_02",
  "confidence": 0.92,
  "valid_from": 128,
  "valid_until": null
}
```

账本用途：

- 避免“角色已经死了又突然出现”“道具已碎又被使用”。
- 让 `Baseline Worldline`、干预世界线、Canon Replay 都有证据来源。
- 为后续 GraphRAG / Zep / 图数据库留下迁移口。

> **v0.8.2-A 已落地（2026-05-30）**：导入时生成 `memory/canon_ledger.jsonl`，并在 `memory_manifest.json` 中登记 `canon_ledger` layer。当前账本从章节、角色状态、角色关系、开放伏笔 deterministic 生成统一字段：`id/type/chapter/scene/entities/statement/truth_status/source_ref/confidence/valid_from/valid_until`。旧 `canon/facts.jsonl` 仍保留给 v0.3 检索链路使用；新账本先作为一致性审计和后续 GraphRAG/Zep 的迁移口。已验证：`tests/test_v082_canon_ledger.py` 2 passed；前三刀导入/记忆/检索回归 57 passed。

#### v0.8.3：Hybrid Retrieval / 混合检索

默认不强制上向量库，但长篇必须有可升级检索策略：

```text
Query
  -> entity extraction
  -> BM25
  -> chapter distance decay
  -> entity boost
  -> source weight
  -> optional vector / reranker
  -> prompt budget pack
```

Prompt 预算建议：

```text
固定必带：story_contract + 当前角色状态 + 当前时间线
近邻必带：最近 3-5 章摘要 / 最近事件
检索补充：与当前场景相关的事实、伏笔、旧章节证据
审计反馈：上一轮发现的矛盾和待修复项
```

向量 / embedding / reranker 的触发条件：

- 50+ 章后 BM25 召回不稳定。
- 用户上传 100 万字以上作品。
- Canon Replay 命中率长期不足。
- 角色/地名别名复杂，纯关键词无法稳定对齐。

> **v0.8.3-A 已落地（2026-05-30）**：先把 `memory/canon_ledger.jsonl` 接入现有零依赖 BM25 检索，不引入向量库。`ContextCorpus` 新增 `canon_ledger`，`retrieve_context()` 将账本记录作为 `canon_ledger` source 纳入语料，source weight 1.1，artifact item 保留 `entities/ledger_type/confidence`；prompt 仍并入“正史事实”块。v0.8.x 又补上 `memory/entity_aliases.yaml` 与 query/doc alias expansion，canon ledger 命中项 additive 返回 `resolved_entities`；Runtime Memory Consumption-A 将这些安全子集打包为 `runtime_memory_context.json` 并注入既有 `retrieved_context`；Frontend Artifact Panel 已将相关解释层收束到右侧「机制档案」；Long Upload Productization 已补 txt/md/zip/epub 文件导入与分片体验。已验证：完整后端 573 passed，前端 build 通过。

#### v0.8.x：Entity Aliases / Entity Resolution

目标：在不引入 NER、向量库或 runner 重构的前提下，先解决同一角色、地点、势力、物品多名称导致的检索与审计断裂。

当前已完成第一刀：

- 导入时写 `memory/entity_aliases.yaml`，并在 `memory_manifest.json` 登记 `entity_aliases` layer。
- alias skeleton 从 `characters.yaml`、`world.yaml` 的地点/势力和 `memory/canon_ledger.jsonl` 的 entities deterministic 生成。
- `load_entity_aliases()` 对缺失/损坏文件分别返回 `missing` / `damaged`，检索与 UI 均稳定降级。
- `retrieve_context()` 读取 alias index，对 query 与 corpus 文本做轻量 alias expansion；`retrieval_context.json` item 可带 `resolved_entities`。
- `consistency_report.json` summary additive 写入 `entity_alias_count`；世界锚定页只读展示别名表状态和样例。

明确未做：LLM/NER 实体抽取、人工别名编辑、跨 run 写回别名、向量检索。

#### v0.8.x：Runtime Memory Consumption-A

目标：在不改 `run_scene` 默认行为、不引入新 runner 的前提下，让 imported 项目的运行时真正只读消费 memory/alias/ledger 安全子集，并留下可审计 artifact。

当前已完成第一刀：

- 新增 `runtime_memory.py`，把 entity alias 状态、query 实体归一化、`retrieve_context()` 结果、consumed layers 与 warnings 打包为 `RuntimeMemoryContext`。
- `service.run_intervention()`、baseline 服务与 CLI resume 通过既有 `retrieved_context` 参数把该 prompt block 注入 character agent / narrator；`run_scene` 签名与默认语义不变。
- 分支目录 additive 写 `runtime_memory_context.json`，字段含 `query/current_chapter/prompt_block/consumed_layers/entity_aliases/resolved_query_entities/warnings/retrieval`。
- `entity_aliases.yaml` 缺失或损坏只降级为 warning，不阻断生成。
- `browser.indexer.get_branch()` additive 返回 `runtime_memory_context`；React 右侧解释面板新增「运行记忆」只读标签页。

明确未做：让 `act_director_plan.json`、`dynamic_action_registry.yaml`、`emergence_nodes.json` 真正驱动状态变化；运行后写回一致性审计。

#### v0.8.x：Frontend Artifact Panel

目标：把 v0.8+ 已经落盘但分散的解释性 artifact 收束到产品前端右侧只读解释层，让用户在读分支正文时能一次看懂“引擎为什么这样写、还留下了哪些后续机会”。

当前已完成第一刀：

- `browser.indexer.get_branch()` additive 返回 run 级 `act_director_plan.json`、`dynamic_action_registry.yaml`、`emergence_nodes.json` 与 branch 级 `narrative_diagnostics.json`，并保留既有 `runtime_memory_context.json`。
- 缺失 artifact 返回 `None`，损坏 JSON 返回 `{}`，损坏 YAML 返回 `None`；前端只展示空态，不白屏。
- React 右侧解释面板新增「机制档案」tab，统一展示运行记忆、动作计划、动作注册表、叙事诊断、涌现节点；原「运行记忆」独立 tab 收束进该只读面板。

明确未做：runner 消费动作计划/动作注册表/涌现节点并改变世界状态；运行后一致性审计写回；跨 run 涌现节点聚类和推荐系统。

#### v0.8.4：Consistency Audit / 长篇一致性审计

审计维度：

- 角色一致性：目标、恐惧、关系、口癖、能力边界是否漂移。
- 时间线一致性：日期、地点、同时性、事件先后是否矛盾。
- 资源一致性：道具、伤势、货币、灵力、身份、秘密是否凭空变化。
- 战力与合约：是否越过世界规则或题材边界。
- 伏笔与债务：未解伏笔是否遗忘，设定改动是否产生 propagation debt。

输出：

```text
consistency_report.json
  persona_drift
  timeline_conflicts
  resource_conflicts
  contract_violations
  forgotten_threads
  repair_suggestions
```

> **v0.8.4-A 已落地（2026-05-30）**：先做导入级静态一致性审计，不打 LLM、不接 runner。导入时写 `memory/consistency_report.json`，并在 manifest 登记 `consistency_report` layer；报告包含 `persona_drift`、`timeline_conflicts`、`resource_conflicts`、`contract_violations`、`forgotten_threads`、`repair_suggestions`。当前审计来源为 `import_report` 风险（乱码/重复章名/缺章）、`canon_ledger` 是否为空、开放伏笔待追踪。已验证：`tests/test_v084_consistency_audit.py` 2 passed；v0.8 导入/记忆/检索回归 61 passed。

#### v0.8.5：Long Canon Replay Evaluation / 长篇正史回放评估

如果用户上传完结小说，需要严格隔离运行时可见文本和隐藏评估集：

```text
runtime_visible/
  前 N 章，角色和 narrator 可以看到

holdout_private/
  后续章节，只给 evaluator 看
```

原则：

- 后续章节不得进入 retrieval、character_agent、narrator、multi_agent_runner prompt。
- evaluator 可以读取 holdout，生成 `canon_replay_report.json`。
- 如果用户只上传第一章，系统只能合理预测后续，不能承诺复现原作。
- 如果用户上传全本，默认只作为本地个人评估，不提供公开分发受保护文本续写的能力。

验收标准：

- 能导入 100 万字以上文本并生成结构化导入报告。
- 导入任务可恢复，失败后不丢已完成章节。
- 无干预续章时能引用相关正史证据，而不是只看最近几章。
- 生成后能发现至少一类人设、时间线、资源或伏笔矛盾。
- 隐藏评估集不会泄漏到角色和 narrator。

> **v0.8.5-A 已落地（2026-05-30）**：在 v0.7.4 holdout/replay 基础上补长篇可见/隐藏边界。`write_holdout()` 保留旧 `canon/holdout/chapter_*.md`，同时镜像到根目录 `holdout_private/chapter_*.md`，并写 `canon/visibility_manifest.json`：其中 `runtime_visible` 指向可检索/可运行的 `source/` 章节，`holdout_private` 只给 evaluator 使用。`get_holdout()` additive 返回 `visibility_manifest` 摘要；检索测试确认 holdout 私有文本不会进入 `retrieval_context`。已验证：`tests/test_v085_long_canon_replay.py` 3 passed；Canon Replay / 检索回归 68 passed。

### v0.8.6-v0.8.10：长篇产品化收束

v0.8.x Long Upload Productization 已让 txt/md/zip/epub 能通过浏览器分片进入现有导入流水线，但产品还需要把“上传成功”收束成“用户确认系统理解了原文”。因此 v0.8 后半段按以下顺序推进，不直接跳 v0.9。

| 版本 | 名称 | 范围 | 验收重点 |
| --- | --- | --- | --- |
| v0.8.6 | Long Import Review | 导入报告细化、章节列表/正文片段预览、导入质量空态、坏 zip/epub/空文件/章节过少等错误态 | 用户导入后能确认章节、来源文件、风险与可体验范围 |
| v0.8.7 | Resumable Ingest Jobs | 服务端分片 session、断点续传/恢复、hash 校验、重复 chunk 幂等、过期清理 | 刷新/中断后可恢复，不重复写坏项目 |
| v0.8.8 | Long Project Workspace | 长篇项目详情页，集中展示章节、记忆、正史账本、实体别名、检索命中、审计报告 | 已收口：上传后的项目成为可回看的创作资产 |
| v0.8.9 | Long Replay & Audit UI | 长篇 Canon Replay / Consistency Audit 前端产品化，支持章节范围、风险维度和实体归一化审计展示 | 已收口：用户能看到长篇偏移、冲突、伏笔风险 |
| v0.8.10-A | Runner State Execution Spike | opt-in 评估动作计划、动作注册表、涌现节点是否能安全转成状态变化；不改默认行为 | 已收口：给 runner 状态执行层做可回退 dry-run 验证 |
| v0.8.10-B | Runner State Execution MVP | Spike 可行后做最小状态执行层，保持 artifact/API additive 与可回退 | 已收口：low-risk delta 显式写入 overlay，可回滚，默认链路仍安全 |

> **v0.8.6 已落地（2026-05-31）**：`import_report.json` 升级为 additive `v0.8.6` 报告，新增来源信息、章节统计、章节片段、解析 warning、质量风险与建议动作；`get_story()` / `get_world_anchor()` additive 返回 `import_review`，报告缺失或损坏时从 `source/` 章节稳定降级为 `missing` / `damaged` 空态；前端世界锚定页新增「导入检查」区，帮助用户理解导入了什么、有什么风险、下一步做什么。坏 zip / epub / 空文件 / 章节过少会返回更明确的 400 或前端失败空态。已验证：新增 v0.8.6 测试 4 passed；导入相关回归 22 passed；完整后端 577 passed；前端 build 通过。

> **v0.8.7 已落地（2026-05-31）**：新增持久化 ingest session，`POST /api/ingest-sessions` 创建 session，`GET` 查询缺失分片，`POST /chunks` 写单片并对重复 chunk 做幂等，`POST /complete` 合并分片后复用既有 import job。服务端 manifest 记录 chunk sha256、file sha256、过期时间和 import request；缺片、冲突、坏 session 分别降级为 409/409/400 或 404。前端导入页改为 localStorage 恢复 session，只补缺失分片并逐片 sha256，完成后进入既有 job 轮询。已验证：新增 v0.8.7 测试 4 passed；导入/job 回归 28 passed；完整后端 581 passed；前端 build 通过。

> **v0.8.8 已落地（2026-05-31）**：新增 `GET /api/stories/<slug>/project-workspace`，聚合导入检查、章节预览、分层记忆、正史账本、实体别名、最近检索命中、静态审计和下一步入口。缺失或损坏的记忆/正史/审计 artifact 降级为 `missing` / `damaged` 空态；非法 slug 返回 400，缺失项目返回 404。前端 `WorkspacePage` 在未选择世界线时展示长篇项目资产页，选中世界线后保留原阅读、机制档案与干预体验。已验证：新增 v0.8.8 测试 3 passed；完整后端 584 passed；前端 build 通过。

> **v0.8.9 已落地（2026-05-31）**：新增 `run_canon_replay_range()` 和 `canon_replay_range_report.json`，支持按章节范围批量回放并汇总平均分、风险等级、弱章、风险维度和实体审计。新增 `GET /api/stories/<slug>/replay-audit` 与 `POST /api/stories/<slug>/canon/replay-range`，聚合 baseline、range replay、静态审计维度、实体别名和下一步建议；slug/run/branch 均安全校验，错误降级为 400/404/409 或前端空态。前端「回放与审计」面板支持 holdout 状态、单章回放、章节范围回放、风险维度和实体归一化审计。已验证：新增 v0.8.9 测试 3 passed；完整后端 587 passed；前端 build 通过。

> **v0.8.10-A 已落地（2026-05-31）**：新增 `runner_state_execution_report.json` dry-run 评估，读取动作计划、动作注册表与涌现节点，输出候选状态变化、gate 状态、阻断原因、warnings 与 MVP 前置清单。新增 `POST /api/runs/<run_id>/state-execution-evaluate` 与 `GET /api/runs/<run_id>/state-execution-report`；run id 安全校验，缺失报告 404、损坏报告 400、缺必要 artifact 409。前端右侧「机制档案」新增「状态执行评估」区，可生成/重评估报告并展示候选 delta、阻断和安全说明。已验证：新增 v0.8.10-A 测试 4 passed；完整后端 591 passed；前端 build 通过。该 Spike 不写 `state_snapshot.json`，不改 `run_scene` 默认行为。

> **v0.8.10-B 已落地（2026-05-31）**：新增 `apply_runner_state_execution()` 与 `rollback_runner_state_execution()`，必须显式 `confirm=True` 才会把 dry-run 报告中的 low-risk / executable / 白名单 delta 写入分支 `state_execution_overlay.json`；原 `state_snapshot.json` 不被覆盖。新增 `runner_state_execution_apply_report.json` 与 `runner_state_execution_rollback_report.json`，并开放 `POST /api/runs/<run_id>/state-execution-apply`、`POST /api/runs/<run_id>/state-execution-rollback`；未确认 400，缺报告 404，无可应用候选 409，坏 id 400。前端「状态执行评估」区新增应用低风险状态与回滚覆盖层按钮。已验证：v0.8.10 测试扩充至 8 passed；完整后端 595 passed；前端 build 通过。

### v0.9.0-alpha：Long Novel Creation Loop

v0.9.0-alpha 已启动。它应把长篇上传、记忆、分支运行、审计、世界线选择和导出串成完整产品闭环：

```text
上传原作/设定 -> 查看记忆与导入报告 -> 发起分支运行 -> 审计偏移 -> 选择世界线 -> 导出章节
```

> **v0.9.0-alpha Chapter Export 已落地（2026-05-31）**：新增只读 `build_chapter_export()`，从所选分支读取 `chapter.md`、`worldline_judgement.json`、`causal_diff.json` 与可选 `state_execution_overlay.json`，返回包含来源说明、AI 生成说明、评审摘要和章节正文的 Markdown 导出负载；不写回 `chapter.md`，不改 `run_scene` 默认行为。新增 `GET /api/runs/<run_id>/branches/<branch_id>/chapter-export`，坏 id 400、缺章节 404。前端阅读区新增「导出章节」按钮，下载当前世界线 Markdown 并给出中文成功/失败状态。已验证：新增 v0.9.0-alpha 测试 3 passed；完整后端 598 passed；前端 build 通过。

> **仍未整体收口**：世界线选择/继续创作清单、运行后审计写回、多章节合集导出、公开分享、版权工作流、provider/cost gateway 均未进入本子刀。

### Phase 5：社区与分享

远期方向：

- 世界线摘要分享。
- 导出分支小说。
- 世界线模板市场。
- 用户上传原创世界供他人干预。
- 本地个人使用与公开分享的版权边界。

暂不建议现在投入。原因是底层世界线连续性、文本导入和 UI 尚未稳定。

## 6. 两条优先主线

### 主线 A：演示 / 连续剧

适合目标：

- 对内汇报。
- 对外 demo。
- 让别人快速理解“活体小说”。

推荐顺序：

```text
v0.1.2 resume continue
  -> v0.1.3 resume intervene
  -> v0.4 只读世界线浏览器（已完成）
  -> v0.3 Context Retrieval Lite
  -> v0.4.2 检索记忆展示与 UI polish
  -> v0.5 第四面墙轻量版
```

理由：

- 不依赖真实文本导入。
- 当前《天荒城残夜》已经足够支撑演示。
- UI 已提升可感知价值；下一步让 UI 能展示“引擎为什么这么判断”。

### 主线 B：真实用户 / 自有内容

适合目标：

- 续写断更。
- 同人探索。
- 作者大纲压测。

推荐顺序：

```text
v0.1.2 resume continue
  -> v0.2 import-novel
  -> v0.1.3 resume intervene
  -> v0.4 Web UI（已完成）
  -> v0.3.0 Context Retrieval Lite（已完成）
  -> v0.3.1 retrieval artifact + Brief 接入（已完成）
  -> v0.4.2 检索记忆展示（已完成）
  -> v0.5 第四面墙（已完成）
  -> v0.6.0 Runner Adapter（已完成）
  -> v0.6.1 Multi-Agent Runner Protocol（已完成）
  -> v0.6.2 multi_agent_stub runner（已完成）
  -> v0.6.3 multi_agent_trace 可视化（已完成）
  -> v0.6.4 multi_agent_llm 小模型推演（已完成）
  -> v0.6.5 推演工程可靠性：generation_meta/质量校验/重试/usage（已完成）
  -> v0.7 产品级 Web App（已完成九刀主闭环）
  -> v0.7.2 Agent Interaction（角色动作/情绪探针/干预护栏，已收口）
  -> v0.7.3 Visual Asset Generation（Seedream 视觉资产，已收口）
  -> v0.7.4 Baseline & Canon Replay（无干预基线 + 正史回放，已收口）
  -> v0.7.5 Worldline Judge（世界线评分 + 故事弧 + emergence_score，已收口）
  -> v0.8 Long Novel Memory（长篇记忆 artifact 底座，已收口）
  -> v0.8+ ActDirector / Narrator Diagnostics / Dynamic Action / Emergence Mining（已收口底座）
  -> v0.8.x entity aliases / runtime memory consumption / 前端 artifact 面板（已收口）
  -> 长篇上传产品化（已收口）
  -> v0.8.6 Long Import Review（已收口：导入报告细化 + 章节预览 + 质量/失败空态）
  -> v0.8.7 Resumable Ingest Jobs（已收口：断点续传与恢复）
  -> v0.8.8 Long Project Workspace（已收口：长篇项目资产页）
  -> v0.8.9 Long Replay & Audit UI（已收口：长篇回放与审计 UI）
  -> v0.8.10-A Runner State Execution Spike（已收口：状态执行层 dry-run 评估）
  -> v0.8.10-B Runner State Execution MVP（已收口：最小 opt-in 状态写入）
  -> v0.9.0-alpha Long Novel Creation Loop（进行中：Chapter Export 已收口）
```

理由：

- 用户自己的书才是真实需求验证。
- 导入质量决定后续干预体验。
- WenShape 的上下文工程已在 v0.2.2 固化为产物；v0.3 要把它们接入运行时。

## 7. 推荐执行顺序

综合工程风险、演示价值和产品心智，推荐如下：

| 优先级 | 版本 | 目标 | 状态 |
| --- | --- | --- | --- |
| P0 | v0.1.2 resume continue | 沿分支续写下一章 | 已收口 |
| P1 | v0.1.3 resume intervene | 在已选分支上再次干预 | 已收口 |
| P2 | v0.2 import-novel | 支持用户自己的文本 | 已收口 |
| P2.5 | v0.2.1 resume on projects | 导入项目可续章/再干预 | 已收口 |
| P2.6 | v0.2.2 精华固化 | genre templates / facts / summaries / story_contract | 已收口 |
| P2.7 | v0.4 只读 UI + v0.4.1 边界加固 | 世界线可视化、安全校验、稳定降级 | 已收口 |
| P3 | v0.3.0 Context Retrieval Lite | BM25 lite / 章节距离衰减 / prompt 注入 | 已收口 |
| **P3.1** | **v0.3.1 检索 artifact + Brief** | **retrieval_context.json / source_weight / VolumeBrief** | **已收口** |
| P4 | v0.4.2 UI polish | 检索记忆展示、阅读体验优化 | 已收口 |
| P5 | v0.5 第四面墙 | 干预记忆、角色觉察与抗拒 | 已收口 |
| P6.0 | v0.6.0 Runner Adapter | 可插拔 SceneRunner / 注册表 / 契约 additive | 已收口 |
| P6.1 | v0.6.1 Multi-Agent Protocol | `protocol.py` 数据结构骨架 + 设计文档（未接入运行） | 已收口 |
| P6.2 | v0.6.2 multi_agent_stub | `projection.py` + stub runner；协议→投影→契约；非默认 | 已收口 |
| P6.3 | v0.6.3 trace 可视化 | browse「Agent 轨迹」标签页 + 树角标；additive API | 已收口 |
| P6.4 | v0.6.4 multi_agent_llm | 共享装配层 + 小模型推演 `MultiAgentTrace`；非默认；隐私加固 + 健壮回退 | 已收口 |
| P6.5 | v0.6.5 推演工程可靠性 | generation_meta + trace 质量校验器 + 有限重试 + token usage | 已收口 |
| P7.1-A | v0.7.1-A Intervention Compiler 最小闭环 | rule-based 自由输入 -> AbstractIntervention -> 动态 BranchAxis | 已收口 |
| P7.1-B | v0.7.1-B LLM Compiler | LLM 编译 + fallback + rule_rewrite 安全兜底 | 已收口 |
| P7.1-C | v0.7.1-C Causal Diff 后端数据 | `causal_diff.json`；段落级 old/new diff；确立/抹除/回滚字段预留 | 已收口 |
| **P7** | **v0.7 Product Web App** | **React/Vite 产品级前端，Web 内导入/创世/锚定/干预/Causal Diff/设置/异步 Job；见 `docs/completed/v0.7-product-web-app-ui-spec.md`** | **已收口** |
| P7.2 | v0.7.2 Agent Interaction | CharacterAction / CharacterProbe / InterventionGuardrail / 轻量角色配置 UI | 已收口 |
| P7.3 | v0.7.3 Visual Asset Generation | 接入 Seedream 5.0 Lite：故事封面、角色头像、场景背景（世界线节点缩略图预留字段+UI 占位）；无 Key 古风占位降级 | 已收口 |
| P7.4 | v0.7.4 Baseline & Canon Replay | 无干预基线（不写 intervention.json/causal_diff.json）；正史 holdout 读写；deterministic 回放评估（不打 LLM）；锚定页区块 | 已收口 |
| P7.5 | v0.7.5 Worldline Judge | branch 级 `worldline_judgement.json`、世界线评分、anti-slop、emergence_score、故事弧/转折点/张力、工作台右侧评审标签页 | 已收口 |
| P8 | v0.8 Long Novel Memory | 长篇导入报告、分层记忆、正史账本、账本检索、一致性审计、隐藏评估集隔离 | 已收口底座 |
| P8.1 | v0.8+ Action/Discourse/Emergence | ActDirector、叙事诊断、动态动作注册表、涌现节点汇总 | 已收口底座 |
| P8.2 | v0.8.x 收束 | entity aliases、runner consumption、前端 artifact 面板、长篇上传产品化 | 已收口 |
| P8.6 | v0.8.6 Long Import Review | 导入报告细化、章节预览、导入质量空态、失败空态收束 | 已收口 |
| P8.7 | v0.8.7 Resumable Ingest Jobs | 服务端分片 session、断点续传/恢复、hash 校验、重复 chunk 幂等、过期清理 | 已收口 |
| P8.8 | v0.8.8 Long Project Workspace | 长篇项目详情页：章节、记忆、正史账本、实体别名、检索命中、审计报告 | 已收口 |
| P8.9 | v0.8.9 Long Replay & Audit UI | 长篇 Canon Replay / Consistency Audit 前端产品化 | 已收口 |
| P8.10-A | v0.8.10-A Runner State Execution Spike | opt-in 评估动作计划/动作注册表/涌现节点是否可安全转成状态变化；不改默认行为 | 已收口 |
| P8.10-B | v0.8.10-B Runner State Execution MVP | Spike 可行后做最小状态执行层，保持 artifact/API additive 与可回退 | 已收口 |
| P9.0-alpha | v0.9.0-alpha Long Novel Creation Loop | 上传 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出 | 进行中：Chapter Export 已收口 |
| P9.1 | v0.9.1 Provider & Cost Gateway Lite | 多 provider 配置、模型路由、成本/用量估算、失败回退、Key 脱敏展示 | 待 v0.9.0-alpha 后按成本/稳定性触发 |
| P9.2 | v0.9.2 MasterSetting Workspace Lite | 项目级世界设定、人物、时间线、道具、伏笔、章节摘要的只读/轻编辑工作台 | 待长篇项目页稳定后 |
| P9.3 | v0.9.3 Graph Memory Evaluation Spike | 评估 Zep / 图数据库 / GraphRAG 是否增强 `canon_ledger` + BM25 + entity aliases | 待 50+ 章或百万字项目召回不足时触发 |
| P9.4 | v0.9.4 Advanced Runner Evaluation Spike | 评估 LangGraph 局部 runner、OASIS/CAMEL 可选 runner | 待 v0.8.10 状态执行层不足时触发 |
| P10 | v1.0-beta Commercial Hardening | 账号/项目空间、权限、云端持久化、配额、审计日志、版权提示、部署与观测 | 待真实外部用户/团队长期使用 |

## 8. 近期详细任务清单

### 8.1 v0.1.2 收口任务（已完成）

- [x] `resume continue` 命令与 `meta.json` 父链
- [x] 读取父分支快照/事件/章节，输出 `linear/`
- [x] mock 测试 + `engine/README.md`
- 验收 run：`run_20260528_155153_c3275c_continue_branch_a`

### 8.2 v0.1.3 收口任务（已完成）

- [x] `resume intervene` 从续章 `linear` 再干预三分叉
- [x] lineage / 第十五章章节号 / 传讯玉简归属锁等质量修复
- [x] pytest 46 passed
- 验收 run：`run_20260528_171207_94a6b9_resume_intervene_linear`

### 8.3 v0.2 实施任务（已收口）

设计文档：[v0.2-import-novel-mvp.md](./v0.2-import-novel-mvp.md)

**PR-A（已完成）**

- [x] `import_novel` 包：`splitter` / `mock_extractor` / `writer` / `validator`
- [x] `lne import-novel tests/fixtures/mini_novel/ --name test-story --mock` → `projects/test-story/`
- [x] 产物：`source/`、`world.yaml`、`characters.yaml`、`canon_chapter.md`、`anchor_proposal.yaml`、`import_meta.json`
- [x] `lne list-projects` / `show-project` / `validate-project`
- [x] 覆盖保护 `--force`
- [x] 单测 26 项

**PR-B（已完成）**

- [x] `story_loader.py`：`load_story(slug)` 统一 `projects/` 与 `samples/`
- [x] `intervention.json` / `meta.json` 写入 `story_slug`、`source_kind`（不再默认 `tianhuang-night`）
- [x] 天荒城硬编码规则按 `source_type` 隔离（`scene_runner`、`character_agent`）
- [x] `lne intervene cli-test --target zhao_xuan ... --mock` → 三分叉，无天荒城污染
- [x] 单测 6 项；全量 79 passed

**PR-C（已完成）**

- [x] `llm_extractor.py`：world pass + character pass
- [x] `lne import-novel <path> --name <slug>`（无 `--mock`）调 LLM
- [x] JSON 解析容错、字段补全、`validate_and_repair`
- [x] 单测 11 项；全量 **90 passed**

**v0.2.1（已完成）**

- [x] `resume/loader` 改用 `load_story`，`ParentSnapshot` 含 `story_slug` / `source_kind`
- [x] `meta.json` / `intervention.json` 稳定写入 story 元数据
- [x] `resume continue` / `resume intervene` 传 `source_type`，imported 不走天荒城规则
- [x] `test_resume_imported_project.py`；全量 **94 passed**

**v0.2.2（已完成）**

- [x] 复制并归档 37 个 genre templates，加入 `genre_loader.py` 与 `list-genres`
- [x] `import-novel` 自动生成 `canon/facts.jsonl`
- [x] 自动生成 `summaries/chapter_*.yaml`
- [x] 自动生成 `story_contract.yaml`
- [x] `validate-project` 增加 facts / summaries / story_contract warning 级校验
- [x] `docs/research/open-source-essence-absorption.md`

### 8.4 v0.4 / v0.4.1 收口任务（已完成）

- [x] `lne browse`：stdlib HTTP + 零新依赖
- [x] `/api/stories`、`/api/tree`、分支详情 API
- [x] 三栏只读 UI：故事列表、世界线树、章节阅读、状态面板、CLI hints
- [x] `validators.py` 统一 URL identifier 校验
- [x] 多 root / 多 orphan 排序稳定，孤儿 run 可识别
- [x] 前端 loading / error / 空态兜底，不因缺文件白屏
- [x] `docs/v0.4-worldline-browser-release.md`
- [x] 全量 **145 passed**

### 8.5 v0.3.0 实施任务（已收口）

目标：把 v0.2.2 生成的 `facts.jsonl`、`summaries/`、`story_contract.yaml` 接入运行时。

- [x] 新建 retrieval 模块，加载 facts / summaries / story_contract 为统一 corpus item
- [x] 实现 BM25 lite / 关键词检索，不引入向量库和 embedding
- [x] 实现章节距离衰减，并区分事实、章节摘要、世界规则的 `source_weight`
- [x] 在 `character_agent` prompt 注入 `retrieved_context`
- [x] 在 narrator / chapter renderer prompt 注入 `retrieved_context`
- [x] 将检索结果写入 run metadata 或独立 artifact，供 v0.4.2 UI 展示
- [x] imported project 缺少检索文件时稳定降级
- [x] 测试覆盖排序、距离衰减、prompt 注入、缺文件降级、builtin/imported 隔离
- [x] 全量 **174 passed**

### 8.6 v0.3.1 实施任务（已收口）

- [x] `SimulationResult.retrieval_record` + `retrieval_context.json` 写盘（intervene / resume continue / resume intervene）
- [x] `source_weight` + contract 不衰减
- [x] `context_loader` 读 VolumeBrief；`evidence_refs` 进入 SummaryItem
- [x] retriever corpus 含 volume brief；items 含 source/text/chapter/evidence
- [x] 真实 `tianhuang-night` builtin 隔离测试
- [x] 全量 **183 passed**

### 8.7 后续排期触发条件

| 能力 | 开始时机 |
| --- | --- |
| ~~v0.4.2 UI polish~~ | **已完成**（v0.4.2）：`retrieval_context.json` 已在 browse「检索记忆」标签页按 source 分组展示 |
| ~~v0.5 第四面墙~~ | **已完成**（v0.5）：干预记忆账本 + 五级觉察 + 决策/渲染注入；`LNE_FOURTH_WALL` 可关闭 |
| ~~v0.6.0 Runner Adapter~~ | **已完成**（v0.6.0）：可插拔 `SceneRunner` + 注册表，`LNE_SCENE_RUNNER` 可切换 |
| ~~v0.6.1 Multi-Agent Protocol~~ | **已完成**（v0.6.1）：`protocol.py` 数据结构骨架 + 设计文档（未接入运行） |
| ~~v0.6.2 multi_agent_stub~~ | **已完成**（v0.6.2）：`projection.py` + stub runner，协议→投影→契约，非默认，私有不泄漏 |
| ~~v0.6.3 trace 可视化~~ | **已完成**（v0.6.3）：browse「Agent 轨迹」标签页 + 树角标，缺失空态/损坏不抛 |
| ~~v0.6.4 multi_agent_llm~~ | **已完成**（v0.6.4）：OpenAI-compatible API 小模型推演 `MultiAgentTrace`，非默认，隐私加固 + 健壮回退 |
| ~~v0.6.5 推演工程化~~ | **已完成**（v0.6.5）：generation_meta + trace 质量校验器 + 有限重试 + token usage |
| Zep / OASIS / CAMEL | 长篇记忆或群体仿真强到自研轻量 runner 不够时，分别作为 v0.9.3 / v0.9.4 spike 评估项 |
| ~~v0.7 Product Web App~~ | **已完成**：React/Vite 前端、三入口、锚定编辑、Web 干预、Causal Diff、设置、异步 Job 主闭环 |
| v0.7.2 Agent Interaction | v0.7 产品前端跑通后，需要角色动作、情绪探针、干预护栏和轻量角色配置时 |
| v0.7.3 Visual Asset Generation | 产品 UI 需要角色头像、故事封面、场景背景和世界线节点图，且不阻塞文字主链路时 |
| v0.7.4 Baseline & Canon Replay | 需要比较无干预基线与干预后偏离，或用后续章节做正史回放评估时 |
| v0.7.5 Worldline Judge | v0.7 产品前端跑通后，需要帮助用户选择“哪条世界线值得继续”时 |
| v0.8 Long Novel Memory | 用户上传 100 万字以上作品，或出现角色漂移、时间线矛盾、伏笔遗忘、BM25 召回不足时 |
| v0.8 ActDirector | 多次干预后需要把读者高层意图稳定转成角色动作序列时 |
| v0.8 Discourse-aware Narrator | 分支正文出现太平、过早收束、缺少重大挫败和高潮时 |
| v0.8 Dynamic Action Registry | 用户频繁提出未预设动作，需要动态动作落地为状态变化时 |
| v0.8 Emergence Mining | 积累大量用户干预后，需要挖掘高价值涌现节点和世界线模板时 |
| 向量数据库 / embedding / reranker | BM25 lite 在 50+ 章导入项目上召回不够时 |
| MasterSetting Workspace Lite | 服务作者/编辑而不只是读者干预，且长篇项目页稳定后；先做轻量版，不做完整作者工作台 |
| Provider & Cost Gateway Lite | 出现成本、稳定性、模型路由、客户私有化部署要求时；排在 v0.9.1 |

**预研（并行、不阻塞 MVP）**

先写研究文档，再按需吸收：

```text
docs/research/
├── wenshape-analysis.md
├── mirofish-analysis.md
├── webnovel-writer-analysis.md
├── eastworld-agent-interaction-triage.md
├── autonovel-static-pipeline-triage.md
├── ai-novel-generator-context-triage.md
├── paper-player-driven-emergence-integration.md
├── paper-storyverse-abstract-acts-integration.md
├── paper-human-level-narratives-discourse-integration.md
├── paper-story2game-action-system-integration.md
├── integration-strategy.md
└── phase1-roadmap.md
```

WenShape 优先阅读路径：

1. `backend/app/context_engine/`
2. `backend/app/services/`
3. `backend/app/storage/`
4. `backend/app/agents/`
5. `backend/app/llm_gateway/`
6. `frontend/src/pages/`

研究问题：

- 它如何组织项目目录。
- 它如何保存人物卡、世界观卡、文风卡。
- 它如何构建 `facts.jsonl`。
- 它如何做章节距离衰减。
- 它如何做同人导入 proposal，而不是直接写入。
- 哪些机制可以借鉴，哪些会把我们带偏成作者工作台。

eastworld 研读边界：

- 只看 Agent Actions、Emotion Query、Player Guardrails、Agent Studio 配置体验。
- 只吸收交互协议和 UI 设计，不接 server / Redis / generated client。
- 不把 LNE 改成游戏 NPC 框架。
- 目标是增强 `CharacterAction`、`CharacterProbe`、`InterventionGuardrail`。

autonovel / AI_NovelGenerator 研读边界：

- 只看评审团、anti-slop、上下文压缩、一致性检查。
- 不复刻静态写稿流水线。
- 不引入源码依赖。
- 不改变 LNE 的命运沙盘 / 读者干预主线。

## 9. 数据结构演进

### 当前 Phase 0

```text
samples/
outputs/
  run_xxx/
    branch_a/
    branch_b/
    branch_c/
```

适合 demo，但不够支撑导入、多次干预和 Web UI。

### v0.2 后建议

```text
projects/
  <story_slug>/
    source/
    cards/
      characters/
      world/
      style.yaml
    canon/
      facts.jsonl
      open_threads.yaml
    summaries/
    world.yaml
    runs/
      run_xxx/
```

优势：

- 每本书有独立项目空间。
- 世界状态、原文、事实库、run 记录分离。
- Web UI 更容易读取。
- 后续可接 Git 版本管理。

## 10. 风险与取舍

| 风险 | 说明 | 应对 |
| --- | --- | --- |
| 过早集成 Zep / OASIS / CAMEL | 账号、服务、依赖、数据同步与调试成本高，会稀释 LNE 叙事运行时主线 | v0.6.4 已自研 `multi_agent_llm`；v0.8+ 再按触发条件评估 |
| 变成普通 AI 续写器 | 只生成文字，不维护世界状态 | 坚持 snapshot、events、contract、lineage |
| 变成 WenShape 式作者工作台 | 功能堆到写作管理，而非读者干预 | v0.2 只借鉴上下文工程，不复制产品定位 |
| 导入质量不稳定 | LLM 抽取角色/规则会漏 | proposal + 人工确认 + 可编辑 YAML |
| 版权风险 | 续写商业小说容易涉及公开传播问题 | 本地个人使用优先，禁止冒充原作者和公开分发受保护内容 |
| 章节越写越漂 | 长篇状态不一致 | v0.3 用 facts.jsonl + summaries + story_contract 做检索注入 |
| 第四面墙滥用 | 太早出现会变俗套 | **默认开启**；可用 `LNE_FOURTH_WALL=0` 完全关闭（不累积、不落盘、不注入）；多次强干预后分数自然升高 |
| 过早做产品级前端 | React/交互工程会吞掉大量时间，但核心玩法尚未完全证明 | v0.7 再做；v0.5/v0.6 先补独特机制 |
| 误把 eastworld 当运行时底座 | eastworld 的互动 Agent 很接近，但直接接入会引入 server / Redis / client 复杂度 | v0.7.2 只吸收 Actions / Emotion Query / Guardrails / Agent Studio 设计 |

## 11. 产品决策待拍板

1. v0.1.2 是否只做 `resume continue`，把再次干预放到 v0.1.3？建议：是。
2. v0.2 导入是否先支持单文件 txt/md，而不是网页抓取？建议：是。
3. 世界线默认固定三分支，还是用户选择生成数量？建议：Phase 0/1 固定三分支，UI 后再开放。
4. 干预是否引入成本/冷却？建议：v0.5 前只做风险提示，不做硬成本。
5. 第四面墙默认开关？建议：**默认开启**；题材敏感或演示时可设 `LNE_FOURTH_WALL=0` 关闭。
6. MVP 文案主打“续写断更”还是“拯救意难平”？建议：对外主打“拯救意难平”，功能上兼容续写断更。

最新决策（2026-05-29）：

- 固定三分支只适用于早期 demo 和信息型干预；长期产品不固定相信/怀疑/拒绝。
- 每次自由输入干预都应先生成 `AbstractIntervention` 和本次 `BranchAxis`。
- 普通规则内分叉记为 `Divergent Worldline`；改写世界前提或题材规则的强干预记为 `Alternate Novel / AU Worldline`。
- 例如中世纪/修仙世界中的 AK47、系统降临、现代科技乱入，不能静默塞进原世界线；必须拒绝、转译，或另开 AU 并记录合约差异。

## 12. 一句话结论

v0.1.x、v0.2.x、v0.3.0/v0.3.1、v0.4/v0.4.1、v0.4.2、v0.5/v0.5.1、v0.6.0–v0.6.5 已收口；下一步最稳的路线是：

```text
v0.7.1 Intervention Compiler（自由输入转抽象干预 + 动态分支轴，已完成）
  -> v0.7 Product Web App（React/Vite 产品级前端九刀主闭环，已完成）
  -> v0.7.2 Agent Interaction（角色动作/情绪探针/干预护栏，已收口）
  -> v0.7.3 Visual Asset Generation（Seedream 5.0 Lite 视觉资产，已收口）
  -> v0.7.4 Baseline & Canon Replay（无干预基线 + 正史回放，已收口）
  -> v0.7.5 Worldline Judge（世界线评分 + 故事弧 + emergence_score，已收口）
  -> v0.8 Long Novel Memory（百万字上传 + 分层记忆 + 正史账本 + 一致性审计，已收口底座）
  -> v0.8+ ActDirector / Discourse-aware Narrator / Dynamic Action Registry / Emergence Mining（已收口 A-slices）
  -> v0.8.x entity aliases / runtime memory consumption / 前端 artifact 面板（已收口）
  -> 长篇上传产品化（已收口）
  -> v0.8.6 Long Import Review（已收口：导入报告细化 + 章节预览 + 质量/失败空态）
  -> v0.8.7 Resumable Ingest Jobs（已收口：断点续传与恢复）
  -> v0.8.8 Long Project Workspace（已收口：长篇项目资产页）
  -> v0.8.9 Long Replay & Audit UI（已收口：长篇回放与审计 UI）
  -> v0.8.10-A Runner State Execution Spike（已收口：状态执行层 dry-run 评估）
  -> v0.8.10-B Runner State Execution MVP（已收口：最小 opt-in 状态写入）
  -> v0.9.0-alpha Long Novel Creation Loop（进行中：Chapter Export 已收口）
  -> v0.9.1 Provider & Cost Gateway Lite（按成本/稳定性触发）
  -> v0.9.2 MasterSetting Workspace Lite（长篇项目页稳定后）
  -> v0.9.3 Graph Memory Evaluation Spike（BM25/ledger 召回不足时评估 Zep/图数据库）
  -> v0.9.4 Advanced Runner Evaluation Spike（状态执行层不足时评估 LangGraph/OASIS/CAMEL）
  -> v1.0-beta Commercial Hardening（真实外部用户/团队长期使用时）
```

WenShape 解决“长篇上下文怎么不崩”，webnovel-writer 解决“故事合约和网文味”，MiroFish 解决“角色群体怎么自己动起来”，eastworld 解决“互动媒体 Agent 如何做动作、情绪查询和玩家护栏”的参考问题；四篇论文分别补上“用户涌现、意图调度、叙事质量、动作落地”的理论底座。Living Novel Engine 自己要牢牢抓住的，是它们都没有真正覆盖的核心：

> 读者干预、世界线分支、角色反抗、活体小说运行时。
