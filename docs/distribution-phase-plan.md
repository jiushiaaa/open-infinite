# 未终章 发行路径计划

> 状态：本地运行脚本与 Bundled Release Readiness MVP 已落地；安装包、自动部署和线上多用户实现仍后置，等本地产品闭环稳定、用户本地验证通过后再进入。

## 1. 目标

把未终章的使用方式整理成三条可并行存在的路径：

| 使用方式 | 面向用户 | 当前状态 | 进入条件 |
| --- | --- | --- | --- |
| 本地 clone + 配环境 | 技术用户、早期体验者 | 现有路径 | README、设置页模型配置和本地 smoke 足够清晰 |
| GitHub Release 安装包 | 不想手动配置 Python/Node 的普通用户 | 后置排期；已有本地启动脚本底座与发行准备只读清单 | 本地产品大体稳定、无大迭代、安装脚本可重复验证 |
| 服务器在线体验 | 不想 clone 或下载安装的用户 | 后置排期 | 本地版本稳定、服务器资源已购买、认证与数据边界明确 |

## 2. 本地 Clone 路径

短期主路径仍是 GitHub README 指引：

1. clone 仓库。
2. 安装 Python 与 Node/pnpm 依赖。
3. 在设置页配置文本模型、视觉模型和默认运行参数。
4. 本地启动后端与前端，完成导入、创作、审计、导出闭环。

当前优先级是让这条路径足够稳：模型配置状态要清楚、错误态不白屏、本地 smoke 能指导用户自查。

### 2.1 本地一键运行脚本

当前已新增两条脚本路径，面向 clone 仓库后的本地启动：

```powershell
# Windows
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start-local.ps1
```

```bash
# macOS / Linux
bash scripts/start-local.sh
```

脚本会检查 Python、Node 与 pnpm，创建 `engine/.venv`，安装后端 package 与前端依赖，启动后端 `lne browse` 服务和 Vite 前端，并打开 `http://127.0.0.1:5173/`。日志写入 `.local-run/`。

可用于自检的轻量命令：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start-local.ps1 -CheckOnly -NoBrowser
```

```bash
bash scripts/start-local.sh --check-only --no-browser
```

这不是 GitHub Release 安装包，也不内置 Python/Node runtime；发行准备清单只负责说明当前仓库离打包还差什么，D2/D3 再处理更干净环境下的依赖 bootstrap 与打包形态。

## 3. Release 安装包路径

后续目标是提供 Windows 与 macOS 的一键运行包，放到 GitHub Releases：

- Windows：优先评估 `.exe` 或解压即用目录，内置启动器负责检查/安装依赖并启动前后端。
- macOS：优先评估 `.app` / `.dmg` 或 shell 启动器，尽量减少用户手动命令。
- 两端都需要：
  - 首次启动检查 Python、Node、pnpm 或内置 runtime。
  - 一键安装 Python package 与前端依赖。
  - 自动启动后端和 Vite/静态前端。
  - 打开浏览器到本地入口。
  - 提供清晰日志和失败提示。

本阶段不引入真实计费；安装包只面向本地单机体验。

## 4. 服务器在线体验路径

用户计划后续购买腾讯云 2 核 4G 服务器，届时目标是提供一个可线上体验的入口：

- 初期可以是单机部署：后端 + 前端 + 本地文件目录。
- 需要先明确是否开放登录；未接真实认证前，不承载隐私敏感或多人隔离数据。
- 模型配置应支持服务器侧安全注入，不在前端泄漏 API Key。
- 数据目录、备份、日志、进程守护和反向代理要作为部署任务处理。

服务器部署排在本地产品稳定和 Release 安装体验明确之后；不抢当前功能闭环优先级。

## 5. 后续拆刀建议

| 顺序 | 名称 | 范围 | 验证 |
| --- | --- | --- | --- |
| D1 | Local Run Script | `scripts/start-local.ps1` 与 `scripts/start-local.sh` 一键启动后端和前端 | 已落地；Windows check-only 已验证，完整启动需本机 HTTP smoke |
| D2 | Bundled Release Readiness | 设置页只读检查脚本、package、前端 dist、发行文档和密钥边界 | 已落地；不创建安装包、不内置 runtime |
| D3 | Dependency Bootstrap | 自动检查并安装 Python/Node/pnpm 依赖 | 干净环境或半干净环境重复执行 |
| D4 | Release Packager Spike | 评估 `.exe`、`.app/.dmg`、压缩包三种形式 | GitHub Release 草包本地安装 |
| D5 | Tencent Cloud Deploy Guide | 2c4g 单机部署脚本与文档 | 云端后端/前端健康检查 |
| D6 | Hosted Safety Boundary | 在线体验的数据隔离、密钥、日志和权限边界 | 不泄漏 Key，不暴露本地文件路径 |

暂停条件：只要本地产品仍有明显主流程缺口，就不进入 D1-D5。
