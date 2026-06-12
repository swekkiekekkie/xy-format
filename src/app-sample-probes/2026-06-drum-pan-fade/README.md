# M3 — Drum pan vs fade fixtures

> **Status:** captured

**Capture procedure:**
capture recipe in [`docs/workflows/phase_1_2_fixture_generation_plan.md`](../../../../docs/workflows/phase_1_2_fixture_generation_plan.md)

24 files. T1 drum `pp`, voice **23** (low F kick, key 53). Fade stored on **v22**.

| File | Change |
| --- | --- |
| `d0-baseline-pp.xy` | baseline |
| `d1-v23-pan-hard-left.xy` | pan −100 @ v23 `+0x06` |
| `d2-v23-pan-hard-right.xy` | pan +100 @ v23 `+0x06` |
| `d3-v23-fade-01`…`14.xy` | fade UI 1–14 → v22 `+0x7C` |
| `d3-v23-fade-27/63/99.xy` | fade high/mid/max (legacy byte0) |
| `d3-v23-fade-44`…`47.xy` | fade UI 44–47 |

Encoding: `u32 = ui × 0x0147AF00`, max `0x7FFFFFFF`.

Log: `docs/logs/2026-06-12_drum_pan_fade_inspection.md`  
Tests: `tests/test_drum_pan_fade_inspection.py`
