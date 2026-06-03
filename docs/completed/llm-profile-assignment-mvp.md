# LLM Profile Assignment MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第五刀，模型配置产品化的只读任务画像切片。  
> 范围：任务级模型、温度、预算和降级策略汇总；不保存 profile、不测试连接、不调真实模型、不回显密钥。

## 1. 目标

LLM Profile Assignment MVP 用于回答“不同任务应该用什么模型策略、温度、预算和降级策略”。它把现有模型路由矩阵、模型配置状态和本地确定性能力汇总成设置页可读清单，先帮助用户理解当前运行配置，不改变 runner 默认行为。

## 2. 已完成

- 新增 service：`living_novel_engine.service.get_llm_profile_assignment()`。
- 新增 API：`GET /api/settings/llm-profile-assignment`。
- 新增设置页入口：「任务模型画像」只读面板。
- 覆盖任务：
  - 读者干预生成。
  - 主题创世。
  - 导入抽取。
  - 读者修订建议。
  - 世界线评审。
  - 视觉资产生成。
- 输出每个任务的 provider、mode、model、temperature、max tokens、budget tier、fallback 标识和中文说明。

## 3. API 契约

返回核心字段：

```json
{
  "version": "llm-profile-assignment-mvp",
  "mode": "read_only_llm_profile_assignment",
  "status": "ready | attention",
  "summary": {
    "profile_count": 6,
    "provider_profile_count": 0,
    "mock_or_deterministic_count": 0,
    "writes_artifacts": false,
    "external_services_required": false,
    "plaintext_key_returned": false
  },
  "routing": {
    "llm_route": "mock | provider",
    "visual_route": "placeholder | disabled | seedream_visual",
    "fallback_policy": "mock/placeholder"
  },
  "profiles": [],
  "warnings": [],
  "boundaries": [],
  "next_steps": []
}
```

## 4. 安全边界

- 不发起连接测试。
- 不发起真实 LLM 或 Seedream 请求。
- 不写环境变量、配置文件或 artifact。
- 不返回明文 API Key。
- 不返回密钥环境变量名。
- 不改变 `run_scene`、job 或前端生成默认行为。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_llm_profile_assignment.py -q
python -m pytest engine\tests\test_llm_profile_assignment.py engine\tests\test_v100_model_configuration_summary.py engine\tests\test_runtime_settings_api.py -q
cd engine\ui
pnpm run build
cd ..
python -m pytest -q
cd ..
git diff --check
```

说明：第一次后端全量在 Windows 本地 HTTP 用例 `test_bad_branch_id_400` 出现过一次 `ConnectionAbortedError`；单用例与模块重跑均通过，第二次全量通过，未发现本切片稳定回归。当前全量基线以根目录 `memory.md` 为准。

## 6. 后续状态

`Cards Workspace MVP` 已在后续第六刀收口。LLM Profile Assignment 继续保持只读任务画像；只有在需要 opt-in 保存 profile、版本化或真实模型实验时再深化。
