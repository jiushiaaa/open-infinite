import {
  Component,
  lazy,
  Suspense,
  useEffect,
  type ComponentType,
  type ErrorInfo,
  type ReactNode,
} from "react";
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

class RouteChunkBoundary extends Component<
  { children: ReactNode; resetKey: string },
  { failed: boolean }
> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Route chunk load failed", error, errorInfo);
  }

  componentDidUpdate(previousProps: { resetKey: string }) {
    if (previousProps.resetKey !== this.props.resetKey && this.state.failed) {
      this.setState({ failed: false });
    }
  }

  render() {
    if (this.state.failed) {
      return (
        <div className="route-error" role="alert">
          <div className="route-error__panel">
            <small>世界卷宗没有展开</small>
            <strong>这一页的材料加载失败了</strong>
            <span>可以重新展开当前页面，或先回世界书架再进入。</span>
            <div className="route-error__actions">
              <button
                className="btn btn--primary tiny"
                onClick={() => window.location.reload()}
                type="button"
              >
                重新展开
              </button>
              <button
                className="btn btn--ghost tiny"
                onClick={() => {
                  window.location.hash = "#/";
                }}
                type="button"
              >
                回世界书架
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export function App() {
  const route = useRoute();
  useEffect(() => {
    writeRecentReading(window.localStorage, route);
  }, [route]);

  return (
    <AppShell route={route}>
      <RouteChunkBoundary resetKey={window.location.hash}>
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
      </RouteChunkBoundary>
    </AppShell>
  );
}
