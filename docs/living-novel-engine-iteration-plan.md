# 未终章产品迭代计划

> 用途：当前路线图入口。它回答“下一步该沿哪条主线继续”，不再复制完整历史实施清单。
> 最新事实以 `../memory.md` 为准；文档分层见 `index.md`；完整历史见 `project-changelog.md`；旧长版计划已归档到 `completed/living-novel-engine-iteration-plan-legacy-2026-06-01.md`。

## 1. 当前结论

当前默认主线是 **World Sandbox Loop / 小说世界沙盘体验深化**。

```text
导入 / 创世
  -> 《天命书》
  -> 多 Agent 世界沙盘轮次
  -> 角色主观记忆链
  -> 干预投放与世界线代偿
  -> 世界自演检查点
  -> 多视角活体小说 / 连续阅读
  -> 作者采纳台 / Reviewer / 下一章入口
```

已经完成的是“第一版产品链路闭环”，不是完整愿景终局。下一步不再补“有没有 API / 有没有 artifact”，而是继续打磨用户能否真实感到：

- 世界会运行。
- 角色会自主。
- 角色会记得。
- 干预有后果。
- 角色可能反抗。
- 世界会代偿。
- 章节来自世界演化。

## 2. 已闭环等级

| 分层 | 当前口径 | 后续处理 |
| --- | --- | --- |
| 历史底座 | v0.7-v1.0-local、后续增强四十五刀、真实 retrieval provider、Vector Retrieval Pipeline 都已收口 | 作为支撑层保留，不默认继续扩张 |
| 世界沙盘 S1-S9 | 《天命书》、沙盘轮次、主观记忆、干预投放、L5 觉醒/模因传播、因果债具象化、自演检查点、多视角正文、作者采纳、连续阅读、确认入卷均有第一版 | 继续深化体验，不从 v1 重做 |
| 阅读入口产品化 | `dossier-reading`、卷宗阅读页、卷首题签、连续阅读分场景、当前场景导读条、正文证据锚点、误会图谱、阅读进度书签、角色个人卷独立页、势力卷独立页、事件多视角详情页、跨事件长线卷、长线阅读进度、多事件索引、误会回收台、本机最近阅读续航、AppShell 全局续读入口与卷宗速览盘、移动端壳层压缩、未解线索、移动端先读正文、`readable_entry`、世界线/检查点/角色/事件/长线跳转和检查点醒来回放中枢已完成第一版 | 继续做更深跨章误会网络、账号级用户阅读进度持久化和跨章节回收 |
| 作者链路产品化 | Reviewer 片段级建议 -> 作者勾选采纳 -> `edited_final_chapter` -> 确认入卷 -> 下一轮入口已完成第一版；作者采纳台首屏已有四步工作流中枢和下一步主行动 | 继续做整章风格润色、可回滚对照、真实模型编辑器 |
| 世界入口与导航第一版 | 世界书架、故事卡下一步导览、导入/创世开卷中枢、顶栏世界内卷宗导航、AppShell 世界位置条/世界体验轨道/全局续读入口/卷宗速览盘/移动端壳层压缩、锚定到天命书、天命书首屏宪法封面、世界线首屏工作流中枢、检查点首屏醒来回放中枢、多视角首屏工作流中枢、机制档案首屏中枢、沙盘空态导引、机制档案降噪、入口首屏 QA、世界内导览层 `WorldRunway`、锚定页启动卡、最近阅读续航、世界卷宗总览、当前旅程状态、角色个人卷独立页、势力卷独立页、事件多视角详情页、沙盘运行导览、移动端世界卷宗导航盘和移动端栏目保功能已完成第一轮 | 继续做更完整的 `WorldWorkspaceShell`、跨页面视觉 QA 和状态提示 |

## 3. 当前官方下一步

优先级从高到低：

1. **真实 LLM 多 Agent 策略博弈**
   - 已有 `llm_decision_mode=advisory`、`agent_decision_advisory.json` 和 `strategy_board`。
   - 下一步做多轮策略规划、长期关系/势力博弈、误判/隐瞒/试探的跨轮结算，让世界状态真正被策略互动改变。

