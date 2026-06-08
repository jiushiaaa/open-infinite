# 未终章 - 项目记忆（跨会话）

> **用途**：供 Codex / Cursor / 多会话 Agent 快速恢复项目事实，避免重复劳动或把历史待办误判成当前任务。
> **维护约定**：本文件只保留“当前事实、路线、边界、入口索引”；完整历史变更日志已迁移到 `docs/project-changelog.md`。每次有意义的开发/设计/验收任务结束后，请把状态同步到本文对应章节，并将历史记录追加到变更日志文档末尾；每完成一个独立切片都必须即时追加 changelog，不等无人值守总收口再补。
> **最后更新**：2026-06-08（沙盘势力反制账）。当前事实：World Sandbox Loop / 世界沙盘改造 S1-S9 已有第一版可运行链路；最近几刀分别完成卷宗阅读页产品化、卷宗阅读正文证据锚点与阅读进度、卷宗阅读当前场景导读条、卷宗阅读误会图谱第一版、卷宗阅读移动端“开始读正文 / 查卷宗 / 作者台”导读条、卷宗阅读“读小说 / 查卷宗”模式切换、卷宗阅读“本卷场景”横向阅读轨道、卷宗阅读“读完之后”余波承接台、卷宗阅读“续读签”、卷宗阅读“本章读感罗盘”、世界沙盘“本轮已发生”结果承接台、世界沙盘结果阅读顺序导读台、世界沙盘角色行动焦点台、世界沙盘角色跨轮追踪台、世界沙盘策略博弈读法、世界沙盘暗线续推判断、世界沙盘关系势力发酵预告、世界沙盘多轮策略规划预告、世界沙盘策略结算预告、世界沙盘势力反制账、世界沙盘下一轮影响预演、世界沙盘下一轮草稿提示、世界沙盘本轮承接来源回执、世界沙盘本轮因果回执回填下一轮、世界沙盘本轮因果回执、世界沙盘策略棋盘、世界沙盘策略暗线承接台、世界沙盘后续可能性可回填下一轮、世界沙盘干预后果预演台、世界沙盘事件种子台、世界书架开卷路径选择、世界书架世界魅力前厅、世界自演结果页“昨夜世界醒来台”、长线卷移动端“读长线 / 按事件追 / 回收误会 / 作者台”导读条、长线卷跨章回收台、长线卷跨章承接地图、长线卷角色/势力追踪上下文台、长线卷跨章误会网络图、事件多视角移动端“读事件 / 看信息差 / 查证据 / 作者台”导读条、事件多视角信息差接力台、事件多视角误读弧线、角色个人卷移动端“读立场 / 查记忆 / 换角色 / 作者台”导读条、角色个人卷记忆接力台、角色个人卷记忆弧线、势力卷移动端“看站位 / 查代偿 / 换势力 / 作者台”导读条、势力卷压力接力台、势力卷代偿弧线、检查点回放“读报告 / 查证据”模式切换、检查点回放移动端“继续读 / 看记忆 / 看代偿 / 作者台”醒来导读条、检查点醒来接力台、世界线移动端“回放 / 看代偿 / 看任务 / 长线卷”承接导读条、世界线状态接力台、世界线代偿罗盘、世界线世界发酵账、多视角移动端“生成 / 改事件 / 读卷宗 / 作者台”分镜导读条、天命书移动端“生成/确认/沙盘 / 看锚点 / 投干预 / 去沙盘”宪法速断条、天命书确认后的“天命生效接力台”和“下一轮启动简报”、机制档案移动端“天命书 / 沙盘 / 读卷宗 / 查证据”导读条、世界自演结果页可读入口、Reviewer 局部重写采纳、自动编辑后定稿、前端世界书架/世界内卷宗导航第一轮降噪与首屏 QA、世界书架故事卡下一步导览/故事卡旅程脉冲/推荐世界面板/推荐世界续行台、导入/创世开卷中枢、导入/创世开卷旅程接力条、世界内导览层 `WorldRunway` 下一步承接层、WorldWorkspaceShell 世界扫读带/旅程总线与状态预告/导航焦点反馈/移动 summary 焦点反馈/卡片焦点等价反馈/体验轨道焦点反馈、AppShell 当前任务条/世界工作区总览/世界脉搏条/世界位置条/世界体验轨道/全局续读入口/全局卷宗速览盘/世界旅程指针/移动端壳层压缩与折叠导航/沙盘运行台主动作锚点、前端路由级拆包、路由 chunk 失败兜底、高频路由 chunk 预取、共享壳层 route chunk 预取、路由感知加载态、路由感知失败恢复态、当前位置语义导航、世界壳层导航地标语义、主内容跳转入口/焦点目标/中文可读名称/随路由命名/跳转文案/浏览器标题、顶栏焦点反馈、世界锚定页启动卡/世界续行台/世界状态条/世界卷宗总览/世界脉搏/本机最近阅读续航/旅程状态面板、世界正史卷/主锚点卷独立页、世界正史卷/主锚点卷承接弧线、角色个人卷独立页、势力卷独立页、事件多视角详情页、跨事件长线卷及其阅读进度/多事件索引/误会回收台/跨章承接地图/角色势力追踪/误会网络、移动端栏目保功能、世界沙盘页运行导览与运行台分步化/首屏运行台前置/沙盘开跑前路标、移动端世界卷宗导航盘、卷宗阅读卷首题签、作者采纳台工作流中枢/写作台与审稿台模式切换/移动端材料入口/确认入卷接力台/Reviewer 质检门/定稿对照台/章节质感雷达/整章修订路线/跨章回收清单、天命书首屏宪法封面、多视角首屏工作流中枢、世界线首屏工作流中枢、检查点首屏醒来回放中枢，以及机制档案首屏中枢。后续默认继续深化真实 LLM 多 Agent 策略、长正文/连续阅读质量、跨章节误会回收、更强真实语义 Reviewer 和整章风格润色，不回 provider、GraphRAG、检索评测、OpenAPI、发行或商业化主线。
> **最新补充**：2026-06-08（沙盘势力反制账）。详见下方同日补充和 `docs/project-changelog.md` 的 `Sandbox Strategy Faction Counter Ledger`。
> **文档治理口径**：本文件只写当前事实和真实未做项；完整历史见 `docs/project-changelog.md`，文档分类见 `docs/index.md`，已收口专项见 `docs/completed/README.md`。旧文档若和本文冲突，以本文为准。

2026-06-08 沙盘势力反制账已完成第一版：`WorldSandboxPage` 在“策略结算预告”和“下一轮暗线承接”之间新增“势力反制账”。当真实模型 advisory 产出策略互动时，用户会先看到“谁会借势 / 资源卡在哪里 / 秘密流向哪里 / 下一轮怎么投”四张反制卡，前三张分别追角色行动、世界线代偿或长线卷，最后一张可把势力索债直接放入运行台，并在下一轮草稿中标明来源为“势力反制”。该刀只改前端跑后势力层理解、样式、回填状态和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘策略结算预告已完成第一版：`WorldSandboxPage` 在“多轮策略规划”和“下一轮暗线承接”之间新增“策略结算预告”。当真实模型 advisory 产出策略互动时，用户承接下一轮前会先看到“成败看什么 / 谁会反噬 / 世界记到哪里 / 跑完先验哪里”四张结算卡，并可直接验收首步、承接反噬线、看世界线或追长线卷。该刀只改前端跑后跨轮策略结算理解层、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘多轮策略规划预告已完成第一版：`WorldSandboxPage` 在“关系势力发酵”和“下一轮暗线承接”之间新增“多轮策略规划”。当真实模型 advisory 产出策略互动时，用户承接下一轮前会先看到“下一轮先试什么 / 中段谁会反制 / 后段写进哪里”三步计划，并可直接承接首步、承接反制线或追长线卷。该刀只改前端跑后跨轮策略理解层、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘关系势力发酵预告已完成第一版：`WorldSandboxPage` 在“暗线续推判断”和“下一轮暗线承接”之间新增“关系势力发酵”。当真实模型 advisory 产出策略互动时，用户读完棋盘和续推判断后，会先看到关系会怎样变、势力会怎样索债、谁会带着记忆、下一轮看哪里四张长期压力卡，并可直接追角色行动、看世界线代偿、读角色卷或进长线卷。该刀只改前端跑后长期压力理解层、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘暗线续推判断已完成第一版：`WorldSandboxPage` 在“策略棋盘”和“下一轮暗线承接”之间新增“暗线续推判断”。当真实模型 advisory 产出多条策略互动时，用户会在读完棋盘后看到“优先承接 / 风险最高 / 影响最深”三张决策卡，并可立即把推荐线、风险线或影响线续推到下一轮。该刀只改前端跑后策略决策层、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘策略博弈读法已完成第一版：`WorldSandboxPage` 在“结果阅读顺序”和“策略棋盘”之间新增“策略博弈读法”。当真实模型 advisory 产出策略互动时，用户会先看到“先看谁在施压 / 再看谁误判 / 然后看反制风险 / 最后决定是否续推”四步读法，并可直接跳到策略棋盘或把首条暗线承接进下一轮。该刀只改前端跑后策略阅读层、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘下一轮影响预演已完成第一版：`WorldSandboxPage` 在“下一轮草稿已准备”内新增“下一轮影响预演”，当用户从事件种子、后续可能性、策略暗线、角色行动、角色弧线或因果回执回填草稿后，启动前会先看到“谁会先承压 / 世界会怎样记账 / 旧干预边界 / 跑完先看哪里”四枚扫读卡。该刀只改前端下一轮草稿解释层、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘因果回执回填下一轮已完成第一版：`WorldSandboxPage` 在“本轮因果回执”动作区新增“带入下一轮”，会把事件入账、因果债、代偿落点和下一轮代价合成为运行台大事件草稿，草稿来源显示为“因果回执”，并清空上一轮临时干预，避免用户误把旧干预重复投放。该刀只改前端跑后因果回填交互、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘因果回执已完成第一版：`WorldSandboxPage` 在“本轮已发生”结果承接台内、承接来源之后新增“本轮因果回执”。跑完一轮后，页面会把事件入账、`world_state_delta.causal_debt`、`world_state_delta.compensation_effects` / `consequence_state` 代偿落点和 `consequenceNextRoundHint` 下一轮代价整理成四枚可扫读卡，并提供“看代偿账”和“追长线卷”两个出口。该刀只改前端跑后因果解释层、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘开跑前路标已完成第一版：`WorldSandboxPage` 在未运行、无自演报告的空态中，把旧“这一页的世界回路”升级为“开跑前路标”；用户可直接“去写事件”聚焦大事件输入、“添加/调整干预”打开可选干预，并在空态内看到“跑完先看本轮已发生”的结果路径和“从这里启动推演”主动作。该刀只改前端沙盘页空态导引、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘结果阅读顺序导读台已完成第一版：`WorldSandboxPage` 在“本轮已发生”结果承接台之后、策略棋盘和角色行动链之前新增“结果阅读顺序”。跑完一轮后，用户会先看到“先读总览 / 再看暗线 / 然后追角色行动 / 最后选择出口”四步导读；按钮可回到结果总览、滚到策略棋盘或角色行动链，也可直接读成正文。该刀只改前端结果区导读、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘角色行动焦点台已完成第一版：`WorldSandboxPage` 在跑后结果导读、策略棋盘/模型建议之后、完整“角色行动链”之前新增“角色行动焦点”。它会从本轮 `character_actions` 派生最多三张可扫读卡，先提示“最值得追的角色”、行动背后的真实意图、风险与结果、记忆种子，并提供定位行动链、追角色卷、回填为下一轮事件三个动作。该刀只改前端跑后行动理解层、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘角色跨轮追踪台已完成第一版：`WorldSandboxPage` 在“角色行动焦点”之后、完整“角色行动链”之前新增“角色跨轮追踪”。它会从本轮 `character_actions` 和既有 worldline/possibility 提示派生最多三条角色弧线，把上一轮记忆、本轮行动、结果压力和下一轮推力串成可读卡；用户可追这条弧线、读角色卷，或把该角色弧线带入下一轮事件。该刀只改前端跑后角色弧线理解层、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘下一轮草稿提示已完成第一版：`WorldSandboxPage` 在首屏运行台的大事件输入之后、事件入局预演台之前新增“下一轮草稿已准备”。当用户从事件种子、后续可能性、策略暗线、角色行动焦点或角色跨轮追踪回填事件时，运行台会显示来源、事件草稿和干预状态，并提供继续编辑事件或直接启动下一轮动作。该刀只改前端运行台反馈层、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 沙盘本轮承接来源回执已完成第一版：`WorldSandboxPage` 在“本轮已发生”结果承接台内新增“本轮承接来源”。启动一轮时页面会把事件种子、后续可能性、策略暗线、角色行动焦点、角色跨轮追踪或手写事件保存成 `lastRoundLaunchReceipt`，跑后继续展示来源、事件和干预边界，并提供回到运行台或读结果顺序动作。该刀只改前端跑后来源回执、样式和结构检查脚本，不新增后端 API，不改变 `POST /api/stories/<slug>/sandbox/run` 字段、路由、阅读进度、世界自演、作者采纳或 artifact 契约。`check:sandbox-runner-ux` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 当前位置语义导航已完成第一版：`AppShell` 顶栏世界内卷宗导航在锚定、天命书、沙盘、阅读、长线卷、世界线、多视角、作者台和机制档案当前项上补充 `aria-current="page"`；角色卷、势力卷和事件卷这些只在当前路由显示的 active chip 也补充 `aria-current="page"`。`WorldWorkspaceShell` 的旅程总线与世界体验轨道在当前阶段补充 `aria-current="step"`，卷宗速览当前入口补充 `aria-current="page"`。该刀只改共享壳层语义、结构检查脚本和文档，不改变视觉样式、路由 hash、route chunk 预取、移动端折叠导航、阅读进度或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 主内容跳转入口已完成第一版：`AppShell` 在顶栏和世界工作区导航之前新增键盘可聚焦的“跳到当前页面内容”入口，聚焦时以纸面浮层回到屏幕内；主内容区补充稳定 `#main-content` 锚点，让键盘用户和辅助技术可以绕过密集世界导航直接进入当前页面。该刀只改共享壳层结构、AppShell 样式、结构检查脚本和文档，不改变视觉常态、hash 路由、route chunk 预取、移动端折叠导航、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 主内容跳转焦点目标已完成第一版：`AppShell` 的主内容区在稳定 `#main-content` 锚点之外补充 `tabIndex={-1}`，让“跳到当前页面内容”不只滚到正文区域，也能把焦点落到主内容目标上。该刀只改前端壳层结构、结构检查脚本和文档，不改变视觉常态、路由、预取、移动端折叠导航、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 世界壳层导航地标语义已完成第一版：`WorldWorkspaceShell` 的世界旅程总线、世界工作区总览、世界状态预告、世界脉搏、世界体验轨道和世界卷宗速览都以带中文 `aria-label` 的 `nav` landmark 暴露；移动端“展开世界导航”折叠区补充“移动端世界导航”标签，让辅助技术不只听见一串按钮，也能理解这些入口分别属于旅程、状态、脉搏、阶段和卷宗。该刀只改共享壳层语义结构、结构检查脚本和文档，不改变视觉常态、桌面/移动导航布局、路由、预取、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 主内容区中文可读名称已完成第一版：`AppShell` 的 `main#main-content` 在稳定锚点和 `tabIndex={-1}` 之外补充 `aria-label="当前页面内容"`，让“跳到当前页面内容”落点不只是可聚焦区域，也能被辅助技术读成明确的当前页面正文区域。该刀只改共享壳层语义结构、结构检查脚本和文档，不改变视觉常态、路由、预取、移动端折叠导航、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 主内容区随路由命名已完成第一版：`AppShell` 的 `main#main-content` 继续保留稳定锚点、`tabIndex={-1}` 和中文可读名称，但 `aria-label` 已从固定“当前页面内容”升级为 `当前页面内容：${routeContext.title}`；世界内页面会读出“当前页面内容：世界沙盘 / 卷宗阅读 / 作者采纳台”等当前路由标题，非世界页回退到现有路由标签或“世界书架”。该刀只改共享壳层语义和结构检查脚本，不改变视觉常态、路由、预取、移动端折叠导航、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 跳转入口随路由命名已完成第一版：`AppShell` 把 `routeContext.title` 或现有路由标签提成 `currentPageTitle`，同时生成 `mainContentLabel` 和 `skipLinkLabel`；键盘用户最先遇到的 skip link 不再固定读成“跳到当前页面内容”，而会随页面读成“跳到世界沙盘内容 / 跳到卷宗阅读内容 / 跳到作者采纳台内容”。该刀只改共享壳层语义和结构检查脚本，不改变视觉常态、路由、预取、移动端折叠导航、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 浏览器标题随路由命名已完成第一版：`AppShell` 复用 `currentPageTitle` 在路由变化时写入 `<当前页面> · 未终章`，让浏览器标签和窗口标题也能区分世界沙盘、卷宗阅读、作者采纳台等当前页面。该刀只改共享壳层语义和结构检查脚本，不改变视觉常态、路由、预取、移动端折叠导航、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 顶栏焦点反馈已完成第一版：`AppShell` 的品牌入口、世界卷宗导航按钮和顶栏右侧动效/设置按钮新增一致的 `:focus-visible` 描边；世界卷宗按钮聚焦时还复用纸面 hover 背景，让键盘用户能清楚看见当前停在哪个高频入口。该刀只改 AppShell 样式、结构检查脚本和文档，不改变常态视觉、布局、路由、预取、移动端折叠导航、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 WorldWorkspaceShell 导航焦点反馈已完成第一版：`WorldWorkspaceShell` 的世界旅程总线按钮和卷宗速览按钮新增显式 `:focus-visible` 描边；旅程按钮聚焦时复用纸面 hover 背景，卷宗按钮聚焦时复用青绿 `jade-wash` 背景，让键盘用户在密集世界导航里能稳定看见当前焦点。该刀只改共享壳层样式、结构检查脚本和文档，不改变常态布局、路由、预取、移动端折叠导航、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 移动世界导航 summary 焦点反馈已完成第一版：`WorldWorkspaceShell` 移动端“展开世界导航”折叠入口新增显式 `:focus-visible` 描边和纸面聚焦背景，让键盘用户在展开完整世界导航前也能看见当前焦点。该刀只改共享壳层移动端样式、结构检查脚本和文档，不改变常态布局、桌面导航、路由、预取、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 共享壳层卡片焦点等价反馈已完成第一版：`WorldWorkspaceShell` 的世界扫读带 chip、轻量工作区指针、状态预告卡和世界脉搏卡在 `:focus-visible` 时补齐与 hover 等价的纸面背景和边框反馈，让键盘用户扫过密集世界壳层卡片时不只看到细描边，也能稳定辨认当前可执行卡片。该刀只改共享壳层样式、结构检查脚本和文档，不改变常态布局、桌面/移动导航结构、路由、预取、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 世界体验轨道焦点反馈已完成第一版：`WorldWorkspaceShell` 的“定界 / 运行 / 阅读 / 采纳”世界体验轨道按钮新增显式 `:focus-visible` 描边和纸面聚焦背景，让键盘用户在共享壳层里切换阶段入口时不只依赖浏览器默认焦点。该刀只改共享壳层样式、结构检查脚本和文档，不改变常态布局、桌面/移动导航结构、路由、预取、阅读进度、沙盘请求字段或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿；完整验证结果见本轮 changelog。

