"""West Frisian language module for toponymic analysis.

West Frisian (Frysk) is a West Germanic language spoken in Friesland province
of the Netherlands by ~470,000 people. It is the closest living relative of
English. Frisian toponymy features: -um (< OFris. -hēm), -wâld (forest),
-gea (district), -stins (fortified house). Note: Old Frisian is handled as
a separate historical module for medieval name forms.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class WestFrisianModule(BaseLanguageModule):
    """Language module for West Frisian toponyms."""

    language_code = "fry"
    language_name = "West Frisian"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Anglo-Frisian"
    period = "Modern (1550 CE–present)"
    script = "Latn"

    prefixes = [
        "Grut-",
        "Lyts-",
        "Ald-",
        "Nij-",
        "East-",
        "West-",
    ]

    suffixes = [
        "-um",
        "-wâld",
        "-wâlde",
        "-gea",
        "-stins",
        "-bûr",
        "-wier",
        "-terp",
        "-dyk",
        "-mar",
        "-feart",
        "-sleat",
        "-wier",
    ]

    stems = [
        "wetter",
        "stien",
        "hout",
        "lân",
        "sân",
        "mar",
        "terp",
        "dyk",
        "bûr",
        "tsjerke",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "grut": "large",
            "lyts": "small",
            "ald": "old",
            "nij": "new",
            "east": "east",
            "west": "west",
            "um": "home, settlement (< -hēm)",
            "wâld": "forest",
            "wâlde": "forest",
            "gea": "district, region",
            "stins": "fortified house",
            "bûr": "farm, dwelling",
            "wier": "mound, terp",
            "terp": "artificial dwelling mound",
            "dyk": "dike",
            "mar": "lake",
            "feart": "canal",
            "sleat": "ditch",
            "wetter": "water",
            "stien": "stone",
            "hout": "wood",
            "lân": "land",
            "sân": "sand",
            "tsjerke": "church",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a West Frisian toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 1:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="prefix",
                        lemma=prefix,
                        meaning=self._element_meaning(prefix),
                        confidence=0.7,
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
                        confidence=0.7,
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
        """Classify whether a name form belongs to West Frisian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"West Frisian suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"West Frisian prefix {prefix}-")
                score += 0.25
                break

        frisian_markers = ["â", "û", "ê", "ij"]
        for marker in frisian_markers:
            if marker in form_lower:
                evidence.append(f"Frisian grapheme '{marker}'")
                score += 0.25
                break

        frisian_elements = ["terp", "wier", "stins", "gea", "feart"]
        for elem in frisian_elements:
            if elem in form_lower:
                evidence.append(f"Frisian element '{elem}'")
                score += 0.25
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
            "um": ("*haimaz", "home (< OFris. -hēm)", ["OE hām", "En. home"]),
            "wâld": ("*walþuz", "forest", ["OE weald", "De. Wald"]),
            "terp": ("*þerpa-", "dwelling mound", ["NL terp", "De. Wurt"]),
            "bûr": ("*būraz", "dwelling, farmer", ["OE būr", "En. bower"]),
            "dyk": ("*dīkaz", "dike", ["OE dīc", "En. dike"]),
            "mar": ("*mari-", "lake, sea", ["OE mere", "En. mere"]),
            "stins": ("*stainaz", "stone house", ["OFris. stēnhūs"]),
            "gea": ("*gawją", "district, region", ["OE gā", "De. Gau"]),
        }
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in lexicon:
                lemma, meaning, cognates = lexicon[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.7,
                        cognates=cognates,
                        sources=["Fryske Akademy, Toponymic Database"],
                    )
                )
        return candidates
