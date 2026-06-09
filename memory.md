# 未终章 - 项目记忆（跨会话）

> **用途**：给 Codex / Cursor / 其他 Agent 快速恢复当前事实，避免把历史待办误判成当前路线。
> **维护约定**：本文件只保留当前事实、路线、边界、缺口和入口索引；完整历史变更日志见 `docs/history/project-changelog.md`，已收口专项见 `docs/completed/`，当前后续优化见 `docs/unfinale-current-optimization-backlog.md`。
> **最后更新**：2026-06-09（前端按 docs/image 视觉基准完成第二轮剩余卷宗页与边缘入口纸面化）。

## 1. 当前一句话

未终章（Unfinale）当前默认主线是 **World Sandbox Loop / 小说世界沙盘体验深化**：导入或创世一个故事世界，确认《天命书》，让多 Agent 角色在世界沙盘里自主行动、记住、误判、反抗、代偿，并把世界演化渲染成可读章节和可被作者采纳的下一章材料。

技术缩写、Python 包、CLI 与环境变量前缀仍沿用 LNE / `living_novel_engine`。核心代码在 `engine/`。前端是产品入口，API 是能力层，CLI 是工程外壳。

## 2. 当前完成度

| 分类 | 当前事实 |
| --- | --- |
| 支撑层 | v0.7-v1.0-local、真实 retrieval provider、opt-in Vector Retrieval Pipeline、Graph/长期记忆 mock 复核链等已收口为支撑层；除非用户明确点名，不作为默认下一刀 |
| 世界沙盘主链 | S1-S9 已有第一版 service/API/UI/artifact/tests：沙盘轮次、主观记忆、《天命书》、干预投放、L5 觉醒/模因传播、因果债具象化、自演检查点、多视角正文、作者采纳、连续阅读、确认入卷 |
| 阅读体验 | 卷宗阅读、世界正史卷、主锚点卷、角色个人卷、势力卷、事件多视角、跨事件长线卷、检查点回放和世界线页已有第一版可读入口 |
| 作者链路 | Reviewer 局部重写、作者勾选采纳、编辑后定稿、确认入卷、下一轮沙盘启动台和跨章回收清单已有第一版 |
| 导航壳层 | 世界书架、世界锚定房间、AppShell、WorldWorkspaceShell、WorldRunway、移动端折叠导航、全局续读和卷宗速览已有第一版 |
| 最近收口 | 2026-06-09 已在 2026-06-08 第一轮核心页纸面化基础上，继续按 `docs/image` 视觉基准覆盖世界正史卷、主锚点卷、角色个人卷、势力卷、事件多视角、跨事件长线卷、世界线档案、检查点回放、多视角入口、导入、创世和机制档案等剩余前端页面；全局纸面基座、墨色侧栏、朱砂主动作、玉青状态、卷宗卡片、山水题签和移动端 360px 无水平溢出已完成第二轮验证 |
| 最近记录验证基线 | `cd engine && python -m pytest -q` 最近完整基线记录为 `951 passed`；`cd engine/ui && pnpm run build` 通过；docs-only 任务至少跑 `git diff --check` |

判定完成时不要只看“有 API / 有测试 / 有页面 / 有 artifact”。后续切片应让用户真实感到：世界会运行、角色会自主、角色会记得、干预有后果、角色可能反抗、世界会代偿、章节来自世界演化。

## 3. 当前最高主线

默认路线：

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

“沙盘 / 阅读 / 干预 / 作者”是同一个世界里的场景能力，不是一级工作区。不要继续把新面板堆进 `WorkspacePage.tsx`；旧工程能力应收纳到机制档案或明确的支撑层入口。

## 4. 当前优先深入

1. **真实 LLM 多 Agent 策略博弈**：多轮规划、长期关系、势力资源、欺骗/隐瞒/试探、反抗/妥协、失败和误判跨轮结算。
2. **长正文与连续阅读质量**：更自然的章节节奏、人物动机、视角稳定、伏笔回收、结尾悬念和真实文风一致性。
3. **跨章节误会与伏笔回收**：正文内证据、误会图谱、长线卷、角色/势力追踪继续接到下一章和下一轮沙盘。
4. **更强语义 Reviewer 与整章润色**：从片段级改写走向整章风格一致性、可回滚对照、真实模型编辑器和定稿质量门。
5. **世界状态长期化**：`consequence_state`、因果债、代偿、角色主观记忆和世界线状态要跨章节发酵，并被下一轮真实决策消费。

## 5. 默认不做

以下方向只有用户明确点名，或真实样本证明主线必须依赖它们时才进入：

- GraphRAG / Zep / Temporal Memory 重型 provider 试验。
- 默认 hybrid vector 替换 BM25。
- provider / cost / route matrix 继续扩张。
- OpenAPI / typed client 深化。
- 发行安装包、云端部署、多租户、认证、对象存储、计费。
- LangGraph / OASIS / CAMEL 默认替换现有 runner。
- 纯工程健康报告、readiness gate 或 checklist，但没有新的小说世界体验。

## 6. 必读入口与事实优先级

新会话或新任务如果涉及未终章、`engine/`、版本路线、产品 UI、API、测试或文档，先读：

