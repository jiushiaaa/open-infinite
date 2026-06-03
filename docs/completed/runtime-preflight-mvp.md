# Runtime Preflight MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第一刀，只读产品化切片。  
> 范围：创作前运行时健康聚合，不改 runner、不写 artifact、不调用外部服务。

## 1. 目标

Runtime Preflight MVP 用于长篇续写或读者干预前，快速回答“当前项目能不能安全继续跑”。它聚合已有本地证据，而不是创建新的状态真源。

## 2. 已完成

- 新增 service：`living_novel_engine.service.get_runtime_preflight(story_slug)`。
- 新增 API：`GET /api/stories/<slug>/runtime-preflight`。
- 新增前端入口：项目工作台「运行前体检」面板。
- 聚合检查项：
  - 导入检查 `import_report.json`
  - MasterSetting `memory/master_setting.yaml`
  - 正史账本 `memory/canon_ledger.jsonl`
  - 实体别名 `memory/entity_aliases.yaml`
  - 检索探针 `evaluate_retrieval_probes`
  - 续写起点 `selected_worldline.json`
  - 状态覆盖 `state_execution_overlay.json`
  - 版权/来源声明
  - 项目保留策略
  - 项目审计日志
  - provider 路由状态

## 3. API 契约

返回核心字段：

```json
{
  "version": "runtime-preflight-mvp",
  "mode": "read_only_runtime_preflight",
  "status": "ready | attention | blocked",
  "summary": {
    "checkpoint_count": 11,
    "ready_count": 0,
    "attention_count": 0,
    "blocked_count": 0,
    "external_services_required": false,
    "writes_artifacts": false
  },
  "checkpoints": []
}
```

错误边界：

- 坏 slug 返回 400。
- 缺项目返回 404。
- 坏 JSON/YAML 或缺 artifact 不抛 500，降级为 `attention` 或 `blocked` checkpoint。

## 4. 安全边界

- 不写任何 artifact。
- 不调用真实 LLM、Seedream、embedding、向量库、GraphRAG、Zep 或 reranker。
- 不读取或返回明文 API Key；provider 检查只展示路由和降级状态。
- 不覆盖 `state_snapshot.json`。
- 不改变 `run_scene` 默认行为。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_runtime_preflight.py -q
python -m pytest engine\tests\test_v088_long_project_workspace.py engine\tests\test_v093_retrieval_probe.py engine\tests\test_runtime_settings_api.py engine\tests\test_v100_release_preflight_checklist.py -q
cd engine
python -m pytest -q
cd ui
pnpm run build
cd ..\..
git diff --check
```

## 6. 后续状态

`Chapter Commit / Projection Health MVP` 的只读健康报告已作为后续增强第二刀收口，见 `projection-health-mvp.md`；`Reader Panel / Adversarial Revision Lab MVP` 已作为第三刀收口，见 `reader-panel-revision-lab-mvp.md`；`Prompt Budget Pack MVP` 已作为第四刀收口，见 `prompt-budget-pack-mvp.md`。下一刀建议进入 `LLM Profile Assignment MVP`。
