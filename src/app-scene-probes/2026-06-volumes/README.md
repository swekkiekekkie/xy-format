# P2-D — Scene volume fixtures

> **Status:** captured

**Capture procedure:**
capture recipe in [`docs/workflows/phase_1_2_fixture_generation_plan.md`](../../../../docs/workflows/phase_1_2_fixture_generation_plan.md)

8 files. Use **s0b** series as canonical (distinct scene patterns).

| File | Finding |
| --- | --- |
| `s0b-baseline-2scenes.xy` | default T vol `0x60`, master `0x40` |
| `s1b-scene1-t1-vol-low.xy` | scene 1 T1 @ T1+0x38FE → `0x00` |
| `s2b-scene2-t1-vol-high.xy` | scene 2 T1 @ T2+0x38FE → `0x7F` |
| `s5b-scene1-master-vol.xy` | master @ global+0x94 → `0x7F` |
| `s0-baseline-2scenes.xy` … | flawed baseline (spurious s2 diffs) |

Log: `docs/logs/2026-06-12_scene_volume_inspection.md`  
Tests: `tests/test_scene_volume_inspection.py`  
API: `xy/scene_volume_inspection.py`
