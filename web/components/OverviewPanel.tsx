"use client";

import { ArrowDownRight, ArrowUpRight, Droplets, Leaf, MapPinned, ThermometerSun } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer, Tooltip } from "recharts";
import type { Field, FieldBundle, Lang, SourcesFile, Crop, Rotation, CopyFile, CardTextFile } from "@/lib/types";
import { fill, formatVar, t } from "@/lib/i18n";
import { SourceChips } from "@/components/SourceChips";

const monthLabels = {
  en: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
  es: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
};

export function OverviewPanel({
  field,
  bundle,
  crops,
  rotations,
  sources,
  copy,
  cardText,
  lang,
}: {
  field: Field;
  bundle: FieldBundle;
  crops: Crop[];
  rotations: Rotation[];
  sources: SourcesFile;
  copy: CopyFile["strings"];
  cardText: CardTextFile;
  lang: Lang;
}) {
  const cropMap = new Map(crops.map((crop) => [crop.id, crop]));
  const rotation = rotations.find((item) => item.id === bundle.summary.current_rotation.id);
  const graceData = bundle.water.grace.map((point) => ({ month: point.month, value: point.anomaly_mm }));
  const trend = bundle.water.grace.at(-1)?.anomaly_mm ?? 0;
  const outlook = t(`overview.outlook.${bundle.water.outlook}`, copy, lang);
  const years = bundle.summary.current_rotation.years[1] - bundle.summary.current_rotation.years[0] + 1;
  const hotDayDelta = bundle.summary.climate.recent.hot_days - bundle.summary.climate.normal.hot_days;
  return (
    <section className="workspace-section" id="overview">
      <div className="section-title-row">
        <div>
          <div className="eyebrow"><span className="eyebrow-rule" /> FIELD SNAPSHOT</div>
          <h2>{t("overview.title", copy, lang)}</h2>
          <p>{t("overview.subtitle", copy, lang)}</p>
        </div>
        <span className="section-index">01 / 06</span>
      </div>

      <div className="overview-grid">
        <article className="overview-card current-rotation-card">
          <div className="card-kicker"><span className="icon-disc"><Leaf size={17} /></span><span>{t("overview.current", copy, lang)}</span></div>
          <h3>{rotation?.name[lang] || rotation?.name.en || "Current rotation"}</h3>
          <div className="crop-chip-line">
            <div className="crop-chip-group">
              {(field.current_crops || bundle.summary.current_rotation.steps).map((id, index) => {
                const crop = cropMap.get(id);
                return crop ? <span className="crop-chip" key={`${id}-${index}`} style={{ "--chip-color": crop.color } as React.CSSProperties}>{crop.name[lang] || crop.name.en}</span> : null;
              })}
            </div>
          </div>
          <p className="small-note">{fill(copy["overview.detected_from"], { years }, lang)}</p>
          <SourceChips ids={["CDL"]} sources={sources} lang={lang} />
        </article>

        <article className="overview-card soil-card">
          <div className="card-kicker"><span className="icon-disc sand"><MapPinned size={17} /></span><span>{t("overview.soil", copy, lang)}</span></div>
          <div className="soil-texture">{bundle.summary.soil.texture[lang] || bundle.summary.soil.texture.en}</div>
          <div className="soil-metrics">
            <div><small>{t("overview.water_storage", copy, lang)}</small><strong>{formatVar("storage_mm", bundle.summary.soil.water_storage_mm, lang)}</strong></div>
            <div><small>{t("overview.organic_matter", copy, lang)}</small><strong>{formatVar("organic_pct", bundle.summary.soil.organic_matter_pct, lang)}</strong></div>
          </div>
          <div className="wind-note"><span>{t("overview.wind_erosion", copy, lang)}</span><strong>{bundle.summary.soil.wind_erosion[lang] || bundle.summary.soil.wind_erosion.en}</strong></div>
          <p className="micro-note">{t("overview.soil_note", copy, lang)}</p>
          <SourceChips ids={bundle.summary.soil.source_ids} sources={sources} lang={lang} />
        </article>

        <article className="overview-card climate-card">
          <div className="card-kicker"><span className="icon-disc orange"><ThermometerSun size={17} /></span><span>{t("overview.climate", copy, lang)}</span></div>
          <div className="climate-legend"><span><i className="dot normal" />{t("overview.normal", copy, lang)}</span><span><i className="dot recent" />{t("overview.recent", copy, lang)}</span></div>
          <ClimatePair label={t("overview.frost_free", copy, lang)} normal={bundle.summary.climate.normal.frost_free_days} recent={bundle.summary.climate.recent.frost_free_days} lang={lang} />
          <ClimatePair label={t("overview.hot_days", copy, lang)} normal={bundle.summary.climate.normal.hot_days} recent={bundle.summary.climate.recent.hot_days} lang={lang} />
          <ClimatePair label={t("overview.precip", copy, lang)} normal={bundle.summary.climate.normal.precipitation_mm} recent={bundle.summary.climate.recent.precipitation_mm} unit=" mm" lang={lang} />
          <span className={`climate-delta ${hotDayDelta >= 0 ? "up" : "down"}`}>
            {hotDayDelta >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
            {fill(copy["overview.hot_day_change"], { count: Math.abs(hotDayDelta) }, lang)}
          </span>
          <SourceChips ids={bundle.summary.climate.source_ids} sources={sources} lang={lang} />
        </article>

        <article className="overview-card water-card">
          <div className="card-kicker"><span className="icon-disc blue"><Droplets size={17} /></span><span>{t("overview.water", copy, lang)}</span></div>
          <div className="water-status"><span className="water-status-dot" />{outlook}</div>
          <div className="water-chart">
            <ResponsiveContainer width="100%" height={85}>
              <AreaChart data={graceData}>
                <defs><linearGradient id="waterFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#5c8e7a" stopOpacity={0.3} /><stop offset="100%" stopColor="#5c8e7a" stopOpacity={0} /></linearGradient></defs>
                <Tooltip
                  contentStyle={{
                    background: "var(--surface)",
                    border: "1px solid var(--line)",
                    borderRadius: 8,
                    fontSize: 13,
                    color: "var(--ink)",
                    boxShadow: "0 6px 18px rgba(0, 0, 0, 0.25)",
                  }}
                  itemStyle={{ color: "var(--ink)" }}
                  formatter={(value) => [`${value} mm`, "Anomaly"]}
                  labelFormatter={(label) => String(label)}
                />
                <Area type="monotone" dataKey="value" stroke="#4b8c76" fill="url(#waterFill)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <p className="micro-note">{t("overview.grace_note", copy, lang)} {bundle.water.well && <span>{lang === "es" ? "Tendencia del pozo cercano:" : "Nearby well trend:"} {bundle.water.well.trend_m_per_year.toFixed(1)} m/year.</span>}</p>
          <SourceChips ids={["SMAP"]} sources={sources} lang={lang} />
        </article>
      </div>

      <div className="headline-row">
        <div className="headline-title"><span>FIELD NOTES</span><h3>{t("overview.headlines", copy, lang)}</h3></div>
        {bundle.summary.headline_facts.map((fact, index) => {
          const text = cardText.headline[fact.text_id];
          return (
            <article className="headline-fact" key={`${fact.text_id}-${index}`}>
              <span className="headline-number">0{index + 1}</span>
              <p>{fill(text, fact.vars, lang)}</p>
              <SourceChips ids={fact.source_ids} sources={sources} lang={lang} />
            </article>
          );
        })}
      </div>
    </section>
  );
}

function ClimatePair({ label, normal, recent, unit = " days", lang = "en" }: { label: string; normal: number; recent: number; unit?: string; lang?: Lang }) {
  const max = Math.max(normal, recent, 1);
  return (
    <div className="climate-pair">
      <div className="climate-pair-label"><span>{label}</span><b>{recent}{unit}</b></div>
      <div className="climate-track"><span className="climate-bar normal" style={{ width: `${normal / max * 100}%` }} /><span className="climate-bar recent" style={{ width: `${recent / max * 100}%` }} /></div>
      <div className="climate-values"><span>{lang === "es" ? "Referencia" : "Reference"} {normal}{unit}</span><span>{lang === "es" ? "Reciente" : "Recent"} {recent}{unit}</span></div>
    </div>
  );
}

export function WaterTrend({ bundle, lang }: { bundle: FieldBundle; lang: Lang }) {
  const data = bundle.water.grace.map((point, index) => ({ month: monthLabels[lang][index] || point.month, value: point.anomaly_mm }));
  return (
    <ResponsiveContainer width="100%" height={72}>
      <AreaChart data={data}><Area dataKey="value" type="monotone" stroke="#4b8c76" fill="#dcebe3" strokeWidth={2} /></AreaChart>
    </ResponsiveContainer>
  );
}
