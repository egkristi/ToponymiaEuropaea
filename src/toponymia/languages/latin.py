"""Latin language module for toponymic analysis.

Latin toponymy covers Roman-era place names across Europe:
- Military/administrative: castra, castrum, colonia, vicus, forum
- Geographic features: aquae, mons, vallis, silva, flumen
- Personal names with suffixes: -anum, -acum (> French -ac, -y)
- Survival in modern forms: -chester, -caster (< castra), -street (< strata)

The Latin stratum is critical for understanding pre-Germanic layers in
Northern Europe and the foundation of Romance toponymy.

Key references:
- Rivet & Smith 1979 "Place-Names of Roman Britain"
- Nicolaisen 2001 "Scottish Place-Names" (ch. on Latin names)
- Ekwall 1960 "English River-Names" (Latin elements)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class LatinModule(BaseLanguageModule):
    """Language module for Latin (Roman-era) toponyms."""

    language_code = "la"  # ISO 639-1 for Latin
    language_name = "Latin"
    family = "Indo-European"
    branch = "Italic > Latin"
    period = "100 BCE–500 CE (primary); survivals to present"
    script = "Latn"

    # Latin toponymic prefixes and first elements
    prefixes = [
        "Aquae-",  # waters, spa
        "Ad-",  # at, near
        "Sub-",  # under, below
        "Trans-",  # across
        "Inter-",  # between
        "Super-",  # above, over
        "Magna-",  # great
        "Nova-",  # new
        "Vetus-",  # old
        "Alta-",  # high
        "Longa-",  # long
    ]

    # Latin toponymic suffixes and derivative forms
    suffixes = [
        "-castra",  # military camp
        "-castrum",  # fort
        "-chester",  # English reflex of castra
        "-caster",  # English reflex of castra
        "-cester",  # English reflex of castra
        "-dunum",  # fort (Celtic loan in Latin)
        "-burgum",  # fortified place
        "-villa",  # estate, farm
        "-vicus",  # settlement
        "-wick",  # English reflex of vicus
        "-acum",  # estate of (Celtic-Latin hybrid)
        "-anum",  # estate of (Latin)
        "-ensis",  # belonging to
        "-briga",  # hill-fort (Celtic in Latin)
        "-magus",  # market (Celtic in Latin)
        "-ritum",  # ford (Celtic in Latin)
        "-strata",  # paved road
        "-street",  # English reflex of strata
        "-portus",  # harbor
        "-pons",  # bridge
        "-fons",  # spring
        "-mons",  # mountain
        "-silva",  # forest
        "-campus",  # field
        "-vallis",  # valley
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Latin/Latin-derived toponym."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Try suffix matching first (most diagnostic for Latin)
        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix):
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
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.7,
                )
            )
        else:
            # Try prefix matching
            sorted_prefixes = sorted(
                [p.rstrip("-").lower() for p in self.prefixes],
                key=len,
                reverse=True,
            )
            matched_prefix = None
            for prefix in sorted_prefixes:
                if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
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
        """Classify whether a name form is likely Latin-derived."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Check suffixes (strongest signal for Latin survival)
        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"Latin suffix -{suffix}")
                score += 0.5
                break

        # Check prefixes
        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"Latin prefix {prefix}-")
                score += 0.4
                break

        # Latin phonological markers
        latin_endings = ["-um", "-us", "-a", "-ae", "-is", "-ium"]
        for ending in latin_endings:
            if form_lower.endswith(ending):
                evidence.append(f"Latin nominal ending '{ending}'")
                score += 0.2
                break

        # Known Latin elements within the name
        latin_internals = [
            "pont",
            "port",
            "font",
            "mont",
            "cast",
            "strat",
            "colon",
        ]
        for elem in latin_internals:
            if elem in form_lower:
                evidence.append(f"Latin element '{elem}'")
                score += 0.15
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="roman" if confidence > 0.5 else None,
        )

    ELEMENT_MEANINGS: dict[str, tuple[str, str, list[str]]] = {
        # --- Military/Administrative ---
        "castra": ("castra", "military camp, fort", ["English -chester/-caster"]),
        "castrum": ("castrum", "fort, fortified place", ["English -chester"]),
        "chester": ("castra", "fort (English reflex)", []),
        "caster": ("castra", "fort (English reflex)", []),
        "cester": ("castra", "fort (English reflex)", []),
        "colonia": ("colonia", "colony, settlement", ["English Lincoln < Lindum Colonia"]),
        "vicus": ("vicus", "village, small settlement", ["English -wick/-wich"]),
        "wick": ("vicus", "village (English reflex)", []),
        "villa": ("villa", "estate, farm", ["French -ville"]),
        "burgum": ("burgum", "fortified place", ["English -bury/-burgh"]),
        "forum": ("forum", "market-place", []),
        # --- Roads/Infrastructure ---
        "strata": ("strata", "paved road", ["English street"]),
        "street": ("strata", "road (English reflex)", []),
        "pons": ("pons", "bridge", ["French pont", "Welsh pont"]),
        "portus": ("portus", "harbor, port", ["English port"]),
        # --- Geographic ---
        "aquae": ("aquae", "waters, hot springs", ["French Aix, Ax-"]),
        "mons": ("mons", "mountain, hill", ["French mont"]),
        "silva": ("silva", "forest, wood", []),
        "campus": ("campus", "field, plain", ["French champ"]),
        "vallis": ("vallis", "valley", ["French val-"]),
        "fons": ("fons", "spring, fountain", ["French fontaine"]),
        "flumen": ("flumen", "river", []),
        "insula": ("insula", "island", ["French île"]),
        # --- Celtic-Latin hybrids ---
        "dunum": ("*dūnon", "fort (Celtic element in Latin)", ["English -down"]),
        "briga": ("*brig-", "hill-fort (Celtic in Latin)", []),
        "magus": ("*magos", "market, field (Celtic in Latin)", []),
        "ritum": ("*ritu-", "ford (Celtic in Latin)", []),
        "acum": ("-acum", "estate of (Gallo-Roman suffix)", ["French -ac, -y"]),
        "anum": ("-anum", "estate of (Latin possessive)", ["Italian -ano"]),
        # --- Descriptive ---
        "magna": ("magna", "great", []),
        "nova": ("nova", "new", []),
        "vetus": ("vetus", "old", []),
        "alta": ("alta", "high", []),
        "longa": ("longa", "long", []),
        "ad": ("ad", "at, near", []),
    }

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Latin components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            key = (comp.lemma or comp.component).lower()
            if key in self.ELEMENT_MEANINGS:
                proto_form, meaning, cognates = self.ELEMENT_MEANINGS[key]
                candidates.append(
                    EtymologyCandidate(
                        lemma=proto_form,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=cognates,
                    )
                )
        return candidates
