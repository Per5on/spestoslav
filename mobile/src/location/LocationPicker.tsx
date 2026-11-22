import { useEffect, useState } from "react";
import { ActivityIndicator, Keyboard, ScrollView, StyleSheet, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { Pressable, Text, Input, useUI } from "../ui";
import { fetchWithRetry } from "../network";
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
  const { t, localStyle, color } = useUI();
  const [query, setQuery] = useState<string | null>(null),
    [results, setResults] = useState<Locality[]>([]),
    [loading, setLoading] = useState(false),
    [error, setError] = useState(false),
    [retry, setRetry] = useState(0);
  useEffect(() => {
    if (query === null || query.trim().length < 2) {
      setLoading(false);
      setError(false);
      return;
    }
    let cancelled = false;
    const controller = new AbortController();
    setLoading(true);
    setError(false);
    const timer = setTimeout(async () => {
      try {
        const rows = await fetchWithRetry<Locality[]>(
          `${apiBaseUrl.replace(/\/$/, "")}/api/v1/localities?q=${encodeURIComponent(query.trim())}`,
          { signal: controller.signal },
          { timeoutMs: 20000, retries: 2 },
          async (response) => {
            if (!response.ok) {
              const failure = new Error("Location search unavailable");
              failure.name = `HTTP${response.status}`;
              throw failure;
            }
            return (await response.json()) as Locality[];
          },
        );
        if (!cancelled) setResults(filterLocalities(rows, query));
      } catch (failure) {
        if (!cancelled) {
          console.warn("Location search unavailable", failure instanceof Error ? failure.name : "UnknownError");
          setError(true);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 300);
    return () => {
      cancelled = true;
      controller.abort();
      clearTimeout(timer);
    };
  }, [query, apiBaseUrl, retry]);
  return (
    <View style={s.wrap}>
      <View style={localStyle(s.field)}>
        <Ionicons name="location-outline" size={22} color={color("#19562a")} />
        <Input
          testID="location-search"
          accessibilityLabel={t("searchLocation")}
          placeholder={t("location")}
          value={query ?? (selected?.name_bg || selected?.name || "")}
          maxLength={80}
          onChangeText={(value) => {
            setResults([]);
            setLoading(value.trim().length >= 2);
            setError(false);
            setQuery(value);
          }}
          autoCorrect={false}
          selectTextOnFocus
          style={s.input}
        />
      </View>
      {query !== null && query.trim().length >= 2 && (
        <ScrollView style={{ maxHeight: 180 }} keyboardShouldPersistTaps="handled">
          {loading && <ActivityIndicator color={color("#19562a")} />}
          {error ? (
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
                  setQuery(null);
                  Keyboard.dismiss();
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
            !results.length && <Text style={s.meta}>{t("noLocations")}</Text>}
        </ScrollView>
      )}
    </View>
  );
}
const s = StyleSheet.create({
  wrap: { gap: 8 },
  field: {
    flexDirection: "row",
    alignItems: "center",
    gap: 9,
    paddingHorizontal: 12,
    borderRadius: 13,
    borderWidth: 1,
    borderColor: "#dae2d6",
    backgroundColor: "#fff",
  },
  input: {
    flex: 1,
    minWidth: 0,
    minHeight: 44,
    paddingVertical: 8,
    fontSize: 15,
    fontWeight: "600",
    color: "#234b2d",
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
