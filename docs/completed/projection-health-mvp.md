# Projection Health MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第二刀，只读产品化切片。  
> 范围：生成后分支投影健康聚合，不替换 canon ledger、不覆盖 state snapshot、不写 artifact。

## 1. 目标

Projection Health MVP 用于长篇分支生成后，快速回答“这条分支的正文、事件、状态、账本和审计投影是否可被信任”。它只读已有本地 artifact，先把成功、缺失、损坏说清楚，为后续真正 opt-in Chapter Commit 铺路。

## 2. 已完成

- 新增 service：`living_novel_engine.service.get_projection_health(run_id, branch_id)`。
- 新增 API：`GET /api/runs/<run_id>/branches/<branch_id>/projection-health`。
- 新增前端入口：分支右栏「投影健康」tab。
- 聚合检查项：
  - 章节正文 `chapter.md`
  - 事件投影 `events.json`
  - 状态投影 `state_snapshot.json`
  - 因果差异 `causal_diff.json`
  - 多 Agent 轨迹 `multi_agent_trace.json`
  - 运行时记忆消费 `runtime_memory_context.json`
  - 叙事诊断 `narrative_diagnostics.json`
  - 世界线评估 `worldline_judgement.json`
  - 正史账本 `memory/canon_ledger.jsonl`
  - 项目审计日志 `memory/project_audit_log.jsonl`

## 3. API 契约

返回核心字段：

```json
{
  "version": "projection-health-mvp",
  "mode": "read_only_projection_health",
  "status": "ready | attention | blocked",
  "summary": {
    "check_count": 10,
    "ready_count": 0,
    "attention_count": 0,
    "blocked_count": 0,
    "writes_artifacts": false,
    "mutates_state_snapshot": false,
    "replaces_canon_ledger": false,
    "external_services_required": false
  },
  "checks": []
}
```

错误边界：

- 坏 `run_id` / `branch_id` 返回 400。
- 缺 run 或 branch 返回 404。
- 坏 JSON/JSONL 或缺 artifact 不抛 500，降级为 `attention` 或 `blocked` check。

## 4. 安全边界

- 不写任何 artifact。
- 不替换 `memory/canon_ledger.jsonl`。
- 不覆盖 `state_snapshot.json`。
- 不调用真实 LLM、Seedream、embedding、向量库、GraphRAG、Zep 或 reranker。
- 不改变 `run_scene` 默认行为。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_projection_health.py -q
python -m pytest engine\tests\test_browser_server.py engine\tests\test_projection_health.py engine\tests\test_v075_worldline_judge.py engine\tests\test_v090_long_creation_loop.py -q
cd engine\ui
pnpm run build
cd ..
python -m pytest -q
cd ..
git diff --check
```

## 6. 后续状态

`Reader Panel / Adversarial Revision Lab MVP` 已作为后续增强第三刀收口，见 `reader-panel-revision-lab-mvp.md`；`Prompt Budget Pack MVP` 已作为第四刀收口，见 `prompt-budget-pack-mvp.md`。下一刀建议进入 `LLM Profile Assignment MVP`。
