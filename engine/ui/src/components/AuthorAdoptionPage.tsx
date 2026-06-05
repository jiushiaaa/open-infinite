import { useState } from "react";
import { api } from "../api/client";
import type { AuthorAdoptionReport, AuthorChapterDraftReport } from "../api/types";
import { navigate } from "../routing";
import { EmptyState, ErrorState } from "./common/States";
import "./authorAdoption.css";

const DEFAULT_OUTLINE = "赵轩按旧大纲公开风鸣铃线索，苍澜派保持稳定。";
const DEFAULT_EMERGENCE = "赵轩选择隐瞒消息，沈冰月开始怀疑，苍澜派内部压力上升。";

const DECISIONS = [
  ["adopted", "采纳"],
  ["partial", "部分采纳"],
  ["new_branch", "另开分支"],
  ["export_brief", "导出 brief"],
] as const;

export function AuthorAdoptionPage({ slug }: { slug: string }) {
  const [sourceEvent, setSourceEvent] = useState("风鸣铃现世。");
  const [sourceRunId, setSourceRunId] = useState("");
  const [originalOutline, setOriginalOutline] = useState(DEFAULT_OUTLINE);
  const [sandboxSummary, setSandboxSummary] = useState(DEFAULT_EMERGENCE);
  const [decision, setDecision] = useState("partial");
  const [authorNote, setAuthorNote] = useState("保留隐瞒动作，但不立刻推翻苍澜派。");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<AuthorAdoptionReport | null>(null);
  const [draftLoading, setDraftLoading] = useState(false);
  const [draftError, setDraftError] = useState<string | null>(null);
  const [draft, setDraft] = useState<AuthorChapterDraftReport | null>(null);

  async function submitAdoption() {
    setLoading(true);
    setError(null);
    try {
      setReport(
        await api.recordAuthorAdoption(slug, {
          source_event: sourceEvent.trim(),
          source_run_id: sourceRunId.trim(),
          sandbox_summary: sandboxSummary.trim(),
          decision,
          original_outline: originalOutline.trim(),
          author_note: authorNote.trim(),
          worldline_id: "main",
        }),
      );
      setDraft(null);
      setDraftError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  async function generateDraft() {
    if (!report?.run_id) return;
    setDraftLoading(true);
    setDraftError(null);
    try {
      setDraft(await api.generateAuthorChapterDraft(slug, report.run_id, { mock: true }));
    } catch (err) {
      setDraftError(err instanceof Error ? err.message : String(err));
    } finally {
      setDraftLoading(false);
    }
  }

  return (
    <div className="adoption-page">
      <header className="adoption-hero">
        <div>
          <p className="adoption-hero__eyebrow muted">世界内部卷宗 · 作者采纳台</p>
          <h1>把沙盘涌现剧情纳入作者手稿</h1>
          <p className="muted">
            原大纲与世界自演结果并排校对，采纳动作只追加账本，不自动覆盖正史。
          </p>
        </div>
        <div className="adoption-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "lens", slug })}
          >
            多视角卷
          </button>
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "sandbox", slug })}
          >
            世界沙盘
          </button>
        </div>
      </header>

      <div className="adoption-layout">
        <aside className="adoption-panel">
          <h2>采纳决策</h2>
          <label>
            <span className="muted tiny">来源 run</span>
            <input
              value={sourceRunId}
              onChange={(event) => setSourceRunId(event.target.value)}
              placeholder="可留空，或填 lens_*"
            />
          </label>
          <label>
            <span className="muted tiny">来源事件</span>
            <input
              value={sourceEvent}
              onChange={(event) => setSourceEvent(event.target.value)}
            />
          </label>
          <div className="adoption-decisions">
            {DECISIONS.map(([value, label]) => (
              <button
                key={value}
                className={`btn btn--ghost ${decision === value ? "is-active" : ""}`}
                onClick={() => setDecision(value)}
              >
                {label}
              </button>
            ))}
          </div>
          <button className="btn btn--primary" disabled={loading} onClick={submitAdoption}>
            {loading ? "正在入账…" : "写入采纳台"}
          </button>
        </aside>

        <main className="adoption-main">
          {error && <ErrorState message={error} onRetry={submitAdoption} />}
          <section className="adoption-compare">
            <article>
              <h2>原大纲</h2>
              <textarea
                value={originalOutline}
                onChange={(event) => setOriginalOutline(event.target.value)}
                rows={8}
              />
            </article>
            <article>
              <h2>沙盘涌现剧情</h2>
              <textarea
                value={sandboxSummary}
                onChange={(event) => setSandboxSummary(event.target.value)}
                rows={8}
              />
            </article>
          </section>

          <section className="adoption-panel adoption-note">
            <h2>作者备注</h2>
            <textarea
              value={authorNote}
              onChange={(event) => setAuthorNote(event.target.value)}
              rows={4}
            />
          </section>

          {!error && !report && (
            <EmptyState
              title="尚未写入采纳记录"
              hint="选择采纳方式后，采纳台会追加本地账本并导出 brief。"
            />
          )}
          {!error && report && (
            <section className="adoption-result">
              <div className="adoption-result__head">
                <h2>{report.mode_label}</h2>
                <span className="badge badge--jade">{report.artifact}</span>
              </div>
              <p>{report.comparison.difference}</p>
              <dl>
                <div>
                  <dt>账本</dt>
                  <dd>{report.artifacts.ledger}</dd>
                </div>
                <div>
                  <dt>导出</dt>
                  <dd>{report.artifacts.author_adoption_brief}</dd>
                </div>
                {report.artifacts.next_chapter_brief && (
                  <div>
                    <dt>下一章</dt>
                    <dd>{report.artifacts.next_chapter_brief}</dd>
                  </div>
                )}
                <div>
                  <dt>运行</dt>
                  <dd className="mono">{report.run_id}</dd>
                </div>
              </dl>
              {report.next_chapter_brief && (
                <div className="adoption-next">
                  <h3>下一章可写方案</h3>
                  <p>{report.next_chapter_brief.opening_scene}</p>
                  <p className="muted tiny">
                    冲突焦点：{report.next_chapter_brief.conflict_focus}
                  </p>
                  <p className="muted tiny">
                    后续沙盘入口：{report.next_chapter_brief.sandbox_inputs.major_event}
                  </p>
                  <button
                    className="btn btn--primary"
                    disabled={draftLoading}
                    onClick={generateDraft}
                  >
                    {draftLoading ? "正在生成草稿…" : "生成下一章草稿"}
                  </button>
                </div>
              )}
              {report.foreshadowing_adjustments && (
                <div className="adoption-next">
                  <h3>伏笔调整</h3>
                  <ul>
                    {report.foreshadowing_adjustments.map((item) => (
                      <li key={`${item.type}-${item.text}`}>{item.text}</li>
                    ))}
                  </ul>
                </div>
              )}
              {report.reviewer_suggestions && (
                <div className="adoption-next">
                  <h3>Reviewer 建议</h3>
                  <ul>
                    {report.reviewer_suggestions.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
              {report.continuation_effect?.affects_future_sandbox && (
                <p className="muted tiny">
                  已写入 {report.continuation_effect.worldline_state_artifact}，后续沙盘会读取本次采纳结果。
                </p>
              )}
              {draftError && <ErrorState message={draftError} onRetry={generateDraft} />}
              {draft && (
                <div className="adoption-draft">
                  <div className="adoption-draft__head">
                    <h3>{draft.chapter_title}</h3>
                    <span className="badge badge--gold">{draft.artifact}</span>
                  </div>
                  <pre>{draft.chapter_text}</pre>
                  <dl>
                    <div>
                      <dt>采纳记录</dt>
                      <dd>{draft.evidence_chain.adoption_record}</dd>
                    </div>
                    <div>
                      <dt>下一章 brief</dt>
                      <dd>{draft.evidence_chain.next_chapter_brief}</dd>
                    </div>
                    <div>
                      <dt>世界线</dt>
                      <dd>{draft.evidence_chain.worldline_state_artifact}</dd>
                    </div>
                    <div>
                      <dt>导出</dt>
                      <dd>{draft.artifacts.next_chapter_markdown}</dd>
                    </div>
                  </dl>
                  <div className="adoption-draft__checks">
                    {draft.reviewer_checklist.map((item) => (
                      <span
                        key={item.item}
                        className={`badge ${item.passed ? "badge--jade" : "badge--gold"}`}
                      >
                        {item.passed ? "通过" : "待补"} · {item.item}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
