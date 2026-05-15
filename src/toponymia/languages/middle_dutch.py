"""Middle Dutch language module.

Middle Dutch (1150-1500 CE) was spoken in the Low Countries. Important
for dating place-names in Belgium, the Netherlands, and adjacent areas.
Characteristic toponymic elements include -dam, -dijk, -sluys, reflecting
the water-management landscape. Amsterdam, Rotterdam, Breda are examples.
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class MiddleDutchModule(BaseLanguageModule):
    """Language module for Middle Dutch toponyms."""

    language_code = "dum"
    language_name = "Middle Dutch"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Low Franconian"
    period = "1150-1500 CE"
    script = "Latn"

    suffixes = [
        "-dam",  # dam
        "-dijk",  # dike
        "-sluys",  # sluice, lock
        "-vliet",  # stream, canal
        "-broek",  # marsh
        "-donk",  # sandy rise in marsh
        "-drech",  # portage, crossing
        "-hout",  # wood, forest
        "-kerk",  # church
        "-lede",  # watercourse
        "-wijk",  # settlement, district
        "-brug",  # bridge
        "-loo",  # forest, clearing
        "-veld",  # field
        "-zele",  # hall, dwelling
        "-hem",  # home
        "-rode",  # clearing
    ]

    prefixes = [
        "Nieu-",  # new
        "Oud-",  # old
        "Groot-",  # great
        "Klein-",  # small
        "Oost-",  # east
        "West-",  # west
        "Noord-",  # north
        "Zuid-",  # south
        "Schoon-",  # beautiful, clean
    ]

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Middle Dutch toponym into morphological components."""
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
        """Classify whether a name form is likely Middle Dutch."""
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

        # Dutch-specific water management terms
        water_terms = ["dam", "dijk", "sluys", "vliet", "polder"]
        for term in water_terms:
            if term in form_lower:
                evidence.append(f"Low Countries water term '{term}'")
                score += 0.2
                break

        confidence = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=confidence,
            evidence=evidence,
            period_estimate="late-medieval" if confidence > 0.4 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymological candidates for segmented components."""
        meanings: dict[str, tuple[str, str, list[str]]] = {
            "dam": ("dam", "dam, barrier", ["OE damm", "ON dammr"]),
            "dijk": ("dīc", "dike, embankment", ["OE dīc", "OHG tīh"]),
            "sluys": ("slūse", "sluice, lock", ["OF escluse", "Lat. exclusa"]),
            "vliet": ("vliet", "stream, canal", ["OE flēot"]),
            "broek": ("broec", "marsh, wetland", ["OE brōc", "OHG bruoh"]),
            "donk": ("donk", "sandy rise in marsh", []),
            "hout": ("hout", "wood, forest", ["OE holt", "ON holt"]),
            "kerk": ("kerke", "church", ["OE cirice", "Gk kyriakon"]),
            "loo": ("lō", "forest clearing", ["OE lēah", "OHG lōh"]),
            "rode": ("rode", "clearing (assart)", ["OHG rod", "OE *roð"]),
            "zele": ("sele", "hall, dwelling", ["OE sele", "ON salr"]),
            "hem": ("heem", "home, settlement", ["OE hām"]),
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
                        sound_changes=["WGmc *ai > MDu ei/ī", "WGmc *au > MDu ou"],
                        sources=["MNW", "Gysseling 1960"],
                    )
                )

        return candidates
