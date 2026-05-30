"""v0.8.4-A Consistency Audit：导入时生成静态一致性审计报告。"""

from __future__ import annotations

import json

from living_novel_engine.service import import_novel_from_payload


def _chapters() -> list[dict]:
    return [
        {
            "filename": "chapter_001.md",
            "content": "重复标题\n林凡发现退魂铃裂痕。",
        },
        {
            "filename": "chapter_003.md",
            "content": "重复标题\n林晚舟记录线索。���????",
        },
        {
            "filename": "chapter_004.md",
            "content": "第四章\n墨青烟暗中观察。",
        },
    ]


class TestConsistencyAudit:
    def test_import_writes_consistency_report(self, tmp_path):
        import_novel_from_payload(
            name="audit-story",
            chapters=_chapters(),
            mock=True,
            long_mode=True,
            projects_dir=tmp_path,
        )

        memory_dir = tmp_path / "audit-story" / "memory"
        report = json.loads(
            (memory_dir / "consistency_report.json").read_text(encoding="utf-8")
        )

        assert report["version"] == "v0.8.4"
        assert report["story_slug"] == "audit-story"
        assert "persona_drift" in report
        assert "timeline_conflicts" in report
        assert "resource_conflicts" in report
        assert "contract_violations" in report
        assert "forgotten_threads" in report
        assert report["summary"]["issue_count"] >= 2
        assert report["repair_suggestions"]

    def test_manifest_counts_consistency_report_issues(self, tmp_path):
        import_novel_from_payload(
            name="audit-manifest",
            chapters=_chapters(),
            mock=True,
            long_mode=True,
            projects_dir=tmp_path,
        )

        memory_dir = tmp_path / "audit-manifest" / "memory"
        report = json.loads(
            (memory_dir / "consistency_report.json").read_text(encoding="utf-8")
        )
        manifest = json.loads(
            (memory_dir / "memory_manifest.json").read_text(encoding="utf-8")
        )

        assert manifest["layers"]["consistency_report"]["path"] == (
            "memory/consistency_report.json"
        )
        assert manifest["layers"]["consistency_report"]["count"] == report["summary"]["issue_count"]