2026-06-08 WorldWorkspaceShell 世界扫读带已完成第一版：`WorldWorkspaceShell` 把“当前环节 / 承接世界线 / 当前任务 / 为什么建议先做 / 继续阅读 / 主动作 / 次动作”合并成更强的“世界扫读带”，并前置到旅程总线、工作区指针、状态预告、世界脉搏和卷宗速览之前。原“当前环节 / 承接世界线 / 下一步为什么做”工作区总览降级为“旅程入口 / 世界线档案 / 为什么建议这步”的轻量旅程指针，所有导航、续读、主动作、同路由锚点滚动和移动端折叠导航仍保留。该刀只改共享壳层组件、AppShell 样式和 `check:app-shell-mobile-layout`，不新增后端 API、不改变路由、阅读、作者采纳或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿，`check:world-route-context` 和 `pnpm.cmd run build` 通过；完整验证结果见本轮 changelog。

2026-06-08 前端路由级拆包已完成第一版：`App.tsx` 不再静态导入所有页面，而是用 `React.lazy`/`Suspense` 按路由懒加载 `StoryEntryPage`、世界锚定、天命书、沙盘、卷宗、长线卷、作者台等页面，并提供“正在展开世界卷宗”的中文纸面加载态。新增 `check:route-code-splitting` 锁定页面组件不得回到首包静态导入。该刀只改前端入口、加载态样式、检查脚本和文档，不新增后端 API、不改变 hash 路由、页面 props、阅读进度或 artifact 契约。`pnpm.cmd run build` 已把入口 JS 从约 711.66 kB 降到约 231.50 kB，页面拆成独立 chunks，且 Vite 大 chunk 警告消失。

2026-06-08 路由 chunk 失败兜底已完成第一版：`App.tsx` 在懒加载页面外新增 `RouteChunkBoundary`，当某个动态页面 chunk 因网络、缓存或部署版本漂移加载失败时，会显示“世界卷宗没有展开”的中文纸面错误态，并提供“重新展开”和“回世界书架”两个恢复动作；路由 hash 改变时错误态会自动重置。`check:route-code-splitting` 已扩展为同时锁定 `Suspense`、中文加载态和 chunk 失败恢复态。该刀只改前端入口、壳层样式、检查脚本和文档，不新增后端 API、不改变 hash 路由、页面 props、阅读进度或 artifact 契约。`pnpm.cmd run build` 通过，入口 JS 约 232.47 kB，页面仍拆成独立 chunks，且无 Vite 大 chunk 警告。

2026-06-08 高频路由 chunk 预取已完成第一版：新增 `routePagePreload.ts` 作为页面动态 import 的共享注册表，`App.tsx` 和预取 helper 共用同一份 `routePageLoaders`，避免懒加载和预取维护两份页面映射；`AppShell` 的品牌入口和世界内高频导航在 `onMouseEnter`、`onFocus`、`onPointerDown` 时调用 `preloadRoutePage`，让锚定、天命书、沙盘、卷宗阅读、长线卷、世界线、多视角、作者台和机制档案等页面在点击前提前热身。`check:route-code-splitting` 已扩展为锁定共享 loader registry、失败重试和导航意图预取。该刀只改前端入口、导航壳层、检查脚本和文档，不新增后端 API、不改变 hash 路由、页面 props、阅读进度或 artifact 契约。`pnpm.cmd run build` 通过，入口 JS 约 233.56 kB，页面仍拆成独立 chunks，且无 Vite 大 chunk 警告。

2026-06-08 共享壳层 route chunk 预取已完成第一版：`WorldWorkspaceShell` 复用同一套 `preloadRoutePage`，为世界扫读带、旅程总线、工作区指针、状态预告、世界脉搏、体验轨道、卷宗速览、主动作和次动作统一接入 `onMouseEnter`、`onFocus`、`onPointerDown` 预取。用户在世界内部点击“当前任务”“继续沙盘”“追长线卷”“送往作者台”“世界线档案”等共享壳层动作前，目标页面 chunk 会提前加载。`check:app-shell-mobile-layout` 已扩展为锁定共享壳层预取，不改变移动端折叠导航、按钮层级、路由 hash、页面 props、阅读进度或 artifact 契约。`pnpm.cmd run build` 通过，入口 JS 约 233.81 kB，页面仍拆成独立 chunks，且无 Vite 大 chunk 警告。

2026-06-08 路由感知加载态已完成第一版：`RouteLoading` 现在接收当前 `Route`，通过 `routeLoadingCopy(route)` 显示目标明确的中文加载反馈；进入世界沙盘、卷宗阅读、作者采纳台、天命书、世界线档案、跨事件长线卷和世界锚定时，会分别显示“正在展开世界沙盘 / 卷宗阅读 / 作者采纳台 / 天命书”等标题和一句说明，避免懒加载期间用户只看到通用提示或误以为页面没反应。`check:route-code-splitting` 已扩展为锁定 route-aware loading copy 和结构化 title/detail。该刀只改前端入口加载态、AppShell 样式、检查脚本和文档，不新增后端 API、不改变 hash 路由、页面 props、预取机制、阅读进度或 artifact 契约。`pnpm.cmd run build` 通过，入口 JS 约 234.61 kB，页面仍拆成独立 chunks，且无 Vite 大 chunk 警告。

2026-06-08 路由感知失败恢复态已完成第一版：`RouteChunkBoundary` 现在接收当前 `Route`，通过 `routeErrorCopy(route)` 显示目标明确的 chunk 失败反馈；世界沙盘、卷宗阅读、作者采纳台和天命书加载失败时，会分别显示“世界沙盘没有展开 / 卷宗阅读没有展开 / 作者采纳台没有展开 / 天命书没有展开”，并说明可重新展开对应房间或先回世界书架再进入。`check:route-code-splitting` 已扩展为锁定 route-aware recovery copy 和 route-aware boundary props。该刀只改前端入口错误态、检查脚本和文档，不新增后端 API、不改变 hash 路由、页面 props、预取机制、阅读进度或 artifact 契约。`pnpm.cmd run build` 通过，入口 JS 约 235.08 kB，页面仍拆成独立 chunks，且无 Vite 大 chunk 警告。

2026-06-07 StoryEntryPage 开卷路径选择已完成第一版：`StoryEntryPage` 的三张入口卡在原有内置样例、导入小说、主题创世动作上新增“适合谁”和四段开卷路径。用户能在世界书架首屏判断自己该先试样例、导入已有章节，还是从题材冲突创世，并看见三条路径如何分别接到天命书、世界锚定、世界沙盘和卷宗阅读。该刀只改前端世界书架 JSX/CSS 和 `check:story-shelf-focus`，不新增后端 API、不改导入/创世路由、不删除任何既有入口。`check:story-shelf-focus` 先 RED 后转绿，后续验证结果见本轮 changelog。

2026-06-07 DossierReadingPage 本章读感罗盘已完成第一版：`DossierReadingPage` 在“续读签”之后、连续正文之前新增“本章读感罗盘”，从 `continuous_reading.reading_flow` 的开场钩子、转折、下一章悬念，以及当前场景误会/`chapter_cliffhanger` 派生四枚阅读前信号。用户进入正文前能先明白这一章为什么值得读、哪里会转折、误会怎样驱动下一轮、读完后接向哪里，并可直接“进入正文”或查看“阅读节奏”。该刀只改前端卷宗阅读 JSX/CSS 和结构检查脚本，不新增后端 API、不改 `dossier-reading` 契约、不改 artifact。`check:dossier-reading-ux` 先 RED 后转绿，后续验证结果见本轮 changelog。

2026-06-07 WorldSandboxPage 事件种子台已完成第一版：`WorldSandboxPage` 在“写事件 / 可选干预 / 启动推演”步骤之后、大事件输入之前新增“事件种子台”，从当前锚点、`worldline_state.continuation_inputs.major_event_hint`、`consequence_state.next_round_hint`、代偿域、最近 ledger、后续剧情可能性和首条策略暗线派生三枚可扫读事件种子。用户不知道下一轮写什么时可一键“放入事件”，运行台会填入事件草稿并给出已放入反馈，同时保留下方可选干预，不新增后端 API、不改 `POST /api/stories/<slug>/sandbox/run` 字段、不改变沙盘 artifact。`check:sandbox-runner-ux` 先 RED 后转绿，`pnpm.cmd run build` 通过；本轮工具面未暴露 in-app Browser 控制，因此移动端/桌面视觉仅完成结构与构建验证，待下一轮有浏览器工具时补真实视口截图验收。

2026-06-07 TianmingPage 下一轮启动简报已完成第一版：`TianmingPage` 在确认后的“天命生效接力台”和详细天命面板之间新增“下一轮启动简报”，把会被下一轮沙盘消费的主锚点、当前压力档、首个叙事吸引子和候选天命承载者组织成四枚可扫读卡，并提供“启动世界沙盘 / 先投放干预 / 看锚点压力”三项动作。该层只复用既有 `tianming.json` 字段和现有导航/滚动动作，不新增后端 API、不改天命书 artifact、不删生成、确认、干预编译、代偿或锚点详情；旧接力台的同名按钮已改为“查看锚点压力”，避免同屏重复 accessible name。`check:tianming-mobile-guide` 先 RED 后转绿，`pnpm.cmd run build`、`python -X utf8 -m pytest -q` 和 in-app Browser 1280px/390px 验证均通过；390px 下简报单列、按钮等宽、无水平溢出且浏览器 error 日志为空。

2026-06-07 WorldWorkspaceShell 移动端折叠导航已完成第一版：`WorldWorkspaceShell` 在桌面仍完整展开“世界旅程总线 / 工作区总览 / 当前任务 / 状态预告 / 世界脉搏 / 体验轨道 / 卷宗速览”，但在 640px 以下把全局世界导航收进“展开世界导航”折叠区，让移动端首屏先显示当前位置、当前任务、主动作和页面正文。折叠区展开后仍保留 4 个旅程入口、4 个体验阶段、4 个世界脉搏和 8 个卷宗入口，桌面结构不变，移动端无水平溢出。该刀只改共享壳层组件、AppShell 样式和 `check:app-shell-mobile-layout`，不新增后端 API、不改变路由、阅读、作者采纳或 artifact 契约。`check:app-shell-mobile-layout` 先 RED 后转绿，`pnpm.cmd run build` 通过；in-app Browser 在 `http://localhost:5183/#/world/demo-world/author` 390px 下验证默认折叠、任务条位于导航前、展开后入口完整、无水平溢出且浏览器 error 日志为空。

2026-06-07 WorldWorkspaceShell 沙盘运行台主动作锚点已完成第一版：`worldRouteContext` 在沙盘路由下把共享壳层“当前任务”从“进入卷宗阅读”改为“启动一轮推演”，主路由保持在当前沙盘页，并提供 `primaryTargetId="sandbox-runner"`；卷宗阅读改为次动作保留。`WorldWorkspaceShell` 的主动作、下一步信息签和状态预告 receipt 现在会在同路由目标上滚到运行台，并支持 `.sandbox-page` 这类内部滚动容器；`WorldSandboxPage` 的运行台暴露稳定 `id="sandbox-runner"`。该刀只改前端路由语义、共享壳层滚动 helper、沙盘运行台锚点和结构检查脚本，不新增后端 API、不改路由 hash 契约、不改沙盘 artifact。`check:world-route-context`、`check:sandbox-runner-ux`、`check:app-shell-mobile-layout` 先 RED 后转绿，`pnpm.cmd run build` 通过；in-app Browser 在 `http://localhost:5183/#/world/my-story/sandbox` 390px 干净标签页验证主按钮文案为“启动一轮推演”，点击后仍在沙盘路由，`.sandbox-page` 从 `scrollTop 0` 滚到 `130`，运行台与页面容器顶部距离约 `0.28px`，无水平溢出且浏览器 error 日志为空。

2026-06-07 WorldAnchorPage 世界续行台已完成第一版：`WorldAnchorPage` 在锚定页新增“世界续行台”，把此刻世界、被推到台前的角色、牵引伏笔和建议先做集中成四枚可扫读卡，并复用 `deriveWorldJourney`、本机 `recentReading`、`data.world.scene_description`、`data.divergence_point`、首个角色和首条开放伏笔。桌面左栏显示紧凑续行台，中心栏在世界苏醒台和世界卷宗总览之间保留完整续行台；移动端显示紧凑版并隐藏完整版本。三个动作分别执行推荐下一步、进入世界沙盘或读世界线；在工作台路由下主动作会进入 `#/world/<slug>/tianming` 等正确世界内路由。该刀只改前端锚定页 JSX/CSS 和 `check:world-anchor-status-ribbon`，不新增后端 API、不改 `world-anchor` 字段、不改 artifact、不删世界启动、苏醒台、卷宗总览、视觉资产、编辑锚定或角色栏。`check:world-anchor-status-ribbon` 先 RED 后转绿，`pnpm.cmd run build`、`python -X utf8 -m pytest -q` 和 in-app Browser 1280px/390px smoke 均通过；390px 下无水平溢出且浏览器 error 日志为空。

2026-06-07 作者采纳台跨章回收清单已完成第一版：`AuthorAdoptionPage` 在“下一章可写方案”之后、草稿输出之前新增“跨章回收清单”，从既有 `next_chapter_brief.conflict_focus`、`feed_forward.sandbox_continuation_inputs.major_event`、`feed_forward.next_round_reads`、`writing_plan.manual_review_points` 和草稿状态派生冲突回收、下一轮事件、回读材料、人工复核、正文落点五类行动卡。用户把沙盘涌现剧情写入采纳台后，不只看到下一章 brief，还能直接判断这章必须回收什么、应回哪类卷宗核对、是否先生成草稿或进入 Reviewer 质检门，并可跳回沙盘、长线卷、brief、草稿或审稿台。该刀只改前端作者采纳页 JSX/CSS 和结构检查脚本，不新增后端 API、不改变采纳、草稿、Reviewer、确认入卷或 artifact 契约。`check:author-adoption-ux` 先 RED 后转绿，`pnpm.cmd run build` 通过；in-app Browser 在 `http://localhost:5182/#/world/my-story/author` 验证真实提交后渲染 5 张回收卡，390px 下同一结果为单列、无水平溢出，浏览器 error/warning 日志为空。

2026-06-07 长线卷角色/势力追踪上下文台已完成第一版：`LonglineReadingPage` 在“跨章承接地图”和长线阅读状态区之间新增“角色与势力追踪带”，并在用户选择角色/势力卡片后显示“角色/势力追踪上下文台”。该层从既有 `timeline_entries.affected_characters`、`timeline_entries.affected_factions`、`misbelief_recovery.items` 和 `evidence_refs` 派生最多四条追踪卡，以及选中线的沿线节点、牵连误会和证据读数。用户读跨事件长线时不只按事件顺序看，还能直接沿角色记忆和势力压力继续追“谁还带着后果往前走”，点进后看到这条线经过哪些节点、哪些偏差还会回到下一章，并可继续聚焦任一节点或回到全部长线。该刀只改前端长线卷 JSX/CSS 和结构检查脚本，不新增后端 API、不改变 `longline-reading` 契约、不改 artifact。`check:longline-reading-ux` 先 RED 后转绿，`pnpm.cmd run build` 通过；in-app Browser 在 `http://127.0.0.1:5187/#/world/my-story/worldlines/main/longline` 验证真实数据下桌面点击追踪卡会打开上下文台、选中卡片、显示 5 个沿线节点和 5 条牵连误会，390px 下追踪卡和上下文台均为单列且无水平溢出，浏览器日志无应用 error/warning。

2026-06-07 长线卷跨章误会网络图已完成第一版：`LonglineReadingPage` 在长线阅读状态区和“误会回收台”之间新增“跨章误会网络图”，从既有 `misbelief_recovery.items` 派生最多六个可选误会节点，并在右侧详情里并排展示当前误会、误会来源、牵动角色、证据数量、回收步骤、回卷宗核对和送到作者台动作。用户读长线卷时不只看到误会卡片列表，还能理解一条误会如何从来源事件拖到下一章、影响哪些角色、要按什么步骤回收，并可点击切换不同误会节点。该刀只改前端长线卷 JSX/CSS 和结构检查脚本，不新增后端 API、不改变 `longline-reading` 契约、不改 artifact。`check:longline-reading-ux` 先 RED 后转绿，`pnpm.cmd run build` 通过；`GET /api/stories/my-story/worldlines/main/longline-reading` 返回 200；in-app Browser 在 `http://127.0.0.1:5188/#/world/my-story/worldlines/main/longline` 验证真实数据下桌面渲染 5 个误会节点、网络图位于回收卡片之前、点击第二个节点会切换详情且无水平溢出，390px 下网络图和详情均单列、移动导读显示、浏览器 error/warning 日志为空。

2026-06-07 世界正史卷/主锚点卷承接弧线已完成第一版：`WorldVolumePage` 在“正史/锚点接力台”和三栏阅读布局之间新增“世界卷承接弧线”，从既有 `continuous_reading`、`continuity_threads`、`consequence_state.ledger`、`next_round_hint`、相邻卷和 `evidence_panel` 派生四步承接：卷内事实、相邻卷牵引、代偿落点、下一步回收。用户读正史卷或主锚点卷时不只看到单卷正文和证据，还能理解世界承认的事实、锚点压力、ledger 代偿和长线卷回收之间怎样互相压回下一章；并可直接查卷内证据或去长线卷回收。该刀只改前端世界卷 JSX/CSS 和结构检查脚本，不新增后端 API、不改变 `dossier-reading` 契约、不改 artifact。`check:world-volume-ux` 先 RED 后转绿，`pnpm.cmd run build` 和浏览器烟测通过；in-app Browser 在 `http://127.0.0.1:5185/#/world/my-story/worldlines/main/chronicle` 和 `/anchors` 验证真实数据下 4 步弧线、长线卷跳转、无控制台 error，390px 下弧线单列且无水平溢出。

2026-06-07 事件多视角误读弧线已完成第一版：`EventPerspectivePage` 在“事件信息差接力台”和三栏事件阅读布局之间新增“事件误读弧线”，从既有 `perspective_biases`、`information_gap` 和 `next_actions` 派生最近四条误读信号，把谁看错了、正史裂缝、偏差怎样发酵和下一步回收串成可扫读的连续卡片。用户读事件卷时不仅能看到信息差列表，还能理解同一事件如何分裂成不同角色的下一次判断，并可直接看全部误读或去长线卷回收。该刀只改前端事件多视角 JSX/CSS 和结构检查脚本，不新增后端 API、不改变 `event-perspective` 契约、不改 artifact。`check:event-perspective-ux` 先 RED 后转绿，`pnpm.cmd run build` 和 `git diff --check` 通过；in-app Browser 在 `http://127.0.0.1:5184/#/world/my-story/worldlines/main/events/main/perspectives` 验证真实数据下 4 条误读弧线、操作按钮、无控制台 error，390px 下弧线单列且无水平溢出。

