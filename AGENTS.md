# 未终章 Agent Instructions

本文件是 Codex / 其他代码 Agent 进入 `D:\AI\open-infinite` 时的项目级约定。若系统级指令与本文件冲突，以系统级指令为准；若项目文档互相冲突，以 `memory.md` 的最新收口状态为准。

## 用户背景

用户以个人开发者身份探索 AI 叙事项目。当前仓库 `D:\AI\open-infinite` 的核心项目是 **未终章（Unfinale）**，代码集中在 `engine/`。技术缩写、Python 包、CLI 和环境变量前缀仍沿用 LNE / `living_novel_engine`，不要在代码层面机械改名。

默认使用中文沟通。用户偏好：先读项目事实和现有代码，再做判断；不要靠聊天摘要臆测；实现要闭环到测试、文档同步和 `docs/project-changelog.md` 历史记录。

## 会话开始必读

只要任务与未终章、`engine/`、版本路线、产品 UI、API、测试或文档有关，开始动手前先阅读并对齐：

- `memory.md`
- `docs/unfinale-world-sandbox-remodel-prd.md`
- `docs/unfinale-product-vision-correction-draft.md`
- `docs/unfinale-ai-development-alignment-checklist.md`
- `docs/living-novel-engine-iteration-plan.md`
- `docs/productization-phase-map.md`
- `docs/living-novel-engine-prd.md`
- `docs/completed/v0.7-product-web-app-ui-spec.md`
- `engine/README.md`
- 如存在接力任务，再读 `docs/codex-handoff.md`

读取重点：

- `memory.md`：当前状态、测试基线、已知缺口、文档索引
- `docs/unfinale-world-sandbox-remodel-prd.md`：当前世界沙盘改造 PRD，说明现有代码如何接入《天命书》、沙盘轮次、主观记忆链、世界自演、多视角活体小说和作者采纳台
- `docs/unfinale-product-vision-correction-draft.md`：产品愿景纠偏草稿，记录当前讨论定稿和 UI 原型方向
- `docs/unfinale-ai-development-alignment-checklist.md`：后续 AI 开工前自检，避免把旧工程化面板、provider spike 或检索评测当成默认下一步
- `docs/project-changelog.md`：完整历史变更日志；每完成一个独立切片都必须追加本文件末尾，入口阅读时仅在追溯版本过程或补历史记录时读取，避免新会话入口过重
- `docs/living-novel-engine-iteration-plan.md`：版本路线和下一刀范围
- `docs/productization-phase-map.md`：技术 MVP、产品化 MVP、长篇产品化、商业化加固的阶段归类
- `docs/living-novel-engine-prd.md`：产品定位和用户流程
- `docs/completed/v0.7-product-web-app-ui-spec.md`：已收口的 Web UI 风格和交互边界
- `engine/README.md`：CLI/API/输出结构/验收命令

事实优先级：

1. `memory.md`
2. `docs/unfinale-world-sandbox-remodel-prd.md`
3. `docs/unfinale-product-vision-correction-draft.md`
4. `docs/unfinale-ai-development-alignment-checklist.md`
5. `docs/living-novel-engine-iteration-plan.md`
6. `engine/README.md`
7. `docs/living-novel-engine-prd.md`
8. 聊天摘要

## 当前纠偏主线（最高优先级）

截至 2026-06-03，用户已经明确：项目后续要从工程化支撑层拉回最初愿望，即 **Living Novel Engine / 小说世界沙盘**。

后续默认主线是：

```text
导入故事世界
  -> AI 预抽并确认《天命书》
  -> 多 Agent 世界沙盘轮次
  -> 每个角色写入独立主观记忆链
  -> 世界状态、因果债、锚点和候选天命承载者变化
  -> 世界自演生成检查点
  -> 读者自由干预经干预编译器投放
  -> 多视角活体小说渲染
  -> 作者模式采纳或导出沙盘涌现剧情
```

主导航已定稿：

```text
世界书架
  -> 某个故事世界
      -> 天命书
      -> 世界沙盘
      -> 世界正史卷
      -> 主锚点卷
      -> 角色个人卷
      -> 势力卷
      -> 事件多视角
      -> 世界线
      -> 检查点
      -> 作者采纳台
```

不要把一级导航设计成“沙盘 / 阅读 / 干预 / 作者”四大工作区；这些只是同一个世界里的场景能力。主导航按世界组织，功能按场景浮现。

后续每一刀必须服务至少一项：

```text
世界会运行。
角色会自主。
角色会记得。
干预有后果。
角色可能反抗。
世界会代偿。
章节来自世界演化。
```

