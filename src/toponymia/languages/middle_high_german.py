"""Middle High German language module.

Middle High German (1050-1350 CE) was the courtly literary language
of the German-speaking lands. Important for dating Germanic place-name
forms in central Europe, particularly those reflecting the High Medieval
period of castle-building and town foundation.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class MiddleHighGermanModule(BaseLanguageModule):
    """Language module for Middle High German toponyms."""

    language_code = "gmh"
    language_name = "Middle High German"
    family = "Indo-European"
    branch = "Germanic > West Germanic > High German"
    period = "1050-1350 CE"
    script = "Latn"

    suffixes = [
        "-stein",  # stone, castle
        "-burg",  # castle, fortification
        "-heim",  # home, settlement
        "-dorf",  # village
        "-berg",  # mountain
        "-feld",  # field
        "-bach",  # brook
        "-wald",  # forest
        "-hausen",  # houses, settlement
        "-kirchen",  # church
        "-brücke",  # bridge
        "-brunn",  # spring, well
        "-au",  # water meadow (< ouwe)
        "-ach",  # water (< ahe)
        "-weil",  # settlement (< Lat. villa)
        "-zell",  # cell, hermitage (< Lat. cella)
        "-stetten",  # place
        "-ingen",  # patronymic
    ]

    prefixes = [
        "Niuwe-",  # new (< niuwe)
        "Alt-",  # old
        "Grōz-",  # great
        "Klein-",  # small
        "Ober-",  # upper
        "Nider-",  # lower
        "Schœn-",  # beautiful
        "Hohen-",  # high
        "Liehten-",  # bright
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Middle High German toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted([s.lstrip("-") for s in self.suffixes], key=len, reverse=True)

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix.lower()):
                matched_suffix = suffix
                break

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            suffix_part = form[len(form) - len(matched_suffix) :]

            if stem:
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=0,
                        morph_type="compound_modifier",
                        confidence=0.6,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="compound_head",
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
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Middle High German."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"suffix -{suffix}")
                score += 0.4
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"prefix {prefix}-")
                score += 0.3
                break

        # MHG orthographic/phonological features
        mhg_features = ["uo", "ie", "üe", "ou", "öu", "iu"]
        for feat in mhg_features:
            if feat in form_lower:
                evidence.append(f"MHG vowel '{feat}'")
                score += 0.15
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="high-medieval" if confidence > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "stein": ("stein", "stone, castle", ["OHG stein", "NHG Stein"]),
            "burg": ("burc", "castle, fortification", ["OHG burg", "NHG Burg"]),
            "heim": ("heim", "home, settlement", ["OHG heim", "ON heimr"]),
            "dorf": ("dorf", "village", ["OHG dorf", "NHG Dorf"]),
            "berg": ("berc", "mountain", ["OHG berg", "NHG Berg"]),
            "bach": ("bach", "brook", ["OHG bah", "NHG Bach"]),
            "wald": ("walt", "forest", ["OHG wald", "NHG Wald"]),
            "hausen": ("hūsen", "houses, settlement", ["OHG hūs"]),
            "brunn": ("brunne", "spring, well", ["OHG brunno"]),
            "au": ("ouwe", "water meadow", ["OHG ouwa", "NHG Aue"]),
            "ingen": ("-ingen", "patronymic", ["OHG -ingun"]),
            "weil": ("wīler", "settlement < Lat. villare", ["Lat. villa"]),
            "zell": ("zelle", "cell < Lat. cella", ["Lat. cella"]),
        }

        candidates: list[EtymologyCandidate] = []
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in meanings:
                lemma, meaning, cognates = meanings[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=cognates,
                        sound_changes=["OHG uo > MHG uo", "OHG ī > MHG ī"],
                        sources=["Lexer MHG dictionary", "Bach 1953"],
                    )
                )

        return candidates
