/** Retry only safe reads during a transient outage or free-host cold start. */
function aborted() {
  const error = new Error("Request cancelled");
  error.name = "AbortError";
  return error;
}
function pause(ms: number, signal?: AbortSignal | null): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(aborted());
    const cancel = () => {
      clearTimeout(timer);
      signal?.removeEventListener("abort", cancel);
      reject(aborted());
    };
    const timer = setTimeout(() => {
      signal?.removeEventListener("abort", cancel);
      resolve();
    }, ms);
    signal?.addEventListener("abort", cancel, { once: true });
  });
}
export async function fetchWithRetry<T = Response>(
  url: string,
  init: RequestInit = {},
  { timeoutMs = 20000, retries = 2, retryDelayMs = 400 } = {},
  readResponse: (response: Response) => Promise<T> = async (response) => response as unknown as T,
): Promise<T> {
  const attempts = (init.method ?? "GET").toUpperCase() === "GET"
    ? Math.min(2, Math.max(0, Math.floor(retries))) : 0;
  for (let attempt = 0; attempt <= attempts; attempt++) {
    if (init.signal?.aborted) throw aborted();
    const controller = new AbortController();
    let timedOut = false;
    const cancel = () => controller.abort();
    init.signal?.addEventListener("abort", cancel, { once: true });
    const timer = setTimeout(() => { timedOut = true; controller.abort(); }, timeoutMs);
    try {
      const response = await fetch(url, { ...init, signal: controller.signal });
      if (![502, 503, 504].includes(response.status) || attempt === attempts)
        return await readResponse(response);
    } catch (error) {
      const timeout = error instanceof Error && error.name === "AbortError";
      if (init.signal?.aborted || attempt === attempts ||
        (!timedOut && !timeout && !(error instanceof TypeError))) throw error;
    } finally {
      clearTimeout(timer);
      init.signal?.removeEventListener("abort", cancel);
    }
    await pause(retryDelayMs, init.signal);
  }
  throw new Error("Read request retry budget exhausted");
}
