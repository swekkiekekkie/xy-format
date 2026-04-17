"""Extract decoded intent from an .xy file as a ``BuildSpec`` JSON dict.

This is the inverse of ``xy/json_build_spec.py``: it reads a binary
``.xy`` project and produces a dict that, when passed back through
``build_xy_bytes`` with the same template, produces functionally
equivalent output.

Round-trip strength: **intent round-trip, not byte-exact.** Fields the
encoder understands are extracted and re-applied; everything else
comes from the scaffold template unchanged. Two files with different
undecoded state can therefore produce the same JSON but different
bytes — that's expected, and is why this emits a ``template`` field.

What's decoded today (matching the current profile catalog):
- Header transport: tempo, groove type/amount, metronome level
- Per-track notes on pattern 1 (the top-level track block) for every
  single-pattern track, via ``xy/note_reader.read_event``

What's **not** decoded (stays opaque in the scaffold):
- Multi-pattern clone bodies (patterns 2..N live in the overflow
  region; reading them needs the block-rotation walker which is not
  yet wired to this path)
- Scene and song state
- Engine parameters, envelopes, filter, LFO, preset references
- Step components, parameter locks
- Mix/master controls

For the fields it doesn't decode, the round-trip story is: edit the
JSON's decoded fields, keep ``template`` pointing at the original
file, and ``build_xy_bytes`` will re-apply your intent on top of the
template's undecoded bytes.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

from .container import XYContainer, XYProject
from .note_reader import read_track_notes
from .profiles import PROFILES, infer_profile


SUPPORTED_SPEC_VERSION = 1
BASELINE_PRE_TRACK_LEN = 0x7C  # 124: the baseline single-pattern length
DESCRIPTOR_V56_OFFSET = 0x56
DESCRIPTOR_V57_OFFSET = 0x57


def _looks_multi_pattern(project: XYProject) -> bool:
    """Detect whether the project uses multi-pattern topology.

    A single-pattern project has ``v56 == 0 and v57 == 0`` AND a
    baseline-length pre-track (``0x7C`` bytes). Multi-pattern files
    set v56/v57 for T1/T2 multi-pattern, or insert a longer pre-track
    to accommodate the Scheme A descriptor body at ``0x58``.

    A handful of corpus files have shorter pre-tracks (119-123 bytes)
    from older firmware versions; those are conservatively treated as
    single-pattern because their v56/v57 bytes are zero and they
    never carry a multi-pattern descriptor.

    See docs/format/descriptor_encoding.md for the authoritative
    layout.
    """
    pre_track = project.pre_track
    if len(pre_track) < 0x58:
        return False
    v56 = pre_track[DESCRIPTOR_V56_OFFSET]
    v57 = pre_track[DESCRIPTOR_V57_OFFSET]
    if v56 != 0 or v57 != 0:
        return True
    # v56==0 and v57==0: T1 and T2 are single-pattern. A longer
    # pre-track still indicates a Scheme A descriptor for T3+ tracks
    # was inserted.
    return len(pre_track) > BASELINE_PRE_TRACK_LEN


def _note_to_dict(note) -> Dict:
    """Serialise a ``Note`` into the JSON shape ``BuildSpec`` expects."""
    out: Dict = {
        "step": note.step,
        "note": note.note,
        "velocity": note.velocity,
    }
    if note.tick_offset:
        out["tick_offset"] = note.tick_offset
    if note.gate_ticks:
        out["gate_ticks"] = note.gate_ticks
    return out


def _extract_track_patterns(
    project: XYProject,
) -> List[Dict]:
    """Return the JSON ``tracks`` array, one entry per track with notes.

    Only pattern 1 (the top-level track block body) is emitted. Tracks
    with no decodable notes are omitted from the list — they'd add
    noise and the template carries their state regardless.
    """
    tracks: List[Dict] = []
    for idx, track in enumerate(project.tracks):
        if track.type_byte == 0x05:
            # Inactive track (padding still present). No note payload.
            continue
        notes = read_track_notes(track, idx + 1)
        if not notes:
            continue
        tracks.append({
            "track": idx + 1,
            "patterns": [[_note_to_dict(n) for n in notes]],
        })
    return tracks


def project_to_json(
    xy_bytes: bytes,
    *,
    template_path: Path,
) -> Dict:
    """Extract decoded project intent from an .xy file.

    Parameters
    ----------
    xy_bytes : bytes
        The full ``.xy`` file contents.
    template_path : Path
        Path to the file that will be used as the scaffold template
        on re-build. Typically this is the same file being read —
        round-tripping applies the extracted intent on top of the
        original bytes. The path is embedded in the returned dict.

    Returns
    -------
    dict
        A ``BuildSpec`` payload with a declared profile that matches
        what was decoded. Can be fed back into
        ``xy.json_build_spec.parse_build_spec`` and
        ``build_xy_bytes`` for a round-trip.

    Notes
    -----
    The returned ``profile`` is inferred from decoded content. If the
    file has multi-pattern topology that wasn't captured in ``tracks``,
    the profile will be ``header_only`` (safe — only tempo/groove/
    metronome round-trip). Extending decode coverage (e.g. multi-
    pattern clone walking) will allow richer profiles to be inferred.
    """
    project = XYProject.from_bytes(xy_bytes)
    container = XYContainer.from_bytes(xy_bytes)
    header = container.header

    # Multi-pattern projects store patterns 2..N in overflow blocks
    # that our top-level-blocks-only extraction can't reach. Emitting
    # ``single_pattern_notes`` for them would ask the builder to
    # re-encode only pattern 1, which would break the template's
    # clone state. For those, we only surface decoded header intent.
    multi_pattern = _looks_multi_pattern(project)
    tracks = [] if multi_pattern else _extract_track_patterns(project)

    payload: Dict = {
        "version": SUPPORTED_SPEC_VERSION,
        "mode": "multi_pattern",
        "template": str(template_path),
        "header": {
            "tempo_tenths": header.tempo_tenths,
            "groove_type": header.groove_type,
            "groove_amount": header.groove_amount,
            "metronome_level": header.metronome_level,
        },
    }

    # Always include ``tracks`` (possibly empty) so ``parse_build_spec``
    # doesn't trip on the field being absent.
    payload["tracks"] = tracks
    # If multi-pattern, note the limitation in a ``_notes`` key the
    # reader can surface. (``_``-prefixed keys are ignored by the
    # BuildSpec parser.)
    if multi_pattern:
        payload["_notes"] = [
            "multi-pattern topology detected: pattern 2+ bodies are "
            "in the overflow region and not decoded by project_to_json "
            "yet. Only header changes will round-trip."
        ]

    # Infer the profile by running the same validators the build path
    # uses, against the payload we just assembled. Prefer the most
    # specific profile that matches.
    payload["profile"] = _infer_profile_from_payload(payload)

    return payload


def _infer_profile_from_payload(payload: Dict) -> str:
    """Pick the most-specific profile this payload fits.

    We mimic ``build_spec``'s parse step with a minimal in-memory
    object so we can call ``infer_profile`` from ``xy.profiles``.
    This avoids importing ``json_build_spec`` (which imports this
    module's peer ``project_builder`` and would risk a circular
    import).
    """
    # Build a lightweight duck-typed spec object for profile inference.
    class _FakeHeader:
        def __init__(self, hdr: Dict) -> None:
            self.tempo_tenths = hdr.get("tempo_tenths")
            self.groove_type = hdr.get("groove_type")
            self.groove_amount = hdr.get("groove_amount")
            self.metronome_level = hdr.get("metronome_level")

        def has_changes(self) -> bool:
            return any(
                v is not None
                for v in (
                    self.tempo_tenths,
                    self.groove_type,
                    self.groove_amount,
                    self.metronome_level,
                )
            )

    class _FakeSceneSong:
        def has_changes(self) -> bool:
            return False

    class _FakeTrackEntry:
        def __init__(self, track: int, patterns: List) -> None:
            self.track = track
            # Convert each pattern's notes list into a proxy list; only
            # the length matters to the validator, so we can pass raw
            # note dicts directly.
            self.patterns = [list(p) if p else None for p in patterns]

    class _FakeSpec:
        def __init__(self) -> None:
            self.mode = payload.get("mode", "multi_pattern")
            self.header = _FakeHeader(payload.get("header", {}))
            self.scene_song = _FakeSceneSong()
            self.scene_assignments = {}
            self.song_arrangement = []
            self.descriptor_strategy = "strict"
            self.topology_policy = "none"
            self.multi_tracks = [
                _FakeTrackEntry(t["track"], t["patterns"])
                for t in payload.get("tracks", [])
            ]

    fake = _FakeSpec()
    inferred = infer_profile(fake)
    if inferred is None:
        # Nothing decoded that matches a profile — safest is header_only
        # if the header decoded, otherwise we can't say.
        if fake.header.has_changes():
            return "header_only"
        raise ValueError(
            "project_to_json: could not infer a profile from decoded "
            "content. File may have no decodable intent in the current "
            "profile catalog."
        )
    return inferred
