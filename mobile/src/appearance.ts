import type { ImageStyle, TextStyle, ViewStyle } from "react-native";

export const palettes = [
  { header: "#195b27", accent: "#ff8500", tint: "#edf3e5", ink: "#19562a" },
  { header: "#174679", accent: "#855600", tint: "#e8f0fb", ink: "#163d6b" },
  { header: "#452873", accent: "#94413e", tint: "#efe9f8", ink: "#492b73" },
  { header: "#195651", accent: "#9b482a", tint: "#e1f1ee", ink: "#164741" },
  { header: "#712c3d", accent: "#865219", tint: "#f9e8ed", ink: "#692a39" },
  { header: "#31445a", accent: "#3e6c53", tint: "#e9edf3", ink: "#30455c" },
  { header: "#63411d", accent: "#8c4536", tint: "#f6eee1", ink: "#5a3817" },
  { header: "#334b26", accent: "#7350a3", tint: "#edf1e2", ink: "#344c26" },
] as const;

const greens = new Set(["#19562a", "#234b2d", "#267133", "#1a5228", "#263e2d", "#243d2b", "#283f2e"]);
const pale = new Set(["#edf3e5", "#eaf1dd", "#eff4e8", "#dbead3"]);
const accentColors = new Set(["#ff8500", "#f48100", "#de7300"]);
const foreground = new Set(["#111", "#606a73", "#617363", "#526e4d", "#63816a", "#8a4200", "#855511"]);
const borders = new Set(["#d9e2d3", "#dce4d6", "#dfe5d8", "#dae2d6", "#edf0e9", "#e7ebdf", "#aaa"]);

export function appearanceColor(color: string, index: number, dark: boolean, background = false) {
  if (!dark && index === 0) return color;
  const palette = palettes[index] ?? palettes[0];
  const value = color.toLowerCase();
  if (value === "#195b27") return palette.header;
  if (accentColors.has(value)) {
    if (dark && !background) return "#ffc073";
    return dark && index === 0 ? "#9b4e00" : palette.accent;
  }
  if (pale.has(value)) return dark ? (value === "#dbead3" ? "#45564c" : "#293831") : palette.tint;
  if (dark && borders.has(value)) return "#53655b";
  if (background && dark && (value === "#fff" || value === "#ffffff")) return "#161e1a";
  if (background && dark && value === "#fff6e7") return "#392d1e";
  if (greens.has(value)) return dark && !background ? "#c1edcf" : palette.ink;
  if (dark && !background && foreground.has(value)) return "#d4e4da";
  return color;
}

export function appearanceStyle<T extends ViewStyle | TextStyle | ImageStyle>(style: T, index: number, dark: boolean): T {
  if (!dark && index === 0) return style;
  const themed = { ...style };
  for (const key of Object.keys(themed)) {
    const value = themed[key as keyof T];
    if (key.toLowerCase().endsWith("color") && typeof value === "string") {
      Object.assign(themed, { [key]: appearanceColor(value, index, dark, key === "backgroundColor") });
    }
  }
  return themed;
}
