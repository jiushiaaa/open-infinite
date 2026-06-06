import { useState } from "react";
import { api } from "../api/client";
import type {
  AuthorAdoptionReport,
  AuthorChapterConfirmationReport,
  AuthorChapterDraftReport,
  AuthorChapterRewriteApplicationReport,
} from "../api/types";
import { navigate } from "../routing";
import { EmptyState, ErrorState } from "./common/States";
import { WorldRunway } from "./WorldRunway";
import "./authorAdoption.css";

const DEFAULT_OUTLINE = "赵轩按旧大纲公开风鸣铃线索，苍澜派保持稳定。";
const DEFAULT_EMERGENCE = "赵轩选择隐瞒消息，沈冰月开始怀疑，苍澜派内部压力上升。";

const DECISIONS = [
  ["adopted", "采纳"],
  ["partial", "部分采纳"],
  ["new_branch", "另开分支"],
  ["export_brief", "导出 brief"],
] as const;

function decisionLabel(value: string) {
  return DECISIONS.find(([decision]) => decision === value)?.[1] || value || "待选择";
}

function readingTrailStatusLabel(status: string) {
  return status === "ready" ? "可回读" : "部分证据";
}

function writingStanceLabel(stance?: string) {
  if (stance === "canon_candidate") return "可入正史候选";
  if (stance === "revision_required") return "需作者复核";
  if (stance === "author_branch") return "作者分支";
  return "素材留档";
}

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
  const [editedChapterText, setEditedChapterText] = useState("");
  const [selectedRewriteIds, setSelectedRewriteIds] = useState<string[]>([]);
  const [rewriteNote, setRewriteNote] = useState("采纳可直接变成下一章写作材料的局部改写。");
  const [rewriteLoading, setRewriteLoading] = useState(false);
  const [rewriteError, setRewriteError] = useState<string | null>(null);
  const [rewriteApplication, setRewriteApplication] =
    useState<AuthorChapterRewriteApplicationReport | null>(null);
  const [confirmationNote, setConfirmationNote] = useState("确认入卷，下一轮从本章余波继续。");
  const [confirmationLoading, setConfirmationLoading] = useState(false);
  const [confirmationError, setConfirmationError] = useState<string | null>(null);
  const [confirmation, setConfirmation] =
    useState<AuthorChapterConfirmationReport | null>(null);
  const [workspaceMode, setWorkspaceMode] = useState<"writing" | "review">("writing");
  const selectedRewriteCount = selectedRewriteIds.length;
  const localizedRewriteCount = draft?.revision_pack?.localized_rewrites.length ?? 0;
  const workflowStage = confirmation
    ? "confirmed"
    : draft
      ? "draft"
      : report
        ? "adopted"
        : "compare";
  const nextActionLabel = confirmation
    ? "去卷宗阅读"
    : draft && selectedRewriteCount > 0 && !rewriteApplication
      ? "先采纳选中改写"
      : draft
        ? "确认入卷"
        : report
          ? "生成下一章草稿"
          : "写入采纳台";
  const nextActionHint = confirmation
    ? "已进入正史卷与连续阅读链，可回到 main 世界线阅读。"
    : draft && selectedRewriteCount > 0 && !rewriteApplication
      ? "Reviewer 的高优先级局部改写已被勾选，先反哺修订稿会更稳。"
      : draft
        ? "正文编辑框里的内容会成为本章入卷文本。"
        : report
          ? "采纳记录已入账，下一步把 brief 变成可编辑章节。"
          : "先把原大纲与沙盘涌现差异写入采纳账本。";
  const workflowCards = [
    {
      key: "compare",
      label: "对照",
      title: "确认差异",
      detail: report ? report.comparison.difference : "比较原大纲和沙盘涌现剧情。",
      done: !!report,
      active: workflowStage === "compare",
    },
    {
      key: "adopted",
      label: "入账",
      title: "作者决策",
      detail: report
        ? `${decisionLabel(report.decision)} · ${report.artifacts.author_adoption_record}`
        : `${decisionLabel(decision)} · 不覆盖正史`,
      done: !!report,
      active: workflowStage === "adopted",
    },
    {
      key: "draft",
      label: "修订",
      title: "下一章草稿",
      detail: draft
        ? `${draft.chapter_title} · ${selectedRewriteCount}/${localizedRewriteCount} 条改写已选`
        : "生成草稿后可手改、采纳局部改写。",
      done: !!draft,
      active: workflowStage === "draft",
    },
    {
      key: "confirmed",
      label: "入卷",
      title: "确认正史",
      detail: confirmation
        ? `${confirmation.artifact} · 下一轮沙盘已可继续`
        : "定稿确认后进入阅读链和下一轮世界状态。",
      done: !!confirmation,
      active: workflowStage === "confirmed",
    },
  ];
  const scrollToPageItem = (selector: string) => {
    document.querySelector(selector)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  const openWritingDesk = () => {
    setWorkspaceMode("writing");
    window.setTimeout(() => scrollToPageItem(".adoption-layout"), 80);
  };
  const openReviewDesk = () => {
    setWorkspaceMode("review");
    window.setTimeout(() => scrollToPageItem(".adoption-main"), 80);
  };

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
      setEditedChapterText("");
      setSelectedRewriteIds([]);
      setRewriteApplication(null);
      setRewriteError(null);
      setConfirmation(null);
      setConfirmationError(null);
      setWorkspaceMode("review");
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
      const nextDraft = await api.generateAuthorChapterDraft(slug, report.run_id, { mock: true });
      setDraft(nextDraft);
      setEditedChapterText(nextDraft.chapter_text);
      setSelectedRewriteIds(
        (nextDraft.revision_pack?.localized_rewrites ?? [])
          .filter((item) => item.priority === "blocking" || item.priority === "high")
          .map((item) => item.id),
      );
      setRewriteApplication(null);
      setRewriteError(null);
      setConfirmation(null);
      setConfirmationError(null);
      setWorkspaceMode("review");
    } catch (err) {
      setDraftError(err instanceof Error ? err.message : String(err));
    } finally {
      setDraftLoading(false);
    }
  }

  function toggleRewrite(id: string) {
    setSelectedRewriteIds((current) =>
      current.includes(id) ? current.filter((item) => item !== id) : [...current, id],
    );
    setRewriteApplication(null);
    setConfirmation(null);
  }

  async function applySelectedRewrites() {
    if (!report?.run_id || !draft || selectedRewriteIds.length === 0) return;
    setRewriteLoading(true);
    setRewriteError(null);
    try {
      const application = await api.applyAuthorChapterRewrites(slug, report.run_id, {
        rewrite_ids: selectedRewriteIds,
        author_note: rewriteNote.trim(),
      });
      setRewriteApplication(application);
      setEditedChapterText(
        application.edited_final_chapter?.final_chapter_text ||
          application.revised_chapter_text,
      );
      setConfirmation(null);
      setConfirmationError(null);
      setWorkspaceMode("review");
    } catch (err) {
      setRewriteError(err instanceof Error ? err.message : String(err));
    } finally {
      setRewriteLoading(false);
    }
  }

  async function confirmChapter() {
    if (!report?.run_id || !draft) return;
    setConfirmationLoading(true);
    setConfirmationError(null);
    try {
      const autoFinalText =
        rewriteApplication?.edited_final_chapter?.final_chapter_text.trim() || "";
      const editedText = editedChapterText.trim();
      const request =
        autoFinalText && editedText === autoFinalText
          ? { author_note: confirmationNote.trim() }
          : {
              edited_chapter_text: editedText,
              author_note: confirmationNote.trim(),
            };
      setConfirmation(
        await api.confirmAuthorChapterEntry(slug, report.run_id, request),
      );
      setWorkspaceMode("review");
    } catch (err) {
      setConfirmationError(err instanceof Error ? err.message : String(err));
    } finally {
      setConfirmationLoading(false);
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
      </header>

      <section className="adoption-command" aria-label="作者采纳工作流总览">
        <div className="adoption-command__lead">
          <p className="adoption-command__eyebrow muted">当前下一步</p>
          <h2>{nextActionLabel}</h2>
          <p className="muted">{nextActionHint}</p>
          <div className="adoption-command__meta">
            <span className="badge badge--jade">世界线 main</span>
            <span className="badge">{decisionLabel(report?.decision || decision)}</span>
            {report?.run_id && <span className="badge badge--gold">{report.run_id}</span>}
          </div>
          <div className="adoption-desk-switch" aria-label="作者工作台模式">
            <button
              type="button"
              className={workspaceMode === "writing" ? "is-active" : ""}
              onClick={openWritingDesk}
            >
              写作台
            </button>
            <button
              type="button"
              className={workspaceMode === "review" ? "is-active" : ""}
              disabled={!report}
              onClick={openReviewDesk}
            >
              审稿台
            </button>
          </div>
        </div>

        <div className="adoption-command__steps">
          {workflowCards.map((item, index) => (
            <article
              className={`adoption-command__step ${
                item.active ? "is-active" : item.done ? "is-done" : ""
              }`}
              key={item.key}
            >
              <span className="adoption-command__index">{index + 1}</span>
              <div>
                <span className="muted tiny">{item.label}</span>
                <strong>{item.title}</strong>
                <p>{item.detail}</p>
              </div>
            </article>
          ))}
        </div>

        <div className="adoption-command__actions">
          {!confirmation && !draft && !report && (
            <button className="btn btn--primary" disabled={loading} onClick={submitAdoption}>
              {loading ? "正在入账…" : "写入采纳台"}
            </button>
          )}
          {!confirmation && report && !draft && (
            <button className="btn btn--primary" disabled={draftLoading} onClick={generateDraft}>
              {draftLoading ? "正在生成…" : "生成草稿"}
            </button>
          )}
          {!confirmation && draft && selectedRewriteCount > 0 && !rewriteApplication && (
            <button
              className="btn btn--primary"
              disabled={rewriteLoading}
              onClick={applySelectedRewrites}
            >
              {rewriteLoading ? "正在采纳…" : "采纳选中改写"}
            </button>
          )}
          {!confirmation && draft && (
            <button
              className="btn btn--ghost"
              disabled={confirmationLoading || !editedChapterText.trim()}
              onClick={confirmChapter}
            >
              {confirmationLoading ? "正在确认…" : "确认入卷"}
            </button>
          )}
          {confirmation && (
            <button
              className="btn btn--primary"
              onClick={() =>
                navigate({ name: "dossierReading", slug, worldlineId: "main" })
              }
            >
              去卷宗阅读
            </button>
          )}
          {!confirmation && (
            <button
              className="btn btn--ghost"
              onClick={openWritingDesk}
            >
              调整材料
            </button>
          )}
          <button className="btn btn--ghost" onClick={() => navigate({ name: "sandbox", slug })}>
            回世界沙盘
          </button>
        </div>
      </section>

      <WorldRunway
        eyebrow="作者工作流"
        title="从沙盘涌现到下一章定稿"
        summary="这里不是让模型直接覆盖正史，而是让作者比较原大纲与世界自演结果：先采纳，再生成草稿，最后确认入卷。"
        meta={
          <>
            <span className="badge badge--jade">
              {confirmation ? "已确认入卷" : draft ? "草稿待定稿" : report ? "已入采纳台" : "待采纳"}
            </span>
            <span className="badge">main</span>
            {report?.run_id && <span className="badge badge--gold">{report.run_id}</span>}
          </>
        }
        steps={[
          {
            label: "比较差异",
            detail: "把原大纲和沙盘涌现并排看。",
            active: !report,
          },
          {
            label: "采纳并改写",
            detail: "生成下一章 brief、草稿和局部重写。",
            active: !!report && !confirmation,
          },
          {
            label: "确认入卷",
            detail: "让定稿进入阅读链和下一轮沙盘入口。",
            active: !!confirmation,
          },
        ]}
        actions={[
          {
            label: "多视角卷",
            detail: "先让同一事件生成角色视角",
            onClick: () => navigate({ name: "lens", slug }),
          },
          {
            label: "卷宗阅读",
            detail: "回到 main 世界线连续阅读",
            onClick: () =>
              navigate({ name: "dossierReading", slug, worldlineId: "main" }),
          },
          {
            label: "世界沙盘",
            detail: "把确认结果继续投回世界",
            primary: true,
            onClick: () => navigate({ name: "sandbox", slug }),
          },
        ]}
      />

      <div className={`adoption-layout adoption-layout--${workspaceMode}`}>
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
              <div className="adoption-triad" aria-label="原大纲与沙盘涌现剧情对照">
                <article>
                  <span className="muted tiny">原大纲</span>
                  <p>{report.comparison.original_outline}</p>
                </article>
                <article>
                  <span className="muted tiny">沙盘涌现剧情</span>
                  <p>{report.comparison.sandbox_emergence}</p>
                </article>
                <article>
                  <span className="muted tiny">下一章可写方案</span>
                  <p>
                    {report.next_chapter_brief?.writing_plan?.next_chapter_brief_md ||
                      report.next_chapter_brief?.opening_scene ||
                      "采纳后会在这里生成下一章方案。"}
                  </p>
                </article>
              </div>
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
                  <div className="adoption-next__head">
                    <h3>下一章可写方案</h3>
                    <span className="badge badge--gold">
                      {writingStanceLabel(report.next_chapter_brief.writing_plan?.stance)}
                    </span>
                  </div>
                  <p>{report.next_chapter_brief.opening_scene}</p>
                  <p className="muted tiny">
                    冲突焦点：{report.next_chapter_brief.conflict_focus}
                  </p>
                  <p className="muted tiny">
                    后续沙盘入口：
                    {report.next_chapter_brief.feed_forward?.sandbox_continuation_inputs
                      .major_event || report.next_chapter_brief.sandbox_inputs.major_event}
                  </p>
                  {report.next_chapter_brief.author_branch?.branch_id && (
                    <p className="muted tiny">
                      作者分支：
                      {report.next_chapter_brief.author_branch.branch_id}
                      ，根正史保持不覆盖。
                    </p>
                  )}
                  {report.next_chapter_brief.writing_plan?.manual_review_points?.length ? (
                    <div className="adoption-review-points">
                      {report.next_chapter_brief.writing_plan.manual_review_points.map((item) => (
                        <span className="badge badge--gold" key={item}>
                          {item}
                        </span>
                      ))}
                    </div>
                  ) : null}
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
                <div className="adoption-feed-forward">
                  <strong>已反哺后续入口</strong>
                  <p className="muted tiny">
                    已写入 {report.continuation_effect.worldline_state_artifact}，后续沙盘会读取采纳记录、下一章 brief、世界线状态和确认章节入口。
                  </p>
                  {report.next_chapter_brief?.feed_forward?.next_round_reads?.length ? (
                    <div className="adoption-reading__refs">
                      {report.next_chapter_brief.feed_forward.next_round_reads.map((item) => (
                        <span className="badge" key={item}>
                          {item}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </div>
              )}
              {draftError && <ErrorState message={draftError} onRetry={generateDraft} />}
              {draft && (
                <div className="adoption-draft">
                  <div className="adoption-draft__head">
                    <h3>{draft.chapter_title}</h3>
                    <span className="badge badge--gold">{draft.artifact}</span>
                  </div>
                  <label className="adoption-editor">
                    <span className="muted tiny">作者修订稿</span>
                    <textarea
                      value={editedChapterText}
                      onChange={(event) => {
                        setEditedChapterText(event.target.value);
                        setConfirmation(null);
                      }}
                      rows={14}
                    />
                  </label>
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
                  {draft.continuous_reading_chapter && (
                    <div className="adoption-reading">
                      <div className="adoption-reading__head">
                        <div>
                          <h4>连续阅读稿</h4>
                          <p className="muted tiny">
                            来源沙盘：
                            {draft.continuous_reading_chapter.s8_source
                              .source_sandbox_run_id || "未绑定"}
                          </p>
                        </div>
                        <span
                          className={`badge ${
                            draft.continuous_reading_chapter.status === "ready"
                              ? "badge--jade"
                              : "badge--gold"
                          }`}
                        >
                          {readingTrailStatusLabel(draft.continuous_reading_chapter.status)}
                        </span>
                      </div>
                      <div className="adoption-reading-flow">
                        <span>
                          {draft.continuous_reading_chapter.reading_flow.scene_count} 场
                        </span>
                        {draft.continuous_reading_chapter.story_beat_source && (
                          <span>
                            来源：
                            {draft.continuous_reading_chapter.story_beat_source.kind ===
                            "s8_novel_scene_plan"
                              ? "S8 场景节拍"
                              : "草稿段落"}
                          </span>
                        )}
                        <span>
                          默认：
                          {draft.continuous_reading_chapter.default_mode === "novel"
                            ? "小说阅读"
                            : draft.continuous_reading_chapter.default_mode || "正文"}
                        </span>
                        {draft.continuous_reading_chapter.evidence_toggle && (
                          <span>
                            {draft.continuous_reading_chapter.evidence_toggle.label}默认
                            {draft.continuous_reading_chapter.evidence_toggle
                              .default_visible
                              ? "展开"
                              : "收起"}
                          </span>
                        )}
                        <span>
                          {draft.continuous_reading_chapter.reading_flow.turning_point}
                        </span>
                        <span>
                          {draft.continuous_reading_chapter.reading_flow.next_chapter_hook}
                        </span>
                      </div>
                      {draft.continuous_reading_chapter.viewpoint_tabs &&
                        draft.continuous_reading_chapter.viewpoint_tabs.length > 0 && (
                          <div className="adoption-reading__refs">
                            {draft.continuous_reading_chapter.viewpoint_tabs.map((tab) => (
                              <span className="badge" key={tab.id}>
                                {tab.label}
                              </span>
                            ))}
                          </div>
                        )}
                      <div className="adoption-reading__sections">
                        {draft.continuous_reading_chapter.reading_sections.map((section) => (
                          <div className="adoption-reading__section" key={section.id}>
                            <div>
                              <strong>{section.title}</strong>
                              <span className="muted tiny">{section.narrative_role}</span>
                            </div>
                            {section.source_beat_type && (
                              <span className="badge badge--gold">
                                {section.source_beat_type}
                              </span>
                            )}
                            {(section.viewpoint || section.cognitive_bias) && (
                              <p className="muted tiny">
                                {section.viewpoint}
                                {section.cognitive_bias ? ` · ${section.cognitive_bias}` : ""}
                              </p>
                            )}
                            <p>{section.body}</p>
                            {section.evidence_refs.length > 0 && (
                              <div className="adoption-reading__refs">
                                {section.evidence_refs.map((ref) => (
                                  <span className="badge" key={ref}>
                                    {ref}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                      {draft.continuous_reading_chapter.cross_volume_refs.length > 0 && (
                        <div className="adoption-reading__refs">
                          {draft.continuous_reading_chapter.cross_volume_refs.map((ref) => (
                            <span className="badge" key={ref.id}>
                              {ref.label} · {ref.artifact}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
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
                  {draft.revision_pack && (
                    <div className="adoption-next">
                      <div className="adoption-next__head">
                        <h3>局部修订包</h3>
                        <span
                          className={`badge ${
                            draft.revision_pack.confirmation_gate.ready_for_confirmation
                              ? "badge--jade"
                              : "badge--gold"
                          }`}
                        >
                          {draft.revision_pack.confirmation_gate.ready_for_confirmation
                            ? "可确认"
                            : "需修订"}
                        </span>
                      </div>
                      <p>{draft.revision_pack.summary}</p>
                      <p className="muted tiny">
                        {draft.revision_pack.confirmation_gate.author_action}
                      </p>
                      <div className="adoption-rewrite-toolbar">
                        <div>
                          <strong>可采纳局部改写</strong>
                          <p className="muted tiny">
                            已选 {selectedRewriteIds.length} /{" "}
                            {draft.revision_pack.localized_rewrites.length} 条；采纳后会写入修订稿和下一章草稿记录。
                          </p>
                        </div>
                        <button
                          className="btn btn--primary"
                          disabled={rewriteLoading || selectedRewriteIds.length === 0}
                          onClick={applySelectedRewrites}
                        >
                          {rewriteLoading ? "正在采纳…" : "采纳选中改写到修订稿"}
                        </button>
                      </div>
                      <label className="adoption-editor adoption-rewrite-note">
                        <span className="muted tiny">采纳备注</span>
                        <textarea
                          value={rewriteNote}
                          onChange={(event) => setRewriteNote(event.target.value)}
                          rows={2}
                        />
                      </label>
                      {rewriteError && (
                        <ErrorState message={rewriteError} onRetry={applySelectedRewrites} />
                      )}
                      {rewriteApplication && (
                        <div className="adoption-rewrite-result">
                          <div>
                            <strong>已写入编辑后定稿</strong>
                            <span className="badge badge--jade">
                              {rewriteApplication.edited_final_chapter?.markdown_artifact ||
                                rewriteApplication.markdown_artifact}
                            </span>
                          </div>
                          <p>
                            已采纳 {rewriteApplication.applied_rewrite_ids.length} 条局部重写，正文编辑框已换成可直接确认入卷的编辑后定稿。
                          </p>
                          {rewriteApplication.edited_final_chapter && (
                            <p className="muted tiny">
                              确认时若未继续手改，服务端会自动读取{" "}
                              {rewriteApplication.edited_final_chapter.artifact}
                              ，避免把审稿清单当正文入卷。
                            </p>
                          )}
                          <div className="adoption-reading__refs">
                            {rewriteApplication.applied_rewrite_ids.map((id) => (
                              <span className="badge" key={id}>
                                {id}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {draft.revision_pack.semantic_reviewer && (
                        <div className="adoption-reading__section">
                          <div>
                            <strong>语义审稿</strong>
                            <span className="muted tiny">
                              {draft.revision_pack.semantic_reviewer.status}
                            </span>
                          </div>
                          <p>{draft.revision_pack.semantic_reviewer.diagnosis_summary}</p>
                          <div className="adoption-reading__refs">
                            {draft.revision_pack.semantic_reviewer.review_items.map((item) => (
                              <span className="badge" key={item.id}>
                                {item.priority} · {item.dimension}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {draft.revision_pack.editorial_revision_draft?.status === "ready" && (
                        <div className="adoption-reading__section">
                          <div>
                            <strong>编辑应用预览</strong>
                            <span className="muted tiny">
                              {draft.revision_pack.editorial_revision_draft.applied_rewrite_ids.length}
                              条建议
                            </span>
                          </div>
                          <p>{draft.revision_pack.editorial_revision_draft.preview_text_md}</p>
                          <div className="adoption-reading__refs">
                            {draft.revision_pack.editorial_revision_draft.feeds.map((feed) => (
                              <span className="badge" key={feed}>
                                {feed}
                              </span>
                            ))}
                          </div>
                          <p className="muted tiny">
                            不自动覆盖：
                            {draft.revision_pack.editorial_revision_draft.does_not_overwrite.join(
                              " / ",
                            )}
                          </p>
                        </div>
                      )}
                      <div className="adoption-reading__sections">
                        {draft.revision_pack.localized_rewrites.map((item) => (
                          <div
                            className={`adoption-reading__section adoption-rewrite-card ${
                              selectedRewriteIds.includes(item.id) ? "is-selected" : ""
                            }`}
                            key={item.id}
                          >
                            <div className="adoption-rewrite-card__head">
                              <label>
                                <input
                                  type="checkbox"
                                  checked={selectedRewriteIds.includes(item.id)}
                                  onChange={() => toggleRewrite(item.id)}
                                />
                                <strong>{item.rewrite_instruction}</strong>
                              </label>
                              <span className="muted tiny">
                                {priorityLabel(item.priority)} · {item.id}
                              </span>
                            </div>
                            <p>
                              <b>原问题：</b>
                              {item.original_problem || item.issue}
                            </p>
                            <p>
                              <b>建议改写：</b>
                              {item.suggested_rewrite || item.suggested_revision}
                            </p>
                            {(item.revision_intent || item.impact_on_world_state) && (
                              <p className="muted tiny">
                                修改意图：{item.revision_intent}
                                {item.impact_on_world_state
                                  ? ` · 影响范围：${item.impact_on_world_state}`
                                  : ""}
                              </p>
                            )}
                            {item.adoption_direction && (
                              <span className="badge badge--jade">
                                {item.adoption_direction}
                              </span>
                            )}
                            {item.target_text && (
                              <p className="muted tiny">对应段落：{item.target_text}</p>
                            )}
                            {item.evidence_refs.length > 0 && (
                              <div className="adoption-reading__refs">
                                {item.evidence_refs.map((ref) => (
                                  <span className="badge" key={ref}>
                                    {ref}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="adoption-confirm">
                    <label className="adoption-editor">
                      <span className="muted tiny">确认备注</span>
                      <textarea
                        value={confirmationNote}
                        onChange={(event) => setConfirmationNote(event.target.value)}
                        rows={3}
                      />
                    </label>
                    <button
                      className="btn btn--primary"
                      disabled={confirmationLoading || !editedChapterText.trim()}
                      onClick={confirmChapter}
                    >
                      {confirmationLoading ? "正在确认…" : "确认入卷"}
                    </button>
                  </div>
                  {confirmationError && (
                    <ErrorState message={confirmationError} onRetry={confirmChapter} />
                  )}
                  {confirmation && (
                    <div className="adoption-confirmation">
                      <div className="adoption-draft__head">
                        <h3>已确认入卷</h3>
                        <span className="badge badge--jade">{confirmation.artifact}</span>
                      </div>
                      <dl>
                        <div>
                          <dt>正文</dt>
                          <dd>{confirmation.artifacts.confirmed_chapter_markdown}</dd>
                        </div>
                        <div>
                          <dt>阅读链</dt>
                          <dd>{confirmation.artifacts.confirmed_chapter_reading_trail}</dd>
                        </div>
                        <div>
                          <dt>状态</dt>
                          <dd>{confirmation.continuation_effect.worldline_state_artifact}</dd>
                        </div>
                        <div>
                          <dt>下一轮</dt>
                          <dd>
                            {confirmation.continuation_effect.next_sandbox_entry.major_event}
                          </dd>
                        </div>
                        <div>
                          <dt>编辑</dt>
                          <dd>
                            {confirmation.edit_source === "auto_reviewer_final"
                              ? "已采用 Reviewer 编辑后定稿"
                              : confirmation.edited
                                ? "已采用作者修订稿"
                                : "沿用草稿"}
                          </dd>
                        </div>
                        <div>
                          <dt>局部改写</dt>
                          <dd>
                            {confirmation.accepted_local_rewrites?.applied_rewrite_count
                              ? `${confirmation.accepted_local_rewrites.applied_rewrite_count} 条已反哺下一轮`
                              : "未采纳局部改写"}
                          </dd>
                        </div>
                      </dl>
                      {confirmation.accepted_local_rewrites?.applied_rewrite_ids?.length ? (
                        <div className="adoption-rewrite-result">
                          <div>
                            <strong>Reviewer 改写已随章节入卷</strong>
                            <span className="badge badge--jade">
                              {confirmation.accepted_local_rewrites.artifact}
                            </span>
                          </div>
                          <div className="adoption-reading__refs">
                            {confirmation.accepted_local_rewrites.applied_rewrite_ids.map((id) => (
                              <span className="badge" key={id}>
                                {id}
                              </span>
                            ))}
                          </div>
                        </div>
                      ) : null}
                      <div className="adoption-reading">
                        <div className="adoption-reading__head">
                          <div>
                            <h4>跨卷宗阅读链</h4>
                            <p className="muted tiny">
                              来源沙盘：{confirmation.reading_trail.source_sandbox_run_id || "未绑定"}
                            </p>
                          </div>
                          <span
                            className={`badge ${
                              confirmation.reading_trail.status === "ready"
                                ? "badge--jade"
                                : "badge--gold"
                            }`}
                          >
                            {readingTrailStatusLabel(confirmation.reading_trail.status)}
                          </span>
                        </div>
                        <div className="adoption-reading__sections">
                          {confirmation.reading_trail.sections.map((section) => (
                            <div className="adoption-reading__section" key={section.id}>
                              <div>
                                <strong>{section.label}</strong>
                                {section.character_name && (
                                  <span className="muted tiny">
                                    {section.character_name}
                                    {typeof section.event_node_count === "number"
                                      ? ` · ${section.event_node_count} 个事件节点`
                                      : ""}
                                  </span>
                                )}
                              </div>
                              <p>{section.reason}</p>
                              <p className="mono tiny">{section.artifact}</p>
                              {section.evidence_refs.length > 0 && (
                                <div className="adoption-reading__refs">
                                  {section.evidence_refs.map((ref) => (
                                    <span className="badge" key={ref}>
                                      {ref}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                      <p className="muted tiny">
                        后续沙盘会读取已确认章节、采纳记录、下一章 brief 与世界线状态继续推进。
                      </p>
                      <div className="adoption-draft__checks">
                        {confirmation.reviewer_checklist.map((item) => (
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
                </div>
              )}
            </section>
          )}
        </main>
      </div>
    </div>
  );
}

function priorityLabel(priority: string) {
  if (priority === "blocking") return "阻断";
  if (priority === "high") return "高优先级";
  if (priority === "medium") return "中优先级";
  if (priority === "low") return "低优先级";
  return priority || "未分级";
}
