"""v0.8+ Discourse-aware Narrator-A：分支叙事诊断 artifact。"""

from __future__ import annotations

import json

from living_novel_engine.narrative_diagnostics import analyze_narrative
from living_novel_engine.service import run_intervention


def test_analyze_narrative_flags_flat_short_text():
    report = analyze_narrative("林凡走了。林凡想了想。事情结束。", branch_id="branch_a")

    assert report["version"] == "v0.8-narrative-diagnostics-a"
    assert report["branch_id"] == "branch_a"
    assert report["metrics"]["char_count"] > 0
    assert report["warnings"]
    assert report["suggestions"]
    assert report["tension_curve"]


def test_run_intervention_writes_narrative_diagnostics(tmp_path, monkeypatch):
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    monkeypatch.setenv("LNE_OUTPUTS_DIR", str(outputs))
    monkeypatch.setenv("LLM_API_KEY", "")

    result = run_intervention(
        story_slug="tianhuang-night",
        target="lin_wan_zhou",
        content="告诉林晚舟今夜不要去竹林",
        mock=True,
        rounds=1,
    )

    branch = result.branch_ids[0]
    path = outputs / result.run_id / branch / "narrative_diagnostics.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["kind"] == "narrative_diagnostics"
    assert data["branch_id"] == branch
    assert "pacing" in data["metrics"]
    assert isinstance(data["suggestions"], list)
