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

const banana = require("../../assets/produce/banana.webp");
const carrot = require("../../assets/produce/carrot.webp");
const lemon = require("../../assets/produce/lemon.webp");
const bread = require("../../assets/produce/bread.webp");
const meat = require("../../assets/produce/meat.webp");
const pepper = require("../../assets/produce/pepper.webp");
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


const technologyExamples: Record<string, string> = {
  mobile: "smartphone",
  "major-appliances": "washer",
  "small-appliances": "kettle",
  "tv-computing": "laptop",
  "smart-home-mobility": "tv",
};

const groceryExamples: Record<string, ImageSourcePropType> = {
  "dairy-eggs": thumbnails.milk,
  "bakery-breakfast": bread,
  "meat-fish": meat,
  pantry: thumbnails.sugar,
  produce: banana,
  "spices-drinks": pepper,
};

export function groupPhoto(product: Product): { source: ImageSourcePropType; credit?: typeof galaxyCredit } {
  const group = product.group_code ?? "";
  if (product.category_code === "technology") {
    const example = technologyExamples[group] ?? "laptop";
    const credit = sampleCredit("demo-" + example);
    return { source: thumbnails[example], credit: credit?.source_url
      ? { author: credit.author, license: credit.license + " · resized WebP", source_url: credit.source_url }
      : undefined };
  }
  return {
    source: groceryExamples[group] ?? thumbnails.oil,
    credit: group === "spices-drinks" ? {
      author: "Eliška Jindříšková", license: "CC BY-SA 4.0 · resized WebP",
      source_url: "https://commons.wikimedia.org/wiki/File:Ground_black_pepper.jpg",
    } : undefined,
  };
}
