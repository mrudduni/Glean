# Data probe results

The phase 2 probe agents ran live calls on 2026-11-14. We stopped them early to save usage, so the full written reports were never finished. This folder keeps everything they saved: the probe scripts in `scripts/` and the raw responses in `samples/`. Every sample is a real API response, cut to under 100 KB.

## Status by probe

| Probe | Saved | Missing |
|---|---|---|
| NASA catalog (POWER, CMR, AppEEARS, GIBS, earthaccess) | `scripts/probe_nasa.py` and 20 samples, including the 53-collection CMR table below | The written report and the "corrections to phase 1" list |
| US agriculture APIs (SDA, CropScape, NASS, OpenET, USGS, PRISM, GAEZ, AMS) | `samples/probe_cdl_result.json` only | Script, SDA queries, and the report. Rerun this probe with a small scoped agent |
| Global and India (SoilGrids, Open-Meteo, CHIRPS, WorldCereal, FAOSTAT, WFP) | `scripts/probe_global.py`, FAOSTAT and WFP price samples, Open-Meteo, FAO crop calendar, `global_probe_results.json`. The `india` and `soilgrids_rest` probes ran on 2026-11-14 and are written up in `01_datasets/global/` and `01_datasets/india/`. | The `soilgrids_wcs` and `ssurgo_iowa` probes have not run |

## NASA collections confirmed in CMR

Pulled from `samples/cmr_collections_summary.json`. The last column counts granules over study point S1 (central Iowa, 42.03 N, 93.75 W) in 2024. The query URLs are in `samples/cmr_query_urls.txt`.

