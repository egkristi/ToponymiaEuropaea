"""Dalmatian language module.

Dalmatian was a Romance language spoken along the Adriatic coast.
It became extinct in 1898 when the last speaker, Tuone Udaina, was
killed in an explosion on Krk/Veglia island. The Vegliote dialect
is best attested. Important as Adriatic substrate in coastal toponymy.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class DalmatianModule(BaseLanguageModule):
    """Language module for Dalmatian toponyms."""

    language_code = "dlm"
    language_name = "Dalmatian"
    family = "Indo-European"
    branch = "Italic > Romance > Eastern Romance"
    period = "ca. 7th century - 1898 CE"
    script = "Latn"

    suffixes = [
        "-uota",  # < Lat. -ūta
        "-aica",  # diminutive
        "-essa",  # < Lat. -itia
        "-ica",  # Slavicized diminutive
        "-ostra",  # < Lat. -astra
        "-grad",  # Slavic overlay (city)
        "-al",  # place suffix
    ]

    prefixes = [
        "Veg-",  # Veglia (Krk)
        "Rag-",  # Ragusa (Dubrovnik)
        "Jadr-",  # Zadar (< Lat. Iadera)
        "Spal-",  # Split (< Lat. Spalatum)
        "Cat-",  # Cattaro (Kotor)
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Dalmatian toponym into morphological components."""
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
                        morph_type="stem",
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
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
        """Classify whether a name form is likely Dalmatian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"historical Dalmatian city prefix {prefix}-")
                score += 0.3
                break

        # Dalmatian phonological features (Vegliote)
        dlm_features = ["uota", "laup", "kauv", "tuot"]
        for feat in dlm_features:
            if feat in form_lower:
                evidence.append(f"Vegliote feature '{feat}'")
                score += 0.2
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="medieval-to-modern" if confidence > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "uota": ("-ūta", "place suffix", ["Lat. -ūta"]),
            "veg": ("Vegla", "Veglia/Krk island", ["Lat. Vecla/Veglia"]),
            "rag": ("Ragusa", "Dubrovnik", ["Lat. Ragusium"]),
            "jadr": ("Iadera", "Zadar", ["Lat. Iadera", "Liburnian *?"]),
            "spal": ("Spalatum", "Split", ["Lat. Spalatum", "Gk. Aspalathos"]),
            "al": ("-al", "pertaining to (place)", ["Lat. -ālis"]),
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
                        sound_changes=[
                            "Lat. ū > Dlm. u/o",
                            "Lat. ct > Dlm. it",
                        ],
                        sources=["Bartoli 1906", "Muljačić 2000"],
                    )
                )

        return candidates
