import type { ReactNode } from "react";
import "./worldRunway.css";

export interface WorldRunwayStep {
  label: string;
  detail: string;
  active?: boolean;
  onClick?: () => void;
}

export interface WorldRunwayAction {
  label: string;
  detail: string;
  primary?: boolean;
  onClick: () => void;
}

export function WorldRunway({
  eyebrow,
  title,
  summary,
  meta,
  steps,
  actions,
}: {
  eyebrow: string;
  title: string;
  summary: string;
  meta?: ReactNode;
  steps: WorldRunwayStep[];
  actions: WorldRunwayAction[];
}) {
  return (
    <section className="world-runway" aria-label="世界内部导览">
      <div className="world-runway__intro">
        <p className="world-runway__eyebrow muted">{eyebrow}</p>
        <h2>{title}</h2>
        <p className="muted">{summary}</p>
        {meta && <div className="world-runway__meta">{meta}</div>}
      </div>

      <ol className="world-runway__steps">
        {steps.map((step, index) => (
          <li key={`${step.label}-${index}`}>
            <button
              className={step.active ? "is-active" : ""}
              disabled={!step.onClick}
              onClick={step.onClick}
              type="button"
            >
              <span>{index + 1}</span>
              <strong>{step.label}</strong>
              <small>{step.detail}</small>
            </button>
          </li>
        ))}
      </ol>

      <div className="world-runway__actions">
        {actions.map((action) => (
          <button
            key={action.label}
            className={`world-runway__action ${action.primary ? "is-primary" : ""}`}
            onClick={action.onClick}
            type="button"
          >
            <strong>{action.label}</strong>
            <small>{action.detail}</small>
          </button>
        ))}
      </div>
    </section>
  );
}
