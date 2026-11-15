# content/

Farmer-facing text and crop data for Glean.

- `card_text.json`, `copy.json`, `glossary.json`, `assistant_questions.json`: text in English and Spanish. Placeholders and keys follow README sections 7.4 and 8.6 of the team contract.
- `crops.yaml`: crop traits for the model, with sources. Lines marked `# verify` still need a check against K-State or FAO sources.
- `validate.py`: run `python content/validate.py` from the repo root. It checks keys, placeholders, banned words and design tokens.

Content drafts by Himal (branch `himal/content`). Some sentences in `card_text.json` come from those drafts. Final text, crop research, tokens and checks by the U role.
