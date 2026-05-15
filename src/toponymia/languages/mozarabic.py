"""Mozarabic language module.

Mozarabic was a group of Romance dialects spoken in Al-Andalus
(711-13th century) by Christians under Muslim rule. Known from kharjas
(refrains in Arabic/Hebrew muwashshahat) and place-name substrate in
southern Spain and Portugal. Suffixes are often preserved in Arabicized
phonological forms.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class MozarabicModule(BaseLanguageModule):
    """Language module for Mozarabic toponyms."""

    language_code = "mxi"
    language_name = "Mozarabic"
    family = "Indo-European"
    branch = "Italic > Romance > Ibero-Romance"
    period = "711-13th century CE"
    script = "Latn"

    suffixes = [
        "-uel",  # < Lat. -olum (diminutive)
        "-iel",  # < Lat. -ellum
        "-ench",  # < Lat. -inicum
        "-ix",  # < Lat. -ice
        "-uch",  # < Lat. -uculum
        "-et",  # < Lat. -ētum (collective)
        "-ón",  # augmentative
        "-ín",  # diminutive
        "-alba",  # white (< Lat. alba)
    ]

    prefixes = [
        "Guad-",  # < Arabic wādī (river) + Romance
        "Medina-",  # < Arabic madīna (city)
        "Alcalá-",  # < Arabic al-qalʿa (fortress)
        "Almod-",  # < Arabic al- + Romance
        "Ben-",  # < Arabic ibn- in hybrid names
        "Mont-",  # mountain (Romance preserved)
        "Font-",  # spring (< Lat. fons)
        "Val-",  # valley (< Lat. vallis)
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Mozarabic toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Try prefix first (Arabic-Romance hybrids common)
        sorted_prefixes = sorted([p.rstrip("-") for p in self.prefixes], key=len, reverse=True)

        matched_prefix = None
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix.lower()):
                matched_prefix = prefix
                break

        if matched_prefix:
            prefix_part = form[: len(matched_prefix)]
            remainder = form[len(matched_prefix) :]

            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="prefix",
                    lemma=matched_prefix,
                    confidence=0.6,
                )
            )
            if remainder:
                results.append(
                    SegmentationResult(
                        component=remainder,
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
        """Classify whether a name form is likely Mozarabic."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Arabic-Romance hybrid prefix {prefix}-")
                score += 0.4
                break

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"suffix -{suffix}")
                score += 0.3
                break

        # Mozarabic phonological retentions
        moz_features = ["uel", "ench", "uch", "iel"]
        for feat in moz_features:
            if feat in form_lower:
                evidence.append(f"Mozarabic diphthong/cluster '{feat}'")
                score += 0.15
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="al-andalus" if confidence > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "guad": ("wādī", "river (Arabic + Romance)", ["Ar. wādī"]),
            "medina": ("madīna", "city (Arabic)", ["Ar. madīna"]),
            "alcalá": ("al-qalʿa", "fortress (Arabic)", ["Ar. al-qalʿa"]),
            "mont": ("monte", "mountain", ["Lat. mons", "Sp. monte"]),
            "font": ("fonte", "spring", ["Lat. fontem", "Sp. fuente"]),
            "val": ("val", "valley", ["Lat. vallis", "Sp. valle"]),
            "uel": ("-olum", "diminutive", ["Lat. -olum"]),
            "iel": ("-ellum", "diminutive", ["Lat. -ellum"]),
            "ench": ("-inicum", "pertaining to", ["Lat. -inicum"]),
            "alba": ("alba", "white, dawn", ["Lat. alba"]),
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
                            "Lat. -ol- > Moz. -uel-",
                            "Lat. cl/fl/pl preserved (no palatalization)",
                        ],
                        sources=["Galmés de Fuentes 1983", "Corriente 1997"],
                    )
                )

        return candidates
