import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/CheckpointReplayPage.tsx", "utf8");
const css = readFileSync("src/components/worldlineDossier.css", "utf8");

assert(
  page.includes("scrollToCheckpointItem"),
  "checkpoint replay page should expose direct scroll actions",
);
assert(page.includes("replayMode"), "checkpoint replay page should track a replay mode");
assert(
  page.includes("checkpoint-replay-mode"),
  "checkpoint replay page should expose a mode switch",
);
assert(page.includes("读报告"), "checkpoint replay mode should include a report option");
assert(page.includes("查证据"), "checkpoint replay mode should include an evidence option");
assert(
  page.includes("worldline-layout--${replayMode}"),
  "checkpoint replay mode should affect the layout",
);
assert(
  page.includes("openEvidenceMode(\".worldline-memory-section\")") &&
    page.includes("openEvidenceMode(\".worldline-consequence-section\")"),
  "mobile memory and consequence actions should reveal evidence mode before scrolling",
);
assert(
  page.includes('className="checkpoint-mobile-guide"'),
  "checkpoint replay mobile guide should be present",
);
assert(
  page.indexOf('className="checkpoint-mobile-guide"') < page.indexOf("<WorldRunway"),
  "checkpoint replay mobile guide should appear before the explanatory runway",
);
assert(
  page.indexOf('className="checkpoint-mobile-guide"') <
    page.indexOf('className="worldline-command"'),
  "checkpoint replay mobile guide should appear before the full workflow summary",
);
assert(
  page.includes('className="checkpoint-wake-handoff"'),
  "checkpoint replay page should include a wake handoff rail",
);
assert(
  page.indexOf("<WorldRunway") < page.indexOf('className="checkpoint-wake-handoff"'),
  "checkpoint wake handoff rail should appear after the explanatory runway",
);
assert(
  page.indexOf('className="checkpoint-wake-handoff"') <
    page.indexOf("<main className={`worldline-layout worldline-layout--${replayMode}`}>"),
  "checkpoint wake handoff rail should appear before the detailed replay layout",
);
for (const label of [
  "检查点醒来接力台",
  "醒来大事",
  "谁记住了",
  "代偿压力",
  "接回正文",
  "把醒来报告送到作者台",
]) {
  assert(page.includes(label), `checkpoint wake handoff rail should include ${label}`);
}
for (const field of [
  "primaryMemory",
  "primaryCompensation",
  "readableEntry",
  "report.checkpoint",
  "report.readable_entry",
]) {
  assert(page.includes(field), `checkpoint wake handoff rail should use ${field}`);
}
for (const label of ["继续读", "看记忆", "看代偿", "作者台"]) {
  assert(page.includes(label), `checkpoint replay mobile guide should include ${label}`);
}
for (const targetClass of [
  "worldline-wake-bridge",
  "worldline-memory-section",
  "worldline-consequence-section",
]) {
  assert(page.includes(targetClass), `checkpoint replay page should keep ${targetClass}`);
}
assert(
  css.includes(".checkpoint-mobile-guide") && css.includes("display: none"),
  "checkpoint replay mobile guide should be hidden by default",
);
assert(css.includes(".checkpoint-wake-handoff"), "checkpoint wake handoff rail should have styles");
assert(
  /\.checkpoint-wake-handoff[\s\S]*grid-template-columns: repeat\(4, minmax\(0, 1fr\)\)/.test(
    css,
  ),
  "checkpoint wake handoff rail should render four stable desktop cards",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.checkpoint-wake-handoff[\s\S]*grid-template-columns: 1fr/.test(
    css,
  ),
  "checkpoint wake handoff rail should collapse to one column on mobile",
);
assert(css.includes(".checkpoint-replay-mode"), "checkpoint replay mode switch should have styles");
assert(css.includes(".worldline-layout--report"), "checkpoint report mode should have layout styles");
assert(
  /\.worldline-layout--report \.worldline-summary,[\s\S]*\.worldline-layout--report \.worldline-consequence-section[\s\S]*display: none/.test(
    css,
  ),
  "report mode should hide evidence sections without removing them",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.checkpoint-mobile-guide[\s\S]*display: grid/.test(css),
  "checkpoint replay mobile guide should be visible on mobile widths",
);

console.log("checkpoint replay ux structure ok");
