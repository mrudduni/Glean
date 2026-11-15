"use client";

import { useEffect } from "react";
import { MapContainer, Polygon, TileLayer, Tooltip, useMap } from "react-leaflet";
import type { LatLngBoundsExpression, LatLngExpression } from "leaflet";
import type { Field, Lang } from "@/lib/types";
import type { TFunction } from "@/lib/i18n";
import type { MapNeighbor } from "@/components/FieldMap";
import { loc } from "@/lib/i18n";
import { theme } from "@/lib/theme";

export const kindColors: Record<Field["kind"], string> = {
  irrigated_pivot: theme.crop.corn,
  dryland: theme.crop.wheat,
  sandy_wind: theme.risk.wind,
};

/** GeoJSON [lon, lat] rings → Leaflet [lat, lon]. */
function ring(polygon: Field["geometry"]): LatLngExpression[][] {
  return polygon.coordinates.map((r) => r.map(([lon, lat]) => [lat, lon] as [number, number]));
}

function FitBounds({ bounds, signature }: { bounds: LatLngBoundsExpression; signature: string }) {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(bounds, { padding: [24, 24] });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [map, signature]);
  return null;
}

export default function FieldMapCanvas({
  fields, neighbors, selected, onSelect, lang, t,
}: {
  fields: Field[];
  neighbors: MapNeighbor[];
  selected?: string;
  onSelect?: (id: string) => void;
  lang: Lang;
  t: TFunction;
}) {
  const focus = selected ? fields.filter((field) => field.id === selected) : fields;
  const points = [...focus, ...(selected ? neighbors : [])].flatMap((item) => item.geometry.coordinates[0].map(([lon, lat]) => [lat, lon] as [number, number]));
  const bounds: LatLngBoundsExpression = points.length ? points : [[37.9, -101], [38.1, -100.7]];
  return (
    <MapContainer center={[37.99, -100.87]} zoom={11} scrollWheelZoom={false} className="leaflet-map" zoomControl={false}>
      <TileLayer
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attribution="Tiles &copy; Esri"
      />
      <FitBounds bounds={bounds} signature={`${selected ?? "all"}:${fields.length}:${neighbors.length}`} />
      {neighbors.map((neighbor) => (
        <Polygon
          key={neighbor.id}
          positions={ring(neighbor.geometry)}
          pathOptions={{ color: neighbor.color ?? "#e8eadf", fillColor: neighbor.color ?? "#e8eadf", fillOpacity: neighbor.color ? 0.35 : 0.08, weight: 1 }}
        >
          <Tooltip sticky>{neighbor.rotation_class} · {Math.round(neighbor.similarity * 100)}%</Tooltip>
        </Polygon>
      ))}
      {fields.map((field) => (
        <Polygon
          key={field.id}
          positions={ring(field.geometry)}
          pathOptions={{
            color: selected === field.id ? "#ffffff" : kindColors[field.kind],
            fillColor: kindColors[field.kind],
            fillOpacity: selected === field.id ? 0.5 : 0.3,
            weight: selected === field.id ? 3 : 2,
          }}
          eventHandlers={{ click: () => onSelect?.(field.id) }}
        >
          <Tooltip sticky>{loc(field.name, lang)} · {t(`field.kind.${field.kind}`, field.kind)}</Tooltip>
        </Polygon>
      ))}
    </MapContainer>
  );
}
