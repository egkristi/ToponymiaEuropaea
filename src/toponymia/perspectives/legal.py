"""Legal/Administrative perspective (Perspective J).

Analyses place names reflecting legal, administrative, and governance structures.
Detects thing-sites, parish boundaries, hundred divisions, and administrative
naming patterns across European jurisdictions.

Example hypotheses:
- Places with "ting-/thing-" cluster at geographically central locations
- Places with "by-" as administrative unit show regular spacing
- Places with "herad-" correlate with historical district boundaries
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from toponymia.perspectives.base import BasePerspective, Hypothesis

# Legal/administrative elements across Nordic and European naming traditions
_LEGAL_ELEMENTS: dict[str, dict[str, Any]] = {
    # Assembly sites
    "ting": {"type": "assembly", "meaning": "thing/assembly", "tradition": "germanic"},
    "thing": {"type": "assembly", "meaning": "thing/assembly", "tradition": "germanic"},
    "mot": {"type": "assembly", "meaning": "meeting place", "tradition": "english"},
    # Administrative divisions
    "herad": {"type": "district", "meaning": "hundred/district", "tradition": "norse"},
    "hundred": {"type": "district", "meaning": "hundred", "tradition": "english"},
    "fylke": {"type": "province", "meaning": "folk/province", "tradition": "norse"},
    "syssel": {"type": "district", "meaning": "district/jurisdiction", "tradition": "norse"},
    "amt": {"type": "district", "meaning": "office/county", "tradition": "danish_german"},
    "len": {"type": "district", "meaning": "fief/county", "tradition": "norse"},
    # Parish/church administration
    "kirke": {"type": "parish", "meaning": "church", "tradition": "norse"},
    "sokn": {"type": "parish", "meaning": "parish/congregation", "tradition": "norse"},
    "prestegjeld": {"type": "parish", "meaning": "parish district", "tradition": "norse"},
    # Boundaries and borders
    "grense": {"type": "boundary", "meaning": "border/boundary", "tradition": "norse"},
    "mark": {"type": "boundary", "meaning": "boundary/march", "tradition": "germanic"},
    "rå": {"type": "boundary", "meaning": "boundary marker", "tradition": "norse"},
    "skille": {"type": "boundary", "meaning": "division/boundary", "tradition": "norse"},
    # Royal/state authority
    "kong": {"type": "royal", "meaning": "king", "tradition": "norse"},
    "kron": {"type": "royal", "meaning": "crown", "tradition": "norse"},
    "slott": {"type": "royal", "meaning": "castle/palace", "tradition": "norse"},
    "borg": {"type": "fortification", "meaning": "fortified place", "tradition": "germanic"},
    # Taxation and economy
    "toll": {"type": "taxation", "meaning": "toll/customs", "tradition": "germanic"},
    "torg": {"type": "market", "meaning": "market place", "tradition": "norse"},
    "køping": {"type": "market", "meaning": "market town", "tradition": "norse"},
    "kaupang": {"type": "market", "meaning": "trading post", "tradition": "norse"},
    # Law enforcement
    "galge": {"type": "law", "meaning": "gallows", "tradition": "germanic"},
    "rett": {"type": "law", "meaning": "court/right", "tradition": "norse"},
}


class LegalPerspective(BasePerspective):
    """Legal and administrative analysis of place names.

    Identifies places named for governance structures, assembly sites,
    administrative boundaries, and legal functions. Tests whether these
    names show spatial patterns consistent with historical jurisdictions.
    """

    perspective_id = "legal"
    name = "Legal/Administrative"
    description = "Assembly sites, boundaries, jurisdictions, and governance names"
    required_data = ["databank", "administrative_boundaries"]

    def __init__(self, *, include_boundaries: bool = True):
        """Initialize legal perspective.

        Args:
            include_boundaries: Whether to include boundary analysis.
        """
        self._include_boundaries = include_boundaries
        self._legal_elements = _LEGAL_ELEMENTS

    def extract_features(self, place_id: UUID) -> dict[str, Any]:
        """Extract legal/administrative features for a place.

        Returns administrative classification, proximity to known
        boundaries, centrality measures, and jurisdictional history.
        """
        return {
            "place_id": str(place_id),
            "legal_element": None,
            "element_type": None,
            "tradition": None,
            "nearest_boundary_m": None,
            "centrality_score": None,
            "historical_jurisdiction": None,
            "is_central_place": None,
        }

    def generate_hypotheses(self, place_id: UUID) -> list[Hypothesis]:
        """Generate legal/administrative hypotheses.

        Tests whether governance-related place names correlate with
        known administrative structures and boundaries.
        """
        hypotheses: list[Hypothesis] = []

        for element, info in self._legal_elements.items():
            if info["type"] == "assembly":
                hypotheses.append(
                    Hypothesis(
                        claim=(
                            f"Places with '{element}' are at geographically central "
                            f"locations within their historical districts"
                        ),
                        null_hypothesis=(
                            f"'{element}' names are not more centrally located "
                            f"than random points in their districts"
                        ),
                        test_family="centrality_test",
                        parameters={
                            "element": element,
                            "type": info["type"],
                            "tradition": info["tradition"],
                        },
                        source=self.perspective_id,
                    )
                )
            elif info["type"] == "boundary":
                hypotheses.append(
                    Hypothesis(
                        claim=(
                            f"Places with '{element}' ({info['meaning']}) are closer to "
                            f"historical administrative boundaries than expected by chance"
                        ),
                        null_hypothesis=(
                            f"No correlation between '{element}' names and boundary proximity"
                        ),
                        test_family="distance_test",
                        parameters={
                            "element": element,
                            "type": info["type"],
                            "tradition": info["tradition"],
                        },
                        source=self.perspective_id,
                    )
                )
            else:
                hypotheses.append(
                    Hypothesis(
                        claim=(
                            f"Places with '{element}' ({info['meaning']}) show spatial "
                            f"patterns consistent with {info['type']} functions"
                        ),
                        null_hypothesis=(
                            f"No spatial pattern distinguishes '{element}' names "
                            f"from random locations"
                        ),
                        test_family="spatial_pattern",
                        parameters={
                            "element": element,
                            "type": info["type"],
                            "tradition": info["tradition"],
                        },
                        source=self.perspective_id,
                    )
                )

        return hypotheses

    def classify_element(self, element: str) -> dict[str, Any] | None:
        """Classify a name element as a legal/administrative term.

        Args:
            element: Name element to classify.

        Returns:
            Classification dict or None if not recognized.
        """
        lower = element.lower()
        if lower in self._legal_elements:
            return self._legal_elements[lower]
        return None
