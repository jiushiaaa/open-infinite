# 未终章 · v0.7 Product Web App（前端骨架）

古风纸面阅读工作台。第一刀打通**只读链路**：故事入口 → 阅读工作台 → 选择 run/branch
→ 展示 chapter / state / retrieval / agent trace / intervention_compilation / causal_diff。

- 不重写 engine 核心推演逻辑。
- 不替换 `lne browse`：前端复用其只读 HTTP 端点（additive）。
- `branch_a/b/c` 只是目录 ID，用户看到的是 `intervention_compilation.branch_axis` 的动态 label。
- Causal Diff 是第一版核心展示。

## 运行

需要先启动引擎后端（提供 `/api/*`）：

```bash
# 在 engine/ 下
lne browse            # 默认 127.0.0.1:8765
```

再启动前端开发服务器：

```bash
# 在 engine/ui/ 下
pnpm install
pnpm run dev          # http://localhost:5173 ，/api 自动代理到 8765
```

代理目标可用环境变量覆盖：`LNE_API_TARGET=http://127.0.0.1:8765`。
若前端独立部署到其它域，构建时用 `VITE_API_BASE` 指定后端绝对地址。

## 校验

```bash
pnpm run typecheck    # tsc -b --noEmit
pnpm run build        # tsc -b && vite build
```

## 结构

```
src/
  api/            client.ts / types.ts —— 只读端点封装与契约类型
  components/     AppShell / StoryEntryPage / WorkspacePage
                  WorldlineTree / ChapterReader / CausalDiffBlock
                  RightPanel + CompilationPanel / CharacterStatePanel
                  / RetrievalPanel / AgentTracePanel / InterventionComposer
  styles/         theme.css（古风纸面设计令牌） / global.css
  branchLabels.ts 目录 ID → 动态分支 label 映射
  markdown.tsx    极简小说正文渲染
  routing.ts      hash 路由（entry / workspace）
  motion.ts       强反馈动效降级开关
```

## 边界（第一刀不做）

- 自由干预的实际生成（`POST /api/interventions`）留待下一刀；输入抽屉与按钮先占位。
- accept / reject / revert 命令未接后端，Diff 操作按钮 disabled 显示「即将支持」。
- Seedream 视觉资产、世界锚定页完整实现留待后续；数据/路由已留位。
