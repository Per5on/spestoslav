export const overflowMenu = [
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
  | "terms"
  | "privacy"
  | (typeof overflowMenu)[number]["id"];
