# Codex Handoff — 未终章

> 用途：新开 Codex 窗口时的最小接力包。当前事实以 `../memory.md` 为准；完整历史变更见 `project-changelog.md`；旧版长接力稿已归档到 `completed/codex-handoff-legacy-2026-06-01.md`。

## 新窗口第一条消息建议

```text
请先阅读并对齐：
- AGENTS.md
- memory.md
- docs/index.md
- docs/codex-handoff.md
- docs/unfinale-world-sandbox-remodel-prd.md
- docs/unfinale-product-vision-correction-draft.md
- docs/unfinale-ai-development-alignment-checklist.md
- docs/living-novel-engine-iteration-plan.md
- docs/productization-phase-map.md
- docs/living-novel-engine-prd.md
- docs/completed/v0.7-product-web-app-ui-spec.md
- engine/README.md

当前项目是 未终章（Unfinale），核心代码在 engine/；技术缩写、包名、CLI 和环境变量前缀仍沿用 LNE / `living_novel_engine`。
产品入口边界：前端是产品入口，API 是能力层，CLI 是工程外壳；用户级功能优先走 Web UI + API，CLI 只服务开发者、本地服务启动、自动化验收、批处理和无人值守复跑。
当前最高优先级是 World Sandbox Loop / 世界沙盘改造：主导航按“世界书架 -> 世界内部卷宗”组织，优先做《天命书》、沙盘轮次、角色主观记忆链、世界自演、多视角活体小说和作者采纳台。不要继续默认扩 Graph/provider/检索评测/工程看板。
请不要只靠这段摘要；读完文档和相关代码后，再继续下一步。
```

如需追溯完整历史变更日志，再读 `docs/project-changelog.md`。日常接力优先以 `memory.md` 当前事实为准。

## 当前项目状态

未终章是 `D:\AI\open-infinite\engine` 下的故事世界运行时。核心闭环：

```text
文本输入 -> 世界锚定 -> 角色自主行动 -> 读者干预 -> 世界线分叉 -> 章节渲染 -> 可继续运行
```

截至 2026-06-01：

| 阶段 | 状态 |
| --- | --- |
| v0.7-v0.7.5 | 短中篇产品化 Web App 与交互增强已收口 |
| v0.8-v0.8.10 | 长篇导入、分层记忆、账本、审计、项目工作台、状态 overlay 已收口 |
| v0.9.0-alpha | 长篇共创闭环已整体收口：上传/创建 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出 -> closeout record |
| v0.9.1-v0.9.4 | Provider/Cost、MasterSetting、Graph Memory Evaluation、Advanced Runner Evaluation 均已收口 |
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
| Embedding / Vector Retrieval Readiness Probe MVP | 后续增强第九刀已收口，项目工作台只读展示 BM25、账本、别名、失败样本与向量检索触发证据 |
| Embedding Evaluation Samples MVP | 后续增强第十刀已收口，项目工作台只读评估失败样本、BM25 命中与 mock semantic oracle 差异 |
| Retrieval Failure Sample Authoring MVP | 后续增强第十一刀已收口，项目工作台可安全追加本地检索失败样本并刷新 embedding 样本评估 |
| Memory CLI MVP | 后续增强第十二刀已收口，命令行可追加、复跑和检查本地检索失败样本 |
| Retrieval Sample Export Pack MVP | 后续增强第十三刀已收口，service/API/UI/CLI 可只读导出失败样本 Markdown/manifest |
| Embedding Mock Evaluation Report MVP | 后续增强第十四刀已收口，service/API/UI/CLI 可只读生成 BM25 vs mock semantic oracle 对照报告 |
| Retrieval Sample Replay Report MVP | 后续增强第十五刀已收口，service/API/UI/CLI 可只读复跑失败样本并输出 case report |
| Retrieval Sample Migration Pack MVP | 后续增强第十六刀已收口，service/API/UI/CLI 可只读整理稳定 retrieval eval records 与 manifest |
| Cross Project Retrieval Samples Index MVP | 后续增强第十七刀已收口，service/API/CLI/设置页可只读汇总跨项目 retrieval eval records |
| Retrieval Samples Trend Snapshot MVP | 后续增强第十八刀已收口，service/API/CLI/设置页可只读输出样本覆盖、词面缺口、空样本项目和重型检索触发暂缓信号 |
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

验证基线：后端 `cd engine && python -m pytest -q` 为 `872 passed`；前端 `cd engine/ui && pnpm run build` 通过。真实检索烟测已确认 `v090-alpha-proof` 可写入 `unfinale_memory` 20 条，并以 `hybrid_vector_rerank` 模式返回 5 条检索结果，embedding、Zilliz 和 reranker 均实际参与且不返回明文密钥。

