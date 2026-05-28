# Living Novel Engine 产品迭代计划

> 版本：2026-05-28（v0.1.3 收口 + v0.2 设计启动）  
> 范围：对齐 PRD v0.1-v0.5、仓库根目录 Roadmap、`engine/` Phase 0 实况，并吸收 WenShape / MiroFish / webnovel-writer 三个开源项目的可借鉴能力。  
> 核心原则：`MiroFish/`、`webnovel-writer/`、`WenShape/` 只读研究和能力参考，不把它们的源码并入最终仓库；Living Novel Engine 的新能力集中在 `engine/` 编排层和后续自研 UI/API 层。

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
v0.2     文本导入与世界锚定  当前 · 见 docs/v0.2-import-novel-mvp.md
    ↓
v0.3     深度多 Agent 推演   接入或借鉴 MiroFish OASIS
    ↓
v0.4     世界线浏览器        Web UI 展示、阅读、对比、选择
    ↓
v0.5     第四面墙机制        干预记忆、角色觉察、反抗命运
    ↓
Phase 5  社区与分享          远期
```

当前最重要的判断：

> v0.1.x 已证明「干预 → 选线续章 → 再干预三分叉」可闭环。下一步要证明引擎能脱离内置样例，吃进用户自己的文本。

因此，短期优先级是 **v0.2 import-novel 最小闭环**，而不是立刻接 MiroFish 或做大而全 Web UI。

## 3. 已完成能力

| 里程碑 | 内容 | 状态 |
| --- | --- | --- |
| Phase 0 Alpha | CLI、`lne list-samples` / `show-sample` / `intervene` / `compare`、内置样例《天荒城残夜》、三分支、mock + 真实 LLM | 已完成 |
| Phase 0 Beta | 状态渲染器、快照钳制、玉简/示警锁、章节非空兜底 | 已完成 |
| v0.1.1 polish | 快照 `location` 同步、天荒城/玉简措辞、正史锁、重生禁用、退魂铃来源、墨青烟错字修正 | 已完成 |
| v0.1.2 resume continue | `lne resume continue <run_id> --branch branch_a`，父链 `meta.json`，`linear/` 续章 | 已完成 |
| v0.1.3 resume intervene | `lne resume intervene <continue_run_id> --branch linear`，续章上再干预三分叉 | 已完成 |

**版本收口参考 run（验收用）**

| 版本 | 参考 run_id | 说明 |
| --- | --- | --- |
| v0.1.2 | `run_20260528_155153_c3275c_continue_branch_a` | 从 `branch_a` 无新干预续写 `linear/` |
| v0.1.3 | `run_20260528_171207_94a6b9_resume_intervene_linear` | 从续章 `linear` 再干预，生成第十五章三分叉 |

**测试基线**：`cd engine && python -m pytest -q` → **46 passed**（截至 2026-05-28）。

当前用户可演示的闭环：

```text
lne intervene <sample>
  -> branch_a / branch_b / branch_c

lne resume continue <run_id> --branch branch_a
  -> linear/

lne resume intervene <continue_run_id> --branch linear
  -> branch_a / branch_b / branch_c
```

当前刻意未完成的能力：

- 上传自己的小说（v0.2 目标）。
- Web 阅读器和世界线树（v0.4）。
- 多场景长程仿真 / MiroFish OASIS（v0.3）。
- 第四面墙数值真正驱动角色行为（v0.5）。

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

Living Novel Engine 当前 `scene_runner` 只是轻量轮询。等 v0.2 解决真实文本导入后，再考虑 v0.3 将它升级为真正多 Agent runtime。

短期不建议过早接 MiroFish，因为它会增加依赖、服务部署、数据同步和调试成本，而当前产品最核心的“连续读下去”还没完全验证。

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

### v0.2：Import Novel 与世界锚定（进行中）

目标：让用户上传自己的文本，不再依赖内置样例。

**最小闭环设计文档**：[v0.2-import-novel-mvp.md](./v0.2-import-novel-mvp.md)

这是 WenShape 最值得借鉴的阶段；v0.2.0 MVP 只实现「能导入 → 能编辑 → 能 intervene」，不复制 WenShape 全量工作台。

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

### v0.3：Deep Simulation 与 MiroFish OASIS

目标：让角色群体推演更像活人，而不是单轮 LLM 即兴。

可分两步：

1. 自研轻量 adapter：保留当前 `scene_runner` 接口，先支持外部 runner 替换。
2. 接 MiroFish/OASIS：通过 HTTP 或子进程调用，不把源码复制进仓库。

接口抽象：

```python
class SimulationRunner:
    def run_scene(world, characters, intervention, branch_seed) -> SimulationResult:
        ...
