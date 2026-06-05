# 未终章 AI 开发对齐检查清单

> 用途：给后续 Codex / Cursor / 其他开发 Agent 做开工前自检，避免继续沿着旧的工程化面板、provider spike 或检索评测方向跑偏。
> 当前主 PRD：`unfinale-world-sandbox-remodel-prd.md`。
> 2026-06-05 状态：World Sandbox Loop v1-v8 已完成第一版可运行闭环；S4 已新增沉浸模式 / 暴走 AU 投放选择，AK47 等异物干预可本土化重释或写世界线《天命书》快照。本次继续补上可持续世界线状态、L5 觉醒反抗、因果债持续驱动、自演任务状态、多视角正文证据链和作者采纳反哺下一章 brief。本清单后续用于判断“是否在加深活体小说体验”，而不是继续证明这些模块是否存在。

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

默认开发方向已经从“搭建 v1-v8 第一版”切换为“强化 v1-v8 的真实体验”：

```text
导入 / 创世
  -> AI 预抽并确认《天命书》
  -> 多 Agent 沙盘轮次
  -> 角色主观记忆链
  -> 世界自演检查点
  -> 多视角活体小说
  -> 作者采纳台
```

上述链路已有本地 deterministic service/API/UI/artifact 第一版。后续每一刀都应该让这些能力更像一个会运行的小说世界，而不是再新增一张只读报告。

每一刀都必须能回答至少一个问题：

- 用户是否看到了角色真的在行动？
- 用户是否看到了某个角色自己的主观记忆变化？
- 用户是否看到了世界状态、世界线、锚点或因果债变化？
- 用户是否能从沙盘结果得到可读章节、角色个人卷、事件多视角或作者可采纳素材？

如果答案全是否，这一刀大概率跑偏。

如果一刀只是在已有 v1-v8 外面再套一层 checklist、readiness、状态汇总或 provider 评估，也大概率跑偏。

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

## 5. 已落地的第一批 artifact 与下一步

新增 artifact 必须 additive，不破坏既有 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。

第一版已落地：

- `projects/<slug>/tianming.json`
- `projects/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective_memory.jsonl`
- `outputs/<run_id>/sandbox_rounds.jsonl`
- `outputs/<run_id>/subjective_memory_delta.json`
- `outputs/<run_id>/tianming_delta.json`
- `outputs/<run_id>/autopilot_report.json`
- `outputs/<run_id>/character_lens_briefs.json`
- `projects/<slug>/author_adoption_ledger.jsonl`
- `outputs/<run_id>/author_adoption_record.json`
- `outputs/<run_id>/author_adoption_brief.md`

仍需补强：

- `outputs/<run_id>/event_materials.json` 或等价事件材料账本，目前多视角 brief 已存在，但事件材料化还不够独立。
- 世界线《天命书》快照第一刀已存在：L4/L5 / AU 预编译可写 `worldlines/<worldline_id>/tianming_snapshot.json` 且不覆盖根天命书；本次新增 `worldlines/<worldline_id>/worldline_state.json`，记录快照审计状态、来源干预、分支承接、因果债、锚点状态、候选承载者、模因污染和作者采纳反哺，后续沙盘会读取它。
- 持久世界状态 ledger 已有第一版：`worldline_state.json` 已成为下一轮沙盘输入；仍需把代偿代价从文字解释进一步具象为地点、势力、资源、伤势、公开舆论等世界内状态。
- 章节 brief / 正文产物已有第一版：`character_lens_volumes.json` 生成世界正史卷、主锚点卷、角色个人卷和事件多视角正文；`next_chapter_brief.json` 由作者采纳生成并回写世界线状态；仍需接入更正式的章节生成入口和真实 LLM 长文质量控制。

## 6. 已落地的第一批 API 与下一步

第一版已落地：

- `GET /api/stories/<slug>/tianming`
- `POST /api/stories/<slug>/tianming/generate`
- `POST /api/stories/<slug>/tianming/confirm`
- `POST /api/stories/<slug>/tianming/intervention-compile`
- `POST /api/stories/<slug>/sandbox/run`
- `GET /api/sandbox-runs/<run_id>`
- `GET /api/stories/<slug>/worldlines/<worldline_id>/characters/<character_id>/subjective-memory`
- `POST /api/stories/<slug>/narrative-compensation/run`
- `POST /api/stories/<slug>/world-autopilot/run`
- `POST /api/stories/<slug>/character-lens/generate`
- `POST /api/stories/<slug>/author-adoption`

仍需补强：

- `GET /api/stories/<slug>/events/<event_id>/perspectives`：读取已发生事件的多视角和证据链，而不是每次生成新 brief。
- `GET /api/stories/<slug>/character-lens/<character_id>`：读取某角色连续个人卷。
- 世界自演任务的启动、暂停、恢复、进度查询和 checkpoint 回放 API 已有本地同步任务第一版；仍未做后台队列、长时运行守护和中断自动恢复。
- 作者采纳后的章节 brief / 大纲差异 / Reviewer 修订 API 已有第一版；仍需接入章节生成入口和更强 Reviewer。

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

当前 UI 已有：

- 世界沙盘页。
- 天命书页。
- 多视角活体小说页。
- 作者采纳台页。

仍需补齐：

- 完整 `WorldWorkspaceShell`。
- 世界正史卷 / 主锚点卷独立页面。
- 角色个人卷连续阅读页。
- 事件多视角详情页。
- 世界线 / 检查点页。
- 机制档案页，把旧工程面板收纳到支撑层。

## 8. 后续默认迭代判断

