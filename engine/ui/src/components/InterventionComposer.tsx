import { useEffect, useRef, useState } from "react";
import { ApiError, api } from "../api/client";
import { JobCancelled, pollJob } from "../api/jobs";
import type { InterventionResponse } from "../api/types";
import "./composer.css";

export interface CharOption {
  id: string;
  name: string;
}

export function InterventionComposer({
  slug,
  characters,
  onGenerated,
}: {
  slug: string;
  characters: CharOption[];
  onGenerated: (runId: string, branchId: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [target, setTarget] = useState("");
  const [manualTarget, setManualTarget] = useState("");
  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [mock, setMock] = useState(true);
  const stoppedRef = useRef(false);

  // 默认选第一个在场角色
  useEffect(() => {
    if (!target && characters.length > 0) setTarget(characters[0].id);
  }, [characters, target]);

  // 默认 mock 来自运行设置（用户仍可局部覆盖）。
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

  // 卸载时停止轮询，避免对已卸载组件 setState。
  useEffect(() => {
    return () => {
      stoppedRef.current = true;
    };
  }, []);

  const effectiveTarget = characters.length > 0 ? target : manualTarget.trim();
  const canSubmit = !!text.trim() && !!effectiveTarget && !busy;

  async function submit() {
    if (!canSubmit) return;
    setBusy(true);
    setError(null);
    setStage("排队中…");
    try {
      const { job_id } = await api.postJobIntervention({
        story_slug: slug,
        target: effectiveTarget,
        content: text.trim(),
        branches: 3,
        mock,
      });
      const result = await pollJob<InterventionResponse>(
        job_id,
        (p) => setStage(p.stage ? `${p.stage}…` : "推演中…"),
        () => stoppedRef.current,
      );
      const branch = result.primary_branch ?? result.branch_ids[0];
      if (!branch) throw new ApiError("生成成功但未返回分支", 0);
      setText("");
      setOpen(false);
      onGenerated(result.run_id, branch);
    } catch (err) {
      if (err instanceof JobCancelled) return;
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={`composer ${open ? "is-open" : ""}`}>
      <button
        className="composer__handle"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <span className="composer__handle-dot" aria-hidden />
        {open ? "收起干预" : "在此施加一个变量…"}
      </button>
      {open && (
        <div className="composer__body">
          <div className="composer__target">
            <label className="composer__label">干预目标</label>
            {characters.length > 0 ? (
              <select
                className="composer__select"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                disabled={busy}
              >
                {characters.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}（{c.id}）
                  </option>
                ))}
              </select>
            ) : (
              <input
                className="composer__select"
                placeholder="角色 ID（当前快照无角色，手填）"
                value={manualTarget}
                onChange={(e) => setManualTarget(e.target.value)}
                disabled={busy}
              />
            )}
          </div>
          <textarea
            className="composer__input"
            placeholder="例：我不希望沈砚进入书房，以免触发机关。"
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={3}
            disabled={busy}
          />
          {error && <p className="composer__error">{error}</p>}
          <label className="composer__mock">
            <input
              type="checkbox"
              checked={mock}
              onChange={(e) => setMock(e.target.checked)}
              disabled={busy}
            />
            <span className="tiny muted">模拟生成（不消耗模型额度）</span>
          </label>
          <div className="composer__foot">
            <span className="muted tiny">
              {busy ? (
                <span className="composer__stage">
                  <span className="composer__stage-dot" aria-hidden />
                  {stage || "推演中…"}
                </span>
              ) : (
                <>
                  系统会先解释「理解成了什么」，再生成世界线。
                  <span className="mono"> {slug}</span>
                </>
              )}
            </span>
            <button className="btn btn--primary" disabled={!canSubmit} onClick={submit}>
              {busy ? "推演中…" : "施加干预"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
