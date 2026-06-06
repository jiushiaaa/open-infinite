import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import type {
  DossierReadingReport,
  DossierReadingVolumeTab,
  WorldAnchor,
  WorldlineState,
} from "../api/types";
import { renderProse } from "../markdown";
import { navigate } from "../routing";
import { EmptyState, ErrorState, Loading } from "./common/States";
import { WorldRunway } from "./WorldRunway";
import "./factionVolume.css";

interface FactionEntry {
  id: string;
  name: string;
  hint: string;
  evidenceCount: number;
}

export function FactionVolumePage({
  slug,
  worldlineId,
  factionId,
}: {
  slug: string;
  worldlineId: string;
  factionId: string;
}) {
  const [anchor, setAnchor] = useState<WorldAnchor | null>(null);
  const [report, setReport] = useState<DossierReadingReport | null>(null);
  const [worldlineState, setWorldlineState] = useState<WorldlineState | null>(null);
  const [partialError, setPartialError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    setPartialError(null);
    try {
      const [anchorResult, readingResult, stateResult] = await Promise.allSettled([
        api.getWorldAnchor(slug),
        api.getDossierReading(slug, worldlineId),
        api.getWorldlineState(slug, worldlineId),
      ]);
      if (anchorResult.status === "fulfilled") setAnchor(anchorResult.value);
      if (readingResult.status === "fulfilled") setReport(readingResult.value);
      if (stateResult.status === "fulfilled") setWorldlineState(stateResult.value);
      const failures = [anchorResult, readingResult, stateResult].filter(
        (item): item is PromiseRejectedResult => item.status === "rejected",
      );
      if (failures.length === 3) {
        throw failures[0].reason;
      }
      if (failures.length > 0) {
        setPartialError(
          failures
            .map((item) => (item.reason instanceof Error ? item.reason.message : String(item.reason)))
            .join("；"),
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [slug, worldlineId, factionId]);

  const factionVolumes = useMemo(() => factionVolumeTabs(report), [report]);
  const entries = useMemo(
    () => factionEntries(anchor, factionVolumes, factionId),
    [anchor, factionId, factionVolumes],
  );
  const activeEntry =
    entries.find((item) => item.id === factionId || item.name === factionId) || entries[0] || null;
  const activeVolume = chooseFactionVolume(factionVolumes, activeEntry?.name || factionId);
  const consequence = worldlineState?.consequence_state || report?.worldline_dossier?.worldline_state?.consequence_state;
  const domain = consequence?.domains?.faction;
  const latestLedger = consequence?.ledger?.[Math.max(0, (consequence.ledger?.length ?? 1) - 1)];
  const resourceSignals = anchor?.world.factions.length ?? entries.length;
  const activeName = activeEntry?.name || activeVolume?.faction_name || activeVolume?.title || factionId;
  const hasVolume = Boolean(activeVolume?.body_md);

  if (loading) return <Loading label="正在翻开势力卷…" />;

  return (
    <div className="faction-volume-page">
      <header className="faction-volume-hero">
        <div>
          <p className="muted faction-volume-hero__eyebrow">世界内部卷宗 · 势力卷</p>
          <h1>{activeName}</h1>
          <p className="muted">
            这一页只看势力如何被事件推动：谁获得解释权，谁承担代偿，谁把个人误会放大成世界秩序的变化。
          </p>
        </div>
        <div className="faction-volume-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() =>
              navigate({
                name: "dossierReading",
                slug,
                worldlineId,
                tab: "faction_volume",
              })
            }
          >
            回卷宗阅读
          </button>
          <button className="btn btn--primary" onClick={() => navigate({ name: "sandbox", slug })}>
            继续沙盘
          </button>
        </div>
      </header>

      {error && <ErrorState message={error} onRetry={load} />}
      {!error && (
        <>
          {partialError && (
            <div className="faction-volume-alert">
              <strong>部分材料暂未读到</strong>
              <p>{partialError}</p>
            </div>
          )}

          <WorldRunway
            eyebrow="势力压力链"
            title="先看势力站位，再看世界如何把代价压回秩序"
            summary="势力卷不是角色内心独白。它把资源、秘密、公开姿态和因果债放在一起，帮助用户理解世界为什么会继续变化。"
            meta={
              <>
                <span className="badge badge--jade">{resourceSignals} 个势力</span>
                <span className="badge badge--gold">
                  {domain?.pressure || consequence?.status || "压力待显形"}
                </span>
                <span className="badge">世界线 {worldlineId}</span>
              </>
            }
            steps={[
              {
                label: "立场",
                detail: "读取势力卷正文，判断解释权在哪一方手里。",
                active: hasVolume,
              },
              {
                label: "代偿",
                detail: "核对因果债如何压向资源、秘密和公开秩序。",
                active: Boolean(domain || latestLedger),
              },
              {
                label: "行动",
                detail: "回到沙盘观察势力压力如何影响下一轮角色选择。",
                onClick: () => navigate({ name: "sandbox", slug }),
              },
            ]}
            actions={[
              {
                label: "世界锚定",
                detail: "回到势力、地点和规则总览",
                onClick: () => navigate({ name: "anchor", slug }),
              },
              {
                label: "多视角",
                detail: "重新生成势力卷和事件多视角",
                onClick: () => navigate({ name: "lens", slug }),
              },
              {
                label: "作者台",
                detail: "把势力压力写进下一章",
                primary: true,
                onClick: () => navigate({ name: "author", slug }),
              },
            ]}
          />

          <main className="faction-volume-layout">
            <aside className="faction-volume-index" aria-label="势力卷目录">
              <div className="faction-volume-index__head">
                <h2>势力卷</h2>
                <span className="tiny muted">{entries.length || 0} 支</span>
              </div>
              {entries.length === 0 ? (
                <EmptyState title="尚无势力" hint="世界锚定页声明势力后，这里会出现独立阅读入口。" />
              ) : (
                <div className="faction-volume-index__list">
                  {entries.map((item) => (
                    <button
                      key={item.id}
                      className={item.id === activeEntry?.id ? "is-active" : ""}
                      onClick={() =>
                        navigate({
                          name: "factionVolume",
                          slug,
                          worldlineId,
                          factionId: item.id,
                        })
                      }
                    >
                      <strong>{item.name}</strong>
                      <small>{item.hint}</small>
                      <em>{item.evidenceCount} 条证据</em>
                    </button>
                  ))}
                </div>
              )}
            </aside>

            <article className="faction-volume-reader">
              <section className="faction-volume-cover">
                <div>
                  <p className="muted tiny">当前势力</p>
                  <h2>{activeVolume?.title || `${activeName} 的势力卷`}</h2>
                  <p>
                    {activeVolume?.cognitive_bias ||
                      domain?.pressure ||
                      "等待世界沙盘把资源、秘密和公开姿态推到台前。"}
                  </p>
                </div>
                <dl>
                  <div>
                    <dt>势力状态</dt>
                    <dd>{domain?.current || consequence?.summary || "待显形"}</dd>
                  </div>
                  <div>
                    <dt>压力承载</dt>
                    <dd>{domain?.bearer || activeName}</dd>
                  </div>
                  <div>
                    <dt>证据</dt>
                    <dd>{activeVolume?.evidence_refs.length ?? 0} 条</dd>
                  </div>
                </dl>
              </section>

              {hasVolume ? (
                <div className="prose faction-volume-prose">
                  {renderProse(activeVolume!.body_md)}
                </div>
              ) : (
                <EmptyState
                  title="这一支势力还没有正文卷"
                  hint="可以先去多视角页生成势力卷，或继续沙盘让势力压力显形。"
                />
              )}

              {activeVolume?.evidence_refs.length ? (
                <section className="faction-volume-evidence">
                  <h2>卷内证据</h2>
                  <div>
                    {activeVolume.evidence_refs.map((ref) => (
                      <code key={ref}>{ref}</code>
                    ))}
                  </div>
                </section>
              ) : null}
            </article>

            <aside className="faction-volume-state" aria-label="势力代偿状态">
              <section className="faction-volume-state-card">
                <div className="faction-volume-state-card__head">
                  <h2>势力代偿</h2>
                  <span className="badge badge--jade tiny">{consequence?.status || "partial"}</span>
                </div>
                <p>{consequence?.summary || "尚未形成可读代偿摘要。继续运行沙盘后，这里会显示世界把代价压向哪里。"}</p>
                {consequence?.next_round_hint && (
                  <blockquote>{consequence.next_round_hint}</blockquote>
                )}
              </section>

              <section className="faction-volume-state-card">
                <div className="faction-volume-state-card__head">
                  <h2>压力域</h2>
                  <span className="tiny muted">domains.faction</span>
                </div>
                {domain ? (
                  <dl className="faction-volume-domain">
                    <div>
                      <dt>当前</dt>
                      <dd>{domain.current || "未标注"}</dd>
                    </div>
                    <div>
                      <dt>压力</dt>
                      <dd>{domain.pressure || "未标注"}</dd>
                    </div>
                    <div>
                      <dt>承载者</dt>
                      <dd>{domain.bearer || "未标注"}</dd>
                    </div>
                  </dl>
                ) : (
                  <EmptyState title="暂无势力压力域" hint="新一轮沙盘会把代偿写入 worldline_state。" />
                )}
              </section>

              <section className="faction-volume-state-card">
                <div className="faction-volume-state-card__head">
                  <h2>最近记录</h2>
                  <span className="tiny muted">ledger</span>
                </div>
                {latestLedger ? (
                  <div className="faction-volume-ledger">
                    <strong>{latestLedger.major_event || latestLedger.source_run_id}</strong>
                    <span className="badge tiny">债务 {latestLedger.debt_score ?? "待评估"}</span>
                    {latestLedger.impacts?.length ? (
                      <div>
                        {latestLedger.impacts.map((impact, index) => (
                          <p key={`${impact.domain}-${index}`}>
                            <b>{impact.domain || "domain"}</b>：{impact.current || "未标注"} · {impact.pressure || "未标注压力"}
                          </p>
                        ))}
                      </div>
                    ) : null}
                  </div>
                ) : (
                  <EmptyState title="暂无 ledger" hint="代偿记录会在自演或干预后累积。" />
                )}
              </section>
            </aside>
          </main>
        </>
      )}
    </div>
  );
}

function factionVolumeTabs(report: DossierReadingReport | null): DossierReadingVolumeTab[] {
  return report?.volume_tabs.filter((tab) => tab.id === "faction_volume") ?? [];
}

function factionEntries(
  anchor: WorldAnchor | null,
  volumes: DossierReadingVolumeTab[],
  fallbackId: string,
): FactionEntry[] {
  const names = anchor?.world.factions.filter((name) => name.trim().length > 0) ?? [];
  if (names.length > 0) {
    return names.map((name) => {
      const volume = chooseFactionVolume(volumes, name);
      return {
        id: name,
        name,
        hint:
          volume?.cognitive_bias ||
          "查看这支势力在资源、秘密和公开姿态上的压力。",
        evidenceCount: volume?.evidence_refs.length ?? 0,
      };
    });
  }
  if (volumes.length > 0) {
    return volumes.map((volume) => ({
      id: volume.faction_id || volume.faction_name || volume.title,
      name: volume.faction_name || volume.title,
      hint: volume.cognitive_bias,
      evidenceCount: volume.evidence_refs.length,
    }));
  }
  return [
    {
      id: fallbackId,
      name: fallbackId,
      hint: "这一支势力还没有进入世界锚定，但可以先查看代偿压力。",
      evidenceCount: 0,
    },
  ];
}

function chooseFactionVolume(
  volumes: DossierReadingVolumeTab[],
  factionName: string,
): DossierReadingVolumeTab | null {
  if (volumes.length === 0) return null;
  const needle = factionName.trim();
  return (
    volumes.find(
      (volume) =>
        volume.faction_id === needle ||
        volume.faction_name === needle ||
        volume.title.includes(needle),
    ) || volumes[0]
  );
}
