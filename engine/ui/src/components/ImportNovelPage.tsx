import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import { JobCancelled, pollJob } from "../api/jobs";
import type {
  ImportChapterInput,
  ImportNovelRequest,
  ImportNovelResponse,
  ImportUploadPayload,
} from "../api/types";
import { navigate } from "../routing";
import "./importNovel.css";

const MIN_CH = 3;
const MAX_CH = 10;
const CHUNK_SIZE = 256 * 1024;
const ACCEPTED_UPLOADS = [".txt", ".md", ".zip", ".epub"];

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
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState("");
  const [progress, setProgress] = useState(0);
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
  const uploadOk = !!uploadFile && isAcceptedUpload(uploadFile.name);
  const useUpload = !!uploadFile;
  const canSubmit =
    slugOk &&
    !busy &&
    (useUpload ? uploadOk : filled.length >= MIN_CH && filled.length <= MAX_CH);

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
  function chooseUpload(file: File | null) {
    setUploadFile(file);
    setError(null);
    setExists(false);
  }

  async function submit() {
    if (!canSubmit) return;
    setBusy(true);
    setError(null);
    setExists(false);
    setProgress(0);
    setStage("排队中…");
    try {
      const payload = await buildImportRequest({
        name: name.trim(),
        genre: genre.trim() || "xianxia",
        mock,
        force,
        chapters: filled,
        uploadFile,
        setStage,
        setProgress,
      });
      const { job_id } = await api.postJobImportNovel(payload);
      setStage("排队中…");
      setProgress((p) => Math.max(p, 25));
      const result = await pollJob<ImportNovelResponse>(
        job_id,
        (p) => {
          setProgress(Math.max(25, p.progress));
          setStage(p.stage ? `${p.stage}…` : "导入中…");
        },
        () => stoppedRef.current,
      );
      navigate({ name: "anchor", slug: result.story_slug });
    } catch (err) {
      if (err instanceof JobCancelled) return;
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("已存在")) setExists(true);
      setError(msg);
      setProgress(0);
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
            上传 txt/md/epub/zip，或粘贴 {MIN_CH}–{MAX_CH} 章正文。长篇文件会先切成小片段，
            再由引擎抽取世界、角色、伏笔。仅作本地个人探索，请遵守版权。
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
              <span>模拟抽取（不调 LLM，推荐先用）</span>
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

          <section className="import__upload">
            <div>
              <label className="import__label" htmlFor="imp-file">
                长篇文件
              </label>
              <p className="muted tiny import__upload-hint">
                支持 txt、md、zip、epub。zip 请放入按文件名排序的 txt/md 章节。
              </p>
            </div>
            <input
              id="imp-file"
              className="import__file"
              type="file"
              accept=".txt,.md,.zip,.epub,text/plain,text/markdown,application/zip,application/epub+zip"
              onChange={(e) => chooseUpload(e.target.files?.[0] ?? null)}
              disabled={busy}
            />
            {uploadFile ? (
              <div className={`import__file-card ${uploadOk ? "" : "is-bad"}`}>
                <div>
                  <strong>{uploadFile.name}</strong>
                  <span className="muted tiny">
                    {formatBytes(uploadFile.size)} · 约 {chunkCount(uploadFile.size)} 片
                  </span>
                </div>
                <button
                  className="btn btn--ghost tiny"
                  onClick={() => chooseUpload(null)}
                  disabled={busy}
                >
                  移除
                </button>
                {!uploadOk && (
                  <p className="import__hint-bad tiny">只支持 txt / md / zip / epub。</p>
                )}
              </div>
            ) : (
              <p className="muted tiny">未选择文件时，可在下方粘贴章节正文。</p>
            )}
          </section>

          {!useUpload && (
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
          )}

          {error && (
            <div className={`import__error ${exists ? "import__error--exists" : ""}`}>
              <strong>导入没有完成</strong>
              <p>{error}</p>
              <div className="import__error-actions">
                {exists && !force && (
                  <button
                    className="btn btn--ghost tiny"
                    onClick={() => setForce(true)}
                    disabled={busy}
                  >
                    开启「允许覆盖」
                  </button>
                )}
                <button className="btn btn--ghost tiny" onClick={submit} disabled={!canSubmit}>
                  重试导入
                </button>
              </div>
            </div>
          )}

          <div className="import__foot">
            <div className="import__status">
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
              {busy && (
                <div className="import__progress" aria-label="导入进度">
                  <span style={{ width: `${Math.max(8, progress)}%` }} />
                </div>
              )}
            </div>
            <button className="btn btn--primary" disabled={!canSubmit} onClick={submit}>
              {busy ? "导入中…" : useUpload ? "上传并锚定" : "导入并锚定"}
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}

async function buildImportRequest({
  name,
  genre,
  mock,
  force,
  chapters,
  uploadFile,
  setStage,
  setProgress,
}: {
  name: string;
  genre: string;
  mock: boolean;
  force: boolean;
  chapters: Draft[];
  uploadFile: File | null;
  setStage: (stage: string) => void;
  setProgress: (progress: number) => void;
}): Promise<ImportNovelRequest> {
  if (uploadFile) {
    setStage("切分上传文件…");
    const upload = await buildUploadPayload(uploadFile, (done) => {
      setProgress(Math.min(24, Math.max(1, done)));
    });
    return {
      name,
      chapters: [],
      upload,
      genre,
      mock,
      force,
      long_mode: true,
    };
  }

  const payloadChapters: ImportChapterInput[] = chapters.map((c, i) => ({
    filename: `chapter_${String(i + 1).padStart(3, "0")}.md`,
    content: c.content.trim(),
  }));
  return {
    name,
    chapters: payloadChapters,
    genre,
    mock,
    force,
  };
}

async function buildUploadPayload(
  file: File,
  onProgress: (progress: number) => void,
): Promise<ImportUploadPayload> {
  const chunks = [];
  for (let offset = 0, index = 0; offset < file.size; offset += CHUNK_SIZE, index += 1) {
    const end = Math.min(offset + CHUNK_SIZE, file.size);
    const buffer = await file.slice(offset, end).arrayBuffer();
    chunks.push({
      index,
      data_b64: arrayBufferToBase64(buffer),
    });
    onProgress(Math.round((end / Math.max(1, file.size)) * 24));
  }
  return {
    filename: file.name,
    total_size: file.size,
    chunk_size: CHUNK_SIZE,
    chunks,
  };
}

function arrayBufferToBase64(buffer: ArrayBuffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function isAcceptedUpload(filename: string) {
  const lower = filename.toLowerCase();
  return ACCEPTED_UPLOADS.some((suffix) => lower.endsWith(suffix));
}

function chunkCount(size: number) {
  return Math.max(1, Math.ceil(size / CHUNK_SIZE));
}

function formatBytes(size: number) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`;
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${size} B`;
}