2026-06-07 势力卷代偿弧线已完成第一版：`FactionVolumePage` 在“势力压力接力台”和长阅读布局之间新增“势力代偿弧线”，取最近四条 `consequence_state.ledger`，把来源事件、债务分数、承压领域、资源/秘密压力和 `next_round_hint` 串成可扫读的连续卡片。用户读势力卷时不仅能看到最近记录，还能理解这些记录如何一步步改写下一轮秩序，并可直接看完整代偿账或回沙盘验证。该刀只改前端势力卷 JSX/CSS 和结构检查脚本，不新增后端 API、不改变 `dossier-reading` 或 `worldline-state` 契约、不改 artifact。`check:faction-volume-ux` 先 RED 后转绿，`pnpm.cmd run build` 和 `git diff --check` 通过；in-app Browser 在 `http://localhost:5181/#/world/my-story/worldlines/main/factions/%E8%8B%8D%E6%BE%9C%E6%B4%BE` 验证势力卷路由、3 段 ledger 弧线、操作按钮、无控制台 error，390px 下弧线单列且无水平溢出。

2026-06-07 角色个人卷记忆弧线已完成第一版：`CharacterVolumePage` 在“记忆接力台”和长阅读布局之间新增“角色记忆弧线”，取最近四段主观记忆，把事件、上一段主观记忆、新信念、信任变化、异常感和下一次预期组织成可扫读的连续卡片。用户读角色卷时不仅能看到最新记忆，还能理解这些记忆怎样一步步改写角色的下一次选择，并可直接看完整记忆链或回沙盘验证。该刀只改前端角色卷 JSX/CSS 和结构检查脚本，不新增后端 API、不改变 `dossier-reading` 或 `subjective-memory` 契约、不改 artifact。`check:character-volume-ux` 先 RED 后转绿，`pnpm.cmd run build` 和 `git diff --check` 通过；in-app Browser 在 `http://localhost:5181/#/world/v090-alpha-proof/worldlines/branch_a/characters/han_wu_gui` 验证角色卷路由、空态、记忆接力台、390px 移动端导读条和无水平溢出，当前后端样本没有主观记忆时记忆弧线按预期不渲染。

2026-06-07 作者采纳台整章修订路线已完成第一版：`AuthorAdoptionPage` 在作者修订稿编辑框之后、章节质感雷达之前新增“整章修订路线”，把“先看风险 / 再收改写 / 然后磨正文 / 最后入卷”组织成四步可点击路线。路线复用 `urgentReviewerItems`、`selectedRewriteCount`、`localizedRewriteCount`、`finalTextSource`、`currentFinalPreview` 和 `edited_final_chapter.quality_gate`，可直接跳到 Reviewer 质检门、采纳已选局部改写、回到正文编辑或去确认入卷。该刀只改前端作者采纳页 JSX/CSS 和结构检查脚本，不新增后端 API、不改变采纳、草稿、Reviewer、确认入卷或 artifact 契约。`check:author-adoption-ux` 先 RED 后转绿，`pnpm.cmd run build` 通过；in-app Browser 在 `http://localhost:5173/#/world/demo/author` 验证作者采纳台可打开、首屏工作流中枢可见且无前端白屏或告警。

2026-06-07 世界线世界发酵账已完成第一版：`WorldlineDossierPage` 在“代偿罗盘”之后、`WorldRunway` 之前新增“世界发酵账”，把最近三条 `state.consequence_state.ledger`、前四个代偿域、`state.consequence_state.next_round_hint` 和 `nextRoundReads` 组织成“最近写入 / 承压域 / 下一轮会消费”的可行动路径。用户进入世界线页后不仅能知道世界为什么会继续变，还能直接看见哪些代价会进入下一轮角色行动、哪些域正在承压，以及应去长线卷还是看详细代偿账。该刀只改前端世界线档案页 JSX/CSS 和结构检查脚本，不新增后端 API、不改 `worldline_dossier` / `worldline_state` 字段、不改 artifact。`check:worldline-dossier-ux` 先 RED 后转绿，`pnpm.cmd run build` 和 `git diff --check` 通过；in-app Browser 在 `http://localhost:5180/#/world/my-story/worldlines/main` 验证桌面三列发酵账位于代偿罗盘之后、世界导览之前，“去长线卷”能跳转长线卷，390px 下单列且无水平溢出。

2026-06-07 世界锚定页“世界苏醒台”已完成第一版：`WorldAnchorPage` 在桌面中栏的世界卷宗总览之前、移动端状态条之后新增“世界苏醒台”，用既有 `deriveWorldJourney`、`deriveWorldPulse`、本机 `recentReading`、`data.run_count`、首个角色和首条开放伏笔整理“世界醒着吗 / 谁会行动 / 哪条伏笔牵引 / 从哪里继续”四枚信号。用户进入某个世界后不必先读完整设定、视觉资产或机制档案，就能先判断世界是否已经运行、谁会被推到台前、哪条伏笔牵引下一轮，以及应确认天命、续读、看世界线还是让世界运行。该刀只改前端锚定页 JSX/CSS 和结构检查脚本，不新增后端 API、不改 `world-anchor` 字段、不改 artifact、不删编辑锚定、视觉资产、基线回放、世界启动、卷宗总览、角色栏或角色探针。`check:world-anchor-status-ribbon`、`pnpm.cmd run build` 和 Chrome 1366px/390px 页面 smoke 均通过。

2026-06-07 世界正史卷/主锚点卷独立页已完成第一版：新增 `WorldVolumePage` 共享组件与 `#/world/<slug>/worldlines/<worldline_id>/chronicle`、`#/world/<slug>/worldlines/<worldline_id>/anchors` 两条路由，复用既有 `GET /api/stories/<slug>/worldlines/<worldline_id>/dossier-reading` 的 `world_chronicle` / `anchor_volume` tab、证据链、世界线状态和最近阅读机制，不新增后端 API 或 artifact。AppShell 卷宗速览里的“正史 / 锚点”现在进入独立页面；卷宗阅读 tab 内也保留跳入独立卷的动作。两页都有移动端导读条、`WorldRunway`、正史/锚点接力台、三栏阅读布局、证据栏和世界承接状态，帮助用户先理解世界怎样记住事实、锚点怎样承压，再回沙盘、卷宗阅读或作者台。`check:world-volume-ux`、`check:world-route-context`、`check:reading-progress`、`pnpm.cmd run build` 和 Chrome 1366px/390px 页面 smoke 均通过。

2026-06-07 长线卷跨章承接地图已完成第一版：`LonglineReadingPage` 在“跨章回收台”之后、长线阅读状态区之前新增“跨章承接地图”，把当前阅读节点、来源事件、误会余波和下一轮去向连成一条可点击因果链。该层只消费既有 `activeEntry`、`activeEvent`、`misbelief_recovery`、`current_tension`、`open_threads` 和 `next_actions`，不新增后端 API、不改 `longline-reading` 契约、不改 artifact。用户读长线卷时能先判断“现在读到哪里、这段来自哪个事件、哪个误会还在发酵、世界线接下来会去哪里”，再进入阅读进度、多事件索引、误会回收台和正文时间线。`check:longline-reading-ux` 先 RED 后转绿，`pnpm.cmd run build` 通过；in-app Browser 在 `http://127.0.0.1:5180/#/world/my-story/worldlines/main/longline` 验证桌面 1366px 下地图为稳定 5 列、点击当前节点能把当前长线节点带入视口，390px 下地图单列且无水平溢出。

2026-06-07 世界线代偿罗盘已完成第一版：`WorldlineDossierPage` 在状态接力台之后、`WorldRunway` 之前新增“代偿罗盘”，用 `state.consequence_state.summary`、`state.consequence_state.ledger`、`state.consequence_state.next_round_hint` 和代偿域整理“最近代价 / 承压领域 / 下一轮提示 / 从这里继续看”四枚信号。用户进入世界线页后不必直接读密集 worldline state，就能先理解这条世界线为什么还会继续变、代价落到哪里、下一轮该怎样承接，以及应回放检查点、看详细代偿账、读长线卷还是继续沙盘。该刀只改前端世界线档案页 JSX/CSS 和结构检查脚本，不新增后端 API、不改 `worldline_dossier` / `worldline_state` 字段、不改 artifact。`check:worldline-dossier-ux`、`pnpm.cmd run build`、Chrome 1366px/390px 页面 smoke 均通过。

2026-06-07 世界沙盘事件入局预演台已完成第一版：`WorldSandboxPage` 在首屏运行台的大事件输入之后、可选干预之前新增“事件入局预演台”，随 `majorEvent.trim()`、是否已有读者干预和投放方式解释“谁会先动 / 世界怎样记账 / 干预怎样入局 / 跑完先看哪里”。用户在点击启动前能先理解这轮事件会把哪些角色推到台前、会写入角色行动/主观记忆/因果债/世界线状态、干预会怎样贴着事件进入角色判断，以及跑完应先看本轮已发生、卷宗正文、世界线代偿和角色记忆。预演台提供“修改事件”和“让读者干预入局/调整干预”动作，分别聚焦大事件输入和干预输入；原有启动推演、可选干预、清空干预、真实模型 advisory、结果承接、策略棋盘、自演结果和 API 字段全部保留。`check:sandbox-runner-ux`、`pnpm.cmd run build`、Chrome 1366px/390px 页面交互 smoke 均通过。该刀只改前端沙盘页 JSX/CSS 和检查脚本，不新增后端 API、不改 `POST /api/stories/<slug>/sandbox/run` 字段、不改 artifact。

2026-06-07 作者采纳台章节质感雷达已完成第一版：`AuthorAdoptionPage` 在作者修订稿编辑框之后、定稿对照台之前新增“章节质感雷达”，用 `draft.reviewer_checklist`、语义 Reviewer review items、`selectedRewriteCount`、`finalTextSource` 和 `edited_final_chapter.quality_gate` 汇总“读感节奏 / 角色动机 / 世界入文 / 入卷准备”四枚信号。该雷达可直接跳到 Reviewer 细节、正文编辑和确认入卷；若已有高优先级改写被选中且尚未应用，也可一键采纳高优先级改写。该刀只改前端作者采纳页 JSX/CSS 和结构检查脚本，不新增后端 API、不改变采纳、草稿、Reviewer、确认入卷或 artifact 契约。`check:author-adoption-ux`、`pnpm.cmd run build` 和浏览器 UI 流程检查通过。

2026-06-07 世界书架世界魅力前厅已完成第一版：`StoryEntryPage` 的推荐世界卡新增“世界魅力前厅”，把“世界会运行 / 角色会记得 / 干预有后果 / 章节来自演化”四枚活性信号放在旅程脉冲前，分别随 `runCount` 显示待启动/已运行、待写入/可回看、待投放/可追踪、待生成/可写下一章。该层复用 `deriveStoryShelfFocus.vitalitySignals` 与推荐世界数据，不新增 API、不改 story list 契约、不删原有推荐主按钮、故事卡旅程脉冲、世界沙盘/天命书/卷宗阅读/作者台/机制档案入口。`check:story-shelf-focus`、`pnpm.cmd run build`、`git diff --check` 和浏览器 DOM 检查通过。

2026-06-07 世界沙盘干预后果预演台已完成第一版：`WorldSandboxPage` 在首屏运行台的可选干预之后新增“干预后果预演台”，会随读者干预文本、投放对象和投放方式实时解释这条输入会怎样进入世界、由谁承接、沉浸模式或暴走 AU 会怎样被世界吸收，以及运行后应从角色主观记忆、世界线代偿和多视角正文三处观察后果。预演台提供“添加/调整干预”和“清空干预”动作，避免用户误把旧干预带入下一轮；无干预时也说明只运行大事件仍会写入角色行动、主观记忆和世界线变化。`check:sandbox-runner-ux` 已锁定预演台语义、控制动作和移动端单列；`pnpm.cmd run build` 通过。该刀只改前端沙盘页 JSX/CSS 和检查脚本，不新增后端 API、不改 `POST /api/stories/<slug>/sandbox/run` 字段、不改 artifact。

2026-06-07 作者采纳台定稿对照台已完成第一版：`AuthorAdoptionPage` 在作者修订稿编辑框之后、确认入卷动作之前新增“定稿对照台”，把原始草稿、当前定稿、入卷质量门和回滚/采用动作组织在同一纸面区。该台复用 `draft.chapter_text`、`editedChapterText`、`rewriteApplication.edited_final_chapter.final_chapter_text` 与 `edited_final_chapter.quality_gate`，可恢复原草稿、采用 Reviewer 定稿或回看局部改写；若用户恢复原草稿，当前定稿来源会回到“原始草稿”，不会误标成 Reviewer 定稿。不新增 API、不改 artifact。`check:author-adoption-ux` 和 `pnpm.cmd run build` 通过。

2026-06-07 作者采纳台 Reviewer 质检门已完成第一版：`AuthorAdoptionPage` 在局部修订包摘要和局部改写列表之间新增“Reviewer 质检门”，把阻断/高优先级审稿项、已选局部改写、自动定稿预览和入卷判断组织成四枚可扫读卡，并保留采纳选中改写和检查正文编辑动作。该门直接消费 `draft.revision_pack.semantic_reviewer.review_items`、`editorial_revision_draft.status`、`selectedRewriteCount`、`localizedRewriteCount`、`confirmation_gate.author_action` 与现有 `applySelectedRewrites` / `scrollToPageItem`，不新增 API、不改 artifact。`check:author-adoption-ux` 和 `pnpm.cmd run build` 通过。

2026-06-07 导入/创世开卷旅程接力条已完成第一版：`ImportNovelPage` 在开卷前台和详细表单之间新增“开卷旅程”，把当前素材状态、世界锚定、天命书、世界沙盘和卷宗阅读组织成四段可扫读路径；`GenesisPage` 在无稿创世台和详细表单之间新增“创世旅程”，把世界雏形、世界锚定、天命书和世界沙盘串起来。两页接力条复用现有 `slugOk`、`sourceLabel` / `premiseReady`、`mock`、`canSubmit` 和 `submit`，并保留选择文件、填写章节、填写主题和返回书架动作；原有上传、可恢复分片、章节粘贴、主题创世、mock/真实模型、允许覆盖、错误提示、job polling 和进入锚定逻辑全部保留。新增 `check:open-world-onboarding-ux` 已锁定接力条位置、四段旅程、真实 state 引用和移动端两列；`pnpm.cmd run build` 通过。该刀只改前端导入/创世 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变路由/API/artifact 契约。

2026-06-07 世界书架故事卡旅程脉冲已完成第一版：`StoryEntryPage` 的每张最近故事卡现在不仅显示阶段、推荐下一步、来源和世界线运行数，还会复用 `focus.journeyPulse` 渲染“天命 / 沙盘 / 阅读 / 采纳”四段可点击旅程签。未运行世界突出“下一步确认边界”，已运行世界突出“现在读”，用户不必只依赖推荐世界卡，也能从任意故事卡直接进入对应阶段；原有推荐主按钮、世界沙盘、天命书、卷宗阅读、作者采纳台和机制档案入口全部保留。`check:story-shelf-focus` 已锁定故事卡必须复用 `journeyPulse`、旅程签必须在主打开按钮之外且位于主推荐按钮之前、移动端两列布局；`pnpm.cmd run build` 通过。该刀只改前端故事书架 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改 story list 契约、不改 artifact。

2026-06-07 卷宗阅读续读签已完成第一版：`DossierReadingPage` 在连续阅读态的当前场景导读条之后、正文段落之前新增“续读签”，把当前正在读的场景、下一场、本场误会和 `continuity_threads` 承接线集中到一处。用户不用在侧栏、sticky 导读和读后承接台之间来回找，就能知道“我读到哪、下一场看什么、这场偏差怎样影响角色下一次行动”，并可直接读下一场、回到本场或追本场误会。该刀复用 `continuous_reading.reading_sections`、`continuity_threads`、`chapter_cliffhanger`、误会图谱和既有滚动/作者台动作，不新增后端 API、不改 `dossier-reading` 契约、不改 artifact。`check:dossier-reading-ux` 已锁定续读签位置、真实字段引用、继续/追误会动作和移动端单列，`pnpm.cmd run build` 通过。

2026-06-07 沙盘策略暗线承接台已完成第一版：`WorldSandboxPage` 在策略棋盘之后、干预约束和角色行动链等密集证据前新增“下一轮暗线承接”。当真实模型 advisory 写出 `strategic_interaction` 时，页面不仅解释谁在算计谁，也会把每条暗线整理成可继续发酵的下一轮事件种子；用户可一键“作为下一轮暗线”回填到首屏运行台，并自动清空上一轮临时干预内容和投放对象，避免旧干预被误重复投放。接力台复用既有 `strategyInteractions`、`item.misread`、`item.effect`、`item.hook` 和运行台 state，不新增后端 API、不改 `POST /api/stories/<slug>/sandbox/run` 字段、不改 artifact。`check:sandbox-runner-ux` 已锁定接力台位置、真实字段引用、回填 helper、清空旧干预和移动端单列，`pnpm.cmd run build` 通过。

2026-06-07 天命生效接力台已完成第一版：`TianmingPage` 在天命书确认后、详情面板前新增“天命生效接力台”，把世界宪法已生效、锚点承压、干预边界和沙盘就绪整理成四枚可行动承接卡。用户确认根天命后不必先读完整 artifact 详情，就能直接进入世界沙盘、预编译干预、查看锚点压力或回世界锚定；接力台复用既有 `book.artifact`、`book.anchor_status`、`book.contract_pressure.pressure_tiers`、`book.mutation_policy` 和 `book.narrative_attractors`，原有宪法封面、移动端速断条、吸引子、锚点、压力、候选承载者、干预预编译和世界线代偿全部保留。`check:tianming-mobile-guide` 已锁定接力台位置、四类语义、真实字段引用和移动端单列，`pnpm.cmd run build` 通过。该刀只改前端天命书 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改 `tianming` / 干预编译 / narrative compensation 契约、不改 artifact。

2026-06-07 作者确认入卷接力台已完成第一版：`AuthorAdoptionPage` 在确认入卷详情前新增“确认入卷接力台”，把已成正史、反哺下一轮、Reviewer 定稿和回到世界整理成四段可行动承接。用户确认章节后不必先读 artifact 字段，就能直接读确认正文、查看 reading trail 或继续沙盘；接力台复用既有 `confirmation.artifacts`、`confirmation.continuation_effect.next_sandbox_entry`、`confirmation.reading_trail`、`confirmation.edit_source` 和 `confirmation.accepted_local_rewrites`，原有确认详情、Reviewer 检查和跨卷宗阅读链全部保留。`check:author-adoption-ux` 已锁定接力台位置、四类语义、真实字段引用和移动端单列，`pnpm.cmd run build` 通过。该刀只改前端作者采纳 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改采纳/草稿/Reviewer/确认入卷契约、不改 artifact。

2026-06-07 世界自演昨夜醒来台已完成第一版：`WorldSandboxPage` 的世界自演结果在“昨夜世界演化报告”内新增“昨夜世界醒来台”，把 `overnight_report.what_happened`、首条角色记忆、`why_world_changed` 和 `readable_entry`/继续阅读提示整理成四枚可点击承接卡。用户能先像读醒来报告一样判断这一夜发生了什么、谁带着记忆醒来、世界为什么变了、从哪里继续读，再进入卷宗阅读或昨夜时间线；原有任务进度、刷新/暂停/恢复、停止证据、中断原因、恢复检查点、`WakeReadingEntry`、醒来时间线、小说节拍和检查点回放列表全部保留。`check:sandbox-runner-ux` 已锁定醒来台位置、四类语义、真实字段引用和移动端单列，`pnpm.cmd run build` 通过。该刀只改前端沙盘页 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改变 `world-autopilot` / `readable_entry` 契约、不改 artifact。

