import assert from "node:assert/strict";
import { deriveDossierReadingFocus } from "../.tmp-dossier-reading-focus/dossierReadingFocus.js";

const sections = [
  {
    id: "s1",
    title: "雨夜起誓",
    viewpoint: "赵玄",
    narrative_role: "开场钩子",
    evidence_refs: ["memory:zhao"],
  },
  {
    id: "s2",
    title: "殿前误判",
    viewpoint: "",
    narrative_role: "冲突转折",
    evidence_refs: [],
    evidence_mode: { refs: ["ledger:debt", "trace:round"] },
  },
  {
    id: "s3",
    title: "",
    viewpoint: "",
    narrative_role: "",
    evidence_refs: [],
  },
];

const middle = deriveDossierReadingFocus({
  sections,
  activeSectionId: "s2",
  totalEvidenceCount: 9,
  misbeliefCount: 4,
});

assert.equal(middle.currentIndex, 1);
assert.equal(middle.positionLabel, "02 / 03");
assert.equal(middle.title, "殿前误判");
assert.equal(middle.roleLabel, "冲突转折");
assert.equal(middle.evidenceLabel, "本场 2 条证据 · 全卷 9 条");
assert.equal(middle.misbeliefLabel, "4 条误会可追");
assert.equal(middle.previousSectionId, "s1");
assert.equal(middle.nextSectionId, "s3");

const fallback = deriveDossierReadingFocus({
  sections,
  activeSectionId: "missing",
  totalEvidenceCount: 0,
  misbeliefCount: 0,
});

assert.equal(fallback.currentIndex, 0);
assert.equal(fallback.positionLabel, "01 / 03");
assert.equal(fallback.title, "雨夜起誓");
assert.equal(fallback.roleLabel, "赵玄");
assert.equal(fallback.evidenceLabel, "本场 1 条证据");
assert.equal(fallback.misbeliefLabel, "暂无误会图谱");
assert.equal(fallback.previousSectionId, null);
assert.equal(fallback.nextSectionId, "s2");

const empty = deriveDossierReadingFocus({
  sections: [],
  activeSectionId: "",
  totalEvidenceCount: 0,
  misbeliefCount: 0,
});

assert.equal(empty, null);

console.log("dossier reading focus helper ok");
