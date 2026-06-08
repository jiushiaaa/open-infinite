# LNE 支撑层与后置增强索引

> 用途：说明哪些能力已经作为支撑层收口、哪些只在明确触发时继续。本文不是当前默认路线；当前路线请读 `../../memory.md`、`../index.md`、`../unfinale-world-sandbox-remodel-prd.md` 和 `../unfinale-current-optimization-backlog.md`。

## 1. 当前边界

当前默认主线是 **World Sandbox Loop / 小说世界沙盘体验深化**。支撑层只有在能直接强化世界运行、角色自主、角色记忆、干预后果、世界代偿或章节生成时才进入。

## 2. 已收口支撑层

| 分类 | 当前状态 |
| --- | --- |
| 本地运行 | v1.0-local 设置页、一键启动脚本、运行前体检和本地复用路径已收口 |
| Provider | 真实 embedding/reranker/vector provider、opt-in Vector Retrieval Pipeline 和相关 smoke 已收口为支撑层 |
| Graph/长期记忆 | Graph Memory Provider Spike、mock adapter、人工复核 packet 已收口，默认暂停 |
| CLI/API 支撑 | 开发者验证、批处理、JSON 输出和无人值守复跑能力保留为工程外壳 |

## 3. 触发式后续

只有出现明确样本证据或用户点名时，才继续：

- GraphRAG / Zep / Temporal Memory 重型 provider。
- 默认 hybrid vector 替换 BM25。
- provider cost/route matrix 扩张。
- OpenAPI / typed client 面板深化。
- LangGraph / OASIS / CAMEL 替换现有 runner。
- 云端多用户、对象存储、认证、计费、安装包和在线体验。

## 4. 追溯入口

| 入口 | 用途 |
| --- | --- |
| `../history/project-changelog.md` | 完整历史变更日志 |
| `README.md` | completed 目录索引 |
| `productization-phase-map.md` | 阶段边界历史说明 |
| `../postponed/distribution-phase-plan.md` | 后置发行路径 |
| `../../memory.md` | 当前事实和主线边界 |

如果本文与 `../../memory.md` 冲突，以 `../../memory.md` 为准。
