# Open-Source Essence Absorption Report

> v0.2.2 — Living Novel Engine 从 WenShape 和 webnovel-writer 中吸收可复用资产的归档记录。

---

## 1. 来源项目概览

| 项目 | 许可证 | 核心定位 |
|------|--------|----------|
| **WenShape** | PolyForm Noncommercial 1.0.0 | 长上下文工程：多层摘要、事实检索、章节距离衰减 |
| **webnovel-writer** | GPL v3 | 结构化网文写作：题材模板、故事合约、分层大纲、事件输出 |

---

## 2. 已吸收能力

| 能力 | 来源 | LNE 对应文件 | 吸收方式 |
|------|------|-------------|----------|
| **题材模板 (37 个)** | webnovel-writer/templates/genres/ | `engine/src/living_novel_engine/resources/genre_templates/*.md` | 文件复制 + slug 映射加载器 |
| **题材加载器** | 原创（受 webnovel-writer 启发） | `engine/src/living_novel_engine/resources/genre_loader.py` | 新建 |
| **story_contract.yaml** | webnovel-writer 的 story contract 概念 | `projects/<slug>/story_contract.yaml` | 概念吸收，结构重新设计 |
| **facts.jsonl** | WenShape 的事实断言层 | `projects/<slug>/canon/facts.jsonl` | 概念吸收，轻量实现 |
| **章节摘要** | WenShape 的分层摘要 | `projects/<slug>/summaries/chapter_xxx.yaml` | 概念吸收，轻量占位 |
| **forbidden_additions 约束** | webnovel-writer 的正史锁概念 | `story_contract.yaml` 内 `forbidden_additions` | 结构化落盘 |
| **character_boundaries** | webnovel-writer 的角色红线 | `story_contract.yaml` 内 `character_boundaries` | 从 characters.yaml 提取汇总 |

---

## 3. 刻意不做的能力

| 能力 | 来源 | 原因 |
|------|------|------|
| BM25 事实检索 | WenShape | v0.3.0 已吸收为 Context Retrieval Lite |
| 章节距离衰减 | WenShape | v0.3.0 已随 BM25 lite 一起吸收 |
| Vector projection | WenShape | 等 BM25 在 50+ 章项目上不够用再加 |
| MasterSetting / VolumeBrief / ChapterBrief 工作台 | WenShape | v0.3.1 做 ChapterBrief / VolumeBrief 轻量版；完整工作台留到 v0.6+ |
| 多 provider gateway | webnovel-writer | 当前 base_url 兼容已够用；商业化或私有化部署时再做 |
| 作者 Web UI | WenShape | LNE 定位是读者干预运行时，非作者工具 |
| 直接复制大段源码 | 两者 | 避免许可证污染和架构耦合 |

---

## 4. 复制的资产清单

### 4.1 genre_templates (37 files)

来源：`webnovel-writer/webnovel-writer/templates/genres/*.md`

目标：`engine/src/living_novel_engine/resources/genre_templates/`

文件列表：修仙、克苏鲁、历史古代、历史脑洞、古言、多子多福、女频悬疑、宫斗宅斗、年代、幻想言情、悬疑灵异、悬疑脑洞、抗战谍战、无限流、替身文、末世、民国言情、游戏体育、狗血言情、现实题材、现言脑洞、电竞、直播文、知乎短篇、种田、科幻、系统流、职场婚恋、西幻、规则怪谈、豪门总裁、都市异能、都市日常、都市脑洞、青春甜宠、高武、黑暗题材。

许可证说明：webnovel-writer 采用 GPL v3，genre templates 作为文本资产复制后，LNE 需遵守 GPL v3 对衍生作品的要求。

---

## 5. 后续版本继续使用计划

| 版本 | 使用方式 |
|------|---------|
| **v0.3.0** | facts.jsonl + summaries + story_contract 结合 BM25 lite 注入 narrator / character_agent |
| **v0.3.1** | 扩展 summaries 为 ChapterBrief 轻量版；加入 VolumeBrief 层 |
| **v0.4.2** | UI 展示 v0.3 检索命中的事实、记忆、合约约束 |
| **v0.5** | story_contract 扩展为 override ledger，支持干预记忆持久化 |
| **v0.6** | 评估 MiroFish / OASIS 或自研多 Agent runner |
| **v0.6+** | 按规模化需求补向量库、embedding、reranker、多 provider gateway、完整 MasterSetting 工作台 |

---

## 6. 删除决定

在确认以下条件后删除外部项目源码目录：

1. **WenShape/**: PolyForm Noncommercial — 未复制任何源码，仅吸收设计概念。可安全删除。
2. **webnovel-writer/**: GPL v3 — 已复制 genre templates（文本资产）。在 LNE 中保留 GPL v3 归属声明。可安全删除源码目录。

归属声明位于：`engine/src/living_novel_engine/resources/genre_templates/ATTRIBUTION.md`

---

## 7. 归属声明

```
Genre templates in this directory were originally created by the webnovel-writer project
(https://github.com/nicekate/webnovel-writer), licensed under GPL v3.

Design concepts for facts.jsonl and chapter summaries were inspired by WenShape
(PolyForm Noncommercial 1.0.0). No source code was copied.
```
