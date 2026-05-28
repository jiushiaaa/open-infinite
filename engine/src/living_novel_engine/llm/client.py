from __future__ import annotations

import json
import os
from typing import Any, TypeVar

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

T = TypeVar("T", bound=BaseModel)


def _engine_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(_engine_root(), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model_name: str = "gpt-4o-mini"

    @classmethod
    def from_env(cls) -> "LLMSettings":
        load_dotenv(os.path.join(_engine_root(), ".env"))
        # Also try repo root MiroFish .env for convenience
        repo_root = os.path.abspath(os.path.join(_engine_root(), ".."))
        miro_env = os.path.join(repo_root, "MiroFish", ".env")
        if os.path.exists(miro_env):
            load_dotenv(miro_env, override=False)
        return cls(
            llm_api_key=os.environ.get("LLM_API_KEY", ""),
            llm_base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
            llm_model_name=os.environ.get("LLM_MODEL_NAME", "gpt-4o-mini"),
        )


class LLMClient:
    def __init__(self, settings: LLMSettings | None = None, mock: bool = False):
        self.settings = settings or LLMSettings.from_env()
        self.mock = mock
        self._client: OpenAI | None = None
        if not mock and self.settings.llm_api_key:
            self._client = OpenAI(
                api_key=self.settings.llm_api_key,
                base_url=self.settings.llm_base_url,
            )

    @property
    def available(self) -> bool:
        return self.mock or bool(self._client)

    def chat(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        if self.mock:
            return self._mock_response(system, user)
        if not self._client:
            raise RuntimeError("LLM_API_KEY 未配置，请复制 .env.example 为 .env 并填写密钥")
        resp = self._client.chat.completions.create(
            model=self.settings.llm_model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (resp.choices[0].message.content or "").strip()

    def chat_json(
        self,
        system: str,
        user: str,
        model_type: type[T],
        *,
        temperature: float = 0.4,
    ) -> T:
        schema_hint = json.dumps(model_type.model_json_schema(), ensure_ascii=False)
        full_system = (
            f"{system}\n\n"
            "你必须只输出合法 JSON，不要 markdown 代码块。\n"
            f"JSON Schema:\n{schema_hint}"
        )
        raw = self.chat(full_system, user, temperature=temperature)
        data = _extract_json(raw)
        return model_type.model_validate(data)

    def _mock_response(self, system: str, user: str) -> str:
        if "章节正文" in system or "网文" in system:
            return (
                "【模拟章节】雨夜天荒，林晚舟在听雨轩前驻足。"
                "一道无形低语落入她心湖，她指尖微颤，却未立刻折返。"
                "林凡在暗处咬破舌尖，传讯玉简终究没有捏碎。"
                "子时更漏已尽，竹林方向传来一声极轻的铃响——"
                "故事在此分叉，等待读者选择的世界线继续生长。"
            )
        if "JSON" in system or "json" in system.lower():
            return json.dumps(
                {
                    "stance": "doubt",
                    "action_type": "investigate",
                    "target": "lin_wan_zhou",
                    "content": "低声唤住师姐，以半真半假之语试探",
                    "internal_thought": "低语来得蹊跷，但不能让师姐孤身赴险",
                    "intervention_response": "doubt",
                },
                ensure_ascii=False,
            )
        return "【模拟响应】已处理请求。"


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [ln for ln in lines if not ln.strip().startswith("```")]
        text = "\n".join(lines)
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    return json.loads(text)
