from __future__ import annotations

import os

import click
from rich.console import Console
from rich.table import Table

from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.llm.client import LLMClient, LLMSettings
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import build_branch_specs
from living_novel_engine.output.writer import load_run_for_compare, write_run_output
from living_novel_engine.samples import list_samples, load_sample

console = Console()


def _item(text: str) -> str:
    """ASCII list marker; avoids Windows legacy console encoding failures."""
    return f"  - {text}"


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
    if bundle.canon_chapter:
        console.print("\n[bold]原作章节（节选）[/bold]")
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
    bundle = load_sample(slug)
    char_map = bundle.character_map()
    if target not in char_map:
        raise click.ClickException(f"未知角色: {target}，可选: {', '.join(char_map.keys())}")

    llm = _resolve_llm(mock)

    intervention = build_intervention(
        target=target,
        content=content,
        intervention_type=intervention_type,  # type: ignore[arg-type]
    )
    intervention = audit_intervention(intervention, bundle.world, char_map)

    console.print(
        f"[green]干预已解析[/green] strength={intervention.strength} "
        f"risk={intervention.contract_risk}"
    )
    audit = intervention.contract_audit
    if audit:
        console.print(f"  allowed={audit.allowed} resistance={audit.expected_character_resistance}")
        for v in audit.violations:
            console.print(f"  [red]违规:[/red] {v}")
        for s in audit.repair_suggestions:
            console.print(f"  [dim]建议:[/dim] {s}")

    specs = build_branch_specs(intervention, count=max(2, min(3, branches)))
    results = []
    for spec in specs:
        console.print(f"[cyan]推演 {spec.branch_id}[/cyan] — {spec.theme}")
        result = run_scene(
            bundle.world,
            bundle.characters,
            intervention,
            spec,
            llm,
            max_rounds=rounds,
            canon_excerpt=bundle.canon_chapter,
        )
        results.append(result)

    output = write_run_output(intervention, results)
    console.print(f"\n[bold green]完成[/bold green] 输出目录: {output.run_dir}")
    console.print(f"对比表: {output.run_dir / 'compare.md'}")


@main.command("compare")
@click.argument("run_path", type=click.Path(exists=True))
def compare_cmd(run_path: str) -> None:
    """查看一次运行的世界线对比"""
    text = load_run_for_compare(run_path)
    console.print(text)


if __name__ == "__main__":
    main()
