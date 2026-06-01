# 未终章 产品迭代计划

> 用途：作为当前路线图入口，说明阶段状态、下一步原则和后续触发条件。完整历史实施清单已归档到 `completed/living-novel-engine-iteration-plan-legacy-2026-06-01.md`；最新事实以 `../memory.md` 为准。
> 品牌口径：产品名为“未终章”，英文名为 “Unfinale”；代码包名、CLI、artifact 与环境变量前缀仍沿用 LNE / `living_novel_engine`。
> 版本：2026-06-01，本地模型配置 UX 与本地一键运行脚本已收口；当前暂停继续新刀，等待用户本地试用反馈。

## 1. 产品北极星

未终章（Unfinale）不是普通 AI 续写器，而是一个“故事世界运行时”：

```text
文本输入 -> 世界锚定 -> 角色自主行动 -> 读者干预 -> 世界线分叉 -> 章节渲染 -> 可继续运行
```

它要验证的不是“AI 能不能写下一章”，而是：

- 小说世界能否在没有作者继续写作的情况下继续运行。
- 读者能否从阅读者变成命运干预者。
- 角色能否因为人设、记忆、利益和世界规则而拒绝用户命令。
- 同一段原文能否长出不同读者专属的平行世界线。

## 2. 当前状态总览

| 阶段 | 当前状态 | 说明 |
| --- | --- | --- |
| v0.1-v0.6.5 | 已收口 | CLI 原型、导入、检索、浏览器、第四面墙、runner adapter、多 Agent 协议/LLM runner/可靠性。 |
| v0.7-v0.7.5 | 已收口 | 产品级 Web App、Agent Interaction、视觉资产、Baseline/Canon Replay、Worldline Judge。 |
| v0.8-v0.8.10 | 已收口 | 长篇导入、分层记忆、正史账本、检索、审计、holdout 隔离、项目工作台、回放审计 UI、状态 overlay。 |
| v0.9.0-alpha | 已整体收口 | 长篇共创闭环：上传/创建、项目资产、分支运行、审计、选择世界线、续写、导出、closeout record。 |
| v0.9.1-v0.9.4 | 已整体收口 | Provider/Cost、MasterSetting Workspace、Graph Memory Evaluation、Advanced Runner Evaluation。 |
| v1.0-beta | 已收口 | 本地优先商业化边界：账号、权限、云端持久化、配额、审计、版权、部署观测、认证、对象存储、计费 adapter。 |
| v1.0-local | 已收口 | Model Configuration UX 与 Local Run Scripts。 |

当前验证基线：后端 `713 passed`；前端 `cd engine/ui && pnpm run build` 通过。

## 3. 当前暂停点

按用户要求，真实用户模型配置 UI 与本地一键运行脚本完成后暂停。下一步不自动开新版本，先等待用户本地试用反馈。

本地体验稳定后，再由用户选择进入：

1. GitHub Release 安装包 / 内置 runtime。
2. 腾讯云或服务器单机在线体验。
3. 真实认证、对象存储、配额执行、计费 adapter 等平台化能力。

## 4. 已完成能力分层

### 引擎能力

- 样例运行、导入小说、续写、干预、世界线分叉。
- 检索上下文、章节摘要、事实账本、story contract。
- 第四面墙、runner adapter、多 Agent trace 与可视化。

### 产品能力

- React/Vite Web App：导入、创世、锚定、阅读、自由干预、Causal Diff、运行设置、异步 job。
- 长篇项目工作台：导入检查、章节预览、分层记忆、正史账本、实体别名、检索命中、审计报告、设定工作台。
- 创作闭环：推荐世界线、世界线评审、设为起点、续写 job、选择后审计、章节/合集导出、closeout。

### 解释与安全边界

- 右侧机制档案：运行记忆、动作计划、动作注册表、叙事诊断、涌现节点、状态执行评估、overlay。
- 本地审计日志：版权声明、保留策略、设定编辑、世界线选择、状态执行 apply/rollback 等关键写操作。
- Provider/Cost 与模型配置：脱敏 provider 状态、usage、route matrix、模型配置状态、本地 mock/真实模型切换。

## 5. 当前真实未做项

| 缺口 | 当前处理原则 |
| --- | --- |
| ChapterBrief 质量仍偏规则化 | 长篇质量明显受限时，再接 LLM 摘要或人工校正工作台。 |
| `contract_audit` 主链路偏静态 | 出现合约越界误判/漏判时，再把磁盘 contract 接入运行时强约束。 |
| overlay 未自动喂回 runner | 等用户确认需要连续状态演化后，再做 opt-in 消费链路。 |
| 运行后审计未写入正史账本 | 需要“审计结论影响正史”时再做。 |
| 云端多用户、对象存储、认证、计费 | 本地试用稳定并明确发行路径后再拆。 |
| 向量库 / embedding / GraphRAG | 只有 BM25/ledger/alias probe 证明不足时再评估。 |
| LangGraph / OASIS / CAMEL | 只有复杂 run probe 证明自研 runner 不足时再评估。 |

## 6. 后续候选路线

### D 线：发行与本地体验

| 候选 | 触发条件 | 边界 |
| --- | --- | --- |
| GitHub Release 安装包 | 本地脚本在用户机器跑通，依赖安装痛点明确 | 不接云端多租户，不内置明文 Key。 |
| 内置 runtime / 依赖 bootstrap | 普通用户无法稳定安装 Python/Node/pnpm | 先做安装体验，不扩展业务功能。 |
| 服务器单机在线体验 | 用户确认需要公网试玩 | 先做单机边界和密钥注入，不承载多人隐私数据。 |

### P 线：产品质量

| 候选 | 触发条件 | 边界 |
| --- | --- | --- |
| ChapterBrief/设定质量增强 | 长篇续写明显缺少远期信息 | 先增强摘要/记忆，不直接接重型图数据库。 |
| overlay 连续消费 | 用户希望状态覆盖影响下一章 | 继续 opt-in，不改默认 `run_scene`。 |
| 正史账本写后审计 | 需要把审计结论纳入下一轮记忆 | 明确人工确认和回滚策略。 |

### C 线：平台化边界

| 候选 | 触发条件 | 边界 |
| --- | --- | --- |
| 认证执行 | 出现真实多用户或团队协作需求 | 先接 ACL guard，不改本地单用户默认路径。 |
| 对象存储 adapter | 项目资源需要跨机器持久化 | 先做 adapter 边界和迁移脚本，不直接上传现有数据。 |
| 配额 / 计费 adapter | 真实外部用户产生费用风险 | 先做 idempotency、账单事件和硬配额前置清单。 |

## 7. 维护规则

- 本文只保留当前路线，不再承载逐刀历史实施过程。
- 完成新版本后：更新 `../memory.md` 当前状态，必要时追加 `project-changelog.md`，再同步本文当前状态和候选路线。
- 已收口专项文档放 `completed/`；论文/项目研读报告放 `article/reports/`；完整旧路线图见 `completed/living-novel-engine-iteration-plan-legacy-2026-06-01.md`。
- 所有后续实现继续保持 additive，不破坏既有 artifact/API 契约。
