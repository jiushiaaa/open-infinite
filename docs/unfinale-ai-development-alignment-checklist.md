# 未终章 AI 开发对齐检查清单

> 用途：给 Codex / Cursor / 其他开发 Agent 开工前自检，避免把已收口支撑层误当成当前主线。当前事实以 `../memory.md` 为准；世界沙盘执行路线以 `unfinale-world-sandbox-remodel-prd.md` 为准。

## 1. 开工前必读

只要任务涉及未终章、`engine/`、产品 UI、API、runner、记忆、世界线或文档，先读：

1. `../memory.md`
2. `../AGENTS.md`
3. `index.md`
4. `unfinale-world-sandbox-remodel-prd.md`
5. `living-novel-engine-iteration-plan.md`
6. `../engine/README.md`
7. 需要愿景判断时读 `unfinale-product-vision-correction-draft.md` 与 `living-novel-engine-prd.md`

若这些文档与聊天摘要冲突，以 `memory.md`、`index.md` 和世界沙盘 PRD 为准。

## 2. 当前唯一默认主线

默认主线是继续深化小说世界沙盘：

```text
导入 / 创世
  -> AI 预抽并确认《天命书》
  -> 多 Agent 世界沙盘轮次
  -> 角色主观记忆链
  -> 世界状态、锚点、因果债和代偿持续变化
  -> 世界自演检查点
  -> 读者干预经干预编译器投放
  -> 多视角活体小说和连续阅读
  -> 作者采纳、局部重写、编辑后定稿、确认入卷
```

World Sandbox Loop S1-S9、卷宗阅读页、自演结果可读入口、Reviewer 局部重写采纳、编辑后定稿和确认入卷反哺下一轮入口已经是第一版产品链路。后续不是“证明它存在”，而是让它更真实、更好读、更可用。

## 3. 这一刀是否该做

开工前逐项回答：

| 问题 | 通过条件 |
| --- | --- |
| 它是否让世界更像会运行？ | 状态、锚点、因果债、检查点或世界线会被用户看见并延续 |
| 它是否让角色更自主？ | 行动会受私有目标、主观记忆、信任/怀疑、误判、风险或利益影响 |
| 它是否让角色更会记得？ | 角色个人记忆链、误解、秘密或世界线残影被写入并被下一轮消费 |
| 它是否让干预有后果？ | 干预会被编译、投放、吸收、抵抗、反噬、分叉或生成代偿 |
| 它是否让章节来自世界演化？ | 正文、brief、Reviewer 或作者采纳能引用沙盘事实和世界状态 |
| 它是否让用户体验更像小说？ | 默认是阅读、卷宗、角色视角、事件多视角或作者可写材料，而不是 JSON/工程面板 |

如果全部答不上来，这一刀大概率跑偏。

## 4. 当前优先候选

当前主线优先做：

- 真实 LLM 多 Agent 策略博弈：多轮规划、长期关系、势力资源、欺骗/隐瞒/试探、反抗/妥协和失败结算。
- 长正文与连续阅读：开场钩子、场景推进、人物动机、冲突递进、视角切换、伏笔回收、结尾悬念。
- 正文内证据锚点与误会图谱：阅读时自然展开证据，不打断正文。
- 更强真实语义 Reviewer：人物动机、冲突张力、世界状态入文、视角稳定、记忆使用和章节好读度。
- 整章风格润色和真实模型编辑器：从片段级改写继续走向整章定稿。
- 角色/势力独立卷：让角色个人卷和势力卷可长期阅读、追踪和回看。
- 世界自演醒来报告文学化：让结果页像一夜世界发生过事情，而不是运行摘要。

## 5. 默认不做

除非用户明确点名，以下都不是下一刀：

- GraphRAG / Zep / Temporal Memory provider spike。
- 真实向量检索收益评测或默认 hybrid vector 替换 BM25。
- provider / cost / route matrix 继续扩张。
- OpenAPI / typed client 深化。
- 发行、桌面打包、对象存储、云端多租户、认证、计费。
- 继续往 `WorkspacePage.tsx` 堆工程面板、状态面板或只读报告。
- 只做 readiness gate、checklist、证据汇总，但没有新的小说世界体验。

支撑层可以被复用，但必须服务当前主线。

## 6. 代码接入判断

优先复用现有底座，并按世界内部卷宗重组：

| 现有能力 | 当前语义 |
| --- | --- |
| `ImportNovelPage.tsx` | 世界书架里的“导入故事世界” |
| `GenesisPage.tsx` | 世界书架里的“新建世界” |
| `WorldAnchorPage.tsx` | 《天命书》确认与世界锚定 |
| `WorkspacePage.tsx` | 旧工程支撑入口，不继续堆主体验面板 |
| `DossierReadingPage.tsx` | 世界内部卷宗阅读入口，默认连续正文，证据折叠 |
| `intervention_compiler/*` | 读取《天命书》后编译干预 |
| `multi_agent` runner / trace | 沙盘轮次与角色行动轨迹 |
| `runtime_memory.py` | 检索辅助层，不替代角色主观记忆链 |
| `worldline_judge` / `causal_diff` | 世界线、锚点转移、作者采纳台支撑 |

## 7. Artifact / API 边界

新增内容必须 additive，不破坏：

- `chapter.md`
- `events.json`
- `state_snapshot.json`
- `multi_agent_trace.json`
- `causal_diff.json`

HTTP-facing identifier 必须安全校验；失败返回明确 400/404/409；坏 artifact 降级为空态、需留意或需修复，不白屏、不 500。

不要改 `run_scene` 默认行为，除非用户明确要求进入 runner 重构。

## 8. 真实模型验收

涉及叙事质量、Agent 决策、章节 brief、多视角正文、Reviewer 或视觉生成时：

- mock / deterministic 回归必须保留。
- 小样本真实模型 smoke 应作为产品体验验证。
- 不打印明文 key。
- 不把真实外网调用放进默认全量 pytest。
- 记录真实输出暴露的问题，不只看结构是否存在。

## 9. 完成判断

完成前确认：

- 用户是否能从 Web UI 或 API 直接体验能力，CLI 不是唯一入口。
- 文案是否中文，风格是否仍是古风纸面、克制系统感。
- 结果是否进入世界状态、角色记忆、章节材料、作者采纳或阅读入口。
- 是否补 focused tests、必要 build/smoke、`git diff --check`。
- 是否同步 `memory.md`、世界沙盘 PRD、路线图、README、handoff 和 changelog 中相关事实。
- 是否只提交本轮文件，不提交 `.local-run/` 或 `engine/.local-run/`。

如果只是“新增一块状态面板”而没有加强世界沙盘体验，不要宣布阶段完成。
