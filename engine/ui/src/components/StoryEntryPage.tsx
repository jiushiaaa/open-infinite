import { api } from "../api/client";
import { useAsync } from "../hooks/useAsync";
import { navigate } from "../routing";
import { StoryCoverThumb } from "./VisualAssetPanel";
import { EmptyState, ErrorState, Loading } from "./common/States";
import "./storyEntry.css";

export function StoryEntryPage() {
  const { data, loading, error, reload } = useAsync(() => api.listStories(), []);

  const stories = data?.stories ?? [];
  const builtin = stories.filter((s) => s.source_kind === "builtin");
  const imported = stories.filter((s) => s.source_kind === "imported");

  return (
    <div className="entry">
      <section className="entry__hero">
        <p className="entry__eyebrow muted">活体小说引擎 · v0.7</p>
        <h1 className="entry__title">让你写下的一句话，被世界自行消化</h1>
        <p className="entry__lede muted">
          你施加变量，世界依据合约、角色人设、记忆与资源状态自行推演。
          每一次干预都会留下「旧现实」与「新世界线」的因果差异。
        </p>
      </section>

      <section className="entry__starts">
        <StartCard
          seal="样"
          title="内置样例"
          desc="点开即体验，推荐从《天荒城残夜》入手，无需准备任何素材。"
          action="进入样例"
          tone="jade"
          disabled={builtin.length === 0}
          onClick={() => {
            const first = builtin[0] ?? stories[0];
            if (first) navigate({ name: "workspace", slug: first.slug });
          }}
        />
        <StartCard
          seal="纳"
          title="导入小说"
          desc="粘贴 3–10 章 txt / md，抽取世界与角色后进入世界锚定。仅作本地个人探索，请遵守版权。"
          action="导入小说"
          tone="gold"
          onClick={() => navigate({ name: "import" })}
        />
        <StartCard
          seal="创"
          title="主题创世"
          desc="输入题材、主角与想看的味道，AI 生成首章、角色与初始合约，直接进入世界锚定。"
          action="主题创世"
          tone="cinnabar"
          onClick={() => navigate({ name: "genesis" })}
        />
      </section>

      <section className="entry__recent">
        <h2 className="entry__section-title">最近的故事</h2>
        {loading && <Loading label="正在读取故事书架…" />}
        {error && <ErrorState message={error} onRetry={reload} />}
        {!loading && !error && stories.length === 0 && (
          <EmptyState
            title="书架还空着"
            hint="点上方「导入小说」粘贴 3–10 章文本，或用 CLI 跑一次 intervene。"
          />
        )}
        {!loading && !error && stories.length > 0 && (
          <div className="story-grid">
            {[...imported, ...builtin].map((s) => (
              <div key={s.slug} className="story-card">
                <button
                  className="story-card__open"
                  onClick={() => navigate({ name: "workspace", slug: s.slug })}
                >
                  <StoryCoverThumb
                    slug={s.slug}
                    seal={s.display_name.slice(0, 1) || "书"}
                  />
                  <div className="story-card__head">
                    <span className="story-card__name">{s.display_name}</span>
                    <span
                      className={`badge ${
                        s.source_kind === "imported" ? "badge--indigo" : "badge--jade"
                      }`}
                    >
                      {s.source_kind === "imported" ? "导入" : "内置"}
                    </span>
                  </div>
                  <div className="story-card__meta muted tiny">
                    <span className="mono">{s.slug}</span>
                    <span>· {s.run_count} 条世界线运行</span>
                  </div>
                </button>
                <div className="story-card__foot">
                  <button
                    className="story-card__link"
                    onClick={() => navigate({ name: "workspace", slug: s.slug })}
                  >
                    进入阅读
                  </button>
                  <button
                    className="story-card__link"
                    onClick={() => navigate({ name: "anchor", slug: s.slug })}
                  >
                    世界锚定
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function StartCard({
  seal,
  title,
  desc,
  action,
  tone,
  disabled,
  onClick,
}: {
  seal: string;
  title: string;
  desc: string;
  action: string;
  tone: "jade" | "gold" | "cinnabar";
  disabled?: boolean;
  onClick?: () => void;
}) {
  return (
    <div className={`start-card start-card--${tone}`}>
      <div className="start-card__seal" aria-hidden>
        {seal}
      </div>
      <h3 className="start-card__title">{title}</h3>
      <p className="start-card__desc muted">{desc}</p>
      <button
        className={`btn ${disabled ? "" : "btn--primary"}`}
        disabled={disabled}
        onClick={onClick}
      >
        {action}
      </button>
    </div>
  );
}
