import directorySnapshot from "../../assets/catalogue/merchant-directory.json";
import { useEffect, useState } from "react";
import { ActivityIndicator, View } from "react-native";
import { api, httpStatus } from "../api";
import { Button } from "../Action";
import { Text, useUI } from "../ui";
import type { Store } from "./model";

type Branch = Omit<Store, "branch_name"> & {
  category_code: string;
  locality_id: string;
  locality_name: string;
  municipality: string | null;
  region: string | null;
  branch_name: string | null;
};
type Page = { branches: Branch[]; next_offset: number | null };
const categoryLabels = { groceries: "food", technology: "technology", fuel: "fuel" } as const;

export function MerchantDirectoryScreen() {
  const { t, styles: s, color } = useUI();
  const [page, setPage] = useState<Page>({ branches: [], next_offset: null });
  const [request, setRequest] = useState({ offset: 0 });
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [snapshot, setSnapshot] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setFailed(false);
    api<Page>(`/api/v1/merchant-directory?offset=${request.offset}`, { signal: controller.signal })
      .then(result => {
        if (controller.signal.aborted) return;
        setSnapshot(false);
        setPage(previous => ({
          branches: request.offset === 0 ? result.branches :
            [...new Map([...previous.branches, ...result.branches].map(branch => [branch.id, branch])).values()],
          next_offset: result.next_offset,
        }));
      })
      .catch(error => {
        if (controller.signal.aborted) return;
        if (request.offset === 0 && httpStatus(error) === 404) {
          setPage({ branches: directorySnapshot.branches, next_offset: null });
          setSnapshot(true);
        } else {
          setFailed(true);
        }
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [request]);

  const categories = new Map<string, Map<string, Branch[]>>();
  for (const branch of page.branches) {
    const category = branch.category_code === "FOOD" ? "groceries" : branch.category_code;
    const localities = categories.get(category) ?? new Map<string, Branch[]>();
    const branches = localities.get(branch.locality_id) ?? [];
    branches.push(branch);
    localities.set(branch.locality_id, branches);
    categories.set(category, localities);
  }

  return (
    <View testID="merchant-directory" style={{ gap: 11 }}>
      <Button label={t("refresh")} disabled={loading} onPress={() => setRequest({ offset: 0 })} />
      {loading && <ActivityIndicator accessibilityRole="progressbar" color={color("#19562a")} />}
      {snapshot && <Text accessibilityLiveRegion="polite" style={s.notice}>
        {t("directorySnapshot")} {directorySnapshot.checked_through}
      </Text>}
      {failed && <>
        <Text accessibilityLiveRegion="polite" style={s.notice}>{t("storesError")}</Text>
        <Button label={t("retry")} onPress={() => setRequest({ offset: request.offset })} />
      </>}
      {!loading && !failed && !page.branches.length && <Text style={s.notice}>{t("noStores")}</Text>}
      {Array.from(categories).sort(([a], [b]) => {
        const order = ["groceries", "technology", "fuel"];
        return (order.includes(a) ? order.indexOf(a) : order.length) -
          (order.includes(b) ? order.indexOf(b) : order.length);
      }).map(([category, localities]) => (
        <View key={category} style={s.panel}>
          <Text accessibilityRole="header" style={s.heading}>
            {Object.hasOwn(categoryLabels, category) ? t(categoryLabels[category as keyof typeof categoryLabels]) : category}
          </Text>
          {Array.from(localities, ([id, branches]) => (
            <View key={id} style={{ gap: 5 }}>
              <Text accessibilityRole="header" style={s.productName}>{branches[0].locality_name}</Text>
              {branches[0].region && <Text style={s.meta}>{[branches[0].municipality, branches[0].region].filter(Boolean).join(" · ")}</Text>}
              {branches.map(branch => (
                <Text key={branch.id} style={s.meta}>
                  {[branch.retailer_name, branch.branch_name, branch.address].filter(Boolean).join(" · ")}
                </Text>
              ))}
            </View>
          ))}
        </View>
      ))}
      {page.next_offset !== null && !failed &&
        <Button label={t("showMore")} disabled={loading} onPress={() => {
          if (page.next_offset !== null) setRequest({ offset: page.next_offset });
        }} />}
    </View>
  );
}
