# Codex Handoff — 未终章

> 用途：新开 Codex 窗口时的最小接力包。本文件只给启动摘要，不替代 `../memory.md`、`index.md` 或世界沙盘 PRD。
> 完整历史见 `project-changelog.md`；旧长接力稿见 `completed/codex-handoff-legacy-2026-06-01.md`。

## 新窗口第一条消息建议

```text
请先阅读并对齐：
- AGENTS.md
- memory.md
- docs/index.md
- docs/unfinale-world-sandbox-remodel-prd.md
- docs/unfinale-ai-development-alignment-checklist.md
- docs/living-novel-engine-iteration-plan.md
- engine/README.md

需要愿景判断时再读：
- docs/unfinale-product-vision-correction-draft.md
- docs/living-novel-engine-prd.md

需要 UI 风格时再读：
- docs/completed/v0.7-product-web-app-ui-spec.md
- docs/image/README.md

当前项目是未终章（Unfinale），核心代码在 engine/；技术缩写、包名、CLI 和环境变量前缀仍沿用 LNE / living_novel_engine。
当前默认主线是 World Sandbox Loop / 小说世界沙盘，不是 provider、GraphRAG、检索评测、OpenAPI、发行或商业化。
下一步应继续深化：真实 LLM 多 Agent 策略博弈、长正文/连续阅读质量、更深跨章误会回收、跨章节回收、更强真实语义 Reviewer、整章风格润色和世界状态长期发酵。
请不要只靠这段摘要；读完文档和相关代码后再动手。
```

## 当前事实速记

| 分类 | 当前状态 |
| --- | --- |
| 主线 | World Sandbox Loop / 小说世界沙盘体验深化 |
| 已完成第一版 | S1-S9 世界沙盘链路、世界书架推荐世界面板、世界书架故事卡下一步导览、导入/创世开卷中枢、卷宗阅读页、卷宗阅读移动端导读条、卷宗阅读余波承接台、卷宗阅读正文证据锚点/阅读进度/当前场景导读条/误会图谱、自演结果可读入口、Reviewer 局部重写采纳、编辑后定稿、确认入卷反哺下一轮入口、天命书首屏宪法封面、天命书移动端宪法速断条、世界线首屏工作流中枢、世界线移动端承接导读条、检查点首屏醒来回放中枢、检查点回放移动端醒来导读条、多视角首屏工作流中枢、多视角移动端分镜导读条、机制档案首屏中枢、机制档案移动端导读条、AppShell 世界位置条/世界体验轨道/全局续读入口/卷宗速览盘/移动端壳层压缩、世界内导览层 `WorldRunway`、作者采纳台工作流中枢/移动端材料入口、锚定页启动卡与世界状态条/世界卷宗总览、世界脉搏、当前旅程状态、本机最近阅读续航、角色个人卷独立页、角色个人卷移动端导读条、势力卷独立页、势力卷移动端导读条、事件多视角详情页、事件多视角移动端导读条、跨事件长线卷、长线卷移动端导读条、长线阅读进度、多事件索引、误会回收台、未解线索、沙盘运行导览与运行台分步化/首屏前置、沙盘结果承接台、沙盘策略棋盘、沙盘后续可能性回填下一轮、移动端世界卷宗导航盘与移动端保功能布局 |
| 当前测试基线 | `cd engine && python -m pytest -q` -> `951 passed`；`cd engine/ui && pnpm run build` 通过 |
| 当前文档分层 | 入口事实看 `memory.md`；文档地图看 `docs/index.md`；路线看 `docs/living-novel-engine-iteration-plan.md` |
| 支撑层 | v0.7-v1.0-local、后续增强四十五刀、真实 retrieval provider、Vector Retrieval Pipeline 都已收口为支撑层 |

## 最近世界沙盘链路

