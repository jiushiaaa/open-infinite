import { useState } from "react";
import type {
  AnchorCharacter,
  AnchorPatch,
  ProjectHealth,
  VisualAssets,
  WorldAnchor,
} from "../api/types";
import { ApiError, api } from "../api/client";
import { useAsync } from "../hooks/useAsync";
import { navigate } from "../routing";
import { BaselineCanonPanel } from "./BaselineCanonPanel";
import { CharacterProbePanel } from "./CharacterProbePanel";
import { CharacterAvatar, VisualAssetsControls } from "./VisualAssetPanel";
import { EmptyState, ErrorState, Loading } from "./common/States";
import "./worldAnchor.css";

const ROLE_LABEL: Record<string, string> = {
  protagonist: "主角",
  protagonist_candidate: "主角候选",
  antagonist: "对立面",
  supporting: "配角",
};

interface CharDraft {
  boundaries: string[];
  location: string;
  emotion: string;
}
interface ThreadDraft {
  id?: string;
  title: string;
  description: string;
  status: string;
}
interface Draft {
  rules: string[];
  scene: string;
  threads: ThreadDraft[];
  chars: Record<string, CharDraft>;
}

function initDraft(a: WorldAnchor): Draft {
  const chars: Record<string, CharDraft> = {};
  for (const c of a.characters) {
    chars[c.id] = {
      boundaries: [...c.persona.boundaries],
      location: c.current_state.location,
      emotion: c.current_state.emotion,
    };
  }
  return {
    rules: [...a.world.rules],
    scene: a.world.scene_description,
    threads: a.open_threads.map((t) => ({
      id: t.id,
      title: t.title,
      description: t.description,
      status: t.status,
    })),
    chars,
  };
}

