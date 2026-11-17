import React, { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { Text, Input, useUI } from "../ui";
import { filterLocalities } from "../catalog/model";
export type Locality = {
  id: string;
  name: string;
  name_bg?: string | null;
  name_latin?: string | null;
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
  const { t } = useUI();
  const [query, setQuery] = useState(""),
    [results, setResults] = useState<Locality[]>([]),
    [open, setOpen] = useState(false),
    [loading, setLoading] = useState(false),
    [error, setError] = useState(false),
    [retry, setRetry] = useState(0);
  useEffect(() => {
    if (!open || query.trim().length < 2) {
      setResults([]);
      setLoading(false);
      setError(false);
      return;
    }
    let cancelled = false;
    const controller = new AbortController();
    setLoading(true);
    setError(false);
    setResults([]);
    let timeout: ReturnType<typeof setTimeout>;
    const timer = setTimeout(async () => {
      timeout = setTimeout(() => controller.abort(), 60000);
      try {
        const response = await fetch(
          `${apiBaseUrl.replace(/\/$/, "")}/api/v1/localities?q=${encodeURIComponent(query.trim())}`,
          { signal: controller.signal },
        );
        if (!response.ok) throw Error("Location search unavailable");
        const rows: Locality[] = await response.json();
        if (!cancelled) setResults(filterLocalities(rows, query));
      } catch {
        if (!cancelled) setError(true);
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
  }, [query, open, apiBaseUrl, retry]);
  return (
    <View style={s.wrap}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={t("location")}
        accessibilityState={{ expanded: open }}
        onPress={() => setOpen(!open)}
        style={s.trigger}
      >
        <Ionicons name="location-outline" size={22} color="#19562a" />
        <Text style={s.title}>
          {selected?.name_bg || selected?.name || t("location")}
        </Text>
        <Ionicons
          name={open ? "chevron-up" : "chevron-down"}
          size={19}
          color="#19562a"
        />
      </Pressable>
      {open && (
        <View style={s.menu}>
          <Input
            accessibilityLabel={t("searchLocation")}
            placeholder={t("searchLocation")}
            value={query}
            maxLength={80}
            onChangeText={setQuery}
            autoCorrect={false}
            style={s.input}
          />
          {loading ? (
            <ActivityIndicator color="#19562a" />
          ) : error ? (
            <>
              <Text style={s.meta}>{t("locationUnavailable")}</Text>
              <Pressable
                accessibilityRole="button"
                onPress={() => setRetry((v) => v + 1)}
                style={s.option}
              >
                <Text>{t("retry")}</Text>
              </Pressable>
            </>
          ) : (
            results.map((l) => (
              <Pressable
                key={l.id}
                accessibilityRole="button"
                style={s.option}
                onPress={() => {
                  const clean = {
                    id: l.id,
                    name: l.name,
                    name_bg: l.name_bg,
                    name_latin: l.name_latin,
                    type: l.type,
                    municipality: l.municipality,
                    region: l.region,
                  };
                  onSelect(clean);
                  setOpen(false);
                  setQuery("");
                }}
              >
                <Text style={s.optionTitle}>{l.name_bg || l.name}</Text>
                <Text style={s.meta}>
                  {[l.municipality, l.region].filter(Boolean).join(" · ")}
                </Text>
              </Pressable>
            ))
          )}
          {!loading &&
            !error &&
            query.trim().length >= 2 &&
            !results.length && <Text style={s.meta}>{t("noLocations")}</Text>}
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
    gap: 9,
    paddingHorizontal: 12,
    paddingVertical: 9,
    minHeight: 44,
    borderRadius: 13,
    borderWidth: 1,
    borderColor: "#dae2d6",
    backgroundColor: "#fff",
  },
  title: { flex: 1, fontSize: 15, fontWeight: "600", color: "#234b2d" },
  menu: {
    padding: 10,
    borderWidth: 1,
    borderColor: "#dae2d6",
    borderRadius: 13,
    gap: 8,
    backgroundColor: "#fff",
  },
  input: {
    fontSize: 16,
    padding: 10,
    borderWidth: 1,
    borderColor: "#dae2d6",
    borderRadius: 10,
    color: "#233c2a",
  },
  option: {
    paddingVertical: 10,
    minHeight: 44,
    borderBottomWidth: 1,
    borderBottomColor: "#edf0e9",
  },
  optionTitle: { fontSize: 15, color: "#234b2d", fontWeight: "600" },
  meta: { fontSize: 12, color: "#617363", marginTop: 3 },
});
