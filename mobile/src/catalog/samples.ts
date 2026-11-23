import { ImageSourcePropType } from "react-native";
import { products } from "../../../data/demo-thumbnails/catalog.json";
import { Product } from "./model";

const thumbnails: Record<string, ImageSourcePropType> = {
  milk: require("../../assets/beta-illustrations/milk.webp"),
  oil: require("../../assets/beta-illustrations/oil.webp"),
  sugar: require("../../assets/beta-illustrations/sugar.webp"),
  laptop: require("../../assets/beta-illustrations/laptop.webp"),
  washer: require("../../assets/beta-illustrations/washer.webp"),
  tv: require("../../assets/beta-illustrations/tv.webp"),
  kettle: require("../../assets/technology/kettle.webp"),
  headphones: require("../../assets/technology/headphones.webp"),
  smartphone: require("../../assets/technology/smartphone.webp"),
};

export const sampleProducts: Product[] = products.map(row => ({
  id: "demo-" + row.code,
  name: row.name,
  category_code: row.category_code,
  package: row.package,
  is_demo: true,
}));

export function sampleThumbnail(id: string): ImageSourcePropType | undefined {
  return id.startsWith("demo-") ? thumbnails[id.slice(5)] : undefined;
}

const banana = require("../../assets/produce/banana.webp");
const carrot = require("../../assets/produce/carrot.webp");
const lemon = require("../../assets/produce/lemon.webp");
const galaxyA17 = require("../../assets/technology/galaxy-a17.webp");
const producePhotos: Record<string, ImageSourcePropType> = {
  "81590": banana, "88590": banana,
  "81078": carrot, "89078": carrot,
  "81581": lemon, "88581": lemon,
};
export function referencePhoto(product: Product): ImageSourcePropType | undefined {
  const code = product.source_product_code ?? "";
  if (product.category_code === "technology" && code === "43832") {
    return galaxyA17;
  }
  if (product.category_code === "groceries" && product.group_code === "produce" && Object.hasOwn(producePhotos, code)) {
    return producePhotos[code];
  }
}

const technologySymbols: Record<string, ImageSourcePropType> = {
  mobile: thumbnails.smartphone,
  "major-appliances": thumbnails.washer,
  "small-appliances": thumbnails.kettle,
  "tv-computing": thumbnails.laptop,
  "smart-home-mobility": require("../../assets/technology/smart-home.webp"),
};
const grocerySymbols: Record<string, ImageSourcePropType> = {
  "dairy-eggs": require("../../assets/grocery-symbols/dairy-eggs.webp"),
  "bakery-breakfast": require("../../assets/grocery-symbols/bakery-breakfast.webp"),
  "meat-fish": require("../../assets/grocery-symbols/meat-fish.webp"),
  pantry: require("../../assets/grocery-symbols/pantry.webp"),
  produce: require("../../assets/grocery-symbols/produce.webp"),
  "spices-drinks": require("../../assets/grocery-symbols/spices-drinks.webp"),
};
const tomato = require("../../assets/grocery-symbols/tomato.webp");
const groceries = require("../../assets/grocery-symbols/groceries.webp");
const technology = require("../../assets/technology/technology.webp");

export function productSymbol(product: Product): ImageSourcePropType {
  const group = product.group_code ?? "";
  if (product.category_code === "technology") return technologySymbols[group] ?? technology;
  if (group === "produce" && /(?:^|\s)домат(?:и)?(?:\s|$)/iu.test(product.name)) return tomato;
  return grocerySymbols[group] ?? groceries;
}
