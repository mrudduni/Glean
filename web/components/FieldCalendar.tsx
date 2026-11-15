"use client";

import { CloudLightning, Droplet, Snowflake, Sun, Wind } from "lucide-react";
import type { CalendarCell, CalendarFile, RotationId } from "@/lib/types";
import { interpolate, loc } from "@/lib/i18n";
import { cropColor } from "@/lib/theme";
import { cropLabel, type UI } from "@/lib/ui";

type Flag = CalendarCell["flags"][number];
const flagIcon: Record<Flag, typeof Sun> = { heat: Sun, frost: Snowflake, dry: Droplet, bare_storm: CloudLightning, bare_wind: Wind };
const flagColor: Record<Flag, string> = {
  heat: "var(--risk-heat)", frost: "var(--risk-frost)", dry: "var(--risk-dry)", bare_storm: "var(--risk-storm)", bare_wind: "var(--risk-wind)",
};
const FLAGS: Flag[] = ["heat", "frost", "dry", "bare_storm", "bare_wind"];

function monthNames(lang: "en" | "es", style: "short" | "long") {
  const format = new Intl.DateTimeFormat(lang === "es" ? "es-ES" : "en-US", { month: style, timeZone: "UTC" });
  return Array.from({ length: 12 }, (_, i) => format.format(new Date(Date.UTC(2001, i, 15))));
}

/**
 * Field Calendar (wireframe s3). One 13-column grid (label + 12 months) is shared by the climate-odds
 * table and every rotation, so a July column means the same July all the way down. Rotations are
 * stacked in card order, so none can hide off-screen. Each year row names its crops in words;
 * colour repeats it, and flag icons carry the risks.
 */
