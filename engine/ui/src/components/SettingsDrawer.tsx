import { Component, useState, type ReactNode } from "react";
import type {
  ApiContractReport,
  AuthBoundaryChecklist,
  BundledReleaseReadinessReport,
  ConnectivityResult,
  CommercialStatusOverview,
  CrossProjectRetrievalSamplesIndexReport,
  DeploymentObservabilityChecklist,
  LLMProfileAssignmentReport,
  LocalSmokeChecklist,
  ModelConfigurationPreset,
  ModelConfigurationSummary,
  ObjectStorageBoundaryChecklist,
  QuotaEnforcementBoundaryChecklist,
  ReleasePreflightChecklist,
  RetrievalProviderConfigurationReport,
  RetrievalProviderConnectivityResult,
  RetrievalSamplesTrendSnapshotReport,
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
        {open && (
          <SettingsBoundary>
            <SettingsBody onClose={onClose} />
          </SettingsBoundary>
        )}
      </aside>
    </div>
  );
}

class SettingsBoundary extends Component<
  { children: ReactNode },
  { message: string | null }
> {
  state = { message: null };

  static getDerivedStateFromError(error: unknown) {
    return { message: error instanceof Error ? error.message : String(error) };
  }

  render() {
    if (this.state.message) {
      return (
        <div className="settings__inner">
          <ErrorState message={`设置面板异常：${this.state.message}`} />
        </div>
      );
    }
    return this.props.children;
  }
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
  const modelConfigState = useAsync(() => api.getModelConfiguration(), []);
  const retrievalProviderState = useAsync(
    async () => {
      const [configuration, mockSmoke] = await Promise.all([
        api.getRetrievalProviderConfiguration(),
        api.testRetrievalProviderConnectivity(true),
      ]);
      return { configuration, mockSmoke };
    },
    [],
  );
  const profileState = useAsync(() => api.getLLMProfileAssignment(), []);
  const apiContractState = useAsync(() => api.getApiContract(), []);
  const retrievalSamplesIndexState = useAsync(() => api.getRetrievalSamplesIndex(), []);
  const retrievalSamplesTrendState = useAsync(
    () => api.getRetrievalSamplesTrendSnapshot(),
    [],
  );
  const packagingReadinessState = useAsync(() => api.getPackagingReadiness(), []);
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
  const commercialState = useAsync(() => api.getCommercialStatusOverview(), []);
  const smokeState = useAsync(() => api.getLocalSmokeChecklist(), []);
  const preflightState = useAsync(() => api.getReleasePreflight(), []);
  const deploymentObsState = useAsync(() => api.getDeploymentObservability(), []);
  const authBoundaryState = useAsync(() => api.getAuthBoundary(), []);
  const objectStorageState = useAsync(() => api.getObjectStorageBoundary(), []);
  const quotaEnforcementState = useAsync(() => api.getQuotaEnforcementBoundary(), []);
  const textModelPresets: ModelConfigurationPreset[] =
    modelConfigState.data?.text_model_presets ?? [];
  const visualModelPresets: ModelConfigurationPreset[] =
    modelConfigState.data?.visual_model_presets ?? [];

  function applyResult(s: RuntimeSettings) {
    setPresent(s.llm_api_key_present);
    setMasked(s.masked_key);
    setSdPresent(s.seedream_key_present);
    setSdMasked(s.seedream_masked_key);
  }

  function reloadConfigurationPanels() {
    modelConfigState.reload();
    retrievalProviderState.reload();
    profileState.reload();
    apiContractState.reload();
    retrievalSamplesIndexState.reload();
    retrievalSamplesTrendState.reload();
    packagingReadinessState.reload();
    providerState.reload();
    commercialState.reload();
    deploymentObsState.reload();
    authBoundaryState.reload();
    objectStorageState.reload();
    quotaEnforcementState.reload();
  }

  function applyTextPreset(presetId: string) {
    const preset = textModelPresets.find((item) => item.id === presetId);
    if (!preset || preset.id === "custom") return;
    setBaseUrl(preset.base_url);
    setModel(preset.model_name);
  }

  function applyVisualPreset(presetId: string) {
    const preset = visualModelPresets.find((item) => item.id === presetId);
    if (!preset) return;
    setVisualEnabled(preset.enabled !== false);
    if (preset.base_url) setSdBase(preset.base_url);
    if (preset.model_name) setSdModel(preset.model_name);
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
      reloadConfigurationPanels();
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
      reloadConfigurationPanels();
    } catch (err) {
      setSaveErr(err instanceof ApiError ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  async function clearSeedreamKey() {
    setSaving(true);
    setSaveErr(null);
    try {
      const updated = await api.updateRuntimeSettings({ seedream_api_key: "" });
      applyResult(updated);
      setSavedMsg("已清除视觉模型密钥");
      reloadConfigurationPanels();
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
        {textModelPresets.length > 0 && (
          <div className="settings__field">
            <label className="settings__label" htmlFor="set-text-preset">
              常用接口模板
            </label>
            <select
              id="set-text-preset"
              className="settings__input"
              defaultValue=""
              onChange={(e) => applyTextPreset(e.target.value)}
              disabled={saving}
            >
              <option value="">选择后自动填写接口地址和模型名</option>
              {textModelPresets.map((preset) => (
                <option key={preset.id} value={preset.id}>
                  {preset.label}
                </option>
              ))}
            </select>
            <p className="settings__note tiny muted">
              模板只填接口地址和模型名，密钥仍需你自己输入；页面不会回显明文。
            </p>
          </div>
        )}
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
        <label className="settings__toggle">
          <input
            type="checkbox"
            checked={!mock}
            onChange={(e) => setMock(!e.target.checked)}
            disabled={saving}
          />
          <span>使用真实文本模型生成</span>
        </label>
        <p className="settings__note tiny muted">
          未勾选时继续使用本地模拟，适合先体验流程；勾选后后续生成会尝试调用上方模型。
        </p>
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

      <ModelConfigurationPanel
        data={modelConfigState.data}
        loading={modelConfigState.loading}
        error={modelConfigState.error}
        onRetry={modelConfigState.reload}
      />

      <RetrievalProviderPanel
        data={retrievalProviderState.data}
        loading={retrievalProviderState.loading}
        error={retrievalProviderState.error}
        onRetry={retrievalProviderState.reload}
      />

      <LLMProfileAssignmentPanel
        data={profileState.data}
        loading={profileState.loading}
        error={profileState.error}
        onRetry={profileState.reload}
      />

      <ApiContractPanel
        data={apiContractState.data}
        loading={apiContractState.loading}
        error={apiContractState.error}
        onRetry={apiContractState.reload}
      />

      <RetrievalSamplesIndexPanel
        data={retrievalSamplesIndexState.data}
        loading={retrievalSamplesIndexState.loading}
        error={retrievalSamplesIndexState.error}
        onRetry={retrievalSamplesIndexState.reload}
      />

      <RetrievalSamplesTrendPanel
        data={retrievalSamplesTrendState.data}
        loading={retrievalSamplesTrendState.loading}
        error={retrievalSamplesTrendState.error}
        onRetry={retrievalSamplesTrendState.reload}
      />

      <PackagingReadinessPanel
        data={packagingReadinessState.data}
        loading={packagingReadinessState.loading}
        error={packagingReadinessState.error}
        onRetry={packagingReadinessState.reload}
      />

      <ProviderStatusPanel
        data={providerState.data}
        loading={providerState.loading}
        error={providerState.error}
        onRetry={providerState.reload}
      />

      <CommercialStatusPanel
        data={commercialState.data}
        loading={commercialState.loading}
        error={commercialState.error}
        onRetry={commercialState.reload}
      />

      <LocalSmokeChecklistPanel
        data={smokeState.data}
        loading={smokeState.loading}
        error={smokeState.error}
        onRetry={smokeState.reload}
      />

      <ReleasePreflightPanel
        data={preflightState.data}
        loading={preflightState.loading}
        error={preflightState.error}
        onRetry={preflightState.reload}
      />

      <DeploymentObservabilityPanel
        data={deploymentObsState.data}
        loading={deploymentObsState.loading}
        error={deploymentObsState.error}
        onRetry={deploymentObsState.reload}
      />

      <AuthBoundaryPanel
        data={authBoundaryState.data}
        loading={authBoundaryState.loading}
        error={authBoundaryState.error}
        onRetry={authBoundaryState.reload}
      />

      <ObjectStorageBoundaryPanel
        data={objectStorageState.data}
        loading={objectStorageState.loading}
        error={objectStorageState.error}
        onRetry={objectStorageState.reload}
      />

      <QuotaEnforcementBoundaryPanel
        data={quotaEnforcementState.data}
        loading={quotaEnforcementState.loading}
        error={quotaEnforcementState.error}
        onRetry={quotaEnforcementState.reload}
      />

      <section className="settings__group">
        <h3 className="settings__group-title">默认运行参数</h3>
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
        {visualModelPresets.length > 0 && (
          <div className="settings__field">
            <label className="settings__label" htmlFor="set-visual-preset">
              视觉模型模板
            </label>
            <select
              id="set-visual-preset"
              className="settings__input"
              defaultValue=""
              onChange={(e) => applyVisualPreset(e.target.value)}
              disabled={saving}
            >
              <option value="">选择视觉资产模式</option>
              {visualModelPresets.map((preset) => (
                <option key={preset.id} value={preset.id}>
                  {preset.label}
                </option>
              ))}
            </select>
          </div>
        )}
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
          <div className="settings__key-row">
            <input
              id="set-sd-key"
              className="settings__input"
              type="password"
              placeholder={sdPresent ? "如需更换，输入新密钥" : "粘贴 Seedream API 密钥"}
              value={sdKeyInput}
              onChange={(e) => setSdKeyInput(e.target.value)}
              disabled={saving}
            />
            {sdPresent && (
              <button
                className="btn btn--ghost tiny"
                onClick={clearSeedreamKey}
                disabled={saving}
              >
                清除
              </button>
            )}
          </div>
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

function LocalSmokeChecklistPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: LocalSmokeChecklist | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">本地冒烟清单</h3>
      {loading && <p className="settings__note tiny muted">正在读取本地冒烟清单…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">待核对路径</span>
              <strong>{data.summary.check_count}</strong>
            </div>
            <div>
              <span className="muted tiny">外部服务</span>
              <strong>{data.summary.external_services_required ? "需要" : "不需要"}</strong>
            </div>
          </div>
          <div className="settings__route-list settings__route-list--smoke">
            {data.checks.slice(0, 6).map((check) => (
              <div className="settings__route-row" key={check.id}>
                <span>{check.label}</span>
                <strong title={check.expected}>{check.path}</strong>
              </div>
            ))}
          </div>
          {data.run_steps.slice(0, 2).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function ModelConfigurationPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: ModelConfigurationSummary | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">模型配置状态</h3>
      {loading && <p className="settings__note tiny muted">正在读取模型配置状态…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">已就绪</span>
              <strong>
                {data.summary.ready_count} /{" "}
                {data.summary.ready_count + data.summary.attention_count}
              </strong>
            </div>
            <div>
              <span className="muted tiny">当前模式</span>
              <strong>{data.summary.mock_enabled ? "本地模拟" : "真实模型"}</strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.sections.map((section) => (
              <div className="settings__status-row" key={section.id}>
                <div>
                  <strong>{section.label}</strong>
                  <span className="muted tiny">{section.evidence}</span>
                </div>
                <span className={`badge tiny ${modelConfigBadgeClass(section.status)}`}>
                  {section.status_label}
                </span>
              </div>
            ))}
          </div>
          {data.warnings.slice(0, 2).map((warning) => (
            <p className="settings__note tiny muted" key={settingsWarningKey(warning)}>
              {settingsWarningText(warning)}
            </p>
          ))}
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function RetrievalProviderPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: {
    configuration: RetrievalProviderConfigurationReport;
    mockSmoke: RetrievalProviderConnectivityResult;
  } | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  const config = data?.configuration;
  const smoke = data?.mockSmoke;
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">检索增强 Provider</h3>
      {loading && <p className="settings__note tiny muted">正在读取检索增强配置…</p>}
      {error && (
        <div className="settings__inline-error">
          <span>{error}</span>
          <button className="btn btn--ghost tiny" onClick={onRetry}>
            重试
          </button>
        </div>
      )}
      {config && smoke && (
        <>
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">已配置</span>
              <strong>
                {config.summary.ready_count} /{" "}
                {config.summary.ready_count + config.summary.attention_count}
              </strong>
            </div>
            <div>
              <span className="muted tiny">本地契约</span>
              <strong>
                {smoke.summary.available_count} / {smoke.summary.check_count}
              </strong>
            </div>
          </div>
          <div className="settings__status-list">
            <div className="settings__status-row">
              <div>
                <strong>百炼 Embedding</strong>
                <span className="muted tiny">
                  {config.providers.embedding.model} · {config.providers.embedding.dimension} 维
                </span>
              </div>
              <span
                className={`badge tiny ${
                  config.providers.embedding.configured ? "badge--jade" : "badge--gold"
                }`}
              >
                {config.providers.embedding.configured ? "已配置" : "待配置"}
              </span>
            </div>
            <div className="settings__status-row">
              <div>
                <strong>Zilliz Cloud</strong>
                <span className="muted tiny">
                  {config.providers.vector_store.collection} ·{" "}
                  {config.providers.vector_store.route}
                </span>
              </div>
              <span
                className={`badge tiny ${
                  config.providers.vector_store.configured ? "badge--jade" : "badge--gold"
                }`}
              >
                {config.providers.vector_store.configured ? "已配置" : "待配置"}
              </span>
            </div>
            <div className="settings__status-row">
              <div>
                <strong>百炼 Reranker</strong>
                <span className="muted tiny">
                  {config.providers.reranker.model} · 前 {config.providers.reranker.top_n} 条
                </span>
              </div>
              <span
                className={`badge tiny ${
                  config.providers.reranker.configured ? "badge--jade" : "badge--gold"
                }`}
              >
                {config.providers.reranker.configured ? "已配置" : "待配置"}
              </span>
            </div>
          </div>
          <div className="settings__route-list">
            <div className="settings__route-row">
              <span>向量生成路径</span>
              <strong>{config.providers.embedding.route}</strong>
            </div>
            <div className="settings__route-row">
              <span>向量库路径</span>
              <strong>{config.providers.vector_store.route}</strong>
            </div>
            <div className="settings__route-row">
              <span>重排路径</span>
              <strong>{config.providers.reranker.route}</strong>
            </div>
          </div>
          {config.warnings.slice(0, 3).map((warning) => (
            <p className="settings__note tiny muted" key={warning}>
              {warning}
            </p>
          ))}
          <p className="settings__note tiny muted">
            页面只展示脱敏状态；本地 smoke 不调用外部 provider，不改变默认 BM25 检索。
          </p>
        </>
      )}
    </section>
  );
}

function LLMProfileAssignmentPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: LLMProfileAssignmentReport | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">任务模型画像</h3>
      {loading && <p className="settings__note tiny muted">正在读取任务画像…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">任务画像</span>
              <strong>{data.summary.profile_count}</strong>
            </div>
            <div>
              <span className="muted tiny">真实 / 本地</span>
              <strong>
                {data.summary.provider_profile_count} /{" "}
                {data.summary.mock_or_deterministic_count}
              </strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.profiles.map((profile) => (
              <div className="settings__status-row" key={profile.id}>
                <div>
                  <strong>{profile.label}</strong>
                  <span className="muted tiny">
                    {profileTaskLabel(profile.task_kind)} ·{" "}
                    {profileModelLabel(profile.model)} · {profile.note}
                  </span>
                </div>
                <span className={`badge tiny ${profileModeBadgeClass(profile.mode)}`}>
                  {profileModeLabel(profile.mode)}
                </span>
              </div>
            ))}
          </div>
          <div className="settings__route-list">
            <div className="settings__route-row">
              <span>文本路由</span>
              <strong>{profileModeLabel(data.routing.llm_route)}</strong>
            </div>
            <div className="settings__route-row">
              <span>视觉路由</span>
              <strong>{profileModeLabel(data.routing.visual_route)}</strong>
            </div>
            <div className="settings__route-row">
              <span>降级策略</span>
              <strong>{fallbackPolicyLabel(data.routing.fallback_policy)}</strong>
            </div>
          </div>
          {data.warnings.slice(0, 2).map((warning) => (
            <p className="settings__note tiny muted" key={settingsWarningKey(warning)}>
              {settingsWarningText(warning)}
            </p>
          ))}
          {data.boundaries.slice(0, 1).map((boundary) => (
            <p className="settings__note tiny muted" key={boundary}>
              {boundary}
            </p>
          ))}
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function ApiContractPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: ApiContractReport | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">接口契约</h3>
      {loading && <p className="settings__note tiny muted">正在读取接口契约…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">端点 / 路径</span>
              <strong>
                {data.summary.endpoint_count} / {data.summary.openapi_path_count}
              </strong>
            </div>
            <div>
              <span className="muted tiny">类型方法</span>
              <strong>{data.summary.typed_client_method_count}</strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.groups.map((group) => (
              <div className="settings__status-row" key={group.id}>
                <div>
                  <strong>{group.label}</strong>
                  <span className="muted tiny">{group.endpoint_count} 个本地端点</span>
                </div>
                <span className="badge tiny badge--jade">只读</span>
              </div>
            ))}
          </div>
          <div className="settings__route-list settings__route-list--api">
            {data.endpoints.slice(0, 8).map((endpoint) => (
              <div
                className="settings__route-row settings__route-row--api"
                key={`${endpoint.method}-${endpoint.path}`}
              >
                <span>
                  <strong>{endpoint.method}</strong>{" "}
                  <span className="settings__api-path">{endpoint.path}</span>
                </span>
                <strong>{endpoint.summary}</strong>
              </div>
            ))}
          </div>
          <p className="settings__note tiny muted">
            类型入口：{data.typed_client.client_source} / {data.typed_client.types_source}
          </p>
          {data.boundaries.slice(0, 2).map((boundary) => (
            <p className="settings__note tiny muted" key={boundary}>
              {boundary}
            </p>
          ))}
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function RetrievalSamplesIndexPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: CrossProjectRetrievalSamplesIndexReport | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">跨项目样本索引</h3>
      {loading && <p className="settings__note tiny muted">正在汇总检索样本…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">项目 / Records</span>
              <strong>
                {data.summary.project_count} / {data.summary.record_count}
              </strong>
            </div>
            <div>
              <span className="muted tiny">可迁移 / 空样本</span>
              <strong>
                {data.summary.ready_project_count} / {data.summary.empty_project_count}
              </strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.projects.slice(0, 6).map((project) => (
              <div className="settings__status-row" key={project.story_slug}>
                <div>
                  <strong>{project.display_name}</strong>
                  <span className="muted tiny">
                    {project.story_slug} · records {project.record_count} · case{" "}
                    {project.replay_case_count}
                  </span>
                </div>
                <span
                  className={`badge tiny ${sampleIndexBadgeClass(project.status)}`}
                >
                  {sampleIndexStatusLabel(project.status)}
                </span>
              </div>
            ))}
          </div>
          {data.records.length > 0 && (
            <div className="settings__route-list settings__route-list--api">
              {data.records.slice(0, 5).map((record) => (
                <div
                  className="settings__route-row settings__route-row--api"
                  key={`${record.story_slug}:${record.eval_id}`}
                >
                  <span>
                    <strong>{record.display_name}</strong>{" "}
                    <span className="settings__api-path">{record.eval_id}</span>
                  </span>
                  <strong>{record.expected_item_id || record.replay_status}</strong>
                </div>
              ))}
            </div>
          )}
          {data.warnings.slice(0, 2).map((warning) => (
            <p className="settings__note tiny muted" key={settingsWarningKey(warning)}>
              {settingsWarningText(warning)}
            </p>
          ))}
          {data.boundaries.slice(0, 1).map((boundary) => (
            <p className="settings__note tiny muted" key={boundary}>
              {boundary}
            </p>
          ))}
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function RetrievalSamplesTrendPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: RetrievalSamplesTrendSnapshotReport | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">样本趋势快照</h3>
      {loading && <p className="settings__note tiny muted">正在读取样本趋势…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">词面缺口 / 已覆盖</span>
              <strong>
                {data.summary.still_failing_lexically_count} /{" "}
                {data.summary.covered_by_current_retrieval_count}
              </strong>
            </div>
            <div>
              <span className="muted tiny">空样本 / 损坏</span>
              <strong>
                {data.summary.empty_project_count} / {data.summary.blocked_project_count}
              </strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.signals.slice(0, 5).map((signal) => (
              <div className="settings__status-row" key={signal.id}>
                <div>
                  <strong>{signal.label}</strong>
                  <span className="muted tiny">{signal.detail}</span>
                </div>
                <span className={`badge tiny ${trendBadgeClass(signal.status)}`}>
                  {trendStatusLabel(signal.status)}
                </span>
              </div>
            ))}
          </div>
          {data.project_trends.length > 0 && (
            <div className="settings__route-list settings__route-list--api">
              {data.project_trends.slice(0, 5).map((project) => (
                <div
                  className="settings__route-row settings__route-row--api"
                  key={project.story_slug}
                >
                  <span>
                    <strong>{project.display_name}</strong>{" "}
                    <span className="settings__api-path">{project.story_slug}</span>
                  </span>
                  <strong>{trendBucketLabel(project.trend_bucket)}</strong>
                </div>
              ))}
            </div>
          )}
          {data.warnings.slice(0, 2).map((warning) => (
            <p className="settings__note tiny muted" key={settingsWarningKey(warning)}>
              {settingsWarningText(warning)}
            </p>
          ))}
          {data.boundaries.slice(0, 1).map((boundary) => (
            <p className="settings__note tiny muted" key={boundary}>
              {boundary}
            </p>
          ))}
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function PackagingReadinessPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: BundledReleaseReadinessReport | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">发行准备</h3>
      {loading && <p className="settings__note tiny muted">正在读取发行准备清单…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">已具备 / 需留意</span>
              <strong>
                {data.summary.ready_count} / {data.summary.attention_count}
              </strong>
            </div>
            <div>
              <span className="muted tiny">后置目标</span>
              <strong>{data.summary.deferred_target_count}</strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.checks.slice(0, 6).map((check) => (
              <div className="settings__status-row" key={check.id}>
                <div>
                  <strong>{check.label}</strong>
                  <span className="muted tiny">{check.evidence}</span>
                </div>
                <span className={`badge tiny ${statusBadgeClass(check.status)}`}>
                  {check.status_label}
                </span>
              </div>
            ))}
          </div>
          <div className="settings__route-list settings__route-list--api">
            {data.package_targets.map((target) => (
              <div className="settings__route-row settings__route-row--api" key={target.id}>
                <span>{target.label}</span>
                <strong>{target.reason}</strong>
              </div>
            ))}
          </div>
          {data.boundaries.slice(0, 2).map((boundary) => (
            <p className="settings__note tiny muted" key={boundary}>
              {boundary}
            </p>
          ))}
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function CommercialStatusPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: CommercialStatusOverview | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">商业化状态总览</h3>
      {loading && <p className="settings__note tiny muted">正在读取商业化状态…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">本地已就绪</span>
              <strong>
                {data.summary.ready_domains} / {data.summary.total_domains}
              </strong>
            </div>
            <div>
              <span className="muted tiny">需留意 / 暂缓</span>
              <strong>
                {data.summary.attention_domains} / {data.summary.deferred_domains}
              </strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.domains.map((domain) => (
              <div className="settings__status-row" key={domain.id}>
                <div>
                  <strong>{domain.label}</strong>
                  <span className="muted tiny">{domain.evidence}</span>
                </div>
                <span className={`badge tiny ${commercialBadgeClass(domain.status)}`}>
                  {domain.status_label}
                </span>
              </div>
            ))}
          </div>
          {data.next_steps.slice(0, 2).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
          {data.warnings.slice(0, 1).map((warning) => (
            <p className="settings__note tiny muted" key={settingsWarningKey(warning)}>
              {settingsWarningText(warning)}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function ReleasePreflightPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: ReleasePreflightChecklist | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">发布前检查</h3>
      {loading && <p className="settings__note tiny muted">正在读取发布前检查…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">已具备</span>
              <strong>
                {data.summary.ready_count} / {data.summary.checkpoint_count}
              </strong>
            </div>
            <div>
              <span className="muted tiny">需留意</span>
              <strong>{data.summary.attention_count}</strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.checkpoints.slice(0, 6).map((checkpoint) => (
              <div className="settings__status-row" key={checkpoint.id}>
                <div>
                  <strong>{checkpoint.label}</strong>
                  <span className="muted tiny">{checkpoint.evidence}</span>
                </div>
                <span className={`badge tiny ${commercialBadgeClass(checkpoint.status)}`}>
                  {checkpoint.status_label}
                </span>
              </div>
            ))}
          </div>
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
          {data.warnings.slice(0, 1).map((warning) => (
            <p className="settings__note tiny muted" key={settingsWarningKey(warning)}>
              {settingsWarningText(warning)}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function DeploymentObservabilityPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: DeploymentObservabilityChecklist | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">部署观测清单</h3>
      {loading && <p className="settings__note tiny muted">正在读取部署观测清单…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">已具备</span>
              <strong>
                {data.summary.ready_count} / {data.summary.signal_count}
              </strong>
            </div>
            <div>
              <span className="muted tiny">云端观测</span>
              <strong>{data.summary.cloud_monitoring_enabled ? "已接入" : "未接入"}</strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.signals.slice(0, 6).map((signal) => (
              <div className="settings__status-row" key={signal.id}>
                <div>
                  <strong>{signal.label}</strong>
                  <span className="muted tiny">{signal.evidence}</span>
                </div>
                <span className={`badge tiny ${commercialBadgeClass(signal.status)}`}>
                  {signal.status_label}
                </span>
              </div>
            ))}
          </div>
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
          {data.warnings.slice(0, 1).map((warning) => (
            <p className="settings__note tiny muted" key={settingsWarningKey(warning)}>
              {settingsWarningText(warning)}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function AuthBoundaryPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: AuthBoundaryChecklist | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">认证边界清单</h3>
      {loading && <p className="settings__note tiny muted">正在读取认证边界…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">已具备</span>
              <strong>
                {data.summary.ready_count} / {data.summary.checkpoint_count}
              </strong>
            </div>
            <div>
              <span className="muted tiny">认证执行</span>
              <strong>{data.summary.auth_enforced ? "已启用" : "未启用"}</strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.checkpoints.map((checkpoint) => (
              <div className="settings__status-row" key={checkpoint.id}>
                <div>
                  <strong>{checkpoint.label}</strong>
                  <span className="muted tiny">{checkpoint.evidence}</span>
                </div>
                <span className={`badge tiny ${commercialBadgeClass(checkpoint.status)}`}>
                  {checkpoint.status_label}
                </span>
              </div>
            ))}
          </div>
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
          {data.warnings.slice(0, 1).map((warning) => (
            <p className="settings__note tiny muted" key={settingsWarningKey(warning)}>
              {settingsWarningText(warning)}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function ObjectStorageBoundaryPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: ObjectStorageBoundaryChecklist | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">对象存储边界</h3>
      {loading && <p className="settings__note tiny muted">正在读取对象存储边界…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">已具备</span>
              <strong>
                {data.summary.ready_count} / {data.summary.check_count}
              </strong>
            </div>
            <div>
              <span className="muted tiny">远端写入</span>
              <strong>{data.summary.remote_writes_enabled ? "已启用" : "未启用"}</strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.checks.slice(0, 6).map((check) => (
              <div className="settings__status-row" key={check.id}>
                <div>
                  <strong>{check.label}</strong>
                  <span className="muted tiny">{check.evidence}</span>
                </div>
                <span className={`badge tiny ${commercialBadgeClass(check.status)}`}>
                  {check.status_label}
                </span>
              </div>
            ))}
          </div>
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
          {data.warnings.slice(0, 1).map((warning) => (
            <p className="settings__note tiny muted" key={settingsWarningKey(warning)}>
              {settingsWarningText(warning)}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function QuotaEnforcementBoundaryPanel({
  data,
  loading,
  error,
  onRetry,
}: {
  data: QuotaEnforcementBoundaryChecklist | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}) {
  return (
    <section className="settings__group">
      <h3 className="settings__group-title">配额执行边界</h3>
      {loading && <p className="settings__note tiny muted">正在读取配额执行边界…</p>}
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
          <div className="settings__metric-row">
            <div>
              <span className="muted tiny">已具备</span>
              <strong>
                {data.summary.ready_count} / {data.summary.check_count}
              </strong>
            </div>
            <div>
              <span className="muted tiny">硬配额</span>
              <strong>{data.summary.hard_limits_enabled ? "已启用" : "未启用"}</strong>
            </div>
          </div>
          <div className="settings__status-list">
            {data.checks.slice(0, 6).map((check) => (
              <div className="settings__status-row" key={check.id}>
                <div>
                  <strong>{check.label}</strong>
                  <span className="muted tiny">{check.evidence}</span>
                </div>
                <span className={`badge tiny ${commercialBadgeClass(check.status)}`}>
                  {check.status_label}
                </span>
              </div>
            ))}
          </div>
          {data.next_steps.slice(0, 1).map((step) => (
            <p className="settings__note tiny muted" key={step}>
              {step}
            </p>
          ))}
          {data.warnings.slice(0, 1).map((warning) => (
            <p className="settings__note tiny muted" key={settingsWarningKey(warning)}>
              {settingsWarningText(warning)}
            </p>
          ))}
        </>
      )}
    </section>
  );
}

function commercialBadgeClass(status: string): string {
  if (status === "ready") return "badge--jade";
  if (status === "deferred") return "badge--cinnabar";
  return "badge--gold";
}

function sampleIndexStatusLabel(status: string): string {
  const map: Record<string, string> = {
    ready: "可汇总",
    empty: "暂无样本",
    attention: "需补样本",
    blocked: "需修复",
  };
  return map[status] ?? status;
}

function sampleIndexBadgeClass(status: string): string {
  if (status === "ready") return "badge--jade";
  if (status === "blocked") return "badge--cinnabar";
  return "badge--gold";
}

function trendStatusLabel(status: string): string {
  const map: Record<string, string> = {
    ready: "正常",
    attention: "需关注",
    blocked: "需修复",
    deferred: "暂缓",
  };
  return map[status] ?? status;
}

function trendBadgeClass(status: string): string {
  if (status === "ready") return "badge--jade";
  if (status === "blocked") return "badge--cinnabar";
  return "badge--gold";
}

function trendBucketLabel(bucket: string): string {
  const map: Record<string, string> = {
    has_samples: "有样本缺口",
    covered_samples: "样本已覆盖",
    empty_samples: "暂无样本",
    blocked: "样本需修复",
  };
  return map[bucket] ?? bucket;
}

function modelConfigBadgeClass(status: string): string {
  return status === "ready" ? "badge--jade" : "badge--gold";
}

function profileModeBadgeClass(mode: string): string {
  if (mode === "provider" || mode === "seedream_visual") return "badge--jade";
  if (mode === "disabled") return "badge--cinnabar";
  return "badge--gold";
}

function settingsWarningText(
  warning: string | { code?: string; message?: string },
): string {
  if (typeof warning === "string") return warning;
  return warning.message ?? warning.code ?? "设置提示";
}

function settingsWarningKey(
  warning: string | { code?: string; message?: string },
): string {
  if (typeof warning === "string") return warning;
  return warning.code ?? warning.message ?? "settings-warning";
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
          <div className="settings__route-list">
            {data.gateway.routes.map((route) => (
              <div className="settings__route-row" key={route.id}>
                <span>{route.label}</span>
                <strong>{routeProviderLabel(route.provider_id, data.gateway)}</strong>
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
          <p className="settings__note tiny muted">
            当前只统计本地生成用量，暂不展示计费或价格估算。
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

function routeProviderLabel(providerId: string, gateway: ProviderGatewaySummary): string {
  const provider = gateway.providers.find((item) => item.id === providerId);
  if (provider) return provider.display_name;
  if (providerId === "mock") return "本地模拟";
  if (providerId === "placeholder") return "占位图";
  if (providerId === "disabled") return "已关闭";
  return providerId;
}

function profileTaskLabel(kind: string): string {
  if (kind === "generation") return "生成";
  if (kind === "extraction") return "抽取";
  if (kind === "revision") return "修订";
  if (kind === "evaluation") return "评审";
  if (kind === "image") return "视觉";
  return kind;
}

function profileModeLabel(mode: string): string {
  if (mode === "provider") return "真实模型";
  if (mode === "mock") return "本地模拟";
  if (mode === "deterministic") return "本地规则";
  if (mode === "disabled") return "已关闭";
  if (mode === "placeholder") return "占位图";
  if (mode === "seedream_visual") return "视觉模型";
  return mode;
}

function profileModelLabel(model: string): string {
  if (!model) return "未指定模型";
  if (model === "local_rules") return "本地规则";
  return model;
}

function fallbackPolicyLabel(policy: string): string {
  if (policy === "mock/placeholder") return "本地模拟 / 占位图";
  return policy.replace("mock", "本地模拟").replace("placeholder", "占位图");
}

function statusBadgeClass(status: string): string {
  if (status === "ready") return "badge--jade";
  if (status === "attention" || status === "deferred") return "badge--gold";
  return "badge--cinnabar";
}

function formatTokens(value: number): string {
  return Math.max(0, value).toLocaleString("zh-CN");
}

const RUNNER_LABEL: Record<string, string> = {
  lightweight: "轻量（最快，规则推演）",
  multi_agent_stub: "多角色（占位，不调模型）",
  multi_agent_llm: "多角色（真实模型，更慢更细）",
};
