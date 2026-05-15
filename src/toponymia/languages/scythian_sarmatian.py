"""Scythian-Sarmatian language module for toponymic analysis.

The Scythian and Sarmatian languages were Eastern Iranian languages spoken
by nomadic peoples who dominated the Pontic-Caspian steppe from ~700 BCE
to ~400 CE. Their toponymic legacy is CRITICAL for European name analysis:

Major European river names of Iranian (Scythian/Sarmatian) origin:
- Don (Tanais) < Iranian *dānu "river, water" (cf. Avestan dānu-)
- Dnieper (Danapris) < *Dānu-apara "far river"
- Dniester (Danastris) < *Dānu-nazdya "near river"
- Danube (Danuvius) < *Dānu "river" (or Celtic, debated)
- Kuban < *Kubā "winding" (Sarmatian?)

Also contributed to:
- Ossetic (modern survivor of Sarmatian > Alan)
- Alan names in Western Europe (Catalonia, Brittany settlements)
- Substrate in Slavic river names

Connection to Norse studies:
- Vikings on the Dnieper/Don routes encountered these ancient names
- The name "Rus" itself may involve Iranian elements (debated)
- Sarmatian cultural and naming influence on early Slavs

Key references:
- Abaev 1979 "Historical-Etymological Dictionary of Ossetic"
- Harmatta 1970 "Studies in the History and Language of the Sarmatians"
- Zgusta 1955 "Die Personennamen griechischer Städte der nördlichen
  Schwarzmeerküste"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class ScythianSarmatianModule(BaseLanguageModule):
    """Language module for Scythian-Sarmatian (Eastern Iranian) toponyms."""

    language_code = "xsc"  # ISO 639-3 for Scythian
    language_name = "Scythian-Sarmatian"
    family = "Indo-European"
    branch = "Iranian > Eastern Iranian (Scytho-Sarmatian)"
    period = "700 BCE – 400 CE (relic names persist to present)"
    script = "None (unwritten; names preserved via Greek/Latin)"

    prefixes = [
        "Dan-",  # river, water (Danube, Dnieper, Don)
        "Var-",  # wide, broad (Vardar? debated)
        "As-",  # Alan/Os tribal name (Azov < As?)
        "Ard-",  # holy, divine (Ardahan?)
        "Khvar-",  # sun (cf. Avestan hvar-)
        "Paru-",  # broad, wide
        "Nar-",  # man, hero (cf. Ossetic nart)
    ]

    suffixes = [
        "-don",  # water, river (Don, Terek-don > London? controversial)
        "-dan",  # variant of -don (Gordan, Jordan? unrelated)
        "-apa",  # water (Sarmatian; cf. Olbia area names)
        "-ard",  # plains, place (Sarmatian)
        "-var",  # enclosure, protected area
        "-gard",  # city, enclosure (shared with Germanic/Iranian)
        "-ast",  # place suffix (Sarmatian; cf. Ossetic)
        "-ān",  # place/land (Iranian; cf. Persian -istan)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "danu": "river, water (reconstructed *dānu; > Don, Dnieper)",
        "don": "river, water (< *dānu; cf. Ossetic don 'water')",
        "dnieper": "far river (< *Dānu-apara 'river-far')",
        "dniester": "near river (< *Dānu-nazdya 'river-near')",
        "danube": "river (< *Dānu; also possibly Celtic)",
        "ap": "water (cf. Avestan āp-; > Sarmatian hydronyms)",
        "as": "Alan, Ossete (tribal autonym; > Azov, Ossetia)",
        "ard": "holy, sacred (cf. Avestan aṣ̌a-)",
        "nart": "hero, man (Ossetic/Scythian epic cycle)",
        "var": "broad, wide; also enclosure",
        "gard": "city, enclosure (cf. Germanic garðr)",
        "kuban": "winding, twisting (river name; Sarmatian)",
        "istr": "flowing (< *sr̥tu- 'flow'; > Dniester, Istria?)",
        "para": "far, beyond (in Danapris compound)",
        "nazdya": "near, close (in Danastris compound)",
        "tana": "river (Greek form of *dānu; > Tanais = Don)",
        "arya": "noble, Iranian (self-designation)",
        "varu": "wide, spacious",
        "xšaya": "ruler, king (> Greek Skythēs?)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a potential Scythian-Sarmatian toponym."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Check for the critical *dānu- element (Don, Dnieper, Dniester)
        if form_lower.startswith(("dn", "dan", "don")):
            if form_lower.startswith("dn"):
                # Dnieper / Dniester pattern
                remainder = form[2:]
                results.extend(
                    [
                        SegmentationResult(
                            component="Dn-", position=0, morph_type="prefix", confidence=0.7
                        ),
                        SegmentationResult(
                            component=remainder, position=1, morph_type="stem", confidence=0.7
                        ),
                    ]
                )
            elif form_lower.startswith("dan"):
                remainder = form[3:]
                results.extend(
                    [
                        SegmentationResult(
                            component="Dan-", position=0, morph_type="prefix", confidence=0.65
                        ),
                        SegmentationResult(
                            component=remainder, position=1, morph_type="stem", confidence=0.65
                        ),
                    ]
                )

        # Check for -don suffix (common in Ossetic/Sarmatian territory)
        if form_lower.endswith("don") and len(form_lower) > 4:
            stem = form[: len(form) - 3]
            results.extend(
                [
                    SegmentationResult(
                        component=stem, position=0, morph_type="compound_modifier", confidence=0.6
                    ),
                    SegmentationResult(
                        component="don", position=1, morph_type="compound_head", confidence=0.6
                    ),
                ]
            )

        # Other Iranian suffixes
        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes if s != "-don"],
            key=len,
            reverse=True,
        )
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
        """Classify whether a form is likely Scythian-Sarmatian."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Critical: *dānu- river names
        if form_lower in ("don", "tanais"):
            evidence.append("Known Scythian river name (Don/Tanais < *dānu)")
            score += 0.9
        elif form_lower.startswith(("dniep", "dnepr", "dnip")):
            evidence.append("Dnieper < *Dānu-apara 'far river'")
            score += 0.85
        elif form_lower.startswith(("dniest", "dnestr", "dnist")):
            evidence.append("Dniester < *Dānu-nazdya 'near river'")
            score += 0.85
        elif form_lower.startswith(("danub", "dunaj", "dunăr", "duna")):
            evidence.append("Danube < *Dānu (Iranian) or Celtic *dānu- (debated)")
            score += 0.5

        # Sarmatian -don suffix in North Caucasus
        if form_lower.endswith("don") and len(form_lower) > 4:
            evidence.append("Suffix -don (< *dānu 'water'; Ossetic territory)")
            score += 0.5

        # Alan/As tribal name
        if "alan" in form_lower or form_lower.startswith("as"):
            evidence.append("Possible Alan/As tribal name element")
            score += 0.25

        # Ossetic-like phonology (no initial clusters, -æ- vowel)
        if "ae" in form_lower or "æ" in form_lower:
            evidence.append("Ossetic-type æ vowel")
            score += 0.15

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Suggest Scythian-Sarmatian etymologies for a toponym."""
        candidates: list[EtymologyCandidate] = []
        form = components[0].component if components else ""
        form_lower = form.lower()

        # High-confidence: known Iranian river name elements
        if form_lower.startswith(("don", "dn", "dan", "tana")):
            candidates.append(
                EtymologyCandidate(
                    lemma="*dānu-",
                    meaning="river, water (Eastern Iranian; cf. Avestan dānu-)",
                    language_code=self.language_code,
                    confidence=0.7,
                )
            )

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                if element in ("don", "danu"):
                    continue  # already handled above
                candidates.append(
                    EtymologyCandidate(
                        lemma=f"*{element}",
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=0.4,
                    )
                )

        return candidates
