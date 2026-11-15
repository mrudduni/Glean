#!/usr/bin/env bash
# Copy the other roles' published web files into public/data and styles.
# Run from web/ after `git fetch origin`. Re-running is safe.
set -euo pipefail

copy() { # branch source destination
  mkdir -p "$(dirname "$3")"
  git show "origin/$1:$2" > "$3"
  echo "$1:$2 -> $3"
}

# D: data pipeline
for f in fields sources; do copy role/data "data-pipeline/out/web/$f.json" "public/data/$f.json"; done
for id in f1 f2 f3; do for f in neighbors observed water; do
  copy role/data "data-pipeline/out/web/field/$id/$f.json" "public/data/field/$id/$f.json"
done; done

# M: model outputs
copy role/model model/out/web/crops.json public/data/crops.json
copy role/model model/out/web/rotations.json public/data/rotations.json
for id in f1 f2 f3; do for f in summary calendar replay strategies validation assistant_context assistant_cache; do
  copy role/model "model/out/web/field/$id/$f.json" "public/data/field/$id/$f.json"
done; done

# M (assistant): the built prompt and the shared number-check cases
copy role/model-assistant model/out/web/assistant/prompt.json public/data/assistant/prompt.json
copy role/model-assistant model/assistant/number_check_cases.json tests/fixtures/number_check_cases.json

# U: content and design tokens
for f in copy card_text glossary assistant_questions; do copy role/content "content/$f.json" "public/data/content/$f.json"; done
copy role/content design/tokens.css styles/tokens.css
copy role/content design/tokens.json styles/tokens.json
