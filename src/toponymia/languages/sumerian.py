"""Sumerian language module for toponymic analysis.

Sumerian (c. 3100–2000 BCE, literary use until c. 100 CE) is a
language isolate of southern Mesopotamia. Oldest known written language.
Many Sumerian place-names survive as substrate in Akkadian transmission
and reached Europe through Greek/Latin sources.
Characterized by:
- Agglutinative morphology (unlike Semitic root-pattern)
- Key elements: ki (place), kur (mountain/foreign), e (house/temple)
- City names: Ur, Uruk, Eridu, Lagash, Nippur

Key references:
- Edzard 2003 "Sumerian Grammar"
- Jacobsen 1939 "The Sumerian King List"
- Steinkeller 2013 "An Archaic 'Prisoner Plaque' from Kiš"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SumerianModule(BaseLanguageModule):
    """Language module for Sumerian toponyms."""

    language_code = "sux"
    language_name = "Sumerian"
    family = "Language isolate"
    branch = "Sumerian (no known relatives)"
    period = "c. 3100–2000 BCE (literary use until c. 100 CE)"
    script = "Xsux"

    prefixes = [
        "E-",  # house, temple (É-anna)
        "Ur-",  # city/base (Ur, Uruk)
        "Unug-",  # Uruk (native form)
        "Ki-",  # place
        "Kur-",  # mountain, foreign land
        "Iri-",  # city
        "Bad-",  # wall, fortress
        "Id-",  # river (íd)
    ]

    suffixes = [
        "-ki",  # place determinative
        "-kur",  # mountain/foreign land
        "-uru",  # city
        "-ab",  # sea (a-ab-ba)
        "-nun",  # great, prince
        "-gal",  # great, large
        "-banda",  # small, junior
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "e": "é (house, temple)",
        "ur": "uru/ur (city, base, foundation)",
        "unug": "unug (Uruk – city of Inanna)",
        "ki": "ki (place, earth, ground)",
        "kur": "kur (mountain, foreign land, underworld)",
        "iri": "iri (city)",
        "bad": "bàd (wall, fortress)",
        "id": "íd (river, watercourse)",
        "nun": "nun (prince, great)",
        "gal": "gal (great, large)",
        "banda": "banda (small, young, junior)",
        "ab": "ab (sea, lake – a-ab-ba)",
        "eridu": "eridug (mighty city – oldest city)",
        "lagash": "lagaš (surveyor's peg?)",
        "nibru": "nibru (Nippur – crossing point)",
        "shuruppak": "šuruppak (healing place)",
        "girsu": "girsu (Girsu – meaning uncertain)",
        "umma": "umma (mother city?)",
        "an": "an (heaven, sky – god Anu)",
        "enlil": "en-líl (lord wind/air – supreme deity)",
        "inanna": "inanna (lady of heaven – goddess)",
        "abzu": "abzu (underground water, abyss)",
        "dingir": "diŋir (god, deity)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Sumerian toponym into components."""
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
            if matched_suffix and remainder.lower().endswith(matched_suffix):
                stem = remainder[: len(remainder) - len(matched_suffix)]
                if stem:
                    results.append(
                        SegmentationResult(
                            component=stem,
                            position=1,
                            morph_type="stem",
                            lemma=stem.lower(),
                            confidence=0.5,
                        )
                    )
                results.append(
                    SegmentationResult(
                        component=remainder[len(remainder) - len(matched_suffix) :],
                        position=len(results),
                        morph_type="suffix",
                        lemma=matched_suffix,
                        meaning=self.ELEMENT_MEANINGS.get(matched_suffix),
                        confidence=0.7,
                    )
                )
            else:
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
                    meaning=self.ELEMENT_MEANINGS.get(matched_suffix),
                    confidence=0.7,
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
        """Classify whether a toponym is likely Sumerian in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        sumerian_cities = [
            "eridu",
            "lagash",
            "nibru",
            "nippur",
            "shuruppak",
            "girsu",
            "umma",
            "uruk",
            "unug",
        ]
        for city in sumerian_cities:
            if city in form_lower:
                evidence.append(f"Known Sumerian city '{city}'")
                score += 0.5
                break

        if form_lower.startswith(("e-", "e ")):
            evidence.append("Sumerian temple prefix É-")
            score += 0.3

        sumerian_elements = ["abzu", "enlil", "inanna", "dingir", "an"]
        for elem in sumerian_elements:
            if elem in form_lower:
                evidence.append(f"Sumerian theonym/element '{elem}'")
                score += 0.3
                break

        if form_lower.endswith("ki"):
            evidence.append("Sumerian place determinative -ki")
            score += 0.3

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Early Dynastic–Ur III (3100–2000 BCE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Sumerian components."""
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
                        sources=["Edzard 2003", "Jacobsen 1939"],
                    )
                )
        return candidates
