import { useEffect, useState } from "react";
import { api } from "../api/client";
import type {
  NarrativeCompensationReport,
  TianmingBook,
  TianmingInterventionCompileReport,
} from "../api/types";
import { navigate } from "../routing";
import { EmptyState, ErrorState, Loading } from "./common/States";
import "./tianming.css";

export function TianmingPage({ slug }: { slug: string }) {
  const [book, setBook] = useState<TianmingBook | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [interventionText, setInterventionText] = useState(
    "给赵轩一封来自未来的大纲信，提醒他风鸣铃会引来新的代价。",
  );
  const [target, setTarget] = useState("");
  const [worldlineId, setWorldlineId] = useState("reader_au");
  const [compileBusy, setCompileBusy] = useState(false);
  const [compileError, setCompileError] = useState<string | null>(null);
  const [compileReport, setCompileReport] =
    useState<TianmingInterventionCompileReport | null>(null);
  const [compensationEvent, setCompensationEvent] = useState(
    "赵轩拒绝追查风鸣铃，并试图离开云城。",
  );
  const [compensationBusy, setCompensationBusy] = useState(false);
  const [compensationError, setCompensationError] = useState<string | null>(null);
  const [compensationReport, setCompensationReport] =
    useState<NarrativeCompensationReport | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .getTianmingBook(slug)
      .then((next) => {
        if (!cancelled) setBook(next);
      })
      .catch((err) => {
        if (!cancelled) {
          setBook(null);
          const message = err instanceof Error ? err.message : String(err);
          if (!message.includes("404")) setError(message);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  async function generate() {
    setBusy(true);
    setError(null);
    try {
      setBook(await api.generateTianmingBook(slug));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
      setLoading(false);
    }
  }

  async function confirm() {
    setBusy(true);
    setError(null);
    try {
      setBook(await api.confirmTianmingBook(slug));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function compileIntervention() {
    if (!interventionText.trim()) return;
    setCompileBusy(true);
    setCompileError(null);
    try {
      setCompileReport(
        await api.compileTianmingIntervention(slug, {
          content: interventionText.trim(),
          target: target.trim() || undefined,
          worldline_id: worldlineId.trim() || "main",
        }),
      );
    } catch (err) {
      setCompileError(err instanceof Error ? err.message : String(err));
    } finally {
      setCompileBusy(false);
    }
  }

  async function runCompensation() {
    if (!compensationEvent.trim()) return;
    setCompensationBusy(true);
    setCompensationError(null);
    try {
      setCompensationReport(
        await api.runNarrativeCompensation(slug, {
          trigger_event: compensationEvent.trim(),
          worldline_id: "main",
        }),
      );
    } catch (err) {
      setCompensationError(err instanceof Error ? err.message : String(err));
    } finally {
      setCompensationBusy(false);
    }
  }

  return (
    <div className="tianming-page">
      <header className="tianming-hero">
        <div>
          <p className="muted tianming-hero__eyebrow">世界内部卷宗 · 天命书</p>
          <h1>给这个世界立一卷天命</h1>
          <p className="muted">
            天命书承载叙事吸引子、题材约束、主锚点、合约压力和候选天命承载者。
            普通干预只能制造分叉和因果债，不能永久改写它。
          </p>
        </div>
        <div className="tianming-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "sandbox", slug })}
          >
            去世界沙盘
          </button>
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "anchor", slug })}
          >
            世界锚定
          </button>
        </div>
      </header>

      {loading && <Loading label="正在查找天命书…" />}
      {error && <ErrorState message={error} onRetry={generate} />}
      {!loading && !error && !book && (
        <EmptyState
          title="还没有天命书"
          hint="生成一份本地草案，确认后它会成为沙盘和干预编译的世界宪法。"
        />
      )}
      {!loading && !error && !book && (
        <button className="btn btn--primary" disabled={busy} onClick={generate}>
          {busy ? "生成中…" : "生成天命书草案"}
        </button>
      )}

      {book && (
        <main className="tianming-layout">
          <section className="tianming-panel tianming-status">
            <div>
              <p className="muted tiny">状态</p>
              <h2>{book.status === "confirmed" ? "已确认" : "待确认"}</h2>
            </div>
            <dl>
              <div>
                <dt>产物</dt>
                <dd className="mono">{book.artifact}</dd>
              </div>
              <div>
                <dt>锚点</dt>
                <dd>{book.anchor_status.current_anchor_name || "待定"}</dd>
              </div>
              <div>
                <dt>合约压力</dt>
                <dd>{book.contract_pressure.level}</dd>
              </div>
            </dl>
            {book.requires_confirmation && (
              <button className="btn btn--primary" disabled={busy} onClick={confirm}>
                {busy ? "确认中…" : "轻量确认"}
              </button>
            )}
          </section>

          <section className="tianming-panel">
            <h2>叙事吸引子</h2>
            <div className="tianming-list">
              {book.narrative_attractors.map((item) => (
                <article key={item.id}>
                  <div className="tianming-row">
                    <strong>{item.title}</strong>
                    {typeof item.weight === "number" && (
                      <span className="badge badge--gold">权重 {item.weight}</span>
                    )}
                  </div>
                  <p>{item.pull}</p>
                  <span className="muted tiny">
                    类别 {attractorCategoryLabel(item.category)} · {item.source}
                  </span>
                </article>
              ))}
            </div>
          </section>

          {book.anchor_status.anchors?.length ? (
            <section className="tianming-panel">
              <h2>多锚点结构</h2>
              <div className="tianming-anchors">
                {book.anchor_status.anchors.map((item) => (
                  <article key={item.id}>
                    <div className="tianming-row">
                      <strong>{item.name}</strong>
                      <span className="badge badge--jade">
                        {anchorTypeLabel(item.type)} · 稳定 {item.stability}
                      </span>
                    </div>
                    <p>{item.pressure}</p>
                    <span className="muted tiny">{anchorStatusLabel(item.status)}</span>
                  </article>
                ))}
              </div>
            </section>
          ) : null}

          {book.contract_pressure.pressure_tiers?.length ? (
            <section className="tianming-panel">
              <h2>合约压力四档</h2>
              <div className="tianming-pressure">
                {book.contract_pressure.pressure_tiers.map((item) => (
                  <article className={item.active ? "is-active" : ""} key={item.id}>
                    <strong>{item.label}</strong>
                    <p>{item.drivers.join("；")}</p>
                    <span className="muted tiny">阈值 {item.threshold}</span>
                  </article>
                ))}
              </div>
            </section>
          ) : null}

          <section className="tianming-panel">
            <h2>题材与世界约束</h2>
            <div className="tianming-list">
              {book.genre_constraints.map((item) => (
                <article key={item.id}>
                  <strong>{item.name}</strong>
                  <p>{item.rule}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="tianming-panel">
            <h2>候选天命承载者</h2>
            <div className="tianming-candidates">
              {book.replacement_anchor_candidates.map((item) => (
                <article key={item.character_id}>
                  <div>
                    <strong>{item.character_name}</strong>
                    <span className="badge badge--gold">契合 {item.anchor_fit}</span>
                  </div>
                  <p>{item.reason}</p>
                  <p className="muted tiny">欲望：{item.desire}</p>
                  <p className="muted tiny">风险：{item.risk}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="tianming-panel tianming-policy">
            <h2>干预边界</h2>
            <p>{book.mutation_policy.ordinary_intervention}</p>
            <p>{book.mutation_policy.l4_l5_intervention}</p>
            {book.confirmation && <p className="muted tiny">{book.confirmation.message}</p>}
          </section>

          <section className="tianming-panel tianming-compiler">
            <div className="tianming-compiler__head">
              <div>
                <h2>干预预编译</h2>
                <p className="muted">
                  先读取《天命书》，再判断自由干预如何投放进世界。
                </p>
              </div>
              <span className="badge badge--jade">不改写天命书</span>
            </div>
            <label>
              <span className="muted tiny">目标角色 ID</span>
              <input
                value={target}
                onChange={(event) => setTarget(event.target.value)}
                placeholder="可留空，例如 zhao_xuan"
              />
            </label>
            <label>
              <span className="muted tiny">投放世界线</span>
              <input
                value={worldlineId}
                onChange={(event) => setWorldlineId(event.target.value)}
                placeholder="例如 reader_au"
              />
            </label>
            <label>
              <span className="muted tiny">自由干预</span>
              <textarea
                value={interventionText}
                onChange={(event) => setInterventionText(event.target.value)}
                rows={4}
              />
            </label>
            <button
              className="btn btn--primary"
              disabled={compileBusy || !interventionText.trim()}
              onClick={compileIntervention}
            >
              {compileBusy ? "编译中…" : "读取天命书并编译"}
            </button>
            {compileError && <ErrorState message={compileError} onRetry={compileIntervention} />}
            {compileReport && (
              <div className="tianming-compile-result">
                <dl>
                  <div>
                    <dt>干预类型</dt>
                    <dd>{compileReport.intervention_type}</dd>
                  </div>
                  <div>
                    <dt>层级</dt>
                    <dd>{compileReport.intervention_level}</dd>
                  </div>
                  <div>
                    <dt>兼容性</dt>
                    <dd>{compileReport.compatibility.status}</dd>
                  </div>
                  <div>
                    <dt>世界线判断</dt>
                    <dd>{compileReport.worldline_judgement.kind}</dd>
                  </div>
                  <div>
                    <dt>因果债</dt>
                    <dd>
                      {compileReport.causal_debt.level} · {compileReport.causal_debt.score}
                    </dd>
                  </div>
                </dl>
                <article>
                  <strong>转译策略</strong>
                  <p>{compileReport.translation_strategy.strategy}</p>
                  <p className="muted tiny">{compileReport.translation_strategy.packaging}</p>
                </article>
                <article>
                  <strong>{compileReport.branch_axis.axis}</strong>
                  <p>{compileReport.branch_axis.question}</p>
                  <p className="muted tiny">{compileReport.audit.message}</p>
                </article>
                {compileReport.worldline_tianming_snapshot && (
                  <article>
                    <strong>世界线天命书快照</strong>
                    <p className="mono">
                      {compileReport.worldline_tianming_snapshot.artifact}
                    </p>
                    <p className="muted tiny">
                      根天命书未被覆盖；状态：
                      {compileReport.worldline_tianming_snapshot.status}
                    </p>
                  </article>
                )}
                <div className="tianming-debt">
                  {compileReport.causal_debt.spread.map((item) => (
                    <span key={item}>{item}</span>
                  ))}
                </div>
              </div>
            )}
          </section>

          <section className="tianming-panel tianming-compensation">
            <div className="tianming-compiler__head">
              <div>
                <h2>世界线代偿</h2>
                <p className="muted">
                  当主锚点死亡、摆烂或离场，世界不会抹杀角色，而会在关系、势力和环境中自然代偿。
                </p>
              </div>
              <span className="badge badge--gold">写入 tianming_delta.json</span>
            </div>
            <label>
              <span className="muted tiny">代偿触发事件</span>
              <textarea
                value={compensationEvent}
                onChange={(event) => setCompensationEvent(event.target.value)}
                rows={3}
              />
            </label>
            <button
              className="btn btn--primary"
              disabled={compensationBusy || !compensationEvent.trim()}
              onClick={runCompensation}
            >
              {compensationBusy ? "推演代偿中…" : "生成代偿 delta"}
            </button>
            {compensationError && (
              <ErrorState message={compensationError} onRetry={runCompensation} />
            )}
            {compensationReport && (
              <div className="tianming-compensation-result">
                <dl>
                  <div>
                    <dt>锚点状态</dt>
                    <dd>{compensationReport.anchor_transfer.status}</dd>
                  </div>
                  <div>
                    <dt>因果债</dt>
                    <dd>
                      {compensationReport.causal_debt_diffusion.level} ·{" "}
                      {compensationReport.causal_debt_diffusion.score}
                    </dd>
                  </div>
                  <div>
                    <dt>产物</dt>
                    <dd className="mono">{compensationReport.artifact}</dd>
                  </div>
                </dl>
                <article>
                  <strong>锚点转移</strong>
                  <p>{compensationReport.anchor_transfer.reason}</p>
                </article>
                <div className="tianming-candidates">
                  {compensationReport.replacement_anchor_candidates.slice(0, 3).map((item) => (
                    <article key={item.character_id}>
                      <div>
                        <strong>{item.character_name}</strong>
                        <span className="badge badge--jade">
                          能力 {item.ability_score} · 资源 {item.resource_score}
                        </span>
                      </div>
                      <p>{item.reason}</p>
                      <p className="muted tiny">风险：{item.risk}</p>
                    </article>
                  ))}
                </div>
                <div className="tianming-pressure">
                  {compensationReport.world_pressure_events.map((event) => (
                    <article key={event.id}>
                      <strong>{event.domain}</strong>
                      <p>{event.event}</p>
                      <span className="muted tiny">{event.evidence}</span>
                    </article>
                  ))}
                </div>
              </div>
            )}
          </section>
        </main>
      )}
    </div>
  );
}

function attractorCategoryLabel(value?: string): string {
  if (value === "open_thread") return "开放伏笔";
  if (value === "character_desire") return "角色欲望";
  if (value === "world_continuity") return "世界惯性";
  if (value === "world_trend") return "世界大势";
  if (value === "genre_promise") return "题材承诺";
  if (value === "anchor_replacement") return "锚点代偿";
  return value || "叙事牵引";
}

function anchorTypeLabel(value: string): string {
  if (value === "character") return "角色锚点";
  if (value === "faction") return "势力锚点";
  if (value === "mystery") return "谜团锚点";
  if (value === "place") return "地点锚点";
  return value;
}

function anchorStatusLabel(value: string): string {
  if (value === "active") return "正在承压";
  if (value === "latent") return "潜伏待发";
  if (value === "missing") return "缺失";
  return value;
}
