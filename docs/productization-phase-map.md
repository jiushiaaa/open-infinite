# Living Novel Engine 产品化阶段归类

> 用途：统一解释 “MVP / A-slice / 产品化 / 商业化” 的口径，避免把已完成的技术底座误读为完整商业产品。当前状态以 `memory.md` 和 `docs/living-novel-engine-iteration-plan.md` 为准。

## 1. 一句话结论

Living Novel Engine 已完成 **短中篇可交互产品化 MVP**、**长篇记忆与机制底座 MVP**，并已把 **v0.9.0-alpha Long Novel Creation Loop** 收口为第一条长篇共创产品闭环。v0.8.6-v0.8.10 已把导入检查、断点续传、项目资产页、回放审计 UI、状态执行 dry-run 评估和可回滚 overlay 写入收口；v0.9.0-alpha 已把章节导出、父链合集导出、版权/分享 guard、闭环完成度、阻塞动作、判定依据、审计快捷运行、alpha closeout 报告、HTTP/CLI closeout 验收、ready 后 `creation_loop_alpha_closeout.json` 收口记录、推荐世界线、显式续写 job、起点持久化与选择后审计串成闭环。v0.9.1 Provider & Cost Gateway Lite 已整体收口，完成只读 provider 摘要、脱敏展示、降级策略、成本观测口径、usage 聚合、设置页展示、手动单价估算与只读路由矩阵；v0.9.2 MasterSetting Workspace Lite 已整体收口，完成只读聚合、工作台展示、后端白名单轻编辑与前端最小写控件；v0.9.3 Graph Memory Evaluation Spike 已整体收口，完成图记忆触发报告、代表性检索 probe 和失败样例收集，当前不触发重依赖接入；v0.9.4 Advanced Runner Evaluation Spike 已整体收口，完成高级 runner 触发报告、代表性 runner probe 和失败样例收集，当前不接 LangGraph/OASIS/CAMEL；v1.0-beta Commercial Hardening Scope-A 已收口，完成商业化七域范围复核和本地优先边界说明；v1.0-beta Commercial Audit Log Schema-B 已收口，完成本地项目审计日志 schema 与既有 artifact 只读聚合；v1.0-beta Permission Matrix Draft-C 已收口，完成 owner/editor/viewer 权限矩阵草案；v1.0-beta Project Copyright Statement-D 已收口，完成项目级版权/来源声明 schema 与导出 `rights_basis`；v1.0-beta Quota & Observability Lite-E 已收口，完成本地配额/观测口径；v1.0-beta Local Deployment Readiness-F 已收口，完成本地部署就绪清单；v1.0-beta Cloud Persistence Boundary-G 已收口，完成本地 artifact 到未来平台资源的迁移边界；v1.0-beta Account Project Space Boundary-H 已收口，完成本地账号语义、项目空间清单和未来团队归属边界；v1.0-beta Audit Log Append Policy-I 已收口，完成本地审计日志白名单追加策略；v1.0-beta Project Retention Policy-J 已收口，完成本地项目删除/保留策略；v1.0-beta Copyright Audit Hook-K 已收口，完成版权/来源声明写入审计钩子；v1.0-beta MasterSetting Audit Hook-L 已收口，完成设定轻编辑写入审计钩子；v1.0-beta Worldline Selection Audit Hook-M 已收口，完成世界线选择写入审计钩子；v1.0-beta State Execution Audit Hook-N 已收口，完成状态 overlay apply/rollback 写入审计钩子；v1.0-beta Commercial Status Overview-O 已收口，完成设置页商业化状态总览；v1.0-beta Audit Log UI & Export-P 已收口，完成项目工作台审计时间线展示和本地 Markdown 导出；v1.0-beta Settings Local Smoke Checklist-Q 已收口，完成设置页本地冒烟清单；v1.0-beta Release Preflight Checklist-R 已收口，完成设置页发布前只读检查；v1.0-beta Rights Approval Checklist-S 已收口，完成项目工作台版权审批准备度只读检查；v1.0-beta Deployment Observability Checklist-T 已收口，完成设置页部署观测只读清单；v1.0-beta Auth Boundary Checklist-U 已收口，完成设置页认证边界只读清单；v1.0-beta Object Storage Boundary Checklist-V 已收口，完成设置页对象存储边界只读清单；v1.0-beta Quota Enforcement Boundary Checklist-W 已收口，完成设置页配额执行边界只读清单；v1.0-beta Billing Adapter Boundary Checklist-X 已收口，完成设置页计费 adapter 边界只读清单；v1.0-local Model Configuration UX 与 Local Run Scripts 已收口。当前不接云端多租户、真实对象存储、真实认证或真实计费系统。

