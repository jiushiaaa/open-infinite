import "./states.css";

export function Loading({ label = "正在展开世界线…" }: { label?: string }) {
  return (
    <div className="state state--loading">
      <span className="state__brush" aria-hidden />
      <span className="muted">{label}</span>
    </div>
  );
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="state state--error">
      <p className="state__title">无法读取</p>
      <p className="muted tiny">{message}</p>
      {onRetry && (
        <button className="btn btn--ghost" onClick={onRetry}>
          重试
        </button>
      )}
    </div>
  );
}

// 缺 artifact 不是错误，而是「该分支尚未生成该资料」。
export function EmptyState({
  title,
  hint,
}: {
  title: string;
  hint?: string;
}) {
  return (
    <div className="state state--empty">
      <p className="state__title muted">{title}</p>
      {hint && <p className="muted tiny">{hint}</p>}
    </div>
  );
}
