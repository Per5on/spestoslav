import { BasketComparison, type Comparison } from "./src/catalog/BasketComparison";
import { contrastingInk } from "./src/appearance";
import { CategoryGroups } from "./src/catalog/CategoryGroups";
import { MerchantDirectoryScreen } from "./src/catalog/MerchantDirectoryScreen";
import { DeleteDataScreen } from "./src/navigation/DeleteDataScreen";
import { eraseLocalData, savedListKey as storageKey, type CloudErasure } from "./src/localData";
import { LegalDocument } from "./src/legal/LegalDocument";
import { groceryThumbnail, referencePhoto, sampleCredit, technologyThumbnail } from "./src/catalog/samples";
import { ProductThumbnail } from "./src/catalog/ProductThumbnail";
import { AppearanceScreen } from "./src/navigation/AppearanceScreen";
import { SettingsChoices } from "./src/navigation/SettingsChoices";
import { FeedbackScreen } from "./src/workflows/FeedbackScreen";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  ActivityIndicator,
  Image,
  Linking,
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
import { api, API_BASE_URL, SIMULATION_MODE } from "./src/api";
import {
  BasketItem,
  MAX_BASKET_ITEMS,
  Product,
  changeQuantity,
  restoreBasket,
  indexLowestPrices,
  matchesProduct,
  productName,
} from "./src/catalog/model";
import { Category, useCatalog } from "./src/catalog/useCatalog";
import { Language, languages, MessageKey } from "./src/i18n";
import { Pressable, Input, Text, UIProvider, useUI, AutoFitLabel } from "./src/ui";
import { Screen } from "./src/navigation/menu";
import { OverflowMenu } from "./src/navigation/OverflowMenu";
import { AboutScreen } from "./src/navigation/AboutScreen";
import {
  CatalogToolbar,
  fuelChoices,
  FuelChoice,
} from "./src/catalog/CatalogToolbar";
import { Button } from "./src/Action";
import { SessionProvider } from "./src/workflows/session";
import { AccountScreen } from "./src/workflows/AccountScreen";
import { ScanScreen } from "./src/workflows/ScanScreen";
import { ReceiptsScreen } from "./src/workflows/ReceiptsScreen";
const tabs = [
  { id: "groceries", label: "food", icon: "cart-outline" },
  { id: "technology", label: "technology", icon: "laptop-outline" },
  { id: "fuel", label: "fuel", icon: "car-outline" },
  { id: "basket", label: "list", icon: "list-outline" },
] as const;
function AddButton({
  name,
  onAdd,
  disabled,
}: {
  name: string;
  onAdd: () => boolean;
  disabled: boolean;
}) {
  const { t, styles: s, color } = useUI();
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
        color={added ? "#fff" : color("#f48100")}
      />
    </Pressable>
  );
}
export default function App() {
  const [reset, setReset] = useState<Promise<CloudErasure> | null>(null);
  const [resetNotice, setResetNotice] = useState<MessageKey | "">("");
  useEffect(() => {
    if (!reset) return;
    // Main and both providers are unmounted before clearing their persisted state.
    void (async () => {
      const cloud = await reset.catch(() => "unconfirmed");
      const local = await eraseLocalData().catch(() => false);
      setResetNotice(!local ? "deleteDataFailed" : cloud === "unconfirmed"
        ? "deleteDataPartial" : cloud === "deleted" ? "deleteDataDone" : "deleteDataLocal");
      setReset(null);
    })();
  }, [reset]);
  return (
    <SafeAreaProvider>
      {reset ? <View style={{ flex: 1, justifyContent: "center" }}>
        <ActivityIndicator accessibilityRole="progressbar" color="#195b27" />
      </View> : <UIProvider>
        <SessionProvider>
          <Main initialNotice={resetNotice} onErase={setReset} />
        </SessionProvider>
      </UIProvider>}
    </SafeAreaProvider>
  );
}
function Main({ initialNotice, onErase }: {
  initialNotice: MessageKey | "";
  onErase: (cloud: Promise<CloudErasure>) => void;
}) {
  const { t, language, setLanguage, fontScale, setFontScale, styles: s, color, palette } = useUI();
  const insets = useSafeAreaInsets();
  const headerInk = palette === 0 ? "#fff" : contrastingInk(color("#195b27", true));
  const selectedInk = palette === 0 ? "#fff" : contrastingInk(color("#ff8500", true));
  const contentRef = useRef<ScrollView>(null);
  const [category, setCategory] = useState<Category>("groceries"),
    [screen, setScreen] = useState<Screen>("catalog");
  const [locality, setLocality] = useState<Locality | null>(null),
    [basket, setBasket] = useState<BasketItem[]>([]),
    [restored, setRestored] = useState(false);
  const [fuel, setFuel] = useState<FuelChoice>("petrol"),
    [fuelMenuOpen, setFuelMenuOpen] = useState(false);
  const [appliedQuery, setAppliedQuery] = useState("");
  const [query, setQuery] = useState(""),
    [searchOpen, setSearchOpen] = useState(false),
    [pageSize, setPageSize] = useState(40),
    [suggestionLimit,setSuggestionLimit]=useState(40),
    [group, setGroup] = useState<string | null>(null),
    [selected, setSelected] = useState<string[]>([]),
    [draft, setDraft] = useState<string[]>([]);
  const [notice, setNotice] = useState<MessageKey | "">(initialNotice),
    [comparing, setComparing] = useState(false);
  const [quote, setQuote] = useState<{ key: string; data: Comparison } | null>(
    null,
  );
  const catalog = useCatalog(category, locality?.id, true, true, screen === "catalog" || screen === "basket");
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
    setFuelMenuOpen(false);
    if (id === "basket") {
      setScreen("basket");
      return;
    }
    if (category !== id) {
      setGroup(null);
      setQuery("");
      setSelected([]);
      setAppliedQuery("");
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
    if (new Set(basket.map((i) => i.product.category_code)).size > 1) {
      setNotice("mixedCompare");
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
  const active =
    screen === "basket" ? "basket" : screen === "catalog" ? category : null;
  const title = screen === "basket" ? "list" : screen === "catalog" ? "products" : screen;
  const fuelProduct = catalog.products.find(p => p.fuel_type === fuel);
  const [priceRevision, setPriceRevision] = useState(0);
  useEffect(() => {
    const now = Date.now();
    let next = Infinity;
    for (const row of catalog.prices) {
      const expiry = row.expires_at ? Date.parse(row.expires_at) : NaN;
      if (expiry > now) next = Math.min(next, expiry);
    }
    if (!Number.isFinite(next)) return;
    const timer = setTimeout(() => setPriceRevision(v => v + 1), Math.min(next - now, 2147483647));
    return () => clearTimeout(timer);
  }, [catalog.prices, priceRevision]);
  const priceIndex = useMemo(
    () => indexLowestPrices(catalog.prices, catalog.stores),
    [catalog.prices, catalog.stores, priceRevision],
  );
  const hasFuelPrices = Boolean(fuelProduct && priceIndex.products.has(fuelProduct.id));
  const visible = useMemo(() => {
    const ids = new Set(selected);
    return catalog.products.filter(
      p => (!group || p.group_code === group) &&
        (ids.size ? ids.has(p.id) : !appliedQuery || matchesProduct(p, appliedQuery)),
    );
  }, [catalog.products, group, selected, appliedQuery]);
  const groups = useMemo(() => [...new Set(
    catalog.products.map(p => p.group_code).filter((code): code is string => Boolean(code)),
  )], [catalog.products]);
  const groupNames: Record<string, MessageKey> = {"mobile":"groupMobile","major-appliances":"groupMajor","small-appliances":"groupSmall","tv-computing":"groupComputing","smart-home-mobility":"groupSmart","dairy-eggs":"groupDairy","bakery-breakfast":"groupBakery",produce:"groupProduce","meat-fish":"groupMeat",pantry:"groupPantry","spices-drinks":"groupSpices"};
  const normalizedQuery = query.trim().toLocaleLowerCase(language);
  const suggestions = searchOpen && normalizedQuery
    ? catalog.products.filter(p => matchesProduct(p, query) ||
        displayName(p).toLocaleLowerCase(language).includes(normalizedQuery))
    : [];
  useEffect(()=>setSuggestionLimit(40),[query,category]);
  useEffect(() => setPageSize(40), [selected, group, category]);
  function productCard(p: Product) {
    const reference = referencePhoto(p);
    const credit = p.is_demo ? sampleCredit(p.id) : reference?.credit;
    const technology = p.category_code === "technology";
    const fallback = reference?.source ?? (technology
      ? technologyThumbnail(p.id, p.group_code) : groceryThumbnail(p.group_code));
    const price = p.is_demo ? null : priceIndex.products.get(p.id) ?? null;
    return (
      <View key={p.id} style={s.card}>
        <ProductThumbnail key={catalog.revision} id={p.id} name={displayName(p)} uri={p.image_url}
          illustration={technology && p.is_demo ? fallback : undefined} fallback={fallback}
          fallbackLabel={reference ? t("representativePhoto") : undefined} />

        <View style={{ flex: 1, gap: 4 }}>
          {p.is_demo && <Text style={s.badge}>{t("demo")}</Text>}
          <Text style={s.productName}>{displayName(p)}</Text>
          {credit && (
            <Pressable accessibilityRole="link"
              onPress={() => void Linking.openURL(credit.source_url).catch(() => undefined)}>
              <Text style={[s.meta, { textDecorationLine: "underline" }]}>
                {credit.author} · {credit.license}
              </Text>
            </Pressable>
          )}
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
      <StatusBar style={headerInk === "#fff" ? "light" : "dark"} />
      <View testID="app-header" style={s.header}>
        <Image
          source={require("./assets/header-logo.webp")}
          accessibilityLabel="Спестовник"
          style={s.logo}
          resizeMode="contain"
        />
        <View style={{ flex: 1 }}>
          <AutoFitLabel label="Спестовник" baseSize={25} style={[s.brand, { color: headerInk, width: "100%" }]} />
          <Text style={[s.tagline, palette !== 0 && { color: headerInk }]}>{t("tagline")}</Text>
        </View>
        <OverflowMenu iconColor={headerInk} top={insets.top + 54} onSelect={(next) => {
          setScreen(next);
          setNotice("");
        }} />
      </View>
      <View style={s.tabs}>
        {tabs.map((tab) => (
          <Pressable
            key={tab.id}
            accessibilityRole="tab"
            accessibilityLabel={t(tab.label)}
            accessibilityState={{ selected: active === tab.id }}
            aria-selected={active === tab.id}
            style={[s.tab, active === tab.id && s.activeTab]}
            onPress={() => switchTab(tab.id)}
          >
            <Ionicons
              name={tab.icon}
              size={24}
              color={active === tab.id ? selectedInk : color("#19562a")}
            />
            <AutoFitLabel
              label={t(tab.label)}
              baseSize={12}
              allowWrap
              style={[
                s.tabText,
                { width: "100%" },
                active === tab.id && { color: selectedInk },
              ]}
            />
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
        {screen !== "merchants" && <LocationPicker
          apiBaseUrl={API_BASE_URL}
          selected={locality}
          onSelect={(l) => {
            setLocality(l);
            setQuote(null);
          }}
        />}
        {screen === "catalog" ? (
          <CatalogToolbar onRefresh={() => {
            catalog.refresh();
            setNotice("");
            setSelected([]);
            setDraft([]);
            setQuery("");
            setAppliedQuery("");
            setSearchOpen(false);
            setQuote(null);
          }}>
            {category === "fuel" ? (
              <Button label={t(fuel)} accessibilityLabel={`${t("selectedFuel")}: ${t(fuel)}`}
                expanded={fuelMenuOpen} onPress={() => setFuelMenuOpen(open => !open)} />
            ) : (
              <Input
                testID="product-search"
                accessibilityLabel={t("searchProduct")}
                placeholder={t("searchProduct")}
                style={s.productSearch}
                value={query}
                onFocus={() => {
                  if (!searchOpen) setDraft(selected);
                  setSearchOpen(true);
                }}
                onChangeText={(value) => {
                  setQuery(value);
                  setSearchOpen(true);
                }}
              />
            )}
          </CatalogToolbar>
        ) : (
          <View style={s.headingRow}>
            {screen !== "basket" && (
              <Pressable
                accessibilityRole="button"
                accessibilityLabel={t("back")}
                style={s.button}
                onPress={() =>
                  setScreen(
                    ["font", "language", "appearance", "deleteData", "terms", "privacy"].includes(screen)
                      ? "settings"
                      : screen === "feedback"
                        ? "about"
                        : "catalog",
                  )
                }
              >
                <Ionicons name="arrow-back" color={color("#19562a")} size={20} />
              </Pressable>
            )}
            <Text style={[s.heading, ["settings", "language", "font", "terms", "privacy"].includes(screen) && { color: "#111" }]}>{t(title)}</Text>
          </View>
        )}
        {SIMULATION_MODE && <Text style={s.notice}>{t("simulationNotice")}</Text>}
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
            {category === "fuel" && (
              <>
                {fuelMenuOpen && (
                  <View
                    testID="fuel-type-menu"
                    accessibilityRole="radiogroup"
                    style={s.panel}
                  >
                    {fuelChoices.map((f) => (
                      <Pressable
                        key={f}
                        accessibilityRole="radio"
                        accessibilityLabel={t(f)}
                        accessibilityState={{ checked: fuel === f }}
                        aria-checked={fuel === f}
                        style={[s.choice, fuel === f && s.selectedChoice]}
                        onPress={() => {
                          setFuel(f);
                          setFuelMenuOpen(false);
                        }}
                      >
                        <Text style={s.productName}>{t(f)}</Text>
                        {fuel === f && (
                          <Ionicons
                            name="checkmark"
                            size={22}
                            color={color("#267133")}
                          />
                        )}
                      </Pressable>
                    ))}
                  </View>
                )}
                {!hasFuelPrices && <Text style={s.notice}>{t("fuelPending")}</Text>}
              </>
            )}
            {category !== "fuel" ? (
              <>
                {searchOpen && (
                  <View style={s.panel}>
                    {suggestions.slice(0,suggestionLimit)
                      .map((p) => (
                        <Pressable
                          key={p.id}
                          accessibilityRole="checkbox"
                          accessibilityLabel={displayName(p)}
                          accessibilityState={{ checked: draft.includes(p.id) }}
                          aria-checked={draft.includes(p.id)}
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
                            color={color("#267133")}
                          />
                          <Text style={{ flex: 1, color: "#264c30" }}>
                            {displayName(p)}
                          </Text>
                        </Pressable>
                      ))}
                    {suggestions.length>suggestionLimit&&<Button label={`${t("showMore")} (${suggestionLimit}/${suggestions.length})`} onPress={()=>setSuggestionLimit(n=>n+40)}/>}
                    <View style={s.row}>
                      <Button
                        label={t("clear")}
                        onPress={() => {
                          setDraft([]);
                          setSelected([]);
                          setAppliedQuery("");
                          setQuery("");
                        }}
                      />
                      <Button
                        label={`${t("apply")} (${draft.length || (query.trim() ? suggestions.length : 0)})`}
                        primary
                        onPress={() => {
                          setSelected(draft);
                          setAppliedQuery(draft.length ? "" : query.trim());
                          setSearchOpen(false);
                        }}
                      />
                    </View>
                  </View>
                )}
                {catalog.loading && <ActivityIndicator color={color("#19562a")} />}
                {!!catalog.error && (
                  <View style={{ gap: 8 }}>
                    <Text style={s.notice}>{t(catalog.error)}</Text>
                    <Button label={t("retry")} onPress={catalog.refresh} />
                  </View>
                )}
                {catalog.cached && (
                  <Text style={s.meta}>{t("cachedCatalog")}</Text>
                )}
                {!!groups.length && (
                  <CategoryGroups key={category} technology={category === "technology"}
                    groups={[
                      { code: null, label: t(category === "technology" ? "allProducts" : "allGroceries") },
                      ...groups.map(code => ({ code, label: groupNames[code] ? t(groupNames[code]) : code })),
                    ]}
                    selected={group} onSelect={code => {
                      setGroup(code);
                      setSelected([]);
                      setDraft([]);
                      setAppliedQuery("");
                      setQuery("");
                      setSearchOpen(false);
                    }} />
                )}
                {visible.slice(0, pageSize).map(productCard)}
                {visible.length > pageSize && (
                  <Button
                    label={`${t("showMore")} (${pageSize}/${visible.length})`}
                    onPress={() => setPageSize((n) => n + 40)}
                  />
                )}
                {!catalog.loading && !catalog.error && !visible.length && (
                  <Text style={s.meta}>{t("emptyProducts")}</Text>
                )}
              </>
            ) : (
              <>
                {!locality ? <>
                  <Text style={s.notice}>{t("chainCoverage")}</Text>
                  {catalog.chainLoading && <ActivityIndicator color={color("#19562a")} />}
                  {catalog.chainError && <Text style={s.notice}>{t("storesError")}</Text>}
                  {catalog.retailers.map(chain => <View key={chain.code} style={s.store}>
                    <View style={{ flex: 1, gap: 5 }}>
                      <Text style={s.productName}>{chain.name}</Text>
                      {chain.website_url && <Text style={s.meta}>{chain.website_url}</Text>}
                      <Text style={s.meta}>{t("chainOverview")}</Text>
                    </View>
                  </View>)}
                </> : catalog.storeLoading ? <ActivityIndicator color={color("#19562a")} /> : null}
                {catalog.stores.map((store) => {
                  const fuelQuote = fuelProduct && category === "fuel" ? priceIndex.branches.get(store.id)?.get(fuelProduct.id) ?? null : null;
                  return (
                  <View key={store.id} style={s.store}>
                    <View style={s.storeMark}>
                      <Ionicons
                        name={
                          category === "fuel"
                            ? "car-outline"
                            : "storefront-outline"
                        }
                        size={25}
                        color={color("#19562a")}
                      />
                    </View>
                    <View style={{ flex: 1, gap: 5 }}>
                      <Text style={s.productName}>{store.retailer_name}</Text>
                      <Text style={s.meta}>{store.address}</Text>
                      <Text style={fuelQuote === null ? s.meta : s.price}>{fuelQuote === null ? t("noPrice") : `${fuelQuote.toFixed(2)} €/L`}</Text>
                    </View>
                  </View>
                );})}
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
        {screen === "merchants" && <MerchantDirectoryScreen />}
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
                      source={{ uri: p.image_url }}
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
              <BasketComparison key={comparison.quoted_at ?? comparisonKey}
                comparison={comparison} basket={basket} stores={catalog.stores} />
            )}
          </>
        )}
        {screen === "scan" && (
          <ScanScreen onAdd={(product) => change(product, 1)} />
        )}
        {screen === "login" && <AccountScreen />}
        {screen === "receipts" && (
          <ReceiptsScreen
            localityId={locality?.id}
            onLogin={() => setScreen("login")}
          />
        )}
        {screen === "settings" && (
          <SettingsChoices items={[{ value: "appearance", label: t("appearance"), icon: "color-palette-outline" }, { value: "font", label: t("font"), icon: "text-outline" }, { value: "language", label: t("language"), icon: "language-outline" }, { value: "terms", label: t("terms"), icon: "document-text-outline" }, { value: "privacy", label: t("privacy"), icon: "shield-checkmark-outline" }, { value: "deleteData", label: t("deleteData"), icon: "trash-outline" }]}
            onSelect={value => setScreen(value as "appearance" | "font" | "language" | "terms" | "privacy" | "deleteData")} />
        )}
        {screen === "deleteData" && <DeleteDataScreen onErase={onErase} />}
        {screen === "appearance" && <AppearanceScreen />}
        {screen === "about" && <AboutScreen onFeedback={() => setScreen("feedback")} />}
        {screen === "feedback" && <FeedbackScreen />}
        {(screen === "terms" || screen === "privacy") && <LegalDocument key={screen} kind={screen} />}
        {screen === "language" && <SettingsChoices radio items={languages.map(l => ({ value: l.code, label: l.name }))}
          selected={language} onSelect={value => setLanguage(value as Language)} />}
        {screen === "font" && <View style={{ gap: 12 }}>
          <SettingsChoices radio items={[
            { value: "0.9", label: t("small") }, { value: "1", label: t("normal") },
            { value: "1.15", label: t("large") }, { value: "1.3", label: t("extraLarge") },
          ]} selected={String(fontScale)} onSelect={value => setFontScale(Number(value))} />
          <Text style={{ color: "#111" }}>{t("fontPreview")}</Text>
        </View>}

      </ScrollView>
    </SafeAreaView>
  );
}
