"use client";

import { AlertTriangle, CircleCheck, Info } from "lucide-react";
import type { Level } from "@/lib/types";

const icons = { good: CircleCheck, fair: Info, limited: AlertTriangle };
const legacyClass = { good: "high", fair: "medium", limited: "low" } as const;

export function TrustBadge({ level, label }: { level: Level; label: string }) {
  const Icon = icons[level];
  return <span className={`trust-badge trust-${legacyClass[level]}`}><Icon size={15} aria-hidden="true" />{label}</span>;
}
