# Living Novel Engine Docs Index

> 用途：说明 `docs/` 下各类文档的位置、职责和推荐读取顺序。进入项目时仍以根目录 `AGENTS.md` 与 `memory.md` 作为第一入口；本文件负责把 `docs/` 资料库串起来。

## 0. 根目录入口

| 路径 | 作用 | 什么时候读 |
| --- | --- | --- |
| `../AGENTS.md` | Agent 项目级规则、硬约束、会话开始必读清单 | 每个新 Codex/Agent 会话先读 |
| `../memory.md` | 当前事实收口、版本状态、测试基线、变更日志 | 判断“现在做到哪了”和“下一刀是什么”时先读 |
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
2. `research/open-source-essence-absorption.md`
3. `living-novel-engine-iteration-plan.md`
4. `../memory.md`

## 2. docs 根层文档

| 路径 | 类型 | 作用 |
| --- | --- | --- |
| `index.md` | 导航 | 当前文件，说明文档地图和读取顺序 |
| `codex-handoff.md` | 接力包 | 新开 Codex 窗口时的最小上下文、已完成版本、下一刀建议和开发约束 |
| `codex-migration-guide.md` | 迁移说明 | `.cursor/rules`、`.cursor/skills` 与 Codex skills/plugins 的迁移关系 |
| `living-novel-engine-prd.md` | 主 PRD | 产品定位、用户流程、核心能力、版本级需求入口 |
| `living-novel-engine-iteration-plan.md` | 主路线图 | v0.1-v0.9+ 的迭代顺序、阶段状态、下一步路线 |
| `productization-phase-map.md` | 阶段归类 | 统一解释技术 MVP、短中篇产品化 MVP、长篇底座、长篇产品化、商业化加固的边界 |
| `distribution-phase-plan.md` | 发行路径 | 本地 clone、GitHub Release 安装包、服务器在线体验三条后置使用路径 |
| `completed/` | 收口归档 | 已收口版本 PRD、Release Note、工程协议、UI spec 与版本审计，供追溯和必要时引用 |

## 3. completed/ 收口归档

`completed/` 存放已收口的阶段专项 PRD、Release Note、工程协议、UI spec 与版本审计。它们是历史阶段的细化依据，不承担当前最高优先级；当前状态以 `../memory.md`、主迭代计划和 `productization-phase-map.md` 为准。

| 路径 | 阶段 | 作用 |
| --- | --- | --- |
| `completed/v0.1-to-v0.8-version-audit.md` | v0.1-v0.8 | 已完成能力、产物边界、未做项和下一步建议 |
| `completed/v0.2-import-novel-mvp.md` | v0.2 | 导入已有小说的最小闭环设计、命令面和成功标准 |
| `completed/v0.4-worldline-browser-release.md` | v0.4 | 只读世界线浏览器的 Release Note、功能矩阵和复现验收链路 |
| `completed/v0.6.1-multi-agent-runner-protocol.md` | v0.6.1 | Multi-Agent Runner Protocol 的数据结构、输出契约和边界 |
| `completed/v0.6.4-multi-agent-llm-runner.md` | v0.6.4 | `multi_agent_llm` runner 的架构、隐私加固、回退和用法 |
| `completed/v0.6.5-multi-agent-reliability.md` | v0.6.5 | 多 Agent 推演可靠性、trace 质量校验、重试和 token usage |
| `completed/v0.7-product-web-app-ui-spec.md` | v0.7 | 产品级 Web App 的信息架构、视觉风格、组件边界和增量能力 |
| `completed/v0.9.0-alpha-long-creation-loop.md` | v0.9.0-alpha | 长篇共创闭环收口说明、closeout proof、边界与下一步 |
| `completed/v0.9.1-provider-cost-gateway-lite.md` | v0.9.1 | Provider/Cost Lite 收口说明、脱敏 provider 状态、usage 汇总、成本估算与路由矩阵 |
| `completed/v0.9.2-master-setting-workspace-lite.md` | v0.9.2 | MasterSetting Workspace Lite 收口说明、设定资产聚合、白名单轻编辑、前端最小写控件与边界 |
| `completed/v0.9.3-graph-memory-evaluation-spike.md` | v0.9.3 | Graph Memory Evaluation Spike 收口说明、触发报告、检索 probe、失败样例边界与下一步 |
| `completed/v0.9.4-advanced-runner-evaluation-spike.md` | v0.9.4 | Advanced Runner Evaluation Spike 收口说明、触发报告、runner probe、失败样例边界与下一步 |
| `completed/v1.0-beta-commercial-hardening-scope-a.md` | v1.0-beta | Commercial Hardening Scope-A 收口说明、商业化七域范围复核、本地优先边界与下一步 |
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

## 5. research/ 参考项目吸收

| 路径 | 作用 |
| --- | --- |
| `research/open-source-essence-absorption.md` | 记录 WenShape / webnovel-writer 的可吸收能力、已复制资产、许可证边界和明确不做项 |

## 6. 维护约定

- 新增仍在跟进的主线文档可留在 `docs/` 根部；已收口版本专项文档归档到 `completed/`，并在本文件登记。
- 新增论文原文放 `article/`，论文解读放 `article/reports/`，不要只放 PDF 不写报告。
- 新增参考项目分析放 `research/`，并写清“吸收什么 / 不做什么 / 是否复制资产 / 许可证边界”。
- `AGENTS.md` 和 `memory.md` 保持在根目录：前者是 Agent 入口规则，后者是当前事实收口。
- 完成版本后同步顺序建议为：`memory.md` -> `living-novel-engine-iteration-plan.md` -> 相关 PRD/UI spec/README -> `codex-handoff.md` -> 本文件。
