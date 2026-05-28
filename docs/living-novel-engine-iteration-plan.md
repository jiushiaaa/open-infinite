# Living Novel Engine 产品迭代计划

> 版本：2026-05-28（v0.2.2 精华固化收口）  
> 范围：对齐 PRD v0.1-v0.5、仓库根目录 Roadmap、`engine/` 全版本实况。  
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
v0.4.2   UI polish + 检索记忆展示  下一步
    ↓
v0.5     第四面墙机制        干预记忆、角色觉察、反抗命运
    ↓
v0.6     Deep Simulation     MiroFish / 多 Agent runtime
    ↓
Phase 5  社区与分享          远期
```

当前最重要的判断：

> v0.3.1 已封板（183 passed）。检索章节号从 import_meta 推导；`retrieval_context.json` 写盘完成。

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
- 检索结果已写入各分支 `retrieval_context.json`，可供 v0.4.2 UI 读取。
- Web UI 尚未展示检索记忆（v0.4.2）。
- 第四面墙数值、干预记忆、override ledger 尚未真正驱动角色行为（v0.5）。
- 多场景长程仿真 / MiroFish OASIS 尚未接入（v0.6）。
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

Living Novel Engine 当前 `scene_runner` 仍是轻量轮询。v0.3 先补长篇上下文检索；等单 prompt 多角色轮询明显表达不了计划、误解、延迟行动时，再在 v0.6 考虑升级为真正多 Agent runtime。

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
- 不接 MiroFish / OASIS 多 Agent runtime。
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
  -> v0.3.1 ChapterBrief / VolumeBrief
  -> v0.6 Deep Simulation / MiroFish
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
| **P4** | **v0.4.2 UI polish** | **检索记忆展示、阅读体验优化** | **下一步** |
| P5 | v0.5 第四面墙 | 干预记忆、角色觉察与抗拒 | 待做 |
| P6 | v0.6 Deep Simulation / MiroFish | 深度多 Agent 推演 | 待做 |
| P7 | v0.6+ Commercial hardening | 向量库、embedding、reranker、多 provider gateway、完整工作台 | 待定 |

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
| v0.4.2 UI polish | v0.3.0 写出检索 artifact 后，让 UI 展示“引用了哪些事实/记忆” |
| v0.5 第四面墙 | 角色决策已能稳定引用历史事实与干预痕迹后 |
| v0.6 Deep Simulation / MiroFish | 单 prompt 多角色轮询明显无法表达计划、误解、延迟行动时 |
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
| 过早集成 MiroFish | 多服务、多依赖、调试成本高 | v0.6 再接，v0.3 先补上下文检索 |
| 变成普通 AI 续写器 | 只生成文字，不维护世界状态 | 坚持 snapshot、events、contract、lineage |
| 变成 WenShape 式作者工作台 | 功能堆到写作管理，而非读者干预 | v0.2 只借鉴上下文工程，不复制产品定位 |
| 导入质量不稳定 | LLM 抽取角色/规则会漏 | proposal + 人工确认 + 可编辑 YAML |
| 版权风险 | 续写商业小说容易涉及公开传播问题 | 本地个人使用优先，禁止冒充原作者和公开分发受保护内容 |
| 章节越写越漂 | 长篇状态不一致 | v0.3 用 facts.jsonl + summaries + story_contract 做检索注入 |
| 第四面墙滥用 | 太早出现会变俗套 | 默认关闭或低强度，等多次干预后触发 |

## 11. 产品决策待拍板

1. v0.1.2 是否只做 `resume continue`，把再次干预放到 v0.1.3？建议：是。
2. v0.2 导入是否先支持单文件 txt/md，而不是网页抓取？建议：是。
3. 世界线默认固定三分支，还是用户选择生成数量？建议：Phase 0/1 固定三分支，UI 后再开放。
4. 干预是否引入成本/冷却？建议：v0.5 前只做风险提示，不做硬成本。
5. 第四面墙默认开关？建议：默认关闭或按题材开启。
6. MVP 文案主打“续写断更”还是“拯救意难平”？建议：对外主打“拯救意难平”，功能上兼容续写断更。

## 12. 一句话结论

v0.1.x、v0.2.x、v0.3.0/v0.3.1、v0.4/v0.4.1 已收口；下一步最稳的路线是：

```text
v0.4.2 检索记忆展示与 UI polish
  -> v0.5 第四面墙
  -> v0.6 Deep Simulation / MiroFish
  -> v0.6+ 向量库 / 多 provider / 完整工作台
```

WenShape 解决“长篇上下文怎么不崩”，webnovel-writer 解决“故事合约和网文味”，MiroFish 解决“角色群体怎么自己动起来”。Living Novel Engine 自己要牢牢抓住的，是它们都没有真正覆盖的核心：

> 读者干预、世界线分支、角色反抗、活体小说运行时。
