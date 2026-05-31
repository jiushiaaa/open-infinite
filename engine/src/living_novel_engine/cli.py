from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient, LLMSettings
from living_novel_engine.models import Intervention
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import (
    build_branch_specs_from_compilation,
    build_continuation_spec,
)
from living_novel_engine.intervention_compiler import (
    InterventionCompilation,
    compile_intervention_with_llm,
)
from living_novel_engine.fourth_wall import (
    FourthWallLedger,
    accumulate_intervention,
    fourth_wall_enabled,
)
from living_novel_engine.output.writer import (
    load_lineage_ledger,
    load_run_for_compare,
    write_resume_intervene_output,
    write_resume_output,
    write_run_output,
)
from living_novel_engine.resume import (
    build_seed_scene_state,
    build_seed_scene_state_for_intervene,
    load_parent_snapshot,
    project_characters_from_parent,
)
from living_novel_engine.samples import list_samples, load_sample

from living_novel_engine.import_novel.splitter import split_chapters
from living_novel_engine.import_novel.mock_extractor import mock_extract
from living_novel_engine.import_novel.writer import write_project, _default_projects_dir
from living_novel_engine.import_novel.validator import validate_project
from living_novel_engine.story_loader import load_story, list_stories
from living_novel_engine.resources.genre_loader import (
    get_genre_display_name,
    list_genres,
)
from living_novel_engine.runtime_memory import build_runtime_memory_context

console = Console()


def _prepare_retrieval(
    bundle,
    query: str,
    source_type: str,
    *,
    current_chapter: int = 1,
) -> tuple[str, dict | None, dict | None]:
    """imported 项目检索上下文；builtin 返回空且不写 artifact。"""
    if bundle.project_dir and source_type != "builtin_sample":
        ctx = build_runtime_memory_context(
            bundle.project_dir,
            query,
            current_chapter=current_chapter,
        )
        return ctx.as_prompt_block(), ctx.retrieval.to_artifact(), ctx.to_artifact()
    return "", None, None


def _attach_retrieval(
    result,
    record: dict | None,
    runtime_record: dict | None = None,
):
    if record is not None:
        result.retrieval_record = record
    if runtime_record is not None:
        result.runtime_memory_record = runtime_record
    return result


def _present_ids(bundle) -> list[str]:
    return [c.id for c in bundle.characters if getattr(c, "present_in_scene", True)]


def _report_awareness(ledger: FourthWallLedger | None, target: str) -> None:
    """打印目标角色的第四面墙觉察变化。"""
    if ledger is None or not ledger.enabled:
        return
    aw = ledger.awareness.get(target)
    if aw is None or aw.score <= 0:
        return
    triggers = "、".join(aw.triggers) if aw.triggers else "无"
    console.print(
        f"  [magenta]第四面墙[/magenta] {target} 觉察={aw.score:.2f} "
        f"等级={aw.level} 触发={triggers}"
    )


def _fw_load_for_resume(parent_run_id: str) -> FourthWallLedger | None:
    """开启时：沿 lineage 继承关闭前的账本；关闭时：返回 None。"""
    if not fourth_wall_enabled():
        return None
    return load_lineage_ledger(parent_run_id)


def _fw_resume_intervene(
    parent_run_id: str,
    intervention: Intervention,
    *,
    chapter: int,
    present_ids: list[str],
) -> FourthWallLedger | None:
    """开启时：继承 lineage 并累加本次干预；关闭时：不累积。"""
    ledger = _fw_load_for_resume(parent_run_id)
    if ledger is None:
        return None
    accumulate_intervention(
        ledger, intervention, chapter=chapter, present_ids=present_ids
    )
    return ledger


def _item(text: str) -> str:
    """ASCII list marker; avoids Windows legacy console encoding failures."""
    return f"  - {text}"


