"""Shared utilities for working with OP-XY project structures."""

from .container import (  # noqa: F401
    HEADER_SIZE,
    MAGIC,
    MIN_PROJECT_SIZE,
    PRE_TRACK_SIZE,
    TrackBlock,
    XYContainer,
    XYHeader,
    XYProject,
)
from .structs import (  # noqa: F401
    SENTINEL_BYTES,
    STEP_TICKS,
    TrackHandle,
    find_track_blocks,
    find_track_handles,
    find_track_payload_window,
    parse_pointer_words,
    pattern_max_slot,
    SlotDescriptor,
)
from .plocks import (  # noqa: F401
    CONFIG_TAIL_SIG,
    CONTINUATION_MARKER,
    EMPTY_ENTRY,
    STANDARD_ENTRY_COUNT,
    StandardSlot,
    T10Header,
    count_lane_values,
    find_plock_start,
    first_real_param_id,
    list_standard_nonempty_values,
    parse_standard_slots,
    parse_standard_table,
    parse_t10_header,
    rewrite_standard_nonempty_values,
    rewrite_standard_values_for_param_groups,
    t1_first_param_id,
)
from .project_inspection import (  # noqa: F401
    PatternInspection,
    PresetReference,
    ProjectInspection,
    TrackInspection,
    inspect_project,
    inspect_project_bytes,
)
from .drum_sample_inspection import (  # noqa: F401
    DRUM_FADE_STEP,
    DRUM_FADE_UI_MAX,
    DrumTrackSamples,
    DrumVoiceSample,
    ProjectDrumSamples,
    decode_drum_fade_u32,
    drum_fade_storage_voice,
    encode_drum_fade_ui,
    inspect_drum_samples,
    inspect_drum_samples_bytes,
)
from .scene_volume_inspection import (  # noqa: F401
    SceneVolumeInspection,
    TrackMixVolume,
    encode_mix_vol_byte,
    inspect_scene_volumes,
    inspect_scene_volumes_bytes,
    read_scene_track_volume,
    scene_volume_storage_track,
)
from .preset_path_inspection import (  # noqa: F401
    ProjectPresetPaths,
    TrackPresetPath,
    inspect_preset_paths,
    inspect_preset_paths_bytes,
)
