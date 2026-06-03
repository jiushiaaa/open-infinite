"""Retrieval provider configuration and smoke checks.

This slice prepares real embedding, vector store, and reranker providers, but
does not replace the current BM25 retrieval path or write vector artifacts.
"""

from __future__ import annotations

import importlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import request

from dotenv import load_dotenv
from openai import OpenAI

VERSION = "retrieval-provider-configuration-mvp"

_EMBEDDING_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
_EMBEDDING_MODEL = "text-embedding-v3"
_EMBEDDING_DIMENSION = 1024
_RERANK_ENDPOINT = (
    "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank"
)
_RERANK_MODEL = "gte-rerank-v2"
_ZILLIZ_COLLECTION = "unfinale_memory"
_HTTP_TIMEOUT_SECONDS = 20


@dataclass(frozen=True)
class RetrievalProviderSettings:
    embedding_api_key: str
    embedding_base_url: str
    embedding_model: str
    embedding_dimension: int
    embedding_batch_size: int
    vector_store_provider: str
    zilliz_uri: str
    zilliz_token: str
    zilliz_collection: str
    rerank_api_key: str
    rerank_endpoint: str
    rerank_model: str
    rerank_top_n: int


def _engine_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_env_file() -> None:
    load_dotenv(_engine_root() / ".env", override=False)


def _env(name: str, fallback: str = "") -> str:
    return os.environ.get(name, "").strip() or fallback


