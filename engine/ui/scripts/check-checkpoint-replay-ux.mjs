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
