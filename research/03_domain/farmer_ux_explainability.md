# Farmer UX, explainability and uncertainty

This file covers why farm decision tools fail or succeed, how to show uncertainty to people without a statistics background, which explanation formats to use, and how to use a large language model (LLM) to write explanations that stay grounded in computed evidence. It ends with the Space Apps rules that apply to an in-app LLM.

The challenge video asks teams to "compare rotations, reveal trade-offs, understand risk, make uncertainty visible". We treat the last phrase as a top-level design requirement: no number appears on screen without its range, its source and a confidence label.

## Why farm decision tools fail or get used

| Finding | Source | What it means for us |
| --- | --- | --- |
| Farmer use of agricultural DSS has been low for decades. Expert systems that bypass the farmer's own decision process were not used. Tools that fit into a modified decision process, or a simulator in the hands of an adviser, did better. McCown also notes that farmers often learned from a DSS and then dropped it without loss | McCown (2002) | Build a conversation aid for a farmer and an adviser, not an oracle. Success can mean the farmer learns something, not daily use |
| Mixed-methods study of UK farmers and advisers found 15 factors that drive uptake, including usability, cost-effectiveness, performance, relevance to the user and fit with compliance needs | Rose et al. (2016) | Free, fast, relevant to the farmer's own field, and linked to programmes the farmer already uses (NRCS CSP in the US, Mera Pani Meri Virasat in Haryana) |
| Uptake stays low without real user involvement. The authors recommend a "decision support context assessment" before building | Rose et al. (2018), 78 interviews and 5 focus groups | Spend the first hours deciding who uses the tool and when. For Haryana, that is likely a farmer with an adviser from a Krishi Vigyan Kendra (KVK) |
| Agronomic models are often designed without end users in mind | Prost et al. (2011) | Show model limits in plain words |
| Success depends on user-centred and post-development work, not modelling alone | Lacoste and Powles (2016) | Budget time for onboarding and support, not only features |
| Participatory DSS development needs a framework for engaging users | Jakku and Thorburn (2010) | Use a short co-design loop with one farmer and one adviser per region |
| Most economic DSS for irrigated cropping were technology push, few showed uncertainty, and few let users compare tactical and strategic decisions | Ara et al. (2021) | Separate this season's choices from multi-year rotation planning, and show uncertainty |
| Site-specific nutrient tools for smallholders rarely scaled beyond pilots. Technical problems cut the odds of reaching 5 to 10 percent of target farmers sharply | Sida et al. (2023) | For Indian smallholders, reliability on a cheap phone and a weak connection matters more than features |
| Midwest survey of 2,633 farmers and 2,719 advisers: advisers use public DSTs more and act as change agents | Lu et al. (2020) | Design for the adviser too: printable reports, field lists |
| Trust in smart farming depends on transparency about data use and on benefit sharing | Jakku et al. (2019) | State what we store (nothing by default) and what data we use |
| Advisers are central to digital farm advice | Eastwood et al. (2019); Ayre et al. (2019) | Give advisers an "agronomist view" with methods and checks |

## Showing uncertainty to non-experts

Evidence we rely on.

- Spiegelhalter et al. (2011) and Spiegelhalter (2017) review ways to show uncertainty about the future and recommend matching the format to the audience and the decision.
- van der Bles et al. (2019) give a framework with three objects of uncertainty (facts, numbers, science) and two levels (direct and indirect). They list nine ways to express direct uncertainty and review evidence on trust. The abstract notes that communicating epistemic uncertainty does not necessarily reduce trust; the full findings are not confirmed here.
- Joslyn and LeClerc (2012) found that adding uncertainty to forecasts improved weather-related decisions and softened the effect of forecast errors.
- Kay et al. (2016) and Fernandes et al. (2018) found that quantile dot plots help people make better decisions under uncertainty than single numbers.
- Gigerenzer and Hoffrage (1995) showed that natural frequencies ("7 out of 25") are easier to reason with than percentages.
- Tversky and Kahneman (1981) showed that gain and loss framing change choices. We should show both "saves 300 mm" and "uses 300 mm less than now", and never only the flattering frame.
- Hullman (2020) found that authors often leave uncertainty out because they think readers will not understand it. Kinkeldey et al. (2014) and Padilla et al. (2021) review how to test uncertainty displays.

Design rules for Field Shift.

