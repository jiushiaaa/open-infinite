"""Reader Panel / Adversarial Revision Lab MVP：确定性读者评审。"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir
from living_novel_engine.browser.validators import safe_id

VERSION = "reader-panel-mvp"

_SENTENCE_RE = re.compile(r"[^。！？!?；;\n]+[。！？!?；;]?")
_QUOTE_RE = re.compile(r"[“\"]([^”\"]+)[”\"]")
_EXPLANATION_MARKERS = (
    "解释",
    "原因是",
    "也就是说",
    "换句话说",
    "这是因为",
    "意味着",
    "显然",
    "其实",
)
_TENSION_MARKERS = (
    "忽然",
    "却",
    "但",
    "危",
    "杀",
    "血",
    "怒",
    "惊",
    "疑",
    "断",
    "碎",
    "逼近",
    "背叛",
    "代价",
    "失败",
    "阻碍",
)


class ReaderPanelRequestError(ValueError):
    """Invalid reader panel request, mapped to HTTP 400."""


def get_reader_panel(
    run_id: str,
    branch_id: str,
    *,
    outputs_root: Path | None = None,
) -> dict[str, Any]:
    """Return a deterministic reader/revision report for one branch.

    This MVP does not call LLMs, write artifacts, or mutate branch state. It is
    intentionally mockable and stable so future LLM reader panels can be judged
    against the same baseline issue ids.
    """

    rid = _safe_id(run_id, "run_id")
    bid = _safe_id(branch_id, "branch_id")
    root = outputs_root or outputs_dir()
    run_dir = root / rid
    if not run_dir.is_dir():
        raise FileNotFoundError(f"运行不存在: {rid}")
    branch_dir = run_dir / bid
    if not branch_dir.is_dir():
        raise FileNotFoundError(f"分支不存在: {rid}/{bid}")

    chapter_status, chapter_text = _read_chapter(branch_dir / "chapter.md")
    diagnostics_status, diagnostics = _read_json_status(
        branch_dir / "narrative_diagnostics.json"
    )
    judgement_status, judgement = _read_json_status(
        branch_dir / "worldline_judgement.json"
    )
    warnings = _artifact_warnings(
        diagnostics_status=diagnostics_status,
        judgement_status=judgement_status,
    )

    issues = (
        _detect_issues(
            chapter_text,
            diagnostics=diagnostics,
            judgement=judgement,
        )
        if chapter_status == "ready"
        else []
    )
    if chapter_status != "ready":
        warnings.append(
            "chapter.md 缺失或无法读取，读者评审只能返回阻塞状态。"
        )
    personas = _personas(issues)
    revision_briefs = [_brief_from_issue(issue) for issue in issues]
    status = (
        "blocked"
        if chapter_status != "ready"
        else "attention"
        if issues or warnings
        else "ready"
    )

    return {
        "version": VERSION,
        "mode": "deterministic_reader_panel",
        "status": status,
        "run_id": rid,
        "branch_id": bid,
        "summary": {
            "issue_count": len(issues),
            "persona_count": len(personas),
            "revision_brief_count": len(revision_briefs),
            "writes_artifacts": False,
            "external_services_required": False,
            "llm_required": False,
        },
        "personas": personas,
        "issues": issues,
        "revision_briefs": revision_briefs,
        "warnings": warnings,
        "boundaries": [
            "只读检查 chapter.md、narrative_diagnostics.json、worldline_judgement.json。",
            "不调用真实 LLM，不写 revision artifact，不改变 chapter.md。",
            "建议用于人工修订或后续 opt-in 改写，不自动覆盖正文。",
        ],
        "next_steps": _next_steps(status),
    }


def _safe_id(value: str, label: str) -> str:
    checked = safe_id(str(value or ""))
    if checked is None:
        raise ReaderPanelRequestError(f"invalid {label}")
    return checked


def _read_chapter(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "missing", ""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "damaged", ""
    return ("ready", text) if text.strip() else ("missing", "")


def _read_json_status(path: Path) -> tuple[str, dict[str, Any]]:
    if not path.exists():
        return "missing", {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "damaged", {}
    return ("ready", data) if isinstance(data, dict) else ("damaged", {})


def _artifact_warnings(
    *,
    diagnostics_status: str,
    judgement_status: str,
) -> list[str]:
    warnings: list[str] = []
    if diagnostics_status == "damaged":
        warnings.append("narrative_diagnostics.json 损坏，已跳过诊断信号。")
    if judgement_status == "damaged":
        warnings.append("worldline_judgement.json 损坏，已跳过评审信号。")
    return warnings


def _detect_issues(
    text: str,
    *,
    diagnostics: dict[str, Any],
    judgement: dict[str, Any],
) -> list[dict[str, Any]]:
    candidates = [
        _over_explanation_issue(text),
        _three_part_stack_issue(text),
        _repeated_ending_issue(text),
        _same_voice_dialogue_issue(text),
        _flat_pacing_issue(text, diagnostics=diagnostics, judgement=judgement),
    ]
    return [issue for issue in candidates if issue is not None]


def _over_explanation_issue(text: str) -> dict[str, Any] | None:
    hits = [marker for marker in _EXPLANATION_MARKERS for _ in range(text.count(marker))]
    if len(hits) < 3:
        return None
    evidence = _sentences_with(text, _EXPLANATION_MARKERS)[:3]
    return _issue(
        issue_id="over_explanation",
        label="过度解释",
        severity="high" if len(hits) >= 5 else "medium",
        evidence=evidence,
        persona_ids=["impatient_reader", "line_editor"],
        revision_brief="删掉重复因果说明，只保留角色当下能感知到的一处证据，把结论留给动作或对话承接。",
    )


def _three_part_stack_issue(text: str) -> dict[str, Any] | None:
    marker_groups = (("首先", "然后", "最后"), ("第一", "第二", "第三"), ("其一", "其二", "其三"))
    matched = next((group for group in marker_groups if all(m in text for m in group)), None)
    if not matched:
        return None
    evidence = _sentences_with(text, matched)[:3]
    return _issue(
        issue_id="three_part_stack",
        label="三段式堆叠",
        severity="medium",
        evidence=evidence,
        persona_ids=["impatient_reader", "pacing_reader"],
        revision_brief="拆掉“首先/然后/最后”的说明梯子，改成一个目标受阻、一个角色选择、一个新代价。",
    )


def _repeated_ending_issue(text: str) -> dict[str, Any] | None:
    sentences = _sentences(text)
    tails = [
        _tail_key(sentence)
        for sentence in sentences
        if len(_tail_key(sentence)) >= 4
    ]
    repeated = [tail for tail, count in Counter(tails).items() if count >= 2]
    if not repeated:
        return None
    tail = repeated[0]
    evidence = [sentence for sentence in sentences if _tail_key(sentence) == tail][:3]
    return _issue(
        issue_id="repeated_ending",
        label="重复结尾",
        severity="medium",
        evidence=evidence,
        persona_ids=["line_editor", "pacing_reader"],
        revision_brief="删掉重复收束句，让第二个结尾转成未解决风险、反问或下一章钩子。",
    )


def _same_voice_dialogue_issue(text: str) -> dict[str, Any] | None:
    quotes = [_normalize_dialogue(q) for q in _QUOTE_RE.findall(text)]
    repeated = [quote for quote, count in Counter(quotes).items() if quote and count >= 2]
    if not repeated:
        return None
    phrase = repeated[0]
    evidence = [f"“{q}”" for q in _QUOTE_RE.findall(text) if _normalize_dialogue(q) == phrase][:3]
    return _issue(
        issue_id="same_voice_dialogue",
        label="对话同声",
        severity="high" if len(evidence) >= 3 else "medium",
        evidence=evidence,
        persona_ids=["line_editor", "continuity_reader"],
        revision_brief="保留一个角色说出直白判断，其他角色改用动作、隐瞒、反问或带个人立场的短句。",
    )


def _flat_pacing_issue(
    text: str,
    *,
    diagnostics: dict[str, Any],
    judgement: dict[str, Any],
) -> dict[str, Any] | None:
    marker_count = sum(text.count(marker) for marker in _TENSION_MARKERS)
    diagnostic_warning = any(
        "张力" in str(item) or "冲突" in str(item)
        for item in diagnostics.get("warnings", [])
        if isinstance(diagnostics.get("warnings"), list)
    )
    scores = judgement.get("scores") if isinstance(judgement.get("scores"), dict) else {}
    low_tension = _num(scores.get("tension")) < 0.4 if scores else False
    low_anti_slop = _num(scores.get("anti_slop")) < 0.5 if scores else False
    if marker_count > 2 and not diagnostic_warning and not low_tension:
        return None
    evidence = []
    if diagnostic_warning:
        evidence.append("叙事诊断提示张力或冲突不足。")
    if low_tension:
        evidence.append(f"世界线评审张力 {scores.get('tension')}。")
    if low_anti_slop:
        evidence.append(f"世界线评审反水文 {scores.get('anti_slop')}。")
    if not evidence:
        evidence = ["正文中阻碍、代价、反转等张力信号偏少。"]
    return _issue(
        issue_id="flat_pacing",
        label="节奏过平",
        severity="medium",
        evidence=evidence,
        persona_ids=["impatient_reader", "pacing_reader"],
        revision_brief="新增一个立即阻碍或代价，把“顺利等待”改成必须选择的压力点，结尾保留未解决风险。",
    )


def _issue(
    *,
    issue_id: str,
    label: str,
    severity: str,
    evidence: list[str],
    persona_ids: list[str],
    revision_brief: str,
) -> dict[str, Any]:
    return {
        "id": issue_id,
        "label": label,
        "severity": severity,
        "severity_label": {"low": "轻微", "medium": "中等", "high": "高"}.get(
            severity,
            severity,
        ),
        "evidence": evidence,
        "persona_ids": persona_ids,
        "revision_brief": revision_brief,
    }


def _personas(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    issue_ids = {issue["id"] for issue in issues}
    specs = [
        (
            "impatient_reader",
            "急性子读者",
            "只看追读压力和信息密度。",
            {"over_explanation", "three_part_stack", "flat_pacing"},
        ),
        (
            "line_editor",
            "句线编辑",
            "盯重复句、口癖和可删字。",
            {"over_explanation", "repeated_ending", "same_voice_dialogue"},
        ),
        (
            "continuity_reader",
            "连续性读者",
            "关心角色声音和事实是否能接上。",
            {"same_voice_dialogue"},
        ),
        (
            "pacing_reader",
            "节奏读者",
            "关心段落推进、转折和收束钩子。",
            {"three_part_stack", "repeated_ending", "flat_pacing"},
        ),
    ]
    result: list[dict[str, Any]] = []
    for persona_id, label, focus, owned in specs:
        matched = sorted(issue_ids & owned)
        result.append(
            {
                "id": persona_id,
                "label": label,
                "focus": focus,
                "status": "attention" if matched else "ready",
                "issue_ids": matched,
                "verdict": (
                    f"命中 {len(matched)} 个修订点。"
                    if matched
                    else "当前没有命中该视角的明显问题。"
                ),
            }
        )
    return result


def _brief_from_issue(issue: dict[str, Any]) -> dict[str, Any]:
    return {
        "issue_id": issue["id"],
        "label": issue["label"],
        "severity": issue["severity"],
        "revision_brief": issue["revision_brief"],
        "keep": "保留角色目标、关键线索和已发生事件。",
        "avoid": "不要整章重写，不引入新的设定真源，不覆盖已有 artifact。",
    }


def _sentences(text: str) -> list[str]:
    return [item.strip() for item in _SENTENCE_RE.findall(text) if item.strip()]


def _sentences_with(text: str, markers: tuple[str, ...]) -> list[str]:
    return [
        sentence
        for sentence in _sentences(text)
        if any(marker in sentence for marker in markers)
    ]


def _tail_key(sentence: str) -> str:
    stripped = re.sub(r"[。！？!?；;，,\s]", "", sentence.strip())
    return stripped[-6:]


def _normalize_dialogue(text: str) -> str:
    return re.sub(r"[\s。！？!?；;，,、]", "", text.strip())


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _next_steps(status: str) -> list[str]:
    if status == "blocked":
        return ["先恢复 chapter.md，再生成读者评审。"]
    if status == "ready":
        return ["当前没有命中明显 deterministic 修订点；可结合人工阅读继续判断。"]
    return [
        "先按高/中严重度处理可删解释、重复结尾和同声对话。",
        "需要自动改写时，后续再接 opt-in LLM 修订，不默认覆盖正文。",
    ]