```

能力目标：

- 多角色并行决策。
- 角色间消息传播。
- 关系和情绪随事件变化。
- 场景内可出现计划、误解、背叛、延迟行动。
- 结构化事件流可被故事合约审计。

验收标准：

- 同一场景至少 5 个 Agent 参与。
- 推演结果能输出结构化 `accepted_events`。
- 合约审计能拦截越界行为。
- 小模型跑推演，大模型写正文的分层策略可配置。

产品价值：

- 形成 Living Novel Engine 与普通 AI 续写器的核心差异：先有世界运行，再有章节文字。

### v0.4：Worldline Browser Web UI

目标：让用户不再盯文件夹，而是能阅读、对比、选择和继续世界线。

建议提前做“只读轻 UI”，不必等 v0.3。

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

第一版只读即可：

- 读取 `outputs/` 和 `projects/`。
- 展示章节、分支和状态。
- 允许复制命令继续运行 CLI。

第二版再加写操作：

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

### v0.5：Fourth Wall Awareness

目标：多次干预后，角色逐渐意识到命运被外部力量触碰。

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
  -> v0.4 只读世界线浏览器
  -> v0.5 第四面墙轻量版
```

理由：

- 不依赖真实文本导入。
- 当前《天荒城残夜》已经足够支撑演示。
- UI 能快速提升可感知价值。

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
  -> v0.4 Web UI
  -> v0.3 MiroFish 深度推演
```

理由：

- 用户自己的书才是真实需求验证。
- 导入质量决定后续干预体验。
- WenShape 的上下文工程应优先服务 v0.2。

## 7. 推荐执行顺序

综合工程风险、演示价值和产品心智，推荐如下：

| 优先级 | 版本 | 目标 | 状态 |
| --- | --- | --- | --- |
| P0 | v0.1.2 resume continue | 沿分支续写下一章 | 已收口 |
| P1 | v0.1.3 resume intervene | 在已选分支上再次干预 | 已收口 |
| **P2** | **v0.2 import-novel** | **支持用户自己的文本** | **当前** |
| P3 | v0.4 只读 UI | 世界线可视化 | 待做 |
| P4 | v0.3 MiroFish adapter | 深度多 Agent 推演 | 待做 |
| P5 | v0.5 第四面墙 | 角色觉察与反抗 | 待做 |

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

### 8.3 v0.2 实施任务（当前）

设计文档：[v0.2-import-novel-mvp.md](./v0.2-import-novel-mvp.md)

**v0.2.0 MVP（先做）**

- [ ] `lne import-novel <path> --name <slug>`：拆分 3–10 章 → LLM 抽取 → 写入 `projects/<slug>/`
- [ ] 输出与 `samples/tianhuang-night/` 同构的 `world.yaml` / `characters.yaml` / `canon_chapter.md` + `anchor_proposal.yaml`
- [ ] `lne list-projects` / `load_project`：与现有 `intervene` / `resume` 共用
- [ ] `lne validate-project <slug>`：YAML/schema 校验
- [ ] mock 抽取路径 + 单测；真实 LLM 为可选验收

**v0.2.1（可后置）**

- [ ] `facts.jsonl`、章节 `summaries/`、文风卡
- [ ] 从 `projects/` 目录 `resume continue` / `resume intervene`

**预研（并行、不阻塞 MVP）**

先写研究文档，再按需吸收：

```text
docs/research/
├── wenshape-analysis.md
├── mirofish-analysis.md
├── webnovel-writer-analysis.md
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
| 过早集成 MiroFish | 多服务、多依赖、调试成本高 | v0.3 再接，先保留 runner adapter |
| 变成普通 AI 续写器 | 只生成文字，不维护世界状态 | 坚持 snapshot、events、contract、lineage |
| 变成 WenShape 式作者工作台 | 功能堆到写作管理，而非读者干预 | v0.2 只借鉴上下文工程，不复制产品定位 |
| 导入质量不稳定 | LLM 抽取角色/规则会漏 | proposal + 人工确认 + 可编辑 YAML |
| 版权风险 | 续写商业小说容易涉及公开传播问题 | 本地个人使用优先，禁止冒充原作者和公开分发受保护内容 |
| 章节越写越漂 | 长篇状态不一致 | facts.jsonl + summaries + chapter commit + contract audit |
| 第四面墙滥用 | 太早出现会变俗套 | 默认关闭或低强度，等多次干预后触发 |

## 11. 产品决策待拍板

1. v0.1.2 是否只做 `resume continue`，把再次干预放到 v0.1.3？建议：是。
2. v0.2 导入是否先支持单文件 txt/md，而不是网页抓取？建议：是。
3. 世界线默认固定三分支，还是用户选择生成数量？建议：Phase 0/1 固定三分支，UI 后再开放。
4. 干预是否引入成本/冷却？建议：v0.5 前只做风险提示，不做硬成本。
5. 第四面墙默认开关？建议：默认关闭或按题材开启。
6. MVP 文案主打“续写断更”还是“拯救意难平”？建议：对外主打“拯救意难平”，功能上兼容续写断更。

## 12. 一句话结论

v0.1.x 已收口；下一步最稳的路线是：

```text
v0.2 import-novel 最小闭环（用户自己的书能 intervene）
  -> v0.4 轻 UI 世界线浏览器
  -> v0.3 MiroFish 深度推演
  -> v0.5 第四面墙
```

WenShape 解决“长篇上下文怎么不崩”，webnovel-writer 解决“故事合约和网文味”，MiroFish 解决“角色群体怎么自己动起来”。Living Novel Engine 自己要牢牢抓住的，是它们都没有真正覆盖的核心：

> 读者干预、世界线分支、角色反抗、活体小说运行时。
