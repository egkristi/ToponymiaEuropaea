"""Khwarezmian language module for toponymic analysis.

Khwarezmian was a Northeastern Iranian language spoken in the Khwarezm region
(around the Aral Sea, modern Uzbekistan/Turkmenistan) from the 3rd century
BCE to the 14th century CE. The Khwarezmian Empire was a major power before
the Mongol invasions, and its geographic names were transmitted to Europe
through Islamic geography and Mongol-era contacts.

Khwarezmian toponymic features:
- Aral Sea region geography
- Key names: Khiva (Xīwa), Urgench (Gurgānǰ/Ürgenç), Kath
- Connected to European knowledge through Mongol invasions (1219-1221)
- Al-Khwarizmi (from Khwarezm) → "algorithm" — this geographic name
  entered European intellectual history

Key references:
- Henning 1956 "The Khwarezmian Language"
- MacKenzie 1971 "Khwarezmian Language and Literature"
- Bosworth 1968 "Khwārazm" (Encyclopaedia of Islam)
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class KhwarezmianModule(BaseLanguageModule):
    """Language module for Khwarezmian-origin toponyms."""

    language_code = "xco"
    language_name = "Khwarezmian"
    family = "Indo-European"
    branch = "Indo-Iranian > Iranian > Northeastern Iranian"
    period = "Khwarezmian (3rd c. BCE – 14th c. CE); DEAD"
    script = "Arab (Arabic script in later period); earlier Aramaic-derived"

    prefixes = []

    suffixes = [
        "-ik",  # adjectival (Khwarezmik)
        "-ānč",  # place/locative (Gurgānǰ > Urgench)
        "-kath",  # city (shared with Sogdian; Kath was a major city)
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "xwārazm": "land (< Old Iranian *xwāra-zmi = lowland? sun-land?)",
        "gurgānǰ": "Urgench (< *wṛkāna- = wolf-place?)",
        "kath": "city (< Old Iranian *kanta-; shared with Sogdian)",
        "xīwa": "Khiva (etymology uncertain; < xēw = pleasant?)",
        "āb": "water (< *āp-)",
        "zamīn": "earth, land (< *zam-)",
        "mard": "man (< *marta-)",
        "asp": "horse (< *aspa-)",
        "mihr": "sun, Mithra (< *Miθra-)",
        "bag": "god (< *baga-)",
        "nav": "new (< *nava-)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Khwarezmian-origin toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        khw_suffixes = sorted([s.lstrip("-").lower() for s in self.suffixes], key=len, reverse=True)

        matched_suffix = None
        for suffix in khw_suffixes:
            if form_lower.endswith(suffix) and len(form_lower) > len(suffix) + 1:
                matched_suffix = suffix
                break

        if matched_suffix:
            stem = form[: len(form) - len(matched_suffix)]
            results.append(
                SegmentationResult(
                    component=stem,
                    position=0,
                    morph_type="stem",
                    lemma=stem.lower(),
                    confidence=0.6,
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
        """Classify whether a toponym has Khwarezmian origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Known Khwarezmian toponyms
        known = {
            "khwarezm": "region name (< *xwāra-zmi)",
            "khorezm": "modern variant",
            "khiva": "major Khwarezmian city",
            "urgench": "< Gurgānǰ, Khwarezmian capital",
            "gurganj": "older form of Urgench",
            "kath": "ancient Khwarezmian city",
        }
        for name, note in known.items():
            if name in form_lower:
                evidence.append(f"Known Khwarezmian toponym: {note}")
                score += 0.5
                break

        # Khwarezmian suffixes
        if form_lower.endswith(("ānč", "anch")):
            evidence.append("Khwarezmian locative suffix -ānč")
            score += 0.3

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Khwarezmian period (3rd c. BCE – 14th c. CE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Khwarezmian components."""
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
                        cognates=["Sogdian", "Avestan"],
                        sources=["Henning 1956", "MacKenzie 1971"],
                    )
                )
        return candidates
