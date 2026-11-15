"use client";

import { Info } from "lucide-react";
import { FieldMap } from "@/components/FieldMap";
import { SourceChips } from "@/components/SourceChips";
import type { CopyFile, Field, FieldsFile, Lang, NeighborsFile, Rotation, SourcesFile } from "@/lib/types";
import { formatVar, t } from "@/lib/i18n";

export function NeighborsView({
  neighbors,
  fields,
  field,
  rotations,
  sources,
  copy,
  lang,
}: {
  neighbors: NeighborsFile | null;
  fields: FieldsFile;
  field: Field;
  rotations: Rotation[];
  sources: SourcesFile;
  copy: CopyFile["strings"];
  lang: Lang;
}) {
  if (!neighbors) {
    return <section className="workspace-section" id="neighbors"><div className="empty-state"><Info size={16} />{t("not_available", copy, lang)}</div></section>;
  }
  const rotationMap = new Map(rotations.map((rotation) => [rotation.id, rotation]));
  return (
    <section className="workspace-section neighbors-section" id="neighbors">
      <div className="section-title-row">
        <div>
          <div className="eyebrow"><span className="eyebrow-rule" /> LEARN FROM THE LANDSCAPE</div>
          <h2>{t("neighbors.title", copy, lang)}</h2>
          <p>{t("neighbors.subtitle", copy, lang)}</p>
        </div>
        <span className="section-index">06 / 06</span>
      </div>
      <div className="neighbors-grid">
        <div className="neighbors-map">
          <FieldMap fields={fields.fields} neighbors={fields.neighbors || []} selected={field.id} />
          <p className="map-caption">{t("neighbors.map_note", copy, lang)}</p>
        </div>
        <div className="neighbors-table-wrap">
          <table className="neighbors-table">
            <thead>
              <tr>
                <th>{t("neighbors.rotation", copy, lang)}</th>
                <th>{t("neighbors.fields", copy, lang)}</th>
                <th>{t("neighbors.et", copy, lang)}</th>
                <th>{t("neighbors.drop12", copy, lang)}</th>
                <th>{t("neighbors.drop22", copy, lang)}</th>
              </tr>
            </thead>
            <tbody>
              {neighbors.groups.map((group) => (
                <tr className={group.is_current ? "current-neighbor" : ""} key={group.rotation_id}>
                  <td><span className="neighbor-rotation">{group.rotation_id}</span>{rotationMap.get(group.rotation_id)?.name[lang] || rotationMap.get(group.rotation_id)?.name.en || group.rotation_id}{group.is_current && <small>{lang === "es" ? "ACTUAL" : "CURRENT"}</small>}</td>
                  <td>{group.n_fields}</td>
                  <td>{formatVar("amount_mm", group.median_et_mm, lang)}</td>
                  <td className={group.drought_greenness.y2012 < 0 ? "negative" : ""}>{(group.drought_greenness.y2012 * 100).toFixed(0)}%</td>
                  <td className={group.drought_greenness.y2022 < 0 ? "negative" : ""}>{(group.drought_greenness.y2022 * 100).toFixed(0)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="neighbors-disclaimer"><Info size={18} /><p>{t("neighbors.disclaimer", copy, lang)}</p></div>
          <SourceChips ids={["MODIS"]} sources={sources} lang={lang} />
        </div>
      </div>
    </section>
  );
}
