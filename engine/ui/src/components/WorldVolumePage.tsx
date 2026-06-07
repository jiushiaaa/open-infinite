import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import type { DossierReadingReport } from "../api/types";
import { renderProse } from "../markdown";
import { navigate } from "../routing";
import { EmptyState, ErrorState, Loading } from "./common/States";
import { WorldRunway } from "./WorldRunway";
import "./worldVolume.css";

type WorldVolumeKind = "chronicle" | "anchor";

interface VolumeCopy {
  id: "world_chronicle" | "anchor_volume";
  siblingId: "world_chronicle" | "anchor_volume";
  eyebrow: string;
  title: string;
  emptyTitle: string;
  handoffTitle: string;
  handoffLead: string;
  firstSignal: string;
  secondSignal: string;
  thirdSignal: string;
  fourthSignal: string;
  firstFallback: string;
  secondFallback: string;
  thirdFallback: string;
  fourthFallback: string;
  mobilePrimary: string;
  mobileSecondary: string;
}

const COPY: Record<WorldVolumeKind, VolumeCopy> = {
  chronicle: {
    id: "world_chronicle",
    siblingId: "anchor_volume",
    eyebrow: "世界内部卷宗 · 世界正史卷",
    title: "世界正史卷",
    emptyTitle: "这一条世界线还没有正史卷",
    handoffTitle: "正史接力台",
    handoffLead: "先判断世界怎样记住这件事，再看它怎样把事实压回角色、锚点和下一章。",
    firstSignal: "世界怎样记住",
    secondSignal: "谁被写入正史",
    thirdSignal: "哪条证据成立",
    fourthSignal: "从哪里继续",
    firstFallback: "等待多视角或确认正文把事件写成正史。",
    secondFallback: "正史卷生成后会列出被事件推到台前的人。",
    thirdFallback: "证据锚点会告诉用户这不是旁白猜测。",
    fourthFallback: "可以先回卷宗阅读，或继续一轮沙盘让世界留下事实。",
    mobilePrimary: "读正史",
    mobileSecondary: "查锚点",
  },
  anchor: {
    id: "anchor_volume",
    siblingId: "world_chronicle",
    eyebrow: "世界内部卷宗 · 主锚点卷",
    title: "主锚点卷",
    emptyTitle: "这一条世界线还没有主锚点卷",
    handoffTitle: "锚点接力台",
    handoffLead: "先判断锚点怎样承压，再看它怎样限制干预、改写世界线和牵动下一轮行动。",
    firstSignal: "锚点怎样承压",
    secondSignal: "哪条规则被触碰",
    thirdSignal: "谁会承担代价",
    fourthSignal: "从哪里继续",
    firstFallback: "等待天命书、干预或代偿状态把锚点压力写清楚。",
    secondFallback: "主锚点卷生成后会解释哪些边界被触碰。",
    thirdFallback: "承载者会从角色、势力或世界线代偿里显形。",
    fourthFallback: "可以先回天命书核对边界，或继续沙盘观察压力发酵。",
    mobilePrimary: "读锚点",
    mobileSecondary: "看正史",
  },
};

