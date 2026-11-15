"use client";

import dynamic from "next/dynamic";
import { MapPin } from "lucide-react";
import type { Field, NeighborsFile } from "@/lib/types";
import type { TFunction } from "@/lib/i18n";

const MapCanvas = dynamic(() => import("@/components/FieldMapCanvas"), {
  ssr: false,
  loading: () => <div className="map-placeholder"><span className="map-spinner" /></div>,
});

export type MapNeighbor = NeighborsFile["fields"][number] & { color?: string };

export function FieldMap({
  fields, neighbors = [], selected, onSelect, t, lang,
}: {
  fields: Field[];
  neighbors?: MapNeighbor[];
  selected?: string;
  onSelect?: (id: string) => void;
  t: TFunction;
  lang: "en" | "es";
}) {
  return (
    <div className="map-shell">
      <div className="map-topline">
        <span><MapPin size={16} aria-hidden="true" /> {t("map.area", "Garden City area")}</span>
        <span className="map-scale">{t("map.boundaries", "USDA field boundaries")}</span>
      </div>
      <MapCanvas fields={fields} neighbors={neighbors} selected={selected} onSelect={onSelect} lang={lang} t={t} />
      <div className="map-legend">
        <span><i className="legend-dot irrigated" /> {t("field.kind.irrigated_pivot", "Irrigated pivot")}</span>
        <span><i className="legend-dot dryland" /> {t("field.kind.dryland", "Dryland")}</span>
        <span><i className="legend-dot sandy" /> {t("field.kind.sandy_wind", "Sandy, wind-erodible")}</span>
        <small>Esri World Imagery</small>
      </div>
    </div>
  );
}