def _report_compilation(compilation: InterventionCompilation) -> None:
    """打印 Intervention Compiler 的理解结果与本次专属分支轴。"""
    ai = compilation.abstract_intervention
    comp = compilation.compatibility
    console.print(
        f"[bold magenta]干预编译[/bold magenta] source={compilation.source} "
        f"类型={ai.intervention_type} "
        f"兼容性={comp.status}/{comp.risk} 谱系={compilation.lineage_type}"
    )
    meta = compilation.generation_meta or {}
    if meta.get("fallback_reason"):
        console.print(f"  [yellow]回退原因:[/yellow] {meta['fallback_reason']}")
    if meta.get("reconciled"):
        console.print("  [yellow]已触发规则改写安全兜底[/yellow]")
    for r in comp.reasons:
        console.print(f"  [dim]理由:[/dim] {r}")
    for c in comp.contract_conflicts:
        console.print(f"  [red]规则冲突:[/red] {c}")
    console.print(f"  [dim]落地方式:[/dim] {compilation.realization.description}")
    axis_labels = "  |  ".join(
        f"{a.label}({a.outcome})" for a in compilation.branch_axis
    )
    console.print(f"  [cyan]本次分支轴:[/cyan] {axis_labels}")


def _resolve_llm(mock_flag: bool) -> LLMClient:
    settings = LLMSettings.from_env()
    env_mock = os.environ.get("LNE_MOCK", "").lower() in ("1", "true", "yes")
    use_mock = mock_flag or env_mock or not settings.llm_api_key

    if use_mock and not mock_flag and not settings.llm_api_key:
        console.print(
            "[yellow]未检测到 LLM_API_KEY，已自动启用 mock 模式（端到端演示）[/yellow]"
        )

    llm = LLMClient(mock=use_mock)
    if not llm.available:
        raise click.ClickException("无法初始化 LLM 客户端，请使用 --mock 或配置 engine/.env")
    return llm


@click.group()
@click.version_option(package_name="living-novel-engine")
def main() -> None:
    """Living Novel Engine — Phase 0 CLI"""


@main.command("list-samples")
def list_samples_cmd() -> None:
    """列出内置样例世界（英文 slug）"""
    samples = list_samples()
    if not samples:
        console.print("[yellow]未找到样例，请确认 samples/ 目录存在[/yellow]")
        return
    table = Table(title="内置样例")
    table.add_column("slug", style="cyan")
    table.add_column("display_name", style="green")
    for slug in samples:
        try:
            bundle = load_sample(slug)
            table.add_row(slug, bundle.display_name)
        except Exception:
            table.add_row(slug, "?")
    console.print(table)


@main.command("show-sample")
@click.argument("slug")
def show_sample_cmd(slug: str) -> None:
    """查看样例世界详情"""
    bundle = load_sample(slug)
    w = bundle.world
    console.print(f"[bold]{bundle.display_name}[/bold] slug={slug} id={w.id}")
    console.print(f"\n[dim]分歧节点:[/dim] {w.divergence_point}")
    console.print(f"\n[dim]场景:[/dim]\n{w.scene_description}")
    console.print("\n[bold]世界规则[/bold]")
    for r in w.rules:
        console.print(_item(r))
    console.print("\n[bold]角色[/bold]")
    for c in bundle.characters:
        console.print(_item(f"{c.name} ({c.id}) - {c.narrative_role}"))
        console.print(f"    {c.persona_summary()}")
    console.print("\n[bold]开放伏笔[/bold]")
    for t in w.open_threads:
        console.print(_item(f"{t.title}: {t.description}"))
    if bundle.prologue:
        console.print("\n[bold]前情提要[/bold]")
        preview = bundle.prologue[:600]
        console.print(preview + ("..." if len(bundle.prologue) > 600 else ""))
    if bundle.canon_opening:
        console.print("\n[bold]第一章（节选）[/bold]")
        preview = bundle.canon_opening[:400]
        console.print(preview + ("..." if len(bundle.canon_opening) > 400 else ""))
    if bundle.canon_chapter:
        console.print("\n[bold]第十二章·干预节点（节选）[/bold]")
        console.print(bundle.canon_chapter[:800] + ("..." if len(bundle.canon_chapter) > 800 else ""))


