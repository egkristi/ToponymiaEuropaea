"""Svan language module for toponymic analysis.

Svan (ლუშნუ ნინ, sva) is a Kartvelian (South Caucasian) language spoken in
Svaneti, NW Georgia. Distinct from Georgian within the same family, retaining
many archaic features. Key toponymic elements: mush- (ice/glacier), tqe
(mountain top), latakh (valley), kor (gorge); place-names: Mestia, Ushguli,
Latali. Important for Caucasian substrate and proto-Kartvelian reconstruction.
~15,000–30,000 speakers, endangered.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SvanModule(BaseLanguageModule):
    """Language module for Svan toponyms."""

    language_code = "sva"
    language_name = "Svan"
    family = "Kartvelian"
    branch = "South Caucasian (Kartvelian) > Svan"
    period = "Modern (archaic features, 1800 CE–present)"
    script = "Geor"

    prefixes = [
        "La-",
        "Me-",
        "Ka-",
    ]

    suffixes = [
        "-shi",
        "-al",
        "-ari",
        "-er",
        "-ish",
        "-kh",
        "-vr",
        "-ld",
    ]

    stems = [
        "mush",
        "tqe",
        "latakh",
        "kor",
        "zagar",
        "lemkh",
        "tskh",
        "shgul",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "la": "diminutive/locative (prefix)",
            "me": "place of (prefix)",
            "ka": "at, by (prefix)",
            "shi": "place, locative",
            "al": "near, by (locative)",
            "ari": "place of",
            "er": "adjectival/place suffix",
            "ish": "locative/adjectival",
            "kh": "locative (archaic)",
            "vr": "place (variant locative)",
            "ld": "village/settlement",
            "mush": "ice, glacier",
            "tqe": "mountain top, peak",
            "latakh": "valley, hollow",
            "kor": "gorge, ravine",
            "zagar": "bell (church bell → place)",
            "lemkh": "rocky ground",
            "tskh": "water, spring",
            "shgul": "feared/revered (Ushguli)",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Svan toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 2:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="prefix",
                        lemma=prefix,
                        meaning=self._element_meaning(prefix),
                        confidence=0.6,
                    )
                )
                form = form[len(prefix) :]
                form_lower = form.lower()
                break

        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                pos = len(results)
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=pos,
                        morph_type="stem",
                        confidence=0.5,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(form) - len(suffix) :],
                        position=pos + 1,
                        morph_type="suffix",
                        lemma=suffix,
                        meaning=self._element_meaning(suffix),
                        confidence=0.65,
                    )
                )
                return results

        pos = len(results)
        results.append(
            SegmentationResult(
                component=form,
                position=pos,
                morph_type="stem",
                confidence=0.3,
            )
        )
        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Svan."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Svan suffix -{suffix}")
                score += 0.25
                break

        svan_clusters = ["tskh", "sgw", "chkh", "shgw", "ldz"]
        for cl in svan_clusters:
            if cl in form_lower:
                evidence.append(f"Svan consonant cluster '{cl}'")
                score += 0.25
                break

        known_stems = ["mesti", "ushgul", "latal", "lenjer", "mulakh"]
        for stem in known_stems:
            if stem in form_lower:
                evidence.append(f"Known Svan toponym stem '{stem}'")
                score += 0.35
                break

        svan_vowels = ["ä", "ö", "ü"]
        for v in svan_vowels:
            if v in form_lower:
                evidence.append(f"Svan umlaut vowel '{v}'")
                score += 0.15
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "mush": ("mūšg", "ice, glacier", ["Georgian mq'inv-"]),
            "tqe": ("tqe", "mountain top, peak", ["Georgian t'q'e"]),
            "latakh": ("latäx", "valley, hollow", []),
            "kor": ("kor", "gorge, ravine", ["Georgian xeoba (semantic)"]),
            "shi": ("-ši", "locative (in, at)", ["Georgian -ši"]),
            "shgul": ("šgul", "feared/revered (heart)", ["Georgian gul- 'heart'"]),
            "tskh": ("c'xal", "water, spring", ["Georgian c'q'ali 'water'"]),
            "al": ("-al", "near, by (locative)", []),
        }
        for comp in components:
            key = (comp.lemma or comp.component).lower().rstrip("-")
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.6,
                        cognates=cognates,
                        sources=["Klimov, Etymological Dictionary of Kartvelian Languages"],
                    )
                )
        return candidates
