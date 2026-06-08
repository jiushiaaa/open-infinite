# 未终章当前迭代路线

> 用途：给下一位 Agent 判断“现在该做什么”。最新事实以 `../memory.md` 为准；当前优化项见 `unfinale-current-optimization-backlog.md`；完整历史见 `history/project-changelog.md`；旧长版计划已归档到 `completed/living-novel-engine-iteration-plan-legacy-2026-06-01.md`。

## 0. 当前结论

当前默认主线是 **World Sandbox Loop / 小说世界沙盘体验深化**。S1-S9 已有第一版 service/API/UI/artifact/tests，且最近产品化切片已经把世界入口、卷宗阅读、世界自演结果、作者采纳、编辑后定稿、确认入卷和下一轮入口串成可操作链路。

下一阶段不再扩张支撑层，而是把“第一版可用”打磨成“用户能感到世界真的在运行”。

## 1. 已完成第一版的路线段

| 段落 | 当前状态 |
| --- | --- |
| 世界入口 | 世界书架、世界锚定房间、WorldWorkspaceShell、WorldRunway 和卷宗速览已有第一版 |
| 天命书 | AI 预抽、确认、快照、候选承载者和世界线初始状态已有第一版 |
| 沙盘轮次 | 多 Agent 沙盘、LLM decision advisory、策略博弈结果和可读化入口已有第一版 |
| 主观记忆 | 角色个人记忆链、主观记忆 delta、角色卷和势力卷已有第一版 |
| 干预与代偿 | 干预约束、L5 觉醒/模因传播、因果债、代偿和后果状态已有第一版 |
| 世界自演 | 检查点、可读结果页、世界线状态和跑后行动台已有第一版 |
| 阅读与正文 | 多视角正文、连续阅读、正文证据锚点、事件多视角和跨事件长线卷已有第一版 |
| 作者链路 | Reviewer 局部重写、勾选采纳、编辑后定稿、确认入卷和下一章入口已有第一版 |

这些内容不再作为根文档里的待办长表展示。需要追溯某一刀时读 `history/project-changelog.md` 和 `completed/README.md`。

## 2. 当前下一刀候选

下一刀从 `unfinale-current-optimization-backlog.md` 选，优先顺序：

1. 真实 LLM 多 Agent 多轮策略博弈。
2. 长正文与连续阅读质量。
3. 跨章节误会与伏笔回收。
4. Reviewer 整章风格润色与真实模型编辑器。
5. 世界状态长期化和下一轮真实决策消费。

每一刀都要能被 Web UI 直接看见，不只停在 API、artifact 或测试里。

## 3. 暂停线

默认暂停：

- GraphRAG / Zep / Temporal Memory 重型 provider 试验。
- 默认 hybrid vector 替换 BM25。
- OpenAPI / typed client 面板深化。
- 发行安装包、服务器在线体验、多租户、认证、对象存储、计费。
- LangGraph / OASIS / CAMEL 等框架替换。
- 纯工程健康报告，但没有新的世界体验。

支撑层追溯见 `completed/support-layer-enhancement-index.md`；发行路径见 `postponed/distribution-phase-plan.md`。

## 4. 下一刀成功标准

一个切片完成时至少满足：

1. 目标明确对应“世界会运行、角色会自主、角色会记得、干预有后果、角色可能反抗、世界会代偿、章节来自世界演化”之一。
2. 代码改动保持 additive，不破坏既有 artifact 契约。
3. API 失败降级为明确 400/404/409，前端有空态或修复提示，不白屏。
4. 前端入口遵循世界内部卷宗/结果页/作者台组织，不继续堆进旧工程面板。
5. 完成后同步 `../memory.md`、相关 PRD/README/handoff、本路线和 `history/project-changelog.md`。

## 5. 常用验证

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

docs-only 任务至少跑 `git diff --check`，并用搜索确认入口文档没有旧路径、旧基线或把支撑层误写成当前下一刀。
