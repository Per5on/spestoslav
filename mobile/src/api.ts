import { fetchWithRetry } from "./network";
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
  return fetchWithRetry<T>(API_BASE_URL + path, options, { timeoutMs }, async (response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    if (response.status === 204) return undefined as T;
    return (await response.json()) as T;
  });
}
