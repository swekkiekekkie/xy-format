# P1-B — Structural preset path fixtures

> **Status:** captured

**Capture procedure:**
capture recipe in [`docs/workflows/phase_1_2_fixture_generation_plan.md`](../../../../docs/workflows/phase_1_2_fixture_generation_plan.md)

6 files. T1 preset identity @ struct `+0x453F` (`category/preset-name`).

| File | Path |
| --- | --- |
| `e0-baseline-empty.xy` | `drum/boop` |
| `e1-t1-drum-pp.xy` | `drum/pp` |
| `e2-t1-drum-aeroplane.xy` | `drum/nt-aeroplane` |
| `e3-t1-sampler-106bass.xy` | `bass/nt-106 bass` |
| `e4-t1-axis-accord.xy` | `wind/nt-accord` |
| `e5-t1-engine-only-no-preset.xy` | `/` |

Log: `docs/logs/2026-06-12_preset_path_structural.md`  
Tests: `tests/test_preset_path_structural.py`  
API: `xy/preset_path_inspection.py`
