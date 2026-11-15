// Spanish for the source descriptions in sources.json, which is English only today.
// Each line applies only while the English text is exactly as below; data-owner text always wins.
// Proposed to the data owner in HANDOFF_OTHER_OWNERS.md.
const ES: Record<string, [string, string]> = {
  "Rotation Replay weather, reference ET, heat, frost and wind days": ["Clima de la repetición de rotaciones, ET de referencia, días de calor, helada y viento", ""],
  "Daily max/min/mean air temperature, humidity, wind at 2 m and 10 m, solar radiation, corrected precipitation": ["Temperatura del aire diaria máxima, mínima y media, humedad, viento a 2 m y 10 m, radiación solar, precipitación corregida", ""],
  "Regional aquifer / water-storage trend in the water outlook": ["Tendencia regional del acuífero y del agua almacenada en la perspectiva del agua", ""],
  "Monthly terrestrial water storage anomaly (liquid water equivalent)": ["Anomalía mensual del agua almacenada en tierra (equivalente en agua líquida)", ""],
  "Field slope and cold-air low-spot flag": ["Pendiente del campo y aviso de zonas bajas con aire frío", ""],
  "Elevation": ["Elevación", ""],
  "Soil water holding, erodibility, soil-health inputs and neighbour matching": ["Agua que retiene el suelo, erosionabilidad, datos de salud del suelo y comparación con campos vecinos", ""],
  "Map units, components and horizons: AWC, AWS 0–100 cm, organic matter, K factor, hydrologic group, WEG/WEI, drainage, restrictions": ["Unidades de mapa, componentes y horizontes: AWC, AWS 0–100 cm, materia orgánica, factor K, grupo hidrológico, WEG/WEI, drenaje, restricciones", ""],
  "Demo field outlines, crop history, detected rotation, neighbour pool": ["Contornos de los campos de ejemplo, historial de cultivos, rotación detectada, campos vecinos", ""],
  "Field polygons with the Cropland Data Layer crop for each year": ["Polígonos de campo con el cultivo del Cropland Data Layer de cada año", ""],
  "Yields, prices and the local-market check": ["Rendimientos, precios y la comprobación de mercado local", ""],
  "Survey yields (irrigated / non-irrigated), prices received, acres planted": ["Rendimientos de encuesta (con y sin riego), precios recibidos, acres sembrados", ""],
  "Replay validation and neighbours' real water use": ["Validación de la repetición y uso real de agua de los campos vecinos", ""],
  "Actual evapotranspiration, ensemble of 6 satellite models": ["Evapotranspiración real, conjunto de 6 modelos satelitales", ""],
  "1991–2020 climate normals vs 2016–2025, ground-based check of POWER": ["Normales climáticas 1991–2020 frente a 2016–2025, comprobación en tierra de POWER", ""],
  "Daily min/max temperature and precipitation": ["Temperatura mínima y máxima diaria y precipitación", ""],
  "Local aquifer trend near each field": ["Tendencia local del acuífero cerca de cada campo", ""],
  "Depth to water below land surface at monitoring wells (USGS, KGS and Kansas DWR wells)": ["Profundidad del agua bajo el suelo en pozos de monitoreo (pozos de USGS, KGS y Kansas DWR)", ""],
  "Reference ET and crop water demand in the Replay": ["ET de referencia y demanda de agua de los cultivos en la repetición", ""],
  "Reference ET method and crop coefficients (Kc)": ["Método de ET de referencia y coeficientes de cultivo (Kc)", ""],
  "Rotation Replay results and the calendar": ["Resultados de la repetición de rotaciones y el calendario", ""],
  "Simulated yield, water use and soil outputs built from the inputs above": ["Rendimiento, uso de agua y resultados de suelo simulados a partir de los datos de arriba", ""],
  "0.5° × 0.625° grid, daily": ["Cuadrícula de 0.5° × 0.625°, diaria", ""],
  "1981–2025 (solar from 1984)": ["1981–2025 (radiación solar desde 1984)", ""],
  "2002-04 → latest (gap 2017-07 → 2018-05)": ["2002-04 → más reciente (sin datos 2017-07 → 2018-05)", ""],
  "0.5° grid; ~300 km true resolution": ["Cuadrícula de 0.5°; resolución real ~300 km", ""],
  "February 2000": ["Febrero de 2000", ""],
  "Current release": ["Versión actual", ""],
  "Map units at 1:12,000–1:24,000": ["Unidades de mapa a 1:12,000–1:24,000", ""],
  "Field polygons from 30 m CDL": ["Polígonos de campo del CDL de 30 m", ""],
  "2000–2025 (prices 2015–2024)": ["2000–2025 (precios 2015–2024)", ""],
  "Finney County, SW Kansas district, Kansas": ["Condado de Finney, distrito del suroeste de Kansas, Kansas", ""],
  "2016 → latest": ["2016 → más reciente", ""],
  "30 m, monthly": ["30 m, mensual", ""],
  "4 km, daily": ["4 km, diaria", ""],
  "Individual wells": ["Pozos individuales", ""],
  "Method, not a dataset": ["Método, no un conjunto de datos", ""],
  "Field, daily/annual": ["Campo, diario/anual", ""],
};

/** The source text in the viewer's language: Spanish from the table above while the data has none. */
export function sourceText(text: string, lang: "en" | "es"): string {
  return lang === "es" ? ES[text]?.[0] ?? text : text;
}
