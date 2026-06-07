import { api } from "../api/client";
import { useAsync } from "../hooks/useAsync";
import { navigate } from "../routing";
import {
  deriveStoryShelfFocus,
  deriveStoryShelfSpotlight,
  type StoryShelfActionKey,
  type StoryShelfJourneyKey,
} from "../storyShelfFocus";
import { StoryCoverThumb } from "./VisualAssetPanel";
import { EmptyState, ErrorState, Loading } from "./common/States";
import "./storyEntry.css";

export function StoryEntryPage() {
  const { data, loading, error, reload } = useAsync(() => api.listStories(), []);

  const stories = data?.stories ?? [];
  const builtin = stories.filter((s) => s.source_kind === "builtin");
  const imported = stories.filter((s) => s.source_kind === "imported");
  const spotlight = deriveStoryShelfSpotlight(
    [...imported, ...builtin].map((s) => ({
      slug: s.slug,
      displayName: s.display_name,
      sourceKind: s.source_kind,
      runCount: s.run_count,
    })),
  );

  return (
    <div className="entry">
      <section className="entry__hero">
        <div className="entry__hero-copy">
          <p className="entry__eyebrow muted">未终章 · 世界书架</p>
          <h1 className="entry__title">进入一个仍会运行的小说世界</h1>
          <p className="entry__lede muted">
            这里不是把故事改成你指定的答案，而是把变量投进世界：
            角色会按欲望、记忆、误会和利益行动，世界会吸收、抵抗、代偿，再生成可继续阅读的卷宗。
          </p>
        </div>
        {spotlight && <StorySpotlightCard spotlight={spotlight} />}
        <div className="entry__journey" aria-label="世界沙盘主链路">
          <JourneyStep index="一" title="确认天命" desc="先看世界的锚点、吸引子和干预边界。" />
          <JourneyStep index="二" title="运行沙盘" desc="投放大事件或读者干预，让角色自己动起来。" />
          <JourneyStep index="三" title="阅读卷宗" desc="按连续正文、角色个人卷和事件多视角回看结果。" />
          <JourneyStep index="四" title="采纳续写" desc="把沙盘涌现剧情整理成下一章材料。" />
        </div>
      </section>

      <section className="entry__starts">
        <StartCard
          seal="样"
          title="内置样例"
          desc="直接进入一部已有世界，从天命书开始体验沙盘、干预、卷宗阅读和作者采纳。"
          action="打开样例世界"
          tone="jade"
          disabled={builtin.length === 0}
          onClick={() => {
            const first = builtin[0] ?? stories[0];
            if (first) navigate({ name: "tianming", slug: first.slug });
          }}
        />
        <StartCard
          seal="纳"
          title="导入小说"
          desc="把已有章节带进本地，抽取角色、规则、伏笔和正史，再进入世界锚定。"
          action="导入小说"
          tone="gold"
          onClick={() => navigate({ name: "import" })}
        />
        <StartCard
          seal="创"
          title="主题创世"
          desc="从题材、主角和冲突开始生成一个新世界，再让它进入同一套沙盘链路。"
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
            hint="先导入一段小说，或用主题创世生成一个新世界。完成后会从世界锚定进入天命书和沙盘。"
          />
        )}
        {!loading && !error && stories.length > 0 && (
          <div className="story-grid">
            {[...imported, ...builtin].map((s) => {
              const focus = deriveStoryShelfFocus({
                sourceKind: s.source_kind,
                runCount: s.run_count,
              });
              const openRecommended = () =>
                navigateStoryRecommendation(s.slug, focus.recommendedKey);
              return (
                <div key={s.slug} className="story-card">
                  <button className="story-card__open" onClick={openRecommended}>
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
                    <div className="story-card__status">
                      <span className={`story-card__stage story-card__stage--${focus.stageTone}`}>
                        {focus.stageLabel}
                      </span>
                      <span className="story-card__source tiny">{focus.sourceLabel}</span>
                    </div>
                    <p className="story-card__brief muted">{focus.stageDescription}</p>
                    <div
                      className="story-card__metrics"
                      aria-label={`${s.display_name} 的世界状态`}
                    >
                      {focus.metrics.map((metric) => (
                        <span key={metric.label}>
                          <strong>{metric.value}</strong>
                          <small>{metric.label}</small>
                        </span>
                      ))}
                    </div>
                    <div className="story-card__meta muted tiny">
                      <span className="mono">{s.slug}</span>
                    </div>
                  </button>
                  <button className="story-card__primary" onClick={openRecommended}>
                    {focus.recommendedAction}
                  </button>
                  <div className="story-card__foot">
                    <button
                      className="story-card__link"
                      onClick={() => navigate({ name: "sandbox", slug: s.slug })}
                    >
                      世界沙盘
                    </button>
                    <button
                      className="story-card__link"
                      onClick={() => navigate({ name: "tianming", slug: s.slug })}
                    >
                      天命书
                    </button>
                    <button
                      className="story-card__link"
                      onClick={() =>
                        navigate({
                          name: "dossierReading",
                          slug: s.slug,
                          worldlineId: "main",
                        })
                      }
                    >
                      卷宗阅读
                    </button>
                    <button
                      className="story-card__link"
                      onClick={() => navigate({ name: "author", slug: s.slug })}
                    >
                      作者采纳台
                    </button>
                    <button
                      className="story-card__link"
                      onClick={() => navigate({ name: "workspace", slug: s.slug })}
                    >
                      机制档案
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

function navigateStoryRecommendation(slug: string, key: StoryShelfActionKey) {
  if (key === "reading") {
    navigate({ name: "dossierReading", slug, worldlineId: "main" });
    return;
  }
  navigate({ name: "tianming", slug });
}

function navigateStoryJourney(slug: string, key: StoryShelfJourneyKey) {
  if (key === "sandbox") {
    navigate({ name: "sandbox", slug });
    return;
  }
  if (key === "reading") {
    navigate({ name: "dossierReading", slug, worldlineId: "main" });
    return;
  }
  if (key === "author") {
    navigate({ name: "author", slug });
    return;
  }
  navigate({ name: "tianming", slug });
}

function StorySpotlightCard({
  spotlight,
}: {
  spotlight: NonNullable<ReturnType<typeof deriveStoryShelfSpotlight>>;
}) {
  const openRecommended = () =>
    navigateStoryRecommendation(spotlight.slug, spotlight.focus.recommendedKey);

  return (
    <aside className="entry__spotlight" aria-label="推荐进入的故事世界">
      <div className="entry__spotlight-cover">
        <StoryCoverThumb slug={spotlight.slug} seal={spotlight.seal} />
      </div>
      <div className="entry__spotlight-body">
        <p className="entry__spotlight-kicker muted">推荐进入 · {spotlight.priorityLabel}</p>
        <h2 className="entry__spotlight-title">{spotlight.displayName}</h2>
        <div className="entry__spotlight-status">
          <span className={`story-card__stage story-card__stage--${spotlight.focus.stageTone}`}>
            {spotlight.focus.stageLabel}
          </span>
          <span
            className={`badge ${
              spotlight.sourceKind === "imported" ? "badge--indigo" : "badge--jade"
            }`}
          >
            {spotlight.focus.sourceLabel}
          </span>
        </div>
        <p className="entry__spotlight-reason muted">{spotlight.spotlightReason}</p>
        <div className="entry__spotlight-pulse" aria-label="推荐世界的旅程状态">
          {spotlight.focus.journeyPulse.map((pulse) => (
            <button
              key={pulse.key}
              className={`entry__spotlight-pulse-card is-${pulse.status}`}
              onClick={() => navigateStoryJourney(spotlight.slug, pulse.key)}
              title={pulse.hint}
              type="button"
            >
              <small>{pulse.label}</small>
              <strong>{pulse.title}</strong>
              <span>{pulse.hint}</span>
            </button>
          ))}
        </div>
        <div className="entry__spotlight-metrics">
          {spotlight.focus.metrics.map((metric) => (
            <span key={metric.label}>
              <strong>{metric.value}</strong>
              <small>{metric.label}</small>
            </span>
          ))}
        </div>
        <button className="entry__spotlight-primary" onClick={openRecommended}>
          {spotlight.focus.recommendedAction}
        </button>
        <div className="entry__spotlight-links">
          <button onClick={() => navigate({ name: "sandbox", slug: spotlight.slug })}>
            世界沙盘
          </button>
          <button
            onClick={() =>
              navigate({
                name: "dossierReading",
                slug: spotlight.slug,
                worldlineId: "main",
              })
            }
          >
            卷宗阅读
          </button>
          <button onClick={() => navigate({ name: "workspace", slug: spotlight.slug })}>
            机制档案
          </button>
        </div>
      </div>
    </aside>
  );
}

function JourneyStep({
  index,
  title,
  desc,
}: {
  index: string;
  title: string;
  desc: string;
}) {
  return (
    <article className="journey-step">
      <span aria-hidden>{index}</span>
      <strong>{title}</strong>
      <p className="muted">{desc}</p>
    </article>
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
