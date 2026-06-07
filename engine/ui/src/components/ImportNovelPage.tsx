import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import { JobCancelled, pollJob } from "../api/jobs";
import type {
  IngestSessionSummary,
  ImportChapterInput,
  ImportNovelRequest,
  ImportNovelResponse,
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
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const chaptersRef = useRef<HTMLDivElement | null>(null);

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
  const sourceLabel = useUpload
    ? uploadOk
      ? `文件已就绪，约 ${chunkCount(uploadFile.size)} 片`
      : "文件格式待确认"
    : `已填写 ${filled.length} / 至少 ${MIN_CH} 章`;
  const importSteps = [
    {
      title: "命名世界",
      detail: slugOk ? name.trim() : "先给世界一个英文代号",
      done: slugOk,
    },
    {
      title: "放入正文",
      detail: sourceLabel,
      done: useUpload ? uploadOk : filled.length >= MIN_CH,
    },
    {
      title: "抽取世界",
      detail: mock ? "模拟抽取，适合先试流程" : "真实模型抽取，适合正式导入",
      done: canSubmit,
    },
    {
      title: "进入锚定",
      detail: "确认世界、角色与伏笔后再开跑",
      done: false,
    },
  ];
  const handoffReady = slugOk && (useUpload ? uploadOk : filled.length >= MIN_CH);
  const importHandoffStages = [
    {
      title: "世界锚定",
      state: handoffReady ? "待进入" : "准备中",
      detail: slugOk ? `${name.trim()} 将先被定界` : "先命名世界，再放入正文",
    },
    {
      title: "天命书",
      state: "下一卷",
      detail: "确认主锚点、因果债和候选承载者。",
    },
    {
      title: "世界沙盘",
      state: mock ? "模拟可试" : "真实运行",
      detail: "角色会按记忆行动，世界会自演出后果。",
    },
    {
      title: "卷宗阅读",
      state: "可续读",
      detail: "沙盘结果会沉淀为正史、角色卷和正文。",
    },
  ];

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
      const trimmedName = name.trim();
      const effectiveGenre = genre.trim() || "xianxia";
      const submit = uploadFile
        ? await startResumableImport({
            name: trimmedName,
            genre: effectiveGenre,
            mock,
            force,
            uploadFile,
            setStage,
            setProgress,
          })
        : {
            ...(await api.postJobImportNovel(
              buildManualImportRequest({
                name: trimmedName,
                genre: effectiveGenre,
                mock,
                force,
                chapters: filled,
              }),
            )),
            storageKey: "",
          };
      setStage("排队中…");
      setProgress((p) => Math.max(p, uploadFile ? 50 : 25));
      const result = await pollJob<ImportNovelResponse>(
        submit.job_id,
        (p) => {
          const base = uploadFile ? 50 : 25;
          const scaled = uploadFile
            ? 50 + Math.round(p.progress * 0.5)
            : p.progress;
          setProgress(Math.max(base, scaled));
          setStage(p.stage ? `${p.stage}…` : "导入中…");
        },
        () => stoppedRef.current,
      );
      if (submit.storageKey) localStorage.removeItem(submit.storageKey);
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

        <section className="import__command" aria-label="导入工作流总览">
          <div className="import__command-copy">
            <span className="import__eyebrow">开卷前台</span>
            <h2>把小说导成可运行的世界</h2>
            <p>
              这里不是单纯上传文件，而是把正文交给引擎拆解成世界书、角色卷、伏笔与锚点。
              完成后会进入「世界锚定」，让你确认这个世界是否值得开始自演。
            </p>
          </div>
          <div className="import__status-grid">
            {importSteps.map((step, index) => (
              <article
                className={`import__step ${step.done ? "is-done" : index === 1 ? "is-active" : ""}`}
                key={step.title}
              >
                <span className="import__step-index">{String(index + 1).padStart(2, "0")}</span>
                <strong>{step.title}</strong>
                <span>{step.detail}</span>
              </article>
            ))}
          </div>
          <div className="import__quick-actions">
            <button
              className="btn btn--primary"
              disabled={!canSubmit}
              onClick={submit}
            >
              {busy ? "导入中…" : useUpload ? "上传并锚定" : "导入并锚定"}
            </button>
            <button
              className="btn btn--ghost"
              disabled={busy}
              onClick={() => fileInputRef.current?.click()}
            >
              选择文件
            </button>
            <button
              className="btn btn--ghost"
              disabled={busy || useUpload}
              onClick={() => chaptersRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })}
            >
              填写章节
            </button>
          </div>
        </section>

        <section className="import__handoff" aria-label="导入后的世界旅程">
          <div className="import__handoff-copy">
            <span className="import__eyebrow">开卷旅程</span>
            <h2>导入不是结束，是世界开始运行前的第一步</h2>
            <p>
              当前素材状态：{sourceLabel}。点击导入后，系统会先把正文变成可确认的世界锚定，
              再进入天命书、世界沙盘和卷宗阅读，不会让你迷失在单纯的上传表单里。
            </p>
            <div className="import__handoff-actions">
              <button className="btn btn--primary" disabled={!canSubmit} onClick={submit}>
                {busy ? "导入中…" : useUpload ? "上传并进入锚定" : "导入并进入锚定"}
              </button>
              <button
                className="btn btn--ghost"
                disabled={busy}
                onClick={() => fileInputRef.current?.click()}
              >
                选择文件
              </button>
              <button
                className="btn btn--ghost"
                disabled={busy || useUpload}
                onClick={() => chaptersRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })}
              >
                填写章节
              </button>
            </div>
          </div>
          <div className="import__handoff-stages">
            {importHandoffStages.map((stage, index) => (
              <article
                className={`import__handoff-stage ${index === 0 ? "is-active" : ""}`}
                key={stage.title}
              >
                <span className="import__handoff-index">{String(index + 1).padStart(2, "0")}</span>
                <strong>{stage.title}</strong>
                <small>{stage.state}</small>
                <p>{stage.detail}</p>
              </article>
            ))}
          </div>
        </section>

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
                支持 txt、md、zip、epub。文件会写入可恢复上传会话，刷新后可续传缺失分片。
              </p>
            </div>
            <input
              ref={fileInputRef}
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
            <div className="import__chapters" ref={chaptersRef}>
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

