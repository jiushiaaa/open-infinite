# Prompt Budget Pack MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第四刀，长篇记忆增强 B 线的轻量只读切片。  
> 范围：检索上下文预算包，不接 embedding、向量库、GraphRAG、Zep、reranker，不改变默认 prompt 注入链路。

## 1. 目标

Prompt Budget Pack MVP 用于长篇分支生成后，快速回答“现有检索命中了哪些内容、哪些能放进上下文预算、哪些被排除”。它先压缩和解释已有 `retrieval_context.json`，不引入重型检索依赖。

## 2. 已完成

- 新增 service：`living_novel_engine.service.get_prompt_budget_pack(run_id, branch_id)`。
- 新增 API：`GET /api/runs/<run_id>/branches/<branch_id>/prompt-budget-pack`，支持可选 `char_budget`。
- 新增前端入口：分支右栏「上下文包」tab。
- 支持能力：
  - 按 source 优先级排序：contract、canon ledger、fact、chapter brief、volume brief。
  - 按 source + text 去重，保留高优先级条目。
  - 按字符预算截断，并解释被排除条目。
  - 分组渲染为合约约束、正史事实、章节摘要、其他记忆。
  - 输出压缩后的 `prompt_block`、估算 token、压缩比和预算统计。

## 3. API 契约

返回核心字段：

```json
{
  "version": "prompt-budget-pack-mvp",
  "mode": "read_only_prompt_budget_pack",
  "status": "ready | attention | blocked",
  "summary": {
    "char_budget": 1600,
    "source_item_count": 0,
    "deduped_item_count": 0,
    "included_item_count": 0,
    "excluded_item_count": 0,
    "estimated_prompt_chars": 0,
    "estimated_prompt_tokens": 0,
    "writes_artifacts": false,
    "external_services_required": false,
    "uses_vector_store": false
  },
  "sections": [],
  "packed_items": [],
  "excluded_items": [],
  "prompt_block": ""
}
```

错误边界：

- 坏 `run_id` / `branch_id` 返回 400。
- 非法 `char_budget` 返回 400。
- 缺 run 或 branch 返回 404。
- `retrieval_context.json` 缺失或损坏不抛 500，分别降级为 `attention` 或 `blocked`。

## 4. 安全边界

- 不调用真实 LLM。
- 不调用 embedding、向量库、GraphRAG、Zep 或 reranker。
- 不写 artifact。
- 不改变 `retrieval_context.json`、`runtime_memory_context.json` 或默认 runner prompt 注入链路。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_prompt_budget_pack.py -q
python -m pytest engine\tests\test_prompt_budget_pack.py engine\tests\test_context_retrieval.py engine\tests\test_retrieval_artifact.py engine\tests\test_v08x_runtime_memory_context.py engine\tests\test_projection_health.py -q
cd engine\ui
pnpm run build
cd ..
python -m pytest -q
cd ..
git diff --check
```

## 6. 后续状态

`LLM Profile Assignment MVP` 已在后续第五刀收口。Prompt Budget Pack 继续保持只读预算包；只有在需要接入 opt-in prompt 编排或 reranker 时再深化。
