import { useState, type ReactNode } from "react";
import { navigate, type Route } from "../routing";
import { useMotionPref } from "../motion";
import { SettingsDrawer } from "./SettingsDrawer";
import "./appShell.css";

const MOTION_LABEL: Record<string, string> = {
  auto: "动效·跟随系统",
  full: "动效·开",
  reduced: "动效·弱",
};

export function AppShell({
  route,
  children,
}: {
  route: Route;
  children: ReactNode;
}) {
  const [motion, setMotion] = useMotionPref();
  const [settingsOpen, setSettingsOpen] = useState(false);

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
              墨
            </span>
            <span className="brand__name">活体小说引擎</span>
          </button>
          {route.name === "workspace" && (
            <span className="topbar__crumb muted tiny">
              阅读工作台 · {route.slug}
            </span>
          )}
          {route.name === "sandbox" && (
            <span className="topbar__crumb muted tiny">世界沙盘 · {route.slug}</span>
          )}
          {route.name === "tianming" && (
            <span className="topbar__crumb muted tiny">天命书 · {route.slug}</span>
          )}
          {route.name === "lens" && (
            <span className="topbar__crumb muted tiny">
              多视角活体小说 · {route.slug}
            </span>
          )}
          {route.name === "author" && (
            <span className="topbar__crumb muted tiny">
              作者采纳台 · {route.slug}
            </span>
          )}
          {route.name === "anchor" && (
            <span className="topbar__crumb muted tiny">世界锚定 · {route.slug}</span>
          )}
        </div>
        <div className="topbar__right">
          {route.name === "workspace" && (
            <button
              className="btn btn--ghost tiny"
              onClick={() => navigate({ name: "sandbox", slug: route.slug })}
              title="进入世界沙盘，输入大事件并观察角色行动"
            >
              世界沙盘
            </button>
          )}
          {route.name === "sandbox" && (
            <button
              className="btn btn--ghost tiny"
              onClick={() => navigate({ name: "workspace", slug: route.slug })}
              title="返回阅读工作台"
            >
              世界正史卷
            </button>
          )}
          {(route.name === "workspace" || route.name === "sandbox") && (
            <button
              className="btn btn--ghost tiny"
              onClick={() => navigate({ name: "tianming", slug: route.slug })}
              title="生成并轻量确认这部故事的天命书"
            >
              天命书
            </button>
          )}
          {(route.name === "workspace" ||
            route.name === "sandbox" ||
            route.name === "tianming") && (
            <button
              className="btn btn--ghost tiny"
              onClick={() => navigate({ name: "lens", slug: route.slug })}
              title="把同一事件生成世界正史、角色个人卷和事件多视角"
            >
              多视角
            </button>
          )}
          {(route.name === "workspace" ||
            route.name === "sandbox" ||
            route.name === "tianming" ||
            route.name === "lens") && (
            <button
              className="btn btn--ghost tiny"
              onClick={() => navigate({ name: "author", slug: route.slug })}
              title="采纳、部分采纳、另开分支或导出沙盘涌现剧情"
            >
              作者采纳台
            </button>
          )}
          {route.name === "tianming" && (
            <button
              className="btn btn--ghost tiny"
              onClick={() => navigate({ name: "sandbox", slug: route.slug })}
            >
              世界沙盘
            </button>
          )}
          {route.name === "lens" && (
            <button
              className="btn btn--ghost tiny"
              onClick={() => navigate({ name: "sandbox", slug: route.slug })}
            >
              世界沙盘
            </button>
          )}
          {route.name === "author" && (
            <button
              className="btn btn--ghost tiny"
              onClick={() => navigate({ name: "lens", slug: route.slug })}
            >
              多视角卷
            </button>
          )}
          {route.name === "anchor" && (
            <button
              className="btn btn--ghost tiny"
              onClick={() => navigate({ name: "workspace", slug: route.slug })}
            >
              返回阅读
            </button>
          )}
          <span className="badge badge--gold tiny" title="推荐榜占位（v0.7 后续）">
            推荐榜 · 待启
          </span>
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
      <main className="shell__body">{children}</main>
      <SettingsDrawer open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}
