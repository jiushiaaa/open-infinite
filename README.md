# 未终章

> 一个会自己生长、能被读者干预、角色可能反抗命运的 AI 小说世界。

未终章（Unfinale）是 `open-infinite` 的本地产品原型：它不把小说当作一次性续写文本，而是把故事拆成可运行的世界状态、角色主观记忆、干预变量、世界线代偿和章节渲染。用户进入的不是“下一段生成器”，而是一部正在活着的小说。

当前核心代码在 [`engine/`](./engine)。技术缩写、Python 包、CLI 和环境变量前缀仍沿用 LNE / `living_novel_engine`。

## 当前状态

World Sandbox Loop / 世界沙盘改造 S1-S9 已形成第一版可运行链路：

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

已经完成第一版的产品入口包括：世界书架、世界锚定房间、天命书、世界沙盘、世界正史卷、主锚点卷、角色个人卷、势力卷、事件多视角、跨事件长线卷、世界线、检查点回放、卷宗阅读和作者采纳台。最近状态、验证基线和真实未做项以 [`memory.md`](./memory.md) 为准。

Graph/provider/真实向量检索/OpenAPI/发行/商业化已降为支撑层；除非用户明确要求，不作为默认下一步。

## 快速开始

推荐从仓库根目录启动本地产品工作台：

```powershell
cd D:\AI\open-infinite
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start-local.ps1
```

脚本会检查 Python、Node.js、pnpm，准备后端环境，启动本地 HTTP API 与 Vite 前端，并打开产品工作台。

只检查环境、不启动服务：

```powershell
cd D:\AI\open-infinite
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start-local.ps1 -CheckOnly -NoBrowser
```

macOS / Linux：

```bash
cd /path/to/open-infinite
bash scripts/start-local.sh
bash scripts/start-local.sh --check-only --no-browser
```

普通用户入口是前端产品工作台；CLI 只作为本地服务启动、开发者验收、批处理复跑和 JSON 导出的工程工具。

## 文档入口

| 文档 | 用途 |
| --- | --- |
| [`AGENTS.md`](./AGENTS.md) | Agent 执行规则、硬约束和会话必读清单 |
| [`memory.md`](./memory.md) | 当前事实、闭环等级、验证基线、真实未做项 |
| [`docs/index.md`](./docs/index.md) | `docs/` 分类地图，说明哪些是当前主线、历史归档、支撑层或后置路径 |
| [`docs/unfinale-world-sandbox-remodel-prd.md`](./docs/unfinale-world-sandbox-remodel-prd.md) | 当前世界沙盘主线 PRD |
| [`docs/unfinale-ai-development-alignment-checklist.md`](./docs/unfinale-ai-development-alignment-checklist.md) | 后续 AI 开工前自检 |
| [`docs/living-novel-engine-iteration-plan.md`](./docs/living-novel-engine-iteration-plan.md) | 当前路线和下一刀候选 |
| [`docs/unfinale-current-optimization-backlog.md`](./docs/unfinale-current-optimization-backlog.md) | 已有第一版但还要继续深化的主线优化项 |
| [`engine/README.md`](./engine/README.md) | 后端运行、API、artifact 和验证命令 |
| [`engine/ui/README.md`](./engine/ui/README.md) | 前端结构、路由和 UI 边界 |

完整历史见 [`docs/history/project-changelog.md`](./docs/history/project-changelog.md)，已收口专项见 [`docs/completed/`](./docs/completed/)，后置路径见 [`docs/postponed/`](./docs/postponed/)。不要从旧 changelog、`completed/` 或 `postponed/` 文档里直接派生当前待办。

## 产品结构

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

“沙盘 / 阅读 / 干预 / 作者”是同一个世界里的场景能力，不是一级工作区。前端是产品入口，API 是能力层，CLI 是工程外壳。

## 核心体验

未终章想解决的问题不是“把一段文字续写下去”，而是：

```text
创作者设定世界规则
  -> 角色自主行动
  -> 读者观察或干预
  -> 世界继续演化
  -> 系统生成可读章节
```

关键体验包括：

- **续写断更小说**：导入已有文本后，让角色和世界状态从断点继续运行。
- **拯救意难平**：读者投放变量，世界吸收、抵抗、代偿或分叉，而不是简单服从。
- **平行世界线探索**：同一本小说可以长出多条世界线，每条都有自己的状态、记忆和章节历史。
- **作者大纲压力测试**：作者把设定和大纲交给沙盘，让角色自主推演，观察剧情是否成立。

## 设计原则

- 世界状态、角色主观记忆和天命书是主真源；章节是观察窗口。
- 干预必须被世界理解，不是被模型无条件服从。
- 角色应该有私有目标、记忆、误判、利益和边界。
- 世界代偿要进入后续状态，不能只停留在摘要。
- Reviewer 是小说编辑，不是单纯规则清单。
- 用户级能力优先 Web UI + API，CLI 不承载独立业务规则。

## 版权与伦理边界

本项目优先支持原创文本、公版文本和用户拥有权利的文本。对受版权保护的商业小说，默认定位为本地个人探索，不鼓励公开分发生成内容，不声称生成内容代表原作者意图，也不冒充原作者继续连载。

文档中引用具体作品时只抽象机制，不复刻专有设定与表达。

## License

TBD.
