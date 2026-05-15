"""Akkadian language module for toponymic analysis.

Akkadian (c. 2500 BCE – 100 CE) was the primary Semitic language of
Mesopotamia, comprising Babylonian and Assyrian dialects. Many
Akkadian place-names were transmitted to Europe via Greek and Latin.
Characterized by:
- Bāb- (gate): Babylon = Bāb-ilī (gate of the gods)
- Dūr- (fortress): Dur-Sharrukin
- Cuneiform writing preserving ancient pronunciations
- Substrate from earlier Sumerian

Key references:
- von Soden 1995 "Grundriss der akkadischen Grammatik"
- Black et al. 2000 "A Concise Dictionary of Akkadian"
- Parpola 1970 "Neo-Assyrian Toponyms"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AkkadianModule(BaseLanguageModule):
    """Language module for Akkadian toponyms."""

    language_code = "akk"
    language_name = "Akkadian"
    family = "Afro-Asiatic"
    branch = "Semitic > East Semitic"
    period = "c. 2500 BCE – 100 CE (Babylonian + Assyrian)"
    script = "Xsux"

    prefixes = [
        "Bab-",  # gate (Babylon)
        "Bāb-",  # gate (with macron)
        "Dur-",  # fortress (Dur-Sharrukin)
        "Dūr-",  # fortress (with macron)
        "Bit-",  # house/estate (Bīt-Adini)
        "Kar-",  # quay, trading post (Kār-Tukulti-Ninurta)
        "Alu-",  # city (ālu)
        "Til-",  # ruin mound (cf. Hebrew Tel)
    ]

    suffixes = [
        "-ili",  # god(s) (Bāb-ilī)
        "-ānu",  # adjectival
        "-ūtu",  # abstract noun
        "-āti",  # feminine plural
        "-ī",  # gentilicium
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "bab": "bābu (gate, door)",
        "dur": "dūru (fortress, city wall)",
        "bit": "bītu (house, estate, temple)",
        "kar": "kāru (quay, trading post, harbour)",
        "alu": "ālu (city, settlement)",
        "til": "tillu (ruin mound)",
        "ili": "ilu/ilī (god/gods)",
        "sharru": "šarru (king)",
        "assur": "Aššur (city/god Assur)",
        "ninua": "Ninua (Nineveh – fish city?)",
        "sippar": "Sippar (book city?)",
        "nipur": "Nippur (< Sum. Nibru)",
        "kalhu": "Kalḫu (Calah/Nimrud)",
        "arbail": "Arbā-ilu (four gods – Arbela/Erbil)",
        "mashkan": "maškanu (threshing floor, settlement)",
        "nahr": "nāru (river)",
        "shadu": "šadû (mountain)",
        "tam": "tâmtu (sea)",
        "ekallu": "ēkallu (palace < Sum. é-gal)",
        "harranu": "ḫarrānu (road, caravan route – Harran)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Akkadian toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower().replace("ā", "a").replace("ū", "u").replace("ī", "i")

        sorted_prefixes = sorted(
            [p.rstrip("-").lower().replace("ā", "a").replace("ū", "u") for p in self.prefixes],
            key=len,
            reverse=True,
        )

        matched_prefix = None
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                matched_prefix = prefix
                break

        sorted_suffixes = sorted(
            [
                s.lstrip("-").lower().replace("ā", "a").replace("ū", "u").replace("ī", "i")
                for s in self.suffixes
            ],
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
                    confidence=0.8,
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
        """Classify whether a toponym is likely Akkadian in origin."""
        form_lower = form.lower().replace("ā", "a").replace("ū", "u")
        score = 0.0
        evidence: list[str] = []

        akkadian_prefixes = ["bab", "dur", "bit", "kar", "til"]
        for prefix in akkadian_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                evidence.append(f"Akkadian prefix {prefix}-")
                score += 0.4
                break

        akkadian_names = [
            "assur",
            "ninua",
            "nineveh",
            "babylon",
            "sippar",
            "nippur",
            "kalhu",
            "arbail",
            "harranu",
        ]
        for name in akkadian_names:
            if name in form_lower:
                evidence.append(f"Known Akkadian toponym '{name}'")
                score += 0.4
                break

        if form_lower.endswith(("ili", "ilu")):
            evidence.append("Akkadian theophoric -ilī/ilu (god)")
            score += 0.3

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Mesopotamian (2500 BCE – 100 CE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Akkadian components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            lemma_key = comp.lemma.lower().rstrip("-").replace("ā", "a").replace("ū", "u")
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
                        sources=["Black et al. 2000", "Parpola 1970"],
                    )
                )
        return candidates
