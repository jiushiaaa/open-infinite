import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const app = readFileSync(resolve("src/App.tsx"), "utf8");
const packageJson = JSON.parse(readFileSync(resolve("package.json"), "utf8"));

const failures = [];

const routePages = [
  "StoryEntryPage",
  "WorkspacePage",
  "WorldAnchorPage",
  "ImportNovelPage",
  "GenesisPage",
  "WorldSandboxPage",
  "TianmingPage",
  "CharacterLensPage",
  "AuthorAdoptionPage",
  "WorldlineDossierPage",
  "DossierReadingPage",
  "WorldVolumePage",
  "LonglineReadingPage",
  "CharacterVolumePage",
  "FactionVolumePage",
  "EventPerspectivePage",
  "CheckpointReplayPage",
];

if (packageJson.scripts["check:route-code-splitting"] !== "node scripts/check-route-code-splitting.mjs") {
  failures.push("package.json should expose check:route-code-splitting");
}

if (!/import\s+\{[^}]*lazy[^}]*Suspense[^}]*useEffect[^}]*\}\s+from\s+"react";/.test(app)) {
  failures.push("App should import lazy and Suspense from React");
}

if (!app.includes("function loadPage")) {
  failures.push("App should centralize named-export lazy loading in a small helper");
}

if (!app.includes("<Suspense fallback={<RouteLoading />}>")) {
  failures.push("App should wrap routed pages in Suspense with a visible loading state");
}

if (!app.includes("正在展开世界卷宗")) {
  failures.push("route loading fallback should use Chinese product copy instead of a blank screen");
}

for (const pageName of routePages) {
  const staticImportPattern = new RegExp(
    `import\\s+\\{\\s*${pageName}\\s*\\}\\s+from\\s+[\"']\\.\\/components\\/${pageName}[\"'];`,
  );
  if (staticImportPattern.test(app)) {
    failures.push(`${pageName} should not be statically imported into the first route bundle`);
  }

  if (!app.includes(`const ${pageName} = lazy(`)) {
    failures.push(`${pageName} should be lazily loaded by route`);
  }

  if (!app.includes(`loadPage(() => import("./components/${pageName}"), "${pageName}")`)) {
    failures.push(`${pageName} should use the shared named-export lazy loader`);
  }
}

if (failures.length > 0) {
  console.error("Route code splitting check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("Route code splitting keeps the first bundle focused.");
