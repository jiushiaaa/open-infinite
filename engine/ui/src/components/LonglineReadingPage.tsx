import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import type { LonglineReadingReport, LonglineTimelineEntry } from "../api/types";
import { navigate } from "../routing";
import { EmptyState, ErrorState, Loading } from "./common/States";
import { WorldRunway } from "./WorldRunway";
import "./longlineReading.css";

const PHASE_LABELS: Record<string, string> = {
  scene: "正文场景",
  volume: "卷宗回声",
  confirmation: "确认入卷",
  checkpoint: "检查点",
};

interface LonglineEntityLaneEntry {
  id: string;
  sequence: number;
  phase: string;
  title: string;
  summary: string;
  evidenceCount: number;
}

interface LonglineEntityLaneMisbelief {
  id: string;
  status: string;
  misunderstanding: string;
  originEventTitle: string;
  authorPrompt: string;
  evidenceCount: number;
  nextRoute: string;
}

interface LonglineEntityLane {
  id: string;
  kind: "character" | "faction";
  label: string;
  name: string;
  summary: string;
  entryCount: number;
  evidenceCount: number;
  primaryEntryId: string;
  primaryEntryTitle: string;
  unresolvedCount: number;
  entries: LonglineEntityLaneEntry[];
  misbeliefs: LonglineEntityLaneMisbelief[];
}

interface LonglineMisbeliefNetworkNode {
  id: string;
  status: string;
  misunderstanding: string;
  originEventTitle: string;
  affectedCharacters: string[];
  evidenceCount: number;
  recoverySteps: string[];
  nextRoute: string;
  authorPrompt: string;
}

function buildLonglineEntityLanes(report: LonglineReadingReport): LonglineEntityLane[] {
  const lanes = new Map<string, LonglineEntityLane>();

  const toLaneEntry = (entry: LonglineTimelineEntry): LonglineEntityLaneEntry => ({
    id: entry.id,
    sequence: entry.sequence,
    phase: PHASE_LABELS[entry.phase] || entry.label,
    title: entry.title,
    summary: entry.consequence_hint || entry.body,
    evidenceCount: entry.evidence_refs.length,
  });

  const addLane = (kind: LonglineEntityLane["kind"], name: string, entry: LonglineTimelineEntry) => {
    const normalizedName = name.trim();
    if (!normalizedName) return;
    const id = `${kind}:${normalizedName}`;
    const existing = lanes.get(id);
    if (existing) {
      existing.entryCount += 1;
      existing.evidenceCount += entry.evidence_refs.length;
      if (!existing.summary && entry.consequence_hint) existing.summary = entry.consequence_hint;
      existing.entries.push(toLaneEntry(entry));
      return;
    }
    lanes.set(id, {
      id,
      kind,
      label: kind === "character" ? "按角色追" : "按势力追",
      name: normalizedName,
      summary: entry.consequence_hint || entry.body,
      entryCount: 1,
      evidenceCount: entry.evidence_refs.length,
      primaryEntryId: entry.id,
      primaryEntryTitle: entry.title,
      unresolvedCount: 0,
      entries: [toLaneEntry(entry)],
      misbeliefs: [],
    });
  };

  for (const entry of report.timeline_entries) {
    for (const character of entry.affected_characters) addLane("character", character, entry);
    for (const faction of entry.affected_factions) addLane("faction", faction, entry);
  }

  for (const item of report.misbelief_recovery.items) {
    for (const character of item.affected_characters) {
      const id = `character:${character.trim()}`;
      const lane = lanes.get(id);
      if (lane) {
        lane.unresolvedCount += item.status === "unresolved" ? 1 : 0;
        lane.summary = item.author_prompt || item.misunderstanding || lane.summary;
        lane.misbeliefs.push({
          id: item.id,
          status: item.status,
          misunderstanding: item.misunderstanding,
          originEventTitle: item.origin_event_title,
          authorPrompt: item.author_prompt,
          evidenceCount: item.evidence_refs.length,
          nextRoute: item.next_route,
        });
      }
    }
  }

  return [...lanes.values()]
    .sort((a, b) => {
      if (b.unresolvedCount !== a.unresolvedCount) return b.unresolvedCount - a.unresolvedCount;
      if (b.entryCount !== a.entryCount) return b.entryCount - a.entryCount;
      return b.evidenceCount - a.evidenceCount;
    })
    .slice(0, 4);
}

