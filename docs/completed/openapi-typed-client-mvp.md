# OpenAPI / Typed Client MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第七刀，本地 HTTP 契约与 typed client 准备层。  
> 范围：只读 API contract、OpenAPI skeleton、前端手写类型映射和设置页展示；不生成文件，不接外部 API 网关，不开放公网 API。

## 1. 目标

OpenAPI / Typed Client MVP 用于把已有本地 HTTP API 从“散落在 server 与前端手写类型里”整理成可查看、可测试、可对齐的契约清单。第一刀先提供只读 schema 与 typed client 映射，服务后续桌面壳、插件、外部前端或生成型 client 的准备工作。

## 2. 已完成

- 新增 service：`living_novel_engine.service.get_api_contract()`。
- 新增 API：`GET /api/settings/api-contract`。
- 新增前端 client：`api.getApiContract()`。
- 新增前端类型：`ApiContractReport`、`ApiContractEndpoint`、`ApiContractGroup`、`ApiContractTypedClientMethod`。
- 设置抽屉新增「接口契约」只读面板，展示端点数、OpenAPI 路径数、typed client 方法数、分组和代表端点。
- 契约覆盖本地常用分组：故事与项目、运行与分支、异步任务、设置与边界、导出与评审。

## 3. API 契约

返回核心字段：

```json
{
  "version": "openapi-typed-client-mvp",
  "mode": "read_only_api_contract",
  "status": "ready",
  "summary": {
    "endpoint_count": 41,
    "openapi_path_count": 40,
    "typed_client_method_count": 40,
    "writes_artifacts": false,
    "external_services_required": false,
    "plaintext_key_returned": false,
    "generated_client_written": false
  },
  "openapi": {},
  "groups": [],
  "endpoints": [],
  "typed_client": {
    "client_source": "engine/ui/src/api/client.ts",
    "types_source": "engine/ui/src/api/types.ts",
    "methods": []
  },
  "boundaries": [],
  "next_steps": []
}
```

当前 OpenAPI 仍是 skeleton：路径、method、operationId、summary、tag、响应状态和 response type 先稳定下来；字段级 schema 与自动生成 client 保持后置。

## 4. 安全边界

- 不读取 `.env` 或明文密钥。
- 不调用真实 LLM、Seedream、embedding、向量库、GraphRAG、Zep、reranker。
- 不写 artifact，不生成 client 文件，不修改现有手写 client 行为。
- 不改变 `run_scene`、job、runner 或既有 API 契约。
- 不接外部 API 网关、插件市场或云端 schema registry。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_api_contract.py -q
python -m pytest engine\tests\test_api_contract.py engine\tests\test_runtime_settings_api.py engine\tests\test_llm_profile_assignment.py engine\tests\test_cards_workspace.py -q
cd engine\ui
pnpm.cmd run build
cd ..
python -m pytest -q
```

浏览器烟测：本地后端 + Vite 下打开设置抽屉，确认「接口契约」面板显示本地端点/路径、typed client 方法和类型入口。

当前后端全量基线：`803 passed`。

## 6. 后续状态

`Bundled Release Readiness MVP` 已在后续第八刀收口，见 `bundled-release-readiness-mvp.md`。`Embedding / Vector Retrieval Readiness Probe MVP` 已在后续第九刀收口，见 `vector-retrieval-readiness-probe-mvp.md`。`Embedding Evaluation Samples MVP`、`Retrieval Failure Sample Authoring MVP`、`Memory CLI MVP`、`Retrieval Sample Export Pack MVP`、`Embedding Mock Evaluation Report MVP`、`Retrieval Sample Replay Report MVP`、`Retrieval Sample Migration Pack MVP`、`Cross Project Retrieval Samples Index MVP`、`Retrieval Samples Trend Snapshot MVP`、`GraphRAG / Zep Trigger Evidence MVP`、`Graph Memory Spike Design Pack MVP`、`Graph Memory Shadow Compare Pack MVP`、`Graph Memory Shadow Case Matrix MVP`、`Graph Memory Provider Boundary Matrix MVP` 、`Graph Memory Offline Shadow Replay Plan MVP` 与 `Graph Memory Offline Shadow Replay Report MVP` 已在后续第十至二十五刀收口，见 `embedding-evaluation-samples-mvp.md`、`retrieval-failure-sample-authoring-mvp.md`、`memory-cli-mvp.md`、`retrieval-sample-export-pack-mvp.md`、`embedding-mock-evaluation-report-mvp.md`、`retrieval-sample-replay-report-mvp.md`、`retrieval-sample-migration-pack-mvp.md`、`cross-project-retrieval-samples-index-mvp.md`、`retrieval-samples-trend-snapshot-mvp.md`、`graph-memory-trigger-evidence-mvp.md`、`graph-memory-spike-design-pack-mvp.md`、`graph-memory-shadow-compare-pack-mvp.md`、`graph-memory-shadow-case-matrix-mvp.md`、`graph-memory-provider-boundary-matrix-mvp.md`、`graph-memory-offline-shadow-replay-plan-mvp.md` 与 `graph-memory-offline-shadow-replay-report-mvp.md`。Graph Memory Offline Shadow Replay Plan MVP 与 Graph Memory Offline Shadow Replay Report MVP 已接续收口；后续建议进入 Graph Memory Provider Spike Fixture Pack，继续不接生产向量库或外部 provider。
