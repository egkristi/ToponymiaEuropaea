"""Old East Slavic language module.

Old East Slavic (Древнерусский язык) was the common ancestor of
Russian, Ukrainian, and Belarusian, spoken from the 10th to 14th
century CE in Kievan Rus'. Major toponymic suffixes include -gorod,
-grad (city), and -ovo/-evo (possessive). Well-attested from
chronicles, birch bark letters, and inscriptions.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldEastSlavicModule(BaseLanguageModule):
    """Language module for Old East Slavic toponyms."""

    language_code = "orv"
    language_name = "Old East Slavic"
    family = "Indo-European"
    branch = "Slavic > East Slavic"
    period = "10th-14th century CE"
    script = "Cyrl"

    suffixes = [
        "-gorod",  # city, fortified settlement
        "-grad",  # city (South Slavic variant)
        "-ovo",  # possessive
        "-evo",  # possessive (after palatals)
        "-ichi",  # descendants of
        "-sk",  # adjectival/settlement
        "-pol",  # field
        "-slavl",  # glory (theophoric/princely)
    ]

    prefixes = [
        "Nov-",  # new (Novgorod)
        "Bel-",  # white
        "Vladi-",  # rule/power
        "Svjato-",  # holy
        "Pere-",  # across/over
    ]

    stems = [
        "novgorod",  # Novgorod
        "kyiv",  # Kyiv (< Kyi personal name)
        "vladimir",  # Vladimir
        "smolensk",  # Smolensk
        "polotsk",  # Polotsk
        "chernigov",  # Chernigov
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Old East Slavic toponym."""
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
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.6,
                )
            )
        else:
            # Check for prefixes
            matched_prefix = None
            for prefix in sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True):
                if form_lower.startswith(prefix.lower()):
                    matched_prefix = prefix
                    break

            if matched_prefix:
                results.append(
                    SegmentationResult(
                        component=form[: len(matched_prefix)],
                        position=0,
                        morph_type="prefix",
                        lemma=matched_prefix,
                        confidence=0.6,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(matched_prefix) :],
                        position=1,
                        morph_type="stem",
                        confidence=0.5,
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
        """Classify whether a name form is likely Old East Slavic."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"suffix -{suffix}")
                score += 0.35
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"prefix {prefix}-")
                score += 0.3
                break

        # Distinctive East Slavic phonological markers
        if "gorod" in form_lower or "grad" in form_lower:
            evidence.append("settlement element -gorod/-grad")
            score += 0.2

        # Full-liquid (polnoglasie) marker
        polnoglasie = ["orod", "olod", "olot", "olog", "oron"]
        for marker in polnoglasie:
            if marker in form_lower:
                evidence.append(f"polnoglasie (pleophony) '{marker}'")
                score += 0.2
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="kievan-rus" if confidence > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "gorod": ("gordъ", "city, fortified settlement", ["Russian gorod", "Ukrainian horod"]),
            "grad": ("gradъ", "city (bookish)", ["OCS gradъ", "Serbian grad"]),
            "ovo": ("-ovъ", "possessive suffix", ["Common Slavic *-ovъ"]),
            "evo": ("-evъ", "possessive (palatal)", ["Common Slavic *-evъ"]),
            "sk": ("-ьskъ", "adjectival/locative", ["Common Slavic *-ьskъ"]),
            "nov": ("novъ", "new", ["OCS novъ", "Russian novyj"]),
            "bel": ("bělъ", "white", ["OCS bělъ", "Russian belyj"]),
            "vladi": ("vlad-", "rule, power", ["OCS vladěti", "Russian vladet'"]),
            "slavl": ("slavь", "glory", ["OCS slava", "Russian slava"]),
            "pol": ("polje", "field", ["OCS polje", "Russian pole"]),
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
                        sound_changes=["*TorT > OES ToroT (pleophony)"],
                        sources=["Vasmer 1953-1958", "Primary Chronicle"],
                    )
                )

        return candidates
