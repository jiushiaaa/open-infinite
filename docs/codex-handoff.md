# Codex Handoff — 未终章

> 用途：新开 Codex 窗口时的最小接力包。本文件只给启动摘要，不替代 `../memory.md`、`index.md` 或世界沙盘 PRD。
> 完整历史见 `history/project-changelog.md`；旧长接力稿见 `completed/codex-handoff-legacy-2026-06-01.md`。

## 新窗口第一条消息建议

```text
请先阅读并对齐：
- AGENTS.md
- memory.md
- docs/index.md
- docs/unfinale-world-sandbox-remodel-prd.md
- docs/unfinale-ai-development-alignment-checklist.md
- docs/living-novel-engine-iteration-plan.md
- docs/unfinale-current-optimization-backlog.md
- engine/README.md

需要愿景判断时再读：
- docs/unfinale-product-vision-correction-draft.md
- docs/living-novel-engine-prd.md

需要 UI 风格时再读：
- docs/completed/v0.7-product-web-app-ui-spec.md
- docs/image/README.md

当前项目是未终章（Unfinale），核心代码在 engine/；技术缩写、包名、CLI 和环境变量前缀仍沿用 LNE / living_novel_engine。
当前默认主线是 World Sandbox Loop / 小说世界沙盘，不是 provider、GraphRAG、检索评测、OpenAPI、发行或商业化。
下一步应继续深化：真实 LLM 多 Agent 策略博弈、长正文/连续阅读质量、跨章节误会回收、跨章伏笔回收、更强真实语义 Reviewer、整章风格润色和世界状态长期发酵。
请不要只靠这段摘要；读完文档和相关代码后再动手。
```

## 当前事实速记

| 分类 | 当前状态 |
| --- | --- |
| 主线 | World Sandbox Loop / 小说世界沙盘体验深化 |
| 已完成第一版 | S1-S9 世界沙盘链路、世界书架、世界锚定房间、天命书、世界沙盘、世界正史卷、主锚点卷、角色个人卷、势力卷、事件多视角、跨事件长线卷、世界线、检查点回放、卷宗阅读、作者采纳台、Reviewer 局部重写、编辑后定稿、确认入卷和下一轮入口 |
| 最近产品化 | 沙盘策略博弈结果可读化、卷宗正文内证据跳转、世界入口重组、跑后下一步行动台、作者采纳确认后回沙盘、卷宗阅读下一章接力台等已完成第一版 |
| 当前验证基线 | 最近完整后端记录：`cd engine && python -m pytest -q` -> `951 passed`；前端 `cd engine/ui && pnpm run build` 通过 |
| 文档分层 | 入口事实看 `memory.md`；文档地图看 `docs/index.md`；路线看 `docs/living-novel-engine-iteration-plan.md`；当前优化看 `docs/unfinale-current-optimization-backlog.md`；完整历史看 `docs/history/project-changelog.md` |
| 支撑层 | v0.7-v1.0-local、真实 retrieval provider、Vector Retrieval Pipeline、Graph/长期记忆 mock 复核链等已收口为支撑层 |

## 当前真实未做项

优先继续：

- 真实 LLM 多 Agent 多轮策略规划、长期关系/势力博弈、稳定误判/隐瞒/试探和跨轮结算。
- 长正文读感、跨章节误会回收、跨章伏笔回收、账号级用户阅读进度持久化和真实文风一致性。
- Reviewer 整章风格润色、可回滚对照、真实模型编辑器和定稿质量门。
- `consequence_state` 长期状态机、人工确认、跨章节发酵和真实 LLM 决策消费。
- 跨章角色/势力长线阅读、跨卷证据联动、真实世界状态长期化和更完整的机制档案分区。

不要默认继续：

- GraphRAG / Zep / Temporal Memory 重型 provider 试验。
- 默认 hybrid vector 替换 BM25。
- OpenAPI / typed client 深化。
- 发行安装包、云端部署、多租户、认证、对象存储、计费。
- LangGraph / OASIS / CAMEL。
- 继续往 `WorkspacePage.tsx` 堆工程面板。

## 执行纪律

- 不改 `run_scene` 默认行为，除非用户明确要求 runner 重构。
- 新 artifact、API 字段、前端字段默认 additive。
- 不破坏 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 用户级能力优先 Web UI + API；CLI 只做开发者/自动化外壳。
- 不泄漏 API key；真实模型 smoke 不打印明文 key、不大规模消耗、不进入默认全量 pytest。
- 每个独立切片完成后同步 `memory.md`、相关 PRD/README/本文件和 `history/project-changelog.md`。
- 验证通过后默认提交并推送当前分支；不要提交 `.local-run/` 或 `engine/.local-run/`。

## 常用验证

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

docs-only 任务至少运行 `git diff --check`，并用 `rg` 搜索旧基线、旧下一刀和支撑层误导口径。
