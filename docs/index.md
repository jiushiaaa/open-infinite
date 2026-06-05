# 未终章 Docs Index

> 用途：说明 `docs/` 的文档分层、读取顺序和维护规则。进入项目时仍以根目录 `AGENTS.md` 与 `memory.md` 作为第一入口；本文件负责避免把历史归档、支撑层清单或后置发行路径误读成当前主线。

> 2026-06-06 整理结论：本次扫描确认 `docs/` 物理目录无需大搬家；为了不破坏历史链接，继续用本索引和各目录 README 做逻辑归类。根层只保留当前主线、路线、阶段、接力和后置路径；`completed/` 是已收口归档；`article/`、`brand/`、`image/` 是资料资产；`后续增强清单.md` 已改为支撑层索引，`distribution-phase-plan.md` 是发行后置路径，二者只在用户明确点名时进入。

## 0. 文档事实层级

| 层级 | 文档 | 当前职责 |
| --- | --- | --- |
| Agent 入口规则 | `../AGENTS.md` | 开工流程、硬约束、主线边界、验证和提交规则 |
| 当前事实收口 | `../memory.md` | 当前完成度、验证基线、闭环等级、真实未做项 |
| 文档地图 | `index.md` | 当前文件；告诉下一位读者每类文档该不该当待办来源 |
| 当前主线 PRD | `unfinale-world-sandbox-remodel-prd.md` | 世界沙盘 S1-S9 及后续深化路线 |
| 开工自检 | `unfinale-ai-development-alignment-checklist.md` | 判断下一刀是否服务世界运行、角色自主、记忆、干预、反抗、代偿和章节生成 |
| 路线图 | `living-novel-engine-iteration-plan.md` | 当前阶段、暂停点、下一刀候选 |
| 产品愿景 | `unfinale-product-vision-correction-draft.md`、`living-novel-engine-prd.md` | 愿景原则、用户场景、产品结构和当前产品验收口径；执行细节以当前主线 PRD 为准 |
| 历史归档 | `completed/`、`project-changelog.md` | 已收口专项和完整历史日志，供追溯，不直接产生当前待办 |
| 支撑层/后置路径 | `后续增强清单.md`、`distribution-phase-plan.md` | 支撑层索引与发行路径；除非用户明确点名，不抢当前世界沙盘主线 |
| 研究与资产 | `article/`、`brand/`、`image/` | 论文、品牌、原型图和视觉参考 |
| 运行说明 | `../engine/README.md`、`../engine/ui/README.md` | 后端/API/artifact/验证与当前前端结构、路由、UI 边界 |

## 1. 推荐读取顺序

### 新会话或接力任务

1. `../AGENTS.md`
2. `../memory.md`
3. `index.md`
4. `unfinale-world-sandbox-remodel-prd.md`
5. `unfinale-ai-development-alignment-checklist.md`
6. `living-novel-engine-iteration-plan.md`
7. `../engine/README.md`
8. 如需愿景判断：`unfinale-product-vision-correction-draft.md`、`living-novel-engine-prd.md`
9. 如需 UI 风格：`completed/v0.7-product-web-app-ui-spec.md`
10. 如需接力摘要：`codex-handoff.md`

### 判断下一步

1. `../memory.md`
2. `unfinale-world-sandbox-remodel-prd.md`
3. `unfinale-ai-development-alignment-checklist.md`
4. `living-novel-engine-iteration-plan.md`
5. 必要时读 `productization-phase-map.md`

不要从 `project-changelog.md` 或 `completed/` 旧专项里直接捞下一刀。它们记录当时的上下文，不保证仍是当前路线。

### 做前端 UI 或产品体验

1. `unfinale-world-sandbox-remodel-prd.md`
2. `unfinale-product-vision-correction-draft.md`
3. `completed/v0.7-product-web-app-ui-spec.md`
4. `image/README.md`
5. `../engine/README.md`

