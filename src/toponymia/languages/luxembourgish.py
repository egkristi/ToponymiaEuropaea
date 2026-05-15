"""Luxembourgish language module for toponymic analysis.

Luxembourgish (Lëtzebuergesch) is a West Germanic language of the Moselle
Franconian group, official language of Luxembourg. Its toponymy shows a mix
of Germanic suffixes (-burg, -dorf, -weiler, -ingen) with French influence
in border areas. The small territory preserves dense medieval settlement
patterns with distinctive Franconian phonology (e.g. Éisleck, Guttland).
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LuxembourgishModule(BaseLanguageModule):
    """Language module for Luxembourgish toponyms."""

    language_code = "ltz"
    language_name = "Luxembourgish"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Moselle Franconian"
    period = "Modern (1400 CE–present)"
    script = "Latn"

    prefixes = [
        "Nidder-",
        "Ober-",
        "Kleng-",
        "Grouss-",
        "Nei-",
    ]

    suffixes = [
        "-burg",
        "-duerf",
        "-dorf",
        "-weiler",
        "-wiler",
        "-ingen",
        "-ange",
        "-ach",
        "-ert",
        "-em",
        "-ech",
        "-bréck",
        "-haff",
    ]

    stems = [
        "lëtze",
        "buerg",
        "bréck",
        "dall",
        "waasser",
        "steen",
        "bësch",
        "feld",
        "bierg",
        "haff",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "nidder": "lower",
            "ober": "upper",
            "kleng": "small",
            "grouss": "large",
            "nei": "new",
            "burg": "castle, fortification",
            "duerf": "village",
            "dorf": "village",
            "weiler": "hamlet",
            "wiler": "hamlet",
            "ingen": "people of",
            "ange": "meadow (French influence)",
            "ach": "water, stream",
            "ert": "settlement",
            "bréck": "bridge",
            "haff": "farm, estate",
            "buerg": "castle",
            "dall": "valley",
            "waasser": "water",
            "steen": "stone",
            "bësch": "forest",
            "feld": "field",
            "bierg": "mountain",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Luxembourgish toponym into morphological components."""
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
        """Classify whether a name form belongs to Luxembourgish."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Luxembourgish suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Luxembourgish prefix {prefix}-")
                score += 0.25
                break

        ltz_markers = ["ë", "é", "ä"]
        for marker in ltz_markers:
            if marker in form_lower:
                evidence.append(f"Luxembourgish grapheme '{marker}'")
                score += 0.2
                break

        ltz_elements = ["lëtze", "buerg", "bréck", "duerf"]
        for elem in ltz_elements:
            if elem in form_lower:
                evidence.append(f"Luxembourgish element '{elem}'")
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
            "burg": ("*burg-", "fortified place", ["De. Burg", "En. borough"]),
            "duerf": ("*þurpa-", "village", ["De. Dorf", "NL dorp"]),
            "weiler": ("*wīlāri", "hamlet (< Lat. villare)", ["De. Weiler", "Fr. -villiers"]),
            "ingen": ("*-ingōs", "people of", ["De. -ingen", "En. -ing"]),
            "bréck": ("*brukjō", "bridge", ["De. Brücke", "En. bridge"]),
            "haff": ("*huba-", "farm, estate", ["De. Hof", "NL hof"]),
            "bierg": ("*bergaz", "mountain", ["De. Berg", "En. barrow"]),
            "bësch": ("*buskaz", "forest, bush", ["De. Busch", "En. bush"]),
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
                        sources=["Luxemburger Wörterbuch"],
                    )
                )
        return candidates
