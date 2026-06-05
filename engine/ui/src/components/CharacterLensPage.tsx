import { useState } from "react";
import { api } from "../api/client";
import type { CharacterLensReport } from "../api/types";
import { navigate } from "../routing";
import { EmptyState, ErrorState } from "./common/States";
import "./characterLens.css";

const DEFAULT_EVENT = "风鸣铃现世，苍澜派诸峰各自隐瞒消息。";

const LENS_LABELS: Record<string, string> = {
  world_chronicle: "世界正史卷",
  anchor_volume: "主锚点卷",
  character_volume: "角色个人卷",
  faction_volume: "势力卷",
  event_multi_perspective: "事件多视角",
};

export function CharacterLensPage({ slug }: { slug: string }) {
  const [sourceEvent, setSourceEvent] = useState(DEFAULT_EVENT);
  const [characterId, setCharacterId] = useState("zhao_xuan");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<CharacterLensReport | null>(null);

  async function generateLens() {
    if (!sourceEvent.trim()) return;
    setLoading(true);
    setError(null);
    try {
      setReport(
        await api.generateCharacterLens(slug, {
          source_event: sourceEvent.trim(),
          character_id: characterId.trim(),
          worldline_id: "main",
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="lens-page">
      <header className="lens-hero">
        <div>
          <p className="lens-hero__eyebrow muted">世界内部卷宗 · 多视角活体小说</p>
          <h1>同一事件，分出不同的小说镜头</h1>
          <p className="muted">
            世界正史、主锚点、角色个人卷、势力卷和事件多视角共用同一份沙盘事实。
          </p>
        </div>
        <div className="lens-hero__actions">
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "sandbox", slug })}
          >
            世界沙盘
          </button>
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "author", slug })}
          >
            作者采纳台
          </button>
          <button
            className="btn btn--ghost"
            onClick={() => navigate({ name: "workspace", slug })}
          >
            世界正史卷
          </button>
        </div>
      </header>

      <div className="lens-layout">
        <aside className="lens-panel">
          <h2>事件材料</h2>
          <textarea
            value={sourceEvent}
            onChange={(event) => setSourceEvent(event.target.value)}
            rows={6}
            placeholder="写下要被多视角观察的事件"
          />
          <label>
            <span className="muted tiny">角色个人卷</span>
            <input
              value={characterId}
              onChange={(event) => setCharacterId(event.target.value)}
            />
          </label>
          <button
            className="btn btn--primary"
            disabled={loading || !sourceEvent.trim()}
            onClick={generateLens}
          >
            {loading ? "正在分镜…" : "生成多视角"}
          </button>
          {report && (
            <dl className="lens-proof">
              <div>
                <dt>沙盘</dt>
                <dd className="mono">{report.source.sandbox_run_id}</dd>
              </div>
              <div>
                <dt>写入</dt>
                <dd>{report.artifact}</dd>
              </div>
              <div>
                <dt>卷宗</dt>
                <dd>
                  {report.brief_count} 篇 brief
                  {report.volume_count ? ` / ${report.volume_count} 篇正文` : ""}
                </dd>
              </div>
              {report.artifacts.character_lens_volumes && (
                <div>
                  <dt>正文</dt>
                  <dd>{report.artifacts.character_lens_volumes}</dd>
                </div>
              )}
            </dl>
          )}
        </aside>

        <main className="lens-main">
          {error && <ErrorState message={error} onRetry={generateLens} />}
          {!error && !report && (
            <EmptyState
              title="还没有分镜"
              hint="写下一个事件，让同一份沙盘事实长出不同视角。"
            />
          )}
          {!error && report && (
            <>
              <section className="lens-section lens-source">
                <div>
                  <h2>事件源</h2>
                  <p>{report.source.source_event}</p>
                </div>
                <span className="badge badge--jade">{report.worldline_id}</span>
              </section>

              {report.volumes && report.volumes.length > 0 && (
                <section className="lens-volumes">
                  {report.volumes.map((volume) => (
                    <article className="lens-volume" key={volume.volume_type}>
                      <div className="lens-brief__head">
                        <span className="lens-brief__seal" aria-hidden>
                          {LENS_LABELS[volume.volume_type]?.slice(0, 1) ?? "卷"}
                        </span>
                        <div>
                          <h2>{LENS_LABELS[volume.volume_type] ?? volume.title}</h2>
                          {volume.character_name && (
                            <p className="muted tiny">{volume.character_name}</p>
                          )}
                        </div>
                        <span className="badge badge--gold">正文</span>
                      </div>
                      <p>{volume.prose}</p>
                      {volume.event_nodes && (
                        <div className="lens-perspectives">
                          {volume.event_nodes.map((node) => (
                            <div key={node.id}>
                              <strong>{node.title}</strong>
                              <p>{node.body}</p>
                              <span className="muted tiny">
                                {node.evidence_refs.join(" / ")}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                      {volume.information_gap?.canon_vs_character && (
                        <p className="muted tiny">
                          信息差：{volume.information_gap.canon_vs_character}
                        </p>
                      )}
                    </article>
                  ))}
                </section>
              )}

              <section className="lens-briefs">
                {report.briefs.map((brief) => (
                  <article className="lens-brief" key={brief.lens_type}>
                    <div className="lens-brief__head">
                      <span className="lens-brief__seal" aria-hidden>
                        {LENS_LABELS[brief.lens_type]?.slice(0, 1) ?? "卷"}
                      </span>
                      <div>
                        <h2>{LENS_LABELS[brief.lens_type] ?? brief.title}</h2>
                        {brief.character_name && (
                          <p className="muted tiny">{brief.character_name}</p>
                        )}
                      </div>
                      <span className="badge badge--gold">{brief.evidence.source as string}</span>
                    </div>
                    <p>{brief.body}</p>
                    {brief.perspectives && brief.perspectives.length > 0 && (
                      <div className="lens-perspectives">
                        {brief.perspectives.map((item) => (
                          <div key={item.character_id}>
                            <strong>{item.character_name}</strong>
                            <span className="muted tiny">{item.stance}</span>
                            <p>{item.voice}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </article>
                ))}
              </section>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
