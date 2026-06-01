# Cursor to Codex Migration Guide

> 用途：说明本仓库 `.cursor/rules`、`.cursor/skills` 和插件类能力如何迁移到 Codex 工作流。不要把 Cursor 资产整包复制到 Codex 上下文；按需要迁移核心规则和少量项目专属工作流。

## 已迁移内容

### `.cursor/rules/project-memory.mdc`

核心内容已迁移到：

- `AGENTS.md`：项目级硬规则、会话开始必读、开发约束、验证命令
- `docs/codex-handoff.md`：新窗口接力包、当前版本状态、暂停点和开发约束
- `memory.md`：当前项目事实、路线、边界和入口索引
- `docs/project-changelog.md`：从 `memory.md` 迁出的完整历史变更日志

Cursor rule 的要点：

- LNE 相关任务开始时必须读四文档，不只读 `memory.md`
- 文档事实优先级明确
- 任务完成后同步 `memory.md` 当前状态；如需追加历史记录，写入 `docs/project-changelog.md`
- 版本路线和测试基线要以项目文档为准

Codex 侧等价做法：

1. 新窗口先读 `AGENTS.md` 和 `docs/codex-handoff.md`
2. 再读 `memory.md`、迭代计划、PRD、UI spec、README
3. 实现后跑测试，更新 `memory.md` 当前状态；如需追加历史记录，更新 `docs/project-changelog.md`

## Cursor skills 迁移策略

`.cursor/skills/` 当前包含大量通用技能，例如：

- `frontend-design`
- `webapp-testing`
- `doc-coauthoring`
- `docx` / `pptx` / `xlsx` / `pdf`
- `claude-api`
- `mcp-builder`
- `skill-creator`
- `web-artifacts-builder`
- `canvas-design`
- `theme-factory`

这些大多不是 LNE 项目专属知识。Codex 中优先使用已安装插件/skills 的等价能力：

| Cursor skill | Codex 等价能力 | 迁移建议 |
| --- | --- | --- |
| `frontend-design` | Build Web Apps / Vercel frontend skills | 不迁移整包；按本项目 UI spec 执行 |
| `webapp-testing` | Vercel browser/testing skills + 本地 Playwright/浏览器验证 | 只在需要端到端 UI 验证时使用 |
| `doc-coauthoring` | Documents / 普通 Markdown 编辑 | 不迁移；本项目以 Markdown docs 为主 |
| `docx` / `pptx` / `xlsx` / `pdf` | Codex Documents / Presentations / Spreadsheets plugins | 不迁移；需要时调用对应插件 |
| `claude-api` | OpenAI Developers 或项目自己的 LLM client | 不迁移；LNE 当前是 OpenAI-compatible 配置 |
| `mcp-builder` | Codex plugin/MCP 能力 | 暂不迁移，LNE 当前不做 MCP server |
| `skill-creator` | Codex skill-creator | 只有创建项目专属 skill 时再用 |
| `web-artifacts-builder` | Build Web Apps | 不迁移 |
| `canvas-design` / `theme-factory` | imagegen / design skills | 不迁移；LNE UI 已有风格约束 |

## 什么时候需要新建 Codex skill

只有当一个工作流会被频繁复用，并且不是普通项目文档能承载时，才值得做 Codex skill。例如：

- LNE release audit workflow：固定读取 docs、跑测试、查 artifact 契约、更新 memory
- LNE worldline artifact inspection：固定检查 `compare.md`、`events.json`、`state_snapshot.json`、`chapter.md`
- LNE UI visual regression workflow：固定启动 browse/ui、截图、检查中文文案和空态

当前阶段不必急着创建 skill；`AGENTS.md` + `docs/codex-handoff.md` 已足够让新窗口恢复上下文。

## 插件对应关系

当前 Codex 环境可用插件与 LNE 的关系：

- **Superpowers**：适合大版本开发、TDD、系统化调试、代码审查。
- **Build Web Apps / Vercel**：适合 React/Vite UI 开发、前端测试和浏览器验证。
- **OpenAI Developers**：适合 OpenAI API / Agents SDK / API Key 相关任务；LNE 当前主要使用 OpenAI-compatible LLM client。
- **Documents / Presentations / Spreadsheets**：仅当用户要求对应文件格式时使用。
- **Figma**：仅当用户明确要设计稿、Figma 生成或同步时使用。

迁移原则：

- 项目规则放 `AGENTS.md`
- 当前事实和路线边界放 `memory.md`
- 完整历史变更日志放 `docs/project-changelog.md`
- 新窗口接力放 `docs/codex-handoff.md`
- 通用技能不复制
- 项目专属重复流程再考虑 Codex skill

## 新窗口最小接力流程

1. 打开 `D:\AI\open-infinite`
2. 发送 `docs/codex-handoff.md` 中的第一条消息建议
3. 等 Codex 读完文档和代码后，再让它执行 v0.7.5
4. 每完成一刀，要求它更新 `memory.md` 当前状态、必要时追加 `docs/project-changelog.md`，并给出验证结果
