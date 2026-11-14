# Challenge video and the people behind it

Source: https://www.youtube.com/watch?v=cF0U2WXsM7o (embedded on the Details tab). The video is 217 seconds long and has captions in 21 languages, including Hindi, Punjabi, Bengali, Tamil, Telugu, and Malayalam. Its description says it includes generated imagery. We read the English captions on 2026-11-14 with `youtube-transcript-api`.

We re-read the Details and Resources tabs on 2026-11-14. Both match the 2026-11-13 snapshot in `details.md` and `resources.md` word for word. NASA has added no new resources.

## What the video asks for

The first half is a narrated teaser. It names five signals: rainfall, soil moisture, heat, vegetation, and water. It frames them as "different observations, different scales, pieces of the same story".

The mission statement in the video has four verbs that the written text does not stress as much:

- "Compare rotations"
- "reveal trade-offs"
- "understand risk"
- "make uncertainty visible"

It then lists accepted forms: an SI model, an interactive map, a visualization, or a decision-support tool. It also invites "something none of us has imagined yet".

## Who wrote the challenge and who judges the science

All four speakers work at NASA Johnson Space Center (JSC), not at an Earth science centre such as Goddard or JPL.

| Person | Role stated in the video | What it suggests for us |
|---|---|---|
| Sadie Burnett Boudro | Challenge author. Engineer and developer supporting Artemis mission management and integration. | The author cares about integration and a working tool, not only science. |
| Mani Deep Gogineni | Data solutions architect. Builds custom web apps and tooling. | A clean, working web app and sound data architecture will register with this reviewer. |
| William Stefanov | Senior Earth system scientist. Works with Earth imagery from the ISS for disaster response and remote sensing science. Named subject matter expert for this challenge. | ISS-hosted data and honest remote sensing caveats will register. |
| Alex Stoken | Data scientist in the JSC Earth Science and Remote Sensing Unit. Applies machine learning to astronaut photography of Earth. | The SI part should be real and explainable, not decoration. |

## Takeaways for design

1. Treat "make uncertainty visible" as a first-class requirement. Every number the tool shows should carry a confidence or range, and the interface should show it, not hide it in a footnote.
2. Lead with trade-offs, not a single winner. A side-by-side comparison of at least three rotations, with what each one gains and loses, matches the video's wording better than a single recommended answer.
3. Use at least one ISS-hosted dataset where it truly helps. The challenge text already names two: ECOSTRESS (heat and ET at about 70 m) and GEDI (canopy structure). Astronaut photography and EMIT are also ISS sources. A separate research note checks whether they are useful for a farm field.
4. Captions exist in Hindi and Punjabi. NASA is clearly thinking about a global, multilingual audience, which supports a multilingual output feature.

## Sources

- https://www.youtube.com/watch?v=cF0U2WXsM7o
- https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/?tab=details
- https://www.spaceappschallenge.org/2026/challenges/adapting-farms-with-nasa-data/?tab=resources
