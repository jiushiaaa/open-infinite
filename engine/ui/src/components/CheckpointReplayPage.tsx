import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { WorldAutopilotCheckpointReplayReport } from "../api/types";
import { navigate } from "../routing";
import { EmptyState, ErrorState } from "./common/States";
import "./worldlineDossier.css";

export function CheckpointReplayPage({
  slug,
  worldlineId,
  runId,
  checkpointId,
}: {
  slug: string;
  worldlineId: string;
  runId: string;
  checkpointId: string;
}) {
  const [report, setReport] = useState<WorldAutopilotCheckpointReplayReport | null>(
    null,
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setReport(await api.replayWorldAutopilotCheckpoint(runId, checkpointId));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [runId, checkpointId]);

  const checkpoint = report?.checkpoint;
  const readableEntry = report?.readable_entry;
  const consequenceDomains = checkpoint?.consequence_state?.domains
    ? Object.entries(checkpoint.consequence_state.domains)
    : [];

  return (
    <div className="worldline-page">
      <header className="worldline-hero">
        <div>
          <p className="worldline-hero__eyebrow muted">世界内部卷宗 · 检查点</p>
          <h1>{checkpointId} 回放</h1>
          <p className="muted">
            回看这一轮世界如何推进、谁记住了什么，以及下一轮应承接哪些代价。
          </p>
        </div>
        <div className="worldline-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "worldline", slug, worldlineId })}
          >
            返回世界线
          </button>
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "sandbox", slug })}
          >
            继续沙盘
          </button>
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "lens", slug })}
          >
            多视角卷
          </button>
        </div>
      </header>

      <main className="worldline-layout">
        {loading && <EmptyState title="正在回放检查点" hint="正在读取本地检查点证据。" />}
        {error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && report && checkpoint && (
          <>
            {readableEntry && (
              <section className="worldline-section worldline-wake-bridge">
                <div className="worldline-section__title">
                  <div>
                    <h2>从这个检查点继续读</h2>
                    <p className="muted tiny">
                      {readableEntry.state_change_explanation.why_world_changed}
                    </p>
                  </div>
                </div>
                <div className="worldline-action-row">
                  {readableEntry.primary_actions
                    .filter((action) => action.id !== "latest_checkpoint")
                    .map((action) => (
                      <button
                        key={action.id}
                        className="btn btn--ghost"
                        onClick={() => {
                          if (action.route.startsWith("#/")) {
                            window.location.hash = action.route;
                          }
                        }}
                        title={action.reason}
                      >
                        {action.label}
                      </button>
                    ))}
                </div>
              </section>
            )}

            <section className="worldline-section worldline-summary">
              <div className="worldline-section__title">
                <h2>回放摘要</h2>
                <span className="badge badge--jade">
                  第 {checkpoint.round_index} 轮
                </span>
              </div>
              <dl>
                <div>
                  <dt>自演运行</dt>
                  <dd className="mono">{report.run_id}</dd>
                </div>
                <div>
                  <dt>沙盘运行</dt>
                  <dd className="mono">{report.replay.sandbox_run_id}</dd>
                </div>
                <div>
                  <dt>大事件</dt>
                  <dd>{checkpoint.major_event}</dd>
                </div>
                <div>
                  <dt>世界阶段</dt>
                  <dd>{checkpoint.stage}</dd>
                </div>
                <div>
                  <dt>锚点压力</dt>
                  <dd>{checkpoint.anchor_pressure}</dd>
                </div>
                <div>
                  <dt>因果债</dt>
                  <dd>{checkpoint.causal_debt}</dd>
                </div>
              </dl>
            </section>

            <section className="worldline-section">
              <div className="worldline-section__title">
                <h2>这一轮谁记住了什么</h2>
                <span className="badge badge--gold">
                  {checkpoint.who_remembered_what?.length ?? 0}
                </span>
              </div>
              <div className="worldline-memory-list">
                {checkpoint.who_remembered_what?.map((item, index) => (
                  <article key={`${item.character_id}-${index}`}>
                    <span>{item.character_id || "角色"}</span>
                    <strong>{item.remembered || "记住了本轮变化"}</strong>
                  </article>
                ))}
              </div>
            </section>

            <section className="worldline-section">
              <div className="worldline-section__title">
                <h2>具象代偿</h2>
                <span className="badge badge--gold">
                  {checkpoint.consequence_state?.status ?? "none"}
                </span>
              </div>
              {consequenceDomains.length === 0 ? (
                <EmptyState title="本检查点没有代偿记录" hint="后续沙盘会在世界线档案中持续补充代偿账。" />
              ) : (
                <>
                  <p className="muted">{checkpoint.consequence_state?.summary}</p>
                  <div className="worldline-domain-grid">
                    {consequenceDomains.map(([key, item]) => (
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
                  {checkpoint.consequence_state?.next_round_hint && (
                    <p className="muted tiny">
                      {checkpoint.consequence_state.next_round_hint}
                    </p>
                  )}
                </>
              )}
            </section>

            <section className="worldline-section">
              <div className="worldline-section__title">
                <h2>下一步可写方向</h2>
                <button
                  className="btn btn--ghost tiny"
                  onClick={() => navigate({ name: "author", slug })}
                >
                  去采纳
                </button>
              </div>
              <div className="worldline-stack">
                {checkpoint.next_story_possibilities.map((item) => (
                  <article key={item.id || item.title}>
                    <strong>{item.title || "后续可能性"}</strong>
                    <p>{item.brief || "等待沙盘继续显形。"}</p>
                  </article>
                ))}
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}