def _int_env(name: str, fallback: int, *, minimum: int, maximum: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return fallback
    try:
        value = int(raw)
    except ValueError:
        return fallback
    return max(minimum, min(maximum, value))


def _mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "*" * len(value)
    return "*" * 6 + value[-4:]


def get_retrieval_provider_settings() -> RetrievalProviderSettings:
    _load_env_file()
    dashscope_key = _env("DASHSCOPE_API_KEY")
    embedding_key = _env("LNE_EMBEDDING_API_KEY", dashscope_key)
    rerank_key = _env("LNE_RERANK_API_KEY", dashscope_key)
    return RetrievalProviderSettings(
        embedding_api_key=embedding_key,
        embedding_base_url=_env("LNE_EMBEDDING_BASE_URL", _EMBEDDING_BASE_URL),
        embedding_model=_env("LNE_EMBEDDING_MODEL", _EMBEDDING_MODEL),
        embedding_dimension=_int_env(
            "LNE_EMBEDDING_DIMENSION",
            _EMBEDDING_DIMENSION,
            minimum=64,
            maximum=2048,
        ),
        embedding_batch_size=_int_env(
            "LNE_EMBEDDING_BATCH_SIZE",
            10,
            minimum=1,
            maximum=10,
        ),
        vector_store_provider=_env("LNE_VECTOR_STORE_PROVIDER", "zilliz_cloud"),
        zilliz_uri=_env("LNE_ZILLIZ_URI", _env("ZILLIZ_CLOUD_URI")),
        zilliz_token=_env("LNE_ZILLIZ_TOKEN", _env("ZILLIZ_CLOUD_TOKEN")),
        zilliz_collection=_env("LNE_ZILLIZ_COLLECTION", _ZILLIZ_COLLECTION),
        rerank_api_key=rerank_key,
        rerank_endpoint=_env(
            "LNE_RERANK_ENDPOINT",
            _env("LNE_RERANK_BASE_URL", _RERANK_ENDPOINT),
        ),
        rerank_model=_env("LNE_RERANK_MODEL", _RERANK_MODEL),
        rerank_top_n=_int_env("LNE_RERANK_TOP_N", 5, minimum=1, maximum=50),
    )


def get_retrieval_provider_configuration() -> dict[str, Any]:
    """Return a read-only, secret-safe provider configuration report."""

    settings = get_retrieval_provider_settings()
    embedding_configured = bool(settings.embedding_api_key)
    vector_store_configured = bool(settings.zilliz_uri and settings.zilliz_token)
    reranker_configured = bool(settings.rerank_api_key)
    ready_count = sum(
        1
        for flag in (embedding_configured, vector_store_configured, reranker_configured)
        if flag
    )
    return {
        "version": VERSION,
        "mode": "read_only_retrieval_provider_configuration",
        "status": "ready" if ready_count == 3 else "attention",
        "summary": {
            "embedding_provider": "aliyun_bailian",
            "embedding_configured": embedding_configured,
            "vector_store_provider": settings.vector_store_provider,
            "vector_store_configured": vector_store_configured,
            "reranker_provider": "aliyun_bailian",
            "reranker_configured": reranker_configured,
            "ready_count": ready_count,
            "attention_count": 3 - ready_count,
            "plaintext_key_returned": False,
            "writes_artifacts": False,
            "provider_calls": False,
            "default_retrieval_changed": False,
        },
        "providers": {
            "embedding": {
                "provider": "aliyun_bailian",
                "base_url": settings.embedding_base_url,
                "model": settings.embedding_model,
                "dimension": settings.embedding_dimension,
                "batch_size": settings.embedding_batch_size,
                "configured": embedding_configured,
                "masked_key": _mask_secret(settings.embedding_api_key),
                "route": "openai_compatible_embeddings",
            },
            "vector_store": {
                "provider": settings.vector_store_provider,
                "uri_configured": bool(settings.zilliz_uri),
                "token_configured": bool(settings.zilliz_token),
                "configured": vector_store_configured,
                "masked_token": _mask_secret(settings.zilliz_token),
                "collection": settings.zilliz_collection,
                "route": "zilliz_cloud_milvus_client",
            },
            "reranker": {
                "provider": "aliyun_bailian",
                "endpoint": settings.rerank_endpoint,
                "model": settings.rerank_model,
                "top_n": settings.rerank_top_n,
                "configured": reranker_configured,
                "masked_key": _mask_secret(settings.rerank_api_key),
                "route": "dashscope_text_rerank_http",
            },
        },
        "boundaries": [
            "只读返回检索增强 provider 配置，不读取或返回明文凭据。",
            "不创建 embedding 索引，不连接生产向量库写入，不替换 BM25 默认检索。",
            "真实 smoke 只在用户显式调用时执行，mock smoke 不打外网。",
        ],
        "next_steps": [
            "先用 mock smoke 校验本地契约，再填入密钥运行真实 smoke。",
            "真实 embedding/rerank 可用后，再用失败样本做离线对照，不直接改默认检索。",
            "Zilliz Cloud 写入索引前先定义 collection schema、维度、回滚和删除策略。",
        ],
        "warnings": _configuration_warnings(
            embedding_configured=embedding_configured,
            vector_store_configured=vector_store_configured,
            reranker_configured=reranker_configured,
        ),
    }


def test_retrieval_provider_connectivity(*, mock: bool = False) -> dict[str, Any]:
    """Run an explicit retrieval-provider smoke check.

    In mock mode this never calls providers. In real mode failures are returned
    as data instead of raising so HTTP callers do not produce 500s.
    """

    settings = get_retrieval_provider_settings()
    started = time.perf_counter()
    if mock:
        checks = {
            "embedding": _mock_embedding_check(settings),
            "vector_store": _mock_vector_store_check(settings),
            "reranker": _mock_reranker_check(settings),
        }
        mode = "mock"
    else:
        checks = {
            "embedding": _real_embedding_check(settings),
            "vector_store": _real_vector_store_check(settings),
            "reranker": _real_reranker_check(settings),
        }
        mode = "provider"
    available_count = sum(1 for check in checks.values() if check["available"])
    return {
        "version": VERSION,
        "mode": mode,
        "status": "ready" if available_count == 3 else "attention",
        "summary": {
            "check_count": 3,
            "available_count": available_count,
            "attention_count": 3 - available_count,
            "provider_calls": not mock,
            "writes_artifacts": False,
            "default_retrieval_changed": False,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        },
        "checks": checks,
        "boundaries": [
            "smoke 只验证 provider 可达性与返回格式，不保存 embedding 或 rerank 结果。",
            "Zilliz smoke 只尝试连接/列集合，不创建 collection、不写向量。",
        ],
    }


def _configuration_warnings(
    *,
    embedding_configured: bool,
    vector_store_configured: bool,
    reranker_configured: bool,
) -> list[str]:
    warnings: list[str] = []
    if not embedding_configured:
        warnings.append("百炼 text-embedding-v3 未配置，真实 embedding smoke 会跳过。")
    if not vector_store_configured:
        warnings.append("Zilliz Cloud uri/token 未配置，真实向量库 smoke 会跳过。")
    if not reranker_configured:
        warnings.append("百炼 gte-rerank-v2 未配置，真实 rerank smoke 会跳过。")
    return warnings


def _mock_embedding_check(settings: RetrievalProviderSettings) -> dict[str, Any]:
    return {
        "available": True,
        "mode": "mock",
        "provider": "aliyun_bailian",
        "model": settings.embedding_model,
        "dimension": settings.embedding_dimension,
        "sample_count": 2,
        "provider_call": False,
    }


def _mock_vector_store_check(settings: RetrievalProviderSettings) -> dict[str, Any]:
    return {
        "available": True,
        "mode": "mock",
        "provider": settings.vector_store_provider,
        "collection": settings.zilliz_collection,
        "provider_call": False,
        "writes_artifacts": False,
    }


def _mock_reranker_check(settings: RetrievalProviderSettings) -> dict[str, Any]:
    return {
        "available": True,
        "mode": "mock",
        "provider": "aliyun_bailian",
        "model": settings.rerank_model,
        "top_n": min(2, settings.rerank_top_n),
        "provider_call": False,
    }


def _real_embedding_check(settings: RetrievalProviderSettings) -> dict[str, Any]:
    if not settings.embedding_api_key:
        return _unavailable("embedding", "not_configured", settings.embedding_model)
    try:
        client = OpenAI(
            api_key=settings.embedding_api_key,
            base_url=settings.embedding_base_url,
        )
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=["未终章检索增强 smoke", "角色记忆与伏笔召回"],
            dimensions=settings.embedding_dimension,
        )
        vectors = [item.embedding for item in response.data]
        dimensions = len(vectors[0]) if vectors else 0
        return {
            "available": bool(vectors),
            "mode": "provider",
            "provider": "aliyun_bailian",
            "model": settings.embedding_model,
            "dimension": dimensions,
            "sample_count": len(vectors),
            "provider_call": True,
        }
    except Exception as exc:
        return _failure("embedding", settings.embedding_model, exc)


