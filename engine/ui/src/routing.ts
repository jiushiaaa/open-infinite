import { useEffect, useState } from "react";

// 极简 hash 路由，避免引入 react-router。
// "#/"                          → 故事入口
// "#/workspace/<slug>"          → 阅读工作台
// "#/world/<slug>/sandbox"      → 世界沙盘
// "#/world/<slug>/tianming"     → 天命书
// "#/world/<slug>/lens"         → 多视角活体小说
// "#/world/<slug>/author"       → 作者采纳台
// "#/anchor/<slug>"             → 世界锚定页
// "#/import"                    → 导入小说
// "#/genesis"                   → 主题创世
export type Route =
  | { name: "entry" }
  | { name: "workspace"; slug: string }
  | { name: "sandbox"; slug: string }
  | { name: "tianming"; slug: string }
  | { name: "lens"; slug: string }
  | { name: "author"; slug: string }
  | { name: "anchor"; slug: string }
  | { name: "import" }
  | { name: "genesis" };

function parseHash(): Route {
  const hash = window.location.hash.replace(/^#/, "");
  const parts = hash.split("/").filter(Boolean);
  if (parts[0] === "workspace" && parts[1]) {
    return { name: "workspace", slug: decodeURIComponent(parts[1]) };
  }
  if (parts[0] === "world" && parts[1] && parts[2] === "sandbox") {
    return { name: "sandbox", slug: decodeURIComponent(parts[1]) };
  }
  if (parts[0] === "world" && parts[1] && parts[2] === "tianming") {
    return { name: "tianming", slug: decodeURIComponent(parts[1]) };
  }
  if (parts[0] === "world" && parts[1] && parts[2] === "lens") {
    return { name: "lens", slug: decodeURIComponent(parts[1]) };
  }
  if (parts[0] === "world" && parts[1] && parts[2] === "author") {
    return { name: "author", slug: decodeURIComponent(parts[1]) };
  }
  if (parts[0] === "anchor" && parts[1]) {
    return { name: "anchor", slug: decodeURIComponent(parts[1]) };
  }
  if (parts[0] === "import") {
    return { name: "import" };
  }
  if (parts[0] === "genesis") {
    return { name: "genesis" };
  }
  return { name: "entry" };
}

export function navigate(route: Route): void {
  let next = "#/";
  if (route.name === "workspace") next = `#/workspace/${encodeURIComponent(route.slug)}`;
  else if (route.name === "sandbox") {
    next = `#/world/${encodeURIComponent(route.slug)}/sandbox`;
  }
  else if (route.name === "tianming") {
    next = `#/world/${encodeURIComponent(route.slug)}/tianming`;
  }
  else if (route.name === "lens") {
    next = `#/world/${encodeURIComponent(route.slug)}/lens`;
  }
  else if (route.name === "author") {
    next = `#/world/${encodeURIComponent(route.slug)}/author`;
  }
  else if (route.name === "anchor") next = `#/anchor/${encodeURIComponent(route.slug)}`;
  else if (route.name === "import") next = "#/import";
  else if (route.name === "genesis") next = "#/genesis";
  if (window.location.hash !== next) {
    window.location.hash = next;
  }
}

export function useRoute(): Route {
  const [route, setRoute] = useState<Route>(parseHash);
  useEffect(() => {
    const onChange = () => setRoute(parseHash());
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);
  return route;
}