@main.command("intervene")
@click.argument("slug")
@click.option("--target", required=True, help="干预目标角色 ID")
@click.option("--type", "intervention_type", default="whisper", help="干预类型")
@click.option("--content", required=True, help="干预内容")
@click.option("--branches", default=3, type=int, help="世界线数量 2-3")
@click.option("--rounds", default=4, type=int, help="推演轮次")
@click.option("--mock", is_flag=True, help="强制 mock LLM（无需 API Key）")
def intervene_cmd(
    slug: str,
    target: str,
    intervention_type: str,
    content: str,
    branches: int,
    rounds: int,
    mock: bool,
) -> None:
    """执行一次干预并生成多条世界线"""
    # v0.7：核心编排收敛到 service.run_intervention（与 Web API 共用，不复制推演逻辑）。
    from living_novel_engine.service import (
        InterventionRequestError,
        run_intervention,
    )

    try:
        result = run_intervention(
            story_slug=slug,
            target=target,
            content=content,
            intervention_type=intervention_type,
            branches=branches,
            rounds=rounds,
            mock=mock,
        )
    except InterventionRequestError as exc:
        raise click.ClickException(str(exc)) from exc

    if result.llm_mock and not mock:
        console.print(
            "[yellow]未检测到 LLM_API_KEY，已自动启用 mock 模式（端到端演示）[/yellow]"
        )
    _report_compilation(result.compilation)
    console.print(
        f"分支: {', '.join(result.branch_ids)}"
    )
    console.print(
        f"干预编译结果: {result.run_dir / 'intervention_compilation.json'}"
    )
    console.print(f"\n[bold green]完成[/bold green] 输出目录: {result.run_dir}")
    console.print(f"对比表: {result.run_dir / 'compare.md'}")


@main.command("compare")
@click.argument("run_path", type=click.Path(exists=True))
def compare_cmd(run_path: str) -> None:
    """查看一次运行的世界线对比"""
    text = load_run_for_compare(run_path)
    console.print(text)


# ─── v0.2 Import Novel 命令 ────────────────────────────────────────


@main.command("import-novel")
@click.argument("path", type=click.Path(exists=True))
@click.option("--name", "-n", required=True, help="项目 slug（英文小写+连字符）")
@click.option("--anchor", default="last", help="干预锚定章：last / 章节序号")
@click.option("--genre", default="xianxia", help="题材提示")
@click.option("--mock", is_flag=True, help="使用 mock 抽取（不调 LLM）")
@click.option("--max-chapters", default=10, type=int, help="最大章节数")
@click.option("--force", is_flag=True, help="覆盖已存在的同名项目")
def import_novel_cmd(
    path: str,
    name: str,
    anchor: str,
    genre: str,
    mock: bool,
    max_chapters: int,
    force: bool,
) -> None:
    """导入小说文本，生成可干预的世界锚定项目"""
    import re as _re

    if not _re.match(r"^[a-z0-9][a-z0-9-]*$", name):
        raise click.ClickException("--name 须为英文小写字母+数字+连字符，如 my-story")

    projects_dir = _default_projects_dir()
    existing = projects_dir / name
    if existing.exists() and not force:
        raise click.ClickException(
            f"项目 '{name}' 已存在: {existing}\n"
            f"如需覆盖请加 --force"
        )

    source_path = Path(path)
    console.print(f"[cyan]拆分章节[/cyan] 来源: {source_path}")

    chapters = split_chapters(source_path, max_chapters=max_chapters)
    console.print(f"  识别到 {len(chapters)} 章")

    anchor_idx: int | None = None
    if anchor == "last":
        anchor_idx = len(chapters) - 1
    else:
        try:
            anchor_idx = int(anchor) - 1
        except ValueError:
            raise click.ClickException(f"--anchor 须为 last 或章节序号，不支持: {anchor}")
        if anchor_idx < 0 or anchor_idx >= len(chapters):
            raise click.ClickException(
                f"--anchor {anchor} 超出范围（共 {len(chapters)} 章）"
            )

    settings = LLMSettings.from_env()
    env_mock = os.environ.get("LNE_MOCK", "").lower() in ("1", "true", "yes")
    use_mock_extract = mock or env_mock or not settings.llm_api_key

    if not use_mock_extract:
        llm = LLMClient(settings=settings, mock=False)
        if not llm.available:
            raise click.ClickException(
                "真实 LLM 抽取需要配置 LLM_API_KEY（engine/.env）。或使用 --mock。"
            )
        console.print(f"[cyan]抽取世界锚定[/cyan] 模式: llm ({llm.settings.llm_model_name})")
        from living_novel_engine.import_novel.llm_extractor import llm_extract

        extraction = llm_extract(
            chapters, llm, story_name=name, genre=genre, anchor_chapter_index=anchor_idx
        )
    else:
        if not mock and not env_mock and not settings.llm_api_key:
            console.print(
                "[yellow]未检测到 LLM_API_KEY，已自动启用 mock 模式（端到端演示）[/yellow]"
            )
        console.print(f"[cyan]抽取世界锚定[/cyan] 模式: mock")
        extraction = mock_extract(
            chapters, story_name=name, genre=genre, anchor_chapter_index=anchor_idx
        )
    for w in extraction.warnings:
        console.print(f"  [dim]! {w}[/dim]")

    console.print(f"[cyan]写入项目[/cyan] slug: {name}")
    project_dir = write_project(
        name,
        chapters,
        extraction,
        anchor_chapter_index=anchor_idx,
        allow_overwrite=force,
        genre=genre,
    )
    console.print(f"\n[bold green]导入完成[/bold green] 项目目录: {project_dir}")
    console.print("后续步骤:")
    console.print(_item(f"lne validate-project {name}"))
    console.print(_item(f"手动编辑 {project_dir / 'world.yaml'} 和 characters.yaml"))
    console.print(_item(f"lne intervene {name} --target <char_id> --content '...'"))


