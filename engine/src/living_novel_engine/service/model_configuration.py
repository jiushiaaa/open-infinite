"""只读模型配置摘要，供设置页解释当前本机模型状态。"""

from __future__ import annotations

from .runtime_settings import get_runtime_settings


def _section(
    *,
    id: str,
    label: str,
    status: str,
    status_label: str,
    evidence: str,
    next_step: str,
) -> dict[str, str]:
    return {
        "id": id,
        "label": label,
        "status": status,
        "status_label": status_label,
        "evidence": evidence,
        "next_step": next_step,
    }


def _text_model_presets() -> list[dict[str, object]]:
    return [
        {
            "id": "openai_compatible",
            "label": "OpenAI 兼容",
            "base_url": "https://api.openai.com/v1",
            "model_name": "gpt-4o-mini",
            "api_key_help": "填入对应平台的文本模型密钥。",
            "editable": False,
        },
        {
            "id": "deepseek",
            "label": "DeepSeek",
            "base_url": "https://api.deepseek.com/v1",
            "model_name": "deepseek-chat",
            "api_key_help": "填入 DeepSeek 控制台创建的密钥。",
            "editable": False,
        },
        {
            "id": "qwen",
            "label": "通义千问",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model_name": "qwen-plus",
            "api_key_help": "填入阿里云百炼控制台创建的密钥。",
            "editable": False,
        },
        {
            "id": "volcengine_ark",
            "label": "火山方舟",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "model_name": "doubao-seed-1-6",
            "api_key_help": "填入火山方舟控制台创建的密钥。",
            "editable": False,
        },
        {
            "id": "custom",
            "label": "自定义接口",
            "base_url": "",
            "model_name": "",
            "api_key_help": "手动填写兼容 OpenAI Chat Completions 的接口地址、模型名和密钥。",
            "editable": True,
        },
    ]


def _visual_model_presets() -> list[dict[str, object]]:
    return [
        {
            "id": "seedream_lite",
            "label": "Seedream 5.0 Lite",
            "base_url": "https://ark.cn-beijing.volces.com",
            "model_name": "seedream-5-0-lite",
            "enabled": True,
            "api_key_help": "填入火山方舟视觉模型密钥；不需要图片时可关闭。",
            "editable": False,
        },
        {
            "id": "visual_disabled",
            "label": "关闭视觉资产",
            "base_url": "",
            "model_name": "",
            "enabled": False,
            "api_key_help": "只保留文字主流程，封面、头像和场景图使用占位图。",
            "editable": True,
        },
    ]


def get_model_configuration_summary() -> dict:
    """返回脱敏、只读的模型配置摘要；不做网络探测，不写环境或文件。"""
    settings = get_runtime_settings()

    if settings.llm_api_key_present and not settings.default_mock:
        text_status = "ready"
        text_label = "已接入"
        text_evidence = f"{settings.llm_model_name} · {settings.masked_key}"
        text_next = "可直接使用真实文本模型生成；必要时点击测试连接确认可达。"
    elif settings.llm_api_key_present:
        text_status = "attention"
        text_label = "已配置但模拟中"
        text_evidence = f"{settings.llm_model_name} · {settings.masked_key}"
        text_next = "关闭“默认用模拟生成”后，新的生成才会调用真实文本模型。"
    else:
        text_status = "attention"
        text_label = "未配置"
        text_evidence = f"{settings.llm_model_name} · 当前走本地模拟"
        text_next = "填入 API 密钥、接口地址和模型名称后，再测试连接。"

    if not settings.visual_assets_enabled:
        visual_status = "ready"
        visual_label = "已关闭"
        visual_evidence = "视觉资产生成关闭，文字主流程不受影响。"
        visual_next = "需要封面、头像或场景图时再启用视觉资产生成。"
    elif settings.seedream_key_present:
        visual_status = "ready"
        visual_label = "已配置"
        visual_evidence = f"{settings.seedream_model} · {settings.seedream_masked_key}"
        visual_next = "视觉资产可在项目页按需生成；失败时仍会降级为占位图。"
    else:
        visual_status = "attention"
        visual_label = "占位降级"
        visual_evidence = f"{settings.seedream_model} · 未配置密钥"
        visual_next = "不需要图片时可保持现状；需要真实图像时填入 Seedream 密钥。"

    warnings: list[str] = []
    if not settings.llm_api_key_present:
        warnings.append("文本模型未配置密钥，当前默认使用本地模拟生成。")
    elif settings.default_mock:
        warnings.append("文本模型已配置，但默认仍启用模拟生成。")
    if settings.visual_assets_enabled and not settings.seedream_key_present:
        warnings.append("视觉资产未配置密钥，生成失败时会展示占位图。")

    sections = [
        _section(
            id="text_model",
            label="文本模型",
            status=text_status,
            status_label=text_label,
            evidence=text_evidence,
            next_step=text_next,
        ),
        _section(
            id="connection_test",
            label="连接测试",
            status="ready",
            status_label="可测试",
            evidence="设置页提供一次轻量连通性检查；mock 模式不会触发外网。",
            next_step="保存设置后点击“测试连接”，确认接口地址、密钥和模型名可用。",
        ),
        _section(
            id="default_runner",
            label="默认推演",
            status="ready",
            status_label="已设置",
            evidence=(
                f"{settings.default_runner} · {settings.default_rounds} 轮 · "
                f"{'模拟' if settings.default_mock else '真实模型'}"
            ),
            next_step="需要更细的多角色推演时再切换 runner；默认行为不改 run_scene。",
        ),
        _section(
            id="visual_model",
            label="视觉模型",
            status=visual_status,
            status_label=visual_label,
            evidence=visual_evidence,
            next_step=visual_next,
        ),
        _section(
            id="secret_boundary",
            label="密钥边界",
            status="ready",
            status_label="仅脱敏展示",
            evidence="设置只写当前本机进程，页面只显示尾号，不返回明文密钥。",
            next_step="部署到服务器前再补正式的密钥托管和多用户隔离。",
        ),
    ]

    ready_count = sum(1 for item in sections if item["status"] == "ready")
    attention_count = len(sections) - ready_count

    return {
        "version": "v1.0-local-model-configuration-ux",
        "mode": "read_only_model_configuration_summary",
        "status": "ready" if attention_count == 0 else "attention",
        "summary": {
            "llm_configured": settings.llm_api_key_present,
            "mock_enabled": settings.default_mock,
            "visual_configured": settings.seedream_key_present,
            "visual_enabled": settings.visual_assets_enabled,
            "connectivity_check_available": True,
            "plaintext_key_returned": False,
            "ready_count": ready_count,
            "attention_count": attention_count,
        },
        "sections": sections,
        "text_model_presets": _text_model_presets(),
        "visual_model_presets": _visual_model_presets(),
        "form_guidance": {
            "save_scope": "process_only",
            "plaintext_key_returned": False,
            "connection_test_note": "只有用户点击测试连接时才会发起轻量模型请求；mock 测试不打外网。",
            "secret_boundary": "当前设置仅写入本机运行中的引擎进程，页面只显示脱敏尾号。",
        },
        "warnings": warnings,
        "next_steps": [
            "先让文本模型配置可用，再继续长篇创作闭环本地验证。",
            "安装包和线上体验入口放到本地产品稳定后的分发阶段推进。",
        ],
    }
