"""Proto-Balto-Slavic language module.

Proto-Balto-Slavic is the reconstructed common ancestor of all Baltic and
Slavic languages (3rd-2nd millennium BCE). Key hydronymic elements include
*danu- (river) and *apa- (water). Important for Hans Krahe's "Old European"
hydronymy theory, which identifies a pre-Celtic, pre-Germanic substrate
layer across European river names.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ProtoBaltoSlavicModule(BaseLanguageModule):
    """Language module for Proto-Balto-Slavic toponyms."""

    language_code = "ine-bsl"
    language_name = "Proto-Balto-Slavic"
    family = "Indo-European"
    branch = "Balto-Slavic (reconstructed ancestor)"
    period = "3rd-2nd millennium BCE (reconstructed)"
    script = "Latn"

    suffixes = [
        "-apa",  # water (hydronymic)
        "-ava",  # water, river
        "-upė",  # river (> Baltic)
        "-ina",  # adjectival/diminutive
        "-ista",  # place/river suffix
        "-antā",  # participial (flowing)
    ]

    prefixes = [
        "Danu-",  # river (cf. Don, Danube, Dnieper)
        "Ner-",  # dive/submerge (hydronymic)
        "Sal-",  # salt, flow
        "Vis-",  # all, entire
        "Gar-",  # mountain (> Slavic gora)
    ]

    stems = [
        "danu",  # river (> Danube, Don, Dnieper, Dniester)
        "ner",  # dive/flow (> Neris, Narew, Nera)
        "apa",  # water (> Old Prussian ape)
        "sala",  # island, flow (> Saale, Sala)
        "alba",  # white/river (> Elbe/Labe)
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Proto-Balto-Slavic toponym."""
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
                    confidence=0.5,
                )
            )
        else:
            # Check for known prefixes/stems
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
                        morph_type="compound_modifier",
                        lemma=matched_prefix,
                        confidence=0.5,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(matched_prefix) :],
                        position=1,
                        morph_type="compound_head",
                        confidence=0.4,
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
        """Classify whether a name form is likely Proto-Balto-Slavic."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"PBS hydronymic suffix *-{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"PBS element *{prefix}-")
                score += 0.3
                break

        # Old European hydronymy markers (Krahe)
        old_european = ["dan", "ner", "sal", "alb", "vis"]
        for marker in old_european:
            if marker in form_lower:
                evidence.append(f"Old European hydronym element *{marker}-")
                score += 0.25
                break

        # Baltic-Slavic shared innovations visible in reflexes
        if form_lower.endswith(("ava", "upa")):
            evidence.append("Baltic-Slavic water suffix")
            score += 0.15

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="bronze-age-hydronymic" if confidence > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "danu": ("*danu-", "river, flow", ["Lat. Danuvius", "Ossetic don", "Vedic dā́nu-"]),
            "apa": ("*apā", "water, river", ["OPrussian ape", "Vedic áp-", "Hittite ḫāpa-"]),
            "ava": ("*auā", "water, river", ["Lithuanian ùpė", "Latin aqua (< *akʷā)"]),
            "ner": ("*ner-", "dive, submerge", ["Lithuanian nėrti", "Slavic *norъ"]),
            "sal": ("*sal-", "salt, flowing", ["Latin sal", "Lithuanian saldùs"]),
            "vis": ("*wis-", "all, entire", ["Lithuanian vìsas", "OCS vьsь"]),
            "gar": ("*garā", "mountain", ["Lithuanian girià", "OCS gora"]),
            "ina": ("*-inā", "adjectival suffix", ["Lithuanian -inė", "Slavic -ina"]),
            "alba": ("*albā", "white, river", ["Latin albus", "Lithuanian ãlbas (dial.)"]),
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
                        sound_changes=["PIE *o > PBS *a", "PIE *bh > PBS *b"],
                        sources=["Krahe 1964", "Derksen 2008"],
                    )
                )

        return candidates
