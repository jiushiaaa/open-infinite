from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from living_novel_engine.models import Intervention
from living_novel_engine.models.events import SimulationResult


def _outputs_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "outputs"


@dataclass
class RunOutput:
    run_id: str
    run_dir: Path
    intervention: Intervention
    results: list[SimulationResult] = field(default_factory=list)


def write_run_output(
    intervention: Intervention,
    results: list[SimulationResult],
    *,
    run_id: str | None = None,
) -> RunOutput:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = run_id or f"run_{ts}_{uuid.uuid4().hex[:6]}"
    run_dir = _outputs_dir() / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    intervention_payload = intervention.model_dump(mode="json")
    if intervention.contract_audit:
        intervention_payload["contract_audit"] = intervention.contract_audit.model_dump()

    with open(run_dir / "intervention.json", "w", encoding="utf-8") as f:
        json.dump(intervention_payload, f, ensure_ascii=False, indent=2, default=str)

    for result in results:
        branch_dir = run_dir / result.worldline_id
        branch_dir.mkdir(exist_ok=True)

        snapshot = result.state_snapshot or result.final_scene_state

        with open(branch_dir / "events.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "worldline_id": result.worldline_id,
                    "theme": result.theme,
                    "branch_seed": result.branch_seed,
                    "termination_reason": result.termination_reason,
                    "accepted_events": [e.model_dump() for e in result.accepted_events],
                    "state_deltas": [d.model_dump() for d in result.state_deltas],
                    "final_scene_state": result.final_scene_state,
                },
                f,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

        (branch_dir / "summary.md").write_text(result.summary_text, encoding="utf-8")
        (branch_dir / "chapter.md").write_text(result.chapter_text, encoding="utf-8")

        with open(branch_dir / "state_snapshot.json", "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2, default=str)

    compare_md = _build_compare_md(results)
    (run_dir / "compare.md").write_text(compare_md, encoding="utf-8")

    return RunOutput(run_id=run_id, run_dir=run_dir, intervention=intervention, results=results)


def _build_compare_md(results: list[SimulationResult]) -> str:
    lines = ["# 世界线对比\n", f"生成时间: {datetime.now().isoformat()}\n"]
    lines.append("| 世界线 | 主题 | 种子 | 终止原因 | 下一章钩子 |")
    lines.append("| --- | --- | --- | --- | --- |")
    for r in results:
        snap = r.state_snapshot or {}
        hook = str(snap.get("next_chapter_hook", ""))[:80]
        lines.append(
            f"| {r.worldline_id} | {r.theme} | {r.branch_seed} | {r.termination_reason} | {hook} |"
        )
    lines.append("\n## 分歧要点\n")
    lines.append("- 固定三分支：相信干预 / 半信半疑调查 / 拒绝干预·反弹\n")
    for r in results:
        lines.append(f"### {r.worldline_id}: {r.theme}\n")
        lines.append(r.summary_text + "\n")
        snap = r.state_snapshot or {}
        if snap.get("next_chapter_hook"):
            lines.append(f"**钩子**: {snap['next_chapter_hook']}\n")
    return "\n".join(lines)


def load_run_for_compare(run_path: str | Path) -> str:
    run_dir = Path(run_path)
    compare_file = run_dir / "compare.md"
    if compare_file.exists():
        return compare_file.read_text(encoding="utf-8")
    results = []
    for branch in sorted(run_dir.glob("branch_*")):
        summary = (branch / "summary.md").read_text(encoding="utf-8")
        results.append(f"## {branch.name}\n\n{summary}\n")
    return "\n".join(results) if results else "未找到可对比的世界线输出"