1. Frequencies from real years. Every outcome is a set of past weather years. "In 6 of the last 25 kharif seasons, maize would have needed more than 2 irrigations in July." This is honest, local and easy to grasp.
2. Quantile dot plots. One dot per weather year (20 to 25 dots) for irrigation need, relative yield and stress days. A farmer can count dots.
3. Confidence labels with rules, not feelings.
   - High: the input is checked against ground data near this field, and the method reproduced published trial directions (see validation_plan.md).
   - Medium: checked elsewhere, or the model is standard but uncalibrated here.
   - Low: no ground check is possible here (for example, SMAP soil moisture in Haryana), or the claim rests on one study.
4. Native resolution on every card. "Soil moisture is a 9 km average. Your field is 0.8 ha." Show the field outline inside the grid cell on a small map.
5. Agreement as a signal. When the simple water balance and the crop model disagree, say so and lower the confidence label.
6. Never a single best answer. Show the ranking with its stability: "Rotation B is first in 72 of 100 test runs."

## Explanation formats

### Evidence card

One card per claim. Fields:

| Field | Example |
| --- | --- |
| Claim | Maize-mustard needs less irrigation than rice-wheat on this field |
| Number and range | 420 mm less per year; middle 80 percent of years 310 to 540 mm |
| How we computed it | FAO-56 dual crop coefficient water balance, 2001 to 2025 weather |
| Data used | NASA POWER (0.5 degree), IMERG (0.1 degree), SoilGrids water holding (250 m) |
| Citation | FAO-56 chapters 7 and 8; dataset DOIs |
| Confidence | Medium: water balance checked against ECOSTRESS ET here with bias x percent |
| What would change this | Puddling losses on your soil, actual tubewell hours, a different rice duration |
| Check locally | Ask your KVK about mustard aphid pressure in late sowing |

### Counterfactuals

Wachter et al. (2017) describe counterfactual explanations: the smallest change to the inputs that would change the outcome. For us: "If you could only irrigate 3 times in rabi, chickpea would rank first." The ranking engine can search for these by moving one input or weight at a time. Counterfactuals answer the farmer's real question ("what would make you say something else?") without exposing model internals.

### "What would change my mind" checks for agronomists

Each strategy lists the assumptions that, if wrong, would flip the result, with the threshold. Example: "If the local maize price falls below the level where its margin drops under wheat's minimum support price, Rotation B loses its lead." The agronomist ticks each one as checked, not checked, or wrong. This also builds the local review list the challenge asks for.

### Rank flip display

A small table of weights shows how far each weight must move before the top rotation changes. See mcda_ranking.md.

## Indian smallholder considerations

- Many Haryana farmers will use the tool with an adviser, on a phone, with a weak connection. Keep the field report printable and the main view usable offline after one load.
- Hindi output is needed. Haryanvi voice input is a stretch goal. Machine translation must be reviewed by a native speaker before the demo, and labelled as SI-generated.
- Money matters most. Show rupees per acre, the Mera Pani Meri Virasat incentive (Rs 7,000 per acre at launch, raised to Rs 8,000 for kharif 2025 according to press reports), and the risk that maize or pulse prices fall below the minimum support price. The incentive amount must be rechecked against the current government order before the demo.
- Groundwater is the main shared stake. GRACE showed groundwater depletion across Rajasthan, Punjab and Haryana (Rodell et al., 2009). Show this as regional context, not as a field fact.

## Using an LLM to write explanations

Principle. The LLM never computes. All numbers come from the deterministic engine. The LLM turns a structured evidence ledger into plain sentences in English or Hindi, and every sentence must cite a ledger entry.

Pipeline.

1. The engine writes an evidence ledger: a list of entries, each with an ID, a claim, a value, a range, units, the dataset, the method, the citation URL and a confidence label.
2. The app sends the ledger to the LLM as source documents, plus a short curated set of agronomy notes with their own sources. With the Claude API, use the citations feature: put each ledger entry in a custom content document block so a citation points to exactly one entry. The documentation warns that prompts asking for JSON only may return few or no citations, and that the API does not guarantee a citation for every field, so the app must check.
3. A validator runs on the output:
   - every sentence has at least one citation to a ledger entry;
   - every number in the text matches a ledger value or range after unit normalisation;
   - no banned words ("guarantee", "will increase", "best for you");
   - the "check locally" items from the ledger all appear.
4. If any check fails, the app shows the template text built directly from the ledger instead. The demo must work with the LLM switched off.
5. Label all generated text "Written by SI from the evidence above. Check the evidence cards."

Literature. Retrieval-augmented generation grounds outputs in retrieved documents (Lewis et al., 2020; NeurIPS paper, not found in Crossref). Surveys by Ji et al. (2023) and Huang et al. (2025) classify hallucination types and controls. Gao et al. (2023) built a benchmark for LLM text with citations and found that citation quality needs explicit checking. Min et al. (2023) score factual precision by splitting text into atomic facts, which suits our validator design.

