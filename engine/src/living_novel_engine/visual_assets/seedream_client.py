"""Seedream 5.0 Lite 图像生成客户端（增强层，非核心运行时依赖）。

边界与降级原则：
- import 时不读取网络、不创建连接。
- 无 SEEDREAM_API_KEY 或 LNE_VISUAL_ASSETS=0 时 available=False，返回明确不可用。
- 网络异常 / HTTP 错误 / 返回格式异常一律被捕获，返回 ok=False，不外溢。
- 兼容解析 base64（b64_json/b64/image_base64）或 url；都识别不了返回 failed。
- 不在错误信息里拼接 API Key。
- 单测用 fake client / monkeypatch _raw_generate，不打真实外网。

接口路径默认 /api/v3/images/generations（火山方舟 Ark 风格），可用 SEEDREAM_PATH 覆盖。
由于线上接口格式可能调整，解析写成兼容式；无法识别即 failed，详见 README smoke checklist。
"""

from __future__ import annotations

import base64
import json
import os
import urllib.request
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com"
DEFAULT_MODEL = "seedream-5-0-lite"
DEFAULT_PATH = "/api/v3/images/generations"

_OFF_VALUES = ("0", "off", "false", "no")


def _env_enabled() -> bool:
    raw = os.environ.get("LNE_VISUAL_ASSETS", "").strip().lower()
    return raw not in _OFF_VALUES


@dataclass
class SeedreamSettings:
    api_key: str = ""
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    path: str = DEFAULT_PATH
    enabled: bool = True

    @classmethod
    def from_env(cls) -> "SeedreamSettings":
        return cls(
            api_key=os.environ.get("SEEDREAM_API_KEY", "") or "",
            base_url=(os.environ.get("SEEDREAM_BASE_URL", "").strip() or DEFAULT_BASE_URL),
            model=(os.environ.get("SEEDREAM_MODEL", "").strip() or DEFAULT_MODEL),
            path=(os.environ.get("SEEDREAM_PATH", "").strip() or DEFAULT_PATH),
            enabled=_env_enabled(),
        )


@dataclass
class ImageResult:
    ok: bool
    data: bytes | None = None
    ext: str = "png"
    error: str = ""


class SeedreamClient:
    def __init__(
        self,
        settings: SeedreamSettings | None = None,
        *,
        mock: bool = False,
        timeout: float = 30.0,
    ) -> None:
        self.settings = settings or SeedreamSettings.from_env()
        self.mock = mock
        self.timeout = timeout

    @property
    def available(self) -> bool:
        if not self.settings.enabled:
            return False
        if self.mock:
            return True
        return bool(self.settings.api_key)

    def generate_image(self, prompt: str) -> ImageResult:
        """生成图片字节。任何失败都返回 ok=False，不抛异常。"""
        if not self.settings.enabled:
            return ImageResult(ok=False, error="视觉资产已关闭（LNE_VISUAL_ASSETS=0）")
        if self.mock:
            # mock 不打网络，由 service 落为占位条目。
            return ImageResult(ok=False, error="mock 模式不生成真实图片")
        if not self.settings.api_key:
            return ImageResult(ok=False, error="未配置 SEEDREAM_API_KEY")
        try:
            payload = self._raw_generate(prompt)
        except Exception as exc:  # 网络/HTTP/超时一律降级
            return ImageResult(ok=False, error=f"Seedream 调用失败：{exc}")
        return self._parse(payload)

    # ── 网络层（单测 monkeypatch 这里，不打真实外网） ──

    def _raw_generate(self, prompt: str) -> dict:
        url = self.settings.base_url.rstrip("/") + self.settings.path
        body = json.dumps(
            {
                "model": self.settings.model,
                "prompt": prompt,
                "response_format": "b64_json",
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.settings.api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310
            raw = resp.read().decode("utf-8")
        return json.loads(raw)

    def _parse(self, payload: dict) -> ImageResult:
        if not isinstance(payload, dict):
            return ImageResult(ok=False, error="Seedream 返回格式无法识别")
        data = payload.get("data") or payload.get("images") or []
        if not isinstance(data, list) or not data:
            return ImageResult(ok=False, error="Seedream 返回中无图片数据")
        first = data[0] if isinstance(data[0], dict) else {}
        b64 = first.get("b64_json") or first.get("b64") or first.get("image_base64")
        if b64:
            try:
                return ImageResult(ok=True, data=base64.b64decode(b64), ext="png")
            except Exception as exc:
                return ImageResult(ok=False, error=f"base64 解码失败：{exc}")
        url = first.get("url") or first.get("image_url")
        if isinstance(url, str) and url:
            return self._download(url)
        return ImageResult(ok=False, error="Seedream 返回中未找到 b64_json 或 url")

    def _download(self, url: str) -> ImageResult:
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as resp:  # noqa: S310
                data = resp.read()
        except Exception as exc:
            return ImageResult(ok=False, error=f"图片下载失败：{exc}")
        ext = "png"
        clean = url.lower().split("?")[0]
        for candidate in ("png", "jpg", "jpeg", "webp"):
            if clean.endswith("." + candidate):
                ext = "jpg" if candidate == "jpeg" else candidate
                break
        return ImageResult(ok=True, data=data, ext=ext)
