import { useState, type ReactNode } from "react";
import { navigate, type Route } from "../routing";
import { useMotionPref } from "../motion";
import { readRecentReading, shouldShowRecentReading } from "../readingProgress";
import { getWorldRouteContext } from "../worldRouteContext";
import { SettingsDrawer } from "./SettingsDrawer";
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
  const activeStageRoute = routeContext?.stages.find((stage) => stage.status === "active")?.route;
  const worldlineDossierRoute = routeContext?.dossiers.find(
    (dossier) => dossier.key === "worldline",
  )?.route;

  const cycleMotion = () =>
    setMotion(motion === "auto" ? "full" : motion === "full" ? "reduced" : "auto");

  return (
    <div className="shell">
      <header className="topbar">
        <div className="topbar__left">
          <button
            className="brand"
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
                onClick={() => navigate({ name: "anchor", slug })}
                title="回到世界锚定，检查角色、规则和导入结果"
              >
                锚定
              </button>
              <button
                className={active === "tianming" ? "is-active" : ""}
                onClick={() => navigate({ name: "tianming", slug })}
                title="确认叙事吸引子、锚点和干预边界"
              >
                天命书
              </button>
              <button
                className={active === "sandbox" ? "is-active" : ""}
                onClick={() => navigate({ name: "sandbox", slug })}
                title="运行角色行动、干预投放和世界自演"
              >
                沙盘
              </button>
              <button
                className={active === "reading" ? "is-active" : ""}
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
                onClick={() =>
                  navigate({ name: "worldline", slug, worldlineId: currentWorldline })
                }
                title="查看因果债、检查点和世界线承接"
              >
                世界线
              </button>
              <button
                className={active === "lens" ? "is-active" : ""}
                onClick={() => navigate({ name: "lens", slug })}
                title="生成世界正史卷、角色个人卷和事件多视角"
              >
                多视角
              </button>
              <button
                className={active === "author" ? "is-active" : ""}
                onClick={() => navigate({ name: "author", slug })}
                title="把沙盘涌现剧情采纳为下一章材料"
              >
                作者台
              </button>
              <button
                className={active === "workspace" ? "is-active" : ""}
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
        <section className="shell-context" aria-label="当前世界位置">
          <div className="shell-context__copy">
            <span className="shell-context__eyebrow">当前位置 · {routeContext.sectionLabel}</span>
            <strong>{routeContext.title}</strong>
            <span>{routeContext.description}</span>
          </div>
          <div className="shell-context__workspace" aria-label="世界工作区总览">
            <button
              className="shell-context__workspace-card"
              onClick={() => activeStageRoute && navigate(activeStageRoute)}
              title="回到当前旅程环节的主入口"
              type="button"
            >
              <small>当前环节</small>
              <strong>
                {routeContext.workspaceSummary.stageLabel} ·{" "}
                {routeContext.workspaceSummary.stageTitle}
              </strong>
            </button>
            <button
              className="shell-context__workspace-card"
              onClick={() => worldlineDossierRoute && navigate(worldlineDossierRoute)}
              title="查看这条世界线的检查点、因果债和代偿"
              type="button"
            >
              <small>承接世界线</small>
              <strong>{routeContext.workspaceSummary.worldlineLabel}</strong>
            </button>
            <button
              className="shell-context__workspace-card shell-context__workspace-card--next"
              onClick={() => navigate(routeContext.primaryRoute)}
              title={routeContext.workspaceSummary.why}
              type="button"
            >
              <small>下一步为什么做</small>
              <strong>{routeContext.workspaceSummary.nextStepLabel}</strong>
              <em>{routeContext.workspaceSummary.why}</em>
            </button>
          </div>
          <div className="shell-context__stages" aria-label="世界体验轨道">
            {routeContext.stages.map((stage) => (
              <button
                key={stage.key}
                className={stage.status === "active" ? "is-active" : ""}
                onClick={() => navigate(stage.route)}
                type="button"
              >
                <span>{stage.label}</span>
                <strong>{stage.title}</strong>
              </button>
            ))}
          </div>
          <nav className="shell-context__dossiers" aria-label="世界卷宗速览">
            {routeContext.dossiers.map((dossier) => (
              <button
                key={dossier.key}
                className={dossier.status === "active" ? "is-active" : ""}
                onClick={() => navigate(dossier.route)}
                title={dossier.title}
                type="button"
              >
                <span>{dossier.label}</span>
                <strong>{dossier.title}</strong>
              </button>
            ))}
          </nav>
          <div className="shell-context__actions">
            {showRecentReading && recentReading && (
              <button
                className="btn btn--ghost tiny shell-context__resume"
                onClick={() => {
                  window.location.hash = recentReading.hash;
                }}
                title={`${recentReading.title} · ${recentReading.worldlineId}`}
                type="button"
              >
                继续阅读
              </button>
            )}
            <button
              className="btn btn--primary tiny"
              onClick={() => navigate(routeContext.primaryRoute)}
            >
              {routeContext.primaryActionLabel}
            </button>
            {routeContext.secondaryRoute && routeContext.secondaryActionLabel && (
              <button
                className="btn btn--ghost tiny"
                onClick={() => navigate(routeContext.secondaryRoute!)}
              >
                {routeContext.secondaryActionLabel}
              </button>
            )}
          </div>
        </section>
      )}
      <main className="shell__body">{children}</main>
      <SettingsDrawer open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}
