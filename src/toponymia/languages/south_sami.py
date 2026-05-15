"""South Sami language module for toponymic analysis.

South Sami (åarjelsaemien gïele) is critically endangered and spoken in
central Scandinavia: Trøndelag, Jämtland, Härjedalen, Helgeland, and
parts of Nordland. It is DISTINCT from Northern Sami and has a different
toponymic vocabulary:

Key differences from Northern Sami:
- Different phonology (no consonant gradation in same pattern)
- Different vocabulary for geographic features
- Different suffixes and compounding patterns
- Covers the critical Trøndelag/Jämtland region where Norse-Sami
  contact was most intensive

South Sami toponymic elements in Norwegian/Swedish areas:
- Many "unexplained" names in Trøndelag are South Sami
- Jämtland/Härjedalen has extensive South Sami naming layer
- Some names look Norwegian but are actually South Sami calques

Important for the project because:
- Trøndelag is a core Norse area (Trondheim / Niðaróss)
- The South Sami substrate predates Norse settlement
- Many farm names have Sami origins hidden by Norwegianization
- Helgeland coast: intensive Norse-South Sami bilingual zone

Key references:
- Bergsland 1985 "Sydsamisk-norsk stedsnamnsamling"
- Dunfjeld-Aagård 2006 "Sørsamisk natur- og kulturlandskap"
- Qvigstad 1935 "De lappiske stedsnavn i Troms fylke"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SouthSamiModule(BaseLanguageModule):
    """Language module for South Sami toponyms in central Scandinavia."""

    language_code = "sma"  # ISO 639-3
    language_name = "South Sami"
    family = "Uralic"
    branch = "Sami > Western Sami > South Sami"
    period = "Continuous presence; substrate predates Norse settlement"
    script = "Latn"

    prefixes = [
        "Gaske-",  # middle (Gaske-Nansen)
        "Noerthe-",  # north (South Sami form)
        "Saemien-",  # Sami (Saemien Sijte)
        "Stoerre-",  # big (Stoerre-Snåsa)
        "Smarre-",  # smaller
        "Åarjel-",  # south (Åarjelsaemien = South Sami)
    ]

    suffixes = [
        "-jaevrie",  # lake (cf. Northern Sami jávri)
        "-johke",  # river (cf. Northern Sami johka)
        "-njaarke",  # cape, headland (cf. N.Sami njárga)
        "-vaerie",  # mountain (cf. Northern Sami várri)
        "-daelvie",  # valley
        "-laante",  # land, area
        "-sijjie",  # place, dwelling (cf. N.Sami sadji)
        "-tjaetsie",  # water (cf. N.Sami čáhci)
        "-gåetie",  # house, dwelling (traditional lávvu/goahti)
        "-suenje",  # grass meadow
        "-aejlege",  # island
        "-bïenje",  # dog (in names of peaks; shape reference)
        "-saevjie",  # reindeer grazing area
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "jaevrie": "lake (South Sami; cf. N.Sami jávri, Finnish järvi)",
        "johke": "river, stream (South Sami; cf. N.Sami johka)",
        "njaarke": "cape, headland (cf. N.Sami njárga)",
        "vaerie": "mountain (cf. N.Sami várri)",
        "daelvie": "valley, lowland",
        "laante": "land, territory, area",
        "sijjie": "place, site, dwelling place",
        "tjaetsie": "water (South Sami; cf. N.Sami čáhci)",
        "gåetie": "traditional dwelling (goahti type)",
        "suenje": "grass meadow, hay-making area",
        "aejlege": "island",
        "saevjie": "reindeer grazing land",
        "tjåanghkoe": "point, tip (geographic feature)",
        "vuelie": "song; also mountain slope",
        "dansen": "dance (in mountain names; shape reference)",
        "snåase": "Snåsa (major South Sami area; < S.Sami *snaase)",
        "raaste": "border, boundary (between territories)",
        "gïjle": "spring (water source)",
        "voene": "dwelling, home (< S.Sami vuöne)",
    }

    # Known South Sami names that appear in Norwegian/Swedish forms
    KNOWN_SUBSTRATES: dict[str, str] = {
        "snåsa": "< South Sami Snaase (major cultural center)",
        "røros": "Contains possible Sami elements (debated)",
        "namsos": "< Namsosen; Nams- possibly Sami origin",
        "bindal": "Possible South Sami origin (Bïndalen?)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a South Sami toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )
        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes],
            key=len,
            reverse=True,
        )

        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                self.ELEMENT_MEANINGS.get(suffix, "")
                results.extend(
                    [
                        SegmentationResult(
                            component=stem,
                            position=0,
                            morph_type="compound_modifier",
                            confidence=0.7,
                        ),
                        SegmentationResult(
                            component=suffix, position=1, morph_type="compound_head", confidence=0.7
                        ),
                    ]
                )
                break

        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                remainder = form[len(prefix) :]
                results.extend(
                    [
                        SegmentationResult(
                            component=prefix, position=0, morph_type="prefix", confidence=0.6
                        ),
                        SegmentationResult(
                            component=remainder, position=1, morph_type="stem", confidence=0.6
                        ),
                    ]
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely South Sami."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Known South Sami place elements
        sami_elements = [
            "jaevrie",
            "johke",
            "njaarke",
            "vaerie",
            "tjaetsie",
            "gåetie",
            "sijjie",
            "laante",
        ]
        for elem in sami_elements:
            if elem in form_lower:
                evidence.append(f"South Sami element '{elem}'")
                score += 0.7
                break

        # South Sami orthographic markers (ï, oe, ae digraphs)
        if "ï" in form_lower:
            evidence.append("South Sami ï vowel")
            score += 0.4
        if "oe" in form_lower or "ae" in form_lower:
            evidence.append("South Sami digraph (oe/ae)")
            score += 0.2

        # Known substrate names
        for name, desc in self.KNOWN_SUBSTRATES.items():
            if name in form_lower:
                evidence.append(f"Known South Sami substrate: {desc}")
                score += 0.5
                break

        # South Sami phonological pattern: -ie final vowels
        if form_lower.endswith("ie"):
            evidence.append("Final -ie (common South Sami word ending)")
            score += 0.2

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Suggest South Sami etymologies for a toponym."""
        candidates: list[EtymologyCandidate] = []
        form = components[0].component if components else ""
        form_lower = form.lower()

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                candidates.append(
                    EtymologyCandidate(
                        lemma=f"*{element}",
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.55,
                    )
                )

        return candidates
