import React, { useEffect, useRef } from "react";
import { BrowserMultiFormatReader, IScannerControls } from "@zxing/browser";
import { barcodeHints } from "./scanImage.web";
import { validGTIN } from "./barcode";
export function BarcodeCamera({
  onCode,
  onError,
}: {
  onCode: (code: string) => void;
  onError: () => void;
}) {
  const video = useRef<HTMLVideoElement>(null),
    code = useRef(onCode),
    error = useRef(onError);
  code.current = onCode;
  error.current = onError;
  useEffect(() => {
    let cancelled = false,
      controls: IScannerControls | undefined;
    const reader = new BrowserMultiFormatReader(barcodeHints);
    reader
      .decodeFromConstraints(
        { audio: false, video: { facingMode: { ideal: "environment" } } },
        video.current!,
        (result) => {
          if (!cancelled && result && validGTIN(result.getText()))
            code.current(result.getText());
        },
      )
      .then((c) => {
        controls = c;
        if (cancelled) c.stop();
      })
      .catch(() => {
        if (!cancelled) error.current();
      });
    return () => {
      cancelled = true;
      controls?.stop();
    };
  }, []);
  return (
    <video
      data-testid="barcode-camera"
      ref={video}
      muted
      playsInline
      style={{
        width: "100%",
        height: 240,
        objectFit: "contain",
        borderRadius: 12,
      }}
    />
  );
}
