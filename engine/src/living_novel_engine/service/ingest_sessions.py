"""Persistent chunk sessions for resumable long novel ingestion.

v0.8.7 keeps the existing import pipeline intact. This module only stores
upload chunks, validates integrity, and rebuilds the additive `upload` payload
that `import_novel_from_payload()` already understands.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import os
import shutil
import time
import uuid
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from living_novel_engine.import_novel.writer import _default_projects_dir

DEFAULT_TTL_SECONDS = 24 * 60 * 60
_MAX_TOTAL_SIZE = 128 * 1024 * 1024
_MAX_CHUNKS = 2000
_SESSION_ID_LEN = 16


class IngestSessionRequestError(ValueError):
    """Bad client input. HTTP layer maps this to 400."""


class IngestSessionNotFound(FileNotFoundError):
    """Session id is valid but no manifest exists. HTTP layer maps this to 404."""


class IngestSessionConflict(RuntimeError):
    """Valid request conflicts with current session state. Maps to 409."""


def create_ingest_session(
    *,
    name: str,
    filename: str,
    total_size: int,
    chunk_size: int,
    total_chunks: int | None = None,
    file_sha256: str = "",
    genre: str = "xianxia",
    mock: bool = True,
    force: bool = False,
    long_mode: bool = True,
    sessions_dir: Path | None = None,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> dict[str, Any]:
    _cleanup_expired(_sessions_dir(sessions_dir))
    filename = _safe_filename(filename)
    total_size = _positive_int(total_size, "total_size")
    chunk_size = _positive_int(chunk_size, "chunk_size")
    if total_size > _MAX_TOTAL_SIZE:
        raise IngestSessionRequestError("上传文件超过当前本地会话上限")
    computed_total = (total_size + chunk_size - 1) // chunk_size
    if total_chunks is None:
        total_chunks = computed_total
    total_chunks = _positive_int(total_chunks, "total_chunks")
    if total_chunks != computed_total:
        raise IngestSessionRequestError("total_chunks 与 total_size/chunk_size 不匹配")
    if total_chunks > _MAX_CHUNKS:
        raise IngestSessionRequestError("上传分片数量超过当前本地会话上限")
    if file_sha256 and not _is_sha256(file_sha256):
        raise IngestSessionRequestError("file_sha256 必须是 64 位 sha256 hex")
    ttl_seconds = _positive_int(ttl_seconds, "ttl_seconds")

    session_id = uuid.uuid4().hex[:_SESSION_ID_LEN]
    now = time.time()
    manifest = {
        "version": "v0.8.7",
        "session_id": session_id,
        "status": "uploading",
        "filename": filename,
        "total_size": total_size,
        "chunk_size": chunk_size,
        "total_chunks": total_chunks,
        "file_sha256": file_sha256,
        "created_at": now,
        "updated_at": now,
        "expires_at": now + ttl_seconds,
        "chunks": {},
        "import_request": {
            "name": str(name or "").strip(),
            "genre": str(genre or "xianxia"),
            "mock": bool(mock),
            "force": bool(force),
            "long_mode": bool(long_mode),
        },
    }
    sdir = _session_dir(session_id, sessions_dir=sessions_dir)
    (sdir / "chunks").mkdir(parents=True, exist_ok=False)
    _write_manifest(sdir, manifest)
    return _summary(manifest)


def get_ingest_session(
    session_id: str, *, sessions_dir: Path | None = None
) -> dict[str, Any]:
    sdir, manifest = _load_session(session_id, sessions_dir=sessions_dir)
    _ensure_not_expired(sdir, manifest)
    return _summary(manifest)


def write_ingest_chunk(
    session_id: str,
    *,
    index: int,
    data_b64: str,
    sha256: str = "",
    sessions_dir: Path | None = None,
) -> dict[str, Any]:
    sdir, manifest = _load_session(session_id, sessions_dir=sessions_dir)
    _ensure_not_expired(sdir, manifest)
    index = _chunk_index(index, manifest)
    if sha256 and not _is_sha256(sha256):
        raise IngestSessionRequestError("sha256 必须是 64 位 sha256 hex")
    try:
        raw = base64.b64decode(str(data_b64 or ""), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise IngestSessionRequestError("chunk.data_b64 不是合法 base64") from exc
    expected_size = _expected_chunk_size(index, manifest)
    if len(raw) != expected_size:
        raise IngestSessionRequestError(
            f"chunk {index} 大小不匹配，应为 {expected_size} B，实际 {len(raw)} B"
        )
    actual_sha = hashlib.sha256(raw).hexdigest()
    if sha256 and actual_sha != sha256:
        raise IngestSessionRequestError(f"chunk {index} sha256 校验失败")

    chunk_path = sdir / "chunks" / f"{index:06d}.part"
    existing = manifest["chunks"].get(str(index))
    duplicate = False
    if chunk_path.exists() or existing:
        old_sha = str((existing or {}).get("sha256") or "")
        if old_sha == actual_sha:
            duplicate = True
        else:
            raise IngestSessionConflict(f"chunk {index} 已存在且内容不同")
    else:
        _atomic_write_bytes(chunk_path, raw)
        manifest["chunks"][str(index)] = {
            "index": index,
            "size": len(raw),
            "sha256": actual_sha,
            "updated_at": time.time(),
        }
        manifest["updated_at"] = time.time()
        _write_manifest(sdir, manifest)

    summary = _summary(manifest)
    summary["duplicate"] = duplicate
    return summary


def build_upload_from_session(
    session_id: str, *, sessions_dir: Path | None = None
) -> dict[str, Any]:
    sdir, manifest = _load_session(session_id, sessions_dir=sessions_dir)
    _ensure_not_expired(sdir, manifest)
    missing = _missing_chunks(manifest)
    if missing:
        raise IngestSessionConflict(
            "上传分片缺失：" + ", ".join(str(i) for i in missing[:20])
        )

    raw_parts: list[bytes] = []
    chunks: list[dict[str, Any]] = []
    for index in range(int(manifest["total_chunks"])):
        path = sdir / "chunks" / f"{index:06d}.part"
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise IngestSessionConflict(f"chunk {index} 文件缺失") from exc
        meta = manifest["chunks"].get(str(index), {})
        actual_sha = hashlib.sha256(raw).hexdigest()
        if meta.get("sha256") != actual_sha:
            raise IngestSessionConflict(f"chunk {index} sha256 与 manifest 不一致")
        raw_parts.append(raw)
        chunks.append({"index": index, "data_b64": base64.b64encode(raw).decode("ascii")})

    full = b"".join(raw_parts)
    if len(full) != int(manifest["total_size"]):
        raise IngestSessionConflict("上传文件大小与 manifest 不一致")
    expected_sha = str(manifest.get("file_sha256") or "")
    if expected_sha and hashlib.sha256(full).hexdigest() != expected_sha:
        raise IngestSessionConflict("上传文件 sha256 校验失败")

    manifest["status"] = "ready"
    manifest["updated_at"] = time.time()
    _write_manifest(sdir, manifest)
    return {
        "filename": manifest["filename"],
        "total_size": manifest["total_size"],
        "chunk_size": manifest["chunk_size"],
        "chunks": chunks,
    }


def mark_ingest_session_imported(
    session_id: str, *, sessions_dir: Path | None = None
) -> dict[str, Any]:
    sdir, manifest = _load_session(session_id, sessions_dir=sessions_dir)
    manifest["status"] = "imported"
    manifest["updated_at"] = time.time()
    _write_manifest(sdir, manifest)
    return _summary(manifest)


def import_request_from_session(
    session_id: str, *, sessions_dir: Path | None = None
) -> dict[str, Any]:
    _sdir, manifest = _load_session(session_id, sessions_dir=sessions_dir)
    return dict(manifest.get("import_request") or {})


def _sessions_dir(value: Path | None = None) -> Path:
    if value is not None:
        return Path(value)
    env = os.environ.get("LNE_INGEST_SESSIONS_DIR")
    if env:
        return Path(env)
    return _default_projects_dir().parent / "_ingest_sessions"


def _session_dir(session_id: str, *, sessions_dir: Path | None = None) -> Path:
    safe = _safe_session_id(session_id)
    return _sessions_dir(sessions_dir) / safe


def _load_session(
    session_id: str, *, sessions_dir: Path | None = None
) -> tuple[Path, dict[str, Any]]:
    sdir = _session_dir(session_id, sessions_dir=sessions_dir)
    manifest_path = sdir / "manifest.json"
    if not manifest_path.exists():
        raise IngestSessionNotFound(f"ingest session not found: {session_id}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise IngestSessionConflict("ingest session manifest 损坏") from exc
    return sdir, manifest


def _write_manifest(sdir: Path, manifest: dict[str, Any]) -> None:
    sdir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(manifest, ensure_ascii=False, indent=2)
    with NamedTemporaryFile(
        "w", encoding="utf-8", dir=sdir, delete=False, newline="\n"
    ) as tmp:
        tmp.write(payload)
        tmp.write("\n")
        tmp_path = Path(tmp.name)
    tmp_path.replace(sdir / "manifest.json")


def _atomic_write_bytes(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("wb", dir=path.parent, delete=False) as tmp:
        tmp.write(raw)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def _summary(manifest: dict[str, Any]) -> dict[str, Any]:
    received = sorted(int(i) for i in manifest.get("chunks", {}).keys())
    received_bytes = sum(
        int(meta.get("size") or 0) for meta in manifest.get("chunks", {}).values()
    )
    total_size = int(manifest.get("total_size") or 0)
    progress = round(received_bytes / total_size * 100, 1) if total_size else 0
    return {
        "version": manifest.get("version", "v0.8.7"),
        "session_id": manifest["session_id"],
        "status": manifest.get("status", "uploading"),
        "filename": manifest.get("filename", ""),
        "total_size": total_size,
        "chunk_size": int(manifest.get("chunk_size") or 0),
        "total_chunks": int(manifest.get("total_chunks") or 0),
        "received_chunks": received,
        "missing_chunks": _missing_chunks(manifest),
        "received_bytes": received_bytes,
        "progress": progress,
        "created_at": manifest.get("created_at"),
        "updated_at": manifest.get("updated_at"),
        "expires_at": manifest.get("expires_at"),
        "import_request": dict(manifest.get("import_request") or {}),
    }


def _missing_chunks(manifest: dict[str, Any]) -> list[int]:
    received = {int(i) for i in manifest.get("chunks", {}).keys()}
    return [i for i in range(int(manifest["total_chunks"])) if i not in received]


def _safe_filename(filename: str) -> str:
    raw = str(filename or "").replace("\\", "/").strip()
    name = Path(raw).name
    if not name:
        raise IngestSessionRequestError("filename 不能为空")
    if len(name) > 240:
        raise IngestSessionRequestError("filename 过长")
    return name


def _safe_session_id(session_id: str) -> str:
    raw = str(session_id or "")
    if len(raw) != _SESSION_ID_LEN or not all(c in "0123456789abcdef" for c in raw):
        raise IngestSessionRequestError("invalid ingest session id")
    return raw


def _positive_int(value: int | str, field: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise IngestSessionRequestError(f"{field} 必须为正整数") from exc
    if parsed <= 0:
        raise IngestSessionRequestError(f"{field} 必须为正整数")
    return parsed


def _chunk_index(value: int | str, manifest: dict[str, Any]) -> int:
    try:
        index = int(value)
    except (TypeError, ValueError) as exc:
        raise IngestSessionRequestError("chunk.index 非法") from exc
    if index < 0 or index >= int(manifest["total_chunks"]):
        raise IngestSessionRequestError("chunk.index 超出范围")
    return index


def _expected_chunk_size(index: int, manifest: dict[str, Any]) -> int:
    total_chunks = int(manifest["total_chunks"])
    chunk_size = int(manifest["chunk_size"])
    total_size = int(manifest["total_size"])
    if index < total_chunks - 1:
        return chunk_size
    return total_size - chunk_size * (total_chunks - 1)


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(c in "0123456789abcdefABCDEF" for c in value)


def _ensure_not_expired(sdir: Path, manifest: dict[str, Any]) -> None:
    expires = float(manifest.get("expires_at") or 0)
    if expires and expires < time.time():
        manifest["status"] = "expired"
        _write_manifest(sdir, manifest)
        raise IngestSessionConflict("ingest session 已过期，请重新选择文件上传")


def _cleanup_expired(root: Path) -> None:
    if not root.exists():
        return
    now = time.time()
    for path in root.iterdir():
        if not path.is_dir():
            continue
        manifest_path = path / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        if float(manifest.get("expires_at") or 0) < now:
            shutil.rmtree(path, ignore_errors=True)
