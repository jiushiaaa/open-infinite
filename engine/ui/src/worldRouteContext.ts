import type { Route } from "./routing";

export interface WorldRouteContext {
  sectionLabel: string;
  title: string;
  description: string;
  workspaceSummary: WorldWorkspaceSummary;
  stateHandoffs: WorldStateHandoff[];
  continuitySignals: WorldContinuitySignal[];
  primaryActionLabel: string;
  primaryRoute: Route;
  secondaryActionLabel?: string;
  secondaryRoute?: Route;
  stages: WorldRouteStage[];
  dossiers: WorldRouteDossierLink[];
}

export type WorldRouteStageKey = "tianming" | "sandbox" | "reading" | "author";
export type WorldRouteStageStatus = "ready" | "active";
export type WorldRouteDossierKey =
  | "continuous"
  | "world"
  | "anchor"
  | "character"
  | "faction"
  | "event"
  | "longline"
  | "worldline";
export type WorldRouteDossierStatus = "ready" | "active";

export interface WorldRouteStage {
  key: WorldRouteStageKey;
  label: string;
  title: string;
  status: WorldRouteStageStatus;
  route: Route;
}

export interface WorldRouteDossierLink {
  key: WorldRouteDossierKey;
  label: string;
  title: string;
  status: WorldRouteDossierStatus;
  route: Route;
}

export interface WorldWorkspaceSummary {
  stageLabel: string;
  stageTitle: string;
  worldlineLabel: string;
  nextStepLabel: string;
  why: string;
}

export interface WorldStateHandoff {
  key: "source" | "effect" | "receipt";
  label: string;
  title: string;
  detail: string;
  route: Route;
}

