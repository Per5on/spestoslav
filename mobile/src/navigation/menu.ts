export const overflowMenu = [
  { id: "merchants", label: "merchants", icon: "storefront-outline" },
  { id: "scan", label: "scan", icon: "scan-outline" },
  { id: "receipts", label: "receipts", icon: "receipt-outline" },
  { id: "login", label: "login", icon: "person-outline" },
  { id: "settings", label: "settings", icon: "settings-outline" },
  { id: "about", label: "about", icon: "information-circle-outline" },
] as const;
export type Screen =
  | "catalog"
  | "basket"
  | "font"
  | "deleteData"
  | "appearance"
  | "language"
  | "feedback"
  | "thirdParties"
  | "terms"
  | "privacy"
  | (typeof overflowMenu)[number]["id"];