2026-06-07 检查点醒来接力台已完成第一版：`CheckpointReplayPage` 在 `WorldRunway` 之后、检查点回放详情之前新增“检查点醒来接力台”，把醒来大事、角色记忆、代偿压力和接回正文整理成四枚可点击承接卡。用户能先判断这一夜世界发生了什么、谁记住了什么、代价压向哪里、下一段正文该从哪里继续，再跳到醒来报告、角色记忆、具象代偿或作者采纳台；原有移动端“继续读 / 看记忆 / 看代偿 / 作者台”醒来导读条、醒来回放中枢、读报告/查证据模式、回放摘要、记忆变化、具象代偿和后续可写方向全部保留。`check:checkpoint-replay-ux` 已锁定接力台位置、四类语义、真实字段引用和移动端单列，`pnpm.cmd run build` 通过。该刀只改前端检查点回放 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改自演检查点或 `readable_entry` 契约、不改 artifact。

2026-06-07 事件多视角信息差接力台已完成第一版：`EventPerspectivePage` 在 `WorldRunway` 之后、三栏事件阅读布局之前新增“事件信息差接力台”，把事件现场、信息差、首要误读和送入下一章整理成四枚可点击承接卡。用户能先判断这一刻被谁看错了，再跳到事件封面、信息差、误读列表或作者采纳台；原有移动端“读事件 / 看信息差 / 查证据 / 作者台”导读条、事件节拍、事件正文、信息差、误读列表、下一步动作和证据区全部保留。`check:event-perspective-ux` 已锁定接力台位置、四类语义、真实字段引用和移动端单列，`pnpm.cmd run build` 通过。该刀只改前端事件多视角 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改 `event-perspective` 契约、不改 artifact。

2026-06-07 势力卷压力接力台已完成第一版：`FactionVolumePage` 在 `WorldRunway` 之后、三栏势力阅读布局之前新增“势力压力接力台”，把当前站位、代偿压力、最近 ledger 和下一轮秩序整理成四枚可点击承接卡。用户能先判断这支势力会把代价推向哪里，再跳到势力卷封面、势力代偿状态、最近记录或作者采纳台；原有移动端“看站位 / 查代偿 / 换势力 / 作者台”导读条、势力目录、势力正文、代偿状态、ledger 和证据区全部保留。`check:faction-volume-ux` 已锁定压力接力台位置、四类语义、真实字段引用和移动端单列，`pnpm.cmd run build` 通过。该刀只改前端势力卷 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改 `dossier-reading` / `worldline-state` 契约、不改 artifact。

2026-06-07 长线卷跨章回收台已完成第一版：`LonglineReadingPage` 在 `WorldRunway` 之后、长线阅读状态区之前新增“跨章回收台”，把 `current_tension`、首条待回收 `misbelief_recovery`、首条 `open_threads` 和 `next_chapter_hook` 组织成四枚可点击承接卡。用户能先判断当前张力、首要误会、活跃线索和下一章钩子，再跳到当前节点、回收误会、追线索或送到作者台；原有长线阅读进度、多事件索引、误会回收台、未解线索、移动端导读条和证据区全部保留。`check:longline-reading-ux` 已锁定回收台位置、四类语义、真实字段引用和移动端单列，`pnpm.cmd run build` 通过。该刀只改前端长线卷 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改 `longline-reading` 契约、不改 artifact。

2026-06-07 角色个人卷记忆接力台已完成第一版：`CharacterVolumePage` 在 `WorldRunway` 之后、三栏长阅读布局之前新增“记忆接力台”，把当前立场、最新主观记忆、首要误会和下一轮行动整理成四枚可点击承接卡。用户能先判断这个角色会带着什么偏见、误会、秘密和行动预期进入下一章，再跳到角色卷封面、主观记忆链、误会核对或作者采纳台；原有移动端“读立场 / 查记忆 / 换角色 / 作者台”导读条、角色目录、角色卷正文、主观记忆链和证据区全部保留。`check:character-volume-ux` 已锁定记忆接力台位置、四类语义、真实字段引用和移动端单列，`pnpm.cmd run build` 通过。该刀只改前端角色个人卷 JSX/CSS、结构检查脚本和文档，不新增后端 API、不改 `dossier-reading` / `subjective-memory` 契约、不改 artifact。

2026-06-07 世界线状态接力台已完成第一版：`WorldlineDossierPage` 在世界线工作流总览之后、`WorldRunway` 之前新增“状态接力台”，把角色记忆、因果代偿、最近检查点和下一轮入口四件事组织成同一排可点击承接卡。该接力台只消费既有 `worldline_state`、`next_round_reads`、`consequenceDomains`、`latestCheckpoint` 和自演任务数据，不新增后端 API、不改 artifact；用户能从这里直接进入长线卷、具象代偿账、检查点回放、任务区或继续沙盘。`check:worldline-dossier-ux` 已锁定接力台位置、四类语义和移动端单列，`pnpm.cmd run build` 通过。

2026-06-07 WorldWorkspaceShell 状态预告已完成第一版：`worldRouteContext` 为所有世界内路由新增 `stateHandoffs`，按“正在承接 / 会留下 / 下一处看见”说明当前页面正在消费什么、会把后果写到哪里、沿建议动作能在哪里看见结果。`WorldWorkspaceShell` 在当前任务条与世界脉搏之间渲染三枚可点击状态预告签，沙盘页会提示“事件与干预 -> 记忆与代偿 -> 进入卷宗阅读”，角色卷会提示主观记忆怎样回到下一轮行动，作者台会提示采纳结果如何反哺下一章入口。`check:world-route-context` 已锁定沙盘和角色卷的状态预告语义，`check:app-shell-mobile-layout` 已锁定共享壳必须渲染状态预告、桌面三列、移动端单列；`pnpm.cmd run build` 通过。该刀只改前端语义 helper、共享壳层、样式和检查脚本，不新增后端 API、不改路由契约、不改 artifact。

2026-06-07 WorldWorkspaceShell 旅程总线已完成第一版：前端新增共享 `WorldWorkspaceShell` 组件，`AppShell` 不再直接承载世界位置区的 JSX，而是把 `worldRouteContext`、本机最近阅读和下一步动作交给统一世界工作区壳渲染。壳层在原有当前位置、世界工作区总览、当前任务条、世界脉搏、体验轨道和卷宗速览盘之外，新增“世界旅程总线”，把“定界 / 运行 / 阅读 / 采纳”四段变成稳定的可点击扫读行，当前阶段标出“当前所在”，其它阶段标出“可随时进入”。`check:app-shell-mobile-layout` 已锁定 AppShell 必须委托 `WorldWorkspaceShell`、共享壳必须保留阶段和卷宗导航、旅程总线必须桌面四列/移动端两列；`check:world-route-context` 和 `pnpm.cmd run build` 通过。该刀只改前端共享壳层组件、样式和检查脚本，不新增后端 API、不改路由契约、不改 artifact；完整 `WorldWorkspaceShell` 仍需继续承接跨页面视觉 QA 和更深世界状态提示。

2026-06-07 AppShell 当前任务条已完成第一版：`AppShell` 在世界工作区总览和世界脉搏之间新增“当前任务”承接条，把 `worldRouteContext.primaryActionLabel`、`workspaceSummary.why`、全局继续阅读、主动作和次动作放在同一纸面行里。用户跨天命书、沙盘、阅读、角色卷、势力卷、事件卷、长线卷、世界线、检查点、多视角、作者台和机制档案时，不必再从右上按钮区或多个导航盘里猜下一步；移动端任务条先显示“建议先做”和理由，再用自适应紧凑动作保留继续阅读、主动作和次动作。`check:app-shell-mobile-layout` 已锁定任务条存在、主动作与理由绑定、桌面一行扫读、移动端不丢动作；`check:world-route-context` 和 `pnpm.cmd run build` 通过。该刀只改前端共享壳层 JSX/CSS 和检查脚本，不新增后端 API、不改路由契约、不改 artifact。

2026-06-07 WorldRunway 下一步承接层已完成第一版：共享 `WorldRunway` 会从传入 `actions` 中自动提取 `primary` 动作，渲染为“建议先做”纸面承接卡，其余动作保留在下方“还可以”出口里；沙盘、卷宗阅读、角色卷、势力卷、事件卷、长线卷、世界线、检查点和作者采纳台都能在同一导览层里先看到主动作，再选择其它出口。新增 `check:world-runway-ux` 锁定 primary action 提炼、secondary actions 保留、桌面三栏导览和移动端不强撑高行；`pnpm.cmd run build` 通过。该刀只改前端共享导览组件、样式、检查脚本和文档，不新增后端 API、不改 artifact、不删各页面原有按钮。

2026-06-07 AppShell 世界脉搏条已完成第一版：`worldRouteContext` 为所有世界内路由新增 `continuitySignals`，按“记忆 / 代偿 / 正文 / 写作”四类输出可点击世界连续性信号；`AppShell` 在工作区总览和体验轨道之间渲染“世界脉搏”纸面条，让用户跨天命书、沙盘、阅读、长线、角色卷、势力卷、事件卷、世界线、检查点、多视角、作者台和机制档案时，都能持续看到角色记忆、世界代偿、正文续读和下一章材料该接到哪里。`check:app-shell-mobile-layout` 已锁定脉搏条必须渲染、四类信号必须可点击并在移动端压成两列；`check:world-route-context` 和 `pnpm.cmd run build` 通过。该刀只改前端共享壳层、route context、样式和检查脚本，不新增后端 API、不改 artifact。

2026-06-07 AppShell 世界工作区总览已完成第一版：`worldRouteContext` 为所有世界内路由提供 `workspaceSummary`，AppShell 位置条在既有当前位置、体验轨道、卷宗速览和继续阅读入口之外，新增“当前环节 / 承接世界线 / 下一步为什么做”三枚纸面信息签。用户跨天命书、沙盘、阅读、长线、角色卷、势力卷、事件卷、世界线、检查点、活体小说、作者台或机制档案时，都能一眼看见自己处在定界/运行/阅读/采纳哪一环、当前承接哪条世界线、下一步动作为什么服务世界沙盘链路。`check:world-route-context` 已锁定语义数据，`check:app-shell-mobile-layout` 已锁定共享壳层总览、移动端单列和既有导航不丢；`pnpm.cmd run build` 通过。该刀只改前端共享壳层、route context、样式和检查脚本，不新增后端 API、不改 artifact。

2026-06-07 AppShell 世界旅程指针已完成第一版：AppShell 顶栏下的“当前环节 / 承接世界线 / 下一步为什么做”不再只是静态说明，三枚纸面信息签均可点击：当前环节回到对应旅程入口，承接世界线进入世界线档案，下一步说明直接执行主动作。这样用户跨页面时既能理解自己在定界、运行、阅读或采纳哪一环，也能马上进入对应操作，不必再到顶栏和页面深处找按钮。`check:app-shell-mobile-layout` 已锁定这些信息签必须保持可点击旅程指针、下一步必须执行 `primaryRoute`、世界线签必须进入世界线档案；该刀只改前端共享壳层 JSX/CSS 和检查脚本，不新增后端 API、不改 artifact。

2026-06-07 世界书架推荐世界续行台已完成第一版：`storyShelfFocus` 为推荐世界新增 `journeyPulse`，按“天命 / 沙盘 / 阅读 / 采纳”输出当前状态和提示；`StoryEntryPage` 的推荐进入卡新增四枚可点击旅程状态签，新世界会把“天命”标为下一步，已运行世界会把“阅读”标为现在读，同时可直达沙盘或作者采纳台。`check:story-shelf-focus` 已锁定 fresh/running 两类世界的旅程脉冲语义、推荐卡必须渲染 `entry__spotlight-pulse`，以及移动端两列布局；该刀只改前端入口 helper、故事书架 JSX/CSS 和检查脚本，不新增后端 API、不改 artifact。

2026-06-07 卷宗阅读本卷场景轨道已完成第一版：`DossierReadingPage` 在连续阅读正文卡内、当前场景导读条之前新增“本卷场景”横向阅读轨道，读小说模式隐藏侧栏时仍能看到整卷场景结构、当前阅读进度、每场视角和证据数；点击任一场景会复用既有 `scrollToSection` 定位正文段落。移动端轨道横向滚动，不挤压正文；查卷宗模式原有侧栏阅读进度、误会图谱、卷宗 tab 和证据链全部保留。`check:dossier-reading-ux` 已锁定轨道位置、跳转入口和窄屏横向滚动；该刀只改前端卷宗阅读 JSX/CSS 和检查脚本，不新增后端 API、不改 `dossier-reading` 契约、不改 artifact。

2026-06-07 检查点回放模式切换已完成第一版：`CheckpointReplayPage` 顶部醒来回放中枢新增“读报告 / 查证据”切换，默认读报告模式聚焦“从这个检查点继续读”和“下一步可写方向”，隐藏回放摘要、角色记忆和具象代偿证据区；查证据模式恢复摘要、记忆和代偿核对。移动端“看记忆 / 看代偿”会先切到查证据再定位对应区块。`check:checkpoint-replay-ux` 已锁定模式状态、布局切换和证据区保留；`pnpm.cmd run build` 通过。该刀只改前端检查点回放 JSX、共用世界线 CSS 和检查脚本，不新增后端 API、不改自演检查点或 `readable_entry` 契约、不改 artifact。

2026-06-07 作者采纳台工作台模式切换已完成第一版：`AuthorAdoptionPage` 顶部工作流中枢新增“写作台 / 审稿台”切换，默认写作台保留采纳决策、原大纲、沙盘涌现剧情和作者备注；采纳记录、生成草稿、采纳局部改写或确认入卷后自动切到审稿台，把注意力集中到采纳结果、下一章草稿、Reviewer 局部重写、编辑后定稿和确认入卷。`check:author-adoption-ux` 已锁定工作台模式状态、布局切换和材料区保留；`pnpm.cmd run build` 通过。该刀只改前端作者采纳 JSX/CSS 和检查脚本，不新增后端 API、不改采纳/草稿/Reviewer/确认入卷契约、不改 artifact。

2026-06-07 卷宗阅读模式切换已完成第一版：`DossierReadingPage` 顶部新增“读小说 / 查卷宗”切换，默认读小说模式隐藏侧栏并把正文居中为更舒展的纸面阅读；查卷宗模式恢复卷宗目录、阅读进度、误会图谱和 tab 切换。移动端“开始读正文 / 查卷宗”导读条也接入同一模式切换。`check:dossier-reading-ux` 已锁定模式状态、布局切换和侧栏保留；`pnpm.cmd run build` 通过。该刀只改前端卷宗阅读 JSX/CSS 和检查脚本，不新增后端 API、不改 `dossier-reading` 契约、不改 artifact。

2026-06-07 沙盘下一轮承接已完成第一版：`WorldSandboxPage` 的“后续剧情可能性”从静态展示改为可继续运行的入口，每条可能性都可一键“作为下一轮事件”回填到首屏运行台，并清空上一轮临时干预内容和投放对象，避免用户无意重复投放旧干预；页面会显示“已放入运行台”反馈。`check:sandbox-runner-ux` 已锁定后续可能性必须可回填下一轮、必须提示不沿用上轮临时干预，并覆盖窄屏动作布局；`pnpm.cmd run build` 通过。该刀只改前端沙盘页 JSX/CSS 和检查脚本，不新增后端 API、不改 `POST /api/stories/<slug>/sandbox/run` 字段、不改 artifact。

2026-06-07 沙盘策略棋盘已完成第一版：`WorldSandboxPage` 在单轮结果承接台之后、角色行动链之前新增“策略棋盘”，只在真实模型 advisory 写出 `strategic_interaction` 时出现，把“谁在算计谁”、策略、私下目的、筹码、误判、风险和预期世界影响提前整理成可扫读卡片。原有角色行动链里的模型临场判断和策略明细仍保留；`check:sandbox-runner-ux` 已锁定策略棋盘必须桥接在结果总览和角色行动链之间，并覆盖窄屏单列布局；`pnpm.cmd run build` 通过。该刀只改前端沙盘页 JSX/CSS 和检查脚本，不新增后端 API、不改 `POST /api/stories/<slug>/sandbox/run` 字段、不改 artifact。

2026-06-07 沙盘结果承接台已完成第一版：`WorldSandboxPage` 在单轮沙盘出结果后、干预约束/世界线/角色行动链等细节前新增“本轮已发生”承接区，把本轮事件、角色行动数、主观记忆数、因果债、锚点压力、资源/秘密变化和最先被推到台前的角色整理成一眼可读的结果总览；四个动作“读成正文 / 看世界线 / 生成多视角 / 再推一轮”分别接到既有卷宗阅读、世界线档案、多视角和运行台，帮助用户从“跑完一轮”自然进入阅读、追因果或继续运行。`check:sandbox-runner-ux` 已锁定承接区必须出现在角色行动链前、包含四个动作和移动端折叠；`pnpm.cmd run build` 通过。该刀只改前端沙盘页 JSX/CSS 和检查脚本，不新增后端 API、不改 `POST /api/stories/<slug>/sandbox/run` 字段、不改 artifact。

2026-06-07 卷宗阅读余波承接台已完成第一版：`DossierReadingPage` 在连续阅读正文、关联卷宗之后和证据附录之前新增“读完之后，世界还在继续”承接区，把下一章悬念、误会数量和下一步动作整理为“回看误会图谱 / 追踪跨事件余波 / 继续一轮沙盘 / 写成下一章材料”。四个入口分别复用既有误会图谱滚动、长线卷、世界沙盘和作者采纳台路由，帮助用户读完正文后立刻把余波接回世界运行与作者承接。`check:dossier-reading-ux` 已锁定承接区位于证据附录之前、包含四个动作，并在 640px 下折为单列；`pnpm.cmd run build` 通过。该刀只改前端卷宗阅读 JSX/CSS 和检查脚本，不新增后端 API、不改 `dossier-reading` 契约、不改 artifact。

2026-06-07 机制档案移动端导读条已完成第一版：`WorkspacePage` 仍作为“世界正史与机制档案”保留旧正史、旧分支、导入检查、检索/Graph 支撑层、审计和运行证据，不继续承载新的主线面板；移动端在标题区后、完整档案中枢前新增“天命书 / 沙盘 / 读卷宗 / 查证据”四格导读条，前三项回到主旅程，最后一项滚到机制档案证据指标区。新增 `check:workspace-archive-ux` 锁定导读条必须出现在完整档案中枢前、桌面隐藏/移动端显示。Chrome CDP smoke 验证 390px 下导读条位于 631-782px 首屏内，真实坐标点击“查证据”后指标区进入 390-838px 可见区，页面宽度保持 390px、无业务内容横向溢出。该刀只改前端机制档案 JSX/CSS 和检查脚本，不新增后端 API、不改 workspace/project API、不改 artifact。

2026-06-07 天命书移动端宪法速断条已完成第一版：`TianmingPage` 在移动端 hero 后、完整天命书工作流中枢前新增“生成/确认/沙盘 / 看锚点 / 投干预 / 去沙盘”四格速断条，主按钮随状态生成草案、确认天命或进入世界沙盘；辅助入口分别滚到锚点/状态区、干预预编译区或进入沙盘。新增 `check:tianming-mobile-guide` 锁定速断条必须出现在完整工作流中枢前、桌面隐藏/移动端显示。Chrome CDP smoke 验证 390px 下速断条位于 640-788px 首屏内，真实坐标点击“投干预”后干预预编译区进入可见区，页面宽度保持 390px、无业务内容横向溢出。该刀只改前端天命书 JSX/CSS 和检查脚本，不新增后端 API、不改 `tianming` / 干预编译 / narrative compensation 契约、不改 artifact。

