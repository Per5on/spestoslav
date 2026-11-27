const sofiaClock = new Intl.DateTimeFormat("en-GB", {
  timeZone: "Europe/Sofia", year: "numeric", month: "2-digit", day: "2-digit",
  hour: "2-digit", hourCycle: "h23",
});

export function publishedPriceWindow(timestamp: number): string {
  const parts = Object.fromEntries(
    sofiaClock.formatToParts(timestamp).map(({ type, value }) => [type, value]),
  );
  const hour = Number(parts.hour);
  // 00:00–05:59 belongs to the previous evening's window.
  if (hour < 6) {
    const previous = new Date(Date.UTC(Number(parts.year), Number(parts.month) - 1, Number(parts.day) - 1));
    return previous.toISOString().slice(0, 10) + ":18";
  }
  return `${parts.year}-${parts.month}-${parts.day}:${hour < 18 ? "06" : "18"}`;
}
