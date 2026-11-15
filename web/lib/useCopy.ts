"use client";

import { useEffect, useMemo, useState } from "react";
import { getContent } from "@/lib/data";
import { makeT, type TFunction } from "@/lib/i18n";
import { useFieldShift } from "@/lib/state";
import type { CopyFile } from "@/lib/types";

const NO_STRINGS: CopyFile["strings"] = {};

/** t() bound to copy.json and the current language, for components outside the workspace. */
export function useCopy(): TFunction {
  const { lang } = useFieldShift();
  const [strings, setStrings] = useState<CopyFile["strings"]>(NO_STRINGS);
  useEffect(() => {
    getContent().then((content) => setStrings(content.copy.strings)).catch(() => {});
  }, []);
  return useMemo(() => makeT(strings, lang), [strings, lang]);
}
