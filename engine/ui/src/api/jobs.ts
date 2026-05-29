import { api } from "./client";

export interface JobProgress {
  progress: number;
  stage: string;
  status: string;
}

/**
 * 轮询一个 job 直到 succeeded（resolve 结果）或 failed（reject 错误）。
 * `shouldStop` 返回 true 时静默中止（用于组件卸载），不再 setState。
 */
export async function pollJob<T>(
  jobId: string,
  onProgress: (p: JobProgress) => void,
  shouldStop: () => boolean,
  intervalMs = 800,
): Promise<T> {
  // eslint-disable-next-line no-constant-condition
  while (true) {
    if (shouldStop()) throw new JobCancelled();
    const job = await api.getJob<T>(jobId);
    onProgress({ progress: job.progress, stage: job.stage, status: job.status });
    if (job.status === "succeeded") return job.result as T;
    if (job.status === "failed") throw new Error(job.error || "生成失败");
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
}

export class JobCancelled extends Error {
  constructor() {
    super("cancelled");
    this.name = "JobCancelled";
  }
}