export interface WorldContinuitySignal {
  key: "memory" | "consequence" | "reading" | "writing";
  label: string;
  title: string;
  detail: string;
  route: Route;
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

function stageKey(route: Route): WorldRouteStageKey {
  if (route.name === "tianming" || route.name === "anchor" || route.name === "workspace") {
    return "tianming";
  }
  if (route.name === "sandbox") {
    return "sandbox";
  }
  if (route.name === "author") {
    return "author";
  }
  return "reading";
}

function buildStages(route: Route, slug: string, currentWorldline: string): WorldRouteStage[] {
  const active = stageKey(route);
  const stages: Array<Omit<WorldRouteStage, "status">> = [
    {
      key: "tianming",
      label: "定界",
      title: "天命书",
      route: { name: "tianming", slug },
    },
    {
      key: "sandbox",
      label: "运行",
      title: "世界沙盘",
      route: { name: "sandbox", slug },
    },
    {
      key: "reading",
      label: "阅读",
      title: "卷宗阅读",
      route: {
        name: "dossierReading",
        slug,
        worldlineId: currentWorldline,
      },
    },
    {
      key: "author",
      label: "采纳",
      title: "作者台",
      route: { name: "author", slug },
    },
  ];

  return stages.map((stage) => ({
    ...stage,
    status: stage.key === active ? "active" : "ready",
  }));
}

function dossierKey(route: Route): WorldRouteDossierKey | null {
  if (route.name === "longlineReading") return "longline";
  if (route.name === "worldline" || route.name === "checkpoint") return "worldline";
  if (route.name === "characterVolume") return "character";
  if (route.name === "factionVolume") return "faction";
  if (route.name === "eventPerspective") return "event";
  if (route.name !== "dossierReading") return null;
  if (route.tab === "world_chronicle") return "world";
  if (route.tab === "anchor_volume") return "anchor";
  if (route.tab === "character_volume") return "character";
  if (route.tab === "faction_volume") return "faction";
  if (route.tab === "event_multi_perspective") return "event";
  return "continuous";
}

function dossierReadingRoute(
  slug: string,
  worldlineId: string,
  tab?: string,
): Route {
  return {
    name: "dossierReading",
    slug,
    worldlineId,
    tab,
  };
}

function buildDossiers(route: Route, slug: string, currentWorldline: string): WorldRouteDossierLink[] {
  const active = dossierKey(route);
  const dossiers: Array<Omit<WorldRouteDossierLink, "status">> = [
    {
      key: "continuous",
      label: "正文",
      title: "连续阅读",
      route: dossierReadingRoute(slug, currentWorldline),
    },
    {
      key: "world",
      label: "正史",
      title: "世界正史卷",
      route: dossierReadingRoute(slug, currentWorldline, "world_chronicle"),
    },
    {
      key: "anchor",
      label: "锚点",
      title: "主锚点卷",
      route: dossierReadingRoute(slug, currentWorldline, "anchor_volume"),
    },
    {
      key: "character",
      label: "角色",
      title: "角色个人卷",
      route: dossierReadingRoute(slug, currentWorldline, "character_volume"),
    },
    {
      key: "faction",
      label: "势力",
      title: "势力卷",
      route: dossierReadingRoute(slug, currentWorldline, "faction_volume"),
    },
    {
      key: "event",
      label: "事件",
      title: "事件多视角",
      route: dossierReadingRoute(slug, currentWorldline, "event_multi_perspective"),
    },
    {
      key: "longline",
      label: "长线",
      title: "跨事件长线卷",
      route: { name: "longlineReading", slug, worldlineId: currentWorldline },
    },
    {
      key: "worldline",
      label: "世界线",
      title: "世界线档案",
      route: { name: "worldline", slug, worldlineId: currentWorldline },
    },
  ];

  return dossiers.map((dossier) => ({
    ...dossier,
    status: dossier.key === active ? "active" : "ready",
  }));
}

function workspaceWhy(route: Route): string {
  if (route.name === "anchor") return "先定界，再运行；用户不用从机制档案猜入口。";
  if (route.name === "tianming") return "宪法确认后，干预和沙盘才有边界。";
  if (route.name === "sandbox") return "本轮行动会进入记忆、代偿和下一章材料。";
  if (route.name === "dossierReading") return "先读正文，证据和误会按需展开。";
  if (route.name === "longlineReading") return "把误会、压力和未解线索回收成后续剧情。";
  if (route.name === "characterVolume") return "角色的记忆、误会和秘密会解释下一轮行动。";
  if (route.name === "factionVolume") return "势力压力和资源流向会牵动世界代偿。";
  if (route.name === "eventPerspective") return "同一事件的视角差会暴露谁误读了真相。";
  if (route.name === "worldline") return "分支状态、检查点和代偿决定世界怎么继续。";
  if (route.name === "checkpoint") return "醒来后先接回阅读，再查证谁记住了什么。";
  if (route.name === "lens") return "多视角卷把沙盘事实变成可读小说材料。";
  if (route.name === "author") return "把涌现剧情、Reviewer 和定稿接回下一轮沙盘。";
  return "机制档案只负责追溯，主旅程仍回到世界卷宗。";
}

function buildWorkspaceSummary(
  route: Route,
  stages: WorldRouteStage[],
  currentWorldline: string,
  primaryActionLabel: string,
): WorldWorkspaceSummary {
  const activeStage = stages.find((stage) => stage.status === "active") ?? stages[0];

  return {
    stageLabel: activeStage.label,
    stageTitle: activeStage.title,
    worldlineLabel: `世界线 ${currentWorldline}`,
    nextStepLabel: primaryActionLabel,
    why: workspaceWhy(route),
  };
}

function stateHandoffCopy(
  route: Route,
  key: WorldStateHandoff["key"],
  primaryActionLabel: string,
): Pick<WorldStateHandoff, "label" | "title" | "detail"> {
  if (key === "source") {
    if (route.name === "tianming" || route.name === "anchor") {
      return {
        label: "正在承接",
        title: "世界边界",
        detail: "锚点、合约压力和干预边界先被确认",
      };
    }
    if (route.name === "sandbox") {
      return {
        label: "正在承接",
        title: "事件与干预",
        detail: "大事件、可选干预和角色私念正在合流",
      };
    }
    if (route.name === "characterVolume") {
      return {
        label: "正在承接",
        title: "角色主观记忆",
        detail: "这个角色的主观记忆、误会和秘密会回到行动",
      };
    }
    if (route.name === "factionVolume") {
      return {
        label: "正在承接",
        title: "势力压力",
        detail: "资源、秘密和立场会牵动世界代偿",
      };
    }
    if (route.name === "eventPerspective") {
      return {
        label: "正在承接",
        title: "事件信息差",
        detail: "同一事件的多重视角正在互相校验",
      };
    }
    if (route.name === "author") {
      return {
        label: "正在承接",
        title: "可写材料",
        detail: "沙盘涌现、Reviewer 和定稿正在合并",
      };
    }
    if (route.name === "checkpoint") {
      return {
        label: "正在承接",
        title: "醒来报告",
        detail: "检查点、记忆变化和代偿正在接回正文",
      };
    }
    return {
      label: "正在承接",
      title: "卷宗证据",
      detail: "正文、误会、长线和证据链正在汇合",
    };
  }

  if (key === "effect") {
    if (route.name === "tianming" || route.name === "anchor") {
      return {
        label: "会留下",
        title: "干预边界",
        detail: "之后的投放会被世界宪法吸收或拆分",
      };
    }
    if (route.name === "sandbox") {
      return {
        label: "会留下",
        title: "记忆与代偿",
        detail: "行动会写入主观记忆、因果债和世界线",
      };
    }
    if (route.name === "author") {
      return {
        label: "会留下",
        title: "下一章入口",
        detail: "采纳结果会反哺定稿和下一轮沙盘",
      };
    }
    if (route.name === "longlineReading") {
      return {
        label: "会留下",
        title: "跨章回收",
        detail: "误会、压力和未解线索会变成后续任务",
      };
    }
    return {
      label: "会留下",
      title: "世界状态",
      detail: "证据会落到世界线、角色记忆和作者材料",
    };
  }

  return {
    label: "下一处看见",
    title: primaryActionLabel,
    detail: "沿着建议动作继续，能看到本步造成的后果",
  };
}

function buildStateHandoffs(
  route: Route,
  readingRoute: Route,
  worldlineRoute: Route,
  primaryRoute: Route,
  primaryActionLabel: string,
): WorldStateHandoff[] {
  return [
    {
      key: "source",
      ...stateHandoffCopy(route, "source", primaryActionLabel),
      route: readingRoute,
    },
    {
      key: "effect",
      ...stateHandoffCopy(route, "effect", primaryActionLabel),
      route: worldlineRoute,
    },
    {
      key: "receipt",
      ...stateHandoffCopy(route, "receipt", primaryActionLabel),
      route: primaryRoute,
    },
  ];
}

function continuityDetail(route: Route, key: WorldContinuitySignal["key"]): string {
  if (key === "memory") {
    if (route.name === "characterVolume") return "正在查看这个角色怎样记住世界";
    if (route.name === "sandbox") return "本轮行动会写入主观记忆";
    if (route.name === "checkpoint") return "先核对谁记住了这一夜";
    return "角色会带着误会和秘密继续行动";
  }
  if (key === "consequence") {
    if (route.name === "tianming") return "锚点和合约压力会约束干预";
    if (route.name === "sandbox") return "行动会变成因果债和资源流向";
    if (route.name === "factionVolume") return "势力压力正在牵动代偿";
    return "世界线会记录代偿、检查点和分支压力";
  }
  if (key === "reading") {
    if (route.name === "dossierReading") return "当前正在读正文，可按需查卷宗";
    if (route.name === "longlineReading") return "长线卷正在回收跨事件伏笔";
    if (route.name === "eventPerspective") return "同一事件会拆成多个视角";
    return "把世界运行结果接成可读章节";
  }
  if (route.name === "author") return "正在把涌现剧情修成下一章";
  if (route.name === "dossierReading" || route.name === "longlineReading") {
    return "读完后可把余波送进作者台";
  }
  return "把当前材料送往下一章和下一轮沙盘";
}

function buildContinuitySignals(
  route: Route,
  readingRoute: Route,
  worldlineRoute: Route,
  longlineRoute: Route,
  authorRoute: Route,
): WorldContinuitySignal[] {
  return [
    {
      key: "memory",
      label: "记忆",
      title: "角色还记得什么",
      detail: continuityDetail(route, "memory"),
      route: readingRoute,
    },
    {
      key: "consequence",
      label: "代偿",
      title: "世界正在怎样变",
      detail: continuityDetail(route, "consequence"),
      route: worldlineRoute,
    },
    {
      key: "reading",
      label: "正文",
      title: "读到哪里继续",
      detail: continuityDetail(route, "reading"),
      route: longlineRoute,
    },
    {
      key: "writing",
      label: "写作",
      title: "下一章材料",
      detail: continuityDetail(route, "writing"),
      route: authorRoute,
    },
  ];
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
  const stages = buildStages(route, slug, currentWorldline);
  const dossiers = buildDossiers(route, slug, currentWorldline);
  const continuitySignals = buildContinuitySignals(
    route,
    readingRoute,
    worldlineRoute,
    longlineRoute,
    authorRoute,
  );

  if (route.name === "anchor") {
    const primaryActionLabel = "确认天命书";
    const primaryRoute: Route = { name: "tianming", slug };
    return {
      sectionLabel: "入口",
      title: "世界锚定",
      description: "校准角色、规则和卷宗地图，决定先确认天命还是继续上次阅读。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        primaryRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute,
      secondaryActionLabel: "运行沙盘",
      secondaryRoute: sandboxRoute,
      stages,
      dossiers,
    };
  }
  if (route.name === "tianming") {
    const primaryActionLabel = "进入世界沙盘";
    return {
      sectionLabel: "定界",
      title: "天命书",
      description: "先确认世界宪法、锚点和干预边界，再让角色按规则行动。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        sandboxRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute: sandboxRoute,
      secondaryActionLabel: "回世界锚定",
      secondaryRoute: { name: "anchor", slug },
      stages,
      dossiers,
    };
  }
  if (route.name === "sandbox") {
    const primaryActionLabel = "进入卷宗阅读";
    return {
      sectionLabel: "运行",
      title: "世界沙盘",
      description: "让角色行动、记忆发酵并把干预投放进世界状态。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        readingRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute: readingRoute,
      secondaryActionLabel: "查看世界线",
      secondaryRoute: worldlineRoute,
      stages,
      dossiers,
    };
  }
  if (route.name === "dossierReading") {
    const primaryActionLabel = "追跨事件长线";
    return {
      sectionLabel: "阅读",
      title: "卷宗阅读",
      description: "先读连续正文，再按证据、误会和角色视角查清世界发生了什么。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        longlineRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute: longlineRoute,
      secondaryActionLabel: "送往作者台",
      secondaryRoute: authorRoute,
      stages,
      dossiers,
    };
  }
  if (route.name === "longlineReading") {
    const primaryActionLabel = "送往作者台";
    return {
      sectionLabel: "长线",
      title: "跨事件长线卷",
      description: "把事件、误会、角色记忆和势力压力连成可回收的后续线索。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        authorRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute: authorRoute,
      secondaryActionLabel: "回卷宗阅读",
      secondaryRoute: readingRoute,
      stages,
      dossiers,
    };
  }
  if (route.name === "characterVolume") {
    const primaryActionLabel = "继续沙盘";
    return {
      sectionLabel: "角色卷",
      title: "角色个人卷",
      description: "查看这个角色的主观记忆、误会、秘密可见性和下一轮行动理由。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        sandboxRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute: sandboxRoute,
      secondaryActionLabel: "去多视角",
      secondaryRoute: lensRoute,
      stages,
      dossiers,
    };
  }
  if (route.name === "factionVolume") {
    const primaryActionLabel = "继续沙盘";
    return {
      sectionLabel: "势力卷",
      title: "势力卷",
      description: "查看势力立场、资源压力、代偿账和它会怎样牵动下一章。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        sandboxRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute: sandboxRoute,
      secondaryActionLabel: "去多视角",
      secondaryRoute: lensRoute,
      stages,
      dossiers,
    };
  }
  if (route.name === "eventPerspective") {
    const primaryActionLabel = "追长线卷";
    return {
      sectionLabel: "事件卷",
      title: "事件多视角",
      description: "拆开同一事件里的信息差、误读和证据，判断谁看见了哪一部分真相。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        longlineRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute: longlineRoute,
      secondaryActionLabel: "送往作者台",
      secondaryRoute: authorRoute,
      stages,
      dossiers,
    };
  }
  if (route.name === "worldline") {
    const primaryActionLabel = "进入卷宗阅读";
    return {
      sectionLabel: "世界线",
      title: "世界线档案",
      description: "查看分支状态、因果债、检查点和世界自演留下的承接关系。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        readingRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute: readingRoute,
      secondaryActionLabel: "追长线卷",
      secondaryRoute: longlineRoute,
      stages,
      dossiers,
    };
  }
  if (route.name === "checkpoint") {
    const primaryActionLabel = "继续读正文";
    return {
      sectionLabel: "检查点",
      title: "醒来回放",
      description: "回看这一夜世界如何变化、谁记住了什么，以及后果该往哪里接。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        readingRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute: readingRoute,
      secondaryActionLabel: "回世界线",
      secondaryRoute: worldlineRoute,
      stages,
      dossiers,
    };
  }
  if (route.name === "lens") {
    const primaryActionLabel = "进入卷宗阅读";
    return {
      sectionLabel: "多视角",
      title: "活体小说",
      description: "生成世界正史卷、角色个人卷、势力卷和事件多视角，暴露信息差。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        readingRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute: readingRoute,
      secondaryActionLabel: "送往作者台",
      secondaryRoute: authorRoute,
      stages,
      dossiers,
    };
  }
  if (route.name === "author") {
    const primaryActionLabel = "继续沙盘";
    return {
      sectionLabel: "作者",
      title: "作者采纳台",
      description: "把沙盘涌现、Reviewer 建议和编辑后定稿写成下一章入口。",
      workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
      stateHandoffs: buildStateHandoffs(
        route,
        readingRoute,
        worldlineRoute,
        sandboxRoute,
        primaryActionLabel,
      ),
      continuitySignals,
      primaryActionLabel,
      primaryRoute: sandboxRoute,
      secondaryActionLabel: "回卷宗阅读",
      secondaryRoute: readingRoute,
      stages,
      dossiers,
    };
  }

  const primaryActionLabel = "确认天命书";
  const primaryRoute: Route = { name: "tianming", slug };
  return {
    sectionLabel: "机制",
    title: "机制档案",
    description: "旧正史、支撑层和运行证据都收在这里；主旅程仍回到世界内部卷宗。",
    workspaceSummary: buildWorkspaceSummary(route, stages, currentWorldline, primaryActionLabel),
    stateHandoffs: buildStateHandoffs(
      route,
      readingRoute,
      worldlineRoute,
      primaryRoute,
      primaryActionLabel,
    ),
    continuitySignals,
    primaryActionLabel,
    primaryRoute,
    secondaryActionLabel: "进入卷宗阅读",
    secondaryRoute: readingRoute,
    stages,
    dossiers,
  };
}