2026-06-07 多视角移动端分镜导读条已完成第一版：`CharacterLensPage` 在移动端 hero 后、完整多视角工作流中枢前新增“生成 / 改事件 / 读卷宗 / 作者台”四格导读条，分别生成多视角、滚到事件材料表单、进入卷宗阅读或跳作者采纳台；生成后主按钮会改为“看结果”并滚到多视角输出区。新增 `check:character-lens-ux` 锁定导读条必须出现在完整工作流中枢前、桌面隐藏/移动端显示。Chrome CDP smoke 验证 390px 下导读条位于 689-841px 首屏内，点击“改事件”能把表单带入可见区，页面宽度保持 390px、无业务内容横向溢出。该刀只改前端多视角页 JSX/CSS 和检查脚本，不新增后端 API、不改 `character_lens` 契约、不改 artifact。

2026-06-07 世界线移动端承接导读条已完成第一版：`WorldlineDossierPage` 在移动端 hero 后、完整世界线工作流中枢前新增“回放 / 看代偿 / 看任务 / 长线卷”四格导读条，分别回放最近检查点（无检查点时进入沙盘）、滚到具象代偿账、滚到自演任务/检查点区或跳长线卷；桌面仍保持原世界线档案工作台。新增 `check:worldline-dossier-ux` 锁定导读条必须出现在完整工作流中枢和 `WorldRunway` 前、桌面隐藏/移动端显示。Chrome CDP smoke 验证 390px 下导读条位于 573-743px 首屏内，点击“看代偿”和“看任务”能把对应段落带入可见区，页面宽度保持 390px、无业务内容横向溢出。该刀只改前端世界线页 JSX/CSS 和检查脚本，不新增后端 API、不改 `worldline_dossier` 契约、不改 artifact。

2026-06-07 检查点回放移动端醒来导读条已完成第一版：`CheckpointReplayPage` 在移动端 hero 后、完整醒来回放中枢前新增“继续读 / 看记忆 / 看代偿 / 作者台”四格导读条，分别进入连续阅读、滚到角色记忆、滚到具象代偿或跳作者采纳台；桌面仍保持原检查点回放工作台。新增 `check:checkpoint-replay-ux` 锁定导读条必须出现在完整工作流中枢和 `WorldRunway` 前、桌面隐藏/移动端显示。Chrome CDP smoke 验证 390px 下导读条位于 573-767px 首屏内，点击“看记忆”和“看代偿”能把对应证据段带入可见区，页面宽度保持 390px、无业务内容横向溢出。该刀只改前端检查点回放 JSX/CSS 和检查脚本，不新增后端 API、不改自演检查点或 `readable_entry` 契约、不改 artifact。

2026-06-07 势力卷移动端导读条已完成第一版：`FactionVolumePage` 在移动端首屏新增“看站位 / 查代偿 / 换势力 / 作者台”四格导读条，分别滚到当前势力站位、势力代偿状态、势力目录或跳作者采纳台；桌面仍保持原势力卷工作台。新增 `check:faction-volume-ux` 锁定导读条必须出现在 `WorldRunway` 前、桌面隐藏/移动端显示。Chrome CDP smoke 验证 390px 下导读条位于 592-646px 首屏内，点击“查代偿”和“换势力”能把势力代偿与势力目录带入可见区，桌面 1366px 下导读条隐藏，两个尺寸均无业务内容横向溢出。该刀只改前端势力卷 JSX/CSS 和检查脚本，不新增后端 API、不改 `dossier-reading` 或 `worldline-state` 契约、不改 artifact。

2026-06-07 角色个人卷移动端导读条已完成第一版：`CharacterVolumePage` 在移动端首屏新增“读立场 / 查记忆 / 换角色 / 作者台”四格导读条，分别滚到当前角色立场、主观记忆链、角色目录或跳作者采纳台；桌面仍保持原角色卷工作台。新增 `check:character-volume-ux` 锁定导读条必须出现在 `WorldRunway` 前、桌面隐藏/移动端显示。Chrome CDP smoke 验证 390px 下导读条位于 592-646px 首屏内，点击“查记忆”和“换角色”能把主观记忆链和角色目录带入可见区，桌面 1366px 下导读条隐藏，两个尺寸均无业务内容横向溢出。该刀只改前端角色卷 JSX/CSS 和检查脚本，不新增后端 API、不改 `dossier-reading` 或 `subjective-memory` 契约、不改 artifact。

2026-06-07 事件多视角移动端导读条已完成第一版：`EventPerspectivePage` 在移动端首屏新增“读事件 / 看信息差 / 查证据 / 作者台”四格导读条，分别滚到当前事件、信息差、证据链或跳作者采纳台；桌面仍保持原事件三栏工作台。新增 `check:event-perspective-ux` 锁定导读条必须出现在 `WorldRunway` 前、桌面隐藏/移动端显示。Chrome CDP smoke 验证 390px 下导读条位于 653-706px 首屏内，点击“看信息差”和“查证据”能把对应段落带入可见区，桌面 1366px 下导读条隐藏，两个尺寸均无业务内容横向溢出。该刀只改前端事件页 JSX/CSS 和检查脚本，不新增后端 API、不改 `event-perspective` 契约、不改 artifact。

2026-06-07 世界锚定页状态条已完成第一版：`WorldAnchorPage` 新增复用 `worldJourney` / `deriveWorldPulse` 的“当前阶段 / 下一步 / 世界脉搏”状态条，桌面显示在世界卷宗总览顶部，移动端额外前置到世界品牌和启动卡之间，帮助用户进世界后先理解“世界现在到哪、下一步该做什么、为什么值得继续”。新增 `check:world-anchor-status-ribbon` 锁定状态条位置、journey/pulse 复用和移动端样式。Chrome CDP smoke 验证 390px 下状态条位于 468-726px 首屏内，点击“下一步”可跳最近阅读，桌面 1366px 下状态条在中栏总览内，两个尺寸均无业务内容横向溢出。该刀只改前端锚定页 JSX/CSS 和检查脚本，不新增后端 API、不改 artifact、不删编辑锚定、视觉资产、基线回放、实体别名、角色栏或既有入口。

2026-06-07 长线卷移动端导读条已完成第一版：`LonglineReadingPage` 在移动端首屏新增“读长线 / 按事件追 / 回收误会 / 作者台”四格导读条，分别滚到长线阅读进度、事件索引、误会回收台或跳作者采纳台；新增 `check:longline-reading-ux` 锁定导读条位于 `WorldRunway` 前、桌面隐藏/移动端显示。Chrome CDP smoke 验证 390px 下导读条在首屏内，四枚入口都可把对应区域带入可见区或跳到作者台，页面业务内容无水平溢出。该刀只改前端长线卷 JSX/CSS 和检查脚本，不新增后端 API、不改 `longline-reading` 契约、不改 artifact。

2026-06-07 作者采纳台移动端中枢压缩与材料入口已完成第一版：`AuthorAdoptionPage` 顶部工作流中枢新增“调整材料”动作，可直接滚到采纳决策、原大纲、沙盘涌现剧情和作者备注表单；620px 以下压缩标题、中枢卡片和四步说明，把“写入采纳台 / 调整材料 / 回世界沙盘”稳定放进 390px 首屏。新增 `check:author-adoption-ux` 锁定材料入口、导览前位置和移动端两列动作布局；Chrome CDP smoke 验证 390px 下中枢动作 bottom 从 851 降到 760，三枚动作完整可见，点击“调整材料”后表单进入可见区且页面无业务内容横向溢出。该刀只改前端作者采纳页 JSX/CSS 和检查脚本，不新增后端 API、不改采纳/草稿/Reviewer/确认入卷契约、不改 artifact。

2026-06-07 卷宗阅读移动端导读条已完成第一版：`DossierReadingPage` 在移动端首屏新增“开始读正文 / 查卷宗 / 作者台”三步导读条，桌面仍保持原阅读工作台；三个入口分别滚到正文卡、卷宗目录和作者采纳台，帮助用户不用先理解 artifact 或侧栏结构，也能立刻开始阅读、核对卷宗或进入续写。新增 `check:dossier-reading-ux` 锁定导读条必须出现在 `WorldRunway` 前且只在移动端显示；Chrome CDP smoke 验证 390px 下导读条在首屏内，点击三枚入口分别把正文/卷宗目录带入可见区或跳到作者台，页面宽度保持 390px。该刀只改前端阅读页 JSX/CSS 和检查脚本，不新增后端 API、不改 `dossier-reading` 契约、不改 artifact。

2026-06-07 沙盘页首屏运行台前置已完成第一版：`WorldSandboxPage` 将现有“写事件 / 可选干预 / 启动推演”运行台从导览层下方提升到首屏 hero 右侧，移动端排在标题说明后、导览之前；默认路径调整为先写大事件并立即可点“启动一轮推演”，读者干预、投放对象、投放方式和真实模型建议仍保留在可选区。`check:sandbox-runner-ux` 已锁定运行台必须出现在 `WorldRunway` 前；Chrome CDP smoke 验证桌面运行台在导览前、390px 下“启动一轮推演”按钮完整进入 844px 首屏（bottom=823）、可选干预展开后仍无水平溢出，旧的天命书、多视角、世界线、机制档案入口均保留。该刀只改前端沙盘页布局/CSS 和检查脚本，不改 `POST /api/stories/<slug>/sandbox/run` 字段、不新增后端 API、不改 artifact。

2026-06-07 世界书架推荐世界面板已完成第一版：`storyShelfFocus` 新增 `deriveStoryShelfSpotlight`，按导入优先、已有沙盘结果次之、原顺序兜底选择推荐世界，并输出推荐理由、状态、主动作和指标；`StoryEntryPage` 首屏新增推荐进入面板，桌面右侧展示，390px 移动端排在流程卡前，并将封面压成横幅，确保推荐主按钮进入首屏。旧的内置样例、导入小说、主题创世、最近故事卡，以及世界沙盘、天命书、卷宗阅读、作者采纳台、机制档案入口全部保留。`check:story-shelf-focus` 已覆盖 spotlight 选择规则；Chrome CDP smoke 验证 `#/` 桌面和 390px 下均有 1 个推荐面板、3 张启动卡、3 个故事卡组、无水平溢出，移动端主按钮首屏可见并能进入 `#/world/my-story/tianming`。该刀只改前端入口理解和 CSS，不新增后端 API、不改 artifact。

2026-06-07 世界锚定页世界脉搏已完成第一版：`worldJourney` 新增 `deriveWorldPulse`，把当前正文、可行动角色、开放伏笔和沙盘运行次数整理成四张“世界脉搏”卡；`WorldAnchorPage` 在世界卷宗总览中前置该脉搏条，让用户进入某个世界后先看见世界活到哪一步，再选择天命书、沙盘、卷宗阅读、世界线、多视角或作者台。`check:world-journey` 已覆盖脉搏 key、章节值和沙盘提示；Chrome CDP smoke 验证 `#/anchor/my-story` 桌面和 390px 各只有 4 张可见脉搏卡，无水平溢出，移动端仍只显示紧凑总览。该刀只改前端状态推导和锚定页 CSS/JSX，不新增后端 API、不改 artifact、不删编辑锚定、视觉资产、角色栏或既有入口。

2026-06-07 世界沙盘运行台分步化已完成第一版：`WorldSandboxPage` 的本轮运行面板从普通表单重组为“写事件 / 可选干预 / 启动推演”三步控制台，默认只要求用户输入大事件；读者干预、投放对象和投放方式被收纳进可选折叠区，真实模型决策建议和启动按钮仍保留。新增 `check:sandbox-runner-ux` 静态检查，锁定运行台结构、可选干预分组和“启动一轮推演”主动作。Chrome CDP smoke 验证桌面与 390px 下三步、主按钮和折叠干预均可用，展开后仍无水平溢出。该刀只改前端沙盘页 JSX/CSS 和检查脚本，不改 `POST /api/stories/<slug>/sandbox/run` 请求字段、不新增后端 API、不改 artifact。

2026-06-07 AppShell 移动端壳层压缩已完成第一版：`appShell.css` 将 640px 以下世界顶栏、体验轨道、动作区和卷宗速览盘整体压缩，9 个世界入口保持两行直接可见，4 个“定界 / 运行 / 阅读 / 采纳”阶段保持一行，8 个卷宗入口保持两行短标签。新增 `check:app-shell-mobile-layout` 静态检查，防止窄屏 override 把世界导航重新撑回三行以上。Chrome CDP smoke 验证 `#/world/my-story/sandbox` 在 390px 与 360px 下均为 9 个世界入口、4 个阶段、8 个卷宗入口、无水平溢出；390px 主标题起点从约 524px 提前到 417px。该刀只改前端壳层 CSS 和检查脚本，不新增后端 API、不改 artifact、不删顶栏导航/体验轨道/全局续读/卷宗速览盘。

2026-06-07 AppShell 全局卷宗速览盘已完成第一版：`worldRouteContext` 新增 `dossiers` 语义，给每个世界内路由统一输出“正文 / 正史 / 锚点 / 角色 / 势力 / 事件 / 长线 / 世界线”八个可点击卷宗入口和当前高亮；`AppShell` 在世界位置条下方渲染卷宗速览盘，桌面保留短标签和全名，390px 移动端压成两行短标签，帮助用户随时理解这个世界有哪些可读卷宗。桌面 smoke 验证 `#/world/my-story/sandbox` 点击“事件”进入 `#/world/my-story/worldlines/main/reading/event_multi_perspective`；角色卷 tab 正确高亮；390px 移动端八个入口完整可见且无水平溢出。该刀只改前端壳层和路由 helper，不新增后端 API、不改 artifact、不删顶栏导航/体验轨道/全局续读。

2026-06-07 AppShell 全局续读入口已完成第一版：`readingProgress` 新增 `shouldShowRecentReading` helper；`AppShell` 会在同一世界已有最近阅读记录且当前不在该阅读位置时，在世界位置条动作区显示“继续阅读”，点击回到最近阅读 hash。桌面 smoke 验证先访问长线卷写入最近阅读，再到沙盘页出现“继续阅读 / 进入卷宗阅读 / 查看世界线”，点击续读回到 `#/world/my-story/worldlines/main/longline`；390px 移动端三枚动作按钮完整可见且无水平溢出。该刀只复用浏览器 localStorage，不新增后端 API、不做账号级同步、不删锚定页原续读能力。

2026-06-07 AppShell 世界体验轨道已完成第一版：`worldRouteContext` 在原有当前位置、页面职责和主动作/次动作之外，新增“定界 / 运行 / 阅读 / 采纳”四段世界体验轨道；`AppShell` 在世界内位置条里渲染可点击阶段按钮，当前段高亮，点击可跳天命书、世界沙盘、卷宗阅读或作者台。桌面 smoke 验证 `#/world/my-story/sandbox` 高亮“运行”，点击“阅读”进入 `#/world/my-story/worldlines/main/reading`；390px 移动端验证角色个人卷高亮“阅读”、轨道完整可见且无水平溢出。该刀只改前端壳层理解与跳转，不新增后端 API、不改 artifact、不删既有导航或按钮。

2026-06-07 世界书架下一步导览已完成第一版：前端新增 `storyShelfFocus` helper 与 `check:story-shelf-focus` 轻量检查脚本；`StoryEntryPage` 的最近故事卡现在按运行次数和来源显示“待确认天命 / 已有沙盘结果”、来源、世界线运行数和解释文案，并把主按钮切到“确认天命”或“进入卷宗阅读”。旧的世界沙盘、天命书、卷宗阅读、作者采纳台和机制档案入口全部保留；桌面 smoke 验证第一张故事卡推荐动作进入 `#/world/my-story/tianming`，390px 移动端故事卡完整可见且无水平溢出。该刀只改前端入口理解和样式，不新增后端 API、不改 artifact、不删旧路由。

2026-06-07 卷宗阅读当前场景导读条已完成第一版：前端新增 `dossierReadingFocus` helper 与 `check:dossier-reading-focus` 轻量检查脚本；`DossierReadingPage` 连续阅读态在正文上方新增纸面导读条，显示当前场次、场景标题、视角/叙事角色、本场/全卷证据和误会数量，并提供“上一场 / 下一场 / 看证据 / 追误会”动作。桌面 smoke 验证 `#/world/my-story/worldlines/main/reading` 导读条从 `01 / 05` 点击“下一场”后切到 `02 / 05`，点击“看证据”可滚到证据区；390px 移动端导读条完整可见且无水平溢出。该刀只改前端阅读交互，不新增后端 API、不改 artifact、不删既有卷宗目录/误会图谱/证据链。

2026-06-07 AppShell 世界位置条已完成第一版：前端新增 `worldRouteContext` helper 与 `check:world-route-context` 轻量检查脚本；`AppShell` 在所有世界内路由下方新增纸面“当前位置”条，按锚定、天命书、世界沙盘、卷宗阅读、长线卷、角色卷、势力卷、事件卷、世界线、检查点、多视角、作者台和机制档案说明当前页面职责，并提供主动作/次动作跳到已有路由。桌面 smoke 验证 `#/world/my-story/sandbox` 显示“当前位置 · 运行 / 世界沙盘”且主动作进入 `#/world/my-story/worldlines/main/reading`；390px 移动端验证角色卷位置条可见且无水平溢出。该刀只改前端壳层理解与跳转，不新增后端 API、不改 artifact、不删既有入口。

2026-06-07 世界锚定页旅程状态面板已完成第一版：前端新增 `worldJourney` 状态推导 helper 与 `check:world-journey` 轻量检查脚本；`WorldAnchorPage` 的世界卷宗总览新增“当前旅程”纸面面板，把天命书、世界沙盘、卷宗阅读和作者台标成“下一步/可用/待生成”，并按是否已有本机续读或沙盘运行推荐“继续阅读 / 进入卷宗阅读 / 确认天命”。该刀只改前端组织与本地状态推导，不新增后端 API、不改 artifact、不删既有入口；Chrome 桌面与 390px 移动端已验证只有一套可见旅程面板、主动作可跳转、无水平溢出。

2026-06-07 本机最近阅读续航入口已完成第一版：前端新增 `readingProgress` 本地续读 helper，自动记录同一浏览器最近访问的卷宗阅读、长线卷、角色卷、势力卷、事件卷和检查点回放；`WorldAnchorPage` 的“世界启动”区会在有记录时显示“从上次读到的地方继续”和续读卡，点击可回到最近阅读位置。该刀只使用浏览器 localStorage，不新增后端表、不改 API/artifact、不删天命书/沙盘/卷宗阅读入口；后续若要跨设备、账号级或多用户进度，再做真实用户阅读进度持久化。

2026-06-07 长线卷误会回收台已完成第一版：`longline_reading` 在阅读进度、多事件索引和未解线索之外，additive 返回 `misbelief_recovery`，把 `perspective_biases` 中已经显形的误会整理成来源事件、牵动角色、证据数量、三步回收路径和去卷宗/作者台动作；`LonglineReadingPage` 首屏新增“误会回收台 / 把误会写回下一章”纸面面板，用户可先核对误会来源，再送到作者采纳台承接下一章。该刀不新增持久 artifact，不改 `run_scene` 默认行为，不破坏既有 artifact/API；后续仍需跨章节误会回收、跨章伏笔回收和更自然长正文节奏。

