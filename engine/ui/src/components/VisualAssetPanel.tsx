import { type CSSProperties, useEffect, useState } from "react";
import type { AssetEntry, VisualAssets } from "../api/types";
import { ApiError, api, assetUrl } from "../api/client";
import fallbackCover from "../assets/generated/ink-landscape-desk.webp";
import fallbackArchivist from "../assets/generated/ink-portrait-archivist.png";
import fallbackGeneral from "../assets/generated/ink-portrait-general.png";
import fallbackScholar from "../assets/generated/ink-portrait-scholar.png";
import fallbackSwordwoman from "../assets/generated/ink-portrait-swordwoman.png";
import "./visualAssets.css";

function toMessage(e: unknown): string {
  if (e instanceof ApiError) return e.message;
  if (e instanceof Error) return e.message;
  return String(e);
}

const avatarFallbacks = [fallbackScholar, fallbackSwordwoman, fallbackGeneral, fallbackArchivist];

function fallbackIndex(seed: string): number {
  let hash = 0;
  for (const char of seed) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return hash % avatarFallbacks.length;
}

/** 资产图：ready 且有图则显示，否则显示古风占位；加载失败回退占位。 */
export function AssetImage({
  slug,
  entry,
  seal,
  variant,
  alt,
  fallbackSrc,
}: {
  slug: string;
  entry?: AssetEntry | null;
  seal: string;
  variant: "cover" | "avatar" | "scene";
  alt: string;
  fallbackSrc?: string;
}) {
  const [broken, setBroken] = useState(false);
  const ready = entry?.status === "ready" && Boolean(entry.path) && !broken;
  if (ready) {
    return (
      <img
        className={`vasset vasset--${variant} vasset--img`}
        src={assetUrl(slug, entry.path)}
        alt={alt}
        loading="lazy"
        onError={() => setBroken(true)}
      />
    );
  }
  const style = fallbackSrc
    ? ({ "--vasset-fallback": `url("${fallbackSrc}")` } as CSSProperties)
    : undefined;
  return (
    <div
      className={`vasset vasset--${variant} vasset--placeholder`}
      role="img"
      aria-label={`${alt}（暂无图像）`}
      style={style}
    >
      <span className="vasset__seal">{seal}</span>
    </div>
  );
}

/** 角色头像（小尺寸方形）。取角色名首字作为占位印记。 */
export function CharacterAvatar({
  slug,
  charId,
  name,
  visual,
}: {
  slug: string;
  charId: string;
  name: string;
  visual?: VisualAssets | null;
}) {
  const entry = visual?.characters?.[charId] ?? null;
  const fallbackSrc = avatarFallbacks[fallbackIndex(`${charId}:${name}`)];
  return (
    <AssetImage
      slug={slug}
      entry={entry}
      seal={name.slice(0, 1) || "角"}
      variant="avatar"
      alt={`${name} 头像`}
      fallbackSrc={fallbackSrc}
    />
  );
}

function summarize(va: VisualAssets): string {
  const entries: AssetEntry[] = [
    ...(va.cover ? [va.cover] : []),
    ...Object.values(va.characters),
    ...Object.values(va.scenes),
  ];
  if (entries.length === 0) return "尚未生成视觉资产。";
  const ready = entries.filter((e) => e.status === "ready").length;
  const failed = entries.filter((e) => e.status === "failed").length;
  const placeholder = entries.filter((e) => e.status === "placeholder").length;
  if (ready > 0 && failed === 0 && placeholder === 0) return `已生成 ${ready} 张图像。`;
  if (ready > 0) return `已生成 ${ready} 张图像，其余为占位或未成。`;
  if (failed > 0) return `生成未成功（${failed} 项），已保留占位。`;
  return "已生成古风占位。如需真实图像，请在设置中配置 Seedream 密钥后重新生成。";
}

/** 封面 + 生成控制区，放在世界锚定左栏。 */
export function VisualAssetsControls({
  slug,
  visual,
  loading,
  onReload,
}: {
  slug: string;
  visual?: VisualAssets | null;
  loading: boolean;
  onReload: () => void;
}) {
  const [working, setWorking] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function generate(force: boolean) {
    setWorking(true);
    setErr(null);
    try {
      await api.generateVisualAssets(slug, {
        kinds: ["cover", "characters", "scenes"],
        force,
      });
      onReload();
    } catch (e) {
      setErr(toMessage(e));
    } finally {
      setWorking(false);
    }
  }

  return (
    <section className="anchor__block vassets-panel">
      <h3 className="anchor__block-title">视觉资产</h3>
      <AssetImage
        slug={slug}
        entry={visual?.cover ?? null}
        seal={slug.slice(0, 1).toUpperCase() || "封"}
        variant="cover"
        alt="故事封面"
        fallbackSrc={fallbackCover}
      />
      <p className="muted tiny vassets-panel__hint">
        {loading ? "正在读取视觉资产…" : visual ? summarize(visual) : "暂无视觉资产。"}
      </p>
      <div className="vassets-panel__actions">
        <button
          className="btn btn--primary tiny"
          onClick={() => generate(false)}
          disabled={working}
        >
          {working ? "正在生成…" : "生成视觉资产"}
        </button>
        <button
          className="btn btn--ghost tiny"
          onClick={() => generate(true)}
          disabled={working}
          title="忽略已有图像，全部重新生成"
        >
          重新生成
        </button>
      </div>
      {err && <p className="anchor__save-err tiny">{err}</p>}
    </section>
  );
}

/** 故事书架封面缩略（自取数据，失败静默占位，不阻塞列表）。 */
export function StoryCoverThumb({ slug, seal }: { slug: string; seal: string }) {
  const [cover, setCover] = useState<AssetEntry | null>(null);
  useEffect(() => {
    let alive = true;
    api
      .getVisualAssets(slug)
      .then((va) => {
        if (alive) setCover(va.cover);
      })
      .catch(() => {
        if (alive) setCover(null);
      });
    return () => {
      alive = false;
    };
  }, [slug]);
  return (
    <AssetImage
      slug={slug}
      entry={cover}
      seal={seal}
      variant="cover"
      alt="故事封面"
      fallbackSrc={fallbackCover}
    />
  );
}
