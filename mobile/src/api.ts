import { fetchWithRetry } from "./network";
export const SIMULATION_MODE = process.env.EXPO_PUBLIC_SIMULATION_MODE === "true";
export const API_BASE_URL = (
  process.env.EXPO_PUBLIC_API_URL ?? "https://spestoslav-api.onrender.com"
).replace(/\/$/, "");
if (SIMULATION_MODE && (!['127.0.0.1', 'localhost'].includes(new URL(API_BASE_URL).hostname) || new URL(API_BASE_URL).protocol !== 'http:')) {
  throw new Error('Simulation mode requires a localhost-only API');
}

/** Non-2xx response. The message stays `HTTP <status>` for older string checks. */
export class ApiError extends Error {
  status: number;
  constructor(status: number) {
    super(`HTTP ${status}`);
    this.name = "ApiError";
    this.status = status;
    Object.setPrototypeOf(this, ApiError.prototype);
  }
}
/** HTTP status of a failed request, or null for network errors, timeouts and cancellation. */
export function httpStatus(error: unknown): number | null {
  if (error instanceof ApiError) return error.status;
  const match = /^(?:\w+: )?HTTP (\d{3})$/.exec(error instanceof Error ? error.message : String(error));
  return match ? Number(match[1]) : null;
}

export async function api<T>(
  path: string,
  options: RequestInit = {},
  timeoutMs = 20000,
): Promise<T> {
  return fetchWithRetry<T>(API_BASE_URL + path, options, { timeoutMs }, async (response) => {
    if (!response.ok) throw new ApiError(response.status);
    if (response.status === 204) return undefined as T;
    return (await response.json()) as T;
  });
}