@main.command("list-genres")
def list_genres_cmd() -> None:
    """列出所有可用的题材模板 slug"""
    table = Table(title="可用题材模板")
    table.add_column("slug", style="cyan")
    table.add_column("中文名", style="green")
    for slug in list_genres():
        table.add_row(slug, get_genre_display_name(slug))
    console.print(table)


@main.command("list-projects")
def list_projects_cmd() -> None:
    """列出已导入的项目"""
    projects_dir = _default_projects_dir()
    if not projects_dir.exists():
        console.print("[yellow]尚无导入项目（projects/ 不存在）[/yellow]")
        return

    dirs = sorted(
        d.name for d in projects_dir.iterdir()
        if d.is_dir() and (d / "world.yaml").exists()
    )
    if not dirs:
        console.print("[yellow]projects/ 下无有效项目[/yellow]")
        return

    table = Table(title="已导入项目")
    table.add_column("slug", style="cyan")
    table.add_column("title", style="green")
    table.add_column("状态")
    for slug in dirs:
        pdir = projects_dir / slug
        title = slug
        try:
            import yaml as _yaml

            with open(pdir / "world.yaml", encoding="utf-8") as f:
                w = _yaml.safe_load(f)
            title = w.get("display_name") or w.get("title", slug)
        except Exception:
            pass
        vr = validate_project(pdir)
        status = "[green]VALID[/green]" if vr.valid else f"[red]FAIL ({len(vr.errors)} errors)[/red]"
        table.add_row(slug, title, status)
    console.print(table)


@main.command("show-project")
@click.argument("slug")
def show_project_cmd(slug: str) -> None:
    """查看导入项目的摘要"""
    projects_dir = _default_projects_dir()
    project_dir = projects_dir / slug
    if not project_dir.exists():
        raise click.ClickException(f"项目不存在: {slug}（查找路径: {project_dir}）")

    vr = validate_project(project_dir)
    if vr.world:
        w = vr.world
        console.print(f"[bold]{w.display_name or w.title}[/bold]  slug={slug}")
        console.print(f"  source_type: {w.source_type}")
        console.print(f"  divergence_point: {w.divergence_point}")
        console.print(f"  rules: {len(w.rules)} 条")
        console.print(f"  locations: {len(w.locations)} 个")
        console.print(f"  factions: {len(w.factions)} 个")
    if vr.characters:
        console.print(f"\n[bold]角色[/bold] ({len(vr.characters)} 个)")
        for c in vr.characters:
            present = "*" if c.present_in_scene else " "
            console.print(f"  {present} {c.name} ({c.id}) - {c.narrative_role}")
    if vr.errors:
        console.print("\n[red]校验错误:[/red]")
        for e in vr.errors:
            console.print(f"  [red]x[/red] {e}")
    if vr.warnings:
        console.print("\n[yellow]warnings:[/yellow]")
        for w_msg in vr.warnings:
            console.print(f"  [yellow]![/yellow] {w_msg}")


