"""Cultural/Social perspective (Perspective F).

Analyses place names from cultural and social angles — person names embedded
in toponyms, ethnonymic references, social class indicators, and ownership
patterns. This perspective helps reveal historical social structures and
identity markers preserved in the landscape.

ROADMAP: 12.6

Example hypotheses:
- Places with personal-name specifics cluster around historical estate centres
- Ethnonymic elements (Finn-, Kvæn-, Lapp-) correlate with known contact zones
- Social-rank indicators (-karl, -jarl, -kong-) cluster near power centres
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Social class indicators found in Scandinavian toponyms
_SOCIAL_INDICATORS: dict[str, dict[str, str]] = {
    # Ruling/elite
    "kong": {"class": "royal", "meaning": "king"},
    "dron": {"class": "royal", "meaning": "queen"},
    "jarl": {"class": "nobility", "meaning": "earl/jarl"},
    "herse": {"class": "nobility", "meaning": "local chieftain"},
    "hovding": {"class": "nobility", "meaning": "chieftain"},
    # Free farmers
    "karl": {"class": "free", "meaning": "free man"},
    "bonde": {"class": "free", "meaning": "farmer"},
    "hauldr": {"class": "free", "meaning": "allodial farmer"},
    # Dependent / servant
    "træl": {"class": "unfree", "meaning": "thrall/slave"},
    "svein": {"class": "service", "meaning": "servant/lad"},
    "husmann": {"class": "cotter", "meaning": "cotter/smallholder"},
}

# Ethnonymic elements indicating contact between groups
_ETHNONYMIC_ELEMENTS: dict[str, dict[str, str]] = {
    "finn": {"group": "sami", "note": "Norse term for Sami"},
    "lapp": {"group": "sami", "note": "Older term for Sami"},
    "kvæn": {"group": "finnic", "note": "Kven/Finnish settlers"},
    "bjarm": {"group": "finnic", "note": "Bjarmians (Karelian/Finnic)"},
    "dansk": {"group": "danish", "note": "Danish"},
    "svea": {"group": "swedish", "note": "Swedish (Svear)"},
    "gaut": {"group": "swedish", "note": "Geatish (Götar)"},
    "saks": {"group": "germanic", "note": "Saxon"},
    "vend": {"group": "slavic", "note": "Wends (Slavic)"},
    "irsk": {"group": "celtic", "note": "Irish"},
    "skott": {"group": "celtic", "note": "Scottish"},
}

# Ownership / habitative generics that imply social structure
_OWNERSHIP_GENERICS: dict[str, str] = {
    "gard": "owned farmstead",
    "bol": "assessed farm unit",
    "plass": "cotter's place (dependent)",
    "eie": "property/possession",
    "gods": "estate/manor",
    "hovud": "main/head farm",
    "sæter": "seasonal shieling (shared use)",
}


@dataclass
class CulturalFeatures:
    """Extracted cultural/social features for a toponym."""

    social_indicators: list[dict[str, str]] = field(default_factory=list)
    ethnonymic_refs: list[dict[str, str]] = field(default_factory=list)
    ownership_type: str = ""
    possible_personal_name: bool = False
    personal_name_element: str = ""


class CulturalPerspective(BasePerspective):
    """Cultural and social analysis of place names.

    Identifies embedded personal names, ethnonymic references, social
    class markers, and ownership patterns in toponyms. Useful for
    reconstructing historical social geography.
    """

    perspective_id = "cultural_social"
    name = "Cultural/Social"
    description = "Person names, ethnonyms, social class, and ownership patterns"
    required_data = ["databank", "ner_annotations"]

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract cultural/social features.

        In the full system this would query the databank; here we
        provide the feature schema.
        """
        return {
            "social_indicators": [],
            "ethnonymic_refs": [],
            "ownership_type": "",
            "possible_personal_name": False,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate cultural/social hypotheses for a place."""
        return [
            Hypothesis(
                claim="Personal-name toponyms cluster around estate centres",
                null_hypothesis=("Personal-name specifics are uniformly distributed"),
                test_family="spatial_cluster",
                source=self.perspective_id,
            ),
            Hypothesis(
                claim="Ethnonymic elements correlate with documented contact zones",
                null_hypothesis=("Ethnonymic elements are randomly distributed"),
                test_family="spatial_correlation",
                source=self.perspective_id,
            ),
        ]


def analyse_toponym(name: str) -> CulturalFeatures:
    """Analyse a toponym for cultural/social features.

    Args:
        name: The place name to analyse.

    Returns:
        CulturalFeatures with detected indicators.
    """
    lower = name.lower()
    features = CulturalFeatures()

    # Check social class indicators
    for element, info in _SOCIAL_INDICATORS.items():
        if element in lower:
            features.social_indicators.append({"element": element, **info})

    # Check ethnonymic elements
    for element, info in _ETHNONYMIC_ELEMENTS.items():
        if element in lower:
            features.ethnonymic_refs.append({"element": element, **info})

    # Check ownership generics
    for generic, meaning in _OWNERSHIP_GENERICS.items():
        if lower.endswith((generic, generic + "en")):
            features.ownership_type = meaning
            break

    # Heuristic: if the first element looks like a personal name
    # (starts with uppercase and the name has a recognizable generic)
    if len(name) > 3 and name[0].isupper():
        for generic in _OWNERSHIP_GENERICS:
            if lower.endswith((generic, generic + "en")):
                prefix = lower[: lower.rfind(generic)]
                if prefix and prefix[-1] == "s":
                    features.possible_personal_name = True
                    features.personal_name_element = prefix.rstrip("s")
                    break

    return features
