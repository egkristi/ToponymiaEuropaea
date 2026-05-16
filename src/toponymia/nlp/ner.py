"""Historical Named Entity Recognition for medieval documents.

Provides rule-based and pattern-based NER for extracting entities from
historical texts (charters, sagas, land surveys). Designed to handle
the orthographic variation and formulaic language of medieval documents.

Entity types:
- PLACE: Place names (primary target)
- PERSON: Personal names (patronymics, bynames)
- ETHNONYM: Ethnic/tribal names (Finn-, Kvæn-, Lapp-)
- DEITY: Theophoric references (Þór-, Óðinn-, Freyr-)
- TITLE: Titles and offices (konungr, jarl, biskup)

Supports integration with:
- Diplomatarium connector (issue #21)
- Norske Gaardnavne (issue #20)
- Attestation pipeline

References:
- Bjerva & Praet 2020. "NER for Historical Documents: A Survey."
- Pettersson et al. 2013. "Normalisation of Historical Text."
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """A named entity extracted from historical text."""

    text: str
    entity_type: str  # PLACE, PERSON, ETHNONYM, DEITY, TITLE
    start: int
    end: int
    confidence: float = 0.5
    normalized: str = ""
    context: str = ""


@dataclass
class HistoricalNER:
    """Rule-based NER for medieval Scandinavian documents.

    Uses formulaic patterns from Latin/ON charters to identify
    named entities without requiring a trained ML model.
    """

    # Latin charter formulas indicating place names
    PLACE_INDICATORS_LAT: list[str] = field(
        default_factory=lambda: [
            r"in\s+(\w+)",  # "in [place]"
            r"de\s+(\w+)",  # "de [place]" (from/of)
            r"apud\s+(\w+)",  # "apud [place]" (at/near)
            r"ad\s+(\w+)",  # "ad [place]" (to/at)
            r"super\s+(\w+)",  # "super [place]" (above/on)
            r"iuxta\s+(\w+)",  # "iuxta [place]" (near)
            r"ecclesi[ae]+\s+(?:de\s+)?(\w+)",  # "ecclesiae [de] [place]"
            r"parochi[ae]+\s+(\w+)",  # "parochiae [place]"
            r"villa\s+(?:de\s+)?(\w+)",  # "villa [de] [place]"
            r"terra[ms]?\s+(?:in\s+)?(\w+)",  # "terram [in] [place]"
        ]
    )

    # Old Norse/Norwegian indicators
    PLACE_INDICATORS_ON: list[str] = field(
        default_factory=lambda: [
            r"í\s+(\w+)",  # "í [place]" (in)
            r"at\s+(\w+)",  # "at [place]" (at)
            r"á\s+(\w+)",  # "á [place]" (on)
            r"til\s+(\w+)",  # "til [place]" (to)
            r"fra\s+(\w+)",  # "fra [place]" (from)
            r"við\s+(\w+)",  # "við [place]" (by)
        ]
    )

    # Known title patterns
    TITLE_PATTERNS: list[str] = field(
        default_factory=lambda: [
            r"\b(konungr|konungs|konungi)\b",
            r"\b(jarl|jarls|jarli)\b",
            r"\b(biskup|biskups|biskupi)\b",
            r"\b(herra|herr)\b",
            r"\b(fru|frú)\b",
            r"\b(prestr|prests|presti)\b",
            r"\b(rex|regis|regi)\b",
            r"\b(episcopus|episcopi)\b",
            r"\b(dominus|domini)\b",
            r"\b(comes|comitis)\b",
        ]
    )

    # Theophoric elements (deity names in place names)
    DEITY_ELEMENTS: list[str] = field(
        default_factory=lambda: [
            "Tor",
            "Þór",
            "Thor",
            "Odin",
            "Óðin",
            "Frey",
            "Freyr",
            "Frøy",
            "Freyja",
            "Ull",
            "Ullr",
            "Njord",
            "Njǫrð",
            "Tyr",
            "Týr",
            "Baldr",
            "Bald",
            "Hel",
            "Hǫð",
        ]
    )

    # Ethnonym elements
    ETHNONYM_ELEMENTS: list[str] = field(
        default_factory=lambda: [
            "Finn",
            "Kvæn",
            "Kven",
            "Lapp",
            "Same",
            "Sámi",
            "Dan",
            "Svea",
            "Gaut",
            "Bjarm",
            "Kirjal",
            "Væring",
            "Rus",
        ]
    )

    def extract_entities(self, text: str, *, language: str = "lat") -> list[Entity]:
        """Extract named entities from historical text.

        Args:
            text: The historical text to analyze.
            language: Language code ('lat', 'non', 'nor').

        Returns:
            List of Entity objects found in text.
        """
        entities: list[Entity] = []

        # Select patterns based on language
        if language in ("lat", "la"):
            place_patterns = self.PLACE_INDICATORS_LAT
        else:
            place_patterns = self.PLACE_INDICATORS_ON

        # Extract places from formulaic patterns
        for pattern in place_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                candidate = match.group(1)
                if self._is_likely_place(candidate):
                    entities.append(
                        Entity(
                            text=candidate,
                            entity_type="PLACE",
                            start=match.start(1),
                            end=match.end(1),
                            confidence=0.7,
                            context=text[max(0, match.start() - 20) : match.end() + 20],
                        )
                    )

        # Extract titles
        for pattern in self.TITLE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(
                    Entity(
                        text=match.group(1),
                        entity_type="TITLE",
                        start=match.start(1),
                        end=match.end(1),
                        confidence=0.9,
                    )
                )

        # Check for deity elements
        for deity in self.DEITY_ELEMENTS:
            for match in re.finditer(rf"\b({re.escape(deity)}\w*)\b", text):
                entities.append(
                    Entity(
                        text=match.group(1),
                        entity_type="DEITY",
                        start=match.start(1),
                        end=match.end(1),
                        confidence=0.6,
                    )
                )

        # Check for ethnonym elements
        for ethnonym in self.ETHNONYM_ELEMENTS:
            for match in re.finditer(rf"\b({re.escape(ethnonym)}\w*)\b", text):
                entities.append(
                    Entity(
                        text=match.group(1),
                        entity_type="ETHNONYM",
                        start=match.start(1),
                        end=match.end(1),
                        confidence=0.6,
                    )
                )

        # Deduplicate by position
        return self._deduplicate(entities)

    def _is_likely_place(self, candidate: str) -> bool:
        """Check if a candidate string is likely a place name."""
        if len(candidate) < 3:
            return False
        # Must start with uppercase (in normalized text)
        if candidate[0].islower():
            return False
        # Reject common Latin function words
        reject = {
            "anno",
            "die",
            "mense",
            "dei",
            "domini",
            "sancti",
            "ecclesie",
            "terre",
            "regis",
            "quod",
            "quia",
            "quam",
            "hoc",
            "haec",
            "ille",
            "illa",
            "cum",
            "per",
            "pro",
        }
        return candidate.lower() not in reject

    def _deduplicate(self, entities: list[Entity]) -> list[Entity]:
        """Remove duplicate entities at the same position."""
        seen: set[tuple[int, int, str]] = set()
        result = []
        for ent in entities:
            key = (ent.start, ent.end, ent.entity_type)
            if key not in seen:
                seen.add(key)
                result.append(ent)
        return result

    def extract_attestations(
        self, text: str, *, year: int | None = None, source: str = "", language: str = "lat"
    ) -> list[dict]:
        """Extract place-name attestations suitable for the databank.

        Args:
            text: Charter/document text.
            year: Year of the document (if known).
            source: Source identifier (e.g. "DN I 123").
            language: Document language.

        Returns:
            List of attestation dicts compatible with attestation pipeline.
        """
        entities = self.extract_entities(text, language=language)
        attestations = []

        for ent in entities:
            if ent.entity_type == "PLACE":
                attestations.append(
                    {
                        "form": ent.text,
                        "year": year,
                        "source": source,
                        "language": language,
                        "context": ent.context,
                        "confidence": ent.confidence,
                        "entity_type": ent.entity_type,
                    }
                )

        return attestations
