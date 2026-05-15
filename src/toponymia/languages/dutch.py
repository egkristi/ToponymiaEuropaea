"""Dutch language module for toponymic analysis.

Dutch (Nederlands) is important for European toponymy because:
- North Sea trade zone: Netherlands was a major trading partner of Scandinavia
- VOC colonial naming spread Dutch toponyms globally
- Close relationship to Frisian and Low German
- Shared heritage with Flemish (Belgium) place-naming
- Dutch merchants in Scandinavian ports (Bergen, Stockholm)
- Historical Hanseatic connections alongside Low German
- Distinctive compound system for place-names

Key references:
- Künzel, Blok & Verhoeff 1989 "Lexicon van Nederlandse toponiemen tot 1200"
- de Vries 1962 "Woordenboek der Noordse Mythologie en Etymologie"
- Schönfeld 1955 "Nederlandse waternamen"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class DutchModule(BaseLanguageModule):
    """Language module for Dutch toponyms."""

    language_code = "nld"  # ISO 639-3 for Dutch
    language_name = "Dutch"
    family = "Indo-European"
    branch = "Germanic > West Germanic > Low Franconian"
    period = "12th century CE – present"
    script = "Latn"

    prefixes = [
        "Nieuw-",  # new (Nieuw-Amsterdam, Nieuwegein)
        "Oud-",  # old (Oud-Beijerland)
        "Groot-",  # great (Groot-Ammers)
        "Klein-",  # small (Klein-Zundert)
        "Noord-",  # north (Noord-Holland)
        "Zuid-",  # south (Zuid-Holland)
        "Oost-",  # east (Oost-Vlieland)
        "West-",  # west (West-Friesland)
        "Hoog-",  # high (Hoogezand)
        "Laag-",  # low (Laag-Soeren)
        "Schoon-",  # beautiful/clean (Schoonhoven)
        "'s-",  # genitive article (< des; 's-Gravenhage)
    ]

    suffixes = [
        "-dam",  # dam (Amsterdam, Rotterdam, Zaandam)
        "-dijk",  # dike (Noordwijk→wijk, Beverwijk)
        "-drecht",  # ford, crossing (Dordrecht, Papendrecht)
        "-donk",  # elevated ground in marsh (Bosch-en-donk)
        "-hoven",  # gardens, court (Eindhoven, Veldhoven)
        "-kerk",  # church (Middelkerke, Dunkirk)
        "-meer",  # lake (Haarlemmer Meer)
        "-polder",  # reclaimed land
        "-sluis",  # lock, sluice (Terneuzen-Sluise)
        "-veen",  # peat bog (Hoogeveen, Heerenveen)
        "-vliet",  # stream, channel (Rijswijk-Vliet, Delfshaven)
        "-wijk",  # settlement, district (Beverwijk, Harderwijk)
        "-zijl",  # watergate, sluice (Lemmer-Zijl)
        "-broek",  # marsh, wetland (Hazebroek, Boelbroek)
        "-berg",  # mountain/hill (Valkenburg, Middelburg)
        "-burg",  # fortress (Middelburg, Tilburg)
        "-hem",  # home (Arnhem, Haarlem < Haralem)
        "-loo",  # forest clearing (Waterloo, Venlo)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "nieuw": "new",
        "oud": "old",
        "groot": "great, large",
        "klein": "small, little",
        "noord": "north",
        "zuid": "south",
        "oost": "east",
        "west": "west",
        "hoog": "high",
        "laag": "low",
        "schoon": "beautiful, clean",
        "dam": "dam, embankment",
        "dijk": "dike, embankment",
        "drecht": "ford, river crossing",
        "donk": "elevated ground in marshland",
        "hoven": "gardens, court (< hof)",
        "kerk": "church",
        "meer": "lake",
        "polder": "reclaimed land",
        "sluis": "lock, sluice, water gate",
        "veen": "peat bog, fenland",
        "vliet": "stream, small canal",
        "wijk": "settlement, district (< Lat. vicus)",
        "broek": "marsh, wetland",
        "berg": "mountain, hill",
        "burg": "fortress, castle",
        "hem": "home, settlement",
        "loo": "forest clearing (< *lauh-)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Dutch toponym into components."""
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

        if matched_prefix and matched_suffix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.8,
                )
            )
            middle = form[len(matched_prefix) : len(form) - len(matched_suffix)]
            if middle:
                results.append(
                    SegmentationResult(
                        component=middle,
                        position=1,
                        morph_type="stem",
                        lemma=middle.lower(),
                        confidence=0.5,
                    )
                )
            results.append(
                SegmentationResult(
                    component=form[len(form) - len(matched_suffix) :],
                    position=len(results),
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.85,
                )
            )
        elif matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
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
                    position=1,
                    morph_type="compound_head",
                    lemma=matched_suffix,
                    confidence=0.85,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.8,
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
        """Classify whether a toponym is likely Dutch."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        dutch_suffixes = [
            "dam",
            "dijk",
            "drecht",
            "hoven",
            "veen",
            "vliet",
            "sluis",
            "polder",
            "broek",
            "loo",
        ]
        for marker in dutch_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Dutch suffix -{marker}")
                score += 0.35
                break

        dutch_prefixes = ["nieuw", "oud", "groot", "klein", "noord", "zuid"]
        for marker in dutch_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Dutch prefix {marker}-")
                score += 0.25
                break

        # Dutch digraphs
        dutch_patterns = ["ij", "oe", "ui", "aa", "ee", "oo"]
        for pat in dutch_patterns:
            if pat in form_lower:
                evidence.append(f"Dutch orthography '{pat}'")
                score += 0.1
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="12th century – present" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Dutch components."""
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