@main.command("validate-project")
@click.argument("slug")
def validate_project_cmd(slug: str) -> None:
    """校验导入项目的 YAML 结构与字段完整性"""
    projects_dir = _default_projects_dir()
    project_dir = projects_dir / slug
    if not project_dir.exists():
        raise click.ClickException(f"项目不存在: {slug}（查找路径: {project_dir}）")

    vr = validate_project(project_dir)

    if vr.valid:
        console.print(f"[bold green]OK[/bold green] 项目 {slug} 校验通过")
        console.print(f"  world: {vr.world.title if vr.world else '?'}")
        console.print(f"  characters: {len(vr.characters)} 个")
    else:
        console.print(f"[bold red]FAIL[/bold red] 项目 {slug} 校验失败")
        for e in vr.errors:
            console.print(f"  [red]x[/red] {e}")

    if vr.warnings:
        for w_msg in vr.warnings:
            console.print(f"  [yellow]![/yellow] {w_msg}")

    if not vr.valid:
        raise SystemExit(1)


def _write_creation_loop_closeout_report(slug: str, payload: dict) -> Path:
    from living_novel_engine.browser.paths import projects_dir

    project_dir = projects_dir() / slug
    if not project_dir.is_dir():
        raise click.ClickException("只有导入项目可写入 alpha 收口报告")

    record = {
        "kind": "creation_loop_alpha_closeout_record",
        "version": payload.get("version", "v0.9.0-alpha"),
        "story_slug": slug,
        "created_at": datetime.now().isoformat(),
        "completion_status": payload.get("completion_status", "unknown"),
        "actions": payload.get("actions") or [],
        "closeout": payload.get("closeout") or {},
    }
    report_path = project_dir / "creation_loop_alpha_closeout.json"
    report_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report_path


@main.command("creation-loop-closeout")
@click.argument("slug")
@click.option("--json", "json_output", is_flag=True, help="输出机器可读 JSON")
@click.option("--require-ready", is_flag=True, help="未达到 ready 时以退出码 1 失败")
@click.option("--write-report", is_flag=True, help="ready 后写入 alpha 收口报告")
def creation_loop_closeout_cmd(
    slug: str,
    json_output: bool,
    require_ready: bool,
    write_report: bool,
) -> None:
    """验收 v0.9.0-alpha 长篇共创闭环收口状态。"""
    from living_novel_engine.browser import indexer
    from living_novel_engine.browser.validators import safe_id

    safe_slug = safe_id(slug)
    if not safe_slug:
        raise click.ClickException("slug 非法")

    try:
        workspace = indexer.get_project_workspace(safe_slug)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    creation_loop = workspace.get("creation_loop") or {}
    closeout = creation_loop.get("closeout") or {}
    completion = creation_loop.get("completion") or {}
    payload = {
        "story_slug": safe_slug,
        "version": creation_loop.get("version", "v0.9.0-alpha"),
        "completion_status": completion.get("status", "unknown"),
        "actions": completion.get("actions") or [],
        "closeout": closeout,
    }
    report_path: Path | None = None
    if write_report and closeout.get("can_close_alpha"):
        report_path = _write_creation_loop_closeout_report(safe_slug, payload)
        payload["closeout_report_path"] = str(report_path)

    if json_output:
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        blocker_ids = closeout.get("remaining_blocker_ids") or []
        blocker_labels = closeout.get("remaining_blockers") or []
        actions = payload["actions"]
        status_text = "可收口" if closeout.get("can_close_alpha") else "待补齐"
        console.print(f"[bold]v0.9.0-alpha 创作闭环[/bold] {safe_slug}: {status_text}")
        console.print(f"  completion_status: {payload['completion_status']}")
        console.print(f"  closeout_status: {closeout.get('status', 'unknown')}")
        if blocker_ids:
            console.print(f"  remaining_blocker_ids: {', '.join(blocker_ids)}")
        if blocker_labels:
            console.print(f"  remaining_blockers: {'、'.join(blocker_labels)}")
        if actions:
            console.print("  actions:")
            for action in actions:
                action_id = str(action.get("id") or "")
                label = str(action.get("label") or action_id)
                console.print(f"    - {action_id}: {label}")
        if closeout.get("next_step"):
            console.print(f"  next_step: {closeout.get('next_step')}")
        if report_path:
            console.print(f"  closeout_report: {report_path}")

    if write_report and not closeout.get("can_close_alpha"):
        raise click.ClickException("v0.9.0-alpha 尚未收口，未写入收口报告")

    if require_ready and not closeout.get("can_close_alpha"):
        raise click.ClickException("v0.9.0-alpha 尚未收口")


