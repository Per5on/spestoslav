import { BasketComparison } from "./src/catalog/BasketComparison";
import { contrastingInk } from "./src/appearance";
import { CategoryGroups } from "./src/catalog/CategoryGroups";
import { MerchantDirectoryScreen } from "./src/catalog/MerchantDirectoryScreen";
import { DeleteDataScreen } from "./src/navigation/DeleteDataScreen";
import { eraseLocalData, savedListKey as storageKey, type CloudErasure } from "./src/localData";
import { LegalDocument } from "./src/legal/LegalDocument";
import { productArtwork } from "./src/catalog/samples";
import { useThumbnailManifest } from "./src/catalog/thumbnailManifest";
import { ProductThumbnail } from "./src/catalog/ProductThumbnail";
import { AppearanceScreen } from "./src/navigation/AppearanceScreen";
import { SettingsChoices } from "./src/navigation/SettingsChoices";
import { FeedbackScreen } from "./src/workflows/FeedbackScreen";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Platform,
  RefreshControl,
  ScrollView,
  View,
} from "react-native";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import {
  SafeAreaProvider,
  SafeAreaView,
  useSafeAreaInsets,
} from "react-native-safe-area-context";
import Ionicons from "@expo/vector-icons/Ionicons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { LocationPicker, Locality } from "./src/location/LocationPicker";
import { API_BASE_URL, SIMULATION_MODE } from "./src/api";
import {
  BasketItem,
  MAX_BASKET_ITEMS,
  Product,
  type Retailer,
  changeQuantity,
  comparePublishedBasket,
  moyatMagazinOffers,
  type Comparison,
  restoreBasket,
  indexLowestPrices, indexIndicativePrices, groupFuelResults,
  prioritizePricedProducts,
  matchesSearchText, productSearchText, searchText,
  duplicateProductQualifiers,
  productName,
} from "./src/catalog/model";
import { groupGroceryChoices, isGroceryChoice } from "./src/catalog/groceryChoices";
import { loadCatalogProducts, onlineResource, pricesResource, storesResource, type Category } from "./src/catalog/catalogData";
import { enableCatalogSync } from "./src/catalog/backgroundSync";
import { useCatalog } from "./src/catalog/useCatalog";
import { Language, languages, MessageKey } from "./src/i18n";
import { Pressable, Input, Text, UIProvider, useUI, AutoFitLabel } from "./src/ui";
import { Screen } from "./src/navigation/menu";
import { OverflowMenu } from "./src/navigation/OverflowMenu";
import { AboutScreen } from "./src/navigation/AboutScreen";
import { ThirdPartiesScreen } from "./src/navigation/ThirdPartiesScreen";
import {
  CatalogToolbar,
  FuelChoice,
} from "./src/catalog/CatalogToolbar";
import { Button } from "./src/Action";
import { SessionProvider } from "./src/workflows/session";
import { AccountScreen } from "./src/workflows/AccountScreen";
import { ScanScreen } from "./src/workflows/ScanScreen";
import { ReceiptsScreen } from "./src/workflows/ReceiptsScreen";

if (Platform.OS !== "web") {
  void SplashScreen.preventAutoHideAsync().catch(() => undefined);
}

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
const mockBatch = SIMULATION_MODE && Platform.OS === "web" && typeof location !== "undefined"
  ? Number(new URLSearchParams(location.search).get("batch"))
  : 0;
const tabBatchSize = mockBatch === 10 || mockBatch === 20 ? mockBatch : 15;
type TabRow =
  | { kind: "product"; key: string; value: Product }
  | { kind: "basket"; key: string; value: BasketItem }
  | { kind: "fuel"; key: string; value: ReturnType<typeof groupFuelResults>[number] }
  | { kind: "retailer"; key: string; value: Retailer };

