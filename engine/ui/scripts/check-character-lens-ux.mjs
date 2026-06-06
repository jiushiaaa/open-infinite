import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/CharacterLensPage.tsx", "utf8");
const css = readFileSync("src/components/characterLens.css", "utf8");

assert(
  page.includes("scrollToLensItem"),
  "character lens page should expose direct scroll actions",
);
assert(
  page.includes('className="lens-mobile-guide"'),
  "character lens mobile guide should be present",
);
assert(
  page.indexOf('className="lens-mobile-guide"') < page.indexOf('className="lens-command"'),
  "character lens mobile guide should appear before the full workflow summary",
);
for (const label of ["生成", "改事件", "读卷宗", "作者台"]) {
  assert(page.includes(label), `character lens mobile guide should include ${label}`);
}
for (const targetClass of ["lens-form-section", "lens-output-section"]) {
  assert(page.includes(targetClass), `character lens page should keep ${targetClass}`);
}
assert(
  css.includes(".lens-mobile-guide") && css.includes("display: none"),
  "character lens mobile guide should be hidden by default",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.lens-mobile-guide[\s\S]*display: grid/.test(css),
  "character lens mobile guide should be visible on mobile widths",
);

console.log("character lens ux structure ok");
