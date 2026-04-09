# Profile comparisons (what changed and why)

Plain-language notes comparing pairs of runs from `python -m src.main`. Think of it as explaining the terminal to someone who will never read the code.

## High-energy pop vs chill lofi

**What changed:** The winner list stops being about peppy, produced hooks and slides toward softer drums, higher acousticness numbers, and the `lofi` label.

**Why that makes sense:** Chill lofi turns on the `likes_acoustic` flag, so songs that are basically pillow-textured (**Library Rain**, **Midnight Coding**) pick up honest points. Pop profiles were biased toward crunchy, synth-heavy masters because acoustic tracks lose that branch.

## High-energy pop vs deep intense rock

**What changed:** The top slot jumps from “bright happy pop” (`Sunrise City`) to “angry tempo” rock (`Storm Runner`), and mood `intense` becomes part of the bonus.

**Why that makes sense:** Same energy target ballpark, different mood keyword—so the recommender stops paying the +1 happy bonus to Rooftop Lights and pays intense where it exists. Gym Hero still sneaks high for rock because it carries intense mood even though the genre is pop—useful, because it exposes how mood matching can drag tracks across aisle lines.

## Chill lofi vs adversarial (moody + max energy)

**What changed:** Chill profiles anchored near 0.35 energy; the adversarial profile cranks energy to 0.95 while keeping mood `moody`.

**Why that makes sense:** You get a tug-of-war: mood match pulls toward **Night Drive Loop** (synthwave + moody), but the huge energy gap penalty hurts softer moody songs. **Gym Hero** rises because it is loud, intense pop that still clears the genre bump—even though “moody” is not its label—which is exactly the kind of edge case that reminds you metadata tags are imperfect.

## Pop default vs weight experiment (README)

**What changed:** When I halved genre weight and doubled the energy cap, the middle ranks shuffled more than the absolute #1 in my run, because several contenders already sat close to the 0.8 energy target.

**Why that makes sense:** You told the scorer to care less about the sign on the genre column and more about being near the numeric vibe. That is how real product teams accidentally ship “everything feels the same tempo” if they over-correct.
