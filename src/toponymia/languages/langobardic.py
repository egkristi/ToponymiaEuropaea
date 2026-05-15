"""Langobardic language module.

Langobardic (Lombard) was an East Germanic(?) language spoken by the
Lombards in Northern Italy ca. 568-774 CE. Attestation is limited to
glosses, laws (Edictum Rothari), and personal/place names. Important
substrate in Lombardy and Emilia-Romagna place-names.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LangobardicModule(BaseLanguageModule):
    """Language module for Langobardic/Lombard toponyms."""

    language_code = "lng"
    language_name = "Langobardic"
    family = "Indo-European"
    branch = "Germanic > East Germanic (?)"
    period = "568-774 CE"
    script = "Latn"

    suffixes = [
        "-fara",  # clan settlement
        "-sala",  # hall, dwelling
        "-wald",  # forest / power
        "-aldo",  # Romanized -wald
        "-ingo",  # patronymic (< *-ing)
        "-engo",  # patronymic variant
        "-ago",  # < *-akr (field) or patronymic
        "-asco",  # settlement suffix
        "-ate",  # collective suffix
        "-braida",  # broad field
        "-garda",  # enclosure
        "-stalla",  # stable, place
        "-mund",  # protection
    ]

    prefixes = [
        "Ari-",  # eagle
        "Gari-",  # spear
        "Guntha-",  # battle
        "Wald-",  # rule, power
        "Bert-",  # bright
        "Grim-",  # mask, helmet
        "Lan-",  # land
        "Rot-",  # fame (cf. Rothari)
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Langobardic toponym into morphological components."""
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
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.6,
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
        """Classify whether a name form is likely Langobardic."""
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

        # Langobardic phonological markers
        markers = ["sch", "braida", "fara", "sala"]
        for m in markers:
            if m in form_lower:
                evidence.append(f"Langobardic element '{m}'")
                score += 0.15

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="early-medieval" if confidence > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "fara": ("fara", "clan, kindred group", ["OHG fara", "Gothic faran"]),
            "sala": ("sala", "hall, dwelling", ["OHG sal", "Gothic saljan"]),
            "wald": ("wald", "power, rule; forest", ["OHG walt", "Gothic waldan"]),
            "braida": ("braida", "broad plain", ["OHG breit", "Gothic braiþs"]),
            "garda": ("garda", "enclosure", ["Gothic gards", "ON garðr"]),
            "ingo": ("-ing", "patronymic suffix", ["OHG -ing", "ON -ingr"]),
            "engo": ("-ing", "patronymic (Romanized)", ["OHG -ing"]),
            "asco": ("-asco", "settlement suffix", []),
            "stalla": ("stalla", "stable, place", ["OHG stal"]),
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
                        sound_changes=["Gmc. *a > Lgb. a", "Gmc. *ō > Lgb. ō/a"],
                        sources=["Edictum Rothari", "Bruckner 1895"],
                    )
                )

        return candidates
