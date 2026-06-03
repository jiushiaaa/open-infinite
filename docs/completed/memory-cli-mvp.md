# Memory CLI MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第十二刀，检索失败样本的命令行采集与复跑入口。  
> 范围：新增 `lne memory add-sample` 与 `lne memory samples`；复用本地失败样本 service 与 embedding 样本评估 service；不调用真实 embedding provider，不创建向量索引，不接外部服务。

## 1. 目标

上一刀已把失败样本采集接入项目工作台，但无人值守与批处理场景仍需要 CLI。Memory CLI MVP 把同一套本地样本能力暴露给命令行，让后续可以通过脚本批量追加、复跑和检查候选样本，而不是手写 JSONL 或打开 UI。

## 2. 已完成

- 新增 CLI group：`lne memory`。
- 新增命令：`lne memory add-sample <slug>`。
  - 参数：`--query`、`--entity`、`--entities`、`--reason`、`--chapter`、`--json`。
  - 复用 `add_retrieval_failure_sample()`，保持 UI/API 相同校验边界。
- 新增命令：`lne memory samples <slug>`。
  - 参数：`--json`、`--require-candidate`。
  - 复用 `get_embedding_evaluation_samples()`，输出 BM25 vs mock semantic oracle 评估。
- 修复 `living_novel_engine.browser.__init__` 的 eager server import，避免干净进程中 CLI 懒加载 service 时触发循环导入。

## 3. 用法

追加失败样本：

```powershell
lne memory add-sample my-story `
  --query "她必须追查那个遗失的关键物证" `
  --entity mo_qing_yan `
  --entity retreat_bell `
  --reason "换说法未命中" `
  --chapter 2
```

复跑并输出 JSON：

```powershell
lne memory samples my-story --json --require-candidate
```

`--require-candidate` 会在没有 `candidate` 状态时返回非零退出码，方便无人值守脚本判断当前样本集是否真的证明了词面召回缺口。

## 4. 安全边界

- 仅复用本地 JSONL 样本和本地 BM25/mock oracle 评估。
- 不读取 `.env` 或明文密钥。
- 不调用真实 LLM、embedding provider、Seedream 或外部 HTTP 服务。
- 不生成 embedding，不创建向量索引，不连接向量库、GraphRAG、Zep 或 reranker。
- 不替换 `retrieve_context()`，不改变 `run_scene` 默认行为。
- `add-sample` 与 UI/API 共用疑似密钥校验和内置样例只读冲突处理。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_memory_cli.py -q
python -m pytest engine\tests\test_memory_cli.py engine\tests\test_retrieval_failure_samples.py engine\tests\test_embedding_evaluation_samples.py -q
cd engine\ui
pnpm.cmd run build
cd ..
python -m pytest -q
```

当前后端全量基线：`803 passed`。

## 6. 下一刀

`Retrieval Sample Export Pack MVP` 已在后续第十三刀收口，见 `retrieval-sample-export-pack-mvp.md`：失败样本可通过 service/API/UI/CLI 导出为 Markdown 与 manifest。`Embedding Mock Evaluation Report MVP` 已在后续第十四刀收口，见 `embedding-mock-evaluation-report-mvp.md`。`Retrieval Sample Replay Report MVP` 已在后续第十五刀收口，见 `retrieval-sample-replay-report-mvp.md`。`Retrieval Sample Migration Pack MVP` 已在后续第十六刀收口，见 `retrieval-sample-migration-pack-mvp.md`。`Cross Project Retrieval Samples Index MVP`、`Retrieval Samples Trend Snapshot MVP`、`GraphRAG / Zep Trigger Evidence MVP`、`Graph Memory Spike Design Pack MVP`、`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已在后续第十七至二十五刀收口，见 `cross-project-retrieval-samples-index-mvp.md`、`retrieval-samples-trend-snapshot-mvp.md`、`graph-memory-trigger-evidence-mvp.md`、`graph-memory-spike-design-pack-mvp.md`、`graph-memory-shadow-compare-pack-mvp.md`、`graph-memory-shadow-case-matrix-mvp.md`、`graph-memory-provider-boundary-matrix-mvp.md`、`graph-memory-offline-shadow-replay-plan-mvp.md` 与 `graph-memory-offline-shadow-replay-report-mvp.md`。后续 `Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已收口，下一刀建议进入 `Graph Memory Provider Spike Fixture Pack MVP`，继续不接真实 provider。
