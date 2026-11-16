import React from "react";
import { View } from "react-native";
import { Button } from "../Action";
import { useUI } from "../ui";
import { s } from "../styles";
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
  const { t } = useUI();
  const fuel = category === "fuel";
  return (
    <View testID="catalog-toolbar" style={s.headingRow}>
      <Button
        layout="equal"
        labelSize={13}
        label={fuel ? t("stations") : `${t("stores")} (${count})`}
        primary={fuel ? !fuelExpanded : view === "stores"}
        onPress={() => onView("stores")}
      />
      <Button
        layout="equal"
        label={t(fuel ? "fuelType" : "products")}
        primary={fuel ? fuelExpanded : view === "products"}
        expanded={fuel ? fuelExpanded : undefined}
        onPress={() => (fuel ? onFuel() : onView("products"))}
      />
      <Button layout="snug" refreshOutline label={t("refresh")} onPress={onRefresh} />
    </View>
  );
}
