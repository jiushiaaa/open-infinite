# 未终章 - 项目记忆（跨会话）

> **用途**：供 Codex / Cursor / 多会话 Agent 快速恢复项目事实，避免重复劳动或把历史待办误判成当前任务。
> **维护约定**：本文件只保留“当前事实、路线、边界、入口索引”；完整历史变更日志已迁移到 `docs/project-changelog.md`。每次有意义的开发/设计/验收任务结束后，请把状态同步到本文对应章节，并将历史记录追加到变更日志文档末尾。
> **最后更新**：2026-06-01（品牌名从 Living Novel Engine / 活体小说引擎收口为“未终章 / Unfinale”；当前暂停继续新刀，等待用户本地试用反馈。）

---

## 1. 当前状态（先读）

| 项 | 当前事实 |
| --- | --- |
| 项目 | 未终章（Unfinale）；技术缩写、Python 包、CLI 与环境变量前缀仍沿用 LNE / `living_novel_engine`，核心代码在 `D:\AI\open-infinite\engine` |
| 北极星 | 文本输入 -> 世界锚定 -> 角色自主行动 -> 读者干预 -> 世界线分叉 -> 章节渲染 -> 可继续运行 |
| 当前完成度 | v0.7 短中篇产品化 MVP、v0.8 长篇底座 MVP、v0.9.0-alpha 长篇共创闭环、v0.9.1-v0.9.4 触发式增强、v1.0-beta 本地优先商业化边界、v1.0-local 本地模型配置与一键运行脚本均已收口 |
| 测试基线 | `cd engine && python -m pytest -q` -> `713 passed`；`cd engine/ui && pnpm run build` 通过 |
| 官方下一步 | 当前按用户要求暂停继续新刀；先等用户本地试用反馈 |
| 后续候选 | 本地体验稳定后再排 GitHub Release 安装包、内置 runtime、服务器/腾讯云在线体验；真实云端多租户、对象存储、认证、计费继续后置 |

判断“下一刀”时，先以本节和 `docs/living-novel-engine-iteration-plan.md` 为准；不要从旧变更日志里直接捞历史待办。

---

## 2. 必读入口与事实优先级

新会话或新任务如果涉及 LNE、`engine/`、版本路线、产品 UI、API、测试或文档，先读：

1. `memory.md`：当前事实、边界、测试基线、已知缺口。
2. `docs/living-novel-engine-iteration-plan.md`：版本路线与官方下一步。
3. `docs/productization-phase-map.md`：技术 MVP、产品化 MVP、长篇产品化、商业化加固的阶段边界。
4. `docs/living-novel-engine-prd.md`：产品定位和用户流程。
5. `docs/completed/v0.7-product-web-app-ui-spec.md`：Web UI 风格和交互边界。
6. `engine/README.md`：CLI/API/输出结构/验收命令。
7. `docs/codex-handoff.md`：存在接力任务时再读。

事实优先级：`memory.md` > 主迭代计划 > `engine/README.md` > 主 PRD > 聊天摘要。

文档导航见 `docs/index.md`；完整历史变更日志见 `docs/project-changelog.md`。

---

## 3. 阶段收口总览

### 已收口主阶段

- v0.1-v0.6：CLI 原型、导入、检索、世界线浏览、multi-agent runner 与 trace 可靠性。
- v0.7：产品级 Web App 九刀、Agent Interaction、Visual Asset Generation、Baseline & Canon Replay、Worldline Judge。
- v0.8：长篇导入、分层记忆、正史账本、混合检索、审计、ActDirector、Narrator diagnostics、Dynamic Action Registry、Emergence Mining、Entity Alias、Runtime Memory Consumption、Artifact Panel、Long Upload Productization。
- v0.9.0-alpha：长篇创作闭环，覆盖章节导出、续写、世界线选择、审计入口、closeout API/CLI/record、alpha ready 和 closeout report。
- v0.9.1：Provider & Cost Gateway Lite。
- v0.9.2：MasterSetting Workspace Lite。
- v0.9.3：Graph Memory Evaluation Spike。
- v0.9.4：Advanced Runner Evaluation Spike。
- v1.0-beta：本地优先商业化边界，从 Scope-A 到 Billing Adapter Boundary-X 均已收口。
- v1.0-local：Model Configuration UX 与 Local Run Scripts 已收口。

### 当前暂停点

- 真实用户模型配置 UI 与本地一键运行脚本已完成。
- 后续不默认继续新刀，等待用户本地试用反馈。
- 若用户要继续，可在发行路径中选择：GitHub Release 安装包、内置 runtime、腾讯云/服务器在线体验。

---

## 4. 当前产品与工程能力

### 创作闭环

