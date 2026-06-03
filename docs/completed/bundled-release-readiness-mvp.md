# Bundled Release / Desktop Packaging Readiness MVP 收口说明

> 日期：2026-06-01  
> 性质：后续增强第八刀，本地发行与桌面打包准备度只读清单。  
> 范围：检查本地启动脚本、后端 package、前端 package/dist、发行文档和密钥边界；不创建安装包，不内置 runtime，不上传 Release。

## 1. 目标

Bundled Release / Desktop Packaging Readiness MVP 用于在真正打包前回答“本地版本离安装包/桌面壳还差什么”。第一刀只读检查仓库已有文件和边界，不做 PyInstaller、Tauri、Electron、dmg/exe/zip 生成，也不把密钥或外部账号纳入流程。

## 2. 已完成

- 新增 service：`living_novel_engine.service.get_bundled_release_readiness()`。
- 新增 API：`GET /api/settings/packaging-readiness`。
- 新增前端 client：`api.getPackagingReadiness()`。
- 新增前端类型：`BundledReleaseReadinessReport`、`BundledReleaseReadinessCheck`、`BundledReleasePackageTarget`。
- 设置抽屉新增「发行准备」只读面板，展示：
  - Windows / macOS/Linux 启动脚本。
  - 后端 `pyproject.toml`。
  - 前端 `package.json` 与 `dist/index.html`。
  - 发行路径文档与 README 本地运行说明。
  - 密钥边界。
  - Windows 解压包、macOS 包、桌面壳、内置 runtime 的后置状态。

## 3. API 契约

返回核心字段：

```json
{
  "version": "bundled-release-readiness-mvp",
  "mode": "read_only_packaging_readiness",
  "status": "ready | attention",
  "summary": {
    "check_count": 8,
    "ready_count": 8,
    "attention_count": 0,
    "deferred_target_count": 4,
    "writes_artifacts": false,
    "external_services_required": false,
    "plaintext_key_returned": false,
    "builds_package": false,
    "bundles_runtime": false
  },
  "checks": [],
  "package_targets": [],
  "boundaries": [],
  "next_steps": [],
  "warnings": []
}
```

缺脚本、缺 package 或缺前端 dist 时返回 `attention` 与 warning，不抛 500，不尝试自动安装或构建。

## 4. 安全边界

- 不读取 `.env` 或明文密钥。
- 不启动进程、不安装依赖、不执行构建。
- 不创建 `.exe`、`.app`、`.dmg`、zip 或任何发行 artifact。
- 不内置 Python / Node / pnpm runtime，不做自动升级。
- 不上传 GitHub Release，不接对象存储、云端部署或在线多用户系统。

## 5. 验证

已通过：

```powershell
python -m pytest engine\tests\test_bundled_release_readiness.py -q
python -m pytest engine\tests\test_bundled_release_readiness.py engine\tests\test_api_contract.py engine\tests\test_runtime_settings_api.py engine\tests\test_v100_model_configuration_summary.py -q
cd engine\ui
pnpm.cmd run build
cd ..
python -m pytest -q
```

浏览器烟测：本地后端 + Vite 下打开设置抽屉，确认「发行准备」面板显示本地脚本、package、dist 和后置桌面壳目标。

当前后端全量基线：`737 passed`。

## 6. 后续状态

`Embedding / Vector Retrieval Readiness Probe MVP` 已在后续第九刀收口，见 `vector-retrieval-readiness-probe-mvp.md`。下一步建议进入 `Embedding Evaluation Samples MVP`：继续不接真实 provider，先稳定失败样本结构和 mock embedding 对照报告。
