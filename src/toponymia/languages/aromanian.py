"""Aromanian language module for toponymic analysis.

Aromanian (Vlach) is an Eastern Romance language spoken by scattered
communities across the southern Balkans (Greece, North Macedonia,
Albania, Bulgaria, Romania). Its toponymy reflects transhumance
pastoral culture, with heavy Slavic and Greek contact layers.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AromanianModule(BaseLanguageModule):
    """Language module for Aromanian toponyms."""

    language_code = "rup"
    language_name = "Aromanian"
    family = "Indo-European"
    branch = "Romance > Eastern"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Vlaho-",
        "Vla-",
        "Mosco-",
        "Gramu-",
        "Arma-",
        "Sâr-",
        "Câmpu-",
        "Munts-",
        "Gura-",
        "Fântân-",
    ]

    suffixes = [
        "-ean",
        "-ișt",
        "-ov",
        "-ova",
        "-ești",
        "-ari",
        "-ură",
        "-inu",
        "-eț",
        "-ane",
        "-ațu",
        "-ălu",
    ]

    stems = [
        "munte",
        "vale",
        "apă",
        "câmpu",
        "pădure",
        "piatra",
        "fântână",
        "gura",
        "stână",
        "cârstig",
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()
        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix.lower()) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                results.append(
                    SegmentationResult(
                        component=stem, position=0, morph_type="compound_modifier", confidence=0.6
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(form) - len(suffix) :],
                        position=1,
                        morph_type="compound_head",
                        lemma=suffix,
                        meaning=self._element_meaning(suffix),
                        confidence=0.7,
                    )
                )
                return results
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
                        confidence=0.65,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(prefix) :], position=1, morph_type="stem", confidence=0.5
                    )
                )
                return results
        results.append(
            SegmentationResult(component=form, position=0, morph_type="stem", confidence=0.3)
        )
        return results

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "vlaho": "Vlach, Romanian-speaking",
            "vla": "Vlach (short form)",
            "mosco": "Moscopolitan (Aromanian town)",
            "gramu": "Gramos mountain area",
            "arma": "Aromanian settlement",
            "sâr": "salt (< Lat. sal)",
            "câmpu": "field, plain",
            "munts": "mountain",
            "gura": "mouth (of river/valley)",
            "fântân": "fountain, spring",
            "ean": "inhabitant of, pertaining to",
            "ișt": "place (Slavic -ište)",
            "ov": "Slavic possessive",
            "ova": "Slavic possessive (feminine)",
            "ești": "settlement of (people of)",
            "ari": "agent/place",
            "ură": "place characterized by",
            "inu": "diminutive",
            "eț": "diminutive",
        }
        return meanings.get(element.lower(), "")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Aromanian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0
        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Aromanian suffix -{suffix}")
                score += 0.3
                break
        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Aromanian/Vlach prefix {prefix}-")
                score += 0.3
                break
        # Vlach ethnonym marker
        if "vlah" in form_lower or "vlach" in form_lower or "vlasi" in form_lower:
            evidence.append("Vlach ethnonym")
            score += 0.35
        # Aromanian â/ă vowels
        if "â" in form_lower or "ă" in form_lower:
            evidence.append("Romanian/Aromanian central vowel (â/ă)")
            score += 0.2
        # Slavic contact suffixes in Romance context
        if form_lower.endswith(("ov", "ova")):
            evidence.append("Slavic possessive suffix in Balkan Romance")
            score += 0.15
        # Transhumance-related terminology
        transhumance = ["stân", "cârstig", "arman"]
        for term in transhumance:
            if term in form_lower:
                evidence.append(f"Transhumance term '{term}'")
                score += 0.2
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
            "munte": ("montem", "mountain", ["Ro. munte", "It. monte"]),
            "vale": ("vallem", "valley", ["Ro. vale", "It. valle"]),
            "apă": ("aquam", "water", ["Ro. apă", "It. acqua"]),
            "câmpu": ("campum", "field", ["Ro. câmp", "It. campo"]),
            "piatra": ("petra", "stone", ["Ro. piatră", "It. pietra"]),
            "fântână": ("fontanam", "fountain", ["Ro. fântână", "It. fontana"]),
            "gura": ("gula", "mouth, entrance", ["Ro. gură"]),
            "stână": ("*stannam", "sheepfold (substrate)", ["Ro. stână"]),
            "vlaho": ("*wlach-", "Romance-speaker (Germanic exonym)", ["Sl. Vlah"]),
            "pădure": ("*padule", "forest (< paludem)", ["Ro. pădure"]),
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
                        confidence=0.65,
                        cognates=cognates,
                        sources=["Papahagi 1963", "Capidan 1932"],
                    )
                )
        return candidates
