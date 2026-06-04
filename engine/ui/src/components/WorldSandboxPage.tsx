import { useMemo, useState } from "react";
import { api } from "../api/client";
import type {
  SubjectiveMemoryReport,
  WorldAutopilotReport,
  WorldSandboxRunReport,
} from "../api/types";
import { navigate } from "../routing";
import { ErrorState, EmptyState } from "./common/States";
import "./worldSandbox.css";

const DEFAULT_EVENT = "老皇帝驾崩，边境军报同时传入归云斋。";

export function WorldSandboxPage({ slug }: { slug: string }) {
  const [majorEvent, setMajorEvent] = useState(DEFAULT_EVENT);
  const [report, setReport] = useState<WorldSandboxRunReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCharacterId, setSelectedCharacterId] = useState<string | null>(null);
  const [memoryReport, setMemoryReport] = useState<SubjectiveMemoryReport | null>(null);
  const [memoryLoading, setMemoryLoading] = useState(false);
  const [memoryError, setMemoryError] = useState<string | null>(null);
  const [autopilotEvent, setAutopilotEvent] = useState(
    "老皇帝驾崩，边境军报传来。",
  );
  const [autopilotObjective, setAutopilotObjective] = useState("rounds");
  const [autopilotStopEvent, setAutopilotStopEvent] = useState("风鸣铃");
  const [autopilotTimeLimit, setAutopilotTimeLimit] = useState("三日后");
  const [autopilotRounds, setAutopilotRounds] = useState(3);
  const [autopilotLoading, setAutopilotLoading] = useState(false);
  const [autopilotError, setAutopilotError] = useState<string | null>(null);
  const [autopilotReport, setAutopilotReport] = useState<WorldAutopilotReport | null>(null);

  const round = report?.rounds[0] ?? null;
  const canRun = majorEvent.trim().length > 0 && !loading;
  const actionCount = round?.character_actions.length ?? 0;
  const deltaItems = useMemo(() => {
    if (!round) return [];
    return [
      ["锚点压力", round.world_state_delta.anchor_pressure],
      ["因果债", round.world_state_delta.causal_debt],
      ["资源变化", round.world_state_delta.resource_changes.join("；")],
      ["秘密流动", round.world_state_delta.secret_changes.join("；")],
    ];
  }, [round]);

  async function runRound() {
    if (!majorEvent.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const next = await api.runSandboxRound(slug, {
        major_event: majorEvent.trim(),
        worldline_id: "main",
      });
      setReport(next);
      const firstCharacter = next.rounds[0]?.character_actions[0]?.character_id;
      if (firstCharacter) {
        setSelectedCharacterId(firstCharacter);
        await loadMemory(firstCharacter, next.worldline_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function loadMemory(characterId: string, worldlineId = report?.worldline_id ?? "main") {
    setSelectedCharacterId(characterId);
    setMemoryLoading(true);
    setMemoryError(null);
    try {
      const next = await api.getSubjectiveMemory(slug, worldlineId, characterId);
      setMemoryReport(next);
    } catch (err) {
      setMemoryError(err instanceof Error ? err.message : String(err));
    } finally {
      setMemoryLoading(false);
    }
  }

  async function runAutopilot() {
    if (!autopilotEvent.trim()) return;
    setAutopilotLoading(true);
    setAutopilotError(null);
    try {
      setAutopilotReport(
        await api.runWorldAutopilot(slug, {
          seed_event: autopilotEvent.trim(),
          objective_type: autopilotObjective,
          stop_event:
            autopilotObjective === "event" ? autopilotStopEvent.trim() : undefined,
          time_limit:
            autopilotObjective === "time" ? autopilotTimeLimit.trim() : undefined,
          round_limit: autopilotRounds,
          worldline_id: "main",
        }),
      );
    } catch (err) {
      setAutopilotError(err instanceof Error ? err.message : String(err));
    } finally {
      setAutopilotLoading(false);
    }
  }

  return (
    <div className="sandbox-page">
      <header className="sandbox-hero">
        <div>
          <p className="sandbox-hero__eyebrow muted">世界内部卷宗 · 世界沙盘</p>
          <h1>让世界先动一轮</h1>
          <p className="muted">
            输入一个大事件，观察角色各自的意图、行动、冲突、信息传播和世界状态变化。
          </p>
        </div>
        <div className="sandbox-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "tianming", slug })}
          >
            查看天命书
          </button>
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "lens", slug })}
          >
            多视角卷
          </button>
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "workspace", slug })}
          >
            返回正史卷
          </button>
        </div>
      </header>

      <div className="sandbox-layout">
        <aside className="sandbox-control">
          <div className="sandbox-panel">
            <h2>本轮大事件</h2>
            <textarea
              value={majorEvent}
              onChange={(event) => setMajorEvent(event.target.value)}
              rows={7}
              placeholder="写下世界刚刚发生的事"
            />
            <button className="btn btn--primary" disabled={!canRun} onClick={runRound}>
              {loading ? "沙盘推演中…" : "运行一轮"}
            </button>
            <p className="muted tiny">
              第一版只写入沙盘轮次，不覆盖章节、事件、状态快照或既有世界线。
            </p>
          </div>

          {report && (
            <div className="sandbox-panel sandbox-proof">
              <h2>本地产物</h2>
              <dl>
                <div>
                  <dt>运行</dt>
                  <dd className="mono">{report.run_id}</dd>
                </div>
                <div>
                  <dt>轮次</dt>
                  <dd>{report.round_count}</dd>
                </div>
                <div>
                  <dt>角色行动</dt>
                  <dd>{actionCount}</dd>
                </div>
                <div>
                  <dt>写入</dt>
                  <dd>{report.artifacts.sandbox_rounds}</dd>
                </div>
                <div>
                  <dt>记忆</dt>
                  <dd>{report.summary.subjective_memory_entries_written} 条</dd>
                </div>
              </dl>
            </div>
          )}

          <div className="sandbox-panel sandbox-autopilot">
            <h2>世界自演</h2>
            <textarea
              value={autopilotEvent}
              onChange={(event) => setAutopilotEvent(event.target.value)}
              rows={4}
              placeholder="写下世界自演的起点事件"
            />
            <label>
              <span className="muted tiny">自演目标</span>
              <select
                value={autopilotObjective}
                onChange={(event) => setAutopilotObjective(event.target.value)}
              >
                <option value="rounds">运行到轮数</option>
                <option value="event">运行到事件</option>
                <option value="time">运行到时间</option>
                <option value="anchor_change">运行到锚点变化</option>
              </select>
            </label>
            {autopilotObjective === "event" && (
              <label>
                <span className="muted tiny">目标事件</span>
                <input
                  value={autopilotStopEvent}
                  onChange={(event) => setAutopilotStopEvent(event.target.value)}
                />
              </label>
            )}
            {autopilotObjective === "time" && (
              <label>
                <span className="muted tiny">目标时间</span>
                <input
                  value={autopilotTimeLimit}
                  onChange={(event) => setAutopilotTimeLimit(event.target.value)}
                />
              </label>
            )}
            <label>
              <span className="muted tiny">自演轮数</span>
              <input
                type="number"
                min={1}
                max={10}
                value={autopilotRounds}
                onChange={(event) => setAutopilotRounds(Number(event.target.value) || 1)}
              />
            </label>
            <button
              className="btn btn--primary"
              disabled={autopilotLoading || !autopilotEvent.trim()}
              onClick={runAutopilot}
            >
              {autopilotLoading ? "世界自演中…" : "启动自演"}
            </button>
            <p className="muted tiny">
              自演会连续运行沙盘轮次，写入检查点和 autopilot_report.json。
            </p>
          </div>
        </aside>

        <main className="sandbox-main">
          {error && <ErrorState message={error} onRetry={runRound} />}
          {autopilotError && <ErrorState message={autopilotError} onRetry={runAutopilot} />}
          {autopilotReport && (
            <section className="sandbox-section sandbox-autopilot-report">
              <div className="sandbox-section__title">
                <h2>昨夜世界演化报告</h2>
                <span className="badge badge--gold">
                  {autopilotReport.rounds_completed} 个检查点
                </span>
              </div>
              <p>{autopilotReport.final_world_stage.summary}</p>
              <p className="muted tiny">
                {autopilotReport.stop_reason} · {autopilotReport.artifact}
              </p>
              <div className="sandbox-checkpoints">
                {autopilotReport.checkpoints.map((checkpoint) => (
                  <article key={checkpoint.round_index}>
                    <div>
                      <strong>第 {checkpoint.round_index} 轮</strong>
                      <span className="muted tiny mono">
                        {checkpoint.sandbox_run_id}
                      </span>
                    </div>
                    <p>{checkpoint.stage}</p>
                    <p className="muted tiny">{checkpoint.causal_debt}</p>
                  </article>
                ))}
              </div>
            </section>
          )}
          {!error && !round && !autopilotReport && (
            <EmptyState
              title="沙盘尚未运行"
              hint="写下一个大事件，先看角色会如何各自行动。"
            />
          )}
          {!error && round && (
            <>
              <section className="sandbox-section">
                <div className="sandbox-section__title">
                  <h2>角色行动链</h2>
                  <span className="badge badge--jade">
                    第 {round.round_index} 轮
                  </span>
                </div>
                <div className="sandbox-actions">
                  {round.character_actions.map((item) => (
                    <article className="sandbox-action" key={item.character_id}>
                      <div className="sandbox-action__head">
                        <span className="sandbox-action__seal" aria-hidden>
                          {item.character_name.slice(0, 1)}
                        </span>
                        <div>
                          <h3>{item.character_name}</h3>
                          <p className="muted tiny">{item.narrative_role}</p>
                        </div>
                        <span className="badge badge--gold">{item.stance}</span>
                      </div>
                      <p className="sandbox-action__line">{item.intent}</p>
                      <p>{item.visible_action ?? item.action}</p>
                      {item.true_intent && (
                        <p className="muted tiny">真实意图：{item.true_intent}</p>
                      )}
                      <p className="muted tiny">{item.reason}</p>
                      {item.decision_inputs && (
                        <div className="sandbox-action__decision-block">
                          <span>决策输入</span>
                          <dl className="sandbox-action__decision">
                            <div>
                              <dt>欲望</dt>
                              <dd>{item.decision_inputs.desire}</dd>
                            </div>
                            <div>
                              <dt>恐惧</dt>
                              <dd>{item.decision_inputs.fear}</dd>
                            </div>
                            <div>
                              <dt>上一轮记忆</dt>
                              <dd>
                                {item.decision_inputs.previous_memory_belief ||
                                  "暂无上一轮主观认知"}
                              </dd>
                            </div>
                            <div>
                              <dt>天命压力</dt>
                              <dd>{item.decision_inputs.tianming_pressure}</dd>
                            </div>
                          </dl>
                        </div>
                      )}
                      {(item.expected_outcome || item.risk || item.action_outcome) && (
                        <div className="sandbox-action__memory">
                          <span>预期与风险</span>
                          <strong>
                            {item.expected_outcome ?? "继续观察"}；风险：
                            {item.risk ?? "未记录"}
                          </strong>
                          {item.action_outcome?.reason && (
                            <p className="muted tiny">
                              结果：{item.action_outcome.status ?? "pending"} ·{" "}
                              {item.action_outcome.reason}
                            </p>
                          )}
                        </div>
                      )}
                      <div className="sandbox-action__memory">
                        <span>将写入记忆种子</span>
                        <strong>{item.memory_seed?.inferred?.[0] ?? "形成新的判断"}</strong>
                      </div>
                      <p className="muted tiny">
                        {item.memory_influence ?? item.previous_subjective_memory}
                      </p>
                      <button
                        className={`btn btn--ghost sandbox-action__button ${
                          selectedCharacterId === item.character_id ? "is-active" : ""
                        }`}
                        onClick={() => loadMemory(item.character_id, round.worldline_id)}
                      >
                        查看个人记忆
                      </button>
                    </article>
                  ))}
                </div>
              </section>

              <section className="sandbox-section">
                <div className="sandbox-section__title">
                  <h2>角色个人卷雏形</h2>
                  <span className="badge badge--jade">
                    {memoryReport?.entry_count ?? 0} 条主观记忆
                  </span>
                </div>
                {memoryLoading && <p className="muted">正在读取角色记忆…</p>}
                {memoryError && (
                  <ErrorState
                    message={memoryError}
                    onRetry={() => {
                      if (selectedCharacterId) loadMemory(selectedCharacterId, round.worldline_id);
                    }}
                  />
                )}
                {!memoryLoading && !memoryError && !memoryReport && (
                  <EmptyState
                    title="尚未选择角色"
                    hint="点击角色行动卡片下方的「查看个人记忆」。"
                  />
                )}
                {!memoryLoading && !memoryError && memoryReport && (
                  <div className="sandbox-memory">
                    <p className="muted tiny mono">{memoryReport.artifact}</p>
                    {memoryReport.entries.map((entry) => (
                      <article key={`${entry.source_run_id}-${entry.source_round_index}`}>
                        <div>
                          <strong>{entry.character_name}</strong>
                          <span className="muted tiny">
                            第 {entry.source_round_index} 轮 · {entry.source_major_event}
                          </span>
                        </div>
                        <p>{entry.new_belief}</p>
                        <dl>
                          {entry.perceived_event && (
                            <div className="sandbox-memory__wide">
                              <dt>主观感知</dt>
                              <dd>{entry.perceived_event}</dd>
                            </div>
                          )}
                          {entry.inner_thought && (
                            <div className="sandbox-memory__wide">
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
                          {entry.secret_visibility && (
                            <div>
                              <dt>秘密可见性</dt>
                              <dd>{entry.secret_visibility}</dd>
                            </div>
                          )}
                          <div>
                            <dt>看到</dt>
                            <dd>{entry.saw.join("；")}</dd>
                          </div>
                          <div>
                            <dt>做了</dt>
                            <dd>{entry.did.join("；")}</dd>
                          </div>
                          <div>
                            <dt>情绪</dt>
                            <dd>{entry.emotion_delta}</dd>
                          </div>
                          <div>
                            <dt>信任</dt>
                            <dd>{entry.trust_delta}</dd>
                          </div>
                          <div>
                            <dt>异常感</dt>
                            <dd>
                              {entry.anomaly_delta}
                              {typeof entry.anomaly_weight === "number"
                                ? `；权重 ${entry.anomaly_weight}`
                                : ""}
                            </dd>
                          </div>
                        </dl>
                      </article>
                    ))}
                  </div>
                )}
              </section>

              <section className="sandbox-section sandbox-grid">
                <div>
                  <div className="sandbox-section__title">
                    <h2>冲突与信息传播</h2>
                  </div>
                  <div className="sandbox-list">
                    {round.conflicts.map((item) => (
                      <div className="sandbox-list__item" key={item.id}>
                        <strong>{item.title}</strong>
                        <p className="muted tiny">{item.cause}</p>
                      </div>
                    ))}
                    {round.information_flow.map((item) => (
                      <div className="sandbox-list__item" key={`${item.to}-${item.distortion}`}>
                        <strong>{item.to}</strong>
                        <p className="muted tiny">
                          以「{item.distortion}」理解：{item.content}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="sandbox-section__title">
                    <h2>世界状态变化</h2>
                  </div>
                  <div className="sandbox-delta">
                    {deltaItems.map(([label, value]) => (
                      <div key={label}>
                        <span>{label}</span>
                        <strong>{value}</strong>
                      </div>
                    ))}
                  </div>
                </div>
              </section>

              <section className="sandbox-section">
                <div className="sandbox-section__title">
                  <h2>后续剧情可能性</h2>
                </div>
                <div className="sandbox-possibilities">
                  {round.next_story_possibilities.map((item) => (
                    <article key={item.id}>
                      <h3>{item.title}</h3>
                      <p className="muted">{item.brief}</p>
                    </article>
                  ))}
                </div>
              </section>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
