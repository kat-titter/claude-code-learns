---
name: beat-align-audio
description: Beat-aligns two pieces of music before they overlap (DJ transitions, mashups, stitched tracks, a loop or stem over a song) so kicks land together with no flam. Use when code overlaps two musical signals, or when a mix sounds flammy, galloping, off-beat, bumpy or "not smooth" even though the tempos match.
when_to_use: Before rendering any beat-matched overlap of two tracks; when a listener says a transition is rough, jumping or not blended.
---

# Beat-align audio: local phase + waveform match + look at it

## The trap
A global constant-tempo grid from a beat tracker (beat_this, madmom, librosa) is NOT
safe to cut and overlap on. Seen in practice (a DJ set, 2026-09-26):
- beat_this beats are quantised to its frame rate (50 fps = 20 ms steps);
- beats get lost/doubled in breakdowns, so ONE lattice fitted to the whole track fails
  (only 3-30% of beats fit on steady house tracks);
- downbeat-phase anchors were off by up to ~half a beat -> kicks flam in the overlap;
- "steepest rise" of a folded kick envelope lands early on long (808/organic) kicks;
- autocorrelation "beat clarity" and half-beat ratios CANNOT detect a flam (two kick
  trains half a beat apart are still periodic; the tracks' own bass patterns confound it).

## The procedure that worked
1. **Fix the grid phase locally** at each mix point (not globally): take ~20-30 bars
   of the drum stem (demucs) around the cue, low-pass <150 Hz, amplitude envelope,
   fold onto one beat period, take the **energy peak** minus ~12 ms attack. Shift the
   grid there. Skip when fold contrast (peak/mean) < 1.3 (no real kick).
2. **Waveform-match the two decks**: cross-correlate onset envelopes of the two drum
   stems over the overlap, search +-2 beats at ~1.5 ms hop, parabolic refine; on
   near-ties (within 3%) prefer the smallest shift. Apply **whole-beat** moves only if
   the normalised score >= 0.6, otherwise keep bar phase and apply the sub-beat part.
3. **Verify visually before claiming it's fixed**: render stacked drum waveforms of
   both decks with beat lines (entry and swap). Kicks must sit on the same lines.
   `python ${CLAUDE_SKILL_DIR}/scripts/check_beat_alignment.py out.wav in.wav --bpm 120 --out-start 30 --in-start 0`
4. **Measure jumps** separately: half-bar loudness steps (pyloudnorm) across the transition;
   > 3 dB steps are audible jumps. Fix with equal-power crossfades, entry fades, a slow
   gain rider, and choosing out/in points whose energy curves sum flat.

5. **Check the time-stretcher keeps time.** Rubber Band's offline mode and its R3
   (finer) engine distribute the stretch unevenly to protect transients: total length
   is exact but beats drift 20-80 ms mid-file. Use R2 (ENGINE_FASTER) in
   PROCESS_REALTIME mode, compensating get_preferred_start_pad / get_start_delay, then
   trim to round(n * ratio). Verify with kick timing: detect kicks (<120 Hz envelope
   peaks) in source and output, compare against source_time * ratio; p5-p95 should be
   within ~+-7 ms. Envelope cross-correlation on full music is NOT a valid check
   (repetitive 8ths/16ths lock onto the wrong hit).

## Gotchas
- **A nudge that hits its cap** (a quarter beat) means the grid is wrong: re-fit the grid from the kicks.
- **A stretcher's timing** is proven by measured kicks; a correct output length alone says little.
- **Blend swaps over hard swaps** by default: a drop-swap or hard swap tends to create a structural jump.
- **Claude has no ears: report measurements, and the listener gives the verdict.** Describe a take by its kick offsets,
  level steps and beat clarity, with how it sounds left to the person (a DJ tool, 2026-10-31: "show measurements rather than
  claims, never say a take 'sounds good' (no ears)").

## Echo throws between two tempos

- High-pass the echo (about 200 Hz): an unfiltered echo of a full mix is mostly bass (measured: its energy under 150 Hz
  only 1.6 dB below the whole echo), which muds the incoming kick.
- The repeats run on the outgoing's grid. Where the tempos differ, count the repeats heard (to -24 dB) times the per-repeat
  offset against the incoming's same note value; past about 20 ms, fade the repeats out over a beat from the incoming's
  downbeat (BABYLON 135 into PINKY UP 152: 4 repeats, 99 ms off).
- A 'both decks audible' weave meter credits echoed bass as weaving; after the low cut it reads less. Report that trade-off
  to the listener rather than tuning the meter or the echo to pass it.
