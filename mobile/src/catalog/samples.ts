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
