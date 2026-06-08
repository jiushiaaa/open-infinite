# 未终章当前后续优化清单

> 用途：集中存放“已经有第一版，但还值得继续打磨”的主线优化项。入口文档只保留结论和链接，不再把完成项、支撑层和后置发行计划重复显示在根目录。

## 0. 使用规则

- 本文件只收当前世界沙盘主线的后续优化，不收 provider、GraphRAG、检索评测、发行、商业化等支撑层事项。
- 每一项进入开发前，先回到 `../memory.md` 和 `unfinale-ai-development-alignment-checklist.md` 复核是否仍是当前主线。
- 完成某一项后，把“已完成第一版”的证据收回 `../memory.md`、相关 PRD/README/handoff，并追加 `history/project-changelog.md`。
- 如果某项已经从“优化项”变成“收口专项”，新建或移动到 `completed/`，不要继续留在本清单里。

## 1. 已完成第一版，但继续优化

| 优先级 | 方向 | 当前证据 | 下一步应优化 |
| --- | --- | --- | --- |
| P0 | 真实 LLM 多 Agent 策略博弈 | `world_sandbox` service/API/UI/tests 已有策略结果和可读化入口 | 多轮规划、长期关系、势力资源、隐瞒/试探/误判、失败与反抗跨轮结算 |
| P0 | 长正文与连续阅读质量 | `continuous_reading_chapter`、卷宗阅读页和下一章接力台已有第一版 | 更自然章节节奏、视角稳定、真实文风一致性、结尾悬念和跨章承接 |
| P0 | 跨章节误会与伏笔回收 | 正文证据锚点、长线卷、事件多视角和跨章回收清单已有第一版 | 误会图谱、伏笔状态、回收触发、证据跨卷联动和下一轮沙盘消费 |
| P1 | Reviewer 与作者定稿 | 局部重写、勾选采纳、编辑后定稿、确认入卷已有第一版 | 整章风格润色、可回滚对照、真实模型编辑器、质量门和编辑意图保持 |
| P1 | 世界状态长期化 | `consequence_state`、因果债、世界线状态和主观记忆已有第一版 | 跨章节发酵、人工确认、长期代偿、角色记忆消费和状态冲突解释 |
| P1 | 卷宗与世界内部导航 | 世界书架、世界锚定房间、WorldWorkspaceShell、WorldRunway、卷宗入口已有第一版 | 更清晰的世界内部卷宗分区、移动端可读性、跳转语义和机制档案收纳 |
| P2 | 真实样本验收 | 默认测试隔离外网，产品验收允许小样本 opt-in smoke | 选固定样本，记录真实模型读感差距，不把真实调用放进默认 pytest |

## 2. 暂不进入默认下一刀

这些方向已有资料或历史闭环，但不应从本清单直接派生任务：

- GraphRAG / Zep / Temporal Memory 重型 provider 试验。
- 默认 hybrid vector 替换 BM25。
- OpenAPI / typed client 面板深化。
- 发行安装包、服务器在线体验、多租户、认证、对象存储、计费。
- LangGraph / OASIS / CAMEL 等框架替换现有 runner。
- 纯工程健康报告、readiness gate 或 checklist，但没有新的小说世界体验。

对应追溯入口：

| 类型 | 入口 |
| --- | --- |
| 已收口支撑层 | `completed/support-layer-enhancement-index.md` |
| 后置发行路径 | `postponed/distribution-phase-plan.md` |
| 阶段归类历史 | `completed/productization-phase-map.md` |
| 完整历史日志 | `history/project-changelog.md` |

## 3. 下一刀判定问题

开工前至少回答：

1. 这一刀会让“世界会运行、角色会自主、角色会记得、干预有后果、角色可能反抗、世界会代偿、章节来自世界演化”中的哪一项更强？
2. 用户是否能在 Web UI 中直接看见结果，而不是只在 API、artifact 或测试里看见？
3. 这是否复用了现有世界/卷宗/作者台入口，而不是继续往旧工程面板堆功能？
4. 是否保持 artifact/API additive，不破坏 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`？
5. 完成后需要同步哪些文档，哪些旧条目应该归档而不是继续显示在根目录？
