"""Real retrieval pipeline: embedding -> Zilliz -> rerank."""

from __future__ import annotations

import json
from types import SimpleNamespace

from test_context_retrieval import _make_project

from living_novel_engine import runtime_memory
from living_novel_engine.runtime_memory import build_runtime_memory_context
from living_novel_engine.service import (
    build_vector_retrieval_index,
    retrieve_hybrid_vector_context,
)
from living_novel_engine.service import vector_retrieval_pipeline as pipeline


class FakeMilvusClient:
    def __init__(self):
        self.collections: set[str] = set()
        self.rows: list[dict] = []
        self.created: list[dict] = []
        self.deleted_ids: list[int] = []

    def has_collection(self, collection_name: str) -> bool:
        return collection_name in self.collections

    def create_collection(self, **kwargs):
        self.collections.add(kwargs["collection_name"])
        self.created.append(kwargs)

    def delete(self, collection_name: str, ids: list[int]):
        self.deleted_ids.extend(ids)
        self.rows = [row for row in self.rows if row["id"] not in set(ids)]

    def insert(self, collection_name: str, data: list[dict]):
        self.collections.add(collection_name)
        self.rows.extend(data)
        return {"insert_count": len(data)}

    def search(self, collection_name: str, data: list[list[float]], **kwargs):
        limit = int(kwargs.get("limit") or 10)
        hits = [
            {
                "id": row["id"],
                "distance": 0.92 - index * 0.05,
                "entity": row,
            }
            for index, row in enumerate(self.rows[:limit])
        ]
        return [hits]


def _configured_env(monkeypatch):
    monkeypatch.setattr(pipeline.rpc, "_load_env_file", lambda: None)
    monkeypatch.setenv("DASHSCOPE_API_KEY", "dashscope-secret-123456")
    monkeypatch.setenv("LNE_ZILLIZ_URI", "https://example.zillizcloud.com")
    monkeypatch.setenv("LNE_ZILLIZ_TOKEN", "user:password-secret")
    monkeypatch.setenv("LNE_ZILLIZ_COLLECTION", "unfinale_memory")


def _make_resolvable_project(tmp_path):
    project = _make_project(tmp_path)
    (project / "world.yaml").write_text(
        "title: 测试故事\nsource_type: imported\n",
        encoding="utf-8",
    )
    return project


def _fake_clients(monkeypatch, fake: FakeMilvusClient):
    monkeypatch.setattr(
        pipeline,
        "_embed_texts",
        lambda texts, settings: [
            [1.0 if i == 0 else 0.0 for i in range(settings.embedding_dimension)]
            for _ in texts
        ],
    )
    monkeypatch.setattr(pipeline, "_new_milvus_client", lambda settings: fake)

    def fake_rerank(query, items, settings):
        reranked = list(reversed(items))
        for index, item in enumerate(reranked):
            item["rerank_score"] = round(0.95 - index * 0.1, 4)
            path = str(item.get("retrieval_path") or "")
            if path == "hybrid":
                item["retrieval_path"] = "hybrid_rerank"
            elif path == "vector":
                item["retrieval_path"] = "vector_rerank"
            elif path == "bm25":
                item["retrieval_path"] = "bm25_rerank"
        return reranked

    monkeypatch.setattr(pipeline, "_rerank_items", fake_rerank)


def test_vector_index_writes_corpus_documents_to_zilliz(monkeypatch, tmp_path):
    project = _make_resolvable_project(tmp_path)
    fake = FakeMilvusClient()
    _configured_env(monkeypatch)
    _fake_clients(monkeypatch, fake)

    report = build_vector_retrieval_index(
        "test-project",
        projects_dir=tmp_path,
        refresh=True,
    )
    text = json.dumps(report, ensure_ascii=False)

    assert report["version"] == "vector-retrieval-pipeline-mvp"
    assert report["mode"] == "write_vector_retrieval_index"
    assert report["status"] == "ready"
    assert report["summary"]["document_count"] > 0
    assert report["summary"]["indexed_count"] == report["summary"]["document_count"]
    assert report["summary"]["writes_vector_store"] is True
    assert fake.created[0]["dimension"] == 1024
    assert fake.rows
    assert any(row["doc_id"] == "canon_ledger:canon_000001" for row in fake.rows)
    assert all(isinstance(row["id"], int) for row in fake.rows)
    assert "dashscope-secret" not in text
    assert "password-secret" not in text
    assert project.exists()


def test_hybrid_vector_retrieval_uses_vector_hits_and_reranker(monkeypatch, tmp_path):
    _make_resolvable_project(tmp_path)
    fake = FakeMilvusClient()
    _configured_env(monkeypatch)
    _fake_clients(monkeypatch, fake)
    build_vector_retrieval_index("test-project", projects_dir=tmp_path)

    ctx = retrieve_hybrid_vector_context(
        tmp_path / "test-project",
        "退魂铃在哪里响过",
        current_chapter=3,
        top_k=3,
    )
    artifact = ctx.to_artifact()

    assert artifact["retrieval_mode"] == "hybrid_vector_rerank"
    assert artifact["provider"]["vector_store"] == "zilliz_cloud"
    assert artifact["provider"]["reranker_model"] == "gte-rerank-v2"
    assert artifact["items"]
    assert any(
        item["retrieval_path"] in {"vector_rerank", "hybrid_rerank"}
        for item in artifact["items"]
    )
    assert any(item["source"] == "canon_ledger" for item in artifact["items"])
    assert "【向量检索与重排结果】" in ctx.as_prompt_block()


def test_runtime_memory_uses_hybrid_vector_only_when_opted_in(monkeypatch, tmp_path):
    _make_resolvable_project(tmp_path)
    monkeypatch.setenv("LNE_RETRIEVAL_STRATEGY", "hybrid_vector")

    def fake_hybrid(project_dir, query, *, current_chapter=1, top_k=8):
        return SimpleNamespace(
            items=[
                {
                    "id": "canon_ledger:canon_000001",
                    "source": "canon_ledger",
                    "retrieval_path": "vector_rerank",
                    "text": "墨青烟确认退魂铃曾在听雨轩响过。",
                }
            ],
            as_prompt_block=lambda: "【向量检索与重排结果】\n- 墨青烟确认退魂铃曾在听雨轩响过。",
            to_artifact=lambda: {
                "retrieval_mode": "hybrid_vector_rerank",
                "items": [
                    {
                        "id": "canon_ledger:canon_000001",
                        "source": "canon_ledger",
                        "retrieval_path": "vector_rerank",
                        "text": "墨青烟确认退魂铃曾在听雨轩响过。",
                    }
                ],
            },
        )

    monkeypatch.setattr(runtime_memory, "_retrieve_hybrid_vector_context", fake_hybrid)

    ctx = build_runtime_memory_context(
        tmp_path / "test-project",
        "退魂铃在哪里响过",
        current_chapter=3,
    )
    artifact = ctx.to_artifact()

    assert artifact["retrieval"]["retrieval_mode"] == "hybrid_vector_rerank"
    assert "vector_retrieval" in artifact["consumed_layers"]
    assert "【向量检索与重排结果】" in artifact["prompt_block"]
