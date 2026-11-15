# UI/UX polish checklist

Branch `role/web-ui-polish`, cut from `origin/main` at `6de2157`. Scope **B**: fix the audit findings and bring the layout back to `design/wireframes/index.html`, inside `web/` only, using the existing tokens in `web/styles/tokens.css`.

Each item names its audit ID. Ticked items are committed and checked with `npm test`, `npm run typecheck` and `npm run build`.

## Direction

"Survey sheet, not SaaS." The only image is the real satellite basemap (pivot circles inside section squares). Everything else is quiet: token ink on the token background, one accent (token blue, read as water), crop colours only where they mean a crop, hairline rules shared by the calendar, charts and map. Fraunces only for the field name and page titles; Source Sans 3 for the rest; tabular figures on every number; IBM Plex Mono only for source tags.

## P0

- [x] **#1** Assistant drawer renders above the site header (portal); title and close button visible on desktop and phone
- [x] **#2** Cached answers flag when they were written for a different set of cards than the ones on screen

## Remove the generic chrome

- [x] **#7** No cursor glow, drifting orbs, particle canvas, fake "live" dot, pulsing assistant button or decorative blur
- [x] **#8** No eyebrow kicker above every heading, no `0N / 06` counters, no `01 02 03` numbering on non-sequences
- [ ] **#8b** Strategies is in the section nav (lands with #5, where priorities and cards merge)

## Foundation

- [ ] **#10** Styles read only token variables; dark mode comes from the token swap, not a second hand-written stylesheet
  - [x] Foundation: `styles/base.css` (type scale, text/rule ramp, header, footer, buttons, chips, badges, form controls, states)
  - [x] Home + map (`styles/home.css`, `styles/map.css`) · [ ] Field workspace · [ ] Overview · [ ] Calendar · [ ] Cards · [ ] Replay · [ ] Neighbours · [ ] Assistant · [ ] How we know
- [ ] **#11** Text meets WCAG AA (4.5:1) in light and dark; labels ≥ 14px, body 16px
- [x] **#15** Tabular figures on every number (set once on `body`)

## Layout (wireframes)

- [x] **#9** Home: the map is the hero, zoomed to the three fields with thick labelled outlines; one field list; no stats panel
- [ ] **#4** Field page: headline facts and the best-fit summary sit in the masthead, above the fold
- [ ] **#5** Priorities sit in a sticky rail beside the strategy cards, so a slider change visibly re-ranks them; collapsible on phones
- [ ] **#6** Strategy cards: caveats shared by every card shown once; evidence collapsed; crop sequence as coloured blocks with arrows
- [ ] **#17** Rotation names lead; R-codes are secondary

## Charts and data

- [ ] **#3** Replay: straight lines, theme-aware colours, direct end labels, neutral drought bands with labels
- [ ] **#12** Calendar: rotations stacked so none hide off-screen; readable risk strip; legend instead of two-letter codes
- [ ] **#16** Farms like yours: map zooms to matched fields; readable tooltips and table
- [x] **#14** Assistant: verified-number mark stays inline

## Copy, states, i18n

- [ ] **#13** Plural-aware `fill()` (F side); wording issues reported to U
- [ ] **#18** Loading skeleton shaped like the page; errors in plain words
- [ ] **#20** No hard-coded English in TSX; numbers formatted per language
- [ ] **#21** Well trend states direction; units never wrap
- [ ] **#22** Disclaimer shown once per page
- [ ] **#23** How-we-know: validation as a readable table

## Verification

- [ ] Before/after screenshots at 1440, 768 and 375, light and dark
- [ ] Keyboard run-through: section nav, sliders, toggles, drawer (focus trap, Escape)
- [ ] `prefers-reduced-motion` honoured

## Not changed here (owner decisions or other folders)

- **Mock banner** is switched off on `main` ("suppressed per production requirements"); left as is.
- **M** (`model/`): `assistant_cache.json` was generated for top order R4, R5, R1, R0, but the default cards are R0, R5, R1, R2. Rebuild for the default order; round numbers such as 75.43.
- **D** (`data-pipeline/`): `neighbors.json` NDVI drought columns are all null.
- **U** (`content/`, `design/`): "changed by −3 days a year" is a period difference, not a rate; "−0.9 cm/yr a year" doubles the unit; plural workarounds read robotic ("in years: 1"); criterion label "Heat and frost risk" reads backwards (100 = least risk); `web/styles/tokens.css` has drifted from `design/tokens.css` (dark muted text #eaf3ed is nearly the body colour).
