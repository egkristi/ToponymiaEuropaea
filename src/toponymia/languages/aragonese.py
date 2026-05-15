"""Aragonese language module for toponymic analysis.

Aragonese is a Romance language of the Pyrenean region of Aragon, Spain.
Its toponymy preserves pre-Roman (Basque/Iberian/Celtic) substrate,
especially in the northern valleys, with distinctive Pyrenean geographic
vocabulary and sound changes different from Castilian.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AragoneseModule(BaseLanguageModule):
    """Language module for Aragonese toponyms."""

    language_code = "arg"
    language_name = "Aragonese"
    family = "Indo-European"
    branch = "Romance > Western > Ibero-Romance > Pyrenean"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Val-",
        "Pueyo-",
        "Peña-",
        "Selva-",
        "Campo-",
        "Fuent-",
        "Plan-",
        "San-",
        "Bal-",
        "Foz-",
    ]

    suffixes = [
        "-ero",
        "-al",
        "-ón",
        "-uelo",
        "-ás",
        "-és",
        "-ué",
        "-iello",
        "-arre",
        "-arri",
        "-eta",
        "-ato",
    ]

    stems = [
        "val",
        "pueyo",
        "peña",
        "campo",
        "fuent",
        "selva",
        "plan",
        "foz",
        "barranco",
        "ibón",
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
            "val": "valley",
            "pueyo": "hill (< Lat. podium)",
            "peña": "rock, cliff",
            "selva": "forest",
            "campo": "field",
            "fuent": "spring, fountain",
            "plan": "flat area, plateau",
            "san": "saint",
            "bal": "valley (variant)",
            "foz": "gorge, narrow pass",
            "ero": "place of, agent",
            "al": "place with abundance of",
            "ón": "augmentative",
            "uelo": "diminutive",
            "ás": "place with",
            "és": "inhabitant of",
            "ué": "Aragonese diphthong marker",
            "iello": "diminutive (< -ellum)",
            "arre": "Basque substrate element",
            "arri": "stone (Basque substrate)",
            "eta": "diminutive/collective",
        }
        return meanings.get(element.lower(), "")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Aragonese."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0
        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Aragonese suffix -{suffix}")
                score += 0.3
                break
        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Aragonese prefix {prefix}-")
                score += 0.25
                break
        # Aragonese-specific diphthongization (ue < o, ie < e)
        if "ué" in form_lower or "iello" in form_lower:
            evidence.append("Aragonese diphthongization")
            score += 0.2
        # Basque substrate (northern Aragon)
        basque_markers = ["arre", "arri", "gorri", "berri", "etxe"]
        for marker in basque_markers:
            if marker in form_lower:
                evidence.append(f"Basque substrate element '{marker}'")
                score += 0.2
                break
        # Preserved f- (unlike Castilian h-)
        if form_lower.startswith("f") and not form_lower.startswith("fu"):
            evidence.append("Preserved initial f- (vs. Castilian h-)")
            score += 0.15
        # Pyrenean geographical terms
        if "ibón" in form_lower or "foz" in form_lower or "pueyo" in form_lower:
            evidence.append("Pyrenean Aragonese lexical element")
            score += 0.2
        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "val": ("vallem", "valley", ["Sp. valle", "Cat. vall"]),
            "pueyo": ("podium", "hill", ["Oc. puèg", "Cat. puig"]),
            "peña": ("pinnam", "rock", ["Sp. peña", "Ast. peña"]),
            "foz": ("faucem", "gorge, throat", ["Sp. hoz", "Pt. foz"]),
            "campo": ("campum", "field", ["Sp. campo", "Cat. camp"]),
            "fuent": ("fontem", "spring", ["Sp. fuente", "Cat. font"]),
            "selva": ("silvam", "forest", ["Sp. selva", "Cat. selva"]),
            "ibón": ("*ibone", "mountain lake (pre-Roman)", []),
            "arre": ("*arri", "stone (Basque)", ["Basq. harri"]),
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
                        sources=["EBA", "Rohlfs 1935"],
                    )
                )
        return candidates
