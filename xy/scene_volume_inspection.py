"""Read mixer volume fields from decoded project images (P2-D probes)."""

from __future__ import annotations

from dataclasses import dataclass

from .image_writer import GLOBAL_SCENE_COUNT, ImageProject, SCENE_SLOT0, SCENE_SLOT_SIZE
from .rle import decode_project

TRACK_MIX_VOL_U32_OFFSET = 0x38FB
TRACK_MIX_VOL_BYTE_OFFSET = 0x38FE
GLOBAL_MASTER_VOL_U32_OFFSET = 0x91
GLOBAL_MASTER_VOL_BYTE_OFFSET = 0x94
MIX_VOL_BYTE_MAX = 0x7F
MIX_VOL_U32_MAX = 0x7FFFFFFF


@dataclass(frozen=True)
class TrackMixVolume:
    track: int
    vol_byte: int
    vol_u32: int

    @property
    def vol_ui(self) -> int:
        """Approximate device UI 0..100 from stored byte (0..0x7F)."""
        return round(self.vol_byte * 100 / MIX_VOL_BYTE_MAX)


@dataclass(frozen=True)
class SceneVolumeInspection:
    scene_count: int
    active_scene_ordinal: int
    master_vol_byte: int
    master_vol_u32: int
    track_volumes: tuple[TrackMixVolume, ...]

    @property
    def master_vol_ui(self) -> int:
        return round(self.master_vol_byte * 100 / MIX_VOL_BYTE_MAX)


def mix_vol_byte_from_u32(u32: int) -> int:
    return (u32 >> 24) & 0xFF


def encode_mix_vol_byte(vol_byte: int) -> int:
    if vol_byte <= 0:
        return 0
    if vol_byte >= MIX_VOL_BYTE_MAX:
        return MIX_VOL_U32_MAX
    return (vol_byte & 0xFF) << 24


def scene_volume_storage_track(scene: int, track: int) -> int:
    """Map (scene, track) to the struct that stores that scene's mix volume.

  Validated on P2-D ``s0b`` captures for scene 1 T1 (→ T1) and scene 2 T1
  (→ T2). Full 16×scene matrix is not closed."""
    if scene < 1 or track < 1:
        raise ValueError("scene and track are 1-based")
    return track + (scene - 1)


def inspect_scene_volumes_bytes(data: bytes) -> SceneVolumeInspection:
    header, image = decode_project(data)
    project = ImageProject(header, bytearray(image))
    project._rescan()
    return inspect_scene_volumes(project)


def inspect_scene_volumes(project: ImageProject) -> SceneVolumeInspection:
    img = project.image
    master_u32 = int.from_bytes(
        img[GLOBAL_MASTER_VOL_U32_OFFSET : GLOBAL_MASTER_VOL_U32_OFFSET + 4],
        "little",
    )
    tracks: list[TrackMixVolume] = []
    for track in range(1, 17):
        base = project.track_start(track)
        u32 = int.from_bytes(
            img[base + TRACK_MIX_VOL_U32_OFFSET : base + TRACK_MIX_VOL_U32_OFFSET + 4],
            "little",
        )
        tracks.append(
            TrackMixVolume(
                track=track,
                vol_byte=img[base + TRACK_MIX_VOL_BYTE_OFFSET],
                vol_u32=u32,
            )
        )
    return SceneVolumeInspection(
        scene_count=img[GLOBAL_SCENE_COUNT] + 1,
        active_scene_ordinal=img[GLOBAL_SCENE_COUNT + 1],
        master_vol_byte=img[GLOBAL_MASTER_VOL_BYTE_OFFSET],
        master_vol_u32=master_u32,
        track_volumes=tuple(tracks),
    )


def read_scene_track_volume(
    project: ImageProject, scene: int, track: int
) -> TrackMixVolume:
    storage = scene_volume_storage_track(scene, track)
    if storage > 16:
        raise ValueError(f"no storage track for scene={scene} track={track}")
    base = project.track_start(storage)
    img = project.image
    u32 = int.from_bytes(
        img[base + TRACK_MIX_VOL_U32_OFFSET : base + TRACK_MIX_VOL_U32_OFFSET + 4],
        "little",
    )
    return TrackMixVolume(
        track=track,
        vol_byte=img[base + TRACK_MIX_VOL_BYTE_OFFSET],
        vol_u32=u32,
    )


def read_scene_slot_pattern_sel(project: ImageProject, scene: int) -> tuple[int, ...]:
    """Pattern index (0-based) per track for a scene slot (0 = live)."""
    slot = SCENE_SLOT0 + scene * SCENE_SLOT_SIZE
    return tuple(project.image[slot + t] for t in range(16))
