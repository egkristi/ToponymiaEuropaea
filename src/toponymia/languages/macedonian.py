"""Macedonian language module for toponymic analysis.

Macedonian (македонски) is a South Slavic language spoken in North
Macedonia. Its toponymy features -ovo/-evo possessive endings, -ane/-ani
inhabitant plurals, and -ište place suffixes. A strong Ottoman/Turkish
layer overlays older Slavic names. Key examples: Skopje (< *skopiti
'to watch'), Ohrid (possibly pre-Slavic), Bitola (< *obitělь 'monastery').
The language lacks case endings (unique among South Slavic with Bulgarian).
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class MacedonianModule(BaseLanguageModule):
    """Language module for Macedonian toponyms."""

    language_code = "mkd"
    language_name = "Macedonian"
    family = "Indo-European"
    branch = "Slavic > South Slavic > Eastern"
    period = "Modern (1000 CE–present)"
    script = "Latn"

    prefixes = [
        "Novo-",
        "Staro-",
        "Gorni-",
        "Dolni-",
        "Sv-",
        "Belo-",
        "Crno-",
        "Debar-",
        "Kriva-",
        "Makedonski-",
    ]

    suffixes = [
        "-ovo",
        "-evo",
        "-ane",
        "-ani",
        "-ište",
        "-ica",
        "-ec",
        "-nik",
        "-ino",
        "-ci",
    ]

    stems = [
        "grad",
        "selo",
        "pole",
        "reka",
        "gora",
        "dol",
        "kamen",
        "voda",
        "brod",
        "drvo",
    ]

    def _element_meaning(self, element: str) -> str:
        """Look up meaning for a toponymic element."""
        meanings = {
            "novo": "new",
            "staro": "old",
            "gorni": "upper",
            "dolni": "lower",
            "sv": "saint",
            "belo": "white",
            "crno": "black",
            "kriva": "crooked",
            "ovo": "possessive (masc.)",
            "evo": "possessive (palatal)",
            "ane": "inhabitants",
            "ani": "inhabitants",
            "ište": "place of",
            "ica": "diminutive / river",
            "ec": "diminutive (masc.)",
            "ino": "possessive",
            "grad": "city",
            "selo": "village",
            "pole": "field",
            "reka": "river",
            "gora": "mountain",
            "dol": "valley",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Macedonian toponym into morphological components."""
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
        """Classify whether a name form belongs to Macedonian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Macedonian suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Macedonian prefix {prefix}-")
                score += 0.25
                break

        macedonian_markers = ["ќ", "ѓ", "џ"]
        for marker in macedonian_markers:
            if marker in form_lower:
                evidence.append(f"Macedonian-specific grapheme '{marker}'")
                score += 0.25
                break

        if form_lower.endswith(("ište", "ani")):
            evidence.append("Common Macedonian toponymic ending")
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
            "grad": ("*gordъ", "city", ["Sr. grad", "Bg. grad"]),
            "selo": ("*selo", "village", ["Sr. selo", "Bg. selo"]),
            "pole": ("*polje", "field", ["Sr. polje", "Bg. pole"]),
            "reka": ("*rěka", "river", ["Sr. reka", "Bg. reka"]),
            "gora": ("*gora", "mountain", ["Sr. gora", "Bg. gora"]),
            "dol": ("*dolъ", "valley", ["Sr. dol", "Bg. dol"]),
            "brod": ("*brodъ", "ford", ["Sr. brod", "Bg. brod"]),
            "novo": ("*novъ", "new", ["Sr. novo", "Bg. novo"]),
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
                        sources=["Duridanov, Mestnite imena v Makedonija"],
                    )
                )
        return candidates