function Main({ initialNotice, onErase }: {
  initialNotice: MessageKey | "";
  onErase: (cloud: Promise<CloudErasure>) => void;
}) {
  const startupShown = useRef(false);
  const { t, language, setLanguage, fontScale, setFontScale, styles: s, color, palette } = useUI();
  const insets = useSafeAreaInsets();
  const [headerHeight, setHeaderHeight] = useState(48);
  const headerInk = palette === 0 ? "#fff" : contrastingInk(color("#195b27", true));
  const selectedInk = palette === 0 ? "#fff" : contrastingInk(color("#ff8500", true));
  const contentRef = useRef<ScrollView>(null);
  const tabList = useRef<FlatList<TabRow>>(null);
  const [category, setCategory] = useState<Category>("groceries"),
    [screen, setScreen] = useState<Screen>("catalog");
  const [locality, setLocality] = useState<Locality | null>(null),
    [basket, setBasket] = useState<BasketItem[]>([]),
    [restored, setRestored] = useState(false);
  const [fuel, setFuel] = useState<FuelChoice>("petrol");
  const [appliedQuery, setAppliedQuery] = useState("");
  const [selectedProductId, setSelectedProductId] = useState<string>();
  const [query, setQuery] = useState(""),
    [searchOpen, setSearchOpen] = useState(false),
    [suggestionLimit, setSuggestionLimit] = useState(tabBatchSize),
    [group, setGroup] = useState<string | null>(null);
  const [notice, setNotice] = useState<MessageKey | "">(initialNotice),
    [comparing, setComparing] = useState(false);
  const [quote, setQuote] = useState<{ key: string; data: Comparison } | null>(
    null,
  );
  const catalog = useCatalog(category, locality?.id, SIMULATION_MODE, {
    active: restored && (screen === "catalog" || screen === "basket"),
  });
  const thumbnailUrls = useThumbnailManifest(catalog.revision, restored);
  useEffect(() => {
    if (restored) void enableCatalogSync().catch(error => console.warn("Could not schedule catalogue sync", error));
  }, [restored]);
  useEffect(() => {
    contentRef.current?.scrollTo({ y: 0, animated: false });
    tabList.current?.scrollToOffset({ offset: 0, animated: false });
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
  const qualifiers = useMemo(() => duplicateProductQualifiers([
    ...basket.map(item => item.product), ...catalog.products,
  ]), [basket, catalog.products]);
  const displayName = useCallback((p: Product) => {
    if (p.is_demo) {
      if (p.id === "demo-milk") return t("demoMilk");
      if (p.id === "demo-oil") return t("demoOil");
      if (p.id === "demo-sugar") return t("demoSugar");
    }
    const qualifier = isGroceryChoice(p) ? p.package : qualifiers.get(p.id) ?? p.identityQualifier;
    return qualifier ? `${productName(p)} · ${qualifier}` : productName(p);
  }, [qualifiers, t]);
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
    const qualifier = qualifiers.get(p.id) ?? p.identityQualifier;
    setBasket((items) => changeQuantity(items, qualifier ? { ...p, identityQualifier: qualifier } : p, delta));
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
      setGroup(null);
      setQuery("");
      setAppliedQuery("");
      setSelectedProductId(undefined);
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
    const category = basket[0]?.product.category_code;
    if (!category) return;
    if ((category !== "groceries" && category !== "technology") ||
        basket.some(item => item.product.category_code !== category)) {
      setNotice("mixedCompare");
      return;
    }
    const key = comparisonKey;
    const { signal } = new AbortController();
    setComparing(true);
    setNotice("");
    try {
      const scope = { category, localityId: locality.id } as const;
      const storesRead = storesResource.load(scope, signal);
      const [offers, stores, groceries, localPrices] = await Promise.all([
        onlineResource.load({ category, localityId: "" }, signal),
        storesRead,
        category === "groceries" && basket.some(({ product }) => isGroceryChoice(product))
          ? loadCatalogProducts({ category }, signal, false, () => {})
          : undefined,
        category === "groceries" ? storesRead.then(rows => rows.some(row => row.retailer_code === "moyat_magazin")
          ? pricesResource.load(scope, signal).catch(() => []) : []) : [],
      ]);
      const localOffers = [...offers, ...moyatMagazinOffers(localPrices, stores)];
      const eligibleOffers = groceries ? groupGroceryChoices(groceries.products, localOffers).offers : localOffers;
      const data = comparePublishedBasket(basket, eligibleOffers, stores);
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
    for (const row of catalog.online) {
      const expiry = Date.parse(row.valid_until);
      if (expiry > now) next = Math.min(next, expiry);
    }
    if (!Number.isFinite(next)) return;
    const timer = setTimeout(() => setPriceRevision(v => v + 1), Math.min(next - now, 2147483647));
    return () => clearTimeout(timer);
  }, [catalog.prices, catalog.online, priceRevision]);
  const priceIndex = useMemo(
    () => indexLowestPrices(catalog.prices, catalog.stores),
    [catalog.prices, catalog.stores, priceRevision],
  );
  const catalogue = useMemo(
    () => category === "groceries" ? groupGroceryChoices(catalog.products,
      [...catalog.online, ...moyatMagazinOffers(catalog.prices, catalog.stores)]) : {
      products: catalog.products, offers: catalog.online,
    },
    [catalog.products, catalog.online, catalog.prices, catalog.stores, category, priceRevision],
  );
  const indicativePrices = useMemo(
    () => indexIndicativePrices(catalogue.offers, category === "fuel" ? catalog.stores : undefined),
    [catalogue.offers, catalog.stores, category, priceRevision],
  );
  const fuelResults = useMemo(() => category === "fuel"
    ? groupFuelResults(catalog.stores, fuelProduct?.id, priceIndex.branches, indicativePrices.chains)
    : [], [category, catalog.stores, fuelProduct?.id, priceIndex.branches, indicativePrices.chains]);
  const fuelBranchLabel = useMemo(
    () => typeof Intl.PluralRules === "function" ? new Intl.PluralRules(language) : undefined,
    [language],
  );
  const hasFuelPrices = fuelResults.some(row =>
    row.branchCount > 0 || row.stations.some(station => station.price !== undefined));
  const searchActive = searchOpen || Boolean(appliedQuery);
  const searchIndex = useMemo(() => searchActive
    ? new Map(catalogue.products.map(p => [p.id, productSearchText(p, displayName(p))]))
    : undefined, [catalogue.products, displayName, searchActive]);
  const visible = useMemo(() => {
    if (selectedProductId) return catalogue.products.filter(p => p.id === selectedProductId);
    if (appliedQuery && searchIndex) {
      const tokens = appliedQuery.split(" ");
      return catalogue.products.filter(p => matchesSearchText(searchIndex.get(p.id) ?? "", tokens));
    }
    const filtered = group ? catalogue.products.filter(p => p.group_code === group) : catalogue.products;
    return prioritizePricedProducts(filtered, indicativePrices.products);
  }, [catalogue.products, group, appliedQuery, selectedProductId, searchIndex, indicativePrices.products]);
  function refreshCatalogue() {
    catalog.refresh();
    setNotice("");
    setQuery("");
    setAppliedQuery("");
    setSelectedProductId(undefined);
    setSearchOpen(false);
    setQuote(null);
  }
  const groups = useMemo(() => [...new Set(
    catalogue.products.map(p => p.group_code).filter((code): code is string => Boolean(code)),
  )], [catalogue.products]);
  const groupNames: Record<string, MessageKey> = {"mobile":"groupMobile","major-appliances":"groupMajor","small-appliances":"groupSmall","tv-computing":"groupComputing","smart-home-mobility":"groupSmart","dairy-eggs":"groupDairy","bakery-breakfast":"groupBakery",produce:"groupProduce","meat-fish":"groupMeat",pantry:"groupPantry","spices-drinks":"groupSpices"};
  const suggestions = useMemo(() => {
    const normalizedQuery = searchText(query);
    if (!searchOpen || !normalizedQuery || !searchIndex) return [];
    const tokens = normalizedQuery.split(" ");
    return catalogue.products.filter(p => matchesSearchText(searchIndex.get(p.id) ?? "", tokens));
  }, [catalogue.products, query, searchIndex, searchOpen]);
  useEffect(() => setSuggestionLimit(tabBatchSize), [query, category]);
  function thumbnail(p: Product) {
    const art = productArtwork(p.groceryAliases ? { ...p, name: p.groceryAliases[0] } : p);
    return <ProductThumbnail key={catalog.revision} id={p.id} name={displayName(p)}
      uri={p.image_url} representativeUri={art.code ? thumbnailUrls[art.code] : undefined}
      fallback={art.source} symbolic={art.symbolic} />;
  }
  function productCard(p: Product) {
    const price = p.is_demo ? null : indicativePrices.products.get(p.id) ?? null;
    return (
      <View key={p.id} style={s.card}>
        {thumbnail(p)}

        <View style={{ flex: 1, gap: 4 }}>
          {p.is_demo && <Text style={s.badge}>{t("demo")}</Text>}
          <Text style={s.productName}>{displayName(p)}</Text>
          <Text style={s.meta}>
            {p.package ||
              [p.package_quantity, p.package_unit].filter(Boolean).join(" ")}
          </Text>
          <Text style={price === null ? s.meta : s.price}>
            {price === null
              ? t(catalog.onlineError ? "priceUnavailable" : "noPrice")
              : `${t("from")} ${price.toFixed(2)} €`}
          </Text>
          {price !== null && indicativePrices.promotionalMaxima.has(p.id) &&
            <Text style={s.meta}>{t("promotionalMaximum")}</Text>}
        </View>
        <AddButton
          name={displayName(p)}
          disabled={!restored}
          onAdd={() => change(p, 1)}
        />
      </View>
    );
  }
  const photoFooter = screen === "catalog" && category !== "fuel";
  const cachedFooter = photoFooter && catalog.cached;
  const footerError = screen === "catalog" &&
    (catalog.storeError || (category === "fuel" && !locality && catalog.chainError ? "storesError" : ""));
  const tabRows = useMemo<TabRow[]>(() => {
    if (screen === "basket") {
      return basket.map(value => ({ kind: "basket", key: value.product.id, value }));
    }
    if (screen !== "catalog") return [];
    if (category !== "fuel") {
      return visible.map(value => ({ kind: "product", key: value.id, value }));
    }
    return locality
      ? fuelResults.map(value => ({ kind: "fuel", key: value.key, value }))
      : catalog.retailers.map(value => ({ kind: "retailer", key: value.code, value }));
  }, [screen, basket, category, visible, locality, fuelResults, catalog.retailers]);
  function renderTabRow({ item }: { item: TabRow }) {
    switch (item.kind) {
      case "product":
        return productCard(item.value);
      case "retailer": {
        const chain = item.value;
        return (
          <View style={s.store}>
            <View style={{ flex: 1, gap: 5 }}>
              <Text style={s.productName}>{chain.name}</Text>
              <Text style={s.meta}>{t("chainOverview")}</Text>
            </View>
          </View>
        );
      }
      case "fuel": {
        const row = item.value;
        const count = fuelBranchLabel?.select(row.branchCount) ?? (row.branchCount === 1 ? "one" : "other");
        const label = count === "one" ? "fuelBranchOne" : count === "few" ? "fuelBranchFew" : "fuelBranchMany";
        return <View key={row.key} style={s.store}>
          <View style={s.storeMark}>
            <Ionicons name="car-outline" size={25} color={color("#19562a")} />
          </View>
          <View style={{ flex: 1, gap: 5 }}>
            <Text style={s.productName}>{row.name}</Text>
            {row.branchCount > 0 && row.estimate && (
              <>
                <Text style={s.price}>{Number(row.estimate.price_eur).toFixed(2)} €/L</Text>
                <Text style={s.meta}>{row.branchCount} {t(label)}</Text>
              </>
            )}
            {row.stations.map(({ store, price }) => (
              <View key={store.id} style={{ gap: 4 }}>
                <Text style={s.meta}>{store.address}</Text>
                <Text style={price === undefined ? s.meta : s.price}>
                  {price === undefined ? (catalog.fuelLoading ? "" : t("noPrice")) : `${price.toFixed(2)} €/L`}
                </Text>
              </View>
            ))}
          </View>
        </View>;
      }
      case "basket": {
        const { product: p, quantity } = item.value;
        return (
          <View key={p.id} style={s.panel}>
            <View
              style={{
                flexDirection: "row",
                alignItems: "center",
                gap: 12,
              }}
            >
              {(p.category_code === "groceries" || p.category_code === "technology") && thumbnail(p)}
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
        );
      }
    }
  }
  const bodyHeader = (
    <View style={{ gap: 11 }}>
      {screen === "catalog" ? (
        <CatalogToolbar onRefresh={refreshCatalogue} fuel={category === "fuel" ? fuel : undefined}
          onFuel={setFuel}>
          {category !== "fuel" && (
            <Input
              testID="product-search"
              accessibilityLabel={t("searchProduct")}
              placeholder={t("searchProduct")}
              style={s.productSearch}
              value={query}
              maxLength={80}
              returnKeyType="search"
              onFocus={() => setSearchOpen(true)}
              onChangeText={(value) => {
                setQuery(value);
                setSelectedProductId(undefined);
                setSearchOpen(true);
                if (!value.trim()) setAppliedQuery("");
              }}
              onSubmitEditing={({ nativeEvent }) => {
                const normalizedQuery = searchText(nativeEvent.text);
                setSelectedProductId(undefined);
                setAppliedQuery(normalizedQuery);
                if (normalizedQuery) setGroup(null);
                setSearchOpen(false);
                tabList.current?.scrollToOffset({ offset: 0, animated: false });
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
                    : screen === "feedback" || screen === "thirdParties"
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
          {category !== "fuel" ? (
            <>
              {suggestions.length > 0 && (
                <View testID="product-suggestions" style={s.panel}>
                  {suggestions.slice(0, suggestionLimit).map(p => (
                    <Button key={p.id} label={displayName(p)} onPress={() => {
                      setSelectedProductId(p.id);
                      setAppliedQuery("");
                      setGroup(null);
                      setQuery(displayName(p));
                      setSearchOpen(false);
                      tabList.current?.scrollToOffset({ offset: 0, animated: false });
                    }} />
                  ))}
                  {suggestions.length > suggestionLimit && (
                    <Button label={`${t("showMore")} (${suggestionLimit}/${suggestions.length})`}
                      onPress={() => setSuggestionLimit(n => n + tabBatchSize)} />
                  )}
                </View>
              )}
              {catalog.loading && <ActivityIndicator color={color("#19562a")} />}
              {!!catalog.error && (
                <View style={{ gap: 8 }}>
                  <Text style={s.notice}>{t(catalog.error)}</Text>
                  <Button label={t("retry")} onPress={catalog.refresh} />
                </View>
              )}
              {!!groups.length && (
                <CategoryGroups key={category} technology={category === "technology"}
                  groups={[
                    { code: null, label: t(category === "technology" ? "allProducts" : "allGroceries") },
                    ...groups.map(code => ({ code, label: groupNames[code] ? t(groupNames[code]) : code })),
                  ]}
                  selected={group} onSelect={code => {
                    setGroup(code);
                    setAppliedQuery("");
                    setSelectedProductId(undefined);
                    setQuery("");
                    setSearchOpen(false);
                  }} />
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
              </> : !hasFuelPrices && (
                catalog.fuelLoading
                  ? <ActivityIndicator testID="fuel-loading" color={color("#19562a")} />
                  : <Text accessibilityLiveRegion="polite" style={s.notice}>
                      {t(catalog.storeError || catalog.error || "noFuelPrices")}
                    </Text>
              )}
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
      {screen === "basket" && !basket.length && <Text style={s.notice}>{t("emptyList")}</Text>}
    </View>
  );
  const bodyFooter = (
    <View style={{ gap: 11 }}>
      {screen === "merchants" && <MerchantDirectoryScreen />}
      {screen === "basket" && (
        <>
          <Button
            label={t(comparing ? "comparing" : "compare")}
            primary
            disabled={comparing || !basket.length}
            onPress={compare}
          />
          {comparison && (
            <BasketComparison key={comparison.quoted_at ?? comparisonKey}
              comparison={comparison} basket={basket} productLabel={displayName} />
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
        <View testID="settings-columns" style={{ flexDirection: "row", gap: 8 }}>
          <View style={{ flex: 1, minWidth: 0 }}>
            <SettingsChoices singleColumn items={[
              { value: "language", label: t("language"), icon: "language-outline" },
              { value: "appearance", label: t("appearance"), icon: "color-palette-outline" },
              { value: "font", label: t("font"), icon: "text-outline" },
            ]} onSelect={value => setScreen(value as "appearance" | "font" | "language")} />
          </View>
          <View style={{ flex: 1, minWidth: 0 }}>
            <SettingsChoices singleColumn items={[
              { value: "terms", label: t("terms"), icon: "document-text-outline" },
              { value: "privacy", label: t("privacy"), icon: "shield-checkmark-outline" },
              { value: "deleteData", label: t("deleteData"), icon: "trash-outline" },
            ]} onSelect={value => setScreen(value as "deleteData" | "terms" | "privacy")} />
          </View>
        </View>
      )}
      {screen === "deleteData" && <DeleteDataScreen onErase={onErase} />}
      {screen === "appearance" && <AppearanceScreen />}
      {screen === "about" && <AboutScreen onFeedback={() => setScreen("feedback")}
        onThirdParties={() => setScreen("thirdParties")} />}
      {screen === "thirdParties" && <ThirdPartiesScreen />}
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
    </View>
  );
  return (
    <SafeAreaView style={s.page} edges={["top", "bottom"]} onLayout={() => {
      if (Platform.OS === "web" || startupShown.current) return;
      startupShown.current = true;
      SplashScreen.hide();
    }}>
      <StatusBar style={headerInk === "#fff" ? "light" : "dark"} />
      <View testID="app-header" style={s.header} onLayout={event => setHeaderHeight(event.nativeEvent.layout.height)}>
        <View style={{ flex: 1 }}>
          <AutoFitLabel label="Спестовник" baseSize={19} style={[s.brand, { color: headerInk, width: "100%" }]} />
          <Text style={[s.tagline, palette !== 0 && { color: headerInk }]}>{t("tagline")}</Text>
        </View>
        <OverflowMenu iconColor={headerInk} top={insets.top + headerHeight} onSelect={(next) => {
          setScreen(next);
          setNotice("");
        }} />
      </View>
      {screen !== "merchants" && <View style={s.locationBar}>
        <LocationPicker
          apiBaseUrl={API_BASE_URL}
          selected={locality}
          onSelect={(l) => {
            setLocality(l);
            setQuote(null);
          }}
        />
      </View>}
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
            <Ionicons testID={`tab-icon-${tab.id}`} name={tab.icon} size={20}
              accessible={false} color={active === tab.id ? selectedInk : color("#19562a")} />
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
      {screen === "catalog" || screen === "basket" ? (
        <FlatList
          key={screen === "basket" ? "basket" : category}
          ref={tabList}
          data={tabRows}
          keyExtractor={row => row.key}
          renderItem={renderTabRow}
          initialNumToRender={tabBatchSize}
          maxToRenderPerBatch={tabBatchSize}
          windowSize={5}
          keyboardShouldPersistTaps="handled"
          contentContainerStyle={s.body}
          ListHeaderComponent={bodyHeader}
          ListFooterComponent={screen === "basket" ? bodyFooter : null}
          refreshControl={Platform.OS !== "web" && screen === "catalog"
            ? <RefreshControl refreshing={catalog.refreshing} onRefresh={catalog.refresh}
                colors={[color("#19562a")]} tintColor={color("#19562a")} />
            : undefined}
        />
      ) : (
        <ScrollView ref={contentRef} keyboardShouldPersistTaps="handled" contentContainerStyle={s.body}>
          {bodyHeader}
          {bodyFooter}
        </ScrollView>
      )}
      {(photoFooter || cachedFooter || footerError) ? (
        <View testID="catalog-footer" style={s.catalogFooter} accessibilityLiveRegion="polite">
          {photoFooter && <Text style={s.catalogFooterText}>{t("illustrativePhotoShort")}</Text>}
          {!!footerError && <Text style={[s.catalogFooterText, s.catalogFooterWarning]}>{t(footerError)}</Text>}
          {cachedFooter && <Text style={s.catalogFooterText}>{t("cachedCatalog")}</Text>}
        </View>
      ) : null}
    </SafeAreaView>
  );
}
