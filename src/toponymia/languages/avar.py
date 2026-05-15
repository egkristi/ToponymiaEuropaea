"""Avar language module for toponymic analysis.

The Avars (Pannonian Avars) were a powerful nomadic confederation that
dominated the Carpathian Basin from c. 567–822 CE, before the Hungarian
arrival. Their language is debated (likely Turkic or Mongolic, possibly
mixed), but they left toponymic traces:

Historical context:
- Avar Khaganate controlled Hungary, Austria, Slovakia, Croatia, Serbia
- 250+ years of dominance left substrate names in the region
- Charlemagne destroyed the Avar realm (796 CE), but populations remained
- Some Avar names were absorbed into Slavic and later Hungarian

Connection to broader European toponymy:
- Pannonian basin names that are neither Slavic, Germanic, nor Hungarian
- Ring-fortress (hring) names in the Danube region
- Possible Avar elements in early medieval Austrian/Bavarian names
- Debated connection to East Asian Rouran (柔然)

Linguistic challenge: Very few securely Avar words are known:
- Khagan (supreme ruler)
- Tudun (governor, shared with Khazars/Turks)
- Jugurrus (a drink)
- Some tribal/clan names from Byzantine sources

Key references:
- Pohl 1988 "Die Awaren: Ein Steppenvolk in Mitteleuropa 567-822"
- Róna-Tas 1999 "Hungarians and Europe in the Early Middle Ages"
- Csanád Bálint 1989 "Die Archäologie der Steppe"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class AvarModule(BaseLanguageModule):
    """Language module for Pannonian Avar (extinct) toponyms."""

    language_code = "ave"  # No ISO 639-3; using conventional code
    language_name = "Avar (Pannonian)"
    family = "Uncertain (Turkic/Mongolic/mixed)"
    branch = "Pannonian Avar (possibly Oghur Turkic or para-Mongolic)"
    period = "567–822 CE (Avar Khaganate in Pannonia)"
    script = "None (unwritten; names from Byzantine/Frankish sources)"

    prefixes = [
        "Avar-",  # self-designation? (in external sources)
        "Khan-",  # ruler (shared Turkic/Mongolic)
        "Kara-",  # black (if Turkic; common steppe color)
        "Tur-",  # possibly 'tower/fort' or tribal
        "Bai-",  # rich, noble (shared Turkic/Mongolic)
    ]

    suffixes = [
        "-ring",  # circular fortress (German Hring < Avar fortification)
        "-avar",  # ethnic name
        "-khan",  # ruler title
        "-var",  # fortress? (cf. Iranian/Turkic var)
        "-grad",  # likely Slavic overlay on Avar sites
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "avar": "ethnonym (possibly 'snake' in Mongolic? or from Rouran)",
        "khagan": "supreme ruler (Avar title; shared Turkic/Mongolic)",
        "tudun": "governor, viceroy (shared with Khazars/Turks)",
        "ring": "circular fortress (Avar military architecture; > German Ring)",
        "hring": "ring-fortress (Frankish term for Avar fortifications)",
        "bai": "rich, noble (Turkic/Mongolic title)",
        "khan": "ruler, chief (shared steppe title)",
        "tarkan": "military commander (Avar rank; cf. Turkic tarqan)",
        "kapkan": "gate-keeper? (Avar title; cf. Turkish kapgan)",
        "jugur": "drink (one of few attested Avar words)",
    }

    # Known probable Avar place-name connections
    FULL_ELEMENTS: dict[str, str] = {
        "ring": "Avar ring-fortress sites in Pannonia",
        "avar": "Direct ethnic name reference",
        "obari": "Byzantine name for Avars (Theophylact Simocatta)",
        "hring": "Carolingian term for Avar treasure-fortress",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a potential Avar toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Check for known Avar-associated elements
        for element, _meaning in self.FULL_ELEMENTS.items():
            if element in form_lower:
                idx = form_lower.index(element)
                prefix_part = form[:idx] if idx > 0 else ""
                suffix_part = form[idx + len(element) :]
                segments = [s for s in [prefix_part, element, suffix_part] if s]
                for pos, seg in enumerate(segments):
                    results.append(
                        SegmentationResult(
                            component=seg,
                            position=pos,
                            morph_type="stem" if seg == element else "compound_modifier",
                            confidence=0.5,
                        )
                    )
                break

        # General prefix/suffix analysis
        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes],
            key=len,
            reverse=True,
        )
        for prefix in sorted_prefixes:
            if form_lower.startswith(prefix) and len(form_lower) > len(prefix) + 1:
                remainder = form[len(prefix) :]
                results.extend(
                    [
                        SegmentationResult(
                            component=prefix, position=0, morph_type="prefix", confidence=0.35
                        ),
                        SegmentationResult(
                            component=remainder, position=1, morph_type="stem", confidence=0.35
                        ),
                    ]
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form may have Avar origins."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Known Avar-associated elements
        if "avar" in form_lower or "obari" in form_lower:
            evidence.append("Contains Avar ethnonym")
            score += 0.6

        if "ring" in form_lower or "hring" in form_lower:
            evidence.append("Contains 'ring/hring' (Avar fortress terminology)")
            score += 0.3

        # Avar-era administrative titles in names
        avar_titles = ["khagan", "tudun", "tarkan", "kapkan"]
        for title in avar_titles:
            if title in form_lower:
                evidence.append(f"Contains Avar-era title '{title}'")
                score += 0.4
                break

        # Pannonian context: names that resist Slavic/Germanic/Hungarian etymology
        # This is heuristic — flag if it contains steppe-type elements
        steppe_elements = ["bai", "khan", "kara", "tur"]
        matches = [e for e in steppe_elements if e in form_lower]
        if len(matches) >= 2:
            evidence.append(f"Multiple steppe elements: {', '.join(matches)}")
            score += 0.3

        return LanguageClassification(
            language_code=self.language_code,
            confidence=min(score, 1.0),
            evidence=evidence,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Suggest Avar etymologies for a toponym."""
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
                        confidence=0.35,
                    )
                )

        return candidates
