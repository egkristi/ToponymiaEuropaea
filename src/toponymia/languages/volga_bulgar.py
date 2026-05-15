"""Volga Bulgar language module for toponymic analysis.

Volga Bulgaria (c. 660–1236 CE) was a major trade state on the
middle Volga/Kama confluence — and a KEY Viking trade destination:

- Ibn Fadlan (921 CE) describes Varangian (Rus) traders at Bulgar
- Norse sagas reference "Bjarmaland" trade routes via Volga
- Silver dirham trade: Bulgar was the main exchange point for Norse
  traders bringing furs/slaves and buying Islamic silver
- Volga trade route: Ladoga → Novgorod → Volga → Bulgar → Caspian

The Volga Bulgar language was Oghur Turkic (lir-Turkic), ancestral
to modern Chuvash. Distinct from Common Turkic in key sound changes:
- *-z- > -r- (Oghur/lir vs Oghuz/shaz)
- *-sh- > -l-
- Preserved archaic Turkic features

Toponymic traces:
- Bulgar/Bolgar (the capital city itself)
- Bilar (second capital)
- Suvar (major city; cf. Chuvash Çăvaş?)
- Many Volga/Kama region names
- Influence on Russian names in the region

Key references:
- Róna-Tas 1999 "Hungarians and Europe in the Early Middle Ages"
- Zimonyi 1990 "The Origins of the Volga Bulgars"
- Ibn Fadlan 921 CE (Risāla — account of Volga journey)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class VolgaBulgarModule(BaseLanguageModule):
    """Language module for Volga Bulgar (Oghur Turkic) toponyms."""

    language_code = "xbo"  # ISO 639-3 for Bulgar (extinct)
    language_name = "Volga Bulgar"
    family = "Turkic"
    branch = "Oghur (Lir-Turkic; ancestor of Chuvash)"
    period = "660–1236 CE (Volga Bulgaria; continues as Chuvash)"
    script = "Runic (Old Turkic) / Arab (after Islamization 922)"

    prefixes = [
        "Bul-",  # Bulgar (ethnonym; possibly 'mixed')
        "Su-",  # water (Suvar city)
        "Bil-",  # know? (Bilar capital; etymology debated)
        "Kara-",  # black (shared Turkic)
        "Aq-",  # white (Oghur form)
        "Çal-",  # grey (Chuvash/Bulgar form)
    ]

    suffixes = [
        "-gar",  # possibly 'people/tribe' (in Bulgar)
        "-ar",  # people/tribe suffix (Suvar, Bulgar)
        "-var",  # city/place (Suvar; < Iranian?)
        "-tal",  # field, steppe (Chuvash tul)
        "-su",  # water (shared Turkic)
        "-çik",  # diminutive (Bulgar/Chuvash)
        "-la",  # place marker (Chuvash locative)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "bulgar": "ethnonym (possibly 'mixed people' or 'rebel')",
        "bilar": "second Bulgar capital (etymology uncertain)",
        "suvar": "major Bulgar city (possibly 'water-people')",
        "su": "water (shared Turkic)",
        "kara": "black (shared Turkic color term)",
        "aq": "white (Oghur form of ak)",
        "çal": "grey, grey-haired (Bulgar/Chuvash)",
        "gar": "people, tribe (in ethnonyms: Bulgar, Magyar?)",
        "itil": "great river (Volga; shared with Khazars)",
        "çulman": "river (Bulgar name for Kama?; > Chulman)",
        "tavar": "goods, merchandise (trade term; > Russian tovar)",
        "yul": "road, path (Chuvash/Bulgar)",
        "kil": "come, house (Chuvash form)",
        "shir": "land, country (Bulgar; cf. Bashkir -shire?)",
    }

    # Known Volga Bulgar settlements and geographic names
    FULL_ELEMENTS: dict[str, str] = {
        "bolgar": "Bulgar capital on the Volga (UNESCO site)",
        "bilar": "Bulgar second capital (largest medieval Volga city)",
        "suvar": "Major Bulgar trade city",
        "bulgar": "Variant spelling of capital/ethnonym",
        "çulman": "Bulgar name for Kama river",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a potential Volga Bulgar toponym."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Check known Bulgar city/place names
        for element, _meaning in self.FULL_ELEMENTS.items():
            if element in form_lower:
                results.append(
                    SegmentationResult(
                        component=element,
                        position=0,
                        morph_type="stem",
                        confidence=0.75,
                    )
                )
                return results

        # Prefix/suffix analysis
        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes],
            key=len,
            reverse=True,
        )
        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )

        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                remainder = form[len(prefix) :]
                self.ELEMENT_MEANINGS.get(prefix, "")
                results.extend(
                    [
                        SegmentationResult(
                            component=prefix, position=0, morph_type="prefix", confidence=0.45
                        ),
                        SegmentationResult(
                            component=remainder, position=1, morph_type="stem", confidence=0.45
                        ),
                    ]
                )
                break

        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 2:
                stem = form[: len(form) - len(suffix)]
                self.ELEMENT_MEANINGS.get(suffix, "")
                results.extend(
                    [
                        SegmentationResult(
                            component=stem,
                            position=0,
                            morph_type="compound_modifier",
                            confidence=0.45,
                        ),
                        SegmentationResult(
                            component=suffix,
                            position=1,
                            morph_type="compound_head",
                            confidence=0.45,
                        ),
                    ]
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Volga Bulgar."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Known Bulgar settlements
        known_names = ["bolgar", "bulgar", "bilar", "suvar"]
        for name in known_names:
            if name in form_lower:
                evidence.append(f"Known Volga Bulgar toponym '{name}'")
                score += 0.8
                break

        # Oghur Turkic phonological markers (r-language)
        # Where Common Turkic has -z-, Bulgar/Chuvash has -r-
        if "çal" in form_lower or "çul" in form_lower:
            evidence.append("Oghur/Chuvash-type ç- phonology")
            score += 0.3

        # Trade route connection terms
        trade_terms = ["tavar", "yul", "itil"]
        for term in trade_terms:
            if term in form_lower:
                evidence.append(f"Volga Bulgar trade/route term '{term}'")
                score += 0.35
                break

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Suggest Volga Bulgar etymologies for a toponym."""
        candidates: list[EtymologyCandidate] = []
        form = components[0].component if components else ""
        form_lower = form.lower()

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                candidates.append(
                    EtymologyCandidate(
                        lemma=f"*{element}",
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.4,
                    )
                )

        return candidates
