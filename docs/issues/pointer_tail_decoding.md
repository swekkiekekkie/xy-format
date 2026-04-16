# Issue: Pointer-Tail Note Decode Gaps

## Status (2026-04-16 update)

**Multi-note 0x25 events (previously classified `hybrid-tail`) now decode
cleanly for the standard sequential encoding.** The inspector routes
events that use the continuation-byte state machine through
`xy/note_reader.read_event`, which was already the correct decoder for
0x21 events. The unified parser recovers note, velocity, step, and gate
for every multi-note 0x25 event in the corpus except `unnamed 3`, which
uses a device-native variable-length tick encoding the unified parser
does not yet handle. For `unnamed 3` the inspector falls back to the
legacy tail-word heuristic (correct note identities, imperfect step/gate).

Regression coverage: `tests/test_multi_note_decode.py` locks the
decoded notes for `unnamed 80` (6-note sequence with chord), `unnamed
94` (MIDI-harness drum pair with gate 480), `unnamed 101` (48-note
4-bar drum groove), `unnamed 93b`, and `unnamed 3` (fallback path).

**Still open**:
1. **Pointer-21 events** (202 corpus files). Different header layout
   (`21 00 <count_u16_le> …` rather than `21 <count:byte> …`) and the
   payload lives in pointer-referenced slabs, not inline. The unified
   sequential parser rejects these. Decode work is the same as the
   historical notes in this issue — no change.
2. **`unnamed 3` tick encoding**. The native variable-length form
   (flag 0x00 with 2 extra bytes before the gate field) needs a
   parser extension in `xy/note_reader.read_event`.

## Summary
- Pointer-21 blocks (variant 0 / live-record events) still report `note data unresolved`.
- Per-voice node records at `track+0x16xx` mingle live note nodes with static lookup tables, so naïvely reading every 16-byte slice prints garbage (e.g. remnant preset tables, parameter defaults).
- Without a reliable rule for identifying real nodes and converting the `step_token` / `gate` words into track steps, the report would mis-state note positions and durations for pointer-21 events.

## Latest Investigation (2024-xx-xx)
- Triad / chord captures (`unnamed_3`, `unnamed_80`) show the pointer tail landing on:
  - `track+0x1600` → step bitmap / node headers (`0xDF00`, `voice_id`, `note`, `step_token`, `gate_ticks`).
  - `track+0x1680` and beyond → follow-on slabs whose layout still needs decoding (likely micro offset, allocator state).
  - `track+0x10F0` → parameter slabs (voice envelopes, filter state) – not directly needed for inspector output.
- Inline single-note captures (`unnamed_81`) do **not** allocate these slabs, which confirms the nodes are only present for stacked voices / pointer-driven notes.
- Pointer-21 captures (`unnamed_38`, `unnamed_39`, `unnamed_65`, `unnamed_87`) exhibit the same pointer ladder but with `count=0` or `count=1` headers; the musical data lives entirely in the slabs referenced from the tail.

## Data We Can Trust Today
- `tail_entries` already expose a clean note/velocity pair whenever the velocity byte is > 1. Those values match the change-log descriptions.
- Pointer arrays (`swap_hi`, `swap_lo`) correctly resolve to track-relative offsets; we can log these addresses without guessing at their structure.
- Inline single-note (fine tick) events are decoded correctly and already pass regression coverage.

## Blockers
- Need a deterministic rule to differentiate “live” per-voice nodes from static tables inside `track+0x16xx`.
- Require a formula for turning the `step_token` word into 0-based step indices (triad captures suggest multiples of six, but the pattern breaks on multi-pattern files).
- Gate ticks in these slabs must be verified against controlled captures (e.g., known 2-step / 4-step gates) before we surface them in the report.

## Proposed Next Steps
1. Build a corpus sweep that compares every `track+0x16xx` slice in a chord file against the baseline to isolate strictly the mutated slabs.
2. Capture additional pointer-tail examples with notes on steps {1, 5, 9, 13} and varying gates; document how `step_token` and `gate` change per step.
3. Once mapping is proven, extend `tools/inspect_xy.py` so pointer-tail events emit real `step=` / `beat=` / `gate=` values, and add regression tests for triad & chord cases.
4. Mirror the same decode path for pointer-21 events so live-recorded takes stop emitting the placeholder “note data unresolved”.

## Related Files / Work
- Code: `tools/inspect_xy.py` (tail parsing, pointer metadata).
- Docs: `docs/pointer_tail_notes.md` (structure notes), `docs/format/events.md` (canonical format summary), `docs/logs/2026-02-13_agents_legacy_snapshot.md` (full historical log).
- Tests:
  - `tests/test_inspector_outputs.py` currently fail if bogus extra notes appear; they will need extra assertions once decoding lands.
  - `tests/test_pointer_tail_characterization.py` pins current pointer-tail / pointer-21 event classification behavior for known fixtures.
