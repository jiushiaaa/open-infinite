# 未终章 产品迭代计划

> 用途：作为当前路线图入口，说明阶段状态、下一步原则和后续触发条件。完整历史实施清单已归档到 `completed/living-novel-engine-iteration-plan-legacy-2026-06-01.md`；最新事实以 `../memory.md` 为准。
> 品牌口径：产品名为“未终章”，英文名为 “Unfinale”；代码包名、CLI、artifact 与环境变量前缀仍沿用 LNE / `living_novel_engine`。
> 版本：2026-06-03，本地模型配置 UX、本地一键运行脚本、Runtime Preflight 至 Graph Memory Provider Spike Manual Mock Adapter Review MVP 已收口，共四十五刀。

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
| Runtime Preflight MVP | 第一刀已收口 | 后续增强自主迭代第一刀：创作前只读聚合导入、记忆、账本、别名、检索、续写起点、overlay、版权、保留策略、审计日志和 provider 状态。 |
| Projection Health MVP | 第二刀已收口 | 后续增强自主迭代第二刀：生成后只读聚合 branch/project 关键投影的成功、缺失或损坏状态。 |
| Reader Panel / Adversarial Revision Lab MVP | 第三刀已收口 | 后续增强自主迭代第三刀：deterministic/mockable 读者评审与修订 brief。 |
| Prompt Budget Pack MVP | 第四刀已收口 | 后续增强自主迭代第四刀：只读检索上下文预算包、去重、优先级压缩和 UI 解释。 |
| LLM Profile Assignment MVP | 第五刀已收口 | 后续增强自主迭代第五刀：设置页只读展示任务级模型画像、温度、预算和降级策略。 |
| Cards Workspace MVP | 第六刀已收口 | 后续增强自主迭代第六刀：项目工作台只读展示世界卡、角色卡、风格卡设定资产。 |
| OpenAPI / Typed Client MVP | 第七刀已收口 | 后续增强自主迭代第七刀：设置页只读展示本地 API 契约、OpenAPI skeleton 与 typed client 映射。 |
| Bundled Release Readiness MVP | 第八刀已收口 | 后续增强自主迭代第八刀：设置页只读展示本地发行与桌面打包准备度。 |
| Embedding / Vector Retrieval Readiness Probe MVP | 第九刀已收口 | 后续增强自主迭代第九刀：项目工作台只读展示 BM25、账本、别名、失败样本与向量检索触发证据。 |
| Embedding Evaluation Samples MVP | 第十刀已收口 | 后续增强自主迭代第十刀：项目工作台只读评估失败样本、BM25 命中与 mock semantic oracle 差异。 |
| Retrieval Failure Sample Authoring MVP | 第十一刀已收口 | 后续增强自主迭代第十一刀：项目工作台可安全追加本地检索失败样本，形成 embedding 接入前的可复跑证据。 |
| Memory CLI MVP | 第十二刀已收口 | 后续增强自主迭代第十二刀：命令行追加、复跑和检查失败样本，服务无人值守与批处理评测。 |
| Retrieval Sample Export Pack MVP | 第十三刀已收口 | 后续增强自主迭代第十三刀：service/API/UI/CLI 只读导出失败样本 Markdown/manifest，服务评测集迁移和人工复盘。 |
| Embedding Mock Evaluation Report MVP | 第十四刀已收口 | 后续增强自主迭代第十四刀：service/API/UI/CLI 只读生成 BM25 vs mock semantic oracle 对照报告与 candidate gate。 |
| Retrieval Sample Replay Report MVP | 第十五刀已收口 | 后续增强自主迭代第十五刀：service/API/UI/CLI 只读复跑失败样本，输出当前检索 case report。 |
| Retrieval Sample Migration Pack MVP | 第十六刀已收口 | 后续增强自主迭代第十六刀：service/API/UI/CLI 只读整理稳定 retrieval eval records 与 JSON manifest。 |
| Cross Project Retrieval Samples Index MVP | 第十七刀已收口 | 后续增强自主迭代第十七刀：service/API/CLI/设置页只读汇总跨项目 retrieval eval records、project rows 与 index gate。 |
| Retrieval Samples Trend Snapshot MVP | 第十八刀已收口 | 后续增强自主迭代第十八刀：service/API/CLI/设置页只读输出跨项目样本覆盖、词面缺口、空样本项目、blocked 项目和重型检索触发暂缓信号。 |
| GraphRAG / Zep Trigger Evidence MVP | 第十九刀已收口 | 后续增强自主迭代第十九刀：service/API/CLI/项目工作台只读聚合图记忆触发、retrieval probe、样本趋势和关系/因果/状态证据。 |
| Graph Memory Spike Design Pack MVP | 第二十刀已收口 | 后续增强自主迭代第二十刀：service/API/CLI/项目工作台只读展示 GraphRAG/Zep/Temporal Memory 设计包、验收门槛和 no-go 条件。 |
| Graph Memory Shadow Compare Pack MVP | 第二十一刀已收口 | 后续增强自主迭代第二十一刀：service/API/CLI/项目工作台只读展示 GraphRAG/Zep/Temporal Memory 候选层 shadow 对照、样本案例、验收结果和 no-go 条件。 |
| Graph Memory Shadow Case Matrix MVP | 第二十二刀已收口 | 后续增强自主迭代第二十二刀：service/API/CLI/项目工作台只读展示 eval case x 候选层矩阵、本地证据、缺口、收益/风险和 no-go 条件。 |
| Graph Memory Provider Boundary Matrix MVP | 第二十三刀已收口 | 后续增强自主迭代第二十三刀：service/API/CLI/项目工作台只读展示 GraphRAG/Zep/Temporal Memory 的 opt-in provider 边界、成本、隐私、回滚和验收要求。 |
| Graph Memory Offline Shadow Replay Plan MVP | 第二十四刀已收口 | 后续增强自主迭代第二十四刀：service/API/CLI/项目工作台只读展示 provider plans、replay cases、固定 fixture 步骤、验收、回滚、人工复核和 no-go 条件。 |
| Graph Memory Offline Shadow Replay Report MVP | 第二十五刀已收口 | 后续增强自主迭代第二十五刀：service/API/CLI/项目工作台只读展示 mock replay 结果、候选收益、失败降级和人工复核结论。 |
| Graph Memory Provider Spike Fixture Pack MVP | 第二十六刀已收口 | 后续增强自主迭代第二十六刀：service/API/CLI/项目工作台只读展示单 provider、单项目、单 fixture 的 dry-run 前置包、成本/隐私/回滚 checklist、人工验收和 no-go 条件。 |
| Graph Memory Provider Spike Readiness Gate MVP | 第二十七刀已收口 | 后续增强自主迭代第二十七刀：service/API/CLI/项目工作台只读展示 provider spike readiness gate、人工复核项、no-go 和暂缓原因。 |
| Graph Memory Provider Spike Runbook MVP | 第二十八刀已收口 | 后续增强自主迭代第二十八刀：service/API/CLI/项目工作台只读展示人工 opt-in dry-run SOP、验收/回滚/暂停条件和证据引用。 |
| Graph Memory Provider Spike Dry-run Result Template MVP | 第二十九刀已收口 | 后续增强自主迭代第二十九刀：service/API/CLI/项目工作台只读展示人工 dry-run 结果记录模板、对比字段、暂停/升级判定和证据引用。 |
| Graph Memory Provider Spike Mock Result Report MVP | 第三十刀已收口 | 后续增强自主迭代第三十刀：service/API/CLI/项目工作台只读展示 mock 填充结果、收益/风险判定、人工复核摘要和暂停/升级建议。 |
| Graph Memory Provider Spike Review Gate MVP | 第三十一刀已收口 | 后续增强自主迭代第三十一刀：service/API/CLI/项目工作台只读展示人工复核 gate、provider review rows、no-go 摘要和下一步分流。 |
| Graph Memory Provider Spike Manual Approval Pack MVP | 第三十二刀已收口 | 后续增强自主迭代第三十二刀：service/API/CLI/项目工作台只读展示人工审批包、风险签收、回滚确认、opt-in 材料和真实 provider 继续禁止边界。 |
| Graph Memory Provider Spike Manual Approval Evidence Checklist MVP | 第三十三刀已收口 | 后续增强自主迭代第三十三刀：service/API/CLI/项目工作台只读展示审批证据核对表、待签收项、材料缺口、回滚材料缺口和真实 provider 继续禁止边界。 |
| Graph Memory Provider Spike Opt-in Evidence Snapshot MVP | 第三十四刀已收口 | 后续增强自主迭代第三十四刀：service/API/CLI/项目工作台只读展示 opt-in 证据快照、阻塞项摘要、签收待办和真实 provider 继续禁止边界。 |
| Graph Memory Provider Spike Opt-in No-go Matrix MVP | 第三十五刀已收口 | 后续增强自主迭代第三十五刀：service/API/CLI/项目工作台只读展示 no-go 分类矩阵、阻塞类别、签收/材料/回滚缺口分布和真实 provider 继续禁止边界。 |
| Graph Memory Provider Spike Opt-in Operator Checklist MVP | 第三十六刀已收口 | 后续增强自主迭代第三十六刀：service/API/CLI/项目工作台只读展示人工操作 checklist、暂停/升级判断、证据核对顺序和真实 provider 继续禁止边界。 |
| Graph Memory Provider Spike Opt-in Review Packet MVP | 第三十七刀已收口 | 后续增强自主迭代第三十七刀：service/API/CLI/项目工作台只读展示人工复核包、证据顺序、暂停材料、升级材料和真实 provider 继续禁止边界。 |
| Graph Memory Provider Spike Opt-in Decision Ledger Preview MVP | 第三十八刀已收口 | 后续增强自主迭代第三十八刀：service/API/CLI/项目工作台只读展示决策账本预览、待签收字段占位、阻塞行和真实 provider 继续禁止边界。 |
| Graph Memory Provider Spike Opt-in Final Readiness Summary MVP | 第三十九刀已收口 | 后续增强自主迭代第三十九刀：service/API/CLI/项目工作台只读展示最终就绪摘要、未签收字段、阻塞原因和真实 provider 继续禁止边界。 |
| Graph Memory Provider Spike Opt-in Human Signoff Schema Draft MVP | 第四十刀已收口 | 后续增强自主迭代第四十刀：service/API/CLI/项目工作台只读展示人工签收 schema 草案、字段定义、校验规则和真实 provider 继续禁止边界。 |
| Graph Memory Provider Spike Opt-in Config Draft MVP | 第四十一刀已收口 | 后续增强自主迭代第四十一刀：service/API/CLI/项目工作台只读展示本地 opt-in 配置草案、字段映射和 adapter 边界；不保存配置、不读取明文 Key。 |
| Graph Memory Provider Spike Local Provider Contract / Adapter Boundary MVP | 第四十二刀已收口 | 后续增强自主迭代第四十二刀：service/API/CLI/项目工作台只读展示本地 provider contract、adapter boundary 和 mock-only 方法约束。 |
| Graph Memory Provider Spike Single Fixture Dry-run Harness MVP | 第四十三刀已收口 | 后续增强自主迭代第四十三刀：service/API/CLI/项目工作台只读展示单 fixture dry-run harness；只允许 local mock，不保存 dry-run 结果。 |
| Graph Memory Provider Spike Mock-compatible Adapter MVP | 第四十四刀已收口 | 后续增强自主迭代第四十四刀：service/API/CLI/项目工作台只读展示 mock-compatible adapter 规格、方法要求和 validation cases；不创建真实 adapter。 |
| Graph Memory Provider Spike Manual Mock Adapter Review MVP | 第四十五刀已收口 | 后续增强自主迭代第四十五刀：service/API/CLI/项目工作台只读展示 mock adapter 人工复核包、合规检查、阻断项和本刀后暂停建议；不保存人工结论、不创建真实 adapter。 |

