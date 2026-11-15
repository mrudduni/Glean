"use client";

import { Info } from "lucide-react";
import { FieldMap, type MapNeighbor } from "@/components/FieldMap";
import { SourceChips } from "@/components/SourceChips";
import type { Field, NeighborsFile, RotationClass } from "@/lib/types";
import { formatVar, interpolate, loc } from "@/lib/i18n";
import { theme } from "@/lib/theme";
import { ROTATION_CLASS_LABEL, type UI } from "@/lib/ui";

export function NeighborsView({ neighbors, field, ui }: { neighbors: NeighborsFile | null; field: Field; ui: UI }) {
  const { t, lang } = ui;
  const heading = (
    <div className="section-title-row">
      <div>
        <h2 id="neighbors-heading">{t("neighbors.title")}</h2>
        <p>{t("neighbors.subtitle")}</p>
      </div>
    </div>
  );
  if (!neighbors) {
    return (
      <section className="workspace-section neighbors-section" id="neighbors" aria-labelledby="neighbors-heading">
        {heading}
        <div className="empty-state"><Info size={16} aria-hidden="true" />{t("section.not_available", "Not available for this field yet.")}</div>
      </section>
    );
  }
  const matchFor = new Map<RotationClass, string | null>(neighbors.groups.map((group) => [group.rotation_class, group.matches_rotation]));
  const mapNeighbors: MapNeighbor[] = neighbors.fields.map((item) => {
    const rid = matchFor.get(item.rotation_class);
    return { ...item, color: rid ? theme.rot[rid] : "#b8bab2" };
  });
  const className = (rc: RotationClass) => t(`rotation_class.${rc}`, ROTATION_CLASS_LABEL[rc]);
  const pct = (value: number | null) => (value === null ? "—" : formatVar("drop_pct", value, lang));

  return (
    <section className="workspace-section neighbors-section" id="neighbors" aria-labelledby="neighbors-heading">
      {heading}
      <div className="neighbors-grid">
        <div className="neighbors-map">
          <FieldMap fields={[field]} neighbors={mapNeighbors} selected={field.id} t={t} lang={lang} />
          <p className="map-caption">
            {neighbors.matched} / {neighbors.pool_size} {t("neighbors.matched_note", "nearby fields matched on soil and irrigation")}
          </p>
        </div>
        <div className="neighbors-table-wrap">
          <table className="neighbors-table">
            <thead>
              <tr>
                <th scope="col">{t("neighbors.rotation", "Rotation")}</th>
                <th scope="col">{t("neighbors.fields_header", "Nearby fields")}</th>
                <th scope="col">{t("neighbors.water_use")}</th>
                <th scope="col">{t("neighbors.drought_greenness")} 2012</th>
                <th scope="col">{t("neighbors.drought_greenness")} 2022</th>
              </tr>
            </thead>
            <tbody>
              {neighbors.groups.map((group) => (
                <tr className={group.is_current ? "current-neighbor" : ""} key={group.rotation_class}>
                  <th scope="row">
                    <span className="neighbor-rotation" style={{ background: group.matches_rotation ? theme.rot[group.matches_rotation] : "#b8bab2" }}>{group.matches_rotation ?? "—"}</span>
                    {group.matches_rotation ? loc(ui.cardText.rotations[group.matches_rotation]?.name, lang) : className(group.rotation_class)}
                    {group.is_current && <small>{t("neighbors.like_yours", "Like yours")}</small>}
                  </th>
                  <td>{interpolate(t("neighbors.n_fields", "{n} fields"), { n: group.n })}</td>
                  <td>{group.et_mm_yr_median === null ? "—" : formatVar("et_mm", group.et_mm_yr_median, lang)}</td>
                  <td>{pct(group.ndvi_drop_2012_pct)}</td>
                  <td>{pct(group.ndvi_drop_2022_pct)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="neighbors-disclaimer"><Info size={18} aria-hidden="true" /><p>{t("neighbors.disclaimer")}</p></div>
          <p className="micro-note">{neighbors.method.note}</p>
          <SourceChips tags={["CSB", "SSURGO", "OpenET", "MODIS"]} sources={ui.sources} />
        </div>
      </div>
    </section>
  );
}
