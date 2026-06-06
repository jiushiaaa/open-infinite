# 未终章 · 前端工作台

> 当前口径：本前端已经不只是 v0.7 只读阅读器。它是本地产品入口，承载世界书架、世界锚定、天命书、世界沙盘、世界线/检查点、卷宗阅读、作者采纳台、设置和支撑层机制档案。最新事实以 `../../memory.md`、`../../docs/index.md` 和 `../README.md` 为准。

## 定位

- 前端是普通用户入口；API 是能力层；CLI 是开发者和自动化外壳。
- 当前默认主线是 World Sandbox Loop / 世界沙盘体验深化，不是继续堆 provider、Graph、检索评测、OpenAPI、发行或商业化面板。
- UI 风格沿用古风纸面、克制系统感；新增用户可见文案默认中文。
- 世界入口第一轮已经把故事书架、天命书、世界沙盘、卷宗阅读、世界线、多视角和作者台串成世界内卷宗导航；首屏 QA 已覆盖浏览器标题、无天命书空态和真实 390px 移动端入口换行；移动端顶栏已把世界内部导航改为可换行卷宗盘，锚定、天命书、沙盘、阅读、世界线、多视角、作者台和机制档案全部直接可见；世界内导览层 `WorldRunway` 已在世界沙盘、卷宗阅读、世界线档案、检查点回放和作者采纳台中统一“当前位置 -> 理解路径 -> 下一步行动”；世界锚定页已把天命书、沙盘和卷宗阅读前置为“世界启动”行动卡，移动端不再隐藏锚定侧栏或角色栏；`WorkspacePage.tsx` 现在按“世界正史与机制档案”理解，用于收纳旧正史、机制解释和支撑层入口。
- 后续不要继续把新功能塞进 `WorkspacePage.tsx`。世界沙盘能力优先拆到世界内部卷宗、结果页和具体场景页。

## 运行

需要先启动引擎后端（提供 `/api/*`）：

```bash
# 在 engine/ 下
lne browse
```

再启动前端开发服务器：

```bash
# 在 engine/ui/ 下
pnpm install
pnpm run dev
```

默认开发地址是 `http://localhost:5173`，`/api` 会代理到 `http://127.0.0.1:8765`。代理目标可用 `LNE_API_TARGET` 覆盖；构建时可用 `VITE_API_BASE` 指定后端绝对地址。

## 校验

```bash
pnpm run typecheck
pnpm run build
```

文档-only 任务通常不需要跑前端 build；改 TS/TSX、路由、类型或样式时必须至少跑 `pnpm run build`。

## 当前主要页面

| 页面/组件 | 当前职责 |
| --- | --- |
| `StoryEntryPage` | 世界书架入口，展示“确认天命 -> 运行沙盘 -> 阅读卷宗 -> 采纳续写”的主旅程，并进入已有故事或新建/导入流程 |
| `GenesisPage` | 主题创世 |
| `ImportNovelPage` | 导入长篇文本 |
| `WorldAnchorPage` | 世界锚定、设定确认、视觉/审计/角色校准和“世界启动”行动卡；移动端保留左栏与角色栏功能 |
| `WorldSandboxPage` | 世界沙盘、运行导览、干预投放、真实 LLM 决策 advisory、世界自演结果和阅读出口 |
| `WorldlineDossierPage` | 世界线档案，展示世界线状态、自演任务、检查点与可读入口 |
| `CheckpointReplayPage` | 检查点回放，解释状态变化、记忆变化和因果债 |
| `DossierReadingPage` | 世界内部卷宗阅读页，默认连续阅读，可切换世界正史卷、主锚点卷、角色个人卷、事件多视角和确认正文 |
| `AuthorAdoptionPage` | 作者采纳台，覆盖采纳/部分采纳/另开分支、下一章 brief、草稿、连续阅读、Reviewer 局部重写、编辑后定稿和确认入卷 |
| `WorldRunway` | 世界内导览组件，用同一套纸面导览说明当前世界线、三步理解路径和下一步行动，已接入世界沙盘、卷宗阅读、世界线、检查点和作者采纳台 |
| `SettingsDrawer` | 本地模型配置、provider 脱敏状态、任务模型画像、发行准备等设置/支撑层能力 |
| `WorkspacePage` | 世界正史与机制档案，保留旧正史、世界线树、机制档案和支撑层入口，不再作为默认主体验 |

## 当前路由心智

路由以 `hash` 为主，关键世界沙盘入口包括：

- `#/`：世界书架入口。
- `#/world/<slug>`：世界锚定/世界入口。
- `#/world/<slug>/tianming`：天命书，当前故事卡默认进入的第一站。
- `#/world/<slug>/sandbox`：世界沙盘。
- `#/world/<slug>/worldlines/<worldline_id>`：世界线档案。
- `#/world/<slug>/worldlines/<worldline_id>/reading`：卷宗阅读，默认连续阅读。
- `#/world/<slug>/worldlines/<worldline_id>/reading/<tab>`：精准落到某个卷宗 tab，例如 `character_volume` 或 `event_multi_perspective`。
- `#/world/<slug>/worldlines/<worldline_id>/checkpoints/<run_id>/<checkpoint_id>`：检查点回放。
- `#/world/<slug>/author-adoption/<adoption_run_id>`：作者采纳台。

## 结构

```text
src/
  api/            client.ts / types.ts，封装 HTTP API 与前端契约类型
  components/     页面、卷宗、沙盘、作者台、设置和机制档案组件
  styles/         theme.css / global.css，古风纸面设计令牌
  routing.ts      hash 路由解析与构建
  markdown.tsx    小说正文 Markdown 渲染
  motion.ts       强反馈动效降级开关
```

## 当前边界

- 不把 Graph/provider/检索评测/发行/商业化支撑层做成新的默认主体验。
- 不打印或回显明文 API key；设置与日志只展示脱敏状态。
- 不假装旧 workspace 面板就是最终产品结构；它现在只是机制档案入口，后续读者体验优先世界内部卷宗。
- `DossierReadingPage`、世界自演可读入口和作者采纳台已完成第一版，但仍需正文内证据锚点、误会图谱、长正文文风和更强真实语义 Reviewer。
