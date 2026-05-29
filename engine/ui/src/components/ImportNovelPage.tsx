import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import { JobCancelled, pollJob } from "../api/jobs";
import type { ImportChapterInput, ImportNovelResponse } from "../api/types";
import { navigate } from "../routing";
import "./importNovel.css";

const MIN_CH = 3;
const MAX_CH = 10;

interface Draft {
  id: number;
  content: string;
}

let _seq = 0;
const blank = (): Draft => ({ id: ++_seq, content: "" });

export function ImportNovelPage() {
  const [name, setName] = useState("");
  const [genre, setGenre] = useState("xianxia");
  const [mock, setMock] = useState(true);
  const [force, setForce] = useState(false);
  const [chapters, setChapters] = useState<Draft[]>([blank(), blank(), blank()]);

  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [exists, setExists] = useState(false);
  const stoppedRef = useRef(false);

  useEffect(() => {
    let alive = true;
    api
      .getRuntimeSettings()
      .then((s) => alive && setMock(s.default_mock))
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, []);

  useEffect(() => {
    return () => {
      stoppedRef.current = true;
    };
  }, []);

  const filled = chapters.filter((c) => c.content.trim().length > 0);
  const slugOk = /^[a-z0-9][a-z0-9-]*$/.test(name);
  const canSubmit =
    slugOk && filled.length >= MIN_CH && filled.length <= MAX_CH && !busy;

  function setContent(id: number, content: string) {
    setChapters((prev) => prev.map((c) => (c.id === id ? { ...c, content } : c)));
  }
  function addChapter() {
    setChapters((prev) =>
      prev.length >= MAX_CH ? prev : [...prev, blank()],
    );
  }
  function removeChapter(id: number) {
    setChapters((prev) => (prev.length <= 1 ? prev : prev.filter((c) => c.id !== id)));
  }

  async function submit() {
    if (!canSubmit) return;
    setBusy(true);
    setError(null);
    setExists(false);
    setStage("排队中…");
    const payloadChapters: ImportChapterInput[] = filled.map((c, i) => ({
      filename: `chapter_${String(i + 1).padStart(3, "0")}.md`,
      content: c.content.trim(),
    }));
    try {
      const { job_id } = await api.postJobImportNovel({
        name: name.trim(),
        chapters: payloadChapters,
        genre: genre.trim() || "xianxia",
        mock,
        force,
      });
      const result = await pollJob<ImportNovelResponse>(
        job_id,
        (p) => setStage(p.stage ? `${p.stage}…` : "导入中…"),
        () => stoppedRef.current,
      );
      navigate({ name: "anchor", slug: result.story_slug });
    } catch (err) {
      if (err instanceof JobCancelled) return;
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("已存在")) setExists(true);
      setError(msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="import">
      <div className="import__sheet">
        <header className="import__head">
          <button className="import__back" onClick={() => navigate({ name: "entry" })}>
            ← 返回书架
          </button>
          <h1 className="import__title">导入小说</h1>
          <p className="muted import__lede">
            粘贴 {MIN_CH}–{MAX_CH} 章正文，引擎将抽取世界、角色、伏笔，
            导入后直接进入「世界锚定」确认。仅作本地个人探索，请遵守版权。
          </p>
        </header>

        <section className="import__form">
          <div className="import__row">
            <label className="import__label" htmlFor="imp-name">
              项目名
            </label>
            <input
              id="imp-name"
              className="import__input"
              placeholder="英文小写 + 连字符，如 my-story"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={busy}
            />
            {name && !slugOk && (
              <span className="import__hint-bad tiny">
                只能用英文小写字母、数字、连字符
              </span>
            )}
          </div>

          <div className="import__row import__row--inline">
            <div className="import__field">
              <label className="import__label" htmlFor="imp-genre">
                题材
              </label>
              <input
                id="imp-genre"
                className="import__input"
                placeholder="xianxia"
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                disabled={busy}
              />
            </div>
            <label className="import__toggle">
              <input
                type="checkbox"
                checked={mock}
                onChange={(e) => setMock(e.target.checked)}
                disabled={busy}
              />
              <span>mock 抽取（不调 LLM，推荐先用）</span>
            </label>
            <label className="import__toggle">
              <input
                type="checkbox"
                checked={force}
                onChange={(e) => setForce(e.target.checked)}
                disabled={busy}
              />
              <span>允许覆盖同名项目</span>
            </label>
          </div>

          <div className="import__chapters">
            <div className="import__chapters-head">
              <label className="import__label">
                章节正文 <span className="muted tiny">已填 {filled.length} / 需 {MIN_CH}–{MAX_CH}</span>
              </label>
              <button
                className="btn btn--ghost tiny"
                onClick={addChapter}
                disabled={busy || chapters.length >= MAX_CH}
              >
                + 添加章节
              </button>
            </div>
            {chapters.map((c, i) => (
              <div key={c.id} className="import__chapter">
                <div className="import__chapter-bar">
                  <span className="muted tiny mono">chapter_{String(i + 1).padStart(3, "0")}</span>
                  {chapters.length > 1 && (
                    <button
                      className="import__chapter-del"
                      onClick={() => removeChapter(c.id)}
                      disabled={busy}
                      title="移除此章"
                    >
                      ✕
                    </button>
                  )}
                </div>
                <textarea
                  className="import__textarea"
                  placeholder={`粘贴第 ${i + 1} 章正文（首行将作为标题）`}
                  value={c.content}
                  onChange={(e) => setContent(c.id, e.target.value)}
                  rows={5}
                  disabled={busy}
                />
              </div>
            ))}
          </div>

          {error && (
            <div className={`import__error ${exists ? "import__error--exists" : ""}`}>
              <p>{error}</p>
              {exists && !force && (
                <button
                  className="btn btn--ghost tiny"
                  onClick={() => setForce(true)}
                  disabled={busy}
                >
                  开启「允许覆盖」后重试
                </button>
              )}
            </div>
          )}

          <div className="import__foot">
            <span className="muted tiny">
              {busy ? (
                <span className="import__stage">
                  <span className="import__stage-dot" aria-hidden />
                  {stage || "导入中…"}
                </span>
              ) : (
                "导入成功后将进入世界锚定页确认世界与角色。"
              )}
            </span>
            <button className="btn btn--primary" disabled={!canSubmit} onClick={submit}>
              {busy ? "导入中…" : "导入并锚定"}
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
