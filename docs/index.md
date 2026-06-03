# 未终章 Docs Index

> 用途：说明 `docs/` 下各类文档的位置、职责和推荐读取顺序。进入项目时仍以根目录 `AGENTS.md` 与 `memory.md` 作为第一入口；本文件负责把 `docs/` 资料库串起来。

## 0. 根目录入口

| 路径 | 作用 | 什么时候读 |
| --- | --- | --- |
| `../AGENTS.md` | Agent 项目级规则、硬约束、会话开始必读清单 | 每个新 Codex/Agent 会话先读 |
| `../memory.md` | 当前事实收口、版本状态、测试基线、历史变更日志索引 | 判断“现在做到哪了”和“下一刀是什么”时先读 |
| `../engine/README.md` | CLI/API/产物结构/验收命令 | 改代码、跑 demo、确认 artifact 契约时读 |

## 1. 推荐读取顺序

### 新会话接力

1. `../AGENTS.md`
2. `codex-handoff.md`
3. `../memory.md`
4. `living-novel-engine-iteration-plan.md`
5. `productization-phase-map.md`
6. `living-novel-engine-prd.md`
7. `completed/v0.7-product-web-app-ui-spec.md`
8. `../engine/README.md`

### 做版本规划或判断下一步

1. `../memory.md`
2. `living-novel-engine-iteration-plan.md`
3. `productization-phase-map.md`
4. `completed/v0.1-to-v0.8-version-audit.md`
5. `living-novel-engine-prd.md`
6. 必要时读 `completed/` 下对应阶段专项文档

### 做前端 UI 或产品体验

1. `completed/v0.7-product-web-app-ui-spec.md`
2. `living-novel-engine-prd.md`
3. `codex-handoff.md`
4. `../engine/README.md`

### 做论文能力或参考项目吸收

1. `article/reports/` 下对应论文研读报告
2. `completed/open-source-essence-absorption.md`
3. `living-novel-engine-iteration-plan.md`
4. `../memory.md`

## 2. docs 根层文档

| 路径 | 类型 | 作用 |
| --- | --- | --- |
| `index.md` | 导航 | 当前文件，说明文档地图和读取顺序 |
| `codex-handoff.md` | 接力包 | 新开 Codex 窗口时的最小上下文、当前暂停点和开发约束 |
| `codex-migration-guide.md` | 迁移说明 | `.cursor/rules`、`.cursor/skills` 与 Codex skills/plugins 的迁移关系 |
| `project-changelog.md` | 历史日志 | 从 `memory.md` 迁出的完整变更日志，供追溯版本过程和历史验收记录 |
| `brand/` | 品牌资产 | 未终章 / Unfinale 的 SVG 标识、图标和 imagegen 概念稿 |
| `living-novel-engine-prd.md` | 主 PRD | 产品定位、用户流程、核心能力、版本级需求入口 |
| `living-novel-engine-iteration-plan.md` | 主路线图 | 当前阶段状态、暂停点、真实未做项和后续候选路线 |
| `productization-phase-map.md` | 阶段归类 | 统一解释技术 MVP、短中篇产品化 MVP、长篇底座、长篇产品化、商业化加固的边界 |
| `distribution-phase-plan.md` | 发行路径 | 本地 clone、GitHub Release 安装包、服务器在线体验三条后置使用路径 |
| `completed/` | 收口归档 | 已收口版本 PRD、Release Note、工程协议、UI spec 与版本审计，供追溯和必要时引用 |

## 3. completed/ 收口归档

`completed/` 存放已收口的阶段专项 PRD、Release Note、工程协议、UI spec 与版本审计。它们是历史阶段的细化依据，不承担当前最高优先级；当前状态以 `../memory.md`、主迭代计划和 `productization-phase-map.md` 为准。

