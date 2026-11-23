import type { ImageSourcePropType } from "react-native";
import { products } from "../../../data/demo-thumbnails/catalog.json";
import type { Product } from "./model";

const art = {
  groceries: require("../../../data/catalogue-thumbnails/groceries.webp"),
  "dairy-eggs": require("../../../data/catalogue-thumbnails/dairy-eggs.webp"),
  "bakery-breakfast": require("../../../data/catalogue-thumbnails/bakery-breakfast.webp"),
  produce: require("../../../data/catalogue-thumbnails/produce.webp"),
  "meat-fish": require("../../../data/catalogue-thumbnails/meat-fish.webp"),
  pantry: require("../../../data/catalogue-thumbnails/pantry.webp"),
  "spices-drinks": require("../../../data/catalogue-thumbnails/spices-drinks.webp"),
  technology: require("../../../data/catalogue-thumbnails/technology.webp"),
  mobile: require("../../../data/catalogue-thumbnails/mobile.webp"),
  "major-appliances": require("../../../data/catalogue-thumbnails/major-appliances.webp"),
  "small-appliances": require("../../../data/catalogue-thumbnails/small-appliances.webp"),
  "tv-computing": require("../../../data/catalogue-thumbnails/tv-computing.webp"),
  "smart-home-mobility": require("../../../data/catalogue-thumbnails/smart-home-mobility.webp"),
  tomato: require("../../../data/catalogue-thumbnails/tomato.webp"),
  banana: require("../../../data/catalogue-thumbnails/banana.webp"),
  carrot: require("../../../data/catalogue-thumbnails/carrot.webp"),
  headphones: require("../../../data/catalogue-thumbnails/headphones.webp"),
  "fridge": require("../../../data/catalogue-thumbnails/fridge.webp"),
  "air-conditioner": require("../../../data/catalogue-thumbnails/air-conditioner.webp"),
  "coffee-maker": require("../../../data/catalogue-thumbnails/coffee-maker.webp"),
  "microwave": require("../../../data/catalogue-thumbnails/microwave.webp"),
  "blender": require("../../../data/catalogue-thumbnails/blender.webp"),
  "toaster": require("../../../data/catalogue-thumbnails/toaster.webp"),
  "hair-dryer": require("../../../data/catalogue-thumbnails/hair-dryer.webp"),
  "monitor": require("../../../data/catalogue-thumbnails/monitor.webp"),
  "printer": require("../../../data/catalogue-thumbnails/printer.webp"),
  "router": require("../../../data/catalogue-thumbnails/router.webp"),
  "desktop": require("../../../data/catalogue-thumbnails/desktop.webp"),
  "watch": require("../../../data/catalogue-thumbnails/watch.webp"),
  "cable": require("../../../data/catalogue-thumbnails/cable.webp"),
  "power-bank": require("../../../data/catalogue-thumbnails/power-bank.webp"),
  "smart-plug": require("../../../data/catalogue-thumbnails/smart-plug.webp"),
  "kettle": require("../../../data/catalogue-thumbnails/kettle.webp"),
} satisfies Record<string, ImageSourcePropType>;
type ArtCode = keyof typeof art;

const samples: Record<string, ImageSourcePropType> = {
  milk: require("../../assets/beta-illustrations/milk.webp"),
  oil: require("../../assets/beta-illustrations/oil.webp"),
  sugar: require("../../assets/beta-illustrations/sugar.webp"),
  laptop: art.technology,
  washer: art["major-appliances"],
  tv: art["tv-computing"],
  kettle: art.kettle,
  headphones: art.headphones,
  smartphone: art.mobile,
};

export const sampleProducts: Product[] = products.map(row => ({
  id: "demo-" + row.code,
  name: row.name,
  category_code: row.category_code,
  package: row.package,
  is_demo: true,
}));

const produceArt: ReadonlyArray<readonly [RegExp, ArtCode]> = [
  [/^(?:био\s+)?банани(?:\s|$)/iu, "banana"],
  [/^(?:био\s+)?моркови(?:\s|$)/iu, "carrot"],
  [/^(?:био\s+)?(?:(?:чери|розови)\s+)?домат(?:и)?(?:\s|$)/iu, "tomato"],
];

const technologyArt: ReadonlyArray<readonly [RegExp, ArtCode]> = [
  [/^(?:електрическа\s+|ел\.\s*)?кана(?=\s|$)/iu, "kettle"],
  [/^кафемашина(?=\s|$)/iu, "coffee-maker"],
  [/^микровълнова(?=\s|$)/iu, "microwave"],
  [/^блендер(?=\s|$)/iu, "blender"],
  [/^тостер(?=\s|$)/iu, "toaster"],
  [/^сешоар(?=\s|$)/iu, "hair-dryer"],
  [/^хладилник(?=\s|$)/iu, "fridge"],
  [/^климатик(?=\s|$)/iu, "air-conditioner"],
  [/^(?:пералня|сушилня)(?=\s|$)/iu, "major-appliances"],
  [/^телевизор(?=\s|$)/iu, "tv-computing"],
  [/^монитор(?=\s|$)/iu, "monitor"],
  [/^лаптоп(?=\s|$)/iu, "technology"],
  [/^настолен компютър(?=\s|$)/iu, "desktop"],
  [/^(?:(?:мастиленоструен|лазерен)\s+)?принтер(?=\s|$)/iu, "printer"],
  [/^(?:рутер|\S+\s+\S+\s+(?:wi-fi\s+)?router)(?=\s|$)/iu, "router"],
  [/^(?:смарт\s+контакт|smart\s+контакт)(?=\s|$)/iu, "smart-plug"],
  [/^смарт\s*часовник(?=\s|$)/iu, "watch"],
  [/^външна батерия(?=\s|$)/iu, "power-bank"],
  [/^кабел(?=\s|$)/iu, "cable"],
  [/^слушалки(?=\s|$)/iu, "headphones"],
  [/^(?:смартфон|мобилен телефон)(?=\s|$)/iu, "mobile"],
];

const galaxyA17 = require("../../assets/technology/galaxy-a17.webp");
const lemon = require("../../assets/produce/lemon.webp");

export function productArtwork(product: Product): { code?: ArtCode; source: ImageSourcePropType; symbolic: boolean } {
  const sample = product.is_demo ? samples[product.id.slice(5)] : undefined;
  const tech = product.category_code === "technology";
  if (sample) return { source: sample, symbolic: tech };

  const group = product.group_code ?? "";
  const name = product.name.trim();
  if (tech && product.source_product_code === "43832" && /\bGALAXY A17\b/i.test(name)) {
    return { source: galaxyA17, symbolic: false };
  }
  if (!tech && group === "produce") {
    if (/^(?:био\s+)?лимони(?:\s|$)/iu.test(name)) return { source: lemon, symbolic: false };
    const match = produceArt.find(([pattern]) => pattern.test(name));
    if (match) {
      const code = match[1];
      return { code, source: art[code], symbolic: code === "tomato" };
    }
  }
  const matchedType = tech ? technologyArt.find(([pattern]) => pattern.test(name))?.[1] : undefined;
  const code = matchedType ?? (Object.hasOwn(art, group) ? group as ArtCode : tech ? "technology" : "groceries");
  return { code, source: art[code], symbolic: true };
}
