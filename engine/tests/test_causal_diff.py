"""v0.7.1-C Causal Diff 后端数据预留测试。

覆盖：
- 普通 intervene 分支写出 causal_diff.json（含 blocks / status=proposed）。
- resume intervene 用 parent.chapter_text 作为 old_text。
- old_text 缺失时不崩，写稳定空结构（blocks=[] + reason）。
- rule_rewrite / AK47 类干预标记 alternate_novel（diff_mode=alternate_novel_seed）。
- 生命周期字段预留（accepted_at/rejected_at/reverted_from/parent_diff_id）。
- 不传 compilation 时不写 causal_diff.json（向后兼容）。
- 浏览器 indexer additive：has_causal_diff / causal_diff_count；旧 run 不崩。
"""

from __future__ import annotations

import json

import pytest

from living_novel_engine.browser import indexer
from living_novel_engine.causal_diff import build_causal_diff
from living_novel_engine.intervention.contract_audit import audit_intervention
from living_novel_engine.intervention.parser import build_intervention
from living_novel_engine.intervention_compiler import compile_intervention
from living_novel_engine.llm.client import LLMClient
from living_novel_engine.orchestrator.scene_runner import run_scene
from living_novel_engine.orchestrator.worldline_brancher import (
    build_branch_specs_from_compilation,
)
from living_novel_engine.output.writer import write_run_output
from living_novel_engine.samples import load_sample

OLD = "第一段：林晚舟整理行装。\n\n第二段：她走向竹林。\n\n第三段：夜色深沉。"
NEW = "第一段：林晚舟整理行装。\n\n第二段：她忽然停下脚步，没有去竹林。\n\n第三段：夜色深沉。"


@pytest.fixture(scope="module")
def tianhuang():
    return load_sample("tianhuang-night")


def _compile(text, target, world, characters):
    return compile_intervention(text, target=target, world=world, characters=characters)


# ─── builder 单元 ───────────────────────────────────────────


class TestBuilder:
    def test_paragraph_diff_blocks(self, tianhuang):
        comp = _compile("林晚舟不要去竹林", "lin_wan_zhou", tianhuang.world, tianhuang.character_map())
        art = build_causal_diff(
            branch_id="branch_a", old_text=OLD, new_text=NEW,
            compilation=comp, chapter_number=12,
        )
        assert art.status == "proposed"
        assert art.blocks, "新旧文本不同应产生差异块"
        # 第二段被替换
        replaced = [b for b in art.blocks if b.op == "replace"]
        assert replaced
        assert "竹林" in replaced[0].old_text
        assert replaced[0].anchor.chapter == 12
        assert art.diff_mode == "local_divergence"

    def test_missing_old_text_stable_empty(self, tianhuang):
        comp = _compile("林晚舟不要去竹林", "lin_wan_zhou", tianhuang.world, tianhuang.character_map())
        art = build_causal_diff(
            branch_id="branch_a", old_text="", new_text=NEW,
            compilation=comp, chapter_number=12,
        )
        assert art.blocks == []
        assert art.reason
        assert art.intervention_summary  # 结构仍稳定
        assert art.affected_scope is not None

    def test_both_missing(self, tianhuang):
        comp = _compile("林晚舟不要去竹林", "lin_wan_zhou", tianhuang.world, tianhuang.character_map())
        art = build_causal_diff(
            branch_id="branch_a", old_text=None, new_text=None,
            compilation=comp,
        )
        assert art.blocks == []
        assert "无法生成" in art.reason

    def test_rule_rewrite_alternate_novel_seed(self, tianhuang):
        comp = _compile("给林凡一把AK47", "lin_fan", tianhuang.world, tianhuang.character_map())
        assert comp.lineage_type == "alternate_novel"
        art = build_causal_diff(
            branch_id="branch_a", old_text=OLD, new_text=NEW, compilation=comp,
        )
        assert art.lineage_type == "alternate_novel"
        assert art.diff_mode == "alternate_novel_seed"

    def test_lifecycle_fields_reserved(self, tianhuang):
        comp = _compile("林晚舟不要去竹林", "lin_wan_zhou", tianhuang.world, tianhuang.character_map())
        art = build_causal_diff(
            branch_id="branch_a", old_text=OLD, new_text=NEW, compilation=comp,
        )
        assert art.accepted_at is None
        assert art.rejected_at is None
        assert art.reverted_from is None
        assert art.parent_diff_id is None
        assert art.diff_id.startswith("diff_")

    def test_summary_contains_compilation_fields(self, tianhuang):
        comp = _compile("林晚舟不要去竹林", "lin_wan_zhou", tianhuang.world, tianhuang.character_map())
        art = build_causal_diff(
            branch_id="branch_a", old_text=OLD, new_text=NEW, compilation=comp,
        )
        s = art.intervention_summary
        assert s["intervention_type"] == "forced_action"
        assert "compatibility" in s
        assert "realization" in s
        assert "branch_axis" in s
        assert s["lineage_type"] == "divergent_worldline"


