import { useEffect, useMemo, useState } from "react";
import type {
  BaselineReport,
  CanonReplayRangeReport,
  CanonReplayReport,
  HoldoutManifest,
  ReplayAuditWorkspace,
  SourceKind,
} from "../api/types";
import { ApiError, api } from "../api/client";
import "./baselineCanon.css";

function toMessage(e: unknown): string {
  if (e instanceof ApiError) return e.message;
  if (e instanceof Error) return e.message;
  return String(e);
}

const SCORE_LABELS: Record<string, string> = {
  lexical_overlap: "字词重合",
  entity_overlap: "实体命中",
  thread_overlap: "伏笔命中",
  length_ratio: "篇幅比",
  state_consistency: "状态一致",
  overall: "总分",
};

function pct(v: number): string {
  return `${Math.round((v ?? 0) * 100)}%`;
}

/** 基线与长篇回放审计区块：放在世界锚定左栏。失败降级为提示，不阻塞主流程。 */
export function BaselineCanonPanel({
  slug,
  sourceKind,
}: {
  slug: string;
  sourceKind: SourceKind;
}) {
  const isBuiltin = sourceKind === "builtin";

  const [audit, setAudit] = useState<ReplayAuditWorkspace | null>(null);
  const [holdout, setHoldout] = useState<HoldoutManifest | null>(null);
  const [baseline, setBaseline] = useState<BaselineReport | null>(null);
  const [baselineRunId, setBaselineRunId] = useState<string>("");
  const [replay, setReplay] = useState<CanonReplayReport | null>(null);
  const [rangeReplay, setRangeReplay] = useState<CanonReplayRangeReport | null>(null);

  const [genWorking, setGenWorking] = useState(false);
  const [replayWorking, setReplayWorking] = useState(false);
  const [rangeWorking, setRangeWorking] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [uploadChapter, setUploadChapter] = useState<string>("");
  const [uploadTitle, setUploadTitle] = useState<string>("");
  const [uploadContent, setUploadContent] = useState<string>("");
  const [uploadWorking, setUploadWorking] = useState(false);
  const [replayChapter, setReplayChapter] = useState<number | null>(null);
  const [rangeStart, setRangeStart] = useState<number | null>(null);
  const [rangeEnd, setRangeEnd] = useState<number | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function reloadAudit() {
    try {
      const data = await api.getReplayAuditWorkspace(slug);
      setAudit(data);
      setHoldout(data.holdout);
      if (!baselineRunId && data.baseline_runs[0]) {
        setBaselineRunId(data.baseline_runs[0].run_id);
      }
    } catch {
      try {
        setHoldout(await api.getHoldout(slug));
      } catch {
        setHoldout(null);
      }
    }
  }

  useEffect(() => {
    let alive = true;
    api
      .getReplayAuditWorkspace(slug)
      .then((data) => {
        if (!alive) return;
        setAudit(data);
        setHoldout(data.holdout);
        if (data.baseline_runs[0]) {
          setBaselineRunId(data.baseline_runs[0].run_id);
        }
      })
      .catch(() => {
        if (!alive) return;
        api
          .getHoldout(slug)
          .then((m) => alive && setHoldout(m))
          .catch(() => alive && setHoldout(null));
      });
    return () => {
      alive = false;
    };
  }, [slug]);

  const available = holdout?.available_chapters ?? [];
  const currentRange = useMemo(() => {
    if (available.length === 0) return null;
    const start = rangeStart ?? available[0];
    const end = rangeEnd ?? available[available.length - 1];
    return start <= end ? { start, end } : { start: end, end: start };
  }, [available, rangeEnd, rangeStart]);

  async function generateBaseline() {
    setGenWorking(true);
    setErr(null);
    setNotice(null);
    setReplay(null);
    setRangeReplay(null);
    try {
      const res = await api.generateBaseline(slug, { mock: true });
      setBaseline(res.report);
      setBaselineRunId(res.run_id);
      setNotice("无干预基线已生成。");
      await reloadAudit();
    } catch (e) {
      setErr(toMessage(e));
    } finally {
      setGenWorking(false);
    }
  }

  async function runReplay() {
    const chapter = replayChapter ?? available[0];
    if (!baselineRunId || chapter == null) return;
    setReplayWorking(true);
    setErr(null);
    setNotice(null);
    try {
      const rep = await api.runCanonReplay(slug, {
        baseline_run_id: baselineRunId,
        baseline_branch_id: "baseline",
        holdout_chapter: chapter,
      });
      setReplay(rep);
    } catch (e) {
      setErr(toMessage(e));
    } finally {
      setReplayWorking(false);
    }
  }

  async function runRangeReplay() {
    if (!baselineRunId || !currentRange) return;
    setRangeWorking(true);
    setErr(null);
    setNotice(null);
    try {
      const rep = await api.runCanonReplayRange(slug, {
        baseline_run_id: baselineRunId,
        baseline_branch_id: "baseline",
        chapter_start: currentRange.start,
        chapter_end: currentRange.end,
      });
      setRangeReplay(rep);
      setNotice(`已完成第 ${currentRange.start}-${currentRange.end} 章范围回放。`);
      await reloadAudit();
    } catch (e) {
      setErr(toMessage(e));
    } finally {
      setRangeWorking(false);
    }
  }

  async function submitHoldout() {
    const chapter = parseInt(uploadChapter, 10);
    if (!Number.isInteger(chapter) || chapter < 1) {
      setErr("章号必须为 ≥1 的整数。");
      return;
    }
    if (!uploadContent.trim()) {
      setErr("正史章节正文不能为空。");
      return;
    }
    setUploadWorking(true);
    setErr(null);
    setNotice(null);
    try {
      await api.writeHoldout(slug, {
        chapters: [
          { chapter, title: uploadTitle.trim(), content: uploadContent.trim() },
        ],
        force: false,
      });
      setUploadOpen(false);
      setUploadChapter("");
      setUploadTitle("");
      setUploadContent("");
      setNotice(`已保存正史第 ${chapter} 章为 holdout。`);
      await reloadAudit();
    } catch (e) {
      setErr(toMessage(e));
    } finally {
      setUploadWorking(false);
    }
  }

  return (
    <section className="anchor__block bcanon">
      <h3 className="anchor__block-title">回放与审计</h3>
      <p className="muted tiny bcanon__note">
        基线不是原作；长篇回放用 holdout 章节做本地评估，审计结果只辅助判断世界线偏移与实体缺口。
      </p>

      <AuditSnapshot audit={audit} />

      <div className="bcanon__holdout">
        <div className="bcanon__row">
          <span className="muted tiny">正史 holdout</span>
          <span className="badge tiny">
            {available.length > 0 ? `已录入 ${available.length} 章` : "暂无"}
          </span>
        </div>
        {available.length > 0 && (
          <p className="muted tiny mono">章节：{available.join(", ")}</p>
        )}
        {isBuiltin ? (
          <p className="muted tiny">内置样例为只读，不能录入正史 holdout。</p>
        ) : (
          <button
            className="btn btn--ghost tiny"
            onClick={() => setUploadOpen((v) => !v)}
          >
            {uploadOpen ? "收起录入" : "录入正史章节"}
          </button>
        )}
      </div>

      {uploadOpen && !isBuiltin && (
        <div className="bcanon__upload">
          <div className="bcanon__upload-bar">
            <input
              className="anchor__edit-input bcanon__chapnum"
              placeholder="章号"
              value={uploadChapter}
              onChange={(e) => setUploadChapter(e.target.value)}
            />
            <input
              className="anchor__edit-input"
              placeholder="章节标题（可选）"
              value={uploadTitle}
              onChange={(e) => setUploadTitle(e.target.value)}
            />
          </div>
          <textarea
            className="anchor__edit-textarea"
            rows={4}
            placeholder="粘贴该章正史正文（仅本地存储，用于评估，不公开分享）"
            value={uploadContent}
            onChange={(e) => setUploadContent(e.target.value)}
          />
          <button
            className="btn btn--primary tiny"
            onClick={submitHoldout}
            disabled={uploadWorking}
          >
            {uploadWorking ? "保存中…" : "保存为 holdout"}
          </button>
        </div>
      )}

      <div className="bcanon__actions">
        <button
          className="btn btn--primary tiny"
          onClick={generateBaseline}
          disabled={genWorking}
        >
          {genWorking ? "正在推进基线…" : "生成无干预基线"}
        </button>
        {available.length > 0 && baselineRunId && (
          <>
            <div className="bcanon__replay-ctl">
              <select
                className="bcanon__select"
                value={replayChapter ?? available[0]}
                onChange={(e) => setReplayChapter(parseInt(e.target.value, 10))}
              >
                {available.map((c) => (
                  <option key={c} value={c}>
                    第 {c} 章
                  </option>
                ))}
              </select>
              <button
                className="btn btn--ghost tiny"
                onClick={runReplay}
                disabled={replayWorking}
              >
                {replayWorking ? "评估中…" : "单章回放"}
              </button>
            </div>
            <div className="bcanon__replay-ctl">
              <select
                className="bcanon__select"
                value={currentRange?.start ?? available[0]}
                onChange={(e) => setRangeStart(parseInt(e.target.value, 10))}
              >
                {available.map((c) => (
                  <option key={c} value={c}>
                    起 第 {c} 章
                  </option>
                ))}
              </select>
              <select
                className="bcanon__select"
                value={currentRange?.end ?? available[available.length - 1]}
                onChange={(e) => setRangeEnd(parseInt(e.target.value, 10))}
              >
                {available.map((c) => (
                  <option key={c} value={c}>
                    至 第 {c} 章
                  </option>
                ))}
              </select>
              <button
                className="btn btn--ghost tiny"
                onClick={runRangeReplay}
                disabled={rangeWorking}
              >
                {rangeWorking ? "审计中…" : "范围回放"}
              </button>
            </div>
          </>
        )}
      </div>

      {notice && <p className="bcanon__notice tiny">{notice}</p>}
      {err && <p className="anchor__save-err tiny">{err}</p>}

      {baseline && <BaselineSummary report={baseline} />}
      {rangeReplay && <RangeReplayScorecard report={rangeReplay} />}
      {replay && <ReplayScorecard report={replay} />}
      {audit?.replay_ranges?.[0] && !rangeReplay && (
        <RangeReplaySnapshot range={audit.replay_ranges[0]} />
      )}
    </section>
  );
}

