import { useState, type ReactNode } from "react";
import { navigate, type Route } from "../routing";
import { useMotionPref } from "../motion";
import { readRecentReading, shouldShowRecentReading } from "../readingProgress";
import { preloadRoutePage } from "../routePagePreload";
import { getWorldRouteContext } from "../worldRouteContext";
import { SettingsDrawer } from "./SettingsDrawer";
import { WorldWorkspaceShell } from "./WorldWorkspaceShell";
import "./appShell.css";

const MOTION_LABEL: Record<string, string> = {
  auto: "动效·跟随系统",
  full: "动效·开",
  reduced: "动效·弱",
};

const ROUTE_LABELS: Partial<Record<Route["name"], string>> = {
  workspace: "正史与机制",
  sandbox: "世界沙盘",
  tianming: "天命书",
  lens: "多视角",
  author: "作者采纳台",
  worldline: "世界线",
  dossierReading: "卷宗阅读",
  longlineReading: "长线卷",
  characterVolume: "角色个人卷",
  factionVolume: "势力卷",
  eventPerspective: "事件多视角",
  checkpoint: "检查点",
  anchor: "世界锚定",
  import: "导入小说",
  genesis: "主题创世",
};

function worldSlug(route: Route): string | null {
  if (
    route.name === "workspace" ||
    route.name === "sandbox" ||
    route.name === "tianming" ||
    route.name === "lens" ||
    route.name === "author" ||
    route.name === "worldline" ||
    route.name === "dossierReading" ||
    route.name === "longlineReading" ||
    route.name === "characterVolume" ||
    route.name === "factionVolume" ||
    route.name === "eventPerspective" ||
    route.name === "checkpoint" ||
    route.name === "anchor"
  ) {
    return route.slug;
  }
  return null;
}

function worldlineId(route: Route): string {
  if (
    route.name === "worldline" ||
    route.name === "dossierReading" ||
    route.name === "longlineReading" ||
    route.name === "characterVolume" ||
    route.name === "factionVolume" ||
    route.name === "eventPerspective" ||
    route.name === "checkpoint"
  ) {
    return route.worldlineId;
  }
  return "main";
}

function activeSection(route: Route): string {
  if (route.name === "checkpoint") return "worldline";
  if (route.name === "characterVolume") return "character";
  if (route.name === "factionVolume") return "faction";
  if (route.name === "eventPerspective") return "event";
  if (route.name === "longlineReading") return "longline";
  if (route.name === "dossierReading") return "reading";
  return route.name;
}