| Group | Short name | Version | Concept ID | Cloud | Start | End | Resolution | Format | Granules S1 2024 |
|---|---|---|---|---|---|---|---|---|---|
| SMAP | `SPL3SMP_E` | 006 | `C2938664763-NSIDC_CPRD` | yes | 2015-03-31 | ongoing | 9.0 Kilometers | HDF5 | 366 |
| SMAP | `SPL4SMGP` | 008 | `C3480440870-NSIDC_CPRD` | yes | 2015-03-31 | ongoing | 9.0 Kilometers | HDF5 | 2936 |
| SMAP | `SPL2SMP_E` | 006 | `C2938663676-NSIDC_CPRD` | yes | 2015-03-31 | ongoing | 9.0 Kilometers | HDF5 | 365 |
| SMAP | `SPL2SMAP_S` | 003 | `C2938663471-NSIDC_CPRD` | yes | 2015-03-31 | ongoing | 3.0 Kilometers | HDF5 | 49 |
| SMAP | `SPL3SMP` | 009 | `C2938664585-NSIDC_CPRD` | yes | 2015-03-31 | ongoing | 36.0 Kilometers | HDF5 | 366 |
| IMERG | `GPM_3IMERGDF` | 07 | `C2723754864-GES_DISC` | yes | 1998-01-01 | 2025-09-30 |  |  | 366 |
| IMERG | `GPM_3IMERGDL` | 07 | `C2723754859-GES_DISC` | yes | 1998-01-01 | ongoing |  |  | 366 |
| IMERG | `GPM_3IMERGDE` | 07 | `C2723754850-GES_DISC` | yes | 1998-01-01 | ongoing |  |  | 366 |
| IMERG | `GPM_3IMERGM` | 07 | `C2723754851-GES_DISC` | yes | 1998-01-01 | 2025-09-30 |  |  | 12 |
| HLS | `HLSL30` | 2.0 | `C2021957657-LPCLOUD` | yes | 2013-04-11 | ongoing | 30 Meters | COG | 70 |
| HLS | `HLSS30` | 2.0 | `C2021957295-LPCLOUD` | yes | 2015-11-28 | ongoing | 30 Meters | COG | 114 |
| HLS | `HLSL30_VI` | 2.0 | `C3246892554-LPCLOUD` | yes | 2013-04-11 | ongoing | 30 Meters | COG | 70 |
| HLS | `HLSS30_VI` | 2.0 | `C3246894861-LPCLOUD` | yes | 2015-11-28 | ongoing | 30 Meters | COG | 113 |
| Landsat | `Landsat Level-2 Surface Reflectance Collection 2` | Collection 2 | `C3442503899-USGS_EROS` | no | 1982-08-22 | ongoing |  | GeoTIFF | 0 |
| Landsat | `Landsat Level-2 Surface Temperature Collection 2` | Collection 2 | `C3442506077-USGS_EROS` | no | 1982-08-22 | ongoing |  | GeoTIFF | 0 |
| MODIS | `MOD13Q1` | 061 | `C1748066515-LPCLOUD` | yes | 2000-02-18 | ongoing | 250 Meters | HDF-EOS2 | 24 |
| MODIS | `MYD13Q1` | 061 | `C2307290656-LPCLOUD` | yes | 2002-07-04 | ongoing | 250 Meters | HDF-EOS2 | 24 |
| MODIS | `MOD16A2GF` | 061 | `C2565791021-LPCLOUD` | yes | 2000-01-01 | ongoing | 500 Meters | HDF-EOS2 | 46 |
| MODIS | `MOD16A2` | 061 | `C2343113232-LPCLOUD` | yes | 2021-01-01 | ongoing | 500 Meters | HDF-EOS2 | 46 |
| MODIS | `MOD11A2` | 061 | `C2269056084-LPCLOUD` | yes | 2000-02-18 | ongoing | 1000 Meters | HDF-EOS2 | 46 |
| MODIS | `MCD12Q1` | 061 | `C2484079608-LPCLOUD` | yes | 2001-01-01 | ongoing | 500 Meters | HDF-EOS2 | 1 |
| VIIRS | `VNP13A1` | 002 | `C2519127224-LPCLOUD` | yes | 2012-01-17 | ongoing | 500 Meters | HDF-EOS5 | 48 |
| VIIRS | `VJ113A1` | 002 | `C2519122065-LPCLOUD` | yes | 2018-01-01 | ongoing | 500 Meters | HDF-EOS5 | 48 |
| VIIRS | `VNP21A2` | 002 | `C2545314562-LPCLOUD` | yes | 2012-01-17 | ongoing | 1000 Meters | HDF-EOS5 | 46 |
| VIIRS | `VJ121A2` | 002 | `C2545310897-LPCLOUD` | yes | 2018-01-01 | ongoing | 1000 Meters | HDF-EOS5 | 46 |
| VIIRS | `VNP21A1D` | 002 | `C2545314555-LPCLOUD` | yes | 2012-01-17 | ongoing | 1000 Meters | HDF-EOS5 | 345 |
| ECOSTRESS | `ECO_L2T_LSTE` | 002 | `C2076090826-LPCLOUD` | yes | 2018-07-09 | ongoing | 70 Meters | COG | 167 |
| ECOSTRESS | `ECO_L2T_LSTE` | 003 | `C3998139651-LPCLOUD` | yes | 2018-07-09 | ongoing | 70 Meters | COG | 0 |
| ECOSTRESS | `ECO_L3T_JET` | 002 | `C2076106409-LPCLOUD` | yes | 2018-07-10 | ongoing | 70 Meters | COG | 36 |
| ECOSTRESS | `ECO_L3T_JET` | 003 | `C4057232489-LPCLOUD` | yes | 2018-07-09 | ongoing | 70 Meters | COG | 0 |
| ECOSTRESS | `ECO_L4T_ESI` | 002 | `C2076104650-LPCLOUD` | yes | 2018-07-10 | ongoing | 70 Meters | COG | 36 |
| ECOSTRESS | `ECO_L4T_ESI` | 003 | `C4057232495-LPCLOUD` | yes | 2018-07-09 | ongoing | 70 Meters | COG | 0 |
| ECOSTRESS | `ECO_L4T_WUE` | 002 | `C2076102081-LPCLOUD` | yes | 2018-07-10 | ongoing | 70 Meters | COG | 36 |
| ECOSTRESS | `ECO_L4T_WUE` | 003 | `C4057232498-LPCLOUD` | yes | 2018-07-09 | ongoing | 70 Meters | COG | 0 |
| ECOSTRESS | `ECO_L3T_ET_ALEXI` | 002 | `C2076105456-LPCLOUD` | yes | 2018-07-15 | ongoing | 70 Meters | COG | 0 |
| ECOSTRESS | `ECO_L4T_ESI_ALEXI` | 002 | `C2683463996-LPCLOUD` | yes | 2018-07-15 | ongoing | 70 Meters | COG | 0 |
| GRACE | `TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06.3_V4` | RL06.3Mv04 | `C3195527175-POCLOUD` | yes | 2002-04-04 | ongoing | 0.5 Decimal Degrees | netCDF-4 | 1 |
| GRACE | `TELLUS_GRAC-GRFO_MASCON_GRID_RL06.3_V4` | RL06.3Mv04 | `C3195502222-POCLOUD` | yes | 2002-04-04 | ongoing | 0.5 Decimal Degrees | netCDF-4 | 1 |
| GRACE | `GRACEDADM_CLSM0125US_7D` | 4.0 | `C1993409520-GES_DISC` | yes | 2002-04-01 | ongoing |  |  | 53 |
| GRACE | `GRACEDADM_CLSM025GL_7D` | 3.0 | `C2283200566-GES_DISC` | yes | 2003-02-03 | ongoing |  |  | 53 |
| DEM | `SRTMGL1` | 003 | `C2763266360-LPCLOUD` | yes | 2000-02-11 | 2000-02-21 | 30 Meters | HGT | 0 |
| DEM | `NASADEM_HGT` | 001 | `C2763264762-LPCLOUD` | yes | 2000-02-11 | 2000-02-21 | 30 Meters | HGT | 0 |
| GEDI | `GEDI02_A` | 003 | `C3974616071-LPCLOUD` | yes | 2019-04-04 | ongoing | 25 Meters | HDF5 | 0 |
| GEDI | `GEDI02_A` | 002 | `C2142771958-LPCLOUD` | yes | 2019-04-04 | 2025-07-10 | 25 Meters | HDF5 | 0 |
| GEDI | `GEDI_L4A_AGB_Density_V2_1_2056` | 2.1 | `C2237824918-ORNL_CLOUD` | yes | 2019-04-17 | 2025-07-09 |  | HDF5 | 0 |
| GEDI | `GEDI_L4B_Gridded_Biomass_V2_1_2299` | 2.1 | `C2792577683-ORNL_CLOUD` | yes | 2019-04-18 | 2023-03-16 |  | COG | 0 |
| LDAS | `NLDAS_FORA0125_H` | 2.0 | `C2033151148-GES_DISC` | yes | 1979-01-01 | ongoing | 0.125 Decimal Degrees |  | 8784 |
| LDAS | `NLDAS_NOAH0125_H` | 2.0 | `C2069246977-GES_DISC` | yes | 1979-01-02 | ongoing | 0.125 Decimal Degrees |  | 8784 |
| LDAS | `GLDAS_NOAH025_3H` | 2.1 | `C1342986035-GES_DISC` | yes | 2000-01-01 | ongoing | 0.25 Decimal Degrees |  | 2928 |
| LDAS | `GLDAS_NOAH025_3H` | 2.0 | `C1233767545-GES_DISC` | yes | 1948-01-01 | 2014-12-31 | 0.25 Decimal Degrees |  | 0 |
| LDAS | `GLDAS_NOAH025_M` | 2.1 | `C1342986036-GES_DISC` | yes | 2000-01-01 | ongoing | 0.25 Decimal Degrees |  | 12 |
| LDAS | `GLDAS_NOAH025_M` | 2.0 | `C1233767569-GES_DISC` | yes | 1948-01-01 | 2014-12-31 | 0.25 Decimal Degrees |  | 0 |
| LDAS | `GLDAS_CLSM025_DA1_D` | 2.2 | `C1700900796-GES_DISC` | yes | 2003-02-01 | ongoing | 0.25 Decimal Degrees |  | 366 |

## NASA POWER facts from the probe

- The AG daily parameter list returned 152 parameters in 1.98 seconds, with no rate-limit headers.
- The full probe output, including latency and climatology checks, is in `samples/probe_power_result.json`.

## How to rerun

```bash
python research/04_data_probes/scripts/probe_nasa.py
python research/04_data_probes/scripts/probe_global.py
```

Neither script needs a key. Neither one downloads rasters.
