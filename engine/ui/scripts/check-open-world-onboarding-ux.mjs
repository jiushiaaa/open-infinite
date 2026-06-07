import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const importPage = readFileSync(resolve("src/components/ImportNovelPage.tsx"), "utf8");
const genesisPage = readFileSync(resolve("src/components/GenesisPage.tsx"), "utf8");
const importCss = readFileSync(resolve("src/components/importNovel.css"), "utf8");
const genesisCss = readFileSync(resolve("src/components/genesis.css"), "utf8");

const failures = [];

function requireIncludes(source, text, message) {
  if (!source.includes(text)) failures.push(message);
}

function requireOrder(source, before, after, message) {
  const beforeIndex = source.indexOf(before);
  const afterIndex = source.indexOf(after);
  if (beforeIndex === -1 || afterIndex === -1 || beforeIndex >= afterIndex) {
    failures.push(message);
  }
}

function requireRegex(source, pattern, message) {
  if (!pattern.test(source)) failures.push(message);
}

requireIncludes(importPage, 'className="import__handoff"', "Import page should render a dedicated post-import journey rail.");
requireIncludes(importPage, 'aria-label="导入后的世界旅程"', "Import journey rail should have a clear accessible label.");
for (const label of ["世界锚定", "天命书", "世界沙盘", "卷宗阅读"]) {
  requireIncludes(importPage, label, `Import journey rail should explain the ${label} stage.`);
}
for (const state of ["slugOk", "sourceLabel", "mock", "canSubmit", "submit"]) {
  requireIncludes(importPage, state, `Import journey rail should reuse live ${state} state instead of static copy.`);
}
requireIncludes(importPage, 'fileInputRef.current?.click()', "Import journey rail should keep a direct file-pick action.");
requireIncludes(importPage, 'chaptersRef.current?.scrollIntoView', "Import journey rail should keep a direct chapter-writing action.");
requireIncludes(importPage, 'navigate({ name: "entry" })', "Import journey rail should keep a shelf exit.");
requireOrder(
  importPage,
  'className="import__command"',
  'className="import__handoff"',
  "Import journey rail should sit after the command overview.",
);
requireOrder(
  importPage,
  'className="import__handoff"',
  'className="import__form"',
  "Import journey rail should sit before the detailed form.",
);

requireIncludes(genesisPage, 'className="gen__handoff"', "Genesis page should render a dedicated post-genesis journey rail.");
requireIncludes(genesisPage, 'aria-label="创世后的世界旅程"', "Genesis journey rail should have a clear accessible label.");
for (const label of ["世界雏形", "世界锚定", "天命书", "世界沙盘"]) {
  requireIncludes(genesisPage, label, `Genesis journey rail should explain the ${label} stage.`);
}
for (const state of ["slugOk", "premiseReady", "mock", "canSubmit", "submit"]) {
  requireIncludes(genesisPage, state, `Genesis journey rail should reuse live ${state} state instead of static copy.`);
}
requireIncludes(genesisPage, 'premiseRef.current?.focus()', "Genesis journey rail should keep a direct premise-writing action.");
requireIncludes(genesisPage, 'navigate({ name: "entry" })', "Genesis journey rail should keep a shelf exit.");
requireOrder(
  genesisPage,
  'className="gen__command"',
  'className="gen__handoff"',
  "Genesis journey rail should sit after the command overview.",
);
requireOrder(
  genesisPage,
  'className="gen__handoff"',
  'className="gen__form"',
  "Genesis journey rail should sit before the detailed form.",
);

requireRegex(importCss, /\.import__handoff[\s\S]*grid-template-columns:\s*minmax\(0,\s*0\.8fr\)\s+minmax\(0,\s*1\.2fr\)/, "Import journey rail should use a stable two-column desktop layout.");
requireRegex(importCss, /\.import__handoff-stages[\s\S]*grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\)/, "Import journey rail should expose four scannable stages.");
requireRegex(importCss, /@media \(max-width: 760px\)[\s\S]*\.import__handoff[\s\S]*grid-template-columns:\s*1fr/, "Import journey rail should collapse cleanly on mobile.");
requireRegex(importCss, /@media \(max-width: 560px\)[\s\S]*\.import__handoff-stages[\s\S]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/, "Import journey stages should become two columns on narrow mobile.");

requireRegex(genesisCss, /\.gen__handoff[\s\S]*grid-template-columns:\s*minmax\(0,\s*0\.8fr\)\s+minmax\(0,\s*1\.2fr\)/, "Genesis journey rail should use a stable two-column desktop layout.");
requireRegex(genesisCss, /\.gen__handoff-stages[\s\S]*grid-template-columns:\s*repeat\(4,\s*minmax\(0,\s*1fr\)\)/, "Genesis journey rail should expose four scannable stages.");
requireRegex(genesisCss, /@media \(max-width: 760px\)[\s\S]*\.gen__handoff[\s\S]*grid-template-columns:\s*1fr/, "Genesis journey rail should collapse cleanly on mobile.");
requireRegex(genesisCss, /@media \(max-width: 560px\)[\s\S]*\.gen__handoff-stages[\s\S]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/, "Genesis journey stages should become two columns on narrow mobile.");

if (failures.length > 0) {
  console.error("Open-world onboarding UX check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("open-world onboarding journey rails ok");
