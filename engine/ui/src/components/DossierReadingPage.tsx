import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api/client";
import type {
  ContinuousReadingSection,
  DossierReadingReport,
  DossierReadingVolumeTab,
} from "../api/types";
import { renderProse } from "../markdown";
import { navigate } from "../routing";
import { EmptyState, ErrorState } from "./common/States";
import { WorldRunway } from "./WorldRunway";
import "./dossierReading.css";

type ReadingTab =
  | "continuous_reading"
  | "confirmed_chapter"
  | "world_chronicle"
  | "anchor_volume"
  | "character_volume"
  | "faction_volume"
  | "event_multi_perspective"
  | string;

interface MisbeliefNode {
  key: string;
  id: string;
  label: string;
  cognitiveBias: string;
  source: string;
  sourceLabel: string;
  targetTab: ReadingTab;
  sectionId?: string;
  evidenceCount: number;
}

const TAB_LABELS: Record<string, string> = {
  continuous_reading: "连续阅读",
  confirmed_chapter: "确认正文",
  world_chronicle: "世界正史卷",
  anchor_volume: "主锚点卷",
  character_volume: "角色个人卷",
  faction_volume: "势力卷",
  event_multi_perspective: "事件多视角",
};

export function DossierReadingPage({
  slug,
  worldlineId,
  initialTab,
}: {
  slug: string;
  worldlineId: string;
  initialTab?: string;
}) {
  const [report, setReport] = useState<DossierReadingReport | null>(null);
  const [activeTab, setActiveTab] = useState<ReadingTab>("continuous_reading");
  const [activeSectionId, setActiveSectionId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const readerRef = useRef<HTMLElement | null>(null);
  const sectionRefs = useRef<Record<string, HTMLElement | null>>({});
  const sectionFocusLockRef = useRef({ id: "", until: 0 });

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const next = await api.getDossierReading(slug, worldlineId);
      setReport(next);
      setActiveTab(initialTab || next.default_tab || "continuous_reading");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [slug, worldlineId, initialTab]);

  const tabs = useMemo(() => readingTabs(report), [report]);
  const activeVolume = report?.volume_tabs.find((item) => item.id === activeTab);
  const activeBody = bodyForTab(report, activeTab, activeVolume);
  const activeBias = biasForTab(report, activeTab, activeVolume);
  const activeContext = readingContext(report, activeTab, activeVolume);
  const misbeliefNodes = useMemo(() => buildMisbeliefNodes(report), [report]);
  const continuousSections =
    activeTab === "continuous_reading"
      ? report?.continuous_reading?.reading_sections ?? []
      : [];
  const activeSectionIndex = Math.max(
    0,
    continuousSections.findIndex((section) => section.id === activeSectionId),
  );
  const readingProgress =
    continuousSections.length > 0
      ? Math.round(((activeSectionIndex + 1) / continuousSections.length) * 100)
      : 0;
  const focusReader = () =>
    readerRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  const scrollToSection = (id: string) => {
    sectionFocusLockRef.current = { id, until: Date.now() + 900 };
    setActiveSectionId(id);
    sectionRefs.current[id]?.scrollIntoView({ behavior: "smooth", block: "center" });
  };
  const activeMisbeliefId =
    activeTab === "continuous_reading" && activeSectionId
      ? activeSectionId
      : String(activeTab);
  const openMisbelief = (node: MisbeliefNode) => {
    setActiveTab(node.targetTab);
    if (node.sectionId) {
      setActiveSectionId(node.sectionId);
      window.setTimeout(() => scrollToSection(node.sectionId!), 80);
      return;
    }
    focusReader();
  };

  useEffect(() => {
    const firstSection = continuousSections[0]?.id || "";
    if (!firstSection) {
      setActiveSectionId("");
      return;
    }
    if (!continuousSections.some((section) => section.id === activeSectionId)) {
      setActiveSectionId(firstSection);
    }
  }, [activeSectionId, continuousSections]);

  useEffect(() => {
    if (continuousSections.length === 0) return;
    const currentVisibleSectionId = () => {
      const readerCenter = window.innerHeight * 0.48;
      let bestId = "";
      let bestDistance = Number.POSITIVE_INFINITY;
      for (const section of continuousSections) {
        const node = sectionRefs.current[section.id];
        if (!node) continue;
        const rect = node.getBoundingClientRect();
        if (rect.bottom < 0 || rect.top > window.innerHeight) continue;
        const sectionCenter = rect.top + rect.height / 2;
        const distance = Math.abs(sectionCenter - readerCenter);
        if (distance < bestDistance) {
          bestDistance = distance;
          bestId = section.id;
        }
      }
      return bestId;
    };
    const observer = new IntersectionObserver(
      () => {
        const locked = sectionFocusLockRef.current;
        if (locked.id && Date.now() < locked.until) {
          setActiveSectionId(locked.id);
          return;
        }
        if (locked.id) sectionFocusLockRef.current = { id: "", until: 0 };
        const id = currentVisibleSectionId();
        if (id) setActiveSectionId(id);
      },
      { rootMargin: "-20% 0px -48% 0px", threshold: [0.2, 0.45, 0.7] },
    );
    for (const section of continuousSections) {
      const node = sectionRefs.current[section.id];
      if (node) observer.observe(node);
    }
    return () => observer.disconnect();
  }, [continuousSections]);

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
      </header>

      <WorldRunway
        eyebrow="当前世界线"
        title="先按正文读，再回卷宗查证据"
        summary="这里把连续正文、角色偏见、事件多视角和作者确认稿放在同一个阅读流里。用户不用先懂 artifact，也能顺着故事进入世界状态。"
        meta={
          <>
            <span className="badge badge--jade">
              {report?.status === "ready" ? "可连续阅读" : "资料不完整"}
            </span>
            <span className="badge">{worldlineId}</span>
            {report?.evidence_panel && (
              <span className="badge badge--gold">
                证据 {report.evidence_panel.ref_count}
              </span>
            )}
          </>
        }
        steps={[
          {
            label: "读正文",
            detail: "默认进入连续阅读，不先打断沉浸。",
            active: activeTab === "continuous_reading",
            onClick: () => {
              setActiveTab("continuous_reading");
              focusReader();
            },
          },
          {
            label: "查卷宗",
            detail: "切到角色、锚点、势力或事件多视角核对误会。",
            active:
              activeTab === "character_volume" ||
              activeTab === "anchor_volume" ||
              activeTab === "faction_volume" ||
              activeTab === "event_multi_perspective",
          },
          {
            label: "写下一章",
            detail: "把可读结果带去作者采纳台或继续沙盘。",
            onClick: () => navigate({ name: "author", slug }),
          },
        ]}
        actions={[
          {
            label: "世界线档案",
            detail: "看因果债、检查点和承接状态",
            onClick: () => navigate({ name: "worldline", slug, worldlineId }),
          },
          {
            label: "作者采纳台",
            detail: "把这条阅读结果变成下一章材料",
            primary: true,
            onClick: () => navigate({ name: "author", slug }),
          },
        ]}
      />

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

              {misbeliefNodes.length > 0 && (
                <section className="dossier-misbelief-map" aria-label="误会图谱">
                  <div className="dossier-misbelief-map__head">
                    <h2>误会图谱</h2>
                    <span className="tiny muted">{misbeliefNodes.length} 条</span>
                  </div>
                  <div className="dossier-misbelief-map__list">
                    {misbeliefNodes.slice(0, 8).map((node) => (
                      <button
                        key={node.key}
                        className={node.id === activeMisbeliefId ? "is-active" : ""}
                        onClick={() => openMisbelief(node)}
                      >
                        <span>{node.sourceLabel}</span>
                        <strong>{node.label}</strong>
                        <small>{node.cognitiveBias}</small>
                        <em>{node.evidenceCount} 条证据</em>
                      </button>
                    ))}
                  </div>
                </section>
              )}

              {continuousSections.length > 0 && (
                <section className="dossier-reading-map" aria-label="阅读进度">
                  <div className="dossier-reading-map__head">
                    <h2>阅读进度</h2>
                    <span className="tiny muted">{readingProgress}%</span>
                  </div>
                  <div className="dossier-reading-map__bar" aria-hidden>
                    <span style={{ width: `${readingProgress}%` }} />
                  </div>
                  <div className="dossier-reading-map__list">
                    {continuousSections.map((section, index) => (
                      <button
                        key={section.id}
                        className={section.id === activeSectionId ? "is-active" : ""}
                        onClick={() => scrollToSection(section.id)}
                      >
                        <span>{String(index + 1).padStart(2, "0")}</span>
                        <strong>{section.title || `第 ${index + 1} 场`}</strong>
                        <small>
                          {section.viewpoint || section.narrative_role || "正文场景"} ·{" "}
                          {section.evidence_refs.length} 证据
                        </small>
                      </button>
                    ))}
                  </div>
                </section>
              )}
            </aside>

            <article className="dossier-reader" ref={readerRef}>
              <section className="dossier-reader__cover" aria-label="当前阅读卷">
                <div>
                  <p className="dossier-reader__eyebrow muted">正在阅读</p>
                  <h2>{activeContext.title}</h2>
                  <p>{activeContext.summary}</p>
                </div>
                <div className="dossier-reader__actions">
                  <button
                    className="btn btn--ghost tiny"
                    onClick={() => navigate({ name: "worldline", slug, worldlineId })}
                  >
                    世界线
                  </button>
                  <button
                    className="btn btn--ghost tiny"
                    onClick={() => navigate({ name: "sandbox", slug })}
                  >
                    继续沙盘
                  </button>
                  <button
                    className="btn btn--primary tiny"
                    onClick={() => navigate({ name: "author", slug })}
                  >
                    作者台
                  </button>
                  {activeVolume?.character_id && (
                    <button
                      className="btn btn--ghost tiny"
                      onClick={() =>
                        navigate({
                          name: "characterVolume",
                          slug,
                          worldlineId,
                          characterId: activeVolume.character_id!,
                        })
                      }
                    >
                      角色个人卷
                    </button>
                  )}
                  {activeVolume?.id === "faction_volume" && (
                    <button
                      className="btn btn--ghost tiny"
                      onClick={() =>
                        navigate({
                          name: "factionVolume",
                          slug,
                          worldlineId,
                          factionId:
                            activeVolume.faction_id ||
                            activeVolume.faction_name ||
                            activeVolume.title ||
                            "势力卷",
                        })
                      }
                    >
                      势力卷
                    </button>
                  )}
                  {activeTab === "event_multi_perspective" && (
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
                  )}
                </div>
                <dl className="dossier-reader__stats">
                  {activeContext.stats.map((stat) => (
                    <div key={stat.label}>
                      <dt>{stat.label}</dt>
                      <dd>{stat.value}</dd>
                    </div>
                  ))}
                </dl>
              </section>

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

              {activeTab === "continuous_reading" && continuousSections.length > 0 ? (
                <div className="dossier-section-stack">
                  {continuousSections.map((section, index) => {
                    const evidenceRefs = sectionEvidenceRefs(section);
                    return (
                      <section
                        className={`dossier-section ${
                          section.id === activeSectionId ? "is-current" : ""
                        }`}
                        data-section-id={section.id}
                        id={`reading-section-${section.id}`}
                        key={section.id}
                        ref={(node) => {
                          sectionRefs.current[section.id] = node;
                        }}
                      >
                        <header className="dossier-section__head">
                          <span className="dossier-section__index">
                            {String(index + 1).padStart(2, "0")}
                          </span>
                          <div>
                            <h3>{section.title || `第 ${index + 1} 场`}</h3>
                            <p>
                              {section.viewpoint || "未标注视角"}
                              {section.source_beat_type ? ` · ${section.source_beat_type}` : ""}
                              {section.narrative_role ? ` · ${section.narrative_role}` : ""}
                            </p>
                          </div>
                        </header>

                        {section.cognitive_bias && (
                          <p className="dossier-section__bias">{section.cognitive_bias}</p>
                        )}
                        {section.conflict_turn && (
                          <p className="dossier-section__turn">{section.conflict_turn}</p>
                        )}

                        <div className="prose dossier-prose dossier-section__body">
                          {renderProse(section.body)}
                        </div>

                        {evidenceRefs.length > 0 && (
                          <aside className="dossier-section__evidence">
                            <span>证据锚点</span>
                            <div>
                              {evidenceRefs.map((ref) => (
                                <code key={ref}>{ref}</code>
                              ))}
                            </div>
                          </aside>
                        )}
                      </section>
                    );
                  })}
                </div>
              ) : activeBody ? (
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

              {report.continuous_reading?.cross_volume_refs &&
                report.continuous_reading.cross_volume_refs.length > 0 &&
                activeTab === "continuous_reading" && (
                  <section className="dossier-cross-refs">
                    <h2>关联卷宗</h2>
                    <div>
                      {report.continuous_reading.cross_volume_refs.slice(0, 4).map((item) => (
                        <article key={item.id}>
                          <span className="tiny muted">{item.label}</span>
                          <strong>{item.title}</strong>
                          <p>{item.summary}</p>
                          <small>{item.evidence_refs.length} 条证据</small>
                        </article>
                      ))}
                    </div>
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

function buildMisbeliefNodes(report: DossierReadingReport | null): MisbeliefNode[] {
  if (!report) return [];
  return report.perspective_biases
    .map((item) => {
      if (item.source === "continuous_reading") {
        const section = report.continuous_reading?.reading_sections.find(
          (candidate) => candidate.id === item.id,
        );
        return {
          key: `${item.source}-${item.id}`,
          id: item.id,
          label: item.label || section?.title || "正文场景",
          cognitiveBias: item.cognitive_bias,
          source: item.source,
          sourceLabel: "正文场景",
          targetTab: "continuous_reading",
          sectionId: item.id,
          evidenceCount: sectionEvidenceRefs(
            section || {
              id: item.id,
              title: item.label,
              body: "",
              narrative_role: "",
              evidence_refs: [],
            },
          ).length,
        };
      }
      const tab = report.volume_tabs.find((candidate) => candidate.id === item.id);
      return {
        key: `${item.source}-${item.id}`,
        id: item.id,
        label: item.label || tab?.label || TAB_LABELS[item.id] || "卷宗视角",
        cognitiveBias: item.cognitive_bias,
        source: item.source,
        sourceLabel: "卷宗视角",
        targetTab: item.id,
        evidenceCount: tab?.evidence_refs.length ?? 0,
      };
    })
    .filter((node) => node.cognitiveBias.trim().length > 0);
}

function sectionEvidenceRefs(section: ContinuousReadingSection): string[] {
  const refs = section.evidence_mode?.refs.length
    ? section.evidence_mode.refs
    : section.evidence_refs;
  return refs.filter((ref) => ref.trim().length > 0);
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

function readingContext(
  report: DossierReadingReport | null,
  activeTab: ReadingTab,
  activeVolume?: DossierReadingVolumeTab,
): {
  title: string;
  summary: string;
  stats: Array<{ label: string; value: string }>;
} {
  if (!report) {
    return {
      title: "卷宗阅读",
      summary: "正在聚合连续正文、角色卷和事件证据。",
      stats: [],
    };
  }

  if (activeTab === "continuous_reading") {
    const flow = report.continuous_reading?.reading_flow;
    return {
      title: "连续阅读正文",
      summary:
        flow?.opening_hook ||
        "按小说正文继续读；证据、误会和多视角卷都收在后面，先不打断沉浸。",
      stats: [
        {
          label: "场景",
          value: flow ? `${flow.scene_count} 场` : "待生成",
        },
        {
          label: "证据",
          value: `${report.evidence_panel.ref_count} 条`,
        },
        {
          label: "下一章",
          value: flow?.next_chapter_hook || "等待作者采纳",
        },
      ],
    };
  }

  if (activeTab === "confirmed_chapter") {
    return {
      title: report.confirmed_chapter?.chapter_title || "确认正文",
      summary:
        report.confirmed_chapter?.author_note ||
        "作者确认入卷后的正式章节，可作为下一轮世界沙盘的可靠正史。",
      stats: [
        {
          label: "状态",
          value: report.confirmed_chapter?.edited ? "编辑后定稿" : "确认入卷",
        },
        {
          label: "证据",
          value: `${report.evidence_panel.ref_count} 条`,
        },
        {
          label: "世界线",
          value: report.worldline_id,
        },
      ],
    };
  }

  if (activeTab === "faction_volume") {
    return {
      title: activeVolume?.title || "势力卷",
      summary:
        activeVolume?.cognitive_bias ||
        "这一卷从资源、秘密、公开姿态和因果代偿解释同一段世界演化。",
      stats: [
        {
          label: "卷宗",
          value: activeVolume?.label || "势力卷",
        },
        {
          label: "证据",
          value: `${activeVolume?.evidence_refs.length ?? 0} 条`,
        },
        {
          label: "下一步",
          value: "进入势力卷",
        },
      ],
    };
  }

  return {
    title: activeVolume?.title || TAB_LABELS[activeTab] || "世界卷宗",
    summary:
      activeVolume?.cognitive_bias ||
      "这一卷从特定角色、锚点或事件角度解释同一段世界演化。",
    stats: [
      {
        label: "卷宗",
        value: activeVolume?.label || TAB_LABELS[activeTab] || "未命名",
      },
      {
        label: "证据",
        value: `${activeVolume?.evidence_refs.length ?? 0} 条`,
      },
      {
        label: "来源",
        value: activeVolume?.artifact || "等待生成",
      },
    ],
  };
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
