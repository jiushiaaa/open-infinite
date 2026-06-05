import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import type { DossierReadingReport, DossierReadingVolumeTab } from "../api/types";
import { renderProse } from "../markdown";
import { navigate } from "../routing";
import { EmptyState, ErrorState } from "./common/States";
import "./dossierReading.css";

type ReadingTab =
  | "continuous_reading"
  | "confirmed_chapter"
  | "world_chronicle"
  | "anchor_volume"
  | "character_volume"
  | "event_multi_perspective"
  | string;

const TAB_LABELS: Record<string, string> = {
  continuous_reading: "连续阅读",
  confirmed_chapter: "确认正文",
  world_chronicle: "世界正史卷",
  anchor_volume: "主锚点卷",
  character_volume: "角色个人卷",
  event_multi_perspective: "事件多视角",
};

export function DossierReadingPage({
  slug,
  worldlineId,
}: {
  slug: string;
  worldlineId: string;
}) {
  const [report, setReport] = useState<DossierReadingReport | null>(null);
  const [activeTab, setActiveTab] = useState<ReadingTab>("continuous_reading");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const next = await api.getDossierReading(slug, worldlineId);
      setReport(next);
      setActiveTab(next.default_tab || "continuous_reading");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [slug, worldlineId]);

  const tabs = useMemo(() => readingTabs(report), [report]);
  const activeVolume = report?.volume_tabs.find((item) => item.id === activeTab);
  const activeBody = bodyForTab(report, activeTab, activeVolume);
  const activeBias = biasForTab(report, activeTab, activeVolume);

  return (
    <div className="dossier-page">
      <header className="dossier-hero">
        <div>
          <p className="dossier-hero__eyebrow muted">世界内部卷宗 · 连续阅读</p>
          <h1>{report?.title || `${worldlineId} 的卷宗阅读`}</h1>
          <p className="muted">
            默认按正文读下去；需要核对时再切到卷宗或展开证据链。
          </p>
        </div>
        <div className="dossier-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "worldline", slug, worldlineId })}
          >
            世界线
          </button>
          <button className="btn btn--ghost" onClick={() => navigate({ name: "author", slug })}>
            作者采纳台
          </button>
        </div>
      </header>

      <main className="dossier-layout">
        {loading && (
          <EmptyState title="正在翻开卷宗" hint="正在聚合连续阅读、确认稿和多视角证据。" />
        )}
        {error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && report && (
          <>
            <aside className="dossier-sidebar" aria-label="卷宗目录">
              <div className="dossier-sidebar__head">
                <span className="badge badge--jade">
                  {report.status === "ready" ? "可连续阅读" : "资料不完整"}
                </span>
                <span className="tiny muted mono">{report.worldline_id}</span>
              </div>
              <nav className="dossier-tabs">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    className={tab.id === activeTab ? "is-active" : ""}
                    onClick={() => setActiveTab(tab.id)}
                    title={tab.hint}
                  >
                    <span>{tab.label}</span>
                    {tab.badge && <small>{tab.badge}</small>}
                  </button>
                ))}
              </nav>

              {report.perspective_biases.length > 0 && (
                <section className="dossier-bias-list" aria-label="认知偏差">
                  <h2>认知偏差</h2>
                  {report.perspective_biases.slice(0, 5).map((item) => (
                    <article key={`${item.source}-${item.id}`}>
                      <strong>{item.label}</strong>
                      <p>{item.cognitive_bias}</p>
                    </article>
                  ))}
                </section>
              )}
            </aside>

            <article className="dossier-reader">
              <div className="dossier-reader__meta">
                <span className="badge badge--gold">{TAB_LABELS[activeTab] || "卷宗"}</span>
                {report.source_runs.adoption_run_id && (
                  <span className="tiny muted mono">{report.source_runs.adoption_run_id}</span>
                )}
              </div>

              {activeBias && (
                <div className="dossier-bias-note">
                  <strong>这一卷的偏差</strong>
                  <p>{activeBias}</p>
                </div>
              )}

              {activeBody ? (
                <div className="prose dossier-prose">{renderProse(activeBody)}</div>
              ) : (
                <EmptyState title="这一卷还没有正文" hint="生成多视角卷或作者确认后会在这里出现。" />
              )}

              {report.continuous_reading?.reading_flow && activeTab === "continuous_reading" && (
                <section className="dossier-flow">
                  <h2>阅读节奏</h2>
                  <dl>
                    <div>
                      <dt>开场钩子</dt>
                      <dd>{report.continuous_reading.reading_flow.opening_hook}</dd>
                    </div>
                    <div>
                      <dt>转折</dt>
                      <dd>{report.continuous_reading.reading_flow.turning_point}</dd>
                    </div>
                    <div>
                      <dt>下一章悬念</dt>
                      <dd>{report.continuous_reading.reading_flow.next_chapter_hook}</dd>
                    </div>
                  </dl>
                </section>
              )}

              <details className="dossier-evidence" open={report.evidence_panel.default_open}>
                <summary>
                  {report.evidence_panel.label} · {report.evidence_panel.ref_count}
                </summary>
                <p className="muted">{report.evidence_panel.description}</p>
                <div className="dossier-evidence__refs">
                  {report.evidence_panel.refs.map((ref) => (
                    <code key={ref}>{ref}</code>
                  ))}
                </div>
                {report.reading_trail?.sections && report.reading_trail.sections.length > 0 && (
                  <div className="dossier-trail">
                    {report.reading_trail.sections.map((section) => (
                      <article key={section.id}>
                        <strong>{section.label}</strong>
                        <p>{section.reason}</p>
                      </article>
                    ))}
                  </div>
                )}
              </details>
            </article>
          </>
        )}
      </main>
    </div>
  );
}

