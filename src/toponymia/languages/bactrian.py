"""Bactrian language module for toponymic analysis.

Bactrian was a Northeastern Iranian language spoken in ancient Bactria
(northern Afghanistan/southern Uzbekistan/Tajikistan) from the 2nd century
BCE to the 9th century CE. Uniquely among Iranian languages, it was written
in Greek script (inherited from Hellenistic colonization).

Bactrian toponymic features:
- Hellenistic-Iranian fusion: Greek city names + Iranian elements
- Alexander's campaigns left Greek names (Alexandria, Ai-Khanoum)
- Key names: Balkh (< Bactra < *Bāxtrī), Kunduz, Bamiyan
- Greek script evidence for Iranian phonology
- Connected to European geographic knowledge through classical sources

Key references:
- Sims-Williams 2000 "Bactrian Documents from Northern Afghanistan"
- Sims-Williams 2007 "Bactrian Personal Names"
- Grenet 2005 "Bactrian Toponymy"
- Bernard 1967 "Ai Khanoum" (Hellenistic city)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class BactrianModule(BaseLanguageModule):
    """Language module for Bactrian-origin toponyms."""

    language_code = "xbc"
    language_name = "Bactrian"
    family = "Indo-European"
    branch = "Indo-Iranian > Iranian > Northeastern Iranian"
    period = "Bactrian (2nd c. BCE – 9th c. CE); DEAD"
    script = "Grek (Greek script, unique for Iranian)"

    prefixes = [
        "Βαχλ-",  # Balkh (< *Bāxtrī)
        "Αλ-",  # Greek-Bactrian prefix
    ]

    suffixes = [
        "-βαγο",  # god (< *baga-; in theophoric names)
        "-ασπο",  # horse (< *aspa-; in personal/place names)
        "-αβαδο",  # settlement (< *ābād, shared with Persian)
        "-γαν",  # place (< *-gāna)
        "-ιγο",  # adjectival suffix
        "-ανο",  # locative suffix
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "βαχλ": "Balkh, Bactria (< Old Iranian *Bāxtrī = splendid?)",
        "βαγο": "god (< *baga-; cf. Slavic bog)",
        "ασπο": "horse (< *aspa-; cf. Persian asp)",
        "αβαδο": "settlement (< *ābād)",
        "μαρο": "great? (cf. Maracanda)",
        "χοαδ": "self, own (< *xwat-)",
        "φαρο": "glory (< *farnah-; cf. Avestan xᵛarənah-)",
        "μιρο": "Mithra, sun (< *Miθra-)",
        "ναν": "bread, sustenance",
        "σαδο": "hundred (< *sata-)",
        "λαδο": "brought (< *ni-āta- ?)",
        "κανδ": "city (shared with Sogdian < *kanta-)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Bactrian-origin toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        # Check for Greek-script Bactrian patterns (transliterated)
        bactrian_suffixes = ["bago", "aspo", "abado", "gan", "igo", "ano"]
        bactrian_suffixes_sorted = sorted(bactrian_suffixes, key=len, reverse=True)

        matched_suffix = None
        for suffix in bactrian_suffixes_sorted:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_suffix:
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
                    confidence=0.7,
                )
            )
        else:
            results.append(
                SegmentationResult(
                    component=form,
                    position=0,
                    morph_type="stem",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym has Bactrian origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Known Bactrian toponyms
        known = {
            "balkh": "< *Bāxtrī (Bactria)",
            "bactra": "Greek form of Balkh",
            "kunduz": "Bactrian settlement",
            "bamiyan": "< Bactrian *bāmiyāno?",
        }
        for name, note in known.items():
            if name in form_lower:
                evidence.append(f"Known Bactrian toponym: {note}")
                score += 0.5
                break

        # Bactrian suffix patterns (transliterated from Greek script)
        bactrian_markers = ["bago", "aspo", "faro", "abado"]
        for marker in bactrian_markers:
            if marker in form_lower:
                evidence.append(f"Bactrian element -{marker}")
                score += 0.35
                break

        # Hellenistic overlay (Alexandria etc.)
        if form_lower.startswith("alexand"):
            evidence.append("Hellenistic foundation name (Alexander)")
            score += 0.3

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Bactrian period (2nd c. BCE – 9th c. CE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Bactrian components."""
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
                        cognates=["Sogdian βγ- (god)", "Avestan baga-"]
                        if "bag" in comp.lemma.lower()
                        else [],
                        sound_changes=["Written in Greek script (unique for Iranian)"],
                        sources=["Sims-Williams 2000"],
                    )
                )
        return candidates
