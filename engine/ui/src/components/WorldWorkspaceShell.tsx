import { navigate, type Route } from "../routing";
import type { RecentReading } from "../readingProgress";
import { preloadRoutePage } from "../routePagePreload";
import type { WorldRouteContext } from "../worldRouteContext";

function findScrollableParent(target: HTMLElement): HTMLElement | null {
  let current = target.parentElement;
  while (current) {
    const style = window.getComputedStyle(current);
    const canScroll = /(auto|scroll)/.test(style.overflowY);
    if (canScroll && current.scrollHeight > current.clientHeight) {
      return current;
    }
    current = current.parentElement;
  }
  return null;
}

function activateShellAction(targetId?: string) {
  if (!targetId) return;

  const scrollToTarget = () => {
    const target = document.getElementById(targetId);
    if (!target) return;

    const scroller = findScrollableParent(target);
    if (scroller) {
      const targetRect = target.getBoundingClientRect();
      const scrollerRect = scroller.getBoundingClientRect();
      scroller.scrollTo({
        top: scroller.scrollTop + targetRect.top - scrollerRect.top,
        behavior: "smooth",
      });
      return;
    }

    target.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(scrollToTarget);
  });
  window.setTimeout(scrollToTarget, 120);
}

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
  const routeIntent = (target?: Route) => ({
    onMouseEnter: () => target && preloadRoutePage(target),
    onFocus: () => target && preloadRoutePage(target),
    onPointerDown: () => target && preloadRoutePage(target),
  });

  const renderJourneyAndWorkspace = () => (
    <>
      <nav className="world-workspace-shell__journey" aria-label="世界旅程总线">
        {routeContext.stages.map((stage) => (
          <button
            key={stage.key}
            className={`world-workspace-shell__journey-item${
              stage.status === "active" ? " is-active" : ""
            }`}
            aria-current={stage.status === "active" ? "step" : undefined}
            {...routeIntent(stage.route)}
            onClick={() => navigate(stage.route)}
            type="button"
          >
            <small>{stage.label}</small>
            <strong>{stage.title}</strong>
            <span>{stage.status === "active" ? "当前所在" : "可随时进入"}</span>
          </button>
        ))}
      </nav>

      <nav className="shell-context__workspace" aria-label="世界工作区总览">
        <button
          className="shell-context__workspace-card"
          {...routeIntent(activeStageRoute)}
          onClick={() => activeStageRoute && navigate(activeStageRoute)}
          title="回到当前旅程环节的主入口"
          type="button"
        >
          <small>旅程入口</small>
          <strong>
            {routeContext.workspaceSummary.stageLabel} ·{" "}
            {routeContext.workspaceSummary.stageTitle}
          </strong>
        </button>
        <button
          className="shell-context__workspace-card"
          {...routeIntent(worldlineDossierRoute)}
          onClick={() => worldlineDossierRoute && navigate(worldlineDossierRoute)}
          title="查看这条世界线的检查点、因果债和代偿"
          type="button"
        >
          <small>世界线档案</small>
          <strong>{routeContext.workspaceSummary.worldlineLabel}</strong>
        </button>
        <button
          className="shell-context__workspace-card shell-context__workspace-card--next"
          {...routeIntent(routeContext.primaryRoute)}
          onClick={() => {
            navigate(routeContext.primaryRoute);
            activateShellAction(routeContext.primaryTargetId);
          }}
          title={routeContext.workspaceSummary.why}
          type="button"
        >
          <small>为什么建议这步</small>
          <strong>{routeContext.workspaceSummary.nextStepLabel}</strong>
          <em>{routeContext.workspaceSummary.why}</em>
        </button>
      </nav>
    </>
  );

  const renderRestNavigation = () => (
    <>
      <nav className="shell-context__handoffs" aria-label="世界状态预告">
        {routeContext.stateHandoffs.map((handoff) => (
          <button
            key={handoff.key}
            className={`shell-context__handoff-card is-${handoff.key}`}
            {...routeIntent(handoff.route)}
            onClick={() => {
              navigate(handoff.route);
              activateShellAction(handoff.targetId);
            }}
            title={handoff.detail}
            type="button"
          >
            <small>{handoff.label}</small>
            <strong>{handoff.title}</strong>
            <span>{handoff.detail}</span>
          </button>
        ))}
      </nav>

      <nav className="shell-context__continuity" aria-label="世界脉搏">
        {routeContext.continuitySignals.map((signal) => (
          <button
            key={signal.key}
            className={`shell-context__pulse is-${signal.key}`}
            {...routeIntent(signal.route)}
            onClick={() => navigate(signal.route)}
            title={signal.detail}
            type="button"
          >
            <small>{signal.label}</small>
            <strong>{signal.title}</strong>
            <span>{signal.detail}</span>
          </button>
        ))}
      </nav>

      <nav className="shell-context__stages" aria-label="世界体验轨道">
        {routeContext.stages.map((stage) => (
          <button
            key={stage.key}
            className={stage.status === "active" ? "is-active" : ""}
            aria-current={stage.status === "active" ? "step" : undefined}
            {...routeIntent(stage.route)}
            onClick={() => navigate(stage.route)}
            type="button"
          >
            <span>{stage.label}</span>
            <strong>{stage.title}</strong>
          </button>
        ))}
      </nav>

      <nav className="shell-context__dossiers" aria-label="世界卷宗速览">
        {routeContext.dossiers.map((dossier) => (
          <button
            key={dossier.key}
            className={dossier.status === "active" ? "is-active" : ""}
            aria-current={dossier.status === "active" ? "page" : undefined}
            {...routeIntent(dossier.route)}
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

      <div
        className="shell-context__taskbar world-workspace-shell__focus-band"
        aria-label="世界扫读带"
      >
        <div className="world-workspace-shell__focus-map">
          <span className="world-workspace-shell__focus-kicker">世界扫读带</span>
          <button
            className="world-workspace-shell__focus-chip"
            {...routeIntent(activeStageRoute)}
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
            className="world-workspace-shell__focus-chip"
            {...routeIntent(worldlineDossierRoute)}
            onClick={() => worldlineDossierRoute && navigate(worldlineDossierRoute)}
            title="查看这条世界线的检查点、因果债和代偿"
            type="button"
          >
            <small>承接世界线</small>
            <strong>{routeContext.workspaceSummary.worldlineLabel}</strong>
          </button>
        </div>
        <div className="shell-context__taskcopy">
          <small>当前任务 · 现在先看这一条 · 建议先做</small>
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
            {...routeIntent(routeContext.primaryRoute)}
            onClick={() => {
              navigate(routeContext.primaryRoute);
              activateShellAction(routeContext.primaryTargetId);
            }}
          >
            {routeContext.primaryActionLabel}
          </button>
          {routeContext.secondaryRoute && routeContext.secondaryActionLabel && (
            <button
              className="btn btn--ghost tiny"
              {...routeIntent(routeContext.secondaryRoute)}
              onClick={() => navigate(routeContext.secondaryRoute!)}
            >
              {routeContext.secondaryActionLabel}
            </button>
          )}
        </div>
      </div>

      <div className="world-workspace-shell__desktop-nav-top">
        {renderJourneyAndWorkspace()}
      </div>

      <div className="world-workspace-shell__desktop-nav-rest">
        {renderRestNavigation()}
      </div>

      <details className="world-workspace-shell__mobile-nav" aria-label="移动端世界导航">
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
