import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import { JobCancelled, pollJob } from "../api/jobs";
import type { StoryGenesisResponse } from "../api/types";
import { navigate } from "../routing";
import "./genesis.css";

export function GenesisPage() {
  const [name, setName] = useState("");
  const [genre, setGenre] = useState("xianxia");
  const [premise, setPremise] = useState("");
  const [protagonist, setProtagonist] = useState("");
  const [style, setStyle] = useState("");
  const [mock, setMock] = useState(true);
  const [force, setForce] = useState(false);

  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [exists, setExists] = useState(false);
  const stoppedRef = useRef(false);
  const premiseRef = useRef<HTMLTextAreaElement | null>(null);

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

  const slugOk = /^[a-z0-9][a-z0-9-]*$/.test(name);
  const canSubmit = slugOk && premise.trim().length > 0 && !busy;
  const premiseReady = premise.trim().length > 0;
  const genesisSteps = [
    {
      title: "命名世界",
      detail: slugOk ? name.trim() : "先给世界一个英文代号",
      done: slugOk,
    },
    {
      title: "写下冲突",
      detail: premiseReady ? "主题已经可以创世" : "一句话也可以开始",
      done: premiseReady,
    },
    {
      title: "补足手感",
      detail: protagonist || style ? "主角或文风已有提示" : "主角与文风可选",
      done: !!(protagonist.trim() || style.trim()),
    },
    {
      title: "进入锚定",
      detail: mock ? "模拟创世后先确认世界" : "真实模型创世后确认世界",
      done: false,
    },
  ];

  async function submit() {
    if (!canSubmit) return;
    setBusy(true);
    setError(null);
    setExists(false);
    setStage("排队中…");
    try {
      const { job_id } = await api.postJobStoryGenesis({
        name: name.trim(),
        premise: premise.trim(),
        genre: genre.trim() || "xianxia",
        protagonist_hint: protagonist.trim(),
        style_hint: style.trim(),
        mock,
        force,
      });
      const result = await pollJob<StoryGenesisResponse>(
        job_id,
        (p) => setStage(p.stage ? `${p.stage}…` : "创世中…"),
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
    <div className="gen">
      <div className="gen__sheet">
        <header className="gen__head">
          <button className="gen__back" onClick={() => navigate({ name: "entry" })}>
            ← 返回书架
          </button>
          <h1 className="gen__title">主题创世</h1>
          <p className="muted gen__lede">
            不上传任何文本，只给出题材与想看的故事，引擎将生成初始世界、角色与第一章，
            随后进入「世界锚定」确认。先从一个念头开始。
          </p>
        </header>

        <section className="gen__command" aria-label="创世工作流总览">
          <div className="gen__command-copy">
            <span className="gen__eyebrow">无稿创世台</span>
            <h2>从一个故事念头生成世界雏形</h2>
            <p>
              适合还没有正文、只有题材或冲突的时候。引擎会先生成初始世界、角色与第一章，
              再把你带到「世界锚定」页确认，不会直接把世界丢进沙盘乱跑。
            </p>
          </div>
          <div className="gen__status-grid">
            {genesisSteps.map((step, index) => (
              <article
                className={`gen__step ${step.done ? "is-done" : index === 1 ? "is-active" : ""}`}
                key={step.title}
              >
                <span className="gen__step-index">{String(index + 1).padStart(2, "0")}</span>
                <strong>{step.title}</strong>
                <span>{step.detail}</span>
              </article>
            ))}
          </div>
          <div className="gen__quick-actions">
            <button className="btn btn--primary" disabled={!canSubmit} onClick={submit}>
              {busy ? "创世中…" : "创世并锚定"}
            </button>
            <button
              className="btn btn--ghost"
              disabled={busy}
              onClick={() => premiseRef.current?.focus()}
            >
              填写主题
            </button>
            <button className="btn btn--ghost" onClick={() => navigate({ name: "entry" })}>
              返回书架
            </button>
          </div>
        </section>

        <section className="gen__form">
          <div className="gen__row">
            <label className="gen__label" htmlFor="gen-name">
              项目名
            </label>
            <input
              id="gen-name"
              className="gen__input"
              placeholder="英文小写 + 连字符，如 my-story"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={busy}
            />
            {name && !slugOk && (
              <span className="gen__hint-bad tiny">
                只能用英文小写字母、数字、连字符
              </span>
            )}
          </div>

          <div className="gen__row">
            <label className="gen__label" htmlFor="gen-premise">
              主题 / 想看的故事 <span className="gen__req">必填</span>
            </label>
            <textarea
              ref={premiseRef}
              id="gen-premise"
              className="gen__textarea"
              placeholder="例：一名守陵人发现先祖留下的禁忌封印松动，必须在城破之前找出真相。"
              value={premise}
              onChange={(e) => setPremise(e.target.value)}
              rows={4}
              disabled={busy}
            />
          </div>

          <div className="gen__row gen__row--inline">
            <div className="gen__field">
              <label className="gen__label" htmlFor="gen-genre">
                题材
              </label>
              <input
                id="gen-genre"
                className="gen__input"
                placeholder="xianxia"
                value={genre}
                onChange={(e) => setGenre(e.target.value)}
                disabled={busy}
              />
            </div>
            <div className="gen__field gen__field--grow">
              <label className="gen__label" htmlFor="gen-prot">
                主角提示 <span className="muted tiny">可空</span>
              </label>
              <input
                id="gen-prot"
                className="gen__input"
                placeholder="例：守陵人 顾长夜，沉默而执拗"
                value={protagonist}
                onChange={(e) => setProtagonist(e.target.value)}
                disabled={busy}
              />
            </div>
          </div>

          <div className="gen__row">
            <label className="gen__label" htmlFor="gen-style">
              文风偏好 <span className="muted tiny">可空</span>
            </label>
            <textarea
              id="gen-style"
              className="gen__textarea"
              placeholder="例：克制、画面感强、留白多，偏冷峻。"
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              rows={2}
              disabled={busy}
            />
          </div>

          <div className="gen__row gen__row--inline">
            <label className="gen__toggle">
              <input
                type="checkbox"
                checked={mock}
                onChange={(e) => setMock(e.target.checked)}
                disabled={busy}
              />
              <span>mock 创世（不调 LLM，推荐先用）</span>
            </label>
            <label className="gen__toggle">
              <input
                type="checkbox"
                checked={force}
                onChange={(e) => setForce(e.target.checked)}
                disabled={busy}
              />
              <span>允许覆盖同名项目</span>
            </label>
          </div>

          {error && (
            <div className={`gen__error ${exists ? "gen__error--exists" : ""}`}>
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

          <div className="gen__foot">
            <span className="muted tiny">
              {busy ? (
                <span className="gen__stage">
                  <span className="gen__stage-dot" aria-hidden />
                  {stage || "创世中…"}
                </span>
              ) : (
                "创世成功后将进入世界锚定页确认世界与角色。"
              )}
            </span>
            <button className="btn btn--primary" disabled={!canSubmit} onClick={submit}>
              {busy ? "创世中…" : "创世并锚定"}
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}
