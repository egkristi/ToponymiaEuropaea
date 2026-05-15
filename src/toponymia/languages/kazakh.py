"""Kazakh language module for toponymic analysis.

Kazakh (Қазақша/Qazaqsha) is a Kipchak Turkic language spoken in Kazakhstan.
It represents the steppe Turkic toponymic tradition and connects to European
Kipchak (Cuman/Polovtsian) name layers in Ukraine, Hungary, and Romania.

Kazakh toponymic features:
- Steppe landscape vocabulary: tau (mountain), köl (lake), su (water)
- Suffixes: -tau, -köl, -su, -qala (fortress), -ata (father/saint)
- Color modifiers: aq (white), qara (black), sary (yellow), köl (blue)
- Notable names: Astana (= capital), Almaty (= Father of Apples),
  Qaraghandy (Karaganda), Shymkent, Aqtöbe (Aktobe)
- Connected to Cuman/Kipchak names in European steppe (Ukraine, Hungary)

Key references:
- Konkashpaev 1959 "Kazakh Geographic Names"
- Januzakov 1982 "Toponymy of Kazakhstan"
- Golden 1992 "Turkic Peoples in Medieval Eurasia"
"""

from __future__ import annotations

from toponymia.languages.base import (
    BaseLanguageModule,
    EtymologyCandidate,
    LanguageClassification,
    SegmentationResult,
)


class KazakhModule(BaseLanguageModule):
    """Language module for Kazakh-origin toponyms."""

    language_code = "kaz"
    language_name = "Kazakh"
    family = "Turkic"
    branch = "Kipchak"
    period = "Proto-Kipchak 11th c.; Modern Kazakh 15th c.–"
    script = "Latn (since 2017); Cyrl (Soviet); Arab (historical)"

    prefixes = [
        "Aq-",  # white (Aqtöbe, Aqtau)
        "Qara-",  # black/large (Qaraghandy)
        "Sary-",  # yellow (Saryarqa)
        "Köl-",  # blue (part of compounds)
        "Uly-",  # great (Uly Jüz)
        "Kishi-",  # small (Kishi Jüz)
        "Jas-",  # young/green
        "Qyzyl-",  # red
    ]

    suffixes = [
        "-tau",  # mountain (Aqtau, Alatau)
        "-köl",  # lake (Balqash köl)
        "-su",  # water, river (Aqsu)
        "-qala",  # fortress (Türkistan qala)
        "-ata",  # father, saint (Shymkent < ?)
        "-kent",  # city (Shymkent, Turkestankent)
        "-arqa",  # ridge (Saryarqa)
        "-töbe",  # hill (Aqtöbe)
        "-orda",  # horde, palace center
        "-steppe",  # plain
        "-köl",  # lake
        "-özen",  # river
        "-bulaq",  # spring
        "-qum",  # sand
    ]

    ELEMENT_MEANINGS: dict[str, str] = {
        "aq": "white",
        "qara": "black, large, great",
        "sary": "yellow, steppe",
        "köl": "lake",
        "tau": "mountain (< Proto-Turkic *tāγ)",
        "su": "water, river",
        "qala": "fortress",
        "ata": "father, saint, ancestor",
        "kent": "city (< Sogdian *kanθ)",
        "arqa": "back, ridge, upland",
        "töbe": "hill, mound",
        "orda": "horde, camp, palace",
        "özen": "river, stream",
        "bulaq": "spring",
        "qum": "sand, desert",
        "alma": "apple (Almaty = alma + ty = Father of Apples)",
        "qyzyl": "red",
        "jas": "young, green",
        "balqa": "muddy, clayey (Balqash)",
        "shym": "turf, lawn (Shymkent)",
    }

    def segment(self, form: str) -> list[SegmentationResult]:
        """Segment a Kazakh-origin toponym into components."""
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
        """Classify whether a toponym has Kazakh/Kipchak origins."""
        form_lower = form.lower()
        score = 0.0
        evidence: list[str] = []

        kz_suffixes = ["tau", "töbe", "arqa", "özen", "orda"]
        for marker in kz_suffixes:
            if form_lower.endswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Kazakh/Kipchak suffix -{marker}")
                score += 0.4
                break

        kz_prefixes = ["aq", "qara", "sary", "qyzyl"]
        for marker in kz_prefixes:
            if form_lower.startswith(marker) and len(form_lower) > len(marker) + 1:
                evidence.append(f"Kazakh prefix {marker}-")
                score += 0.25
                break

        # Kazakh-specific: ö, ü, q (in Latin script)
        if "ö" in form_lower or "ü" in form_lower:
            evidence.append("Kipchak vowel harmony (ö, ü)")
            score += 0.15

        score = min(score, 1.0)
        return LanguageClassification(
            language_code=self.language_code,
            confidence=score,
            evidence=evidence,
            period_estimate="Kipchak/Kazakh steppe period" if score > 0.3 else None,
        )

    def etymologize(self, components: list[SegmentationResult]) -> list[EtymologyCandidate]:
        """Generate etymology candidates for Kazakh components."""
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
                        cognates=["Cuman/Kipchak " + comp.lemma],
                    )
                )
        return candidates
