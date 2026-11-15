import React, { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Image,
  Modal,
  Pressable,
  ScrollView,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import {
  SafeAreaProvider,
  SafeAreaView,
  useSafeAreaInsets,
} from "react-native-safe-area-context";
import Ionicons from "@expo/vector-icons/Ionicons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { LocationPicker, Locality } from "./src/location/LocationPicker";
import { api, API_BASE_URL } from "./src/api";
import {
  BasketItem,
  MAX_BASKET_ITEMS,
  Product,
  changeQuantity,
  restoreBasket,
  lowestPrice,
  matchesProduct,
  productName,
} from "./src/catalog/model";
import { Category, useCatalog } from "./src/catalog/useCatalog";
import { Language, languages, MessageKey } from "./src/i18n";
import { Input, Text, UIProvider, useUI } from "./src/ui";
import { s } from "./src/styles";
const tabs = [
  { id: "groceries", label: "food", icon: "cart-outline" },
  { id: "technology", label: "technology", icon: "laptop-outline" },
  { id: "fuel", label: "fuel", icon: "car-outline" },
  { id: "basket", label: "list", icon: "list-outline" },
] as const;
const menu = [
  { id: "scan", label: "scan", icon: "scan-outline" },
  { id: "login", label: "login", icon: "person-outline" },
  { id: "receipts", label: "receipts", icon: "receipt-outline" },
  { id: "font", label: "font", icon: "text-outline" },
  { id: "language", label: "language", icon: "language-outline" },
] as const;
type Screen = "catalog" | "basket" | (typeof menu)[number]["id"];
type Comparison = {
  quotes: {
    branch_id: string | null;
    retailer_code: string;
    complete: boolean;
    total_eur: string | null;
  }[];
  cheapest: unknown;
};
const storageKey = "spestovnik-preview-001"; // Keep the previous preview's saved list/locality.
function Button({
  label,
  onPress,
  primary = false,
  disabled = false,
}: {
  label: string;
  onPress: () => void;
  primary?: boolean;
  disabled?: boolean;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      disabled={disabled}
      onPress={onPress}
      style={[s.button, primary && s.primary, disabled && { opacity: 0.45 }]}
    >
      <Text
        style={{
          color: primary ? "#fff" : "#19562a",
          fontWeight: "600",
          textAlign: "center",
        }}
      >
        {label}
      </Text>
    </Pressable>
  );
}
function AddButton({
  name,
  onAdd,
  disabled,
}: {
  name: string;
  onAdd: () => boolean;
  disabled: boolean;
}) {
  const { t } = useUI();
  const [added, setAdded] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`${t("add")} ${name}`}
      disabled={disabled}
      onPress={() => {
        if (!onAdd()) return;
        clearTimeout(timer.current);
        setAdded(true);
        timer.current = setTimeout(() => setAdded(false), 1000);
      }}
      style={[s.add, added && s.added]}
    >
      <Ionicons
        name="cart-outline"
        size={22}
        color={added ? "#fff" : "#f48100"}
      />
    </Pressable>
  );
}
export default function App() {
  return (
    <SafeAreaProvider>
      <UIProvider>
        <Main />
      </UIProvider>
    </SafeAreaProvider>
  );
}
function Main() {
  const { t, language, setLanguage, fontScale, setFontScale } = useUI();
  const insets = useSafeAreaInsets();
  const contentRef = useRef<ScrollView>(null);
  const [category, setCategory] = useState<Category>("groceries"),
    [screen, setScreen] = useState<Screen>("catalog"),
    [menuOpen, setMenuOpen] = useState(false);
  const [locality, setLocality] = useState<Locality | null>(null),
    [basket, setBasket] = useState<BasketItem[]>([]),
    [restored, setRestored] = useState(false);
  const [view, setView] = useState<"products" | "stores">("products"),
    [demo, setDemo] = useState(true),
    [fuel, setFuel] = useState<MessageKey>("petrol");
  const [query, setQuery] = useState(""),
    [searchOpen, setSearchOpen] = useState(false),
    [selected, setSelected] = useState<string[]>([]),
    [draft, setDraft] = useState<string[]>([]);
  const [notice, setNotice] = useState<MessageKey | "">(""),
    [barcode, setBarcode] = useState(""),
    [lookup, setLookup] = useState(false),
    [comparing, setComparing] = useState(false);
  const [quote, setQuote] = useState<{ key: string; data: Comparison } | null>(
    null,
  );
  const catalog = useCatalog(category, locality?.id, demo);
  useEffect(() => {
    contentRef.current?.scrollTo({ y: 0, animated: false });
  }, [screen, category]);
  const comparisonKey = JSON.stringify({ basket, locality: locality?.id });
  const comparison = quote?.key === comparisonKey ? quote.data : null;
  useEffect(() => {
    let alive = true;
    AsyncStorage.getItem(storageKey)
      .then((raw) => {
        if (!alive || !raw) return;
        const saved = JSON.parse(raw);
        setBasket(restoreBasket(saved.basket));
        const l = saved.locality;
        if (l && typeof l.id === "string" && typeof l.name === "string")
          setLocality({
            id: l.id,
            name: l.name,
            name_bg: l.name_bg,
            name_latin: l.name_latin,
            type: l.type,
            municipality: l.municipality,
            region: l.region,
          });
      })
      .catch(() => {
        if (alive) setNotice("savedError");
      })
      .finally(() => {
        if (alive) setRestored(true);
      });
    return () => {
      alive = false;
    };
  }, []);
  useEffect(() => {
    if (restored)
      AsyncStorage.setItem(
        storageKey,
        JSON.stringify({ basket, locality }),
      ).catch(() => setNotice("saveError"));
  }, [basket, locality, restored]);
  const displayName = (p: Product) =>
    p.is_demo && p.id === "demo-milk"
      ? t("demoMilk")
      : p.is_demo && p.id === "demo-oil"
        ? t("demoOil")
        : p.is_demo && p.id === "demo-sugar"
          ? t("demoSugar")
          : productName(p);
  function change(p: Product, delta: number) {
    if (delta > 0 && !restored) return false;
    if (
      delta > 0 &&
      basket.length >= MAX_BASKET_ITEMS &&
      !basket.some((i) => i.product.id === p.id)
    ) {
      setNotice("limit");
      return false;
    }
    setBasket((items) => changeQuantity(items, p, delta));
    setQuote(null);
    return true;
  }
  function switchTab(id: Category | "basket") {
    setNotice("");
    if (id === "basket") {
      setScreen("basket");
      return;
    }
    if (category !== id) {
      setQuery("");
      setSelected([]);
      setDraft([]);
      setSearchOpen(false);
    }
    setCategory(id);
    setScreen("catalog");
  }
  async function compare() {
    if (!locality) {
      setNotice("compareLocation");
      return;
    }
    if (basket.some((i) => i.product.is_demo)) {
      setNotice("demoCompare");
      return;
    }
    if (!basket.length) return;
    const key = comparisonKey;
    setComparing(true);
    setNotice("");
    try {
      const data = await api<Comparison>("/api/v1/baskets/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          locality_id: locality.id,
          items: basket.map((i) => ({
            product_id: i.product.id,
            quantity: i.quantity,
          })),
          include_online: false,
        }),
      });
      setQuote({ key, data });
    } catch {
      setNotice("compareError");
    } finally {
      setComparing(false);
    }
  }
  async function findBarcode() {
    if (!/^\d{8,14}$/.test(barcode)) {
      setNotice("invalidBarcode");
      return;
    }
    setLookup(true);
    setNotice("");
    try {
      const p = await api<Product>(`/api/v1/products/barcode/${barcode}`);
      Alert.alert(p.name, t("addQuestion"), [
        { text: t("cancel"), style: "cancel" },
        { text: t("add"), onPress: () => change(p, 1) },
      ]);
    } catch (e) {
      setNotice(String(e).includes("404") ? "unknownBarcode" : "searchError");
    } finally {
      setLookup(false);
    }
  }
  const active =
    screen === "basket" ? "basket" : screen === "catalog" ? category : null;
  const title =
    screen === "catalog"
      ? category === "groceries" && view === "products"
        ? "products"
        : "stores"
      : screen === "basket"
        ? "list"
        : screen;
  const visible = catalog.products.filter(
    (p) => !selected.length || selected.includes(p.id),
  );
  function productCard(p: Product) {
    const price = lowestPrice(p, catalog.prices, catalog.stores);
    return (
      <View key={p.id} style={s.card}>
        {p.image_url ? (
          <Image
            accessibilityLabel={displayName(p)}
            source={{ uri: p.image_url.replace(/^http:/, "https:") }}
            style={s.photo}
            resizeMode="contain"
          />
        ) : (
          <View style={s.photo}>
            <Ionicons name="cube-outline" size={48} color="#63816a" />
          </View>
        )}
        <View style={{ flex: 1, gap: 4 }}>
          {p.is_demo && <Text style={s.badge}>{t("demo")}</Text>}
          <Text style={s.productName}>{displayName(p)}</Text>
          <Text style={s.meta}>
            {p.package ||
              [p.package_quantity, p.package_unit].filter(Boolean).join(" ")}
          </Text>
          <Text style={price === null ? s.meta : s.price}>
            {price === null
              ? t(catalog.storeError ? "priceUnavailable" : "noPrice")
              : `${t("from")} ${price.toFixed(2)} €`}
          </Text>
        </View>
        <AddButton
          name={displayName(p)}
          disabled={!restored}
          onAdd={() => change(p, 1)}
        />
      </View>
    );
  }
  return (
    <SafeAreaView style={s.page} edges={["top", "bottom"]}>
      <StatusBar style="light" />
      <View style={s.header}>
        <Image
          source={require("./assets/money-bag-logo.png")}
          accessibilityLabel="Спестовник"
          style={s.logo}
          resizeMode="contain"
        />
        <View style={{ flex: 1 }}>
          <Text style={s.brand}>Спестовник</Text>
          <Text style={s.tagline}>{t("tagline")}</Text>
        </View>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={t("settings")}
          accessibilityState={{ expanded: menuOpen }}
          style={s.settingsButton}
          onPress={() => setMenuOpen(true)}
        >
          <Ionicons name="ellipsis-vertical" size={25} color="#fff" />
        </Pressable>
      </View>
      <View style={s.tabs}>
        {tabs.map((tab) => (
          <Pressable
            key={tab.id}
            accessibilityRole="tab"
            accessibilityLabel={t(tab.label)}
            accessibilityState={{ selected: active === tab.id }}
            style={[s.tab, active === tab.id && s.activeTab]}
            onPress={() => switchTab(tab.id)}
          >
            <Ionicons
              name={tab.icon}
              size={24}
              color={active === tab.id ? "#fff" : "#19562a"}
            />
            <Text style={[s.tabText, active === tab.id && { color: "#fff" }]}>
              {t(tab.label)}
            </Text>
            {tab.id === "basket" && basket.length > 0 && (
              <Text style={s.count}>
                {basket.reduce((n, i) => n + i.quantity, 0)}
              </Text>
            )}
          </Pressable>
        ))}
      </View>
      <ScrollView
        ref={contentRef}
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={s.body}
      >
        <LocationPicker
          apiBaseUrl={API_BASE_URL}
          selected={locality}
          onSelect={(l) => {
            setLocality(l);
            setQuote(null);
          }}
        />
        <View style={s.headingRow}>
          {screen !== "catalog" && screen !== "basket" && (
            <Pressable
              accessibilityRole="button"
              accessibilityLabel={t("back")}
              onPress={() => setScreen("catalog")}
              style={s.button}
            >
              <Ionicons name="arrow-back" color="#19562a" size={20} />
            </Pressable>
          )}
          <Text style={s.heading}>{t(title)}</Text>
          {screen === "catalog" && (
            <Button
              label={t("refresh")}
              onPress={() => {
                catalog.refresh();
                setNotice("");
                setSelected([]);
                setDraft([]);
              }}
            />
          )}
        </View>
        {!!notice && (
          <Text accessibilityLiveRegion="polite" style={s.notice}>
            {t(notice)}
          </Text>
        )}
        {screen === "catalog" && (
          <>
            {!!catalog.storeError && (
              <Text style={s.notice}>{t(catalog.storeError)}</Text>
            )}
            {category === "groceries" && (
              <View style={s.row}>
                <Button
                  label={t("products")}
                  primary={view === "products"}
                  onPress={() => setView("products")}
                />
                <Button
                  label={`${t("stores")} (${catalog.stores.length})`}
                  primary={view === "stores"}
                  onPress={() => setView("stores")}
                />
              </View>
            )}
            {category === "fuel" && (
              <>
                <View style={s.row}>
                  {(["petrol", "diesel", "lpg"] as const).map((f) => (
                    <Button
                      key={f}
                      label={t(f)}
                      primary={fuel === f}
                      onPress={() => setFuel(f)}
                    />
                  ))}
                </View>
                <Text style={s.notice}>{t("fuelPending")}</Text>
              </>
            )}
            {category === "groceries" && view === "products" ? (
              <>
                <Input
                  accessibilityLabel={t("searchProduct")}
                  placeholder={t("searchProduct")}
                  style={s.input}
                  value={query}
                  onFocus={() => {
                    setSearchOpen(true);
                    setDraft(selected);
                  }}
                  onChangeText={(value) => {
                    setQuery(value);
                    setSearchOpen(true);
                  }}
                />
                {searchOpen && (
                  <View style={s.panel}>
                    {catalog.products
                      .filter(
                        (p) =>
                          matchesProduct(p, query) ||
                          displayName(p)
                            .toLocaleLowerCase(language)
                            .includes(query.trim().toLocaleLowerCase(language)),
                      )
                      .map((p) => (
                        <Pressable
                          key={p.id}
                          accessibilityRole="checkbox"
                          accessibilityState={{ checked: draft.includes(p.id) }}
                          style={s.option}
                          onPress={() =>
                            setDraft((d) =>
                              d.includes(p.id)
                                ? d.filter((id) => id !== p.id)
                                : [...d, p.id],
                            )
                          }
                        >
                          <Ionicons
                            name={
                              draft.includes(p.id)
                                ? "checkbox"
                                : "square-outline"
                            }
                            size={24}
                            color="#267133"
                          />
                          <Text style={{ flex: 1, color: "#264c30" }}>
                            {displayName(p)}
                          </Text>
                        </Pressable>
                      ))}
                    <View style={s.row}>
                      <Button
                        label={t("clear")}
                        onPress={() => {
                          setDraft([]);
                          setSelected([]);
                          setQuery("");
                        }}
                      />
                      <Button
                        label={`${t("apply")} (${draft.length})`}
                        primary
                        onPress={() => {
                          setSelected(draft);
                          setSearchOpen(false);
                        }}
                      />
                    </View>
                  </View>
                )}
                <Pressable
                  accessibilityRole="switch"
                  accessibilityState={{ checked: demo }}
                  style={s.option}
                  onPress={() => setDemo(!demo)}
                >
                  <Ionicons
                    name={demo ? "checkbox" : "square-outline"}
                    color="#267133"
                    size={22}
                  />
                  <Text style={[s.meta, { flex: 1 }]}>{t("demoToggle")}</Text>
                </Pressable>
                {catalog.loading && <ActivityIndicator color="#19562a" />}
                {!!catalog.error && (
                  <View style={{ gap: 8 }}>
                    <Text style={s.notice}>{t(catalog.error)}</Text>
                    <Button label={t("retry")} onPress={catalog.refresh} />
                  </View>
                )}
                {visible.map(productCard)}
                {!catalog.loading && !catalog.error && !visible.length && (
                  <Text style={s.meta}>{t("emptyProducts")}</Text>
                )}
              </>
            ) : (
              <>
                {!locality ? (
                  <Text style={s.notice}>{t("selectLocation")}</Text>
                ) : catalog.storeLoading ? (
                  <ActivityIndicator color="#19562a" />
                ) : null}
                {catalog.stores.map((store) => (
                  <View key={store.id} style={s.store}>
                    <View style={s.storeMark}>
                      <Ionicons
                        name={
                          category === "fuel"
                            ? "car-outline"
                            : "storefront-outline"
                        }
                        size={25}
                        color="#19562a"
                      />
                    </View>
                    <View style={{ flex: 1, gap: 5 }}>
                      <Text style={s.productName}>{store.retailer_name}</Text>
                      <Text style={s.meta}>{store.address}</Text>
                      <Text style={s.meta}>{t("noPrice")}</Text>
                    </View>
                  </View>
                ))}
                {locality &&
                  !catalog.storeLoading &&
                  !catalog.storeError &&
                  !catalog.stores.length && (
                    <Text style={s.notice}>{t("noStores")}</Text>
                  )}
              </>
            )}
          </>
        )}
        {screen === "basket" && (
          <>
            {!basket.length && <Text style={s.notice}>{t("emptyList")}</Text>}
            {basket.map(({ product: p, quantity }) => (
              <View key={p.id} style={s.panel}>
                <View
                  style={{
                    flexDirection: "row",
                    alignItems: "center",
                    gap: 12,
                  }}
                >
                  {p.image_url && (
                    <Image
                      source={{ uri: p.image_url.replace(/^http:/, "https:") }}
                      style={{ width: 64, height: 76 }}
                      resizeMode="contain"
                    />
                  )}
                  <View style={{ flex: 1, gap: 5 }}>
                    <Text style={s.productName}>{displayName(p)}</Text>
                    {p.is_demo && (
                      <Text style={s.meta}>{t("demoProduct")}</Text>
                    )}
                  </View>
                </View>
                <View style={s.row}>
                  <Button
                    label="−"
                    disabled={comparing}
                    onPress={() => change(p, -1)}
                  />
                  <Text
                    accessibilityLabel={`${t("quantity")} ${quantity}`}
                    style={s.price}
                  >
                    {quantity}
                  </Text>
                  <Button
                    label="+"
                    disabled={comparing}
                    onPress={() => change(p, 1)}
                  />
                  <Button
                    label={t("remove")}
                    disabled={comparing}
                    onPress={() => {
                      setBasket((items) =>
                        items.filter((i) => i.product.id !== p.id),
                      );
                      setQuote(null);
                    }}
                  />
                </View>
              </View>
            ))}
            <Button
              label={t(comparing ? "comparing" : "compare")}
              primary
              disabled={comparing || !basket.length}
              onPress={compare}
            />
            {comparison && (
              <View style={s.panel}>
                <Text style={s.productName}>
                  {t(comparison.cheapest ? "quotes" : "incomplete")}
                </Text>
                {comparison.quotes.map((q, i) => (
                  <Text key={i} style={s.meta}>
                    {catalog.stores.find((store) => store.id === q.branch_id)
                      ?.retailer_name || q.retailer_code}
                    :{" "}
                    {q.complete && q.total_eur !== null
                      ? `${Number(q.total_eur).toFixed(2)} €`
                      : t("missingPrices")}
                  </Text>
                ))}
                <Text style={s.meta}>{t("travelExcluded")}</Text>
              </View>
            )}
          </>
        )}
        {screen === "scan" && (
          <>
            <Text style={s.notice}>{t("scanPending")}</Text>
            <Text style={s.productName}>{t("barcode")}</Text>
            <Input
              accessibilityLabel={t("barcode")}
              value={barcode}
              onChangeText={setBarcode}
              keyboardType="number-pad"
              maxLength={14}
              style={s.input}
              placeholder={t("barcodePlaceholder")}
            />
            <Button
              primary
              label={t(lookup ? "searching" : "findProduct")}
              disabled={lookup || !restored}
              onPress={findBarcode}
            />
          </>
        )}
        {screen === "login" && (
          <Text style={s.notice}>{t("loginPending")}</Text>
        )}
        {screen === "receipts" && (
          <Text style={s.notice}>{t("receiptsPending")}</Text>
        )}
        {screen === "language" && (
          <View style={s.panel}>
            {languages.map((l) => (
              <Pressable
                key={l.code}
                accessibilityRole="radio"
                accessibilityLabel={l.name}
                accessibilityState={{ checked: language === l.code }}
                onPress={() => setLanguage(l.code as Language)}
                style={[s.choice, language === l.code && s.selectedChoice]}
              >
                <Text style={[s.productName, { flex: 1 }]}>{l.name}</Text>
                {language === l.code && (
                  <Ionicons name="checkmark" color="#267133" size={23} />
                )}
              </Pressable>
            ))}
          </View>
        )}
        {screen === "font" && (
          <View style={s.panel}>
            {(
              [
                { scale: 0.9, label: "small" },
                { scale: 1, label: "normal" },
                { scale: 1.15, label: "large" },
                { scale: 1.3, label: "extraLarge" },
              ] as const
            ).map((size) => (
              <Pressable
                key={size.scale}
                accessibilityRole="radio"
                accessibilityLabel={t(size.label)}
                accessibilityState={{ checked: fontScale === size.scale }}
                onPress={() => setFontScale(size.scale)}
                style={[s.choice, fontScale === size.scale && s.selectedChoice]}
              >
                <Text style={[s.productName, { flex: 1 }]}>
                  {t(size.label)}
                </Text>
                {fontScale === size.scale && (
                  <Ionicons name="checkmark" color="#267133" size={23} />
                )}
              </Pressable>
            ))}
            <Text style={s.meta}>{t("fontPreview")}</Text>
          </View>
        )}
      </ScrollView>
      <Modal
        transparent
        visible={menuOpen}
        animationType="fade"
        onRequestClose={() => setMenuOpen(false)}
      >
        <View style={{ flex: 1 }}>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel={t("cancel")}
            style={s.menuBackdrop}
            onPress={() => setMenuOpen(false)}
          />
          <View
            accessibilityRole="menu"
            style={[s.menu, { top: insets.top + 54 }]}
          >
            {menu.map((item) => (
              <Pressable
                key={item.id}
                accessibilityRole="menuitem"
                accessibilityLabel={t(item.label)}
                style={s.menuItem}
                onPress={() => {
                  setMenuOpen(false);
                  setScreen(item.id);
                  setNotice("");
                }}
              >
                <Ionicons name={item.icon} color="#19562a" size={22} />
                <Text style={s.menuText}>{t(item.label)}</Text>
              </Pressable>
            ))}
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}