Evaluation. Before the demo, generate explanations for 20 fields and count unsupported numbers and uncited sentences. Report the rate. The target is zero unsupported numbers.

## Space Apps rules on SI

From research/02_hackathon/rules_judging.md:

- SI tools may speed up development, but should not be used to come up with the team's idea for solving the challenge.
- The submission must describe how SI tools were used. Judges see SI markers inside the project.
- SI-generated images and video need a visible watermark. SI audio, code and data must be acknowledged in text and metadata.
- Generated content must not use or modify NASA branding.

For an in-app LLM this means: label every generated explanation and translation as SI output, state in the project details which model writes the text and that it only rewrites computed evidence, and keep the computed evidence visible next to it.

## Sources

- McCown (2002): https://doi.org/10.1016/s0308-521x(02)00026-4
- Rose et al. (2016): https://doi.org/10.1016/j.agsy.2016.09.009
- Rose et al. (2018), user-centred design for agricultural DSS (UEA repository record): https://consensus.app/papers/details/w:ec953bdb-027c-4732-a861-5432508a9e00/
- Prost et al. (2011): https://doi.org/10.1007/s13593-011-0059-4
- Lacoste and Powles (2016): https://doi.org/10.1016/j.compag.2016.01.003
- Jakku and Thorburn (2010): https://doi.org/10.1016/j.agsy.2010.08.007
- Ara et al. (2021), DSS in irrigated agriculture review: https://consensus.app/papers/details/w:2617d154-a04e-4470-befa-339cf65bb336/
- Sida et al. (2023), failure to scale in digital agronomy: https://consensus.app/papers/details/w:6d70c53f-124a-43fe-8242-10216cbb26df/
- Lu et al. (2020), Midwest DST survey: https://consensus.app/papers/details/w:f31c642c-638e-4ea9-8540-9c43986c957a/
- Jakku et al. (2019): https://doi.org/10.1016/j.njas.2018.11.002
- Eastwood et al. (2019): https://doi.org/10.1016/j.njas.2019.04.004
- Ayre et al. (2019): https://doi.org/10.1016/j.njas.2019.05.001
- Spiegelhalter et al. (2011): https://doi.org/10.1126/science.1191181
- Spiegelhalter (2017): https://doi.org/10.1146/annurev-statistics-010814-020148
- van der Bles et al. (2019): https://doi.org/10.1098/rsos.181870
- Joslyn and LeClerc (2012): https://doi.org/10.1037/a0025185
- Kay et al. (2016): https://doi.org/10.1145/2858036.2858558
- Fernandes et al. (2018): https://doi.org/10.1145/3173574.3173718
- Gigerenzer and Hoffrage (1995): https://doi.org/10.1037/0033-295x.102.4.684
- Tversky and Kahneman (1981): https://doi.org/10.1126/science.7455683
- Hullman (2020): https://doi.org/10.1109/tvcg.2019.2934287
- Kinkeldey et al. (2014): https://doi.org/10.1179/1743277414y.0000000099
- Padilla et al. (2021), uncertainty visualization: https://doi.org/10.1002/9781118445112.stat08296
- Wachter et al. (2017): https://doi.org/10.2139/ssrn.3063289
- Lewis et al. (2020), retrieval-augmented generation: https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html
- Ji et al. (2023): https://doi.org/10.1145/3571730
- Huang et al. (2025): https://doi.org/10.1145/3703155
- Gao et al. (2023): https://doi.org/10.18653/v1/2023.emnlp-main.398
- Min et al. (2023): https://doi.org/10.18653/v1/2023.emnlp-main.741
- Claude API citations documentation: https://platform.claude.com/docs/en/build-with-claude/citations
- Rodell et al. (2009): https://doi.org/10.1038/nature08238
- Mera Pani Meri Virasat incentive, Tribune (June 2025): https://tribuneindia.com/news/haryana/haryana-sets-target-of-1l-acre-under-mera-pani-meri-virasat-scheme
- Haryana government press release (Rs 7,000 per acre, 2021): https://www.prharyana.gov.in/en/haryana-government-will-provide-incentives-on-sowing-watersaving-crops-instead-of-paddy-under-the
- Challenge video: https://www.youtube.com/watch?v=cF0U2WXsM7o
- Space Apps project submission guide: https://www.spaceappschallenge.org/resources/project-submission-guide/
