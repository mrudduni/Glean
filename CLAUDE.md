# Field Shift

This repository holds our build for the NASA Space Apps Challenge 2026 problem "Field Shift: Adapting Farms with NASA Data".
Challenge page: https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/

It is a long-running side project and the main portfolio piece for the team. Depth, correctness, and polish matter more than speed.

## The problem in one paragraph

Build a decision-support tool that helps a farmer compare crop-rotation strategies. The tool combines NASA Earth observations (SMAP, GPM/IMERG, Landsat, MODIS/VIIRS, ECOSTRESS, NASA POWER, GRACE/GRACE-FO, SRTM) with soil data, crop traits, and the farmer's own priorities. It compares at least three strategies, one of which is the farmer's current rotation. For each strategy it explains why the tool suggested it, what evidence supports it, what it may gain, where data is missing, and which risks a farmer or agronomist must check locally. The tool supports farmer judgment and never replaces it.

## Where things live

- `research/00_challenge/` holds the official challenge text (Details tab, verbatim) and the Resources tab list.
- `research/01_datasets/` has one file per dataset, split into `nasa/`, `usda_us/`, and `global/`. Each file covers resolution, record length, latency, access method, auth, limits, and its role in the tool.
- `research/02_hackathon/` covers event dates, judging criteria, submission rules, competing teams, and past winners.
- `research/03_domain/` covers existing tools, agronomy facts, science methods, key papers, and open-source libraries.
- `research/INDEX.md` lists every research file with a one-line summary.

Read `research/INDEX.md` before starting design or code work. Read the dataset file before writing code that touches that dataset.

## Working rules

- Writing follows the pstack:unslop rules: sentence-case headings, no em dashes, plain words, active voice, whole sentences. Verbatim quotes of source pages are the only exception.
- Cite a source URL for every agronomic number, dataset spec, or claim the tool shows to a farmer.
- The challenge text says "SI" where most people say AI or ML. Treat the terms as equal.
- Never commit API keys, Earthdata tokens, or `.netrc` files. Keep secrets in a git-ignored `.env`.
- Do not download large raster archives into the repo. Cache data outside version control.

## Hackathon constraints

- The event runs 14 to 15 November 2026. Submission closes 15 November at 23:59 local time.
- Judges score Impact, Creativity, Validity, Relevance, and Presentation from 1 to 5.
- The demo is a video of 30 seconds or less, or at most 7 slides. Going over either limit removes the project from global judging.
- A Global Award requires at least one NASA data source, and the project page must list every source and licence.
- The rules allow AI tools for building, not for coming up with the idea. Generated media needs a watermark.
- The code needs an open-source licence. Apache 2.0 is the default.

Details are in `research/02_hackathon/rules_judging.md`.

## Status

Phase 1 research finished on 2026-11-13. Phase 2 (live data probes, India datasets, full-text papers and news, stack v2) finished on 2026-11-14. Everything is indexed in `research/INDEX.md`. The feature ranking and the hackathon build plan are in `research/07_plan/`. No product code exists yet. Small probe samples are in `research/04_data_probes/samples/`; raw data stays in the cache outside the repo.
