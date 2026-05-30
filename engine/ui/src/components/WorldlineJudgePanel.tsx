import { useEffect, useState } from "react";
import type { BranchDetail, JudgementDimension, WorldlineJudgement } from "../api/types";
import { ApiError, api } from "../api/client";
import { EmptyState } from "./common/States";
import "./worldlineJudge.css";

function pct(v: number): string {
  return `${Math.round((v ?? 0) * 100)}%`;
}

function toMessage(e: unknown): string {
  if (e instanceof ApiError) return e.message;
  if (e instanceof Error) return e.message;
  return String(e);
}

const SCORE_LABELS: Record<string, string> = {
  persona_consistency: "角色一致",
  contract_risk: "合约风险",
  branch_diversity: "分支差异",
  narrative_momentum: "叙事动量",
  emotional_payoff: "情绪兑现",
  anti_slop: "反水文",
  continuation_potential: "续写潜力",
  emergence_score: "涌现价值",
  story_arc: "故事弧",
  turning_points: "转折点",
  tension: "张力",
};

const RECOMMEND_CLASS: Record<string, string> = {
  推荐继续: "badge--jade",
  谨慎继续: "badge--gold",
  建议归档: "badge--cinnabar",
};

export function WorldlineJudgePanel({
  storySlug,
  branch,
}: {
  storySlug: string;
  branch: BranchDetail;
}) {
  const [report, setReport] = useState<WorldlineJudgement | null>(null);
  const [loading, setLoading] = useState(false);
  const [working, setWorking] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    setErr(null);
    setReport(null);
    api
      .getWorldlineJudgement(branch.run_id, branch.branch_id)
      .then((data) => {
        if (alive) setReport(data);
      })
      .catch((e) => {
        if (!alive) return;
        if (e instanceof ApiError && e.status === 404) {
          setReport(null);
        } else {
          setErr(toMessage(e));
        }
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, [branch.run_id, branch.branch_id]);

  async function generate() {
    setWorking(true);
    setErr(null);
    try {
      const data = await api.generateWorldlineJudgement(
        branch.run_id,
        branch.branch_id,
        { story_slug: storySlug },
      );
      setReport(data);
    } catch (e) {
      setErr(toMessage(e));
    } finally {
      setWorking(false);
    }
  }

  if (loading) {
    return <EmptyState title="正在读取评审" hint="若该分支尚未评审，可稍后生成。" />;
  }

  return (
    <div className="wjudge">
      <div className="wjudge__head">
        <div>
          <h3 className="wjudge__title">世界线评审</h3>
          <p className="muted tiny">
            本地 deterministic 评分，不改正文、不写回世界状态。
          </p>
        </div>
        <button className="btn btn--primary tiny" onClick={generate} disabled={working}>
          {working ? "评审中…" : report ? "重新评审" : "生成评审"}
        </button>
      </div>

      {err && <p className="anchor__save-err tiny">{err}</p>}

      {!report ? (
        <EmptyState
          title="尚未评审"
          hint="生成后会写入 worldline_judgement.json，帮助判断这条分支是否值得继续。"
        />
      ) : (
        <JudgeReport report={report} />
      )}
    </div>
  );
}

function JudgeReport({ report }: { report: WorldlineJudgement }) {
  const badgeClass = RECOMMEND_CLASS[report.recommendation] ?? "badge--gold";
  const dimensionMap = new Map(report.dimensions.map((d) => [d.key, d]));
  const rows = Object.entries(SCORE_LABELS).flatMap(([key, label]) => {
    const dim = dimensionMap.get(key);
    if (!dim) return [];
    return [[label, dim] as const];
  });

  return (
    <div className="wjudge__report">
      <div className="wjudge__overall">
        <span className="wjudge__score">{pct(report.scores.overall)}</span>
        <span className={`badge tiny ${badgeClass}`}>{report.recommendation}</span>
      </div>
      {report.interpretation && (
        <p className="wjudge__interpret">{report.interpretation}</p>
      )}

      {report.story_arc_curve.length > 0 && (
        <div className="wjudge__curve">
          {report.story_arc_curve.map((p) => (
            <div key={p.label} className="wjudge__curve-point">
              <span className="tiny muted">{p.label}</span>
              <span className="wjudge__track">
                <span className="wjudge__fill" style={{ width: pct(p.tension) }} />
              </span>
              <span className="tiny mono">{pct(p.tension)}</span>
            </div>
          ))}
        </div>
      )}

      <div className="wjudge__bars">
        {rows.map(([label, dim]) => (
          <DimensionRow key={dim.key} label={label} dim={dim} />
        ))}
      </div>

      <TextList title="优势" items={report.strengths} />
      <TextList title="警告" items={report.warnings} danger />
      <TextList title="建议" items={report.suggestions} />
      <TextList title="转折点" items={report.turning_points} />
    </div>
  );
}

function DimensionRow({
  label,
  dim,
}: {
  label: string;
  dim: JudgementDimension;
}) {
  const isRisk = dim.key === "contract_risk";
  return (
    <div className="wjudge__bar-row" title={dim.comment}>
      <span className="wjudge__bar-label tiny">{label}</span>
      <span className="wjudge__track">
        <span
          className={`wjudge__fill ${isRisk ? "is-risk" : ""}`}
          style={{ width: pct(dim.score) }}
        />
      </span>
      <span className="wjudge__bar-val tiny mono">{pct(dim.score)}</span>
    </div>
  );
}

function TextList({
  title,
  items,
  danger = false,
}: {
  title: string;
  items: string[];
  danger?: boolean;
}) {
  if (!items.length) return null;
  return (
    <div className="wjudge__textlist">
      <span className="wjudge__sub muted tiny">{title}</span>
      <ul className={danger ? "wjudge__warnings" : ""}>
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
