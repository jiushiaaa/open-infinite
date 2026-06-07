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
import { routePageLoaders } from "./routePagePreload";
import { useRoute, type Route } from "./routing";

function loadPage(
  importer: () => Promise<Record<string, unknown>>,
  exportName: string,
) {
  return importer().then((module) => ({
    default: module[exportName] as ComponentType<any>,
  }));
}

const StoryEntryPage = lazy(() =>
  loadPage(routePageLoaders.entry, "StoryEntryPage"),
);
const WorkspacePage = lazy(() =>
  loadPage(routePageLoaders.workspace, "WorkspacePage"),
);
const WorldAnchorPage = lazy(() =>
  loadPage(routePageLoaders.anchor, "WorldAnchorPage"),
);
const ImportNovelPage = lazy(() =>
  loadPage(routePageLoaders.import, "ImportNovelPage"),
);
const GenesisPage = lazy(() =>
  loadPage(routePageLoaders.genesis, "GenesisPage"),
);
const WorldSandboxPage = lazy(() =>
  loadPage(routePageLoaders.sandbox, "WorldSandboxPage"),
);
const TianmingPage = lazy(() =>
  loadPage(routePageLoaders.tianming, "TianmingPage"),
);
const CharacterLensPage = lazy(() =>
  loadPage(routePageLoaders.lens, "CharacterLensPage"),
);
const AuthorAdoptionPage = lazy(() =>
  loadPage(routePageLoaders.author, "AuthorAdoptionPage"),
);
const WorldlineDossierPage = lazy(() =>
  loadPage(routePageLoaders.worldline, "WorldlineDossierPage"),
);
const DossierReadingPage = lazy(() =>
  loadPage(routePageLoaders.dossierReading, "DossierReadingPage"),
);
const WorldVolumePage = lazy(() =>
  loadPage(routePageLoaders.worldChronicle, "WorldVolumePage"),
);
const LonglineReadingPage = lazy(() =>
  loadPage(routePageLoaders.longlineReading, "LonglineReadingPage"),
);
const CharacterVolumePage = lazy(() =>
  loadPage(routePageLoaders.characterVolume, "CharacterVolumePage"),
);
const FactionVolumePage = lazy(() =>
  loadPage(routePageLoaders.factionVolume, "FactionVolumePage"),
);
const EventPerspectivePage = lazy(() =>
  loadPage(routePageLoaders.eventPerspective, "EventPerspectivePage"),
);
const CheckpointReplayPage = lazy(() =>
  loadPage(routePageLoaders.checkpoint, "CheckpointReplayPage"),
);

function routeLoadingCopy(route: Route) {
  if (route.name === "sandbox") {
    return {
      title: "正在展开世界沙盘",
      detail: "角色行动、读者干预和世界代偿材料正在就位。",
    };
  }
  if (route.name === "dossierReading") {
    return {
      title: "正在展开卷宗阅读",
      detail: "连续正文、证据和误会线索正在铺开。",
    };
  }
  if (route.name === "author") {
    return {
      title: "正在展开作者采纳台",
      detail: "下一章 brief、Reviewer 和定稿材料正在接回写作台。",
    };
  }
  if (route.name === "tianming") {
    return {
      title: "正在展开天命书",
      detail: "世界宪法、锚点压力和干预边界正在整理。",
    };
  }
  if (route.name === "worldline") {
    return {
      title: "正在展开世界线档案",
      detail: "检查点、因果债和代偿记录正在汇合。",
    };
  }
  if (route.name === "longlineReading") {
    return {
      title: "正在展开跨事件长线卷",
      detail: "误会、角色记忆和势力压力正在串成后续线索。",
    };
  }
  if (route.name === "anchor") {
    return {
      title: "正在展开世界锚定",
      detail: "角色、规则和世界卷宗地图正在校准。",
    };
  }
  return {
    title: "正在展开世界卷宗",
    detail: "目标页面材料正在加载，马上接回当前世界。",
  };
}

function RouteLoading({ route }: { route: Route }) {
  const copy = routeLoadingCopy(route);
  return (
    <div className="route-loading" role="status" aria-live="polite">
      <div className="route-loading__panel">
        <small>世界房间切换中</small>
        <strong className="route-loading__title">{copy.title}</strong>
        <span className="route-loading__detail">{copy.detail}</span>
      </div>
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
        <Suspense fallback={<RouteLoading route={route} />}>
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