后续任务优先选择以下方向：

1. S4 分支持续运行 / 快照审计确认：在 S4 已能把编译结果投放进单轮沙盘并选择沉浸模式 / 暴走 AU 后，补用户确认后的分支持久继续运行、L4/L5 世界线快照审计确认和多轮分支追踪。
2. L5 觉醒反抗：让高觉醒角色能拒绝、假意服从、欺骗读者、保护他人或传播高维真相。
3. 主观记忆继续加深：在 S2 已有误会/盲区字段后，补长期召回、记忆压缩/遗忘、压抑记忆爆发、误会图谱和“角色不知道的正史事实”对照。
4. Agent 决策继续加深：下一轮可在显式 opt-in 下接真实模型 runner smoke，但默认仍保留 deterministic/mockable 基线。
5. 世界状态持久化：世界线代偿、因果债和锚点变化能驱动后续轮次。
6. 多视角正文：从 brief 升级到可读章节和连续角色个人卷。
7. 作者采纳反哺：采纳结果能生成下一章 brief 并影响后续沙盘。

## 9. 验收口径

第一版不要追求重型架构。优先本地 JSON / JSONL、确定性 mock、可测 service/API/UI。

但后续 S1-S9 不能再把“最小闭环”当成最终完成。每次复盘都必须区分两层：

| 层级 | 含义 | 是否足够收口 |
| --- | --- | --- |
| 工程底线 | 有 service/API/UI/artifact/tests，能稳定跑通。 | 不足够，只能说明可以继续迭代。 |
| 产品能力成立 | 用户能实际感到角色会自主、会记得、干预有后果、世界会代偿、章节来自世界演化。 | 可以作为阶段收口依据。 |

后续 AI 如果完成了一个小切片，不应自动停在“测试通过”。它需要继续检查该切片属于 S1-S9 哪个阶段，并判断阶段验收是否真正满足；若没有满足，应把未满足项写入下一轮迭代，而不是宣布完整完成。

当前正在执行的 S1-S9 不需要中途推翻。等这一轮完成后，统一按本口径检查；若没有全部达到产品能力成立，第三轮迭代从未达标项继续。

2026-06-04 补充：S1 `Agent Decision Deepening MVP` 已让角色行动记录新增决策输入、外在行动、真实意图、风险和行动结果，并通过第二轮记忆影响行动的 focused test。下一刀优先 S2，把这些行动证据写成更细的主观心理和信息差；真实 API 可做显式 smoke，不进入默认 pytest 基线。

2026-06-04 补充：S2 `Subjective Memory Psychology MVP` 已让主观记忆记录角色感知、内心想法、推测动机、误会、未知正史、秘密可见性和异常权重，并通过同一事件双角色矛盾记忆与下一轮误会冲突的 focused test。下一刀优先 S3《天命书》世界线宪法，或继续 S2 的长期召回/误会图谱。

2026-06-04 补充：S3 `Tianming Worldline Constitution MVP` 已让《天命书》记录吸引子权重/类别、多锚点和四档压力；旧版已确认天命书会保守补齐 S3 字段且保留既有吸引子；L4/L5/AU 干预可写世界线《天命书》快照并保持根文件不覆盖。下一刀优先 S4 干预可执行投放，让编译结果进入下一轮沙盘约束。

2026-06-04 补充：S4 `Intervention Execution Constraint MVP` 已让世界沙盘 `sandbox/run` 可选接收干预文本，读取《天命书》编译为 `intervention_constraint.json`，并进入本轮角色决策、冲突、信息流和世界状态 delta；世界沙盘页可填写干预并查看法则吸收、分支轴和因果债。下一刀继续 S4 的沉浸/AU 确认与分支继续运行，或进入 S5 L5 觉醒反抗。

### 9.1 真实模型 smoke 口径

用户已明确允许本项目在验收时调用其真实接入的模型 API。后续不要只用 mock / deterministic 输出判断叙事体验是否合格。

执行规则：

- 单元测试、契约测试、回归测试仍默认 mock-safe，保证稳定、低成本、可复现。
- 涉及 Agent 决策、角色反抗、章节 brief、多视角正文、Reviewer、视觉资产等生成质量的切片，完成 mock 回归后必须尝试小样本真实模型 smoke。
- 若 `.env` 中没有可用 key、外网失败或 provider 报错，需要在验收结论里明确说明“真实 smoke 未完成”的原因。
- 真实 smoke 不打印明文 key，不记录完整敏感请求，不做大批量生成；只保留脱敏配置状态、输入摘要、输出质量观察、失败原因和是否回退。
- 真实 smoke 的目标不是替代 pytest，而是发现 mock 看不到的真实模型问题，例如角色决策空泛、长文本失焦、记忆没有被消费、反抗不自然、文风不稳定。

每个独立切片完成时至少同步：

- `memory.md`
- `docs/living-novel-engine-iteration-plan.md`
- `docs/unfinale-world-sandbox-remodel-prd.md` 或相关 PRD
- `docs/project-changelog.md`

每个独立切片完成且验证通过后，默认还必须完成远程同步：

- 先运行 `git status`，确认哪些文件属于本轮工作。
- 只提交本轮自己负责的文件，不把用户改动、另一轮 AI 的未完成改动或无关脏文件混进提交。
- 提交后推送到远程仓库；若没有远程、没有上游分支、认证失败或网络失败，必须在结论里明确说明。
- 如果当前正在进行长任务且工作树还未收口，不要为了“及时推送”强行推半成品；应在 checkpoint 处提交/推送可验证的独立切片。

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
