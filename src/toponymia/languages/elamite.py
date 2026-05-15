"""Elamite language module for toponymic analysis.

Elamite (c. 2600–300 BCE) was a language isolate spoken in southwestern
Iran (modern Khuzestan/Fars). Capital: Susa (Shush). Important as one
of three administrative languages of the Achaemenid Persian Empire
(alongside Old Persian and Akkadian). Substrate in SW Iranian toponymy.

Key references:
- Stolper 1984 "Political History" in Cambridge History of Iran
- Potts 1999 "The Archaeology of Elam"
- Tavernier 2007 "Iranica in the Achaemenid Period"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ElamiteModule(BaseLanguageModule):
    """Language module for Elamite toponyms."""

    language_code = "elx"
    language_name = "Elamite"
    family = "Language isolate"
    branch = "Elamite (no proven relatives; Elamo-Dravidian debated)"
    period = "c. 2600–300 BCE"
    script = "Xsux"

    prefixes = [
        "Hat-",  # common element (Hatamti = Elam)
        "An-",  # divine/high? (Anshan)
        "Hu-",  # element in personal/place names
        "Shi-",  # element (Shilhak, Shimashki)
    ]

    suffixes = [
        "-shan",  # place element (Anshan)
        "-shki",  # place element (Shimashki)
        "-ak",  # genitive marker
        "-na",  # locative?
        "-ppe",  # collective/plural?
        "-ir",  # element (Shushinar, etc.)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "hat": "ḫat- (element in Ḫatamti = Elam)",
        "hatamti": "Ḫatamti (native name for Elam – meaning debated)",
        "susa": "Šušan/Šušun (lily? – capital Susa)",
        "shush": "Šušan/Šušun (lily? – modern Shush)",
        "anshan": "Anšan (highland capital – modern Tall-e Malyan)",
        "shimashki": "Šimaški (a confederation/place)",
        "awan": "Awan (early dynastic city)",
        "dur": "Dūr (fortress – Akkadian loan: Dur-Untash)",
        "untash": "Untaš (Elamite king name – Untash-Napirisha)",
        "napirisha": "Napiriša (great god – supreme deity)",
        "inshushinak": "Inšušinak (lord of Susa – patron deity)",
        "humban": "Ḫumban (deity – royal protector)",
        "liyan": "Liyan (port city – modern Bushehr area)",
        "huhnur": "Ḫuḫnur (city in highlands)",
        "halme": "ḫalme- (possibly 'throne, seat'?)",
        "kurangun": "Kurangun (rock relief site)",
        "sialk": "Sialk (Teppe Sialk – ancient site)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Elamite toponym into components."""
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
                    confidence=0.6,
                )
            )
            if matched_suffix and remainder.lower().endswith(matched_suffix):
                stem = remainder[: len(remainder) - len(matched_suffix)]
                if stem:
                    results.append(
                        SegmentationResult(
                            component=stem,
                            position=1,
                            morph_type="stem",
                            lemma=stem.lower(),
                            confidence=0.4,
                        )
                    )
                results.append(
                    SegmentationResult(
                        component=remainder[len(remainder) - len(matched_suffix) :],
                        position=len(results),
                        morph_type="suffix",
                        lemma=matched_suffix,
                        confidence=0.6,
                    )
                )
            else:
                results.append(
                    SegmentationResult(
                        component=remainder,
                        position=1,
                        morph_type="compound_modifier",
                        lemma=remainder.lower(),
                        confidence=0.4,
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
                    confidence=0.4,
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
                    confidence=0.5 if known else 0.2,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Elamite in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        elamite_names = [
            "susa",
            "shush",
            "anshan",
            "hatamti",
            "shimashki",
            "awan",
            "liyan",
            "huhnur",
            "kurangun",
            "sialk",
        ]
        for name in elamite_names:
            if name in form_lower:
                evidence.append(f"Known Elamite toponym '{name}'")
                score += 0.5
                break

        elamite_elements = ["napirisha", "inshushinak", "humban", "untash"]
        for elem in elamite_elements:
            if elem in form_lower:
                evidence.append(f"Elamite theophoric '{elem}'")
                score += 0.4
                break

        elamite_suffixes = ["shan", "shki", "ppe"]
        for suffix in elamite_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 2:
                evidence.append(f"Possible Elamite suffix -{suffix}")
                score += 0.2
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Elamite period (2600–300 BCE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Elamite components."""
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
                        sources=["Potts 1999", "Tavernier 2007"],
                    )
                )
        return candidates
