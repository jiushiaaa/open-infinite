# 未终章 AI 开发对齐检查清单

> 用途：给后续 Codex / Cursor / 其他开发 Agent 做开工前自检，避免继续沿着旧的工程化面板、provider spike 或检索评测方向跑偏。
> 当前主 PRD：`unfinale-world-sandbox-remodel-prd.md`。

## 1. 开工前必读

只要任务涉及未终章、`engine/`、产品 UI、API、runner、记忆、世界线或文档，先读：

1. `../memory.md`
2. `../AGENTS.md`
3. `unfinale-world-sandbox-remodel-prd.md`
4. `unfinale-product-vision-correction-draft.md`
5. `living-novel-engine-iteration-plan.md`
6. `living-novel-engine-prd.md`
7. `../engine/README.md`

若这些文档与聊天摘要冲突，以 `memory.md` 和 `unfinale-world-sandbox-remodel-prd.md` 为准。

## 2. 当前唯一默认主线

默认开发方向是：

```text
导入 / 创世
  -> AI 预抽并确认《天命书》
  -> 多 Agent 沙盘轮次
  -> 角色主观记忆链
  -> 世界自演检查点
  -> 多视角活体小说
  -> 作者采纳台
```

每一刀都必须能回答至少一个问题：

- 用户是否看到了角色真的在行动？
- 用户是否看到了某个角色自己的主观记忆变化？
- 用户是否看到了世界状态、世界线、锚点或因果债变化？
- 用户是否能从沙盘结果得到可读章节、角色个人卷、事件多视角或作者可采纳素材？

如果答案全是否，这一刀大概率跑偏。

## 3. 不要默认继续做的方向

以下能力已经降为支撑层。除非用户明确点名，不作为下一刀：

- GraphRAG / Zep / Temporal Memory provider spike
- 真实向量检索收益评测、hybrid vector 默认替换 BM25
- OpenAPI / typed client 继续细化
- 发行、桌面打包、对象存储、云端多租户、认证、计费
- 继续往 `WorkspacePage.tsx` 堆工程面板、状态面板或只读报告
- 只做指标、证据链、readiness gate、checklist，而没有新的小说世界体验

## 4. 代码接入判断

优先复用现有底座，但要按新产品语义重组：

| 现有能力 | 新方向 |
| --- | --- |
| `ImportNovelPage.tsx` | 世界书架里的“导入故事世界” |
| `GenesisPage.tsx` | 世界书架里的“新建世界” |
| `WorldAnchorPage.tsx` | 《天命书》确认页 |
| `WorkspacePage.tsx` | 拆为世界内部卷宗壳，不继续堆面板 |
| `intervention_compiler/*` | 每次读取《天命书》后再编译干预 |
| `multi_agent` runner / trace | 沙盘轮次与角色行动轨迹 |
| `runtime_memory.py` | 可辅助检索，但不能替代角色主观记忆链 |
| `worldline_judge` / `causal_diff` | 世界线、锚点转移、作者采纳台支撑 |

## 5. 第一批目标 artifact

新增 artifact 必须 additive，不破坏既有 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。

建议优先落地：

- `projects/<slug>/tianming.json`
- `projects/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective_memory.jsonl`
- `outputs/<run_id>/sandbox_rounds.jsonl`
- `outputs/<run_id>/subjective_memory_delta.json`
- `outputs/<run_id>/event_materials.json`
- `outputs/<run_id>/tianming_delta.json`
- `outputs/<run_id>/autopilot_report.json`
- `outputs/<run_id>/character_lens_briefs.json`

## 6. 第一批目标 API

建议优先落地：

- `GET /api/stories/<slug>/tianming`
- `POST /api/stories/<slug>/tianming/confirm`
- `POST /api/stories/<slug>/sandbox/run`
- `GET /api/sandbox-runs/<run_id>`
- `GET /api/stories/<slug>/worldlines/<worldline_id>/characters/<character_id>/memories`
- `GET /api/sandbox-runs/<run_id>/events/<event_id>/perspectives`
- `GET /api/sandbox-runs/<run_id>/character-lens`
- `POST /api/sandbox-runs/<run_id>/author-adoptions`

API 规则沿用项目硬约束：identifier 安全校验；失败返回明确 400/404/409；坏 artifact 降级为空态或需修复，不白屏、不 500。

## 7. 前端骨架口径

一级导航是“世界书架”，不是“沙盘 / 阅读 / 干预 / 作者”四大工作区。

进入某个世界后，使用世界内部卷宗：

```text
天命书
世界沙盘
世界正史卷
主锚点卷
角色个人卷
势力卷
事件多视角
世界线
检查点
作者采纳台
机制档案
```

读者模式和作者模式权限原则相同；作者采纳台在作者模式更突出。

## 8. 验收口径

第一版不要追求重型架构。优先本地 JSON / JSONL、确定性 mock、可测 service/API/UI。

每个独立切片完成时至少同步：

- `memory.md`
- `docs/living-novel-engine-iteration-plan.md`
- `docs/unfinale-world-sandbox-remodel-prd.md` 或相关 PRD
- `docs/project-changelog.md`

常规验证：

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

如果只是文档改造，可以不跑后端/前端测试，但必须运行 `git diff --check` 并说明未跑代码测试的原因。