# ─── intervene 写盘集成 ─────────────────────────────────────


class TestInterveneArtifact:
    def _run(self, tianhuang, content, target, *, run_id, with_compilation=True, old_text=None):
        intervention = audit_intervention(
            build_intervention(target=target, content=content, intervention_type="whisper"),
            tianhuang.world, tianhuang.character_map(),
        )
        comp = _compile(content, target, tianhuang.world, tianhuang.character_map())
        specs = build_branch_specs_from_compilation(comp, count=2)
        llm = LLMClient(mock=True)
        results = [
            run_scene(
                tianhuang.world, tianhuang.characters, intervention, spec, llm,
                max_rounds=2, canon_excerpt=tianhuang.canon_chapter,
                canon_chapter=tianhuang.canon_chapter, source_type="builtin_sample",
            )
            for spec in specs
        ]
        kwargs = {"run_id": run_id}
        if with_compilation:
            kwargs["compilation"] = comp
            kwargs["old_text"] = old_text if old_text is not None else tianhuang.canon_chapter
        return write_run_output(intervention, results, **kwargs)

    def test_branch_has_causal_diff(self, tianhuang):
        out = self._run(tianhuang, "今夜不要去城外竹林", "lin_wan_zhou", run_id="test_cd_intervene_a")
        for bid in ("branch_a", "branch_b"):
            path = out.run_dir / bid / "causal_diff.json"
            assert path.exists()
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data["status"] == "proposed"
            assert data["branch_id"] == bid
            assert data["compiler_version"] == "v0.7.1-C"
            assert "blocks" in data

    def test_no_compilation_no_diff(self, tianhuang):
        out = self._run(tianhuang, "今夜不要去城外竹林", "lin_wan_zhou", run_id="test_cd_intervene_b", with_compilation=False)
        assert not (out.run_dir / "branch_a" / "causal_diff.json").exists()

    def test_missing_old_text_stable(self, tianhuang):
        out = self._run(tianhuang, "今夜不要去城外竹林", "lin_wan_zhou", run_id="test_cd_intervene_c", old_text="")
        data = json.loads((out.run_dir / "branch_a" / "causal_diff.json").read_text(encoding="utf-8"))
        assert data["blocks"] == []
        assert data["reason"]


# ─── resume intervene 用 parent.chapter_text 作为 old_text ──────


class TestResumeInterveneOldText:
    def test_uses_parent_chapter_text(self, tmp_path, monkeypatch):
        import living_novel_engine.output.writer as writer_mod
        import living_novel_engine.resume.loader as loader_mod

        monkeypatch.setattr(writer_mod, "_outputs_dir", lambda: tmp_path)
        monkeypatch.setattr(loader_mod, "_outputs_dir", lambda: tmp_path)

        from living_novel_engine.output.writer import (
            write_resume_intervene_output,
            write_resume_output,
        )
        from living_novel_engine.orchestrator.worldline_brancher import (
            build_continuation_spec,
        )
        from living_novel_engine.resume import (
            build_seed_scene_state,
            build_seed_scene_state_for_intervene,
            load_parent_snapshot,
            project_characters_from_parent,
        )

        bundle = load_sample("tianhuang-night")
        llm = LLMClient(mock=True)
        inv = audit_intervention(
            build_intervention(target="lin_wan_zhou", content="今晚不要去城外竹林", intervention_type="whisper"),
            bundle.world, bundle.character_map(),
        )
        inv.story_slug = "tianhuang-night"
        inv.source_kind = "builtin"
        comp0 = _compile("今晚不要去城外竹林", "lin_wan_zhou", bundle.world, bundle.character_map())
        spec = next(s for s in build_branch_specs_from_compilation(comp0, 3) if s.branch_id == "branch_a")
        r = run_scene(bundle.world, bundle.characters, inv, spec, llm, max_rounds=2,
                      canon_excerpt=bundle.canon_chapter, canon_chapter=bundle.canon_chapter)
        intervene_out = write_run_output(inv, [r], run_id="test_cd_ch13", compilation=comp0,
                                         old_text=bundle.canon_chapter)

        parent13 = load_parent_snapshot(intervene_out.run_id, "branch_a")
        characters, world = project_characters_from_parent(parent13)
        cont_spec = build_continuation_spec(parent13.branch_seed, parent13.branch_id)
        cont = run_scene(world, characters, None, cont_spec, llm, max_rounds=2,
                         canon_excerpt=parent13.chapter_text, canon_chapter=parent13.chapter_text,
                         seed_scene_state=build_seed_scene_state(parent13),
                         seed_characters=characters, chapter_number=14)
        continue_out = write_resume_output(parent13, cont)

        parent = load_parent_snapshot(continue_out.run_id, "linear")
        characters, world = project_characters_from_parent(parent)
        inv2 = audit_intervention(
            build_intervention(target="lin_fan", content="告诉林晚舟影子来自乱葬岗", intervention_type="whisper"),
            bundle.world, bundle.character_map(),
        )
        comp = _compile("告诉林晚舟影子来自乱葬岗", "lin_fan", bundle.world, bundle.character_map())
        seed = build_seed_scene_state_for_intervene(parent, inv2.target)
        specs = build_branch_specs_from_compilation(comp, 3)
        results = [
            run_scene(world, characters, inv2, sp, llm, max_rounds=2,
                      canon_excerpt=parent.chapter_text, canon_chapter=parent.chapter_text,
                      seed_scene_state=seed, seed_characters=characters, chapter_number=15)
            for sp in specs
        ]
        out = write_resume_intervene_output(parent, inv2, results, compilation=comp)

        path = out.run_dir / "branch_a" / "causal_diff.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["status"] == "proposed"
        # parent.chapter_text 非空 → 不应是 "缺少 old_text" reason
        assert "缺少 old_text" not in data.get("reason", "")


