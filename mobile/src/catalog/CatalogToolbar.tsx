import type { ReactNode } from "react";
import { View } from "react-native";
import { Button } from "../Action";
import { useUI } from "../ui";

export const fuelChoices = ["petrol", "petrol98", "diesel", "dieselPlus", "lpg"] as const;
export type FuelChoice = (typeof fuelChoices)[number];

export function CatalogToolbar({ children, onRefresh }: {
  children: ReactNode;
  onRefresh: () => void;
}) {
  const { t, styles: s } = useUI();
  return (
    <View testID="catalog-toolbar" style={[s.headingRow, { alignItems: "stretch" }]}>
      <View style={{ flex: 1, minWidth: 0 }}>{children}</View>
      <Button compactRefresh label={t("refresh")} onPress={onRefresh} />
    </View>
  );
}
