import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import type { DossierReadingVolumeTab, EventPerspectiveReport } from "../api/types";
import { renderProse } from "../markdown";
import { navigate } from "../routing";
import { EmptyState, ErrorState, Loading } from "./common/States";
import { WorldRunway } from "./WorldRunway";
import "./eventPerspective.css";

const BEAT_LABELS: Record<string, string> = {
  opening_hook: "开场",
  viewpoint_misread: "误读",
  materialized_consequence: "代偿",
  conflict_turn: "转折",
  cliffhanger: "悬念",
};

export function EventPerspectivePage({
  slug,
  worldlineId,
  eventId,
}: {
  slug: string;
  worldlineId: string;
  eventId: string;
}) {
  const [report, setReport] = useState<EventPerspectiveReport | null>(null);
  const [activeBeatId, setActiveBeatId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const next = await api.getEventPerspective(slug, worldlineId, eventId);
      setReport(next);
      setActiveBeatId(next.scene_beats[0]?.id || "");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [slug, worldlineId, eventId]);

  const activeBeat = useMemo(
    () => report?.scene_beats.find((beat) => beat.id === activeBeatId) || report?.scene_beats[0],
    [activeBeatId, report],
  );
  const eventVolume = report?.event_volume as DossierReadingVolumeTab | undefined;
  const volumeBody = eventVolume?.body_md || "";
  const gap = report?.information_gap || {};
  const primaryBias = report?.perspective_biases[0] || null;
  const authorAction =
    report?.next_actions.find((action) => action.id === "author" || action.route.includes("/author")) ||
    report?.next_actions[0] ||
    null;
  const scrollToEventItem = (selector: string) => {
    document.querySelector(selector)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  if (loading) return <Loading label="正在翻开事件多视角…" />;

  return (
    <div className="event-perspective-page">
      <header className="event-perspective-hero">
        <div>
          <p className="muted event-perspective-hero__eyebrow">
            世界内部卷宗 · 事件多视角
          </p>
          <h1>{report?.title || "事件多视角"}</h1>
          <p className="muted">
            {report?.subtitle ||
              "把同一事件拆成正史、角色误会、势力代偿和作者下一章的可读线索。"}
          </p>
        </div>
        <div className="event-perspective-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() =>
              navigate({
                name: "dossierReading",
                slug,
                worldlineId,
                tab: "event_multi_perspective",
              })
            }
          >
            回卷宗阅读
          </button>
          <button className="btn btn--primary" onClick={() => navigate({ name: "author", slug })}>
            送到作者台
          </button>
        </div>
      </header>

      {error && <ErrorState message={error} onRetry={load} />}
      {!error && report && (
        <>
          <nav className="event-perspective-mobile-guide" aria-label="移动端事件导读">
            <button type="button" onClick={() => scrollToEventItem(".event-perspective-cover")}>
              <span>01</span>
              <strong>读事件</strong>
              <small>先看这一刻发生了什么</small>
            </button>
            <button type="button" onClick={() => scrollToEventItem(".event-perspective-gap")}>
              <span>02</span>
              <strong>看信息差</strong>
              <small>理解谁误读了它</small>
            </button>
            <button type="button" onClick={() => scrollToEventItem(".event-perspective-evidence")}>
              <span>03</span>
              <strong>查证据</strong>
              <small>核对沙盘和卷宗来源</small>
            </button>
            <button type="button" onClick={() => navigate({ name: "author", slug })}>
              <span>04</span>
              <strong>作者台</strong>
              <small>送去采纳续写</small>
            </button>
          </nav>

          <WorldRunway
            eyebrow="事件卷案"
            title="先看这一刻怎样发生，再看它如何被误读和代偿"
            summary="事件页把多视角正文从 tab 里提出来，帮助用户理解世界不是一条摘要，而是一件事在不同主体心里裂开的现场。"
            meta={
              <>
                <span className="badge badge--jade">
                  {report.status === "ready" ? "可读事件" : "资料不完整"}
                </span>
                <span className="badge badge--gold">
                  {report.scene_beats.length} 个节拍
                </span>
                <span className="badge">世界线 {worldlineId}</span>
              </>
            }
            steps={[
              {
                label: "事件",
                detail: "读清楚这一刻发生了什么。",
                active: true,
              },
              {
                label: "误会",
                detail: "比较正史和角色主观记忆的裂缝。",
                active: Boolean(gap.canon_vs_character || report.perspective_biases.length),
              },
              {
                label: "后果",
                detail: "回世界线或作者台，让事件进入下一章。",
                onClick: () => navigate({ name: "author", slug }),
              },
            ]}
            actions={[
              {
                label: "卷宗阅读",
                detail: "回到连续正文和全部卷宗",
                onClick: () =>
                  navigate({
                    name: "dossierReading",
                    slug,
                    worldlineId,
                    tab: "event_multi_perspective",
                  }),
              },
              {
                label: "世界线",
                detail: "核对因果债和检查点",
                onClick: () => navigate({ name: "worldline", slug, worldlineId }),
              },
              {
                label: "长线卷",
                detail: "看这件事如何继续发酵",
                onClick: () => navigate({ name: "longlineReading", slug, worldlineId }),
              },
              {
                label: "作者台",
                detail: "把事件张力写进下一章",
                primary: true,
                onClick: () => navigate({ name: "author", slug }),
              },
            ]}
          />

          <section className="event-gap-handoff" aria-label="事件信息差接力台">
            <div className="event-gap-handoff__lead">
              <p className="muted tiny">事件信息差接力台</p>
              <h2>先抓住这一刻被谁看错了</h2>
              <p>
                把事件现场、信息差、首要误读和下一章承接放在一起，读者不用先懂卷宗结构，也能看见同一事件如何裂成多条命运。
              </p>
            </div>
            <article>
              <span>01</span>
              <p className="muted tiny">事件现场</p>
              <strong>{activeBeat?.title || report.title}</strong>
              <p>{activeBeat?.body || report.subtitle || "等待事件节拍显形。"}</p>
              <button type="button" onClick={() => scrollToEventItem(".event-perspective-cover")}>
                读事件封面
              </button>
            </article>
            <article>
              <span>02</span>
              <p className="muted tiny">信息差</p>
              <strong>{gap.canon_vs_character || "正史与角色视角尚未裂开"}</strong>
              <p>{gap.unknown_canon_facts || `可核对 ${report.evidence_panel.ref_count} 条证据来源。`}</p>
              <button type="button" onClick={() => scrollToEventItem(".event-perspective-gap")}>
                看信息差
              </button>
            </article>
            <article>
              <span>03</span>
              <p className="muted tiny">首要误读</p>
              <strong>{primaryBias?.label || gap.misbeliefs || "等待角色误读显形"}</strong>
              <p>{primaryBias?.cognitive_bias || gap.misbeliefs || "事件的魅力在于：正史发生了，角色却未必这样理解。"}</p>
              <button type="button" onClick={() => scrollToEventItem(".event-perspective-bias-list")}>
                查谁误读了它
              </button>
            </article>
            <article>
              <span>04</span>
              <p className="muted tiny">送入下一章</p>
              <strong>{authorAction?.label || "把信息差送到作者台"}</strong>
              <p>{authorAction?.reason || "把这次误读、证据和余波写进下一章，让世界继续发酵。"}</p>
              <button
                type="button"
                onClick={() =>
                  authorAction
                    ? handleAction(authorAction, slug, worldlineId)
                    : navigate({ name: "author", slug })
                }
              >
                把信息差送到作者台
              </button>
            </article>
          </section>

          <main className="event-perspective-layout">
            <aside className="event-perspective-index" aria-label="事件节拍">
              <div className="event-perspective-index__head">
                <h2>事件节拍</h2>
                <span className="tiny muted">{report.scene_beats.length} 段</span>
              </div>
              {report.scene_beats.length === 0 ? (
                <EmptyState title="尚无事件节拍" hint="生成多视角或连续阅读后会出现事件节拍。" />
              ) : (
                <div className="event-perspective-index__list">
                  {report.scene_beats.map((beat, index) => (
                    <button
                      key={beat.id}
                      className={beat.id === activeBeat?.id ? "is-active" : ""}
                      onClick={() => setActiveBeatId(beat.id)}
                    >
                      <span>{String(index + 1).padStart(2, "0")}</span>
                      <strong>{beat.title}</strong>
                      <small>{BEAT_LABELS[beat.beat_type] || beat.viewpoint}</small>
                    </button>
                  ))}
                </div>
              )}
            </aside>

            <article className="event-perspective-reader">
              <section className="event-perspective-cover">
                <div>
                  <p className="muted tiny">当前事件</p>
                  <h2>{activeBeat?.title || report.title}</h2>
                  <p>{activeBeat?.body || gap.canon_vs_character || "等待事件多视角正文生成。"}</p>
                </div>
                <dl>
                  <div>
                    <dt>来源沙盘</dt>
                    <dd>{report.source_runs.sandbox_run_id || "待关联"}</dd>
                  </div>
                  <div>
                    <dt>证据</dt>
                    <dd>{report.evidence_panel.ref_count} 条</dd>
                  </div>
                  <div>
                    <dt>偏差</dt>
                    <dd>{report.perspective_biases.length} 条</dd>
                  </div>
                </dl>
              </section>

              {activeBeat && (
                <section className="event-perspective-beat">
                  <div className="event-perspective-beat__head">
                    <span className="badge badge--gold">
                      {BEAT_LABELS[activeBeat.beat_type] || "事件"}
                    </span>
                    <span className="tiny muted">{activeBeat.viewpoint}</span>
                  </div>
                  <p>{activeBeat.body}</p>
                  {activeBeat.cognitive_bias && (
                    <div className="event-perspective-bias">
                      <strong>这一段的偏差</strong>
                      <p>{activeBeat.cognitive_bias}</p>
                    </div>
                  )}
                  {activeBeat.evidence_refs.length > 0 && (
                    <div className="event-perspective-evidence-strip">
                      {activeBeat.evidence_refs.map((ref) => (
                        <code key={ref}>{ref}</code>
                      ))}
                    </div>
                  )}
                </section>
              )}

              {volumeBody ? (
                <section className="event-perspective-volume">
                  <h2>事件多视角正文</h2>
                  <div className="prose">{renderProse(volumeBody)}</div>
                </section>
              ) : (
                <EmptyState title="还没有事件正文卷" hint="先去多视角页生成事件多视角正文。" />
              )}
            </article>

            <aside className="event-perspective-aside" aria-label="事件信息差与下一步">
              <section className="event-perspective-gap">
                <h2>信息差</h2>
                <p>{gap.canon_vs_character || "正史和角色视角尚未形成明确差异。"}</p>
                {gap.misbeliefs && <small>误会：{gap.misbeliefs}</small>}
                {gap.unknown_canon_facts && <small>未知正史：{gap.unknown_canon_facts}</small>}
              </section>

              {report.perspective_biases.length > 0 && (
                <section className="event-perspective-bias-list">
                  <h2>谁误读了它</h2>
                  {report.perspective_biases.slice(0, 6).map((bias) => (
                    <article key={`${bias.source}-${bias.id}`}>
                      <strong>{bias.label}</strong>
                      <p>{bias.cognitive_bias}</p>
                    </article>
                  ))}
                </section>
              )}

              <section className="event-perspective-next">
                <h2>下一步</h2>
                {report.next_actions.map((action) => (
                  <button key={action.id} onClick={() => handleAction(action, slug, worldlineId)}>
                    <strong>{action.label}</strong>
                    <small>{action.reason}</small>
                  </button>
                ))}
              </section>

              {report.evidence_panel.refs.length > 0 && (
                <section className="event-perspective-evidence">
                  <h2>{report.evidence_panel.label}</h2>
                  <p>{report.evidence_panel.description}</p>
                  <div>
                    {report.evidence_panel.refs.slice(0, 8).map((ref) => (
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

function handleAction(
  action: EventPerspectiveReport["next_actions"][number],
  slug: string,
  worldlineId: string,
) {
  if (action.route.startsWith("#/")) {
    window.location.hash = action.route;
    return;
  }
  if (action.id === "reading") {
    navigate({ name: "dossierReading", slug, worldlineId, tab: "event_multi_perspective" });
    return;
  }
  if (action.id === "character_volume") {
    navigate({ name: "characterVolume", slug, worldlineId, characterId: "zhao_xuan" });
    return;
  }
  if (action.id === "worldline") {
    navigate({ name: "worldline", slug, worldlineId });
    return;
  }
  navigate({ name: "author", slug });
}