# ─── 浏览器 additive ────────────────────────────────────────


def _write_run_with_diff(tmp_path, run_id, slug, *, with_diff=True, blocks=2):
    run_dir = tmp_path / run_id
    bdir = run_dir / "branch_a"
    bdir.mkdir(parents=True)
    (bdir / "chapter.md").write_text("# branch_a\n\n正文。", encoding="utf-8")
    (bdir / "events.json").write_text(json.dumps({"theme": "相信"}, ensure_ascii=False), encoding="utf-8")
    (bdir / "state_snapshot.json").write_text(json.dumps({"branch_theme": "相信", "characters": {}}, ensure_ascii=False), encoding="utf-8")
    (run_dir / "intervention.json").write_text(
        json.dumps({"target": "lin_wan_zhou", "content": "x", "story_slug": slug, "source_kind": "builtin"}, ensure_ascii=False),
        encoding="utf-8",
    )
    if with_diff:
        diff = {"diff_id": "diff_x", "branch_id": "branch_a", "status": "proposed",
                "blocks": [{"id": f"b{i}", "op": "replace", "old_text": "a", "new_text": "b"} for i in range(blocks)]}
        (bdir / "causal_diff.json").write_text(json.dumps(diff, ensure_ascii=False), encoding="utf-8")
    return run_dir


class TestBrowserAdditive:
    def test_summary_flags(self, tmp_path, monkeypatch):
        monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
        _write_run_with_diff(tmp_path, "run_cd1", "tianhuang-night")
        summary = indexer.index_run(tmp_path / "run_cd1")
        assert summary.branches[0].has_causal_diff is True
        assert summary.branches[0].causal_diff_count == 2

    def test_get_branch_includes_diff(self, tmp_path, monkeypatch):
        monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
        _write_run_with_diff(tmp_path, "run_cd2", "tianhuang-night")
        branch = indexer.get_branch("run_cd2", "branch_a")
        assert branch["causal_diff"] is not None
        assert branch["causal_diff"]["status"] == "proposed"

    def test_old_run_without_diff_ok(self, tmp_path, monkeypatch):
        monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
        _write_run_with_diff(tmp_path, "run_cd3", "tianhuang-night", with_diff=False)
        summary = indexer.index_run(tmp_path / "run_cd3")
        assert summary.branches[0].has_causal_diff is False
        assert summary.branches[0].causal_diff_count == 0
        branch = indexer.get_branch("run_cd3", "branch_a")
        assert branch["causal_diff"] is None

    def test_corrupt_diff_degrades(self, tmp_path, monkeypatch):
        monkeypatch.setattr(indexer, "outputs_dir", lambda: tmp_path)
        run_dir = _write_run_with_diff(tmp_path, "run_cd4", "tianhuang-night")
        (run_dir / "branch_a" / "causal_diff.json").write_text("{bad json", encoding="utf-8")
        summary = indexer.index_run(run_dir)
        assert summary.branches[0].has_causal_diff is True
        assert summary.branches[0].causal_diff_count == 0
        branch = indexer.get_branch("run_cd4", "branch_a")
        assert branch["causal_diff"] == {}
