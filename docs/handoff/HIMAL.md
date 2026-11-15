# Handoff for Himal: pitch, submission and QA

Written 15 Nov 2026, about 20:30 IST. Submission closes 23:59 local time today.

You own the human-facing finish: the demo, the project page and testing the live app. Five build sessions are writing the code in parallel, so stay out of the code folders listed below and you will never hit a merge conflict.

## Where things stand

| Piece | Branch | State |
|---|---|---|
| Data pipeline (D) | `role/data` | Done. Merged into `main`. NASA extras (SMAP, MODIS, ECOSTRESS) still downloading |
| Model (M) | `role/model` | Done. Real numbers for f1, f2, f3. Merged into `main` |
| Assistant | `role/model-assistant` | 36 cached answers being generated and judged |
| Content and design (U) | `role/content` | Done. Merged into `main`. Your wireframes and crop text colours are being added from `himal/content` |
| Web app (F) | `role/web` | Being rewritten to the README contract. Not yet on `main` |
| Pitch deck | `Parisha` | Draft PDF; slides 5 and 7 need work |

Live app (fallback version, sample data): https://field-shift-chi.vercel.app
The real-data version replaces it at the same URL, target about 22:30 IST.
Do not use `field-shift.vercel.app`: that belongs to another team.

## Read first

- `README.md` sections 1 to 3 (what we built, the demo story, standout features)
- `docs/SUBMISSION.md` (draft text for the project page)
- `docs/PITCH.md` (30-second video script)
- `docs/METHODS.md` and `docs/DATA_SOURCES.md` (for the "how it works" and data sections)

## Your tasks, in order

1. **Check the 2026 rules now.** Confirm the deadline time zone and the demo format: a video of 30 seconds or less, or at most 7 slides. Going over either removes the project from global judging. Tell Sarthak the answer.
2. **The name is decided: Stubble.** Stubble is the crop residue that protects soil from wind, which ties to the Dust Bowl story. Use it on the slides, the video and the project page. The app is being renamed now; the live link moves to https://stubble.vercel.app once the alias is set.
3. **Finish the deck** (if slides). Start from Parisha's PDF on branch `Parisha`. Seven slides max: problem, our tool, how it decides (data to model to cards), Rotation Replay, Farms Like Yours plus assistant, validation and honesty, impact and next steps. Use real screenshots once the real-data version is live. No NASA logos or meatball.
4. **Record the video** (if video). Follow `docs/PITCH.md`. Record the live site at 1080p, burn in captions, 30 seconds or less. Watermark any AI-generated media.
5. **Fill the Space Apps project page** from `docs/SUBMISSION.md`. Add the live URL, the repo link (https://github.com/mrudduni/Team-Brackets, public, Apache 2.0) and the video or slides. List every data source from `docs/DATA_SOURCES.md`. Use the AI disclosure from `docs/AI_USE.md` once it lands.
6. **Test the live app** once the real-data version is up. For each of f1, f2, f3, on a phone (375 px) and a laptop: pick the field, read the overview, move every slider, switch water cap and climate, open every card section, the Replay chart, Farms Like Yours, the assistant (one suggested question, one free question, English and Spanish). Write what breaks in `docs/handoff/QA_NOTES.md` on your branch (one line each: field, screen, what you did, what went wrong).

7. **Spanish check (if anyone on the team reads Spanish well).** All Spanish was written with AI help and no native speaker has read it. Read `content/card_text.json` and `content/copy.json` on `main`. Send fixes to Sarthak as a list (key, current text, better text); do not edit `content/` yourself.
8. **Crop timing caveat.** `content/crops.yaml` has 47 lines marked `# verify` (harvest dates, heat and frost thresholds, triticale and rye borrowing wheat values). If a judge asks, say the crop timing uses FAO-56 tables and K-State planting guides, with some working values still to verify.

## Branch and folders

- Work on branch `himal/pitch` (already created from `main`).
- You may edit: `docs/handoff/`, `docs/PITCH.md`, `docs/SUBMISSION.md`, and add a `pitch/` folder for slides, video and screenshots (keep videos under 50 MB or link them instead).
- Do not edit: `data-pipeline/`, `model/`, `scripts/`, `web/`, `content/`, `design/`, `README.md`. Sessions are writing there. Send changes for those to Sarthak.
- Push often: `git push origin himal/pitch`. Sarthak merges it into `main`.
- Never commit API keys or passwords.

## Known issues to mention honestly in the pitch

- Some NASA layers (SMAP soil moisture, MODIS greenness) may show as "limited" if their downloads do not finish in time.
- Revenue ignores costs and uses constant prices; every card lists this as an information gap.
- The tool supports a farmer's judgement and never replaces it. Say this at the end of the demo.
