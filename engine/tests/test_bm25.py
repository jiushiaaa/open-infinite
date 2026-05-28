"""Tests for BM25 Lite implementation."""

from living_novel_engine.retrieval.bm25 import BM25Lite, tokenize


class TestTokenize:
    def test_chinese_chars(self):
        tokens = tokenize("赵轩与沈冰月合作")
        assert "赵" in tokens
        assert "轩" in tokens
        assert "沈" in tokens

    def test_english_words(self):
        tokens = tokenize("hello world test")
        assert tokens == ["hello", "world", "test"]

    def test_mixed(self):
        tokens = tokenize("赵轩 is a hero")
        assert "赵" in tokens
        assert "轩" in tokens
        assert "is" in tokens
        assert "hero" in tokens

    def test_empty(self):
        assert tokenize("") == []
        assert tokenize("   ") == []


class TestBM25Lite:
    def test_basic_ranking(self):
        docs = [
            "赵轩与沈冰月在归云斋合作",
            "韩无归布置灵脉引导阵",
            "风鸣铃从苍澜派失窃三个月",
        ]
        ids = ["doc_a", "doc_b", "doc_c"]
        bm25 = BM25Lite(docs, ids)
        results = bm25.score("赵轩 沈冰月", top_k=3)
        assert len(results) > 0
        assert results[0][0] == "doc_a"

    def test_top_k_limit(self):
        docs = [f"文档 {i}" for i in range(20)]
        ids = [f"id_{i}" for i in range(20)]
        bm25 = BM25Lite(docs, ids)
        results = bm25.score("文档", top_k=5)
        assert len(results) <= 5

    def test_empty_corpus(self):
        bm25 = BM25Lite([], [])
        results = bm25.score("任何查询")
        assert results == []

    def test_no_match(self):
        docs = ["苹果 橘子 香蕉"]
        ids = ["fruits"]
        bm25 = BM25Lite(docs, ids)
        results = bm25.score("飞机 火箭")
        assert results == []

    def test_empty_query(self):
        docs = ["赵轩与沈冰月合作"]
        ids = ["doc"]
        bm25 = BM25Lite(docs, ids)
        results = bm25.score("")
        assert results == []

    def test_single_doc(self):
        docs = ["韩无归十二年前被逐出苍澜派"]
        ids = ["fact_1"]
        bm25 = BM25Lite(docs, ids)
        results = bm25.score("韩无归 苍澜派")
        assert len(results) == 1
        assert results[0][0] == "fact_1"
        assert results[0][1] > 0
