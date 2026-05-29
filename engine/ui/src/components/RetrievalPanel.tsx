import { EmptyState } from "./common/States";

interface RetrievalItem {
  text?: string;
  content?: string;
  source?: string;
  kind?: string;
  score?: number;
}

export function RetrievalPanel({
  retrieval,
}: {
  retrieval: Record<string, unknown> | null;
}) {
  if (!retrieval) {
    return (
      <EmptyState
        title="该分支没有检索记忆"
        hint="retrieval_context.json 缺失（lightweight runner 常见）。"
      />
    );
  }

  const itemsRaw = retrieval.items;
  const items: RetrievalItem[] = Array.isArray(itemsRaw)
    ? (itemsRaw as RetrievalItem[])
    : [];

  return (
    <div>
      <section className="expl-section">
        <h3 className="expl-section__title">引擎引用了哪些正史 / 合约 / 摘要</h3>
        {items.length === 0 ? (
          <p className="muted tiny">没有检索条目。</p>
        ) : (
          items.map((it, i) => (
            <div key={i} className="retr-item">
              <div className="retr-item__src">
                {it.source || it.kind || "片段"}
                {typeof it.score === "number" ? ` · ${it.score.toFixed(2)}` : ""}
              </div>
              <div className="retr-item__text">
                {it.text || it.content || "（无文本）"}
              </div>
            </div>
          ))
        )}
      </section>
    </div>
  );
}