## 2. 阶段归类表

当前用户侧优先级已调整：短期暂停继续推进商业化/计费实现，先把本地模型配置、长篇创作闭环、本地验证体验打磨到可公开试用；本地一键运行脚本已先落地，Release 安装包和服务器在线体验仍后置，详见 [`distribution-phase-plan.md`](./distribution-phase-plan.md)。

| 阶段 | 阶段性质 | 产品化程度 | 当前判断 |
| --- | --- | --- | --- |
| v0.1-v0.3 | CLI、导入、检索、状态与续章底座 | 技术 MVP | 证明 “文本 -> 状态 -> 干预 -> 分叉 -> 续章” 能跑通；主要面向开发者和验证，不是完整产品。 |
| v0.4-v0.4.2 | 只读世界线浏览器与检索展示 | 研发/演示产品化 | 可以浏览世界线、章节、状态和检索记忆，但仍偏开发者 viewer，不承担普通用户主工作流。 |
| v0.5-v0.6.5 | 第四面墙、SceneRunner、多 Agent 协议/runner | 引擎机制 MVP | 角色觉察、多 Agent trace、runner 适配层成立；能力可审计、可演示，但产品入口仍不完整。 |
| v0.7-v0.7.5 | React Product Web App、Agent Interaction、视觉资产、Baseline/Replay、Worldline Judge | 短中篇产品化 MVP | 第一轮真正面向普通用户的产品化闭环已成立，适合短中篇、单项目、单次或少量分支创作。 |
| v0.8.0-A-v0.8.5-A | Long Novel Memory、canon ledger、retrieval、audit、holdout isolation | 长篇引擎底座 MVP | 长篇导入后的记忆、正史账本、检索、一致性审计和回放隔离已经成立，但仍偏 artifact/API。 |
| v0.8+ A-slices | ActDirector-A、Discourse-aware Narrator-A、Dynamic Action Registry-A、Emergence Mining-A、Entity Aliases、Runtime Memory Consumption-A | 机制接缝与解释层 MVP | 这些 A-slice 是可读、可验收、可解释的最小闭环；默认不代表已经进入强状态执行或复杂 runner。 |
| v0.8.6-v0.8.10 | Long Import Review、Resumable Jobs、Long Workspace、Replay/Audit UI、Runner State Execution | 长篇产品化收束 | 已把长篇底座变成清晰的上传、检查、管理、审计、回放、状态覆盖与继续创作前置流程。 |
| v0.9.0-alpha | Long Novel Creation Loop | 长篇产品化闭环成立 | 已整体收口：上传/创建 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出 -> closeout record；仍是 alpha，不等于商业级。 |
| v0.9.1-v0.9.4 | Provider/Cost、MasterSetting Lite、Graph Memory Spike、Advanced Runner Spike | 真实使用压力增强 | v0.9.1-v0.9.4 已整体收口；重依赖仍按触发式评估。 |
| v1.0-beta Scope-A | Commercial Hardening Scope | 商业化范围复核 | 已收口：七域只读 scope report，明确本地优先边界和平台化延后项。 |
| v1.0-beta Schema-B | Commercial Audit Log | 商业化本地审计底座 | 已收口：定义 `project_audit_log.jsonl` schema，并从既有 artifact 只读聚合项目审计时间线。 |
| v1.0-beta Matrix-C | Permission Matrix Draft | 权限模型草案 | 已收口：owner/editor/viewer 三角色与关键资源权限矩阵，只读不执行。 |
| v1.0-beta Retention-J+ | Commercial Hardening | 商业级/规模化 | 项目删除/保留策略、版权声明写入审计钩子、设定轻编辑审计钩子、世界线选择审计钩子、状态执行审计钩子、设置页商业化状态总览、项目审计日志 UI/导出、本地冒烟清单、发布前检查、版权审批准备度清单、部署观测清单、认证边界清单、对象存储边界清单、配额执行边界清单和计费 adapter 边界清单已收口；后续真实认证实现、真实对象存储 adapter、真实配额 guardrail、webhook/idempotency 和真实计费仍需继续拆成小刀加固。 |

