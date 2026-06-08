# 未终章世界沙盘主线 PRD

> 用途：定义当前最高主线。实现事实以 `../memory.md` 为准；下一步优化项集中在 `unfinale-current-optimization-backlog.md`；完整历史见 `history/project-changelog.md`。

## 1. 目标

把未终章从“续写工具”推进为“会自我运行的小说世界”：

```text
导入 / 创世
  -> AI 预抽并确认《天命书》
  -> 多 Agent 世界沙盘轮次
  -> 角色主观记忆链
  -> 读者干预与世界线代偿
  -> 世界自演检查点
  -> 多视角活体小说 / 连续阅读
  -> 作者采纳台 / Reviewer / 下一章入口
```

## 2. 当前第一版闭环

| 模块 | 已有第一版 |
| --- | --- |
| 世界入口 | 世界书架、世界锚定房间、WorldWorkspaceShell、WorldRunway、移动端折叠导航、全局续读 |
| 天命书 | AI 预抽、确认、快照、候选承载者、世界线初始规则 |
| 沙盘轮次 | 多 Agent 决策、LLM decision advisory、策略博弈 readout、sandbox artifact |
| 主观记忆 | 角色个人记忆链、角色卷、势力卷、subjective memory delta |
| 干预与代偿 | 干预约束、L5 觉醒/模因传播、因果债、consequence_state |
| 世界自演 | autopilot report、检查点、可读结果页、跑后行动台 |
| 阅读产物 | 多视角正文、连续阅读正文、事件多视角、跨事件长线卷、正文证据锚点 |
| 作者链路 | Reviewer 局部重写、勾选采纳、编辑后定稿、确认入卷、下一章入口 |

这说明 S1-S9 已经不是“未做主线”，而是“第一版已闭环，继续深化质量”。

## 3. 产品导航

当前主导航按世界组织：

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

“沙盘 / 阅读 / 干预 / 作者”是同一个世界里的场景能力，不是一级工作区。新增能力优先进入世界内部卷宗、结果页、检查点或作者台，不继续堆进旧工程面板。

## 4. 主真源

| 真源 | 说明 |
| --- | --- |
| 天命书 | 命运锚点、候选承载者、世界惯性、可挑战规则 |
| worldline_state | 世界线状态、因果债、代偿、检查点和章节历史 |
| subjective_memory.jsonl | 角色独立主观记忆链 |
| sandbox_rounds.jsonl | 沙盘轮次和角色行动证据 |
| author_adoption_ledger.jsonl | 作者采纳、编辑后定稿、确认入卷记录 |

章节是观察窗口，不是唯一真源。

## 5. 当前真实优化方向

详见 `unfinale-current-optimization-backlog.md`。当前优先：

1. 真实 LLM 多 Agent 多轮策略博弈。
2. 长正文与连续阅读质量。
3. 跨章节误会与伏笔回收。
4. Reviewer 整章风格润色与真实模型编辑器。
5. 世界状态长期化和下一轮真实决策消费。

## 6. 非目标

默认不做：

- GraphRAG / Zep / Temporal Memory 重型 provider 试验。
- 默认 hybrid vector 替换 BM25。
- OpenAPI / typed client 面板深化。
- 发行安装包、服务器在线体验、多租户、认证、对象存储、计费。
- LangGraph / OASIS / CAMEL 替换现有 runner。
- 纯工程健康报告，但没有新的小说世界体验。

## 7. 验收口径

完成某一刀时，不只问“有 API / 有测试 / 有页面 / 有 artifact”，还要问：

- 用户是否能看到角色被记忆驱动？
- 干预是否进入世界并产生后果？
- 世界状态是否持续变化？
- 角色是否可能反抗或误判？
- 章节是否来自世界演化，而不是孤立续写？
- 作者是否能把结果采纳、编辑、定稿并接到下一章？

## 8. 验证

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

docs-only 任务至少运行 `git diff --check`，并搜索确认旧完成项、支撑层和后置发行路径没有重新变成根目录待办。