当前验证基线：后端 `872 passed`；前端 `cd engine/ui && pnpm run build` 通过。

## 3. 当前自主迭代点

用户已授权进入后续增强自主迭代。真实用户模型配置 UI、本地一键运行脚本、Runtime Preflight MVP 至 Graph Memory Provider Spike Manual Mock Adapter Review MVP 共四十五刀已完成。本刀后按用户要求暂停继续开发；恢复时先确认用户选择，不自动进入真实 provider。

本地体验稳定后，发行路径仍由用户选择进入：

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
- 产品入口边界：前端是产品入口，API 是能力层，CLI 是工程外壳；用户级功能优先通过 Web UI + API 完成，CLI 只服务开发者、本地服务启动、自动化验收、批处理和无人值守复跑。

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
| Chapter Commit / Projection Health | Projection Health MVP 已补只读报告/API/UI；真正 Chapter Commit 写后真源、人工确认、回滚和 read-model 重建仍后置。 |
| Reader Panel / Adversarial Revision Lab 深化 | deterministic/mockable MVP 已有；自动改写、Elo 对比、voice fingerprint 仍未做。 |
| Prompt Budget Pack 深化 | 只读/additive MVP 已有；真正接入 prompt 编排或 reranker 仍后置。 |
| LLM Profile Assignment 深化 | 只读/additive MVP 已有；opt-in profile 保存、版本化和真实模型实验仍后置。 |
| Cards Workspace 深化 | 只读/additive MVP 已有；独立卡片 artifact、版本化和批量编辑仍后置。 |
| OpenAPI / Typed Client 深化 | 只读 API contract、OpenAPI skeleton 与前端 typed client 映射已有；字段级 schema、自动生成 client 和外部集成契约仍后置。 |
| Bundled Release / Desktop Packaging 深化 | 本地脚本和只读发行准备清单已有；安装包、内置 runtime、桌面壳 readiness 尚未做 | 等本地试用稳定后再做 opt-in packager spike。 |
| Embedding / Vector Retrieval Readiness Probe | 已有只读 service/API/UI，量化 BM25、canon ledger、aliases、失败样本与项目规模压力 | 已接续完成样本评估；后续补采集/校验入口。 |
| Embedding Evaluation Samples | 已有只读 service/API/UI，对 `retrieval_failure_samples.jsonl` 做 BM25 vs mock semantic oracle 对照 | 已接续完成工作台样本采集；继续做 CLI/批量复跑/导出。 |
| Retrieval Failure Sample Authoring | 已有 service/API/UI，可安全追加本地失败样本并刷新样本评估 | 已接续完成 Memory CLI；继续做样本导出包或报告化。 |
| Memory CLI | 已有 `lne memory add-sample` / `lne memory samples`，可追加、复跑、JSON 输出和 require-candidate 检查 | 已接续完成样本 export pack；继续做 mock evaluation report 或批量 replay report，不接真实 provider。 |
| Retrieval Sample Export Pack | 已有只读 service/API/UI/CLI，可输出 Markdown `content_md` 与 JSON manifest | 已接续完成 mock evaluation report；继续做批量 replay 报告或样本迁移包，不接真实 provider。 |
| Embedding Mock Evaluation Report | 已有只读 service/API/UI/CLI，可输出 candidate gate、分桶样本和 Markdown report | 已接续完成 replay report；继续做样本迁移包或跨项目样本汇总，不接真实 provider。 |
| Retrieval Sample Replay Report | 已有只读 service/API/UI/CLI，可输出当前检索 case report | 已接续完成 migration pack；继续做跨项目样本索引或长期趋势对比，不接真实 provider。 |
| Retrieval Sample Migration Pack | 已有只读 service/API/UI/CLI，可输出稳定 eval records 与 JSON manifest | 已接续完成跨项目样本索引，不接真实 provider。 |
| Cross Project Retrieval Samples Index | 已有只读 service/API/CLI/设置页，可汇总跨项目 migration pack 与 eval records | 已接续完成趋势快照，不接真实 provider。 |
| Retrieval Samples Trend Snapshot | 已有只读 service/API/CLI/设置页，可输出样本覆盖、词面缺口、空样本项目和重型检索暂缓信号 | 已接续完成 GraphRAG/Zep 触发证据，不接真实 provider。 |
| GraphRAG / Zep Trigger Evidence | 已有只读 service/API/CLI/项目工作台，可聚合图记忆触发、retrieval probe、趋势样本和关系/因果/状态证据 | 已接续完成 Graph Memory Spike Design Pack，不接真实 provider。 |
| Graph Memory Spike Design Pack | 已有只读 service/API/CLI/项目工作台，可展示候选层、试验输入、验收门槛、回退策略和 no-go 条件 | 已接续完成 Graph Memory Shadow Compare Pack，不接真实 provider。 |
| Graph Memory Shadow Compare Pack | 已有只读 service/API/CLI/项目工作台，可展示候选层 shadow 对照、样本案例、验收结果和 no-go 条件 | 已接续完成 Graph Memory Shadow Case Matrix，不接真实 provider。 |
| Graph Memory Shadow Case Matrix | 已有只读 service/API/CLI/项目工作台，可展示 eval case x 候选层矩阵、本地证据、缺口、收益/风险和 no-go 条件 | 已接续完成 Graph Memory Provider Boundary Matrix，不接真实 provider。 |
| Graph Memory Provider Boundary Matrix | 已有只读 service/API/CLI/项目工作台，可展示 provider opt-in 边界、成本、隐私、数据同步、回滚、测试、验收和失败降级 | 已接续完成 Graph Memory Offline Shadow Replay Plan 与 Report，不接真实 provider。 |
| Graph Memory Offline Shadow Replay Plan / Report / Fixture Pack / Readiness Gate / Runbook / Result Template / Mock Result Report / Review Gate / Manual Approval Pack / Approval Evidence Checklist / Opt-in Evidence Snapshot / No-go Matrix / Operator Checklist / Review Packet / Decision Ledger Preview / Final Readiness Summary / Human Signoff Schema / Config Draft / Local Contract / Dry-run Harness / Mock-compatible Adapter / Manual Mock Adapter Review | 已有只读 service/API/CLI/项目工作台，可展示 provider plans、replay cases、mock result、候选收益、失败降级、人工复核结论、单 provider dry-run fixture 前置包、readiness gate、人工 opt-in dry-run SOP、结果记录模板、mock 填充报告、人工复核 gate、人工审批包、审批证据核对表、opt-in 证据快照、no-go 分类矩阵、人工操作 checklist、人工复核包、决策账本预览、最终就绪摘要、签收 schema、配置草案、本地 contract、dry-run harness、mock adapter 规格和 mock adapter 人工复核包 | 已按用户要求暂停继续开发；恢复时先确认下一步，继续不接真实 provider。 |
| 云端多用户、对象存储、认证、计费 | 本地试用稳定并明确发行路径后再拆。 |
| 向量库 / embedding / GraphRAG | 只有 BM25/ledger/alias probe 与向量就绪探针证明不足时再评估。 |
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
- 后续新增普通用户能力时，先补 Web UI + API；CLI 只能作为薄封装用于工程、自动化或批处理，不应成为唯一可用入口。
