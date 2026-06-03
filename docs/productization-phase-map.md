# 未终章 产品化阶段归类

> 用途：统一解释 “MVP / A-slice / 产品化 / 商业化” 的口径，避免把已完成的技术底座误读为完整商业产品。当前事实以 `../memory.md` 为准，历史过程见 `project-changelog.md`。

## 1. 当前结论

未终章 已完成三层闭环：

- **短中篇产品化 MVP**：v0.7-v0.7.5，普通用户可通过 React/Vite Web App 完成导入、创世、锚定、干预、评审与基础分支体验。
- **长篇产品化 alpha**：v0.8-v0.9.0-alpha，百万字级导入底座、项目工作台、回放审计、状态 overlay、世界线选择、续写、章节/合集导出与 closeout record 已跑通。
- **本地优先加固与后续增强四十刀**：v0.9.1-v1.0-local + 后续增强，provider/cost、MasterSetting、图记忆/高级 runner 触发评估、商业化边界、本地模型配置、一键运行脚本、Runtime Preflight、Projection Health、Reader Panel、Prompt Budget Pack、LLM Profile Assignment、Cards Workspace、OpenAPI / Typed Client、Bundled Release Readiness、Embedding / Vector Retrieval Readiness Probe、Embedding Evaluation Samples、Retrieval Failure Sample Authoring、Memory CLI、Retrieval Sample Export Pack、Embedding Mock Evaluation Report、Retrieval Sample Replay Report、Retrieval Sample Migration Pack、Cross Project Retrieval Samples Index、Retrieval Samples Trend Snapshot、GraphRAG / Zep Trigger Evidence、Graph Memory Spike Design Pack、Graph Memory Shadow Compare Pack、Graph Memory Shadow Case Matrix、Graph Memory Provider Boundary Matrix、Graph Memory Offline Shadow Replay Plan、Graph Memory Offline Shadow Replay Report、Graph Memory Provider Spike Fixture Pack、Graph Memory Provider Spike Readiness Gate、Graph Memory Provider Spike Runbook、Graph Memory Provider Spike Dry-run Result Template、Graph Memory Provider Spike Mock Result Report、Graph Memory Provider Spike Review Gate、Graph Memory Provider Spike Manual Approval Pack、Graph Memory Provider Spike Manual Approval Evidence Checklist、Graph Memory Provider Spike Opt-in Evidence Snapshot、Graph Memory Provider Spike Opt-in No-go Matrix、Graph Memory Provider Spike Opt-in Operator Checklist、Graph Memory Provider Spike Opt-in Review Packet、Graph Memory Provider Spike Opt-in Decision Ledger Preview、Graph Memory Provider Spike Opt-in Final Readiness Summary 与 Graph Memory Provider Spike Opt-in Human Signoff Schema Draft 已收口。

当前 Graph Memory Provider Spike Opt-in Human Signoff Schema Draft MVP 已收口；下一刀建议 Graph Memory Provider Spike Opt-in Config Draft MVP，继续保持只读配置草案，不保存配置、不读取明文 Key、不接真实 provider。真实云端多租户、对象存储、认证、计费、安装包和服务器在线体验都不默认进入当前主线。

## 2. 阶段归类表

