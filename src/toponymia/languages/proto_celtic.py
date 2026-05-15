"""Proto-Celtic language module.

Proto-Celtic is the reconstructed common ancestor of all Celtic languages
(2nd-1st millennium BCE). Key reconstructed toponymic elements include
*dūnon (fortress), *brigā (hill), *magos (field/plain), and *vindos
(white/fair). Provides the framework for understanding Celtic toponymy
across Europe from Iberia to Anatolia (Galatia).
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ProtoCelticModule(BaseLanguageModule):
    """Language module for Proto-Celtic toponyms."""

    language_code = "cel"
    language_name = "Proto-Celtic"
    family = "Indo-European"
    branch = "Celtic (reconstructed ancestor)"
    period = "2nd-1st millennium BCE (reconstructed)"
    script = "Latn"

    suffixes = [
        "-dūnon",  # fortress, hillfort
        "-brigā",  # hill, high place
        "-magos",  # field, plain
        "-duron",  # fort, door (cf. *dwor-)
        "-ākos",  # place of (suffix)
        "-rīgon",  # kingdom/territory
        "-bona",  # foundation, settlement
    ]

    prefixes = [
        "Vindo-",  # white, fair
        "Brig-",  # high
        "Dūno-",  # fortress
        "Sego-",  # victory, strength
        "Medio-",  # middle
        "Lugu-",  # bright (theonym: Lugus)
        "Nemeto-",  # sacred grove
    ]

    stems = [
        "vindos",  # white (> Wien/Vienne/Gwynedd)
        "brigā",  # hill (> Bregenz/Brig/Brigantes)
        "dūnon",  # fort (> Dundee/Verdun/Lugdunum)
        "magos",  # plain (> Rouen < Rotomagos)
        "nemeton",  # sacred grove (> Drunemeton/Nemetobriga)
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a possible Proto-Celtic toponym."""
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
                        confidence=0.6,
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
            # Check for known prefixes
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
                        confidence=0.6,
                    )
                )
                results.append(
                    SegmentationResult(
                        component=form[len(matched_prefix) :],
                        position=1,
                        morph_type="compound_head",
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
        """Classify whether a name form is likely Proto-Celtic."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        for suffix in [s.lstrip("-").lower() for s in self.suffixes]:
            if form_lower.endswith(suffix):
                evidence.append(f"PCelt. element *-{suffix}")
                score += 0.35
                break

        for prefix in [p.rstrip("-").lower() for p in self.prefixes]:
            if form_lower.startswith(prefix):
                evidence.append(f"PCelt. element *{prefix}-")
                score += 0.35
                break

        # Key Celtic elements in reflexes
        celtic_reflexes = ["dun", "brig", "mag", "vind", "nemet"]
        for reflex in celtic_reflexes:
            if reflex in form_lower:
                evidence.append(f"Celtic reflex *{reflex}-")
                score += 0.25
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="iron-age-celtic" if confidence > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "dūnon": ("*dūnon", "fortress, hillfort", ["OIr dún", "Welsh din", "Gaulish -dunum"]),
            "brigā": ("*brigā", "hill, high place", ["OIr brí", "Welsh bre", "Gaulish -briga"]),
            "magos": ("*magos", "field, plain", ["OIr mag", "Welsh ma", "Gaulish -magos"]),
            "duron": ("*duron", "fort, door", ["OIr dor", "Welsh dor"]),
            "vindo": ("*windos", "white, fair", ["OIr find", "Welsh gwyn"]),
            "sego": ("*segos", "victory, strength", ["OIr seg", "Welsh hy-"]),
            "nemeto": ("*nemeton", "sacred grove", ["OIr nemed", "Gaulish nemeton"]),
            "lugu": ("*lugus", "bright (deity Lugus)", ["OIr Lug", "Welsh Lleu"]),
            "bona": ("*bonā", "foundation, settlement", ["Gaulish -bona"]),
            "medio": ("*medios", "middle", ["OIr mid", "Welsh medd"]),
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
                        sound_changes=["PIE *p > PCelt. ∅", "PIE *kʷ > PCelt. *kʷ (> p/k)"],
                        sources=["Matasović 2009", "Delamarre 2003"],
                    )
                )

        return candidates
