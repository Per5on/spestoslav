export const SIMULATION_MODE = process.env.EXPO_PUBLIC_SIMULATION_MODE === "true";
export const API_BASE_URL = (
  process.env.EXPO_PUBLIC_API_URL ?? "https://spestoslav-api.onrender.com"
).replace(/\/$/, "");
if (SIMULATION_MODE && (!['127.0.0.1', 'localhost'].includes(new URL(API_BASE_URL).hostname) || new URL(API_BASE_URL).protocol !== 'http:')) {
  throw new Error('Simulation mode requires a localhost-only API');
}

export async function api<T>(
  path: string,
  options: RequestInit = {},
  timeoutMs = 20000,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  const cancel = () => controller.abort();
  options.signal?.addEventListener("abort", cancel);
  if (options.signal?.aborted) controller.abort();
  try {
    const response = await fetch(API_BASE_URL + path, {
      ...options,
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    if (response.status === 204) return undefined as T;
    return (await response.json()) as T;
  } finally {
    clearTimeout(timer);
    options.signal?.removeEventListener("abort", cancel);
  }
}
