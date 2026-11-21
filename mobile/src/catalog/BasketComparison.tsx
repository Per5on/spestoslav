import { useState } from "react";
import { View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { Pressable, Text, useUI } from "../ui";
import type { BasketItem, Product, Store } from "./model";

type QuoteLine = {
  product_id: string;
  quantity: number;
  unit_price_eur: string | null;
  subtotal_eur: string | null;
  verified_at: string | null;
};
type Quote = {
  branch_id: string | null;
  branch_address?: string | null;
  retailer_code: string;
  retailer_name?: string | null;
  complete: boolean;
  total_eur: string | null;
  items?: QuoteLine[];
};
export type Comparison = { quotes: Quote[]; cheapest: Quote | null; quoted_at?: string };

function quoteKey(quote: Quote) {
  return quote.branch_id ?? quote.retailer_code;
}

export function BasketComparison({ comparison, basket, stores, productLabel }: {
  comparison: Comparison;
  basket: BasketItem[];
  stores: Store[];
  productLabel: (product: Product) => string;
}) {
  const { t, language, styles: s, color } = useUI();
  const best = comparison.cheapest ? quoteKey(comparison.cheapest) : null;
  const [expanded, setExpanded] = useState<string | null>(
    comparison.cheapest?.items ? best : null,
  );
  const prices = new Intl.NumberFormat(language, {
    style: "currency", currency: "EUR", minimumFractionDigits: 2, maximumFractionDigits: 4,
  });
  const time = new Intl.DateTimeFormat(language, { dateStyle: "short", timeStyle: "short" });
  const names = new Map(basket.map(({ product }) => [product.id, productLabel(product)]));
  const branches = new Map(stores.map(store => [store.id, store]));

  return (
    <View testID="basket-comparison" style={{ gap: 8 }}>
      <Text accessibilityRole="header" style={s.heading}>{t(best ? "quotes" : "incomplete")}</Text>
      {comparison.quoted_at &&
        <Text style={s.meta}>{t("quoteTime")} {time.format(new Date(comparison.quoted_at))}</Text>}
      {comparison.quotes.map(quote => {
        const key = quoteKey(quote);
        const branch = quote.branch_id ? branches.get(quote.branch_id) : undefined;
        const name = quote.retailer_name || branch?.retailer_name || quote.retailer_code;
        const address = quote.branch_address ?? branch?.address;
        const total = quote.complete && quote.total_eur !== null
          ? prices.format(Number(quote.total_eur)) : t("missingPrices");
        const open = key === expanded;
        const header = <>
          <View style={{ flex: 1 }}>
            <Text style={s.productName}>{name}</Text>
            {!!address && <Text style={s.meta}>{address}</Text>}
          </View>
          <View style={{ flexShrink: 1 }}>
            <Text style={quote.complete ? s.price : s.meta}>{total}</Text>
            {key === best && <Text style={s.badge}>{t("bestBasket")}</Text>}
          </View>
        </>;
        return (
          <View key={key} style={[s.panel, key === best && { borderColor: color("#267133") }]}>
            {quote.items ? (
              <Pressable accessibilityRole="button" accessibilityState={{ expanded: open }}
                aria-expanded={open} accessibilityLabel={`${name}: ${total}`}
                style={[s.headingRow, { minHeight: 44 }]} onPress={() => setExpanded(open ? null : key)}>
                {header}
                <Ionicons name={open ? "chevron-up" : "chevron-down"} color={color("#19562a")} size={18} />
              </Pressable>
            ) : <View style={s.headingRow}>{header}</View>}
            {open && quote.items?.map(item => (
              <View key={item.product_id} style={{ gap: 4 }}>
                <View style={s.headingRow}>
                  <Text style={[s.productName, { flex: 1 }]}>{names.get(item.product_id)} ×{item.quantity}</Text>
                  <Text style={s.meta}>{item.subtotal_eur === null
                    ? t("missingPrices") : prices.format(Number(item.subtotal_eur))}</Text>
                </View>
                {item.unit_price_eur !== null &&
                  <Text style={s.meta}>{t("packagePrice")} {prices.format(Number(item.unit_price_eur))}
                    {item.verified_at && ` · ${t("priceVerified")} ${time.format(new Date(item.verified_at))}`}
                  </Text>}
              </View>
            ))}
            {open && quote.complete && <Text style={s.price}>{t("basketTotal")} {total}</Text>}
          </View>
        );
      })}
      <Text style={s.meta}>{t("travelExcluded")}</Text>
    </View>
  );
}