export function WorldVolumePage({
  slug,
  worldlineId,
  volumeKind,
}: {
  slug: string;
  worldlineId: string;
  volumeKind: WorldVolumeKind;
}) {
  const [report, setReport] = useState<DossierReadingReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const copy = COPY[volumeKind];
  const volumeId = copy.id;

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setReport(await api.getDossierReading(slug, worldlineId));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [slug, worldlineId, volumeKind]);

  const activeVolume = useMemo(
    () => report?.volume_tabs.find((tab) => tab.id === volumeId) ?? null,
    [report?.volume_tabs, volumeId],
  );
  const siblingVolume = useMemo(
    () => report?.volume_tabs.find((tab) => tab.id === copy.siblingId) ?? null,
    [copy.siblingId, report?.volume_tabs],
  );
  const chronicleVolume = report?.volume_tabs.find((tab) => tab.id === "world_chronicle") ?? null;
  const anchorVolume = report?.volume_tabs.find((tab) => tab.id === "anchor_volume") ?? null;
  const bodyAvailable = Boolean(activeVolume?.body_md);
  const evidenceRefs = activeVolume?.evidence_refs ?? [];
  const sceneCount = report?.continuous_reading?.reading_sections.length ?? 0;
  const biasCount = report?.perspective_biases.length ?? 0;
  const worldlineState = report?.worldline_dossier?.worldline_state;
  const consequence = worldlineState?.consequence_state;
  const latestLedger = consequence?.ledger?.[Math.max(0, (consequence.ledger?.length ?? 1) - 1)];
  const pressureDomain =
    consequence?.domains?.anchor ||
    consequence?.domains?.faction ||
    consequence?.domains?.character ||
    null;
  const title = activeVolume?.title || copy.title;

  const goSibling = () => {
    if (volumeKind === "chronicle") {
      navigate({ name: "anchorVolume", slug, worldlineId });
      return;
    }
    navigate({ name: "worldChronicle", slug, worldlineId });
  };
  const scrollToItem = (selector: string) => {
    document.querySelector(selector)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  if (loading) return <Loading label={`正在翻开${copy.title}…`} />;

  return (
    <div className="world-volume-page">
      <header className="world-volume-hero">
        <div>
          <p className="muted world-volume-hero__eyebrow">{copy.eyebrow}</p>
          <h1>{title}</h1>
          <p className="muted">
            {volumeKind === "chronicle"
              ? "这一页只读世界承认的事实：事件怎样被写入正史、哪些证据成立，以及它怎样继续牵动下一章。"
              : "这一页只读主锚点承压：边界怎样被触碰、世界怎样代偿，以及下一轮行动会被什么规则牵引。"}
          </p>
        </div>
        <div className="world-volume-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() =>
              navigate({
                name: "dossierReading",
                slug,
                worldlineId,
                tab: volumeId,
              })
            }
          >
            回卷宗阅读
          </button>
          <button className="btn btn--ghost" onClick={goSibling}>
            {volumeKind === "chronicle" ? "查主锚点卷" : "读世界正史卷"}
          </button>
          <button className="btn btn--primary" onClick={() => navigate({ name: "sandbox", slug })}>
            继续沙盘
          </button>
        </div>
      </header>

      {error && <ErrorState message={error} onRetry={load} />}
      {!error && (
        <>
          <nav className="world-volume-mobile-guide" aria-label="移动端世界卷导读">
            <button type="button" onClick={() => scrollToItem(".world-volume-reader")}>
              <span>01</span>
              <strong>{copy.mobilePrimary}</strong>
              <small>先读这卷正文</small>
            </button>
            <button type="button" onClick={goSibling}>
              <span>02</span>
              <strong>{copy.mobileSecondary}</strong>
              <small>核对正史与锚点</small>
            </button>
            <button type="button" onClick={() => scrollToItem(".world-volume-evidence")}>
              <span>03</span>
              <strong>查证据</strong>
              <small>看它来自哪里</small>
            </button>
            <button type="button" onClick={() => navigate({ name: "author", slug })}>
              <span>04</span>
              <strong>作者台</strong>
              <small>写入下一章</small>
            </button>
          </nav>

          <WorldRunway
            eyebrow={volumeKind === "chronicle" ? "世界事实链" : "锚点压力链"}
            title={
              volumeKind === "chronicle"
                ? "先读世界承认的事实，再查锚点为什么会动"
                : "先看锚点如何承压，再回正史核对事实来源"
            }
            summary={copy.handoffLead}
            meta={
              <>
                <span className="badge badge--jade">{bodyAvailable ? "可阅读" : "待生成"}</span>
                <span className="badge badge--gold">证据 {evidenceRefs.length}</span>
                <span className="badge">世界线 {worldlineId}</span>
              </>
            }
            steps={[
              {
                label: volumeKind === "chronicle" ? "正史" : "锚点",
                detail: volumeKind === "chronicle" ? "读世界承认的事件版本。" : "读世界边界被触碰的位置。",
                active: bodyAvailable,
                onClick: () => scrollToItem(".world-volume-reader"),
              },
              {
                label: volumeKind === "chronicle" ? "锚点" : "正史",
                detail: "切到另一卷核对事实与边界怎样互相牵引。",
                active: Boolean(siblingVolume?.body_md),
                onClick: goSibling,
              },
              {
                label: "继续",
                detail: "把这卷材料送回沙盘或作者台。",
                onClick: () => navigate({ name: "author", slug }),
              },
            ]}
            actions={[
              {
                label: "回卷宗阅读",
                detail: "回到连续正文和所有卷宗 tab",
                onClick: () =>
                  navigate({
                    name: "dossierReading",
                    slug,
                    worldlineId,
                    tab: volumeId,
                  }),
              },
              {
                label: "继续沙盘",
                detail: "让世界带着这卷事实继续运行",
                onClick: () => navigate({ name: "sandbox", slug }),
              },
              {
                label: "作者台",
                detail: "把这卷事实写进下一章材料",
                primary: true,
                onClick: () => navigate({ name: "author", slug }),
              },
            ]}
          />

          <section className="world-volume-handoff" aria-label={copy.handoffTitle}>
            <div className="world-volume-handoff__lead">
              <p className="muted tiny">{copy.handoffTitle}</p>
              <h2>{volumeKind === "chronicle" ? "先判断世界怎样记住" : "先判断锚点怎样承压"}</h2>
              <p>{copy.handoffLead}</p>
            </div>
            <article>
              <span>01</span>
              <p className="muted tiny">{copy.firstSignal}</p>
              <strong>{activeVolume?.cognitive_bias || consequence?.summary || copy.firstFallback}</strong>
              <p>{activeVolume?.title || copy.emptyTitle}</p>
              <button type="button" onClick={() => scrollToItem(".world-volume-reader")}>
                读这一卷
              </button>
            </article>
            <article>
              <span>02</span>
              <p className="muted tiny">{copy.secondSignal}</p>
              <strong>
                {volumeKind === "chronicle"
                  ? report?.perspective_biases[0]?.label || copy.secondFallback
                  : pressureDomain?.current || copy.secondFallback}
              </strong>
              <p>
                {volumeKind === "chronicle"
                  ? `共有 ${biasCount} 条视角偏差可与正史互相核对。`
                  : pressureDomain?.pressure || "锚点压力会继续限制干预与下一轮行动。"}
              </p>
              <button type="button" onClick={goSibling}>
                {volumeKind === "chronicle" ? "查锚点压力" : "回看正史"}
              </button>
            </article>
            <article>
              <span>03</span>
              <p className="muted tiny">{copy.thirdSignal}</p>
              <strong>{latestLedger?.major_event || evidenceRefs[0] || copy.thirdFallback}</strong>
              <p>{evidenceRefs.length} 条卷内证据，{report?.evidence_panel.ref_count ?? 0} 条总证据可追溯。</p>
              <button type="button" onClick={() => scrollToItem(".world-volume-evidence")}>
                查证据链
              </button>
            </article>
            <article>
              <span>04</span>
              <p className="muted tiny">{copy.fourthSignal}</p>
              <strong>
                {consequence?.next_round_hint ||
                  report?.continuous_reading?.reading_flow?.next_chapter_hook ||
                  copy.fourthFallback}
              </strong>
              <p>把这卷材料接回沙盘运行、长线阅读或作者采纳台，世界才会继续变化。</p>
              <button type="button" onClick={() => navigate({ name: "author", slug })}>
                送到作者台
              </button>
            </article>
          </section>

          <main className="world-volume-layout">
            <aside className="world-volume-index" aria-label="世界卷目录">
              <div className="world-volume-index__head">
                <h2>世界卷</h2>
                <span className="tiny muted">{report?.volume_tabs.length ?? 0} 卷</span>
              </div>
              <button
                className={volumeKind === "chronicle" ? "is-active" : ""}
                type="button"
                onClick={() => navigate({ name: "worldChronicle", slug, worldlineId })}
              >
                <strong>世界正史卷</strong>
                <small>{chronicleVolume?.cognitive_bias || "世界承认的事实版本"}</small>
                <em>{chronicleVolume?.evidence_refs.length ?? 0} 条证据</em>
              </button>
              <button
                className={volumeKind === "anchor" ? "is-active" : ""}
                type="button"
                onClick={() => navigate({ name: "anchorVolume", slug, worldlineId })}
              >
                <strong>主锚点卷</strong>
                <small>{anchorVolume?.cognitive_bias || "世界边界和锚点压力"}</small>
                <em>{anchorVolume?.evidence_refs.length ?? 0} 条证据</em>
              </button>
              <button
                type="button"
                onClick={() =>
                  navigate({
                    name: "dossierReading",
                    slug,
                    worldlineId,
                  })
                }
              >
                <strong>连续阅读</strong>
                <small>回到正文和全部卷宗</small>
                <em>{sceneCount} 场</em>
              </button>
            </aside>

            <article className="world-volume-reader">
              <section className="world-volume-cover">
                <div>
                  <p className="muted tiny">{volumeKind === "chronicle" ? "当前正史" : "当前锚点"}</p>
                  <h2>{title}</h2>
                  <p>{activeVolume?.cognitive_bias || copy.firstFallback}</p>
                </div>
                <dl>
                  <div>
                    <dt>卷内证据</dt>
                    <dd>{evidenceRefs.length} 条</dd>
                  </div>
                  <div>
                    <dt>相关场景</dt>
                    <dd>{sceneCount} 场</dd>
                  </div>
                  <div>
                    <dt>视角偏差</dt>
                    <dd>{biasCount} 条</dd>
                  </div>
                </dl>
              </section>

              {activeVolume?.body_md ? (
                <div className="prose world-volume-prose">
                  {renderProse(activeVolume.body_md)}
                </div>
              ) : (
                <EmptyState
                  title={copy.emptyTitle}
                  hint="可以先去多视角页生成世界卷，或继续沙盘让世界留下更多事实。"
                />
              )}

              <section className="world-volume-evidence" aria-label="卷内证据">
                <h2>卷内证据</h2>
                {evidenceRefs.length > 0 ? (
                  <div>
                    {evidenceRefs.map((ref) => (
                      <code key={ref}>{ref}</code>
                    ))}
                  </div>
                ) : (
                  <p className="muted">这一卷还没有可展示的证据锚点。</p>
                )}
              </section>
            </article>

            <aside className="world-volume-state" aria-label="世界承接状态">
              <div className="world-volume-state__head">
                <h2>承接状态</h2>
                <span className="badge badge--jade tiny">{worldlineId}</span>
              </div>
              <article>
                <span>世界线状态</span>
                <strong>{worldlineState?.status || report?.status || "等待状态"}</strong>
                <p>{consequence?.summary || "世界状态会在沙盘、代偿和确认入卷后持续累积。"}</p>
              </article>
              <article>
                <span>最近代价</span>
                <strong>{latestLedger?.major_event || "暂无 ledger"}</strong>
                <p>{latestLedger?.source_run_id || "继续运行后，这里会显示哪次事件改变了世界。"}</p>
              </article>
              <article>
                <span>总证据</span>
                <strong>{report?.evidence_panel.ref_count ?? 0} 条</strong>
                <p>{report?.evidence_panel.description || "证据链用于证明正文、正史和锚点不是孤立说明。"}</p>
              </article>
            </aside>
          </main>

          {report?.evidence_panel.refs?.length ? (
            <section className="world-volume-global-evidence" aria-label="全局证据">
              <h2>{report.evidence_panel.label}</h2>
              <p className="muted">{report.evidence_panel.description}</p>
              <div>
                {report.evidence_panel.refs.slice(0, 12).map((ref) => (
                  <code key={ref}>{ref}</code>
                ))}
              </div>
            </section>
          ) : null}
        </>
      )}
    </div>
  );
}
