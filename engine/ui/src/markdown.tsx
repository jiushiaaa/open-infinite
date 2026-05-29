import type { ReactNode } from "react";

// 极简小说正文渲染：仅处理标题 / 引用 / 分隔线 / 段落，不引入 markdown 依赖。
// 目的是保持中文阅读舒适度，不做完整 markdown。
export function renderProse(text: string): ReactNode {
  if (!text || !text.trim()) return null;
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const out: ReactNode[] = [];
  let buf: string[] = [];
  let key = 0;

  const flush = () => {
    if (buf.length === 0) return;
    out.push(
      <p key={key++} className="prose__p">
        {buf.join("")}
      </p>,
    );
    buf = [];
  };

  for (const raw of lines) {
    const line = raw.trimEnd();
    if (line.trim() === "") {
      flush();
      continue;
    }
    if (/^#{1,6}\s/.test(line)) {
      flush();
      const level = line.match(/^#+/)![0].length;
      const content = line.replace(/^#{1,6}\s/, "");
      const Tag = (level <= 2 ? "h2" : "h3") as "h2" | "h3";
      out.push(
        <Tag key={key++} className="prose__h">
          {content}
        </Tag>,
      );
      continue;
    }
    if (/^>\s?/.test(line)) {
      flush();
      out.push(
        <blockquote key={key++} className="prose__quote">
          {line.replace(/^>\s?/, "")}
        </blockquote>,
      );
      continue;
    }
    if (/^[-*]{3,}$/.test(line.trim()) || line.trim() === "---") {
      flush();
      out.push(<hr key={key++} className="prose__rule" />);
      continue;
    }
    // 同段内换行用空格连接，保留中文段落整洁
    buf.push(buf.length ? line.trim() : line.trim());
  }
  flush();
  return out;
}
