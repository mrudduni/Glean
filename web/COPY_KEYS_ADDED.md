# Copy keys added by the web app

These keys are not in README §8.6. The web app calls each one as `t("key", "English fallback")`.

Status: all of them were added to `content/copy.json` with `en` and `es` text in role/content 3c740c7 (2026-11-15). Add new keys here and to copy.json together. Added after that commit, not yet in copy.json: `neighbors.fields_header`, `assistant.busy`, `card.unlock_tick` (Tick “{option}” to include it.), `assistant.own_key*` (9 keys), `card.unlock_cap` (Set the water limit to “{option}” or higher to include it.), `assistant.cache_mismatch` (Saved answer, written for different settings than the cards on screen. Ask in your own words for an answer that matches them.).

Spanish for every key added on role/web-ui-polish is in `lib/copyFallbacks.ts` (used only until the key is in copy.json). Templates may use `{name|one|other}` for plurals, e.g. `{years} {years|year|years}`.

Generated from a grep of `t("…")` calls in `app/`, `components/` and `lib/`.

| Key | Where used | English text |
|---|---|---|
| `app.location` | app/page.tsx | Finney County, Kansas |
| `assistant.busy` | app/api/ask/route.ts | The assistant is busy right now. Try one of the suggested questions below. Their answers are ready. |
| `assistant.cache_mismatch` | components/AssistantDrawer.tsx | Saved answer, written for different settings than the cards on screen. Ask in your own words for an answer that matches them. |
| `error.check_connection` | app/page.tsx | Check your connection and try again. |
| `priorities.rail_hint` | components/PrioritiesPanel.tsx | Move a slider and the cards re-rank instantly. |
| `summary.best_fit` | components/FieldWorkspace.tsx | Best fit for your priorities |
| `summary.vs_current` | components/FieldWorkspace.tsx | Match score {score}, against {current} for your current rotation. |
| `summary.see_options` | components/FieldWorkspace.tsx | Compare all options |
| `card.shared_title` | components/StrategyPanel.tsx | Applies to every option above |
| `card.shared_more` | components/StrategyPanel.tsx | Plus {n} that apply to every option, listed below the cards. |
| `card.bars_hint` | components/StrategyPanel.tsx | Bars compare the options shown: 100 is the best of them on that point. |
| `replay.unit.irrigation` | components/ReplayChart.tsx | Irrigation water, mm per year |
| `replay.unit.revenue` | components/ReplayChart.tsx | Income before costs, $ per acre |
| `replay.unit.stress` | components/ReplayChart.tsx | Days of crop water stress per year |
| `replay.unit.bare` | components/ReplayChart.tsx | Days of bare ground per year |
| `calendar.years_in_10` | components/FieldCalendar.tsx | years in 10 |
| `calendar.days_per_month` | components/FieldCalendar.tsx | days a month |
| `overview.measure` | components/OverviewPanel.tsx | Measure (screen readers only) |
| `overview.change` | components/OverviewPanel.tsx | Change |
| `overview.grace_trend` | components/OverviewPanel.tsx | GRACE trend |
| `overview.well_chart` | components/OverviewPanel.tsx | Depth to water at the nearest well ({km} km), metres below ground |
| `overview.wells_deeper` | components/OverviewPanel.tsx | deeper each year |
| `overview.wells_shallower` | components/OverviewPanel.tsx | shallower each year |
| `neighbors.similarity` | components/NeighborsView.tsx | {pct}% similar |
| `neighbors.matched_count` | components/NeighborsView.tsx | {matched} of {pool} nearby fields match on soil and irrigation. |
| `neighbors.no_greenness` | components/NeighborsView.tsx | Drought-year greenness (MODIS) is not available for these fields yet. |
| `neighbors.method` | components/NeighborsView.tsx | How these fields were matched |
| `neighbors.your_field` | components/NeighborsView.tsx | Your field |
| `trust.check` | app/how-we-know/page.tsx | What we checked |
| `trust.match` | app/how-we-know/page.tsx | Match |
| `trust.n` | app/how-we-know/page.tsx | Data points |
| `error.field_title` | components/FieldWorkspace.tsx | This field could not be loaded |
| `error.detail` | components/FieldWorkspace.tsx | Technical detail |
| `state.loading_field` | components/FieldWorkspace.tsx | Loading this field (screen readers) |
| `constraints.no_irrigation_note` | components/PrioritiesPanel.tsx | This field has no irrigation, so only dryland options apply. |
| `card.bars_hint_tick` | components/StrategyPanel.tsx | Longer bars are better for you; 100 is the best of the options shown. The tick marks your current rotation. |
| `card.uniform` | components/StrategyPanel.tsx | Same for every option, so not drawn: {list}. |
| `card.unavailable` | components/StrategyPanel.tsx | Not available with your current limits |
| `card.needs_water_none` | components/StrategyPanel.tsx | Needs irrigation, and this field has none. Its numbers assume no water. |
| `card.fit_label` | components/StrategyPanel.tsx | Fit with your priorities (wireframe wording; replaces card.score on screen) |
| `card.fit_help` | components/StrategyPanel.tsx | How well this option matches the priorities you set, compared with the other options here. It changes when you move a slider. |
| `card.better_than_current` / `card.worse_than_current` | components/StrategyPanel.tsx | better / worse than your current rotation (screen readers) |
| `criteria.heat_frost_display` | components/StrategyPanel.tsx | Avoids heat and frost damage (wireframe wording) |
| `summary.none_fit_title` | components/FieldWorkspace.tsx | Nothing fits your limits yet |
| `summary.unavailable` | components/FieldWorkspace.tsx | {n} {n\|option is\|options are} shown below, each needing a change to your limits. |
| `strategies.none_fit_dryland` | components/StrategyPanel.tsx | No other dryland rotation fits these limits. Tick the equipment or buyers you have to see more. |
| `theme.system` | components/SiteHeader.tsx | Match this device |
| `priorities.summary_balanced` | components/PrioritiesPanel.tsx | Balanced priorities |
| `priorities.summary_most` | components/PrioritiesPanel.tsx | Most: |
| `priorities.edit` | components/PrioritiesPanel.tsx | Edit |
| `share.copy` / `share.copied` / `share.copy_manual` | components/FieldWorkspace.tsx | Copy link to this view / Link copied / Copy this link |
| `share.print` | components/FieldWorkspace.tsx | Print summary |
| `priorities.print_label` | components/PrioritiesPanel.tsx | Your settings (print summary) |
| `assistant.own_key` | components/AssistantDrawer.tsx | Use my own key |
| `assistant.own_key_on` | components/AssistantDrawer.tsx | on |
| `assistant.own_key_toggle` | components/AssistantDrawer.tsx | Answer free-text questions with my key |
| `assistant.own_key_provider` | components/AssistantDrawer.tsx | Provider |
| `assistant.own_key_custom` | components/AssistantDrawer.tsx | Other (base URL) |
| `assistant.own_key_url` | components/AssistantDrawer.tsx | Base URL (https) |
| `assistant.own_key_model` | components/AssistantDrawer.tsx | Model id |
| `assistant.own_key_key` | components/AssistantDrawer.tsx | API key |
| `assistant.own_key_note` | components/AssistantDrawer.tsx | Your key stays in this browser tab and is sent only with your questions. Suggested questions never use it. |
| `assistant.close` | components/AssistantDrawer.tsx | Close |
| `assistant.subtitle` | components/AssistantDrawer.tsx | Answers use only this field's data. Every number is checked. |
| `assistant.waiting` | components/AssistantDrawer.tsx | Checking the field data |
| `calendar.counts_legend` | components/FieldCalendar.tsx | Numbers: storm days · windy days |
| `calendar.crop_period` | components/FieldCalendar.tsx | Crop in the field |
| `calendar.eyebrow` | components/FieldCalendar.tsx | Plan across seasons |
| `calendar.odds` | components/FieldCalendar.tsx | {risk}: {count} of 10 years |
| `calendar.risk_title` | components/FieldCalendar.tsx | Climate odds by month, 2000 to 2025 |
| `calendar.storm_days` | components/FieldCalendar.tsx | Storm days |
| `calendar.windy_days` | components/FieldCalendar.tsx | Windy days |
| `calendar.year` | components/FieldCalendar.tsx | Year |
| `card.current_benefits` | components/StrategyPanel.tsx | Benefits of the other rotations are measured against this one. |
| `card.current_why` | components/StrategyPanel.tsx | This is your baseline. The other cards are compared against it. |
| `card.lower_score` | components/StrategyPanel.tsx | Fits your limits, but scores lower than the three shown. |
| `card.no_why` | components/StrategyPanel.tsx | No criterion stands out at these priorities. |
| `card.none` | components/StrategyPanel.tsx | Nothing listed. |
| `crop.other` | lib/ui.ts | Other |
| `error.retry` | app/how-we-know/page.tsx | Try again |
| `error.title` | app/how-we-know/page.tsx | The data could not be loaded |
| `field.area` | app/page.tsx | Area |
| `home.crop_history` | app/page.tsx | USDA crop history per field |
| `home.data_in_use` | app/page.tsx | Data behind these fields |
| `home.map_caption` | app/page.tsx | Click a field outline to open it. |
| `home.rotations` | app/page.tsx | Rotations |
| `home.rotations_note` | app/page.tsx | Current rotation against six alternatives |
| `home.soil_storage` | app/page.tsx | Lowest soil water storage of the 3 fields |
| `lang.label` | components/SiteHeader.tsx | Language |
| `map.area` | components/FieldMap.tsx | Garden City area |
| `map.boundaries` | components/FieldMap.tsx | USDA field boundaries |
| `nav.all_fields` | components/FieldWorkspace.tsx | All fields |
| `nav.back_to_field` | app/how-we-know/page.tsx | Back to the field |
| `nav.field` | components/FieldWorkspace.tsx | Field |
| `nav.main` | components/SiteHeader.tsx | Main navigation |
| `nav.sections` | components/FieldWorkspace.tsx | Field sections |
| `neighbors.eyebrow` | components/NeighborsView.tsx | Learn from the landscape |
| `neighbors.fields_header` | components/NeighborsView.tsx | Nearby fields |
| `neighbors.like_yours` | components/NeighborsView.tsx | Like yours |
| `neighbors.matched_note` | components/NeighborsView.tsx | nearby fields matched on soil and irrigation |
| `neighbors.rotation` | components/NeighborsView.tsx | Rotation |
| `overview.eyebrow` | components/OverviewPanel.tsx | Field snapshot |
| `overview.frost_free` | components/OverviewPanel.tsx | Frost-free days |
| `overview.grace_chart` | components/OverviewPanel.tsx | GRACE water storage anomaly, cm |
| `overview.headlines` | components/OverviewPanel.tsx | What stands out |
| `overview.hot_days` | components/OverviewPanel.tsx | Days at or above 35 °C |
| `overview.nearest_well` | components/OverviewPanel.tsx | Nearest well |
| `overview.notes_kicker` | components/OverviewPanel.tsx | Field notes |
| `overview.organic_matter` | components/OverviewPanel.tsx | Organic matter |
| `overview.precip` | components/OverviewPanel.tsx | Rain per year |
| `overview.water_storage` | components/OverviewPanel.tsx | Water storage, top metre |
| `overview.wells_trend` | components/OverviewPanel.tsx | Depth to water, nearby wells |
| `overview.wind_erodibility` | components/OverviewPanel.tsx | Wind erodibility |
| `priorities.eyebrow` | components/PrioritiesPanel.tsx | Make it yours |
| `priorities.subtitle` | components/PrioritiesPanel.tsx | Move the sliders to say what matters most. The cards below re-rank instantly. |
| `replay.average` | components/ReplayChart.tsx | Average |
| `replay.eyebrow` | components/ReplayChart.tsx | Look back before looking ahead |
| `replay.metric_label` | components/ReplayChart.tsx | Choose what to plot |
| `replay.not_feasible` | components/ReplayChart.tsx | over your water limit |
| `replay.note` | components/ReplayChart.tsx | Average across every phase of the rotation, on this field's real weather. |
| `replay.rotation` | components/ReplayChart.tsx | Rotation |
| `replay.summary_caption` | components/ReplayChart.tsx | Average and worst 5 years per rotation |
| `replay.worst5` | components/ReplayChart.tsx | Worst 5 years |
| `section.not_available` | app/how-we-know/page.tsx | Not available for this field yet. |
| `strategies.eyebrow` | components/StrategyPanel.tsx | Compare your options |
| `strategies.none_fit` | components/StrategyPanel.tsx | No other rotation fits these limits. Try a higher water cap or tick the equipment you have. |
| `strategies.score_note` | components/StrategyPanel.tsx | Scores are relative to the rotations compared here, 0 to 100. They are model estimates, not forecasts. |
| `strategies.subtitle` | components/StrategyPanel.tsx | Your current rotation and the three that fit your priorities most closely. |
| `theme.dark` | components/SiteHeader.tsx | Dark theme |
| `theme.label` | components/SiteHeader.tsx | Colour theme |
| `theme.light` | components/SiteHeader.tsx | Light theme |
| `trust.coverage` | app/how-we-know/page.tsx | Resolution and period |
| `trust.eyebrow` | app/how-we-know/page.tsx | Transparency before certainty |
| `trust.no_validation` | components/TrustBadge.tsx | No validation checks for this field yet. |
| `trust.source` | app/how-we-know/page.tsx | Source |
| `trust.tag` | app/how-we-know/page.tsx | Tag |
| `trust.used_for` | app/how-we-know/page.tsx | Used for |
| `trust.validation` | app/how-we-know/page.tsx | Checks against independent data |
| `unit.days` | components/OverviewPanel.tsx | days |
| `field.kind.irrigated_pivot` | FieldMap, home, overview | Irrigated pivot |
| `field.kind.dryland` | FieldMap, home, overview | Dryland |
| `field.kind.sandy_wind` | FieldMap, home, overview | Sandy, wind-erodible |
| `rotation_class.continuous_corn` | OverviewPanel, NeighborsView | Continuous corn |
| `rotation_class.corn_wheat_sorghum` | OverviewPanel, NeighborsView | Corn, wheat, sorghum |
| `rotation_class.corn_soy` | OverviewPanel, NeighborsView | Corn and soybean |
| `rotation_class.wsf` | OverviewPanel, NeighborsView | Wheat, sorghum, fallow |
| `rotation_class.wheat_fallow` | OverviewPanel, NeighborsView | Wheat and fallow |
| `rotation_class.alfalfa` | OverviewPanel, NeighborsView | Alfalfa |
| `rotation_class.mixed` | OverviewPanel, NeighborsView | Mixed |
| `overview.wind.high` | OverviewPanel | Blows easily |
| `overview.wind.moderate` | OverviewPanel | Moderate |
| `overview.wind.low` | OverviewPanel | Low |
| `calendar.stage.ini` | FieldCalendar | Establishing |
| `calendar.stage.dev` | FieldCalendar | Growing |
| `calendar.stage.mid` | FieldCalendar | Peak growth |
| `calendar.stage.late` | FieldCalendar | Ripening |

`calendar.odds` takes `{risk}` and `{count}`. All other added keys take no vars.
| `card.shown_at` | StrategyPanel | Numbers shown with: {cap}. |
| `soil.texture.<snake_case>` | lib/i18n textureLabel | Optional. Without it, Spanish uses a built-in name (fine sand: arena fina, silt loam: franco limoso, clay loam: franco arcilloso). |
| `card.no_water_here` | StrategyPanel | This field is not irrigated. These numbers assume no water, so they understate this rotation. |
| `card.no_water_why` | StrategyPanel | Not suggested here: it needs irrigation this field does not have. |

Spanish for card.shown_at, card.no_water_here and card.no_water_why is in the code fallbacks in StrategyPanel.tsx; copy it into copy.json.
