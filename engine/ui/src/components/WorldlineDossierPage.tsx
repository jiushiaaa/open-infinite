import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { WorldlineDossierReport } from "../api/types";
import { navigate } from "../routing";
import { EmptyState, ErrorState } from "./common/States";
import { WorldRunway } from "./WorldRunway";
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
  const latestTask = report?.tasks[0];
  const branchStatus = state?.branch_state?.continuation_status ?? state?.status ?? "new";
  const causalDebt = `${causalDebtLevelLabel(state?.causal_debt?.level)} / ${
    state?.causal_debt?.score ?? 0
  }`;
  const nextRoundReads = state?.branch_state?.next_round_reads ?? [];
  const commandTitle = latestCheckpoint
    ? "从最近检查点续读世界线"
    : latestTask
      ? "等待自演把世界推向下一轮"
      : "把这条世界线交回沙盘";
  const commandHint = latestCheckpoint
    ? "这条世界线已经留下可回放节点；先看最近一轮谁记住了什么，再进入连续阅读或继续沙盘。"
    : latestTask
      ? "自演任务已经登记；先看任务状态，再决定暂停、恢复或回到沙盘继续推进。"
      : "这条世界线还缺少可读检查点；下一步应先运行沙盘，让角色行动和代偿状态继续发酵。";
  const commandSteps = [
    {
      label: "承接",
      title: "确认分支状态",
      detail: branchStatus,
      active: true,
      done: !!report,
    },
    {
      label: "代偿",
      title: "看世界如何补偿",
      detail: consequenceDomains.length
        ? `${consequenceDomains.length} 个世界域正在承压`
        : "地点、资源、伤势、舆论、势力和环境等待显形。",
      active: false,
      done: consequenceDomains.length > 0,
    },
    {
      label: "检查点",
      title: "回放最近变化",
      detail: latestCheckpoint
        ? latestCheckpoint.major_event
        : "世界自演完成一轮后会出现可回放节点。",
      active: !!latestCheckpoint,
      done: !!latestCheckpoint,
    },
    {
      label: "阅读",
      title: "进入连续正文",
      detail: latestCheckpoint
        ? `${report?.checkpoint_count ?? 0} 个检查点可回读`
        : "先运行沙盘，再进入卷宗阅读。",
      active: false,
      done: !!latestCheckpoint,
    },
  ];
  const goToLatestCheckpoint = () => {
    if (!latestCheckpoint) {
      navigate({ name: "sandbox", slug });
      return;
    }
    navigate({
      name: "checkpoint",
      slug,
      worldlineId,
      runId: latestCheckpoint.run_id,
      checkpointId: latestCheckpoint.checkpoint_id,
    });
  };
  const scrollToWorldlineItem = (selector: string) => {
    document.querySelector(selector)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  const rememberedCount = latestCheckpoint?.who_remembered_what?.length ?? 0;
  const continuityItems = [
    {
      label: "角色记忆",
      title: rememberedCount ? `${rememberedCount} 个角色留下主观记忆` : "等待角色写入主观记忆",
      detail: rememberedCount
        ? latestCheckpoint?.who_remembered_what?.[0]?.remembered || "最近检查点已记录角色记忆。"
        : nextRoundReads.join("；") || "下一轮沙盘会把干预、因果债和角色行动写入个人卷。",
      action: "读长线卷",
      onClick: () => navigate({ name: "longlineReading", slug, worldlineId }),
    },
    {
      label: "因果代偿",
      title: consequenceDomains.length
        ? `${consequenceDomains.length} 个世界域正在承压`
        : "代偿尚未显形",
      detail: state?.consequence_state?.next_round_hint || state?.consequence_state?.summary ||
        "继续运行后，地点、资源、舆论、势力和环境会把干预后果具体化。",
      action: "看代偿",
      onClick: () => scrollToWorldlineItem(".worldline-consequence-section"),
    },
    {
      label: "检查点",
      title: latestCheckpoint ? `第 ${latestCheckpoint.round_index} 轮可回放` : "还没有可回放检查点",
      detail: latestCheckpoint?.major_event || "先让世界自演完成一轮，再回看角色如何误读和记住变化。",
      action: latestCheckpoint ? "回放检查点" : "继续沙盘",
      onClick: goToLatestCheckpoint,
    },
    {
      label: "下一轮入口",
      title: latestTask ? "自演任务正在承接" : "把世界线交回沙盘",
      detail: latestTask
        ? `${latestTask.status || "unknown"} · ${latestTask.progress?.current_round ?? 0}/${
            latestTask.progress?.target_round ?? 0
          }`
        : nextRoundReads.join("；") || "从这里继续运行，让世界状态进入下一章前的行动轮。",
      action: latestTask ? "看任务" : "继续沙盘",
      onClick: () =>
        latestTask
          ? scrollToWorldlineItem(".worldline-task-section")
          : navigate({ name: "sandbox", slug }),
    },
  ];

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
      </header>

      {!loading && !error && report && (
        <section className="worldline-mobile-guide" aria-label="世界线移动端快速导读">
          <div>
            <p className="muted tiny">这条世界线现在怎么走</p>
            <strong>{commandTitle}</strong>
          </div>
          <div className="worldline-mobile-guide__actions">
            <button className="btn btn--primary" onClick={goToLatestCheckpoint}>
              {latestCheckpoint ? "回放" : "沙盘"}
            </button>
            <button
              className="btn btn--ghost"
              onClick={() => scrollToWorldlineItem(".worldline-consequence-section")}
            >
              看代偿
            </button>
            <button
              className="btn btn--ghost"
              onClick={() => scrollToWorldlineItem(".worldline-task-section")}
            >
              看任务
            </button>
            <button
              className="btn btn--ghost"
              onClick={() => navigate({ name: "longlineReading", slug, worldlineId })}
            >
              长线卷
            </button>
          </div>
        </section>
      )}

      {!loading && !error && report && (
        <section className="worldline-command" aria-label="世界线工作流总览">
          <div className="worldline-command__lead">
            <p className="muted worldline-command__eyebrow">当前下一步</p>
            <h2>{commandTitle}</h2>
            <p className="muted">{commandHint}</p>
            <div className="worldline-command__meta">
              <span className="badge badge--jade">{branchStatus}</span>
              <span className="badge">{report.worldline_id}</span>
              <span className="badge badge--gold">因果债 {causalDebt}</span>
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
            {latestCheckpoint && (
              <button
                className="btn btn--primary"
                onClick={goToLatestCheckpoint}
              >
                回放最近检查点
              </button>
            )}
            {!latestCheckpoint && (
              <button
                className="btn btn--primary"
                onClick={() => navigate({ name: "sandbox", slug })}
              >
                继续沙盘
              </button>
            )}
            <button
              className="btn btn--ghost"
              onClick={() => navigate({ name: "dossierReading", slug, worldlineId })}
            >
              卷宗阅读
            </button>
            <button
              className="btn btn--ghost"
              onClick={() => navigate({ name: "longlineReading", slug, worldlineId })}
            >
              长线卷
            </button>
            {latestCheckpoint && (
              <button
                className="btn btn--ghost"
                onClick={() => navigate({ name: "sandbox", slug })}
              >
                继续沙盘
              </button>
            )}
            <button className="btn btn--ghost" onClick={() => navigate({ name: "lens", slug })}>
              多视角
            </button>
          </div>

          <div className="worldline-command__proof" aria-label="世界线摘要">
            <div>
              <span className="muted tiny">检查点</span>
              <strong>{report.checkpoint_count}</strong>
            </div>
            <div>
              <span className="muted tiny">自演任务</span>
              <strong>{report.task_count}</strong>
            </div>
            <div>
              <span className="muted tiny">代偿域</span>
              <strong>{consequenceDomains.length || "待显形"}</strong>
            </div>
            <p>
              {state?.source_intervention?.content ||
                nextRoundReads.join("；") ||
                "这条世界线等待下一轮沙盘写入新的承接材料。"}
            </p>
          </div>
        </section>
      )}

      {!loading && !error && report && (
        <section className="worldline-continuity-rail" aria-label="世界状态接力台">
          <div className="worldline-continuity-rail__intro">
            <p className="muted tiny">状态接力</p>
            <h2>这条世界线会这样进入下一轮</h2>
            <p className="muted">
              先确认谁会记得、世界哪里在代偿、最近检查点能否回放，再决定继续沙盘或进入长线阅读。
            </p>
          </div>
          {continuityItems.map((item) => (
            <article key={item.label}>
              <span>{item.label}</span>
              <strong>{item.title}</strong>
              <p>{item.detail}</p>
              <button className="btn btn--ghost tiny" onClick={item.onClick}>
                {item.action}
              </button>
            </article>
          ))}
        </section>
      )}

      <WorldRunway
        eyebrow="世界线导览"
        title="先看承接状态，再决定读、回放或继续运行"
        summary="世界线档案负责解释这条分支为什么还在变：来源干预、天命审计、因果债、自演任务和检查点都汇总在这里。"
        meta={
          <>
            <span className="badge badge--jade">
              {state?.branch_state?.continuation_status ?? state?.status ?? "new"}
            </span>
            <span className="badge">{worldlineId}</span>
            <span className="badge badge--gold">检查点 {report?.checkpoint_count ?? 0}</span>
          </>
        }
        steps={[
          {
            label: "看状态",
            detail: "确认干预来源、天命审计和因果债。",
            active: true,
          },
          {
            label: "回放检查点",
            detail: "从最近一轮看谁记住了什么。",
            onClick: latestCheckpoint
              ? () =>
                  navigate({
                    name: "checkpoint",
                    slug,
                    worldlineId,
                    runId: latestCheckpoint.run_id,
                    checkpointId: latestCheckpoint.checkpoint_id,
                  })
              : undefined,
          },
          {
            label: "进入阅读",
            detail: "把世界状态切回连续正文和多视角。",
            onClick: () => navigate({ name: "dossierReading", slug, worldlineId }),
          },
        ]}
        actions={[
          {
            label: "卷宗阅读",
            detail: "按正文、角色卷和事件多视角继续读",
            primary: true,
            onClick: () => navigate({ name: "dossierReading", slug, worldlineId }),
          },
          {
            label: "长线卷",
            detail: "追踪误会、记忆和势力压力如何跨事件发酵",
            onClick: () => navigate({ name: "longlineReading", slug, worldlineId }),
          },
          {
            label: "继续沙盘",
            detail: "把这条分支交回角色行动",
            onClick: () => navigate({ name: "sandbox", slug }),
          },
          {
            label: "作者采纳台",
            detail: "整理成下一章写作材料",
            onClick: () => navigate({ name: "author", slug }),
          },
        ]}
      />

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

            <section className="worldline-section worldline-actions-section">
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

            <section className="worldline-section worldline-consequence-section">
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

            <section className="worldline-section worldline-grid worldline-task-section">
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

function causalDebtLevelLabel(level?: string) {
  if (level === "low") return "低";
  if (level === "medium") return "中";
  if (level === "high") return "高";
  if (level === "critical") return "极高";
  return "未知";
}
