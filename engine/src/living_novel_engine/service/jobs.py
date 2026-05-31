"""console-free 异步 Job（v0.7 第九刀：进度轮询）。

把耗时生成任务从同步阻塞 POST 改为可轮询 job。**本地内存**，单进程；
不上数据库 / 队列 / SSE / WebSocket，不做多用户隔离。

设计为通用基础设施：`JobStore.submit(kind, runner)` 接收一个
`runner(update) -> dict` 回调，业务逻辑仍由调用方复用既有 service 拼装，
本模块不复制任何推演/导入/创世逻辑。
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable

JOB_KINDS = ("intervention", "import_novel", "story_genesis", "resume_continue")

# runner 接收一个进度回调 update(progress: int, stage: str)，返回结果 dict。
ProgressFn = Callable[[int, str], None]
RunnerFn = Callable[[ProgressFn], dict]

_MAX_JOBS = 100


@dataclass
class JobRecord:
    job_id: str
    kind: str
    status: str = "queued"  # queued | running | succeeded | failed
    progress: int = 0
    stage: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    result: dict | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "kind": self.kind,
            "status": self.status,
            "progress": self.progress,
            "stage": self.stage,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "result": self.result,
            "error": self.error,
        }


class JobStore:
    """线程安全的内存 job 注册表，保留最近 N 个 job。"""

    def __init__(self, max_jobs: int = _MAX_JOBS, max_workers: int = 2):
        self._jobs: "OrderedDict[str, JobRecord]" = OrderedDict()
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._max = max_jobs

    @staticmethod
    def _new_id() -> str:
        return uuid.uuid4().hex[:16]

    def submit(self, kind: str, runner: RunnerFn) -> JobRecord:
        if kind not in JOB_KINDS:
            raise ValueError(f"未知 job kind: {kind!r}")
        rec = JobRecord(job_id=self._new_id(), kind=kind)
        with self._lock:
            self._jobs[rec.job_id] = rec
            self._evict_locked()
        self._executor.submit(self._run, rec, runner)
        return rec

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)

    def count(self) -> int:
        with self._lock:
            return len(self._jobs)

    def _run(self, rec: JobRecord, runner: RunnerFn) -> None:
        self._touch(rec, status="running", progress=5, stage="排队中")

        def update(progress: int, stage: str) -> None:
            self._touch(rec, progress=max(0, min(100, int(progress))), stage=stage)

        try:
            result = runner(update)
            self._touch(
                rec, status="succeeded", progress=100, stage="完成", result=result
            )
        except Exception as exc:  # 任何业务/运行异常都转为 job failed，不向外抛
            self._touch(rec, status="failed", stage="失败", error=str(exc))

    def _touch(self, rec: JobRecord, **kw) -> None:
        with self._lock:
            for key, value in kw.items():
                setattr(rec, key, value)
            rec.updated_at = time.time()

    def _evict_locked(self) -> None:
        while len(self._jobs) > self._max:
            self._jobs.popitem(last=False)


# 进程级单例（本地单机）。
JOBS = JobStore()