| 阶段 | 阶段性质 | 产品化程度 | 当前判断 |
| --- | --- | --- | --- |
| v0.1-v0.3 | CLI、导入、检索、状态与续章底座 | 技术 MVP | 证明 “文本 -> 状态 -> 干预 -> 分叉 -> 续章” 能跑通；主要面向开发者和验证。 |
| v0.4-v0.4.2 | 只读世界线浏览器与检索展示 | 研发/演示产品化 | 可浏览世界线、章节、状态和检索记忆，但仍偏开发者 viewer。 |
| v0.5-v0.6.5 | 第四面墙、SceneRunner、多 Agent 协议/runner | 引擎机制 MVP | 角色觉察、多 Agent trace、runner 适配层成立；可审计、可演示。 |
| v0.7-v0.7.5 | Product Web App + 交互增强 | 短中篇产品化 MVP | 第一轮真正面向普通用户的产品化闭环。 |
| v0.8.0-v0.8.10 | 长篇导入、记忆、审计、回放、状态执行 | 长篇产品化底座 | 长篇底座从 artifact/API 走向上传、检查、管理、审计、回放、状态覆盖和继续创作工作流。 |
| v0.9.0-alpha | Long Novel Creation Loop | 长篇产品化闭环成立 | 上传/创建 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出 -> closeout record 已整体收口。 |
| v0.9.1-v0.9.4 | Provider/Cost、MasterSetting、Graph/Runner 评估 | 真实使用压力增强 | 成本、设定工作台、召回不足和复杂 runner 缺口都已做触发式评估；重依赖暂不接。 |
| v1.0-beta | 商业化边界与本地审计 | 本地优先商业化加固 | 已定义账号、权限、云端持久化、配额、审计、版权、部署观测、认证、对象存储、计费 adapter 等边界；不伪装成真实 SaaS。 |
| v1.0-local | 模型配置与本地启动 | 本地试用准备 | 设置页模型配置 UX 与本地一键运行脚本已收口，等待真实本地试用反馈。 |
| 后续增强四十刀 | Runtime Preflight、Projection Health、Reader Panel、Prompt Budget Pack、LLM Profile Assignment、Cards Workspace、OpenAPI / Typed Client、Bundled Release Readiness、Embedding / Vector Retrieval Readiness Probe、Embedding Evaluation Samples、Retrieval Failure Sample Authoring、Memory CLI、Retrieval Sample Export Pack、Embedding Mock Evaluation Report、Retrieval Sample Replay Report、Retrieval Sample Migration Pack、Cross Project Retrieval Samples Index、Retrieval Samples Trend Snapshot、GraphRAG / Zep Trigger Evidence、Graph Memory Spike Design Pack、Graph Memory Shadow Compare Pack、Graph Memory Shadow Case Matrix、Graph Memory Provider Boundary Matrix、Graph Memory Offline Shadow Replay Plan、Graph Memory Offline Shadow Replay Report、Graph Memory Provider Spike Fixture Pack、Graph Memory Provider Spike Readiness Gate、Graph Memory Provider Spike Runbook、Graph Memory Provider Spike Dry-run Result Template、Graph Memory Provider Spike Mock Result Report、Graph Memory Provider Spike Review Gate、Graph Memory Provider Spike Manual Approval Pack、Graph Memory Provider Spike Manual Approval Evidence Checklist、Graph Memory Provider Spike Opt-in Evidence Snapshot、Graph Memory Provider Spike Opt-in No-go Matrix、Graph Memory Provider Spike Opt-in Operator Checklist、Graph Memory Provider Spike Opt-in Review Packet、Graph Memory Provider Spike Opt-in Decision Ledger Preview、Graph Memory Provider Spike Opt-in Final Readiness Summary、Graph Memory Provider Spike Opt-in Human Signoff Schema Draft | 产品诊断、上下文、模型画像、设定资产、本地契约、发行准备、检索增强触发评估、样本对照、本地采集、批处理复跑、样本导出、mock 报告、replay case report、migration pack、跨项目索引、趋势快照、重型记忆触发证据、设计包、shadow 对照、per-case 矩阵、provider opt-in 边界、离线 replay 计划、离线 replay 报告、provider dry-run 前置包、readiness gate、人工 dry-run SOP、结果记录模板、mock 填充报告、人工复核 gate、人工审批包、审批证据核对表、opt-in 证据快照、no-go 分类矩阵、operator checklist、review packet、decision ledger preview、final readiness summary 与 human signoff schema draft | 创作前体检、生成后投影健康、读者修订评审、检索上下文预算包、任务模型画像、设定卡片、API 契约、发行准备、向量检索就绪探针、embedding 样本评估、失败样本采集、CLI 复跑、Markdown/manifest 导出包、mock 对照报告、replay case report、migration pack、跨项目索引、趋势快照、GraphRAG/Zep 触发证据、Graph 记忆设计包、Shadow 对照、Case 矩阵、Provider 边界、离线 Replay 计划、离线 Replay 报告、Provider Spike 前置包、Readiness Gate、Runbook、Result Template、Mock Result Report、Review Gate、Manual Approval Pack、Approval Evidence Checklist、Opt-in Evidence Snapshot、No-go Matrix、Operator Checklist、Review Packet、Decision Ledger Preview、Final Readiness Summary 和 Human Signoff Schema Draft 已接入；真实 embedding、向量库、GraphRAG、Zep、reranker 仍保持触发式。 |

## 3. A-slice、MVP 与完整产品能力

**A-slice** 是复杂能力的第一刀最小可验收切片。它必须有稳定 artifact、API 或 UI 解释层，能被测试覆盖，也能安全降级；但通常不会立刻驱动默认 runner 或改变核心状态。

**MVP 完成** 必须说明是哪一层 MVP：

- v0.1-v0.6 是引擎能力 MVP：能运行、能分叉、能续章、能检索、能审计内部机制。
- v0.7-v0.7.5 是短中篇产品化 MVP：普通用户可以通过 Web 完成核心体验。
- v0.8 是长篇底座与产品化工作台：长篇记忆、账本、检索、审计、回放、续写前置流程成立。
- v0.9.0-alpha 是长篇共创 alpha 闭环：可从项目资产走到选择世界线、续写、审计、导出和 closeout。
- v1.0-beta / v1.0-local 是本地优先加固：把商业化、部署、权限、审计、模型配置和本地启动边界讲清楚，但不代表真实云端平台已完成。

## 4. 后续排期原则

1. 先本地体验稳定，再做发行分发：Release 安装包、内置 runtime、服务器在线体验都等用户本地试用反馈。
2. 先只读解释，再状态执行：动作计划、动作注册表、叙事诊断、涌现节点默认作为解释层；状态 overlay 仍需显式 apply/rollback。
3. 先触发式评估，再接重依赖：Zep、图数据库、GraphRAG、LangGraph、OASIS、CAMEL 都不默认进入主线。
4. 商业化/计费暂缓：真实计费、支付、余额、发票、webhook、对象存储和认证执行继续后置。
5. 每次升级都保持 additive：不破坏 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json` 既有契约。