| 路径 | 阶段 | 作用 |
| --- | --- | --- |
| `completed/README.md` | 目录索引 | `completed/` 分组导航、后续状态口径和仍然后置的主边界 |
| `completed/v0.1-to-v0.8-version-audit.md` | v0.1-v0.8 | v0.8 时点历史审计快照；已标注当时未做项在 v1.0 前后的后续状态 |
| `completed/codex-handoff-legacy-2026-06-01.md` | 接力归档 | `codex-handoff.md` 瘦身前的长接力稿，供追溯历史上下文 |
| `completed/living-novel-engine-iteration-plan-legacy-2026-06-01.md` | 路线图归档 | `living-novel-engine-iteration-plan.md` 瘦身前的完整逐刀实施清单 |
| `completed/open-source-essence-absorption.md` | v0.2.2 | WenShape / webnovel-writer 的可吸收能力、已复制资产、许可证边界和明确不做项 |
| `completed/v0.2-import-novel-mvp.md` | v0.2 | 导入已有小说的最小闭环设计、命令面和成功标准 |
| `completed/v0.4-worldline-browser-release.md` | v0.4 | 只读世界线浏览器的 Release Note、功能矩阵和复现验收链路 |
| `completed/v0.6.1-multi-agent-runner-protocol.md` | v0.6.1 | Multi-Agent Runner Protocol 的数据结构、输出契约和边界 |
| `completed/v0.6.4-multi-agent-llm-runner.md` | v0.6.4 | `multi_agent_llm` runner 的架构、隐私加固、回退和用法 |
| `completed/v0.6.5-multi-agent-reliability.md` | v0.6.5 | 多 Agent 推演可靠性、trace 质量校验、重试和 token usage |
| `completed/v0.7-product-web-app-ui-spec.md` | v0.7 | 产品级 Web App 的信息架构、视觉风格、组件边界和增量能力 |
| `completed/v0.9-to-v1.0-product-ui-addenda.md` | v0.9-v1.0 | 从 v0.7 UI spec 拆出的后续产品 UI 增量：长篇闭环、Provider/Cost、MasterSetting、商业化边界和本地模型配置 |
| `completed/v0.9.0-alpha-long-creation-loop.md` | v0.9.0-alpha | 长篇共创闭环收口说明、closeout proof、边界与后续状态 |
| `completed/v0.9.1-provider-cost-gateway-lite.md` | v0.9.1 | Provider/Cost Lite 收口说明、脱敏 provider 状态、usage 汇总、成本估算与路由矩阵 |
| `completed/v0.9.2-master-setting-workspace-lite.md` | v0.9.2 | MasterSetting Workspace Lite 收口说明、设定资产聚合、白名单轻编辑、前端最小写控件与边界 |
| `completed/v0.9.3-graph-memory-evaluation-spike.md` | v0.9.3 | Graph Memory Evaluation Spike 收口说明、触发报告、检索 probe、失败样例边界与后续状态 |
| `completed/v0.9.4-advanced-runner-evaluation-spike.md` | v0.9.4 | Advanced Runner Evaluation Spike 收口说明、触发报告、runner probe、失败样例边界与后续状态 |
| `completed/v1.0-beta-commercial-hardening-scope-a.md` | v1.0-beta | Commercial Hardening Scope-A 收口说明、商业化七域范围复核、本地优先边界与后续状态 |
| `completed/v1.0-beta-commercial-audit-log-schema-b.md` | v1.0-beta | Commercial Audit Log Schema-B 收口说明、本地审计事件 schema、只读聚合与边界 |
| `completed/v1.0-beta-permission-matrix-draft-c.md` | v1.0-beta | Permission Matrix Draft-C 收口说明、owner/editor/viewer 权限矩阵草案与未执行边界 |
| `completed/v1.0-beta-project-copyright-statement-d.md` | v1.0-beta | Project Copyright Statement-D 收口说明、项目级版权/来源声明 schema 与导出 rights basis |
| `completed/v1.0-beta-quota-observability-lite-e.md` | v1.0-beta | Quota & Observability Lite-E 收口说明、本地配额/观测口径、usage 与 job 状态 |
| `completed/v1.0-beta-local-deployment-readiness-f.md` | v1.0-beta | Local Deployment Readiness-F 收口说明、本地部署就绪、脱敏环境、静态资源与 API 冒烟 |
| `completed/v1.0-beta-cloud-persistence-boundary-g.md` | v1.0-beta | Cloud Persistence Boundary-G 收口说明、本地 artifact 到未来平台资源的映射、保留规则与迁移边界 |
| `completed/v1.0-beta-account-project-space-boundary-h.md` | v1.0-beta | Account Project Space Boundary-H 收口说明、本地账号语义、项目空间清单与未来团队归属边界 |
| `completed/v1.0-beta-audit-log-append-policy-i.md` | v1.0-beta | Audit Log Append Policy-I 收口说明、本地项目审计日志白名单追加策略 |
| `completed/v1.0-beta-project-retention-policy-j.md` | v1.0-beta | Project Retention Policy-J 收口说明、本地项目删除/保留策略 artifact 与 API |
| `completed/v1.0-beta-copyright-audit-hook-k.md` | v1.0-beta | Copyright Audit Hook-K 收口说明、版权/来源声明写操作接入本地审计日志 |
| `completed/v1.0-beta-master-setting-audit-hook-l.md` | v1.0-beta | MasterSetting Audit Hook-L 收口说明、设定轻编辑写操作接入本地审计日志 |
| `completed/v1.0-beta-worldline-selection-audit-hook-m.md` | v1.0-beta | Worldline Selection Audit Hook-M 收口说明、世界线选择写操作接入本地审计日志 |
| `completed/v1.0-beta-state-execution-audit-hook-n.md` | v1.0-beta | State Execution Audit Hook-N 收口说明、状态执行 apply/rollback 接入本地审计日志 |
| `completed/v1.0-beta-commercial-status-overview-o.md` | v1.0-beta | Commercial Status Overview-O 收口说明、设置页商业化状态总览 |
| `completed/v1.0-beta-audit-log-ui-export-p.md` | v1.0-beta | Audit Log UI & Export-P 收口说明、项目工作台审计时间线和 Markdown 导出 |
| `completed/v1.0-beta-settings-local-smoke-checklist-q.md` | v1.0-beta | Settings Local Smoke Checklist-Q 收口说明、设置页本地冒烟清单 |
| `completed/v1.0-beta-release-preflight-checklist-r.md` | v1.0-beta | Release Preflight Checklist-R 收口说明、发布前只读检查清单 |
| `completed/v1.0-beta-rights-approval-checklist-s.md` | v1.0-beta | Rights Approval Checklist-S 收口说明、项目版权审批准备度只读检查 |
| `completed/v1.0-beta-deployment-observability-checklist-t.md` | v1.0-beta | Deployment Observability Checklist-T 收口说明、部署观测只读清单 |
| `completed/v1.0-beta-auth-boundary-checklist-u.md` | v1.0-beta | Auth Boundary Checklist-U 收口说明、认证边界只读清单 |
| `completed/v1.0-beta-object-storage-boundary-checklist-v.md` | v1.0-beta | Object Storage Boundary Checklist-V 收口说明、对象存储边界只读清单 |
| `completed/v1.0-beta-quota-enforcement-boundary-checklist-w.md` | v1.0-beta | Quota Enforcement Boundary Checklist-W 收口说明、配额执行边界只读清单 |
| `completed/v1.0-beta-billing-adapter-boundary-checklist-x.md` | v1.0-beta | Billing Adapter Boundary Checklist-X 收口说明、计费 adapter 边界只读清单 |
| `completed/v1.0-local-model-configuration-ux.md` | v1.0-local | Model Configuration UX 收口说明、设置页模型配置状态和计费 UI 暂停边界 |
| `completed/v1.0-local-run-scripts.md` | v1.0-local | Local Run Scripts 收口说明、Windows/macOS 本地一键启动脚本与边界 |
| `completed/runtime-preflight-mvp.md` | 后续增强 | Runtime Preflight MVP 收口说明、创作前只读健康聚合 API 与项目工作台 UI |
| `completed/projection-health-mvp.md` | 后续增强 | Projection Health MVP 收口说明、生成后分支投影健康 API 与右栏 UI |
| `completed/reader-panel-revision-lab-mvp.md` | 后续增强 | Reader Panel / Adversarial Revision Lab MVP 收口说明、确定性读者评审 API 与右栏 UI |
| `completed/prompt-budget-pack-mvp.md` | 后续增强 | Prompt Budget Pack MVP 收口说明、检索上下文预算包 API 与右栏 UI |
| `completed/llm-profile-assignment-mvp.md` | 后续增强 | LLM Profile Assignment MVP 收口说明、任务级模型画像 API 与设置页 UI |
| `completed/cards-workspace-mvp.md` | 后续增强 | Cards Workspace MVP 收口说明、世界卡/角色卡/风格卡 API 与项目工作台 UI |
| `completed/openapi-typed-client-mvp.md` | 后续增强 | OpenAPI / Typed Client MVP 收口说明、本地 API 契约、OpenAPI skeleton 与 typed client 映射 |
| `completed/bundled-release-readiness-mvp.md` | 后续增强 | Bundled Release Readiness MVP 收口说明、本地发行与桌面打包准备度 API 与设置页 UI |
| `completed/vector-retrieval-readiness-probe-mvp.md` | 后续增强 | Embedding / Vector Retrieval Readiness Probe MVP 收口说明、向量检索接入前的召回压力 API 与项目工作台 UI |
| `completed/embedding-evaluation-samples-mvp.md` | 后续增强 | Embedding Evaluation Samples MVP 收口说明、失败样本 BM25 与 mock semantic oracle 对照 API 与项目工作台 UI |
| `completed/retrieval-failure-sample-authoring-mvp.md` | 后续增强 | Retrieval Failure Sample Authoring MVP 收口说明、本地失败样本追加 API 与项目工作台 UI |
| `completed/memory-cli-mvp.md` | 后续增强 | Memory CLI MVP 收口说明、命令行失败样本追加与复跑工具 |
| `completed/retrieval-sample-export-pack-mvp.md` | 后续增强 | Retrieval Sample Export Pack MVP 收口说明、失败样本 Markdown/manifest 导出 API、UI 与 CLI |
| `completed/embedding-mock-evaluation-report-mvp.md` | 后续增强 | Embedding Mock Evaluation Report MVP 收口说明、BM25 与 mock semantic oracle 对照报告 API、UI 与 CLI |
| `completed/retrieval-sample-replay-report-mvp.md` | 后续增强 | Retrieval Sample Replay Report MVP 收口说明、失败样本当前检索 case report API、UI 与 CLI |
| `completed/retrieval-sample-migration-pack-mvp.md` | 后续增强 | Retrieval Sample Migration Pack MVP 收口说明、稳定 eval records 与 JSON manifest API、UI 与 CLI |
| `completed/cross-project-retrieval-samples-index-mvp.md` | 后续增强 | Cross Project Retrieval Samples Index MVP 收口说明、跨项目 migration pack 索引 API、CLI 与设置页 |
| `completed/retrieval-samples-trend-snapshot-mvp.md` | 后续增强 | Retrieval Samples Trend Snapshot MVP 收口说明、样本趋势快照 API、CLI 与设置页 |
| `completed/graph-memory-trigger-evidence-mvp.md` | 后续增强 | GraphRAG / Zep Trigger Evidence MVP 收口说明、图记忆触发证据 API、CLI 与项目工作台 |
| `completed/graph-memory-spike-design-pack-mvp.md` | 后续增强 | Graph Memory Spike Design Pack MVP 收口说明、重型记忆 spike 设计包 API、CLI 与项目工作台 |
| `completed/graph-memory-shadow-compare-pack-mvp.md` | 后续增强 | Graph Memory Shadow Compare Pack MVP 收口说明、重型记忆候选层 shadow 对照 API、CLI 与项目工作台 |
| `completed/graph-memory-shadow-case-matrix-mvp.md` | 后续增强 | Graph Memory Shadow Case Matrix MVP 收口说明、eval case x 候选层矩阵 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-boundary-matrix-mvp.md` | 后续增强 | Graph Memory Provider Boundary Matrix MVP 收口说明、GraphRAG/Zep/Temporal Memory provider 边界矩阵 API、CLI 与项目工作台 |
| `completed/graph-memory-offline-shadow-replay-plan-mvp.md` | 后续增强 | Graph Memory Offline Shadow Replay Plan MVP 收口说明、离线 replay 计划 API、CLI 与项目工作台 |
| `completed/graph-memory-offline-shadow-replay-report-mvp.md` | 后续增强 | Graph Memory Offline Shadow Replay Report MVP 收口说明、mock replay 结果 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-fixture-pack-mvp.md` | 后续增强 | Graph Memory Provider Spike Fixture Pack MVP 收口说明、dry-run 前置包 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-readiness-gate-mvp.md` | 后续增强 | Graph Memory Provider Spike Readiness Gate MVP 收口说明、provider spike 就绪门禁 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-runbook-mvp.md` | 后续增强 | Graph Memory Provider Spike Runbook MVP 收口说明、人工 opt-in dry-run SOP API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-dry-run-result-template-mvp.md` | 后续增强 | Graph Memory Provider Spike Dry-run Result Template MVP 收口说明、人工 dry-run 结果模板 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-mock-result-report-mvp.md` | 后续增强 | Graph Memory Provider Spike Mock Result Report MVP 收口说明、mock 填充结果 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-review-gate-mvp.md` | 后续增强 | Graph Memory Provider Spike Review Gate MVP 收口说明、人工复核 gate API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-manual-approval-pack-mvp.md` | 后续增强 | Graph Memory Provider Spike Manual Approval Pack MVP 收口说明、人工审批包 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-manual-approval-evidence-checklist-mvp.md` | 后续增强 | Graph Memory Provider Spike Manual Approval Evidence Checklist MVP 收口说明、审批证据核对表 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-opt-in-evidence-snapshot-mvp.md` | 后续增强 | Graph Memory Provider Spike Opt-in Evidence Snapshot MVP 收口说明、opt-in 证据快照 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-opt-in-no-go-matrix-mvp.md` | 后续增强 | Graph Memory Provider Spike Opt-in No-go Matrix MVP 收口说明、no-go 分类矩阵 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-opt-in-operator-checklist-mvp.md` | 后续增强 | Graph Memory Provider Spike Opt-in Operator Checklist MVP 收口说明、人工操作 checklist API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-opt-in-review-packet-mvp.md` | 后续增强 | Graph Memory Provider Spike Opt-in Review Packet MVP 收口说明、人工复核包 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-opt-in-decision-ledger-preview-mvp.md` | 后续增强 | Graph Memory Provider Spike Opt-in Decision Ledger Preview MVP 收口说明、决策账本预览 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-opt-in-final-readiness-summary-mvp.md` | 后续增强 | Graph Memory Provider Spike Opt-in Final Readiness Summary MVP 收口说明、最终就绪摘要 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-opt-in-human-signoff-schema-draft-mvp.md` | 后续增强 | Graph Memory Provider Spike Opt-in Human Signoff Schema Draft MVP 收口说明、人工签收 schema 草案 API、CLI 与项目工作台 |
| `completed/graph-memory-provider-spike-opt-in-config-and-adapter-slices-mvp.md` | 后续增强 | Graph Memory Provider Spike Opt-in Config Draft、Local Provider Contract、Single Fixture Dry-run Harness 与 Mock-compatible Adapter 四刀收口说明 |
| `completed/graph-memory-provider-spike-manual-mock-adapter-review-mvp.md` | 后续增强 | Graph Memory Provider Spike Manual Mock Adapter Review 人工复核包与合规检查收口说明 |

