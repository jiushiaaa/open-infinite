import type { InterventionCompilation } from "../api/types";
import { isAlternateNovel } from "../branchLabels";
import { EmptyState, Loading } from "./common/States";

const TYPE_LABEL: Record<string, string> = {
  information: "信息透露",
  forced_action: "强制行动",
  resource_injection: "资源注入",
  rule_rewrite: "规则改写",
};

const COMPAT_LABEL: Record<string, string> = {
  compatible: "兼容",
  partial: "部分兼容",
  incompatible: "不兼容",
};

const RISK_TONE: Record<string, string> = {
  low: "badge--jade",
  medium: "badge--gold",
  high: "badge--cinnabar",
};

export function CompilationPanel({
  compilation,
  loading,
}: {
  compilation: InterventionCompilation | null;
  loading: boolean;
}) {
  if (loading) return <Loading label="读取干预编译…" />;
  if (!compilation) {
    return (
      <EmptyState
        title="这条世界线没有干预编译"
        hint="正史 / 续写节点没有 intervention_compilation.json。"
      />
    );
  }

  const ai = compilation.abstract_intervention ?? {};
  const compat = compilation.compatibility ?? {};
  const real = compilation.realization ?? {};
  const axis = compilation.branch_axis ?? [];
  const scope = compilation.affected_scope ?? {};
  const au = isAlternateNovel(compilation.lineage_type);

  return (
    <div>
      {au && (
        <div className="fourth-wall-note" style={{ borderColor: "#9fb0c0", background: "var(--indigo-wash)", color: "#2f4153" }}>
          这不是普通分支，而是 Alternate Novel / AU 世界线。原世界线不会被静默污染。
        </div>
      )}

      <section className="expl-section">
        <h3 className="expl-section__title">系统理解</h3>
        <Row k="类型" v={TYPE_LABEL[ai.intervention_type ?? ""] ?? ai.intervention_type} />
        {ai.intent && <Row k="意图" v={ai.intent} />}
        {ai.target_refs && ai.target_refs.length > 0 && (
          <Row k="目标" v={ai.target_refs.join("、")} />
        )}
        {ai.desired_effect && <Row k="期望" v={ai.desired_effect} />}
      </section>

      <section className="expl-section">
        <h3 className="expl-section__title">世界观兼容性</h3>
        <div className="chip-row" style={{ marginBottom: 8 }}>
          <span className="badge">{COMPAT_LABEL[compat.status ?? ""] ?? compat.status ?? "未知"}</span>
          {compat.risk && (
            <span className={`badge ${RISK_TONE[compat.risk] ?? ""}`}>
              风险 · {compat.risk}
            </span>
          )}
        </div>
        {(compat.reasons ?? []).map((r, i) => (
          <p key={i} className="muted tiny" style={{ margin: "4px 0", lineHeight: 1.6 }}>
            · {r}
          </p>
        ))}
        {(compat.contract_conflicts ?? []).length > 0 && (
          <p className="tiny" style={{ color: "var(--cinnabar)", marginTop: 6 }}>
            合约冲突：{(compat.contract_conflicts ?? []).join("；")}
          </p>
        )}
      </section>

      {(real.mode || real.description) && (
        <section className="expl-section">
          <h3 className="expl-section__title">落地方式</h3>
          {real.mode && <Row k="模式" v={real.mode} />}
          {real.description && <Row k="说明" v={real.description} />}
          <Row k="在世界内" v={real.in_world ? "是" : "否（越出原世界）"} />
        </section>
      )}

      <section className="expl-section">
        <h3 className="expl-section__title">本次分支轴</h3>
        {axis.length === 0 ? (
          <p className="muted tiny">无动态分支轴。</p>
        ) : (
          <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
            {axis.map((a, i) => (
              <li key={a.id || i} className="trace-turn" style={{ borderLeftColor: "var(--jade-soft)" }}>
                <div style={{ fontFamily: "var(--font-serif)", fontSize: 14 }}>
                  {a.label}
                </div>
                {a.description && (
                  <div className="muted tiny" style={{ lineHeight: 1.55 }}>
                    {a.description}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="expl-section">
        <h3 className="expl-section__title">影响范围 · 世系</h3>
        <Row k="世系" v={compilation.lineage_type} />
        <ScopeRow label="角色" items={scope.characters} />
        <ScopeRow label="地点" items={scope.locations} />
        <ScopeRow label="物品" items={scope.items} />
        <ScopeRow label="规则" items={scope.rules} />
        <p className="muted tiny mono" style={{ marginTop: 8 }}>
          {compilation.source} · {compilation.compiler_version}
        </p>
      </section>
    </div>
  );
}

function Row({ k, v }: { k: string; v?: string | null }) {
  if (!v) return null;
  return (
    <div className="kv">
      <span className="kv__k">{k}</span>
      <span className="kv__v">{v}</span>
    </div>
  );
}

function ScopeRow({ label, items }: { label: string; items?: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="kv">
      <span className="kv__k">{label}</span>
      <span className="chip-row">
        {items.map((it) => (
          <span key={it} className="badge tiny">
            {it}
          </span>
        ))}
      </span>
    </div>
  );
}
