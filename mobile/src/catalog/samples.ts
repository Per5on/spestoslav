import { ImageSourcePropType } from "react-native";
import { products } from "../../../data/demo-thumbnails/catalog.json";
import { Product } from "./model";

const thumbnails: Record<string, ImageSourcePropType> = {
  milk: require("../../assets/thumbnails/milk.webp"),
  oil: require("../../assets/thumbnails/oil.webp"),
  sugar: require("../../assets/thumbnails/sugar.webp"),
};

const creditsById = new Map(products.filter(row => row.category_code === "groceries" && row.source_url)
  .map(row => ["demo-" + row.code, row] as const));

export function sampleCredit(id: string) {
  return creditsById.get(id);
}

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

const technologyImages = {
  laptop: require("../../assets/technology/laptop.webp"),
  washer: require("../../assets/technology/washer.webp"),
  tv: require("../../assets/technology/tv.webp"),
  kettle: require("../../assets/technology/kettle.webp"),
  headphones: require("../../assets/technology/headphones.webp"),
  smartphone: require("../../assets/technology/smartphone.webp"),
  "smart-home": require("../../assets/technology/smart-home.webp"),
  technology: require("../../assets/technology/technology.webp"),
} satisfies Record<string, ImageSourcePropType>;

const technologyGroups: Record<string, keyof typeof technologyImages> = {
  mobile: "smartphone",
  "major-appliances": "washer",
  "small-appliances": "kettle",
  "tv-computing": "tv",
  "smart-home-mobility": "smart-home",
};

export function technologyThumbnail(id: string, group?: string | null): ImageSourcePropType {
  const sample = id.startsWith("demo-") ? id.slice(5) : "";
  return Object.hasOwn(technologyImages, sample)
    ? technologyImages[sample as keyof typeof technologyImages]
    : technologyImages[technologyGroups[group ?? ""] ?? "technology"];
}


const groceryImages: Record<string, ImageSourcePropType> = {
  "bakery-breakfast": require("../../assets/grocery-symbols/bakery-breakfast.webp"),
  "dairy-eggs": require("../../assets/grocery-symbols/dairy-eggs.webp"),
  "meat-fish": require("../../assets/grocery-symbols/meat-fish.webp"),
  pantry: require("../../assets/grocery-symbols/pantry.webp"),
  produce: require("../../assets/grocery-symbols/produce.webp"),
  "spices-drinks": require("../../assets/grocery-symbols/spices-drinks.webp"),
};
const defaultGroceryImage = require("../../assets/grocery-symbols/groceries.webp");

export function groceryThumbnail(group?: string | null): ImageSourcePropType {
  return group && Object.hasOwn(groceryImages, group) ? groceryImages[group] : defaultGroceryImage;
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
const galaxyCredit = {
  author: "Captainmorlypogi1959",
  license: "CC BY-SA 4.0 · cropped/resized WebP",
  source_url: "https://commons.wikimedia.org/wiki/File:Samsung_Galaxy_A17_5G_2026.jpg",
};

export function referencePhoto(product: Product): { source: ImageSourcePropType; credit?: typeof galaxyCredit } | undefined {
  const code = product.source_product_code ?? "";
  if (product.category_code === "technology" && code === "43832") {
    return { source: galaxyA17, credit: galaxyCredit };
  }
  if (product.category_code === "groceries" && product.group_code === "produce" && Object.hasOwn(producePhotos, code)) {
    return { source: producePhotos[code] };
  }
}
