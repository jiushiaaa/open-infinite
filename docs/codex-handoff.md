# Codex Handoff — 未终章

> 用途：新开 Codex 窗口时的最小接力包。当前事实以 `../memory.md` 为准；完整历史变更见 `project-changelog.md`；旧版长接力稿已归档到 `completed/codex-handoff-legacy-2026-06-01.md`。

## 新窗口第一条消息建议

```text
请先阅读并对齐：
- AGENTS.md
- memory.md
- docs/index.md
- docs/codex-handoff.md
- docs/living-novel-engine-iteration-plan.md
- docs/productization-phase-map.md
- docs/living-novel-engine-prd.md
- docs/completed/v0.7-product-web-app-ui-spec.md
- engine/README.md

当前项目是 未终章（Unfinale），核心代码在 engine/；技术缩写、包名、CLI 和环境变量前缀仍沿用 LNE / `living_novel_engine`。
请不要只靠这段摘要；读完文档和相关代码后，再继续下一步。
```

如需追溯完整历史变更日志，再读 `docs/project-changelog.md`。日常接力优先以 `memory.md` 当前事实为准。

## 当前项目状态

未终章 是 `D:\AI\open-infinite\engine` 下的故事世界运行时。核心闭环：

```text
文本输入 -> 世界锚定 -> 角色自主行动 -> 读者干预 -> 世界线分叉 -> 章节渲染 -> 可继续运行
```

截至 2026-06-01：

| 阶段 | 状态 |
| --- | --- |
| v0.7-v0.7.5 | 短中篇产品化 Web App 与交互增强已收口 |
| v0.8-v0.8.10 | 长篇导入、分层记忆、账本、审计、项目工作台、状态 overlay 已收口 |
| v0.9.0-alpha | 长篇共创闭环已整体收口：上传/创建 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出 -> closeout record |
| v0.9.1-v0.9.4 | Provider/Cost、MasterSetting、Graph Memory Evaluation、Advanced Runner Evaluation 均已收口 |
| v1.0-beta | 本地优先商业化边界从 Scope-A 到 Billing Adapter Boundary-X 均已收口 |
| v1.0-local | Model Configuration UX 与 Local Run Scripts 已收口 |

验证基线：后端 `cd engine && python -m pytest -q` 为 `713 passed`；前端 `cd engine/ui && pnpm run build` 通过。

## 当前暂停点

按用户要求，真实用户模型配置 UI 与本地一键运行脚本完成后暂停，不继续自动开新刀。下一次继续前先等用户本地试用反馈。

可选后续方向只有在用户确认后再进入：

- GitHub Release 安装包 / 内置 runtime。
- 腾讯云或服务器单机在线体验。
- 真实认证、对象存储、云端队列、配额执行或计费系统。

当前不默认接 Zep / 图数据库 / GraphRAG / LangGraph / OASIS / CAMEL；这些保持 v0.9.3 / v0.9.4 的触发式评估边界。

## 开发硬约束

- 不改 `run_scene` 默认行为，除非用户明确要求进入 runner 重构。
- 不破坏既有 artifact 契约：`chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
- 新 artifact、API 字段、前端读取字段默认 additive。
- 后端 HTTP-facing identifier 必须安全校验；非法输入返回明确 400/404/409 或前端空态。
- 前端产品文案默认中文，不出现英文占位词。
- 不泄漏 API Key；设置页和日志只能展示脱敏尾号。
- 测试要隔离环境，避免误打真实 LLM/Seedream 外网。

## 当前真实未做项

- ChapterBrief 摘要质量仍偏规则化，未接真实 LLM 摘要。
- `contract_audit` 主链路仍偏静态，未成为运行时强约束。
- `state_execution_overlay.json` 不自动喂回下一轮 runner。
- 运行后审计未写入正史账本。
- 云端多用户持久队列、真实对象存储 adapter、真实认证、真实计费仍未做。
- 向量库 / embedding / GraphRAG 只在 BM25/ledger/alias probe 证明不足时再评估。

## 文档同步规则

完成有意义的开发、设计或验收任务后：

1. 更新 `memory.md` 当前状态和真实未做项。
2. 如需记录历史过程，追加 `docs/project-changelog.md`。
3. 若路线、PRD、README、UI spec 或本接力包发生事实变化，同步对应文档。
4. 至少运行 `git diff --check`；改代码时按风险运行 pytest、前端 build 或 HTTP smoke。

## 常用验证

```powershell
cd D:\AI\open-infinite\engine
python -m pytest -q

cd D:\AI\open-infinite\engine\ui
pnpm run build

cd D:\AI\open-infinite
git diff --check
```
