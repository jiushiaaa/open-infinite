import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/CheckpointReplayPage.tsx", "utf8");
const css = readFileSync("src/components/worldlineDossier.css", "utf8");

assert(
  page.includes("scrollToCheckpointItem"),
  "checkpoint replay page should expose direct scroll actions",
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
assert(
  /@media \(max-width: 760px\)[\s\S]*\.checkpoint-mobile-guide[\s\S]*display: grid/.test(css),
  "checkpoint replay mobile guide should be visible on mobile widths",
);

console.log("checkpoint replay ux structure ok");
