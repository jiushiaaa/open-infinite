import type { Route } from "./routing";

export const routePageLoaders = {
  entry: () => import("./components/StoryEntryPage"),
  workspace: () => import("./components/WorkspacePage"),
  anchor: () => import("./components/WorldAnchorPage"),
  import: () => import("./components/ImportNovelPage"),
  genesis: () => import("./components/GenesisPage"),
  sandbox: () => import("./components/WorldSandboxPage"),
  tianming: () => import("./components/TianmingPage"),
  lens: () => import("./components/CharacterLensPage"),
  author: () => import("./components/AuthorAdoptionPage"),
  worldline: () => import("./components/WorldlineDossierPage"),
  dossierReading: () => import("./components/DossierReadingPage"),
  worldChronicle: () => import("./components/WorldVolumePage"),
  anchorVolume: () => import("./components/WorldVolumePage"),
  longlineReading: () => import("./components/LonglineReadingPage"),
  characterVolume: () => import("./components/CharacterVolumePage"),
  factionVolume: () => import("./components/FactionVolumePage"),
  eventPerspective: () => import("./components/EventPerspectivePage"),
  checkpoint: () => import("./components/CheckpointReplayPage"),
} satisfies Record<Route["name"], () => Promise<Record<string, unknown>>>;

const preloadedRoutePages = new Set<Route["name"]>();

export function preloadRoutePage(route: Route): void {
  if (preloadedRoutePages.has(route.name)) return;
  preloadedRoutePages.add(route.name);
  void routePageLoaders[route.name]().catch(() => {
    preloadedRoutePages.delete(route.name);
  });
}
