"""Phoenician language module for toponymic analysis.

Phoenician (1200–150 BCE) was a Canaanite/Semitic language of the
Lebanese coast. Phoenician colonists founded cities across the
Mediterranean from Iberia (Gadir/Cádiz) to North Africa (Carthage).
Characterized by:
- Qart- (city) element: Carthage (Qart-ḥadašt = new city)
- Toponymic substrate across Mediterranean coastal settlements
- Mother language of Punic (Carthaginian dialect)
- Close relation to Hebrew but distinct phonology

Key references:
- Krahmalkov 2000 "A Phoenician-Punic Grammar"
- Lipiński 1994 "Studies in Aramaic Inscriptions and Onomastics"
- Benz 1972 "Personal Names in the Phoenician and Punic Inscriptions"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class PhoenicianModule(BaseLanguageModule):
    """Language module for Phoenician/Punic toponyms."""

    language_code = "phn"
    language_name = "Phoenician"
    family = "Afro-Asiatic"
    branch = "Semitic > Central Semitic > Northwest Semitic > Canaanite"
    period = "c. 1200–150 BCE (Punic continues to c. 600 CE)"
    script = "Phnx"

    prefixes = [
        "Qart-",  # city (Carthage = Qart-ḥadašt)
        "Bet-",  # house/temple
        "Beit-",  # house variant
        "Gub-",  # hill? (Gubal = Byblos)
        "Maq-",  # place (maqom)
        "Ras-",  # head, cape
        "Rosh-",  # head, cape (variant)
    ]

    suffixes = [
        "-ḥadašt",  # new (Carthage, Cartagena)
        "-im",  # masculine plural
        "-ot",  # feminine plural
        "-on",  # place suffix (Sidon = Ṣaydōn)
        "-it",  # gentilicium/feminine
        "-t",  # feminine marker
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "qart": "qart (city, town)",
        "bet": "bēt (house, temple)",
        "beit": "bēt (house, temple)",
        "gub": "gubl (hill? – root of Byblos/Gubal)",
        "maq": "maqōm (place, site)",
        "ras": "rōš (head, cape, promontory)",
        "rosh": "rōš (head, cape, promontory)",
        "hadašt": "ḥadašt (new)",
        "gadir": "gādir (wall, enclosure – Cádiz)",
        "malak": "milk/malak (king, divine king)",
        "baal": "ba'al (lord, master, deity)",
        "adon": "'adōn (lord)",
        "melqart": "milk-qart (king of the city – patron deity)",
        "tanit": "tannīt (serpent? – goddess)",
        "sayd": "ṣayd (fishing, hunting – Sidon)",
        "sur": "ṣūr (rock – Tyre)",
        "gubal": "gubl (Byblos, papyrus city)",
        "mot": "mōt (death, underworld deity)",
        "ham": "ḥam (hot, warm – Hammon)",
        "rusadir": "rōš-addir (mighty cape – Melilla)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Phoenician toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

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

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_prefix:
            prefix_part = form[: len(matched_prefix)]
            remainder = form[len(matched_prefix) :]
            if remainder.startswith(("-", " ")):
                remainder = remainder[1:]
                prefix_part = form[: len(matched_prefix) + 1]

            results.append(
                SegmentationResult(
                    component=prefix_part,
                    position=0,
                    morph_type="compound_head",
                    lemma=matched_prefix,
                    meaning=self.ELEMENT_MEANINGS.get(matched_prefix),
                    confidence=0.8,
                )
            )
            if matched_suffix and remainder.lower().endswith(matched_suffix):
                stem = remainder[: len(remainder) - len(matched_suffix)]
                if stem:
                    results.append(
                        SegmentationResult(
                            component=stem,
                            position=1,
                            morph_type="stem",
                            lemma=stem.lower(),
                            confidence=0.5,
                        )
                    )
                results.append(
                    SegmentationResult(
                        component=remainder[len(remainder) - len(matched_suffix) :],
                        position=len(results),
                        morph_type="suffix",
                        lemma=matched_suffix,
                        confidence=0.7,
                    )
                )
            else:
                results.append(
                    SegmentationResult(
                        component=remainder,
                        position=1,
                        morph_type="compound_modifier",
                        lemma=remainder.lower(),
                        confidence=0.5,
                    )
                )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="stem",
                    lemma=stem.lower(),
                    confidence=0.5,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=1,
                    morph_type="suffix",
                    lemma=matched_suffix,
                    confidence=0.7,
                )
            )
        else:
            # Check known full forms
            known = self.ELEMENT_MEANINGS.get(form_lower)
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    lemma=form.lower(),
                    meaning=known,
                    confidence=0.6 if known else 0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Phoenician in origin."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        phoenician_prefixes = ["qart", "cart", "bet", "beit", "gub", "ras", "rosh"]
        for prefix in phoenician_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix):
                evidence.append(f"Phoenician prefix {prefix}-")
                score += 0.4
                break

        phoenician_words = [
            "gadir",
            "hadašt",
            "melqart",
            "baal",
            "sayd",
            "sur",
            "gubal",
            "tanit",
            "rusadir",
        ]
        for word in phoenician_words:
            if word in form_lower:
                evidence.append(f"Phoenician element '{word}'")
                score += 0.4
                break

        if form_lower.endswith("on") and len(form_lower) > 4:
            evidence.append("Canaanite place suffix -ōn")
            score += 0.15

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="1200–150 BCE" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Phoenician components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            lemma_key = comp.lemma.lower().rstrip("-")
            meaning = self.ELEMENT_MEANINGS.get(lemma_key)
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=lemma_key,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                        cognates=[],
                        sound_changes=[],
                        sources=["Krahmalkov 2000", "Benz 1972"],
                    )
                )
        return candidates