export function FieldCalendar({ calendar, order, ui }: { calendar: CalendarFile; order: RotationId[]; ui: UI }) {
  const { t, lang } = ui;
  const short = monthNames(lang, "short");
  const long = monthNames(lang, "long");
  const oneDecimal = new Intl.NumberFormat(lang === "es" ? "es-ES" : "en-US", { maximumFractionDigits: 1 });
  const blocks = order
    .map((id) => calendar.rotations.find((rotation) => rotation.rotation_id === id))
    .filter((block): block is CalendarFile["rotations"][number] => Boolean(block));
  const odds = (p: number) => Math.round(p * 10);
  const stageLabel = (stage: CalendarCell["stage"]) => (stage ? t(`calendar.stage.${stage}`, { ini: "Establishing", dev: "Growing", mid: "Peak growth", late: "Ripening" }[stage]) : "");
  const isBare = (state: string) => state === "bare" || state === "fallow";
  const rowCrops = (cells: CalendarCell[]) => {
    const crops = [...new Set(cells.map((cell) => cell.state).filter((state) => !isBare(state)))];
    return crops.length ? crops.map((crop) => cropLabel(ui, crop)).join(", ") : t("calendar.bare");
  };
  const risks = [
    { key: "heat", label: t("calendar.flag.heat"), value: (m: CalendarFile["climate_risk"][number]) => m.p_heat, kind: "odds" },
    { key: "frost", label: t("calendar.flag.frost"), value: (m: CalendarFile["climate_risk"][number]) => m.p_frost, kind: "odds" },
    { key: "dry", label: t("calendar.flag.dry"), value: (m: CalendarFile["climate_risk"][number]) => m.p_dry_spell, kind: "odds" },
    { key: "storm", label: t("calendar.storm_days", "Storm days"), value: (m: CalendarFile["climate_risk"][number]) => m.storm_days, kind: "days" },
    { key: "wind", label: t("calendar.windy_days", "Windy days"), value: (m: CalendarFile["climate_risk"][number]) => m.windy_days, kind: "days" },
  ] as const;
  const maxDays = { storm: Math.max(1, ...calendar.climate_risk.map((m) => m.storm_days)), wind: Math.max(1, ...calendar.climate_risk.map((m) => m.windy_days)) };

  return (
    <section className="workspace-section calendar-section" id="calendar" aria-labelledby="calendar-heading">
      <div className="section-title-row">
        <h2 id="calendar-heading">{t("calendar.title")}</h2>
        <p>{t("calendar.subtitle")}</p>
      </div>

      <div className="calendar-scroll" tabIndex={0} role="region" aria-label={t("calendar.title")}>
        <div className="calendar-sheet">
          <div className="cal-row cal-head" aria-hidden="true">
            <span />
            {short.map((month) => <span key={month}>{month}</span>)}
          </div>

          <table className="cal-risk">
            <caption>{t("calendar.risk_title", "Climate odds by month, 2000 to 2025")}</caption>
            <thead className="sr-only"><tr><th scope="col" />{long.map((month) => <th scope="col" key={month}>{month}</th>)}</tr></thead>
            <tbody>
              {risks.map((risk) => (
                <tr key={risk.key} className={`cal-row risk-${risk.key}`}>
                  <th scope="row">
                    {risk.label}
                    <small>{risk.kind === "odds" ? t("calendar.years_in_10", "years in 10") : t("calendar.days_per_month", "days a month")}</small>
                  </th>
                  {calendar.climate_risk.map((month) => {
                    const v = risk.value(month);
                    const share = risk.kind === "odds" ? v : v / maxDays[risk.key as "storm" | "wind"];
                    const shown = risk.kind === "odds" ? String(odds(v)) : oneDecimal.format(v);
                    return (
                      <td key={month.month} style={{ "--p": share.toFixed(2) } as React.CSSProperties}>
                        {shown}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>

          {blocks.map((block) => (
            <div className="cal-block" key={block.rotation_id} role="group" aria-label={loc(ui.cardText.rotations[block.rotation_id]?.name, lang)}>
              <h3 className="cal-block-title">
                <i className={block.rotation_id === "R0" ? "dashed" : ""} style={{ "--key": `var(--rot-${block.rotation_id})` } as React.CSSProperties} aria-hidden="true" />
                {loc(ui.cardText.rotations[block.rotation_id]?.name, lang) || block.rotation_id}
              </h3>
              {block.years.map((year) => (
                <div className="cal-row cal-year" key={year.year_index}>
                  <span className="cal-year-label">
                    <b>{t("calendar.year", "Year")} {year.year_index}</b>
                    <span>{rowCrops(year.months)}</span>
                  </span>
                  {year.months.map((cell, m) => {
                    const risk = calendar.climate_risk[m];
                    const parts = [
                      `${long[m]}, ${t("calendar.year", "Year")} ${year.year_index}`,
                      isBare(cell.state) ? t("calendar.bare") : cropLabel(ui, cell.state),
                      stageLabel(cell.stage),
                      ...cell.flags.map((flag) => t(`calendar.flag.${flag}`)),
                      risk ? interpolate(t("calendar.odds", "{risk}: {count} of 10 years"), { risk: t("calendar.flag.heat"), count: odds(risk.p_heat) }) : "",
                    ].filter(Boolean);
                    const bare = isBare(cell.state);
                    return (
                      <span
                        key={m}
                        className={`cal-cell ${bare ? "bare" : "occupied"}`}
                        title={parts.join(" · ")}
                        aria-label={parts.join(" · ")}
                        role="img"
                        style={bare ? undefined : ({ "--cell-color": cropColor(cell.state) } as React.CSSProperties)}
                      >
                        {cell.flags.slice(0, 2).map((flag) => {
                          const Icon = flagIcon[flag];
                          return <Icon key={flag} size={13} strokeWidth={2.25} color={flagColor[flag]} aria-hidden="true" />;
                        })}
                      </span>
                    );
                  })}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="calendar-legend">
        <span><i className="legend-crop" style={{ "--cell-color": cropColor("corn") } as React.CSSProperties} />{t("calendar.crop_period", "Crop in the field")}</span>
        <span><i className="legend-crop bare" />{t("calendar.bare")}</span>
        {FLAGS.map((flag) => {
          const Icon = flagIcon[flag];
          return <span key={flag}><Icon size={15} strokeWidth={2.25} color={flagColor[flag]} aria-hidden="true" /> {t(`calendar.flag.${flag}`)}</span>;
        })}
      </div>
    </section>
  );
}
