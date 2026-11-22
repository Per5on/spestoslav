import { useEffect, useMemo, useState } from "react";
import { ActivityIndicator, TextInput, View } from "react-native";
import { Pressable, Text, useUI } from "../ui";
import { filterMerchantDirectory, groupMerchantDirectory, loadMerchantDirectory, merchantLocalityLabel, type MerchantDirectoryEntry } from "./merchantDirectory";

/** Verified backend branches only; never invent store locations. */
export function MerchantDirectoryScreen() {
  const { t, styles: s, color } = useUI();
  const [rows, setRows] = useState<MerchantDirectoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [revision, setRevision] = useState(0);
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setFailed(false);
    setRows([]);
    setExpanded(null);
    loadMerchantDirectory(controller.signal)
      .then(data => { if (!controller.signal.aborted) setRows(data); })
      .catch(() => { if (!controller.signal.aborted) setFailed(true); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [revision]);

  const filteredRows = useMemo(() => filterMerchantDirectory(rows, query), [rows, query]);
  const categories = useMemo(() => groupMerchantDirectory(filteredRows), [filteredRows]);
  return (
    <View testID="merchant-directory" style={{ gap: 10 }}>
      <Pressable accessibilityRole="button" accessibilityLabel={t("refresh")}
        style={s.button} onPress={() => setRevision(v => v + 1)}>
        <Text>{t("refresh")}</Text>
      </Pressable>
      <TextInput testID="merchant-directory-search" accessibilityLabel={t("searchProduct")}
        placeholder={t("searchProduct")} value={query} onChangeText={setQuery}
        autoCorrect={false} style={[s.option, { color: color("#19562a") }]} />
      {loading && <ActivityIndicator accessibilityRole="progressbar" color={color("#19562a")} />}
      {failed && <Text accessibilityRole="alert" style={s.notice}>{t("storesError")}</Text>}
      {!loading && !failed && categories.length === 0 && <Text style={s.meta}>{t("noStores")}</Text>}
      {categories.map(category => (
        <View key={category.category_code} style={s.panel}>
          <Text style={s.productName}>{category.category_code === "groceries" ? t("food") :
            category.category_code === "technology" ? t("technology") :
            category.category_code === "fuel" ? t("fuel") : category.category_code}</Text>
          {category.localities.map(locality => {
            const key = category.category_code + ":" + locality.locality_id;
            const isOpen = expanded === key;
            return (
              <View key={key} style={{ gap: 6 }}>
                <Pressable accessibilityRole="button"
                  accessibilityState={{ expanded: isOpen }}
                  onPress={() => setExpanded(isOpen ? null : key)}
                  style={s.option}>
                  <Text style={s.productName}>{merchantLocalityLabel(locality)} ({locality.branches.length})</Text>
                </Pressable>
                {isOpen && locality.branches.map(branch => (
                  <View key={branch.id} style={s.store}>
                    <Text style={s.productName}>{branch.retailer_name}{branch.branch_name ? " · " + branch.branch_name : ""}</Text>
                    <Text style={s.meta}>{branch.address}</Text>
                  </View>
                ))}
              </View>
            );
          })}
        </View>
      ))}
    </View>
  );
}
