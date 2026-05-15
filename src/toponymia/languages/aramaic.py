"""Aramaic language module for toponymic analysis.

Aramaic served as the lingua franca of the Near East from c. 900 BCE
through the early Islamic period. Still spoken today as Neo-Aramaic.
Characterized by:
- Emphatic/definite state suffix -ā (status emphaticus)
- Plural suffix -in (masculine), -ātā (feminine)
- Place-name elements from administrative/religious contexts
- Extensive influence on Biblical and NT place-names

Key references:
- Beyer 1986 "The Aramaic Language"
- Kaufman 1974 "The Akkadian Influences on Aramaic"
- Fitzmyer 1979 "A Wandering Aramean: Collected Aramaic Essays"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AramaicModule(BaseLanguageModule):
    """Language module for Aramaic toponyms."""

    language_code = "arc"
    language_name = "Aramaic"
    family = "Afro-Asiatic"
    branch = "Semitic > Central Semitic > Northwest Semitic > Aramaic"
    period = "c. 900 BCE – present (Imperial, Biblical, Syriac, Neo-Aramaic)"
    script = "Armi"

    prefixes = [
        "Beth-",  # house (Beth Anya = Bethany)
        "Bet-",  # house variant
        "Kfar-",  # village (shared with Hebrew)
        "Tell-",  # mound (Tell Halaf)
        "Tur-",  # mountain (Tur Abdin)
        "Ain-",  # spring
        "Bar-",  # son of (in compounds)
        "Deir-",  # monastery (Deir ez-Zor)
    ]

    suffixes = [
        "-ā",  # definite/emphatic state (Golgothā)
        "-tā",  # feminine emphatic (Gat-tā)
        "-in",  # masculine plural
        "-ātā",  # feminine plural
        "-ōn",  # place/diminutive suffix
        "-ānā",  # gentilicium/adjective
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "beth": "baytā (house, place)",
        "bet": "baytā (house, place)",
        "kfar": "kafrā (village)",
        "tell": "tellā (mound, ruin hill)",
        "tur": "ṭūrā (mountain)",
        "ain": "'aynā (spring, water source)",
        "bar": "bar (son of)",
        "deir": "dayrā (monastery, enclosure)",
        "gat": "gattā (winepress)",
        "golgotha": "gulgultā (skull, rounded hill)",
        "gethsemane": "gat-šmānē (oil press)",
        "tabitha": "ṭabyāṯā (gazelle)",
        "maranatha": "māranā ṯā (our Lord has come)",
        "abba": "abbā (father)",
        "mammon": "māmōnā (wealth, riches)",
        "aceldama": "ḥaqel demā (field of blood)",
        "dimashq": "dammeśeq (well-watered place?)",
        "bab": "bābā (gate, door)",
        "nahar": "nahrā (river)",
        "maqam": "maqāmā (holy site, station)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Aramaic toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes],
            key=len,
            reverse=True,
        )

        matched_prefix = None
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                matched_prefix = prefix
                break

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_prefix:
            prefix_part = form[: len(matched_prefix)]
            remainder = form[len(matched_prefix) :]
            if remainder.startswith(("-", " ")):
                remainder = remainder[1:]
                prefix_part = form[: len(matched_prefix) + 1]

            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="compound_head",
                    lemma=matched_prefix,
                    meaning=self.ELEMENT_MEANINGS.get(matched_prefix),
                    confidence=0.8,
                )
            )
            if matched_suffix and remainder.lower().endswith(matched_suffix):
                stem = remainder[: len(remainder) - len(matched_suffix)]
                if stem:
                    results.append(
                        SegmentationResult(
                            component=stem,
                            position=1,
                            morph_type="stem",
                            lemma=stem.lower(),
                            confidence=0.5,
                        )
                    )
                results.append(
                    SegmentationResult(
                        component=remainder[len(remainder) - len(matched_suffix) :],
                        position=len(results),
                        morph_type="suffix",
                        lemma=matched_suffix,
                        meaning=self.ELEMENT_MEANINGS.get(matched_suffix),
                        confidence=0.7,
                    )
                )
            else:
                results.append(
                    SegmentationResult(
                        component=remainder,
                        position=1,
                        morph_type="compound_modifier",
                        lemma=remainder.lower(),
                        confidence=0.5,
                    )
                )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="stem",
                    lemma=stem.lower(),
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.7,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Aramaic in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        aramaic_prefixes = ["beth", "bet", "deir", "tell", "tur", "bar"]
        for prefix in aramaic_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                evidence.append(f"Aramaic prefix {prefix}-")
                score += 0.4
                break

        if (
            form_lower.endswith(("ā", "a"))
            and not form_lower.endswith("ia")
            and len(form_lower) > 4
        ):
            evidence.append("Aramaic emphatic state -ā")
            score += 0.2

        aramaic_elements = ["golgotha", "gethsemane", "dimashq", "nahar"]
        for elem in aramaic_elements:
            if elem in form_lower:
                evidence.append(f"Known Aramaic toponym '{elem}'")
                score += 0.4
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Imperial Aramaic (900 BCE – 200 CE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Aramaic components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            lemma_key = comp.lemma.lower().rstrip("-")
            meaning = self.ELEMENT_MEANINGS.get(lemma_key)
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma_key,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=[],
                        sound_changes=[],
                        sources=["Beyer 1986", "Fitzmyer 1979"],
                    )
                )
        return candidates
