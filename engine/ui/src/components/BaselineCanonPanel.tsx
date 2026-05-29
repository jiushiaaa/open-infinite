import { useEffect, useState } from "react";
import type {
  BaselineReport,
  CanonReplayReport,
  HoldoutManifest,
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

/** 基线与正史回放区块：放在世界锚定左栏。所有失败降级为提示，不阻塞主流程。 */
export function BaselineCanonPanel({
  slug,
  sourceKind,
}: {
  slug: string;
  sourceKind: SourceKind;
}) {
  const isBuiltin = sourceKind === "builtin";

  const [holdout, setHoldout] = useState<HoldoutManifest | null>(null);
  const [baseline, setBaseline] = useState<BaselineReport | null>(null);
  const [baselineRunId, setBaselineRunId] = useState<string>("");
  const [replay, setReplay] = useState<CanonReplayReport | null>(null);

  const [genWorking, setGenWorking] = useState(false);
  const [replayWorking, setReplayWorking] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [uploadChapter, setUploadChapter] = useState<string>("");
  const [uploadTitle, setUploadTitle] = useState<string>("");
  const [uploadContent, setUploadContent] = useState<string>("");
  const [uploadWorking, setUploadWorking] = useState(false);
  const [replayChapter, setReplayChapter] = useState<number | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    api
      .getHoldout(slug)
      .then((m) => {
        if (alive) setHoldout(m);
      })
      .catch(() => {
        if (alive) setHoldout(null);
      });
    return () => {
      alive = false;
    };
  }, [slug]);

  const available = holdout?.available_chapters ?? [];

  async function reloadHoldout() {
    try {
      setHoldout(await api.getHoldout(slug));
    } catch {
      /* 静默：缺 holdout 不是错误 */
    }
  }

  async function generateBaseline() {
    setGenWorking(true);
    setErr(null);
    setNotice(null);
    setReplay(null);
    try {
      const res = await api.generateBaseline(slug, { mock: true });
      setBaseline(res.report);
      setBaselineRunId(res.run_id);
      setNotice("无干预基线已生成。");
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
      await reloadHoldout();
    } catch (e) {
      setErr(toMessage(e));
    } finally {
      setUploadWorking(false);
    }
  }

  return (
    <section className="anchor__block bcanon">
      <h3 className="anchor__block-title">基线与正史回放</h3>
      <p className="muted tiny bcanon__note">
        基线不是原作，只是角色在无高维干预下的自然发展对照。正史回放仅用于本地评估，不代表复刻原作。
      </p>

      {/* holdout 状态 */}
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

      {/* 基线生成 */}
      <div className="bcanon__actions">
        <button
          className="btn btn--primary tiny"
          onClick={generateBaseline}
          disabled={genWorking}
        >
          {genWorking ? "正在推进基线…" : "生成无干预基线"}
        </button>
        {baseline && available.length > 0 && (
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
              {replayWorking ? "评估中…" : "运行正史回放"}
            </button>
          </div>
        )}
      </div>

      {notice && <p className="bcanon__notice tiny">{notice}</p>}
      {err && <p className="anchor__save-err tiny">{err}</p>}

      {baseline && <BaselineSummary report={baseline} />}
      {replay && <ReplayScorecard report={replay} />}
    </section>
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
      {report.natural_development_points.length > 0 && (
        <>
          <span className="bcanon__sub muted tiny">自然发展</span>
          <ul className="bcanon__list">
            {report.natural_development_points.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        </>
      )}
      {report.character_state_changes.length > 0 && (
        <>
          <span className="bcanon__sub muted tiny">角色状态变化</span>
          <ul className="bcanon__list">
            {report.character_state_changes.map((c) => (
              <li key={c.character_id}>
                <strong>{c.name || c.character_id}</strong>
                {c.location ? ` · ${c.location}` : ""}
                {c.emotion ? ` · ${c.emotion}` : ""}
              </li>
            ))}
          </ul>
        </>
      )}
      {report.open_threads_touched.length > 0 && (
        <>
          <span className="bcanon__sub muted tiny">触及伏笔</span>
          <div className="chip-row">
            {report.open_threads_touched.map((t, i) => (
              <span key={i} className="badge tiny">
                {t}
              </span>
            ))}
          </div>
        </>
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
        <span className="badge badge--indigo tiny">正史回放</span>
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
              <span
                className="bcanon__bar-fill"
                style={{ width: pct(val) }}
              />
            </span>
            <span className="bcanon__bar-val tiny mono">{pct(val)}</span>
          </div>
        ))}
      </div>
      {report.interpretation && (
        <p className="bcanon__interpret tiny">{report.interpretation}</p>
      )}
      {report.missing_entities.length > 0 && (
        <>
          <span className="bcanon__sub muted tiny">缺失关键实体</span>
          <div className="chip-row">
            {report.missing_entities.map((e, i) => (
              <span key={i} className="badge badge--cinnabar tiny">
                {e}
              </span>
            ))}
          </div>
        </>
      )}
      {report.warnings.length > 0 && (
        <ul className="bcanon__warnings tiny">
          {report.warnings.map((w, i) => (
            <li key={i}>{w}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
