import { useState } from "react";
import { ApiError, api } from "../api/client";
import type { CharacterProbe, GuardrailRisk } from "../api/types";
import "./characterProbe.css";

const RISK_LABEL: Record<GuardrailRisk, string> = {
  low: "低",
  medium: "中",
  high: "高",
};

const FW_LABEL: Record<string, string> = {
  none: "未觉察",
  unsettled: "隐隐不安",
  suspicious: "起疑",
  aware: "已觉察",
  defiant: "公然反抗",
};

/** 角色内心探针：折叠区域，按需向后端拉取只读解释。 */
export function CharacterProbePanel({
  slug,
  charId,
}: {
  slug: string;
  charId: string;
}) {
  const [open, setOpen] = useState(false);
  const [data, setData] = useState<CharacterProbe | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function toggle() {
    const next = !open;
    setOpen(next);
    if (next && !data && !loading) {
      setLoading(true);
      setError(null);
      try {
        const probe = await api.getCharacterProbe(slug, charId);
        setData(probe);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    }
  }

  return (
    <div className="probe">
      <button
        className="probe__toggle tiny"
        onClick={toggle}
        aria-expanded={open}
      >
        {open ? "收起角色探针" : "查看角色探针"}
      </button>
      {open && (
        <div className="probe__body">
          {loading && <p className="muted tiny">正在探查内心…</p>}
          {error && <p className="probe__err tiny">{error}</p>}
          {data && <ProbeContent data={data} />}
        </div>
      )}
    </div>
  );
}

function ProbeContent({ data }: { data: CharacterProbe }) {
  return (
    <div className="probe__content">
      <p className="probe__belief">{data.belief_summary}</p>

      <div className="probe__metrics">
        <Metric k="当前心境" v={data.current_emotion} />
        <Metric k="抗拒程度" v={RISK_LABEL[data.resistance_level]} tone={data.resistance_level} />
        <Metric
          k="盲从风险"
          v={RISK_LABEL[data.obedience_risk]}
          tone={data.obedience_risk === "high" ? "high" : "low"}
        />
        <Metric k="第四面墙" v={FW_LABEL[data.fourth_wall_level] ?? data.fourth_wall_level} />
      </div>

      <ProbeList label="欲望" items={data.desires} />
      <ProbeList label="恐惧" items={data.fears} />
      <ProbeList label="行为边界" items={data.boundaries} emphasize />
      <ProbeList label="已知" items={data.known_information} />
      <ProbeList label="未知" items={data.unknown_information} />

      <div className="probe__predict">
        <span className="probe__predict-k tiny muted">面对干预可能</span>
        <span className="probe__predict-v">{data.likely_intervention_response}</span>
      </div>

      <p className="probe__explain">{data.explanation}</p>
    </div>
  );
}

function Metric({ k, v, tone }: { k: string; v: string; tone?: GuardrailRisk | "low" | "high" }) {
  return (
    <div className="probe__metric">
      <span className="tiny muted">{k}</span>
      <span className={`probe__metric-v ${tone ? `tone--${tone}` : ""}`}>{v}</span>
    </div>
  );
}

function ProbeList({
  label,
  items,
  emphasize,
}: {
  label: string;
  items: string[];
  emphasize?: boolean;
}) {
  if (!items || items.length === 0) return null;
  return (
    <div className={`probe__list ${emphasize ? "probe__list--bound" : ""}`}>
      <span className="probe__list-label tiny">{label}</span>
      <ul>
        {items.map((it, i) => (
          <li key={i}>{it}</li>
        ))}
      </ul>
    </div>
  );
}
