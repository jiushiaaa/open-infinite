"""Retrieval package — BM25 检索 + 章节距离衰减 + 上下文注入。"""

from living_novel_engine.retrieval.retriever import RetrievedContext, retrieve_context

__all__ = ["RetrievedContext", "retrieve_context"]
