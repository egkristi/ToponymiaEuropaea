"""Croatian language module for toponymic analysis.

Croatian (hrvatski) is a South Slavic language written in Latin script.
Its toponymy is characterized by Adriatic coastal names with Italian/Venetian
layers (Split < Lat. palatium, Dubrovnik < dub 'oak'), inland Slavic
settlement patterns (-ovo, -ac, -ica), and Hungarian contact in the north.
The Dalmatian coast preserves pre-Slavic Romance substrate in many names.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class CroatianModule(BaseLanguageModule):
    """Language module for Croatian toponyms."""

    language_code = "hrv"
    language_name = "Croatian"
    family = "Indo-European"
    branch = "Slavic > South Slavic > Western"
    period = "Modern (1100 CE–present)"
    script = "Latn"

    prefixes = [
        "Novo-",
        "Staro-",
        "Veliko-",
        "Malo-",
        "Gornji-",
        "Donji-",
        "Pod-",
        "Pri-",
        "Sv-",
        "Beli-",
    ]

    suffixes = [
        "-ovo",
        "-ac",
        "-ica",
        "-nik",
        "-ane",
        "-evo",
        "-ište",
        "-grad",
        "-ovec",
        "-ina",
    ]

    stems = [
        "grad",
        "dub",
        "polje",
        "gora",
        "rijeka",
        "most",
        "otok",
        "brdo",
        "luka",
        "drvo",
    ]

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "novo": "new",
            "staro": "old",
            "veliko": "great",
            "malo": "small",
            "gornji": "upper",
            "donji": "lower",
            "pod": "below",
            "pri": "near",
            "sv": "saint",
            "beli": "white",
            "ovo": "possessive (masc.)",
            "ac": "settlement suffix",
            "ica": "diminutive / river",
            "nik": "agent, place",
            "ane": "inhabitants",
            "ište": "place of",
            "grad": "city, castle",
            "dub": "oak",
            "polje": "field",
            "gora": "mountain",
            "rijeka": "river",
            "most": "bridge",
            "otok": "island",
            "luka": "harbour",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Croatian toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()) and len(form_lower) > len(prefix) + 1:
                results.append(
                    SegmentationResult(
                        component=form[: len(prefix)],
                        position=0,
                        morph_type="compound_modifier",
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
        """Classify whether a name form belongs to Croatian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Croatian suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Croatian prefix {prefix}-")
                score += 0.25
                break

        croatian_markers = ["ije", "lj", "nj", "dž"]
        for marker in croatian_markers:
            if marker in form_lower:
                evidence.append(f"Croatian phoneme marker '{marker}'")
                score += 0.2
                break

        # Croatian ijekavian reflex
        if "ije" in form_lower:
            evidence.append("Ijekavian reflex (Croatian)")
            score += 0.15

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for segmented components."""
        candidates: list[EtymologyCandidate] = []
        lexicon = {
            "grad": ("*gordъ", "city, fortification", ["Sr. grad", "Cz. hrad"]),
            "dub": ("*dǫbъ", "oak", ["Sr. dub", "Ru. dub"]),
            "rijeka": ("*rěka", "river", ["Sr. reka", "Cz. řeka"]),
            "gora": ("*gora", "mountain", ["Sr. gora", "Sl. gora"]),
            "polje": ("*polje", "field", ["Sr. polje", "Sl. polje"]),
            "most": ("*mostъ", "bridge", ["Sr. most", "Cz. most"]),
            "otok": ("*otokъ", "island (lit. 'what flows around')", ["Sr. otok"]),
            "luka": ("*lǫka", "harbour, meadow", ["Sr. luka", "Sl. loka"]),
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
                        sources=["Skok, Etimologijski rječnik hrvatskoga jezika"],
                    )
                )
        return candidates
