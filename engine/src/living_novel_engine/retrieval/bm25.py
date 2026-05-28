"""BM25 Lite — 零依赖轻量关键词检索。"""

from __future__ import annotations

import math
import re
from collections import Counter

_TOKEN_RE = re.compile(r"[\u4e00-\u9fff]|[a-zA-Z]+|\d+")


def tokenize(text: str) -> list[str]:
    """中文按字、英文/数字按词切分。"""
    return [m.group().lower() for m in _TOKEN_RE.finditer(text)]


class BM25Lite:
    """Okapi BM25 轻量实现，支持中文按字分词。"""

    def __init__(
        self,
        documents: list[str],
        doc_ids: list[str],
        *,
        k1: float = 1.5,
        b: float = 0.75,
    ):
        assert len(documents) == len(doc_ids)
        self.doc_ids = doc_ids
        self.k1 = k1
        self.b = b
        self.n = len(documents)

        self._doc_lens: list[int] = []
        self._doc_tfs: list[Counter[str]] = []
        self._df: Counter[str] = Counter()

        for doc in documents:
            tokens = tokenize(doc)
            tf = Counter(tokens)
            self._doc_tfs.append(tf)
            self._doc_lens.append(len(tokens))
            for term in tf:
                self._df[term] += 1

        self._avgdl = sum(self._doc_lens) / self.n if self.n else 1.0

    def score(self, query: str, top_k: int = 8) -> list[tuple[str, float]]:
        """返回 (doc_id, score) 列表，按 score 降序，取 top_k。"""
        if self.n == 0:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores: list[float] = [0.0] * self.n
        for term in query_tokens:
            df = self._df.get(term, 0)
            if df == 0:
                continue
            idf = math.log((self.n - df + 0.5) / (df + 0.5) + 1.0)
            for i in range(self.n):
                tf = self._doc_tfs[i].get(term, 0)
                if tf == 0:
                    continue
                dl = self._doc_lens[i]
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * dl / self._avgdl)
                scores[i] += idf * numerator / denominator

        ranked = sorted(
            ((self.doc_ids[i], scores[i]) for i in range(self.n) if scores[i] > 0),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:top_k]
