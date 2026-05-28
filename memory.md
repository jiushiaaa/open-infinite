# Living Novel Engine — 项目记忆（跨会话）

> **用途**：供 Cursor / 多会话 Agent 快速恢复上下文，避免遗忘已完成工作与路线。  
> **维护约定**：每完成一次有意义的开发/设计/验收任务后，在本文件末尾 **「变更日志」** 追加一条记录，并视情况更新「当前状态」「已知缺口」「下一步」。  
> **最后更新**：2026-05-28（v0.3.1 收口）

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
| **测试基线** | `183 passed`（2026-05-28） |
| **官方下一版** | **v0.4.2** 检索记忆展示 + UI polish |
| **再下一版** | v0.4.2 UI 展示检索记忆；v0.5 第四面墙 |

---

## 4. 已完成版本（按时间线）

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
| browse 无检索展示 | UI 看不到「本次引用了哪些事实」 | **v0.4.2 下一步** |
| 第四面墙未实现 | awareness 分数、干预记忆、override ledger | v0.5 |
| 多 Agent / MiroFish | scene_runner 仍是轻量轮询 | v0.6 |
| 向量库 / embedding | 刻意不做，BM25 不够再考虑 | 50+ 章后评估 |

---

## 7. 规划路线（官方推荐顺序）

```text
✅ v0.1.x   干预 → 续章 → 再干预
✅ v0.2.x   导入 + resume imported + 精华固化
✅ v0.4     只读世界线浏览器
✅ v0.3.0   Context Retrieval Lite
✅ v0.3.1   检索 artifact + Brief 接入

→ v0.4.2   UI polish + 展示 retrieval_context.json
→ v0.5     第四面墙：干预记忆、角色觉察、反抗命运
→ v0.6     Deep Simulation / MiroFish 多 Agent
→ v0.6+    向量库、多 provider、完整 MasterSetting 工作台
```

### v0.3.1 后续质量优化（非阻塞）

- [ ] ChapterBrief 内容更有用（可选 LLM 摘要 pass，当前 summary 仍为占位）
- [ ] `validate-project` 对 brief 做 warning 级校验

### v0.4.2 待办（下一步）

- [ ] browse 面板：本 run 检索命中、facts、contract 约束
- [ ] 阅读体验 polish（非阻塞核心能力）

### v0.5 待办（方向）

- `fourth_wall_awareness` 分数与 triggers
- 干预记忆持久化、角色对「不可能信息」的反应
- 可选：story_contract 扩展为 override ledger

### 刻意不做（短期）

- vector embedding / 外部向量库 / reranker
- jieba 依赖（当前正则分词）
- browse 内直接写操作（intervene/resume）— 可放 v0.5+ 或单独版本
- 完整 WenShape 式作者工作台

---

## 8. 两条产品主线

### 主线 A：演示 / 连续剧（天荒城）

```text
已完成 UI + 检索注入 → 下一刀侧重 v0.4.2 可解释性 → v0.5 第四面墙
```

### 主线 B：真实用户 / 自有内容（导入书）

```text
已完成导入闭环 + 检索 → 下一刀 v0.3.1 摘要/事实质量 + 分层检索 → 再 v0.6 深度仿真
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
| 场景编排 | `engine/src/living_novel_engine/orchestrator/scene_runner.py` |
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

<!-- 以下由后续会话追加 -->