## 4. article/ 论文资料

`article/` 存放论文 PDF 原文；`article/reports/` 存放已转化为 LNE 路线语言的研读报告。开发时优先读报告，只有需要核对原文时再打开 PDF。

### PDF 原文

| 路径 | 主题 |
| --- | --- |
| `article/2404.17027v3.pdf` | Player-Driven Emergence / 用户驱动涌现 |
| `article/2405.13042v2.pdf` | StoryVerse / Abstract Act / Act Director |
| `article/2407.13248v2.pdf` | Human-Level Narratives / Story Arc / Turning Points |
| `article/2505.03547v1.pdf` | STORY2GAME / Dynamic Action Generation |

### 研读报告

| 路径 | 可借鉴能力 |
| --- | --- |
| `article/reports/2404.17027v3-player-driven-emergence-report.md` | 用户驱动涌现、emergence nodes、玩家动机 |
| `article/reports/2405.13042v2-storyverse-report.md` | Abstract Act、Concrete Act、ActDirector、角色模拟 |
| `article/reports/2407.13248v2-human-level-narratives-report.md` | Story Arc、Turning Points、叙事质量评估 |
| `article/reports/2505.03547v1-story2game-report.md` | Preconditions、Effects、Dynamic Action Generation |

## 5. 维护约定

- 新增仍在跟进的主线文档可留在 `docs/` 根部；已收口版本专项文档归档到 `completed/`，并在本文件登记。
- 新增论文原文放 `article/`，论文解读放 `article/reports/`，不要只放 PDF 不写报告。
- 新增参考项目分析若仍在调研，可先放 `article/reports/` 或临时草稿；完成吸收决策后归档到 `completed/`，并写清“吸收什么 / 不做什么 / 是否复制资产 / 许可证边界”。
- `AGENTS.md` 和 `memory.md` 保持在根目录：前者是 Agent 入口规则，后者是当前事实收口；完整历史变更日志放在 `project-changelog.md`。
- 完成版本后同步顺序建议为：`memory.md` 当前状态 -> `project-changelog.md` 历史记录（如需追加） -> `living-novel-engine-iteration-plan.md` -> 相关 PRD/UI spec/README -> `codex-handoff.md` -> 本文件。
