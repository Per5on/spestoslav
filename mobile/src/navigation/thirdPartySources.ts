import { products } from "../../../data/demo-thumbnails/catalog.json";

export type Credit = {
  name: string;
  url: string;
  author?: string;
  license?: string;
  licenseUrl?: string;
  resized?: boolean;
};

const repo = "https://github.com/Per5on/spestoslav/blob/Beta_10.8/";
const commons = "https://commons.wikimedia.org/wiki/File:";
const cc = "https://creativecommons.org/licenses/";

export const dataCredits: Credit[] = [
  { name: "GeoNames", url: "https://www.geonames.org/export/zip/", license: "CC BY 3.0", licenseUrl: cc + "by/3.0/" },
  { name: "НСИ · ЕКАТТЕ", url: "https://www.nsi.bg/nrnm/ekatte/archive" },
  { name: "КЗП · Колко струва", url: "https://kolkostruva.bg/opendata" },
  { name: "Burlex", url: "https://burlex.bg/kolkostruva/" },
  { name: "Techmart", url: "https://techmart.bg/" },
  { name: "Technopolis", url: "https://www.technopolis.bg/" },
  { name: "KARAI Fuel Index", url: "https://karai.bg/fuel-prices/indeks", license: "CC BY 4.0", licenseUrl: cc + "by/4.0/" },
];

export const storeCredits: Credit[] = [
  { name: "ProMarket", url: "https://promarket.bg/shops/" },
  { name: "BILLA", url: "https://www.billa.bg/magazini" },
  { name: "Burlex", url: "https://burlex.bg/магазини-бурлекс/" },
  { name: "Fantastico", url: "https://www.fantastico.bg/shops" },
  { name: "HIT Max", url: "https://www.hit-max.bg/elements/pages/our-stores/" },
  { name: "Kaufland", url: "https://www.kaufland.bg/moyat-kaufland/uslugi/filiali/" },
  { name: "Klasiko", url: "https://www.klasiko.bg/bg/info/i8/За-нас.html" },
  { name: "Lidl", url: "https://www.lidl.bg/s/bg-BG/magazini/" },
  { name: "METRO", url: "https://www.metro.bg/magazini" },
  { name: "T MARKET", url: "https://tmarket.bg/page/nashite-magazini" },
  { name: "Моят магазин", url: "https://www.moiatmagazin.bg/magazini" },
  { name: "Ardes", url: "https://ardes.bg/magazini-i-servizi" },
  { name: "JAR Computers", url: "https://www.jarcomputers.com/stores/" },
  { name: "Techmart", url: "https://techmart.bg/store/store/list" },
  { name: "Technomarket", url: "https://www.technomarket.bg/magazini" },
  { name: "Technopolis", url: "https://www.technopolis.bg/bg/stores" },
  { name: "Вали", url: "https://www.vali.bg/kontakti" },
  { name: "Зора", url: "https://zora.bg/page/magazini-zora" },
  { name: "EKO", url: "https://www.eko.bg/self-service-terminal-instructions/karta-na-obektite/" },
  { name: "Fuelo · EKO, LUKOIL, OMV, Rompetrol, Shell, Petrol", url: "https://bg.fuelo.net/" },
  { name: "store_branches_seed.csv", url: repo + "data/store_branches_seed.csv" },
];

export const photoCredits: Credit[] = [
  { name: "Ionicons", url: "https://ionic.io/ionicons", author: "Ionic",
    license: "MIT", licenseUrl: repo + "data/symbolic-thumbnails/LICENSE" },
  { name: "Banana", url: commons + "Banana-Single.jpg", author: "Evan-Amos", license: "Public domain", resized: true },
  { name: "Carrot", url: commons + "Vegetable-Carrot-Bundle-wStalks.jpg", author: "Evan-Amos", license: "Public domain", resized: true },
  { name: "Lemon", url: commons + "Whole-Lemon.jpg", author: "Evan-Amos", license: "Public domain", resized: true },
  { name: "Bread", url: commons + "Slices_of_bread.jpg", author: "USDA Agricultural Research Service", license: "Public domain", resized: true },
  { name: "Meat", url: commons + "FoodMeat-white.png", author: "U.S. National Institutes of Health", license: "Public domain", resized: true },
  { name: "Ground black pepper", url: commons + "Ground_black_pepper.jpg", author: "Eliška Jindříšková",
    license: "CC BY-SA 4.0", licenseUrl: cc + "by-sa/4.0/", resized: true },
  { name: "Samsung Galaxy A17 5G", url: commons + "Samsung_Galaxy_A17_5G_2026.jpg", author: "Captainmorlypogi1959",
    license: "CC BY-SA 4.0", licenseUrl: cc + "by-sa/4.0/", resized: true },
  ...products.filter(row => row.source_url && "file_title" in row).map(row => ({
    name: row.file_title?.replace(/^File:|\.[^.]+$/g, "") ?? row.name,
    url: row.source_url,
    author: row.author,
    license: row.license,
    licenseUrl: row.license_url,
  })),
];

export const softwareCredits: Credit[] = [
  { name: "Expo", url: "https://expo.dev/" },
  { name: "React", url: "https://react.dev/" },
  { name: "React Native", url: "https://reactnative.dev/" },
  { name: "React Native Web", url: "https://necolas.github.io/react-native-web/" },
  { name: "React Native Async Storage", url: "https://react-native-async-storage.github.io/async-storage/" },
  { name: "React Native Safe Area Context", url: "https://appandflow.github.io/react-native-safe-area-context/" },
  { name: "ZXing", url: "https://github.com/zxing-js/browser" },
  { name: "Google ML Kit", url: "https://developers.google.com/ml-kit/vision/barcode-scanning" },
  { name: "Tesseract OCR", url: "https://tesseract-ocr.github.io/" },
  { name: "FastAPI", url: "https://fastapi.tiangolo.com/" },
  { name: "SQLAlchemy", url: "https://www.sqlalchemy.org/" },
  { name: "PostgreSQL", url: "https://www.postgresql.org/" },
  { name: "Neon · PostgreSQL & Neon Auth", url: "https://neon.com/" },
  { name: "Render", url: "https://render.com/" },
  { name: "Brevo", url: "https://www.brevo.com/" },
  { name: "GitHub Actions", url: "https://github.com/features/actions" },
  { name: "package.json", url: repo + "mobile/package.json" },
  { name: "requirements.txt", url: repo + "backend/requirements.txt" },
];
