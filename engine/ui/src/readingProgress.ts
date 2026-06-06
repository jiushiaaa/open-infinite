import type { Route } from "./routing";

export const READING_PROGRESS_STORAGE_KEY = "unfinale.recentReading.v1";

type ReadingRoute =
  | Extract<Route, { name: "dossierReading" }>
  | Extract<Route, { name: "longlineReading" }>
  | Extract<Route, { name: "characterVolume" }>
  | Extract<Route, { name: "factionVolume" }>
  | Extract<Route, { name: "eventPerspective" }>
  | Extract<Route, { name: "checkpoint" }>;

export interface RecentReading {
  slug: string;
  worldlineId: string;
  label: string;
  title: string;
  action: string;
  hash: string;
  updatedAt: number;
}

interface StorageLike {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem(key: string): void;
}

export function isReadableRoute(route: Route): route is ReadingRoute {
  return (
    route.name === "dossierReading" ||
    route.name === "longlineReading" ||
    route.name === "characterVolume" ||
    route.name === "factionVolume" ||
    route.name === "eventPerspective" ||
    route.name === "checkpoint"
  );
}

export function describeReadingRoute(route: ReadingRoute): Omit<RecentReading, "updatedAt"> {
  const base = {
    slug: route.slug,
    worldlineId: route.worldlineId,
    hash: hashForReadingRoute(route),
  };
  if (route.name === "dossierReading") {
    const label = tabLabel(route.tab);
    return {
      ...base,
      label,
      title: `继续读${label}`,
      action: `回到${label}`,
    };
  }
  if (route.name === "longlineReading") {
    return {
      ...base,
      label: "长线卷",
      title: "继续读长线卷",
      action: "回到长线卷",
    };
  }
  if (route.name === "characterVolume") {
    return {
      ...base,
      label: `角色卷 · ${route.characterId}`,
      title: "继续读角色卷",
      action: "回到角色卷",
    };
  }
  if (route.name === "factionVolume") {
    return {
      ...base,
      label: `势力卷 · ${route.factionId}`,
      title: "继续读势力卷",
      action: "回到势力卷",
    };
  }
  if (route.name === "eventPerspective") {
    return {
      ...base,
      label: `事件卷 · ${route.eventId}`,
      title: "继续读事件多视角",
      action: "回到事件卷",
    };
  }
  return {
    ...base,
    label: "检查点回放",
    title: "继续读检查点",
    action: "回到检查点",
  };
}

export function writeRecentReading(
  storage: StorageLike | undefined,
  route: Route,
  updatedAt = Date.now(),
): void {
  if (!storage || !isReadableRoute(route)) return;
  const current = readAll(storage);
  const next: RecentReading = {
    ...describeReadingRoute(route),
    updatedAt,
  };
  current[route.slug] = next;
  try {
    storage.setItem(READING_PROGRESS_STORAGE_KEY, JSON.stringify(current));
  } catch {
    // Local reading progress should never break navigation.
  }
}

export function readRecentReading(
  storage: StorageLike | undefined,
  slug: string,
): RecentReading | null {
  if (!storage) return null;
  const item = readAll(storage)[slug];
  return isRecentReading(item) ? item : null;
}

export function shouldShowRecentReading(
  currentHash: string,
  recentReading: RecentReading | null,
): boolean {
  if (!recentReading) return false;
  return normalizeHash(currentHash) !== normalizeHash(recentReading.hash);
}

function readAll(storage: StorageLike): Record<string, RecentReading> {
  try {
    const parsed = JSON.parse(storage.getItem(READING_PROGRESS_STORAGE_KEY) || "{}");
    return parsed && typeof parsed === "object" && !Array.isArray(parsed)
      ? (parsed as Record<string, RecentReading>)
      : {};
  } catch {
    storage.removeItem(READING_PROGRESS_STORAGE_KEY);
    return {};
  }
}

function isRecentReading(value: unknown): value is RecentReading {
  if (!value || typeof value !== "object") return false;
  const item = value as Partial<RecentReading>;
  return Boolean(item.slug && item.worldlineId && item.label && item.title && item.action && item.hash);
}

function normalizeHash(hash: string): string {
  if (!hash) return "#/";
  return hash.startsWith("#") ? hash : `#${hash}`;
}

function hashForReadingRoute(route: ReadingRoute): string {
  const slug = encodeURIComponent(route.slug);
  const worldlineId = encodeURIComponent(route.worldlineId);
  if (route.name === "dossierReading") {
    let hash = `#/world/${slug}/worldlines/${worldlineId}/reading`;
    if (route.tab) hash += `/${encodeURIComponent(route.tab)}`;
    return hash;
  }
  if (route.name === "longlineReading") {
    return `#/world/${slug}/worldlines/${worldlineId}/longline`;
  }
  if (route.name === "characterVolume") {
    return `#/world/${slug}/worldlines/${worldlineId}/characters/${encodeURIComponent(route.characterId)}`;
  }
  if (route.name === "factionVolume") {
    return `#/world/${slug}/worldlines/${worldlineId}/factions/${encodeURIComponent(route.factionId)}`;
  }
  if (route.name === "eventPerspective") {
    return `#/world/${slug}/worldlines/${worldlineId}/events/${encodeURIComponent(route.eventId)}/perspectives`;
  }
  return `#/world/${slug}/worldlines/${worldlineId}/checkpoints/${encodeURIComponent(route.runId)}/${encodeURIComponent(route.checkpointId)}`;
}

function tabLabel(tab?: string): string {
  const labels: Record<string, string> = {
    continuous_reading: "连续阅读",
    confirmed_chapter: "确认正文",
    world_chronicle: "世界正史卷",
    anchor_volume: "主锚点卷",
    character_volume: "角色个人卷",
    faction_volume: "势力卷",
    event_multi_perspective: "事件多视角",
  };
  return labels[tab || "continuous_reading"] || "卷宗阅读";
}
