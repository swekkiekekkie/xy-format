# 2026-06-12 Drum sample path inspection

Read-only extraction of per-voice sample path strings from the drum sampler
table (24 × 128 B at track `+0x3957`, path at slot `+0x08`).

AI-assisted implementation; claims are fixture-backed (round 1 captures below).

## Round 1 captures (canonical)

Operator README:
`opxy_mtp_manager/.../user_probes/2026-06-sample-paths/README.md`.

| File | Pad (UI) | Voice | MIDI key | Sample | Slot path |
|------|----------|-------|----------|--------|-----------|
| `c1-baseline-pp.xy` | — | — | — | `pp` kit | all `…/pp.preset/unnamed-….wav` |
| `c1-pad01-lowf-v23-chi-box.xy` | 1, leftmost **low F** | **23** | 53 F3 | chi box | `content/samples/perc/chi box.wav` |
| `c1-pad02-v00-chi-cham.xy` | 2 | **0** | 54 F#3 | chi cham | `content/samples/perc/chi cham.wav` |
| `c1-pad03-v01-chi-flet.xy` | 3 | **1** | 55 G3 | chi flet | `content/samples/perc/chi flet.wav` |

Each variant is saved from baseline with **one** voice changed; decoded diffs
confirm single-slot isolation.

## Pad index vs voice index (`pp` kit)

The OP-XY drum grid is **not** “voice 0 = leftmost pad” for this kit.

On `pp`, the **leftmost keyboard pad (low F)** maps to **voice 23** (lowest
key in the 24-slot table). The next pad right is voice 0 (F#3), then voice 1
(G3), and so on. Only indices **0–23** exist.

Generic docs sometimes describe “v0 kick … v23 chi” as a factory layout story;
**kit `pp` permutes keys** so the lowest physical pad is slot 23.

## Path anatomy: preset-nested vs library-relative

### Kit-embedded samples (`pp` defaults)

```
/fat32/presets/drum/pp.preset/unnamed-f#2-31.wav
                 ^^              ^^^^^^^^^^^^^^^
           preset bundle    opaque generated name
```

The **drum preset name** (`pp`) is part of the path. User-added kits often
keep the `unnamed-…` pattern, which makes eyeballing assignments hard.

### Built-in / browser picks (`perc/chi *`)

```
content/samples/perc/chi box.wav
                ^^^^ ^^^^^^^^^^^
         sample folder   display name
```

- `perc` here is the **sample library category**, not a `.preset` file.
- The slot does **not** become `/fat32/presets/drum/perc.preset/...`.
- Track-level kit string remains `drum/pp` (~`+0x453F`) while individual
  voices can point at `content/samples/...` paths.

Fragment strings (`chi box`, `perc/chi box.wav`) may also appear elsewhere in
the track image (browser/history); authoritative assignment is the **voice
slot path at `+0x08`**.

## Implementation

- `xy/drum_sample_inspection.py` — reads paths from decoded RAM image via
  `ImageProject` track bases (not scaffold logical-entry bodies).
- `tools/inspect_xy.py` — `[Drum Samples]` section.
- Tests: `tests/test_drum_sample_inspection.py`.

## Round 0 (superseded)

Earlier captures using `nt-z-fx` user presets and `unnamed-…` samples.
Archived in user_probes `archive-round0-nt-z-fx/`. Round 1 replaced them with
named built-in `perc/chi *` samples for verifiability.

## Open questions

- Sampler / multisampler non-drum path layout.
- Whether user `.preset` drum kits always use `/fat32/presets/drum/<kit>.preset/…`
  or can emit `content/samples/…` for some slots.
- Full pad-grid → voice-index map for kits other than `pp`.
