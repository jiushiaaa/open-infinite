# 未终章 Docs Index

> 用途：说明 `docs/` 的文档分层、读取顺序和维护规则。进入项目时仍以根目录 `AGENTS.md` 与 `memory.md` 作为第一入口；本文件负责避免把历史归档、支撑层清单或后置发行路径误读成当前主线。

> 2026-06-08 整理结论：`docs/` 根目录只保留当前活文档；已完成专项进 `completed/`，完整历史进 `history/`，后置发行路径进 `postponed/`。当前未完成但值得继续优化的主线事项集中在 `unfinale-current-optimization-backlog.md`。

## 0. 文档事实层级

| 层级 | 文档 | 当前职责 |
| --- | --- | --- |
| Agent 入口规则 | `../AGENTS.md` | 开工流程、硬约束、主线边界、验证和提交规则 |
| 当前事实收口 | `../memory.md` | 当前完成度、验证基线、闭环等级、真实未做项 |
| 项目总览 | `../README.md` | 面向人类读者的产品定位、快速开始和文档入口 |
| 文档地图 | `index.md` | 当前文件；告诉下一位读者每类文档该不该当待办来源 |
| 当前主线 PRD | `unfinale-world-sandbox-remodel-prd.md` | 世界沙盘目标、已完成第一版范围和主线边界 |
| 当前优化清单 | `unfinale-current-optimization-backlog.md` | 已有第一版但还要继续深化的主线优化项 |
| 开工自检 | `unfinale-ai-development-alignment-checklist.md` | 判断下一刀是否服务世界运行、角色自主、记忆、干预、反抗、代偿和章节生成 |
| 路线图 | `living-novel-engine-iteration-plan.md` | 当前阶段、暂停点、下一刀选择规则 |
| 产品愿景 | `unfinale-product-vision-correction-draft.md`、`living-novel-engine-prd.md` | 愿景原则、用户场景、产品结构和验收口径 |
| 历史归档 | `history/project-changelog.md`、`completed/` | 完整历史日志和已收口专项；供追溯，不直接产生当前待办 |
| 支撑层/后置路径 | `completed/support-layer-enhancement-index.md`、`postponed/distribution-phase-plan.md` | 支撑层索引与发行路径；除非用户明确点名，不抢当前世界沙盘主线 |
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
8. 如需判断下一刀：`unfinale-current-optimization-backlog.md`
9. 如需愿景判断：`unfinale-product-vision-correction-draft.md`、`living-novel-engine-prd.md`
10. 如需 UI 风格：`completed/v0.7-product-web-app-ui-spec.md`
11. 如需接力摘要：`codex-handoff.md`

### 判断下一步

1. `../memory.md`
2. `unfinale-world-sandbox-remodel-prd.md`
3. `unfinale-ai-development-alignment-checklist.md`
4. `living-novel-engine-iteration-plan.md`
5. `unfinale-current-optimization-backlog.md`

不要从 `history/project-changelog.md`、`completed/`、`completed/support-layer-enhancement-index.md` 或 `postponed/distribution-phase-plan.md` 直接捞下一刀。它们记录历史、支撑层或后置路径，不保证仍是当前路线。

### 做前端 UI 或产品体验

1. `unfinale-world-sandbox-remodel-prd.md`
2. `unfinale-product-vision-correction-draft.md`
3. `completed/v0.7-product-web-app-ui-spec.md`
4. `image/README.md`
5. `../engine/ui/README.md`

当前前端组织原则：优先世界内部卷宗、世界线页、检查点和作者采纳台；不要继续往 `WorkspacePage.tsx` 堆工程面板。

### 做论文能力或参考项目吸收

1. `article/reports/` 下对应论文研读报告
2. `completed/open-source-essence-absorption.md`
3. `unfinale-current-optimization-backlog.md`
4. `../memory.md`

## 2. docs 根层活文档

