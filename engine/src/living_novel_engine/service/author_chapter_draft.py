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
CONTINUOUS_READING_ARTIFACT = "continuous_reading_chapter.json"
CONTINUOUS_READING_MARKDOWN_ARTIFACT = "continuous_reading_chapter.md"


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
    root = outputs_dir or default_outputs_dir()
    run_dir = root / rid
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
    continuous_reading = _continuous_reading_chapter(
        record=record,
        brief=brief,
        chapter_text=chapter_text,
        consequences=consequences,
        outputs_root=root,
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
        "continuous_reading_chapter": continuous_reading,
        "artifacts": {
            "next_chapter_draft": ARTIFACT,
            "next_chapter_markdown": MARKDOWN_ARTIFACT,
            "draft_revision_pack": REVISION_ARTIFACT,
            "continuous_reading_chapter": CONTINUOUS_READING_ARTIFACT,
            "continuous_reading_markdown": CONTINUOUS_READING_MARKDOWN_ARTIFACT,
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
    (run_dir / CONTINUOUS_READING_ARTIFACT).write_text(
        json.dumps(continuous_reading, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / CONTINUOUS_READING_MARKDOWN_ARTIFACT).write_text(
        continuous_reading["reading_body_md"],
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


def _continuous_reading_chapter(
    *,
    record: dict[str, Any],
    brief: dict[str, Any],
    chapter_text: str,
    consequences: list[str],
    outputs_root: Path,
) -> dict[str, Any]:
    adoption_entry = (
        record.get("adoption_entry") if isinstance(record.get("adoption_entry"), dict) else {}
    )
    source_lens_run_id = safe_id(str(adoption_entry.get("source_run_id") or "").strip()) or ""
    lens_payload = _read_lens_volumes(outputs_root, source_lens_run_id)
    source = lens_payload.get("source") if isinstance(lens_payload.get("source"), dict) else {}
    volumes = lens_payload.get("volumes") if isinstance(lens_payload.get("volumes"), list) else []
    cross_volume_refs = _cross_volume_refs(
        volumes=volumes,
        lens_run_id=source_lens_run_id,
        sandbox_run_id=str(source.get("sandbox_run_id") or ""),
    )
    reading_sections = _reading_sections(
        chapter_text=chapter_text,
        brief=brief,
        consequences=consequences,
        volumes=volumes,
    )
    status = "ready" if len(cross_volume_refs) >= 3 else "partial"
    reading_body_md = _continuous_reading_markdown(
        title=_chapter_title(brief),
        sections=reading_sections,
        cross_volume_refs=cross_volume_refs,
    )
    next_hook = _next_chapter_hook(brief, consequences)
    return {
        "version": "continuous-reading-chapter-v2",
        "artifact": CONTINUOUS_READING_ARTIFACT,
        "markdown_artifact": CONTINUOUS_READING_MARKDOWN_ARTIFACT,
        "status": status,
        "default_mode": "novel",
        "chapter_title": _chapter_title(brief),
        "reading_body_md": reading_body_md,
        "reading_sections": reading_sections,
        "viewpoint_tabs": _viewpoint_tabs(cross_volume_refs),
        "evidence_toggle": {
            "default_visible": False,
            "label": "证据",
            "description": "默认先读正文；展开后查看沙盘轮次、角色个人卷和事件多视角引用。",
        },
        "continuity_threads": {
            "foreshadowing": _foreshadowing_thread(brief, consequences),
            "payoff": _payoff_thread(brief, cross_volume_refs),
            "misunderstanding": "角色先按自己的记忆和利益误读对方，再由下一轮沙盘结算。",
        },
        "chapter_cliffhanger": next_hook,
        "reading_flow": {
            "scene_count": len(reading_sections),
            "opening_hook": str(brief.get("opening_scene") or reading_sections[0]["title"]),
            "turning_point": str(brief.get("conflict_focus") or "信息差被推到明面"),
            "next_chapter_hook": next_hook,
        },
        "s8_source": {
            "lens_run_id": source_lens_run_id,
            "source_sandbox_run_id": str(source.get("sandbox_run_id") or ""),
            "artifact": (
                f"outputs/{source_lens_run_id}/character_lens_volumes.json"
                if source_lens_run_id
                else ""
            ),
        },
        "cross_volume_refs": cross_volume_refs,
        "reader_guidance": [
            "先按正文顺序阅读，不在段落中插入证据说明。",
            "读完后再看卷宗引用，核对世界正史、角色个人卷和事件多视角。",
            "下一章应从阅读流的末尾钩子和具象代偿继续，而不是另起素材集合。",
        ],
        "boundaries": [
            "连续阅读稿只写入作者采纳 run 目录，不覆盖 next_chapter_draft.md。",
            "正文引用 S8 多视角卷宗，但证据链保留在 JSON 与文末，不打断阅读。",
            "缺少来源 character_lens_volumes.json 时降级为 partial，不阻断草稿生成。",
        ],
    }


def _reading_sections(
    *,
    chapter_text: str,
    brief: dict[str, Any],
    consequences: list[str],
    volumes: list[Any],
) -> list[dict[str, Any]]:
    paragraphs = _chapter_paragraphs(chapter_text)
    world = _find_volume(volumes, "world_chronicle")
    character = _find_volume(volumes, "character_volume")
    event = _find_volume(volumes, "event_multi_perspective")
    sections = [
        {
            "id": "opening_pressure",
            "title": "一、雨声入局",
            "body": paragraphs[0],
            "viewpoint": "世界正史卷",
            "cognitive_bias": "读者先看到客观压力，角色尚未共享彼此底牌。",
            "conflict_turn": "开场钩子把角色推入必须立即选择的现场。",
            "narrative_role": "开场先落入现场，让角色在世界代偿里做选择。",
            "evidence_refs": ["next_chapter_brief.json#opening_scene"],
            "evidence_mode": {
                "default_visible": False,
                "refs": ["next_chapter_brief.json#opening_scene"],
            },
        },
        {
            "id": "character_misread",
            "title": "二、各怀半句真话",
            "body": paragraphs[1],
            "viewpoint": "角色个人卷",
            "cognitive_bias": "角色把对方的沉默当成隐瞒，却不知道自己也在隐瞒。",
            "conflict_turn": "误会从内心判断进入对话和动作。",
            "narrative_role": "把角色个人卷的信息差写成对话和误读。",
            "evidence_refs": _volume_evidence_refs(character, "character_volume"),
            "evidence_mode": {
                "default_visible": False,
                "refs": _volume_evidence_refs(character, "character_volume"),
            },
        },
        {
            "id": "world_counterweight",
            "title": "三、正史不替人辩解",
            "body": _merge_body(paragraphs[2], world, consequences),
            "viewpoint": "世界正史卷",
            "cognitive_bias": "正史只记录代偿落点，不替任何角色解释动机。",
            "conflict_turn": "世界状态把私人误判扩大成公共压力。",
            "narrative_role": "让世界状态和因果代偿成为场景压力。",
            "evidence_refs": _volume_evidence_refs(world, "world_chronicle")
            + ["worldline_state.json#consequence_state"],
            "evidence_mode": {
                "default_visible": False,
                "refs": _volume_evidence_refs(world, "world_chronicle")
                + ["worldline_state.json#consequence_state"],
            },
        },
        {
            "id": "next_round_hook",
            "title": "四、余波写入下一轮",
            "body": _merge_body(paragraphs[-1], event, consequences),
            "viewpoint": "事件多视角",
            "cognitive_bias": "不同卷宗都只拿到事件的一面，悬念留给下一轮沙盘。",
            "conflict_turn": "结尾把伏笔和未解误会交给下一章。",
            "narrative_role": "把确认稿末尾接回后续沙盘入口。",
            "evidence_refs": _volume_evidence_refs(event, "event_multi_perspective")
            + ["next_chapter_brief.json#feed_forward"],
            "evidence_mode": {
                "default_visible": False,
                "refs": _volume_evidence_refs(event, "event_multi_perspective")
                + ["next_chapter_brief.json#feed_forward"],
            },
        },
    ]
    if len(paragraphs) > 4:
        sections.insert(
            3,
            {
                "id": "middle_turn",
                "title": "三更、代价显形",
                "body": paragraphs[3],
                "viewpoint": "主锚点卷",
                "cognitive_bias": "主锚点以为自己在控制局面，其实世界代偿已经先行一步。",
                "conflict_turn": "中段让抽象因果债变成可见阻碍。",
                "narrative_role": "承接正文中段，把抽象因果债转成可见阻碍。",
                "evidence_refs": ["next_chapter_brief.json#materialized_consequences"],
                "evidence_mode": {
                    "default_visible": False,
                    "refs": ["next_chapter_brief.json#materialized_consequences"],
                },
            },
        )
    return sections


def _continuous_reading_markdown(
    *,
    title: str,
    sections: list[dict[str, Any]],
    cross_volume_refs: list[dict[str, Any]],
) -> str:
    lines = [f"# {title}", ""]
    for section in sections:
        lines.extend([f"## {section['title']}", "", str(section["body"]).strip(), ""])
    lines.extend(["## 卷宗回读", ""])
    if cross_volume_refs:
        for ref in cross_volume_refs:
            lines.append(f"- {ref['label']}：{ref['artifact']}")
    else:
        lines.append("- 尚未绑定来源多视角卷宗；正文可读，证据回读降级为部分证据。")
    lines.append("")
    return "\n".join(lines)


def _viewpoint_tabs(cross_volume_refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    labels = {
        "world_chronicle": "世界正史卷",
        "character_volume": "角色个人卷",
        "event_multi_perspective": "事件多视角",
    }
    tabs = [
        {
            "id": ref["id"],
            "label": ref.get("label") or labels.get(ref["id"], ref["id"]),
            "artifact": ref.get("artifact") or "",
            "summary": ref.get("summary") or "",
        }
        for ref in cross_volume_refs
        if ref.get("id")
    ]
    existing = {tab["id"] for tab in tabs}
    for tab_id, label in labels.items():
        if tab_id not in existing:
            tabs.append(
                {
                    "id": tab_id,
                    "label": label,
                    "artifact": "",
                    "summary": "来源卷宗暂缺，阅读稿保留该视角入口。",
                }
            )
    return tabs


def _foreshadowing_thread(brief: dict[str, Any], consequences: list[str]) -> str:
    conflict = str(brief.get("conflict_focus") or "").strip()
    if conflict:
        return f"伏笔从“{_trim(conflict, 70)}”开始，角色暂时只看见其中一半。"
    if consequences:
        return f"伏笔落在“{_trim(consequences[0], 70)}”的世界内代价上。"
    return "伏笔落在角色未说出口的误判和下一轮沙盘入口上。"


def _payoff_thread(brief: dict[str, Any], cross_volume_refs: list[dict[str, Any]]) -> str:
    if cross_volume_refs:
        labels = "、".join(ref.get("label") or ref.get("id") or "" for ref in cross_volume_refs[:3])
        return f"回收时从{labels}核对同一事件的不同说法。"
    sandbox_inputs = (
        brief.get("sandbox_inputs") if isinstance(brief.get("sandbox_inputs"), dict) else {}
    )
    major_event = str(sandbox_inputs.get("major_event") or "").strip()
    if major_event:
        return f"回收时回到沙盘事件“{_trim(major_event, 70)}”。"
    return "回收时回到 next_chapter_brief 和角色主观记忆链。"


def _chapter_paragraphs(chapter_text: str) -> list[str]:
    paragraphs = [
        item.strip()
        for item in str(chapter_text or "").split("\n\n")
        if item.strip() and not item.strip().startswith("#")
    ]
    if len(paragraphs) >= 4:
        return paragraphs
    clean = " ".join(str(chapter_text or "").split())
    return [clean] * 4


def _merge_body(
    paragraph: str,
    volume: dict[str, Any],
    consequences: list[str],
) -> str:
    prose = str(volume.get("prose") or "").strip() if volume else ""
    consequence = consequences[0] if consequences else ""
    parts = [paragraph.strip()]
    if prose:
        parts.append(_trim(prose, 220))
    if consequence and consequence not in parts[0]:
        parts.append(f"这一切还压着一层看得见的代价：{_trim(consequence, 120)}")
    return "\n\n".join(part for part in parts if part)


def _cross_volume_refs(
    *,
    volumes: list[Any],
    lens_run_id: str,
    sandbox_run_id: str,
) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for volume_type, label in (
        ("world_chronicle", "世界正史卷"),
        ("character_volume", "角色个人卷"),
        ("event_multi_perspective", "事件多视角"),
    ):
        volume = _find_volume(volumes, volume_type)
        if not volume:
            continue
        artifact = f"outputs/{lens_run_id}/character_lens_volumes.json#{volume_type}"
        refs.append(
            {
                "id": volume_type,
                "label": label,
                "title": str(volume.get("title") or label),
                "artifact": artifact,
                "evidence_refs": _volume_evidence_refs(
                    volume,
                    volume_type,
                    artifact=artifact,
                    sandbox_run_id=sandbox_run_id,
                ),
                "summary": _trim(volume.get("prose") or "", 180),
            }
        )
    return refs


def _volume_evidence_refs(
    volume: dict[str, Any],
    volume_type: str,
    *,
    artifact: str = "",
    sandbox_run_id: str = "",
) -> list[str]:
    if not volume:
        return []
    refs = [artifact] if artifact else []
    if not refs and volume_type:
        refs.append(f"character_lens_volumes.json#{volume_type}")
    if sandbox_run_id:
        refs.append(f"outputs/{sandbox_run_id}/sandbox_rounds.jsonl")
    evidence_chain = (
        volume.get("evidence_chain")
        if isinstance(volume.get("evidence_chain"), dict)
        else {}
    )
    if evidence_chain.get("subjective_memory_refs"):
        refs.append("subjective_memory.jsonl")
    if evidence_chain.get("consequence_state_refs"):
        refs.append("worldline_state.json#consequence_state")
    return list(dict.fromkeys(ref for ref in refs if ref))


def _read_lens_volumes(outputs_root: Path, lens_run_id: str) -> dict[str, Any]:
    if not lens_run_id:
        return {}
    path = outputs_root / lens_run_id / "character_lens_volumes.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def _find_volume(volumes: list[Any], volume_type: str) -> dict[str, Any]:
    for volume in volumes:
        if isinstance(volume, dict) and volume.get("volume_type") == volume_type:
            return volume
    return {}


def _next_chapter_hook(brief: dict[str, Any], consequences: list[str]) -> str:
    feed_forward = (
        brief.get("feed_forward") if isinstance(brief.get("feed_forward"), dict) else {}
    )
    sandbox_inputs = (
        feed_forward.get("sandbox_continuation_inputs")
        if isinstance(feed_forward.get("sandbox_continuation_inputs"), dict)
        else {}
    )
    major_event = str(sandbox_inputs.get("major_event") or "").strip()
    if major_event:
        return major_event
    if consequences:
        return f"下一轮从“{_trim(consequences[0], 80)}”继续。"
    return "下一轮从确认稿余波和角色未说出口的判断继续。"


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
    semantic_reviewer = _semantic_reviewer(
        chapter_text=chapter_text,
        brief=brief,
        consequences=consequences,
        missing=missing,
    )
    return {
        "version": "draft-revision-pack-v2",
        "artifact": REVISION_ARTIFACT,
        "status": "ready" if not missing else "needs_revision",
        "summary": _revision_summary(brief, consequences, missing),
        "semantic_reviewer": semantic_reviewer,
        "review_focus": [
            str(brief.get("conflict_focus") or "确认章节冲突是否来自沙盘涌现"),
            "把具象代偿落到动作、环境或对话里，而不是只解释因果债。",
            "保留角色信息差，让确认稿能回读角色个人卷。",
        ],
        "localized_rewrites": rewrites,
        "adoption_feedback": {
            "surface": "author_adoption_desk",
            "feeds": ["next_chapter_draft", "chapter_confirmation"],
            "confirmation_use": "作者可采纳局部改写后再确认入卷；未采纳时仍保留审稿证据。",
            "next_chapter_use": "下一章草稿继续读取人物误判、冲突张力和世界代偿入文建议。",
        },
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


def _semantic_reviewer(
    *,
    chapter_text: str,
    brief: dict[str, Any],
    consequences: list[str],
    missing: list[str],
) -> dict[str, Any]:
    conflict = str(brief.get("conflict_focus") or "沙盘涌现冲突")
    consequence = consequences[0] if consequences else "具象代偿"
    opening = str(brief.get("opening_scene") or "开场场景")
    return {
        "status": "needs_revision" if missing else "ready",
        "diagnosis_summary": (
            "语义审稿关注人物动机、冲突张力、世界代偿入文、视角清晰度和记忆消费；"
            "当前草稿可进入确认前局部打磨。"
            if not missing
            else "语义审稿发现 gate 待补项，需先补足沙盘来源、信息差或代偿入文。"
        ),
        "priority_order": ["人物动机", "冲突张力", "世界代偿入文", "视角清晰度", "记忆消费"],
        "review_items": [
            {
                "id": "motivation",
                "priority": "high",
                "dimension": "人物动机",
                "problem": "角色选择需要更明确地来自自己的利益、误判或保护欲。",
                "evidence_text": _pick_sentence(chapter_text, "赵轩") or _trim(chapter_text, 90),
                "recommendation": f"围绕“{_trim(conflict, 58)}”补一句角色自己的判断，而不是让 narrator 替他解释。",
            },
            {
                "id": "tension",
                "priority": "high",
                "dimension": "冲突张力",
                "problem": "冲突应通过互相试探、隐瞒或错判推进，而不是直接摊牌。",
                "evidence_text": _pick_sentence(chapter_text, "沈冰月") or _trim(chapter_text, 90),
                "recommendation": "保留一句没说出口的真话，让下一场景仍有对抗余地。",
            },
            {
                "id": "consequence",
                "priority": "medium",
                "dimension": "世界代偿入文",
                "problem": "代偿要变成地点、资源、舆论、伤势或环境阻碍。",
                "evidence_text": _trim(str(consequence), 90),
                "recommendation": f"把“{_trim(consequence, 58)}”落成角色必须立刻处理的阻碍。",
            },
            {
                "id": "viewpoint",
                "priority": "medium",
                "dimension": "视角清晰度",
                "problem": "多视角切换需要标明谁知道什么，避免全知旁白泄露秘密。",
                "evidence_text": _trim(opening, 90),
                "recommendation": "每次转视角只补该角色能看见或误会的信息。",
            },
            {
                "id": "memory",
                "priority": "medium",
                "dimension": "记忆消费",
                "problem": "章节应消耗角色主观记忆，而不是只复述沙盘结果。",
                "evidence_text": "subjective_memory.jsonl",
                "recommendation": "把上一轮误会、信任变化或异常感写成动作和对话反应。",
            },
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
            "original_problem": "开场压力还可以更早落入具体场景。",
            "revision_intent": "让读者先看到代价，再理解世界线为什么偏移。",
            "suggested_rewrite": (
                f"{opening}先写角色撞上“{_trim(consequence, 46)}”，"
                "再用一句内心判断露出误会。"
            ),
            "impact_on_characters": ["赵轩更早暴露隐瞒压力", "沈冰月更早形成误判"],
            "impact_on_world_state": "具象代偿从背景说明变成现场阻碍。",
            "adoption_direction": "建议采纳后确认入卷",
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
            "original_problem": "信息差已经存在，但误判的主观来源还可更锋利。",
            "revision_intent": "让角色各自的主观记忆真正改变对话节奏。",
            "suggested_rewrite": (
                f"围绕“{_trim(conflict, 52)}”补沈冰月的一句错误推断，"
                "再用赵轩的沉默或藏物回应。"
            ),
            "impact_on_characters": ["沈冰月的怀疑升级", "赵轩的隐瞒变成可观察动作"],
            "impact_on_world_state": "误会被写入下一轮关系压力。",
            "adoption_direction": "建议采纳后确认入卷",
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
            "original_problem": "因果债若停在解释，会削弱世界自我运行的触感。",
            "revision_intent": "把世界代偿写成角色必须处理的行动阻碍。",
            "suggested_rewrite": (
                f"把“{_trim(consequence, 58)}”改成门禁、盘查、物资被扣或盟友倒戈。"
            ),
            "impact_on_characters": ["角色不能只讨论代偿，必须当场选择"],
            "impact_on_world_state": "六域代偿进入正文并反哺下一轮沙盘。",
            "adoption_direction": "建议采纳后确认入卷",
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
            "original_problem": "确认前 gate 仍有阻塞项。",
            "revision_intent": "先让正文满足沙盘来源、信息差和代偿入文底线。",
            "suggested_rewrite": "补一段明确来自沙盘事件、角色信息差和世界代偿的正文。",
            "impact_on_characters": ["角色动机和误判需要补足"],
            "impact_on_world_state": "世界代偿需要自然进入正文。",
            "adoption_direction": "建议先局部改写再确认入卷",
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
            "## 连续阅读稿",
            "",
            f"- 正文：{report['artifacts']['continuous_reading_markdown']}",
            f"- 证据：{report['artifacts']['continuous_reading_chapter']}",
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
