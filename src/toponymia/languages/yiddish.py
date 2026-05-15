"""Yiddish language module for toponymic analysis.

Yiddish (ייִדיש) is a Germanic language with High German base and significant
Hebrew/Aramaic and Slavic components, historically spoken by Ashkenazi Jews
across Central and Eastern Europe. Yiddish toponymy reflects Jewish settlement
patterns: -shtot (city), -dorf (village), -berg, and distinctive shtetl names.
Many original Yiddish place names survive in oral tradition even where the
communities were destroyed.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class YiddishModule(BaseLanguageModule):
    """Language module for Yiddish toponyms."""

    language_code = "yid"
    language_name = "Yiddish"
    family = "Indo-European"
    branch = "Germanic > West Germanic > High German"
    period = "Medieval–Modern (1000 CE–present)"
    script = "Hebr"

    prefixes = [
        "Alt-",
        "Nay-",
        "Groys-",
        "Kleyn-",
    ]

    suffixes = [
        "-shtot",
        "-dorf",
        "-berg",
        "-burg",
        "-hoyz",
        "-feld",
        "-vald",
        "-land",
        "-shtib",
        "-grod",
        "-ov",
        "-its",
        "-itz",
    ]

    stems = [
        "shtetl",
        "shtot",
        "yid",
        "shul",
        "mark",
        "gas",
        "brunem",
        "vaser",
        "goldene",
    ]

    def _element_meaning(self, element: str) -> str:
        meanings = {
            "alt": "old",
            "nay": "new",
            "groys": "large",
            "kleyn": "small",
            "shtot": "city",
            "dorf": "village",
            "berg": "mountain",
            "burg": "castle",
            "hoyz": "house",
            "feld": "field",
            "vald": "forest",
            "land": "land",
            "shtib": "room, house",
            "grod": "city (< Slavic gorod)",
            "shtetl": "small town",
            "shul": "synagogue",
            "mark": "market",
            "gas": "street",
            "vaser": "water",
        }
        return meanings.get(element.lower(), "")

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Yiddish toponym into morphological components."""
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
        """Classify whether a name form belongs to Yiddish."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-") for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Yiddish suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-") for p in self.prefixes]:
            if form_lower.startswith(prefix.lower()):
                evidence.append(f"Yiddish prefix {prefix}-")
                score += 0.25
                break

        yiddish_markers = ["sh", "oy", "ey", "ay"]
        for marker in yiddish_markers:
            if marker in form_lower:
                evidence.append(f"Yiddish phonetic marker '{marker}'")
                score += 0.2
                break

        shtetl_patterns = ["shtetl", "shul", "shtot", "shtib"]
        for pattern in shtetl_patterns:
            if pattern in form_lower:
                evidence.append(f"Yiddish settlement term '{pattern}'")
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
            "shtot": ("*stat", "city, place", ["MHG stat", "De. Stadt"]),
            "dorf": ("*þurpa-", "village", ["De. Dorf", "NL dorp"]),
            "berg": ("*bergaz", "mountain", ["De. Berg", "En. barrow"]),
            "shtetl": ("*stat", "small town (dimin.)", ["De. Städtchen"]),
            "shul": ("schul", "synagogue (< Lat. schola)", ["De. Schule"]),
            "grod": ("*gordъ", "city (Slavic loan)", ["Ru. gorod", "Pl. gród"]),
            "vald": ("*walþuz", "forest", ["De. Wald", "En. wold"]),
            "mark": ("*markō", "market, border", ["De. Markt", "En. market"]),
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
                        sources=["Weinreich, History of the Yiddish Language"],
                    )
                )
        return candidates