@main.group("resume")
def resume_group() -> None:
    """沿已选世界线续写（v0.1.2+）"""


@resume_group.command("continue")
@click.argument("run_id")
@click.option("--branch", required=True, help="父 run 中的分支 ID，如 branch_a")
@click.option("--rounds", default=4, type=int, help="推演轮次")
@click.option("--mock", is_flag=True, help="强制 mock LLM")
def resume_continue_cmd(run_id: str, branch: str, rounds: int, mock: bool) -> None:
    """沿选定分支无新干预推进一章（生成新 run，含 parent 元数据）"""
    llm = _resolve_llm(mock)
    parent = load_parent_snapshot(run_id, branch)
    characters, world = project_characters_from_parent(parent)
    bundle = load_story(parent.story_slug)

    parent_seed = parent.branch_seed or "unknown"
    spec = build_continuation_spec(parent_seed, parent.branch_id)
    next_chapter = parent.chapter_number + 1

    console.print(
        f"[cyan]续章[/cyan] story={parent.story_slug} ({parent.source_kind}) "
        f"父 run={parent.run_id} 分支={parent.branch_id} "
        f"第{parent.chapter_number}章 → 第{next_chapter}章"
    )

    seed_state = build_seed_scene_state(parent)
    prologue = bundle.prologue
    if parent.summary_text.strip():
        prologue = (
            f"{prologue}\n\n【第{parent.chapter_number}章已发生】\n{parent.summary_text.strip()}"
        )

    query = parent.summary_text[:200] if parent.summary_text else parent.branch_theme
    retrieved_ctx, retrieval_record, runtime_memory_record = _prepare_retrieval(
        bundle, query, parent.source_type, current_chapter=next_chapter
    )

    ledger = _fw_load_for_resume(parent.run_id)

    result = run_scene(
        world,
        characters,
        None,
        spec,
        llm,
        max_rounds=rounds,
        canon_excerpt=parent.chapter_text,
        prologue=prologue,
        canon_opening=bundle.canon_opening,
        canon_chapter=parent.chapter_text,
        seed_scene_state=seed_state,
        seed_characters=characters,
        chapter_number=next_chapter,
        source_type=parent.source_type,
        retrieved_context=retrieved_ctx,
        ledger=ledger,
    )
    _attach_retrieval(result, retrieval_record, runtime_memory_record)

    output = write_resume_output(parent, result, ledger=ledger)
    ch_len = len((output.run_dir / "linear" / "chapter.md").read_text(encoding="utf-8"))
    console.print(f"\n[bold green]完成[/bold green] 新 run: {output.run_dir}")
    console.print(f"续章: linear/chapter.md（{ch_len} 字）")
    console.print(f"元数据: {output.run_dir / 'meta.json'}")


