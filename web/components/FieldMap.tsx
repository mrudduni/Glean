"use client";

import dynamic from "next/dynamic";
import { MapPin } from "lucide-react";
import type { Field } from "@/lib/types";
import { useFieldShift } from "@/lib/state";

const MapCanvas = dynamic(() => import("@/components/FieldMapCanvas"), {
  ssr: false,
  loading: () => <div className="map-placeholder"><span className="map-spinner" /> Preparing field map…</div>,
});

export function FieldMap({
  fields,
  neighbors = [],
  selected,
  onSelect,
}: {
  fields: Field[];
  neighbors?: Array<{ id: string; polygon: [number, number][] }>;
  selected?: string;
  onSelect?: (id: string) => void;
}) {
  const { lang } = useFieldShift();
  return (
    <div className="map-shell">
      <div className="map-topline">
        <span><MapPin size={16} /> {lang === "es" ? "ZONA DE GARDEN CITY" : "GARDEN CITY AREA"}</span>
        <span className="map-scale">{lang === "es" ? "LÍMITES DE PARCELAS" : "SATELLITE FIELD BOUNDARIES"}</span>
      </div>
      <MapCanvas fields={fields} neighbors={neighbors} selected={selected} onSelect={onSelect} lang={lang} />
      <div className="map-legend">
        <span><i className="legend-dot irrigated" /> {lang === "es" ? "Regadío" : "Irrigated"}</span>
        <span><i className="legend-dot dryland" /> {lang === "es" ? "Secano" : "Dryland"}</span>
        <small>Esri World Imagery</small>
      </div>
    </div>
  );
}
