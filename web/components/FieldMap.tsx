"use client";

import dynamic from "next/dynamic";
import type { Field, NeighborsFile } from "@/lib/types";
import type { TFunction } from "@/lib/i18n";

const MapCanvas = dynamic(() => import("@/components/FieldMapCanvas"), {
  ssr: false,
  loading: () => <div className="map-placeholder"><span className="map-spinner" /></div>,
});

export type MapNeighbor = NeighborsFile["fields"][number] & { color?: string; label?: string };
export type MapLegendItem = { color: string; label: string; dashed?: boolean };

export function FieldMap({
  fields, neighbors = [], selected, onSelect, t, lang, labels = false, legend,
}: {
  fields: Field[];
  neighbors?: MapNeighbor[];
  selected?: string;
  onSelect?: (id: string) => void;
  t: TFunction;
  lang: "en" | "es";
  /** Show each field's name on the map (home page). */
  labels?: boolean;
  /** Replaces the field-kind legend (Farms like yours shows rotation colours instead). */
  legend?: MapLegendItem[];
}) {
  return (
    <div className="map-shell">
      <MapCanvas fields={fields} neighbors={neighbors} selected={selected} onSelect={onSelect} lang={lang} t={t} labels={labels} />
      <div className="map-legend">
        {legend
          ? legend.map((item) => <span key={item.label}><i className="legend-dot" style={{ background: item.color }} /> {item.label}</span>)
          : (
            <>
              <span><i className="legend-dot irrigated" /> {t("field.kind.irrigated_pivot", "Irrigated pivot")}</span>
              <span><i className="legend-dot dryland" /> {t("field.kind.dryland", "Dryland")}</span>
              <span><i className="legend-dot sandy" /> {t("field.kind.sandy_wind", "Sandy, wind-erodible")}</span>
            </>
          )}
        <small>{t("map.boundaries", "USDA field boundaries")} · Esri World Imagery</small>
      </div>
    </div>
  );
}
