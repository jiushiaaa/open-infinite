import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { WorldAutopilotCheckpointReplayReport } from "../api/types";
import { navigate } from "../routing";
import { EmptyState, ErrorState } from "./common/States";
import { WorldRunway } from "./WorldRunway";
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
  const rememberedCount =
    readableEntry?.memory_readout.who_remembered_what.length ??
    checkpoint?.who_remembered_what?.length ??
    0;
  const storyPossibilityCount = checkpoint?.next_story_possibilities.length ?? 0;
  const readAction = readableEntry?.primary_actions.find(
    (action) => action.id === "continuous_reading",
  );
  const commandTitle = checkpoint
    ? `第 ${checkpoint.round_index} 轮发生了什么`
    : "读取检查点";
  const commandHint =
    readableEntry?.state_change_explanation.headline ||
    checkpoint?.major_event ||
    "正在把这一轮世界变化整理成可继续阅读、回放和采纳的入口。";
  const commandSteps = [
    {
      label: "事件",
      title: "确认大事件",
      detail: checkpoint?.major_event || "读取本轮沙盘事件。",
      active: true,
      done: !!checkpoint,
    },
    {
      label: "记忆",
      title: "看谁被改变",
      detail: rememberedCount ? `${rememberedCount} 条角色记忆` : "等待角色记忆写入。",
      active: false,
      done: rememberedCount > 0,
    },
    {
      label: "代偿",
      title: "承接世界代价",
      detail: consequenceDomains.length
        ? `${consequenceDomains.length} 个世界域承压`
        : "下一轮继续追踪因果债。",
      active: false,
      done: consequenceDomains.length > 0,
    },
    {
      label: "续读",
      title: "回到连续正文",
      detail: readAction?.reason || "把检查点接回卷宗阅读。",
      active: false,
      done: !!readAction,
    },
  ];
  const goToCheckpointReading = () => {
    if (readAction?.route?.startsWith("#/")) {
      window.location.hash = readAction.route;
      return;
    }
    navigate({ name: "dossierReading", slug, worldlineId });
  };
  const scrollToCheckpointItem = (selector: string) => {
    document.querySelector(selector)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

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
      </header>

      {!loading && !error && report && checkpoint && (
        <section className="checkpoint-mobile-guide" aria-label="检查点移动端快速导读">
          <div>
            <p className="muted tiny">醒来后先做什么</p>
            <strong>{checkpoint.major_event}</strong>
          </div>
          <div className="checkpoint-mobile-guide__actions">
            <button className="btn btn--primary" onClick={goToCheckpointReading}>
              继续读
            </button>
            <button
              className="btn btn--ghost"
              onClick={() => scrollToCheckpointItem(".worldline-memory-section")}
            >
              看记忆
            </button>
            <button
              className="btn btn--ghost"
              onClick={() => scrollToCheckpointItem(".worldline-consequence-section")}
            >
              看代偿
            </button>
            <button className="btn btn--ghost" onClick={() => navigate({ name: "author", slug })}>
              作者台
            </button>
          </div>
        </section>
      )}

      {!loading && !error && report && checkpoint && (
        <section className="worldline-command" aria-label="检查点工作流总览">
          <div className="worldline-command__lead">
            <p className="muted worldline-command__eyebrow">醒来回放</p>
            <h2>{commandTitle}</h2>
            <p className="muted">{commandHint}</p>
            <div className="worldline-command__meta">
              <span className="badge badge--jade">{checkpoint.stage}</span>
              <span className="badge">{worldlineId}</span>
              <span className="badge badge--gold">{checkpoint.causal_debt}</span>
            </div>
          </div>

          <div className="worldline-command__steps">
            {commandSteps.map((item, index) => (
              <article
                className={`worldline-command__step ${
                  item.active ? "is-active" : item.done ? "is-done" : ""
                }`}
                key={item.label}
              >
                <span>{index + 1}</span>
                <div>
                  <p className="muted tiny">{item.label}</p>
                  <strong>{item.title}</strong>
                  <small>{item.detail}</small>
                </div>
              </article>
            ))}
          </div>

          <div className="worldline-command__actions">
            <button
              className="btn btn--primary"
              onClick={goToCheckpointReading}
            >
              {readAction?.label || "进入连续阅读"}
            </button>
            <button
              className="btn btn--ghost"
              onClick={() => navigate({ name: "worldline", slug, worldlineId })}
            >
              返回世界线
            </button>
            <button className="btn btn--ghost" onClick={() => navigate({ name: "sandbox", slug })}>
              继续沙盘
            </button>
            <button className="btn btn--ghost" onClick={() => navigate({ name: "author", slug })}>
              作者采纳台
            </button>
          </div>

          <div className="worldline-command__proof" aria-label="检查点摘要">
            <div>
              <span className="muted tiny">本轮</span>
              <strong>第 {checkpoint.round_index} 轮</strong>
            </div>
            <div>
              <span className="muted tiny">角色记忆</span>
              <strong>{rememberedCount || "待写入"}</strong>
            </div>
            <div>
              <span className="muted tiny">后续可能</span>
              <strong>{storyPossibilityCount || "待显形"}</strong>
            </div>
            <p>
              {readableEntry?.state_change_explanation.why_world_changed ||
                readableEntry?.memory_readout.summary ||
                checkpoint.chapter_seed?.next_chapter_hook ||
                report.replay.resume_hint ||
                checkpoint.major_event}
            </p>
          </div>
        </section>
      )}

      <WorldRunway
        eyebrow="检查点导览"
        title="这一轮已经发生，下一步要让它继续影响世界"
        summary="检查点不是日志终点，而是恢复、阅读和下一章采纳的锚点。先回看变化，再把它投回世界线。"
        meta={
          <>
            <span className="badge badge--jade">
              {checkpoint ? `第 ${checkpoint.round_index} 轮` : "读取中"}
            </span>
            <span className="badge">{worldlineId}</span>
            {checkpoint?.causal_debt && (
              <span className="badge badge--gold">{checkpoint.causal_debt}</span>
            )}
          </>
        }
        steps={[
          {
            label: "回看变化",
            detail: "确认事件、锚点压力和因果债。",
            active: true,
          },
          {
            label: "读后续",
            detail: "把这个检查点接到连续阅读。",
            onClick: () => navigate({ name: "dossierReading", slug, worldlineId }),
          },
          {
            label: "写入下一章",
            detail: "让作者台采纳这轮涌现剧情。",
            onClick: () => navigate({ name: "author", slug }),
          },
        ]}
        actions={[
          {
            label: "返回世界线",
            detail: "查看全部任务、检查点和承接状态",
            onClick: () => navigate({ name: "worldline", slug, worldlineId }),
          },
          {
            label: "继续沙盘",
            detail: "从这一条世界线继续让角色行动",
            primary: true,
            onClick: () => navigate({ name: "sandbox", slug }),
          },
          {
            label: "多视角卷",
            detail: "生成或查看角色视角正文",
            onClick: () => navigate({ name: "lens", slug }),
          },
        ]}
      />

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

            <section className="worldline-section worldline-memory-section">
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

            <section className="worldline-section worldline-consequence-section">
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