export function WorldAnchorPage({ slug }: { slug: string }) {
  const anchorReq = useAsync(() => api.getWorldAnchor(slug), [slug]);
  const healthReq = useAsync(() => api.getProjectHealth(slug), [slug]);
  const visualReq = useAsync(() => api.getVisualAssets(slug), [slug]);

  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveErr, setSaveErr] = useState<string | null>(null);
  const [savedMsg, setSavedMsg] = useState<string | null>(null);

  const data = anchorReq.data;
  const health = healthReq.data;

  if (anchorReq.loading) return <Loading label="正在锚定世界…" />;
  if (anchorReq.error) return <ErrorState message={anchorReq.error} onRetry={anchorReq.reload} />;
  if (!data) return <EmptyState title="世界数据为空" />;

  const yamlBroken = health?.status === "error";
  const editable = data.source_kind !== "builtin" && !yamlBroken;

  function startEdit() {
    if (!data) return;
    setDraft(initDraft(data));
    setSaveErr(null);
    setSavedMsg(null);
    setEditing(true);
  }
  function discard() {
    setEditing(false);
    setDraft(null);
    setSaveErr(null);
  }
  async function save() {
    if (!draft) return;
    setSaving(true);
    setSaveErr(null);
    setSavedMsg(null);
    const patch: AnchorPatch = {
      world: {
        rules: draft.rules.map((r) => r.trim()).filter(Boolean),
        scene_description: draft.scene,
      },
      characters: Object.entries(draft.chars).map(([id, c]) => ({
        id,
        persona: { boundaries: c.boundaries.map((b) => b.trim()).filter(Boolean) },
        current_state: { location: c.location, emotion: c.emotion },
      })),
      open_threads: draft.threads
        .filter((t) => t.title.trim())
        .map((t) => ({
          id: t.id,
          title: t.title.trim(),
          description: t.description,
          status: t.status || "open",
        })),
    };
    try {
      await api.updateWorldAnchor(slug, patch);
      setEditing(false);
      setDraft(null);
      setSavedMsg("锚定已保存");
      anchorReq.reload();
      healthReq.reload();
    } catch (err) {
      if (err instanceof ApiError) setSaveErr(err.message);
      else setSaveErr(err instanceof Error ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  const patchDraft = (fn: (d: Draft) => Draft) =>
    setDraft((prev) => (prev ? fn(prev) : prev));

  return (
    <div className="anchor">
      <aside className="anchor__left">
        <LeftColumn
          data={data}
          health={health}
          editing={editing}
          editable={editable}
          saving={saving}
          saveErr={saveErr}
          savedMsg={savedMsg}
          onEdit={startEdit}
          onSave={save}
          onDiscard={discard}
          visual={visualReq.data}
          visualLoading={visualReq.loading}
          onVisualReload={visualReq.reload}
        />
      </aside>
      <section className="anchor__center">
        <CenterColumn data={data} editing={editing} draft={draft} patch={patchDraft} />
      </section>
      <aside className="anchor__right">
        <h2 className="anchor__col-title">
          角色 <span className="muted tiny">{data.characters.length}</span>
        </h2>
        <p className="muted tiny anchor__hint">
          人设边界决定了角色为什么不会无条件服从干预。
        </p>
        {data.characters.length === 0 ? (
          <EmptyState title="尚无角色" />
        ) : (
          data.characters.map((c) => (
            <CharacterCard
              key={c.id}
              slug={data.slug}
              c={c}
              editing={editing}
              draft={draft?.chars[c.id]}
              patch={patchDraft}
              visual={visualReq.data}
            />
          ))
        )}
      </aside>
    </div>
  );
}

// ── 健康徽标 ─────────────────────────────────────────────

function HealthBadge({ health }: { health?: ProjectHealth | null }) {
  if (!health) return null;
  const map: Record<string, { cls: string; label: string }> = {
    ok: { cls: "badge--jade", label: "锚定正常" },
    warning: { cls: "badge--gold", label: "有警告" },
    error: { cls: "badge--cinnabar", label: "YAML 损坏" },
  };
  const m = map[health.status] ?? map.ok;
  return <span className={`badge ${m.cls} tiny`}>{m.label}</span>;
}

// ── 左栏 ─────────────────────────────────────────────────

function LeftColumn({
  data,
  health,
  editing,
  editable,
  saving,
  saveErr,
  savedMsg,
  onEdit,
  onSave,
  onDiscard,
  visual,
  visualLoading,
  onVisualReload,
}: {
  data: WorldAnchor;
  health?: ProjectHealth | null;
  editing: boolean;
  editable: boolean;
  saving: boolean;
  saveErr: string | null;
  savedMsg: string | null;
  onEdit: () => void;
  onSave: () => void;
  onDiscard: () => void;
  visual?: VisualAssets | null;
  visualLoading: boolean;
  onVisualReload: () => void;
}) {
  const w = data.world;
  const brokenFiles = health
    ? Object.entries(health.files)
        .filter(([, st]) => st === "error")
        .map(([f]) => f)
    : [];
  return (
    <div>
      <div className="anchor__brand">
        <h1 className="anchor__name">{data.display_name}</h1>
        <span
          className={`badge ${data.source_kind === "imported" ? "badge--indigo" : "badge--jade"}`}
        >
          {data.source_kind === "imported" ? "项目" : "内置"}
        </span>
      </div>
      <p className="muted tiny mono anchor__slug">{data.slug}</p>

      <section className="anchor__launch" aria-label="启动世界">
        <div>
          <span className="muted tiny">世界启动</span>
          <strong>先确认天命，再让角色行动</strong>
          <p className="muted tiny">
            锚定页负责校准设定；真正体验从天命书、沙盘和卷宗阅读继续。
          </p>
        </div>
        <div className="anchor__launch-actions">
          <button
            className="btn btn--primary tiny"
            onClick={() => navigate({ name: "tianming", slug: data.slug })}
          >
            天命书
          </button>
          <button
            className="btn btn--ghost tiny"
            onClick={() => navigate({ name: "sandbox", slug: data.slug })}
          >
            世界沙盘
          </button>
          <button
            className="btn btn--ghost tiny"
            onClick={() =>
              navigate({
                name: "dossierReading",
                slug: data.slug,
                worldlineId: "main",
              })
            }
          >
            卷宗阅读
          </button>
        </div>
      </section>

      <WorldDossierGateway data={data} compact />

      <VisualAssetsControls
        slug={data.slug}
        visual={visual}
        loading={visualLoading}
        onReload={onVisualReload}
      />

      <BaselineCanonPanel slug={data.slug} sourceKind={data.source_kind} />

      <div className="anchor__health">
        <HealthBadge health={health} />
        {savedMsg && <span className="anchor__saved tiny">{savedMsg}</span>}
      </div>
      {health?.status === "error" && (
        <div className="anchor__broken">
          <p className="tiny">以下文件无法解析，编辑已禁用：</p>
          <ul>
            {brokenFiles.map((f) => (
              <li key={f} className="mono tiny">{f}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="anchor__editbar">
        {!editing && editable && (
          <button className="btn btn--ghost tiny" onClick={onEdit}>
            编辑锚定
          </button>
        )}
        {!editing && data.source_kind === "builtin" && (
          <span className="muted tiny">内置样例只读</span>
        )}
        {editing && (
          <>
            <button className="btn btn--primary tiny" onClick={onSave} disabled={saving}>
              {saving ? "保存中…" : "保存锚定"}
            </button>
            <button className="btn btn--ghost tiny" onClick={onDiscard} disabled={saving}>
              放弃修改
            </button>
          </>
        )}
      </div>
      {saveErr && <p className="anchor__save-err tiny">{saveErr}</p>}

      <div className="anchor__facts">
        <Fact k="叙事场所" v={w.canonical_place_name} />
        <Fact k="来源类型" v={w.source_type} />
        <Fact
          k="当前章节"
          v={w.current_chapter != null ? `第 ${w.current_chapter} 章` : "—"}
        />
        <Fact k="分歧节点" v={data.divergence_point} />
        <Fact k="世界线运行" v={`${data.run_count} 次`} />
      </div>

      <section className="anchor__block">
        <h3 className="anchor__block-title">实体别名</h3>
        <AliasSummary data={data.entity_aliases} />
      </section>

      <section className="anchor__block">
        <h3 className="anchor__block-title">世界合约</h3>
        {data.story_contract ? (
          <pre className="anchor__contract mono">
            {JSON.stringify(data.story_contract, null, 2)}
          </pre>
        ) : (
          <p className="muted tiny">未声明显式合约（story_contract.yaml 不存在）。</p>
        )}
      </section>

      <button
        className="btn btn--primary anchor__back"
        onClick={() => navigate({ name: "tianming", slug: data.slug })}
      >
        进入天命书
      </button>
    </div>
  );
}

// ── 中栏 ─────────────────────────────────────────────────

function CenterColumn({
  data,
  editing,
  draft,
  patch,
}: {
  data: WorldAnchor;
  editing: boolean;
  draft: Draft | null;
  patch: (fn: (d: Draft) => Draft) => void;
}) {
  const w = data.world;
  return (
    <div className="anchor__scroll">
      <WorldDossierGateway data={data} />

      {data.import_review && (
        <section className="anchor__block">
          <ImportReviewPanel review={data.import_review} />
        </section>
      )}

      <section className="anchor__block">
        <h3 className="anchor__block-title">世界规则</h3>
        {editing && draft ? (
          <StringListEditor
            items={draft.rules}
            placeholder="一条世界规则"
            onChange={(rules) => patch((d) => ({ ...d, rules }))}
          />
        ) : w.rules.length === 0 ? (
          <p className="muted tiny">未声明世界规则。</p>
        ) : (
          <ul className="anchor__rules">
            {w.rules.map((r, i) => (
              <li key={i} className="anchor__rule">{r}</li>
            ))}
          </ul>
        )}
      </section>

      <section className="anchor__block">
        <h3 className="anchor__block-title">此刻场景</h3>
        {editing && draft ? (
          <textarea
            className="anchor__edit-textarea"
            value={draft.scene}
            rows={4}
            onChange={(e) => patch((d) => ({ ...d, scene: e.target.value }))}
          />
        ) : w.scene_description ? (
          <p className="anchor__scene">{w.scene_description}</p>
        ) : (
          <p className="muted tiny">未声明场景。</p>
        )}
      </section>

      <section className="anchor__block">
        <h3 className="anchor__block-title">地点</h3>
        {w.locations.length === 0 ? (
          <p className="muted tiny">未声明地点。</p>
        ) : (
          <div className="anchor__locs">
            {w.locations.map((l, i) => (
              <div key={l.id || i} className="anchor__loc">
                <span className="anchor__loc-name">{l.name || l.id}</span>
                {l.description && <span className="muted tiny">{l.description}</span>}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="anchor__block">
        <h3 className="anchor__block-title">势力</h3>
        {w.factions.length === 0 ? (
          <p className="muted tiny">未声明势力。</p>
        ) : (
          <div className="chip-row">
            {w.factions.map((f, i) => (
              <button
                key={i}
                className="badge anchor__faction-link"
                onClick={() =>
                  navigate({
                    name: "factionVolume",
                    slug: data.slug,
                    worldlineId: "main",
                    factionId: f,
                  })
                }
                type="button"
              >
                {f}
              </button>
            ))}
          </div>
        )}
      </section>

      <section className="anchor__block">
        <h3 className="anchor__block-title">开放伏笔</h3>
        {editing && draft ? (
          <ThreadsEditor
            threads={draft.threads}
            onChange={(threads) => patch((d) => ({ ...d, threads }))}
          />
        ) : data.open_threads.length === 0 ? (
          <EmptyState title="尚无开放伏笔" />
        ) : (
          <ul className="anchor__threads">
            {data.open_threads.map((t) => (
              <li key={t.id} className="anchor__thread">
                <div className="anchor__thread-head">
                  <span className="anchor__thread-title">{t.title}</span>
                  <span className="badge tiny">{t.status}</span>
                </div>
                {t.description && (
                  <p className="muted tiny anchor__thread-desc">{t.description}</p>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="anchor__block">
        <h3 className="anchor__block-title">章节摘要</h3>
        {data.summaries.length === 0 ? (
          <EmptyState title="尚无章节摘要" hint="summaries/ 目录不存在。" />
        ) : (
          <ul className="anchor__summaries">
            {data.summaries.map((s, i) => (
              <li key={i} className="anchor__summary">
                <span className="anchor__thread-title">
                  {s.chapter != null ? `第${s.chapter}章 · ` : ""}
                  {s.title}
                </span>
                {s.summary && <p className="muted tiny">{s.summary}</p>}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function WorldDossierGateway({
  data,
  compact = false,
}: {
  data: WorldAnchor;
  compact?: boolean;
}) {
  const worldlineId = "main";
  const portals = [
    {
      key: "tianming",
      label: "天命书",
      title: "先看世界宪法",
      desc: "确认锚点、合约压力和干预边界，避免角色变成无条件执行命令的工具。",
      meta: `${data.open_threads.length} 条伏笔`,
      action: "确认天命",
      primary: true,
      onClick: () => navigate({ name: "tianming", slug: data.slug }),
    },
    {
      key: "sandbox",
      label: "世界沙盘",
      title: "让角色自己行动",
      desc: "投放事件或干预，观察角色基于欲望、记忆、误判和利益做出的选择。",
      meta: `${data.characters.length} 个角色`,
      action: "运行一轮",
      onClick: () => navigate({ name: "sandbox", slug: data.slug }),
    },
    {
      key: "reading",
      label: "卷宗阅读",
      title: "像读小说一样进入结果",
      desc: "连续正文、误会图谱、证据锚点和多卷宗视角都在这里汇合。",
      meta:
        data.world.current_chapter != null
          ? `第 ${data.world.current_chapter} 章`
          : "主线卷",
      action: "开始阅读",
      onClick: () =>
        navigate({ name: "dossierReading", slug: data.slug, worldlineId }),
    },
    {
      key: "worldline",
      label: "世界线",
      title: "检查分支和代偿",
      desc: "看当前世界线是否还能继续、因果债压在哪里、最近检查点发生了什么。",
      meta: `${data.run_count} 次运行`,
      action: "查看世界线",
      onClick: () => navigate({ name: "worldline", slug: data.slug, worldlineId }),
    },
    {
      key: "lens",
      label: "多视角",
      title: "拆开同一事件的信息差",
      desc: "生成世界正史、主锚点、角色个人卷、势力卷和事件多视角，找出谁误会了谁。",
      meta: `${data.world.factions.length} 个势力`,
      action: "生成视角",
      onClick: () => navigate({ name: "lens", slug: data.slug }),
    },
    {
      key: "author",
      label: "作者台",
      title: "把涌现剧情写成下一章",
      desc: "采纳沙盘结果，生成 brief、草稿、Reviewer 修订和确认入卷材料。",
      meta: "定稿入口",
      action: "进入作者台",
      onClick: () => navigate({ name: "author", slug: data.slug }),
    },
  ];
  return (
    <section
      className={`anchor__dossier-gateway ${
        compact ? "anchor__dossier-gateway--compact" : "anchor__dossier-gateway--full"
      }`}
      aria-label="世界卷宗总览"
    >
      <div className="anchor__gateway-head">
        <div>
          <span className="muted tiny">世界卷宗总览</span>
          <h2>从这里选择你要如何理解这个世界</h2>
        </div>
        <button
          className="btn btn--ghost tiny"
          onClick={() => navigate({ name: "workspace", slug: data.slug })}
        >
          机制档案
        </button>
      </div>
      <div className="anchor__gateway-flow" aria-label="推荐路径">
        <span>定界</span>
        <span>运行</span>
        <span>阅读</span>
        <span>采纳</span>
      </div>
      <div className="anchor__portal-grid">
        {portals.map((portal) => (
          <button
            key={portal.key}
            className={`anchor__portal ${portal.primary ? "anchor__portal--primary" : ""}`}
            onClick={portal.onClick}
          >
            <span className="anchor__portal-label">{portal.label}</span>
            <strong>{portal.title}</strong>
            <small>{portal.desc}</small>
            <em>
              <span>{portal.meta}</span>
              <span>{portal.action}</span>
            </em>
          </button>
        ))}
      </div>
    </section>
  );
}

function ImportReviewPanel({
  review,
}: {
  review: NonNullable<WorldAnchor["import_review"]>;
}) {
  const summary = review.summary;
  const source = summary.source?.type ? sourceLabel(summary.source.type) : "未知来源";
  const risks = review.quality_risks ?? [];
  const actions = review.recommended_actions ?? [];
  const previews = review.chapter_previews ?? [];
  return (
    <div className="anchor__import-review">
      <div className="anchor__import-head">
        <div>
          <h3 className="anchor__block-title anchor__block-title--plain">导入检查</h3>
          <p className="muted tiny">
            {source} · {summary.total_chapters} 章 · {summary.total_characters} 字
          </p>
        </div>
        <span className={`badge tiny ${review.status === "ready" ? "badge--jade" : "badge--gold"}`}>
          {reviewStatusLabel(review.status)}
        </span>
      </div>

      <div className="anchor__import-metrics">
        <Fact k="可先体验" v={`前 ${summary.playable_chapter_limit} 章`} />
        <Fact
          k="平均字数"
          v={
            summary.chapter_stats?.average_characters != null
              ? `${summary.chapter_stats.average_characters} 字`
              : "—"
          }
        />
        <Fact k="风险数" v={`${risks.length}`} />
      </div>

      {risks.length === 0 ? (
        <p className="anchor__import-ok tiny">未发现明显导入质量风险。</p>
      ) : (
        <ul className="anchor__import-risks">
          {risks.map((risk) => (
            <li key={`${risk.code}-${risk.message}`}>
              <span className={`anchor__risk-dot anchor__risk-dot--${risk.level}`} />
              <span>{risk.message}</span>
            </li>
          ))}
        </ul>
      )}

      {review.warnings.length > 0 && (
        <div className="anchor__import-warnings">
          {review.warnings.map((w) => (
            <p key={w} className="tiny">{w}</p>
          ))}
        </div>
      )}

      <div className="anchor__preview-list">
        {previews.slice(0, 5).map((ch) => (
          <div key={`${ch.index}-${ch.source_path}`} className="anchor__preview">
            <div className="anchor__preview-title">
              <span>{ch.index != null ? `第${ch.index}章` : "章节"}</span>
              <strong>{ch.title || "未命名章节"}</strong>
              <em>{ch.characters} 字</em>
            </div>
            <p>{ch.preview || "暂无正文片段。"}</p>
          </div>
        ))}
      </div>

      {actions.length > 0 && (
        <div className="anchor__next-actions">
          <span className="muted tiny">下一步</span>
          {actions.slice(0, 3).map((action) => (
            <div key={action.kind} className="anchor__next-action">
              <strong>{action.label}</strong>
              <p className="muted tiny">{action.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function sourceLabel(source: string) {
  const map: Record<string, string> = {
    manual: "手动粘贴",
    txt: "txt 文件",
    md: "md 文件",
    zip: "zip 章节包",
    epub: "epub 文件",
    unknown: "未知来源",
  };
  return map[source] ?? source;
}

function reviewStatusLabel(status: string) {
  if (status === "ready") return "报告完整";
  if (status === "missing") return "报告缺失";
  if (status === "damaged") return "报告损坏";
  return status || "未知状态";
}

// ── 角色卡 ───────────────────────────────────────────────

function CharacterCard({
  slug,
  c,
  editing,
  draft,
  patch,
  visual,
}: {
  slug: string;
  c: AnchorCharacter;
  editing: boolean;
  draft?: CharDraft;
  patch: (fn: (d: Draft) => Draft) => void;
  visual?: VisualAssets | null;
}) {
  const setChar = (fn: (cd: CharDraft) => CharDraft) =>
    patch((d) => ({ ...d, chars: { ...d.chars, [c.id]: fn(d.chars[c.id]) } }));

  return (
    <div className="char-card">
      <div className="char-card__head char-card__head--avatar">
        <CharacterAvatar slug={slug} charId={c.id} name={c.name} visual={visual} />
        <div className="char-card__headtext">
          <span className="char-card__name">{c.name}</span>
          <span className="char-card__tagline">
            <span className="badge tiny">
              {ROLE_LABEL[c.narrative_role] ?? c.narrative_role}
            </span>
            {c.present_in_scene && <span className="badge badge--jade tiny">在场</span>}
          </span>
          <span className="muted tiny mono">{c.id}</span>
        </div>
      </div>

      {editing && draft ? (
        <div className="char-card__state-edit">
          <label className="char-card__field">
            <span className="tiny muted">位置</span>
            <input
              className="anchor__edit-input"
              value={draft.location}
              onChange={(e) => setChar((cd) => ({ ...cd, location: e.target.value }))}
            />
          </label>
          <label className="char-card__field">
            <span className="tiny muted">心境</span>
            <input
              className="anchor__edit-input"
              value={draft.emotion}
              onChange={(e) => setChar((cd) => ({ ...cd, emotion: e.target.value }))}
            />
          </label>
        </div>
      ) : (
        c.current_state.location && (
          <div className="char-card__state muted tiny">
            位置：{c.current_state.location}
            {c.current_state.emotion ? ` · 心境：${c.current_state.emotion}` : ""}
          </div>
        )
      )}

      {!editing && <Tags label="性格" items={c.persona.traits} />}
      {!editing && <Tags label="欲望" items={c.persona.desires} />}
      {!editing && <Tags label="恐惧" items={c.persona.fears} />}

      {!editing && (
        <div className="char-card__actions">
          <button
            className="btn btn--ghost tiny"
            onClick={() =>
              navigate({
                name: "characterVolume",
                slug,
                worldlineId: "main",
                characterId: c.id,
              })
            }
          >
            角色个人卷
          </button>
        </div>
      )}

      <div className="char-card__bounds">
        <span className="char-card__bounds-title">行为边界</span>
        {editing && draft ? (
          <StringListEditor
            items={draft.boundaries}
            placeholder="一条不会做的事"
            onChange={(boundaries) => setChar((cd) => ({ ...cd, boundaries }))}
          />
        ) : c.persona.boundaries.length > 0 ? (
          <ul>
            {c.persona.boundaries.map((b, i) => (
              <li key={i}>{b}</li>
            ))}
          </ul>
        ) : (
          <p className="muted tiny">未声明边界。</p>
        )}
      </div>

      {!editing && <CharacterProbePanel slug={slug} charId={c.id} />}
    </div>
  );
}

// ── 轻编辑控件 ───────────────────────────────────────────

function StringListEditor({
  items,
  placeholder,
  onChange,
}: {
  items: string[];
  placeholder?: string;
  onChange: (items: string[]) => void;
}) {
  return (
    <div className="list-edit">
      {items.map((v, i) => (
        <div key={i} className="list-edit__row">
          <input
            className="anchor__edit-input"
            value={v}
            placeholder={placeholder}
            onChange={(e) =>
              onChange(items.map((x, j) => (j === i ? e.target.value : x)))
            }
          />
          <button
            className="list-edit__del"
            onClick={() => onChange(items.filter((_, j) => j !== i))}
            title="删除"
          >
            ✕
          </button>
        </div>
      ))}
      <button className="btn btn--ghost tiny" onClick={() => onChange([...items, ""])}>
        + 添加一条
      </button>
    </div>
  );
}

function ThreadsEditor({
  threads,
  onChange,
}: {
  threads: ThreadDraft[];
  onChange: (t: ThreadDraft[]) => void;
}) {
  const upd = (i: number, fn: (t: ThreadDraft) => ThreadDraft) =>
    onChange(threads.map((t, j) => (j === i ? fn(t) : t)));
  return (
    <div className="list-edit">
      {threads.map((t, i) => (
        <div key={i} className="thread-edit">
          <div className="thread-edit__bar">
            <input
              className="anchor__edit-input"
              value={t.title}
              placeholder="伏笔标题"
              onChange={(e) => upd(i, (x) => ({ ...x, title: e.target.value }))}
            />
            <input
              className="anchor__edit-input thread-edit__status"
              value={t.status}
              placeholder="open"
              onChange={(e) => upd(i, (x) => ({ ...x, status: e.target.value }))}
            />
            <button
              className="list-edit__del"
              onClick={() => onChange(threads.filter((_, j) => j !== i))}
              title="删除"
            >
              ✕
            </button>
          </div>
          <textarea
            className="anchor__edit-textarea"
            value={t.description}
            rows={2}
            placeholder="伏笔说明"
            onChange={(e) => upd(i, (x) => ({ ...x, description: e.target.value }))}
          />
        </div>
      ))}
      <button
        className="btn btn--ghost tiny"
        onClick={() =>
          onChange([...threads, { title: "", description: "", status: "open" }])
        }
      >
        + 添加伏笔
      </button>
    </div>
  );
}

function Tags({ label, items }: { label: string; items: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="char-card__tags">
      <span className="char-card__tags-label">{label}</span>
      <span className="chip-row">
        {items.map((it, i) => (
          <span key={i} className="badge tiny">{it}</span>
        ))}
      </span>
    </div>
  );
}

function Fact({ k, v }: { k: string; v?: string }) {
  return (
    <div className="anchor__fact">
      <span className="anchor__fact-k muted tiny">{k}</span>
      <span className="anchor__fact-v">{v || "—"}</span>
    </div>
  );
}

function AliasSummary({ data }: { data?: WorldAnchor["entity_aliases"] }) {
  if (!data || data.status === "missing") {
    return <p className="muted tiny">尚未生成实体别名表。</p>;
  }
  if (data.status === "damaged") {
    return <p className="anchor__save-err tiny">实体别名表无法解析，检索会自动跳过。</p>;
  }
  return (
    <div className="anchor__aliases">
      <div className="anchor__alias-head">
        <span className="badge badge--jade tiny">已生成</span>
        <span className="muted tiny mono">{data.path}</span>
      </div>
      <p className="muted tiny">已登记 {data.count} 个实体，用于同名/别称检索归一。</p>
      {data.sample_entities.length > 0 && (
        <div className="chip-row">
          {data.sample_entities.map((e) => (
            <span key={e.entity_id} className="badge tiny">
              {e.canonical_name} · {e.alias_count}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