## 3. A-slice、MVP 与完整产品能力

**A-slice** 表示某个复杂能力的第一刀最小可验收切片。它必须有稳定 artifact、API 或 UI 解释层，能被测试覆盖，也能安全降级；但它通常不会立刻驱动默认 runner 或改变核心状态。

**MVP 完成** 要说明是哪一层 MVP：

- v0.1-v0.6 完成的是引擎能力 MVP：能运行、能分叉、能续章、能检索、能审计内部机制。
- v0.7-v0.7.5 完成的是短中篇产品化 MVP：普通用户可以通过 Web 完成导入/创世/锚定/干预/评审主流程。
- v0.8.0-v0.8.5 完成的是长篇底座 MVP：长篇记忆与正史能力能落盘、检索、审计、隔离。
- v0.8.6-v0.8.10 要做的是长篇产品化：把底座能力变成用户看得懂、修得动、能继续使用的工作台。
- v0.9.0-alpha 已整体收口，长篇共创形成 alpha 产品闭环；v0.9.1 provider/cost、v0.9.2 MasterSetting Lite、v0.9.3 Graph Memory Evaluation、v0.9.4 Advanced Runner Evaluation、v1.0-beta Scope-A、Schema-B、Matrix-C、Copyright-D、Quota-E、Deploy-F、Cloud-G、Account-H、Audit-I、Retention-J、Copyright Audit Hook-K、MasterSetting Audit Hook-L、Worldline Selection Audit Hook-M、State Execution Audit Hook-N、Commercial Status Overview-O、Audit Log UI & Export-P、Settings Local Smoke Checklist-Q、Release Preflight Checklist-R、Rights Approval Checklist-S、Deployment Observability Checklist-T、Auth Boundary Checklist-U、Object Storage Boundary Checklist-V、Quota Enforcement Boundary Checklist-W、Billing Adapter Boundary Checklist-X、v1.0-local Model Configuration UX 与 Local Run Scripts 已整体收口；真实认证、真实对象存储 adapter、真实配额 guardrail、webhook/idempotency 和真实计费继续后置。

## 4. 后续排期原则

1. 先完成用户路径，再引入重依赖：Zep、图数据库、OASIS、CAMEL、LangGraph 都不应抢在 v0.9.0-alpha 之前成为默认路线。
2. 先只读解释，再状态执行：动作计划、动作注册表、叙事诊断、涌现节点先作为右侧只读解释层；v0.8.10-A 已完成 dry-run 评估，v0.8.10-B 已完成 opt-in overlay 写入和回滚。
3. 先本地产品稳定，再做发行分发：本地一键运行脚本已作为 clone 用户辅助路径落地；Windows/macOS 安装包和腾讯云在线体验仍等本地体验稳定后再做。
4. 商业化/计费暂缓：真实计费、支付、余额、发票、webhook 不进入当前优先级；后续如恢复商业化，再重新拆小刀。
5. 每次升级都保持 additive：不破坏 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json` 既有契约。
