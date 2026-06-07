import { navigate } from "../routing";
import type { RecentReading } from "../readingProgress";
import type { WorldRouteContext } from "../worldRouteContext";

export function WorldWorkspaceShell({
  routeContext,
  recentReading,
  showRecentReading,
}: {
  routeContext: WorldRouteContext;
  recentReading: RecentReading | null;
  showRecentReading: boolean;
}) {
  const activeStageRoute = routeContext.stages.find((stage) => stage.status === "active")?.route;
  const worldlineDossierRoute = routeContext.dossiers.find(
    (dossier) => dossier.key === "worldline",
  )?.route;

  const renderJourneyAndWorkspace = () => (
    <>
      <div className="world-workspace-shell__journey" aria-label="世界旅程总线">
        {routeContext.stages.map((stage) => (
          <button
            key={stage.key}
            className={`world-workspace-shell__journey-item${
              stage.status === "active" ? " is-active" : ""
            }`}
            onClick={() => navigate(stage.route)}
            type="button"
          >
            <small>{stage.label}</small>
            <strong>{stage.title}</strong>
            <span>{stage.status === "active" ? "当前所在" : "可随时进入"}</span>
          </button>
        ))}
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
    </>
  );

  const renderRestNavigation = () => (
    <>
      <div className="shell-context__handoffs" aria-label="世界状态预告">
        {routeContext.stateHandoffs.map((handoff) => (
          <button
            key={handoff.key}
            className={`shell-context__handoff-card is-${handoff.key}`}
            onClick={() => navigate(handoff.route)}
            title={handoff.detail}
            type="button"
          >
            <small>{handoff.label}</small>
            <strong>{handoff.title}</strong>
            <span>{handoff.detail}</span>
          </button>
        ))}
      </div>

      <div className="shell-context__continuity" aria-label="世界脉搏">
        {routeContext.continuitySignals.map((signal) => (
          <button
            key={signal.key}
            className={`shell-context__pulse is-${signal.key}`}
            onClick={() => navigate(signal.route)}
            title={signal.detail}
            type="button"
          >
            <small>{signal.label}</small>
            <strong>{signal.title}</strong>
            <span>{signal.detail}</span>
          </button>
        ))}
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
    </>
  );

  return (
    <section className="shell-context world-workspace-shell" aria-label="世界工作区壳">
      <div className="shell-context__copy">
        <span className="shell-context__eyebrow">当前位置 · {routeContext.sectionLabel}</span>
        <strong>{routeContext.title}</strong>
        <span>{routeContext.description}</span>
      </div>

      <div className="world-workspace-shell__desktop-nav-top">
        {renderJourneyAndWorkspace()}
      </div>

      <div className="shell-context__taskbar" aria-label="当前任务">
        <div className="shell-context__taskcopy">
          <small>当前任务 · 建议先做</small>
          <strong>{routeContext.primaryActionLabel}</strong>
          <span>{routeContext.workspaceSummary.why}</span>
        </div>
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
      </div>

      <div className="world-workspace-shell__desktop-nav-rest">
        {renderRestNavigation()}
      </div>

      <details className="world-workspace-shell__mobile-nav">
        <summary>
          <strong>展开世界导航</strong>
          <span>旅程、脉搏、卷宗入口都在这里</span>
        </summary>
        <div className="world-workspace-shell__mobile-nav-body">
          {renderJourneyAndWorkspace()}
          {renderRestNavigation()}
        </div>
      </details>
    </section>
  );
}
