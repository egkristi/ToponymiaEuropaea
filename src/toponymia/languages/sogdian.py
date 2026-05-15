"""Sogdian language module for toponymic analysis.

Sogdian was a Northeastern Iranian language, the lingua franca of the Silk Road
from roughly the 4th century BCE to the 10th century CE. Sogdian merchants
operated from China to Byzantium, and their toponymic legacy survives in
Central Asian city names that European geographers transmitted.

Sogdian toponymic features:
- City suffix *-kanθ/-kand (city, wall): Samarkand, Tashkent, Yarkand
- Settlement name structure: X-kand = "city of X"
- Key names: Samarkand (Maracanda in Greek), Bukhara (< vihāra?),
  Panjikent (= Five Cities), Varakhsha
- Influenced subsequent Turkic and Persian toponymy
- Known to Europeans through Alexander's campaigns and Silk Road trade

Key references:
- Sims-Williams 1996 "Sogdian and Turkish"
- Lurje 2010 "Personal Names in Sogdian Texts"
- de la Vaissière 2005 "Sogdian Traders"
- Henning 1940 "Sogdian Tales"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class SogdianModule(BaseLanguageModule):
    """Language module for Sogdian-origin toponyms."""

    language_code = "sog"
    language_name = "Sogdian"
    family = "Indo-European"
    branch = "Indo-Iranian > Iranian > Northeastern Iranian"
    period = "Sogdian (4th c. BCE – 10th c. CE); DEAD"
    script = "Sogd (Sogdian script, from Aramaic)"

    prefixes = [
        "Panǰ-",  # five (Panjikent)
        "Nav-",  # new (Navākat)
        "Var-",  # fortress? (Varakhsha)
    ]

    suffixes = [
        "-kanθ",  # city, wall (Samarkanθ > Samarkand)
        "-kand",  # city (later form; Samarkand)
        "-kath",  # city (Arabic transcription)
        "-kat",  # city (variant; Tashkat > Tashkent)
        "-nama",  # document, book (used in compounds)
        "-ik",  # diminutive / adjectival
        "-āk",  # nominal derivation
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "kanθ": "city, walled settlement (< Old Iranian *kanta-)",
        "kand": "city (Middle Iranian continuation)",
        "kath": "city (Arabic rendering of *kanθ)",
        "kat": "city (variant)",
        "panǰ": "five (< Old Iranian *panča)",
        "nav": "new (< Old Iranian *nava-)",
        "var": "fortress, enclosure (< *vara-)",
        "samar": "stone? fat? rich? (disputed; Greek Maracanda)",
        "āb": "water (< Old Iranian *āp-)",
        "rūδ": "river (< *rautah-)",
        "βuγ": "god (in theophoric names)",
        "ōš": "consciousness, light (Sogdian *ōš-)",
        "čākar": "servant (in compound names)",
        "δēw": "demon (< *daiva-)",
        "māx": "moon (calendrical names)",
        "miθr": "sun, Mithra (theophoric)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Sogdian-origin toponym into components."""
        results: list[SegmentationResult] = []
        form_lower = form.lower()

        sorted_suffixes = sorted(
            [s.lstrip("-").lower() for s in self.suffixes], key=len, reverse=True
        )
        sorted_prefixes = sorted(
            [p.rstrip("-").lower() for p in self.prefixes], key=len, reverse=True
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
                    confidence=0.7,
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
                    confidence=0.75,
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
                    confidence=0.75,
                )
            )
        elif matched_prefix:
            results.append(
                SegmentationResult(
                    component=form[: len(matched_prefix)],
                    position=0,
                    morph_type="compound_modifier",
                    lemma=matched_prefix,
                    confidence=0.65,
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
                    morph_type="stem",
                    lemma=form.lower(),
                    confidence=0.3,
                )
            )

        return results

    def classify(self, form: str) -> LanguageClassification:
        """Classify whether a toponym has Sogdian origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        # Highly diagnostic Sogdian city suffix
        sog_suffixes = ["kand", "kanθ", "kath", "kat"]
        for marker in sog_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Sogdian city suffix -*{marker} (< *kanta-)")
                score += 0.5
                break

        # Sogdian-specific prefixes
        if form_lower.startswith(("panǰ", "panj")):
            evidence.append("Sogdian numeral panǰ- (five)")
            score += 0.3

        # Known Sogdian names
        known = {"samarkand": "Maracanda", "bukhara": "Bukhārā", "panjikent": "Panǰīkant"}
        for name, note in known.items():
            if name in form_lower:
                evidence.append(f"Known Sogdian toponym ({note})")
                score += 0.3
                break

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Sogdian period (4th c. BCE – 10th c. CE)" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Sogdian components."""
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
                        cognates=["Old Iranian *kanta- (city)"]
                        if "kan" in comp.lemma.lower()
                        else [],
                        sound_changes=["*kanta- > kanθ > kand (Sogdian lenition)"]
                        if "kan" in comp.lemma.lower()
                        else [],
                        sources=["Sims-Williams 1996", "de la Vaissière 2005"],
                    )
                )
        return candidates
