# P2-G — Master saturator fixtures

> **Status:** captured

**Capture procedure:**
capture recipe in [`docs/workflows/phase_1_2_fixture_generation_plan.md`](../../../../docs/workflows/phase_1_2_fixture_generation_plan.md)

9 files. Level bytes @ `0x78` / `0x7C` / `0x80` / `0x84` (mixer-style `u32+3`).

| File | Gain | Clip | Tone | Mix |
| --- | --- | --- | --- | --- |
| `sat0-baseline.xy` | `0x19` | `0x19` | `0x40` | `0x00` |
| `sat1-gain-min.xy` | `0x00` | | | |
| `sat2-gain-max.xy` | `0x7F` | | | |
| `sat3-clip-min.xy` | | `0x00` | | |
| `sat4-clip-max.xy` | | `0x7F` | | |
| `sat5-tone-min.xy` | | | `0x00` | |
| `sat6-tone-max.xy` | | | `0x7F` | |
| `sat7-mix-min.xy` | | | | `0x00` (= baseline) |
| `sat8-mix-max.xy` | | | | `0x7F` |

Log: `docs/logs/2026-06-12_master_saturator_inspection.md`  
Tests: `tests/test_master_saturator_inspection.py`  
API: `xy/master_saturator_inspection.py`
