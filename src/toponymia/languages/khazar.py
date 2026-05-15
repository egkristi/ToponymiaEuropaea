"""Khazar language module for toponymic analysis.

The Khazars were a semi-nomadic Turkic people who established a major
empire (Khazar Khaganate, c. 650–969 CE) controlling:
- Crimea, North Caucasus, Lower Volga, western Kazakhstan
- Key trade routes between Byzantium, Islam, and the Norse world

Critical connection to Norse studies:
- The Varangian (Viking) trade route to Constantinople passed through
  Khazar territory: Rus → Khazar → Caspian/Constantinople
- Ibn Fadlan (921) describes Rus traders in Khazar lands (Volga Bulgaria)
- Khazar capital Itil/Atil on the Volga was a trade nexus
- Some toponyms along Viking eastern routes are Khazar in origin
- Sarkel (White Tower) on the Don: Khazar fortress, later taken by Svyatoslav

The Khazar language is poorly attested but was Oghur Turkic (related
to Bulgar Turkic / ancestor of Chuvash). Toponyms reconstructed from
Greek, Arabic, and Hebrew sources.

Toponymic traces:
- Itil/Atil (Volga, and the Khazar capital)
- Sarkel (Don fortress; Turkic sar 'white' + kel 'house')
- Samandar (Caspian capital; < samandar 'salamander'?)
- Crimean names from Khazar period
- Possible: "Khazar" > "Caspian" (Cazar Sea in some sources)

Key references:
- Golden 1980 "Khazar Studies"
- Brook 2006 "The Jews of Khazaria"
- Dunlop 1954 "The History of the Jewish Khazars"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class KhazarModule(BaseLanguageModule):
    """Language module for Khazar (Oghur Turkic) toponyms."""

    language_code = "zkz"  # ISO 639-3 for Khazar (extinct)
    language_name = "Khazar"
    family = "Turkic"
    branch = "Oghur (Lir-Turkic; related to Bulgar/Chuvash)"
    period = "650–969 CE (Khaganate period)"
    script = "None (reconstructed from Arabic/Greek/Hebrew sources)"

    prefixes = [
        "Sar-",  # white (Sarkel = White Tower/House)
        "Kara-",  # black (shared Turkic)
        "Ak-",  # white (alternate form)
        "Itil-",  # river/Volga (Khazar name for Volga)
        "Bal-",  # honey; also city (Balanjar)
        "Khan-",  # ruler (Khazar khagan)
        "Qaz-",  # Khazar (self-name? cf. Qasar)
    ]

    suffixes = [
        "-kel",  # house, tent (Sarkel = white house)
        "-itil",  # river (cf. Itil = Volga)
        "-saray",  # palace (shared Turkic < Persian)
        "-baliq",  # city (Oghur form; Balanjar?)
        "-gard",  # city, enclosure (< Iranian; Semender?)
        "-su",  # water
        "-dagh",  # mountain (Khazar-influenced Crimean forms)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "sar": "white, pale (Oghur Turkic; cf. Common Turkic sary 'yellow')",
        "kel": "house, tent, dwelling (Sarkel)",
        "itil": "river; also the Volga (Khazar name; cf. Atil)",
        "atil": "great river, Volga (Arabic sources: Itil/Atil)",
        "kara": "black (shared Turkic color term)",
        "bal": "honey; also city element (Balanjar)",
        "khan": "ruler, sovereign (Khazar khagan rank)",
        "khagan": "emperor, supreme ruler (Turkic/Mongolic)",
        "sarkel": "white house/tower (Don fortress; sar+kel)",
        "samandar": "Caspian capital (etymology debated)",
        "balanjar": "early Khazar capital (Dagestan area)",
        "qazar": "Khazar (ethnonym; possibly 'wanderer')",
        "tamgan": "seal, brand (administrative term)",
        "tudun": "governor (Khazar title in Crimea)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a potential Khazar toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Special case: Sarkel (well-attested compound)
        if "sarkel" in form_lower:
            results.append(
                SegmentationResult(
                    segments=["sar", "kel"],
                    language=self.language_code,
                    confidence=0.85,
                    notes="Khazar: sar 'white' + kel 'house' (Don fortress)",
                )
            )
            return results

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
            if form_lower.startswith(prefix):
                remainder = form[len(prefix) :]
                meaning = self.ELEMENT_MEANINGS.get(prefix, "")
                results.append(
                    SegmentationResult(
                        segments=[prefix, remainder],
                        language=self.language_code,
                        confidence=0.5,
                        notes=(f"Khazar prefix '{prefix}' ({meaning}) + '{remainder}'"),
                    )
                )
                break

        for suffix in sorted_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                stem = form[: len(form) - len(suffix)]
                meaning = self.ELEMENT_MEANINGS.get(suffix, "")
                results.append(
                    SegmentationResult(
                        segments=[stem, suffix],
                        language=self.language_code,
                        confidence=0.5,
                        notes=(f"Khazar: '{stem}' + suffix '-{suffix}' ({meaning})"),
                    )
                )
                break

        return results

    def classify(self, form: str) -> list[LanguageClassification]:
        """Classify whether a form is likely Khazar."""
        form_lower = form.lower()
        evidence: list[str] = []
        score = 0.0

        # Known Khazar place names
        known_khazar = {
            "sarkel": "Khazar Don fortress (sar 'white' + kel 'house')",
            "itil": "Khazar capital / Volga river name",
            "atil": "Volga (Arabic form of Itil)",
            "samandar": "Khazar Caspian capital",
            "balanjar": "Early Khazar capital (Dagestan)",
        }
        for name, desc in known_khazar.items():
            if name in form_lower:
                evidence.append(f"Known Khazar toponym: {desc}")
                score += 0.8
                break

        # Oghur Turkic distinctive: sar- instead of sary-
        if form_lower.startswith("sar") and not form_lower.startswith("sary"):
            evidence.append("Oghur Turkic sar- 'white' (vs Common Turkic sary- 'yellow')")
            score += 0.3

        # Khazar-era Crimean/Caucasus context markers
        khazar_elements = ["kel", "qaz", "khagan", "tudun"]
        for elem in khazar_elements:
            if elem in form_lower:
                evidence.append(f"Khazar element '{elem}'")
                score += 0.35
                break

        return [
            LanguageClassification(
                language=self.language_code,
                confidence=min(score, 1.0),
                evidence=evidence,
            )
        ]

    def etymologize(self, form: str) -> list[EtymologyCandidate]:
        """Suggest Khazar etymologies for a toponym."""
        candidates: list[EtymologyCandidate] = []
        form_lower = form.lower()

        for element, meaning in self.ELEMENT_MEANINGS.items():
            if element in form_lower and len(element) >= 3:
                candidates.append(
                    EtymologyCandidate(
                        language=self.language_code,
                        proto_form=f"*{element}",
                        meaning=meaning,
                        confidence=0.45,
                        notes=(f"Khazar (Oghur Turkic) element '{element}' in '{form}'"),
                    )
                )

        return candidates