以下方向默认降级为支撑层，除非用户明确要求，不继续扩张：

```text
GraphRAG / Zep
provider spike
真实向量检索评测
OpenAPI / typed client 面板
发行准备
商业化 / 计费 / 认证 / 对象存储
纯工程健康报告
```

## 当前硬约束

- 不改 `run_scene` 默认行为，除非用户明确要求进入 runner 重构。
- 不破坏既有 artifact 契约：`chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 新增 artifact、API 字段、前端读取字段默认 additive。
- 后端 HTTP-facing identifier 必须走安全校验，不能把未经校验的 slug/run_id/branch_id 拼到文件路径。
- 失败要降级为明确的 400/404/409 或前端空态，不白屏、不 500。
- 前端产品文案默认中文；不要出现英文占位词。
- 视觉风格保持 v0.7 的古风纸面、克制系统感，不做营销落地页。
- 产品入口边界：前端是产品入口，API 是能力层，CLI 是工程外壳。导入、配置、创作、干预、评审、导出、样本采集、Graph Memory 证据查看等用户级能力必须优先通过 Web UI + API 完成；CLI 只服务开发者、本地服务启动、自动化验收、批处理、JSON 输出和无人值守复跑，不承载独立业务规则。
- `Reference_projects/` 与外部项目只作参考，不直接复制源码或引入依赖，除非用户明确要求。
- 不泄漏 API Key；设置页或日志只能展示脱敏尾号。
- 用户在 `.env` 中可能已经配置真实 `SEEDREAM_API_KEY` / `LLM_API_KEY`。测试要隔离环境，避免误打真实外网。

## 当前版本状态

截至 2026-06-03，当前收口状态以 `memory.md` 为准；本文件只保留 Agent 决策所需的高层摘要：

| 阶段 | 当前状态 |
| --- | --- |
| v0.7 | 短中篇产品化 Web App、Agent Interaction、Visual Asset、Baseline/Canon Replay、Worldline Judge 均已收口 |
| v0.8 | 长篇导入、分层记忆、正史账本、混合检索、审计、ActDirector、Narrator diagnostics、Dynamic Action Registry、Emergence Mining、Entity Alias、Runtime Memory Consumption、Artifact Panel、Long Upload Productization 均已收口 |
| v0.9.0-alpha | Long Novel Creation Loop 已整体收口，覆盖续写、世界线选择、审计、章节/合集导出、closeout API/CLI/record |
| v0.9.1-v0.9.4 | Provider/Cost、MasterSetting Workspace、Graph Memory Evaluation Spike、Advanced Runner Evaluation Spike 均已收口 |
| v1.0-beta | 本地优先商业化边界从 Scope-A 到 Billing Adapter Boundary-X 均已收口 |
| v1.0-local | Model Configuration UX 与 Local Run Scripts 已收口 |
| Runtime Preflight MVP | 后续增强第一刀已收口，创作前只读聚合关键运行证据 |
| Projection Health MVP | 后续增强第二刀已收口，生成后只读聚合分支投影健康证据 |
| Reader Panel / Adversarial Revision Lab MVP | 后续增强第三刀已收口，确定性读者评审与修订 brief |
| Prompt Budget Pack MVP | 后续增强第四刀已收口，检索上下文预算包与压缩解释 |
| LLM Profile Assignment MVP | 后续增强第五刀已收口，设置页只读展示任务级模型画像、温度、预算和降级策略 |
| Cards Workspace MVP | 后续增强第六刀已收口，项目工作台只读展示世界卡、角色卡、风格卡设定资产 |
| OpenAPI / Typed Client MVP | 后续增强第七刀已收口，设置页只读展示本地 API 契约、OpenAPI skeleton 与 typed client 映射 |
| Bundled Release Readiness MVP | 后续增强第八刀已收口，设置页只读展示本地发行与桌面打包准备度 |
| Embedding / Vector Retrieval Readiness Probe MVP | 后续增强第九刀已收口，项目工作台只读展示 BM25/账本/别名召回压力和向量检索触发证据 |
| Embedding Evaluation Samples MVP | 后续增强第十刀已收口，项目工作台只读评估失败样本、BM25 命中与 mock semantic oracle 差异 |
| Retrieval Failure Sample Authoring MVP | 后续增强第十一刀已收口，项目工作台可安全追加本地检索失败样本并刷新 embedding 样本评估 |
| Memory CLI MVP | 后续增强第十二刀已收口，`lne memory` 可追加和复跑本地失败样本，便于批量整理评测证据 |
| Retrieval Sample Export Pack MVP | 后续增强第十三刀已收口，service/API/UI/CLI 可只读导出失败样本 Markdown/manifest |
| Embedding Mock Evaluation Report MVP | 后续增强第十四刀已收口，service/API/UI/CLI 可生成 BM25 vs mock semantic oracle 对照报告 |
| Retrieval Sample Replay Report MVP | 后续增强第十五刀已收口，service/API/UI/CLI 可只读复跑失败样本并输出 case report |
| Retrieval Sample Migration Pack MVP | 后续增强第十六刀已收口，service/API/UI/CLI 可只读整理稳定 retrieval eval records 与 manifest |
| Cross Project Retrieval Samples Index MVP | 后续增强第十七刀已收口，service/API/CLI/设置页可只读汇总跨项目 retrieval eval records |
| Retrieval Samples Trend Snapshot MVP | 后续增强第十八刀已收口，service/API/CLI/设置页可只读输出跨项目样本覆盖、词面缺口、空样本项目和重型检索触发暂缓信号 |
| GraphRAG / Zep Trigger Evidence MVP | 后续增强第十九刀已收口，service/API/CLI/项目工作台可只读聚合图记忆触发、retrieval probe、样本趋势和关系/因果/状态证据 |
| Graph Memory Spike Design Pack MVP | 后续增强第二十刀已收口，service/API/CLI/项目工作台可只读展示 GraphRAG/Zep/Temporal Memory 设计包、验收门槛和 no-go 条件 |
| Graph Memory Shadow Compare Pack MVP | 后续增强第二十一刀已收口，service/API/CLI/项目工作台可只读展示 GraphRAG/Zep/Temporal Memory 候选层 shadow 对照、样本案例、验收结果和 no-go 条件 |
| Graph Memory Shadow Case Matrix MVP | 后续增强第二十二刀已收口，service/API/CLI/项目工作台可只读展示 eval case x 候选层矩阵、本地证据、缺口、收益/风险和 no-go 条件 |
| Graph Memory Provider Boundary Matrix MVP | 后续增强第二十三刀已收口，service/API/CLI/项目工作台可只读展示 GraphRAG/Zep/Temporal Memory 的 opt-in provider 边界、成本、隐私、回滚和验收要求 |
| Graph Memory Offline Shadow Replay Plan MVP | 后续增强第二十四刀已收口，service/API/CLI/项目工作台可只读展示高收益 case 的离线 replay 输入、验收、回滚、人工复核和 no-go 条件 |
| Graph Memory Offline Shadow Replay Report MVP | 后续增强第二十五刀已收口，service/API/CLI/项目工作台可只读展示 mock replay 结果、候选收益、失败降级和人工复核结论 |
| Graph Memory Provider Spike Fixture Pack MVP | 后续增强第二十六刀已收口，service/API/CLI/项目工作台可只读展示单 provider、单项目、单 fixture 的 dry-run 前置包、成本/隐私/回滚 checklist、人工验收和 no-go 条件 |
| Graph Memory Provider Spike Readiness Gate MVP | 后续增强第二十七刀已收口，service/API/CLI/项目工作台可只读展示 provider spike readiness gate、人工复核项、no-go 和暂缓原因 |
| Graph Memory Provider Spike Runbook MVP | 后续增强第二十八刀已收口，service/API/CLI/项目工作台可只读展示人工 opt-in dry-run SOP、验收/回滚/暂停条件和证据引用 |
| Graph Memory Provider Spike Dry-run Result Template MVP | 后续增强第二十九刀已收口，service/API/CLI/项目工作台可只读展示人工 dry-run 结果记录模板、对比字段、暂停/升级判定和证据引用 |
| Graph Memory Provider Spike Mock Result Report MVP | 后续增强第三十刀已收口，service/API/CLI/项目工作台可只读展示 mock 填充结果、收益/风险判定、人工复核摘要和暂停/升级建议 |
| Graph Memory Provider Spike Review Gate MVP | 后续增强第三十一刀已收口，service/API/CLI/项目工作台可只读展示人工复核 gate、provider review rows、no-go 摘要和下一步分流 |
| Graph Memory Provider Spike Manual Approval Pack MVP | 后续增强第三十二刀已收口，service/API/CLI/项目工作台可只读展示人工审批包、风险签收、回滚确认、opt-in 材料和真实 provider 继续禁止边界 |
| Graph Memory Provider Spike Manual Approval Evidence Checklist MVP | 后续增强第三十三刀已收口，service/API/CLI/项目工作台可只读展示审批证据核对表、待签收项、材料缺口、回滚材料缺口和真实 provider 继续禁止边界 |
| Graph Memory Provider Spike Opt-in Evidence Snapshot MVP | 后续增强第三十四刀已收口，service/API/CLI/项目工作台可只读展示 opt-in 证据快照、阻塞项摘要、签收待办和真实 provider 继续禁止边界 |
| Graph Memory Provider Spike Opt-in No-go Matrix MVP | 后续增强第三十五刀已收口，service/API/CLI/项目工作台可只读展示 no-go 分类矩阵、阻塞类别、签收/材料/回滚缺口分布和真实 provider 继续禁止边界 |
| Graph Memory Provider Spike Opt-in Operator Checklist MVP | 后续增强第三十六刀已收口，service/API/CLI/项目工作台可只读展示人工操作 checklist、暂停/升级判断、证据核对顺序和真实 provider 继续禁止边界 |
| Graph Memory Provider Spike Opt-in Review Packet MVP | 后续增强第三十七刀已收口，service/API/CLI/项目工作台可只读展示人工复核包、证据顺序、暂停材料、升级材料和真实 provider 继续禁止边界 |
| Graph Memory Provider Spike Opt-in Decision Ledger Preview MVP | 后续增强第三十八刀已收口，service/API/CLI/项目工作台可只读展示决策账本预览、待签收字段占位、阻塞行和真实 provider 继续禁止边界 |
| Graph Memory Provider Spike Opt-in Final Readiness Summary MVP | 后续增强第三十九刀已收口，service/API/CLI/项目工作台可只读展示最终就绪摘要、未签收字段、阻塞原因和真实 provider 继续禁止边界 |
| Graph Memory Provider Spike Opt-in Human Signoff Schema Draft MVP | 后续增强第四十刀已收口，service/API/CLI/项目工作台可只读展示人工签收 schema 草案、字段定义、校验规则和真实 provider 继续禁止边界 |
| Graph Memory Provider Spike Opt-in Config Draft MVP | 后续增强第四十一刀已收口，service/API/CLI/项目工作台可只读展示本地 opt-in 配置草案、字段映射和 adapter 边界 |
| Graph Memory Provider Spike Local Provider Contract / Adapter Boundary MVP | 后续增强第四十二刀已收口，service/API/CLI/项目工作台可只读展示本地 provider contract、adapter boundary 和 mock-only 方法约束 |
| Graph Memory Provider Spike Single Fixture Dry-run Harness MVP | 后续增强第四十三刀已收口，service/API/CLI/项目工作台可只读展示单 fixture dry-run harness |
| Graph Memory Provider Spike Mock-compatible Adapter MVP | 后续增强第四十四刀已收口，service/API/CLI/项目工作台可只读展示 mock-compatible adapter 规格、方法要求和 validation cases |
| Graph Memory Provider Spike Manual Mock Adapter Review MVP | 后续增强第四十五刀已收口，service/API/CLI/项目工作台可只读展示 mock adapter 人工复核包、合规检查、阻断项和本刀后暂停建议 |
| Retrieval Provider Real Connectivity MVP | 已收口，百炼 `text-embedding-v3`、Zilliz Cloud、百炼 `gte-rerank-v2` 的脱敏配置、mock smoke 和真实 smoke 可用 |
| Vector Retrieval Pipeline MVP | 已收口，API/UI 可显式写入 Zilliz collection、执行百炼 embedding + Zilliz + 百炼 rerank 检索预览；运行时需 `LNE_RETRIEVAL_STRATEGY=hybrid_vector` opt-in |

当前验证基线：后端 `cd engine && python -m pytest -q` 为 `872 passed`；前端 `cd engine/ui && pnpm run build` 通过。真实检索 smoke 已确认 `v090-alpha-proof` 可写入 `unfinale_memory` 20 条，并以 `hybrid_vector_rerank` 模式返回 5 条检索结果，embedding、Zilliz 和 reranker 均实际参与且不返回明文密钥。

官方下一步：进入 **World Sandbox Loop / 世界沙盘改造**。真实检索 provider 和向量检索 Pipeline 已显式接入，但当前只作为支撑层；恢复开发时不要继续默认评估 hybrid vector、GraphRAG、Zep 或 provider spike，而应优先做《天命书》、角色主观记忆链、沙盘轮次、世界自演、多视角活体小说和作者采纳台。

### 当前边界备忘

- 长篇导入已写入 `source_raw/`、`import_report.json`、`memory/`、`canon_ledger.jsonl`、`consistency_report.json`。
- `canon_ledger`、entity aliases 与 runtime memory 已进入只读检索/展示链路；正史 holdout 通过 `canon/visibility_manifest.json` 隔离。
- 干预 run 会写 `act_director_plan.json`、`narrative_diagnostics.json`、`dynamic_action_registry.yaml`、`emergence_nodes.json`，但这些机制产物暂不自动驱动 runner。
- 状态执行 overlay 可显式 apply/rollback，但不覆盖 `state_snapshot.json`，也不自动喂回下一轮 runner。
- 设置页已有脱敏 provider 状态、usage、route matrix、模型配置、任务模型画像、本地 API 契约、发行准备、跨项目样本索引、样本趋势快照、本地运行脚本和检索增强 provider 状态；项目工作台已有运行前体检、设定卡片、向量检索就绪探针、真实向量检索、embedding 样本评估、失败样本采集、GraphRAG/Zep 触发证据、Graph 记忆设计包、Graph 记忆 Shadow 对照、Graph 记忆 Case 矩阵、Graph 记忆 Provider 边界、Graph 记忆离线 replay 计划/报告、Provider Spike 前置包、就绪门禁、Runbook、结果模板、Mock 结果报告、复核门禁、人工审批包、审批证据核对表、opt-in 证据、no-go 矩阵、operator checklist、review packet、decision ledger preview、final readiness summary、human signoff schema draft、config draft、local provider contract、single fixture dry-run harness、mock-compatible adapter 和 manual mock adapter review；分支右栏已有投影健康、读者评审和上下文包；不读取或打印明文密钥。
- 仍未做：云端多用户持久队列、真实对象存储 adapter、GraphRAG/Zep、hybrid vector 默认替换 BM25、overlay 自动消费、运行后审计写入正史账本。
- v1.0-beta 后续不默认接 Zep / 图数据库 / OASIS / CAMEL / LangGraph；这些按 v0.9.3 / v0.9.4 的触发式 spike 处理。
- `WorkspacePage.tsx` 已承载过多项目工作台和工程支撑面板；后续不要继续往里面堆 Graph/provider/报告 UI，应按 `docs/unfinale-world-sandbox-remodel-prd.md` 拆出世界内部卷宗壳和具体页面。

## 资料索引

- 已完成的 PRD、UI spec 及版本专项文档存储在 `D:\AI\open-infinite\docs\completed`。
- 参考论文 PDF 与论文解读报告存储在 `D:\AI\open-infinite\docs\article`，其中报告在 `D:\AI\open-infinite\docs\article\reports`。
- 参考开源项目存储在 `D:\AI\open-infinite\Reference_projects`，仅作设计参考和取舍分析，默认不直接复制源码、不引入依赖。
- `docs` 资料导航见 `D:\AI\open-infinite\docs\index.md`，用于快速定位 PRD、专项版本文档、论文报告和研究资料。
- 完整历史变更日志见 `D:\AI\open-infinite\docs\project-changelog.md`，每完成独立切片必须追加；入口阅读时仅在追溯过程或补历史记录时打开。
- 当前主 PRD 入口是 `D:\AI\open-infinite\docs\living-novel-engine-prd.md`；专项 PRD、UI spec 和历史版本说明放在 `docs\completed`。
- v0.1-v0.8 历史审计快照见 `D:\AI\open-infinite\docs\completed\v0.1-to-v0.8-version-audit.md`；该文档不承担当前待办来源。

## 开发流程

默认流程：

1. 读上述文档和相关代码。
2. 用现有模式实现，保持改动局部。
3. 补 service / API / 前端类型和 UI 测试，测试规模随风险调整。
4. 跑验证命令。
5. 同步 `memory.md` 当前状态、相关路线/README/PRD，并且每完成一个独立切片都必须把历史记录追加到 `docs/project-changelog.md` 末尾；不要等多刀总收口再补。

常用验证：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

Windows 注意：

- `rg` 若不可用或被系统拦截，用 `Get-ChildItem` / `Select-String` / `Get-Content`。
- PowerShell 没有原生 `tail` / `printf`，不要把 Linux shell 命令硬套过来。

## Cursor 迁移说明

`.cursor/rules/project-memory.mdc` 的核心规则已迁移到本文件和 `docs/codex-handoff.md`。`.cursor/skills/` 里多数是通用 Claude/Cursor 技能包；在 Codex 中优先使用已安装的 Codex skills/plugins：

- 前端：Build Web Apps / Vercel 相关 skills
- 文档：Documents / Presentations / Spreadsheets
- OpenAI：OpenAI Developers
- 方法论：Superpowers

不要把 `.cursor/skills/` 整包复制进 Codex 上下文；需要某个具体工作流时，再按 `docs/codex-migration-guide.md` 选择性迁移。
