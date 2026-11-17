// One logical point above every existing app font setting; saved scales stay valid.
export function appFontSize(base: number, scale: number, minimum: number): number {
  return Math.max(minimum, base * scale) + 1;
}
