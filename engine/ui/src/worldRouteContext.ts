import type { Route } from "./routing";

export interface WorldRouteContext {
  sectionLabel: string;
  title: string;
  description: string;
  primaryActionLabel: string;
  primaryRoute: Route;
  secondaryActionLabel?: string;
  secondaryRoute?: Route;
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

export function getWorldRouteContext(route: Route): WorldRouteContext | null {
  if (route.name === "entry" || route.name === "import" || route.name === "genesis") {
    return null;
  }

  const slug = route.slug;
  const currentWorldline = worldlineId(route);
  const readingRoute: Route = {
    name: "dossierReading",
    slug,
    worldlineId: currentWorldline,
  };
  const sandboxRoute: Route = { name: "sandbox", slug };
  const authorRoute: Route = { name: "author", slug };
  const lensRoute: Route = { name: "lens", slug };
  const worldlineRoute: Route = {
    name: "worldline",
    slug,
    worldlineId: currentWorldline,
  };
  const longlineRoute: Route = {
    name: "longlineReading",
    slug,
    worldlineId: currentWorldline,
  };

  if (route.name === "anchor") {
    return {
      sectionLabel: "入口",
      title: "世界锚定",
      description: "校准角色、规则和卷宗地图，决定先确认天命还是继续上次阅读。",
      primaryActionLabel: "确认天命书",
      primaryRoute: { name: "tianming", slug },
      secondaryActionLabel: "运行沙盘",
      secondaryRoute: sandboxRoute,
    };
  }
  if (route.name === "tianming") {
    return {
      sectionLabel: "定界",
      title: "天命书",
      description: "先确认世界宪法、锚点和干预边界，再让角色按规则行动。",
      primaryActionLabel: "进入世界沙盘",
      primaryRoute: sandboxRoute,
      secondaryActionLabel: "回世界锚定",
      secondaryRoute: { name: "anchor", slug },
    };
  }
  if (route.name === "sandbox") {
    return {
      sectionLabel: "运行",
      title: "世界沙盘",
      description: "让角色行动、记忆发酵并把干预投放进世界状态。",
      primaryActionLabel: "进入卷宗阅读",
      primaryRoute: readingRoute,
      secondaryActionLabel: "查看世界线",
      secondaryRoute: worldlineRoute,
    };
  }
  if (route.name === "dossierReading") {
    return {
      sectionLabel: "阅读",
      title: "卷宗阅读",
      description: "先读连续正文，再按证据、误会和角色视角查清世界发生了什么。",
      primaryActionLabel: "追跨事件长线",
      primaryRoute: longlineRoute,
      secondaryActionLabel: "送往作者台",
      secondaryRoute: authorRoute,
    };
  }
  if (route.name === "longlineReading") {
    return {
      sectionLabel: "长线",
      title: "跨事件长线卷",
      description: "把事件、误会、角色记忆和势力压力连成可回收的后续线索。",
      primaryActionLabel: "送往作者台",
      primaryRoute: authorRoute,
      secondaryActionLabel: "回卷宗阅读",
      secondaryRoute: readingRoute,
    };
  }
  if (route.name === "characterVolume") {
    return {
      sectionLabel: "角色卷",
      title: "角色个人卷",
      description: "查看这个角色的主观记忆、误会、秘密可见性和下一轮行动理由。",
      primaryActionLabel: "继续沙盘",
      primaryRoute: sandboxRoute,
      secondaryActionLabel: "去多视角",
      secondaryRoute: lensRoute,
    };
  }
  if (route.name === "factionVolume") {
    return {
      sectionLabel: "势力卷",
      title: "势力卷",
      description: "查看势力立场、资源压力、代偿账和它会怎样牵动下一章。",
      primaryActionLabel: "继续沙盘",
      primaryRoute: sandboxRoute,
      secondaryActionLabel: "去多视角",
      secondaryRoute: lensRoute,
    };
  }
  if (route.name === "eventPerspective") {
    return {
      sectionLabel: "事件卷",
      title: "事件多视角",
      description: "拆开同一事件里的信息差、误读和证据，判断谁看见了哪一部分真相。",
      primaryActionLabel: "追长线卷",
      primaryRoute: longlineRoute,
      secondaryActionLabel: "送往作者台",
      secondaryRoute: authorRoute,
    };
  }
  if (route.name === "worldline") {
    return {
      sectionLabel: "世界线",
      title: "世界线档案",
      description: "查看分支状态、因果债、检查点和世界自演留下的承接关系。",
      primaryActionLabel: "进入卷宗阅读",
      primaryRoute: readingRoute,
      secondaryActionLabel: "追长线卷",
      secondaryRoute: longlineRoute,
    };
  }
  if (route.name === "checkpoint") {
    return {
      sectionLabel: "检查点",
      title: "醒来回放",
      description: "回看这一夜世界如何变化、谁记住了什么，以及后果该往哪里接。",
      primaryActionLabel: "继续读正文",
      primaryRoute: readingRoute,
      secondaryActionLabel: "回世界线",
      secondaryRoute: worldlineRoute,
    };
  }
  if (route.name === "lens") {
    return {
      sectionLabel: "多视角",
      title: "活体小说",
      description: "生成世界正史卷、角色个人卷、势力卷和事件多视角，暴露信息差。",
      primaryActionLabel: "进入卷宗阅读",
      primaryRoute: readingRoute,
      secondaryActionLabel: "送往作者台",
      secondaryRoute: authorRoute,
    };
  }
  if (route.name === "author") {
    return {
      sectionLabel: "作者",
      title: "作者采纳台",
      description: "把沙盘涌现、Reviewer 建议和编辑后定稿写成下一章入口。",
      primaryActionLabel: "继续沙盘",
      primaryRoute: sandboxRoute,
      secondaryActionLabel: "回卷宗阅读",
      secondaryRoute: readingRoute,
    };
  }

  return {
    sectionLabel: "机制",
    title: "机制档案",
    description: "旧正史、支撑层和运行证据都收在这里；主旅程仍回到世界内部卷宗。",
    primaryActionLabel: "确认天命书",
    primaryRoute: { name: "tianming", slug },
    secondaryActionLabel: "进入卷宗阅读",
    secondaryRoute: readingRoute,
  };
}
