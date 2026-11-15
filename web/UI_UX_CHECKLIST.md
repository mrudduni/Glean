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
- [x] **#8b** Strategies is in the section nav (lands with #5, where priorities and cards merge)

## Foundation

- [x] **#10** Styles read only token variables; dark mode comes from the token swap, not a second hand-written stylesheet
  - [x] Foundation: `styles/base.css` (type scale, text/rule ramp, header, footer, buttons, chips, badges, form controls, states)
  - [x] Home + map (`styles/home.css`, `styles/map.css`) · [x] Field workspace (`styles/workspace.css`) · [x] Overview (`styles/overview.css`) · [x] Calendar (`styles/calendar.css`) · [x] Cards (`styles/cards.css`) · [x] Replay (`styles/replay.css`) · [x] Neighbours (`styles/neighbors.css`) · [x] Assistant (`styles/assistant.css`) · [x] How we know (`styles/trust.css`)
- [x] **#11** Text meets WCAG AA (4.5:1) in light and dark; labels ≥ 14px, body 16px (only the Leaflet attribution control is smaller)
- [x] **#15** Tabular figures on every number (set once on `body`)

## Layout (wireframes)

- [x] **#9** Home: the map is the hero, zoomed to the three fields with thick labelled outlines; one field list; no stats panel
- [x] **#4** Field page: headline facts and the best-fit summary sit in the masthead, above the fold
- [x] **#5** Priorities sit in a sticky rail beside the strategy cards, so a slider change visibly re-ranks them; collapsible on phones
- [x] **#6** Strategy cards: caveats shared by every card shown once; evidence collapsed; crop sequence as coloured blocks with arrows
- [x] **#17** Rotation names lead; R-codes are gone from cards, calendar, replay and Farms like yours

## Charts and data

- [x] **#3** Replay: straight lines, theme-aware colours, direct end labels, neutral drought bands with labels
- [x] **#12** Calendar: rotations stacked so none hide off-screen; readable risk strip; legend instead of two-letter codes
- [x] **#16** Farms like yours: map zooms to matched fields; readable tooltips and table
- [x] **#14** Assistant: verified-number mark stays inline

## Copy, states, i18n

- [x] **#13** Plural-aware `fill()` and `interpolate()`: templates can write `{years} {years|year|years}` (F side); wording issues reported to U
- [x] **#18** Loading skeleton shaped like the page; errors in plain words
- [x] **#20** No hard-coded English in TSX; numbers formatted per language; new keys have Spanish fallbacks in `lib/copyFallbacks.ts` until they reach `copy.json`
- [x] **#21** Well trend states direction; units never wrap
- [x] **#22** Disclaimer shown once per page
- [x] **#23** How-we-know: validation as a readable table

## Verification

- [x] Before/after screenshots at 1440, 768 and 375, light and dark, every route, drawer and states (71 shots each; no route scrolls sideways at 375)
- [x] Contrast: 0 text elements below WCAG AA across home, field and How we know, light and dark (874 checked)
- [x] Keyboard: logical tab order; drawer moves focus to the question box, traps Tab, closes on Escape and returns focus to its button; a slider moved by keyboard re-ranks the cards; calendar and chart scroll regions are focusable
- [x] `prefers-reduced-motion` honoured (animations and smooth scroll off)
- [x] Hard-coded colours: 582 hex values in `globals.css` before; 4 deliberate literals after (ink on crop fills, labels over satellite imagery)
- [x] `npm test` (134), `npm run typecheck`, `npm run build` pass on every commit


## Round 2 (branch `role/web-ui-polish-2`)

From the follow-up review. Items owned elsewhere are fixed on screen from `web/` and handed to the owner in `HANDOFF_OTHER_OWNERS.md`.

**P1**
- [x] **1** Dryland field starts on "No irrigation"; higher limits disabled with a reason
- [x] **2** Options outside your limits are muted, flagged and sorted last; masthead says the same
- [x] **3** "Why it was suggested" lists only points that beat the current rotation (rule sent to M)
- [x] **4** Bars carry a tick at the current rotation; "Avoids heat and frost damage" label (U asked to change the source label)
- [x] **5** Stale saved answers are answered live when a model is configured, with the saved answer as fallback (cache rebuild sent to M)
- [x] **6** Cards lay out 4 / 2×2 / swipe by available width
- [x] **7** Phones: priorities fold to one summary line; swipe dots show position

**P2**
- [x] **8** Wide screens: "Ask about this field" in the sticky nav, no floating button over content
- [x] **9** Section nav marks the section in view
- [x] **10** Priorities rail shows when it has more to scroll; tighter spacing
- [x] **11** Criteria that score the same for every option are named once, not drawn
- [x] **12** One water warning per card
- [x] **13** Map zoom buttons and "Show my field" / "Show all three fields"
- [x] **14** Replay: worst year marked; flat lines named "no irrigation"; dryland opens on income; phones show the table first
- [x] **15** Calendar: month row on every rotation; best fit tagged
- [x] **16** "Use my own key" only with `?byok=1` or a key already on
- [x] **17** Form-like templates shown in plain language while content keeps the old text (proposals sent to U)
- [x] **18** Rotation colours pass the palette validator over all pairs, light and dark; dark theme back to design tokens (sent to U for `design/`)
- [x] **19** Empty NDVI columns hidden with a note; Spanish source descriptions while the data has none (sent to D)

**P3**
- [x] **20** "Copy link to this view"
- [x] **21** Chart library loads only with Rotation Replay: field page first load 298 kB → 185 kB
- [x] **22** Theme: light, dark or match this device (default)
- [x] **23** "Print summary" with a print stylesheet
- [x] **24** Score labelled "Fit with your priorities" with an explanation

## Not changed here (owner decisions or other folders)

- **Mock banner** is switched off on `main` ("suppressed per production requirements"); left as is.
- **M** (`model/`): `assistant_cache.json` was generated for top order R4, R5, R1, R0, but the default cards are R0, R5, R1, R2. Rebuild for the default order; round numbers such as 75.43.
- **D** (`data-pipeline/`): `neighbors.json` NDVI drought columns are all null; `sources.json` `used_for` / `what` text has no Spanish.
- **U** (`content/`, `design/`): `fill()` now supports `{n|one|other}` plurals, so templates like "in years: 1" can become "{years} {years|year|years}"; please add the keys and Spanish from `COPY_KEYS_ADDED.md` / `lib/copyFallbacks.ts` to `copy.json`; "changed by −3 days a year" is a period difference, not a rate; "−0.9 cm/yr a year" doubles the unit; plural workarounds read robotic ("in years: 1"); criterion label "Heat and frost risk" reads backwards (100 = least risk); the rotation palette fails the dataviz colour checks (light: R0↔R1 ΔE 12.9 normal vision, R1/R3 below the lightness band; dark, hand-tuned: R6↔R3 ΔE 3.6 deutan, R3↔R0 ΔE 9.4 normal) — the chart compensates with dashes, end labels, legend and table, but the tokens need a re-step; `web/styles/tokens.css` has drifted from `design/tokens.css` (dark muted text #eaf3ed is nearly the body colour).
