# Crop traits and rotation effects

Two tables feed the water balance and the strategy comparison:

- `crop_traits.csv` has one row per crop with FAO-56 coefficients.
- `rotation_effects.csv` has one row per measured effect of a rotation change, with its study design and DOI.

We read the FAO-56 tables in full on 2026-11-14. The rotation effects come from paper abstracts for now; the `read_level` column says so for each row. Step 4 of the research plan upgrades the key rows to full text.

## Crop traits: what each column means

All values come from FAO Irrigation and Drainage Paper 56 (Allen et al., 1998).

| Column | FAO-56 table | Use in the tool |
|---|---|---|
| `kc_ini`, `kc_mid`, `kc_end` | Table 12 | Single crop coefficient. Crop ET equals Kc times reference ET. Table 12 assumes a sub-humid climate (RHmin about 45 percent, wind about 2 m/s). Kc mid and Kc end need the climate adjustment in FAO-56 equation 62. |
| `max_height_m` | Table 12 | Input to that climate adjustment. |
| `root_depth_min_m`, `root_depth_max_m` | Table 22 | Sets total available water in the root zone. The larger value applies to deep, free soils. |
| `p_depletion` | Table 22 | Share of total available water the crop can use before stress starts. FAO gives it for ET of about 5 mm per day and adjusts it with p = p_table + 0.04 (5 - ETc). |
| `ky_seasonal` | Table 24 (from FAO-33) | Yield response to water stress: relative yield loss equals Ky times relative ET deficit. |
| `ece_threshold_ds_m`, `ece_slope_pct_per_ds_m`, `salt_rating` | Table 23 | Soil salinity threshold where yield starts to drop, and the percent loss per extra dS/m. Ratings run S, MS, MT, T (sensitive to tolerant). |
| `l_ini_d` to `l_total_d` | Table 11 | Days in each growth stage for one FAO example region and planting date. |

Where Table 12 gives no Kc ini for a single crop, FAO uses a group value. The CSV shows it as, for example, "0.3 (cereal group)". The tool should compute Kc ini from wetting frequency (FAO-56 Figures 29 and 30) instead of using the group value.

Footnote digits stick to numbers in the FAO web tables. For example, "0.9513" in the web text is 0.95 with footnote 13. We removed these by hand and checked each against the table layout.

## Answers to open questions

**Alfalfa Kc.** FAO-56 Table 12 gives two sets for alfalfa hay. Averaged over cuttings: Kc ini 0.40, Kc mid 0.95, Kc end 0.90. For each cutting period: 0.40, 1.20, 1.15. Use the per-cutting set when the model tracks cuts, which is the better choice for a daily water balance. Table 11 gives 30 to 75 days per cutting cycle.

**Mustard.** FAO-56 has no row for Indian mustard (Brassica juncea). The closest row is "Rapeseed, Canola": Kc mid 1.0 to 1.15, Kc end 0.35, root depth 1.0 to 1.5 m, p 0.60. FAO-56 gives no stage lengths or salinity values for it. Before we show mustard numbers to a farmer, we need an Indian source for stage lengths and water use (for example ICAR-DRMR). This is an open gap.

**Rice p value.** Table 22 gives rice p as 0.20 of saturation, not of total available water. Paddy needs a separate ponded water balance. A plain FAO-56 bucket model will be wrong for flooded rice.

**Rice Ky.** FAO-56 Table 24 lists no Ky for rice. AquaCrop has a rice crop file, which is the better route for rice yield under stress.

## Rotation effects: what the evidence says for Haryana

Seven trials in Karnal, Haryana and nearby districts compared rice-wheat with maize-based systems. They agree on direction and roughly on size.

| Finding | Range across studies | Rows |
|---|---|---|
| Irrigation water saved by replacing rice with maize | 64 to 95 percent, depending on the mungbean phase and tillage | in01, in05, in08, in14, in19, in20, in22 |
| Net returns or profitability | +16 to +84 percent | in03, in06, in11, in12, in15, in18, in21 |
| Rice-equivalent yield of maize compared with rice | -6.6 percent (on-farm) | in09 |
| Wheat yield after maize compared with wheat after rice | +16.7 percent (on-farm) | in10 |
| Baseline irrigation of conventional rice-wheat | 1,889 to 2,514 mm per year | in04, in20 |

Points the tool must show with these numbers:

1. Most figures come from research station plots that also used conservation agriculture (zero till, residue, beds). Part of the gain comes from those practices, not only from the crop switch. The tool should keep "change the crop" and "change the practice" as separate levers.
2. The one large on-farm study (in09 to in13) found smaller profit gains in Punjab (+32.5 percent) than in Haryana (+46.5 percent). Free farm electricity changes the result: profit gain fell to 6.2 percent in Punjab under subsidised power.
3. Every study names the same barrier: no assured public procurement for maize. The tool should flag market risk for any maize strategy. Our news file already records that HAFED bought no maize at MSP from 2022-23 to 2024-25.
4. Direct-seeded rice lost 11 to 30 percent of yield in years 4 and 5 of one trial (in16), after good early years. Short trials can mislead, so the tool should prefer multi-year evidence.

These numbers support Parisha's "about 80 percent less irrigation" claim for maize, with two limits. The claim holds for irrigation water, not total crop water use, and it comes mainly from station trials with conservation practices.

## US rows

The US rows (us01 to us06) repeat values from `agronomy_rotations.md` so the engine reads one table. That file has the full discussion.

## Gaps

- Mustard stage lengths, water use, and salinity tolerance from an Indian source.
- Chickpea stage lengths and salinity tolerance.
- Pearl millet Ky.
- GDD base temperatures and season GDD totals by crop. Parisha's figure of 1,800 to 2,200 GDD for wheat is still unchecked.
- Full-text reads of in01 to in22 to get per-crop irrigation in mm, not only percent changes.

## Sources

- FAO-56 Chapter 6, Tables 11 and 12: https://www.fao.org/4/x0490e/x0490e0b.htm
- FAO-56 Chapter 8, Tables 22, 23 and 24: https://www.fao.org/4/x0490e/x0490e0e.htm
- Jat et al. 2019, Scientific Reports: https://doi.org/10.1038/s41598-019-54086-1
- Jat et al. 2020, Scientific Reports: https://doi.org/10.1038/s41598-020-76035-z
- Jat et al. 2025, Frontiers in Sustainable Food Systems: https://doi.org/10.3389/fsufs.2025.1700854
- Kumar et al. 2017, Agriculture, Ecosystems and Environment: https://doi.org/10.1016/j.agee.2017.10.006
- Choudhary et al. 2018, Field Crops Research: https://doi.org/10.1016/j.fcr.2017.12.023
- Gathala et al. 2013, Agriculture, Ecosystems and Environment: https://doi.org/10.1016/j.agee.2013.06.002
- Gora et al. 2022, Scientific Reports: https://doi.org/10.1038/s41598-022-18156-1
- US sources are listed in `agronomy_rotations.md`.
