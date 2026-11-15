# content/ and design/ (role U)

Everything the farmer reads and sees. The formats are fixed by the root [README.md](../README.md) §7.4, §8.5 and §8.6.

| File | What it is | Used by | Status |
|---|---|---|---|
| `card_text.json` | Strategy-card sentences, rotation names, headline and validation text, as templates with `{placeholders}` | F (renders), M (picks the keys) | Draft, EN + ES complete |
| `copy.json` | Every UI label, button and heading | F | Draft, EN + ES complete. `app.name` is a placeholder ("RootCycle") until the team picks a name |
| `glossary.json` | 18 plain-language definitions (ET, NDVI, aquifer…) | F (tooltips, trust page), M (assistant facts) | Draft, EN + ES complete |
| `assistant_questions.json` | The 6 suggested questions in the assistant | F (chips), M (cached answers) | Draft |
| `crops.yaml` | Crop parameters the water model runs on | M | Draft. Lines marked `# verify` still need checking against FAO-56 / FAO-33 / K-State; triticale yield and price are `TODO` |
| `../design/tokens.css` | Colours, fonts, radius as CSS variables | F | Draft, contrast checked |
| `../design/tokens.json` | The same values for chart and map libraries, plus text colour per crop cell | F | Draft, matches tokens.css |
| `../design/wireframes/index.html` | Clickable wireframes of the 5 screens, desktop and phone, with data notes on every element and behaviour notes for F | F | Draft. Open in any browser; sample numbers only |

## Writing rules (short version)

- Plain language, "you / your field", about an 8th-grade reading level.
- "may", "about", "estimated", "in similar fields". Never "will", "guaranteed", "proven".
- **Never type a unit next to a placeholder.** Write `about {saved_mm} of water`; the app renders "about 120 mm (4.7 in) of water".
- Only use placeholders listed for that key in README §8.6.
- Two `copy.json` strings have a placeholder: `card.hidden_count` uses `{n}`.

## Check before handing over

Run from the repo root after any edit:

```bash
py content/check_content.py .
```

It checks every required key exists in both languages, placeholders are allowed and match between English and Spanish, no units are typed next to placeholders, all 9 crops have every field, `tokens.css` and `tokens.json` match, and text and chart colours meet contrast targets.