- 可导入 txt/md/zip/epub，服务端 ingest session 支持分片、hash 校验、缺失分片查询、重复 chunk 幂等与 localStorage 恢复续传。
- 长篇导入会写 `source_raw/`、`import_report.json`、`memory/`、`canon_ledger.jsonl`、`consistency_report.json`。
- 世界锚定页展示导入检查、设定工作台、章节预览、分层记忆、正史账本、实体别名、检索命中、审计报告和下一步入口。
- 干预 run 会生成分支产物，并可进入评审、审计、设为起点、生成下一章、章节/合集导出。

### 运行与状态执行

- `run_scene` 默认行为不变。
- 干预 run 可生成 `runner_state_execution_report.json` dry-run 评估。
- 显式确认后，low-risk/executable/白名单 delta 可写入分支 `state_execution_overlay.json`，并生成 apply/rollback 报告。
- `state_snapshot.json` 不被覆盖；overlay 暂不自动驱动下一轮 runner 消费。

### 记忆、检索与审计

- `canon_ledger` 已进入 BM25 检索 artifact，source 为 `canon_ledger`。
- 正史 holdout 写入 `canon/visibility_manifest.json`，区分 `runtime_visible` / `holdout_private`。
- 干预、baseline 与 CLI resume 通过既有 `retrieved_context` 参数只读消费 memory/alias/ledger 安全子集，并写 `runtime_memory_context.json`。
- 前端“机制档案”只读展示运行记忆、动作计划、动作注册表、叙事诊断、涌现节点。
- 本地审计日志已覆盖版权声明、设定编辑、世界线选择、状态执行 apply/rollback、项目保留策略等关键写操作。

### 设置、本地运行与商业化边界

- 设置抽屉已包含脱敏 provider 状态、usage 汇总、手动价格估算、route matrix、模型配置状态和视觉密钥清除。
- `scripts/start-local.ps1` 与 `scripts/start-local.sh` 支持 clone 后检查/安装依赖并启动后端与 Vite 前端。
- v1.0-beta 只做本地优先商业化边界和只读/本地写入 artifact；不接真实认证、云端对象存储、队列、计费、不可篡改审计或发布系统。

---

## 5. 关键硬约束

