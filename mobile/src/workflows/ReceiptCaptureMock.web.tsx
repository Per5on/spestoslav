import { useState } from "react";
import * as ImagePicker from "expo-image-picker";
import { Image, View } from "react-native";
import { Button } from "../Action";
import { Text, useUI } from "../ui";

const maxPageBytes = 8 * 1024 * 1024;
const maxPagePixels = 20_000_000;

function fiscalMetadata(payload: string) {
  const match = /^([a-z0-9]{8})\*(\d{1,12})\*(\d{4}-\d{2}-\d{2})\*((?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d)\*(-?\d{1,12}[.,]\d{2})$/i.exec(payload.trim());
  if (!match) return null;
  const [, fiscalId, number, date, time, total] = match;
  const timestamp = new Date(date + "T00:00:00Z");
  if (!Number.isFinite(timestamp.getTime()) || timestamp.toISOString().slice(0, 10) !== date) return null;
  return { fiscalId, number, date, time, total };
}

export function ReceiptCaptureMock() {
  const { styles: s } = useUI();
  const [mode, setMode] = useState<"document" | "photo">();
  const [pages, setPages] = useState<ImagePicker.ImagePickerAsset[]>([]);
  const [metadata, setMetadata] = useState<ReturnType<typeof fiscalMetadata>>(null);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  const unavailable = new URLSearchParams(location.search).get("document") === "unavailable";

  async function pick(qr: boolean) {
    setStatus("");
    setBusy(true);
    try {
      const pageLimit = !qr && mode === "document" ? 2 : 1;
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ["images"], allowsMultipleSelection: pageLimit > 1,
        selectionLimit: pageLimit, exif: false,
      });
      if (result.canceled) return;
      if (result.assets.length > pageLimit) {
        setStatus(`Изберете до ${pageLimit} изображения.`);
        return;
      }
      if (result.assets.some(asset => (asset.fileSize ?? 0) > maxPageBytes ||
          asset.width * asset.height > maxPagePixels)) {
        setStatus("Изображението е над лимита от 8 MiB или 20 мегапиксела.");
        return;
      }
      if (!qr) {
        setPages(result.assets);
        setMetadata(null);
        return;
      }
      const { BrowserQRCodeReader } = await import("@zxing/browser");
      const decoded = await new BrowserQRCodeReader().decodeFromImageUrl(result.assets[0].uri);
      const value = fiscalMetadata(decoded.getText());
      setMetadata(value);
      if (!value) setStatus("QR кодът не е във формат за фискален бон.");
    } catch {
      if (qr) setMetadata(null);
      setStatus(qr ? "Не е разпознат фискален QR код." : "Снимката не може да бъде отворена.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <View testID="receipt-capture-mock" style={s.panel}>
      <Text style={s.meta}>Симулация на скенер · тестови данни</Text>
      {!mode ? <Button label="Сканирай документ" onPress={() => setMode(unavailable ? "photo" : "document")} />
        : <>
          <Text style={s.productName}>{mode === "document" ? "Документ · симулация" : "Снимка · резервен режим"}</Text>
          <Text style={s.meta}>{mode === "document"
            ? "Изберете до две изображения на заснетите части."
            : "Скенерът за документи е недостъпен. Изберете една снимка."}</Text>
          <Button label="Избери снимки за теста" disabled={busy} onPress={() => void pick(false)} />
          <Button label="Прочети фискален QR от снимка" disabled={busy} onPress={() => void pick(true)} />
          <Button label="Затвори теста" disabled={busy} onPress={() => {
            setMode(undefined); setPages([]); setMetadata(null); setStatus("");
          }} />
        </>}
      {pages.length > 0 && <Text style={s.meta}>Части от документа: {pages.length}</Text>}
      {pages.map((asset, index) => <Image key={asset.uri + index} source={{ uri: asset.uri }}
        accessibilityLabel={`Част ${index + 1}`} style={{ width: "100%", height: 86 }} resizeMode="contain" />)}
      {!!status && <Text accessibilityRole="alert" style={s.notice}>{status}</Text>}
      {metadata && <View testID="mock-fiscal-metadata" style={{ gap: 6 }}>
        <Text>Фискален идентификатор: {metadata.fiscalId}</Text>
        <Text>Номер на бона: {metadata.number}</Text>
        <Text>Дата и час: {metadata.date} {metadata.time}</Text>
        <Text>Общо според QR: {metadata.total}</Text>
        <Text style={s.meta}>Валутата и редовете на покупките се проверяват от документа.</Text>
      </View>}
    </View>
  );
}
