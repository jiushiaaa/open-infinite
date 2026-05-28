"""Validator coverage for v0.4.1 — exhaustive bad-input audit."""

from __future__ import annotations

import pytest

from living_novel_engine.browser.validators import MAX_ID_LEN, safe_id


@pytest.mark.parametrize(
    "value",
    [
        "run_20260528_215535_8eaa75",
        "branch_a",
        "branch_b",
        "linear",
        "tianhuang-night",
        "my-story",
        "a",
        "a1",
        "a.b",
        "a_b",
        "a-b",
        "x" * MAX_ID_LEN,
        "run_20260528_215547_9579af_continue_branch_a",
        "run_20260528_215600_f42c34_resume_intervene_linear",
    ],
)
def test_accepts_legit_ids(value):
    assert safe_id(value) == value


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        " ",
        "..",
        "../etc",
        "..\\etc",
        "foo/bar",
        "foo\\bar",
        "/abs/path",
        "..%2Fetc",
        "run\x00bad",
        "中文",
        "name with space",
        "name|pipe",
        ";rm -rf /",
        "x" * (MAX_ID_LEN + 1),
        "-leading-dash",
        ".leading-dot",
        "_leading-underscore",
        "a..b",
    ],
)
def test_rejects_unsafe_ids(value):
    assert safe_id(value) is None


def test_rejects_non_string():
    assert safe_id(123) is None  # type: ignore[arg-type]
    assert safe_id(["a"]) is None  # type: ignore[arg-type]
    assert safe_id(b"run_x") is None  # type: ignore[arg-type]
