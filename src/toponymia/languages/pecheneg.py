"""Pecheneg language module.

Pecheneg was an Oghuz Turkic language spoken by the semi-nomadic
Pecheneg people in the Pontic steppe region (8th-12th century CE).
They left place-name traces across Romania, Hungary, and Bulgaria:
Beșenova, Besenyő, etc. An important Balkan Turkic layer between
the earlier Avars and later Cumans.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class PechenegModule(BaseLanguageModule):
    """Language module for Pecheneg toponyms."""

    language_code = "xpc"
    language_name = "Pecheneg"
    family = "Turkic"
    branch = "Oghuz"
    period = "8th-12th century CE"
    script = "Latn"

    suffixes = [
        "-ova",  # Slavicized possessive
        "-ő",  # Magyarized (Besenyő)
        "-tepe",  # hill (Turkic)
        "-su",  # water (Turkic)
        "-köl",  # lake (Turkic)
        "-balık",  # city/settlement (Turkic)
    ]

    prefixes = [
        "Beșen-",  # ethnic: Pecheneg (Romanian)
        "Besen-",  # ethnic: Pecheneg (Hungarian)
        "Pechen-",  # ethnic: Pecheneg (Slavic)
        "Kara-",  # black (Turkic)
        "Ak-",  # white (Turkic)
    ]

    stems = [
        "besenov",  # Beșenova (Romania)
        "besenyő",  # Besenyő (Hungary)
        "pecheneg",  # ethnonym (Slavic form)
        "patzinakia",  # Byzantine Greek form
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Pecheneg toponym."""
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
        """Classify whether a name form is likely Pecheneg."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Turkic suffix -{suffix}")
                score += 0.3
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"prefix {prefix}-")
                score += 0.3
                break

        # Pecheneg ethnonymic markers
        pecheneg_forms = ["beșen", "besen", "pechen", "patzin", "bissenus"]
        for pf in pecheneg_forms:
            if pf in form_lower:
                evidence.append(f"Pecheneg ethnonym variant '{pf}'")
                score += 0.35
                break

        # Turkic color+landscape compounds
        turkic_elements = ["kara", "ak", "tepe", "su", "köl"]
        for elem in turkic_elements:
            if elem in form_lower:
                evidence.append(f"Turkic element '{elem}'")
                score += 0.15
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="early-medieval-steppe" if confidence > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "tepe": ("tepe", "hill, mound", ["Turkish tepe", "Azerbaijani təpə"]),
            "su": ("su", "water, river", ["Turkish su", "Kipchak su"]),
            "köl": ("köl", "lake", ["Turkish göl", "Kipchak köl"]),
            "kara": ("kara", "black", ["Turkish kara", "Common Turkic *kara"]),
            "ak": ("ak", "white", ["Turkish ak", "Common Turkic *āk"]),
            "besen": ("bečenek", "Pecheneg (ethnonym)", ["Byzantine Πατζινάκοι"]),
            "balık": ("balık", "city, settlement", ["Old Turkic balïq"]),
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
                        sound_changes=["Oghuz *d > Pecheneg δ/y"],
                        sources=["Constantine VII DAI", "Németh 1930"],
                    )
                )

        return candidates
