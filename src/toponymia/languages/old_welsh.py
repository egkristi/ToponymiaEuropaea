"""Old Welsh language module.

Old Welsh (8th-12th century CE) represents the earliest attestations
of the Welsh language. Orthography differs significantly from modern
Welsh. Important prefixes include Cair-/Caer- (fortress), Din- (hill
fort), and Llan- (church enclosure). Critical for dating Welsh toponyms.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldWelshModule(BaseLanguageModule):
    """Language module for Old Welsh toponyms."""

    language_code = "owl"
    language_name = "Old Welsh"
    family = "Indo-European"
    branch = "Celtic > Brythonic"
    period = "8th-12th century CE"
    script = "Latn"

    suffixes = [
        "-tref",  # homestead, settlement
        "-coed",  # wood, forest
        "-maes",  # field
        "-llyn",  # lake
        "-mor",  # sea
        "-bach",  # small (diminutive)
        "-mawr",  # great
        "-gwyn",  # white
        "-du",  # black
        "-newydd",  # new
        "-hen",  # old
    ]

    prefixes = [
        "Cair-",  # fortress (> Caer-)
        "Caer-",  # fortress
        "Din-",  # hill fort
        "Llan-",  # church enclosure
        "Aber-",  # river mouth, confluence
        "Pen-",  # head, top
        "Tre-",  # homestead (< tref)
        "Cum-",  # valley (> Cwm)
        "Pont-",  # bridge
        "Llin-",  # lake (> Llyn)
        "Bann-",  # peak (> Ban)
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old Welsh toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Brythonic names are typically prefix-determined
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
                    morph_type="compound_head",
                    lemma=matched_prefix,
                    confidence=0.7,
                )
            )
            if remainder:
                results.append(
                    SegmentationResult(
                        component=remainder,
                        position=1,
                        morph_type="compound_modifier",
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
        """Classify whether a name form is likely Old Welsh."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"prefix {prefix}-")
                score += 0.4
                break

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"suffix -{suffix}")
                score += 0.3
                break

        # Old Welsh orthographic features (differ from Modern Welsh)
        ow_features = ["cair", "din", "lann", "guur", "ir"]
        for feat in ow_features:
            if feat in form_lower:
                evidence.append(f"Old Welsh spelling '{feat}'")
                score += 0.15
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="old-welsh" if confidence > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "cair": ("cair", "fortress", ["MW caer", "Lat. castra(?)"]),
            "caer": ("cair/caer", "fortress", ["Brit. *kagro-", "Lat. castra(?)"]),
            "din": ("din", "hill fort", ["OIr. dún", "Gaul. dūnon"]),
            "llan": ("lann", "church enclosure", ["OIr. lann", "Lat. landa"]),
            "aber": ("aber", "river mouth", ["Pictish aber", "Gaul. *ad-bero-"]),
            "pen": ("penn", "head, summit", ["Gaul. penno-", "Corn. pen"]),
            "tre": ("tref", "homestead", ["Corn. tre", "Bret. trev"]),
            "cum": ("cum", "valley", ["MW cwm", "Lat. cumba(?)"]),
            "pont": ("pont", "bridge", ["Lat. pons/pontem"]),
            "tref": ("tref", "homestead, settlement", ["Brit. *treba"]),
            "coed": ("coit/coed", "wood, forest", ["Brit. *kaito-"]),
            "maes": ("mais/maes", "field", ["Brit. *mageso-"]),
            "llyn": ("linn/llyn", "lake, pool", ["OIr. linn"]),
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
                        sound_changes=["Brit. *k > OW c (not yet ch)"],
                        sources=["GPC", "Jackson LHEB"],
                    )
                )

        return candidates