当前前端组织原则：优先世界内部卷宗、世界线页、检查点和作者采纳台；不要继续往 `WorkspacePage.tsx` 堆工程面板。

### 做论文能力或参考项目吸收

1. `article/reports/` 下对应论文研读报告
2. `completed/open-source-essence-absorption.md`
3. `living-novel-engine-iteration-plan.md`
4. `../memory.md`

## 2. docs 根层文档

| 路径 | 状态标签 | 作用 |
| --- | --- | --- |
| `index.md` | 当前导航 | 文档地图和读取顺序 |
| `codex-handoff.md` | 接力摘要 | 新开 Codex 窗口时的最小上下文；仍需以 `memory.md` 复核 |
| `codex-migration-guide.md` | 迁移说明 | `.cursor/rules`、`.cursor/skills` 与 Codex skills/plugins 的迁移关系 |
| `project-changelog.md` | 历史日志 | 完整变更日志；追加维护，不承担当前待办来源 |
| `unfinale-world-sandbox-remodel-prd.md` | 当前主线 | 世界沙盘改造 PRD，说明现有代码如何接入《天命书》、沙盘轮次、主观记忆链、世界自演、多视角正文和作者采纳台 |
| `unfinale-product-vision-correction-draft.md` | 愿景纠偏 | 原始愿望、设计原则、双入口、领域记忆模型、UI 方向和不扩张边界；不是讨论期长接力 |
| `unfinale-ai-development-alignment-checklist.md` | 开工自检 | 防止下一刀滑回 provider、GraphRAG、检索评测、发行或工程面板 |
| `living-novel-engine-prd.md` | 当前产品 PRD | 产品定位、用户价值、主体验、已闭环/未完成边界和验收口径；历史长表已回指 changelog 与 completed |
| `living-novel-engine-iteration-plan.md` | 当前路线图 | 当前阶段状态、真实未做项和后续候选路线 |
| `productization-phase-map.md` | 阶段归类 | 解释技术 MVP、产品化 MVP、世界沙盘主线和商业化后置边界 |
| `后续增强清单.md` | 支撑层索引 | 记录已收口支撑能力、触发式增强规则和追溯入口；不是当前默认路线 |
| `distribution-phase-plan.md` | 后置发行路径 | 本地 clone、Release 安装包、服务器在线体验；本地世界沙盘体验稳定前不抢优先级 |
| `completed/` | 收口归档 | 已收口专项 PRD、release note、协议、UI spec 和版本审计；旧“下一步”必须回到 `../memory.md` 复核 |
| `article/` | 研究资料 | 论文 PDF 与研读报告 |
| `brand/` | 品牌资产 | 未终章 / Unfinale 标识与概念稿 |
| `image/` | UI 原型参考 | 世界书架、天命书、世界自演、干预编译器、多视角活体小说等原型图 |

## 3. 当前已闭环与仍需深入

| 分类 | 文档入口 | 当前口径 |
| --- | --- | --- |
| 已闭环历史底座 | `completed/README.md`、`project-changelog.md` | v0.7 到 v1.0-local、后续增强四十五刀、真实 retrieval provider、Vector Retrieval Pipeline 均有历史记录和收口说明 |
| 已闭环世界沙盘第一版 | `../memory.md`、`unfinale-world-sandbox-remodel-prd.md` | S1-S9 已具备 additive service/API/UI/artifact/tests；能跑通世界沙盘、觉醒传播、自演、多视角正文、作者采纳、卷宗阅读和局部重写采纳 |
| 已产品化第一刀 | `../memory.md`、`../engine/README.md` | 卷宗阅读页、世界自演结果页可读入口、Reviewer 局部重写到作者采纳台、编辑后定稿和确认入卷反哺下一轮入口已完成第一版 |
| 仍需深入 | `../memory.md`、`living-novel-engine-iteration-plan.md` | 多轮策略规划、长期关系/势力博弈、真实长正文文风、正文内锚点/误会图谱、整章风格润色、更强真实语义 Reviewer 和真实模型编辑器 |
| 明确后置 | `后续增强清单.md`、`distribution-phase-plan.md` | GraphRAG/Zep、默认 hybrid vector、真实商业化、对象存储、认证、计费、发行安装包和云端队列 |

