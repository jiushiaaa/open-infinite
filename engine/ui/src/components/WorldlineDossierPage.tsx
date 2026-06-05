import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { WorldlineDossierReport } from "../api/types";
import { navigate } from "../routing";
import { EmptyState, ErrorState } from "./common/States";
import "./worldlineDossier.css";

export function WorldlineDossierPage({
  slug,
  worldlineId,
}: {
  slug: string;
  worldlineId: string;
}) {
  const [report, setReport] = useState<WorldlineDossierReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [taskBusy, setTaskBusy] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setReport(await api.getWorldlineDossier(slug, worldlineId));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function updateTask(taskId: string, action: "pause" | "resume") {
    setTaskBusy(taskId);
    setError(null);
    try {
      if (action === "pause") {
        await api.pauseWorldAutopilotTask(slug, worldlineId, taskId);
      } else {
        await api.resumeWorldAutopilotTask(slug, worldlineId, taskId);
      }
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setTaskBusy(null);
    }
  }

  useEffect(() => {
    void load();
  }, [slug, worldlineId]);

  const state = report?.worldline_state;
  const consequenceDomains = state?.consequence_state?.domains
    ? Object.entries(state.consequence_state.domains)
    : [];
  const latestCheckpoint = report?.checkpoints[0];

  return (
    <div className="worldline-page">
      <header className="worldline-hero">
        <div>
          <p className="worldline-hero__eyebrow muted">世界内部卷宗 · 世界线</p>
          <h1>{worldlineId} 的承接档案</h1>
          <p className="muted">
            汇总来源干预、天命快照审计、因果债、具象代偿、自演任务和检查点。
          </p>
        </div>
        <div className="worldline-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "dossierReading", slug, worldlineId })}
          >
            卷宗阅读
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
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "author", slug })}
          >
            作者采纳台
          </button>
        </div>
      </header>

      <main className="worldline-layout">
        {loading && <EmptyState title="正在读取世界线" hint="正在聚合状态、任务和检查点。" />}
        {error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && report && (
          <>
            <section className="worldline-section worldline-summary">
              <div className="worldline-section__title">
                <h2>分支状态</h2>
                <span className="badge badge--jade">
                  {state?.branch_state?.continuation_status ?? state?.status ?? "new"}
                </span>
              </div>
              <dl>
                <div>
                  <dt>当前世界线</dt>
                  <dd className="mono">{report.worldline_id}</dd>
                </div>
                <div>
                  <dt>来源干预</dt>
                  <dd>{state?.source_intervention?.content || "没有绑定干预"}</dd>
                </div>
                <div>
                  <dt>投放方式</dt>
                  <dd>
                    {projectionModeLabel(
                      state?.source_intervention?.projection_mode ||
                        state?.branch_state?.projection_mode,
                    )}
                  </dd>
                </div>
                <div>
                  <dt>天命快照审计</dt>
                  <dd>
                    {report.tianming_audit.audit_status}
                    {report.tianming_audit.root_tianming_mutated
                      ? " · 根天命书已变化"
                      : " · 根天命书未覆盖"}
                  </dd>
                </div>
                <div>
                  <dt>因果债</dt>
                  <dd>
                    {state?.causal_debt?.level ?? "unknown"} /{" "}
                    {state?.causal_debt?.score ?? 0}
                  </dd>
                </div>
                <div>
                  <dt>下一轮读取</dt>
                  <dd>{state?.branch_state?.next_round_reads?.join("；") || "等待沙盘运行"}</dd>
                </div>
              </dl>
            </section>

            <section className="worldline-section">
              <div className="worldline-section__title">
                <h2>下一轮如何继续</h2>
                <button
                  className="btn btn--ghost tiny"
                  onClick={() => navigate({ name: "sandbox", slug })}
                >
                  进入沙盘
                </button>
              </div>
              <div className="worldline-action-list">
                {report.next_actions.map((item) => (
                  <article key={`${item.action}-${item.run_id ?? item.worldline_id ?? ""}`}>
                    <strong>{item.label}</strong>
                    <p>{item.reason}</p>
                    {item.action === "replay_checkpoint" && item.run_id && item.checkpoint_id && (
                      <button
                        className="btn btn--ghost tiny"
                        onClick={() =>
                          navigate({
                            name: "checkpoint",
                            slug,
                            worldlineId,
                            runId: item.run_id || "",
                            checkpointId: item.checkpoint_id || "",
                          })
                        }
                      >
                        回放
                      </button>
                    )}
                  </article>
                ))}
              </div>
            </section>

            <section className="worldline-section">
              <div className="worldline-section__title">
                <h2>具象代偿账</h2>
                <span className="badge badge--gold">
                  {state?.consequence_state?.status ?? "none"}
                </span>
              </div>
              {consequenceDomains.length === 0 ? (
                <EmptyState title="代偿尚未显形" hint="运行沙盘或世界自演后会记录地点、资源、伤势、舆论、势力和环境代价。" />
              ) : (
                <>
                  <p className="muted">{state?.consequence_state?.summary}</p>
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
                  {state?.consequence_state?.next_round_hint && (
                    <p className="muted tiny">{state.consequence_state.next_round_hint}</p>
                  )}
                </>
              )}
            </section>

            <section className="worldline-section worldline-grid">
              <div>
                <div className="worldline-section__title">
                  <h2>自演任务</h2>
                  <span className="badge badge--jade">{report.task_count}</span>
                </div>
                <div className="worldline-stack">
                  {report.tasks.length === 0 && (
                    <EmptyState title="还没有自演任务" hint="从世界沙盘启动自演后会在这里出现任务进度。" />
                  )}
                  {report.tasks.map((task) => (
                    <article key={task.task_id}>
                      <strong>{task.task_id || "本地任务"}</strong>
                      <p className="muted tiny">
                        {task.status || "unknown"} · {task.progress?.current_round ?? 0}/
                        {task.progress?.target_round ?? 0} · {task.progress?.percent ?? 0}%
                      </p>
                      {task.latest_report_run_id && (
                        <p className="mono tiny">{task.latest_report_run_id}</p>
                      )}
                      {task.failure?.message && (
                        <p className="muted tiny">
                          中断：{task.failure.message}；最近检查点：
                          {task.failure.latest_checkpoint || "暂无"}
                        </p>
                      )}
                      {task.resume_from_checkpoint && (
                        <p className="muted tiny">
                          可从 {task.resume_from_checkpoint} 恢复自演
                        </p>
                      )}
                      {task.recovered_from?.checkpoint_id && (
                        <p className="muted tiny">
                          已从 {task.recovered_from.checkpoint_id} 接续
                        </p>
                      )}
                      {task.task_id && (
                        <div className="worldline-row-actions">
                          <button
                            className="btn btn--ghost tiny"
                            disabled={taskBusy === task.task_id}
                            onClick={() => updateTask(task.task_id || "", "pause")}
                          >
                            暂停
                          </button>
                          <button
                            className="btn btn--ghost tiny"
                            disabled={taskBusy === task.task_id}
                            onClick={() => updateTask(task.task_id || "", "resume")}
                          >
                            恢复
                          </button>
                        </div>
                      )}
                    </article>
                  ))}
                </div>
              </div>

              <div>
                <div className="worldline-section__title">
                  <h2>检查点</h2>
                  <span className="badge badge--gold">{report.checkpoint_count}</span>
                </div>
                <div className="worldline-stack">
                  {report.checkpoints.length === 0 && (
                    <EmptyState title="暂无检查点" hint="世界自演完成一轮后会生成可回放检查点。" />
                  )}
                  {report.checkpoints.map((checkpoint) => (
                    <article key={`${checkpoint.run_id}-${checkpoint.checkpoint_id}`}>
                      <strong>第 {checkpoint.round_index} 轮</strong>
                      <p>{checkpoint.stage}</p>
                      <p className="muted tiny">
                        {checkpoint.causal_debt || "因果债待定"} ·{" "}
                        {checkpoint.consequence_state?.status ?? "none"}
                      </p>
                      <button
                        className="btn btn--ghost tiny"
                        onClick={() =>
                          navigate({
                            name: "checkpoint",
                            slug,
                            worldlineId,
                            runId: checkpoint.run_id,
                            checkpointId: checkpoint.checkpoint_id,
                          })
                        }
                      >
                        回放检查点
                      </button>
                    </article>
                  ))}
                </div>
              </div>
            </section>

            {latestCheckpoint && (
              <section className="worldline-section">
                <div className="worldline-section__title">
                  <h2>最近世界推进</h2>
                  <span className="badge badge--gold">{latestCheckpoint.checkpoint_id}</span>
                </div>
                <p>{latestCheckpoint.major_event}</p>
                <div className="worldline-memory-list">
                  {latestCheckpoint.who_remembered_what?.map((item, index) => (
                    <article key={`${item.character_id}-${index}`}>
                      <span>{item.character_id || "角色"}</span>
                      <strong>{item.remembered || "记住了本轮变化"}</strong>
                    </article>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}

function projectionModeLabel(mode?: string) {
  if (mode === "wild_au") return "暴走 AU";
  if (mode === "immersive") return "沉浸模式";
  return "普通世界线";
}
