import { useEffect, useState } from "react";

// 极简 hash 路由，避免引入 react-router。
// "#/"                          → 故事入口
// "#/workspace/<slug>"          → 阅读工作台
// "#/world/<slug>/sandbox"      → 世界沙盘
// "#/world/<slug>/tianming"     → 天命书
// "#/world/<slug>/lens"         → 多视角活体小说
// "#/world/<slug>/author"       → 作者采纳台
// "#/world/<slug>/worldlines/<id>" → 世界线档案
// "#/world/<slug>/worldlines/<id>/reading[/tab]" → 世界内部卷宗阅读
// "#/world/<slug>/worldlines/<id>/characters/<char>" → 角色个人卷
// "#/world/<slug>/worldlines/<id>/factions/<faction>" → 势力卷
// "#/world/<slug>/worldlines/<id>/checkpoints/<run>/<checkpoint>" → 检查点回放
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
  | { name: "worldline"; slug: string; worldlineId: string }
  | { name: "dossierReading"; slug: string; worldlineId: string; tab?: string }
  | { name: "characterVolume"; slug: string; worldlineId: string; characterId: string }
  | { name: "factionVolume"; slug: string; worldlineId: string; factionId: string }
  | {
      name: "checkpoint";
      slug: string;
      worldlineId: string;
      runId: string;
      checkpointId: string;
    }
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
  if (parts[0] === "world" && parts[1] && parts[2] === "worldlines" && parts[3]) {
    if (parts[4] === "characters" && parts[5]) {
      return {
        name: "characterVolume",
        slug: decodeURIComponent(parts[1]),
        worldlineId: decodeURIComponent(parts[3]),
        characterId: decodeURIComponent(parts[5]),
      };
    }
    if (parts[4] === "factions" && parts[5]) {
      return {
        name: "factionVolume",
        slug: decodeURIComponent(parts[1]),
        worldlineId: decodeURIComponent(parts[3]),
        factionId: decodeURIComponent(parts[5]),
      };
    }
    if (parts[4] === "checkpoints" && parts[5] && parts[6]) {
      return {
        name: "checkpoint",
        slug: decodeURIComponent(parts[1]),
        worldlineId: decodeURIComponent(parts[3]),
        runId: decodeURIComponent(parts[5]),
        checkpointId: decodeURIComponent(parts[6]),
      };
    }
    if (parts[4] === "reading") {
      return {
        name: "dossierReading",
        slug: decodeURIComponent(parts[1]),
        worldlineId: decodeURIComponent(parts[3]),
        tab: parts[5] ? decodeURIComponent(parts[5]) : undefined,
      };
    }
    return {
      name: "worldline",
      slug: decodeURIComponent(parts[1]),
      worldlineId: decodeURIComponent(parts[3]),
    };
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
  else if (route.name === "worldline") {
    next = `#/world/${encodeURIComponent(route.slug)}/worldlines/${encodeURIComponent(
      route.worldlineId,
    )}`;
  }
  else if (route.name === "dossierReading") {
    next = `#/world/${encodeURIComponent(route.slug)}/worldlines/${encodeURIComponent(
      route.worldlineId,
    )}/reading`;
    if (route.tab) next += `/${encodeURIComponent(route.tab)}`;
  }
  else if (route.name === "characterVolume") {
    next = `#/world/${encodeURIComponent(route.slug)}/worldlines/${encodeURIComponent(
      route.worldlineId,
    )}/characters/${encodeURIComponent(route.characterId)}`;
  }
  else if (route.name === "factionVolume") {
    next = `#/world/${encodeURIComponent(route.slug)}/worldlines/${encodeURIComponent(
      route.worldlineId,
    )}/factions/${encodeURIComponent(route.factionId)}`;
  }
  else if (route.name === "checkpoint") {
    next = `#/world/${encodeURIComponent(route.slug)}/worldlines/${encodeURIComponent(
      route.worldlineId,
    )}/checkpoints/${encodeURIComponent(route.runId)}/${encodeURIComponent(
      route.checkpointId,
    )}`;
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
