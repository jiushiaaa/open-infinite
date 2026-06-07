import { useMemo, useRef, useState } from "react";
import { api } from "../api/client";
import type {
  SubjectiveMemoryReport,
  WorldAutopilotReadableEntry,
  WorldAutopilotReport,
  WorldSandboxRunReport,
} from "../api/types";
import { navigate } from "../routing";
import { ErrorState, EmptyState } from "./common/States";
import { WorldRunway } from "./WorldRunway";
import "./worldSandbox.css";

const DEFAULT_EVENT = "老皇帝驾崩，边境军报同时传入归云斋。";

function openReadableRoute(route: string) {
  if (route.startsWith("#/")) {
    window.location.hash = route;
  }
}

export function WorldSandboxPage({ slug }: { slug: string }) {
  const controlRef = useRef<HTMLDivElement | null>(null);
  const resultsRef = useRef<HTMLElement | null>(null);
  const strategyBoardRef = useRef<HTMLElement | null>(null);
  const actionChainRef = useRef<HTMLElement | null>(null);
  const eventTextareaRef = useRef<HTMLTextAreaElement | null>(null);
  const interventionTextareaRef = useRef<HTMLTextAreaElement | null>(null);
  const [majorEvent, setMajorEvent] = useState(DEFAULT_EVENT);
  const [interventionContent, setInterventionContent] = useState("");
  const [interventionTarget, setInterventionTarget] = useState("");
  const [interventionProjectionMode, setInterventionProjectionMode] =
    useState<"immersive" | "wild_au">("immersive");
  const [interventionDraftOpen, setInterventionDraftOpen] = useState(false);
  const [llmDecisionAdvisory, setLlmDecisionAdvisory] = useState(false);
  const [report, setReport] = useState<WorldSandboxRunReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCharacterId, setSelectedCharacterId] = useState<string | null>(null);
  const [queuedPossibilityTitle, setQueuedPossibilityTitle] = useState("");
  const [queuedStrategyTitle, setQueuedStrategyTitle] = useState("");
  const [queuedActionFocusTitle, setQueuedActionFocusTitle] = useState("");
  const [queuedEventSeedTitle, setQueuedEventSeedTitle] = useState("");
  const [memoryReport, setMemoryReport] = useState<SubjectiveMemoryReport | null>(null);
  const [memoryLoading, setMemoryLoading] = useState(false);
  const [memoryError, setMemoryError] = useState<string | null>(null);
  const [autopilotEvent, setAutopilotEvent] = useState(
    "老皇帝驾崩，边境军报传来。",
  );
  const [autopilotObjective, setAutopilotObjective] = useState("rounds");
  const [autopilotStopEvent, setAutopilotStopEvent] = useState("风鸣铃");
  const [autopilotTimeLimit, setAutopilotTimeLimit] = useState("三日后");
  const [autopilotRounds, setAutopilotRounds] = useState(3);
  const [autopilotLoading, setAutopilotLoading] = useState(false);
  const [autopilotError, setAutopilotError] = useState<string | null>(null);
  const [autopilotReport, setAutopilotReport] = useState<WorldAutopilotReport | null>(null);

  const round = report?.rounds[0] ?? null;
  const hasInterventionDraft = interventionContent.trim().length > 0;
  const eventPreview = useMemo(() => {
    const eventDraft = majorEvent.trim();
    const eventName = eventDraft || "先写一个会打破平衡的大事件";
    const interventionLine = hasInterventionDraft
      ? interventionProjectionMode === "wild_au"
        ? "读者干预会作为异物压进本轮，角色可能抵抗，世界会优先写分支轴和因果债。"
        : "读者干预会被转译成梦兆、密信或资源变化，贴着这个事件进入角色判断。"
      : "本轮暂不带读者干预；角色会先按事件本身、旧记忆和利益关系行动。";
    return [
      {
        label: "谁会先动",
        value: eventDraft
          ? "靠近事件中心、利益受损或背负秘密的角色会先被推到台前。"
          : "写下事件后，沙盘会把相关角色推到台前。",
      },
      {
        label: "世界怎样记账",
        value: `${eventName} 会写入角色行动、主观记忆、因果债和世界线状态。`,
      },
      {
        label: "干预怎样入局",
        value: interventionLine,
      },
      {
        label: "跑完先看哪里",
        value: "先看本轮已发生，再读卷宗正文、世界线代偿和角色个人记忆。",
      },
    ];
  }, [hasInterventionDraft, interventionProjectionMode, majorEvent]);
  const interventionPreview = useMemo(() => {
    const target = interventionTarget.trim() || "由世界选择最容易被波及的角色";
    const projection =
      interventionProjectionMode === "wild_au"
        ? "暴走 AU：保留异物入侵"
        : "沉浸模式：本土化重释";
    const absorption = hasInterventionDraft
      ? interventionProjectionMode === "wild_au"
        ? "世界会把它识别成偏离根天命的异物，优先写成分支轴、天命快照和更高因果债。"
        : "世界会把它翻译成梦兆、密信、谣言或资源变化，再让角色按自己的立场消化。"
      : "本轮只投放大事件；世界仍会把事件写成角色行动、主观记忆和世界线变化。";
    return {
      target,
      projection,
      absorption,
      observations: [
        ["角色主观记忆", "谁相信、误会或隐瞒了这次投放"],
        ["世界线代偿", "因果债、锚点压力和资源/秘密怎样转移"],
        ["多视角正文", "同一事件在不同角色眼中如何变形"],
      ],
    };
  }, [
    hasInterventionDraft,
    interventionContent,
    interventionProjectionMode,
    interventionTarget,
  ]);
  const worldlineState = report?.worldline_state ?? null;
  const consequenceDomains = worldlineState?.consequence_state?.domains
    ? Object.entries(worldlineState.consequence_state.domains)
    : [];
  const latestConsequence =
    worldlineState?.consequence_state?.ledger?.[
      (worldlineState.consequence_state.ledger?.length ?? 1) - 1
    ];
  const consequenceNextRoundHint =
    worldlineState?.consequence_state?.next_round_hint ?? "";
  const interventionConstraint =
    report?.intervention_constraint?.status === "active"
      ? report.intervention_constraint
      : round?.intervention_constraint?.status === "active"
        ? round.intervention_constraint
        : null;
  const canRun = majorEvent.trim().length > 0 && !loading;
  const actionCount = round?.character_actions.length ?? 0;
  const memoryEntries = report?.summary.subjective_memory_entries_written ?? 0;
  const hasReadableResult = Boolean(round || autopilotReport);
  const focusControl = () =>
    controlRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  const focusResults = () =>
    resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  const focusStrategyBoard = () =>
    (strategyBoardRef.current ?? actionChainRef.current)?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  const focusActionChain = () =>
    actionChainRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  function openInterventionControls() {
    setInterventionDraftOpen(true);
    window.requestAnimationFrame(() => {
      interventionTextareaRef.current?.focus();
    });
  }
  function focusEventDraft() {
    eventTextareaRef.current?.focus();
  }
  function clearInterventionDraft() {
    setInterventionContent("");
    setInterventionTarget("");
    setInterventionProjectionMode("immersive");
    setInterventionDraftOpen(false);
  }
  const overnightReport = autopilotReport?.overnight_report;
  const overnightMemory =
    overnightReport?.who_remembered_what?.[0] ??
    overnightReport?.memory_changes?.[0] ??
    autopilotReport?.readable_entry?.memory_readout.who_remembered_what[0] ??
    null;
  const overnightContinuation =
    overnightReport?.where_to_continue?.[0] ??
    (autopilotReport?.readable_entry
      ? {
          checkpoint_id: autopilotReport.readable_entry.latest_checkpoint.checkpoint_id,
          sandbox_run_id: autopilotReport.readable_entry.latest_checkpoint.sandbox_run_id,
          label: autopilotReport.readable_entry.primary_actions[0]?.label,
        }
      : null);
  const overnightScene = overnightReport?.narrative_timeline?.[0] ?? null;
  const overnightReadAction =
    autopilotReport?.readable_entry?.primary_actions.find(
      (action) => action.id === "continuous_reading",
    ) ?? autopilotReport?.readable_entry?.primary_actions[0];
  const sandboxRunwayMeta = report ? (
    <>
      <span className="badge badge--jade">{actionCount} 个角色行动</span>
      <span className="badge badge--gold">{memoryEntries} 条主观记忆</span>
      <span className="badge">世界线 {report.worldline_id}</span>
    </>
  ) : autopilotReport ? (
    <>
      <span className="badge badge--jade">{autopilotReport.rounds_completed} 个检查点</span>
      <span className="badge badge--gold">
        {autopilotReport.task?.status ?? autopilotReport.status ?? "ready"}
      </span>
      <span className="badge">世界线 {autopilotReport.worldline_id}</span>
    </>
  ) : (
    <>
      <span className="badge badge--jade">待投放事件</span>
      <span className="badge">main 世界线</span>
    </>
  );
  const sandboxRunwayActions = hasReadableResult
    ? [
        {
          label: "卷宗阅读",
          detail: "把本轮结果当小说读",
          primary: true,
          onClick: () => navigate({ name: "dossierReading", slug, worldlineId: "main" }),
        },
        {
          label: "世界线档案",
          detail: "看因果债与锚点变化",
          onClick: () => navigate({ name: "worldline", slug, worldlineId: "main" }),
        },
        {
          label: "多视角卷",
          detail: "进入事件多视角正文",
          onClick: () => navigate({ name: "lens", slug }),
        },
      ]
    : [
        {
          label: "运行台",
          detail: "先写事件并启动一轮",
          primary: true,
          onClick: focusControl,
        },
        {
          label: "天命书",
          detail: "查看世界预抽命运",
          onClick: () => navigate({ name: "tianming", slug }),
        },
        {
          label: "卷宗阅读",
          detail: "进入世界可读出口",
          onClick: () => navigate({ name: "dossierReading", slug, worldlineId: "main" }),
        },
      ];
  const deltaItems = useMemo(() => {
    if (!round) return [];
    return [
      ["锚点压力", round.world_state_delta.anchor_pressure],
      ["因果债", round.world_state_delta.causal_debt],
      ["资源变化", round.world_state_delta.resource_changes.join("；")],
      ["秘密流动", round.world_state_delta.secret_changes.join("；")],
      [
        "干预投放",
        round.world_state_delta.intervention_effects?.join("；") || "本轮未投放干预",
      ],
      [
        "分支承接",
        round.world_state_delta.branch_state?.continuation_status || "runnable",
      ],
      [
        "世界代偿",
        round.world_state_delta.compensation_effects?.join("；") || "因果债尚未外溢",
      ],
      [
        "模因污染",
        round.world_state_delta.meme_contamination?.status === "active"
          ? round.world_state_delta.meme_contamination.belief_payload || "高维真相正在传播"
          : "未触发",
      ],
    ];
  }, [round]);
  const leadAction = round?.character_actions[0] ?? null;
  const firstPossibility = round?.next_story_possibilities[0] ?? null;
  const resultBridgeStats = round
    ? [
        ["角色行动", `${actionCount} 条`],
        ["主观记忆", `${memoryEntries} 条`],
        ["因果债", round.world_state_delta.causal_debt || "待观察"],
      ]
    : [];
  const resultBridgeSignals = deltaItems.slice(0, 4);
  const strategyInteractions = useMemo(() => {
    if (!round) return [];
    const characterNameById = new Map(
      round.character_actions.map((item) => [item.character_id, item.character_name]),
    );
    return round.character_actions
      .flatMap((item) => {
        const strategy =
          item.strategic_interaction ?? item.llm_decision_advisory?.strategic_interaction;
        if (!strategy?.target_character_id) return [];
        return [
          {
            actorId: item.character_id,
            actorName: item.character_name,
            targetName:
              characterNameById.get(strategy.target_character_id) ||
              strategy.target_character_id,
            tactic: strategy.tactic || "暗中试探",
            privateGoal: strategy.private_goal || item.true_intent || item.intent,
            leverage: strategy.perceived_leverage || "筹码尚未明示",
            misread: strategy.assumed_misread || "误判还未显形",
            risk: strategy.risk_assessment || item.risk || "风险待观察",
            effect:
              strategy.expected_world_effect ||
              item.expected_outcome ||
              "继续改变世界状态",
            hook:
              strategy.outcome_hook ||
              round.next_story_possibilities[0]?.brief ||
              "下一轮继续观察这条暗线",
          },
        ];
      })
      .slice(0, 4);
  }, [round]);
  const resultReadingGuide = round
    ? [
        {
          label: "先读总览",
          title: "本轮已发生",
          detail: `${actionCount} 个角色行动、${memoryEntries} 条主观记忆先被压成总览，避免直接掉进证据堆。`,
          action: "回看总览",
          onClick: focusResults,
        },
        {
          label: "再看暗线",
          title: strategyInteractions.length
            ? `${strategyInteractions.length} 条算计路线`
            : "没有策略暗线时跳过",
          detail: strategyInteractions.length
            ? "先看谁在试探谁、误判在哪里，再决定要不要把暗线回填到下一轮。"
            : "本轮没有真实模型策略暗线，可以直接追角色行动链。",
          action: strategyInteractions.length ? "看策略棋盘" : "追角色行动",
          onClick: focusStrategyBoard,
        },
        {
          label: "然后追角色行动",
          title: `${actionCount} 条行动链`,
          detail: "逐个角色看意图、行动、记忆种子和信息传播，理解世界为什么这样走。",
          action: "追行动链",
          onClick: focusActionChain,
        },
        {
          label: "最后选择出口",
          title: "读正文或继续运行",
          detail: "读成正文、看世界线、生成多视角，或把余波放回运行台继续推演。",
          action: "读成正文",
          onClick: () =>
            navigate({
              name: "dossierReading",
              slug,
              worldlineId: round.worldline_id || "main",
            }),
        },
      ]
    : [];
  const actionFocusDeck = useMemo(() => {
    if (!round) return [];
    return round.character_actions.slice(0, 3).map((item, index) => {
      const actionLine = item.visible_action ?? item.action;
      const intentLine = item.true_intent || item.intent;
      const riskLine = item.risk || item.llm_decision_advisory?.risk || "风险待观察";
      const resultLine =
        item.action_outcome?.reason ||
        item.expected_outcome ||
        item.llm_decision_advisory?.expected_outcome ||
        "结果还在世界里发酵";
      const memoryLine =
        item.memory_seed?.inferred?.[0] ||
        item.memory_influence ||
        item.previous_subjective_memory ||
        "下一轮会继续影响这名角色的判断";
      return {
        id: `${item.character_id}-${index}`,
        characterId: item.character_id,
        label: index === 0 ? "最值得追的角色" : "继续追踪",
        title: item.character_name,
        role: item.narrative_role,
        action: actionLine,
        intent: intentLine,
        riskResult: `${resultLine}；风险：${riskLine}`,
        memory: memoryLine,
        event: `${item.character_name}继续推动：${actionLine}。行动背后的真实意图：${intentLine}。风险与结果：${resultLine}；${riskLine}。`,
      };
    });
  }, [round]);
  const eventSeedDeck = useMemo<
    Array<{ id: string; label: string; title: string; detail: string; event: string }>
  >(() => {
    const leadStrategy = strategyInteractions[0];
    const anchorName = worldlineState?.anchor_status?.current_anchor || "主锚点";
    const continuationHint =
      worldlineState?.continuation_inputs?.major_event_hint ||
      consequenceNextRoundHint ||
      "上一轮余波还没有被角色真正消化。";
    const domainPressure =
      consequenceDomains[0]?.[1]?.pressure ||
      consequenceDomains[0]?.[1]?.current ||
      latestConsequence?.impacts?.[0]?.pressure ||
      "旧债正在转移到资源、秘密和盟约上。";
    const latestEvent = latestConsequence?.major_event || round?.major_event || DEFAULT_EVENT;

    const seeds = [
      {
        id: "anchor-pressure",
        label: "锚点承压",
        title: `${anchorName}被迫表态`,
        detail: continuationHint,
        event: `${anchorName}被迫表态：${continuationHint}`,
      },
      {
        id: "faction-debt",
        label: "势力索债",
        title: "旧债开始找出口",
        detail: domainPressure,
        event: `势力索债：${domainPressure}`,
      },
      {
        id: "misread-ferment",
        label: "误会发酵",
        title: firstPossibility?.title || "沉默被解读成背叛",
        detail:
          firstPossibility?.brief ||
          `围绕「${latestEvent}」的传言开始变形，新的同盟在暗处改写计划。`,
        event: firstPossibility
          ? `${firstPossibility.title}：${firstPossibility.brief}`
          : `误会发酵：围绕「${latestEvent}」的传言开始变形，新的同盟在暗处改写计划。`,
      },
    ];

    if (leadStrategy) {
      seeds[2] = {
        id: "strategy-pressure",
        label: "暗线试探",
        title: `${leadStrategy.actorName}试探${leadStrategy.targetName}`,
        detail: leadStrategy.hook,
        event: `${leadStrategy.actorName}试探${leadStrategy.targetName}：${leadStrategy.actorName}准备用「${leadStrategy.tactic}」逼近${leadStrategy.targetName}，可能误判：${leadStrategy.misread}。下一轮观察：${leadStrategy.hook}`,
      };
    }

    return seeds;
  }, [
    consequenceDomains,
    consequenceNextRoundHint,
    firstPossibility,
    latestConsequence,
    round?.major_event,
    strategyInteractions,
    worldlineState?.anchor_status?.current_anchor,
    worldlineState?.continuation_inputs?.major_event_hint,
  ]);

  async function runRound() {
    if (!majorEvent.trim()) return;
    setLoading(true);
    setError(null);
    setQueuedPossibilityTitle("");
    setQueuedStrategyTitle("");
    setQueuedActionFocusTitle("");
    setQueuedEventSeedTitle("");
    try {
      const next = await api.runSandboxRound(slug, {
        major_event: majorEvent.trim(),
        worldline_id: "main",
        intervention_content: interventionContent.trim() || undefined,
        intervention_target: interventionTarget.trim() || undefined,
        intervention_projection_mode: interventionContent.trim()
          ? interventionProjectionMode
          : undefined,
        llm_decision_mode: llmDecisionAdvisory ? "advisory" : "deterministic",
      });
      setReport(next);
      const firstCharacter = next.rounds[0]?.character_actions[0]?.character_id;
      if (firstCharacter) {
        setSelectedCharacterId(firstCharacter);
        await loadMemory(firstCharacter, next.worldline_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function loadMemory(characterId: string, worldlineId = report?.worldline_id ?? "main") {
    setSelectedCharacterId(characterId);
    setMemoryLoading(true);
    setMemoryError(null);
    try {
      const next = await api.getSubjectiveMemory(slug, worldlineId, characterId);
      setMemoryReport(next);
    } catch (err) {
      setMemoryError(err instanceof Error ? err.message : String(err));
    } finally {
      setMemoryLoading(false);
    }
  }

  async function runAutopilot() {
    if (!autopilotEvent.trim()) return;
    setAutopilotLoading(true);
    setAutopilotError(null);
    try {
      setAutopilotReport(
        await api.runWorldAutopilot(slug, {
          seed_event: autopilotEvent.trim(),
          objective_type: autopilotObjective,
          stop_event:
            autopilotObjective === "event" ? autopilotStopEvent.trim() : undefined,
          time_limit:
            autopilotObjective === "time" ? autopilotTimeLimit.trim() : undefined,
          round_limit: autopilotRounds,
          worldline_id: "main",
        }),
      );
    } catch (err) {
      setAutopilotError(err instanceof Error ? err.message : String(err));
    } finally {
      setAutopilotLoading(false);
    }
  }

  async function updateAutopilotTask(action: "refresh" | "pause" | "resume") {
    const taskId = autopilotReport?.task?.task_id;
    const worldlineId = autopilotReport?.worldline_id || "main";
    if (!taskId) return;
    setAutopilotLoading(true);
    setAutopilotError(null);
    try {
      const task =
        action === "pause"
          ? await api.pauseWorldAutopilotTask(slug, worldlineId, taskId)
          : action === "resume"
            ? await api.resumeWorldAutopilotTask(slug, worldlineId, taskId)
            : await api.getWorldAutopilotTask(slug, worldlineId, taskId);
      setAutopilotReport((current) =>
        current
          ? {
              ...current,
              task: {
                ...(current.task ?? {}),
                task_id: taskId,
                status: String(task.status || current.task?.status || "unknown"),
                can_pause: current.task?.can_pause ?? true,
                can_resume: current.task?.can_resume ?? true,
                checkpoint_replay: current.task?.checkpoint_replay ?? true,
              },
              progress:
                typeof task.progress === "object" && task.progress
                  ? {
                      current_round: Number(
                        (task.progress as { current_round?: number }).current_round ??
                          current.progress?.current_round ??
                          0,
                      ),
                      target_round: Number(
                        (task.progress as { target_round?: number }).target_round ??
                          current.progress?.target_round ??
                          autopilotRounds,
                      ),
                      percent: Number(
                        (task.progress as { percent?: number }).percent ??
                          current.progress?.percent ??
                          0,
                      ),
                    }
                  : current.progress,
            }
          : current,
      );
    } catch (err) {
      setAutopilotError(err instanceof Error ? err.message : String(err));
    } finally {
      setAutopilotLoading(false);
    }
  }

  function queueNextPossibility(title: string, brief: string) {
    setMajorEvent(`${title}：${brief}`);
    setInterventionContent("");
    setInterventionTarget("");
    setQueuedPossibilityTitle(title);
    setQueuedStrategyTitle("");
    setQueuedActionFocusTitle("");
    setQueuedEventSeedTitle("");
    focusControl();
  }

  function queueStrategySeed(item: (typeof strategyInteractions)[number]) {
    const title = `${item.actorName}试探${item.targetName}`;
    setMajorEvent(
      `${title}：${item.actorName}准备用「${item.tactic}」逼近${item.targetName}，私下目的：${item.privateGoal}。可能误判：${item.misread}。世界影响：${item.effect}。下一轮观察：${item.hook}`,
    );
    setInterventionContent("");
    setInterventionTarget("");
    setQueuedStrategyTitle(title);
    setQueuedPossibilityTitle("");
    setQueuedActionFocusTitle("");
    setQueuedEventSeedTitle("");
    focusControl();
  }

  function queueActionFocusSeed(card: (typeof actionFocusDeck)[number]) {
    setMajorEvent(card.event);
    setInterventionContent("");
    setInterventionTarget("");
    setQueuedActionFocusTitle(card.title);
    setQueuedPossibilityTitle("");
    setQueuedStrategyTitle("");
    setQueuedEventSeedTitle("");
    focusControl();
  }

  function chooseEventSeed(seed: (typeof eventSeedDeck)[number]) {
    setMajorEvent(seed.event);
    setQueuedEventSeedTitle(seed.title);
    setQueuedPossibilityTitle("");
    setQueuedStrategyTitle("");
    setQueuedActionFocusTitle("");
    focusEventDraft();
  }

  const runnerPanel = (
    <div id="sandbox-runner" className="sandbox-panel sandbox-runner" ref={controlRef}>
      <div className="sandbox-runner__head">
        <span className="sandbox-runner__eyebrow">一轮沙盘</span>
        <h2>投放事件</h2>
        <p className="muted tiny">
          先写世界刚刚发生了什么；读者干预是可选项，默认不会覆盖世界规则。
        </p>
      </div>
      <div className="sandbox-runner__steps" aria-label="本轮运行步骤">
        <span className="is-active">
          <em>1</em>
          <strong>写事件</strong>
        </span>
        <span>
          <em>2</em>
          <strong>可选干预</strong>
        </span>
        <span>
          <em>3</em>
          <strong>启动推演</strong>
        </span>
      </div>
      <section className="sandbox-event-seeds" aria-label="事件种子台">
        <div className="sandbox-event-seeds__head">
          <div>
            <p className="tiny muted">事件种子台</p>
            <h3>不知道写什么，就从世界压力开局</h3>
          </div>
          <span className="badge">{report ? "读本轮余波" : "开局建议"}</span>
        </div>
        <div className="sandbox-event-seeds__grid">
          {eventSeedDeck.map((seed) => (
            <article key={seed.id}>
              <span>{seed.label}</span>
              <strong>{seed.title}</strong>
              <p>{seed.detail}</p>
              <div className="sandbox-event-seeds__actions">
                <button className="btn btn--ghost tiny" onClick={() => chooseEventSeed(seed)}>
                  放入事件
                </button>
              </div>
            </article>
          ))}
        </div>
        {queuedEventSeedTitle && (
          <p className="sandbox-event-seeds__feedback">已放入运行台：{queuedEventSeedTitle}</p>
        )}
      </section>
      <label className="sandbox-runner__field sandbox-runner__field--event">
        <span>世界刚刚发生了什么</span>
        <textarea
          ref={eventTextareaRef}
          value={majorEvent}
          onChange={(event) => setMajorEvent(event.target.value)}
          rows={5}
          placeholder="例如：老皇帝驾崩，边境军报同时传入归云斋。"
        />
      </label>
      <section className="sandbox-event-preview" aria-label="事件入局预演台">
        <div className="sandbox-event-preview__head">
          <div>
            <p className="tiny muted">事件入局预演台</p>
            <h3>{majorEvent.trim() ? "这件事会把世界推入下一轮" : "先放入一个能搅动世界的事件"}</h3>
          </div>
          <span className="badge">{hasInterventionDraft ? "带干预" : "纯事件"}</span>
        </div>
        <div className="sandbox-event-preview__grid">
          {eventPreview.map((item) => (
            <article key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </article>
          ))}
        </div>
        <div className="sandbox-event-preview__actions">
          <button className="btn btn--ghost" onClick={focusEventDraft}>
            修改事件
          </button>
          <button className="btn btn--ghost" onClick={openInterventionControls}>
            {hasInterventionDraft ? "调整干预" : "让读者干预入局"}
          </button>
        </div>
      </section>
      <button
        className="btn btn--primary sandbox-runner__submit"
        disabled={!canRun}
        onClick={runRound}
      >
        {loading ? "沙盘推演中…" : "启动一轮推演"}
      </button>
      <details
        className="sandbox-runner__advanced"
        open={interventionDraftOpen}
        onToggle={(event) => setInterventionDraftOpen(event.currentTarget.open)}
      >
        <summary>
          <span>可选：投放读者干预</span>
          <small>梦兆、密信、谣言、资源，或一条会被世界吸收的异物。</small>
        </summary>
        <label>
          <span className="muted tiny">本轮干预</span>
          <textarea
            ref={interventionTextareaRef}
            value={interventionContent}
            onChange={(event) => setInterventionContent(event.target.value)}
            rows={4}
            placeholder="写下要投放进本轮世界线的内容"
          />
        </label>
        <label>
          <span className="muted tiny">投放对象</span>
          <input
            value={interventionTarget}
            onChange={(event) => setInterventionTarget(event.target.value)}
            placeholder="可选：角色 id，例如 zhao_xuan"
          />
        </label>
        <label>
          <span className="muted tiny">投放方式</span>
          <select
            value={interventionProjectionMode}
            onChange={(event) =>
              setInterventionProjectionMode(
                event.target.value === "wild_au" ? "wild_au" : "immersive",
              )
            }
          >
            <option value="immersive">沉浸模式：本土化重释</option>
            <option value="wild_au">暴走 AU：保留异物入侵</option>
          </select>
        </label>
      </details>
      <section
        className={`sandbox-intervention-preview ${
          hasInterventionDraft ? "is-live" : "is-empty"
        }`}
        aria-label="干预后果预演台"
      >
        <div className="sandbox-intervention-preview__head">
          <div>
            <p className="tiny muted">干预后果预演台</p>
            <h3>{hasInterventionDraft ? "这条干预会进入本轮世界" : "不投干预也能推演"}</h3>
          </div>
          <span className="badge">{hasInterventionDraft ? "待投放" : "只运行事件"}</span>
        </div>
        <div className="sandbox-intervention-preview__grid">
          <article>
            <span>投放对象</span>
            <strong>{interventionPreview.target}</strong>
          </article>
          <article>
            <span>投放方式</span>
            <strong>{interventionPreview.projection}</strong>
          </article>
          <article>
            <span>世界会怎样吸收</span>
            <strong>{interventionPreview.absorption}</strong>
          </article>
        </div>
        <div className="sandbox-intervention-preview__map">
          <p>
            <strong>后果观察点</strong>
            <span>运行后先看这些位置，判断干预有没有真正改变世界。</span>
          </p>
          <ul>
            {interventionPreview.observations.map(([label, detail]) => (
              <li key={label}>
                <b>{label}</b>
                <span>{detail}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="sandbox-intervention-preview__actions">
          <button className="btn btn--ghost" onClick={openInterventionControls}>
            {hasInterventionDraft ? "调整干预" : "添加干预"}
          </button>
          {hasInterventionDraft && (
            <button className="btn btn--ghost" onClick={clearInterventionDraft}>
              清空干预
            </button>
          )}
        </div>
      </section>
      <label className="sandbox-check sandbox-runner__model">
        <input
          type="checkbox"
          checked={llmDecisionAdvisory}
          onChange={(event) => setLlmDecisionAdvisory(event.target.checked)}
        />
        <span>启用真实模型决策建议</span>
      </label>
      <p className="muted tiny">
        不填干预也能直接运行；勾选模型建议后，本轮会额外让模型给出采信、欺骗、传播、反抗和临场判断，失败则保留原沙盘行动。
      </p>
    </div>
  );

  return (
    <div className="sandbox-page">
      <header className="sandbox-hero">
        <div className="sandbox-hero__copy">
          <p className="sandbox-hero__eyebrow muted">世界内部卷宗 · 世界沙盘</p>
          <h1>让世界先动一轮</h1>
          <p className="muted">
            输入一个大事件，观察角色各自的意图、行动、冲突、信息传播和世界状态变化。
          </p>
        </div>
        <div className="sandbox-hero__control">{runnerPanel}</div>
        <div className="sandbox-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "tianming", slug })}
          >
            查看天命书
          </button>
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "lens", slug })}
          >
            多视角卷
          </button>
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "worldline", slug, worldlineId: "main" })}
          >
            世界线
          </button>
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "workspace", slug })}
          >
            返回正史卷
          </button>
        </div>
      </header>

      <WorldRunway
        eyebrow="沙盘运行导览"
        title={hasReadableResult ? "世界已经给出回响" : "从一个事件开始，让角色自己走"}
        summary={
          hasReadableResult
            ? "本轮结果已经写入行动、记忆和世界线；你可以继续查看证据，也可以把它转成可读卷宗。"
            : "先投放一个大事件；系统会让每个角色按自己的立场行动，再把后果写回世界状态。"
        }
        meta={sandboxRunwayMeta}
        steps={[
          {
            label: "投放事件",
            detail: "写下大事件，也可以加入读者干预",
            active: !hasReadableResult,
            onClick: focusControl,
          },
          {
            label: "观察角色",
            detail: hasReadableResult
              ? `${actionCount || autopilotReport?.rounds_completed || 0} 条世界回响已生成`
              : "运行后会出现行动、冲突和记忆",
            active: Boolean(round),
            onClick: hasReadableResult ? focusResults : focusControl,
          },
          {
            label: "进入阅读",
            detail: "把沙盘后果带回卷宗、世界线和多视角正文",
            active: hasReadableResult,
            onClick: hasReadableResult
              ? () => navigate({ name: "dossierReading", slug, worldlineId: "main" })
              : undefined,
          },
        ]}
        actions={sandboxRunwayActions}
      />

      <div className="sandbox-layout">
        <aside className="sandbox-control">
          {report && (
            <div className="sandbox-panel sandbox-proof">
              <h2>本地产物</h2>
              <dl>
                <div>
                  <dt>运行</dt>
                  <dd className="mono">{report.run_id}</dd>
                </div>
                <div>
                  <dt>轮次</dt>
                  <dd>{report.round_count}</dd>
                </div>
                <div>
                  <dt>角色行动</dt>
                  <dd>{actionCount}</dd>
                </div>
                <div>
                  <dt>写入</dt>
                  <dd>{report.artifacts.sandbox_rounds}</dd>
                </div>
                <div>
                  <dt>记忆</dt>
                  <dd>{report.summary.subjective_memory_entries_written} 条</dd>
                </div>
                {report.artifacts.intervention_constraint && (
                  <div>
                    <dt>干预</dt>
                    <dd>{report.artifacts.intervention_constraint}</dd>
                  </div>
                )}
                {report.artifacts.agent_decision_advisory && (
                  <div>
                    <dt>模型</dt>
                    <dd>{report.artifacts.agent_decision_advisory}</dd>
                  </div>
                )}
                {report.worldline_state?.artifact && (
                  <div>
                    <dt>世界线</dt>
                    <dd>{report.worldline_state.artifact}</dd>
                  </div>
                )}
              </dl>
            </div>
          )}

          <div className="sandbox-panel sandbox-autopilot">
            <h2>世界自演</h2>
            <textarea
              value={autopilotEvent}
              onChange={(event) => setAutopilotEvent(event.target.value)}
              rows={4}
              placeholder="写下世界自演的起点事件"
            />
            <label>
              <span className="muted tiny">自演目标</span>
              <select
                value={autopilotObjective}
                onChange={(event) => setAutopilotObjective(event.target.value)}
              >
                <option value="rounds">运行到轮数</option>
                <option value="event">运行到事件</option>
                <option value="time">运行到时间</option>
                <option value="anchor_change">运行到锚点变化</option>
                <option value="causal_debt">运行到因果债爆发</option>
                <option value="awakening">运行到角色觉醒</option>
              </select>
            </label>
            {autopilotObjective === "event" && (
              <label>
                <span className="muted tiny">目标事件</span>
                <input
                  value={autopilotStopEvent}
                  onChange={(event) => setAutopilotStopEvent(event.target.value)}
                />
              </label>
            )}
            {autopilotObjective === "time" && (
              <label>
                <span className="muted tiny">目标时间</span>
                <input
                  value={autopilotTimeLimit}
                  onChange={(event) => setAutopilotTimeLimit(event.target.value)}
                />
              </label>
            )}
            <label>
              <span className="muted tiny">自演轮数</span>
              <input
                type="number"
                min={1}
                max={10}
                value={autopilotRounds}
                onChange={(event) => setAutopilotRounds(Number(event.target.value) || 1)}
              />
            </label>
            <button
              className="btn btn--primary"
              disabled={autopilotLoading || !autopilotEvent.trim()}
              onClick={runAutopilot}
            >
              {autopilotLoading ? "世界自演中…" : "启动自演"}
            </button>
            <p className="muted tiny">
              自演会连续运行沙盘轮次，写入任务进度、检查点和 autopilot_report.json。
            </p>
          </div>
        </aside>

        <main className="sandbox-main" ref={resultsRef}>
          {error && <ErrorState message={error} onRetry={runRound} />}
          {autopilotError && <ErrorState message={autopilotError} onRetry={runAutopilot} />}
          {!error && !round && !autopilotReport && (
            <section className="sandbox-section sandbox-preflight-map" aria-label="开跑前路标">
              <div className="sandbox-section__title">
                <div>
                  <p className="tiny muted">开跑前路标</p>
                  <h2>先让这一轮有事可跑</h2>
                </div>
                <span className="badge badge--jade">未运行</span>
              </div>
              <p className="sandbox-preflight-map__intro">
                这不是普通表单。先放入一个会打破平衡的事件，再决定读者是否入局；跑完后优先看“本轮已发生”，再去卷宗和世界线追后果。
              </p>
              <div className="sandbox-preflight-map__grid">
                <article>
                  <span>第一步</span>
                  <strong>写一个能打破平衡的大事件</strong>
                  <p className="muted tiny">
                    当前草稿会被写成角色行动、主观记忆、因果债和世界线状态。
                  </p>
                  <div className="sandbox-preflight-map__actions">
                    <button className="btn btn--ghost tiny" onClick={focusEventDraft}>
                      去写事件
                    </button>
                  </div>
                </article>
                <article>
                  <span>可选</span>
                  <strong>决定读者要不要入局</strong>
                  <p className="muted tiny">
                    不投干预也能运行；投放后世界会解释它怎样被吸收、抵抗或转译。
                  </p>
                  <div className="sandbox-preflight-map__actions">
                    <button className="btn btn--ghost tiny" onClick={openInterventionControls}>
                      {hasInterventionDraft ? "调整干预" : "添加干预"}
                    </button>
                  </div>
                </article>
                <article>
                  <span>出口</span>
                  <strong>跑完先看本轮已发生</strong>
                  <p className="muted tiny">
                    结果会先汇总行动、记忆和世界变化，再接到卷宗阅读与世界线代偿。
                  </p>
                  <div className="sandbox-preflight-map__actions">
                    <button
                      className="btn btn--primary tiny"
                      disabled={!canRun}
                      onClick={runRound}
                    >
                      从这里启动推演
                    </button>
                    <button
                      className="btn btn--ghost tiny"
                      onClick={() =>
                        navigate({ name: "dossierReading", slug, worldlineId: "main" })
                      }
                    >
                      先看卷宗
                    </button>
                  </div>
                </article>
              </div>
            </section>
          )}
          {autopilotReport && (
            <section className="sandbox-section sandbox-autopilot-report">
              <div className="sandbox-section__title">
                <h2>昨夜世界演化报告</h2>
                <div className="sandbox-section__actions">
                  <button
                    className="btn btn--ghost tiny"
                    onClick={() =>
                      navigate({
                        name: "worldline",
                        slug,
                        worldlineId: autopilotReport.worldline_id || "main",
                      })
                    }
                  >
                    查看世界线
                  </button>
                  <span className="badge badge--gold">
                    {autopilotReport.rounds_completed} 个检查点
                  </span>
                </div>
              </div>
              <p>{autopilotReport.final_world_stage.summary}</p>
              {autopilotReport.progress && (
                <p className="muted tiny">
                  任务 {autopilotReport.task?.task_id ?? "本地任务"} ·{" "}
                  {autopilotReport.task?.status ?? autopilotReport.status ?? "unknown"} ·{" "}
                  {autopilotReport.progress.current_round}/
                  {autopilotReport.progress.target_round} ·{" "}
                  {autopilotReport.progress.percent}%
                </p>
              )}
              {autopilotReport.task?.task_id && (
                <div className="sandbox-section__actions sandbox-task-actions">
                  <button
                    className="btn btn--ghost tiny"
                    disabled={autopilotLoading}
                    onClick={() => updateAutopilotTask("refresh")}
                  >
                    刷新进度
                  </button>
                  <button
                    className="btn btn--ghost tiny"
                    disabled={autopilotLoading}
                    onClick={() => updateAutopilotTask("pause")}
                  >
                    暂停
                  </button>
                  <button
                    className="btn btn--ghost tiny"
                    disabled={autopilotLoading}
                    onClick={() => updateAutopilotTask("resume")}
                  >
                    恢复
                  </button>
                </div>
              )}
              {overnightReport && (
                <section className="sandbox-overnight-brief" aria-label="昨夜世界醒来台">
                  <div className="sandbox-overnight-brief__intro">
                    <div>
                      <p className="tiny muted">昨夜世界醒来台</p>
                      <h3>醒来时，世界已经自己走了一夜</h3>
                    </div>
                    <div className="sandbox-overnight-brief__actions">
                      <button
                        className="btn btn--primary tiny"
                        onClick={() => {
                          if (overnightReadAction?.route) {
                            openReadableRoute(overnightReadAction.route);
                            return;
                          }
                          navigate({
                            name: "dossierReading",
                            slug,
                            worldlineId: autopilotReport.worldline_id || "main",
                          });
                        }}
                      >
                        从这里继续读
                      </button>
                      <button
                        className="btn btn--ghost tiny"
                        onClick={() =>
                          document
                            .querySelector(".sandbox-timeline")
                            ?.scrollIntoView({ behavior: "smooth", block: "start" })
                        }
                      >
                        查看昨夜时间线
                      </button>
                    </div>
                  </div>

                  <div className="sandbox-overnight-brief__grid">
                    <article>
                      <span>昨夜发生</span>
                      <strong>{overnightReport.what_happened}</strong>
                      {overnightScene?.scene_hook && (
                        <p className="muted tiny">小说节拍：{overnightScene.scene_hook}</p>
                      )}
                    </article>
                    <article>
                      <span>带着记忆醒来</span>
                      <strong>
                        {overnightMemory?.character_id
                          ? `${overnightMemory.character_id} 记住了`
                          : "角色记忆已经写入"}
                      </strong>
                      <p className="muted tiny">
                        {overnightMemory?.remembered ||
                          autopilotReport.readable_entry?.memory_readout.summary ||
                          "这一夜的变化会进入角色主观记忆链。"}
                      </p>
                    </article>
                    <article>
                      <span>世界为什么变了</span>
                      <strong>{overnightReport.why_world_changed}</strong>
                      {autopilotReport.stop_condition?.evidence && (
                        <p className="muted tiny">
                          停止证据：{autopilotReport.stop_condition.evidence}
                        </p>
                      )}
                    </article>
                    <article>
                      <span>从这里继续读</span>
                      <strong>
                        {overnightContinuation?.label ||
                          overnightReadAction?.label ||
                          "接回连续正文"}
                      </strong>
                      <p className="muted tiny">
                        {overnightContinuation?.checkpoint_id
                          ? `最近检查点：${overnightContinuation.checkpoint_id}`
                          : overnightReadAction?.reason ||
                            "把昨夜自演接到卷宗阅读或作者台。"}
                      </p>
                    </article>
                  </div>

                  {(autopilotReport.failure?.message ||
                    overnightReport.checkpoint_recovery?.can_resume) && (
                    <div className="sandbox-overnight-brief__notice">
                      {autopilotReport.failure?.message && (
                        <p className="muted tiny">
                          中断原因：{autopilotReport.failure.message}；最近检查点：
                          {autopilotReport.failure.latest_checkpoint || "暂无"}
                        </p>
                      )}
                      {overnightReport.checkpoint_recovery?.can_resume && (
                        <p className="muted tiny">
                          可从{" "}
                          {overnightReport.checkpoint_recovery.resume_from_checkpoint}{" "}
                          恢复自演。
                        </p>
                      )}
                    </div>
                  )}
                </section>
              )}
              {autopilotReport.readable_entry && (
                <WakeReadingEntry entry={autopilotReport.readable_entry} />
              )}
              {autopilotReport.overnight_report?.timeline?.length ? (
                <div className="sandbox-timeline">
                  {autopilotReport.overnight_report.timeline.map((item) => (
                    <article key={`${item.round_index}-${item.checkpoint_id}`}>
                      <span>第 {item.round_index} 轮</span>
                      <strong>{item.stage}</strong>
                      <p className="muted tiny">
                        {item.major_event} · {item.causal_debt} · 写入{" "}
                        {item.remembered_count ?? 0} 条记忆
                      </p>
                    </article>
                  ))}
                </div>
              ) : null}
              {autopilotReport.overnight_report?.narrative_timeline?.length ? (
                <div className="sandbox-timeline">
                  {autopilotReport.overnight_report.narrative_timeline.map((item) => (
                    <article key={`story-${item.round_index}-${item.checkpoint_id}`}>
                      <span>小说节拍 · 第 {item.round_index} 轮</span>
                      <strong>{item.scene_hook}</strong>
                      <p>{item.character_miscalculation}</p>
                      <p className="muted tiny">{item.materialized_consequence}</p>
                      <p className="muted tiny">{item.conflict_escalation}</p>
                      <p className="muted tiny">下一章：{item.chapter_handoff}</p>
                    </article>
                  ))}
                </div>
              ) : null}
              <p className="muted tiny">
                {autopilotReport.stop_reason} · {autopilotReport.artifact}
              </p>
              <div className="sandbox-checkpoints">
                {autopilotReport.checkpoints.map((checkpoint) => (
                  <article key={checkpoint.round_index}>
                    <div>
                      <strong>第 {checkpoint.round_index} 轮</strong>
                      <span className="muted tiny mono">
                        {checkpoint.sandbox_run_id}
                      </span>
                    </div>
                    <p>{checkpoint.stage}</p>
                    <p className="muted tiny">{checkpoint.causal_debt}</p>
                    {checkpoint.checkpoint_id && (
                      <button
                        className="btn btn--ghost tiny"
                        onClick={() =>
                          navigate({
                            name: "checkpoint",
                            slug,
                            worldlineId: autopilotReport.worldline_id || "main",
                            runId: autopilotReport.run_id,
                            checkpointId: checkpoint.checkpoint_id || "",
                          })
                        }
                      >
                        回放检查点
                      </button>
                    )}
                  </article>
                ))}
              </div>
            </section>
          )}
          {!error && !round && !autopilotReport && (
            <EmptyState
              title="沙盘尚未运行"
              hint="写下一个大事件，先看角色会如何各自行动。"
            />
          )}
          {!error && round && (
            <>
              <section
                className="sandbox-section sandbox-result-bridge"
                aria-label="本轮沙盘结果承接"
              >
                <div className="sandbox-result-bridge__copy">
                  <p className="tiny muted">本轮已发生</p>
                  <h2>世界把事件消化成行动、记忆和下一章</h2>
                  <p>
                    {round.world_state_delta.trigger ||
                      round.major_event ||
                      "本轮事件已经进入世界状态，等待继续承接。"}
                  </p>
                </div>
                <dl className="sandbox-result-bridge__stats">
                  {resultBridgeStats.map(([label, value]) => (
                    <div key={label}>
                      <dt>{label}</dt>
                      <dd>{value}</dd>
                    </div>
                  ))}
                </dl>
                <div className="sandbox-result-bridge__signals">
                  {resultBridgeSignals.map(([label, value]) => (
                    <article key={label}>
                      <span>{label}</span>
                      <strong>{value || "暂无变化"}</strong>
                    </article>
                  ))}
                </div>
                <div className="sandbox-result-bridge__spotlight">
                  <span>最先被推到台前</span>
                  <strong>{leadAction?.character_name || "角色行动"}</strong>
                  <p>
                    {leadAction?.intent ||
                      firstPossibility?.brief ||
                      "继续推进一轮，观察谁会承压、误判或反抗。"}
                  </p>
                </div>
                <div className="sandbox-result-bridge__actions">
                  <button
                    className="btn btn--primary tiny"
                    onClick={() =>
                      navigate({
                        name: "dossierReading",
                        slug,
                        worldlineId: round.worldline_id || "main",
                      })
                    }
                  >
                    读成正文
                  </button>
                  <button
                    className="btn btn--ghost tiny"
                    onClick={() =>
                      navigate({
                        name: "worldline",
                        slug,
                        worldlineId: round.worldline_id || "main",
                      })
                    }
                  >
                    看世界线
                  </button>
                  <button
                    className="btn btn--ghost tiny"
                    onClick={() => navigate({ name: "lens", slug })}
                  >
                    生成多视角
                  </button>
                  <button className="btn btn--ghost tiny" onClick={focusControl}>
                    再推一轮
                  </button>
                </div>
              </section>
              <section
                className="sandbox-section sandbox-result-reading-guide"
                aria-label="结果阅读顺序"
              >
                <div className="sandbox-section__title">
                  <div>
                    <p className="tiny muted">结果阅读顺序</p>
                    <h2>先读懂这轮，再进入证据和下一章</h2>
                  </div>
                  <span className="badge badge--jade">跑后导读</span>
                </div>
                <div className="sandbox-result-reading-guide__grid">
                  {resultReadingGuide.map((item) => (
                    <article key={item.label}>
                      <span>{item.label}</span>
                      <strong>{item.title}</strong>
                      <p className="muted tiny">{item.detail}</p>
                      <div className="sandbox-result-reading-guide__actions">
                        <button className="btn btn--ghost tiny" onClick={item.onClick}>
                          {item.action}
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
              {strategyInteractions.length > 0 && (
                <section
                  ref={strategyBoardRef}
                  className="sandbox-section sandbox-strategy-board"
                  aria-label="本轮策略棋盘"
                >
                  <div className="sandbox-section__title">
                    <div>
                      <p className="tiny muted">策略棋盘</p>
                      <h2>谁在算计谁，以及世界会怎么被推歪</h2>
                    </div>
                    <span className="badge badge--gold">
                      {strategyInteractions.length} 条暗线
                    </span>
                  </div>
                  <div className="sandbox-strategy-board__grid">
                    {strategyInteractions.map((item) => (
                      <article
                        className="sandbox-strategy-card"
                        key={`${item.actorId}-${item.targetName}-${item.tactic}`}
                      >
                        <div className="sandbox-strategy-card__route">
                          <strong>{item.actorName}</strong>
                          <span aria-hidden>→</span>
                          <strong>{item.targetName}</strong>
                        </div>
                        <p>{item.tactic}</p>
                        <dl>
                          <div>
                            <dt>私下目的</dt>
                            <dd>{item.privateGoal}</dd>
                          </div>
                          <div>
                            <dt>手里筹码</dt>
                            <dd>{item.leverage}</dd>
                          </div>
                          <div>
                            <dt>可能误判</dt>
                            <dd>{item.misread}</dd>
                          </div>
                          <div>
                            <dt>风险</dt>
                            <dd>{item.risk}</dd>
                          </div>
                        </dl>
                        <div className="sandbox-strategy-card__effect">
                          <span>世界影响</span>
                          <strong>{item.effect}</strong>
                          <p>{item.hook}</p>
                        </div>
                      </article>
                    ))}
                  </div>
                </section>
              )}
              {strategyInteractions.length > 0 && (
                <section
                  className="sandbox-section sandbox-strategy-continuation"
                  aria-label="下一轮策略暗线承接"
                >
                  <div className="sandbox-section__title">
                    <div>
                      <p className="tiny muted">策略承接</p>
                      <h2>下一轮暗线承接</h2>
                    </div>
                    {queuedStrategyTitle ? (
                      <span className="badge badge--jade">已放入运行台</span>
                    ) : (
                      <span className="badge">可继续发酵</span>
                    )}
                  </div>
                  <p className="muted">
                    这些算计不只用来阅读，也可以直接成为下一轮事件，让误判、筹码和世界影响继续发酵。
                  </p>
                  {queuedStrategyTitle && (
                    <p className="muted tiny">已放入运行台：{queuedStrategyTitle}</p>
                  )}
                  <div className="sandbox-strategy-continuation__grid">
                    {strategyInteractions.map((item) => (
                      <article
                        key={`${item.actorId}-${item.targetName}-${item.tactic}-seed`}
                      >
                        <div className="sandbox-strategy-continuation__event">
                          <span>暗线种子</span>
                          <strong>
                            {item.actorName}试探{item.targetName}
                          </strong>
                          <p>{item.tactic}</p>
                        </div>
                        <dl>
                          <div>
                            <dt>可能误判</dt>
                            <dd>{item.misread}</dd>
                          </div>
                          <div>
                            <dt>世界影响</dt>
                            <dd>{item.effect}</dd>
                          </div>
                        </dl>
                        <div className="sandbox-strategy-continuation__actions">
                          <button
                            className="btn btn--ghost tiny"
                            onClick={() => queueStrategySeed(item)}
                          >
                            作为下一轮暗线
                          </button>
                          <span className="muted tiny">不沿用上轮临时干预</span>
                        </div>
                      </article>
                    ))}
                  </div>
                </section>
              )}
              {interventionConstraint && (
                <section className="sandbox-section sandbox-intervention">
                  <div className="sandbox-section__title">
                    <h2>已投放干预约束</h2>
                    <span className="badge badge--gold">
                      {projectionModeLabel(interventionConstraint.projection_mode)}
                    </span>
                  </div>
                  <p>{interventionConstraint.content}</p>
                  <dl>
                    <div>
                      <dt>分支轴</dt>
                      <dd>{interventionConstraint.branch_axis?.axis ?? "分支变量"}</dd>
                    </div>
                    <div>
                      <dt>法则吸收</dt>
                      <dd>{interventionConstraint.translation_strategy?.strategy}</dd>
                    </div>
                    <div>
                      <dt>命运线</dt>
                      <dd>{interventionConstraint.branch_axis?.question}</dd>
                    </div>
                    <div>
                      <dt>因果债</dt>
                      <dd>
                        {interventionConstraint.causal_debt?.level ?? "medium"} /{" "}
                        {interventionConstraint.causal_debt?.score ?? 0}
                      </dd>
                    </div>
                    <div>
                      <dt>投放结果</dt>
                      <dd>{interventionConstraint.worldline_judgement?.reason}</dd>
                    </div>
                    {interventionConstraint.compatibility?.foreign_object_intrusion && (
                      <div>
                        <dt>异物入侵</dt>
                        <dd>已标记，原世界线不会被静默污染。</dd>
                      </div>
                    )}
                    {interventionConstraint.worldline_tianming_snapshot && (
                      <div>
                        <dt>天命快照</dt>
                        <dd className="mono">
                          {interventionConstraint.worldline_tianming_snapshot.artifact}
                        </dd>
                      </div>
                    )}
                  </dl>
                  {consequenceDomains.length > 0 && (
                    <div className="sandbox-consequences">
                      <div className="sandbox-consequences__head">
                        <strong>具象代偿账</strong>
                        <span className="muted tiny">
                          {latestConsequence?.source_run_id
                            ? `来自 ${latestConsequence.source_run_id}`
                            : "本轮世界状态"}
                        </span>
                      </div>
                      <div className="sandbox-consequence-grid">
                        {consequenceDomains.map(([key, item]) => (
                          <article key={key}>
                            <span>{item.label || key}</span>
                            <strong>{item.current || "等待世界继续显形"}</strong>
                            <p className="muted tiny">
                              {item.pressure || "压力待定"}
                              {item.bearer ? ` · 承压：${item.bearer}` : ""}
                            </p>
                          </article>
                        ))}
                      </div>
                      {consequenceNextRoundHint && (
                        <p className="muted tiny">
                          {consequenceNextRoundHint}
                        </p>
                      )}
                    </div>
                  )}
                </section>
              )}
              {worldlineState?.status && (
                <section className="sandbox-section sandbox-intervention">
                  <div className="sandbox-section__title">
                    <h2>世界线承接</h2>
                    <div className="sandbox-section__actions">
                      <button
                        className="btn btn--ghost tiny"
                        onClick={() =>
                          navigate({
                            name: "worldline",
                            slug,
                            worldlineId: worldlineState.current_worldline || "main",
                          })
                        }
                      >
                        打开世界线档案
                      </button>
                      <span className="badge badge--jade">
                        {worldlineState.branch_state?.continuation_status ?? "runnable"}
                      </span>
                    </div>
                  </div>
                  <dl>
                    <div>
                      <dt>当前世界线</dt>
                      <dd>{worldlineState.current_worldline}</dd>
                    </div>
                    <div>
                      <dt>来源干预</dt>
                      <dd>
                        {worldlineState.source_intervention?.content ||
                          "本轮未继承干预"}
                      </dd>
                    </div>
                    <div>
                      <dt>快照审计</dt>
                      <dd>
                        {worldlineState.tianming_snapshot?.audit_status ||
                          "无需快照审计"}
                      </dd>
                    </div>
                    <div>
                      <dt>因果债</dt>
                      <dd>
                        {worldlineState.causal_debt?.level}/
                        {worldlineState.causal_debt?.score}
                      </dd>
                    </div>
                    <div>
                      <dt>下一轮</dt>
                      <dd>
                        {worldlineState.continuation_inputs?.major_event_hint ||
                          "继续消化本轮选择"}
                      </dd>
                    </div>
                  </dl>
                </section>
              )}
              {round.llm_decision_advisory &&
                round.llm_decision_advisory.status !== "skipped" && (
                  <section className="sandbox-section sandbox-llm-advisory">
                    <div className="sandbox-section__title">
                      <h2>模型决策建议</h2>
                      <span className="badge badge--gold">
                        {llmDecisionStatusLabel(round.llm_decision_advisory.status)}
                      </span>
                    </div>
                    <p>
                      {round.llm_decision_advisory.summary ||
                        round.llm_decision_advisory.fallback_reason ||
                        "本轮已尝试让真实模型给角色补一层临场判断。"}
                    </p>
                    <p className="muted tiny">
                      {llmGeneratedByLabel(round.llm_decision_advisory.generated_by)} · 命中{" "}
                      {round.llm_decision_advisory.action_count ?? 0} 个角色 · 不改
                      run_scene 默认行为
                    </p>
                  </section>
                )}
              {actionFocusDeck.length > 0 && (
                <section
                  className="sandbox-section sandbox-action-focus"
                  aria-label="角色行动焦点"
                >
                  <div className="sandbox-section__title">
                    <div>
                      <p className="tiny muted">角色行动焦点</p>
                      <h2>先追最能推动下一轮的人</h2>
                    </div>
                    {queuedActionFocusTitle ? (
                      <span className="badge badge--jade">已放入运行台</span>
                    ) : (
                      <span className="badge">行动焦点</span>
                    )}
                  </div>
                  <p className="muted">
                    这里先把完整行动链压成几张可扫读卡：谁最值得追、行动背后的真实意图是什么、风险与结果会怎样进入下一轮。
                  </p>
                  {queuedActionFocusTitle && (
                    <p className="muted tiny">已放入运行台：{queuedActionFocusTitle}</p>
                  )}
                  <div className="sandbox-action-focus__grid">
                    {actionFocusDeck.map((card) => (
                      <article className="sandbox-action-focus-card" key={card.id}>
                        <div className="sandbox-action-focus-card__meta">
                          <span>{card.label}</span>
                          <strong>{card.title}</strong>
                          <small>{card.role}</small>
                        </div>
                        <p className="sandbox-action-focus-card__line">{card.action}</p>
                        <dl className="sandbox-action-focus-card__signals">
                          <div>
                            <dt>行动背后的真实意图</dt>
                            <dd>{card.intent}</dd>
                          </div>
                          <div>
                            <dt>风险与结果</dt>
                            <dd>{card.riskResult}</dd>
                          </div>
                          <div>
                            <dt>记忆种子</dt>
                            <dd>{card.memory}</dd>
                          </div>
                        </dl>
                        <div className="sandbox-action-focus-card__actions">
                          <button
                            className="btn btn--ghost tiny"
                            onClick={focusActionChain}
                          >
                            定位行动链
                          </button>
                          <button
                            className="btn btn--ghost tiny"
                            onClick={() =>
                              navigate({
                                name: "characterVolume",
                                slug,
                                worldlineId: round.worldline_id,
                                characterId: card.characterId,
                              })
                            }
                          >
                            追角色卷
                          </button>
                          <button
                            className="btn btn--ghost tiny"
                            onClick={() => queueActionFocusSeed(card)}
                          >
                            回填为下一轮事件
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                </section>
              )}
              <section className="sandbox-section" ref={actionChainRef}>
                <div className="sandbox-section__title">
                  <h2>角色行动链</h2>
                  <span className="badge badge--jade">
                    第 {round.round_index} 轮
                  </span>
                </div>
                <div className="sandbox-actions">
                  {round.character_actions.map((item) => (
                    <article className="sandbox-action" key={item.character_id}>
                      <div className="sandbox-action__head">
                        <span className="sandbox-action__seal" aria-hidden>
                          {item.character_name.slice(0, 1)}
                        </span>
                        <div>
                          <h3>{item.character_name}</h3>
                          <p className="muted tiny">{item.narrative_role}</p>
                        </div>
                        <span className="badge badge--gold">{item.stance}</span>
                      </div>
                      <p className="sandbox-action__line">{item.intent}</p>
                      <p>{item.visible_action ?? item.action}</p>
                      {item.true_intent && (
                        <p className="muted tiny">真实意图：{item.true_intent}</p>
                      )}
                      {item.awareness?.level === "L5" && (
                        <div className="sandbox-callout">
                          <strong>命痕觉醒 · {item.resistance_behavior?.label}</strong>
                          <p>{item.awareness.abnormality}</p>
                          <p className="muted tiny">
                            {item.resistance_behavior?.description}
                          </p>
                        </div>
                      )}
                      {item.awareness?.level === "contaminated" && (
                        <div className="sandbox-callout sandbox-callout--quiet">
                          <strong>
                            命痕回声 ·{" "}
                            {item.meme_propagation_readout?.reaction_label ??
                              item.meme_propagation?.reaction?.label ??
                              "反应未明"}
                          </strong>
                          <p>{item.awareness.abnormality}</p>
                          <p className="muted tiny">
                            来源：
                            {item.meme_propagation_readout?.source_character_name ??
                              item.meme_propagation?.source_character_name ??
                              "未知"}{" "}
                            ·
                            {item.meme_propagation_readout?.belief_label ??
                              beliefDecisionLabel(item.meme_propagation?.belief_decision)}
                            {typeof item.meme_propagation_readout?.credibility_score ===
                            "number"
                              ? ` · 可信度 ${item.meme_propagation_readout.credibility_score}`
                              : typeof item.meme_propagation?.credibility_score === "number"
                                ? ` · 可信度 ${item.meme_propagation.credibility_score}`
                                : ""}
                          </p>
                          {item.meme_propagation_readout?.truth_payload && (
                            <p className="muted tiny">
                              真相：{item.meme_propagation_readout.truth_payload}
                            </p>
                          )}
                        </div>
                      )}
                      {item.awareness?.level === "L5" &&
                        item.meme_propagation_readout?.truth_payload && (
                          <p className="muted tiny">
                            觉醒传播：
                            {item.meme_propagation_readout.readable_summary ||
                              item.meme_propagation_readout.truth_payload}
                          </p>
                        )}
                      {item.meme_contamination?.status === "active" && (
                        <p className="muted tiny">
                          模因传播：{item.meme_contamination.spread_vector?.join("；")}
                        </p>
                      )}
                      {item.meme_propagation?.status === "received" && (
                        <div className="sandbox-action__meme">
                          <span>模因采信</span>
                          <strong>
                            {item.meme_propagation_readout?.belief_label ??
                              beliefDecisionLabel(item.meme_propagation.belief_decision)}
                          </strong>
                          <p>
                            {item.meme_propagation_readout?.belief_reason ??
                              item.meme_propagation.belief_reason}
                          </p>
                          <dl>
                            <div>
                              <dt>传播来源</dt>
                              <dd>
                                {item.meme_propagation_readout?.source_character_name ??
                                  item.meme_propagation.source_character_name}
                              </dd>
                            </div>
                            <div>
                              <dt>真相载荷</dt>
                              <dd>
                                {item.meme_propagation_readout?.truth_payload ??
                                  item.meme_propagation.belief_payload}
                              </dd>
                            </div>
                            <div>
                              <dt>反应</dt>
                              <dd>
                                {item.meme_propagation_readout?.reaction_label ??
                                  item.meme_propagation.reaction?.label ??
                                  "未记录"}
                              </dd>
                            </div>
                            <div>
                              <dt>人设信号</dt>
                              <dd>{item.meme_propagation.signals?.persona}</dd>
                            </div>
                            <div>
                              <dt>异常感</dt>
                              <dd>{item.meme_propagation.signals?.anomaly}</dd>
                            </div>
                          </dl>
                        </div>
                      )}
                      {item.llm_decision_advisory?.status === "ready" && (
                        <div className="sandbox-action__llm">
                          <span>模型临场判断</span>
                          <strong>{item.llm_decision_advisory.situational_judgement}</strong>
                          <dl>
                            <div>
                              <dt>采信</dt>
                              <dd>{item.llm_decision_advisory.belief_update}</dd>
                            </div>
                            <div>
                              <dt>欺骗</dt>
                              <dd>{item.llm_decision_advisory.deception_strategy}</dd>
                            </div>
                            <div>
                              <dt>传播</dt>
                              <dd>{item.llm_decision_advisory.propagation_choice}</dd>
                            </div>
                            <div>
                              <dt>反抗</dt>
                              <dd>{item.llm_decision_advisory.resistance_choice}</dd>
                            </div>
                            {item.strategic_interaction?.target_character_id && (
                              <>
                                <div>
                                  <dt>算计对象</dt>
                                  <dd>{item.strategic_interaction.target_character_id}</dd>
                                </div>
                                <div>
                                  <dt>策略</dt>
                                  <dd>{item.strategic_interaction.tactic}</dd>
                                </div>
                                <div>
                                  <dt>误判</dt>
                                  <dd>{item.strategic_interaction.assumed_misread}</dd>
                                </div>
                                <div>
                                  <dt>结果</dt>
                                  <dd>{item.strategic_interaction.expected_world_effect}</dd>
                                </div>
                              </>
                            )}
                          </dl>
                        </div>
                      )}
                      <p className="muted tiny">{item.reason}</p>
                      {item.decision_inputs && (
                        <div className="sandbox-action__decision-block">
                          <span>决策输入</span>
                          <dl className="sandbox-action__decision">
                            <div>
                              <dt>欲望</dt>
                              <dd>{item.decision_inputs.desire}</dd>
                            </div>
                            <div>
                              <dt>恐惧</dt>
                              <dd>{item.decision_inputs.fear}</dd>
                            </div>
                            <div>
                              <dt>上一轮记忆</dt>
                              <dd>
                                {item.decision_inputs.previous_memory_belief ||
                                  "暂无上一轮主观认知"}
                              </dd>
                            </div>
                            <div>
                              <dt>天命压力</dt>
                              <dd>{item.decision_inputs.tianming_pressure}</dd>
                            </div>
                          </dl>
                        </div>
                      )}
                      {(item.expected_outcome || item.risk || item.action_outcome) && (
                        <div className="sandbox-action__memory">
                          <span>预期与风险</span>
                          <strong>
                            {item.expected_outcome ?? "继续观察"}；风险：
                            {item.risk ?? "未记录"}
                          </strong>
                          {item.action_outcome?.reason && (
                            <p className="muted tiny">
                              结果：{item.action_outcome.status ?? "pending"} ·{" "}
                              {item.action_outcome.reason}
                            </p>
                          )}
                        </div>
                      )}
                      <div className="sandbox-action__memory">
                        <span>将写入记忆种子</span>
                        <strong>{item.memory_seed?.inferred?.[0] ?? "形成新的判断"}</strong>
                      </div>
                      <p className="muted tiny">
                        {item.memory_influence ?? item.previous_subjective_memory}
                      </p>
                      <div className="sandbox-action__buttons">
                        <button
                          className={`btn btn--ghost sandbox-action__button ${
                            selectedCharacterId === item.character_id ? "is-active" : ""
                          }`}
                          onClick={() => loadMemory(item.character_id, round.worldline_id)}
                        >
                          查看个人记忆
                        </button>
                        <button
                          className="btn btn--ghost sandbox-action__button"
                          onClick={() =>
                            navigate({
                              name: "characterVolume",
                              slug,
                              worldlineId: round.worldline_id,
                              characterId: item.character_id,
                            })
                          }
                        >
                          打开角色卷
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              </section>

              <section className="sandbox-section">
                <div className="sandbox-section__title">
                  <h2>角色个人卷雏形</h2>
                  <span className="badge badge--jade">
                    {memoryReport?.entry_count ?? 0} 条主观记忆
                  </span>
                </div>
                {memoryLoading && <p className="muted">正在读取角色记忆…</p>}
                {memoryError && (
                  <ErrorState
                    message={memoryError}
                    onRetry={() => {
                      if (selectedCharacterId) loadMemory(selectedCharacterId, round.worldline_id);
                    }}
                  />
                )}
                {!memoryLoading && !memoryError && !memoryReport && (
                  <EmptyState
                    title="尚未选择角色"
                    hint="点击角色行动卡片下方的「查看个人记忆」。"
                  />
                )}
                {!memoryLoading && !memoryError && memoryReport && (
                  <div className="sandbox-memory">
                    <p className="muted tiny mono">{memoryReport.artifact}</p>
                    {memoryReport.entries.map((entry) => (
                      <article key={`${entry.source_run_id}-${entry.source_round_index}`}>
                        <div>
                          <strong>{entry.character_name}</strong>
                          <span className="muted tiny">
                            第 {entry.source_round_index} 轮 · {entry.source_major_event}
                          </span>
                        </div>
                        <p>{entry.new_belief}</p>
                        <dl>
                          {entry.perceived_event && (
                            <div className="sandbox-memory__wide">
                              <dt>主观感知</dt>
                              <dd>{entry.perceived_event}</dd>
                            </div>
                          )}
                          {entry.inner_thought && (
                            <div className="sandbox-memory__wide">
                              <dt>内心想法</dt>
                              <dd>{entry.inner_thought}</dd>
                            </div>
                          )}
                          {entry.inferred_motive && (
                            <div>
                              <dt>推测动机</dt>
                              <dd>{entry.inferred_motive}</dd>
                            </div>
                          )}
                          {entry.misbeliefs?.length ? (
                            <div>
                              <dt>误会</dt>
                              <dd>{entry.misbeliefs.join("；")}</dd>
                            </div>
                          ) : null}
                          {entry.unknown_canon_facts?.length ? (
                            <div>
                              <dt>未知正史</dt>
                              <dd>{entry.unknown_canon_facts.join("；")}</dd>
                            </div>
                          ) : null}
                          {entry.secret_visibility && (
                            <div>
                              <dt>秘密可见性</dt>
                              <dd>{entry.secret_visibility}</dd>
                            </div>
                          )}
                          <div>
                            <dt>看到</dt>
                            <dd>{entry.saw.join("；")}</dd>
                          </div>
                          <div>
                            <dt>做了</dt>
                            <dd>{entry.did.join("；")}</dd>
                          </div>
                          <div>
                            <dt>情绪</dt>
                            <dd>{entry.emotion_delta}</dd>
                          </div>
                          <div>
                            <dt>信任</dt>
                            <dd>{entry.trust_delta}</dd>
                          </div>
                          <div>
                            <dt>异常感</dt>
                            <dd>
                              {entry.anomaly_delta}
                              {typeof entry.anomaly_weight === "number"
                                ? `；权重 ${entry.anomaly_weight}`
                                : ""}
                            </dd>
                          </div>
                          {entry.fate_mark?.status && entry.fate_mark.status !== "inactive" && (
                            <div>
                              <dt>命痕</dt>
                              <dd>
                                {entry.fate_mark.label ?? "命痕"} ·{" "}
                                {entry.awareness_level ?? "未记录"}
                              </dd>
                            </div>
                          )}
                          {entry.higher_dimensional_awareness && (
                            <div className="sandbox-memory__wide">
                              <dt>高维真相</dt>
                              <dd>{entry.higher_dimensional_awareness}</dd>
                            </div>
                          )}
                          {entry.meme_propagation?.status === "received" && (
                            <>
                              <div>
                                <dt>传播来源</dt>
                                <dd>
                                  {entry.meme_propagation_readout?.source_character_name ??
                                    entry.meme_propagation.source_character_name}
                                </dd>
                              </div>
                              <div>
                                <dt>真相载荷</dt>
                                <dd>
                                  {entry.meme_propagation_readout?.truth_payload ??
                                    entry.meme_propagation.belief_payload}
                                </dd>
                              </div>
                              <div>
                                <dt>是否采信</dt>
                                <dd>
                                  {entry.meme_propagation_readout?.belief_label ??
                                    beliefDecisionLabel(entry.meme_propagation.belief_decision)}
                                  {typeof entry.meme_propagation_readout?.credibility_score ===
                                  "number"
                                    ? ` · 可信度 ${entry.meme_propagation_readout.credibility_score}`
                                    : typeof entry.meme_propagation.credibility_score === "number"
                                    ? ` · 可信度 ${entry.meme_propagation.credibility_score}`
                                    : ""}
                                </dd>
                              </div>
                              <div className="sandbox-memory__wide">
                                <dt>采信原因</dt>
                                <dd>
                                  {entry.meme_propagation_readout?.belief_reason ??
                                    entry.meme_propagation.belief_reason}
                                </dd>
                              </div>
                              <div>
                                <dt>反应</dt>
                                <dd>
                                  {entry.meme_propagation_readout?.reaction_label ??
                                    entry.meme_propagation.reaction?.label ??
                                    "未记录"}
                                </dd>
                              </div>
                            </>
                          )}
                        </dl>
                      </article>
                    ))}
                  </div>
                )}
              </section>

              <section className="sandbox-section sandbox-grid">
                <div>
                  <div className="sandbox-section__title">
                    <h2>冲突与信息传播</h2>
                  </div>
                  <div className="sandbox-list">
                    {round.conflicts.map((item) => (
                      <div className="sandbox-list__item" key={item.id}>
                        <strong>{item.title}</strong>
                        <p className="muted tiny">{item.cause}</p>
                      </div>
                    ))}
                    {round.information_flow.map((item) => (
                      <div className="sandbox-list__item" key={`${item.to}-${item.distortion}`}>
                        <strong>{item.to}</strong>
                        <p className="muted tiny">
                          以「{item.distortion}」理解：{item.content}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="sandbox-section__title">
                    <h2>世界状态变化</h2>
                  </div>
                  <div className="sandbox-delta">
                    {deltaItems.map(([label, value]) => (
                      <div key={label}>
                        <span>{label}</span>
                        <strong>{value}</strong>
                      </div>
                    ))}
                  </div>
                </div>
              </section>

              <section className="sandbox-section">
                <div className="sandbox-section__title">
                  <div>
                    <h2>后续剧情可能性</h2>
                    {queuedPossibilityTitle && (
                      <p className="muted tiny">
                        已放入运行台：{queuedPossibilityTitle}
                      </p>
                    )}
                  </div>
                </div>
                <div className="sandbox-possibilities">
                  {round.next_story_possibilities.map((item) => (
                    <article key={item.id}>
                      <h3>{item.title}</h3>
                      <p className="muted">{item.brief}</p>
                      <div className="sandbox-possibility__actions">
                        <button
                          className="btn btn--ghost tiny"
                          onClick={() => queueNextPossibility(item.title, item.brief)}
                        >
                          作为下一轮事件
                        </button>
                        <span className="muted tiny">不沿用上轮临时干预</span>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

function WakeReadingEntry({ entry }: { entry: WorldAutopilotReadableEntry }) {
  const memoryRows = entry.memory_readout.who_remembered_what.slice(0, 4);
  const domains = entry.causal_debt_readout.domains
    ? Object.entries(entry.causal_debt_readout.domains).slice(0, 4)
    : [];
  return (
    <section className="sandbox-wake-entry" aria-label="醒来阅读入口">
      <div className="sandbox-section__title">
        <div>
          <h3>醒来从这里读</h3>
          <p className="muted tiny">{entry.state_change_explanation.headline}</p>
        </div>
        <span className="badge badge--jade">
          {entry.latest_checkpoint.checkpoint_id || "最新检查点"}
        </span>
      </div>

      <div className="sandbox-wake-actions">
        {entry.primary_actions.map((action) => (
          <button
            key={action.id}
            className="btn btn--ghost"
            onClick={() => openReadableRoute(action.route)}
            title={action.reason}
          >
            {action.label}
          </button>
        ))}
      </div>

      <div className="sandbox-wake-grid">
        <article>
          <span>为什么世界变了</span>
          <strong>{entry.state_change_explanation.why_world_changed}</strong>
          {entry.state_change_explanation.stop_evidence && (
            <p className="muted tiny">
              停止证据：{entry.state_change_explanation.stop_evidence}
            </p>
          )}
        </article>
        <article>
          <span>谁记住了什么</span>
          <strong>{entry.memory_readout.summary}</strong>
          {memoryRows.map((item, index) => (
            <p className="muted tiny" key={`${item.character_id}-${index}`}>
              {item.character_id || "角色"}：{item.remembered || "记住了本轮变化"}
            </p>
          ))}
        </article>
        <article>
          <span>哪条因果债在发酵</span>
          <strong>{entry.causal_debt_readout.summary}</strong>
          {entry.causal_debt_readout.next_round_hint && (
            <p className="muted tiny">{entry.causal_debt_readout.next_round_hint}</p>
          )}
        </article>
      </div>

      {domains.length > 0 && (
        <div className="sandbox-wake-domains">
          {domains.map(([key, item]) => (
            <article key={key}>
              <span>{item.label || key}</span>
              <strong>{item.current || "等待显形"}</strong>
              <p className="muted tiny">
                {item.pressure || "压力待定"}
                {item.bearer ? ` · 承压：${item.bearer}` : ""}
              </p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function projectionModeLabel(mode?: string) {
  return mode === "wild_au" ? "暴走 AU" : "沉浸模式";
}

function beliefDecisionLabel(decision?: string) {
  if (decision === "accepted") return "采信";
  if (decision === "doubted") return "存疑";
  if (decision === "rejected") return "拒信";
  return "未判定";
}

function llmDecisionStatusLabel(status?: string) {
  if (status === "ready") return "已采入";
  if (status === "fallback") return "已降级";
  return "未启用";
}

function llmGeneratedByLabel(value?: string) {
  if (value === "real_llm") return "真实模型";
  if (value === "mock_llm") return "模拟模型";
  if (value === "fallback") return "本地降级";
  return "未记录来源";
}
