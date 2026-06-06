import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/FactionVolumePage.tsx", "utf8");
const css = readFileSync("src/components/factionVolume.css", "utf8");

assert(
  page.includes("scrollToFactionItem"),
  "faction volume page should expose direct scroll actions",
);
assert(
  page.includes('className="faction-volume-mobile-guide"'),
  "faction volume mobile guide should be present",
);
assert(
  page.indexOf('className="faction-volume-mobile-guide"') < page.indexOf("<WorldRunway"),
  "faction volume mobile guide should appear before the explanatory runway",
);
for (const label of ["看站位", "查代偿", "换势力", "作者台"]) {
  assert(page.includes(label), `faction volume mobile guide should include ${label}`);
}
assert(
  css.includes(".faction-volume-mobile-guide") && css.includes("display: none"),
  "faction volume mobile guide should be hidden by default",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.faction-volume-mobile-guide[\s\S]*display: grid/.test(css),
  "faction volume mobile guide should be visible on mobile widths",
);

console.log("faction volume ux structure ok");
