import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { filterLocalities } from "../catalog/model";
export type Locality = {
  id: string;
  name: string;
  name_bg?: string | null;
  name_latin?: string | null;
  postal_codes: string[];
  type: string;
  municipality?: string | null;
  region?: string | null;
};
type Props = {
  apiBaseUrl: string;
  selected: Locality | null;
  onSelect: (value: Locality) => void;
};
export function LocationPicker({ apiBaseUrl, selected, onSelect }: Props) {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<"name" | "postal">("name");
  const [results, setResults] = useState<Locality[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    if (!open || query.trim().length < 2) {
      setResults([]);
      setLoading(false);
      setError("");
      return;
    }
    let cancelled = false;
    const controller = new AbortController();
    setLoading(true);
    setError("");
    setResults([]);
    let timeout: ReturnType<typeof setTimeout>;
    const timer = setTimeout(async () => {
      timeout = setTimeout(() => controller.abort(), 60000);
      try {
        const response = await fetch(
          `${apiBaseUrl.replace(/\/$/, "")}/api/v1/localities?q=${encodeURIComponent(query.trim())}`,
          { signal: controller.signal },
        );
        if (!response.ok) throw Error("Search unavailable");
        const data: Locality[] = await response.json();
        if (!cancelled) setResults(filterLocalities(data, query, mode));
      } catch {
        if (!cancelled) setError("Търсенето временно не е достъпно.");
      } finally {
        clearTimeout(timeout);
        if (!cancelled) setLoading(false);
      }
    }, 300);
    return () => {
      cancelled = true;
      controller.abort();
      clearTimeout(timer);
      clearTimeout(timeout);
    };
  }, [query, mode, open, apiBaseUrl, retry]);
  return (
    <View style={s.wrap}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Избор на местоположение"
        accessibilityState={{ expanded: open }}
        onPress={() => setOpen(!open)}
        style={s.trigger}
      >
        <Ionicons name="location-outline" size={23} color="#19562a" />
        <View style={{ flex: 1 }}>
          <Text style={s.label}>МЕСТОПОЛОЖЕНИЕ</Text>
          <Text style={s.title}>
            {selected?.name_bg || selected?.name || "Изберете населено място"}
          </Text>
        </View>
        <Ionicons
          name={open ? "chevron-up" : "chevron-down"}
          size={20}
          color="#19562a"
        />
      </Pressable>
      {open && (
        <View style={s.menu}>
          <View style={s.row}>
            {(["name", "postal"] as const).map((m) => (
              <Pressable
                key={m}
                accessibilityRole="radio"
                accessibilityState={{ checked: mode === m }}
                onPress={() => {
                  setMode(m);
                  setQuery("");
                }}
                style={[s.mode, mode === m && s.active]}
              >
                <Text style={{ color: mode === m ? "#fff" : "#245532" }}>
                  {m === "name" ? "Населено място" : "Пощ. код"}
                </Text>
              </Pressable>
            ))}
          </View>
          <TextInput
            accessibilityLabel={
              mode === "name" ? "Търси населено място" : "Търси пощенски код"
            }
            value={query}
            onChangeText={setQuery}
            placeholder={
              mode === "name" ? "Търси населено място…" : "Търси пощенски код…"
            }
            keyboardType={mode === "postal" ? "number-pad" : "default"}
            autoCorrect={false}
            style={s.input}
          />
          {loading ? (
            <ActivityIndicator color="#19562a" />
          ) : error ? (
            <View>
              <Text style={s.meta}>{error}</Text>
              <Pressable onPress={() => setRetry(retry + 1)} style={s.mode}>
                <Text>Опитайте отново</Text>
              </Pressable>
            </View>
          ) : (
            results.map((l) => (
              <Pressable
                accessibilityRole="button"
                key={l.id}
                style={s.option}
                onPress={() => {
                  onSelect(l);
                  setOpen(false);
                  setQuery("");
                }}
              >
                <Text style={s.title}>{l.name_bg || l.name}</Text>
                <Text style={s.meta}>
                  {[l.municipality, l.region, l.postal_codes.join(", ")]
                    .filter(Boolean)
                    .join(" · ")}
                </Text>
              </Pressable>
            ))
          )}
          {!loading &&
            !error &&
            query.trim().length >= 2 &&
            !results.length && (
              <Text style={s.meta}>Няма намерени населени места.</Text>
            )}
        </View>
      )}
    </View>
  );
}
const s = StyleSheet.create({
  wrap: { gap: 8 },
  trigger: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    padding: 14,
    borderRadius: 15,
    borderWidth: 1,
    borderColor: "#dae2d6",
    backgroundColor: "#fff",
    minHeight: 64,
  },
  label: { fontSize: 11, color: "#617363", letterSpacing: 1 },
  title: { color: "#234b2d", fontWeight: "700", fontSize: 15, marginTop: 3 },
  menu: {
    padding: 12,
    borderWidth: 1,
    borderColor: "#dae2d6",
    borderRadius: 15,
    gap: 10,
    backgroundColor: "#fff",
  },
  row: { flexDirection: "row", gap: 6 },
  mode: {
    padding: 12,
    borderRadius: 10,
    backgroundColor: "#eef3e7",
    minHeight: 44,
  },
  active: { backgroundColor: "#ff8500" },
  input: {
    fontSize: 16,
    padding: 12,
    borderWidth: 1,
    borderColor: "#dae2d6",
    borderRadius: 10,
    color: "#233c2a",
  },
  option: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#edf0e9",
    minHeight: 48,
  },
  meta: { fontSize: 12, color: "#617363", marginTop: 4 },
});
