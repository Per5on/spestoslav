import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { Platform } from "react-native";
import * as SecureStore from "expo-secure-store";
import { api, API_BASE_URL } from "../api";
type User = { id: string; email: string; name: string };
type Session = { session: string; access_token: string; user: User };
type ContextValue = {
  user: User | null;
  ready: boolean;
  signIn: (email: string, password: string, register: boolean) => Promise<void>;
  signOut: () => Promise<void>;
  request: <T>(path: string, options?: RequestInit) => Promise<T>;
};
const Context = createContext<ContextValue | null>(null);
const KEY =
  "spestovnik-private-session-" + API_BASE_URL.replace(/[^a-zA-Z0-9._-]/g, "_");
export function SessionProvider({ children }: { children: React.ReactNode }) {
  const current = useRef<Session | null>(null),
    issued = useRef(0),
    generation = useRef(0);
  const pending = useRef<Promise<Session> | null>(null);
  const [user, setUser] = useState<User | null>(null),
    [ready, setReady] = useState(false);
  const memoryOnly = Platform.OS === "web";
  async function clear() {
    generation.current++;
    current.current = null;
    issued.current = 0;
    setUser(null);
    if (!memoryOnly) await SecureStore.deleteItemAsync(KEY);
  }
  async function refresh() {
    if (!current.current) throw new Error("HTTP 401");
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
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const saved = memoryOnly ? null : await SecureStore.getItemAsync(KEY);
        if (!alive || !saved) return;
        const fresh = await api<Session>("/api/v1/auth/refresh", {
          method: "POST",
          headers: { "X-Auth-Session": saved },
        });
        if (alive) {
          current.current = fresh;
          issued.current = Date.now();
          setUser(fresh.user);
        }
      } catch {
        /* A failed restore leaves private screens locked; stored session can retry next launch. */
      } finally {
        if (alive) setReady(true);
      }
    })();
    return () => {
      alive = false;
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
    if (!memoryOnly)
      await SecureStore.setItemAsync(KEY, fresh.session, {
        keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
      });
    generation.current++;
    current.current = fresh;
    issued.current = Date.now();
    setUser(fresh.user);
  }
  async function signOut() {
    const session = current.current?.session;
    let failure:unknown;
    try { await clear(); } catch(e) { failure=e; }
    try {
      if(session)await api("/api/v1/auth/sign-out",{method:"POST",headers:{"X-Auth-Session":session}});
    }catch(e){failure=e;}
    if(failure)throw failure;
  }

  async function request<T>(path: string, options: RequestInit = {}) {
    if (!current.current) throw new Error("HTTP 401");
    const before = generation.current;
    if (Date.now() - issued.current > 12 * 60 * 1000) {
      if (!pending.current)
        pending.current = refresh().finally(() => {
          pending.current = null;
        });
      try {
        await pending.current;
      } catch (e) {
        if (before === generation.current && String(e).includes("401")) await clear();
        throw e;
      }
    }
    const fresh = current.current;
    if (!fresh || before !== generation.current) throw new Error("HTTP 401");
    try {
      const result = await api<T>(path, {
        ...options,
        headers: {
          ...options.headers,
          Authorization: "Bearer " + fresh.access_token,
        },
      });
      if (before !== generation.current) throw new Error("Session changed");
      return result;
    } catch (e) {
      if (before === generation.current && String(e).includes("401")) await clear();
      throw e;
    }
  }
  return (
    <Context.Provider value={{ user, ready, signIn, signOut, request }}>
      {children}
    </Context.Provider>
  );
}
export function useSession() {
  const value = useContext(Context);
  if (!value) throw new Error("SessionProvider required");
  return value;
}