- 不改 `run_scene` 默认行为，除非用户明确要求进入 runner 重构。
- 不破坏既有 artifact 契约：`chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 新增 artifact、API 字段、前端读取字段默认 additive。
- 后端 HTTP-facing identifier 必须走安全校验，不能把未经校验的 slug/run_id/branch_id 拼到文件路径。
- 失败要降级为明确的 400/404/409 或前端空态，不白屏、不 500。
- 前端产品文案默认中文；不要出现英文占位词。
- 视觉风格保持 v0.7 的古风纸面、克制系统感，不做营销落地页。
- `Reference_projects/` 与外部项目只作参考，不直接复制源码或引入依赖，除非用户明确要求。
- 不泄漏 API Key；设置页或日志只能展示脱敏尾号。
- 用户在 `.env` 中可能已经配置真实 `SEEDREAM_API_KEY` / `LLM_API_KEY`。测试要隔离环境，避免误打真实外网。

---

## 6. 当前真实未做项（不要再把历史已完成项当缺口）

| 缺口 | 当前状态 | 下一步触发 |
| --- | --- | --- |
| ChapterBrief 质量仍偏薄 | 导入时可用，但 summary/facts 仍偏规则化，未接真实 LLM 摘要 | 长篇质量明显受限时再做 |
| `contract_audit` 主链路仍偏静态 | 已有多种审计与商业化边界，但运行时 contract 仍未作为主链路强约束 | 出现合约越界误判/漏判时再补 |
| overlay 未自动喂回 runner | 状态执行 overlay 可 apply/rollback，但下一轮 runner 暂不自动消费 overlay | 用户确认需要连续状态演化时再做 |
| 运行后审计未写入正史账本 | 审计日志与 canon ledger 分工仍分离 | 需要“审计结论影响正史”时再做 |
| 云端多用户持久队列/对象存储/认证/计费 | v1.0-beta 已定义边界，但刻意不接真实云端系统 | 外部用户试用或部署路径明确后再做 |
| 向量库 / embedding / GraphRAG | 已有 BM25、ledger、alias、probe 与触发式评估；暂不接 Zep/图数据库 | 50+ 章或 probe 证明 BM25 不够时评估 |
| 高级 runner 框架 | 已有触发式评估，不默认接 LangGraph/OASIS/CAMEL | probe 证明现有 runner 到瓶颈时再做 |

已完成但历史上曾列为缺口的能力：视觉资产、长篇分层记忆、正史账本、长篇混合检索、长篇一致性审计、抽象干预编译层、Worldline Judge、涌现节点、叙事诊断、动态动作注册表、百万字上传入口、无干预 baseline、正史回放等，均不应再作为当前未做项重复安排。

---

## 7. 主要产物索引

| 类型 | 产物 |
| --- | --- |
| 基础 run | `chapter.md`、`events.json`、`state_snapshot.json`、`meta.json` |
| 分支与干预 | `intervention.json`、`causal_diff.json`、`intervention_compilation.json`、`worldline_judgement.json` |
| 多 Agent | `multi_agent_trace.json`、`generation_meta`、trace quality validator |
| 长篇导入 | `source_raw/`、`import_report.json`、`memory/`、`canon_ledger.jsonl`、`consistency_report.json` |
| 运行记忆 | `runtime_memory_context.json`、`retrieval_context.json` |
| 高级机制 | `act_director_plan.json`、`narrative_diagnostics.json`、`dynamic_action_registry.yaml`、`emergence_nodes.json` |
| 状态执行 | `runner_state_execution_report.json`、`state_execution_overlay.json`、apply/rollback report |
| 创作闭环 | `selected_worldline.json`、`creation_loop_alpha_closeout.json`、章节/合集导出与 share guard |
| 商业化本地边界 | `project_audit_log.jsonl`、`project_copyright_statement.json`、`project_retention_policy.json` |

---

## 8. API / CLI 状态索引

### 已有 API 类型

- 项目与导入：story genesis、文件上传、ingest session、project workspace、world anchor。
- 干预与世界线：run/intervene、causal diff、worldline judgement、worldline selection。
- 回放与审计：baseline、canon replay、replay range、replay audit、post-run audit、audit log 与 export。
- 创作闭环：resume continue job、chapter export、collection export、creation loop closeout。
- 设置与 provider：providers、provider usage、manual price estimate、route matrix、model configuration。
- 商业化边界：commercial scope/status、permission matrix、quota/observability、deployment readiness、cloud persistence、account project space、auth/object storage/quota/billing boundary 等。

### 常用 CLI / 验收

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

长篇闭环相关 CLI 以 `engine/README.md` 为准，例如 `lne creation-loop-closeout --write-report` 等。

---

## 9. 文档索引

| 文档 | 用途 |
| --- | --- |
| `AGENTS.md` | Agent 项目规则、硬约束、会话入口 |
| `memory.md` | 当前事实、边界、已知缺口、索引 |
| `docs/project-changelog.md` | 完整历史变更日志 |
| `docs/index.md` | docs 资料导航与推荐读取顺序 |
| `docs/codex-handoff.md` | 新 Codex 窗口接力包 |
| `docs/living-novel-engine-iteration-plan.md` | 主路线图 |
| `docs/productization-phase-map.md` | 阶段边界 |
| `docs/living-novel-engine-prd.md` | 主 PRD |
| `docs/distribution-phase-plan.md` | 后置发行路径 |
| `docs/completed/` | 已收口版本文档、PRD、Release Note、UI spec、工程协议 |
| `docs/article/` | 论文 PDF 与研读报告 |
| `Reference_projects/` | 参考开源项目，仅作设计参考 |

---

## 10. 参考项目与论文吸收边界

已吸收为路线语言的参考方向：

- Player-driven emergence：对应 `emergence_nodes`、分支差异、Worldline Judge。
- StoryVerse / Abstract Act / Act Director：对应 `AbstractIntervention`、compatibility、realization、`act_director_plan.json`。
- Human-Level Narratives / Story Arc / Turning Points：对应 `narrative_diagnostics.json` 与后续 narrator 反馈候选。
- STORY2GAME / Dynamic Action Generation：对应 `dynamic_action_registry.yaml` 与 alias/entity resolution。
- WenShape、webnovel-writer、MiroFish 等开源项目：只作架构与产品启发，不作为已引入依赖。

---

## 11. 决策备忘

- 本地优先：当前更重视单机可运行、可验证、可交付给用户试用，而不是过早云端平台化。
- 长篇路线：先用现有 BM25/ledger/alias/probe 把百万字底座跑通，再用触发式评估决定是否接 vector/graph/rerank。
- Runner 路线：先保持 `SceneRunner` adapter 与当前 runner 安全边界，高级框架只在 probe 证明必要时引入。
- 商业化路线：v1.0-beta 只定义边界、审计口径和本地 artifact，不伪装成真实多租户 SaaS。
- 发行路线：本地脚本完成后暂停，等本地试用反馈，再决定 GitHub Release、内置 runtime 或服务器在线体验。

---

## 12. Agent 维护说明

- 先读当前章节，再读路线图；旧日志只用于追溯“为什么这么做”，不要把旧待办当当前事实。
- 做完有意义的开发/设计/验收任务后，同步三处：`memory.md` 当前状态、相关路线/README/PRD、`docs/project-changelog.md` 末尾历史记录。
- 不要改写历史变更日志；如历史条目过时，只在 `memory.md` 当前章节修正现状，必要时在新日志条目说明“状态已更新”。
- 若只做文档迁移，验证至少跑 `git diff --check`；若改代码，再按风险跑 pytest / UI build / HTTP smoke。

---

## 13. 历史变更日志索引

完整历史变更日志已迁移到 `docs/project-changelog.md`。本入口文档不再承载完整日志，只保留当前事实、路线、边界和索引，避免新会话启动时被历史过程拖慢。
