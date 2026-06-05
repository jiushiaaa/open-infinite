# 未终章 UI 原型参考图

本目录存放当前纠偏讨论阶段生成的 UI 方向参考图。它们不是最终视觉稿，也不是要求立即全量重写前端，而是用于固定“未终章后续产品入口应该长什么样”的参考材料。当前实现已经从“主工作台堆面板”转向“世界内部卷宗、世界线结果页和作者采纳台”；使用这些图时取信息架构，不要把旧 Workspace 布局当默认方向。

整体方向：

- 古风纸面、克制系统感，不做营销页，不做赛博控制台。
- UI 的重点是让用户看见世界运行、角色行动、主观记忆、世界线代偿和章节生成。
- 工程诊断、provider、GraphRAG/Zep、OpenAPI 等内容继续作为支撑层，不占据主体验。

## 原型清单

| 序号 | 文件 | 用途 |
| --- | --- | --- |
| 01 | [unfinale-ui-01-main-workspace-overview.png](./unfinale-ui-01-main-workspace-overview.png) | 早期世界体验总览：世界自演报告、角色镜头、读者干预和检查点入口；实现时优先拆到世界内部卷宗与结果页。 |
| 02 | [unfinale-ui-02-import-tianming-confirmation-a.png](./unfinale-ui-02-import-tianming-confirmation-a.png) | 导入与《天命书》确认 A：偏文件导入、AI 泛读进度和初始化确认。 |
| 03 | [unfinale-ui-03-import-tianming-confirmation-b.png](./unfinale-ui-03-import-tianming-confirmation-b.png) | 导入与《天命书》确认 B：偏结构化预抽结果、候选天命承载者和微调入口。 |
| 04 | [unfinale-ui-04-world-autopilot-control.png](./unfinale-ui-04-world-autopilot-control.png) | 世界自演控制：设置运行到轮次、事件、时间或锚点变化。 |
| 05 | [unfinale-ui-05-autopilot-evolution-report.png](./unfinale-ui-05-autopilot-evolution-report.png) | 昨夜世界演化报告：自动运行后的关键事件、世界状态、记忆变化和检查点。 |
| 06 | [unfinale-ui-06-intervention-compiler.png](./unfinale-ui-06-intervention-compiler.png) | 干预编译器：自由输入、兼容性审计、本土化转译、分支轴和 AU 选择。 |
| 07 | [unfinale-ui-07-character-lens-novel.png](./unfinale-ui-07-character-lens-novel.png) | 多视角活体小说：世界正史卷、主锚点卷、角色个人卷和事件关联。 |
| 08 | [unfinale-ui-08-worldline-anchor-compensation.png](./unfinale-ui-08-worldline-anchor-compensation.png) | 世界线与锚点代偿：叙事吸引子、当前锚点、候选天命承载者和代偿证据。 |
| 09 | [unfinale-ui-09-author-adoption-desk.png](./unfinale-ui-09-author-adoption-desk.png) | 作者采纳台：原大纲与沙盘涌现剧情对照，采纳、部分采纳、另开分支和导出。 |
| 10 | [unfinale-ui-10-event-perspective-memory-inspector.png](./unfinale-ui-10-event-perspective-memory-inspector.png) | 事件多视角：客观事件、角色主观记忆、误会图谱、记忆写入和后续用途。 |

## 推荐使用方式

- 讨论产品方向时，优先引用本目录图片。
- 后续实现 UI 时，先从信息架构和交互职责取舍，不要机械照抄画面细节。
- 若进入前端实现阶段，仍需回到 `docs/completed/v0.7-product-web-app-ui-spec.md` 的风格边界和现有 `engine/ui` 代码结构。
