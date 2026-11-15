"use client";

import { Fragment, useEffect } from "react";
import { MapContainer, Polygon, TileLayer, Tooltip, useMap } from "react-leaflet";
import type { LatLngBoundsExpression, LatLngExpression } from "leaflet";
import type { Field, Lang } from "@/lib/types";
import type { TFunction } from "@/lib/i18n";
import type { MapNeighbor } from "@/components/FieldMap";
import { loc } from "@/lib/i18n";
import { theme } from "@/lib/theme";
import { KIND_LABEL } from "@/lib/ui";

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
    map.fitBounds(bounds, { paddingTopLeft: [90, 56], paddingBottomRight: [90, 96] });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [map, signature]);
  return null;
}

export default function FieldMapCanvas({
  fields, neighbors, selected, onSelect, lang, t, labels = false,
}: {
  fields: Field[];
  neighbors: MapNeighbor[];
  selected?: string;
  onSelect?: (id: string) => void;
  lang: Lang;
  t: TFunction;
  labels?: boolean;
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
        <Fragment key={field.id}>
          {/* White halo under the outline so it reads on any imagery. */}
          <Polygon positions={ring(field.geometry)} interactive={false} pathOptions={{ color: "#ffffff", weight: 6, opacity: 0.9, fill: false }} />
          <Polygon
            positions={ring(field.geometry)}
            pathOptions={{ color: kindColors[field.kind], fillColor: kindColors[field.kind], fillOpacity: 0.35, weight: 3 }}
            eventHandlers={{ click: () => onSelect?.(field.id) }}
          >
            {labels
              ? <Tooltip permanent direction="top" offset={[0, -8]} className="field-label">{loc(field.name, lang)}</Tooltip>
              : <Tooltip sticky>{loc(field.name, lang)} · {t(`field.kind.${field.kind}`, KIND_LABEL[field.kind])}</Tooltip>}
          </Polygon>
        </Fragment>
      ))}
    </MapContainer>
  );
}
