import React, { useState } from "react";
import { Pressable, View } from "react-native";
import { Product, Store, matchesProduct } from "../catalog/model";
import { Input, Text, useUI } from "../ui";
import { Button } from "../Action";
import { s } from "../styles";
import { useSession } from "./session";
export function ReceiptItemReview({
  receiptId,
  itemId,
  receiptBranch,
  products,
  stores,
  onSubmitted,
}: {
  receiptId: string;
  itemId: string;
  receiptBranch: string | null;
  products: Product[];
  stores: Store[];
  onSubmitted: () => Promise<void>;
}) {
  const { t } = useUI(),
    session = useSession();
  const [open, setOpen] = useState(false),
    [query, setQuery] = useState(""),
    [product, setProduct] = useState<Product | null>(null),
    [branch, setBranch] = useState<string | null>(receiptBranch),
    [unitPrice, setUnitPrice] = useState(""),
    [confirmed, setConfirmed] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(false);
  const valid =
    /^\d{1,8}(?:[.,]\d{1,4})?$/.test(unitPrice) &&
    Number(unitPrice.replace(",", ".")) > 0 &&
    product &&
    branch &&
    stores.some((s) => s.id === branch) &&
    confirmed;
  async function submit() {
    if (!valid || !product || !branch) return;
    setBusy(true);
    setError(false);
    try {
      await session.request(
        `/api/v1/receipts/${receiptId}/items/${itemId}/submit-price`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            product_id: product.id,
            branch_id: branch,
            price_eur: unitPrice.replace(",", "."),
            expires_at: new Date(
              Date.now() + 24 * 60 * 60 * 1000,
            ).toISOString(),
          }),
        },
      );
      setOpen(false);
      await onSubmitted();
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }
  if (!open)
    return (
      <Button label={t("reviewReceiptItem")} onPress={() => setOpen(true)} />
    );
  return (
    <View style={s.panel}>
      <Text style={s.meta}>{t("receiptMatchHelp")}</Text>
      <Input
        accessibilityLabel={t("receiptProduct")}
        placeholder={t("receiptProduct")}
        style={s.input}
        value={query}
        onChangeText={(value) => {
          setQuery(value);
          setProduct(null);
          setConfirmed(false);
        }}
      />
      {product ? (
        <Text>{product.name}</Text>
      ) : (
        products
          .filter(
            (p) =>
              !p.is_demo &&
              p.category_code === "groceries" &&
              matchesProduct(p, query),
          )
          .slice(0, 12)
          .map((p) => (
            <Button key={p.id} label={p.name} onPress={() => setProduct(p)} />
          ))
      )}
      <Text style={s.meta}>{t("receiptBranch")}</Text>
      {stores
        .filter((store) => !receiptBranch || store.id === receiptBranch)
        .map((store) => (
          <Pressable
            key={store.id}
            accessibilityRole="radio"
            accessibilityState={{ checked: branch === store.id }}
            aria-checked={branch === store.id}
            style={[s.choice, branch === store.id && s.selectedChoice]}
            onPress={() => {
              setBranch(store.id);
              setConfirmed(false);
            }}
          >
            <Text>
              {store.retailer_name} · {store.address}
            </Text>
          </Pressable>
        ))}
      {!stores.some((s) => s.id === branch) && (
        <Text style={s.notice}>{t("selectLocation")}</Text>
      )}
      <Input
        accessibilityLabel={t("receiptUnitPrice")}
        placeholder={t("receiptUnitPrice")}
        style={s.input}
        keyboardType="decimal-pad"
        value={unitPrice}
        maxLength={13}
        onChangeText={(v) => {
          setUnitPrice(v);
          setConfirmed(false);
        }}
      />
      <Pressable
        accessibilityRole="checkbox"
        accessibilityState={{ checked: confirmed }}
        aria-checked={confirmed}
        style={s.choice}
        onPress={() => setConfirmed(!confirmed)}
      >
        <Text>
          {confirmed ? "☑ " : "☐ "}
          {t("receiptConfirm")}
        </Text>
      </Pressable>
      <Button
        primary
        label={t(busy ? "working" : "submitForReview")}
        disabled={busy || !valid}
        onPress={submit}
      />
      <Button
        label={t("cancel")}
        disabled={busy}
        onPress={() => setOpen(false)}
      />
      {error && <Text style={s.notice}>{t("receiptError")}</Text>}
    </View>
  );
}
