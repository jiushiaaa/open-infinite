# Living Novel Engine 产品迭代计划

> 版本：2026-05-29（v0.6.5 多 Agent 推演工程可靠性）  
> 范围：对齐 PRD v0.1-v0.8、仓库根目录 Roadmap、`engine/` 全版本实况。  
> 核心原则：WenShape / webnovel-writer 的可复用资产已吸收至 engine（genre_templates、数据结构概念），外部项目源码目录已删除。后续新能力集中在 `engine/` 编排层和自研 UI/API 层。

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
v0.7     Product Web App     React/Vite 产品级前端，面向普通用户  下一步
    ↓
v0.7.2   Agent Interaction   角色动作/情绪探针/干预护栏/轻量角色配置  待排期
    ↓
v0.7.5   Worldline Judge     读者/编辑评审团 + 静态流水线项目取舍复盘  待排期
    ↓
Phase 5  社区与分享          远期
```

当前最重要的判断：

> v0.6.5 已封板（269 passed）。在 v0.6.4 `multi_agent_llm` 上补工程可靠性：①`generation_meta`（source=llm/fallback/stub、model_name、attempt_count、duration_ms、validation_status、validator_warnings、usage、cost_estimate 占位）additive 写进 `multi_agent_trace.json`，browse「Agent 轨迹」新增「推演元数据」分组可区分真 LLM/回退/stub；②trace 质量校验器 `trace_quality.validate_and_repair_trace`（空 turn_plans 硬失败、回合号归一化、可见性强制、缺计划/干预未入私域告警，绝不抛）；③有限重试 `LNE_MULTI_AGENT_MAX_RETRIES`（默认 1）带问题反馈，耗尽回退；④token usage（`LLMClient.chat_json_with_usage`，拿不到为 null）。不引入新框架/依赖，不接 Zep/OASIS/CAMEL/LangGraph。下一步转向 v0.7 Product Web App，runner 侧暂不再深挖。eastworld 进入 v0.7.2+ 的角色动作/情绪探针/干预护栏预研；autonovel / AI_NovelGenerator 只进入 v0.7.5+ 的质量评审与上下文压缩预研，不改变 v0.7 主线。

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

**版本收口参考 run（验收用）**

| 版本 | 参考 run_id | 说明 |
| --- | --- | --- |
| v0.1.2 | `run_20260528_155153_c3275c_continue_branch_a` | 从 `branch_a` 无新干预续写 `linear/` |
| v0.1.3 | `run_20260528_171207_94a6b9_resume_intervene_linear` | 从续章 `linear` 再干预，生成第十五章三分叉 |

**测试基线**：`cd engine && python -m pytest -q` → **183 passed**（截至 2026-05-28）。

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
- 产品级前端尚未启动；当前 `lne browse` 是研发/演示 viewer，不是普通用户入口（v0.7）。
- embedding / 向量库 / reranker / 多 provider gateway 尚未做，留到规模化后。

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
- 中后期如果出现复杂状态流转（角色并行思考、裁判节点、规则审计节点、反思/重试节点、多轮共识），可在 v0.8+ 局部引入 LangGraph 作为某个 runner 的内部实现，而不是替换主线协议。

因此后续策略是：

- v0.6.4 已完成自研 `multi_agent_llm` runner：通过 OpenAI-compatible API 调用小模型，不本地部署；输出 `MultiAgentTrace` JSON；复用现有 `project_trace` 与共享装配层。
- v0.6.5 已完成推演工程可靠性：generation_meta、trace 质量校验器、有限重试、token usage；并发与精确成本计算留待 v0.8+。
- v0.8+ 若长篇记忆崩，再评估 Zep / 图数据库；若群体仿真需求很强，再评估 OASIS / CAMEL 作为可选 runner。

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

### v0.7：Product Web App / 产品级前端

目标：把当前 CLI + 研发 viewer 升级为普通用户能直接使用的产品入口。

推荐技术路线：

- 新建独立 `ui/`，使用 React + Vite + TypeScript。
- 复用现有 `browser` API 或抽出更稳定的 local API server，不重写引擎。
- 保留 `lne browse` 作为开发者调试 viewer；产品前端另起 `lne web` 或独立 dev server。

首版产品体验：

- 导入小说：选择 txt/md 文件或目录，显示抽取进度与可编辑世界锚定。
- 世界线浏览：产品级世界线树、章节阅读、检索记忆、角色状态。
- 用户干预：在 Web 内输入目标角色与干预内容，触发 `intervene`。
- 选线续章：点击某条分支继续，必要时再干预。
- 运行状态：长任务 loading / error / retry / 日志摘要，不要求用户复制命令。

暂不放进 v0.5 / v0.6 的原因：

- 现在最稀缺的不是页面框架，而是引擎独特性：第四面墙、深度推演、长篇一致性。
- 过早重构 React 会消耗大量工程时间，却无法弥补核心玩法不够独特的问题。
- 等 v0.5/v0.6 证明“普通续写器做不到的体验”后，再做产品级前端，展示价值会更强。

### v0.7.2：Agent Interaction / 角色交互协议增强

目标：在产品级 Web App 的基础体验跑通后，吸收 `eastworld` 的交互媒体 Agent 经验，让角色不仅能“生成剧情”，还能以更稳定的结构执行动作、暴露内心探针、接受干预护栏。

该版本只借鉴 `eastworld` 的交互协议和 Agent Studio 设计，不接入其 server、Redis 或 OpenAPI client。

能力范围：

- `CharacterAction`：角色结构化动作，作为 `MultiAgentTrace` 与 `accepted_events` 之间的中间层。
- `CharacterProbe`：查询角色信任、怀疑、恐惧、第四面墙觉察等内心状态。
- `InterventionGuardrail`：在 `contract_audit` 前先对用户干预做题材、时代、战力、人格边界检查。
- Web UI 轻量角色配置：核心信念、欲望、恐惧、口癖、已知/未知信息、可执行动作。
- Agent 轨迹页增强：把“计划/误解/延迟行动”进一步展示为“角色动作 -> 状态变化 -> 章节渲染”。

建议数据结构：

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
- 越界干预会给出降级建议，而不是直接污染世界状态。
- 不破坏既有 `multi_agent_llm` / `multi_agent_stub` 输出契约。

暂不做：

- 不做完整 no-code Agent 平台。
- 不做游戏引擎 SDK。
- 不接 Redis / eastworld server。
- 不生成 OpenAPI client。

产品价值：

- 把“角色像活人”从正文表现推进到结构化行为层。
- 让用户在 Web UI 中能理解角色行动，而不是只读生成结果。
- 为第四面墙、干预护栏和后续复杂多 Agent 推演打基础。

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
  -> v0.7 产品级 Web App（下一步）
  -> v0.7.2 Agent Interaction（角色动作/情绪探针/干预护栏，待排期）
  -> v0.7.5 Worldline Judge（质量评审层，待排期）
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
| **P7** | **v0.7 Product Web App** | **React/Vite 产品级前端，Web 内导入/干预/续章/浏览** | **下一步** |
| P7.2 | v0.7.2 Agent Interaction | CharacterAction / CharacterProbe / InterventionGuardrail / 轻量角色配置 UI | 待排期 |
| P7.5 | v0.7.5 Worldline Judge | 读者/编辑评审团、世界线评分、anti-slop 检查、质量建议 | 待排期 |
| P8 | v0.8+ Commercial hardening | 向量库、embedding、reranker、多 provider gateway、完整工作台 | 待定 |

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
| Zep / OASIS / CAMEL | 长篇记忆或群体仿真强到自研轻量 runner 不够时，作为 v0.8+ 可选评估项 |
| v0.7 Product Web App | v0.5/v0.6 证明核心玩法后，准备给普通用户试用时 |
| v0.7.2 Agent Interaction | v0.7 产品前端跑通后，需要角色动作、情绪探针、干预护栏和轻量角色配置时 |
| v0.7.5 Worldline Judge | v0.7 产品前端跑通后，需要帮助用户选择“哪条世界线值得继续”时 |
| 向量数据库 / embedding / reranker | BM25 lite 在 50+ 章导入项目上召回不够时 |
| 完整 MasterSetting 工作台 | 服务作者/编辑而不只是读者干预，且目标章节规模到 100+ 章时 |
| 多 provider gateway | 出现成本、稳定性、模型路由、客户私有化部署要求时 |

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

## 12. 一句话结论

v0.1.x、v0.2.x、v0.3.0/v0.3.1、v0.4/v0.4.1、v0.4.2、v0.5/v0.5.1、v0.6.0–v0.6.5 已收口；下一步最稳的路线是：

```text
v0.7 Product Web App（React/Vite 产品级前端）
  -> v0.7.2 Agent Interaction（角色动作/情绪探针/干预护栏）
  -> v0.7.5 Worldline Judge（世界线评审团）
  -> v0.8+ Zep / OASIS / CAMEL / 向量库 / 多 provider / 完整工作台（按规模触发评估）
```

WenShape 解决“长篇上下文怎么不崩”，webnovel-writer 解决“故事合约和网文味”，MiroFish 解决“角色群体怎么自己动起来”，eastworld 解决“互动媒体 Agent 如何做动作、情绪查询和玩家护栏”的参考问题。Living Novel Engine 自己要牢牢抓住的，是它们都没有真正覆盖的核心：

> 读者干预、世界线分支、角色反抗、活体小说运行时。
