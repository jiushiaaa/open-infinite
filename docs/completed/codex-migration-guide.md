# Codex 迁移说明

> 用途：记录 `.cursor/rules`、`.cursor/skills` 与 Codex skills/plugins 的迁移关系。迁移已完成，本文留作归档，不承担当前待办来源。

## 1. 当前结论

- 项目级规则以根目录 `../../AGENTS.md` 为准。
- 当前事实以 `../../memory.md` 为准。
- 文档分层以 `../index.md` 为准。
- 接力摘要以 `../codex-handoff.md` 为准。
- 完整历史写入 `../history/project-changelog.md`。

`.cursor/rules/project-memory.mdc` 的核心项目规则已经迁入 `../../AGENTS.md` 和 `../codex-handoff.md`。`.cursor/skills/` 多数是通用 Claude/Cursor 技能包；在 Codex 中优先使用当前会话已安装的 Codex skills/plugins。

## 2. 使用方式

只有在需要追溯旧 Cursor 工作流时才读本文。新任务不要整包复制 `.cursor/skills/`，而是按当前 Codex skills/plugins 的触发规则选择最小适用技能。

## 3. 维护口径

如果未来再次迁移工具：

1. 先确认当前规则是否已经写在 `../../AGENTS.md`。
2. 只迁移项目特有约束，不迁移通用提示词噪音。
3. 完成后同步 `../../memory.md`、`../index.md`、`../codex-handoff.md`，并追加 `../history/project-changelog.md`。
