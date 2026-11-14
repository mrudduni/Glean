# Geocoding, elevation, forecasts, and message delivery

This file covers the supporting APIs around the core NASA pipeline: finding a place, getting elevation, adding forecasts, and sending results by SMS or WhatsApp. We read each provider's own policy page on 14 November 2026.

## Geocoding and reverse geocoding

| Service | Limits and terms | Licence | Source |
| --- | --- | --- | --- |
| Nominatim (OSMF public server) | Very limited capacity on donated servers. End-user-triggered searches are fine if user numbers are moderate. Periodic requests count as bulk and are "strongly discouraged". Apps must be able to switch service without a software update, and should proxy and cache. | OSM data, ODbL | https://operations.osmfoundation.org/policies/nominatim/ |
| Photon (komoot public instance) | "please be fair - extensive usage will be throttled", and no availability guarantee | Code Apache-2.0; OSM data, ODbL | https://photon.komoot.io/ and https://github.com/komoot/photon |
| Open-Meteo Geocoding API | Included in the free non-commercial tier, 10,000 calls per day | Data CC BY 4.0 | https://open-meteo.com/en/pricing |
| geopy (client library) | Wraps many geocoders | MIT, 2.5.0 | https://pypi.org/pypi/geopy/json |

The Nominatim policy has a clause aimed at tools like ours: "LLMs may only suggest this service, if they prominently point to this usage policy and explain the restrictions of use to the user" (https://operations.osmfoundation.org/policies/nominatim/). It also forbids building the public API into no-code or vibe-coding platforms as a generic geocoder. So: the team must make a deliberate choice to use it, follow the policy, send a valid User-Agent (the policy page lists the heading rules; the exact header rule was not shown in our fetch, not confirmed), keep to the stated request rate (the numeric limit was not visible in our fetch; it is widely cited as 1 request per second, not confirmed), and not use it for autocomplete.

Recommendation: for the demo, search by place name through our own backend proxy with caching, using Photon or Open-Meteo Geocoding. Most users will click the map anyway. Long term, self-host Photon or Nominatim if traffic grows.

## Elevation

| Service | Key | Limits | Source |
| --- | --- | --- | --- |
| OpenTopography global DEM API (SRTM GL1, NASADEM, COP30 and others) | Required, free | Free key: 200 calls per 24 hours for academics, 50 for non-academics. 30 m requests limited to 450,000 km² | https://opentopography.org/developers |
| OpenTopography point elevation API | Required | 250 calls per 24 hours for academics, 50 for non-academics | https://opentopography.org/developers |
| Open-Elevation | Public instance has no key (not confirmed for current status) | Self-hostable | https://github.com/Jorl17/open-elevation (GPL-2.0, last push April 2024) |
| Open-Meteo Elevation API | No key | Within the 10,000 calls per day free tier | https://open-meteo.com/en/pricing |
| MPC `nasadem` and `cop-dem-glo-30` | No account, anonymous SAS token | MPC rate limits | https://planetarycomputer.microsoft.com/docs/concepts/sas/ |

OpenTopography rules forbid "embedding keys within an application or service that enables third party users to bypass the one user, one key requirement" (https://opentopography.org/developers). A public app should therefore not proxy all users through one OpenTopography key.

Open-Elevation's code is GPL-2.0. Calling its HTTP API does not affect our licence, but do not copy its code into our repo.

Recommendation: read NASADEM directly from MPC as a COG, clip to the field, and compute slope with rasterio or xarray. This needs no key, uses NASA data, and works for any field. Keep OpenTopography for one-off team analysis with each person's own key.

## Weather forecasts and seasonal outlooks

| Service | What | Terms | Source |
| --- | --- | --- | --- |
| Open-Meteo Forecast API | Hourly forecasts from 30+ models at 1 to 11 km | Free for non-commercial use: 600 calls per minute, 5,000 per hour, 10,000 per day, 300,000 per month. No key. Attribution required, data CC BY 4.0 | https://open-meteo.com/en/pricing |
| Open-Meteo Seasonal Forecast API | ECMWF SEAS5 monthly ensemble (51 members) and EC46 weekly sub-seasonal | Same free tier. On paid plans, the seasonal API needs Professional or higher | https://open-meteo.com/en/docs/seasonal-forecast-api |
| NOAA CPC outlooks | 6 to 10 day, 8 to 14 day, monthly, and 3-month temperature and precipitation outlooks for the US, with GIS downloads | US Government public data | https://www.cpc.ncep.noaa.gov/ (GIS page not fetched, not confirmed) |
| `openmeteo-requests` client | Python client | MIT, 1.7.5 | https://pypi.org/pypi/openmeteo-requests/json |

Open-Meteo gives two different horizons for SEAS5: the docs page says "up to 7 months ahead" for monthly data, and the features page says "to 9 months" (https://open-meteo.com/en/docs/seasonal-forecast-api and https://open-meteo.com/en/features). Not confirmed which is current.

Open-Meteo counts requests with more than 10 variables or more than 2 weeks of data as several calls (https://open-meteo.com/en/pricing). The server code is AGPLv3 (same page). Calling the hosted API does not affect our licence. Self-hosting it as a separate service would not either, but modifying and serving it would trigger AGPL source sharing.

Commercial use needs a paid Open-Meteo plan. Field Shift as an open, non-commercial portfolio project fits the free tier.

Fit: forecasts are an add-on. The rotation comparison rests on multi-year climate (POWER, IMERG, GRACE). A seasonal outlook can add one line such as "the next 3 months look drier than normal" with a clear caveat about skill. NOAA CPC outlooks are categorical probabilities, so show them as "chance of above, near, or below normal".

## SMS and WhatsApp delivery

| Channel | Terms that matter | Source |
| --- | --- | --- |
| WhatsApp Cloud API (Meta) | Per-message pricing since 1 July 2025. Template messages (marketing, utility, authentication) can start a conversation. Free-form messages only inside a 24-hour window after the user writes. The first 1,000 service messages per month per business number are free | https://developers.facebook.com/docs/whatsapp/pricing/ |
| Twilio SMS, India | Domestic traffic requires company and Sender ID registration on the operators' DLT portal, and every template must be approved and allowlisted. Listed price $0.0832 per message for international numbers (search snippet) | https://twilio.com/en-us/guidelines/in/sms and https://www.twilio.com/en-us/sms/pricing/in |
| twilio (Python client) | Library only | MIT, 9.13.0, https://pypi.org/pypi/twilio/json |

Assessment:

- Both channels need a business account, a verified number, and, for India SMS, DLT registration that takes time. That is not possible during the hackathon.
- WhatsApp suits a "send me my report" flow: the farmer messages first, which opens the 24-hour window, and the bot replies with a short summary and a link. Replies within that window fall under service messages, which have a free monthly allowance.
- SMS fits a 160-character summary such as the top strategy and one local check. Any message needs explicit opt-in from the farmer.
- Sending messages costs money and stores phone numbers, which is personal data. The Space Apps rules forbid personal data in submissions (`research/02_hackathon/rules_judging.md`).

Recommendation: leave SMS and WhatsApp out of the hackathon build. In the video or slides, show a mock of a short WhatsApp summary as future work, labelled as a mock. Long term, add a WhatsApp Cloud API webhook as a separate service, and use a printable one-page PDF or a shareable link as the free low-bandwidth channel first.

## Low-bandwidth design notes

- Keep the first page under a few hundred kilobytes before map tiles (target, not measured).
- Offer a text-only report view and a print view.
- Cache the last report offline with the PWA (`frontend.md`).
- Use vector basemaps and small PMTiles extracts instead of high-resolution imagery by default.

## Sources

- Nominatim usage policy: https://operations.osmfoundation.org/policies/nominatim/
- Photon: https://photon.komoot.io/ and https://github.com/komoot/photon
- Open-Meteo pricing and terms: https://open-meteo.com/en/pricing
- Open-Meteo seasonal API: https://open-meteo.com/en/docs/seasonal-forecast-api
- Open-Meteo features: https://open-meteo.com/en/features
- OpenTopography developers: https://opentopography.org/developers
- Open-Elevation: https://github.com/Jorl17/open-elevation
- MPC SAS tokens: https://planetarycomputer.microsoft.com/docs/concepts/sas/
- NOAA CPC: https://www.cpc.ncep.noaa.gov/
- WhatsApp pricing: https://developers.facebook.com/docs/whatsapp/pricing/
- Twilio India SMS guidelines: https://twilio.com/en-us/guidelines/in/sms
- Twilio India SMS pricing: https://www.twilio.com/en-us/sms/pricing/in
- PyPI JSON API, queried 14 November 2026: https://pypi.org/pypi/{package}/json
