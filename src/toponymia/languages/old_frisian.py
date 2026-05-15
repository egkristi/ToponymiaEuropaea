"""Old Frisian language module for toponymic analysis.

Old Frisian is crucial for North Sea coastal toponymy:
- Closest relative of Old English (Anglo-Frisian unity)
- Frisian coast from Flanders to Denmark (including North Frisian Islands)
- Norse-Frisian contact in Schleswig/Jutland border zone
- Distinctive terp/wierde (artificial mound) settlements
- Shared elements with Old Saxon in low-lying coastal areas

Key references:
- Blok 1988 "De Franken in Nederland"
- Bremmer 2009 "An Introduction to Old Frisian"
- Markey 1981 "Frisian" in Trends in Linguistics
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class OldFrisianModule(BaseLanguageModule):
    """Language module for Old Frisian toponyms."""

    language_code = "ofs"  # ISO 639-3 for Old Frisian
    language_name = "Old Frisian"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Anglo-Frisian"
    period = "700–1500 CE"
    script = "Latn"

    prefixes = [
        "Nij-",  # new (Nijemirdum)
        "Ald-",  # old (Aldeboarn)
        "Grut-",  # great (Grut-Fryslân)
        "Lyts-",  # small
        "East-",  # east (Easterlittens)
        "West-",  # west (Westergeest)
        "North-",  # north (Nordfriesland)
        "Süd-",  # south
        "Hoge-",  # high
        "Lage-",  # low
    ]

    suffixes = [
        "-um",  # dative plural locative (Harlingen→Harlingum)
        "-heim",  # home (> -em/-um in modern Frisian)
        "-hûs",  # house (Bolsward→Boalsert)
        "-wert",  # raised land, terp (Leeuwarden→Ljouwert)
        "-wierde",  # artificial mound (terp)
        "-terp",  # artificial dwelling mound
        "-bûr",  # dwelling, hamlet
        "-buurt",  # neighbourhood
        "-ga",  # district (Westergo, Oostergo)
        "-gea",  # variant
        "-land",  # land
        "-wâld",  # forest (Opsterland)
        "-mar",  # lake (Bergumermeer)
        "-meer",  # lake
        "-sleat",  # channel, sluice
        "-feart",  # waterway
        "-dyk",  # dike
        "-syl",  # sluice
        "-oard",  # variant of -wert
        "-ens",  # place of (< -ingi; Workum→Warkens)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "nij": "new",
        "ald": "old",
        "grut": "great, large",
        "lyts": "small",
        "um": "at, locative plural (< hēmum)",
        "heim": "home, settlement",
        "hûs": "house",
        "wert": "raised land, dwelling mound",
        "wierde": "artificial mound (terp)",
        "terp": "artificial dwelling mound",
        "bûr": "dwelling, farmer's hamlet",
        "ga": "district, region (gā)",
        "land": "land, territory",
        "wâld": "forest, woodland",
        "mar": "lake",
        "meer": "lake, sea",
        "sleat": "channel, ditch",
        "feart": "waterway, canal",
        "dyk": "dike, embankment",
        "syl": "sluice",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Old Frisian toponym into morphological components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes],
            key=len,
            reverse=True,
        )
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

        matched_suffix = None
        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            if matched_prefix and stem.lower().startswith(matched_prefix):
                results.append(
                    SegmentationResult(
                        component=stem[: len(matched_prefix)],
                        position=0,
                        morph_type="compound_modifier",
                        lemma=matched_prefix,
                        confidence=0.8,
                    )
                )
                mid = stem[len(matched_prefix) :]
                if mid:
                    results.append(
                        SegmentationResult(
                            component=mid,
                            position=1,
                            morph_type="stem",
                            lemma=mid.lower(),
                            confidence=0.5,
                        )
                    )
            else:
                results.append(
                    SegmentationResult(
                        component=stem,
                        position=0,
                        morph_type="compound_modifier",
                        lemma=stem.lower(),
                        confidence=0.6,
                    )
                )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=len(results),
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.8,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.7,
                )
            )
            results.append(
                SegmentationResult(
                    component=form[len(matched_prefix) :],
                    position=1,
                    morph_type="compound_head",
                    lemma=form[len(matched_prefix) :].lower(),
                    confidence=0.5,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="simplex",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym is likely Old Frisian."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        frisian_suffixes = ["um", "wert", "wierde", "terp", "ga", "gea", "bûr", "wâld"]
        for marker in frisian_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Frisian suffix -{marker}")
                score += 0.35
                break

        frisian_prefixes = ["nij", "ald", "grut"]
        for marker in frisian_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Frisian prefix {marker}-")
                score += 0.25
                break

        # Frisian-specific characters
        if "û" in form_lower or "â" in form_lower or "ê" in form_lower:
            evidence.append("Frisian circumflex vowel")
            score += 0.15

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="700–1500 CE" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Old Frisian components."""
        candidates: list[EtymologyCandidate] = []
        for comp in components:
            if comp.lemma is None:
                continue
            meaning = self.ELEMENT_MEANINGS.get(comp.lemma.lower().rstrip("-"))
            if meaning:
                candidates.append(
                    EtymologyCandidate(
                        lemma=comp.lemma,
                        meaning=meaning,
                        language_code=self.language_code,
                        confidence=comp.confidence,
                    )
                )
        return candidates
