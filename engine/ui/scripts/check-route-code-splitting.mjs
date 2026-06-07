import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

const app = readFileSync(resolve("src/App.tsx"), "utf8");
const appShell = readFileSync(resolve("src/components/AppShell.tsx"), "utf8");
const packageJson = JSON.parse(readFileSync(resolve("package.json"), "utf8"));
const preloadPath = resolve("src/routePagePreload.ts");
const routePagePreload = existsSync(preloadPath) ? readFileSync(preloadPath, "utf8") : "";

const failures = [];

const routePages = [
  ["entry", "StoryEntryPage"],
  ["workspace", "WorkspacePage"],
  ["anchor", "WorldAnchorPage"],
  ["import", "ImportNovelPage"],
  ["genesis", "GenesisPage"],
  ["sandbox", "WorldSandboxPage"],
  ["tianming", "TianmingPage"],
  ["lens", "CharacterLensPage"],
  ["author", "AuthorAdoptionPage"],
  ["worldline", "WorldlineDossierPage"],
  ["dossierReading", "DossierReadingPage"],
  ["worldChronicle", "WorldVolumePage"],
  ["anchorVolume", "WorldVolumePage"],
  ["longlineReading", "LonglineReadingPage"],
  ["characterVolume", "CharacterVolumePage"],
  ["factionVolume", "FactionVolumePage"],
  ["eventPerspective", "EventPerspectivePage"],
  ["checkpoint", "CheckpointReplayPage"],
];

const highFrequencyRoutes = [
  "entry",
  "anchor",
  "tianming",
  "sandbox",
  "dossierReading",
  "longlineReading",
  "worldline",
  "lens",
  "author",
  "workspace",
];
const lazyLoaderRoutes = new Map();
for (const [routeName, pageName] of routePages) {
  if (!lazyLoaderRoutes.has(pageName)) lazyLoaderRoutes.set(pageName, routeName);
}

if (packageJson.scripts["check:route-code-splitting"] !== "node scripts/check-route-code-splitting.mjs") {
  failures.push("package.json should expose check:route-code-splitting");
}

if (!/import\s+\{[^}]*lazy[^}]*Suspense[^}]*useEffect[^}]*\}\s+from\s+"react";/.test(app)) {
  failures.push("App should import lazy and Suspense from React");
}

if (!app.includes("function loadPage")) {
  failures.push("App should centralize named-export lazy loading in a small helper");
}

if (!app.includes("import { routePageLoaders } from \"./routePagePreload\";")) {
  failures.push("App should use the shared routePageLoaders registry");
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

if (!routePagePreload.includes("export const routePageLoaders")) {
  failures.push("routePagePreload should export the shared routePageLoaders registry");
}

if (!routePagePreload.includes("export function preloadRoutePage(route: Route): void")) {
  failures.push("routePagePreload should expose a typed route prefetch helper");
}

if (
  !routePagePreload.includes("const preloadedRoutePages = new Set<Route[\"name\"]>()") ||
  !routePagePreload.includes("preloadedRoutePages.delete(route.name)")
) {
  failures.push("route prefetch should avoid duplicate work and allow retry after a failed preload");
}

for (const [routeName, pageName] of routePages) {
  const staticImportPattern = new RegExp(
    `import\\s+\\{\\s*${pageName}\\s*\\}\\s+from\\s+[\"']\\.\\/components\\/${pageName}[\"'];`,
  );
  if (staticImportPattern.test(app)) {
    failures.push(`${pageName} should not be statically imported into the first route bundle`);
  }

  if (!app.includes(`const ${pageName} = lazy(`)) {
    failures.push(`${pageName} should be lazily loaded by route`);
  }

  const lazyLoaderRoute = lazyLoaderRoutes.get(pageName);
  if (!app.includes(`loadPage(routePageLoaders.${lazyLoaderRoute}, "${pageName}")`)) {
    failures.push(`${pageName} should use the shared named-export lazy loader`);
  }

  if (!routePagePreload.includes(`${routeName}: () => import("./components/${pageName}")`)) {
    failures.push(`${routeName} should be registered in routePageLoaders`);
  }
}

if (!appShell.includes("import { preloadRoutePage } from \"../routePagePreload\";")) {
  failures.push("AppShell should import route page preloading for high-frequency navigation");
}

if (!appShell.includes("const routeIntent = (target: Route) => ({")) {
  failures.push("AppShell should centralize hover/focus/pointer route prefetch handlers");
}

for (const handler of ["onMouseEnter", "onFocus", "onPointerDown"]) {
  if (!appShell.includes(`${handler}: () => preloadRoutePage(target)`)) {
    failures.push(`routeIntent should preload on ${handler}`);
  }
}

for (const routeName of highFrequencyRoutes) {
  const routeIntentPattern = new RegExp(
    `routeIntent\\(\\{\\s*name:\\s*"${routeName}"`,
  );
  if (!routeIntentPattern.test(appShell)) {
    failures.push(`${routeName} navigation should prefetch its route chunk before click`);
  }
}

if (failures.length > 0) {
  console.error("Route code splitting check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("Route code splitting keeps the first bundle focused.");
