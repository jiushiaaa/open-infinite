import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/CharacterVolumePage.tsx", "utf8");
const css = readFileSync("src/components/characterVolume.css", "utf8");

assert(
  page.includes("scrollToCharacterItem"),
  "character volume page should expose direct scroll actions",
);
assert(
  page.includes('className="character-volume-mobile-guide"'),
  "character volume mobile guide should be present",
);
assert(
  page.indexOf('className="character-volume-mobile-guide"') < page.indexOf("<WorldRunway"),
  "character volume mobile guide should appear before the explanatory runway",
);
for (const label of ["读立场", "查记忆", "换角色", "作者台"]) {
  assert(page.includes(label), `character volume mobile guide should include ${label}`);
}
assert(
  css.includes(".character-volume-mobile-guide") && css.includes("display: none"),
  "character volume mobile guide should be hidden by default",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.character-volume-mobile-guide[\s\S]*display: grid/.test(css),
  "character volume mobile guide should be visible on mobile widths",
);

console.log("character volume ux structure ok");
