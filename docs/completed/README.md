# Completed Docs Index

> 2026-06-06 文档治理口径：本目录只放已收口或历史归档文档。若某篇旧文档里出现“下一步”“未做”“后续建议”，先按 `../../memory.md` 和 `../index.md` 复核；已经完成的能力会在当前事实中写成已收口，仍未做的能力会明确写成当前后置或触发式评估。不要从本目录直接派生下一刀。

> 2026-06-06 整理补充：本目录暂不吸收世界沙盘 S1-S9 的当前主线文档。S1-S9、卷宗阅读、自演可读入口、Reviewer 局部重写采纳和编辑后定稿仍在 `../../memory.md`、`../unfinale-world-sandbox-remodel-prd.md`、`../living-novel-engine-iteration-plan.md`、`../../engine/README.md` 与 changelog 中维护；等用户明确要求做阶段归档时，再把稳定版本整理进 `completed/`。

## 当前事实入口

- 当前状态、真实暂停点和最新缺口：`../../memory.md`
- docs 分层与读取顺序：`../index.md`
- 当前路线图：`../living-novel-engine-iteration-plan.md`
- 当前世界沙盘主线：`../unfinale-world-sandbox-remodel-prd.md`
- 产品 UI 增量索引：`v0.7-product-web-app-ui-spec.md` + `v0.9-to-v1.0-product-ui-addenda.md`

## 文档分组

| 分组 | 文件 | 用途 |
|------|------|------|
| 历史审计 | `v0.1-to-v0.8-version-audit.md` | v0.1-v0.8 历史快照；已补 2026-06-01 后续状态，不再作为当前 todo 源 |
| 早期能力 | `v0.2-import-novel-mvp.md`、`v0.4-worldline-browser-release.md`、`open-source-essence-absorption.md` | 导入、浏览器、外部项目吸收的历史收口；已标注后续哪些能力已完成 |
| 多 Agent | `v0.6.1-multi-agent-runner-protocol.md`、`v0.6.4-multi-agent-llm-runner.md`、`v0.6.5-multi-agent-reliability.md` | runner / trace / LLM 推演阶段归档；已标注 v0.6.5、v0.9.4 的后续状态 |
| 产品 UI | `v0.7-product-web-app-ui-spec.md`、`v0.9-to-v1.0-product-ui-addenda.md` | v0.7 主规格与 v0.9-v1.0 UI 增量 |
| 长篇闭环 | `v0.9.0-alpha-long-creation-loop.md` 到 `v0.9.4-advanced-runner-evaluation-spike.md` | 长篇创作闭环、provider/cost、设定工作台、图记忆/高级 runner 触发评估 |
| 商业化边界 | `v1.0-beta-*.md` | 本地优先商业化硬化小刀；后续已补到 Billing Adapter Boundary Checklist-X |
| 本地体验 | `v1.0-local-model-configuration-ux.md`、`v1.0-local-run-scripts.md` | 真实模型配置 UX 与本地一键运行脚本 |
| 后续增强 | `runtime-preflight-mvp.md` 至 `graph-memory-provider-spike-manual-mock-adapter-review-mvp.md` | 创作前运行时体检到 Graph Memory Provider Spike Manual Mock Adapter Review 的后续增强 service/API/UI/CLI 收口说明 |
| 入口瘦身备份 | `codex-handoff-legacy-2026-06-01.md`、`living-novel-engine-iteration-plan-legacy-2026-06-01.md` | 从入口文档迁出的长版历史备份 |

当前世界沙盘 S1-S9、卷宗阅读页、自演结果可读入口、Reviewer 局部重写采纳、编辑后定稿等主线产物仍在根层 PRD、`memory.md`、`engine/README.md` 和 changelog 里维护；这些不是 `completed/` 的默认读取入口。

## 仍然后置的主边界

- 云端多用户持久队列、对象存储 adapter、真实认证、硬配额执行、商业计费系统和 webhook。
- 向量库 / embedding / GraphRAG / Zep：只在 BM25 + canon ledger + entity aliases、向量检索就绪探针、样本对照、shadow compare、case matrix、provider boundary、offline replay、fixture pack、readiness gate、runbook、result template、mock result report、review gate、manual approval pack、approval evidence checklist、opt-in evidence snapshot、opt-in no-go matrix、opt-in operator checklist 与 opt-in review packet 明确不足时评估。
- OASIS / CAMEL / LangGraph：只在现有 runner、trace 和状态执行层无法解释真实复杂样例时评估。
- overlay 自动驱动下一轮 runner、真正 Chapter Commit 写后真源、运行后审计写入正史账本、字段级 OpenAPI schema / 自动生成 typed client、真实安装包/桌面壳。
- LLM 语义评审、真实模型编辑器和整章风格润色仍属于世界沙盘作者链路的主线深化方向，不要误读为 `completed/` 已收口能力。
