import { ImageSourcePropType } from "react-native";
import { products } from "../../../data/demo-thumbnails/catalog.json";
import { Product } from "./model";

const thumbnails: Record<string, ImageSourcePropType> = {
  milk: require("../../assets/thumbnails/milk.webp"),
  oil: require("../../assets/thumbnails/oil.webp"),
  sugar: require("../../assets/thumbnails/sugar.webp"),
  laptop: require("../../assets/thumbnails/laptop.webp"),
  washer: require("../../assets/thumbnails/washer.webp"),
  tv: require("../../assets/thumbnails/tv.webp"),
  kettle: require("../../assets/thumbnails/kettle.webp"),
  headphones: require("../../assets/thumbnails/headphones.webp"),
  smartphone: require("../../assets/thumbnails/smartphone.webp"),
};

const creditsById = new Map(products.filter(row => row.source_url)
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