@resume_group.command("intervene")
@click.argument("run_id")
@click.option("--branch", required=True, help="父 run 中的分支 ID，如 linear")
@click.option("--target", required=True, help="干预目标角色 ID")
@click.option("--type", "intervention_type", default="whisper", help="干预类型")
@click.option("--content", required=True, help="干预内容")
@click.option("--branches", default=3, type=int, help="世界线数量 2-3")
@click.option("--rounds", default=4, type=int, help="推演轮次")
@click.option("--mock", is_flag=True, help="强制 mock LLM")
def resume_intervene_cmd(
    run_id: str,
    branch: str,
    target: str,
    intervention_type: str,
    content: str,
    branches: int,
    rounds: int,
    mock: bool,
) -> None:
    """在续章世界线上再次干预并三分叉（生成新 run，含 parent 与 lineage）"""
    llm = _resolve_llm(mock)
    parent = load_parent_snapshot(run_id, branch)
    characters, world = project_characters_from_parent(parent)
    bundle = load_story(parent.story_slug)
    char_map = bundle.character_map()

    if target not in char_map:
        raise click.ClickException(
            f"未知角色: {target}，可选: {', '.join(char_map.keys())}"
        )

    intervention = build_intervention(
        target=target,
        content=content,
        intervention_type=intervention_type,  # type: ignore[arg-type]
    )
    intervention = audit_intervention(intervention, world, char_map)
    intervention.story_slug = parent.story_slug
    intervention.source_kind = parent.source_kind

    console.print(
        f"[green]干预已解析[/green] strength={intervention.strength} "
        f"risk={intervention.contract_risk}"
    )

    next_chapter = parent.chapter_number + 1
    console.print(
        f"[cyan]续章干预[/cyan] story={parent.story_slug} ({parent.source_kind}) "
        f"父 run={parent.run_id} 分支={parent.branch_id} "
        f"第{parent.chapter_number}章 → 第{next_chapter}章（三分叉）"
    )

    seed_state = build_seed_scene_state_for_intervene(parent, target)
    prologue = bundle.prologue
    if parent.summary_text.strip():
        prologue = (
            f"{prologue}\n\n【第{parent.chapter_number}章已发生】\n"
            f"{parent.summary_text.strip()}"
        )

    compilation = compile_intervention_with_llm(
        content,
        target=target,
        world=world,
        characters=char_map,
        llm=llm,
    )
    _report_compilation(compilation)

    specs = build_branch_specs_from_compilation(
        compilation, count=max(2, min(3, branches))
    )
    query = f"{content} {char_map[target].name}"
    retrieved_ctx, retrieval_record, runtime_memory_record = _prepare_retrieval(
        bundle, query, parent.source_type, current_chapter=next_chapter
    )

    ledger = _fw_resume_intervene(
        parent.run_id,
        intervention,
        chapter=next_chapter,
        present_ids=_present_ids(bundle),
    )
    _report_awareness(ledger, target)

    results = []
    for spec in specs:
        console.print(f"[cyan]推演 {spec.branch_id}[/cyan] — {spec.theme}")
        result = run_scene(
            world,
            characters,
            intervention,
            spec,
            llm,
            max_rounds=rounds,
            canon_excerpt=parent.chapter_text,
            prologue=prologue,
            canon_opening=bundle.canon_opening,
            canon_chapter=parent.chapter_text,
            seed_scene_state=seed_state,
            seed_characters=characters,
            chapter_number=next_chapter,
            source_type=parent.source_type,
            retrieved_context=retrieved_ctx,
            ledger=ledger,
        )
        results.append(_attach_retrieval(result, retrieval_record, runtime_memory_record))

    output = write_resume_intervene_output(
        parent, intervention, results, ledger=ledger, compilation=compilation
    )
    console.print(f"\n[bold green]完成[/bold green] 新 run: {output.run_dir}")
    console.print(f"对比表: {output.run_dir / 'compare.md'}")
    console.print(
        f"干预编译结果: {output.run_dir / 'intervention_compilation.json'}"
    )
    for spec in specs:
        ch = output.run_dir / spec.branch_id / "chapter.md"
        if ch.exists():
            console.print(
                f"  {spec.branch_id}/chapter.md（第{next_chapter}章，"
                f"{len(ch.read_text(encoding='utf-8'))} 字）"
            )


@main.command("browse")
@click.option("--host", default="127.0.0.1", help="监听地址")
@click.option("--port", default=8765, type=int, help="监听端口")
@click.option("--no-open", is_flag=True, help="不自动打开浏览器")
def browse_cmd(host: str, port: int, no_open: bool) -> None:
    """启动只读世界线浏览器（v0.4）"""
    from living_novel_engine.browser.paths import outputs_dir, projects_dir
    from living_novel_engine.browser.server import (
        BrowserServerStartError,
        start_browser_server,
    )

    console.print("[bold cyan]世界线浏览器[/bold cyan] v0.4（只读）")
    console.print(_item(f"projects: {projects_dir()}"))
    console.print(_item(f"outputs:  {outputs_dir()}"))
    url = f"http://{host}:{port}/"
    console.print(f"\n[green]访问[/green] {url}")
    console.print("[dim]Ctrl+C 停止服务[/dim]\n")

    try:
        httpd = start_browser_server(host, port, open_browser=not no_open)
    except BrowserServerStartError as exc:
        raise click.ClickException(str(exc))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[yellow]已停止[/yellow]")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
