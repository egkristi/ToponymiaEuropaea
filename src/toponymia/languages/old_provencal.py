"""Old Provençal / Old Occitan language module.

Old Provençal (Old Occitan) was the medieval literary language of
southern France (10th-14th century), famous as the language of the
troubadours. Important for dating southern French place-names with
suffixes like -ac, -argue, -ens vs modern Occitan forms.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldProvencalModule(BaseLanguageModule):
    """Language module for Old Provençal/Occitan toponyms."""

    language_code = "pro"
    language_name = "Old Provençal"
    family = "Indo-European"
    branch = "Italic > Romance > Gallo-Romance"
    period = "10th-14th century CE"
    script = "Latn"

    suffixes = [
        "-ac",  # < Lat. -ācum (estate of)
        "-argue",  # < pre-Latin (field/plain)
        "-ens",  # < Lat. -ēnsis (belonging to)
        "-an",  # < Lat. -ānum
        "-as",  # < Lat. -ās (plural)
        "-iera",  # < Lat. -āria (place of)
        "-ol",  # diminutive
        "-et",  # < Lat. -ētum (grove of)
        "-ós",  # < Lat. -ōsum (abounding in)
        "-enc",  # < Lat. -inicum
        "-anha",  # < Lat. -ānea
    ]

    prefixes = [
        "Mont-",  # mountain
        "Font-",  # spring
        "Roca-",  # rock
        "Peira-",  # stone
        "Bel-",  # beautiful
        "Castel-",  # castle
        "Vila-",  # town
        "Prat-",  # meadow
        "Val-",  # valley
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old Provençal toponym into morphological components."""
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
                        confidence=0.6,
                    )
                )
            results.append(
                SegmentationResult(
                    component=suffix_part,
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
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a name form is likely Old Provençal."""
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

        # Old Provençal orthographic features
        op_features = ["lh", "nh", "tz", "ch"]
        for feat in op_features:
            if feat in form_lower:
                evidence.append(f"Occitan digraph '{feat}'")
                score += 0.1
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="medieval-occitan" if confidence > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "ac": ("-ācum", "estate of (Gallo-Roman)", ["Lat. -ācum", "Fr. -ay"]),
            "argue": ("argue", "field, plain (pre-Latin)", []),
            "ens": ("-ēnsis", "belonging to", ["Lat. -ēnsis"]),
            "an": ("-ānum", "pertaining to", ["Lat. -ānum", "Fr. -ain"]),
            "iera": ("-āria", "place of", ["Lat. -āria", "Fr. -ière"]),
            "et": ("-ētum", "grove, collective", ["Lat. -ētum", "Fr. -aie"]),
            "mont": ("mont", "mountain", ["Lat. montem"]),
            "font": ("font", "spring", ["Lat. fontem"]),
            "roca": ("ròca", "rock, fortress", ["pre-Roman *rokka"]),
            "peira": ("pèira", "stone", ["Lat. petra"]),
            "castel": ("castèl", "castle", ["Lat. castellum"]),
            "vila": ("vila", "town, estate", ["Lat. villa"]),
            "val": ("val", "valley", ["Lat. vallem"]),
            "prat": ("prat", "meadow", ["Lat. pratum"]),
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
                            "Lat. -ācum > OProv. -ac",
                            "Lat. ca- > OProv. cha- (N.Occ.)",
                        ],
                        sources=["Ronjat 1930", "Nègre 1990"],
                    )
                )

        return candidates
