# 未终章 AI 开发对齐清单

> 用途：每次开工前确认下一刀没有从“世界沙盘产品体验”滑回支撑层扩张。当前事实以 `../memory.md` 为准；具体优化池见 `unfinale-current-optimization-backlog.md`。

## 1. 先问一句

这一刀会让用户更明显地感到哪一件事？

```text
世界会运行。
角色会自主。
角色会记得。
干预有后果。
角色可能反抗。
世界会代偿。
章节来自世界演化。
```

如果答不上来，先不要写代码。

## 2. 当前主线判断

| 问题 | 是 | 否 |
| --- | --- | --- |
| 是否发生在某个故事世界内部，而不是抽象工程面板？ | 继续 | 重新拆 |
| 是否强化天命书、沙盘轮次、主观记忆、干预、代偿、正文或作者采纳？ | 继续 | 重新拆 |
| 用户是否能在 Web UI 里看到结果？ | 继续 | 补产品入口 |
| 是否保持 API/artifact additive？ | 继续 | 收缩方案 |
| 是否避免默认真实外网消耗？ | 继续 | 改成 opt-in smoke |

## 3. 推荐下一刀池

从 `unfinale-current-optimization-backlog.md` 选：

1. 真实 LLM 多 Agent 策略博弈。
2. 长正文与连续阅读质量。
3. 跨章节误会与伏笔回收。
4. Reviewer 整章风格润色与真实模型编辑器。
5. 世界状态长期化和下一轮真实决策消费。

## 4. 默认暂停

除非用户明确点名，不做：

- GraphRAG / Zep / Temporal Memory 重型 provider 试验。
- 默认 hybrid vector 替换 BM25。
- provider / cost / route matrix 扩张。
- OpenAPI / typed client 面板深化。
- 发行安装包、云端部署、多租户、认证、对象存储、计费。
- LangGraph / OASIS / CAMEL 替换现有 runner。
- 纯工程健康报告，但没有新的小说世界体验。

支撑层追溯见 `completed/support-layer-enhancement-index.md`；发行路径见 `postponed/distribution-phase-plan.md`。

## 5. 实施纪律

- 不改 `run_scene` 默认行为，除非用户明确要求 runner 重构。
- 不破坏 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 后端 HTTP-facing identifier 必须安全校验；坏输入返回明确 400/404/409。
- 前端坏 artifact 降级为空态、需留意或需修复，不白屏。
- 用户级能力优先 Web UI + API；CLI 只做开发者/自动化外壳。
- 不泄漏 API key；设置页和日志只展示脱敏尾号。

## 6. 完成前检查

1. 是否有 focused test 或 docs-only 验证？
2. 是否跑过对应验证命令？
3. 是否同步 `../memory.md`、相关 PRD/README/handoff？
4. 是否追加 `history/project-changelog.md`？
5. 是否搜索确认旧完成项、支撑层或后置路径没有重新出现在根入口里？
