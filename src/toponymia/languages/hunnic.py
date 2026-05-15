"""Hunnic language module.

Hunnic is the poorly attested language of the Huns (4th-5th century CE,
Attila's empire). Its genetic affiliation is debated—proposed connections
include Turkic, Yeniseian, Uralic, or a language isolate. Only minimal
attestation survives (a few words and personal/tribal names). Place-name
traces in Pannonia remain highly speculative (e.g., Buda < Bleda?).
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class HunnicModule(BaseLanguageModule):
    """Language module for Hunnic toponyms."""

    language_code = "xhc"
    language_name = "Hunnic"
    family = "Uncertain (Turkic? Yeniseian? isolate?)"
    branch = "Unknown"
    period = "4th-5th century CE"
    script = "Latn"

    # Extremely limited corpus—mostly from personal/tribal names
    suffixes = [
        "-var",  # possible fortification (cf. Turkic)
        "-don",  # river (Iranian substrate in steppe?)
        "-dag",  # mountain (Turkic?)
    ]

    prefixes = [
        "At-",  # cf. Attila (Gothic *atta 'father'?)
        "Bled-",  # cf. Bleda (< Hunnic or Gothic?)
        "Mun-",  # cf. Mundzuk (Attila's father)
        "Bud-",  # Buda (debated)
    ]

    stems = [
        "attila",  # Attila (debated: Gothic *atta? Turkic *ata?)
        "bleda",  # Bleda (Attila's brother)
        "buda",  # Buda (< Bleda? debated)
        "hun",  # ethnonym
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Hunnic toponym."""
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
                        confidence=0.3,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.3,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    confidence=0.2,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is possibly Hunnic."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"possible steppe suffix -{suffix}")
                score += 0.2
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Hunnic name element {prefix}-")
                score += 0.2
                break

        # Hunnic ethnonym
        if "hun" in form_lower or "khun" in form_lower:
            evidence.append("Hunnic ethnonym")
            score += 0.25

        # Known Hunnic personal names
        hunnic_names = ["attila", "bleda", "mundzuk", "ruga", "octar"]
        for name in hunnic_names:
            if name in form_lower:
                evidence.append(f"Hunnic personal name '{name}'")
                score += 0.2
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="migration-period" if confidence > 0.2 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "var": ("var", "fortification(?)", ["Turkic *bar 'fortification'?"]),
            "don": ("dōn", "river (Iranian substrate)", ["Ossetic don 'water'"]),
            "bud": ("buda", "< Bleda? (debated)", ["Gothic *Blēda?"]),
            "at": ("atta", "father (Gothic?) or great (Turkic?)", ["Gothic atta", "Turkic ata"]),
            "hun": ("hun", "people (ethnonym)", ["Chinese Xiōngnú (debated)"]),
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
                        confidence=comp.confidence * 0.7,  # Low confidence due to poor attestation
                        cognates=cognates,
                        sound_changes=["Hunnic phonology unknown"],
                        sources=["Priscus of Panium", "Maenchen-Helfen 1973"],
                    )
                )

        return candidates
