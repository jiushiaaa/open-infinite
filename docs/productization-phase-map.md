# Living Novel Engine 产品化阶段归类

> 用途：统一解释 “MVP / A-slice / 产品化 / 商业化” 的口径，避免把已完成的技术底座误读为完整商业产品。当前状态以 `memory.md` 和 `docs/living-novel-engine-iteration-plan.md` 为准。

## 1. 一句话结论

Living Novel Engine 已完成 **短中篇可交互产品化 MVP**，并完成了 **长篇记忆与机制底座 MVP**。v0.8.6 Long Import Review、v0.8.7 Resumable Ingest Jobs、v0.8.8 Long Project Workspace、v0.8.9 Long Replay & Audit UI 与 v0.8.10-A/B Runner State Execution 已把导入检查、断点续传、项目资产页、回放审计 UI、状态执行 dry-run 评估和可回滚 overlay 写入收口；v0.9.0-alpha 已启动，Chapter Export 已让所选世界线章节可带来源/AI 说明导出，Chapter Collection Export 已让父链章节可导出为合集，Export Share Guard 已让导出前可见版权/分享边界，Creation Loop Completion Gate 已让项目工作台显示闭环完成度和阻塞项，Creation Loop Action Hints 已把阻塞项变成可执行/可跳转动作，Creation Loop Readiness Evidence 已把完成度判定映射到 artifact/API/页面依据，Creation Loop Audit Quick Run 已让选择后审计可直接从工作台运行范围回放，Creation Loop Alpha Ready State 已验证 `can_mark_alpha_complete=true` 的完整条件并让前端显示「可收口」，Creation Loop Alpha Closeout Report 已把 ready 状态、阻塞项、依据和下一步整理成只读收口报告，Creation Loop Closeout API 已提供直接 HTTP 验收入口、阻塞动作清单、动作 payload、稳定 blocker id 和审计 requirements，Requirements UI Display 已把审计前置条件展示到创作闭环完成度区，Builtin Holdout Blocked Requirement 已把只读样例无法录入 holdout 的情况标为 blocked，Creation Loop Checklist 已让项目工作台能推荐继续世界线并展示清单，Continuation Hint 已把推荐分支接到 CLI 续写入口，Resume Continue HTTP Job 已让推荐分支可显式生成下一章，Worldline Selection Persistence 已让用户选择的继续起点可持久读回，Post-run Audit Entry 已把已选世界线与审计/回放入口接起来。下一步继续把这些能力串成普通用户可复盘、可审计、可继续创作的长篇共创闭环。

## 2. 阶段归类表

