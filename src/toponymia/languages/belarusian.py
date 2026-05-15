"""Belarusian language module for toponymic analysis.

Belarusian (беларуская) is an East Slavic language spoken in Belarus.
Its toponymy features -ava endings, -оўка/-ічы/-цы settlement suffixes,
and a significant Baltic substrate layer visible in hydronyms. The akanne
(unstressed o → a) is reflected in place names. Key examples: Minsk
(< *měnъ 'exchange'), Brest (possibly Baltic origin), Homiel/Gomel.
Polish and Lithuanian contact layers are present in the west.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class BelarusianModule(BaseLanguageModule):
    """Language module for Belarusian toponyms."""

    language_code = "bel"
    language_name = "Belarusian"
    family = "Indo-European"
    branch = "Slavic > East Slavic"
    period = "Modern (1300 CE–present)"
    script = "Latn"

    prefixes = [
        "Novo-",
        "Staro-",
        "Vjalikі-",
        "Malі-",
        "Verchnі-",
        "Nіžnі-",
        "Bela-",
        "Čorna-",
        "Pod-",
        "Za-",
    ]

    suffixes = [
        "-ava",
        "-oŭka",
        "-ičy",
        "-cy",
        "-ín",
        "-ava",
        "-sk",
        "-ščyna",
        "-oŭ",
        "-ičy",
    ]

    stems = [
        "horad",
        "raka",
        "bor",
        "pole",
        "balota",
        "les",
        "azero",
        "rečka",
        "brod",
        "dub",
    ]

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "novo": "new",
            "staro": "old",
            "vjalikі": "great",
            "malі": "small",
            "verchnі": "upper",
            "nіžnі": "lower",
            "bela": "white",
            "čorna": "black",
            "pod": "below",
            "za": "beyond",
            "ava": "place / possessive (fem.)",
            "oŭka": "settlement diminutive",
            "ičy": "patronymic plural",
            "cy": "inhabitants",
            "ín": "possessive",
            "sk": "adjectival / regional",
            "ščyna": "region of",
            "horad": "city",
            "raka": "river",
            "bor": "pine forest",
            "pole": "field",
            "balota": "swamp",
            "les": "forest",
            "azero": "lake",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Belarusian toponym into morphological components."""
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
        """Classify whether a name form belongs to Belarusian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Belarusian suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Belarusian prefix {prefix}-")
                score += 0.25
                break

        belarusian_markers = ["ŭ", "š", "č", "ž", "dz"]
        for marker in belarusian_markers:
            if marker in form_lower:
                evidence.append(f"Belarusian orthographic marker '{marker}'")
                score += 0.2
                break

        if form_lower.endswith(("ščyna", "oŭka")):
            evidence.append("Distinctive Belarusian derivational suffix")
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
            "horad": ("*gordъ", "city", ["Ru. gorod", "Uk. horod"]),
            "raka": ("*rěka", "river", ["Ru. reka", "Uk. rika"]),
            "bor": ("*borъ", "pine forest", ["Ru. bor", "Pl. bór"]),
            "pole": ("*polje", "field", ["Ru. pole", "Uk. pole"]),
            "balota": ("*bolto", "swamp", ["Ru. boloto", "Uk. boloto"]),
            "les": ("*lěsъ", "forest", ["Ru. les", "Cz. les"]),
            "azero": ("*ezero", "lake", ["Ru. ozero", "Bg. ezero"]),
            "bela": ("*bělъ", "white", ["Ru. belyj", "Pl. biały"]),
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
                        sources=["Žučkevič, Kratkij toponimičeskij slovar' Belorussii"],
                    )
                )
        return candidates
