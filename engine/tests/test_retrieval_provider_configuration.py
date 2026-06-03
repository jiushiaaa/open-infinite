"""Retrieval provider configuration smoke contracts."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import Mock

import living_novel_engine.service as service
from living_novel_engine.service import retrieval_provider_configuration as rpc


def _clear_provider_env(monkeypatch) -> None:
    monkeypatch.setattr(rpc, "_load_env_file", lambda: None)
    for key in (
        "LNE_EMBEDDING_API_KEY",
        "LNE_EMBEDDING_BASE_URL",
        "LNE_EMBEDDING_MODEL",
        "LNE_EMBEDDING_DIMENSION",
        "LNE_VECTOR_STORE_PROVIDER",
        "LNE_ZILLIZ_URI",
        "LNE_ZILLIZ_TOKEN",
        "LNE_ZILLIZ_COLLECTION",
        "LNE_RERANK_API_KEY",
        "LNE_RERANK_ENDPOINT",
        "LNE_RERANK_MODEL",
        "DASHSCOPE_API_KEY",
        "ZILLIZ_CLOUD_URI",
        "ZILLIZ_CLOUD_TOKEN",
    ):
        monkeypatch.delenv(key, raising=False)


def test_retrieval_provider_configuration_defaults_are_secret_safe(monkeypatch):
    _clear_provider_env(monkeypatch)

    report = service.get_retrieval_provider_configuration()
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "retrieval-provider-configuration-mvp"
    assert report["mode"] == "read_only_retrieval_provider_configuration"
    assert report["summary"]["embedding_provider"] == "aliyun_bailian"
    assert report["summary"]["embedding_configured"] is False
    assert report["summary"]["vector_store_provider"] == "zilliz_cloud"
    assert report["summary"]["vector_store_configured"] is False
    assert report["summary"]["reranker_provider"] == "aliyun_bailian"
    assert report["summary"]["reranker_configured"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["summary"]["default_retrieval_changed"] is False
    assert report["providers"]["embedding"]["model"] == "text-embedding-v3"
    assert report["providers"]["embedding"]["base_url"].endswith("/compatible-mode/v1")
    assert report["providers"]["embedding"]["dimension"] == 1024
    assert report["providers"]["vector_store"]["provider"] == "zilliz_cloud"
    assert report["providers"]["reranker"]["model"] == "gte-rerank-v2"
    assert report["providers"]["reranker"]["endpoint"].endswith(
        "/services/rerank/text-rerank/text-rerank"
    )
    assert report["providers"]["reranker"]["route"] == "dashscope_text_rerank_http"
    assert "API_KEY" not in text


def test_retrieval_provider_configuration_masks_configured_secrets(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("LNE_EMBEDDING_API_KEY", "emb-secret-123456")
    monkeypatch.setenv("LNE_ZILLIZ_URI", "https://example.zillizcloud.com:19530")
    monkeypatch.setenv("LNE_ZILLIZ_TOKEN", "zilliz-token-abcdef")
    monkeypatch.setenv("LNE_ZILLIZ_COLLECTION", "unfinale_memory")
    monkeypatch.setenv("LNE_RERANK_API_KEY", "rerank-secret-778899")

    report = service.get_retrieval_provider_configuration()
    text = json.dumps(report, ensure_ascii=False)

    assert report["summary"]["embedding_configured"] is True
    assert report["summary"]["vector_store_configured"] is True
    assert report["summary"]["reranker_configured"] is True
    assert report["providers"]["embedding"]["masked_key"].endswith("3456")
    assert report["providers"]["vector_store"]["masked_token"].endswith("cdef")
    assert report["providers"]["reranker"]["masked_key"].endswith("8899")
    assert "emb-secret" not in text
    assert "zilliz-token" not in text
    assert "rerank-secret" not in text


def test_retrieval_provider_smoke_mock_is_local_only(monkeypatch):
    _clear_provider_env(monkeypatch)

    smoke = service.test_retrieval_provider_connectivity(mock=True)

    assert smoke["mode"] == "mock"
    assert smoke["summary"]["provider_calls"] is False
    assert smoke["summary"]["writes_artifacts"] is False
    assert smoke["checks"]["embedding"]["available"] is True
    assert smoke["checks"]["embedding"]["model"] == "text-embedding-v3"
    assert smoke["checks"]["embedding"]["dimension"] == 1024
    assert smoke["checks"]["vector_store"]["available"] is True
    assert smoke["checks"]["vector_store"]["provider"] == "zilliz_cloud"
    assert smoke["checks"]["reranker"]["available"] is True
    assert smoke["checks"]["reranker"]["model"] == "gte-rerank-v2"


def test_reranker_smoke_uses_dashscope_gte_rerank_v2_payload(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("LNE_RERANK_API_KEY", "rerank-secret-778899")

    captured: dict[str, object] = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps(
                {
                    "output": {
                        "results": [
                            {"index": 0, "relevance_score": 0.91},
                            {"index": 2, "relevance_score": 0.42},
                        ]
                    }
                }
            ).encode("utf-8")

    def fake_urlopen(request, timeout=0):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(rpc.request, "urlopen", fake_urlopen)

    smoke = service.test_retrieval_provider_connectivity(mock=False)

    body = captured["body"]
    assert smoke["checks"]["reranker"]["available"] is True
    assert smoke["checks"]["reranker"]["model"] == "gte-rerank-v2"
    assert body["model"] == "gte-rerank-v2"
    assert body["input"]["query"] == "角色为什么没有服从读者干预"
    assert len(body["input"]["documents"]) == 3
    assert body["parameters"]["return_documents"] is True
    assert body["parameters"]["top_n"] == 2
    assert captured["url"].endswith("/services/rerank/text-rerank/text-rerank")


def test_vector_store_smoke_uses_zilliz_milvus_client(monkeypatch):
    _clear_provider_env(monkeypatch)
    monkeypatch.setenv("LNE_ZILLIZ_URI", "https://example.zillizcloud.com:19530")
    monkeypatch.setenv("LNE_ZILLIZ_TOKEN", "zilliz-token-abcdef")
    monkeypatch.setenv("LNE_ZILLIZ_COLLECTION", "unfinale_memory")

    fake_client = Mock()
    fake_client.list_collections.return_value = ["unfinale_memory"]
    fake_module = SimpleNamespace(MilvusClient=Mock(return_value=fake_client))

    def fake_import(name, *args, **kwargs):
        if name == "pymilvus":
            return fake_module
        return __import__(name, *args, **kwargs)

    monkeypatch.setattr(rpc.importlib, "import_module", fake_import)

    smoke = service.test_retrieval_provider_connectivity(mock=False)

    assert smoke["checks"]["vector_store"]["available"] is True
    assert smoke["checks"]["vector_store"]["collection_exists"] is True
    fake_module.MilvusClient.assert_called_once_with(
        uri="https://example.zillizcloud.com:19530",
        token="zilliz-token-abcdef",
    )