function AuditSnapshot({ audit }: { audit: ReplayAuditWorkspace | null }) {
  if (!audit) return null;
  const issueCount = audit.audit.summary.issue_count ?? 0;
  return (
    <div className="bcanon__audit">
      <div className="bcanon__audit-metrics">
        <Metric label="基线" value={audit.baseline_runs.length} />
        <Metric label="审计项" value={issueCount} />
        <Metric label="别名实体" value={audit.entity_aliases.count} />
      </div>
      {audit.audit.dimensions.length > 0 && (
        <div className="bcanon__dimension-list">
          {audit.audit.dimensions.map((dim) => (
            <span key={dim.key}>
              {dim.label} · {dim.issue_count}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="bcanon__metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function BaselineSummary({ report }: { report: BaselineReport }) {
  return (
    <div className="bcanon__panel">
      <div className="bcanon__panel-head">
        <span className="badge badge--jade tiny">基线</span>
        <span className="muted tiny">第 {report.chapter_number} 章 · 无干预</span>
      </div>
      {report.summary && <p className="bcanon__summary">{report.summary}</p>}
    </div>
  );
}

function RangeReplayScorecard({ report }: { report: CanonReplayRangeReport }) {
  return (
    <div className="bcanon__panel">
      <div className="bcanon__panel-head">
        <span className="badge badge--indigo tiny">范围回放</span>
        <span className="muted tiny">
          第 {report.chapter_range.start}-{report.chapter_range.end} 章 ·{" "}
          {riskLabel(report.summary.risk_level)}
        </span>
      </div>
      <div className="bcanon__overall">
        <span className="bcanon__overall-num">
          {pct(report.summary.average_overall)}
        </span>
        <span className="muted tiny">平均总分</span>
      </div>
      <RiskDimensions dimensions={report.risk_dimensions} />
      <EntityAudit audit={report.entity_audit} />
    </div>
  );
}

function RangeReplaySnapshot({
  range,
}: {
  range: ReplayAuditWorkspace["replay_ranges"][number];
}) {
  return (
    <div className="bcanon__panel">
      <div className="bcanon__panel-head">
        <span className="badge badge--indigo tiny">最近范围回放</span>
        <span className="muted tiny">
          {range.chapter_range.start}-{range.chapter_range.end} 章
        </span>
      </div>
      <p className="bcanon__summary">
        平均总分 {pct(range.summary.average_overall)}，风险：
        {riskLabel(range.summary.risk_level)}。
      </p>
      <RiskDimensions dimensions={range.risk_dimensions} />
    </div>
  );
}

function RiskDimensions({
  dimensions,
}: {
  dimensions: CanonReplayRangeReport["risk_dimensions"];
}) {
  if (dimensions.length === 0) return null;
  return (
    <div className="bcanon__risk-grid">
      {dimensions.map((dim) => (
        <div className={`bcanon__risk bcanon__risk--${dim.risk_level}`} key={dim.key}>
          <div>
            <strong>{dim.label}</strong>
            <span>{pct(dim.score)}</span>
          </div>
          <p>{dim.message}</p>
        </div>
      ))}
    </div>
  );
}

function EntityAudit({
  audit,
}: {
  audit: CanonReplayRangeReport["entity_audit"];
}) {
  const missing = audit.missing_entities ?? [];
  const matched = audit.matched_entities ?? [];
  return (
    <div className="bcanon__entity-audit">
      <span className="bcanon__sub muted tiny">实体归一化</span>
      <p className="muted tiny">
        命中 {matched.length} 个，缺失 {missing.length} 个。
      </p>
      {audit.missing_entities_by_chapter.length > 0 && (
        <ul className="bcanon__list">
          {audit.missing_entities_by_chapter.slice(0, 4).map((row) => (
            <li key={row.chapter}>
              第 {row.chapter} 章缺失：{row.entities.join("、")}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function ReplayScorecard({ report }: { report: CanonReplayReport }) {
  const s = report.scores;
  const rows: Array<[string, number]> = [
    ["lexical_overlap", s.lexical_overlap],
    ["entity_overlap", s.entity_overlap],
    ["thread_overlap", s.thread_overlap],
    ["length_ratio", s.length_ratio],
    ["state_consistency", s.state_consistency],
  ];
  return (
    <div className="bcanon__panel">
      <div className="bcanon__panel-head">
        <span className="badge badge--indigo tiny">单章回放</span>
        <span className="muted tiny">对比第 {report.holdout_chapter} 章</span>
      </div>
      <div className="bcanon__overall">
        <span className="bcanon__overall-num">{pct(s.overall)}</span>
        <span className="muted tiny">{SCORE_LABELS.overall}</span>
      </div>
      <div className="bcanon__bars">
        {rows.map(([key, val]) => (
          <div key={key} className="bcanon__bar-row">
            <span className="bcanon__bar-label tiny">{SCORE_LABELS[key]}</span>
            <span className="bcanon__bar-track">
              <span className="bcanon__bar-fill" style={{ width: pct(val) }} />
            </span>
            <span className="bcanon__bar-val tiny mono">{pct(val)}</span>
          </div>
        ))}
      </div>
      {report.interpretation && (
        <p className="bcanon__interpret tiny">{report.interpretation}</p>
      )}
    </div>
  );
}

function riskLabel(value: string): string {
  const map: Record<string, string> = {
    low: "低风险",
    medium: "中风险",
    high: "高风险",
  };
  return map[value] ?? value;
}
