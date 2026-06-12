# P2-B — One-shot sampler fixtures

> **Status:** captured (`g0`–`g14`)

**Capture procedure:**
capture recipe in [`docs/workflows/phase_1_2_fixture_generation_plan.md`](../../../../docs/workflows/phase_1_2_fixture_generation_plan.md)

25 files: `g0`…`g14` + tune sweep `g-tune-0`…`g-tune-4`, `g-tune-neg1`…`g-tune-neg5`.
Preset: **`nt-acidic`**.

| File | Field changed |
| --- | --- |
| `g0.xy` | baseline |
| `g1.xy` | tune min |
| `g2.xy` | tune max |
| `g3.xy` | start |
| `g4.xy` | end |
| `g5.xy` | loop start |
| `g6.xy` | loop end |
| `g7.xy` | direction backward |
| `g8.xy` | gain min |
| `g9.xy` | gain max |
| `g10.xy` | loop crossfade min (= baseline) |
| `g11.xy` | loop crossfade max (75% UI) |
| `g12.xy` | loop type off |
| `g13.xy` | loop type until-release |
| `g14.xy` | loop type infinite (= baseline fields) |

Log: `docs/logs/2026-06-12_sampler_oneshot_inspection.md`  
Tests: `tests/test_sampler_sample_inspection.py`  
API: `xy/sampler_sample_inspection.py`