## 4. completed/ 收口归档

`completed/` 存放已收口专项文档。它们是历史证据和细节说明，不承担当前最高优先级。若旧文档写了“下一步”，先回到 `../memory.md` 与当前主线 PRD 复核。

| 路径 | 阶段 | 作用 |
| --- | --- | --- |
| `completed/README.md` | 目录索引 | `completed/` 分组导航、当前归档口径和后续状态边界 |
| `completed/v0.1-to-v0.8-version-audit.md` | v0.1-v0.8 | v0.8 时点历史审计快照；已标注当时未做项的后续状态 |
| `completed/codex-handoff-legacy-2026-06-01.md` | 接力归档 | `codex-handoff.md` 瘦身前的长接力稿 |
| `completed/living-novel-engine-iteration-plan-legacy-2026-06-01.md` | 路线图归档 | 主迭代计划瘦身前的逐刀实施清单 |
| `completed/v0.7-product-web-app-ui-spec.md` | v0.7 UI | 当前古风纸面、克制系统感的 UI 风格依据 |
| `completed/v0.9-to-v1.0-product-ui-addenda.md` | v0.9-v1.0 UI | 长篇闭环、provider/cost、MasterSetting、商业化边界和本地模型配置 UI 增量 |
| `completed/open-source-essence-absorption.md` | 参考吸收 | WenShape / webnovel-writer 的吸收决策和许可证边界 |
| `completed/*.md` | 已收口专项 | 各版本 release note、工程协议、商业化边界、后续增强、Graph/provider/retrieval 支撑层文档 |

完整文件级清单见 `completed/README.md`。本索引不再复制 `completed/` 的全部长表，避免入口文档继续膨胀。

## 5. article/ 论文资料

`article/` 存放论文 PDF 原文；`article/reports/` 存放已转化为 LNE 路线语言的研读报告。开发时优先读报告，只有需要核对原文时再打开 PDF。

| 路径 | 可借鉴能力 |
| --- | --- |
| `article/reports/2404.17027v3-player-driven-emergence-report.md` | 用户驱动涌现、emergence nodes、玩家动机 |
| `article/reports/2405.13042v2-storyverse-report.md` | Abstract Act、Concrete Act、ActDirector、角色模拟 |
| `article/reports/2407.13248v2-human-level-narratives-report.md` | Story Arc、Turning Points、叙事质量评估 |
| `article/reports/2505.03547v1-story2game-report.md` | Preconditions、Effects、Dynamic Action Generation |

## 6. 维护约定

- 新增仍在跟进的主线文档可留在 `docs/` 根部；已收口版本专项文档归档到 `completed/`，并在 `completed/README.md` 登记。
- 入口文档不要再复制完整历史状态表；用链接指向 `memory.md`、`completed/README.md` 和 `project-changelog.md`。
- 新增论文原文放 `article/`，论文解读放 `article/reports/`，不要只放 PDF 不写报告。
- 完成独立切片后同步顺序建议：`memory.md` 当前状态 -> `project-changelog.md` 历史记录 -> `living-novel-engine-iteration-plan.md` -> 相关 PRD/UI spec/README -> `codex-handoff.md` -> 本文件。

## 7. 不再合并的原因

本轮没有把 `completed/` 的 80+ 篇历史专项合并成单文件，原因是这些文档承担证据链和版本追溯职责，移动或合并会破坏旧链接和 changelog 语境。后续若要精简，只合并“入口摘要”，不要重写历史事实；当前读者只需从本索引进入，不需要逐篇打开历史归档。