2. **长正文与连续阅读质量**
   - 已有 `continuous_reading_chapter` v2、卷宗阅读页、卷首题签、确认稿阅读链和自演可读入口。
   - 下一步做更自然的长文节奏、更深跨章误会回收、跨章伏笔回收、账号级用户阅读进度持久化和真实文风稳定。

3. **语义 Reviewer 与整章风格润色**
   - 已有语义 Reviewer、局部改写建议、作者勾选采纳、编辑后定稿、自动确认入卷和作者采纳台首屏工作流中枢。
   - 下一步从“应用局部建议”升级到“整章风格一致性润色、可回滚对照、真实模型编辑器和定稿质量门”。

4. **世界状态长期化**
   - 已有 `worldline_state.json`、`consequence_state` 六域代偿和自演 checkpoint。
   - 下一步让代偿状态可累积、可确认、可被真实 LLM 决策消费，并能跨章节发酵。

5. **世界内部卷宗壳**
   - 已有世界线页、检查点首屏醒来回放中枢、卷宗阅读页、角色个人卷独立页、势力卷独立页、事件多视角详情页、跨事件长线卷、世界沙盘页、天命书首屏宪法封面、顶栏世界内卷宗导航、AppShell 世界位置条/世界体验轨道/全局续读入口/卷宗速览盘/移动端壳层压缩、锚定页世界卷宗总览、当前旅程状态和 `WorldRunway` 导览层第一版。
   - 下一步做 `WorldWorkspaceShell`、跨章角色/势力长线阅读、跨章节回收和更完整的机制档案分区，把旧工程面板继续收纳为支撑层。

## 4. 不作为默认下一步

以下方向只有用户明确点名或真实样本证明必要时才进入：

| 方向 | 当前处理 |
| --- | --- |
| GraphRAG / Zep / Temporal Memory | 已有触发证据、shadow、case matrix、provider boundary、manual mock adapter review 等支撑层证据；不默认接生产服务 |
| 默认 hybrid vector 替换 BM25 | 真实 embedding、Zilliz、rerank 和 opt-in runtime 已可用；默认仍不替换 |
| OpenAPI / typed client 深化 | 已有只读 contract；字段级 schema 和自动生成 client 后置 |
| 发行安装包 / 云端部署 | 本地体验稳定后再走 `distribution-phase-plan.md` |
| 认证 / 对象存储 / 计费 / 多租户 | v1.0-beta 只定义边界，真实平台化后置 |
| LangGraph / OASIS / CAMEL | 只有现有 runner 被真实复杂样例证明不足时再评估 |
| 继续往 `WorkspacePage.tsx` 堆面板 | 禁止作为默认做法；应拆到世界内部卷宗或机制档案 |

## 5. 下一刀选择规则

开始任何新切片前，先问：

1. 这一刀是否直接增强世界运行、角色自主、角色记忆、干预后果、角色反抗、世界代偿或章节生成？
2. 用户是否能在 Web UI 或 API 里看见结果，而不是只多一个 CLI 或 JSON？
3. 产物是否 additive，不破坏 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`？
4. 是否保留 deterministic/mockable 回归，并在生成质量相关切片补小样本真实模型 smoke？
5. 是否同步 `memory.md`、相关 PRD/README/handoff 和 `project-changelog.md`？

如果答案不成立，这一刀大概率应重切。

## 6. 验收命令

常规验证：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

docs-only 任务至少运行 `git diff --check`，并用 `rg` 搜索过期基线、旧下一刀和支撑层误导口径。

生成质量相关任务还应在 mock 回归之外做小样本真实模型 smoke：不打印明文 key，不大规模消耗，不把真实外网调用放进默认 pytest。

## 7. 归档索引

- 历史完整计划：`completed/living-novel-engine-iteration-plan-legacy-2026-06-01.md`
- 已收口专项索引：`completed/README.md`
- 完整变更日志：`project-changelog.md`
- 当前主线 PRD：`unfinale-world-sandbox-remodel-prd.md`
- 开工自检：`unfinale-ai-development-alignment-checklist.md`
