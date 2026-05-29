import { EmptyState } from "./common/States";

interface CharState {
  name?: string;
  location?: string;
  emotion?: string;
  emotion_changed_from?: string;
  narrative_role?: string;
  resources?: string[];
}

// 组件接口预留 previous / delta：当前版本用 state_snapshot 内的 *_changed_from
// 字段推导增量；未来接入前后快照 diff 时可替换数据源而不改 UI。
export function CharacterStatePanel({
  snapshot,
}: {
  snapshot: Record<string, unknown> | null;
}) {
  if (!snapshot) {
    return <EmptyState title="该分支尚无状态快照" hint="state_snapshot.json 缺失。" />;
  }

  const charsRaw = snapshot.characters;
  const chars: [string, CharState][] =
    charsRaw && typeof charsRaw === "object" && !Array.isArray(charsRaw)
      ? Object.entries(charsRaw as Record<string, CharState>)
      : [];

  const sceneFlags = snapshot.scene_flags;
  const flags =
    sceneFlags && typeof sceneFlags === "object"
      ? Object.entries(sceneFlags as Record<string, unknown>)
      : [];

  return (
    <div>
      <section className="expl-section">
        <h3 className="expl-section__title">角色现在怎么样</h3>
        {chars.length === 0 ? (
          <p className="muted tiny">快照中没有角色状态。</p>
        ) : (
          chars.map(([id, c]) => (
            <div key={id} className="state-card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <span className="state-card__name">{c.name || id}</span>
                <span className="state-card__role">{c.narrative_role}</span>
              </div>
              {c.location && (
                <div className="kv" style={{ marginTop: 6 }}>
                  <span className="kv__k">位置</span>
                  <span className="kv__v">{c.location}</span>
                </div>
              )}
              {c.emotion && (
                <div className="kv">
                  <span className="kv__k">心境</span>
                  <span className="kv__v">
                    {c.emotion_changed_from && c.emotion_changed_from !== c.emotion ? (
                      <>
                        <span className="muted">{c.emotion_changed_from}</span>
                        <span className="delta"> → {c.emotion}</span>
                      </>
                    ) : (
                      c.emotion
                    )}
                  </span>
                </div>
              )}
              {c.resources && c.resources.length > 0 && (
                <div className="chip-row" style={{ marginTop: 6 }}>
                  {c.resources.map((r, i) => (
                    <span key={i} className="badge tiny">
                      {r}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </section>

      {flags.length > 0 && (
        <section className="expl-section">
          <h3 className="expl-section__title">场景标记</h3>
          <div className="chip-row">
            {flags.map(([k, v]) => (
              <span key={k} className="badge tiny">
                {k}: {String(v)}
              </span>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
