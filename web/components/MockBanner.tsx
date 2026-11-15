"use client";

import { useEffect, useState } from "react";
import { mockFiles, onMockChange } from "@/lib/data";
import { useCopy } from "@/lib/useCopy";

/** Shows copy["banner.mock"] while any loaded file has _meta.mock === true. */
export function MockBanner() {
  const t = useCopy();
  const [files, setFiles] = useState<string[]>([]);
  useEffect(() => {
    setFiles(mockFiles());
    const off = onMockChange(() => setFiles(mockFiles()));
    return () => { off(); };
  }, []);
  if (!files.length) return null;
  return (
    <div className="mock-banner" role="status" title={files.join("\n")}>
      {t("banner.mock", "Mock data: some numbers on this page are placeholders.")}
    </div>
  );
}
