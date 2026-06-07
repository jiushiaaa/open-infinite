import { lazy, Suspense, useEffect, type ComponentType } from "react";
import { AppShell } from "./components/AppShell";
import { writeRecentReading } from "./readingProgress";
import { useRoute } from "./routing";

function loadPage(
  importer: () => Promise<Record<string, unknown>>,
  exportName: string,
) {
  return importer().then((module) => ({
    default: module[exportName] as ComponentType<any>,
  }));
}

const StoryEntryPage = lazy(() =>
  loadPage(() => import("./components/StoryEntryPage"), "StoryEntryPage"),
);
const WorkspacePage = lazy(() =>
  loadPage(() => import("./components/WorkspacePage"), "WorkspacePage"),
);
const WorldAnchorPage = lazy(() =>
  loadPage(() => import("./components/WorldAnchorPage"), "WorldAnchorPage"),
);
const ImportNovelPage = lazy(() =>
  loadPage(() => import("./components/ImportNovelPage"), "ImportNovelPage"),
);
const GenesisPage = lazy(() =>
  loadPage(() => import("./components/GenesisPage"), "GenesisPage"),
);
const WorldSandboxPage = lazy(() =>
  loadPage(() => import("./components/WorldSandboxPage"), "WorldSandboxPage"),
);
const TianmingPage = lazy(() =>
  loadPage(() => import("./components/TianmingPage"), "TianmingPage"),
);
const CharacterLensPage = lazy(() =>
  loadPage(() => import("./components/CharacterLensPage"), "CharacterLensPage"),
);
const AuthorAdoptionPage = lazy(() =>
  loadPage(() => import("./components/AuthorAdoptionPage"), "AuthorAdoptionPage"),
);
const WorldlineDossierPage = lazy(() =>
  loadPage(() => import("./components/WorldlineDossierPage"), "WorldlineDossierPage"),
);
const DossierReadingPage = lazy(() =>
  loadPage(() => import("./components/DossierReadingPage"), "DossierReadingPage"),
);
const WorldVolumePage = lazy(() =>
  loadPage(() => import("./components/WorldVolumePage"), "WorldVolumePage"),
);
const LonglineReadingPage = lazy(() =>
  loadPage(() => import("./components/LonglineReadingPage"), "LonglineReadingPage"),
);
const CharacterVolumePage = lazy(() =>
  loadPage(() => import("./components/CharacterVolumePage"), "CharacterVolumePage"),
);
const FactionVolumePage = lazy(() =>
  loadPage(() => import("./components/FactionVolumePage"), "FactionVolumePage"),
);
const EventPerspectivePage = lazy(() =>
  loadPage(() => import("./components/EventPerspectivePage"), "EventPerspectivePage"),
);
const CheckpointReplayPage = lazy(() =>
  loadPage(() => import("./components/CheckpointReplayPage"), "CheckpointReplayPage"),
);

function RouteLoading() {
  return (
    <div className="route-loading" role="status" aria-live="polite">
      <span>正在展开世界卷宗</span>
    </div>
  );
}

export function App() {
  const route = useRoute();
  useEffect(() => {
    writeRecentReading(window.localStorage, route);
  }, [route]);

  return (
    <AppShell route={route}>
      <Suspense fallback={<RouteLoading />}>
        {route.name === "workspace" && <WorkspacePage slug={route.slug} />}
        {route.name === "sandbox" && <WorldSandboxPage slug={route.slug} />}
        {route.name === "tianming" && <TianmingPage slug={route.slug} />}
        {route.name === "lens" && <CharacterLensPage slug={route.slug} />}
        {route.name === "author" && <AuthorAdoptionPage slug={route.slug} />}
        {route.name === "worldline" && (
          <WorldlineDossierPage slug={route.slug} worldlineId={route.worldlineId} />
        )}
        {route.name === "dossierReading" && (
          <DossierReadingPage
            slug={route.slug}
            worldlineId={route.worldlineId}
            initialTab={route.tab}
          />
        )}
        {route.name === "worldChronicle" && (
          <WorldVolumePage
            slug={route.slug}
            worldlineId={route.worldlineId}
            volumeKind="chronicle"
          />
        )}
        {route.name === "anchorVolume" && (
          <WorldVolumePage
            slug={route.slug}
            worldlineId={route.worldlineId}
            volumeKind="anchor"
          />
        )}
        {route.name === "longlineReading" && (
          <LonglineReadingPage slug={route.slug} worldlineId={route.worldlineId} />
        )}
        {route.name === "characterVolume" && (
          <CharacterVolumePage
            slug={route.slug}
            worldlineId={route.worldlineId}
            characterId={route.characterId}
          />
        )}
        {route.name === "factionVolume" && (
          <FactionVolumePage
            slug={route.slug}
            worldlineId={route.worldlineId}
            factionId={route.factionId}
          />
        )}
        {route.name === "eventPerspective" && (
          <EventPerspectivePage
            slug={route.slug}
            worldlineId={route.worldlineId}
            eventId={route.eventId}
          />
        )}
        {route.name === "checkpoint" && (
          <CheckpointReplayPage
            slug={route.slug}
            worldlineId={route.worldlineId}
            runId={route.runId}
            checkpointId={route.checkpointId}
          />
        )}
        {route.name === "anchor" && <WorldAnchorPage slug={route.slug} />}
        {route.name === "import" && <ImportNovelPage />}
        {route.name === "genesis" && <GenesisPage />}
        {route.name === "entry" && <StoryEntryPage />}
      </Suspense>
    </AppShell>
  );
}
