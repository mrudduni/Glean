# USDA Ag Data Commons

## What it is

The Ag Data Commons is a research data catalog and repository run by the USDA National Agricultural Library (NAL). It holds data produced by research that USDA funds or co-funds. Under the USDA public access rule, every USDA-funded researcher must create a catalog record in the Ag Data Commons that points to the public copy of their data. NAL metadata librarians review each submission before it is published. The repository accepts tabular data, genomic sequences, multimedia, databases, and non-executable software used to process or model data. It does not accept data with personally identifiable information.

The Commons is a catalog of many independent datasets, not one dataset. Spatial and temporal resolution, coverage, and formats differ for each record.

## Datasets relevant to crop rotation, cover crops, and soil health

These records were found through search results that point to agdatacommons.nal.usda.gov. The Ag Data Commons site itself blocked automated fetching during this research, so record details below come from search snippets and partner pages.

| Dataset | What it holds | Source of detail |
| --- | --- | --- |
| Rotational complexity increases cropping system output under poorer growing conditions (code and limited data) | Cross-site analysis from the DRIVES team, which compiled more than 20 long-term cropping systems experiments in North America | Search snippet, record 25943899 |
| North American Project to Evaluate Soil Health Measurements (NAPESHM) | Soil health measurements compiled by the Soil Health Institute from 94 long-term agricultural research sites | Search snippet, record 25632270 |
| Data from: A database for global soil health assessment (SoilHealthDB) | Literature-derived database on cover crops, no-tillage, agroforestry and other conservation practices; 42 soil health indicators and 45 background indicators per the Figshare copy | Search snippets, record 24853500 |
| LTAR Network Standard GIS Data Layers, 2020 version | Site locations, experimental plots, fields, watersheds, eddy flux towers and phenocams for the 18 LTAR sites; DOI 10.15482/USDA.ADC/1521161 | LTAR data access page |
| LTAR Network regions, 2018 version, and LTAR regionalization layers | Three GIS datasets describing agricultural production, environmental impact and rural prosperity regions | LTAR data access page |
| LTAR site data collections | Per-site metadata and data on weather, ecosystem services and conservation at watershed scale | LTAR data access page |

### LTAR network and Common Experiment

The USDA ARS Long-Term Agroecosystem Research (LTAR) network has 18 federal and university sites with an average history of more than 50 years. Its Croplands Common Experiment compares a "business as usual" system with an "aspirational" system at each site (this design detail comes from the published literature and was not confirmed on the fetched pages). A 2024 paper by Liebig and colleagues states that sites using crop rotations should have every rotation phase present every year. LTAR publishes its data through the Ag Data Commons, an Airtable data inventory, the LTAR Open Geo Data Hub, and AgCROS.

### AgCROS

The ARS Agricultural Collaborative Research Outcomes System (AgCROS) is a partner of the Ag Data Commons. It aggregates network datasets including GRACEnet (greenhouse gas and soil carbon), REAP, NUOnet (nutrient uptake), SHAnet (Soil Health Assessment Network) and LTAR.

### SHAPE

The Soil Health Assessment Protocol and Evaluation (SHAPE) is a scoring tool, not a raw dataset. Nunes and colleagues (2021) built it from 14,680 soil organic carbon observations across the United States, and it adjusts scores for soil and climate. A SHAPE data record in the Ag Data Commons was not confirmed in this research.

## Access methods

- Browse and search at https://agdatacommons.nal.usda.gov. No account is needed to view or download data.
- Each record has a DOI and a landing page with file downloads.
- The record URL pattern (`/articles/dataset/<title>/<id>`) matches the Figshare platform. A public Figshare-style REST API for the Ag Data Commons is likely but not confirmed.
- NAL offers a Zotero library of publications that cite Ag Data Commons data.

Example record URL from search results:

```
https://agdatacommons.nal.usda.gov/articles/dataset/North_American_Project_to_Evaluate_Soil_Health_Measurements_Dataset/25632270
```

## Authentication

None for viewing or downloading. An account (Login.gov, USDA eAuth, PIV or CAC) is needed only to submit data. New submitters start with zero storage and must request space from curators.

## License and terms

Licenses are set per record. The NAL guide states that the repository accepts only data intended for public access. A single default license for all records was not confirmed.

## Limitations

- The site returned a bot block to automated fetching, so scripted harvesting may need a slower client or the API.
- Record quality and documentation vary. Many records are plot or site data from research stations, not farm-level data.
- Experimental sites are sparse. Results from a trial may not transfer to a farm with different soil and climate.

## How it plugs into the rotation tool

- Long-term rotation trials (DRIVES, LTAR Common Experiment) give evidence for yield stability and yield effects of more diverse rotations. The tool can cite these when it explains the benefits of a candidate rotation.
- NAPESHM and SoilHealthDB give expected changes in soil organic carbon and other soil health indicators under cover crops and no-till. The tool can use them to estimate soil health benefits and to flag uncertainty.
- LTAR site layers let the tool find the nearest long-term research site to a farm and report how similar its region is.
- The tool should list "no nearby trial" as a data gap when no comparable site exists.

## Sources

- https://www.nal.usda.gov/services/agdatacommons
- https://agdatacommons.nal.usda.gov/ (blocked automated fetch)
- https://ltar.ars.usda.gov/data/data-access/
- https://ltar.ars.usda.gov/research/commonexperiment/
- https://ltar.ars.usda.gov/research/ltar-working-groups/ce-cropland-wg/
- https://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=2802&context=natrespapers
- https://agdatacommons.nal.usda.gov/articles/dataset/Code_and_limited_data_for_Rotational_complexity_increases_cropping_system_output_under_poorer_growing_conditions/25943899
- https://agdatacommons.nal.usda.gov/articles/dataset/North_American_Project_to_Evaluate_Soil_Health_Measurements_Dataset/25632270
- https://agdatacommons.nal.usda.gov/articles/dataset/Data_from_A_database_for_global_soil_health_assessment/24853500
- https://agdatacommons.nal.usda.gov/articles/dataset/The_Long-Term_Agroecosystem_Research_LTAR_Network_Standard_GIS_Data_Layers_2020_version/24854670
- https://figshare.com/articles/dataset/SoilHealthDB/8292176
- https://mssoy.org/sites/default/files/documents/shape-sssaj-june-2021.pdf
