"""Ugaritic language module for toponymic analysis.

Ugaritic (c. 1400–1190 BCE) was a Semitic language of the city-state
of Ugarit (modern Ras Shamra, Syria). Known for the earliest alphabetic
cuneiform script. Important for understanding Canaanite toponymy
and mythological place-names referenced in later traditions.

Key references:
- Pardee 2002 "Ritual and Cult at Ugarit"
- del Olmo Lete & Sanmartín 2003 "A Dictionary of the Ugaritic Language"
- Tropper 2000 "Ugaritische Grammatik"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class UgariticModule(BaseLanguageModule):
    """Language module for Ugaritic toponyms."""

    language_code = "uga"
    language_name = "Ugaritic"
    family = "Afro-Asiatic"
    branch = "Semitic > Central Semitic > Northwest Semitic"
    period = "c. 1400–1190 BCE"
    script = "Ugar"

    prefixes = [
        "Bet-",  # house/temple
        "Ras-",  # head, promontory (Ras Shamra)
    ]

    suffixes = [
        "-ūma",  # locative/plural
        "-ānu",  # adjectival/place
        "-at",  # feminine
        "-ōt",  # feminine plural
        "-im",  # masculine plural
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "ugrt": "ugrt (Ugarit – meaning debated, possibly 'field')",
        "ras": "rāšu (head, cape, promontory)",
        "shamra": "ṯamru (fennel – Ras Shamra = Cape Fennel)",
        "bet": "bētu (house, temple)",
        "il": "'ilu (god, deity – El)",
        "baal": "ba'lu (lord, master – storm deity)",
        "yam": "yammu (sea – sea deity)",
        "mot": "mōtu (death – underworld deity)",
        "sapan": "ṣapānu (north – Mount Zaphon/Casius)",
        "qdsh": "qudšu (holy, sacred)",
        "mlk": "malku (king)",
        "ars": "'arṣu (earth, land)",
        "shm": "šamu (sky, heaven)",
        "nhr": "nahru (river)",
        "gb": "gab'u (hill, height)",
        "mdbr": "midbaru (pasture, steppe)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Ugaritic toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes],
            key=len,
            reverse=True,
        )

        matched_prefix = None
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                matched_prefix = prefix
                break

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_prefix:
            prefix_part = form[: len(matched_prefix)]
            remainder = form[len(matched_prefix) :]
            if remainder.startswith(("-", " ")):
                remainder = remainder[1:]
                prefix_part = form[: len(matched_prefix) + 1]

            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="compound_head",
                    lemma=matched_prefix,
                    meaning=self.ELEMENT_MEANINGS.get(matched_prefix),
                    confidence=0.7,
                )
            )
            results.append(
                SegmentationResult(
                    component=remainder,
                    position=1,
                    morph_type="compound_modifier",
                    lemma=remainder.lower(),
                    confidence=0.5,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="stem",
                    lemma=stem.lower(),
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.6,
                )
            )
        else:
            known = self.ELEMENT_MEANINGS.get(form_lower)
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    lemma=form.lower(),
                    meaning=known,
                    confidence=0.6 if known else 0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Ugaritic in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        ugaritic_elements = ["ugrt", "ugarit", "sapan", "zaphon", "shamra"]
        for elem in ugaritic_elements:
            if elem in form_lower:
                evidence.append(f"Known Ugaritic toponym '{elem}'")
                score += 0.5
                break

        ugaritic_roots = ["baal", "yam", "mot", "qdsh", "mlk"]
        for root in ugaritic_roots:
            if root in form_lower:
                evidence.append(f"Ugaritic theophoric/root '{root}'")
                score += 0.3
                break

        if form_lower.startswith("ras") and len(form_lower) > 4:
            evidence.append("Semitic prefix ras- (head/cape)")
            score += 0.2

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Late Bronze Age (1400–1190 BCE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Ugaritic components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            lemma_key = comp.lemma.lower().rstrip("-")
            meaning = self.ELEMENT_MEANINGS.get(lemma_key)
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma_key,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=[],
                        sound_changes=[],
                        sources=["del Olmo Lete & Sanmartín 2003", "Pardee 2002"],
                    )
                )
        return candidates
