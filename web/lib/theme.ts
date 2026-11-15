// Literal colours for libraries that cannot read CSS variables (Recharts, Leaflet). README §8.5 tokens.json.
import tokens from "@/styles/tokens.json";

type Tokens = {
  color: Record<string, string>;
  crop: Record<string, string>;
  rot: Record<string, string>;
  risk: Record<string, string>;
  font: Record<string, string>;
};

export const theme = tokens as Tokens;

/** CSS variable for a rotation colour, with the literal as fallback. */
export const rotColor = (id: string) => `var(--rot-${id}, ${theme.rot[id] ?? "#888"})`;
export const cropColor = (id: string) => `var(--crop-${id}, ${theme.crop[id] ?? "#ccc"})`;

/** Map colour per field kind (Leaflet needs literal colours). */
export const kindColors: Record<"irrigated_pivot" | "dryland" | "sandy_wind", string> = {
  irrigated_pivot: theme.crop.corn,
  dryland: theme.crop.wheat,
  sandy_wind: theme.risk.wind,
};
