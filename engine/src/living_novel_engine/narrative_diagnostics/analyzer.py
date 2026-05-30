from __future__ import annotations

import re

VERSION = "v0.8-narrative-diagnostics-a"

_SENTENCE_RE = re.compile(r"[^。！？!?；;]+[。！？!?；;]?")
_TENSION_MARKERS = (
    "忽然", "却", "但", "危", "杀", "血", "怒", "惊", "疑", "断", "碎", "逼近", "封印", "背叛",
)
_TURNING_MARKERS = ("忽然", "却", "但", "转身", "终于", "原来", "竟", "反而")
_DIALOGUE_MARKERS = ("“", "”", "：", "\"")


def analyze_narrative(chapter_text: str, *, branch_id: str = "") -> dict:
    text = chapter_text or ""
    sentences = [s.strip() for s in _SENTENCE_RE.findall(text) if s.strip()]
    char_count = len(text)
    paragraph_count = max(1, len([p for p in text.splitlines() if p.strip()]))
    dialogue_count = sum(text.count(m) for m in _DIALOGUE_MARKERS)
    turning_count = sum(text.count(m) for m in _TURNING_MARKERS)
    tension_curve = _tension_curve(sentences)
    warnings: list[str] = []
    suggestions: list[str] = []

    if char_count < 300:
        warnings.append("正文偏短，可能不足以形成完整场景推进。")
        suggestions.append("补足目标、阻碍、转折和余波四段。")
    if dialogue_count == 0:
        warnings.append("缺少明显对话或角色声音，人物行动可能显得平。")
        suggestions.append("加入至少一段角色之间的直接对话或内心反应。")
    if turning_count == 0:
        warnings.append("缺少明显转折标记，分支可能过早收束。")
        suggestions.append("加入一次信息反转、阻碍升级或代价揭示。")
    max_tension = max((p["tension"] for p in tension_curve), default=0.0)
    if max_tension < 0.35:
        warnings.append("张力曲线偏低，冲突或危险信号不足。")
        suggestions.append("让角色面对一个必须选择的代价，而不是顺滑完成目标。")

    return {
        "version": VERSION,
        "kind": "narrative_diagnostics",
        "branch_id": branch_id,
        "metrics": {
            "char_count": char_count,
            "sentence_count": len(sentences),
            "paragraph_count": paragraph_count,
            "dialogue_marker_count": dialogue_count,
            "turning_marker_count": turning_count,
            "pacing": round(char_count / paragraph_count, 2),
        },
        "tension_curve": tension_curve,
        "warnings": warnings,
        "suggestions": list(dict.fromkeys(suggestions)),
    }


def _tension_curve(sentences: list[str]) -> list[dict]:
    if not sentences:
        return [{"index": 1, "tension": 0.0}]
    bucket_size = max(1, len(sentences) // 5)
    buckets = [
        sentences[i : i + bucket_size] for i in range(0, len(sentences), bucket_size)
    ][:5]
    curve: list[dict] = []
    for idx, bucket in enumerate(buckets, start=1):
        joined = "".join(bucket)
        marker_hits = sum(joined.count(m) for m in _TENSION_MARKERS)
        density = min(1.0, marker_hits / max(1, len(bucket) * 2))
        length_factor = min(0.35, len(joined) / 1200)
        curve.append({"index": idx, "tension": round(min(1.0, density + length_factor), 3)})
    return curve