| 阶段 | 阶段性质 | 产品化程度 | 当前判断 |
| --- | --- | --- | --- |
| v0.1-v0.3 | CLI、导入、检索、状态与续章底座 | 技术 MVP | 证明 “文本 -> 状态 -> 干预 -> 分叉 -> 续章” 能跑通；主要面向开发者和验证，不是完整产品。 |
| v0.4-v0.4.2 | 只读世界线浏览器与检索展示 | 研发/演示产品化 | 可以浏览世界线、章节、状态和检索记忆，但仍偏开发者 viewer，不承担普通用户主工作流。 |
| v0.5-v0.6.5 | 第四面墙、SceneRunner、多 Agent 协议/runner | 引擎机制 MVP | 角色觉察、多 Agent trace、runner 适配层成立；能力可审计、可演示，但产品入口仍不完整。 |
| v0.7-v0.7.5 | React Product Web App、Agent Interaction、视觉资产、Baseline/Replay、Worldline Judge | 短中篇产品化 MVP | 第一轮真正面向普通用户的产品化闭环已成立，适合短中篇、单项目、单次或少量分支创作。 |
| v0.8.0-A-v0.8.5-A | Long Novel Memory、canon ledger、retrieval、audit、holdout isolation | 长篇引擎底座 MVP | 长篇导入后的记忆、正史账本、检索、一致性审计和回放隔离已经成立，但仍偏 artifact/API。 |
| v0.8+ A-slices | ActDirector-A、Discourse-aware Narrator-A、Dynamic Action Registry-A、Emergence Mining-A、Entity Aliases、Runtime Memory Consumption-A | 机制接缝与解释层 MVP | 这些 A-slice 是可读、可验收、可解释的最小闭环；默认不代表已经进入强状态执行或复杂 runner。 |
| v0.8.6-v0.8.10 | Long Import Review、Resumable Jobs、Long Workspace、Replay/Audit UI、Runner State Execution | 长篇产品化收束 | 已把长篇底座变成清晰的上传、检查、管理、审计、回放、状态覆盖与继续创作前置流程。 |
| v0.9.0-alpha | Long Novel Creation Loop | 长篇产品化闭环成立 | 进行中：Export / Collection Export / Share Guard / Completion Gate / Action Hints / Readiness Evidence / Audit Quick Run / Alpha Ready State / Alpha Closeout Report / Closeout API / Closeout API Actions / Action Payloads / Stable Blocker IDs / Replay Audit Action Requirements / Requirements UI Display / Builtin Holdout Blocked Requirement / Checklist / Hint / Resume Job / Selection / Post-run Audit 已收口；上传/创建 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出整体走通后仍是 alpha，不等于商业级。 |
| v0.9.1-v0.9.4 | Provider/Cost、MasterSetting Lite、Graph Memory Spike、Advanced Runner Spike | 真实使用压力增强 | 按成本、长篇召回、设定管理、runner 复杂度触发增强，不提前引入重依赖。 |
| v1.0-beta | Commercial Hardening | 商业级/规模化 | 账号、权限、云端持久化、配额、审计日志、版权提示、部署与观测等面向外部用户长期使用。 |

## 3. A-slice、MVP 与完整产品能力

**A-slice** 表示某个复杂能力的第一刀最小可验收切片。它必须有稳定 artifact、API 或 UI 解释层，能被测试覆盖，也能安全降级；但它通常不会立刻驱动默认 runner 或改变核心状态。

**MVP 完成** 要说明是哪一层 MVP：

- v0.1-v0.6 完成的是引擎能力 MVP：能运行、能分叉、能续章、能检索、能审计内部机制。
- v0.7-v0.7.5 完成的是短中篇产品化 MVP：普通用户可以通过 Web 完成导入/创世/锚定/干预/评审主流程。
- v0.8.0-v0.8.5 完成的是长篇底座 MVP：长篇记忆与正史能力能落盘、检索、审计、隔离。
- v0.8.6-v0.8.10 要做的是长篇产品化：把底座能力变成用户看得懂、修得动、能继续使用的工作台。
- v0.9.0-alpha 已启动并完成章节导出、章节合集导出、导出版权/分享 guard、闭环完成度判定、阻塞动作提示、判定依据、审计快捷运行、alpha ready 状态、alpha closeout 报告、closeout HTTP 验收接口与动作清单、动作 payload、稳定 blocker id、审计 requirements、审计前置 UI 展示、builtin holdout blocked 解释、创作闭环清单、CLI 续写入口、显式续写 job、世界线选择持久化和选择后审计入口子刀；完整完成后，长篇共创才算形成产品闭环，但仍需 v0.9.1+ 和 v1.0-beta 才能接近商业级。

## 4. 后续排期原则

1. 先完成用户路径，再引入重依赖：Zep、图数据库、OASIS、CAMEL、LangGraph 都不应抢在 v0.9.0-alpha 之前成为默认路线。
2. 先只读解释，再状态执行：动作计划、动作注册表、叙事诊断、涌现节点先作为右侧只读解释层；v0.8.10-A 已完成 dry-run 评估，v0.8.10-B 已完成 opt-in overlay 写入和回滚。
3. 先本地 artifact 稳定，再商业化平台化：v1.0-beta 才处理账号、权限、云端存储、配额和观测等外部交付问题。
4. 每次升级都保持 additive：不破坏 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json` 既有契约。
