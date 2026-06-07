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
assert(
  page.includes('className="character-memory-handoff"'),
  "character volume page should include a cross-chapter memory handoff",
);
assert(
  page.indexOf("<WorldRunway") < page.indexOf('className="character-memory-handoff"'),
  "character memory handoff should appear after the explanatory runway",
);
assert(
  page.indexOf('className="character-memory-handoff"') <
    page.indexOf('className="character-volume-layout"'),
  "character memory handoff should appear before the long reading layout",
);
for (const label of ["记忆接力台", "当前立场", "最新记忆", "首要误会", "下一轮行动", "把角色弧送到作者台"]) {
  assert(page.includes(label), `character memory handoff should include ${label}`);
}
for (const field of ["latestMemory", "memoryStats", "misbeliefs", "memory_influence"]) {
  assert(page.includes(field), `character memory handoff should use ${field}`);
}
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
assert(
  css.includes(".character-memory-handoff") &&
    css.includes("grid-template-columns: minmax(220px, 0.8fr) repeat(3, minmax(0, 1fr))"),
  "character memory handoff should use a stable desktop grid",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.character-memory-handoff[\s\S]*grid-template-columns: 1fr/.test(css),
  "character memory handoff should collapse to one column on mobile widths",
);

console.log("character volume ux structure ok");