1. `AGENTS.md`：Agent 执行规则、硬约束和会话必读清单。
2. `memory.md`：当前事实、边界、真实未做项和入口索引。
3. `docs/index.md`：文档分层、读取顺序和历史归档边界。
4. `docs/unfinale-world-sandbox-remodel-prd.md`：当前世界沙盘主线 PRD。
5. `docs/unfinale-ai-development-alignment-checklist.md`：开工前自检。
6. `docs/living-novel-engine-iteration-plan.md`：当前路线和下一刀候选。
7. `engine/README.md`：后端运行、API、artifact 和验证命令。
8. 需要判断真实未完成优化时读 `docs/unfinale-current-optimization-backlog.md`。
9. 需要愿景判断时读 `docs/unfinale-product-vision-correction-draft.md` 与 `docs/living-novel-engine-prd.md`。
10. 需要 UI 风格时读 `docs/completed/v0.7-product-web-app-ui-spec.md`。
11. 接力任务再读 `docs/codex-handoff.md`。

事实优先级：

```text
memory.md
  -> docs/index.md
  -> docs/unfinale-world-sandbox-remodel-prd.md
  -> docs/unfinale-ai-development-alignment-checklist.md
  -> docs/living-novel-engine-iteration-plan.md
  -> engine/README.md
  -> docs/living-novel-engine-prd.md
  -> 聊天摘要
```

`docs/history/project-changelog.md` 是追加式历史日志，只用于追溯或补历史记录；不要从旧 changelog 条目里直接派生下一刀。

## 7. 关键硬约束

- 不改 `run_scene` 默认行为，除非用户明确要求 runner 重构。
- 不破坏既有 artifact 契约：`chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 新 artifact、API 字段和前端读取字段默认 additive。
- 后端 HTTP-facing identifier 必须安全校验；失败返回明确 400/404/409；坏 artifact 降级为空态、需留意或需修复，不白屏、不 500。
- 前端用户可见文案默认中文，视觉保持 v0.7 古风纸面、克制系统感。
- 用户级能力优先 Web UI + API；CLI 只服务本地启动、开发者验收、批处理、JSON 输出和无人值守复跑。
- `Reference_projects/` 与外部项目只作参考，不直接复制源码或引入依赖，除非用户明确要求。
- 不泄漏 API Key；日志和设置页只能展示脱敏尾号。
- 默认测试要隔离真实外网；真实模型 smoke 只能 opt-in、小样本、不打印明文 key、不进入默认全量 pytest。

## 8. 主要产物和 API 索引

核心 artifact：

```text
projects/<slug>/tianming.json
projects/<slug>/worldlines/<worldline_id>/tianming_snapshot.json
projects/<slug>/worldlines/<worldline_id>/worldline_state.json
projects/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective_memory.jsonl
projects/<slug>/author_adoption_ledger.jsonl

outputs/<run_id>/sandbox_rounds.jsonl
outputs/<run_id>/agent_decision_advisory.json
outputs/<run_id>/intervention_constraint.json
outputs/<run_id>/subjective_memory_delta.json
outputs/<run_id>/autopilot_report.json
outputs/<run_id>/checkpoints/checkpoint_*.json
outputs/<run_id>/character_lens_briefs.json
outputs/<run_id>/character_lens_volumes.json
outputs/<run_id>/next_chapter_brief.json
outputs/<run_id>/next_chapter_draft.json
outputs/<run_id>/edited_final_chapter.json
outputs/<run_id>/continuous_reading_chapter.json
outputs/<run_id>/confirmed_chapter_entry.json
```

主线 API：

```text
GET/POST /api/stories/<slug>/tianming...
POST     /api/stories/<slug>/sandbox/run
GET      /api/sandbox-runs/<run_id>
GET      /api/stories/<slug>/worldlines/<worldline_id>/dossier
GET      /api/stories/<slug>/worldlines/<worldline_id>/dossier-reading
GET      /api/stories/<slug>/worldlines/<worldline_id>/longline-reading
GET      /api/stories/<slug>/worldlines/<worldline_id>/events/<event_id>/perspectives
POST     /api/stories/<slug>/world-autopilot/run
GET      /api/world-autopilot-runs/<run_id>/readable-entry
GET      /api/world-autopilot-runs/<run_id>/checkpoints/<checkpoint_id>
POST     /api/stories/<slug>/character-lens/generate
POST     /api/stories/<slug>/author-adoption...
```

完整 API、配置和运行说明以 `engine/README.md` 为准。

## 9. 常用验证

代码任务按风险选择：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

docs-only 任务至少运行 `git diff --check`，并搜索旧基线、旧下一刀、支撑层误导口径和坏链接。

## 10. 文档维护规则

- `memory.md` 只写当前事实，不再追加流水账；历史进展写到 `docs/history/project-changelog.md` 末尾。
- `docs/index.md` 负责解释每类文档能不能当待办来源。
- `docs/unfinale-current-optimization-backlog.md` 集中承接当前还要继续优化的主线事项。
- `docs/completed/` 是已收口专项归档；旧“下一步”必须回到本文复核。
- `docs/completed/support-layer-enhancement-index.md` 是支撑层索引，不是当前默认路线。
- `docs/postponed/distribution-phase-plan.md` 是后置发行路径，不抢世界沙盘主线。
- 做完有意义的开发/设计/验收任务后，同步当前事实、相关 PRD/路线/README/handoff，并追加 changelog。
