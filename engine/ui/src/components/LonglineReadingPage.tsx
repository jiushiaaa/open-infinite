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

export function LonglineReadingPage({
  slug,
  worldlineId,
}: {
  slug: string;
  worldlineId: string;
}) {
  const [report, setReport] = useState<LonglineReadingReport | null>(null);
  const [activeEntryId, setActiveEntryId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const next = await api.getLonglineReading(slug, worldlineId);
      setReport(next);
      setActiveEntryId(next.timeline_entries[0]?.id || "");
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
                      onClick={() => setActiveEntryId(entry.id)}
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