2026-06-07 长线卷阅读进度与多事件索引已完成第一版：`longline_reading` 在原有长线时间线、五条发酵线和证据链之外，additive 返回 `reading_progress`、`event_index` 和 `open_threads`，让前端能直接展示读到哪、有哪些事件、哪些误会/角色/势力/作者承接线仍需追踪；`LonglineReadingPage` 首屏新增“长线阅读进度、按事件追长线、未解线索”三块纸面面板，点击事件索引可定位当前长线节点，点击未解线索可跳回卷宗阅读、角色卷、势力卷、事件详情或作者台。该刀不新增持久 artifact，不改 `run_scene` 默认行为，不破坏既有 artifact/API；后续仍需跨章节误会回收、跨章伏笔回收和更自然长正文节奏。

2026-06-07 事件多视角详情页已完成第一版：新增只读 `event_perspective` service 与 `GET /api/stories/<slug>/worldlines/<worldline_id>/events/<event_id>/perspectives`，复用 `dossier-reading`、`character_lens_volumes`、`novel_scene_plan`、信息差、证据链和世界线来源，不新增持久 artifact；前端新增 `EventPerspectivePage` 与 `#/world/<slug>/worldlines/<worldline_id>/events/<event_id>/perspectives` 路由，把同一事件组织成事件节拍、当前片段、事件多视角正文、信息差、误读列表、证据链和去卷宗阅读/角色卷/世界线/长线卷/作者台动作。卷宗阅读页的事件多视角 tab 与多视角生成页的事件正文卡都能进入该页；顶栏会显示“事件卷”。该刀 additive 扩展 S8 事件多视角阅读入口，不改 `run_scene` 默认行为，不破坏既有 artifact/API；后续仍需跨章误会关系和更自然长正文节奏。

2026-06-06 势力卷独立页已完成第一版：`character_lens_volumes.json` 新增 `faction_volume` 正文卷，`dossier-reading` 会把势力卷纳入卷宗 tab 与认知偏差；前端新增 `FactionVolumePage` 与 `#/world/<slug>/worldlines/<worldline_id>/factions/<faction_id>` 路由，聚合世界锚定、卷宗阅读和 `worldline_state.consequence_state`，展示势力正文、势力目录、因果压力域、最近 ledger、卷内证据和去沙盘/多视角/作者台动作。世界锚定页势力标签、多视角势力卷、卷宗阅读势力卷和顶栏都能进入；没有正文卷时显示明确空态。该刀 additive 扩展 S8 正文卷宗，不改 `run_scene` 默认行为，不破坏既有 artifact/API；后续仍需跨章角色/势力长线阅读和更深跨卷证据联动。

2026-06-06 角色个人卷独立页已完成第一版：新增 `CharacterVolumePage` 与 `#/world/<slug>/worldlines/<worldline_id>/characters/<character_id>` 路由，复用既有 `dossier-reading` 与 `subjective-memory` API，把单个角色的个人卷正文、主观记忆链、误会、未知正史、秘密可见性和证据锚点组织成可读页面。锚定页角色卡、卷宗阅读角色卷、多视角角色卷和沙盘角色行动卡都能进入该页；没有 `character_lens_volumes` 正文时会用主观记忆兜底生成当前角色索引，并显示明确空态。Chrome 1366px 与精确 390px 设备模拟验证 `my-story/zhao_xuan` 可打开角色卷、5 条主观记忆可见、锚定页入口可跳转、顶栏激活“角色卷”、无水平溢出。该刀不改后端、不新增 artifact、不改变 API 契约；后续仍需跨章角色长线阅读和更深跨卷证据联动。

2026-06-06 世界锚定页世界卷宗总览已完成第一版：`WorldAnchorPage` 中栏新增“世界卷宗总览”，把天命书、世界沙盘、卷宗阅读、世界线、多视角和作者台六个主入口组织成“定界 -> 运行 -> 阅读 -> 采纳”的世界内地图，并提供机制档案出口；每个入口展示用途、当前读数和可点击动作，全部复用现有路由。移动端在“世界启动”卡后显示紧凑总览，避免用户先被视觉资产/旧机制信息淹没。原有编辑锚定、视觉资产、基线回放、实体别名、世界合约、角色卡、角色探针和三栏/移动端功能保留。Chrome 1366px 与精确 390px 设备模拟验证仅有一套可见总览、6 个入口可见、卷宗阅读和机制档案跳转正确、无水平溢出。该刀不改后端、不改变 API/artifact；后续仍需更完整 `WorldWorkspaceShell`、跨章节回收和跨卷证据联动。

2026-06-06 卷宗阅读误会图谱已完成第一版：`DossierReadingPage` 将 `perspective_biases` 从静态认知偏差列表改为可点击“误会图谱”，每个节点展示来源、卷宗/场景标签、误会说明和证据数量；点击正文场景节点会切到对应段落并高亮当前阅读位置，保留世界正史卷、主锚点卷、角色个人卷、事件多视角、确认正文 tab、底部证据面板和原有路由。章节定位从贴顶滚动改为阅读中心优先，并在用户主动点击节点/书签时短暂锁定目标，避免移动端高亮被相邻段落抢走。Chrome 1366px 与精确 390px 设备模拟验证 5 条误会节点可见，点击第二条/第一条都能定位到对应正文段落，且无水平溢出。该刀不改后端、不改变 API/artifact；后续仍需更深跨章误会关系、用户阅读进度持久化和更自然长正文节奏。

2026-06-06 卷宗阅读正文证据锚点已完成第一版：`DossierReadingPage` 的连续阅读态现在按 `continuous_reading.reading_sections` 分场景渲染正文，每一场展示标题、视角/叙事角色、认知偏差、冲突转折和对应证据锚点；侧栏新增“阅读进度”书签与进度条，点击场景可跳转并高亮当前段落。关联卷宗也从底部证据折叠里前置为可扫读卡片，保留原有卷宗 tab、认知偏差列表、底部证据面板、世界线/沙盘/作者台动作和所有路由。Chrome 1366px 与精确 390px 设备模拟验证无水平溢出，5 个阅读场景、4 个段内证据锚点和书签高亮均可见；同时修复 `0 && <...>` 导致“0 条证据”渲染成裸 `0` 的阅读瑕疵。该刀不改后端、不改变 API/artifact；后续仍需跨章误会关系、用户阅读进度持久化和更自然长正文节奏。

2026-06-06 导入/创世开卷中枢已完成第一版：`ImportNovelPage` 首屏新增“开卷前台”，把命名世界、放入正文、抽取世界、进入锚定四步前置，并提供导入、选择文件和填写章节主动作；`GenesisPage` 首屏新增“无稿创世台”，把命名世界、写下冲突、补足手感和进入锚定前置，并提供创世、填写主题和返回书架动作。两页原有导入、可恢复上传、章节粘贴、主题创世、mock/真实模型、允许覆盖、job polling 和进入世界锚定逻辑全部保留。Chrome 1366px 与精确 390px 设备模拟验证无水平溢出；移动端按钮已前置到流程卡之前，用户能先行动再看步骤。该刀不改后端、不改变路由/API/artifact；后续仍需继续深化世界内部壳、角色/势力独立卷、正文锚点和跨页面视觉 QA。

2026-06-06 前端世界入口与主旅程第一轮改造已完成，并补过首屏 QA：`StoryEntryPage` 从历史版本入口改为“未终章 · 世界书架”，新增“确认天命 -> 运行沙盘 -> 阅读卷宗 -> 采纳续写”主旅程，故事卡默认进入天命书，并保留世界沙盘、卷宗阅读、作者采纳台和机制档案入口；`AppShell` 改为“未终章 / 世界沙盘”品牌与世界内卷宗导航，统一露出锚定、天命书、沙盘、阅读、世界线、多视角、作者台和机制档案；`WorkspacePage` 降级为“世界正史与机制档案”以收纳旧支撑层，不再作为默认主体验；`WorldAnchorPage` 下一步进入天命书，`WorldSandboxPage` 空态新增从事件到正文的世界回路导引。首屏 QA 额外修正浏览器标题、内置样例无天命书时的可生成空态，以及真实 390px 移动端入口换行。该刀不删功能、不破坏路由/API/artifact；后续仍需更完整的世界内部壳、角色/势力独立卷、正文锚点、误会图谱和更强跨页面视觉细节 QA。

2026-06-06 多视角首屏工作流中枢已完成第一版：`CharacterLensPage` 在首屏新增“当前下一步”操作中枢，把选择观察点、生成五类卷宗、阅读信息差和送入作者台四步前置；空态主行动直接生成多视角，生成后主行动切到卷宗阅读，并保留作者采纳台和世界沙盘出口。中枢摘要展示 lens run、artifact、brief 数、正文卷数、角色立场数和来源事件；原有事件材料表单、brief、世界正史卷、主锚点卷、角色卷、势力卷和事件多视角展示全部保留。精确 390px Chrome 设备模拟验证无水平溢出，主操作按钮在首屏内；真实交互烟测执行“生成多视角”，页面正确切到“进入卷宗阅读”。该刀不改后端、不改变路由/API/artifact；后续仍需跨章节回收、跨章误会回收和更自然长正文节奏。

2026-06-06 世界线首屏工作流中枢已完成第一版：`WorldlineDossierPage` 在首屏新增“当前下一步”操作中枢，把确认分支状态、查看代偿、回放最近变化和进入连续正文四步前置；无检查点时主行动是继续沙盘，有检查点时主行动会切到回放最近检查点，同时保留卷宗阅读、多视角和沙盘出口。中枢摘要展示世界线状态、中文因果债等级、检查点数、自演任务数、代偿域数量和来源承接材料；原有分支状态、下一轮行动、具象代偿账、自演任务、检查点和最近世界推进模块全部保留。精确 390px Chrome 设备模拟验证无水平溢出，主操作按钮在首屏内；交互烟测确认“卷宗阅读”能进入卷宗阅读路由。该刀不改后端、不改变路由/API/artifact；后续仍需跨章节回收、跨章角色/势力长线阅读和世界自演醒来报告文学化。

2026-06-06 检查点首屏醒来回放中枢已完成第一版：`CheckpointReplayPage` 在检查点回放页首屏新增“醒来回放”操作中枢，把确认大事件、查看角色记忆、承接因果代偿和回到连续正文四步前置；主行动直接进入连续阅读，同时保留返回世界线、继续沙盘和作者采纳台出口。中枢摘要展示本轮编号、角色记忆数、后续可能数、世界阶段、世界线和因果债；原有状态变化解释、记忆变化、具象代偿、后续可写方向、`WorldRunway` 和详细回放模块全部保留。Chrome 1366px 与精确 390px 设备模拟验证无水平溢出，移动端四枚操作按钮在首屏内；交互烟测确认“继续下一段正文”能进入 `reading/continuous_reading`。该刀不改后端、不改变路由/API/artifact；后续仍需醒来报告文学化、用户阅读进度持久化和跨章节回收。

2026-06-06 机制档案首屏中枢已完成第一版：`WorkspacePage` 在旧“世界正史与机制档案”页首屏新增档案工作流中枢，把定界、运行、阅读和追溯四步前置；主行动仍指向天命书、世界沙盘、卷宗阅读和旧分支查看，原有导入检查、运行前体检、检索/Graph 支撑层、创作闭环、设定、角色卡、审计、章节片段和 artifact 网格全部保留。指标从“章节/记忆层/正史/审计/检索”改为“可读章节、运行记录、记忆/正史、需留意”，避免把机制档案误解成主线工作区。Chrome 1366px 与精确 390px 设备模拟验证无水平溢出；中枢按钮烟测确认天命书、运行沙盘和卷宗阅读路由可用。该刀不改后端、不改变 API/artifact，不往 `WorkspacePage` 继续堆新支撑层面板；后续仍需真正的 `WorldWorkspaceShell`、跨章角色/势力长线阅读和跨章节回收。

2026-06-06 作者采纳台工作流中枢已完成第一版：`AuthorAdoptionPage` 在首屏新增“当前下一步”操作中枢，把对照、入账、修订、入卷四步状态和主行动前置；顶部按钮直接复用现有写入采纳台、生成草稿、采纳局部改写、确认入卷和回世界沙盘动作，不删原有表单、Reviewer、连续阅读、编辑后定稿或确认入卷能力。精确 390px Chrome 设备模拟验证无水平溢出，主操作按钮在首屏内；真实交互烟测执行“写入采纳台 -> 生成下一章草稿”，页面正确切换到“先采纳选中改写”。该刀不改后端、不改变路由/API/artifact；后续仍需整章风格润色、真实模型编辑器、可回滚对照和作者定稿质量门。

2026-06-06 天命书首屏宪法封面已完成第一版：`TianmingPage` 新增“当前下一步”封面，把生成草案、确认根天命、干预预编译和进入沙盘四步前置；封面摘要展示状态、当前锚点、合约压力、叙事吸引子数量、多锚点数量和风险说明。顶部动作直接复用现有生成、确认、跳转沙盘和滚动到干预预编译能力，不删原有吸引子、锚点、压力、候选承载者、干预边界、干预预编译或世界线代偿模块。精确 390px Chrome 设备模拟验证无水平溢出，主按钮在首屏内；真实交互烟测执行“生成草案 -> 确认天命”，页面正确切到“进入世界沙盘”。该刀不改后端、不改变路由/API/artifact；后续仍需动态天命更新、快照审计确认和干预后的多轮追踪。

2026-06-06 世界内导览层第一版已完成：新增 `WorldRunway` 复用组件，把“当前世界线/当前工作流、三步理解路径、下一步行动”统一呈现在 `DossierReadingPage`、`WorldlineDossierPage`、`CheckpointReplayPage` 和 `AuthorAdoptionPage`；卷宗阅读页现在强调“读正文 -> 查卷宗 -> 写下一章”，世界线页强调“看状态 -> 回放检查点 -> 进入阅读”，检查点页强调“回看变化 -> 读后续 -> 写入下一章”，作者采纳台强调“比较差异 -> 采纳并改写 -> 确认入卷”。该刀不改后端、不删按钮能力、不改变路由/API/artifact；后续仍需更完整的 `WorldWorkspaceShell`、跨章角色/势力长线阅读、跨章节回收和跨页面视觉 QA。

2026-06-06 世界锚定启动体验与移动端保功能已完成第一版：`WorldAnchorPage` 左栏新增“世界启动”行动卡，把天命书、世界沙盘和卷宗阅读放在锚定页首屏；`worldAnchor.css` 不再在 1180px/820px 以下隐藏右侧角色栏或左侧锚定/视觉/审计能力，改为平板/移动端纵向排布，保留编辑锚定、视觉资产、基线回放、实体别名、世界合约、角色卡和角色探针等功能。该刀不改后端、不删旧入口、不改变 artifact/API；后续仍需继续做完整 `WorldWorkspaceShell`、跨章角色/势力长线阅读和跨章节回收。

2026-06-06 世界沙盘运行导览已完成第一版：`WorldSandboxPage` 接入 `WorldRunway`，把“投放事件 -> 观察角色 -> 进入阅读”的使用路径前置到沙盘首屏；空态时主行动聚焦运行台和天命书，出结果后切到卷宗阅读、世界线档案和多视角卷。移动端补充沙盘页按钮栅格、内边距和滚动定位约束，真实 390px 截图中沙盘页本体不再被操作按钮撑宽。该刀不改后端、不删旧入口、不改变 artifact/API；后续仍需继续做完整 `WorldWorkspaceShell`、跨章角色/势力长线阅读和跨章节回收。

2026-06-06 移动端世界卷宗导航已完成第一版：`appShell.css` 在窄屏下把顶栏右侧横向滚动的世界内部导航改为可换行卷宗盘，锚定、天命书、沙盘、阅读、长线卷、世界线、多视角、作者台和机制档案 9 个入口全部直接可见；动效与设置按钮保留在同一控制区。精确 390px Chrome 设备模拟验证 `scrollWidth === innerWidth`、导航内容不溢出、按钮文字不截断；桌面顶栏保持原一行形态。该刀不改路由、不删入口、不改变 artifact/API；后续仍需继续做完整 `WorldWorkspaceShell`、跨章角色/势力长线阅读和跨章节回收。

2026-06-06 卷宗阅读卷首题签已完成第一版：`DossierReadingPage` 的正文卡顶部新增“当前阅读卷”题签，按 active tab 展示标题、阅读理由/偏差、场景数、证据数、下一章钩子，并提供世界线、继续沙盘和作者台三枚行动入口；`WorldRunway` 的“读正文”步骤现在会滚到正文卡。移动端下正文卡排在卷宗目录前，用户先读正文、再查目录和偏差；精确 390px Chrome 设备模拟验证页面不横向溢出，行动按钮不截断。该刀不改后端、不删 tab、不改变 artifact/API；后续仍需用户阅读进度持久化、跨章误会关系和独立角色/势力卷。

2026-06-06 卷宗阅读页产品化已完成第一版：新增 `dossier_reading` service 与 `GET /api/stories/<slug>/worldlines/<worldline_id>/dossier-reading`，只读聚合同一世界线的 `continuous_reading_chapter`、`confirmed_chapter.md`、`confirmed_chapter_reading_trail`、S8 `character_lens_volumes` 和 `worldline_dossier`；前端新增 `DossierReadingPage` / `#/world/<slug>/worldlines/<worldline_id>/reading`，默认进入连续阅读正文态，可切换世界正史卷、主锚点卷、角色个人卷、事件多视角和确认正文，认知偏差可见，证据链默认折叠。该刀不新增持久 artifact，不破坏既有 API/artifact，不改 `run_scene` 默认行为；后续仍需正文内锚点跳转、独立角色/势力页、误会图谱和真实长文文风控制。

2026-06-06 世界自演结果页 -> 可读世界线入口已完成第一版：`autopilot_report.json` 新增 additive `readable_entry`，并新增 `GET /api/world-autopilot-runs/<run_id>/readable-entry`；检查点回放 API 同步返回同一入口。世界沙盘页的“昨夜世界演化报告”现在直接展示“醒来从这里读”，可跳最近关键检查点、角色个人卷、事件多视角和连续阅读，并在结果页解释为什么世界状态变了、谁记住了什么、哪条因果债在发酵；世界线档案页也可直接进入连续阅读/角色个人卷/事件多视角，卷宗阅读路由支持 `/reading/<tab>` 精准落卷。该刀不新增持久 artifact，不改旧字段，不往 `WorkspacePage` 继续堆面板；后续仍需正文内证据锚点、角色/势力独立页和误会图谱。

2026-06-06 Reviewer 局部重写 -> 作者采纳台 -> 编辑后定稿 -> 下一章入口链已收口第一版：`author_chapter_rewrite_application` service 与 `POST /api/stories/<slug>/author-adoption/<adoption_run_id>/chapter-rewrites` 支持作者在采纳台勾选 `draft_revision_pack.json` 中的片段级建议，生成 `accepted_local_rewrites.json` / `next_chapter_draft_revised.md`，并新增 `edited_final_chapter.json` / `edited_final_chapter.md`。`edited_final_chapter` 会把选中的建议应用为可确认正文，不再把审稿清单当正文；`next_chapter_draft.json` additive 记录已采纳局部改写、`chapter_text_with_accepted_rewrites` 和 `edited_final_chapter` 摘要。若作者确认入卷时未继续手改，`author_chapter_confirmation` 会自动读取 `edited_final_chapter.json`，并把 `edit_source=auto_reviewer_final`、已采纳改写 ids 和定稿 artifact 写入 `confirmed_chapter_entry.json`、`continuation_effect.next_sandbox_entry` 和 `worldline_state.confirmed_chapter_entry`。UI 仍保持古风纸面风格，局部建议展示原问题、修改意图、建议改写、影响范围和采纳方向；采纳后正文编辑框优先显示编辑后定稿。后续仍需真实长文文风、更强语义 Reviewer 和自动整章风格润色。

