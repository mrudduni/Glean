# Model (role M)

Python that turns D's data and U's crop traits into the static JSON the web app reads: crops, rotations, Rotation Replay, Field Calendar, strategy facts, summary and validation. The method, every constant and the validation results are in [docs/METHODS.md](../docs/METHODS.md). The file formats are section 8.4 of [docs/CONTRACT.md](../docs/CONTRACT.md).

## Setup

```bash
py -V:Astral/CPython3.12.13 -m venv model/.venv
```

```bash
model/.venv/Scripts/python -m pip install -r model/requirements.txt
```

On macOS or Linux use `python3.12 -m venv model/.venv` and `model/.venv/bin/python`.

## Run

From the repo root:

```bash
model/.venv/Scripts/python model/run_all.py
```

This runs library, replay, validation, calendar, scoring and summary for f1, f2 and f3 in about a minute. Then it runs the assistant step (`python -m model.assistant`) if `model/assistant/__main__.py` exists. Options: `--fields f1`, `--skip-assistant`.

It writes:

- `model/out/web/crops.json`, `rotations.json`
- `model/out/web/field/{fid}/replay.json`, `strategies.json`, `calendar.json`, `summary.json`, `validation.json`
- `model/out/run_log.json`: diagnostics (yield and price sources, validation details, top 3 per scenario). It is not served.

The assistant files (`assistant/prompt.json`, `field/{fid}/assistant_context.json`, `assistant_cache.json`) come from `model/assistant/`. Until that step runs they are the mocks from `model/mock/make_mocks.py`.

## Inputs and environment variables

| Variable | Default | What |
|---|---|---|
| `DATA_DIR` | `C:/Users/HP/fieldshift-data/data-pipeline/out` | D's `out/` folder (has `processed/` and `web/`). In the merged repo set it to `../data-pipeline/out`. |
| `CONTENT_DIR` | `../content` | U's folder with `crops.yaml` |
| `MODEL_OUT_DIR` | `model/out/web` | where outputs go |

Relative paths resolve from `model/`. Variables can also live in `model/.env` (see `.env.example`). `crops.yaml` is read from `CONTENT_DIR`. If it is not there, the run reads `git show origin/role/content:content/crops.yaml`, then falls back to the vendored snapshot `model/library/default_crops.yaml`. The run prints which one it used.

To run without D's data, point `DATA_DIR` at a folder with the same layout (`processed/{fid}/weather_daily.csv`, `processed/nass.json`, `web/fields.json`, ...). Optional inputs that are missing (IMERG, SMAP, neighbours, observed) are skipped, and those validation items are left out.

## Mocks

```bash
model/.venv/Scripts/python model/mock/make_mocks.py
```

This writes schema-exact mocks of every M file with `_meta.mock: true`. It overwrites `model/out/web/`, so rerun `run_all.py` afterwards.

## Tests

```bash
model/.venv/Scripts/python -m pytest model
```

These cover the handover 5.3 sanity checks on D's real data for all fields (ET0 range, irrigated corn at cap450, fallow benefit for sorghum, hotdry direction, mass balance), the scoring rules, and the contract check on `model/out/web`.

## Integration scripts

```bash
model/.venv/Scripts/python scripts/sync_data.py
```

```bash
model/.venv/Scripts/python scripts/check_contract.py
```

`sync_data.py` copies the CONTRACT 6.5 mapping into `web/`. `check_contract.py` checks `web/public/data` and exits 1 on any error. Use `--allow-mock` to downgrade mock files to warnings, `--only-model --data-dir model/out/web` to check M's files alone, and `--data-dir` to point anywhere else.

## Layout

```text
model/
├─ config.py            every path and constant
├─ contract.py          CONTRACT 8.6 text keys, JSON writer (rejects NaN, _meta first)
├─ inputs.py            readers for D's files
├─ run_all.py
├─ library/             load_crops.py, rotations.py, default_crops.yaml
├─ replay/              et0.py, crop_calendar.py, water_balance.py, economics.py, exposure.py, run.py
├─ calendar/build.py
├─ scoring/             criteria.py, facts.py, summary.py
├─ validate/run.py
├─ mock/make_mocks.py
├─ tests/
└─ out/web/             committed outputs
```

## Notes for F

- R0 can match a library rotation: f2 R0 (wheat-sorghum-fallow) is R2, and f3 R0 (corn-wheat-sorghum) is R1. Their numbers are identical. Consider hiding a library card whose `steps` equal `summary.current_rotation.steps`.
- On f2 (no well) R1, R4 and R5 are infeasible in every scenario. Under default constraints (no hay, no cotton, no forage buyer) R2 is the only alternative left.
- `validation.json` has only the items whose reference data exists. Today that is `et_vs_openet` alone; SMAP and IMERG items appear when D delivers them.
- `rotations.json` includes R6 (could tier); `replay.json`, `strategies.json` and `calendar.json` include R6 for every field.
