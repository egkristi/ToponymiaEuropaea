"""Acoustic landscape perspective.

Analyses correlation between sound-related place-name elements
and acoustic properties of the landscape (echoes, waterfalls,
wind exposure, animal sounds).

Elements: ljom/ljóm (echo/resonance), dur (roar/rumble),
sus (whisper/rushing), brak (crash), gny (din/noise),
klukk (gurgling), song (singing).
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Acoustic elements → expected sound sources
_ACOUSTIC_ELEMENTS: dict[str, dict[str, Any]] = {
    "ljom": {
        "sound_type": "echo/resonance",
        "features": ["cliff_face", "valley", "enclosed_space"],
        "terrain": "concave",
    },
    "dur": {
        "sound_type": "rumble/roar",
        "features": ["waterfall", "rapids", "strong_wind"],
        "terrain": "exposed",
    },
    "sus": {
        "sound_type": "rushing/whisper",
        "features": ["wind", "tree_canopy", "stream"],
        "terrain": "ridge",
    },
    "brak": {
        "sound_type": "crash/breaking",
        "features": ["surf", "rockfall", "ice_break"],
        "terrain": "coastal_cliff",
    },
    "gny": {
        "sound_type": "din/noise",
        "features": ["rapids", "seabird_colony", "market"],
        "terrain": "any",
    },
    "song": {
        "sound_type": "singing/melodic",
        "features": ["birdsong", "wind_tones", "stream"],
        "terrain": "sheltered",
    },
    "klukk": {
        "sound_type": "gurgling",
        "features": ["spring", "small_stream", "tidal"],
        "terrain": "low",
    },
    "tord": {
        "sound_type": "thunder",
        "features": ["exposed_height", "thunder_frequency"],
        "terrain": "elevated",
    },
    "stil": {
        "sound_type": "silence/calm",
        "features": ["sheltered", "lee_side", "forest"],
        "terrain": "enclosed",
    },
}


class AcousticPerspective(BasePerspective):
    """Acoustic landscape analysis.

    Tests whether sound-related place-name elements correlate with
    landscape features that produce or modify sound (terrain shape,
    water features, wind exposure, vegetation).
    """

    perspective_id = "acoustic"
    name = "Acoustic Landscape Perspective"
    description = "Sound environment correlation with acoustic toponyms"
    required_data = ["dem_terrain", "osm", "climate", "databank"]

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract acoustic-relevant features for a place."""
        return {
            "place_id": str(place_id),
            "terrain_concavity": None,
            "wind_exposure": None,
            "nearest_waterfall_m": None,
            "nearest_rapids_m": None,
            "vegetation_density": None,
            "cliff_proximity_m": None,
            "enclosure_factor": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate acoustic landscape hypotheses."""
        hypotheses: list[Hypothesis] = []

        for element, info in _ACOUSTIC_ELEMENTS.items():
            features_str = ", ".join(info["features"])
            hypotheses.append(
                Hypothesis(
                    claim=(
                        f"Places with '{element}' ({info['sound_type']}) correlate "
                        f"with sound-producing features: {features_str}"
                    ),
                    null_hypothesis=(
                        f"No correlation between '{element}' and acoustic landscape properties"
                    ),
                    test_family="mann_whitney_u",
                    parameters={
                        "element": element,
                        "sound_type": info["sound_type"],
                        "expected_features": info["features"],
                        "terrain_preference": info["terrain"],
                    },
                    source=self.perspective_id,
                )
            )

        return hypotheses
