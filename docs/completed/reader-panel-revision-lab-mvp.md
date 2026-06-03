# Reader Panel / Adversarial Revision Lab MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第三刀，deterministic/mockable 产品化切片。  
> 范围：生成后读者评审与修订 brief，不调真实 LLM、不写 revision artifact、不覆盖正文。

## 1. 目标

Reader Panel / Adversarial Revision Lab MVP 用于长篇分支生成后，快速指出文本层面的可修订问题。它先做稳定、可测试、可解释的确定性版本，为后续 LLM 自动改写或多读者 Elo 对比提供基线。

## 2. 已完成

- 新增 service：`living_novel_engine.service.get_reader_panel(run_id, branch_id)`。
- 新增 API：`GET /api/runs/<run_id>/branches/<branch_id>/reader-panel`。
- 新增前端入口：分支右栏「读者评审」tab。
- 新增四类读者人格：
  - 急性子读者：追读压力和信息密度。
  - 句线编辑：重复句、口癖和可删字。
  - 连续性读者：角色声音与事实承接。
  - 节奏读者：段落推进、转折和收束钩子。
- 新增五类 deterministic issue：
  - 过度解释 `over_explanation`
  - 三段式堆叠 `three_part_stack`
  - 重复结尾 `repeated_ending`
  - 对话同声 `same_voice_dialogue`
  - 节奏过平 `flat_pacing`

## 3. API 契约

返回核心字段：

```json
{
  "version": "reader-panel-mvp",
  "mode": "deterministic_reader_panel",
  "status": "ready | attention | blocked",
  "summary": {
    "issue_count": 0,
    "persona_count": 4,
    "revision_brief_count": 0,
    "writes_artifacts": false,
    "external_services_required": false,
    "llm_required": false
  },
  "personas": [],
  "issues": [],
  "revision_briefs": []
}
```

错误边界：

- 坏 `run_id` / `branch_id` 返回 400。
- 缺 run 或 branch 返回 404。
- `narrative_diagnostics.json` 或 `worldline_judgement.json` 损坏时只写 warning，仍可基于 `chapter.md` 产出评审。

## 4. 安全边界

- 不调用真实 LLM、Seedream、embedding、向量库、GraphRAG、Zep 或 reranker。
- 不写 revision artifact。
- 不覆盖 `chapter.md`。
- 不改变 `run_scene` 默认行为。
- 修订 brief 只作为人工或后续 opt-in 改写输入。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_reader_panel.py -q
python -m pytest engine\tests\test_reader_panel.py engine\tests\test_projection_health.py engine\tests\test_v075_worldline_judge.py engine\tests\test_v087_narrative_diagnostics.py -q
cd engine\ui
pnpm run build
cd ..
python -m pytest -q
cd ..
git diff --check
```

## 6. 后续状态

`Prompt Budget Pack / Retrieval Context Budget MVP` 已作为后续增强第四刀收口，见 `prompt-budget-pack-mvp.md`。下一刀建议进入 `LLM Profile Assignment MVP`，继续保持本地可读/可测，不默认调真实模型。