产品入口边界：前端是产品入口，API 是能力层，CLI 是工程外壳。导入、配置、创作、干预、评审、导出、样本采集、Graph Memory 证据查看等用户级能力应优先通过 Web UI + API 完成；CLI 仅作为开发者、本地服务启动、自动化验收、批处理、JSON 输出和无人值守复跑的薄封装。

## 当前自主迭代点

用户已明确进入产品纠偏：下一步不是继续 provider、Graph Memory、真实向量检索评测或工程化面板，而是把现有底座改造成“小说世界沙盘 / 活体小说运行时”。

当前改造主线：

```text
世界书架
  -> 天命书
  -> 世界沙盘
  -> 角色主观记忆链
  -> 世界自演检查点
  -> 多视角活体小说
  -> 世界线代偿 / 锚点转移
  -> 作者采纳台
```

真实用户模型配置 UI、本地一键运行脚本、Runtime Preflight MVP 至 Graph Memory Provider Spike Manual Mock Adapter Review MVP 共四十五刀、真实检索 provider 和 Vector Retrieval Pipeline 都已完成；这些现在统一视为支撑层。只有用户明确要求时，才继续评估 hybrid vector、GraphRAG/Zep 或 provider spike。

可选后续方向只有在用户确认后再进入：

- GitHub Release 安装包 / 内置 runtime。
- 腾讯云或服务器单机在线体验。
- 真实认证、对象存储、云端队列、配额执行或计费系统。

当前不默认接 Zep / 图数据库 / GraphRAG / LangGraph / OASIS / CAMEL；这些保持触发式评估边界。不要继续往 `WorkspacePage.tsx` 堆工程面板，后续前端应按 `docs/unfinale-world-sandbox-remodel-prd.md` 拆成世界内部卷宗。

## 开发硬约束

- 不改 `run_scene` 默认行为，除非用户明确要求进入 runner 重构。
- 不破坏既有 artifact 契约：`chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 新 artifact、API 字段、前端读取字段默认 additive。
- 后端 HTTP-facing identifier 必须安全校验；非法输入返回明确 400/404/409 或前端空态。
- 前端产品文案默认中文，不出现英文占位词。
- 用户级能力不应只有 CLI 入口；新增普通用户需要理解或操作的功能时，先补 Web UI + API，再按自动化需要补 CLI 薄封装。
- 不泄漏 API Key；设置页和日志只能展示脱敏尾号。
- 测试要隔离环境，避免误打真实 LLM/Seedream 外网。

## 当前真实未做项

- ChapterBrief 摘要质量仍偏规则化，未接真实 LLM 摘要。
- `contract_audit` 主链路仍偏静态，未成为运行时强约束。
- `state_execution_overlay.json` 不自动喂回下一轮 runner。
- 运行后审计未写入正史账本。
- Projection Health MVP 已形成独立只读健康报告/API/UI；真正 Chapter Commit 写后真源仍后置为 opt-in。
- Reader Panel / Adversarial Revision Lab deterministic/mockable MVP 已有；自动改写、Elo 对比、voice fingerprint 仍后置。
- Prompt Budget Pack 已形成独立只读预算包/压缩报告；真正接入 prompt 编排或 reranker 仍后置。
- LLM Profile Assignment 已形成只读任务画像；opt-in profile 保存、版本化和真实模型实验仍后置。
- Cards Workspace 已形成世界卡、角色卡、风格卡只读入口；独立卡片 artifact、版本化和批量编辑仍后置。
- OpenAPI / Typed Client 已形成只读 API contract、OpenAPI skeleton 和前端 typed client 映射；字段级 schema、自动生成 client 和外部集成契约仍后置。
- Bundled Release / Desktop Packaging 已形成只读发行准备评估；安装包、桌面壳、内置 runtime、签名和自动升级仍后置。
- Embedding / Zilliz / reranker 已显式接入：配置页脱敏状态、mock/real smoke、项目工作台真实向量检索、Zilliz 索引写入、混合检索预览和运行时 opt-in 已可用。默认 BM25 仍不替换；GraphRAG/Zep/Temporal Memory 仍保持证据链和 mock adapter 复核边界，不自动接外部服务。
- 云端多用户持久队列、真实对象存储 adapter、真实认证、真实计费仍未做。
- 默认检索替换 / GraphRAG / Zep 只在真实失败样本证明收益明确后再评估。

## 文档同步规则

完成有意义的开发、设计或验收任务后：

1. 更新 `memory.md` 当前状态和真实未做项。
2. 如需记录历史过程，追加 `docs/project-changelog.md`。
3. 若路线、PRD、README、UI spec 或本接力包发生事实变化，同步对应文档。
4. 至少运行 `git diff --check`；改代码时按风险运行 pytest、前端 build 或 HTTP smoke。

## 常用验证

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```
