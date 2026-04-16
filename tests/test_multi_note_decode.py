"""Golden decoded-note matrix for multi-note 0x25 / 0x21 events.

Locks down the decoded notes/steps/gates for every file in the corpus
with multi-voice event payloads. These were previously reported with
wrong steps and missing gates by the inspector's legacy heuristic
parser; the unified parser in ``xy/note_reader.read_event`` now
handles them for the standard sequential encoding.

If a parser change breaks one of these, the regression will tell you
which file, which track, and which note went off.
"""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.inspect_xy import build_track_infos
from xy.structs import find_track_blocks, find_track_handles


CORPUS = REPO_ROOT / "src" / "one-off-changes-from-default"


def _decoded_notes(filename: str):
    """Return list of (track_index_1based, note_tuples) for every
    multi-note event on the file. Each note_tuple is
    ``(note, velocity, step, gate_ticks_or_None)``.
    """
    data = (CORPUS / filename).read_bytes()
    handles = find_track_handles(data)
    blocks = find_track_blocks(data)
    infos = build_track_infos(data, handles, blocks)
    out = []
    for info in infos:
        for event in info.events:
            if event.count < 2:
                continue
            if event.variant not in {"sequential", "hybrid-tail", "inline"}:
                continue
            tuples = tuple(
                (n.note, n.velocity, n.step, n.gate)
                for n in event.notes
            )
            # info.index is already 1-based in TrackInfo.
            out.append((info.index, tuples))
    return out


def test_unnamed_80_t1_six_note_sequence_decodes_cleanly() -> None:
    """Ground truth (change log): C4@1, D4@5, E4@9, F4+G4+A4 chord @13."""
    decoded = _decoded_notes("unnamed 80.xy")
    assert len(decoded) == 1
    track, notes = decoded[0]
    assert track == 1
    assert notes == (
        (0x3C, 100, 1, None),   # C4
        (0x3E, 100, 5, None),   # D4
        (0x40, 100, 9, None),   # E4
        (0x45, 40, 13, None),   # A4 (chord)
        (0x43, 37, 13, None),   # G4 (chord)
        (0x41, 42, 13, None),   # F4 (chord)
    )


def test_unnamed_94_t1_drum_pair_decodes_cleanly() -> None:
    """Ground truth: MIDI harness T1 Drum C4@step1 + D4@step5, gate=480."""
    decoded = _decoded_notes("unnamed 94.xy")
    assert (1, (
        (0x3C, 100, 1, 480),
        (0x3E, 100, 5, 480),
    )) in decoded


def test_unnamed_101_t1_full_drum_pattern_decodes_cleanly() -> None:
    """Ground truth: 4-bar drum groove with kick/snare/hats, 48 notes on T1."""
    decoded = _decoded_notes("unnamed 101.xy")
    # T1 has 48 notes; other tracks may also have multi-note events.
    t1_events = [(tr, n) for tr, n in decoded if tr == 1]
    assert len(t1_events) == 1, t1_events
    _, notes = t1_events[0]
    assert len(notes) == 48
    # Spot-check the first bar pattern (drums on steps 1/3/5/7/9/11/13/15 etc).
    first_four = notes[:4]
    assert first_four == (
        (0x38, 70, 1, None),   # hat step 1
        (0x30, 120, 1, 480),   # kick step 1
        (0x38, 70, 3, None),   # hat step 3
        (0x3A, 80, 5, None),   # open hat step 5
    )
    # Every decoded step should be 1..64 (4 bars x 16 steps).
    for note_val, vel, step, _gate in notes:
        assert 1 <= step <= 64, (note_val, vel, step)
        assert 0 <= note_val <= 127
        assert 1 <= vel <= 127


def test_unnamed_93b_t1_two_notes_decode_cleanly() -> None:
    """``unnamed 93b`` is a 2-note specimen; locks the decode shape."""
    decoded = _decoded_notes("unnamed 93b.xy")
    # At least one event with 2 notes on T1
    t1 = [n for tr, n in decoded if tr == 1]
    assert t1, decoded
    for notes in t1:
        assert len(notes) == 2
        for note_val, vel, step, _gate in notes:
            assert 0 <= note_val <= 127
            assert 0 < vel <= 127
            assert 1 <= step <= 64


def test_unnamed_3_chord_heuristic_fallback_preserves_note_identities() -> None:
    """``unnamed 3`` uses a device-native tick encoding the unified
    parser rejects; we fall back to the legacy heuristic, which gets
    the note identities right but may lose step/gate precision.

    This test locks in that fallback still yields the C-E-G triad.
    """
    decoded = _decoded_notes("unnamed 3.xy")
    assert len(decoded) == 1
    track, notes = decoded[0]
    assert track == 1
    note_pitches = sorted(n for n, _, _, _ in notes)
    assert note_pitches == [0x3C, 0x40, 0x43], note_pitches  # C4, E4, G4
