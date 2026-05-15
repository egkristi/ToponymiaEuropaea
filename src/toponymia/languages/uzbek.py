"""Uzbek language module for toponymic analysis.

Uzbek (Oʻzbekcha) is a Karluk Turkic language spoken in Uzbekistan.
It is the dominant language of Silk Road cities (Samarkand, Bukhara, Tashkent)
whose names reached European geographic consciousness through trade contacts.

Uzbek toponymic features:
- Turkic + Persian compound structure (reflecting historical bilingualism)
- Suffixes: -kent/-kand (city), -abad (settlement), -tepa (hill), -kurgon (fortress)
- Silk Road city names: Samarqand (= stone fortress?), Buxoro (Bukhara),
  Toshkent (= stone city), Xiva (Khiva), Qoʻqon (Kokand)

Key references:
- Nafasov 1988 "Oʻzbekiston toponimlari"
- Karmysheva 1976 "Toponymy of Uzbekistan" (in Russian)
- Grenet 2004 "Maracanda/Samarkand, une métropole pré-mongole"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class UzbekModule(BaseLanguageModule):
    """Language module for Uzbek-origin toponyms."""

    language_code = "uzb"
    language_name = "Uzbek"
    family = "Turkic"
    branch = "Karluk"
    period = "Chagatai period 15th c.; Modern Uzbek 20th c.–"
    script = "Latn (since 1993); Cyrl (Soviet); Arab (historical)"

    prefixes = [
        "Tosh-",  # stone (Toshkent)
        "Oq-",  # white (Oqtepa)
        "Qora-",  # black (Qoratog)
        "Qizil-",  # red (Qizilqum)
        "Yangi-",  # new (Yangiyer)
        "Eski-",  # old (Eski Toshkent)
        "Olti-",  # six (Oltiariq)
    ]

    suffixes = [
        "-kent",  # city (Toshkent)
        "-kand",  # city (Samarqand)
        "-abad",  # settlement (Jizzax < Jizzabad?)
        "-tepa",  # hill, mound (Oqtepa)
        "-kurgon",  # fortress (Shahrikurgon)
        "-qishloq",  # village
        "-ariq",  # canal, irrigation ditch (Oltiariq)
        "-suv",  # water (Qorasuv)
        "-tog",  # mountain (Qoratog)
        "-qum",  # sand (Qizilqum)
        "-daryo",  # river (< Persian daryā)
        "-koʻl",  # lake
        "-buloq",  # spring
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "tosh": "stone, rock",
        "kent": "city, settlement",
        "kand": "city (< Sogdian *kanθ)",
        "tepa": "hill, mound (archaeological tell)",
        "kurgon": "fortress, walled settlement",
        "qishloq": "village (winter quarters)",
        "ariq": "canal, irrigation channel",
        "suv": "water",
        "tog": "mountain",
        "qum": "sand, desert",
        "daryo": "river, sea (< Persian daryā)",
        "oq": "white",
        "qora": "black, large",
        "qizil": "red, gold",
        "yangi": "new",
        "eski": "old",
        "buloq": "spring, source",
        "koʻl": "lake",
        "samar": "stone? fat? (disputed etymology)",
        "buxoro": "monastery? (< Sanskrit vihāra?; disputed)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment an Uzbek-origin toponym into components."""
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
                    confidence=0.8,
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
                    confidence=0.75,
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
        """Classify whether a toponym has Uzbek origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        uz_suffixes = ["kent", "kand", "tepa", "kurgon", "qishloq", "ariq"]
        for marker in uz_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Uzbek/Karluk suffix -{marker}")
                score += 0.4
                break

        uz_prefixes = ["tosh", "yangi", "eski", "qizil"]
        for marker in uz_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Uzbek prefix {marker}-")
                score += 0.3
                break

        # Uzbek-specific orthography (oʻ, gʻ)
        if "oʻ" in form_lower or "gʻ" in form_lower:
            evidence.append("Uzbek-specific graphemes (oʻ, gʻ)")
            score += 0.2

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Karluk/Uzbek Silk Road period" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Uzbek components."""
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
                        cognates=["Sogdian *kanθ (city)"] if "kand" in comp.lemma.lower() else [],
                        sources=["Nafasov 1988"],
                    )
                )
        return candidates
