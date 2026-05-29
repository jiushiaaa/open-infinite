import { EmptyState } from "./common/States";

interface Intent {
  actor_id?: string;
  intent_type?: string;
  visibility?: string;
}
interface TurnPlan {
  round_num?: number;
  actor_id?: string;
  intents?: Intent[];
  delayed_actions?: unknown[];
  relationship_signals?: { from_id?: string; to_id?: string; change?: string }[];
}
interface PrivateKnowledge {
  owner_id?: string;
  content?: string;
  revealed?: boolean;
}
interface Misunderstanding {
  holder_id?: string;
  about?: string;
  corrected?: boolean;
}

export function AgentTracePanel({
  trace,
}: {
  trace: Record<string, unknown> | null;
}) {
  if (!trace) {
    return (
      <EmptyState
        title="该分支没有 Agent 轨迹"
        hint="multi_agent_trace.json 缺失（仅 multi_agent runner 产出）。"
      />
    );
  }

  const turns = (trace.turn_plans as TurnPlan[]) ?? [];
  const pk = (trace.private_knowledge as PrivateKnowledge[]) ?? [];
  const mis = (trace.misunderstandings as Misunderstanding[]) ?? [];

  // 第四面墙提示：克制，仅在存在未纠正误解或已揭示隐秘时给一条短 warning。
  const awareSignal =
    Boolean(trace.fourth_wall) ||
    mis.some((m) => m && m.corrected === false) ||
    pk.some((k) => k && k.revealed);

  return (
    <div>
      {awareSignal && (
        <div className="fourth-wall-note">
          角色觉察上升：检测到异常叙事压力。
        </div>
      )}

      <section className="expl-section">
        <h3 className="expl-section__title">角色如何计划 / 隐瞒 / 延迟</h3>
        {turns.length === 0 ? (
          <p className="muted tiny">没有回合计划。</p>
        ) : (
          turns.map((t, i) => (
            <div key={i} className="trace-turn">
              <div className="tiny" style={{ fontWeight: 600 }}>
                第{t.round_num ?? "?"}回合 · {t.actor_id}
              </div>
              <div className="muted tiny">
                {(t.intents ?? [])
                  .map((it) => `${it.intent_type ?? "?"}(${it.visibility ?? "?"})`)
                  .join(" · ") || "无意图"}
                {t.delayed_actions && t.delayed_actions.length > 0
                  ? ` · 延迟行动 ${t.delayed_actions.length}`
                  : ""}
              </div>
              {(t.relationship_signals ?? []).length > 0 && (
                <div className="muted tiny">
                  关系：
                  {(t.relationship_signals ?? [])
                    .map((s) => `${s.from_id}→${s.to_id} ${s.change}`)
                    .join("，")}
                </div>
              )}
            </div>
          ))
        )}
      </section>

      {pk.length > 0 && (
        <section className="expl-section">
          <h3 className="expl-section__title">隐秘知识</h3>
          {pk.map((k, i) => (
            <div key={i} className="kv">
              <span className="kv__k">{k.owner_id}</span>
              <span className="kv__v">
                {k.content}
                {k.revealed && <span className="delta--down delta"> · 已揭示</span>}
              </span>
            </div>
          ))}
        </section>
      )}

      {mis.length > 0 && (
        <section className="expl-section">
          <h3 className="expl-section__title">误解</h3>
          {mis.map((m, i) => (
            <div key={i} className="kv">
              <span className="kv__k">{m.holder_id}</span>
              <span className="kv__v">
                {m.about}
                {m.corrected ? (
                  <span className="delta"> · 已纠正</span>
                ) : (
                  <span className="delta delta--down"> · 未纠正</span>
                )}
              </span>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
