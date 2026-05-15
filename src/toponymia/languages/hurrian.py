"""Hurrian language module for toponymic analysis.

Hurrian (c. 2300–1000 BCE) was spoken in northern Mesopotamia and
eastern Anatolia. Part of the Hurro-Urartian family (language isolate
family). The Mitanni kingdom (c. 1500–1300 BCE) was Hurrian-speaking.
Many Hittite-era Anatolian toponyms are actually Hurrian substrate.
Important for understanding pre-Indo-European toponymy of eastern Turkey.

Key references:
- Wegner 2007 "Hurritisch: Eine Einführung"
- Wilhelm 1989 "The Hurrians"
- Salvini 2008 "Corpus dei testi urartei"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class HurrianModule(BaseLanguageModule):
    """Language module for Hurrian toponyms."""

    language_code = "xhu"
    language_name = "Hurrian"
    family = "Hurro-Urartian"
    branch = "Hurrian"
    period = "c. 2300–1000 BCE"
    script = "Xsux"

    prefixes = [
        "Wash-",  # (a deity element: Washshukanni)
        "Ur-",  # possibly shared with Sumerian loans
        "Ari-",  # give (verbal root)
    ]

    suffixes = [
        "-šše",  # relational/adjectival suffix
        "-nni",  # locative/place suffix
        "-ugari",  # meaning debated (cf. Ugarit?)
        "-kanni",  # place element (Washshukanni)
        "-whe",  # collective?
        "-ži",  # abstract/nominal
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "wash": "waš- (deity/to pour? – Washshukanni)",
        "kanni": "kanni (place? – in Washshukanni)",
        "nuzi": "Nuzi (city near modern Kirkuk)",
        "alalakh": "Alalakh (city in Hatay, modern Tell Atchana)",
        "mitanni": "Mitanni (kingdom name – meaning debated)",
        "urkesh": "Urkesh (city – modern Tell Mozan)",
        "arrapha": "Arrapha (city – modern Kirkuk)",
        "teshub": "Teššub (storm god)",
        "hepat": "Ḫebat (queen of gods, sun goddess)",
        "shaushka": "Šauška (love/war goddess – cf. Ishtar)",
        "kumme": "Kumme (sacred city of Teššub)",
        "sheri": "Šeri (bull of Teššub, day)",
        "hurri": "Ḫurri (morning, dawn)",
        "nawar": "nawar- (pasture, meadow?)",
        "ari": "ar- (to give)",
        "ewri": "ewri (lord, king)",
        "eni": "eni (god)",
        "puru": "puruli (feast, perhaps 'earth/rock')",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Hurrian toponym into components."""
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
                    confidence=0.5 if known else 0.2,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Hurrian in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        hurrian_cities = [
            "nuzi",
            "alalakh",
            "urkesh",
            "arrapha",
            "kumme",
            "mitanni",
            "washshukanni",
        ]
        for city in hurrian_cities:
            if city in form_lower:
                evidence.append(f"Known Hurrian toponym '{city}'")
                score += 0.5
                break

        hurrian_suffixes = ["šše", "sse", "nni", "kanni", "ugari"]
        for suffix in hurrian_suffixes:
            if form_lower.endswith(suffix):
                evidence.append(f"Hurrian suffix -{suffix}")
                score += 0.3
                break

        hurrian_theonyms = ["teshub", "tessub", "hepat", "shaushka"]
        for theo in hurrian_theonyms:
            if theo in form_lower:
                evidence.append(f"Hurrian theophoric '{theo}'")
                score += 0.3
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Bronze Age (2300–1000 BCE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Hurrian components."""
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
                        sources=["Wegner 2007", "Wilhelm 1989"],
                    )
                )
        return candidates
