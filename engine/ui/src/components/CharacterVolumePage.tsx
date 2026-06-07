import { useEffect, useMemo, useState } from "react";
import { ApiError, api } from "../api/client";
import type {
  DossierReadingReport,
  DossierReadingVolumeTab,
  SubjectiveMemoryEntry,
  SubjectiveMemoryReport,
} from "../api/types";
import { renderProse } from "../markdown";
import { navigate } from "../routing";
import { EmptyState, ErrorState, Loading } from "./common/States";
import { WorldRunway } from "./WorldRunway";
import "./characterVolume.css";

export function CharacterVolumePage({
  slug,
  worldlineId,
  characterId,
}: {
  slug: string;
  worldlineId: string;
  characterId: string;
}) {
  const [report, setReport] = useState<DossierReadingReport | null>(null);
  const [memory, setMemory] = useState<SubjectiveMemoryReport | null>(null);
  const [memoryError, setMemoryError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    setMemoryError(null);
    try {
      const [dossierResult, memoryResult] = await Promise.allSettled([
        api.getDossierReading(slug, worldlineId),
        api.getSubjectiveMemory(slug, worldlineId, characterId),
      ]);
      if (dossierResult.status === "rejected") {
        throw dossierResult.reason;
      }
      setReport(dossierResult.value);
      if (memoryResult.status === "fulfilled") {
        setMemory(memoryResult.value);
      } else {
        const reason = memoryResult.reason;
        if (reason instanceof ApiError && reason.status === 404) {
          setMemory(null);
        } else {
          setMemoryError(reason instanceof Error ? reason.message : String(reason));
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [slug, worldlineId, characterId]);

  const characterTabs = useMemo(
    () => characterVolumeTabs(report, memory, characterId),
    [characterId, memory, report],
  );
  const activeTab = useMemo(
    () =>
      characterTabs.find((tab) => tab.character_id === characterId) ||
      characterTabs.find((tab) => tab.id === "character_volume") ||
      null,
    [characterId, characterTabs],
  );
  const characterName =
    activeTab?.character_name || memory?.entries[0]?.character_name || characterId;
  const latestMemory = memory?.entries[memory.entries.length - 1] ?? null;
  const primaryMisbelief =
    memory?.entries
      .slice()
      .reverse()
      .flatMap((entry) => entry.misbeliefs ?? [])[0] ?? null;
  const memoryStats = summarizeMemory(memory);
  const memoryArcSignals = (memory?.entries.slice(-4) ?? []).map((entry, index, entries) => ({
    key: `${entry.source_run_id}-${entry.source_round_index}-${index}`,
    roundLabel: `第 ${entry.source_round_index} 轮`,
    event: entry.source_major_event,
    previousBelief: entry.previous_subjective_memory || "上一段主观记忆尚未成形。",
    newBelief: entry.new_belief || "等待这段记忆形成新的判断。",
    trustDelta: entry.trust_delta || entry.trust_shift || "信任暂无明显变化。",
    anomalyDelta: entry.anomaly_delta || entry.emotional_impact || "异常感暂未升高。",
    expectedOutcome:
      entry.expected_outcome ||
      entry.memory_influence ||
      entry.action_outcome?.reason ||
      "下一轮行动仍待沙盘验证。",
    isLatest: index === entries.length - 1,
  }));
  const hasVolume = Boolean(activeTab?.body_md);
  const scrollToCharacterItem = (selector: string) => {
    document.querySelector(selector)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  if (loading) return <Loading label="正在翻开角色个人卷…" />;

  return (
    <div className="character-volume-page">
      <header className="character-volume-hero">
        <div>
          <p className="muted character-volume-hero__eyebrow">世界内部卷宗 · 角色个人卷</p>
          <h1>{characterName}</h1>
          <p className="muted">
            这一页只看一个角色的主观世界：他看见什么、误会什么、隐瞒什么，以及这些记忆怎样推动下一轮行动。
          </p>
        </div>
        <div className="character-volume-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() =>
              navigate({
                name: "dossierReading",
                slug,
                worldlineId,
                tab: "character_volume",
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
          <nav className="character-volume-mobile-guide" aria-label="移动端角色卷导读">
            <button type="button" onClick={() => scrollToCharacterItem(".character-volume-cover")}>
              <span>01</span>
              <strong>读立场</strong>
              <small>先看他如何解释世界</small>
            </button>
            <button type="button" onClick={() => scrollToCharacterItem(".character-volume-memory")}>
              <span>02</span>
              <strong>查记忆</strong>
              <small>核对误会和秘密可见性</small>
            </button>
            <button type="button" onClick={() => scrollToCharacterItem(".character-volume-index")}>
              <span>03</span>
              <strong>换角色</strong>
              <small>切到其他主观视角</small>
            </button>
            <button type="button" onClick={() => navigate({ name: "author", slug })}>
              <span>04</span>
              <strong>作者台</strong>
              <small>把角色弧写入下一章</small>
            </button>
          </nav>

          <WorldRunway
            eyebrow="角色主观链"
            title="先读他的立场，再看他的记忆怎样改变行动"
            summary="角色个人卷不是正史摘要。它故意保留盲区、误会和秘密，让用户看见同一世界事实在角色心里变成了什么。"
            meta={
              <>
                <span className="badge badge--jade">{memoryStats.entries} 条记忆</span>
                <span className="badge badge--gold">{memoryStats.misbeliefs} 条误会</span>
                <span className="badge">世界线 {worldlineId}</span>
              </>
            }
            steps={[
              {
                label: "立场",
                detail: "读角色卷正文，理解他如何解释事件。",
                active: hasVolume,
              },
              {
                label: "记忆",
                detail: "核对主观感知、误会、秘密可见性和未知正史。",
                active: Boolean(memory?.entries.length),
              },
              {
                label: "行动",
                detail: "回沙盘观察这些记忆如何影响下一轮选择。",
                onClick: () => navigate({ name: "sandbox", slug }),
              },
            ]}
            actions={[
              {
                label: "卷宗阅读",
                detail: "回到连续正文和多卷宗视角",
                onClick: () =>
                  navigate({
                    name: "dossierReading",
                    slug,
                    worldlineId,
                    tab: "character_volume",
                  }),
              },
              {
                label: "多视角",
                detail: "生成新的事件视角",
                onClick: () => navigate({ name: "lens", slug }),
              },
              {
                label: "作者台",
                detail: "把角色弧写入下一章",
                primary: true,
                onClick: () => navigate({ name: "author", slug }),
              },
            ]}
          />

          <section className="character-memory-handoff" aria-label="记忆接力台">
            <div className="character-memory-handoff__lead">
              <p className="muted tiny">记忆接力台</p>
              <h2>先抓住这个角色会带着什么进入下一章</h2>
              <p>
                把当前立场、最新记忆、首要误会和下一轮行动放在一起，读角色卷时能看见他的偏见怎样继续推动世界。
              </p>
            </div>
            <article>
              <span>当前立场</span>
              <strong>{activeTab?.cognitive_bias || latestMemory?.new_belief || "等待角色留下更清晰的主观立场"}</strong>
              <p>{activeTab?.title || `${characterName} 的角色卷会继续补足他如何解释事件。`}</p>
              <button className="btn btn--ghost tiny" onClick={() => scrollToCharacterItem(".character-volume-cover")}>
                读他的立场
              </button>
            </article>
            <article>
              <span>最新记忆</span>
              <strong>{latestMemory?.new_belief || "尚无新记忆"}</strong>
              <p>
                {latestMemory?.memory_influence ||
                  latestMemory?.action_outcome?.reason ||
                  "运行一轮沙盘后，这里会显示记忆如何改变他的选择。"}
              </p>
              <button className="btn btn--ghost tiny" onClick={() => scrollToCharacterItem(".character-volume-memory")}>
                查主观记忆
              </button>
            </article>
            <article>
              <span>首要误会</span>
              <strong>{primaryMisbelief || "暂无待回收误会"}</strong>
              <p>
                {primaryMisbelief
                  ? `${memoryStats.misbeliefs} 条误会会影响这个角色下一轮如何理解别人。`
                  : "当前更适合先积累行动和记忆，再回收误会。"}
              </p>
              <button className="btn btn--ghost tiny" onClick={() => scrollToCharacterItem(".character-volume-memory")}>
                回看误会
              </button>
            </article>
            <article>
              <span>下一轮行动</span>
              <strong>{latestMemory?.expected_outcome || latestMemory?.source_action || "回沙盘验证这段记忆"}</strong>
              <p>把这条角色弧送回世界，让下一轮行动继续消费他的误会、秘密和主观判断。</p>
              <button className="btn btn--primary tiny" onClick={() => navigate({ name: "author", slug })}>
                把角色弧送到作者台
              </button>
            </article>
          </section>

          {memoryArcSignals.length > 0 && (
            <section className="character-memory-arc" aria-label="角色记忆弧线">
              <div className="character-memory-arc__head">
                <div>
                  <p className="muted tiny">角色记忆弧线</p>
                  <h2>这些记忆正在改写他的下一次选择</h2>
                </div>
                <span className="badge badge--jade">{memoryArcSignals.length} 段连续记忆</span>
              </div>
              <div className="character-memory-arc__grid">
                {memoryArcSignals.map((signal) => (
                  <article
                    className={`character-memory-arc__step${signal.isLatest ? " is-latest" : ""}`}
                    key={signal.key}
                  >
                    <span className="character-memory-arc__round">{signal.roundLabel}</span>
                    <strong>{signal.event}</strong>
                    <dl>
                      <div>
                        <dt>信念变化</dt>
                        <dd>
                          {signal.previousBelief} → {signal.newBelief}
                        </dd>
                      </div>
                      <div>
                        <dt>信任变化</dt>
                        <dd>{signal.trustDelta}</dd>
                      </div>
                      <div>
                        <dt>异常感</dt>
                        <dd>{signal.anomalyDelta}</dd>
                      </div>
                      <div>
                        <dt>下一次会怎样</dt>
                        <dd>{signal.expectedOutcome}</dd>
                      </div>
                    </dl>
                  </article>
                ))}
              </div>
              <div className="character-memory-arc__actions">
                <button className="btn btn--ghost" onClick={() => scrollToCharacterItem(".character-volume-memory")}>
                  看完整记忆链
                </button>
                <button className="btn btn--primary" onClick={() => navigate({ name: "sandbox", slug })}>
                  回沙盘验证
                </button>
              </div>
            </section>
          )}

          <main className="character-volume-layout">
            <aside className="character-volume-index" aria-label="角色卷目录">
              <div className="character-volume-index__head">
                <h2>角色卷</h2>
                <span className="tiny muted">{characterTabs.length || 0} 位</span>
              </div>
              {characterTabs.length === 0 ? (
                <EmptyState title="尚无角色卷" hint="生成多视角卷宗后会在这里出现角色个人卷。" />
              ) : (
                <div className="character-volume-index__list">
                  {characterTabs.map((tab) => (
                    <button
                      key={`${tab.character_id || tab.title}-${tab.artifact}`}
                      className={tab.character_id === characterId ? "is-active" : ""}
                      onClick={() =>
                        tab.character_id &&
                        navigate({
                          name: "characterVolume",
                          slug,
                          worldlineId,
                          characterId: tab.character_id,
                        })
                      }
                      disabled={!tab.character_id}
                    >
                      <strong>{tab.character_name || tab.title}</strong>
                      <small>{tab.cognitive_bias || "尚未标注认知偏差"}</small>
                      <em>{tab.evidence_refs.length} 条证据</em>
                    </button>
                  ))}
                </div>
              )}
            </aside>

            <article className="character-volume-reader">
              <section className="character-volume-cover">
                <div>
                  <p className="muted tiny">当前角色</p>
                  <h2>{activeTab?.title || `${characterName} 的个人卷`}</h2>
                  <p>{activeTab?.cognitive_bias || latestMemory?.new_belief || "等待这个角色留下更多主观记忆。"}</p>
                </div>
                <dl>
                  <div>
                    <dt>主观记忆</dt>
                    <dd>{memoryStats.entries} 条</dd>
                  </div>
                  <div>
                    <dt>误会</dt>
                    <dd>{memoryStats.misbeliefs} 条</dd>
                  </div>
                  <div>
                    <dt>秘密可见</dt>
                    <dd>{memoryStats.secretSignals} 次</dd>
                  </div>
                </dl>
              </section>

              {hasVolume ? (
                <div className="prose character-volume-prose">
                  {renderProse(activeTab!.body_md)}
                </div>
              ) : (
                <EmptyState
                  title="这一位还没有角色卷正文"
                  hint="可以先去多视角页生成角色个人卷，或从沙盘页查看主观记忆。"
                />
              )}

              {activeTab?.evidence_refs.length ? (
                <section className="character-volume-evidence">
                  <h2>卷内证据</h2>
                  <div>
                    {activeTab.evidence_refs.map((ref) => (
                      <code key={ref}>{ref}</code>
                    ))}
                  </div>
                </section>
              ) : null}
            </article>

            <aside className="character-volume-memory" aria-label="主观记忆链">
              <div className="character-volume-memory__head">
                <h2>主观记忆链</h2>
                <span className="badge badge--jade tiny">{memoryStats.entries} 条</span>
              </div>
              {memoryError && <ErrorState message={memoryError} onRetry={load} />}
              {!memoryError && !memory?.entries.length && (
                <EmptyState title="尚无主观记忆" hint="运行一轮世界沙盘后，这里会出现角色自己的记忆链。" />
              )}
              {!memoryError && memory?.entries.length ? (
                <div className="character-volume-memory__timeline">
                  {memory.entries
                    .slice()
                    .reverse()
                    .map((entry) => (
                      <MemoryEntryCard entry={entry} key={`${entry.source_run_id}-${entry.source_round_index}`} />
                    ))}
                </div>
              ) : null}
            </aside>
          </main>
        </>
      )}
    </div>
  );
}

function characterVolumeTabs(
  report: DossierReadingReport | null,
  memory: SubjectiveMemoryReport | null,
  characterId: string,
): DossierReadingVolumeTab[] {
  const tabs = report?.volume_tabs.filter((tab) => tab.id === "character_volume") ?? [];
  if (tabs.some((tab) => tab.character_id === characterId)) return tabs;
  const firstMemory = memory?.entries[0];
  if (!firstMemory) return tabs;
  return [
    ...tabs,
    {
      id: "character_volume",
      label: "角色个人卷",
      title: `${firstMemory.character_name || characterId} 的个人卷`,
      body_md: "",
      character_id: characterId,
      character_name: firstMemory.character_name,
      cognitive_bias: firstMemory.new_belief || "这个角色已经留下主观记忆，正文卷仍待生成。",
      evidence_refs: memory?.entries.map((entry) => entry.source_run_id) ?? [],
      artifact: memory?.artifact ?? "subjective_memory.jsonl",
      default_open: false,
    },
  ];
}

function summarizeMemory(memory: SubjectiveMemoryReport | null) {
  const entries = memory?.entries ?? [];
  return {
    entries: entries.length,
    misbeliefs: entries.reduce((total, entry) => total + (entry.misbeliefs?.length ?? 0), 0),
    secretSignals: entries.filter(
      (entry) => entry.secret_visibility && entry.secret_visibility !== "hidden",
    ).length,
  };
}

function MemoryEntryCard({ entry }: { entry: SubjectiveMemoryEntry }) {
  const tags = [
    entry.awareness_level,
    entry.secret_visibility,
    entry.decision_mode,
    entry.action_outcome?.status,
  ].filter(Boolean);

  return (
    <article className="character-volume-memory-card">
      <header>
        <span className="character-volume-memory-card__round">
          第 {entry.source_round_index} 轮
        </span>
        <div>
          <strong>{entry.source_major_event}</strong>
          <small className="muted mono">{entry.source_run_id}</small>
        </div>
      </header>

      <p>{entry.new_belief}</p>

      <dl>
        {entry.perceived_event && (
          <div>
            <dt>主观感知</dt>
            <dd>{entry.perceived_event}</dd>
          </div>
        )}
        {entry.inner_thought && (
          <div>
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
        {entry.memory_influence && (
          <div>
            <dt>行动影响</dt>
            <dd>{entry.memory_influence}</dd>
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
      </dl>

      {tags.length > 0 && (
        <div className="character-volume-memory-card__tags">
          {tags.map((tag) => (
            <span className="badge tiny" key={tag}>
              {tag}
            </span>
          ))}
        </div>
      )}
    </article>
  );
}
