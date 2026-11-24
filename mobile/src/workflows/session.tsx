import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { Platform } from "react-native";
import * as SecureStore from "expo-secure-store";
import { api, ApiError, httpStatus } from "../api";
import { sessionKey as KEY, type CloudErasure } from "../localData";
type User = { id: string; email: string; name: string };
type Session = { session: string; access_token: string; user: User };
type ContextValue = {
  user: User | null;
  ready: boolean;
  signIn: (email: string, password: string, register: boolean) => Promise<void>;
  restoreUnavailable: boolean;
  retryRestore: () => Promise<void>;
  /** Resolves true after the server revokes or rejects the session. */
  signOut: () => Promise<boolean>;
  /** Erases private data and the sign-in account. Rejects with the HTTP status in the error. */
  deleteAccount: () => Promise<void>;
  eraseServerData: () => Promise<CloudErasure>;
  request: <T>(
    path: string,
    options?: RequestInit,
    timeoutMs?: number,
  ) => Promise<T>;
};
const Context = createContext<ContextValue | null>(null);
/** Network failures, timeouts and 5xx are transient; 4xx answers are final. */
function transient(error: unknown) {
  const status = httpStatus(error);
  return status === null || status >= 500;
}
/** Retry an idempotent call once after a free-host cold start. */
async function retryTransient<T>(call: () => Promise<T>): Promise<T> {
  try {
    return await call();
  } catch (error) {
    if (!transient(error)) throw error;
    await new Promise((resolve) => setTimeout(resolve, 1500));
    return call();
  }
}
export function SessionProvider({ children }: { children: React.ReactNode }) {
  const current = useRef<Session | null>(null),
    issued = useRef(0),
    generation = useRef(0);
  const pending = useRef<Promise<Session> | null>(null);
  const mounted = useRef(false);
  const pendingSave = useRef<Promise<void> | null>(null);
  const [user, setUser] = useState<User | null>(null),
    [ready, setReady] = useState(false),
    [restoreUnavailable, setRestoreUnavailable] = useState(false);
  const memoryOnly = Platform.OS === "web";
  async function clear() {
    generation.current++;
    current.current = null;
    issued.current = 0;
    setUser(null);
    if (!memoryOnly) await SecureStore.deleteItemAsync(KEY);
  }
  async function refresh() {
    if (!current.current) throw new ApiError(401);
    const before = generation.current;
    const fresh = await api<Session>("/api/v1/auth/refresh", {
      method: "POST",
      headers: { "X-Auth-Session": current.current.session },
    });
    if (before !== generation.current) throw new Error("Session changed");
    current.current = fresh;
    issued.current = Date.now();
    setUser(fresh.user);
    return fresh;
  }
  async function retryRestore() {
    const before = ++generation.current;
    setReady(false);
    setRestoreUnavailable(false);
    const isCurrent = () => mounted.current && before === generation.current;
    try {
      const saved = memoryOnly ? null : await SecureStore.getItemAsync(KEY);
      if (!saved || !isCurrent()) return;
      // Wake the free-tier API before exchanging the stored provider session.
      await api("/ready", {}, 30000).catch(() => undefined);
      if (!isCurrent()) return;
      const fresh = await retryTransient(() =>
        api<Session>("/api/v1/auth/refresh", {
          method: "POST",
          headers: { "X-Auth-Session": saved },
        }),
      );
      if (isCurrent()) {
        current.current = fresh;
        issued.current = Date.now();
        setUser(fresh.user);
      }
    } catch (error) {
      if (!isCurrent()) return;
      const status = httpStatus(error);
      if (status === 401 || status === 403)
        await SecureStore.deleteItemAsync(KEY).catch(() => undefined);
      else
        setRestoreUnavailable(true);
    } finally {
      if (isCurrent()) setReady(true);
    }
  }
  useEffect(() => {
    mounted.current = true;
    void retryRestore();
    return () => {
      mounted.current = false;
    };
  }, []);
  async function signIn(email: string, password: string, register: boolean) {
    const fresh = await api<Session>(
      "/api/v1/auth/" + (register ? "sign-up" : "sign-in"),
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      },
    );
    if (!mounted.current) return;
    if (!memoryOnly)
      try {
        pendingSave.current = SecureStore.setItemAsync(KEY, fresh.session, {
          keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
        });
        await pendingSave.current;
      } catch {
        /* Stay signed in for this run rather than orphaning a live server session. */
      } finally {
        pendingSave.current = null;
      }
    if (!mounted.current) return;
    generation.current++;
    setRestoreUnavailable(false);
    current.current = fresh;
    issued.current = Date.now();
    setUser(fresh.user);
  }
  async function signOut() {
    const before = generation.current;
    const session = current.current?.session;
    if (session) {
      try {
        await api("/api/v1/auth/sign-out", {
          method: "POST",
          headers: { "X-Auth-Session": session },
        });
      } catch (error) {
        if (httpStatus(error) !== 401) return false;
      }
    }
    if (before === generation.current) await clear().catch(() => undefined);
    return true;
  }

  async function eraseServerData(): Promise<CloudErasure> {
    const inProgressSignIn = pendingSave.current;
    const session = current.current?.session;
    if (!session) {
      await inProgressSignIn?.catch(() => undefined);
      return restoreUnavailable || !ready || inProgressSignIn ? "unconfirmed" : "guest";
    }
    try {
      await request<void>("/api/v1/account/data", {
        method: "DELETE",
        headers: { "X-Auth-Session": session },
      }, 60000);
      return await signOut() ? "deleted" : "unconfirmed";
    } catch {
      return "unconfirmed";
    }
  }

  async function deleteAccount() {
    const session = current.current?.session;
    if (!session) throw new ApiError(401);
    await request<void>(
      "/api/v1/account",
      { method: "DELETE", headers: { "X-Auth-Session": session } },
      60000,
    );
    await clear().catch(() => undefined);
  }

  async function refreshSession(before: number) {
    if (!pending.current) {
      pending.current = refresh().finally(() => {
        pending.current = null;
      });
    }
    try {
      return await pending.current;
    } catch (error) {
      if (before === generation.current && httpStatus(error) === 401) await clear();
      throw error;
    }
  }

  async function request<T>(
    path: string,
    options: RequestInit = {},
    timeoutMs?: number,
  ) {
    if (!current.current) throw new ApiError(401);
    const before = generation.current;
    if (Date.now() - issued.current > 12 * 60 * 1000) await refreshSession(before);

    async function send() {
      const value = current.current;
      if (!value || before !== generation.current) throw new ApiError(401);
      const result = await api<T>(path, {
        ...options,
        headers: {
          ...options.headers,
          Authorization: "Bearer " + value.access_token,
        },
      }, timeoutMs);
      if (before !== generation.current) throw new Error("Session changed");
      return result;
    }

    const token = current.current?.access_token;
    try {
      return await send();
    } catch (error) {
      if (before !== generation.current || httpStatus(error) !== 401) throw error;
      // A rejected access token does not establish that the provider session ended.
      if (current.current?.access_token === token) await refreshSession(before);
      const method = (options.method ?? "GET").toUpperCase();
      if (method === "GET" || method === "HEAD") return send();
      throw error;
    }
  }

  return (
    <Context.Provider value={{ user, ready, restoreUnavailable, retryRestore, signIn, signOut, deleteAccount, eraseServerData, request }}>
      {children}
    </Context.Provider>
  );
}
export function useSession() {
  const value = useContext(Context);
  if (!value) throw new Error("SessionProvider required");
  return value;
}
