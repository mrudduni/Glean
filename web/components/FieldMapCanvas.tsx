"use client";

import { MapContainer, Polygon, TileLayer, Tooltip, CircleMarker } from "react-leaflet";
import type { Field, Lang } from "@/lib/types";
import { theme } from "@/lib/theme";

const kindColors = { irrigated: theme.accent, dryland: theme.crop.cover };

export default function FieldMapCanvas({
  fields,
  neighbors,
  selected,
  onSelect,
  lang,
}: {
  fields: Field[];
  neighbors: Array<{ id: string; polygon: [number, number][] }>;
  selected?: string;
  onSelect?: (id: string) => void;
  lang: Lang;
}) {
  return (
    <MapContainer center={[37.99, -100.89]} zoom={12} scrollWheelZoom={false} className="leaflet-map" zoomControl={false}>
      <TileLayer
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attribution="Tiles &copy; Esri"
      />
      {neighbors.map((neighbor) => (
        <Polygon key={neighbor.id} positions={neighbor.polygon} pathOptions={{ color: "#e8eadf", fillColor: "#e8eadf", fillOpacity: 0.08, weight: 1, dashArray: "4 5" }} />
      ))}
      {fields.map((field) => (
        <Polygon
          key={field.id}
          positions={field.polygon}
          pathOptions={{
            color: kindColors[field.kind],
            fillColor: kindColors[field.kind],
            fillOpacity: selected === field.id ? 0.48 : 0.25,
            weight: selected === field.id ? 3 : 2,
          }}
          eventHandlers={{ click: () => onSelect?.(field.id) }}
        >
          <Tooltip sticky>{field.name[lang] || field.name.en} · {field.kind === "dryland" ? (lang === "es" ? "secano" : "dryland") : (lang === "es" ? "regadío" : "irrigated")}</Tooltip>
        </Polygon>
      ))}
      <CircleMarker center={[37.99, -100.89]} radius={3} pathOptions={{ color: "#f5f3ea", fillColor: "#f5f3ea", fillOpacity: 1, weight: 0 }} />
    </MapContainer>
  );
}