2026-06-06 文档治理收口：已扫描 `docs/` 根层、`docs/completed/`、论文/品牌/原型资产、根 README、`AGENTS.md`、`engine/README.md` 与 `engine/ui/README.md`。当前不批量移动历史文档，避免破坏既有链接；采用“入口事实层 -> 当前主线层 -> 路线/阶段层 -> 历史归档层 -> 支撑层索引 -> 研究/品牌/原型资产 -> 运行说明层”的分层口径。下一次开工应先读 `AGENTS.md`、本文、`docs/index.md`、世界沙盘 PRD、AI 对齐清单、迭代计划和 `engine/README.md`；`docs/completed/`、`project-changelog.md`、`docs/后续增强清单.md` 与 `docs/distribution-phase-plan.md` 只用于追溯或用户明确点名，不作为默认下一刀来源。

2026-06-06 第二层路线文档瘦身：`docs/living-novel-engine-iteration-plan.md` 已从历史阶段长表改为当前路线判断，只保留世界沙盘主线、已闭环等级、官方下一步、后置项、下一刀选择规则和验收命令；旧长版仍在 `docs/completed/living-novel-engine-iteration-plan-legacy-2026-06-01.md`。`docs/codex-handoff.md` 也已从支撑层长表收束为新窗口最小接力包，避免新会话被 Graph/provider/retrieval 历史清单带偏。

2026-06-06 支撑层清单瘦身：`docs/后续增强清单.md` 已从逐刀长待办改为“LNE 支撑层与后置增强索引”，只保留已收口分组、触发式增强规则、研究参考和追溯入口。它现在用于证明 provider、Graph、检索、OpenAPI、发行、商业化等能力已作为支撑层收口，或在用户明确点名时判断触发条件；不能从中挑选默认下一刀。

2026-06-06 主 PRD 瘦身：`docs/living-novel-engine-prd.md` 已从混有 v0.8/v0.9/v1.0 和 Graph/provider 长历史的综合长文，收束为当前产品 PRD；只保留定位、主体验、用户价值、已闭环、真实未做项、后置边界和验收口径。历史逐刀细节回指 `docs/project-changelog.md`、`docs/completed/README.md` 和 `docs/后续增强清单.md`。

2026-06-06 产品愿景纠偏稿瘦身：`docs/unfinale-product-vision-correction-draft.md` 已从讨论期长记录收束为愿景与设计原则文档，只保留原始愿望、双入口、一套底层、领域记忆模型、《天命书》、干预、代偿、多视角、Reviewer、UI 方向和不再扩张的支撑层边界。讨论期 v1-v12 节奏和长 UI 描述不再作为当前执行路线；执行以世界沙盘 PRD 和本文为准。

2026-06-06 阶段归类与开工自检瘦身：`docs/productization-phase-map.md` 已收束为技术 MVP、产品化 MVP、世界沙盘第一版、完整产品能力和后置排期的判定表；`docs/unfinale-ai-development-alignment-checklist.md` 已收束为开工前问题清单、当前优先候选、默认不做、代码接入判断、artifact/API 边界、真实模型验收和完成判断。二者不再复制 S1-S9 长状态流水或支撑层逐刀历史。

2026-06-06 世界沙盘 PRD 瘦身：`docs/unfinale-world-sandbox-remodel-prd.md` 已从带有多日流水记录的长 PRD 收束为当前 S1-S9 执行说明，保留目标、硬边界、主导航、第一版闭环表、核心 artifact/API、前端页面、S1-S9 后续验收和完成标准；具体历史进展回指 `docs/project-changelog.md`。

---

## 1. 当前状态（先读）

| 项 | 当前事实 |
| --- | --- |
| 项目 | 未终章（Unfinale）；技术缩写、Python 包、CLI 与环境变量前缀仍沿用 LNE / `living_novel_engine`，核心代码在 `D:\AI\open-infinite\engine` |
| 北极星 | 文本输入 -> 世界锚定 -> 角色自主行动 -> 读者干预 -> 世界线分叉 -> 章节渲染 -> 可继续运行 |
| 当前完成度 | v0.7 短中篇产品化 MVP、v0.8 长篇底座 MVP、v0.9.0-alpha 长篇共创闭环、v0.9.1-v0.9.4 触发式增强、v1.0-beta 本地优先商业化边界、v1.0-local 本地模型配置与一键运行脚本均已收口；后续增强运行前体检至 Graph/长期记忆 mock 复核链共四十五刀已收口；Retrieval Provider Real Connectivity MVP、Vector Retrieval Pipeline MVP、World Sandbox Loop S1-S9（Sandbox Round、Subjective Memory Chain、Tianming Book、Intervention Compiler、Narrative Compensation、World Autopilot、Character Lens Novel、Author Adoption Desk、Reviewer/Edited Final Chapter）第一版已收口 |
| 产品入口边界 | 前端是产品入口，API 是能力层，CLI 是工程外壳；用户级功能必须优先通过 Web UI + API 完成，CLI 只服务开发者、本地服务启动、自动化验收、批处理和无人值守复跑 |
| 测试基线 | `cd engine && python -m pytest -q` -> `951 passed`；`cd engine/ui && pnpm run build` 通过 |
| 官方下一步 | **真实模型决策 + 长正文质量 + 更强 Reviewer**：S4 后半与 S5/S6/S7/S8/S9 已形成一条可继续运行的产品链路，新增 `worldline_state.json`、`consequence_state` 六域代偿、自演任务状态、检查点回放、因果债/觉醒停止条件、失败后检查点恢复、多视角正文、下一章 brief、正式下一章草稿、作者确认入卷、确认稿跨卷宗阅读链和 `draft_revision_pack.json` 局部修订包；采纳/部分采纳/另开分支已能生成 `writing_plan` 与 `feed_forward` 并影响章节生成或后续沙盘入口；世界线/检查点独立页已补第一版 dossier 与回放入口；S1 已新增显式 opt-in 的真实 LLM 逐角色决策建议，产出 `agent_decision_advisory.json` 并进入沙盘行动/主观记忆/UI；S8/S9 已新增 `continuous_reading_chapter.json` / `continuous_reading_chapter.md`，并已通过 `dossier-reading` API 与卷宗阅读页组织成默认小说阅读入口；Reviewer 局部重写已可由作者勾选、生成编辑后定稿并反哺确认入卷和下一轮入口；下一步优先加强多轮策略规划、长期关系/势力博弈、长正文文风质量、跨章节误会回收、更强真实语义 Reviewer 和整章风格润色；不默认回到 provider/Graph/检索评测主线 |
| 当前主导航决策 | 一级按“世界书架”组织；进入某世界后使用“天命书、世界沙盘、世界正史卷、主锚点卷、角色个人卷、势力卷、事件多视角、世界线、检查点、作者采纳台”。“沙盘/阅读/干预/作者”是场景能力，不做一级工作区 |
| 支撑层边界 | GraphRAG/Zep、重型 provider 试验、真实向量检索、OpenAPI、发行、计费、对象存储、认证都已降为支撑层；除非用户明确要求，不继续扩展这些方向 |

### 1.0 闭环等级（避免下一轮被旧文档带偏）

| 等级 | 当前结论 | 还能继续深入的地方 |
| --- | --- | --- |
| 已闭环支撑层 | v0.7-v1.0-local、后续增强四十五刀、真实 retrieval provider 和 opt-in Vector Retrieval Pipeline 都有 service/API/UI/CLI 或文档证据、测试和变更记录；它们现在是支撑层，不是默认主线 | 只有用户明确要求时，再评估默认 hybrid vector、GraphRAG/Zep、发行安装包、云端队列、对象存储、认证或计费 |
| 世界沙盘 S1-S9 第一版闭环 | 《天命书》、沙盘轮次、主观记忆、干预投放、L5 觉醒/模因传播、因果债具象化、自演检查点、多视角正文、作者采纳、连续阅读和确认入卷已形成 additive 链路 | 多轮策略规划、长期关系/势力博弈、真实模型误判/欺骗的稳定性、代偿长期发酵仍需继续打磨 |
| 产品化阅读入口第一版 | `dossier-reading`、卷宗阅读页、“读小说 / 查卷宗”模式切换、移动端导读条、正文证据锚点/阅读进度、误会图谱、世界自演 `readable_entry`、角色个人卷独立页、势力卷独立页、事件多视角详情页、跨事件长线卷、长线阅读进度、多事件索引、误会回收台、长线卷移动端导读条、长线卷跨章回收台、长线卷跨章承接地图、长线卷角色/势力追踪上下文台、长线卷跨章误会网络图、本机最近阅读续航、AppShell 全局卷宗速览盘、未解线索和世界线/检查点/角色/事件/长线跳转已让用户能从结果页进入小说化阅读 | 长篇阅读节奏、账号级用户阅读进度持久化、跨章节误会回收和跨章伏笔回收仍需深入 |
| 作者采纳闭环第一版 | Reviewer 片段级建议可在作者采纳台勾选，写入 `accepted_local_rewrites.json`、`next_chapter_draft_revised.md` 与 `edited_final_chapter.json`，确认入卷可自动采用编辑后定稿并反哺下一轮入口；作者采纳台首屏已有四步工作流中枢、可点击下一步、移动端材料直达入口、Reviewer 质检门、整章修订路线、章节质感雷达和定稿对照台 | 真实语义 Reviewer、自动整章风格润色、可回滚对照和文风一致性仍需深化 |

判断“下一刀”时，先以本节和 `docs/unfinale-world-sandbox-remodel-prd.md` 为准；不要从旧变更日志或 Graph/provider 历史面板里直接捞待办。

注意：World Sandbox Loop 的“已收口”是第一版产品链路闭环口径，证明 service/API/UI/artifact/tests 与小样本真实 LLM smoke 能把世界沙盘、觉醒传播、自演、连续阅读、作者采纳、局部重写和编辑后定稿串起来；但这不等于完整愿景已经完成。真实高智商多 Agent 决策、长期心理记忆、L5 觉醒反抗、代偿持续驱动、无人值守自演体验、多视角长正文、真实语义 Reviewer 和整章文风润色仍是后续深化方向。

后续迭代纪律：工程实现可以继续小步安全推进，但产品完成标准不能再停在“最小切片闭环”。S1-S9 第一版已收口，后续深化切片只有在用户能真实感到对应能力成立时才算通过，例如角色决策真的被记忆改变、干预真的进入下一轮沙盘、代偿压力真的持续影响世界状态、采纳真的反哺下一章 brief。`有 API / 有测试 / 有页面 / 有 artifact` 只能算底线，不等于产品能力完成。下一轮复盘和后续迭代必须按这个口径验收。真实模型/API 可在用户明确允许时作为 opt-in smoke 或 LLM runner 联调使用，但默认 pytest 仍应保留 deterministic/mockable 基线，避免外网与额度依赖污染常规验证。

真实模型验收口径：用户已明确允许在本项目测试中调用其真实接入的模型 API。后续涉及叙事生成、Agent 决策、章节 brief、多视角正文、Reviewer 或视觉生成质量的切片，不能只用 mock/deterministic 测试宣布体验合格；应在常规 mock 回归之外，使用 `.env` 中已配置的真实 `LLM_API_KEY` / `SEEDREAM_API_KEY` 做小样本 smoke，并记录真实输出质量、失败原因和是否回退。单元测试仍应 mock-safe、可复现；真实 API smoke 是产品验收补充，不打印明文 key，不做大规模消耗，不把真实外网调用塞进默认全量 pytest。

远程同步纪律：后续 AI 完成一个独立切片并通过对应验证后，不能只停在本地工作树；应提交并推送到远程仓库，除非用户明确说暂不提交/暂不推送。推送前必须先检查 `git status`，只提交本轮自己负责的文件；如果工作树混有用户或另一轮 AI 的未完成改动，不能把脏状态混推，应先隔离提交范围、说明阻塞或等待当前长任务收口。没有远程、无上游分支、认证失败或网络失败时，要在收尾里明确说明未推送原因和下一步。

### 1.1 当前纠偏主线（最高优先级）

当前项目不是要继续证明 provider、检索、Graph Memory 或商业化边界，而是要把已完成的底座重新拉回最初愿望：

```text
小说不是一本写完的静态文本，
而是一个会运行、能被观察、可被干预、会分叉、角色可能反抗的故事世界。
```

后续所有开发默认服务这七件事：

```text
世界会运行。
角色会自主。
角色会记得。
干预有后果。
角色可能反抗。
世界会代偿。
章节来自世界演化。
```

首批改造目标：

```text
1. 沙盘轮次：sandbox_rounds.jsonl 已有第一版，记录每轮角色意图、行动、冲突、信息传播和世界状态 delta；API 为 `POST /api/stories/<slug>/sandbox/run`，前端入口为“世界书架 -> 世界沙盘”。
2. 主观记忆链：每个角色在每条世界线拥有独立 subjective_memory.jsonl；每轮后写入看到、做了、新认知、情绪/信任/异常感变化，并已扩展 perceived_event、inner_thought、inferred_motive、emotional_impact、trust_shift、anomaly_weight、secret_visibility、misbeliefs、unknown_canon_facts、L5 高维真相、命痕、模因传播来源、是否采信、可信度和反应类型等字段，下一轮行动和冲突会引用上一轮记忆/误会。
3. 《天命书》：tianming.json 已有第一版，并已加深为世界线宪法雏形；`narrative_attractors` 有权重/类别，`anchor_status.anchors` 支持角色/势力/谜团/地点多锚点，`contract_pressure.pressure_tiers` 支持轻微/重大/时代/世界崩坏四档；旧版已确认天命书再次读取或生成时会补齐 S3 字段，同时保留既有吸引子。
4. 干预编译器读天命书并可投放沙盘：自由干预可预编译为干预类型、层级、兼容性、转译策略、Divergent/AU、分支轴和因果债；普通干预不改写 `tianming.json`，L4/L5/AU 可写 `projects/<slug>/worldlines/<worldline_id>/tianming_snapshot.json` 且不覆盖根天命书；`POST /api/stories/<slug>/sandbox/run` 已可选接收干预文本并写 `intervention_constraint.json`，让编译结果成为本轮沙盘约束；新增 `projection_mode` / `intervention_projection_mode` 支持沉浸模式和暴走 AU，AK47 等异物会被标记为异物入侵并可选择本土化重释或保留为 AU 入侵。
5. 世界线代偿：可生成 `tianming_delta.json`，解释锚点稳定/转移/失锚、候选天命承载者、因果债扩散和世界内压力事件。
6. 世界自演：已支持运行到轮数、事件、时间、锚点变化、因果债爆发或角色觉醒，并生成 `autopilot_report.json` 与检查点；报告包含醒来时间线、停止证据和恢复入口，中途失败会记录最近检查点，任务可 resume 生成接续报告。
7. 多视角活体小说：已可把同一事件渲染为世界正史卷、主锚点卷、角色个人卷、势力卷和事件多视角，并写入 `character_lens_briefs.json`。
8. 作者采纳台：已可把沙盘涌现剧情采纳、部分采纳、另开分支或导出 brief，并写入 `author_adoption_ledger.jsonl`；采纳 run 会生成 `next_chapter_brief.json`，其中包含 `writing_plan` 与 `feed_forward`，把原大纲差异、沙盘涌现剧情、下一章可写方案、伏笔调整、Reviewer 建议和后续入口串起来；另开分支会创建作者分支 `worldline_state.json` 且不覆盖根正史。采纳 run 可继续生成 `next_chapter_draft.json`、`next_chapter_draft.md`、`draft_revision_pack.json`、`continuous_reading_chapter.json` 和 `continuous_reading_chapter.md`，作者采纳台会展示确认前 gate、局部改写建议、连续阅读稿、阅读流、下一章钩子和 S8 卷宗引用；作者可勾选 Reviewer 局部重写并生成 `accepted_local_rewrites.json` / `next_chapter_draft_revised.md` / `edited_final_chapter.json`，编辑后定稿会 additive 反哺 `next_chapter_draft.json` 与确认入口；作者可继续手改或直接确认入卷为 `confirmed_chapter_entry.json` / `confirmed_chapter.md`，同时生成 `confirmed_chapter_reading_trail.json`，把确认稿回读到世界正史卷、角色个人卷和事件多视角证据；确认结果会回写世界线状态、已采纳改写 ids、定稿 artifact 和后续沙盘入口。
```

本次纠偏新增入口文档：

- `docs/unfinale-world-sandbox-remodel-prd.md`：后续改造 PRD，写清现有代码如何接入新方向。
- `docs/unfinale-product-vision-correction-draft.md`：产品愿景纠偏草稿，记录《天命书》、干预编译、世界代偿、主观记忆、世界自演、多视角活体小说和 UI 原型。
- `docs/unfinale-ai-development-alignment-checklist.md`：后续 AI 开发对齐检查清单，用于开工前确认这一刀是否服务世界沙盘主线。
- `docs/image/README.md`：UI 原型参考图索引。

---

## 2. 必读入口与事实优先级

新会话或新任务如果涉及 LNE、`engine/`、版本路线、产品 UI、API、测试或文档，先读：

1. `memory.md`：当前事实、边界、测试基线、已知缺口。
2. `docs/index.md`：文档地图，先判断某文档是当前主线、历史归档、支撑层索引还是后置发行路径。
3. `docs/unfinale-world-sandbox-remodel-prd.md`：当前改造 PRD，说明如何把现有代码拉回世界沙盘主线。
4. `docs/unfinale-ai-development-alignment-checklist.md`：后续 AI 开工前自检，避免继续沿旧工程化方向跑偏。
5. `docs/living-novel-engine-iteration-plan.md`：版本路线与官方下一步。
6. `engine/README.md`：CLI/API/输出结构/验收命令。
7. 需要愿景/产品定位时读 `docs/unfinale-product-vision-correction-draft.md` 与 `docs/living-novel-engine-prd.md`。
8. 需要 UI 风格时读 `docs/completed/v0.7-product-web-app-ui-spec.md`。
9. 存在接力任务时再读 `docs/codex-handoff.md`。

事实优先级：`memory.md` > `docs/index.md` > 世界沙盘 PRD > AI 对齐清单 > 主迭代计划 > `engine/README.md` > 主 PRD > 聊天摘要。

完整历史变更日志见 `docs/project-changelog.md`；它是追溯材料，不是当前待办来源。

---

## 3. 阶段收口总览

> 本节是历史阶段与支撑能力索引，供确认“某能力是否已做过”。判断当前下一刀时优先看第 1 节闭环等级和第 6 节真实未做项，不要从本节长表重新派生路线。

### 已收口主阶段