function buildLonglineMisbeliefNetwork(report: LonglineReadingReport): LonglineMisbeliefNetworkNode[] {
  return report.misbelief_recovery.items
    .map((item) => ({
      id: item.id,
      status: item.status,
      misunderstanding: item.misunderstanding,
      originEventTitle: item.origin_event_title,
      affectedCharacters: item.affected_characters,
      evidenceCount: item.evidence_refs.length,
      recoverySteps: item.recovery_steps,
      nextRoute: item.next_route,
      authorPrompt: item.author_prompt,
    }))
    .sort((a, b) => {
      const aOpen = a.status === "unresolved" ? 1 : 0;
      const bOpen = b.status === "unresolved" ? 1 : 0;
      if (bOpen !== aOpen) return bOpen - aOpen;
      return b.evidenceCount - a.evidenceCount;
    });
}

export function LonglineReadingPage({
  slug,
  worldlineId,
}: {
  slug: string;
  worldlineId: string;
}) {
  const [report, setReport] = useState<LonglineReadingReport | null>(null);
  const [activeEntryId, setActiveEntryId] = useState("");
  const [activeEntityLaneId, setActiveEntityLaneId] = useState("");
  const [activeMisbeliefId, setActiveMisbeliefId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const next = await api.getLonglineReading(slug, worldlineId);
      setReport(next);
      setActiveEntryId(next.timeline_entries[0]?.id || "");
      setActiveEntityLaneId("");
      setActiveMisbeliefId("");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [slug, worldlineId]);

  const activeEntry = useMemo(
    () =>
      report?.timeline_entries.find((entry) => entry.id === activeEntryId) ||
      report?.timeline_entries[0],
    [activeEntryId, report],
  );
  const activeThreads = report?.longline_threads.filter((thread) => thread.status === "active") || [];
  const activeEvent = report?.event_index.items.find((item) =>
    activeEntry ? item.entry_ids.includes(activeEntry.id) : false,
  );
  const primaryMisbelief =
    report?.misbelief_recovery.items.find((item) => item.status === "unresolved") ||
    report?.misbelief_recovery.items[0];
  const primaryOpenThread = report?.open_threads[0];
  const nextPrimaryAction = report?.next_actions[0];
  const longlineEntityLanes = useMemo(
    () => (report ? buildLonglineEntityLanes(report) : []),
    [report],
  );
  const selectedEntityLane = useMemo(
    () => longlineEntityLanes.find((lane) => lane.id === activeEntityLaneId),
    [activeEntityLaneId, longlineEntityLanes],
  );
  const longlineMisbeliefNetwork = useMemo(
    () => (report ? buildLonglineMisbeliefNetwork(report) : []),
    [report],
  );
  const selectedMisbeliefNode = useMemo(
    () =>
      longlineMisbeliefNetwork.find((node) => node.id === activeMisbeliefId) ||
      longlineMisbeliefNetwork[0],
    [activeMisbeliefId, longlineMisbeliefNetwork],
  );

  function focusEntry(entryId: string) {
    setActiveEntryId(entryId);
    window.requestAnimationFrame(() => {
      document.querySelector(".longline-current")?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    });
  }
  function focusEntityLane(lane: LonglineEntityLane) {
    setActiveEntityLaneId(lane.id);
    setActiveEntryId(lane.primaryEntryId);
    window.requestAnimationFrame(() => {
      document.querySelector(".longline-entity-focus")?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    });
  }
  function focusMisbeliefNode(node: LonglineMisbeliefNetworkNode) {
    setActiveMisbeliefId(node.id);
    window.requestAnimationFrame(() => {
      document.querySelector(".longline-misbelief-network")?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    });
  }
  const scrollToPageItem = (selector: string) => {
    document.querySelector(selector)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  if (loading) return <Loading label="正在铺开长线卷…" />;

  return (
    <div className="longline-page">
      <header className="longline-hero">
        <div>
          <p className="longline-hero__eyebrow muted">世界内部卷宗 · 长线卷</p>
          <h1>{report?.title || `${worldlineId} 的长线卷`}</h1>
          <p className="muted">
            {report?.subtitle ||
              "把事件、误会、角色记忆、势力代偿和作者下一章串成一条可继续阅读的世界长线。"}
          </p>
        </div>
        <div className="longline-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "dossierReading", slug, worldlineId })}
          >
            卷宗阅读
          </button>
          <button className="btn btn--primary" onClick={() => navigate({ name: "author", slug })}>
            送到作者台
          </button>
        </div>
      </header>

      {error && <ErrorState message={error} onRetry={load} />}
      {!error && report && (
        <>
          <nav className="longline-mobile-guide" aria-label="移动端长线导读">
            <button type="button" onClick={() => scrollToPageItem(".longline-briefing")}>
              <span>01</span>
              <strong>读长线</strong>
              <small>看世界发酵到哪</small>
            </button>
            <button type="button" onClick={() => scrollToPageItem(".longline-event-index")}>
              <span>02</span>
              <strong>按事件追</strong>
              <small>定位事件和证据</small>
            </button>
            <button type="button" onClick={() => scrollToPageItem(".longline-recovery")}>
              <span>03</span>
              <strong>回收误会</strong>
              <small>把张力写回下一章</small>
            </button>
            <button type="button" onClick={() => navigate({ name: "author", slug })}>
              <span>04</span>
              <strong>作者台</strong>
              <small>送去采纳续写</small>
            </button>
          </nav>

          <WorldRunway
            eyebrow="长线导览"
            title="先看世界如何持续发酵，再回到单个事件或角色"
            summary="长线卷不是新的生成器，它把已经发生的场景、卷宗、检查点和作者确认串起来，让用户感到这条世界线正在连续生长。"
            meta={
              <>
                <span className="badge badge--jade">
                  {report.status === "ready" ? "可读长线" : "资料不完整"}
                </span>
                <span className="badge">{worldlineId}</span>
                <span className="badge badge--gold">
                  {report.timeline_entries.length} 个节点
                </span>
              </>
            }
            steps={[
              {
                label: "事件",
                detail: "按时间线看发生了什么。",
                active: true,
              },
              {
                label: "发酵",
                detail: "追踪误会、记忆和势力压力如何延续。",
                active: activeThreads.length > 0,
              },
              {
                label: "承接",
                detail: "回到阅读、事件详情或作者台继续推进。",
                onClick: () => navigate({ name: "author", slug }),
              },
            ]}
            actions={[
              {
                label: "事件详情",
                detail: "拆开当前事件多视角",
                onClick: () =>
                  navigate({
                    name: "eventPerspective",
                    slug,
                    worldlineId,
                    eventId: "main",
                  }),
              },
              {
                label: "世界线",
                detail: "核对因果债和检查点",
                onClick: () => navigate({ name: "worldline", slug, worldlineId }),
              },
              {
                label: "作者台",
                detail: "把长线张力写进下一章",
                primary: true,
                onClick: () => navigate({ name: "author", slug }),
              },
            ]}
          />

          <section className="longline-recovery-orchestrator" aria-label="跨章回收台">
            <div className="longline-recovery-orchestrator__lead">
              <p className="muted tiny">跨章回收台</p>
              <h2>先决定这条长线要回收到哪里</h2>
              <p>
                把当前张力、首要误会、活跃线索和下一章钩子并排放好，避免读完长线后不知道该回沙盘、卷宗还是作者台。
              </p>
            </div>
            <article>
              <span>当前张力</span>
              <strong>{report.current_tension.summary}</strong>
              <p>{report.current_tension.primary_misbelief || "当前没有显式误会，但世界仍会沿事件后果继续发酵。"}</p>
              <button className="btn btn--ghost tiny" onClick={() => scrollToPageItem(".longline-current")}>
                看当前节点
              </button>
            </article>
            <article>
              <span>首要误会</span>
              <strong>{primaryMisbelief?.misunderstanding || "暂无待回收误会"}</strong>
              <p>
                {primaryMisbelief?.author_prompt ||
                  report.misbelief_recovery.fallback_action.reason ||
                  "先继续阅读长线，再决定是否送入作者台。"}
              </p>
              <button
                className="btn btn--ghost tiny"
                onClick={() =>
                  primaryMisbelief
                    ? openRoute(primaryMisbelief.next_route)
                    : openRoute(report.misbelief_recovery.fallback_action.route)
                }
              >
                回收误会
              </button>
            </article>
            <article>
              <span>活跃线索</span>
              <strong>
                {primaryOpenThread?.label ||
                  `${report.reading_progress.active_thread_count} 条线正在发酵`}
              </strong>
              <p>
                {primaryOpenThread?.reason ||
                  `${report.reading_progress.unresolved_thread_count} 条未解线索等待跨事件承接。`}
              </p>
              <button
                className="btn btn--ghost tiny"
                onClick={() =>
                  primaryOpenThread
                    ? openRoute(primaryOpenThread.next_route)
                    : scrollToPageItem(".longline-open-threads")
                }
              >
                追线索
              </button>
            </article>
            <article>
              <span>下一章钩子</span>
              <strong>{report.current_tension.next_chapter_hook || "送到作者台承接"}</strong>
              <p>把这条长线整理成下一章材料，保留误会、记忆和势力压力的余波。</p>
              <button className="btn btn--primary tiny" onClick={() => navigate({ name: "author", slug })}>
                送到作者台
              </button>
            </article>
          </section>

          <section className="longline-continuation-map" aria-label="跨章承接地图">
            <div className="longline-continuation-map__lead">
              <p className="muted tiny">跨章承接地图</p>
              <h2>世界线怎样继续</h2>
              <p>
                把当前阅读节点、来源事件、误会余波和下一轮去向连成一条线，让用户知道这不是孤立片段，而是会继续推动世界的因果链。
              </p>
            </div>
            <button
              type="button"
              className="longline-continuation-map__node is-current"
              onClick={() => scrollToPageItem(".longline-current")}
            >
              <span>现在读到</span>
              <strong>{activeEntry?.title || report.reading_progress.current_title}</strong>
              <small>
                {activeEntry
                  ? `${PHASE_LABELS[activeEntry.phase] || activeEntry.label} · ${activeEntry.evidence_refs.length} 条证据`
                  : report.reading_progress.summary}
              </small>
            </button>
            <button
              type="button"
              className="longline-continuation-map__node"
              onClick={() =>
                activeEvent?.entry_ids[0]
                  ? focusEntry(activeEvent.entry_ids[0])
                  : scrollToPageItem(".longline-event-index")
              }
            >
              <span>来源事件</span>
              <strong>{activeEvent?.title || "等待事件索引"}</strong>
              <small>
                {activeEvent
                  ? `${activeEvent.unresolved_count} 条未解线 · ${activeEvent.evidence_count} 条证据`
                  : "按事件追踪这段长线来自哪里。"}
              </small>
            </button>
            <button
              type="button"
              className="longline-continuation-map__node"
              onClick={() =>
                primaryMisbelief
                  ? openRoute(primaryMisbelief.next_route)
                  : scrollToPageItem(".longline-recovery")
              }
            >
              <span>误会余波</span>
              <strong>{primaryMisbelief?.misunderstanding || "暂无待回收误会"}</strong>
              <small>
                {primaryMisbelief?.affected_characters.slice(0, 3).join("、") ||
                  report.current_tension.primary_misbelief ||
                  "世界会沿事件后果继续发酵。"}
              </small>
            </button>
            <button
              type="button"
              className="longline-continuation-map__node"
              onClick={() =>
                nextPrimaryAction ? openRoute(nextPrimaryAction.route) : navigate({ name: "author", slug })
              }
            >
              <span>下一轮去向</span>
              <strong>{nextPrimaryAction?.label || "送到作者台"}</strong>
              <small>
                {nextPrimaryAction?.reason ||
                  report.current_tension.next_chapter_hook ||
                  "把长线材料送进下一章。"}
              </small>
            </button>
          </section>

          {longlineEntityLanes.length > 0 && (
            <section className="longline-entity-lanes" aria-label="角色与势力追踪带">
              <div className="longline-entity-lanes__head">
                <p className="muted tiny">角色与势力追踪带</p>
                <h2>谁还带着后果往前走</h2>
                <p>
                  长线不只按事件发生，也会沿角色记忆和势力压力继续发酵。这里先把最该追的角色与势力挑出来。
                </p>
              </div>
              <div className="longline-entity-lanes__grid">
                {longlineEntityLanes.map((lane) => (
                  <article
                    className={`longline-entity-lane${selectedEntityLane?.id === lane.id ? " is-active" : ""}`}
                    key={lane.id}
                  >
                    <span>{lane.label}</span>
                    <strong>{lane.name}</strong>
                    <p>{lane.summary}</p>
                    <dl>
                      <div>
                        <dt>节点</dt>
                        <dd>{lane.entryCount} 个</dd>
                      </div>
                      <div>
                        <dt>证据</dt>
                        <dd>{lane.evidenceCount} 条</dd>
                      </div>
                      <div>
                        <dt>误会</dt>
                        <dd>{lane.unresolvedCount} 条</dd>
                      </div>
                    </dl>
                    <button className="btn btn--ghost tiny" onClick={() => focusEntityLane(lane)}>
                      看这条长线
                    </button>
                    <small>{lane.primaryEntryTitle}</small>
                  </article>
                ))}
              </div>
              {selectedEntityLane && (
                <section className="longline-entity-focus" aria-label="角色/势力追踪上下文台">
                  <div className="longline-entity-focus__summary">
                    <p className="muted tiny">{selectedEntityLane.label}</p>
                    <h3>{selectedEntityLane.name} · 这条线怎样发酵</h3>
                    <p>{selectedEntityLane.summary}</p>
                    <dl>
                      <div>
                        <dt>沿线节点</dt>
                        <dd>{selectedEntityLane.entryCount} 个</dd>
                      </div>
                      <div>
                        <dt>证据</dt>
                        <dd>{selectedEntityLane.evidenceCount} 条</dd>
                      </div>
                      <div>
                        <dt>牵连误会</dt>
                        <dd>{selectedEntityLane.unresolvedCount} 条</dd>
                      </div>
                    </dl>
                    <button className="btn btn--ghost tiny" onClick={() => setActiveEntityLaneId("")}>
                      回到全部长线
                    </button>
                  </div>
                  <div className="longline-entity-focus__path">
                    <div className="longline-entity-focus__title">
                      <span>沿线节点</span>
                      <strong>这条线经过哪里</strong>
                    </div>
                    {selectedEntityLane.entries.map((entry) => (
                      <button key={entry.id} type="button" onClick={() => focusEntry(entry.id)}>
                        <span>
                          {String(entry.sequence).padStart(2, "0")} · {entry.phase}
                        </span>
                        <strong>{entry.title}</strong>
                        <small>{entry.summary}</small>
                        <em>{entry.evidenceCount} 条证据 · 继续追这个节点</em>
                      </button>
                    ))}
                  </div>
                  <div className="longline-entity-focus__misbeliefs">
                    <div className="longline-entity-focus__title">
                      <span>牵连误会</span>
                      <strong>哪些偏差还会回到下一章</strong>
                    </div>
                    {selectedEntityLane.misbeliefs.length > 0 ? (
                      selectedEntityLane.misbeliefs.map((item) => (
                        <button key={item.id} type="button" onClick={() => openRoute(item.nextRoute)}>
                          <strong>{item.misunderstanding}</strong>
                          <span>{item.authorPrompt || item.originEventTitle}</span>
                          <small>
                            {item.status === "unresolved" ? "待回收" : "已回收"} · {item.evidenceCount} 条证据
                          </small>
                        </button>
                      ))
                    ) : (
                      <p>这条线暂时没有显式未解误会，可以先沿节点继续读它如何影响世界状态。</p>
                    )}
                  </div>
                </section>
              )}
            </section>
          )}

          <section className="longline-briefing" aria-label="长线阅读状态">
            <article className="longline-progress">
              <div className="longline-section-title">
                <div>
                  <p className="muted tiny">{report.reading_progress.label}</p>
                  <h2>{report.reading_progress.current_title}</h2>
                </div>
                <span className="badge badge--jade">{report.reading_progress.percent}%</span>
              </div>
              <div className="longline-progress__bar" aria-hidden="true">
                <span style={{ width: `${Math.min(100, report.reading_progress.percent)}%` }} />
              </div>
              <p>{report.reading_progress.summary}</p>
              <dl>
                <div>
                  <dt>当前位置</dt>
                  <dd>
                    {report.reading_progress.current_sequence}/
                    {report.reading_progress.total_entries || 0}
                  </dd>
                </div>
                <div>
                  <dt>正在发酵</dt>
                  <dd>{report.reading_progress.active_thread_count} 条</dd>
                </div>
                <div>
                  <dt>下一段</dt>
                  <dd>{report.reading_progress.next_title}</dd>
                </div>
              </dl>
            </article>

            <article className="longline-event-index">
              <div className="longline-section-title">
                <div>
                  <p className="muted tiny">{report.event_index.label}</p>
                  <h2>按事件追长线</h2>
                </div>
                <span className="badge">{report.event_index.event_count} 件</span>
              </div>
              <p>{report.event_index.description}</p>
              <div className="longline-event-index__list">
                {report.event_index.items.slice(0, 6).map((item) => (
                  <button
                    key={item.id}
                    className={activeEvent?.id === item.id ? "is-active" : ""}
                    onClick={() => focusEntry(item.entry_ids[0])}
                  >
                    <span>{PHASE_LABELS[item.phase] || item.label}</span>
                    <strong>{item.title}</strong>
                    <small>
                      {item.unresolved_count} 条线 · {item.evidence_count} 证据
                    </small>
                  </button>
                ))}
              </div>
            </article>

            <article className="longline-open-threads">
              <div className="longline-section-title">
                <div>
                  <p className="muted tiny">未解线索</p>
                  <h2>下一步该追哪里</h2>
                </div>
                <span className="badge badge--gold">{report.open_threads.length} 条</span>
              </div>
              <div className="longline-open-threads__list">
                {report.open_threads.slice(0, 5).map((thread) => (
                  <button key={thread.id} onClick={() => openRoute(thread.next_route)}>
                    <strong>{thread.label}</strong>
                    <span>{thread.reason}</span>
                    <small>{thread.source_count} 个来源</small>
                  </button>
                ))}
              </div>
            </article>
          </section>

          {longlineMisbeliefNetwork.length > 0 && selectedMisbeliefNode && (
            <section className="longline-misbelief-network" aria-label="跨章误会网络图">
              <div className="longline-misbelief-network__lead">
                <p className="muted tiny">跨章误会网络图</p>
                <h2>这场误会怎样拖到下一章</h2>
                <p>
                  把误会来源、牵动角色、证据和回收步骤放在同一屏，读者不用猜它为什么重要，作者也能直接决定下一章怎样承接。
                </p>
              </div>
              <div className="longline-misbelief-network__map">
                {longlineMisbeliefNetwork.slice(0, 6).map((node) => (
                  <button
                    key={node.id}
                    type="button"
                    className={`longline-misbelief-network__node${
                      selectedMisbeliefNode.id === node.id ? " is-active" : ""
                    }`}
                    onClick={() => focusMisbeliefNode(node)}
                  >
                    <span>{node.status === "unresolved" ? "待回收" : node.status}</span>
                    <strong>{node.misunderstanding}</strong>
                    <small>{node.originEventTitle}</small>
                  </button>
                ))}
              </div>
              <article className="longline-misbelief-network__detail">
                <span>当前误会</span>
                <strong>{selectedMisbeliefNode.misunderstanding}</strong>
                <p>{selectedMisbeliefNode.authorPrompt || "先核对来源证据，再决定是否送入作者台承接。"}</p>
                <dl>
                  <div>
                    <dt>误会来源</dt>
                    <dd>{selectedMisbeliefNode.originEventTitle}</dd>
                  </div>
                  <div>
                    <dt>牵动角色</dt>
                    <dd>{selectedMisbeliefNode.affectedCharacters.slice(0, 4).join("、") || "待显形"}</dd>
                  </div>
                  <div>
                    <dt>证据</dt>
                    <dd>{selectedMisbeliefNode.evidenceCount} 条</dd>
                  </div>
                </dl>
                <div className="longline-misbelief-network__steps">
                  <span>回收步骤</span>
                  <ol>
                    {selectedMisbeliefNode.recoverySteps.map((step) => (
                      <li key={step}>{step}</li>
                    ))}
                  </ol>
                </div>
                <div className="longline-misbelief-network__actions">
                  <button className="btn btn--ghost tiny" onClick={() => openRoute(selectedMisbeliefNode.nextRoute)}>
                    回卷宗核对
                  </button>
                  <button className="btn btn--primary tiny" onClick={() => navigate({ name: "author", slug })}>
                    送到作者台
                  </button>
                </div>
              </article>
            </section>
          )}

          {report.misbelief_recovery.items.length > 0 && (
            <section className="longline-recovery" aria-label="误会回收台">
              <div className="longline-section-title">
                <div>
                  <p className="muted tiny">{report.misbelief_recovery.label}</p>
                  <h2>把误会写回下一章</h2>
                </div>
                <span className="badge badge--gold">
                  {report.misbelief_recovery.misbelief_count} 条
                </span>
              </div>
              <p>{report.misbelief_recovery.description}</p>
              <div className="longline-recovery__grid">
                {report.misbelief_recovery.items.slice(0, 4).map((item) => (
                  <article key={item.id}>
                    <div className="longline-recovery__head">
                      <span>{item.origin_event_title}</span>
                      <small>{item.status === "unresolved" ? "待回收" : item.status}</small>
                    </div>
                    <strong>{item.misunderstanding}</strong>
                    <dl>
                      <div>
                        <dt>牵动角色</dt>
                        <dd>{item.affected_characters.slice(0, 3).join("、")}</dd>
                      </div>
                      <div>
                        <dt>证据</dt>
                        <dd>{item.evidence_refs.length} 条</dd>
                      </div>
                    </dl>
                    <ol>
                      {item.recovery_steps.map((step) => (
                        <li key={step}>{step}</li>
                      ))}
                    </ol>
                    <div className="longline-recovery__actions">
                      <button className="btn btn--ghost tiny" onClick={() => openRoute(item.next_route)}>
                        回卷宗核对
                      </button>
                      <button className="btn btn--ghost tiny" onClick={() => navigate({ name: "author", slug })}>
                        送到作者台
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          )}

          <main className="longline-layout">
            <aside className="longline-timeline" aria-label="长线时间线">
              <div className="longline-timeline__head">
                <h2>长线时间线</h2>
                <span className="tiny muted">{report.timeline_entries.length} 节</span>
              </div>
              {report.timeline_entries.length === 0 ? (
                <EmptyState title="还没有长线节点" hint="先生成连续阅读、多视角或检查点后会出现长线卷。" />
              ) : (
                <div className="longline-timeline__list">
                  {report.timeline_entries.map((entry) => (
                    <button
                      key={entry.id}
                      className={entry.id === activeEntry?.id ? "is-active" : ""}
                      onClick={() => focusEntry(entry.id)}
                    >
                      <span>{String(entry.sequence).padStart(2, "0")}</span>
                      <strong>{entry.title}</strong>
                      <small>{PHASE_LABELS[entry.phase] || entry.label}</small>
                    </button>
                  ))}
                </div>
              )}
            </aside>

            <article className="longline-reader">
              <section className="longline-current">
                <div>
                  <p className="muted tiny">当前长线节点</p>
                  <h2>{activeEntry?.title || "等待长线节点"}</h2>
                  <p>{activeEntry?.body || report.current_tension.summary}</p>
                </div>
                <dl>
                  <div>
                    <dt>阶段</dt>
                    <dd>{activeEntry ? PHASE_LABELS[activeEntry.phase] || activeEntry.label : "待定"}</dd>
                  </div>
                  <div>
                    <dt>证据</dt>
                    <dd>{activeEntry?.evidence_refs.length ?? 0} 条</dd>
                  </div>
                  <div>
                    <dt>长线</dt>
                    <dd>{activeThreads.length || "待显形"} 条</dd>
                  </div>
                </dl>
              </section>

              {activeEntry && (
                <section className="longline-entry">
                  <div className="longline-entry__head">
                    <span className="badge badge--gold">
                      {PHASE_LABELS[activeEntry.phase] || activeEntry.label}
                    </span>
                    <span className="tiny muted">{activeEntry.source}</span>
                  </div>
                  <p>{activeEntry.body}</p>
                  {activeEntry.consequence_hint && (
                    <div className="longline-entry__hint">
                      <strong>为什么它会继续发酵</strong>
                      <p>{activeEntry.consequence_hint}</p>
                    </div>
                  )}
                  <MetaRows entry={activeEntry} />
                  <div className="longline-entry__actions">
                    <button
                      className="btn btn--ghost tiny"
                      onClick={() => openRoute(activeEntry.route)}
                    >
                      打开来源
                    </button>
                    <button
                      className="btn btn--ghost tiny"
                      onClick={() =>
                        navigate({
                          name: "eventPerspective",
                          slug,
                          worldlineId,
                          eventId: "main",
                        })
                      }
                    >
                      事件详情
                    </button>
                  </div>
                </section>
              )}

              <section className="longline-thread-board">
                <div className="longline-section-title">
                  <h2>正在发酵的线</h2>
                  <span className="tiny muted">{activeThreads.length} 条活跃</span>
                </div>
                <div className="longline-thread-grid">
                  {report.longline_threads.map((thread) => (
                    <article key={thread.id} className={thread.status === "active" ? "is-active" : ""}>
                      <span>{thread.label}</span>
                      <strong>{thread.status === "active" ? "已显形" : "待显形"}</strong>
                      <p>{thread.summary}</p>
                      <small>{thread.source_count} 个来源</small>
                    </article>
                  ))}
                </div>
              </section>
            </article>

            <aside className="longline-aside" aria-label="长线证据与下一步">
              <section className="longline-tension">
                <h2>当前张力</h2>
                <p>{report.current_tension.summary}</p>
                {report.current_tension.primary_misbelief && (
                  <small>误会：{report.current_tension.primary_misbelief}</small>
                )}
              </section>

              <section className="longline-next">
                <h2>下一步</h2>
                {report.next_actions.map((action) => (
                  <button key={action.id} onClick={() => openRoute(action.route)}>
                    <strong>{action.label}</strong>
                    <small>{action.reason}</small>
                  </button>
                ))}
              </section>

              {report.evidence_panel.refs.length > 0 && (
                <section className="longline-evidence">
                  <h2>{report.evidence_panel.label}</h2>
                  <p>{report.evidence_panel.description}</p>
                  <div>
                    {report.evidence_panel.refs.slice(0, 10).map((ref) => (
                      <code key={ref}>{ref}</code>
                    ))}
                  </div>
                </section>
              )}
            </aside>
          </main>
        </>
      )}
    </div>
  );
}

function MetaRows({ entry }: { entry: LonglineTimelineEntry }) {
  const rows = [
    { label: "角色", values: entry.affected_characters },
    { label: "势力", values: entry.affected_factions },
    { label: "证据", values: entry.evidence_refs },
  ].filter((item) => item.values.length > 0);
  if (rows.length === 0) return null;
  return (
    <dl className="longline-entry__meta">
      {rows.map((row) => (
        <div key={row.label}>
          <dt>{row.label}</dt>
          <dd>{row.values.slice(0, 4).join("、")}</dd>
        </div>
      ))}
    </dl>
  );
}

function openRoute(route: string) {
  if (route.startsWith("#/")) {
    window.location.hash = route;
  }
}