export function AppShell({
  route,
  children,
}: {
  route: Route;
  children: ReactNode;
}) {
  const [motion, setMotion] = useMotionPref();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const slug = worldSlug(route);
  const currentWorldline = worldlineId(route);
  const active = activeSection(route);
  const routeContext = getWorldRouteContext(route);
  const recentReading = slug ? readRecentReading(window.localStorage, slug) : null;
  const showRecentReading = shouldShowRecentReading(window.location.hash, recentReading);

  const cycleMotion = () =>
    setMotion(motion === "auto" ? "full" : motion === "full" ? "reduced" : "auto");
  const routeIntent = (target: Route) => ({
    onMouseEnter: () => preloadRoutePage(target),
    onFocus: () => preloadRoutePage(target),
    onPointerDown: () => preloadRoutePage(target),
  });

  return (
    <div className="shell">
      <a className="skip-link" href="#main-content">
        跳到当前页面内容
      </a>
      <header className="topbar">
        <div className="topbar__left">
          <button
            className="brand"
            {...routeIntent({ name: "entry" })}
            onClick={() => navigate({ name: "entry" })}
            title="返回故事入口"
          >
            <span className="brand__seal" aria-hidden>
              未
            </span>
            <span className="brand__copy">
              <span className="brand__name">未终章</span>
              <span className="brand__tag">世界沙盘</span>
            </span>
          </button>
          <span className="topbar__crumb muted tiny">
            {slug
              ? `${slug} · ${ROUTE_LABELS[route.name] ?? "世界卷宗"}`
              : ROUTE_LABELS[route.name] ?? "世界书架"}
          </span>
        </div>
        <div className="topbar__right">
          {slug && (
            <nav className="world-nav" aria-label="世界内部卷宗">
              <button
                className={active === "anchor" ? "is-active" : ""}
                aria-current={active === "anchor" ? "page" : undefined}
                {...routeIntent({ name: "anchor", slug })}
                onClick={() => navigate({ name: "anchor", slug })}
                title="回到世界锚定，检查角色、规则和导入结果"
              >
                锚定
              </button>
              <button
                className={active === "tianming" ? "is-active" : ""}
                aria-current={active === "tianming" ? "page" : undefined}
                {...routeIntent({ name: "tianming", slug })}
                onClick={() => navigate({ name: "tianming", slug })}
                title="确认叙事吸引子、锚点和干预边界"
              >
                天命书
              </button>
              <button
                className={active === "sandbox" ? "is-active" : ""}
                aria-current={active === "sandbox" ? "page" : undefined}
                {...routeIntent({ name: "sandbox", slug })}
                onClick={() => navigate({ name: "sandbox", slug })}
                title="运行角色行动、干预投放和世界自演"
              >
                沙盘
              </button>
              <button
                className={active === "reading" ? "is-active" : ""}
                aria-current={active === "reading" ? "page" : undefined}
                {...routeIntent({
                  name: "dossierReading",
                  slug,
                  worldlineId: currentWorldline,
                })}
                onClick={() =>
                  navigate({
                    name: "dossierReading",
                    slug,
                    worldlineId: currentWorldline,
                  })
                }
                title="按小说正文和卷宗视角阅读世界结果"
              >
                阅读
              </button>
              <button
                className={active === "longline" ? "is-active" : ""}
                aria-current={active === "longline" ? "page" : undefined}
                {...routeIntent({
                  name: "longlineReading",
                  slug,
                  worldlineId: currentWorldline,
                })}
                onClick={() =>
                  navigate({
                    name: "longlineReading",
                    slug,
                    worldlineId: currentWorldline,
                  })
                }
                title="查看事件、角色记忆、势力压力和作者承接如何跨事件发酵"
              >
                长线卷
              </button>
              {route.name === "characterVolume" && (
                <button
                  className="is-active"
                  aria-current="page"
                  {...routeIntent({
                    name: "characterVolume",
                    slug,
                    worldlineId: currentWorldline,
                    characterId: route.characterId,
                  })}
                  onClick={() =>
                    navigate({
                      name: "characterVolume",
                      slug,
                      worldlineId: currentWorldline,
                      characterId: route.characterId,
                    })
                  }
                  title="查看这个角色的主观记忆、误会和个人卷"
                >
                  角色卷
                </button>
              )}
              {route.name === "factionVolume" && (
                <button
                  className="is-active"
                  aria-current="page"
                  {...routeIntent({
                    name: "factionVolume",
                    slug,
                    worldlineId: currentWorldline,
                    factionId: route.factionId,
                  })}
                  onClick={() =>
                    navigate({
                      name: "factionVolume",
                      slug,
                      worldlineId: currentWorldline,
                      factionId: route.factionId,
                    })
                  }
                  title="查看势力的立场、资源压力和世界代偿"
                >
                  势力卷
                </button>
              )}
              {route.name === "eventPerspective" && (
                <button
                  className="is-active"
                  aria-current="page"
                  {...routeIntent({
                    name: "eventPerspective",
                    slug,
                    worldlineId: currentWorldline,
                    eventId: route.eventId,
                  })}
                  onClick={() =>
                    navigate({
                      name: "eventPerspective",
                      slug,
                      worldlineId: currentWorldline,
                      eventId: route.eventId,
                    })
                  }
                  title="查看同一事件在不同角色、正史和世界状态里的分裂"
                >
                  事件卷
                </button>
              )}
              <button
                className={active === "worldline" ? "is-active" : ""}
                aria-current={active === "worldline" ? "page" : undefined}
                {...routeIntent({ name: "worldline", slug, worldlineId: currentWorldline })}
                onClick={() =>
                  navigate({ name: "worldline", slug, worldlineId: currentWorldline })
                }
                title="查看因果债、检查点和世界线承接"
              >
                世界线
              </button>
              <button
                className={active === "lens" ? "is-active" : ""}
                aria-current={active === "lens" ? "page" : undefined}
                {...routeIntent({ name: "lens", slug })}
                onClick={() => navigate({ name: "lens", slug })}
                title="生成世界正史卷、角色个人卷和事件多视角"
              >
                多视角
              </button>
              <button
                className={active === "author" ? "is-active" : ""}
                aria-current={active === "author" ? "page" : undefined}
                {...routeIntent({ name: "author", slug })}
                onClick={() => navigate({ name: "author", slug })}
                title="把沙盘涌现剧情采纳为下一章材料"
              >
                作者台
              </button>
              <button
                className={active === "workspace" ? "is-active" : ""}
                aria-current={active === "workspace" ? "page" : undefined}
                {...routeIntent({ name: "workspace", slug })}
                onClick={() => navigate({ name: "workspace", slug })}
                title="查看旧正史、机制档案和支撑层入口"
              >
                机制档案
              </button>
            </nav>
          )}
          <button
            className="btn btn--ghost tiny"
            onClick={cycleMotion}
            title="切换强反馈动效（服务于因果可见，可降级）"
          >
            {MOTION_LABEL[motion]}
          </button>
          <button
            className="btn btn--ghost tiny"
            onClick={() => setSettingsOpen(true)}
            title="模型连接与默认运行参数"
          >
            设置
          </button>
        </div>
      </header>
      {routeContext && (
        <WorldWorkspaceShell
          routeContext={routeContext}
          recentReading={recentReading}
          showRecentReading={showRecentReading}
        />
      )}
      <main id="main-content" className="shell__body" tabIndex={-1}>
        {children}
      </main>
      <SettingsDrawer open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}
