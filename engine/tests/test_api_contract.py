"""OpenAPI / Typed Client MVP: read-only local API contract."""

from __future__ import annotations

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

from living_novel_engine.browser import server
import living_novel_engine.service as service


def test_api_contract_describes_core_openapi_paths(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-contract-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-contract-secret-8899")

    get_api_contract = getattr(service, "get_api_contract", None)
    assert callable(get_api_contract)
    report = get_api_contract()
    paths = report["openapi"]["paths"]

    assert report["version"] == "openapi-typed-client-mvp"
    assert report["mode"] == "read_only_api_contract"
    assert report["summary"]["writes_artifacts"] is False
    assert report["summary"]["external_services_required"] is False
    assert report["summary"]["plaintext_key_returned"] is False
    assert report["openapi"]["openapi"] == "3.1.0"
    for path in (
        "/api/stories/{slug}/cards-workspace",
        "/api/stories/{slug}/vector-retrieval-readiness",
        "/api/stories/{slug}/embedding-evaluation-samples",
        "/api/stories/{slug}/graph-memory-trigger-evidence",
        "/api/stories/{slug}/graph-memory-spike-design-pack",
        "/api/stories/{slug}/graph-memory-shadow-compare-pack",
        "/api/stories/{slug}/graph-memory-shadow-case-matrix",
        "/api/stories/{slug}/graph-memory-provider-boundary-matrix",
        "/api/stories/{slug}/graph-memory-offline-shadow-replay-plan",
        "/api/stories/{slug}/graph-memory-offline-shadow-replay-report",
        "/api/stories/{slug}/graph-memory-provider-spike-fixture-pack",
        "/api/stories/{slug}/graph-memory-provider-spike-readiness-gate",
        "/api/stories/{slug}/graph-memory-provider-spike-runbook",
        "/api/stories/{slug}/graph-memory-provider-spike-dry-run-result-template",
        "/api/stories/{slug}/graph-memory-provider-spike-mock-result-report",
        "/api/stories/{slug}/graph-memory-provider-spike-review-gate",
        "/api/stories/{slug}/graph-memory-provider-spike-manual-approval-pack",
        "/api/stories/{slug}/graph-memory-provider-spike-manual-approval-evidence-checklist",
        "/api/stories/{slug}/graph-memory-provider-spike-opt-in-evidence-snapshot",
        "/api/stories/{slug}/graph-memory-provider-spike-opt-in-no-go-matrix",
        "/api/stories/{slug}/graph-memory-provider-spike-opt-in-operator-checklist",
        "/api/stories/{slug}/graph-memory-provider-spike-opt-in-review-packet",
        "/api/stories/{slug}/graph-memory-provider-spike-opt-in-decision-ledger-preview",
        "/api/stories/{slug}/graph-memory-provider-spike-opt-in-final-readiness-summary",
        "/api/stories/{slug}/graph-memory-provider-spike-opt-in-human-signoff-schema-draft",
        "/api/stories/{slug}/graph-memory-provider-spike-opt-in-config-draft",
        "/api/stories/{slug}/graph-memory-provider-spike-local-provider-contract",
        "/api/stories/{slug}/graph-memory-provider-spike-single-fixture-dry-run-harness",
        "/api/stories/{slug}/graph-memory-provider-spike-mock-compatible-adapter",
        "/api/stories/{slug}/graph-memory-provider-spike-manual-mock-adapter-review",
        "/api/settings/llm-profile-assignment",
        "/api/settings/retrieval-samples-trend-snapshot",
        "/api/runs/{run_id}/branches/{branch_id}/prompt-budget-pack",
    ):
        assert path in paths
        assert "get" in paths[path]
    assert report["summary"]["endpoint_count"] == 66
    assert report["summary"]["openapi_path_count"] == 65


def test_api_contract_maps_typed_client_without_leaking_secrets(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-contract-secret-7788")
    monkeypatch.setenv("SEEDREAM_API_KEY", "sd-contract-secret-8899")

    get_api_contract = getattr(service, "get_api_contract", None)
    assert callable(get_api_contract)
    report = get_api_contract()
    text = json.dumps(report, ensure_ascii=False)
    client_methods = {
        item["client_method"]: item for item in report["typed_client"]["methods"]
    }

    assert report["typed_client"]["client_source"] == "engine/ui/src/api/client.ts"
    assert report["typed_client"]["types_source"] == "engine/ui/src/api/types.ts"
    assert {
        "getCardsWorkspace",
        "getVectorRetrievalReadiness",
        "getEmbeddingEvaluationSamples",
        "getGraphMemoryTriggerEvidence",
        "getGraphMemorySpikeDesignPack",
        "getGraphMemoryShadowComparePack",
        "getGraphMemoryShadowCaseMatrix",
        "getGraphMemoryProviderBoundaryMatrix",
        "getGraphMemoryOfflineShadowReplayPlan",
        "getGraphMemoryOfflineShadowReplayReport",
        "getGraphMemoryProviderSpikeFixturePack",
        "getGraphMemoryProviderSpikeReadinessGate",
        "getGraphMemoryProviderSpikeRunbook",
        "getGraphMemoryProviderSpikeDryRunResultTemplate",
        "getGraphMemoryProviderSpikeMockResultReport",
        "getGraphMemoryProviderSpikeReviewGate",
        "getGraphMemoryProviderSpikeManualApprovalPack",
        "getGraphMemoryProviderSpikeManualApprovalEvidenceChecklist",
        "getGraphMemoryProviderSpikeOptInEvidenceSnapshot",
        "getGraphMemoryProviderSpikeOptInNoGoMatrix",
        "getGraphMemoryProviderSpikeOptInOperatorChecklist",
        "getGraphMemoryProviderSpikeOptInReviewPacket",
        "getGraphMemoryProviderSpikeOptInDecisionLedgerPreview",
        "getGraphMemoryProviderSpikeOptInFinalReadinessSummary",
        "getGraphMemoryProviderSpikeOptInHumanSignoffSchemaDraft",
        "getGraphMemoryProviderSpikeOptInConfigDraft",
        "getGraphMemoryProviderSpikeLocalProviderContract",
        "getGraphMemoryProviderSpikeSingleFixtureDryRunHarness",
        "getGraphMemoryProviderSpikeMockCompatibleAdapter",
        "getGraphMemoryProviderSpikeManualMockAdapterReview",
        "getLLMProfileAssignment",
        "getRetrievalSamplesTrendSnapshot",
        "getPromptBudgetPack",
    }.issubset(client_methods)
    assert report["summary"]["typed_client_method_count"] == 65
    assert client_methods["getCardsWorkspace"]["response_type"] == "CardsWorkspaceReport"
    assert (
        client_methods["getVectorRetrievalReadiness"]["response_type"]
        == "VectorRetrievalReadinessReport"
    )
    assert (
        client_methods["getEmbeddingEvaluationSamples"]["response_type"]
        == "EmbeddingEvaluationSamplesReport"
    )
    assert "contract-secret" not in text
    assert "LLM_API_KEY" not in text
    assert "SEEDREAM_API_KEY" not in text


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def running_server(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SEEDREAM_API_KEY", "")
    port = _free_port()
    httpd = server.start_browser_server("127.0.0.1", port, open_browser=False)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        httpd.shutdown()
        httpd.server_close()


def _get(port: int, path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"error": raw}
        return exc.code, body


def test_api_contract_http_ok(running_server):
    status, body = _get(running_server, "/api/settings/api-contract")

    assert status == 200
    assert body["version"] == "openapi-typed-client-mvp"
    assert body["summary"]["endpoint_count"] >= 10
    assert any(
        endpoint["path"] == "/api/settings/model-configuration"
        for endpoint in body["endpoints"]
    )