- `run_sandbox_round()` / `POST /api/stories/<slug>/sandbox/run` 可显式启用 `llm_decision_mode=advisory`，写入 `agent_decision_advisory.json` 与 `strategy_board`；默认 deterministic 不变。
- L5 觉醒和模因传播已写入角色主观记忆、世界线状态和 UI 可读传播读数。
- `worldline_state.json` 与 `consequence_state` 让因果债、锚点、具象代偿、作者采纳和确认稿进入后续沙盘读取链。
- `autopilot_report.json` 已有 `readable_entry`；世界沙盘结果页、检查点回放和世界线页都能导向最近关键检查点、角色个人卷、事件多视角和连续阅读。
- `DossierReadingPage` / `GET /api/stories/<slug>/worldlines/<worldline_id>/dossier-reading` 已把连续阅读稿、确认稿、跨卷宗 trail、多视角卷宗和 worldline dossier 组织成默认正文阅读页；正文卡已有卷首题签、阅读进度书签、当前场景导读条、分场景正文、段内证据锚点、可点击误会图谱、世界线/继续沙盘/作者台行动入口，移动端首屏还有“开始读正文 / 查卷宗 / 作者台”导读条。正文和关联卷宗之后新增“读完之后”余波承接台，可回看误会图谱、追长线卷、继续沙盘或送作者台；当前场景导读条可上一场/下一场、看证据和追误会，导读条三枚入口可把正文卡、卷宗目录或作者台带到用户面前；390px 已验无水平溢出。
- `CharacterVolumePage` / `#/world/<slug>/worldlines/<worldline_id>/characters/<character_id>` 已把单个角色的个人卷正文、主观记忆链、误会、未知正史、秘密可见性和证据锚点组织成独立页面；移动端首屏另有“读立场 / 查记忆 / 换角色 / 作者台”导读条，四枚入口可直接滚到对应区块或跳作者台；锚定页角色卡、沙盘角色行动卡、多视角角色卷和卷宗阅读角色卷都能进入。没有角色卷正文时会用主观记忆兜底显示角色索引和明确空态。
- `FactionVolumePage` / `#/world/<slug>/worldlines/<worldline_id>/factions/<faction_id>` 已把势力卷正文、势力目录、因果压力域、最近 ledger 和证据锚点组织成独立页面；移动端首屏另有“看站位 / 查代偿 / 换势力 / 作者台”导读条，四枚入口可直接滚到对应区块或跳作者台；锚定页势力标签、多视角势力卷和卷宗阅读势力卷都能进入。没有势力卷正文时会显示明确空态。
- `EventPerspectivePage` / `GET /api/stories/<slug>/worldlines/<worldline_id>/events/<event_id>/perspectives` / `#/world/<slug>/worldlines/<worldline_id>/events/<event_id>/perspectives` 已把同一事件的节拍、正文、信息差、误读列表、证据链和去卷宗阅读/角色卷/世界线/作者台动作组织成独立页面；移动端首屏另有“读事件 / 看信息差 / 查证据 / 作者台”导读条，四枚入口可直接滚到对应区块或跳作者台；卷宗阅读事件 tab 和多视角页事件正文都能进入。
- `LonglineReadingPage` / `GET /api/stories/<slug>/worldlines/<worldline_id>/longline-reading` / `#/world/<slug>/worldlines/<worldline_id>/longline` 已把连续阅读场景、卷宗、确认入卷、事件信息差和证据链组织成跨事件长线卷；首屏已有长线阅读进度、多事件索引、误会回收台和未解线索，移动端首屏另有“读长线 / 按事件追 / 回收误会 / 作者台”导读条，四枚入口可直接滚到对应区块或跳作者台；顶栏、世界线页、卷宗阅读页和事件详情页都能进入。
- `WorldRunway` 已接入世界沙盘、卷宗阅读、角色个人卷、势力卷、世界线档案、检查点回放和作者采纳台，用统一纸面导览说明当前位置、三步理解路径和下一步行动；沙盘页会按“投放事件 -> 观察角色 -> 进入阅读”引导用户。
- `AppShell` 移动端已把世界内部顶栏导航改成可换行卷宗盘，锚定、天命书、沙盘、阅读、长线卷、世界线、多视角、作者台和机制档案 9 个入口全部直接可见；桌面仍保持一行顶栏。顶栏下方已新增世界位置条和“定界 / 运行 / 阅读 / 采纳”体验轨道，按当前路由说明“当前位置”、页面职责和主动作/次动作；同一世界有最近阅读记录且当前不在该位置时，位置条动作区会显示全局“继续阅读”。位置条下方还有“正文 / 正史 / 锚点 / 角色 / 势力 / 事件 / 长线 / 世界线”卷宗速览盘，能从任意世界页切回具体阅读对象；移动端壳层已压缩，390px/360px 下 9 个顶栏入口、4 个阶段和 8 个卷宗入口均保留且无水平溢出，390px 主标题起点从约 524px 提前到 417px。
- `WorldSandboxPage` 已有沙盘运行导览、首屏运行台、结果承接台、策略棋盘和下一轮承接：运行台把操作重组为“写事件 / 可选干预 / 启动推演”，并前置到首屏 hero；桌面在右侧，390px 移动端排在导览前且“启动一轮推演”完整进入首屏。读者干预、投放对象、投放方式和真实模型建议仍保留为可选项；单轮结果后先显示“本轮已发生”承接区，汇总本轮事件、角色行动数、主观记忆数、因果债、锚点/资源/秘密变化和关键角色，并提供“读成正文 / 看世界线 / 生成多视角 / 再推一轮”。真实模型 advisory 写出 `strategic_interaction` 时，会在结果承接和角色行动链之间显示策略棋盘，解释谁在算计谁、私下目的、误判、风险和世界影响。底部后续剧情可能性可一键回填到运行台作为下一轮事件，并清空上轮临时干预，防止误重复投放。`POST /api/stories/<slug>/sandbox/run` 请求字段未变。
- `StoryEntryPage` 的首屏已接入推荐世界面板，按导入优先、已有沙盘结果次之、原顺序兜底选择最该进入的世界，展示推荐理由、阶段、来源、世界线运行数和主动作；最近故事卡已接入 `storyShelfFocus`，按运行次数和来源显示“待确认天命 / 已有沙盘结果”、推荐下一步、来源和世界线运行数；主按钮进入天命书或卷宗阅读，同时保留世界沙盘、天命书、卷宗阅读、作者采纳台和机制档案入口，390px 书架无水平溢出且推荐主按钮在首屏内。
- `WorldAnchorPage` 已把天命书、世界沙盘和卷宗阅读前置为“世界启动”行动卡，并新增本机最近阅读续航、世界状态条、世界卷宗总览、世界脉搏和当前旅程状态；用户访问卷宗阅读、长线卷、角色卷、势力卷、事件卷或检查点后，回到锚定页可一键续读，进入其他世界内页面时也可通过 AppShell 位置条续读。世界状态条把当前阶段、下一步和三项世界脉搏压到同一行；桌面在世界卷宗总览顶部，移动端在品牌后进入首屏。世界卷宗总览把天命书、沙盘、阅读、世界线、多视角、作者台和机制档案串成可点击地图；当前旅程会把天命书、沙盘、阅读、作者台标成“下一步/可用/待生成”并给出主动作；窄屏下紧凑总览仍在启动卡后，且不隐藏锚定侧栏或角色栏。
- `TianmingPage` 已有首屏宪法封面，按生成草案、确认根天命、干预预编译、进入沙盘组织状态和主动作，并展示当前锚点、合约压力和摘要统计；移动端 hero 后另有“生成/确认/沙盘 / 看锚点 / 投干预 / 去沙盘”宪法速断条，主按钮随状态执行当前动作，辅助入口可直达锚点/状态区或干预预编译区。
- `ImportNovelPage` / `GenesisPage` 已有开卷中枢，导入页按命名世界、放入正文、抽取世界、进入锚定组织状态和主动作；创世页按命名世界、写下冲突、补足手感、进入锚定组织状态和主动作。两页移动端先给出操作按钮，再展示完整流程卡。
- `WorldlineDossierPage` 已有首屏工作流中枢，按确认分支状态、查看代偿、回放最近变化、进入连续正文组织状态和主动作；移动端 hero 后另有“回放 / 看代偿 / 看任务 / 长线卷”承接导读条，四枚入口可直接回放最近检查点、滚到具象代偿、滚到自演任务/检查点区或跳长线卷；无检查点时主行动为继续沙盘，有检查点时主行动切到回放最近检查点。
- `CheckpointReplayPage` 已有首屏醒来回放中枢，按确认大事件、查看角色记忆、承接因果代偿、进入连续正文组织状态和主动作；移动端 hero 后另有“继续读 / 看记忆 / 看代偿 / 作者台”醒来导读条，四枚入口可直接进入连续阅读、滚到角色记忆、滚到具象代偿或跳作者台；同时保留返回世界线、继续沙盘和作者采纳台出口。
- `CharacterLensPage` 已有首屏工作流中枢，按选择观察点、生成五类卷宗、阅读信息差、送入作者台组织状态和主动作；移动端 hero 后另有“生成 / 改事件 / 读卷宗 / 作者台”分镜导读条，生成后主按钮会改为“看结果”，并保留卷宗阅读、作者采纳台和世界沙盘出口。
- `WorkspacePage` 已作为“世界正史与机制档案”保留旧正史、旧分支、导入检查、检索/Graph 支撑层和审计等能力；首屏档案中枢按定界、运行、阅读、追溯把用户接回天命书、世界沙盘、卷宗阅读和旧分支查看，移动端另有“天命书 / 沙盘 / 读卷宗 / 查证据”导读条，把支撑层资料接回世界主旅程。
- 作者采纳台可从采纳结果生成 `next_chapter_brief.json`、`next_chapter_draft.json`、`continuous_reading_chapter.json`、`draft_revision_pack.json`。
- Reviewer 片段级建议可由作者勾选，生成 `accepted_local_rewrites.json`、`next_chapter_draft_revised.md`、`edited_final_chapter.json` 和 `edited_final_chapter.md`；确认入卷未手改时会自动采用编辑后定稿。
- 作者采纳台首屏已有“当前下一步”工作流中枢，按对照、入账、修订、入卷展示状态，并把写入采纳台、生成草稿、采纳局部改写、确认入卷和回世界沙盘动作前置；移动端中枢压缩后还提供“调整材料”入口，能直接滚到采纳决策和原大纲/沙盘涌现/作者备注表单。

## 当前真实未做项

优先继续：

- 真实 LLM 多 Agent 多轮策略规划、长期关系/势力博弈、稳定误判/隐瞒/试探和跨轮结算。
- 长正文读感、更深跨章误会回收、跨章伏笔回收、账号级用户阅读进度持久化和真实文风一致性。
- Reviewer 整章风格润色、可回滚对照、真实模型编辑器和定稿质量门。
- `consequence_state` 长期状态机、人工确认、跨章节发酵和真实 LLM 决策消费。
- `WorldWorkspaceShell`、跨章角色/势力长线阅读、跨章节回收、账号级用户阅读进度持久化和更完整的机制档案分区。

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
- 每个独立切片完成后同步 `memory.md`、相关 PRD/README/本文件和 `project-changelog.md`。
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