function buildManualImportRequest({
  name,
  genre,
  mock,
  force,
  chapters,
}: {
  name: string;
  genre: string;
  mock: boolean;
  force: boolean;
  chapters: Draft[];
}): ImportNovelRequest {
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

async function startResumableImport({
  name,
  genre,
  mock,
  force,
  uploadFile,
  setStage,
  setProgress,
}: {
  name: string;
  genre: string;
  mock: boolean;
  force: boolean;
  uploadFile: File;
  setStage: (stage: string) => void;
  setProgress: (progress: number) => void;
}): Promise<{ job_id: string; status: string; storageKey: string }> {
  const storageKey = ingestStorageKey(name, uploadFile);
  setStage("准备上传会话…");
  let session = await restoreIngestSession(storageKey, uploadFile);
  if (!session) {
    session = await api.createIngestSession({
      name,
      filename: uploadFile.name,
      total_size: uploadFile.size,
      chunk_size: CHUNK_SIZE,
      total_chunks: chunkCount(uploadFile.size),
      genre,
      mock,
      force,
      long_mode: true,
    });
    localStorage.setItem(storageKey, session.session_id);
  }

  session = await uploadMissingChunks(uploadFile, session, setStage, setProgress);
  if (session.missing_chunks.length > 0) {
    throw new Error("仍有分片未上传完成，请稍后重试。");
  }
  setStage("合并上传分片…");
  setProgress(50);
  const submitted = await api.completeIngestSession(session.session_id);
  return { ...submitted, storageKey };
}

async function restoreIngestSession(
  storageKey: string,
  file: File,
): Promise<IngestSessionSummary | null> {
  const sessionId = localStorage.getItem(storageKey);
  if (!sessionId) return null;
  try {
    const session = await api.getIngestSession(sessionId);
    if (
      session.filename === file.name &&
      session.total_size === file.size &&
      session.chunk_size > 0 &&
      session.status !== "imported"
    ) {
      return session;
    }
  } catch {
    localStorage.removeItem(storageKey);
  }
  return null;
}

async function uploadMissingChunks(
  file: File,
  session: IngestSessionSummary,
  setStage: (stage: string) => void,
  setProgress: (progress: number) => void,
): Promise<IngestSessionSummary> {
  let current = session;
  const missing = [...current.missing_chunks];
  const total = Math.max(1, current.total_chunks);
  for (const index of missing) {
    const offset = index * current.chunk_size;
    const end = Math.min(offset + current.chunk_size, file.size);
    const buffer = await file.slice(offset, end).arrayBuffer();
    setStage(`上传第 ${index + 1}/${total} 片…`);
    current = await api.putIngestChunk(current.session_id, {
      index,
      data_b64: arrayBufferToBase64(buffer),
      sha256: await sha256Hex(buffer),
    });
    const uploaded = current.received_chunks.length;
    setProgress(Math.min(49, Math.max(1, Math.round((uploaded / total) * 49))));
  }
  return current;
}

function ingestStorageKey(name: string, file: File) {
  return [
    "lne-ingest",
    name,
    file.name,
    String(file.size),
    String(file.lastModified || 0),
  ].join(":");
}

function arrayBufferToBase64(buffer: ArrayBuffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

async function sha256Hex(buffer: ArrayBuffer) {
  const digest = await crypto.subtle.digest("SHA-256", buffer);
  return [...new Uint8Array(digest)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
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
