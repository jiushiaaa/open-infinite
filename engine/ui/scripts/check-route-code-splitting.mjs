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

if (!app.includes("class RouteChunkBoundary")) {
  failures.push("App should include a route chunk error boundary for failed lazy imports");
}

if (!app.includes("componentDidCatch")) {
  failures.push("route chunk error boundary should record lazy route load errors");
}

if (!app.includes("componentDidUpdate") || !app.includes("resetKey")) {
  failures.push("route chunk error boundary should reset when the route changes");
}

if (!app.includes("<RouteChunkBoundary resetKey={window.location.hash}>")) {
  failures.push("routed pages should be wrapped by RouteChunkBoundary with a route reset key");
}

if (!app.includes("世界卷宗没有展开") || !app.includes("重新展开") || !app.includes("回世界书架")) {
  failures.push("route chunk error state should use Chinese recovery copy and actions");
}

if (!app.includes("window.location.reload()") || !app.includes("window.location.hash = \"#/\"")) {
  failures.push("route chunk error state should let users retry or return to the story shelf");
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
