import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const page = readFileSync("src/components/WorkspacePage.tsx", "utf8");
const css = readFileSync("src/components/workspace.css", "utf8");

assert(
  page.includes("scrollToArchiveItem"),
  "workspace archive should expose direct mobile scroll actions",
);
assert(
  page.includes('className="project-workspace__mobile-guide"'),
  "workspace archive mobile guide should be present",
);
assert(
  page.indexOf('className="project-workspace__mobile-guide"') <
    page.indexOf('className="project-workspace__command"'),
  "workspace archive mobile guide should appear before the full archive command",
);
for (const label of ["天命书", "沙盘", "读卷宗", "查证据"]) {
  assert(page.includes(label), `workspace archive mobile guide should include ${label}`);
}
for (const targetClass of [
  "project-workspace__metrics",
  "runtime-preflight",
  "project-workspace__section",
]) {
  assert(page.includes(targetClass), `workspace archive should keep ${targetClass}`);
}
assert(
  css.includes(".project-workspace__mobile-guide") && css.includes("display: none"),
  "workspace archive mobile guide should be hidden by default",
);
assert(
  /@media \(max-width: 760px\)[\s\S]*\.project-workspace__mobile-guide[\s\S]*display: grid/.test(
    css,
  ),
  "workspace archive mobile guide should be visible on mobile widths",
);

console.log("workspace archive ux structure ok");