- v0.1-v0.6：CLI 原型、导入、检索、世界线浏览、multi-agent runner 与 trace 可靠性。
- v0.7：产品级 Web App 九刀、Agent Interaction、Visual Asset Generation、Baseline & Canon Replay、Worldline Judge。
- v0.8：长篇导入、分层记忆、正史账本、混合检索、审计、ActDirector、Narrator diagnostics、Dynamic Action Registry、Emergence Mining、Entity Alias、Runtime Memory Consumption、Artifact Panel、Long Upload Productization。
- v0.9.0-alpha：长篇创作闭环，覆盖章节导出、续写、世界线选择、审计入口、closeout API/CLI/record、alpha ready 和 closeout report。
- v0.9.1：Provider & Cost Gateway Lite。
- v0.9.2：MasterSetting Workspace Lite。
- v0.9.3：Graph Memory Evaluation Spike。
- v0.9.4：Advanced Runner Evaluation Spike。
- v1.0-beta：本地优先商业化边界，从 Scope-A 到 Billing Adapter Boundary-X 均已收口。
- v1.0-local：Model Configuration UX 与 Local Run Scripts 已收口。
- 后续增强四十五刀已压缩为支撑层能力组：运行前体检与投影健康、读者/作者质量诊断、Prompt Budget Pack、模型画像、设定卡片、本地 API contract、发行准备、检索失败样本采集/评估/导出/replay/migration、跨项目样本索引、检索趋势快照、GraphRAG/Zep/Temporal Memory 触发证据、shadow/case/provider 边界、离线 replay、manual opt-in 审批包、mock-compatible adapter 和 manual mock adapter review。完整逐刀细节只在 `docs/project-changelog.md` 与 `docs/后续增强清单.md` 追溯。
- Retrieval Provider Real Connectivity MVP 已按用户明确要求收口：百炼 `text-embedding-v3`、Zilliz Cloud、百炼 `gte-rerank-v2` 具备脱敏配置摘要、mock/real smoke 和设置页只读状态。
- Vector Retrieval Pipeline MVP 已按用户明确要求收口：API/UI 可显式构建 Zilliz 索引并做百炼 embedding + Zilliz + 百炼 rerank 检索预览；运行时仍需 `LNE_RETRIEVAL_STRATEGY=hybrid_vector` opt-in，默认 BM25 不被替换。

### 当前自主迭代点

- 产品纠偏已完成；当前自主迭代点是 **World Sandbox Loop / 世界沙盘改造**，不是继续扩 provider、Graph Memory、真实向量检索评测或工程化面板。
- 已完成的真实 embedding、Zilliz、reranker、Graph/provider 证据链、OpenAPI、发行和商业化边界全部保留为支撑层；除非用户明确点名，不作为下一刀默认方向。
- 后续如继续，优先沿 `docs/unfinale-world-sandbox-remodel-prd.md` 打磨 S1-S9 第一版闭环：真实 LLM 决策、章节草稿质量、作者可编辑确认、角色个人卷连续阅读和事件多视角证据链。

---

## 4. 当前产品与工程能力

> 本节记录当前系统能力面，包含大量已降级为支撑层的工程能力。产品主线仍是世界沙盘体验；若只判断下一步，可直接跳到第 6 节。

### 创作闭环

- 可导入 txt/md/zip/epub，服务端 ingest session 支持分片、hash 校验、缺失分片查询、重复 chunk 幂等与 localStorage 恢复续传。
- 长篇导入会写 `source_raw/`、`import_report.json`、`memory/`、`canon_ledger.jsonl`、`consistency_report.json`。
- 世界锚定页展示导入检查、设定工作台、章节预览、分层记忆、正史账本、实体别名、检索命中、审计报告和下一步入口。
- 干预 run 会生成分支产物，并可进入评审、审计、设为起点、生成下一章、章节/合集导出。

### 运行与状态执行

- `run_scene` 默认行为不变。
- 干预 run 可生成 `runner_state_execution_report.json` dry-run 评估。
- 显式确认后，low-risk/executable/白名单 delta 可写入分支 `state_execution_overlay.json`，并生成 apply/rollback 报告。
- `state_snapshot.json` 不被覆盖；overlay 暂不自动驱动下一轮 runner 消费。

### 记忆、检索与审计

- `canon_ledger` 已进入 BM25 检索 artifact，source 为 `canon_ledger`。
- 正史 holdout 写入 `canon/visibility_manifest.json`，区分 `runtime_visible` / `holdout_private`。
- 干预、baseline 与 CLI resume 通过既有 `retrieved_context` 参数只读消费 memory/alias/ledger 安全子集，并写 `runtime_memory_context.json`。
- 前端“机制档案”只读展示运行记忆、动作计划、动作注册表、叙事诊断、涌现节点。
- 本地审计日志已覆盖版权声明、设定编辑、世界线选择、状态执行 apply/rollback、项目保留策略等关键写操作。

### 设置、本地运行与商业化边界

- 设置抽屉已包含脱敏 provider 状态、usage 汇总、手动价格估算、route matrix、模型配置状态、任务模型画像、本地 API 契约、发行准备和视觉密钥清除。
- `scripts/start-local.ps1` 与 `scripts/start-local.sh` 支持 clone 后检查/安装依赖并启动后端与 Vite 前端。
- 产品入口边界已固定：用户不应被要求复制或理解 CLI 命令；导入、配置、创作、干预、评审、导出、样本采集和 Graph Memory 证据查看等用户级能力都应优先有前端入口并调用同一套 API/service。CLI 只作为开发者、本地服务启动、自动化验收、批处理、JSON 输出和无人值守复跑的薄封装，不承载独立业务规则。
- 支撑层 UI/API 已收口为几类只读或显式 opt-in 能力：运行前体检、投影健康、读者评审、上下文预算包、任务模型画像、接口契约、发行准备、设定卡片、检索样本采集/评估/导出/replay/migration、跨项目样本索引、Graph/长期记忆触发与 mock opt-in 证据包。坏 ID 和缺失项目按 400/404 降级，坏 JSON/缺 artifact 以需留意或需修复展示，不白屏。
- 真实向量检索已具备显式项目工作台入口和 API：可构建 Zilliz 索引，可用百炼 embedding + Zilliz + 百炼 rerank 做检索预览；默认创作检索不被替换，只有 `LNE_RETRIEVAL_STRATEGY=hybrid_vector` 时运行时消费，失败回退 BM25。
- 支撑层 CLI 已覆盖检索样本、mock/replay/migration、跨项目索引、趋势快照和 Graph/长期记忆 opt-in 证据包，定位为无人值守或批处理外壳；普通用户入口仍优先 Web UI + API。
- v1.0-beta 只做本地优先商业化边界和只读/本地写入 artifact；不接真实认证、云端对象存储、队列、计费、不可篡改审计或发布系统。

---

## 5. 关键硬约束

- 不改 `run_scene` 默认行为，除非用户明确要求进入 runner 重构。
- 不破坏既有 artifact 契约：`chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 新增 artifact、API 字段、前端读取字段默认 additive。
- 后端 HTTP-facing identifier 必须走安全校验，不能把未经校验的 slug/run_id/branch_id 拼到文件路径。
- 失败要降级为明确的 400/404/409 或前端空态，不白屏、不 500。
- 前端产品文案默认中文；不要出现英文占位词。
- 视觉风格保持 v0.7 的古风纸面、克制系统感，不做营销落地页。
- `Reference_projects/` 与外部项目只作参考，不直接复制源码或引入依赖，除非用户明确要求。
- 不泄漏 API Key；设置页或日志只能展示脱敏尾号。
- 用户在 `.env` 中可能已经配置真实 `SEEDREAM_API_KEY` / `LLM_API_KEY`。测试要隔离环境，避免误打真实外网。

---

## 6. 当前真实未做项（不要再把历史已完成项当缺口）

| 缺口 | 当前状态 | 下一步触发 |
| --- | --- | --- |
| 真实 LLM 多 Agent 策略仍需深化 | 已有显式 opt-in `llm_decision_mode=advisory`、`agent_decision_advisory.json`、`strategy_board` 和小样本真实 smoke；能看到采信、欺骗、传播、反抗和临场判断 | 需要多轮策略规划、长期关系/势力博弈、稳定误判/隐瞒/试探和更强世界影响时继续 |
| 长正文/连续阅读仍需打磨 | 已有 `continuous_reading_chapter` v2、`dossier-reading` API、卷宗阅读页、确认稿阅读链、正文证据锚点/阅读进度、误会图谱、长线阅读进度、误会回收台、长线卷跨章回收台、长线卷跨章误会网络图、本机最近阅读续航和世界自演可读入口；默认已像小说阅读而非 JSON 面板 | 需要账号级用户阅读进度持久化、长篇节奏、跨章节误会回收、跨章伏笔回收和真实文风一致性时继续 |
| Reviewer 整章风格润色仍未完成 | 已有语义 Reviewer、片段级问题、修改意图、建议改写、影响范围、作者勾选采纳、编辑后定稿和定稿自动确认入卷 | 需要从“应用局部建议成定稿”升级为“整章风格一致性润色、可回滚/对照和真实模型编辑器”时继续 |
| 世界线阅读入口仍可深化 | `readable_entry`、世界线页、检查点回放、角色个人卷独立页、势力卷独立页、事件多视角详情页、跨事件长线卷、多事件索引和事件/长线跳转已能串起醒来阅读 | 需要跨章角色/势力长线阅读、跨章节回收、跨卷证据联动和用户阅读进度持久化时继续 |
| ChapterBrief 质量仍偏薄 | 导入时可用，但 summary/facts 仍偏规则化，未接真实 LLM 摘要 | 长篇质量明显受限时再做 |
| `contract_audit` 主链路仍偏静态 | 已有多种审计与商业化边界，但运行时 contract 仍未作为主链路强约束 | 出现合约越界误判/漏判时再补 |
| overlay 未自动喂回 runner | 状态执行 overlay 可 apply/rollback，但下一轮 runner 暂不自动消费 overlay | 用户确认需要连续状态演化时再做 |
| 运行后审计未写入正史账本 | Projection Health 可只读说明账本/审计投影状态，但审计日志与 canon ledger 分工仍分离 | 需要“审计结论影响正史”时再做 |
| Reader Panel / Adversarial Revision Lab 深化 | deterministic/mockable 读者面板与修订 brief 已有 | 需要自动改写、Elo 对比、voice fingerprint 或真实 LLM 语义评审时再做 |
| Prompt Budget Pack 深化 | 已有轻量只读预算包、去重、优先级排序和 UI | 需要把预算包真正接入 opt-in prompt 编排或做 reranker 时再做 |
| LLM Profile Assignment 深化 | 已有只读任务画像、温度、预算和降级策略 | 需要 opt-in 保存 profile、版本化或真实模型实验时再做 |
| Cards Workspace 深化 | 已有只读世界卡、角色卡、风格卡入口，世界卡轻编辑复用 MasterSetting 白名单 | 需要独立卡片 artifact、版本化、差异审计或批量编辑时再做 |
| OpenAPI / Typed Client 深化 | 已有只读 API contract、OpenAPI skeleton 与前端 typed client 映射 | 需要字段级 schema、自动生成 client 或外部集成契约时再做 |
| Bundled Release / Desktop Packaging 深化 | 已有只读发行准备清单；安装包、内置 runtime、桌面壳、签名和自动升级仍未做 | 用户本地试用稳定后再做 opt-in packager spike |
| Retrieval Sample Export Pack / Mock Evaluation Report | 已有失败样本工作台、CLI 追加/复跑入口、只读 Markdown/manifest 导出包、mock 对照报告、replay case report 和 migration pack；跨项目样本索引仍未做 | 需要把真实失败 query 跨项目汇总时再做 |
| 云端多用户持久队列/对象存储/认证/计费 | v1.0-beta 已定义边界，但刻意不接真实云端系统 | 外部用户试用或部署路径明确后再做 |
| 生产默认检索替换 / GraphRAG / Zep | 已有 BM25、ledger、alias、probe、Prompt Budget Pack、向量检索就绪探针、mock 样本评估、跨项目趋势快照、GraphRAG/Zep 证据链；已新增百炼 embedding、Zilliz Cloud、百炼 reranker 的显式配置、真实 smoke、Zilliz 写索引、混合检索预览和 opt-in runtime 消费 | 先用真实失败样本评估收益；收益明确后再决定是否默认启用 hybrid vector、接 GraphRAG/Zep 或扩展生产运维能力 |
| 高级 runner 框架 | 已有触发式评估，不默认接 LangGraph/OASIS/CAMEL | probe 证明现有 runner 到瓶颈时再做 |

已完成但历史上曾列为缺口的能力：视觉资产、长篇分层记忆、正史账本、长篇混合检索、长篇一致性审计、抽象干预编译层、Worldline Judge、涌现节点、叙事诊断、动态动作注册表、百万字上传入口、无干预 baseline、正史回放等，均不应再作为当前未做项重复安排。

---

## 7. 主要产物索引

| 类型 | 产物 |
| --- | --- |
| 基础 run | `chapter.md`、`events.json`、`state_snapshot.json`、`meta.json` |
| 分支与干预 | `intervention.json`、`causal_diff.json`、`intervention_compilation.json`、`worldline_judgement.json` |
| 多 Agent | `multi_agent_trace.json`、`generation_meta`、trace quality validator |
| 长篇导入 | `source_raw/`、`import_report.json`、`memory/`、`canon_ledger.jsonl`、`consistency_report.json` |
| 运行记忆 | `runtime_memory_context.json`、`retrieval_context.json` |
| 高级机制 | `act_director_plan.json`、`narrative_diagnostics.json`、`dynamic_action_registry.yaml`、`emergence_nodes.json` |
| 状态执行 | `runner_state_execution_report.json`、`state_execution_overlay.json`、apply/rollback report |
| 创作闭环 | `selected_worldline.json`、`creation_loop_alpha_closeout.json`、章节/合集导出与 share guard |
| 商业化本地边界 | `project_audit_log.jsonl`、`project_copyright_statement.json`、`project_retention_policy.json` |

---

## 8. API / CLI 状态索引

### 已有 API 类型

- 项目与导入：story genesis、文件上传、ingest session、project workspace、world anchor。
- 干预与世界线：run/intervene、causal diff、worldline judgement、worldline selection。
- 回放与审计：baseline、canon replay、replay range、replay audit、post-run audit、audit log 与 export。
- 创作闭环：resume continue job、chapter export、collection export、creation loop closeout。
- 运行前体检：runtime preflight 聚合 import review、master setting、canon ledger、entity aliases、retrieval probe、selected worldline、overlay、copyright、retention、audit log、provider status。
- 向量检索就绪：vector retrieval readiness 聚合导入规模、检索语料、BM25 probe、失败样本、别名覆盖和候选层状态。
- Embedding 样本评估：embedding evaluation samples 读取本地失败样本，对比 BM25 与 mock semantic oracle，区分词面缺口和记忆缺口；失败样本可从项目工作台安全追加。
- 投影健康：projection health 聚合 branch/project 关键投影 artifact 的 ready/attention/blocked 状态。
- 读者评审：reader panel 聚合 deterministic 读者人格、修订问题和 revision brief。
- 上下文预算包：prompt budget pack 对 retrieval_context 做去重、预算分配和 prompt block 压缩。
- API 契约：api contract 显式返回本地 HTTP 契约、OpenAPI skeleton、端点分组和前端 typed client 映射。
- 发行准备：packaging readiness 检查本地脚本、package、前端 dist、发行文档和后置打包目标。
- 设置与 provider：providers、provider usage、manual price estimate、route matrix、model configuration。
- 商业化边界：commercial scope/status、permission matrix、quota/observability、deployment readiness、cloud persistence、account project space、auth/object storage/quota/billing boundary 等。

### 常用 CLI / 验收

CLI 定位为工程/自动化工具：可用于本地服务启动、测试门禁、批处理复跑、JSON 导出和开发者验收；用户级流程不以 CLI 作为主入口。若新增能力涉及普通用户理解或操作，先做 Web UI + API，再视需要补 CLI 薄封装。

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```

长篇闭环相关 CLI 以 `engine/README.md` 为准，例如 `lne creation-loop-closeout --write-report` 等。

检索失败样本 CLI：

```powershell
lne memory add-sample <slug> --query "..." --entity <entity_id> --reason "..." --chapter 2
lne memory samples <slug> --json --require-candidate
lne memory export-samples <slug> --json
lne memory mock-report <slug> --json --require-candidate
lne memory replay-report <slug> --json --require-clean
lne memory migration-pack <slug> --json
lne memory index-samples --json
```

---

## 9. 文档索引

| 文档 | 用途 |
| --- | --- |
| `AGENTS.md` | Agent 项目规则、硬约束、会话入口 |
| `memory.md` | 当前事实、边界、已知缺口、索引 |
| `docs/project-changelog.md` | 完整历史变更日志 |
| `docs/index.md` | docs 资料导航与推荐读取顺序 |
| `docs/codex-handoff.md` | 新 Codex 窗口接力包 |
| `docs/living-novel-engine-iteration-plan.md` | 主路线图 |
| `docs/productization-phase-map.md` | 阶段边界 |
| `docs/living-novel-engine-prd.md` | 主 PRD |
| `docs/distribution-phase-plan.md` | 后置发行路径 |
| `docs/completed/` | 已收口版本文档、PRD、Release Note、UI spec、工程协议 |
| `docs/article/` | 论文 PDF 与研读报告 |
| `docs/brand/`、`docs/image/` | 品牌资产与 UI 原型参考，不承担待办来源 |
| `engine/README.md`、`engine/ui/README.md` | 后端/API/artifact/验证与当前前端结构说明 |
| `Reference_projects/` | 参考开源项目，仅作设计参考 |

---

## 10. 参考项目与论文吸收边界

已吸收为路线语言的参考方向：

- Player-driven emergence：对应 `emergence_nodes`、分支差异、Worldline Judge。
- StoryVerse / Abstract Act / Act Director：对应 `AbstractIntervention`、compatibility、realization、`act_director_plan.json`。
- Human-Level Narratives / Story Arc / Turning Points：对应 `narrative_diagnostics.json` 与后续 narrator 反馈候选。
- STORY2GAME / Dynamic Action Generation：对应 `dynamic_action_registry.yaml` 与 alias/entity resolution。
- WenShape、webnovel-writer、MiroFish 等开源项目：只作架构与产品启发，不作为已引入依赖。

---

## 11. 决策备忘

- 本地优先：当前更重视单机可运行、可验证、可交付给用户试用，而不是过早云端平台化。
- 长篇路线：先用现有 BM25/ledger/alias/probe 与向量检索就绪探针把百万字底座跑通，再用失败样本和 mockable 对照评估决定是否接 vector/graph/rerank。
- Runner 路线：先保持 `SceneRunner` adapter 与当前 runner 安全边界，高级框架只在 probe 证明必要时引入。
- 商业化路线：v1.0-beta 只定义边界、审计口径和本地 artifact，不伪装成真实多租户 SaaS。
- 发行路线：本地脚本完成后暂停，等本地试用反馈，再决定 GitHub Release、内置 runtime 或服务器在线体验。

---

## 12. Agent 维护说明

- 先读当前章节，再读路线图；旧日志只用于追溯“为什么这么做”，不要把旧待办当当前事实。
- 做完有意义的开发/设计/验收任务后，同步三处：`memory.md` 当前状态、相关路线/README/PRD、`docs/project-changelog.md` 末尾历史记录。独立切片完成即记，不要把多刀合并成一次性补记。
- 不要改写历史变更日志；如历史条目过时，只在 `memory.md` 当前章节修正现状，必要时在新日志条目说明“状态已更新”。
- 若只做文档迁移，验证至少跑 `git diff --check`；若改代码，再按风险跑 pytest / UI build / HTTP smoke。

---

## 13. 历史变更日志索引

完整历史变更日志已迁移到 `docs/project-changelog.md`。本入口文档不再承载完整日志，只保留当前事实、路线、边界和索引，避免新会话启动时被历史过程拖慢。