| 路径 | 状态标签 | 作用 |
| --- | --- | --- |
| `index.md` | 当前导航 | 文档地图和读取顺序 |
| `codex-handoff.md` | 接力摘要 | 新开 Codex 窗口时的最小上下文；仍需以 `memory.md` 复核 |
| `unfinale-world-sandbox-remodel-prd.md` | 当前主线 | 世界沙盘目标、第一版闭环和后续深化边界 |
| `unfinale-current-optimization-backlog.md` | 当前优化清单 | 从各 PRD 抽出的真实未完成优化项 |
| `unfinale-product-vision-correction-draft.md` | 愿景纠偏 | 原始愿望、设计原则、双入口、领域记忆模型、UI 方向和不扩张边界 |
| `unfinale-ai-development-alignment-checklist.md` | 开工自检 | 防止下一刀滑回 provider、GraphRAG、检索评测、发行或工程面板 |
| `living-novel-engine-prd.md` | 当前产品 PRD | 产品定位、用户价值、主体验、已闭环/未完成边界和验收口径 |
| `living-novel-engine-iteration-plan.md` | 当前路线图 | 当前阶段状态、下一刀选择规则和验证口径 |

## 3. 子目录职责

| 路径 | 状态标签 | 作用 |
| --- | --- | --- |
| `completed/` | 收口归档 | 已收口专项 PRD、release note、协议、UI spec、迁移说明和阶段归类 |
| `history/` | 历史日志 | 完整追加式 changelog |
| `postponed/` | 后置路径 | 发行、部署、商业化等触发式计划 |
| `article/` | 研究资料 | 论文 PDF 与研读报告 |
| `brand/` | 品牌资产 | 未终章 / Unfinale 标识与概念稿 |
| `image/` | UI 原型参考 | 世界书架、天命书、世界自演、干预编译器、多视角活体小说等原型图 |

## 4. 当前已闭环与仍需深入

| 分类 | 文档入口 | 当前口径 |
| --- | --- | --- |
| 已闭环历史底座 | `completed/README.md`、`history/project-changelog.md` | v0.7 到 v1.0-local、后续增强、真实 retrieval provider、Vector Retrieval Pipeline 均有历史记录和收口说明 |
| 已闭环世界沙盘第一版 | `../memory.md`、`unfinale-world-sandbox-remodel-prd.md` | S1-S9 已具备 additive service/API/UI/artifact/tests；能跑通世界沙盘、觉醒传播、自演、多视角正文、作者采纳、卷宗阅读和局部重写采纳 |
| 已产品化第一版 | `../memory.md`、`../engine/README.md` | 世界入口、卷宗阅读、世界自演结果页、Reviewer 局部重写、编辑后定稿、确认入卷、跑后承接和下一轮入口已有第一版 |
| 仍需深入 | `unfinale-current-optimization-backlog.md` | 多轮策略规划、长期关系/势力博弈、真实长正文文风、跨章节误会/伏笔回收、更强真实语义 Reviewer 和整章风格润色 |
| 明确后置 | `completed/support-layer-enhancement-index.md`、`postponed/distribution-phase-plan.md` | GraphRAG/Zep、默认 hybrid vector、真实商业化、对象存储、认证、计费、发行安装包和云端队列 |

## 5. 维护约定

- `memory.md` 只保留当前事实、边界和真实缺口；不要再追加逐刀流水。
- 当前未完成优化集中写入 `unfinale-current-optimization-backlog.md`；入口文档只保留摘要和链接。
- 独立切片历史写到 `history/project-changelog.md` 末尾；不要改写旧日志。
- 新增仍在跟进的主线文档可留在 `docs/` 根部；已收口版本专项文档归档到 `completed/`，并在 `completed/README.md` 登记。
- 新增论文原文放 `article/`，论文解读放 `article/reports/`，不要只放 PDF 不写报告。
- 完成独立切片后同步顺序建议：`memory.md` 当前状态 -> `history/project-changelog.md` 历史记录 -> `living-novel-engine-iteration-plan.md` -> 相关 PRD/UI spec/README -> `codex-handoff.md` -> 本文件。
