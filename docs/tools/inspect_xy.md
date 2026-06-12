# inspect_xy.py

`tools/inspect_xy.py` emits a multi-section report for a single `.xy` file.

## Current Coverage
- Header summary.
- Pattern directory/pre-track observations.
- Structural track preset paths @ `+0x453F` (`xy/preset_path_inspection.py`) —
  short `category/name` strings; works on blank patterns.
- Active track/pattern preset-reference inference when project bodies expose
  preset folder or fragmented preset-name strings (`xy/project_inspection.py`).
- Drum-engine track voices: paths plus tune/play/direction/pan/start/end/gain/fade
  (`xy/drum_sample_inspection.py`).
- Per-track scan and event summaries.
- EQ/global snippets.

## Usage
- `python tools/inspect_xy.py 'src/one-off-changes-from-default/unnamed 1.xy'`

## Notes
- Pointer-tail and pointer-21 note decode is still incomplete; see `docs/issues/pointer_tail_decoding.md`.
- Use with `docs/workflows/inspector_sweep.md` for structured corpus validation.
