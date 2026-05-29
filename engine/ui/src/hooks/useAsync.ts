import { useCallback, useEffect, useRef, useState } from "react";

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

// 轻量 async 取数：自动取消过期请求，提供 reload。第一版无需引入 react-query。
export function useAsync<T>(
  fn: () => Promise<T>,
  deps: ReadonlyArray<unknown>,
): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);
  const reqId = useRef(0);

  const reload = useCallback(() => setTick((t) => t + 1), []);

  useEffect(() => {
    const id = ++reqId.current;
    setLoading(true);
    setError(null);
    fn()
      .then((result) => {
        if (id === reqId.current) {
          setData(result);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (id === reqId.current) {
          setError(err instanceof Error ? err.message : String(err));
          setLoading(false);
        }
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);

  return { data, loading, error, reload };
}
