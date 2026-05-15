"""Sardinian language module for toponymic analysis.

Sardinian is the most conservative Romance language, retaining many
archaic Latin features. Its toponymy preserves layers of pre-Roman
(Nuragic/Paleo-Sardinian) substrate, Punic, Latin, Byzantine Greek,
and Catalan/Spanish superstrate elements.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SardinianModule(BaseLanguageModule):
    """Language module for Sardinian toponyms."""

    language_code = "srd"
    language_name = "Sardinian"
    family = "Indo-European"
    branch = "Romance > Southern"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Nur-",
        "Gon-",
        "Sar-",
        "Su-",
        "Sa-",
        "S'-",
        "Mont-",
        "Capo-",
        "Nurag-",
        "Funt-",
    ]

    suffixes = [
        "-ddu",
        "-éddu",
        "-ài",
        "-anu",
        "-èri",
        "-osa",
        "-àra",
        "-ùle",
        "-ìni",
        "-ùra",
        "-àthu",
        "-ìthu",
        "-édda",
    ]

    stems = [
        "nuragh",
        "funt",
        "perda",
        "mura",
        "giara",
        "codula",
        "genn",
        "tanca",
        "arcu",
        "bruncu",
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
            "nur": "Nuragic element (pre-Roman)",
            "gon": "Nuragic element (pre-Roman)",
            "sar": "Paleo-Sardinian root",
            "su": "the (masc. article)",
            "sa": "the (fem. article)",
            "s'": "the (elided article)",
            "mont": "mountain",
            "capo": "headland, cape",
            "nurag": "nuraghe, stone tower",
            "funt": "spring (< Lat. fontem)",
            "ddu": "diminutive",
            "éddu": "diminutive",
            "ài": "place characterized by",
            "anu": "belonging to, place of",
            "èri": "place of activity",
            "osa": "abundant in",
            "àra": "place, area",
        }
        return meanings.get(element.lower(), "")

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form belongs to Sardinian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0
        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Sardinian suffix -{suffix}")
                score += 0.3
                break
        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Sardinian/Nuragic prefix {prefix}-")
                score += 0.3
                break
        # Sardinian conservatism: Latin /k/ before /e,i/ preserved
        if "ke" in form_lower or "ki" in form_lower:
            evidence.append("Preserved Latin velar (ke/ki)")
            score += 0.2
        # Sardinian article su/sa
        if form_lower.startswith(("su ", "sa ")):
            evidence.append("Sardinian definite article")
            score += 0.25
        # Nuragic element
        if form_lower.startswith(("nur", "gon")):
            evidence.append("Pre-Roman Nuragic element")
            score += 0.3
        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "nur": ("*nur-", "pre-Roman element (meaning uncertain)", []),
            "nurag": ("*nur-ak-", "stone tower (Nuragic)", []),
            "funt": ("fontem", "spring", ["It. fonte", "Cat. font"]),
            "mont": ("montem", "mountain", ["It. monte", "Cat. mont"]),
            "perda": ("petra", "stone", ["It. pietra", "Sp. piedra"]),
            "giara": ("*giar-", "basalt plateau (pre-Roman)", []),
            "genn": ("janua", "mountain pass, gate", ["It. porta"]),
            "tanca": ("*tanka", "enclosed field (pre-Roman or Punic)", []),
            "codula": ("*cod-ula", "river gorge (pre-Roman)", []),
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
                        sources=["DES", "Wagner 1960"],
                    )
                )
        return candidates