function readingTabs(report: DossierReadingReport | null) {
  if (!report) return [];
  const tabs: Array<{ id: ReadingTab; label: string; hint: string; badge?: string }> = [];
  if (report.continuous_reading?.reading_body_md) {
    tabs.push({
      id: "continuous_reading",
      label: "连续阅读",
      hint: "默认阅读态，按小说正文继续读。",
      badge: `${report.continuous_reading.reading_sections.length} 场`,
    });
  }
  for (const tab of report.volume_tabs) {
    tabs.push({
      id: tab.id,
      label: tab.label,
      hint: tab.cognitive_bias,
      badge: tab.character_name || undefined,
    });
  }
  if (report.confirmed_chapter?.body_md) {
    tabs.push({
      id: "confirmed_chapter",
      label: "确认正文",
      hint: "作者确认入卷的正式章节。",
      badge: report.confirmed_chapter.edited ? "已编辑" : "原稿",
    });
  }
  return tabs;
}

function bodyForTab(
  report: DossierReadingReport | null,
  activeTab: ReadingTab,
  activeVolume?: DossierReadingVolumeTab,
): string {
  if (!report) return "";
  if (activeTab === "continuous_reading") {
    return report.continuous_reading?.reading_body_md || "";
  }
  if (activeTab === "confirmed_chapter") {
    return report.confirmed_chapter?.body_md || "";
  }
  return activeVolume?.body_md || "";
}

function biasForTab(
  report: DossierReadingReport | null,
  activeTab: ReadingTab,
  activeVolume?: DossierReadingVolumeTab,
): string {
  if (!report) return "";
  if (activeVolume?.cognitive_bias) return activeVolume.cognitive_bias;
  const bias = report.perspective_biases.find((item) => item.id === activeTab);
  if (bias) return bias.cognitive_bias;
  if (activeTab === "continuous_reading") {
    return "正文按场景推进，但每一场都带有角色视角限制；误会不是旁注，而是推动下一轮沙盘的燃料。";
  }
  return "";
}
