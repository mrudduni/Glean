"use client";

import { FieldMap, type MapLegendItem, type MapNeighbor } from "@/components/FieldMap";
import { SourceChips } from "@/components/SourceChips";
import type { Field, NeighborsFile, RotationClass } from "@/lib/types";
import { formatVar, interpolate, loc } from "@/lib/i18n";
import { kindColors, theme } from "@/lib/theme";
import { ROTATION_CLASS_LABEL, type UI } from "@/lib/ui";

const UNMATCHED = "#b8bab2";

export function NeighborsView({ neighbors, field, ui }: { neighbors: NeighborsFile | null; field: Field; ui: UI }) {
  const { t, lang } = ui;
  const heading = (
    <div className="section-title-row">
      <h2 id="neighbors-heading">{t("neighbors.title")}</h2>
      <p>{t("neighbors.subtitle")}</p>
    </div>
  );
  if (!neighbors) {
    return (
      <section className="workspace-section neighbors-section" id="neighbors" aria-labelledby="neighbors-heading">
        {heading}
        <p className="empty-state">{t("section.not_available", "Not available for this field yet.")}</p>
      </section>
    );
  }

  // The group farmed like this field is drawn in the current-rotation colour (R0); other groups in their rotation's colour.
  const colourId = (group: NeighborsFile["groups"][number]) => (group.is_current ? "R0" : group.matches_rotation);
  const matchFor = new Map<RotationClass, string | null>(neighbors.groups.map((group) => [group.rotation_class, colourId(group)]));
  const className = (rc: RotationClass) => t(`rotation_class.${rc}`, ROTATION_CLASS_LABEL[rc]);
  const groupName = (rc: RotationClass, rid: string | null) => (rid ? loc(ui.cardText.rotations[rid as keyof typeof ui.cardText.rotations]?.name, lang) : "") || className(rc);
  const pct = (value: number | null) => (value === null ? "—" : formatVar("drop_pct", value, lang));
  const percent = (value: number) => Math.round(value * 100);

  const mapNeighbors: MapNeighbor[] = neighbors.fields.map((item) => {
    const rid = matchFor.get(item.rotation_class);
    return {
      ...item,
      color: rid ? theme.rot[rid] : undefined,
      label: `${groupName(item.rotation_class, rid && rid !== "R0" ? rid : null)} · ${interpolate(t("neighbors.similarity", "{pct}% similar"), { pct: percent(item.similarity) })}`,
    };
  });
  const legend: MapLegendItem[] = [
    { color: kindColors[field.kind], label: t("neighbors.your_field", "Your field") },
    ...neighbors.groups
      .filter((group) => colourId(group))
      .map((group) => ({ color: theme.rot[colourId(group) as string] ?? UNMATCHED, label: groupName(group.rotation_class, group.matches_rotation) })),
  ];
  // Drought greenness columns only appear when the data has them.
  const has2012 = neighbors.groups.some((group) => group.ndvi_drop_2012_pct !== null);
  const has2022 = neighbors.groups.some((group) => group.ndvi_drop_2022_pct !== null);

  return (
    <section className="workspace-section neighbors-section" id="neighbors" aria-labelledby="neighbors-heading">
      {heading}
      <div className="neighbors-grid">
        <div className="neighbors-map">
          <FieldMap fields={[field]} neighbors={mapNeighbors} selected={field.id} t={t} lang={lang} legend={legend} />
          <p className="map-caption">
            {interpolate(t("neighbors.matched_count", "{matched} of {pool} nearby fields match on soil and irrigation."), { matched: neighbors.matched, pool: neighbors.pool_size })}
          </p>
        </div>
        <div className="neighbors-table-wrap">
          <table className="neighbors-table">
            <caption className="sr-only">{t("neighbors.title")}</caption>
            <thead>
              <tr>
                <th scope="col">{t("neighbors.rotation", "Rotation")}</th>
                <th scope="col">{t("neighbors.fields_header", "Nearby fields")}</th>
                <th scope="col">{t("neighbors.water_use")}</th>
                {has2012 && <th scope="col">{t("neighbors.drought_greenness")} 2012</th>}
                {has2022 && <th scope="col">{t("neighbors.drought_greenness")} 2022</th>}
              </tr>
            </thead>
            <tbody>
              {neighbors.groups.map((group) => (
                <tr className={group.is_current ? "current-neighbor" : ""} key={group.rotation_class}>
                  <th scope="row">
                    <span className="neighbor-name">
                      <i style={{ background: colourId(group) ? `var(--rot-${colourId(group)})` : UNMATCHED }} aria-hidden="true" />
                      {groupName(group.rotation_class, group.matches_rotation)}
                    </span>
                    {group.is_current && <small>{t("neighbors.like_yours", "Like yours")}</small>}
                  </th>
                  <td>{formatVar("n", group.n, lang)}</td>
                  <td>{group.et_mm_yr_median === null ? "—" : formatVar("et_mm", group.et_mm_yr_median, lang)}</td>
                  {has2012 && <td>{pct(group.ndvi_drop_2012_pct)}</td>}
                  {has2022 && <td>{pct(group.ndvi_drop_2022_pct)}</td>}
                </tr>
              ))}
            </tbody>
          </table>
          {!has2012 && !has2022 && <p className="micro-note">{t("neighbors.no_greenness", "Drought-year greenness (MODIS) is not available for these fields yet.")}</p>}
          <p className="neighbors-disclaimer">{t("neighbors.disclaimer")}</p>
          <details className="neighbors-method">
            <summary>{t("neighbors.method", "How these fields were matched")}</summary>
            <p>{neighbors.method.note}</p>
          </details>
          <SourceChips tags={["CSB", "SSURGO", "OpenET", "MODIS"]} sources={ui.sources} />
        </div>
      </div>
    </section>
  );
}
