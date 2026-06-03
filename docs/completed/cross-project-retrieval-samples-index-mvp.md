# Cross Project Retrieval Samples Index MVP 收口说明

> 日期：2026-06-01
> 范围：后续增强第十七刀，跨项目检索失败样本索引。

## 收口结论

Cross Project Retrieval Samples Index MVP 已收口。系统新增只读 service/API/CLI/设置页面板，用本地 `projects/` 下各项目的 retrieval sample migration pack 汇总跨项目检索样本证据，帮助判断 lexical gap、covered case、空样本项目和真实 embedding 前的评估准备度。

该切片不写 artifact、不生成 embedding、不创建向量索引、不连接向量库 / GraphRAG / Zep / reranker，也不读取或返回明文 Key。

## 新增能力

- service：`get_cross_project_retrieval_samples_index()` 扫描本地项目，按 `world.yaml` 项目入口聚合 migration pack。
- API：`GET /api/settings/retrieval-samples-index` 返回跨项目 summary、project rows、flattened records、index gate、manifest 与安全边界。
- CLI：`lne memory index-samples --json` 输出同一份只读索引，适合后续脚本和本地诊断使用。
- UI：设置页新增“跨项目样本索引”面板，展示项目 / records、可迁移 / 空样本、项目状态和前几条 eval record。
- 前端韧性：设置页现在兼容 string warning 与 `{code, message}` warning，避免 provider/profile warning 对象导致整页白屏。

## 验证

- focused：`python -m pytest tests/test_cross_project_retrieval_samples_index.py -q`
- API contract：`python -m pytest tests/test_cross_project_retrieval_samples_index.py tests/test_api_contract.py -q`
- adjacent：跨 migration pack、replay report、mock report、export pack、failure samples、memory CLI 与 API contract 回归。
- 浏览器烟测：临时项目 `cross-index-a` / `cross-index-b` 下打开设置页，确认“跨项目样本索引”显示 `2 / 1`、`1 / 1`、`cross-index-a-retrieval-eval-001` 与 `canon_ledger:canon_000001`。
- 全量基线已由后续 Graph Memory Offline Shadow Replay Report MVP 更新为：`python -m pytest -q` -> `803 passed`；`cd engine/ui && pnpm run build` 通过；根目录 `git diff --check` 通过。

## 保持边界

- 不改变 `run_scene` 默认行为。
- 不替换 `canon_ledger.jsonl`，不覆盖 `state_snapshot.json`。
- 不写跨项目索引 artifact，只读返回内存报告。
- HTTP 设置端点不接受用户传入路径，项目 slug 仍由本地项目目录和 `safe_id` 校验链路约束。
- 真实 embedding provider、向量库、GraphRAG、Zep、reranker 继续保持触发式。

## 下一步建议

后续 `Retrieval Samples Trend Snapshot MVP`、`GraphRAG / Zep Trigger Evidence MVP`、`Graph Memory Spike Design Pack MVP` 与 `Graph Memory Shadow Compare Pack MVP` 已收口，见 `retrieval-samples-trend-snapshot-mvp.md`、`graph-memory-trigger-evidence-mvp.md`、`graph-memory-spike-design-pack-mvp.md`、`graph-memory-shadow-compare-pack-mvp.md`、`graph-memory-shadow-case-matrix-mvp.md`、`graph-memory-provider-boundary-matrix-mvp.md`、`graph-memory-offline-shadow-replay-plan-mvp.md` 与 `graph-memory-offline-shadow-replay-report-mvp.md`。后续 `Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已收口。下一刀建议做 `Graph Memory Provider Spike Fixture Pack MVP`：基于 offline replay report 做 provider spike fixture pack，不默认接外部服务。