def _real_vector_store_check(settings: RetrievalProviderSettings) -> dict[str, Any]:
    if not settings.zilliz_uri or not settings.zilliz_token:
        return {
            "available": False,
            "mode": "provider",
            "provider": settings.vector_store_provider,
            "reason": "not_configured",
            "collection": settings.zilliz_collection,
            "provider_call": False,
        }
    try:
        pymilvus = importlib.import_module("pymilvus")
        milvus_client = getattr(pymilvus, "MilvusClient")
    except Exception:
        return {
            "available": False,
            "mode": "provider",
            "provider": settings.vector_store_provider,
            "reason": "dependency_missing",
            "dependency": "pymilvus",
            "collection": settings.zilliz_collection,
            "provider_call": False,
        }
    try:
        client = milvus_client(uri=settings.zilliz_uri, token=settings.zilliz_token)
        collections = client.list_collections()
        return {
            "available": True,
            "mode": "provider",
            "provider": settings.vector_store_provider,
            "collection": settings.zilliz_collection,
            "collection_exists": settings.zilliz_collection in set(collections),
            "collection_count": len(collections),
            "provider_call": True,
            "writes_artifacts": False,
        }
    except Exception as exc:
        return _failure("vector_store", settings.vector_store_provider, exc)


def _real_reranker_check(settings: RetrievalProviderSettings) -> dict[str, Any]:
    if not settings.rerank_api_key:
        return _unavailable("reranker", "not_configured", settings.rerank_model)
    try:
        data = _call_dashscope_rerank(
            api_key=settings.rerank_api_key,
            endpoint=settings.rerank_endpoint,
            model=settings.rerank_model,
            query="角色为什么没有服从读者干预",
            documents=[
                "角色会根据人设、记忆和世界规则抵抗不合理命令。",
                "天气变冷后，城外道路结冰。",
                "检索增强用于找回远章节伏笔。",
            ],
            top_n=min(2, settings.rerank_top_n),
        )
        rows = _extract_rerank_rows(data)
        return {
            "available": bool(rows),
            "mode": "provider",
            "provider": "aliyun_bailian",
            "model": settings.rerank_model,
            "result_count": len(rows),
            "provider_call": True,
        }
    except Exception as exc:
        return _failure("reranker", settings.rerank_model, exc)


def _call_dashscope_rerank(
    *,
    api_key: str,
    endpoint: str,
    model: str,
    query: str,
    documents: list[str],
    top_n: int,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "input": {
            "query": query,
            "documents": documents,
        },
        "parameters": {
            "return_documents": True,
            "top_n": top_n,
        },
    }
    req = request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=_HTTP_TIMEOUT_SECONDS) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise RuntimeError("rerank response is not a JSON object")
    return data


def _extract_rerank_rows(data: dict[str, Any]) -> list[Any]:
    output = data.get("output")
    if isinstance(output, dict) and isinstance(output.get("results"), list):
        return list(output["results"])
    if isinstance(data.get("results"), list):
        return list(data["results"])
    if isinstance(data.get("data"), list):
        return list(data["data"])
    return []


def _unavailable(kind: str, reason: str, model: str) -> dict[str, Any]:
    return {
        "available": False,
        "mode": "provider",
        "kind": kind,
        "model": model,
        "reason": reason,
        "provider_call": False,
    }


def _failure(kind: str, label: str, exc: Exception) -> dict[str, Any]:
    return {
        "available": False,
        "mode": "provider",
        "kind": kind,
        "label": label,
        "reason": "connection_failed",
        "error": str(exc),
        "provider_call": True,
    }
