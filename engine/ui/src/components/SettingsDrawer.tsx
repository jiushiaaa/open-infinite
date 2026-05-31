import { useState } from "react";
import type {
  ConnectivityResult,
  ProviderGatewaySummary,
  ProviderUsageSummary,
  RuntimeSettings,
} from "../api/types";
import { ApiError, api } from "../api/client";
import { useAsync } from "../hooks/useAsync";
import { ErrorState, Loading } from "./common/States";
import "./settings.css";

export function SettingsDrawer({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  return (
    <div
      className={`settings-scrim ${open ? "is-open" : ""}`}
      onClick={onClose}
      role="presentation"
    >
      <aside
        className="settings"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-label="运行设置"
      >
        {open && <SettingsBody onClose={onClose} />}
      </aside>
    </div>
  );
}

function SettingsBody({ onClose }: { onClose: () => void }) {
  const { data, loading, error, reload } = useAsync(() => api.getRuntimeSettings(), []);
  return (
    <div className="settings__inner">
      <header className="settings__head">
        <h2 className="settings__title">运行设置</h2>
        <button className="settings__close" onClick={onClose} aria-label="关闭">
          ✕
        </button>
      </header>
      {loading && <Loading label="正在读取设置…" />}
      {error && <ErrorState message={error} onRetry={reload} />}
      {data && <SettingsForm settings={data} />}
    </div>
  );
}

function SettingsForm({ settings }: { settings: RuntimeSettings }) {
  const [keyInput, setKeyInput] = useState("");
  const [present, setPresent] = useState(settings.llm_api_key_present);
  const [masked, setMasked] = useState(settings.masked_key);
  const [baseUrl, setBaseUrl] = useState(settings.llm_base_url);
  const [model, setModel] = useState(settings.llm_model_name);
  const [mock, setMock] = useState(settings.default_mock);
  const [rounds, setRounds] = useState(settings.default_rounds);
  const [runner, setRunner] = useState(settings.default_runner);

  const [sdKeyInput, setSdKeyInput] = useState("");
  const [sdPresent, setSdPresent] = useState(settings.seedream_key_present);
  const [sdMasked, setSdMasked] = useState(settings.seedream_masked_key);
  const [sdBase, setSdBase] = useState(settings.seedream_base_url);
  const [sdModel, setSdModel] = useState(settings.seedream_model);
  const [visualEnabled, setVisualEnabled] = useState(settings.visual_assets_enabled);

  const [saving, setSaving] = useState(false);
  const [saveErr, setSaveErr] = useState<string | null>(null);
  const [savedMsg, setSavedMsg] = useState<string | null>(null);
  const [testing, setTesting] = useState(false);
  const [testRes, setTestRes] = useState<ConnectivityResult | null>(null);
  const providerState = useAsync(
    async () => {
      const [gateway, usage] = await Promise.all([
        api.getProviderGateway(),
        api.getProviderUsage(),
      ]);
      return { gateway, usage };
    },
    [],
  );

  function applyResult(s: RuntimeSettings) {
    setPresent(s.llm_api_key_present);
    setMasked(s.masked_key);
    setSdPresent(s.seedream_key_present);
    setSdMasked(s.seedream_masked_key);
  }

  async function save() {
    setSaving(true);
    setSaveErr(null);
    setSavedMsg(null);
    try {
      const patch = {
        base_url: baseUrl.trim(),
        model_name: model.trim(),
        default_mock: mock,
        default_rounds: rounds,
        default_runner: runner,
        seedream_base_url: sdBase.trim(),
        seedream_model: sdModel.trim(),
        visual_assets_enabled: visualEnabled,
        ...(keyInput.trim() ? { api_key: keyInput.trim() } : {}),
        ...(sdKeyInput.trim() ? { seedream_api_key: sdKeyInput.trim() } : {}),
      };
      const updated = await api.updateRuntimeSettings(patch);
      applyResult(updated);
      setKeyInput("");
      setSdKeyInput("");
      setSavedMsg("设置已保存（仅本机生效）");
      providerState.reload();
    } catch (err) {
      setSaveErr(err instanceof ApiError ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  async function clearKey() {
    setSaving(true);
    setSaveErr(null);
    try {
      const updated = await api.updateRuntimeSettings({ api_key: "" });
      applyResult(updated);
      setSavedMsg("已清除密钥");
      providerState.reload();
    } catch (err) {
      setSaveErr(err instanceof ApiError ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  async function runTest() {
    setTesting(true);
    setTestRes(null);
    try {
      setTestRes(await api.testConnectivity(false));
    } catch (err) {
      setTestRes({ available: false, error: err instanceof Error ? err.message : String(err) });
    } finally {
      setTesting(false);
    }
  }

  return (
    <div className="settings__form">
      <section className="settings__group">
        <h3 className="settings__group-title">模型连接</h3>
        <div className="settings__field">
          <label className="settings__label" htmlFor="set-key">
            API 密钥
            <span className={`badge tiny ${present ? "badge--jade" : "badge--gold"}`}>
              {present ? `已配置 ${masked}` : "未配置"}
            </span>
          </label>
          <div className="settings__key-row">
            <input
              id="set-key"
              className="settings__input"
              type="password"
              placeholder={present ? "如需更换，输入新密钥" : "粘贴你的模型 API 密钥"}
              value={keyInput}
              onChange={(e) => setKeyInput(e.target.value)}
              disabled={saving}
            />
            {present && (
              <button
                className="btn btn--ghost tiny"
                onClick={clearKey}
                disabled={saving}
              >
                清除
              </button>
            )}
          </div>
          <p className="settings__note tiny muted">
            密钥只保存在本机引擎进程中，不会写入文件，也不会回传明文。
          </p>
        </div>
        <div className="settings__field">
          <label className="settings__label" htmlFor="set-base">接口地址</label>
          <input
            id="set-base"
            className="settings__input"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            disabled={saving}
          />
        </div>
        <div className="settings__field">
          <label className="settings__label" htmlFor="set-model">模型名称</label>
          <input
            id="set-model"
            className="settings__input"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            disabled={saving}
          />
        </div>
        <div className="settings__test">
          <button className="btn btn--ghost tiny" onClick={runTest} disabled={testing}>
            {testing ? "测试中…" : "测试连接"}
          </button>
          {testRes && (
            <span
              className={`badge tiny ${testRes.available ? "badge--jade" : "badge--cinnabar"}`}
            >
              {testRes.available
                ? "连接正常"
                : `不可用${testRes.reason ? "：" + testRes.reason : ""}`}
            </span>
          )}
        </div>
      </section>

      <ProviderStatusPanel
        data={providerState.data}
        loading={providerState.loading}
        error={providerState.error}
        onRetry={providerState.reload}
      />

      <section className="settings__group">
        <h3 className="settings__group-title">默认运行参数</h3>
        <label className="settings__toggle">
          <input
            type="checkbox"
            checked={mock}
            onChange={(e) => setMock(e.target.checked)}
            disabled={saving}
          />
          <span>默认用模拟生成（不消耗模型额度，适合先体验）</span>
        </label>
        <div className="settings__field">
          <label className="settings__label" htmlFor="set-rounds">默认推演轮数（1–12）</label>
          <input
            id="set-rounds"
            className="settings__input settings__input--num"
            type="number"
            min={1}
            max={12}
            value={rounds}
            onChange={(e) => setRounds(Number(e.target.value))}
            disabled={saving}
          />
        </div>
        <div className="settings__field">
          <label className="settings__label" htmlFor="set-runner">默认推演方式</label>
          <select
            id="set-runner"
            className="settings__input"
            value={runner}
            onChange={(e) => setRunner(e.target.value)}
            disabled={saving}
          >
            {settings.available_runners.map((r) => (
              <option key={r} value={r}>
                {RUNNER_LABEL[r] ?? r}
              </option>
            ))}
          </select>
        </div>
      </section>

      <section className="settings__group">
        <h3 className="settings__group-title">视觉资产（Seedream）</h3>
        <label className="settings__toggle">
          <input
            type="checkbox"
            checked={visualEnabled}
            onChange={(e) => setVisualEnabled(e.target.checked)}
            disabled={saving}
          />
          <span>启用视觉资产生成（封面 / 头像 / 场景）</span>
        </label>
        <div className="settings__field">
          <label className="settings__label" htmlFor="set-sd-key">
            Seedream 密钥
            <span className={`badge tiny ${sdPresent ? "badge--jade" : "badge--gold"}`}>
              {sdPresent ? `已配置 ${sdMasked}` : "未配置"}
            </span>
          </label>
          <input
            id="set-sd-key"
            className="settings__input"
            type="password"
            placeholder={sdPresent ? "如需更换，输入新密钥" : "粘贴 Seedream API 密钥"}
            value={sdKeyInput}
            onChange={(e) => setSdKeyInput(e.target.value)}
            disabled={saving}
          />
          <p className="settings__note tiny muted">
            未配置时仍可使用，封面与头像会以古风占位呈现，不影响文字主流程。
          </p>
        </div>
        <div className="settings__field">
          <label className="settings__label" htmlFor="set-sd-base">接口地址</label>
          <input
            id="set-sd-base"
            className="settings__input"
            value={sdBase}
            onChange={(e) => setSdBase(e.target.value)}
            disabled={saving}
          />
        </div>
        <div className="settings__field">
          <label className="settings__label" htmlFor="set-sd-model">模型名称</label>
          <input
            id="set-sd-model"
            className="settings__input"
            value={sdModel}
            onChange={(e) => setSdModel(e.target.value)}
            disabled={saving}
          />
        </div>
      </section>

      {saveErr && <p className="settings__err">{saveErr}</p>}

      <div className="settings__foot">
        <span className="muted tiny">{savedMsg ?? "更改将用于之后的生成。"}</span>
        <button className="btn btn--primary" onClick={save} disabled={saving}>
          {saving ? "保存中…" : "保存设置"}
        </button>
      </div>
    </div>
  );
}

function ProviderStatusPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: { gateway: ProviderGatewaySummary; usage: ProviderUsageSummary } | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">模型与用量状态</h3>
      {loading && <p className="settings__note tiny muted">正在读取模型状态…</p>}
      {error && (
        <div className="settings__inline-error">
          <span>{error}</span>
          <button className="btn btn--ghost tiny" onClick={onRetry}>
            重试
          </button>
        </div>
      )}
      {data && (
        <>
          <div className="settings__status-list">
            {data.gateway.providers.map((provider) => (
              <div className="settings__status-row" key={provider.id}>
                <div>
                  <strong>{provider.display_name}</strong>
                  <span className="muted tiny">{provider.model || "未设置模型"}</span>
                </div>
                <span
                  className={`badge tiny ${
                    provider.active
                      ? "badge--jade"
                      : provider.configured
                        ? "badge--gold"
                        : "badge--cinnabar"
                  }`}
                >
                  {provider.active
                    ? "使用中"
                    : provider.configured
                      ? "已配置未启用"
                      : "未配置"}
                </span>
              </div>
            ))}
          </div>
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">总计用量</span>
              <strong>{formatTokens(data.usage.totals.total_tokens)}</strong>
            </div>
            <div>
              <span className="muted tiny">输入 / 输出</span>
              <strong>
                {formatTokens(data.usage.totals.prompt_tokens)} /{" "}
                {formatTokens(data.usage.totals.completion_tokens)}
              </strong>
            </div>
          </div>
          <p className="settings__note tiny muted">
            已读取 {data.usage.record_count} 条用量记录；
            {data.usage.missing_usage_record_count > 0
              ? `另有 ${data.usage.missing_usage_record_count} 条旧记录缺少用量。`
              : "暂无缺失用量的记录。"}
          </p>
          {data.gateway.warnings.slice(0, 2).map((warning) => (
            <p className="settings__note tiny muted" key={warning.code}>
              {warning.message}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function formatTokens(value: number): string {
  return Math.max(0, value).toLocaleString("zh-CN");
}

const RUNNER_LABEL: Record<string, string> = {
  lightweight: "轻量（最快，规则推演）",
  multi_agent_stub: "多角色（占位，不调模型）",
  multi_agent_llm: "多角色（真实模型，更慢更细）",
};
