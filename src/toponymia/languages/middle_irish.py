"""Middle Irish language module.

Middle Irish (900-1200 CE) is the transitional period between Old Irish
and Early Modern Irish. Important for Gaelic place-name development as
-baile (township) becomes the dominant settlement suffix, and many
modern Irish place-name forms crystallize during this period.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class MiddleIrishModule(BaseLanguageModule):
    """Language module for Middle Irish toponyms."""

    language_code = "mga"
    language_name = "Middle Irish"
    family = "Indo-European"
    branch = "Celtic > Goidelic"
    period = "900-1200 CE"
    script = "Latn"

    suffixes = [
        "-baile",  # township, homestead (becomes dominant)
        "-achadh",  # field
        "-cill",  # church (< Lat. cella)
        "-dún",  # fort
        "-lios",  # fort, enclosure
        "-ráth",  # ringfort
        "-inis",  # island
        "-port",  # port, bank
        "-druim",  # ridge
        "-cnoc",  # hill
        "-mag",  # plain
        "-gleann",  # valley
        "-cluain",  # meadow, pasture
        "-ros",  # wood, promontory
        "-ard",  # height
    ]

    prefixes = [
        "Cill-",  # church
        "Baile-",  # township
        "Dún-",  # fort
        "Ráth-",  # ringfort
        "Inis-",  # island
        "Druim-",  # ridge
        "Cnoc-",  # hill
        "Lios-",  # enclosure
        "Cluain-",  # meadow
        "Ard-",  # height
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Middle Irish toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Try prefix matching first (Gaelic names often prefix-determined)
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
                        morph_type="genitive",
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
        """Classify whether a name form is likely Middle Irish."""
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

        # Middle Irish orthographic features
        mi_features = ["dh", "gh", "mh", "bh", "ch"]
        for feat in mi_features:
            if feat in form_lower:
                evidence.append(f"lenition marker '{feat}'")
                score += 0.1
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="middle-irish" if confidence > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "baile": ("baile", "township, homestead", ["ScG baile", "Manx balley"]),
            "achadh": ("achadh", "field", ["ScG achadh"]),
            "cill": ("cill", "church", ["Lat. cella", "OIr. cell"]),
            "dún": ("dún", "fort", ["OIr. dún", "Welsh din"]),
            "ráth": ("ráth", "ringfort", ["OIr. ráth"]),
            "inis": ("inis", "island", ["OIr. inis", "Welsh ynys"]),
            "druim": ("druim", "ridge", ["OIr. druim", "Welsh trum"]),
            "cnoc": ("cnoc", "hill", ["ScG cnoc"]),
            "cluain": ("cluain", "meadow, pasture", ["OIr. cluain"]),
            "ros": ("ros", "wood, promontory", ["OIr. ros", "Welsh rhos"]),
            "ard": ("ard", "height, promontory", ["OIr. ard", "Welsh ardd"]),
            "lios": ("les/lios", "enclosure, ringfort", ["OIr. les"]),
            "gleann": ("glenn", "valley", ["OIr. glenn", "Welsh glyn"]),
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
                        sound_changes=["OIr. palatalization preserved"],
                        sources=["DIL", "Hogan Onomasticon"],
                    )
                )

        return candidates
