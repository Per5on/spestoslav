import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { LocationPicker, Locality } from "./src/location/LocationPicker";
import { api, API_BASE_URL } from "./src/api";
import {
  BasketItem,
  MAX_BASKET_ITEMS,
  Product,
  Store,
  Price,
  changeQuantity,
  restoreBasket,
  lowestPrice,
  matchesProduct,
  productName,
} from "./src/catalog/model";
const tabs = [
  { id: "groceries", name: "Храни", icon: "cart-outline" },
  { id: "fuel", name: "Горива", icon: "car-outline" },
  { id: "home", name: "Дом", icon: "home-outline" },
  { id: "technology", name: "Техника", icon: "laptop-outline" },
] as const;
type Category = (typeof tabs)[number]["id"];
type Comparison = {
  quotes: {
    branch_id: string | null;
    retailer_code: string;
    complete: boolean;
    total_eur: string | null;
    price_scope: string;
  }[];
  cheapest: unknown;
};
const storageKey = "spestovnik-preview-001";
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
export default function App() {
  return (
    <SafeAreaProvider>
      <Main />
    </SafeAreaProvider>
  );
}
function Main() {
  const [category, setCategory] = useState<Category>("groceries");
  const [locality, setLocality] = useState<Locality | null>(null);
  const [basket, setBasket] = useState<BasketItem[]>([]);
  const [restored, setRestored] = useState(false);
  const [screen, setScreen] = useState<
    "catalog" | "basket" | "scan" | "checks"
  >("catalog");
  const [view, setView] = useState<"products" | "stores">("products");
  const [products, setProducts] = useState<Product[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [prices, setPrices] = useState<Price[]>([]);
  const [loading, setLoading] = useState(false);
  const [storeLoading, setStoreLoading] = useState(false);
  const [error, setError] = useState("");
  const [storeError, setStoreError] = useState("");
  const [notice, setNotice] = useState("");
  const [refresh, setRefresh] = useState(0);
  const [query, setQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const [selected, setSelected] = useState<string[]>([]);
  const [draft, setDraft] = useState<string[]>([]);
  const [demo, setDemo] = useState(true);
  const [fuel, setFuel] = useState("Бензин 95");
  const [quote, setComparison] = useState<{
    key: string;
    data: Comparison;
  } | null>(null);
  const comparisonKey = JSON.stringify({ basket, locality: locality?.id });
  const comparison = quote?.key === comparisonKey ? quote.data : null;
  const [comparing, setComparing] = useState(false);
  const [barcode, setBarcode] = useState("");
  const [lookup, setLookup] = useState(false);
  useEffect(() => {
    let alive = true;
    AsyncStorage.getItem(storageKey)
      .then((raw) => {
        if (!alive || !raw) return;
        const saved = JSON.parse(raw);
        setBasket(restoreBasket(saved.basket));
        if (
          saved.locality &&
          typeof saved.locality.id === "string" &&
          typeof saved.locality.name === "string" &&
          Array.isArray(saved.locality.postal_codes)
        )
          setLocality(saved.locality);
      })
      .catch(() => {
        if (alive) setNotice("Запазените настройки не могат да се заредят.");
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
      ).catch(() =>
        setNotice("Списъкът не може да се запази на устройството."),
      );
  }, [basket, locality, restored]);
  useEffect(() => {
    let alive = true;
    const controller = new AbortController();
    setLoading(true);
    setError("");
    setProducts([]);
    setSelected([]);
    setDraft([]);
    setQuery("");
    setSearchOpen(false);
    if (category !== "groceries") {
      setLoading(false);
      return () => {
        alive = false;
        controller.abort();
      };
    }
    (async () => {
      try {
        const rows = await api<Product[]>(
          `/api/v1/products?category_code=${category}&limit=100`,
          { signal: controller.signal },
        );
        // Demo photos are fetched separately and never inserted into the real catalog.
        if (category === "groceries" && demo) {
          try {
            const sample = await api<{ is_demo: boolean; products: Product[] }>(
              "/api/v1/demo/catalog",
              { signal: controller.signal },
            );
            if (alive)
              setProducts([
                ...rows,
                ...(sample.is_demo
                  ? sample.products.map((p) => ({ ...p, is_demo: true }))
                  : []),
              ]);
          } catch {
            if (alive) {
              setProducts(rows);
              setError("Примерните снимки не се заредиха. Опитайте отново.");
            }
          }
        } else if (alive) setProducts(rows);
      } catch {
        if (alive)
          setError(
            "Каталогът не се зареди. Проверете връзката и опитайте отново.",
          );
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
      controller.abort();
    };
  }, [category, demo, refresh]);
  useEffect(() => {
    let alive = true;
    const controller = new AbortController();
    setStores([]);
    setPrices([]);
    setStoreError("");
    setComparison(null);
    if (!locality) {
      setStoreLoading(false);
      return () => controller.abort();
    }
    setStoreLoading(true);
    (async () => {
      try {
        const branches = await api<Store[]>(
          `/api/v1/stores?locality_id=${locality.id}&category_code=${category}&limit=500`,
          { signal: controller.signal },
        );
        if (alive) setStores(branches);
        try {
          const observations = await api<Price[]>(
            `/api/v1/prices/current?locality_id=${locality.id}&limit=500`,
            { signal: controller.signal },
          );
          if (alive) setPrices(observations);
        } catch {
          if (alive) setStoreError("Цените не се заредиха. Опитайте отново.");
        }
      } catch {
        if (alive)
          setStoreError("Магазините не се заредиха. Проверете връзката.");
      } finally {
        if (alive) setStoreLoading(false);
      }
    })();
    return () => {
      alive = false;
      controller.abort();
    };
  }, [locality?.id, category, refresh]);
  const change = (p: Product, delta: number) => {
    if (
      delta > 0 &&
      basket.length >= MAX_BASKET_ITEMS &&
      !basket.some((i) => i.product.id === p.id)
    ) {
      setNotice(
        `Списъкът може да съдържа най-много ${MAX_BASKET_ITEMS} различни продукта.`,
      );
      return;
    }
    setBasket((b) => changeQuantity(b, p, delta));
    setComparison(null);
  };
  const chooseLocality = (l: Locality) => {
    setStores([]);
    setPrices([]);
    setStoreError("");
    setLocality(l);
    setComparison(null);
  };
  const switchCategory = (c: Category) => {
    if (c !== category) {
      setProducts([]);
      setStores([]);
      setPrices([]);
    }
    setCategory(c);
    setScreen("catalog");
    setNotice("");
  };
  async function compare() {
    if (!locality) {
      setNotice("Изберете населено място за сравнение.");
      return;
    }
    if (basket.some((i) => i.product.is_demo)) {
      setNotice(
        "Примерните продукти нямат проверени цени. Премахнете ги, за да сравните реални продукти.",
      );
      return;
    }
    if (!basket.length) return;
    const key = JSON.stringify({ basket, locality: locality.id });
    setComparing(true);
    setNotice("");
    try {
      const result = await api<Comparison>("/api/v1/baskets/compare", {
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
      // Associate the response with the exact basket and locality requested.
      setComparison({ key, data: result });
    } catch {
      setNotice("Сравнението не е достъпно. Опитайте отново.");
    } finally {
      setComparing(false);
    }
  }
  async function findBarcode() {
    if (!/^\d{8,14}$/.test(barcode)) {
      setNotice("Въведете баркод с 8–14 цифри.");
      return;
    }
    setLookup(true);
    setNotice("");
    try {
      const p = await api<Product>(`/api/v1/products/barcode/${barcode}`);
      Alert.alert(p.name, "Добавяне в списъка за пазаруване?", [
        { text: "Отказ", style: "cancel" },
        { text: "Добави", onPress: () => change(p, 1) },
      ]);
    } catch (e) {
      setNotice(
        String(e).includes("404")
          ? "Непознат баркод. Заявките за идентификация ще изискват вход в следваща версия."
          : "Търсенето не е достъпно. Опитайте отново.",
      );
    } finally {
      setLookup(false);
    }
  }
  const visibleProducts = products.filter(
    (p) => !selected.length || selected.includes(p.id),
  );
  function productCard(p: Product) {
    const price = lowestPrice(p, prices, stores);
    return (
      <View key={p.id} style={s.card}>
        {p.image_url ? (
          <Image
            accessibilityLabel={productName(p)}
            source={{ uri: p.image_url.replace(/^http:/, "https:") }}
            style={s.photo}
            resizeMode="contain"
          />
        ) : (
          <Ionicons
            name="cube-outline"
            size={40}
            color="#63816a"
            style={{ width: 62 }}
          />
        )}
        <View style={{ flex: 1, gap: 5 }}>
          {p.is_demo && <Text style={s.badge}>ДЕМО СНИМКА</Text>}
          <Text style={s.productName}>{productName(p)}</Text>
          <Text style={s.meta}>
            {p.package ||
              [p.package_quantity, p.package_unit].filter(Boolean).join(" ")}
          </Text>
          <Text style={price === null ? s.meta : s.price}>
            {price === null
              ? storeError
                ? "Цените не са заредени"
                : "Няма потвърдена цена"
              : `от ${price.toFixed(2)} €`}
          </Text>
        </View>
        <Pressable
          disabled={!restored}
          accessibilityRole="button"
          accessibilityLabel={`Добави ${productName(p)}`}
          onPress={() => change(p, 1)}
          style={s.add}
        >
          <Ionicons name="cart-outline" size={22} color="#f48100" />
        </Pressable>
      </View>
    );
  }
  const title =
    screen === "basket"
      ? "Моят списък"
      : screen === "scan"
        ? "Сканиране"
        : screen === "checks"
          ? "Преглед 02"
          : category === "groceries" && view === "products"
            ? "Продукти"
            : "Магазини";
  return (
    <SafeAreaView style={s.page} edges={["top", "bottom"]}>
      <StatusBar style="light" />
      <View style={s.header}>
        <Image
          source={require("./assets/piggy-bank-logo.png")}
          style={s.logo}
          resizeMode="cover"
        />
        <View style={{ flex: 1 }}>
          <Text style={s.brand}>Спестовник</Text>
          <Text style={s.tagline}>Сравнявай цените. Пести повече!</Text>
        </View>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Моят списък"
          onPress={() => {
            setScreen("basket");
            setNotice("");
          }}
          style={s.topBasket}
        >
          <Ionicons name="cart-outline" color="#fff" size={25} />
          <Text style={s.count}>
            {basket.reduce((sum, i) => sum + i.quantity, 0)}
          </Text>
        </Pressable>
      </View>
      <View style={s.tabs}>
        {tabs.map((t) => (
          <Pressable
            accessibilityRole="tab"
            accessibilityLabel={t.name}
            accessibilityState={{ selected: category === t.id }}
            key={t.id}
            onPress={() => switchCategory(t.id)}
            style={[s.tab, category === t.id && s.activeTab]}
          >
            <Ionicons
              name={t.icon}
              size={24}
              color={category === t.id ? "#fff" : "#19562a"}
            />
            <Text
              style={{
                fontSize: 13,
                color: category === t.id ? "#fff" : "#19562a",
              }}
            >
              {t.name}
            </Text>
          </Pressable>
        ))}
      </View>
      <ScrollView
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={s.body}
      >
        {comparing ? (
          <Text style={s.meta}>
            Сравняване за {locality?.name_bg || locality?.name}…
          </Text>
        ) : (
          <LocationPicker
            apiBaseUrl={API_BASE_URL}
            selected={locality}
            onSelect={chooseLocality}
          />
        )}
        <View style={s.headingRow}>
          <Text style={s.heading}>{title}</Text>
          <Button
            label="Обнови"
            onPress={() => {
              setRefresh((r) => r + 1);
              setNotice("");
            }}
          />
        </View>
        {!!notice && (
          <Text accessibilityLiveRegion="polite" style={s.notice}>
            {notice}
          </Text>
        )}
        {screen === "catalog" && (
          <>
            {category === "groceries" && (
              <View style={s.row}>
                <Button
                  label="Продукти"
                  primary={view === "products"}
                  onPress={() => setView("products")}
                />
                <Button
                  label={`Магазини (${stores.length})`}
                  primary={view === "stores"}
                  onPress={() => setView("stores")}
                />
              </View>
            )}
            {category === "fuel" && (
              <>
                <View style={s.row}>
                  {["Бензин 95", "Дизел", "LPG"].map((f) => (
                    <Button
                      key={f}
                      label={f}
                      primary={fuel === f}
                      onPress={() => setFuel(f)}
                    />
                  ))}
                </View>
                <Text style={s.notice}>
                  Цени за {fuel} още не са налични. Fuelo изисква API достъп.
                  Обектите по-долу са от регистъра.
                </Text>
              </>
            )}
            {category === "groceries" && view === "products" ? (
              <>
                <TextInput
                  accessibilityLabel="Търси продукт"
                  placeholder="Търси продукт…"
                  style={s.input}
                  value={query}
                  onFocus={() => {
                    setSearchOpen(true);
                    setDraft(selected);
                  }}
                  onChangeText={(q) => {
                    setQuery(q);
                    setSearchOpen(true);
                  }}
                />
                {searchOpen && (
                  <View style={s.panel}>
                    {products
                      .filter((p) => matchesProduct(p, query))
                      .map((p) => (
                        <Pressable
                          accessibilityRole="checkbox"
                          accessibilityState={{ checked: draft.includes(p.id) }}
                          key={p.id}
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
                            {productName(p)}
                            {p.is_demo ? " · демо" : ""}
                          </Text>
                        </Pressable>
                      ))}
                    <View style={s.row}>
                      <Button
                        label="Изчисти"
                        onPress={() => {
                          setDraft([]);
                          setSelected([]);
                          setQuery("");
                        }}
                      />
                      <Button
                        label={`Приложи (${draft.length})`}
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
                  <Text style={s.meta}>Покажи примерните снимки</Text>
                </Pressable>
                {demo && (
                  <Text style={s.notice}>
                    Примерните снимки са от референцията. Те не са реални оферти
                    и нямат цени.
                  </Text>
                )}
                {loading ? (
                  <ActivityIndicator color="#19562a" />
                ) : error ? (
                  <View>
                    <Text style={s.notice}>{error}</Text>
                    <Button
                      label="Опитайте отново"
                      onPress={() => setRefresh((r) => r + 1)}
                    />
                  </View>
                ) : null}
                {visibleProducts.map(productCard)}
                {!loading && !error && !visibleProducts.length && (
                  <Text style={s.meta}>Няма продукти за този избор.</Text>
                )}
              </>
            ) : (
              <>
                {!locality ? (
                  <Text style={s.notice}>
                    Изберете населено място, за да видите регистрираните обекти.
                  </Text>
                ) : storeLoading ? (
                  <ActivityIndicator color="#19562a" />
                ) : null}
                {!!storeError && (
                  <View>
                    <Text style={s.notice}>{storeError}</Text>
                    <Button
                      label="Опитайте отново"
                      onPress={() => setRefresh((r) => r + 1)}
                    />
                  </View>
                )}
                {stores.map((store) => (
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
                      <Text style={s.meta}>Няма показана потвърдена цена</Text>
                    </View>
                  </View>
                ))}
                {locality && !storeLoading && !storeError && !stores.length && (
                  <Text style={s.notice}>
                    Все още няма регистрирани обекти за тази категория и
                    населено място.
                  </Text>
                )}
              </>
            )}
          </>
        )}
        {screen === "basket" && (
          <>
            {!basket.length && (
              <Text style={s.notice}>
                Списъкът е празен. Добавете продукти от „Храни“.
              </Text>
            )}
            {basket.map(({ product: p, quantity }) => (
              <View key={p.id} style={s.panel}>
                <Text style={s.productName}>{productName(p)}</Text>
                {p.is_demo && (
                  <Text style={s.meta}>Примерен продукт · без цена</Text>
                )}
                <View style={s.row}>
                  <Button
                    label="−"
                    disabled={comparing}
                    onPress={() => change(p, -1)}
                  />
                  <Text
                    accessibilityLabel={`Количество ${quantity}`}
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
                    label="Премахни"
                    disabled={comparing}
                    onPress={() =>
                      setBasket((b) => b.filter((i) => i.product.id !== p.id))
                    }
                  />
                </View>
              </View>
            ))}
            <Button
              label={comparing ? "Сравняване…" : "Сравни цени"}
              primary
              disabled={comparing || !basket.length}
              onPress={compare}
            />
            {comparison && (
              <View style={s.panel}>
                <Text style={s.productName}>
                  {comparison.cheapest
                    ? "Сравнение по обекти"
                    : "Няма пълна оферта за целия списък"}
                </Text>
                {comparison.quotes.map((q, i) => (
                  <Text key={i} style={s.meta}>
                    {stores.find((s) => s.id === q.branch_id)?.retailer_name ||
                      q.retailer_code}
                    :{" "}
                    {q.complete && q.total_eur !== null
                      ? `${Number(q.total_eur).toFixed(2)} €`
                      : "липсват цени"}
                  </Text>
                ))}
                <Text style={s.meta}>
                  Физически обекти. Доставката и пътуването не са включени.
                </Text>
              </View>
            )}
          </>
        )}
        {screen === "scan" && (
          <>
            <Text style={s.notice}>
              Камерата и качването на касови бележки не са свързани в преглед
              01.
            </Text>
            <Text style={s.productName}>Търсене по баркод</Text>
            <TextInput
              accessibilityLabel="Баркод"
              value={barcode}
              onChangeText={setBarcode}
              keyboardType="number-pad"
              maxLength={14}
              style={s.input}
              placeholder="8–14 цифри"
            />
            <Button
              primary
              label={lookup ? "Търсене…" : "Намери продукт"}
              disabled={lookup}
              onPress={findBarcode}
            />
          </>
        )}
        {screen === "checks" && (
          <View style={s.panel}>
            <Text style={s.productName}>Работи в тази версия</Text>
            <Text style={s.meta}>
              Четири категории · търсене по населено място или пощенски код ·
              реални обекти от API · примерни снимки от API · запазен списък ·
              търсене по баркод.
            </Text>
            <Text style={s.productName}>Очаква следваща версия</Text>
            <Text style={s.meta}>
              Вход, камера и касови бележки. Данните за цени зависят от
              покритието на бекенда. Примерните продукти не се сравняват.
            </Text>
            <Text style={s.meta}>
              Android преглед 02 · v0.1.2{"\n"}
              {API_BASE_URL}
            </Text>
          </View>
        )}
      </ScrollView>
      <View style={s.footer}>
        {(
          [
            { id: "scan", label: "Сканирай", icon: "scan-outline" },
            { id: "basket", label: "Моят списък", icon: "list-outline" },
            {
              id: "checks",
              label: "Проверка",
              icon: "checkmark-circle-outline",
            },
          ] as const
        ).map((b) => (
          <Pressable
            accessibilityRole="button"
            key={b.id}
            accessibilityLabel={b.label}
            style={s.footerItem}
            onPress={() => {
              setScreen(b.id);
              setNotice("");
            }}
          >
            <Ionicons name={b.icon} size={21} color="#19562a" />
            <Text style={s.footerText}>{b.label}</Text>
          </Pressable>
        ))}
      </View>
    </SafeAreaView>
  );
}
const s = StyleSheet.create({
  page: { flex: 1, backgroundColor: "#195b27" },
  header: {
    backgroundColor: "#195b27",
    padding: 16,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  logo: { width: 38, height: 58, borderRadius: 7 },
  brand: { fontSize: 25, fontWeight: "800", color: "#fff" },
  tagline: { fontSize: 11, color: "#e0f1da", marginTop: 4 },
  topBasket: { padding: 10, minWidth: 44, minHeight: 44 },
  count: {
    position: "absolute",
    right: 0,
    top: 0,
    backgroundColor: "#ff8500",
    color: "#fff",
    fontSize: 11,
    borderRadius: 12,
    minWidth: 20,
    textAlign: "center",
    padding: 3,
  },
  tabs: { flexDirection: "row", backgroundColor: "#eaf1dd" },
  tab: { flex: 1, paddingVertical: 15, alignItems: "center", gap: 5 },
  activeTab: { backgroundColor: "#ff8500" },
  body: {
    padding: 14,
    gap: 12,
    backgroundColor: "#fff",
    flexGrow: 1,
    paddingBottom: 24,
  },
  headingRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 8,
  },
  heading: { fontSize: 20, fontWeight: "700", color: "#243d2b", flex: 1 },
  button: {
    paddingHorizontal: 13,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: "#edf3e5",
    minHeight: 44,
    justifyContent: "center",
  },
  primary: { backgroundColor: "#ff8500" },
  row: { flexDirection: "row", gap: 8, alignItems: "center", flexWrap: "wrap" },
  input: {
    padding: 14,
    borderWidth: 1,
    borderColor: "#d9e2d3",
    borderRadius: 14,
    color: "#263e2d",
    fontSize: 16,
  },
  panel: {
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: "#dce4d6",
    gap: 12,
    backgroundColor: "#fff",
  },
  option: {
    flexDirection: "row",
    alignItems: "center",
    gap: 9,
    minHeight: 44,
    paddingVertical: 8,
  },
  notice: {
    padding: 12,
    borderRadius: 10,
    backgroundColor: "#fff6e7",
    color: "#855511",
    fontSize: 13,
    lineHeight: 19,
  },
  meta: { fontSize: 12, color: "#617363", lineHeight: 18 },
  card: {
    padding: 14,
    borderWidth: 1,
    borderColor: "#dfe5d8",
    borderRadius: 16,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    backgroundColor: "#fff",
    minHeight: 125,
  },
  photo: { width: 60, height: 90 },
  badge: {
    fontSize: 11,
    fontWeight: "700",
    color: "#526e4d",
    backgroundColor: "#eff4e8",
    alignSelf: "flex-start",
    paddingHorizontal: 5,
    paddingVertical: 3,
    borderRadius: 4,
  },
  productName: { fontSize: 15, fontWeight: "700", color: "#283f2e" },
  price: { fontSize: 18, fontWeight: "700", color: "#1a5228" },
  add: {
    borderWidth: 1,
    borderColor: "#ff8500",
    borderRadius: 24,
    width: 44,
    height: 44,
    justifyContent: "center",
    alignItems: "center",
  },
  store: {
    flexDirection: "row",
    gap: 12,
    padding: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#e7ebdf",
    alignItems: "center",
  },
  storeMark: { padding: 8, backgroundColor: "#edf3e5", borderRadius: 10 },
  footer: {
    flexDirection: "row",
    backgroundColor: "#f3f6ed",
    borderTopWidth: 1,
    borderTopColor: "#dfe5d8",
  },
  footerItem: {
    flex: 1,
    paddingVertical: 13,
    alignItems: "center",
    gap: 5,
    minHeight: 58,
  },
  footerText: { fontSize: 12, color: "#275d32" },
});
