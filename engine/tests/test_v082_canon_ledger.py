"""v0.8.2-A Canon Ledger：导入时生成统一正史账本。"""

from __future__ import annotations

import json

from living_novel_engine.service import import_novel_from_payload


def _chapters(n: int = 4) -> list[dict]:
    return [
        {
            "filename": f"chapter_{i + 1:03d}.md",
            "content": (
                f"第{i + 1}章 正史账本\n"
                f"林凡与林晚舟在第 {i + 1} 章确认退魂铃线索，墨青烟暗中观察。"
            ),
        }
        for i in range(n)
    ]


def _read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class TestCanonLedger:
    def test_import_writes_canon_ledger_with_uniform_fields(self, tmp_path):
        import_novel_from_payload(
            name="ledger-story",
            chapters=_chapters(4),
            mock=True,
            projects_dir=tmp_path,
        )

        ledger_path = tmp_path / "ledger-story" / "memory" / "canon_ledger.jsonl"
        records = _read_jsonl(ledger_path)

        assert records
        required = {
            "id",
            "type",
            "chapter",
            "scene",
            "entities",
            "statement",
            "truth_status",
            "source_ref",
            "confidence",
            "valid_from",
            "valid_until",
        }
        assert required <= set(records[0])
        assert {r["type"] for r in records} >= {"event", "state", "relationship"}
        assert all(r["truth_status"] == "canon" for r in records)
        assert all(str(r["source_ref"]) for r in records)

    def test_memory_manifest_counts_canon_ledger(self, tmp_path):
        import_novel_from_payload(
            name="ledger-manifest",
            chapters=_chapters(3),
            mock=True,
            projects_dir=tmp_path,
        )

        memory_dir = tmp_path / "ledger-manifest" / "memory"
        records = _read_jsonl(memory_dir / "canon_ledger.jsonl")
        manifest = json.loads(
            (memory_dir / "memory_manifest.json").read_text(encoding="utf-8")
        )

        assert manifest["layers"]["canon_ledger"]["path"] == "memory/canon_ledger.jsonl"
        assert manifest["layers"]["canon_ledger"]["count"] == len(records)
