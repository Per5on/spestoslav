import React from "react";
import { View } from "react-native";
import { Button } from "../Action";
import { useUI } from "../ui";
import { Category } from "./useCatalog";
export const fuelChoices = [
  "petrol",
  "petrol98",
  "diesel",
  "dieselPlus",
  "lpg",
] as const;
export type FuelChoice = (typeof fuelChoices)[number];
export function CatalogToolbar({
  category,
  view,
  count,
  fuelExpanded,
  onView,
  onFuel,
  onRefresh,
}: {
  category: Category;
  view: "products" | "stores";
  count: number;
  fuelExpanded: boolean;
  onView: (view: "products" | "stores") => void;
  onFuel: () => void;
  onRefresh: () => void;
}) {
  const { t, styles: s } = useUI();
  const fuel = category === "fuel";
  return (
    <View testID="catalog-toolbar" style={[s.headingRow, { alignItems: "stretch" }]}>
      {fuel && <Button
        layout="equal"
        labelSize={13}
        label={t("stations")}
        primary={!fuelExpanded}
        onPress={() => onView("stores")}
      />}
      {fuel && <Button
        layout="equal"
        labelSize={13}
        label={t("fuelType")}
        primary={fuelExpanded}
        expanded={fuelExpanded}
        onPress={onFuel}
      />}
      <Button layout="snug" compactRefresh label={t("refresh")} onPress={onRefresh} />
    </View>
  );
}
