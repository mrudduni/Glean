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

export function FieldCalendar({ calendar, order, ui }: { calendar: CalendarFile; order: RotationId[]; ui: UI }) {
  const { t, lang } = ui;
  const short = monthNames(lang, "short");
  const long = monthNames(lang, "long");
  const oneDecimal = new Intl.NumberFormat(lang === "es" ? "es-ES" : "en-US", { maximumFractionDigits: 1 });
  const days = (value: number) => oneDecimal.format(value);
  const blocks = order
    .map((id) => calendar.rotations.find((rotation) => rotation.rotation_id === id))
    .filter((block): block is CalendarFile["rotations"][number] => Boolean(block));
  const odds = (p: number) => Math.round(p * 10);
  const stageLabel = (stage: CalendarCell["stage"]) => (stage ? t(`calendar.stage.${stage}`, { ini: "Establishing", dev: "Growing", mid: "Peak growth", late: "Ripening" }[stage]) : "");

  return (
    <section className="workspace-section calendar-section" id="calendar" aria-labelledby="calendar-heading">
      <div className="section-title-row">
        <div>
          <h2 id="calendar-heading">{t("calendar.title")}</h2>
          <p>{t("calendar.subtitle")}</p>
        </div>
      </div>

      <div className="calendar-scroll">
        <div className="climate-risk-strip">
          <div className="climate-strip-title">
            <span>{t("calendar.risk_title", "Climate odds by month, 2000 to 2025")}</span>
          </div>
          <div className="climate-months">
            {calendar.climate_risk.map((risk) => {
              const m = risk.month - 1;
              const title = [
                interpolate(t("calendar.odds", "{risk}: {count} of 10 years"), { risk: t("calendar.flag.heat"), count: odds(risk.p_heat) }),
                interpolate(t("calendar.odds", "{risk}: {count} of 10 years"), { risk: t("calendar.flag.frost"), count: odds(risk.p_frost) }),
                interpolate(t("calendar.odds", "{risk}: {count} of 10 years"), { risk: t("calendar.flag.dry"), count: odds(risk.p_dry_spell) }),
                `${t("calendar.storm_days", "Storm days")}: ${days(risk.storm_days)}`,
                `${t("calendar.windy_days", "Windy days")}: ${days(risk.windy_days)}`,
              ].join(". ");
              return (
                <div className="climate-month" key={risk.month} title={`${long[m]}. ${title}`} aria-label={`${long[m]}. ${title}`} role="img">
                  <span>{short[m]}</span>
                  <i className="risk-meter heat-meter" style={{ "--meter-value": `${risk.p_heat * 100}%` } as React.CSSProperties} />
                  <i className="risk-meter frost-meter" style={{ "--meter-value": `${risk.p_frost * 100}%` } as React.CSSProperties} />
                  <i className="risk-meter dry-meter" style={{ "--meter-value": `${risk.p_dry_spell * 100}%` } as React.CSSProperties} />
                  <span className="risk-counts">{days(risk.storm_days)}·{days(risk.windy_days)}</span>
                </div>
              );
            })}
          </div>
          <div className="risk-strip-legend">
            <span><i className="legend-risk heat" />{t("calendar.flag.heat")}</span>
            <span><i className="legend-risk frost" />{t("calendar.flag.frost")}</span>
            <span><i className="legend-risk dry" />{t("calendar.flag.dry")}</span>
            <span>{t("calendar.counts_legend", "Numbers: storm days · windy days")}</span>
          </div>
        </div>

        <div className="calendar-blocks">
          {blocks.map((block) => (
            <article className="calendar-block" key={block.rotation_id}>
              <header className="calendar-block-heading">
                <span className="rotation-id">{block.rotation_id}</span>
                <span>{loc(ui.cardText.rotations[block.rotation_id]?.name, lang)}</span>
                {block.rotation_id === "R0" && <small>{t("card.current_badge")}</small>}
              </header>
              <div className="calendar-month-head" aria-hidden="true">
                <span>{t("calendar.year", "Year")}</span>
                {short.map((month) => <span key={month}>{month}</span>)}
              </div>
              {block.years.map((year) => (
                <div className="calendar-row" key={year.year_index}>
                  <span className="calendar-year">{String(year.year_index).padStart(2, "0")}</span>
                  {year.months.map((cell, m) => {
                    const risk = calendar.climate_risk[m];
                    const parts = [
                      `${long[m]}, ${t("calendar.year", "Year")} ${year.year_index}`,
                      cropLabel(ui, cell.state),
                      stageLabel(cell.stage),
                      ...cell.flags.map((flag) => t(`calendar.flag.${flag}`)),
                      risk ? interpolate(t("calendar.odds", "{risk}: {count} of 10 years"), { risk: t("calendar.flag.heat"), count: odds(risk.p_heat) }) : "",
                    ].filter(Boolean);
                    const bare = cell.state === "bare" || cell.state === "fallow";
                    return (
                      <span
                        key={m}
                        className={`calendar-cell ${bare ? "bare" : "occupied"}`}
                        title={parts.join(" · ")}
                        aria-label={parts.join(" · ")}
                        role="img"
                        style={bare ? undefined : ({ "--cell-color": cropColor(cell.state) } as React.CSSProperties)}
                      >
                        {!bare && <span className="cell-crop" aria-hidden="true">{cropLabel(ui, cell.state).slice(0, 2)}</span>}
                        <span className="cell-flags" aria-hidden="true">
                          {cell.flags.slice(0, 2).map((flag) => {
                            const Icon = flagIcon[flag];
                            return <Icon key={flag} size={11} color={flagColor[flag]} />;
                          })}
                        </span>
                      </span>
                    );
                  })}
                </div>
              ))}
            </article>
          ))}
        </div>
      </div>
      <div className="calendar-legend">
        <span><i className="legend-crop" style={{ "--cell-color": cropColor("corn") } as React.CSSProperties} />{t("calendar.crop_period", "Crop in the field")}</span>
        <span><i className="legend-crop bare-legend" />{t("calendar.bare")}</span>
        {FLAGS.map((flag) => {
          const Icon = flagIcon[flag];
          return <span key={flag}><Icon size={15} color={flagColor[flag]} aria-hidden="true" /> {t(`calendar.flag.${flag}`)}</span>;
        })}
      </div>
    </section>
  );
}
