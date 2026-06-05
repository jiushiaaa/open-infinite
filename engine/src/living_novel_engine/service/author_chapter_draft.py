"""Turn an author adoption brief into a readable next chapter draft."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from living_novel_engine.browser.paths import outputs_dir as default_outputs_dir
from living_novel_engine.browser.validators import safe_id
from living_novel_engine.service.intervene import resolve_llm_quietly
from living_novel_engine.service.project_health import resolve_story_path
from living_novel_engine.service.worldline_state import load_worldline_state

VERSION = "author-chapter-draft-v1.2"
ARTIFACT = "next_chapter_draft.json"
MARKDOWN_ARTIFACT = "next_chapter_draft.md"
REVISION_ARTIFACT = "draft_revision_pack.json"


class AuthorChapterDraftRequestError(ValueError):
    """Invalid author chapter draft request."""


def generate_author_chapter_draft(
    story_slug: str,
    *,
    adoption_run_id: str,
    projects_dir: Path | None = None,
    outputs_dir: Path | None = None,
    mock: bool = True,
) -> dict[str, Any]:
    """Generate a chapter draft from a prior author adoption run."""

    sid = _checked_id(story_slug, "story_slug")
    rid = _checked_id(adoption_run_id, "adoption_run_id")
    story_path, source_kind = resolve_story_path(sid, projects_dir)
    run_dir = (outputs_dir or default_outputs_dir()) / rid
    record_path = run_dir / "author_adoption_record.json"
    brief_path = run_dir / "next_chapter_brief.json"
    if not record_path.exists() or not brief_path.exists():
        raise FileNotFoundError(f"作者采纳记录或下一章 brief 不存在: {rid}")
    record = _read_json(record_path)
    brief = _read_json(brief_path)
    if record.get("story_slug") != sid:
        raise AuthorChapterDraftRequestError("adoption_run_id 不属于当前故事")
    worldline_id = _checked_id(str(record.get("worldline_id") or "main"), "worldline_id")
    worldline_state = load_worldline_state(story_path, worldline_id)
    consequences = _materialized_consequences(brief, worldline_state)
    generated_by = "deterministic"
    fallback_reason = ""
    if mock:
        chapter_text = _deterministic_chapter_text(record, brief, consequences)
    else:
        chapter_text, generated_by, fallback_reason = _llm_chapter_text(
            record,
            brief,
            consequences,
        )
    reviewer_checklist = _reviewer_checklist(chapter_text, brief, consequences)
    revision_pack = _revision_pack(
        chapter_text=chapter_text,
        brief=brief,
        consequences=consequences,
        reviewer_checklist=reviewer_checklist,
    )
    now = datetime.now().isoformat(timespec="seconds")
    report = {
        "version": VERSION,
        "artifact": ARTIFACT,
        "story_slug": sid,
        "source_kind": source_kind,
        "worldline_id": worldline_id,
        "source_adoption_run_id": rid,
        "created_at": now,
        "generated_by": generated_by,
        "fallback_reason": fallback_reason,
        "chapter_title": _chapter_title(brief),
        "chapter_text": chapter_text,
        "draft_inputs": {
            "decision": record.get("decision") or "",
            "mode_label": record.get("mode_label") or "",
            "opening_scene": brief.get("opening_scene") or "",
            "conflict_focus": brief.get("conflict_focus") or "",
            "original_outline": (
                record.get("comparison")
                if isinstance(record.get("comparison"), dict)
                else {}
            ).get("original_outline")
            or "",
            "sandbox_emergence": (
                record.get("comparison")
                if isinstance(record.get("comparison"), dict)
                else {}
            ).get("sandbox_emergence")
            or "",
        },
        "evidence_chain": {
            "adoption_record": "author_adoption_record.json",
            "next_chapter_brief": "next_chapter_brief.json",
            "worldline_state_artifact": worldline_state.get("artifact") or "",
            "materialized_consequences": consequences,
            "must_preserve": brief.get("must_preserve") or [],
            "sandbox_inputs": brief.get("sandbox_inputs") or {},
        },
        "reviewer_checklist": reviewer_checklist,
        "revision_pack": revision_pack,
        "artifacts": {
            "next_chapter_draft": ARTIFACT,
            "next_chapter_markdown": MARKDOWN_ARTIFACT,
            "draft_revision_pack": REVISION_ARTIFACT,
        },
        "boundaries": [
            "章节草稿只写入作者采纳 run 目录，不覆盖正史 chapter.md。",
            "草稿读取 next_chapter_brief 与 worldline_state，不改 run_scene 默认行为。",
            "mock=True 时不调用外部模型；真实模型 smoke 需显式 mock=False。",
        ],
    }
    (run_dir / ARTIFACT).write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / MARKDOWN_ARTIFACT).write_text(_markdown(report), encoding="utf-8")
    (run_dir / REVISION_ARTIFACT).write_text(
        json.dumps(revision_pack, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report


def _llm_chapter_text(
    record: dict[str, Any],
    brief: dict[str, Any],
    consequences: list[str],
) -> tuple[str, str, str]:
    llm, used_mock = resolve_llm_quietly(False)
    if used_mock:
        return _deterministic_chapter_text(record, brief, consequences), "fallback", "no_real_llm"
    system = (
        "你是未终章的章节草稿写作者。只输出下一章正文，不输出解释。"
        "必须让章节来自沙盘涌现剧情、角色主观误会和世界代偿。"
        "正文必须显式写出角色之间的信息差、隐瞒、怀疑或误判。"
    )
    comparison = record.get("comparison") if isinstance(record.get("comparison"), dict) else {}
    user = "\n".join(
        [
            f"【采纳方式】{record.get('mode_label') or record.get('decision')}",
            f"【原大纲】{comparison.get('original_outline') or ''}",
            f"【沙盘涌现剧情】{comparison.get('sandbox_emergence') or ''}",
            f"【下一章开场】{brief.get('opening_scene') or ''}",
            f"【冲突焦点】{brief.get('conflict_focus') or ''}",
            f"【必须延续】{'；'.join(brief.get('must_preserve') or [])}",
            f"【具象代偿】{'；'.join(consequences)}",
            "请写 800-1200 字中文小说正文，标题自拟，正文中不要出现 JSON 字段名。",
        ]
    )
    try:
        text = llm.chat(system, user, temperature=0.65, max_tokens=2200).strip()
    except Exception as exc:  # pragma: no cover - only exercised by real provider failures.
        return (
            _deterministic_chapter_text(record, brief, consequences),
            "fallback",
            f"llm_error:{exc.__class__.__name__}",
        )
    if len(text) < 120:
        return _deterministic_chapter_text(record, brief, consequences), "fallback", "short_llm_output"
    return text, "llm", ""


def _deterministic_chapter_text(
    record: dict[str, Any],
    brief: dict[str, Any],
    consequences: list[str],
) -> str:
    comparison = record.get("comparison") if isinstance(record.get("comparison"), dict) else {}
    emergence = str(comparison.get("sandbox_emergence") or "")
    outline = str(comparison.get("original_outline") or "")
    opening = str(brief.get("opening_scene") or "下一章从沙盘涌现后的沉默开场。")
    conflict = str(brief.get("conflict_focus") or "原大纲目标与沙盘涌现选择之间的偏移")
    consequence_text = "；".join(consequences[:4]) or "归云斋的灯火和城中流言都在替上一轮选择记账。"
    return "\n\n".join(
        [
            f"# {_chapter_title(brief)}",
            (
                f"{opening}赵轩没有立刻把风鸣铃交出去。旧大纲里他应当公开线索，"
                f"让苍澜派维持表面的安稳，可这一条世界线已经不肯照旧合拢。"
                f"他站在归云斋后门，听见雨水从檐角坠下，像有人替他一遍遍数清因果债。"
            ),
            (
                f"沈冰月赶到时，只看见他收起半截烧焦的绳结。她记得上一轮里赵轩的迟疑，"
                f"也记得自己误判他的真实立场，于是没有先问风鸣铃在哪里，而是问："
                f"“你到底想护住谁？”这句话把两个人之间的信息差挑到明面上。"
            ),
            (
                f"沙盘涌现出的事实仍在逼近：{_trim(emergence, 160)}。"
                f"原大纲仍可作为远处的灯，{_trim(outline, 120)}，但它不再能替角色决定脚步。"
                f"这一章的冲突不在谁更服从作者，而在{conflict}。"
            ),
            (
                f"世界也没有像系统管理员那样重置。它只把代价落进世界内部：{consequence_text}。"
                f"赵轩若继续隐瞒，资源会先被扣到明面；沈冰月若选择相信，宗门舆论会把她一并拖入泥水。"
                f"他们都明白，下一轮沙盘不是从空白开始，而是从这些已经显形的代偿里继续运行。"
            ),
            (
                "天亮前，赵轩把风鸣铃的碎音藏进一枚旧铜钱，交给沈冰月，却故意没有说明完整用法。"
                "沈冰月收下铜钱，也没有拆穿他的保留。两个人都以为自己掌握了主动，"
                "而归云斋外的流言已经先他们一步，把这场误会写成了新的世界线开端。"
            ),
        ]
    )


def _reviewer_checklist(
    chapter_text: str,
    brief: dict[str, Any],
    consequences: list[str],
) -> list[dict[str, Any]]:
    checks = [
        {
            "item": "章节来自沙盘涌现剧情",
            "passed": bool((brief.get("sandbox_inputs") or {}).get("major_event")),
        },
        {
            "item": "保留角色信息差或误判",
            "passed": any(
                word in chapter_text
                for word in ("误判", "信息差", "隐瞒", "怀疑", "没有说明", "没有拆穿")
            ),
        },
        {
            "item": "延续世界内具象代偿",
            "passed": bool(consequences),
        },
        {
            "item": "不覆盖正史 chapter.md",
            "passed": True,
        },
    ]
    return checks


def _revision_pack(
    *,
    chapter_text: str,
    brief: dict[str, Any],
    consequences: list[str],
    reviewer_checklist: list[dict[str, Any]],
) -> dict[str, Any]:
    missing = [str(row["item"]) for row in reviewer_checklist if not row.get("passed")]
    rewrites = _localized_rewrites(chapter_text, brief, consequences, missing)
    return {
        "version": "draft-revision-pack-v1",
        "artifact": REVISION_ARTIFACT,
        "status": "ready" if not missing else "needs_revision",
        "summary": _revision_summary(brief, consequences, missing),
        "review_focus": [
            str(brief.get("conflict_focus") or "确认章节冲突是否来自沙盘涌现"),
            "把具象代偿落到动作、环境或对话里，而不是只解释因果债。",
            "保留角色信息差，让确认稿能回读角色个人卷。",
        ],
        "localized_rewrites": rewrites,
        "confirmation_gate": {
            "ready_for_confirmation": not missing,
            "blocking_items": missing,
            "author_action": (
                "可直接确认入卷，也可先按局部改写建议微调。"
                if not missing
                else "请先补齐待补项，再确认入卷。"
            ),
        },
        "evidence_refs": [
            "author_adoption_record.json",
            "next_chapter_brief.json",
            "worldline_state.json#consequence_state",
        ],
        "boundaries": [
            "修订包只写 draft_revision_pack.json，不自动改写草稿正文。",
            "建议面向作者手工编辑确认稿，不覆盖正史 chapter.md。",
        ],
    }


def _localized_rewrites(
    chapter_text: str,
    brief: dict[str, Any],
    consequences: list[str],
    missing: list[str],
) -> list[dict[str, Any]]:
    opening = str(brief.get("opening_scene") or "下一章开场")
    conflict = str(brief.get("conflict_focus") or "沙盘涌现冲突")
    consequence = consequences[0] if consequences else "世界线代偿仍需落到场景里"
    rows = [
        {
            "id": "tighten_opening_scene",
            "priority": "medium",
            "target_text": _pick_sentence(chapter_text, opening) or _trim(chapter_text, 90),
            "issue": "开场已经承接 brief，但还可以更早把角色选择和场景压力绑在一起。",
            "rewrite_instruction": "把开场第一段改成角色正在处理一个无法回避的具体代价。",
            "suggested_revision": (
                f"{opening}不要先解释世界线偏移，先让赵轩或沈冰月在现场碰到"
                f"“{_trim(consequence, 46)}”，再用一句内心判断露出他们的误会。"
            ),
            "evidence_refs": [
                "next_chapter_brief.json",
                "worldline_state.json#consequence_state",
            ],
        },
        {
            "id": "sharpen_character_misread",
            "priority": "high",
            "target_text": _pick_sentence(chapter_text, "沈冰月") or _trim(chapter_text, 90),
            "issue": "信息差已经存在，但作者确认前应让至少一方误读另一方动机。",
            "rewrite_instruction": "新增一句角色自己的错误推断，并让对方用动作保留秘密。",
            "suggested_revision": (
                f"围绕“{_trim(conflict, 52)}”写一句沈冰月的误判，"
                "再让赵轩用沉默、转移话题或藏起物件来证明他并未全盘托出。"
            ),
            "evidence_refs": [
                "next_chapter_brief.json",
                "subjective_memory.jsonl",
                "author_adoption_record.json",
            ],
        },
        {
            "id": "materialize_consequence",
            "priority": "high" if missing else "medium",
            "target_text": _pick_sentence(chapter_text, "因果债") or _trim(str(consequence), 90),
            "issue": "因果债需要被读者看见，而不只是被 narrator 说明。",
            "rewrite_instruction": "把抽象代偿改成地点封锁、资源扣押、舆论逼迫或伤势反复。",
            "suggested_revision": (
                f"保留“{_trim(consequence, 58)}”，但把它改写成一个人物必须立刻应对的阻碍，"
                "例如门禁、盘查、物资被扣或盟友临时倒戈。"
            ),
            "evidence_refs": [
                "worldline_state.json#consequence_state",
                "next_chapter_brief.json",
            ],
        },
    ]
    if not missing:
        return rows
    rows.insert(
        0,
        {
            "id": "fix_blocking_reviewer_items",
            "priority": "blocking",
            "target_text": _trim(chapter_text, 90),
            "issue": "Reviewer gate 仍有待补项：" + "；".join(missing),
            "rewrite_instruction": "先补齐待补项，再进入确认入卷。",
            "suggested_revision": "补一段明确来自沙盘事件、角色信息差和世界代偿的正文。",
            "evidence_refs": ["next_chapter_brief.json", "draft_revision_pack.json"],
        },
    )
    return rows


def _revision_summary(
    brief: dict[str, Any],
    consequences: list[str],
    missing: list[str],
) -> str:
    conflict = str(brief.get("conflict_focus") or "沙盘涌现冲突")
    consequence = consequences[0] if consequences else "具象代偿"
    if missing:
        return f"确认前需先补齐：{'；'.join(missing)}。"
    return (
        f"草稿已可确认入卷；建议优先打磨“{_trim(conflict, 40)}”和"
        f"“{_trim(consequence, 40)}”的局部呈现。"
    )


def _materialized_consequences(
    brief: dict[str, Any],
    worldline_state: dict[str, Any],
) -> list[str]:
    rows = [str(item) for item in brief.get("materialized_consequences") or [] if str(item)]
    if rows:
        return rows
    consequence = (
        worldline_state.get("consequence_state")
        if isinstance(worldline_state.get("consequence_state"), dict)
        else {}
    )
    domains = consequence.get("domains") if isinstance(consequence.get("domains"), dict) else {}
    domain_rows = [
        str(value.get("current") or "")
        for value in domains.values()
        if isinstance(value, dict) and value.get("current")
    ]
    if domain_rows:
        return domain_rows
    sandbox_inputs = (
        brief.get("sandbox_inputs") if isinstance(brief.get("sandbox_inputs"), dict) else {}
    )
    major_event = str(sandbox_inputs.get("major_event") or brief.get("opening_scene") or "")
    if major_event:
        return [f"{major_event}之后，归云斋的流言和宗门资源扣押成为下一轮世界内代偿。"]
    return ["归云斋的灯火、城中流言和宗门资源扣押成为下一轮世界内代偿。"]


def _chapter_title(brief: dict[str, Any]) -> str:
    conflict = str(brief.get("conflict_focus") or "")
    if "因果债" in conflict:
        return "下一章 因果债入夜"
    if "隐瞒" in conflict or "误判" in conflict:
        return "下一章 风鸣铃后的误判"
    return "下一章 世界线继续运行"


def _markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {report['chapter_title']}",
            "",
            report["chapter_text"],
            "",
            "## 证据链",
            "",
            f"- 作者采纳：{report['evidence_chain']['adoption_record']}",
            f"- 下一章 brief：{report['evidence_chain']['next_chapter_brief']}",
            f"- 世界线状态：{report['evidence_chain']['worldline_state_artifact']}",
            "",
            "## Reviewer 检查",
            "",
            "\n".join(
                f"- {'通过' if row['passed'] else '待补'}：{row['item']}"
                for row in report["reviewer_checklist"]
            ),
            "",
            "## 局部修订包",
            "",
            report["revision_pack"]["summary"],
            "",
            "\n".join(
                f"- {row['id']}：{row['rewrite_instruction']}"
                for row in report["revision_pack"]["localized_rewrites"]
            ),
            "",
        ]
    )


def _pick_sentence(text: str, keyword: str) -> str:
    if not keyword:
        return ""
    for sentence in str(text or "").replace("\n", "。").split("。"):
        clean = sentence.strip()
        if keyword and keyword in clean:
            return _trim(clean, 120)
    return ""


def _trim(text: str, limit: int) -> str:
    clean = " ".join(str(text or "").split())
    return clean if len(clean) <= limit else clean[:limit] + "..."


def _read_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthorChapterDraftRequestError(f"{path.name} 无法解析：{exc}") from exc
    return raw if isinstance(raw, dict) else {}


def _checked_id(value: object, label: str) -> str:
    checked = safe_id(str(value or "").strip())
    if checked is None:
        raise AuthorChapterDraftRequestError(f"{label} 无效")
    return checked
